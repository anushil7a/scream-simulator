"""Actual collection renderer/protocol/adapter with synthetic timing and UI stubs."""
from pathlib import Path
import argparse, subprocess, tempfile
root = Path(__file__).resolve().parents[1]
client = (root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
server = (root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
start = client.index('  local nextStyle', client.index('title.Text="SCREAM COLLECTION"'))
render = client[start:client.index(' elseif selected=="Quests"',start)]
assert 'for _,s in ipairs(Config.Sounds)' in render
endfn = server[server.index('local function sustainedEnd('):server.index('local function cancelSustained(')]
bar = client[client.index(' local fraction\n',client.index('voiceTimeTrack.Visible=')):client.index('\n end\n castButton.BackgroundColor3=',client.index('voiceTimeTrack.Visible='))]
setup = '''
local Combat=require('../src/ReplicatedStorage/Shared/VoiceCombat')
local Attack=require('../src/ReplicatedStorage/Shared/SustainedAttack')
local Adapter=require('../src/ServerScriptService/SustainedAttackAdapter').new(Attack,Combat,function(origin,aim)return aim-origin end)
local checks=0
local function check(v,msg)assert(v,msg);checks+=1 end
local function near(a,b)return math.abs(a-b)<1e-6 end
local UDim2={new=function(...)return {...}end,fromOffset=function(...)return {...}end,fromScale=function(x,y)return {X=x,Y=y}end}
local Color3={fromRGB=function(...)return {...}end};local muted={};local gold={}
local Config={VoiceCombat=Combat,Sounds={{id='one',level=1,name='First',description='First sound'},{id='ten',level=10,name='Ten',description='Ten sound'},{id='cap',level=100,name='Cap',description='Cap sound'}}}
local DestructionRules={Types={}}
local action={FireServer=function()error('Rendering sent an action')end}
local messages={}
local function card()return {}end
local function label(_,text)table.insert(messages,text);return {}end
local function info(text)table.insert(messages,text)end
local function button()return {}end
local function draw(data,narrow,sustainedRules)
 messages={}
'''
checks = '''
end
-- The repeated old per-style readout hid that level, not equipped sound, sets power.
for _,level in ipairs({1,10,50,100}) do
 for _,narrow in ipairs({false,true}) do
  for _,style in ipairs(Config.Sounds) do
   draw({level=level,sound=style.id},narrow,Attack)
   local text=table.concat(messages,'\\n')
   check(string.find(text,'CURRENT BEAM · LEVEL '..level,1,true)~=nil,'Missing current-level beam summary')
   local _,count=string.gsub(text,'FULL%-POWER LIMITS','')
   check(count==1,'Stats repeated as individual sound properties')
   check(string.find(text,'Sound styles change audio, not damage or range.',1,true)~=nil,'Sound/level distinction missing')
   local stats=Combat.Stats(level,1,false)
   check(string.find(text,string.format('%.1f DPS · %.2f studs',stats.maxDps,stats.maxRange),1,true)~=nil,'Summary does not match authoritative caps')
   check(string.find(text,'5s cooldown after stopping',1,true)~=nil,'UI cooldown differs from approved five seconds')
  end
 end
end
draw({level=100,sound='one'},false,nil)
check(string.find(table.concat(messages,'\\n'),'28 damage',1,true)~=nil,'Legacy damage mislabeled DPS')
-- Actual adapter/protocol: resolved range, amplified power and integer damage.
for _,level in ipairs({1,10,50,100}) do
 for _,power in ipairs({.08,.5,1}) do
  for _,amp in ipairs({false,true}) do
   local context={origin=0,character={},level=level,amplifier=amp}
   local s=Adapter.New();check(Adapter.Begin(s,0,{sequence=1,aim=10,power=power},context),'Start failed')
   local stats=Combat.Stats(level,power,amp);local total=0
   for tick=1,20 do
    local now=tick*.2
    if tick<20 then check(Adapter.Pulse(s,now,{sequence=1,sample=tick,aim=10,power=power},context),'Pulse failed')end
    local hits=Adapter.Step(s,now,context,function(_,_,actual)
     check(near(actual.range,stats.range),'Resolved range differs from shared stats')
     return {'target'},{}
    end)
    for _,hit in hits do total+=hit.damage end
   end
   check(total==math.floor(stats.maxDps*(.45+.55*stats.power)*4+1e-7),'Damage budget differs from displayed full-power cap')
   check(near(s.protocol.nextStart,9),'Full attack does not end in five-second cooldown')
   check(not Adapter.Begin(s,8.999,{sequence=2,aim=10,power=power},context),'Early restart accepted')
   check(Adapter.Begin(s,9,{sequence=3,aim=10,power=power},context),'Exact five-second restart rejected')
  end
 end
end
local p={UserId=1,attrs={},SetAttribute=function(self,key,value)self.attrs[key]=value end}
local effect={FireAllClients=function()end};local workspace={GetServerTimeNow=function()return 100 end}
'''
tail = '''
sustainedEnd(p,{nextStart=9},4)
check(p.attrs.SustainedReadyAt==105 and p.attrs.SustainedActive==false,'Server deadline replication wrong')
local function fill(voiceCooldown)
 local voiceActive=false;local sustainedRules=Attack;local voiceTimeFill={};local serverNow=100
'''+bar+'''
 return voiceTimeFill.Size.X
end
check(near(fill(5),0) and near(fill(2.5),.5) and near(fill(0),1),'UI cooldown bar denominator incorrect')
print('PASS '..checks..' actual renderer/adapter/deadline checks; synthetic UI/timing, no native or network evidence')
'''
def run(code,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',encoding='utf-8',delete=False) as f:
  path=Path(f.name);f.write(code)
 try:
  r=subprocess.run(['luau',str(path)],capture_output=True,text=True,encoding='utf-8');out=r.stdout+r.stderr
  if expected:
   assert r.returncode and expected in out,out
   print('PASS negative control:',expected)
  else:
   print(out,end='');assert r.returncode==0,out
 finally:path.unlink()
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--negative-controls',action='store_true');args=parser.parse_args()
 code=setup+render+checks+endfn+tail
 run(code)
 if args.negative_controls:
  run(code.replace('local checks=0','Attack.Cooldown=10\nlocal checks=0',1),'UI cooldown differs from approved five seconds')
  run(code.replace('local checks=0','local originalBegin=Attack.Begin;Attack.Begin=function(s,now,...)s.nextStart=0;return originalBegin(s,now,...)end\nlocal checks=0',1),'Early restart accepted')
  run(code.replace('maximum.maxRange','maximum.maxRange+1'),'Summary does not match authoritative caps')
  run(code.replace('voiceCooldown/sustainedRules.Cooldown','voiceCooldown/10'),'UI cooldown bar denominator incorrect')
