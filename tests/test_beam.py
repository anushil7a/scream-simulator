"""Actual visual-only TestBeam module with synthetic vectors/character/server clock.
No native rendering, audio, real microphone, saves or gameplay damage are established.
"""
from pathlib import Path
import subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
pre=r'''
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local Combat=require('../src/ReplicatedStorage/Shared/VoiceCombat')
local V={};local mt={}
function V.new(x,y,z)return setmetatable({X=x,Y=y,Z=z},mt)end
mt.__sub=function(a,b)return V.new(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
mt.__add=function(a,b)return V.new(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
mt.__mul=function(a,b)return V.new(a.X*b,a.Y*b,a.Z*b)end
mt.__index=function(a,k)if k=='Magnitude'then return math.sqrt(a.X*a.X+a.Y*a.Y+a.Z*a.Z)elseif k=='Unit'then return a*(1/a.Magnitude)end end
local Vector3=V;local typeof=function(v)return type(v)=='table'and getmetatable(v)==mt and 'Vector3'or type(v)end
local studio=true;local flag=true
local game={GameId=0,PlaceId=0,GetService=function()return {IsStudio=function()return studio end}end}
local workspace={GetAttribute=function(_,name)assert(name=='LocalSustainedPrototype');return flag end}
local Aim=(function()
'''
mid=r'''
end)()
local Rules=(function()
'''
post=r'''
end)()
local Beam=Rules.new(Combat,Aim)
local function fresh()
 local c={Parent=true};local r={Parent=c,Position=V.new(0,10,0),Anchored=false,IsA=function(_,kind)return kind=='BasePart'end}
 local h={Parent=c,Health=100};local head={Position=V.new(0,12,0),IsA=r.IsA}
 function c:FindFirstChild(name)if name=='Head'then return head elseif name=='HumanoidRootPart'then return r end end
 function c:FindFirstChildOfClass(name)if name=='Humanoid'then return h end end
 local p={Parent=true,Character=c}
 return p,{data={level=1},testBaseline={},micReady=false,voiceEligibility=false},r,h,head
end
local function req(power)return {power=power,aim=V.new(0,12,-100)}end
local p,s,r,h,head=fresh()
check(Beam.Start(p,s,true,true,0,req(100),1),'Start needs no microphone/capture/eligibility')
local b,ended=Beam.Step(p,s,true,true,0)
check(b and not ended and b.length==30 and b.width==4 and b.power==100,'Actual L1 100% geometry changed')
check(b.origin==head.Position and b.direction.Z==-1,'Server origin/validated direction not used')
local active=s.testBeam
check(not Beam.Start(p,s,true,true,.01,req(100),1)and s.testBeam==active,'Duplicate Begin replaced/reset run')
check(Beam.Stop(s,.1)and s.testBeam==nil and s.testBeamReadyAt==5.1,'Stop did not preserve cooldown')
check(not Beam.Stop(s,100)and s.testBeamReadyAt==5.1,'Repeated stop amplified cooldown')
check(not Beam.Start(p,s,true,true,5,req(100),1),'Cooldown bypass')
check(Beam.Start(p,s,true,true,5.1,req(100),1),'Cooldown never recovered')
Beam.Stop(s,5.1)
for _,mode in ipairs({'auth','studio','game','place','fixture','flag','truthy'})do
 p,s=fresh();studio=mode~='studio';game.GameId=mode=='game'and 1 or 0;game.PlaceId=mode=='place'and 1 or 0;flag=mode~='flag'
 local auth=mode=='truthy'and 1 or mode~='auth'
 check(not Beam.Start(p,s,auth,mode~='fixture',0,req(100),1),'Nonlocal/auth start accepted '..mode)
 check(s.testBeam==nil and not s.testBeamReadyAt,'Denied start mutated test state '..mode)
end
studio=true;game.GameId=0;game.PlaceId=0;flag=true
p,s=fresh();s.testBaseline=nil;check(not Beam.Start(p,s,true,true,0,req(100),1),'Implicit profile test activation')
for _,power in ipairs({-1,101,.5,'100',true,{},math.huge,-math.huge,0/0})do
 p,s=fresh();check(not Beam.Start(p,s,true,true,0,req(power),1),'Invalid power accepted')
end
for _,arg in ipairs({false,true,100,'x',{}, {power=100},{power=100,aim=V.new(0,12,-100),damage=100},
 {power=100,aim=V.new(0,12,0)}, {power=100,aim=V.new(0,12,3000)}, {power=100,aim=V.new(0/0,12,0)},
 {power=100,aim=V.new(0,math.huge,0)}, {power=100,aim={X=0,Y=12,Z=-100}}})do
 p,s=fresh();check(not Beam.Start(p,s,true,true,0,arg,1),'Malformed request accepted')
end
p,s=fresh();check(not Beam.Start(p,s,true,true,0,nil,1),'nil request accepted')
p,s=fresh();check(not Beam.Start(p,s,true,true,0,req(0),1)and s.testBeam==nil and not s.testBeamReadyAt,'Zero start emitted beam/cooldown')
for _,level in ipairs({1,10,50,100})do
 for _,power in ipairs({1,10,50,100})do
  p,s=fresh();s.data.level=level
  check(Beam.Start(p,s,true,true,0,req(power),1.32),'Power/level start')
  b=Beam.Step(p,s,true,true,0)
  local expected=Combat.Stats(level,power/100,false,false,1.32)
  check(math.abs(b.length-expected.range)<1e-8 and b.width==expected.width,'Gear amplified twice or wrong power geometry')
 end
end
p,s=fresh();Beam.Start(p,s,true,true,0,req(50),1)
check(not Beam.Pulse(p,s,true,true,.01,req(100))and s.testBeam.power==50 and s.testBeam.lastPulse==0,'Rate limit refreshed input')
check(Beam.Pulse(p,s,true,true,.1,req(100))and s.testBeam.power==100,'Adjustable pulse rejected')
b=Beam.Step(p,s,true,true,.1);check(b and b.length==30,'Live power not mapped')
check(not Beam.Pulse(p,s,true,true,.2,{power=80,aim=V.new(0,12,-100),width=100}),'Extra pulse field accepted')
check(s.testBeam.lastPulse==.1 and s.testBeam.power==100,'Malformed pulse changed preview')
b,ended=Beam.Step(p,s,true,true,.601);check(not b and ended and not s.testBeam and math.abs(s.testBeamReadyAt-5.6)<1e-8,'Lost focus timeout not bounded')
p,s=fresh();Beam.Start(p,s,true,true,0,req(100),1)
local ok;ok,ended=Beam.Pulse(p,s,true,true,.1,req(0));check(not ok and ended and not s.testBeam,'Zero pulse did not stop')
p,s=fresh();Beam.Start(p,s,true,true,0,req(100),1)
for i=1,39 do
 check(Beam.Pulse(p,s,true,true,i*.1,req(100)),'Continuous pulse rejected')
 b,ended=Beam.Step(p,s,true,true,i*.1);check(b and not ended,'Four-second run ended early')
end
b,ended=Beam.Step(p,s,true,true,4);check(not b and ended and s.testBeamReadyAt==9,'Max duration/cooldown not enforced')
for _,mode in ipairs({'auth','studio','game','place','fixture','flag','baseline','death','respawn','root','humanoid','leave','flight','Sit','SeatPart','PlatformStand','anchored','knock','dodge','clock'})do
 p,s,r,h=fresh();Beam.Start(p,s,true,true,1,req(100),1)
 local now=1.1
 if mode=='studio'then studio=false elseif mode=='game'then game.GameId=1 elseif mode=='place'then game.PlaceId=1 elseif mode=='flag'then flag=false
 elseif mode=='baseline'then s.testBaseline=nil elseif mode=='death'then h.Health=0 elseif mode=='respawn'then p.Character=nil
 elseif mode=='root'then r.Parent=nil elseif mode=='humanoid'then h.Parent=nil elseif mode=='leave'then p.Parent=nil
 elseif mode=='flight'then s.flight={} elseif mode=='anchored'then r.Anchored=true elseif mode=='knock'then s.knockedUntil=2
 elseif mode=='dodge'then s.dodgingUntil=2 elseif mode=='clock'then now=.9 elseif mode=='Sit'or mode=='SeatPart'or mode=='PlatformStand'then h[mode]=true end
 b,ended=Beam.Step(p,s,mode~='auth',mode~='fixture',now)
 check(not b and ended and not s.testBeam,'Lifecycle guard failed '..mode)
 studio=true;game.GameId=0;game.PlaceId=0;flag=true
end
for _,mode in ipairs({'flight','dead','anchored','Sit','SeatPart','PlatformStand','knock','dodge'})do
 p,s,r,h=fresh()
 if mode=='flight'then s.flight={} elseif mode=='dead'then h.Health=0 elseif mode=='anchored'then r.Anchored=true
 elseif mode=='knock'then s.knockedUntil=1 elseif mode=='dodge'then s.dodgingUntil=1 else h[mode]=true end
 check(not Beam.Start(p,s,true,true,0,req(100),1),'Unsafe character start '..mode)
end
print('PASS '..checks..' actual silent TestBeam guard/power/timing/lifecycle assertions; synthetic engine only')
'''
server=(ROOT/'src/ServerScriptService/Bootstrap.server.luau').read_text()
end_helper=server[server.index('local function testBeamEnd('):server.index('local function cancelSustained(')]
dispatcher=server[server.index('action.OnServerEvent:Connect(function'):server.index('\nlocal function joined(p)')]
integration_pre=r'''
local TestBeamRules=Rules;local testBeam=Beam
local RunService=game:GetService("RunService")
local now=0;local os={clock=function()return now end}
local localFixture=true;local auth=true;local busy=false;local sanitized=0
local Access={IsAuthorized=function()return auth end}
local Commerce={Busy=function()return busy end}
local Config={Gear={Multiplier=function()return 1.32 end}}
local function copy(t)local out={};for k,v in pairs(t)do out[k]=type(v)=='table'and copy(v)or v end;return out end
local Profiles={Sanitize=function(t)sanitized+=1;return copy(t)end}
local events={};local effect={FireAllClients=function(_,...)table.insert(events,{...})end}
local states={};local function state(p,message)table.insert(states,{p,message})end
local cancels=0;local function cancelSustained()cancels+=1 end
local VoiceCombat={Cancel=function(v)v.capture=nil end}
local sessions={};local dispatch
local action={OnServerEvent={Connect=function(_,fn)dispatch=fn end}}
local function freshDispatch()
 local p,s,r,h=fresh();p.UserId=42;p.attributes={};function p:SetAttribute(k,v)self.attributes[k]=v end
 s.testBaseline=nil;s.data={level=10,coins=123,quests={garden={progress=1}}};s.voice={capture={}};s.nextAction=100;s.micReady=true
 sessions[p]=s;now=0;sanitized=0;events={};states={};cancels=0
 return p,s,r,h
end
'''
integration_checks=r'''
for _,mode in ipairs({'auth','studio','game','place','flag','fixture','flight','busy'})do
 local p,s=freshDispatch();auth=mode~='auth';studio=mode~='studio';game.GameId=mode=='game'and 1 or 0;game.PlaceId=mode=='place'and 1 or 0
 flag=mode~='flag';localFixture=mode~='fixture';busy=mode=='busy';if mode=='flight'then s.flight={}end
 dispatch(p,'TestBeamBegin',req(100))
 check(not s.testBeam and not s.testBaseline and sanitized==0,'Dispatcher guard mutated data '..mode)
end
auth=true;studio=true;game.GameId=0;game.PlaceId=0;flag=true;localFixture=true;busy=false
for _,arg in ipairs({req(0),req(-1),req(101),req(.1),{power=100,aim=V.new(0,12,-100),damage=100},{power=100,aim=V.new(math.huge,0,0)}})do
 local p,s=freshDispatch();dispatch(p,'TestBeamBegin',arg)
 check(not s.testBeam and not s.testBaseline and sanitized==0,'Invalid/0 Begin took profile snapshot')
end
local p,s=freshDispatch();local original=s.data
-- Deliberately no mic readiness or voice eligibility is needed by this separate path.
s.micReady=false;dispatch(p,'TestBeamBegin',req(100))
check(s.testBeam and s.testBaseline and sanitized==2,'Accepted Begin did not isolate exactly once')
check(s.testBaseline~=s.data and original~=s.data and s.testBaseline.quests~=s.data.quests,'Profile snapshot aliases temporary data')
check(s.testBeam.power==100 and s.testBeam.level==10 and s.voice.capture==nil and cancels==1 and s.micReady==false,'Begin bypass/cancellation changed readiness')
check(s.data.coins==123 and s.data.level==10 and s.data.quests.garden.progress==1,'Visual test granted gameplay progress')
s.data.quests.garden.progress=5;check(s.testBaseline.quests.garden.progress==1,'Temporary progression leaked into baseline')
dispatch(p,'TestBeamBegin',req(50));check(sanitized==2 and s.testBeam.power==100,'Duplicate Begin replaced preview or baseline')
now=.1;dispatch(p,'TestBeamPulse',req(50));check(s.testBeam.power==50,'Action pulse did not adjust preview')
for i=1,30 do dispatch(p,'TestBeamPulse',req(50))end
local last=s.testBeam.lastPulse;now=.2;dispatch(p,'TestBeamPulse',req(100));check(s.testBeam.lastPulse==last and s.testBeam.power==50,'Quota-saturated pulse refreshed input')
s.sprintRequested=true;dispatch(p,'Sprint',false);check(s.sprintRequested==false,'Preview guard swallowed release')
local held=s.testBeam;dispatch(p,'SustainedBegin',{sequence=1,power=1,aim=V.new(0,0,-10)})
check(s.testBeam==held,'Preview input entered normal voice path')
dispatch(p,'TestBeamStop',{});check(s.testBeam==held,'Malformed Stop ended preview')
dispatch(p,'TestBeamStop',nil);check(not s.testBeam and #events==1 and events[1][1]=='TestBeamEnd','Saturated Stop did not clear once via silent event')
local ready=s.testBeamReadyAt;local stateCount=#states
for i=1,100 do dispatch(p,'TestBeamStop',nil)end
check(#events==1 and #states==stateCount and s.testBeamReadyAt==ready,'Repeated Stop amplified output/cooldown')
now=1.1;dispatch(p,'TestBeamBegin',req(100));check(not s.testBeam and sanitized==2,'New window bypassed cooldown')
now=ready;dispatch(p,'TestBeamBegin',req(100));check(s.testBeam and sanitized==2,'Cooldown failed or recaptured baseline')
-- Stops only affect their own live session, even when another player is running a test.
local first=p;local firstState=s;local second,secondState=freshDispatch();second.UserId=43
dispatch(second,'TestBeamBegin',req(100));dispatch(first,'TestBeamStop',nil)
check(not firstState.testBeam and secondState.testBeam,'Stop crossed player boundary')
-- An ordinary ready microphone is preserved rather than permanently disabled.
p,s=freshDispatch();dispatch(p,'TestBeamBegin',req(100));check(s.micReady==true,'Preview changed ordinary microphone readiness')
print('PASS '..checks..' total module + actual Action dispatcher preview assertions; synthetic only')
'''
code=pre+(ROOT/'src/ServerScriptService/SustainedAim.luau').read_text()+mid+(ROOT/'src/ServerScriptService/TestBeam.luau').read_text()+post+integration_pre+end_helper+dispatcher+integration_checks
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=ROOT/'tests',delete=False)as f:
 path=Path(f.name);f.write(code)
try:subprocess.run(['luau',str(path)],cwd=ROOT,check=True)
finally:path.unlink()
