"""Deterministic server resolver/step TTK, real protocol/adapter/rules. No native/transport claim."""
from pathlib import Path
import subprocess,tempfile,json,hashlib,re,sys
R=Path(__file__).resolve().parents[1]
b=(R/'src/ServerScriptService/Bootstrap.server.luau').read_text()
c=(R/'src/ReplicatedStorage/Shared/Config.luau').read_text()
l=(R/'src/ReplicatedStorage/Shared/CompactLayout.luau').read_text()
r=(R/'src/ServerScriptService/CombatRules.luau').read_text().split('\n',1)[1]
helpers=b[b.index('local function audible('):b.index('local function restoreBot(')]
evade=b[b.index('local function confirmBeamDodge('):b.index('local function combatChallenge(')]
step=b[b.index('local function stepSustained('):b.index('local function cast(')]
mode=b[b.index('local function sameCombatMode('):b.index('local function recordCredit(')]
zone='\n'.join(x.replace('Layout.','Config.') for x in l.splitlines() if x.startswith('Layout.ZoneMin=') or x.startswith('Layout.ZoneMax='))
assert zone
in_arena=next(x for x in c.splitlines() if x.startswith('function Config.InArena('))
setup=r"""
local mt={};local function v(x,y,z)return setmetatable({X=x,Y=y,Z=z},mt)end
mt.__add=function(a,b)return v(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
mt.__sub=function(a,b)return v(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
mt.__mul=function(a,b)return v(a.X*b,a.Y*b,a.Z*b)end
mt.__index=function(a,k)if k=='Magnitude'then return math.sqrt(a.X*a.X+a.Y*a.Y+a.Z*a.Z)elseif k=='Unit'then local m=a.Magnitude;return v(a.X/m,a.Y/m,a.Z/m)elseif k=='Dot'then return function(x,y)return x.X*y.X+x.Y*y.Y+x.Z*y.Z end end end
local Vector3={new=v};local V=v;local RaycastParams={new=function()return {}end};local Enum={RaycastFilterType={Exclude=true}}
local VoiceCombat=require('../src/ReplicatedStorage/Shared/VoiceCombat')
local Attack=require('../src/ReplicatedStorage/Shared/SustainedAttack')
local Adapter=require('../src/ServerScriptService/SustainedAttackAdapter')
local Healing=require('../src/ReplicatedStorage/Shared/Healing')
local Config={Gear=require("../src/ReplicatedStorage/Shared/GearCatalog"),ObjectDestruction=false,HealQuietSeconds=Healing.QuietSeconds,EffectBroadcastRange=1000}
function Config.GetSound()return {level=1}end
function Config.PlayerKOXP()return 0 end
local TrainingRules=require('../src/ReplicatedStorage/Shared/TrainingRules')
local World={Bots={},ReactToScream=function()end,UpdateBot=function()end};local localFixture=false
local sessions={};local clock=0;local cover=false;local awards=0;local koAt;local victim,attacker
local function player(id,pos,hp)
 local h={Health=hp,MaxHealth=hp,PlatformStand=false}
 local root={Position=pos,Parent=true};local char={Parent=true}
 function char:FindFirstChild(name)if name=='HumanoidRootPart'then return root end end
 local p={UserId=id,Character=char,root=root,h=h,attrs={}}
 function p:GetAttribute(k)return self.attrs[k]end
 return p
end
local function parts(p)if p.h.Health<=0 then return nil end;return p.Character,p.root,p.h end
local roster, sightRay
local Players={GetPlayers=function()return roster or {attacker,victim}end}
function Players:GetPlayerFromCharacter(character)
 for _,p in ipairs(Players:GetPlayers())do if p.Character==character then return p end end
end
local workspace={Raycast=function(_,origin,delta,params)
 if sightRay then return sightRay(origin,delta,params) end
 if cover then return {Distance=3,Instance={GetAttribute=function()return nil end}} end
end}
local VoiceEligibility={Allowed=function(s)return s==true end}
local sustained=Adapter.new(Attack,VoiceCombat,function(origin,aim)return (aim-origin).Unit end)
local dodgeCues,coverCues,evadedCues,bodyCues={},{},{},{}
local visualRecipients,visualColor
local colorReads=0
local effect={FireClient=function(_,p,kind,humanoid,sequence,total)
 if kind=='BeamDodged' then table.insert(dodgeCues,{p,humanoid})
 elseif kind=='BeamBodyBlocked' then table.insert(bodyCues,{p,humanoid,sequence})
 elseif kind=='SustainedCover' then table.insert(coverCues,{p,sequence,clock,total})
 elseif kind=='SustainedEvaded' then table.insert(evadedCues,{p,sequence})
 elseif kind=='SustainedBeam' and visualRecipients then table.insert(visualRecipients,{p,total}) end
end,FireAllClients=function()end}
local function sustainedEnd()end
local function beamColor()if visualRecipients then colorReads+=1 end;return visualColor end
local Soccer={Hit=function()return false end};local BeachVolley=Soccer
local function questProgress()end;local function state()end
local function recordCredit()end
local function recordDamage()end
local function awardCombatKO()awards+=1 end
local function eject(p,h)koAt=clock;h.Health=0 end
local function knockOutBot(bot)bot.alive=false;koAt=clock end
"""
checks=r"""
local n=0;local function check(x,m)assert(x,m);n+=1 end
do
 local origin=v(0,3,0);local destination=v(0,3,25)
 local caster=player(1,origin,100)
 local nearby=player(2,v(100,3,0),100)
 local outside=player(3,v(200,3,0),100)
 local defeated=player(4,v(1,3,0),0)
 local s={data={level=1},micReady=true,voiceEligibility=true,protectedUntil=0,dodgingUntil=0,sustained=sustained.New()}
 roster={caster,nearby,outside,defeated}
 clock=1;check(sustained.Begin(s.sustained,clock,{sequence=1,power=1,aim=destination},sustainedContext(caster,s,clock)),'Beam color fixture did not start')
 for sample,color in ipairs({'Gold','Custom'}) do
  clock=1+sample*.21
  sustained.Pulse(s.sustained,clock,{sequence=1,sample=sample,power=1,aim=destination},sustainedContext(caster,s,clock))
  visualColor=color;visualRecipients={};colorReads=0
  stepSustained(caster,s,clock)
  check(#visualRecipients==2 and visualRecipients[1][1]==caster and visualRecipients[2][1]==nearby,'Beam viewers changed')
  check(visualRecipients[1][2]==color and visualRecipients[2][2]==color,'Beam packet color was inconsistent or stale')
  check(colorReads==1,'Beam color resolved more than once for one update')
 end
 roster={outside,defeated};visualRecipients={};colorReads=0;clock=1.63
 sustained.Pulse(s.sustained,clock,{sequence=1,sample=3,power=1,aim=destination},sustainedContext(caster,s,clock))
 stepSustained(caster,s,clock)
 check(#visualRecipients==0 and colorReads==0,'Beam resolved color without a viewer')
 roster=nil;visualRecipients=nil;visualColor=nil
end
local function measure(level,targetLevel,power,kind,tier,phase,quiet,quantum)
 table.clear(dodgeCues);table.clear(coverCues);table.clear(evadedCues)
 clock=0;cover=kind=='cover';awards=0;koAt=nil;World.Bots={}
 local min,max=Config.ZoneMin,Config.ZoneMax
 local x,z=min.X+20,(min.Z+max.Z)*.5
 if kind=='safe' then x=max.X-8 end
 if tier then x=min.X-80 end
 attacker=player(1,v(x,3,z),VoiceCombat.Stats(level,1,false).health)
 victim=player(2,v(x+(kind=='range' and 120 or 10),3,z),VoiceCombat.Stats(targetLevel,1,false).health)
 local s={data={level=level,sound='TinyAah'},micReady=true,voiceEligibility=kind~='notEligible',protectedUntil=kind=='attackerProtected' and 100 or 0,dodgingUntil=0,sustained=sustained.New()}
 local ts={data={level=targetLevel},protectedUntil=kind=='protected' and 100 or 0,dodgingUntil=kind=='dodge' and 100 or 0}
 sessions={[attacker]=s,[victim]=ts}
 if kind=='mixedMode' or kind=='bothTest'then s.testBaseline={} end
 if kind=='bothTest'then ts.testBaseline={} end
 if kind=='safe' then check(Config.InArena(attacker.root.Position) and not Config.InArena(victim.root.Position),'Cross-boundary guard has invalid setup') end
 if kind=='range' then check(Config.InArena(attacker.root.Position) and Config.InArena(victim.root.Position),'Range guard requires both endpoints within PvP') end
 local bot;if tier then bot={id=1,alive=true,root={Parent=true,Position=v(x+10,3,z)},model={Parent=true},start=v(x+10,3,z),health=tier.health,maxHealth=tier.health,training=tier,credit={}};World.Bots={bot};victim.root.Position=v(x+120,3,z)end
 local sequence,sample,nextPulse,begins=0,0,0,0;local ticks={};local initial=victim.h.Health
 for i=0,math.ceil(45/(quantum or .025)) do
  clock=i*(quantum or .025)
  if kind=='midCover' and clock>=.8 then cover=true end
  if not s.sustained.protocol.active and clock+1e-7>=s.sustained.protocol.nextStart and (kind~='timeout' or sequence==0) then
   sequence+=1;local context=sustainedContext(attacker,s,clock)
   local ok=sustained.Begin(s.sustained,clock,{sequence=sequence,power=power,aim=bot and bot.root.Position or victim.root.Position},context)
   if ok then attacker.attrs.SustainedSequence=sequence;begins+=1;sample=0;nextPulse=clock+.125;if kind=='capturedLevel'then s.data.level=1 end end
  end
  if kind~='timeout' and s.sustained.protocol.active and clock+1e-7>=nextPulse then
   sample+=1;sustained.Pulse(s.sustained,clock,{sequence=sequence,sample=sample,power=power,aim=bot and bot.root.Position or victim.root.Position},sustainedContext(attacker,s,clock));nextPulse=clock+.125
  end
  if i%math.floor(.1/(quantum or .025)+.5)==(phase or 0) and s.sustained.protocol.active then
   local before=victim.h.Health;stepSustained(attacker,s,clock)
   if victim.h.Health<before then table.insert(ticks,string.format('%.1f:%d',clock,before-victim.h.Health))end
  end
  if koAt then break end
  if kind and clock>=4 then break end
 end
 if not quiet then print(string.format('ROW %d %d %.2f %s %.3f %d %.1f %d %s',level,targetLevel,power,kind or 'clear',koAt or -1,begins,victim.h.Health,awards,table.concat(ticks,',')))end
 if tier then check(bot.health==0 and not bot.alive and awards==1,'Trainer authority KO failed')
 elseif kind=='timeout'then check(not koAt and victim.h.Health==56 and not s.sustained.protocol.active,'Timeout continued damage')
 elseif kind=='midCover'then
  check(not koAt and #ticks==3 and victim.h.Health==initial-9,'Cover after an opening hit allowed further damage')
 elseif kind=='bothTest' or kind=='capturedLevel'then check(koAt==1.0,'Same-mode or captured-level parity changed')
 elseif kind then check(not koAt and victim.h.Health==initial,'Guard allowed damage '..kind)else check(koAt~=nil and awards==1,'No authoritative KO')end
 if kind=='dodge' then
  check(#dodgeCues==1 and dodgeCues[1][1]==victim and dodgeCues[1][2]==victim.h,'Real resolver evade did not emit a single defender cue')
  check(#evadedCues==1 and evadedCues[1][1]==attacker and evadedCues[1][2]==1,'Attacker dodge cue incorrectly routed or repeated')
 else
  check(#dodgeCues==0 and #evadedCues==0,'Non-evade resolver branch showed a dodge cue')
 end
 if kind=='cover' or kind=='midCover' then
  check(#coverCues==1 and coverCues[1][1]==attacker and coverCues[1][2]==1,'Missing/duplicate or public cover cue')
  check(coverCues[1][3]>=.4,'Cover cue emitted before two blocked ticks')
  if kind=='midCover' then check(coverCues[1][4]==9 and coverCues[1][3]>=1,'Cover cue lost the last confirmed damage') end
 else
  check(#coverCues==0,'Non-cover resolver branch showed cover')
 end
 return koAt,begins
end
for _,level in ipairs({1,25,50,75,100})do for _,power in ipairs({1,.5,.08})do measure(level,1,power)end end
local time=measure(100,1,1);check(math.abs(time-1.0)<.00001,'Max vs starter full-power TTK changed')
measure(100,25,1);measure(100,50,1);measure(100,75,1);measure(100,100,1)
for _,kind in ipairs({'cover','range','safe','protected','dodge','attackerProtected','notEligible','timeout','mixedMode','bothTest','capturedLevel'})do measure(100,1,1,kind)end
measure(1,1,1,'midCover',nil,nil,true)
for level=75,100 do
 local stats=VoiceCombat.Stats(level,1,false)
 check(math.abs(stats.maxDps-(63+(level-75)*(110-63)/25))<1e-8,'Upper interpolation changed')
 for _,power in ipairs({1,.5,.08})do measure(level,1,power,nil,nil,nil,true)end
end
for _,tier in ipairs(TrainingRules.Tiers)do for _,power in ipairs({1,.5,.08})do
 local t,casts=measure(100,1,power,nil,tier,nil,true);print('TRAINER '..tier.id..' '..power..' '..t..' '..casts)
end end
local worst=0
for phase=0,3 do for k=80,1000 do
 local t=measure(100,1,k/1000,nil,nil,phase,true);worst=math.max(worst,t)
 check(t<=2.0250001,'Accepted-power TTK exceeds quantized target')
end end
print('SWEEP 921 powers x4 phases worst '..worst)
local offgrid=measure(100,1,.08,nil,nil,3,true,.0125);print('OFFGRID .0375 phase '..offgrid)
check(math.abs(offgrid-2.0375)<1e-7,'Off-grid timing changed')
local fineWorst=0;local finePhase=0
for phase=0,99 do local t=measure(100,1,.08,nil,nil,phase,true,.001);if t>fineWorst then fineWorst=t;finePhase=phase*.001 end end
print('FINE minimum-power100 phases .001 spacing worst '..fineWorst..' phase '..finePhase)
local state=sustained.New();local context={character={},origin=v(0,0,0),level=100}
check(sustained.Begin(state,0,{sequence=1,power=1,aim=v(10,0,0)},context),'Begin failed')
sustained.Stop(state,.1,1)
check(not sustained.Begin(state,5,{sequence=2,power=1,aim=v(10,0,0)},context),'Cooldown admitted early')
check(sustained.Begin(state,5.1,{sequence=3,power=1,aim=v(10,0,0)},context),'Cooldown boundary rejected')
do
 local a,b,c
 local x,z=Config.ZoneMin.X+20,(Config.ZoneMin.Z+Config.ZoneMax.Z)*.5
 a=player(1,v(x,3,z),480);b=player(2,v(x+19,3,z),480);c=player(3,v(x+10,3,z),480)
 local observer=player(4,v(x+10,3,z+14),480)
 roster={a,b,c,observer}
 local function session()return {protectedUntil=0,dodgingUntil=0}end
 sessions={[a]=session(),[b]=session(),[c]=session(),[observer]=session()}
 local function instance(class,parent)
  return {IsA=function(_,name)return name==class end,Parent=parent}
 end
 c.Character.IsA=function(_,name)return name=='Model' end
 c.Character.Parent=workspace
 a.Character.IsA=c.Character.IsA;a.Character.Parent=workspace
 b.Character.IsA=c.Character.IsA;b.Character.Parent=workspace
 local accessory=instance('Accessory',c.Character)
 local body=instance('Part',accessory)
 local blocker=body
 local sightCalls=0
 sightRay=function(_,delta,params)
  check(params.RespectCanCollide==true,'Sustained ray stopped respecting collidable cover')
  if params.FilterDescendantsInstances[2]~=b.Character then return end
  sightCalls+=1
  return blocker and {Distance=10,Instance=blocker} or nil
 end
 local stats={range=54.75,width=7,power=1}
 local function resolve(sender,now)
  local ctx={player=sender,character=sender.Character,origin=sender.root.Position,position=sender.root.Position}
  return resolveSustained(ctx,v(1,0,0),stats,now)
 end
 local ids,targets,packet=resolve(a,2)
 check(#bodyCues==1 and bodyCues[1][1]==b and bodyCues[1][2]==b.h and bodyCues[1][3]==nil,'Eligible body cover did not send one private defender cue')
 check(sightCalls==1,'The body-cover cue cast a second target sight ray')
 check(#ids==1 and targets['player:3'].humanoid==c.h and not targets['player:2'] and packet.length==54.75 and #packet.dodged==0,'Body cover changed hits, dodge, or visual beam length')
 -- A different beam shares the same defender cooldown.
 observer.root.Position=v(x,3,z)
 resolve(observer,2.99)
 observer.root.Position=v(x+10,3,z+14)
 check(#bodyCues==1,'Different beam bypassed defender cooldown')
 resolve(a,3)
 check(#bodyCues==2,'Defender cooldown did not expire after one second')
 local ts=sessions[b]
 local function noCue(label)
  resolve(a,5)
  check(#bodyCues==2,'Body cover cue leaked to '..label)
 end
 blocker=instance('Part',instance('Model',workspace));noCue('geometry or NPC')
 blocker=instance('Part',a.Character);noCue('attacker character')
 blocker=instance('Part',b.Character);noCue('defender character')
 blocker=body
 ts.dodgingUntil=6;noCue('dodge');ts.premiumRoll=true;noCue('premium roll')
 ts.dodgingUntil=0;ts.premiumRoll=nil
 ts.protectedUntil=6;noCue('spawn protection');ts.protectedUntil=0
 ts.testBaseline={};noCue('different combat mode');ts.testBaseline=nil
 ts.flight=true;noCue('flight');ts.flight=nil
 local pos=b.root.Position
 b.root.Position=v(Config.ZoneMax.X+1,3,z);noCue('safe area')
 b.root.Position=v(x+19,3,z+12);noCue('outside target volume')
 b.root.Position=pos
 blocker=nil
 ids,targets,packet=resolve(a,5)
 check(#bodyCues==2 and #ids==2 and targets['player:2'].humanoid==b.h and packet.length==54.75,'Unblocked beam changed damage eligibility or emitted cover')
 sightRay=nil;roster=nil
end
print('PASS '..n..' actual authority-path TTK/guard assertions; synthetic scheduling, geometry and humanoid endpoint')
"""
code=setup+zone+'\n'+in_arena+'\nlocal Rules=(function()\n'+r+'\nend)()\n'+mode+helpers+evade+step+checks
def run(payload):
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(payload);path=Path(f.name)
 try:return subprocess.run(['luau',str(path)],capture_output=True,text=True,timeout=15)
 finally:path.unlink()
