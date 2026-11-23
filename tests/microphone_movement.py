"""Actual server movement assignments/helpers/Action dispatcher; mock avatar/clock.
Dodge stops after authoritative admission/cooldown setup, not native movement physics.
"""
from pathlib import Path
import argparse,subprocess,tempfile,re
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');a=p.parse_args()
path='src/ServerScriptService/Bootstrap.server.luau';s=(R/path).read_text()
setup=r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local now=10;local os={clock=function()return now end}
local Config={SprintDuration=10,SprintRecovery=5,SprintRegenDelay=1,DodgeDuration=.4,DodgeCooldown=3,HealthForLevel=function()return 100 end}
local Enum={Material={Air='Air'}};local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local workspace={Gravity=196.2,GetServerTimeNow=function()return now end}
local premium=true;local arena=false;local Entitlements={CanUseMovement=function()return premium and not arena end}
local s,r,h,c;local attrs,writes={},{};local p={SetAttribute=function(_,k,v)attrs[k]=v;writes[k]=(writes[k] or 0)+1 end}
Config.InArena=function()return arena end
local sessions={};local cancel=0;local VoiceCombat={Cancel=function(v)v.capture=nil;cancel+=1 end};local function cancelSustained()cancel+=1 end
local handler;local action={OnServerEvent={Connect=function(_,fn)handler=fn end}}
local function reset()
 h={Health=100,MaxHealth=100,FloorMaterial='Ground',Jump=true};r={Position={Y=5},AssemblyLinearVelocity={X=25,Y=0,Z=0}}
 c={FindFirstChild=function()return r end,FindFirstChildOfClass=function()return h end};p.Character=c
 s={micReady=false,voice={},data={level=1},nextDodge=0,dodgingUntil=0,knockedUntil=0,jumpOriginY=0,jumpPower=47,jumpHeight=6.5,sprintCharge=10,sprintLockedUntil=0,sprintRegenAt=0,sprintRequested=false,sprintRunning=false};sessions[p]=s;premium=true;arena=false;attrs={};writes={};now=10
end
'''
def assemble(src):
 parts=src[src.index('local function parts(p)'):src.index('local function sustainedEnd(')]
 sprint=src[src.index('local function stepSprint('):src.index('task.spawn(function()\n local tick=0')]
 dodge_start=src.index('local function dodge(p')
 dodge_end=re.search(r'^ local direction(?:[,=])',src[dodge_start:],re.M)
 assert dodge_end,'Missing dodge direction boundary'
 dodge=src[dodge_start:dodge_start+dodge_end.start()]+'end\n'
 handler=src[src.index('action.OnServerEvent:Connect('):src.index('local function joined(')]
 begin=src.index('    h.WalkSpeed=',src.index('local function stepSprint('));end=src.index('    local healed,',begin)
 apply='local function applyMovement(running)\n'+src[begin:end]+'end\n'
 begin=src.index('   -- Crossing into PvP');end=src.index('   if s.sustained and s.sustained.protocol.active then stepSustained(',begin)
 arena_dodge='local function updateArenaDodge()\n'+src[begin:end]+'end\n'
 spawn=next(line for line in src.splitlines()if 'h.MaxHealth=Config.HealthForLevel(s.data.level);h.Health=h.MaxHealth;h.WalkSpeed=' in line)
 return setup+parts+sprint+dodge+handler+apply+arena_dodge+'local function spawnSpeed()\n'+spawn+'\nend\n'
checks=r'''
reset();spawnSpeed();check(h.WalkSpeed==16,'Unready spawn immobilized')
applyMovement(false);check(h.WalkSpeed==16 and h.JumpPower==47 and h.JumpHeight==6.5 and h.Jump,'Unready walking/jumping immobilized')
for _,ready in ipairs({false,true})do
 reset();s.micReady=ready;handler(p,'Sprint',true);check(stepSprint(s,r,h,now,0),'Unready sprint rejected');applyMovement(true);check(h.WalkSpeed==25,'Sprint speed wrong')
 handler(p,'Sprint',false);now+=.1;check(not stepSprint(s,r,h,now,.1) and math.abs(s.sprintCharge-9.9)<1e-6,'Released interval not billed')
 reset();s.micReady=ready;handler(p,'Dodge');check(s.nextDodge==10.4 and s.dodgingUntil==10.4,'Unready dodge rejected');applyMovement(false);check(h.WalkSpeed==0,'Rolling allowed walk speed')
 reset();s.micReady=ready;arena=true;handler(p,'Dodge');check(s.nextDodge==13,'Arena dodge entitlement bypass')
 reset();s.micReady=ready;h.FloorMaterial='Air';handler(p,'ExtraJump');check(r.AssemblyLinearVelocity.Y==45 and s.nextExtraJump==10.25,'Unready extra jump rejected')
 now=10.1;r.AssemblyLinearVelocity.Y=0;handler(p,'ExtraJump');check(r.AssemblyLinearVelocity.Y==0,'Extra jump cooldown bypass')
