"""Deterministic server resolver/step TTK, real protocol/adapter/rules. No native/transport claim."""
from pathlib import Path
import subprocess,tempfile,json,hashlib,re,sys
R=Path(__file__).resolve().parents[1]
b=(R/'src/ServerScriptService/Bootstrap.server.luau').read_text()
c=(R/'src/ReplicatedStorage/Shared/Config.luau').read_text()
l=(R/'src/ReplicatedStorage/Shared/CompactLayout.luau').read_text()
r=(R/'src/ServerScriptService/CombatRules.luau').read_text().split('\n',1)[1]
helpers=b[b.index('local function audible('):b.index('local function restoreBot(')]
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
local Config={ObjectDestruction=false,HealQuietSeconds=Healing.QuietSeconds,EffectBroadcastRange=1000}
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
local Players={GetPlayers=function()return {attacker,victim}end}
local workspace={Raycast=function(_,origin,delta,params)
 if cover then return {Distance=3,Instance={GetAttribute=function()return nil end}} end
end}
local VoiceEligibility={Allowed=function(s)return s==true end}
local sustained=Adapter.new(Attack,VoiceCombat,function(origin,aim)return (aim-origin).Unit end)
local effect={FireClient=function()end,FireAllClients=function()end}
local function sustainedEnd()end;local function beamColor()return nil end
local Soccer={Hit=function()return false end};local BeachVolley=Soccer
local function questProgress()end;local function state()end
local function recordCredit()end
local function awardCombatKO()awards+=1 end
local function eject(p,h)koAt=clock;h.Health=0 end
local function knockOutBot(bot)bot.alive=false;koAt=clock end
"""
checks=r"""
local n=0;local function check(x,m)assert(x,m);n+=1 end
local function measure(level,targetLevel,power,kind,tier,phase,quiet,quantum)
 clock=0;cover=kind=='cover';awards=0;koAt=nil;World.Bots={}
 attacker=player(1,v(0,3,0),VoiceCombat.Stats(level,1,false).health)
 victim=player(2,v(kind=='range' and 120 or 10,3,0),VoiceCombat.Stats(targetLevel,1,false).health)
 local s={data={level=level,sound='TinyAah'},micReady=true,voiceEligibility=kind~='notEligible',protectedUntil=kind=='attackerProtected' and 100 or 0,dodgingUntil=0,sustained=sustained.New()}
 local ts={data={level=targetLevel},protectedUntil=kind=='protected' and 100 or 0,dodgingUntil=kind=='dodge' and 100 or 0}
 sessions={[attacker]=s,[victim]=ts}
 if kind=='mixedMode' or kind=='bothTest'then s.testBaseline={} end
 if kind=='bothTest'then ts.testBaseline={} end
 if kind=='safe'then victim.root.Position=v(500,3,0)end
 local bot;if tier then bot={id=1,alive=true,root={Parent=true,Position=v(10,3,0)},model={Parent=true},start=v(10,3,0),health=tier.health,maxHealth=tier.health,training=tier,credit={}};World.Bots={bot};victim.root.Position=v(120,3,0)end
 local sequence,sample,nextPulse,begins=0,0,0,0;local ticks={};local initial=victim.h.Health
 for i=0,math.ceil(45/(quantum or .025)) do
  clock=i*(quantum or .025)
  if not s.sustained.protocol.active and clock+1e-7>=s.sustained.protocol.nextStart and (kind~='timeout' or sequence==0) then
   sequence+=1;local context=sustainedContext(attacker,s,clock)
   local ok=sustained.Begin(s.sustained,clock,{sequence=sequence,power=power,aim=bot and bot.root.Position or victim.root.Position},context)
   if ok then begins+=1;sample=0;nextPulse=clock+.125;if kind=='capturedLevel'then s.data.level=1 end end
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
 elseif kind=='bothTest' or kind=='capturedLevel'then check(koAt==1.0,'Same-mode or captured-level parity changed')
 elseif kind then check(not koAt and victim.h.Health==initial,'Guard allowed damage '..kind)else check(koAt~=nil and awards==1,'No authoritative KO')end
 return koAt,begins
end
for _,level in ipairs({1,25,50,75,100})do for _,power in ipairs({1,.5,.08})do measure(level,1,power)end end
local time=measure(100,1,1);check(math.abs(time-1.0)<.00001,'Max vs starter full-power TTK changed')
measure(100,25,1);measure(100,50,1);measure(100,75,1);measure(100,100,1)
for _,kind in ipairs({'cover','range','safe','protected','dodge','attackerProtected','notEligible','timeout','mixedMode','bothTest','capturedLevel'})do measure(100,1,1,kind)end
for level=75,100 do
 local stats=VoiceCombat.Stats(level,1,false)
 check(math.abs(stats.maxDps-(49+(level-75)*(110-49)/25))<1e-8,'Upper interpolation changed')
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
print('PASS '..n..' actual authority-path TTK/guard assertions; synthetic scheduling, geometry and humanoid endpoint')
"""
code=setup+zone+'\n'+in_arena+'\nlocal Rules=(function()\n'+r+'\nend)()\n'+mode+helpers+step+checks
def run(payload):
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(payload);path=Path(f.name)
 try:return subprocess.run(['luau',str(path)],capture_output=True,text=True,timeout=15)
 finally:path.unlink()
if '--baseline' in sys.argv:
 for module in ['VoiceCombat','SustainedAttack']:
  historical=subprocess.check_output(['git','show','09e0996:src/ReplicatedStorage/Shared/'+module+'.luau'],text=True)
  code=code.replace("require('../src/ReplicatedStorage/Shared/"+module+"')",'(function()\n'+historical+'\nend)()')
 code=code.replace("check(math.abs(offgrid-2.0375)<1e-7,'Off-grid timing changed')","check(offgrid>2,'Historical off-grid exceeds target')")
 code=code.replace('(110-49)','(68-49)').replace("check(t<=2.0250001,'Accepted-power TTK exceeds quantized target')","check(t<=4,'Historical completes one cast')")
 code=code.replace('victim.h.Health==56','victim.h.Health==73').replace('koAt==1.0','koAt==1.6').replace('time-1.0','time-1.6')
result=run(code);print(result.stdout,end='');assert result.returncode==0,result.stderr
if '--negative-controls' in sys.argv:
 for old,new,message in [('sameCombatMode(sessions[ctx.player],ts)','true','Guard allowed damage mixedMode'),('now>=targetProtectedUntil','true','Guard allowed damage protected')]:
  assert old in code
  out=run(code.replace(old,new));assert out.returncode and message in out.stderr,(old,out.stdout,out.stderr)
 original=(R/'src/ReplicatedStorage/Shared/VoiceCombat.luau').read_text()
 assert original.count('level=100,health=450,dps=110')==1
 mutant=original.replace('level=100,health=450,dps=110','level=100,health=450,dps=68')
 out=run(code.replace("require('../src/ReplicatedStorage/Shared/VoiceCombat')",'(function()\n'+mutant+'\nend)()'))
 assert out.returncode and 'Max vs starter full-power TTK changed' in out.stderr,out.stderr
 print('PASS 3 authority/balance negative controls')
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