if '--baseline' in sys.argv:
 for module in ['VoiceCombat','SustainedAttack']:
  historical=subprocess.check_output(['git','show','09e0996:src/ReplicatedStorage/Shared/'+module+'.luau'],text=True)
  code=code.replace("require('../src/ReplicatedStorage/Shared/"+module+"')",'(function()\n'+historical+'\nend)()')
 code=code.replace("check(math.abs(offgrid-2.0375)<1e-7,'Off-grid timing changed')","check(offgrid>2,'Historical off-grid exceeds target')")
 code=code.replace('(63+(level-75)*(110-63)/25)','(49+(level-75)*(68-49)/25)').replace("check(t<=2.0250001,'Accepted-power TTK exceeds quantized target')","check(t<=4,'Historical completes one cast')")
 code=code.replace('victim.h.Health==56','victim.h.Health==73').replace('koAt==1.0','koAt==1.6').replace('time-1.0','time-1.6')
if '--body-cover-baseline' in sys.argv:
 old=subprocess.check_output(['git','show','5e7a18e:src/ServerScriptService/Bootstrap.server.luau'],cwd=R,text=True,encoding='utf8')
 old_helpers=old[old.index('local function audible('):old.index('local function restoreBot(')]
 out=run(code.replace(helpers,old_helpers))
 assert out.returncode and 'Eligible body cover did not send one private defender cue' in out.stderr,out.stderr
 print('PASS baseline failed on missing private defender cue')
 sys.exit(0)