end
for _,mode in ipairs({'dead','missing','anchored','seated','seat','ragdoll','knock','cooldown','air'})do
 reset();h.Health=mode=='dead' and 0 or 100;if mode=='missing'then p.Character=nil end
 r.Anchored=mode=='anchored';h.Sit=mode=='seated';h.SeatPart=mode=='seat' and {} or nil;h.PlatformStand=mode=='ragdoll';s.knockedUntil=mode=='knock' and 11 or 0;s.nextDodge=mode=='cooldown' and 11 or 0;h.FloorMaterial=mode=='air' and 'Air' or 'Ground'
 handler(p,'Dodge');check(s.dodgingUntil==0,'Dodge safeguard lost: '..mode)
end
reset();arena=true;handler(p,'Dodge')
check(attrs.DodgeReady==13 and writes.DodgeReady==1,'Dodge did not publish initial deadline')
for _,time in ipairs({10.1,12.9,13,15})do now=time;updateArenaDodge() end
check(s.nextDodge==13 and attrs.DodgeReady==13 and writes.DodgeReady==1,'Arena rewrote the same dodge deadline')
reset();handler(p,'Dodge');now=10.1;updateArenaDodge()
check(writes.DodgeReady==1 and attrs.DodgeReady==10.4 and s.premiumRoll,'Safe zone changed premium roll')
arena=true;now=10.2;updateArenaDodge()
check(s.nextDodge==13 and attrs.DodgeReady==13 and writes.DodgeReady==2,'Arena failed to extend premium dodge once')
check(not s.premiumRoll and s.dodgingUntil==0 and attrs.DodgeEnds==0,'Arena retained premium roll')
arena=false;now=10.3;updateArenaDodge();arena=true;now=10.5;updateArenaDodge()
check(writes.DodgeReady==2 and attrs.DodgeReady==13,'Reentry rewrote the extended deadline')
reset();handler(p,'Dodge');now=15;arena=true;updateArenaDodge()
check(s.nextDodge==13 and attrs.DodgeReady==10.4 and writes.DodgeReady==1,'Expired extension published a new countdown')
handler(p,'Dodge');check(s.nextDodge==18 and attrs.DodgeReady==18 and writes.DodgeReady==2,'Expired dodge did not rearm')
for _,mode in ipairs({'dead','missing','anchored','seated','seat','ragdoll','knock','cooldown','ground','height','noPremium','arena','rolling'})do
 reset();h.FloorMaterial='Air';h.Health=mode=='dead' and 0 or 100;if mode=='missing'then p.Character=nil end
 r.Anchored=mode=='anchored';h.Sit=mode=='seated';h.SeatPart=mode=='seat' and {} or nil;h.PlatformStand=mode=='ragdoll';s.knockedUntil=mode=='knock' and 11 or 0;s.nextExtraJump=mode=='cooldown' and 11 or 0
 if mode=='ground'then h.FloorMaterial='Ground'end;if mode=='height'then r.Position.Y=24 end;premium=mode~='noPremium';arena=mode=='arena';s.dodgingUntil=mode=='rolling' and 11 or 0
 local previous=s.nextExtraJump;handler(p,'ExtraJump');check(r.AssemblyLinearVelocity.Y==0 and s.nextExtraJump==previous,'ExtraJump safeguard lost: '..mode)
end
for _,mode in ipairs({'dead','missing','anchored','seated','seat','ragdoll','knock','rolling','exhausted','lock','still'})do
 reset();s.sprintRequested=true;h.Health=mode=='dead' and 0 or 100;if mode=='missing'then p.Character=nil end
 r.Anchored=mode=='anchored';h.Sit=mode=='seated';h.SeatPart=mode=='seat' and {} or nil;h.PlatformStand=mode=='ragdoll';s.knockedUntil=mode=='knock' and 11 or 0;s.dodgingUntil=mode=='rolling' and 11 or 0;s.sprintCharge=mode=='exhausted' and 0 or 10;s.sprintLockedUntil=mode=='lock' and 11 or 0;if mode=='still'then r.AssemblyLinearVelocity.X=0 end
 local _,root,hum=parts(p);check(not stepSprint(s,root,hum,now,0),'Sprint safeguard lost: '..mode)