result=run(code);print(result.stdout,end='');assert result.returncode==0,result.stderr
if '--negative-controls' in sys.argv:
 failure=run(code.replace('beam.obstruction and noContact','beam.obstruction and noHit'))
 assert failure.returncode!=0 and 'Missing/duplicate or public cover cue' in failure.stderr,failure.stderr
 print('PASS obstruction after damage negative control')
 for old,new,message in [('sameCombatMode(sessions[ctx.player],ts)','true','Guard allowed damage mixedMode'),('now>=targetProtectedUntil','true','Guard allowed damage protected'),('intent.coverTicks==2','intent.coverTicks==1','Cover cue emitted before two blocked ticks'),('intent.coverReported=true','intent.coverTicks=nil','Missing/duplicate or public cover cue'),('intent.evadeReported=true','intent.evadeReported=false','Attacker dodge cue incorrectly routed or repeated')]:
  assert old in code
  out=run(code.replace(old,new));assert out.returncode and message in out.stderr,(old,out.stdout,out.stderr)
 original=(R/'src/ReplicatedStorage/Shared/VoiceCombat.luau').read_text()
 assert original.count('level=100,health=480,dps=110')==1
 mutant=original.replace('level=100,health=480,dps=110','level=100,health=480,dps=68')
 out=run(code.replace("require('../src/ReplicatedStorage/Shared/VoiceCombat')",'(function()\n'+mutant+'\nend)()'))
 assert out.returncode and 'Max vs starter full-power TTK changed' in out.stderr,out.stderr
 for old,new,message in [
  ('effect:FireClient(p,"BeamBodyBlocked",h)','effect:FireClient(ctx.player,"BeamBodyBlocked",h)','Eligible body cover did not send one private defender cue'),
  ('ts.nextBeamBodyBlockCueAt=now+1','ts.nextBeamBodyBlockCueAt=now','Different beam bypassed defender cooldown'),
  ('now>=ts.dodgingUntil and now>=(ts.nextBeamBodyBlockCueAt or 0)','now>=(ts.nextBeamBodyBlockCueAt or 0)','Body cover cue leaked to dodge'),
  ('if blocker and blocker~=p and blocker~=ctx.player and blocker.Character==ancestor then','if ancestor:IsA("Model") then','Body cover cue leaked to geometry or NPC'),
 ]:
  assert old in code
  out=run(code.replace(old,new));assert out.returncode and message in out.stderr,(old,out.stdout,out.stderr)
 old='tint=tint or beamColor(p,s)'
 assert code.count(old)==1
 out=run(code.replace(old,'tint=beamColor(p,s)'))
 assert out.returncode and 'Beam color resolved more than once for one update' in out.stderr,out.stderr
 print('PASS 11 authority/balance/cover/dodge/visual routing negative controls')