end
reset();s.knockedUntil=11;applyMovement(false);check(h.WalkSpeed==0,'Knockdown speed restored early')
reset();s.sprintRequested=true;stepSprint(s,r,h,10,0);now=20;check(not stepSprint(s,r,h,now,10) and s.sprintCharge==0 and s.sprintLockedUntil==25,'Unready sprint exhaustion bypass')
handler(p,'Sprint',false);now=25;stepSprint(s,r,h,now,5);check(s.sprintCharge==10 and not s.sprintRunning,'Recovery auto-started or failed')
reset();for _,bad in ipairs({{},1,'true'})do handler(p,'Sprint',bad);check(not s.sprintRequested,'Malformed sprint accepted')end
local stranger={};handler(stranger,'Sprint',true);check(sessions[stranger]==nil,'Unknown session created')
print('PASS',n,'actual server movement source assertions; mocked avatar/dispatcher, no physics/network')
'''
def run(src,error=None):
 payload=assemble(src)+checks
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.mic_movement_',dir=R/'tests',encoding='utf-8',delete=False)as t:t.write(payload);q=Path(t.name)
 try:r=subprocess.run(['luau',str(q)],capture_output=True,text=True,timeout=15)
 finally:q.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS expected failure:',error)
 else:print(out,end='');assert r.returncode==0
if a.baseline:
 old=subprocess.check_output(['git','show','b60dada:'+path],cwd=R,text=True,encoding='utf-8');run(old,'Unready spawn immobilized')
else:
 run(s)
 capture=s[s.index('local function canCapture('):s.index('local function attackOrigin(')]
 training=s[s.index('local function stepTraining('):s.index('local function stepSprint(')]
 assert 's.micReady and VoiceEligibility.Allowed' in capture, 'Beam readiness/eligibility gate changed'
 assert 'not strike and (not s.micReady or not audible(' in training, 'New training strike lost its microphone readiness gate'
 print('PASS two source contracts: beam eligibility/readiness and trainer gate retained')
 if a.negative_controls:
  mutations=[
   ('h.WalkSpeed=16','h.WalkSpeed=s.micReady and 16 or 0','Unready spawn immobilized'),
   ('h.WalkSpeed=now<','h.WalkSpeed=not s.micReady and 0 or now<','Unready walking/jumping immobilized'),
   ('h.JumpPower=s.jumpPower or 50;h.JumpHeight=s.jumpHeight or 7.2','h.JumpPower=s.micReady and (s.jumpPower or 50) or 0;h.JumpHeight=s.micReady and (s.jumpHeight or 7.2) or 0','Unready walking/jumping immobilized'),
   ('not humanoid.PlatformStand and s.sprintRequested','not humanoid.PlatformStand and s.micReady and s.sprintRequested','Unready sprint rejected'),
   ('or h.PlatformStand or now<s.nextDodge','or h.PlatformStand or not s.micReady or now<s.nextDodge','Unready dodge rejected'),
   ('not h.PlatformStand and Entitlements.CanUseMovement','not h.PlatformStand and s.micReady and Entitlements.CanUseMovement','Unready extra jump rejected'),
   ('or r.Anchored or h.Sit','or h.Sit','Dodge safeguard lost: anchored'),
   ('and Entitlements.CanUseMovement(p,root.Position)','and true','ExtraJump safeguard lost: noPremium'),
   ('root.Position.Y<s.jumpOriginY+24','true','ExtraJump safeguard lost: height'),
   ('s.sprintCharge-dt','s.sprintCharge','Released interval not billed'),
   ('if deadline>s.nextDodge then','if deadline>=s.nextDodge then','Arena rewrote the same dodge deadline'),
   ('if deadline>s.nextDodge then','if false then','Arena failed to extend premium dodge once'),
   ('if deadline>now then p:SetAttribute("DodgeReady"','if true then p:SetAttribute("DodgeReady"','Expired extension published a new countdown')]
  for old,new,error in mutations:
   assert s.count(old)==1,old;run(s.replace(old,new),error)