if '--report' in sys.argv:
 assert '--baseline' not in sys.argv, 'Historical report must not overwrite candidate evidence'
 paths=['src/ServerScriptService/Bootstrap.server.luau','src/ServerScriptService/SustainedAttackAdapter.luau','src/ServerScriptService/CombatRules.luau','src/ReplicatedStorage/Shared/SustainedAttack.luau','src/ReplicatedStorage/Shared/VoiceCombat.luau','src/ReplicatedStorage/Shared/Healing.luau','src/ReplicatedStorage/Shared/TrainingRules.luau','src/ReplicatedStorage/Shared/Config.luau','src/ReplicatedStorage/Shared/CompactLayout.luau','tests/sustained_ttk.py']
 rows=[]
 for line in result.stdout.splitlines():
  if not line.startswith('ROW '):continue
  values=line.split(' ',9)
  rows.append(dict(attackerLevel=int(values[1]),victimLevel=int(values[2]),power=float(values[3]),condition=values[4],koSeconds=float(values[5]) if float(values[5])>=0 else None,casts=int(values[6]),remainingHealth=float(values[7]),koEndpointCalls=int(values[8]),damageTimeline=values[9] if len(values)>9 else ''))
 report={'scope':'Actual server context/resolver/step and real adapter/protocol/geometry rules; synthetic .1s server observations and .125s pulse delivery, no latency, fixed target. Config arena bounds and InArena extracted; sound unlock and eligibility service mocked. Credit/rewards and eject side effects stubbed; no live/native/microphone claim. Repeated-cast rows include five-second cooldown, exclude human quiet/rearm delay. Healing12s quiet exceeds5s cooldown, so omitted healing loop cannot affect these continuously-hit rows. Pulse-before-step at exact4s expires before final damage tick; other engine event ordering can affect repeated-cast totals, not primary primary result.', 'stdout':result.stdout,'rows':rows,'sourceHashes':{name:hashlib.sha256((R/name).read_bytes()).hexdigest() for name in paths}}
 (R/'build/sustained-ttk-measurement.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 print('REPORT build/sustained-ttk-measurement.json')
