"""Actual microphone controller with fake audio instances, time and eligibility.
No AudioDeviceInput, hardware, voice transport or Roblox scheduling is exercised.
"""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'src/StarterPlayer/StarterPlayerScripts/Microphone.luau').read_text()
setup = r'''
local Power=require('../src/ReplicatedStorage/Shared/MicPower')
local Gate=require('../src/ReplicatedStorage/Shared/VoiceActivation')
local Controls=require('../src/StarterPlayer/StarterPlayerScripts/SustainedControls')
local now=0
local os={clock=function()return now end}
local pending={};local timeouts={};local deferCheck=false
local task={delay=function(_,fn)table.insert(timeouts,fn)end,spawn=function(fn) if deferCheck then table.insert(pending,fn) else fn() end end}
local disconnected=false
local run={Heartbeat={Connect=function(_,fn)return {Disconnect=function()disconnected=true end}end}}
local player={UserId=1,input={Parent=true,Muted=false,Active=true}}
function player:FindFirstChildWhichIsA()return self.input end
local players={LocalPlayer=player}
local voice={IsVoiceEnabledForUserIdAsync=function()return true end}
local shared={WaitForChild=function()return 'power'end}
local game={GetService=function(_,name)
 return ({Players=players,VoiceChatService=voice,RunService=run,ReplicatedStorage={WaitForChild=function()return shared end}})[name]
end}
local instances={}
local Instance={new=function(kind)
 local obj={kind=kind,RmsLevel=0}
 function obj:Destroy()self.destroyed=true;self.Parent=nil end
 table.insert(instances,obj);return obj
end}
local require=function(name)assert(name=='power');return Power end
local function loadMicrophone()
'''
checks = r'''
end
local Mic=loadMicrophone();local checks=0
local function check(value,message)assert(value,message);checks+=1 end
local m=Mic.new();m:Step(.05)
check(m.eligible and not m.ready and m.analyzer~=nil,'Ready before calibration or no analyzer')
local function samples(phase,rms)
 local count=0
 while m.phase==phase and count<100 do
  now+=.05;m.analyzer.RmsLevel=rms;m:Step(.05);count+=1
 end
 check(count<100,'Calibration phase failed to finish')
end
m:Calibrate();samples('quiet',.001);samples('voice',.08)
check(m.ready and m.model.calibrated,'Valid live sample calibration failed')
check(m:Begin(),'Expired-capture fixture failed to start');now+=8.01
local expiredPower,expiredNotice=m:Release()
check(expiredPower==0 and expiredNotice=='Capture expired. Start a new live beam.','Expired legacy capture has stale attack wording')
check(m:Begin(),'Mute calibration fixture did not begin capture')
player.input.Muted=true;m:Calibrate()
check(not m.ready and m.power==0 and m.captureStarted==nil,'Calibrate on muted input retained readiness until next heartbeat')
check(not m:Begin(),'Muted calibration allowed a new capture before heartbeat')
m:Step(.05)
check(not m.ready and m.power==0 and m.captureStarted==nil,'Mute retained readiness or energy')
player.input.Muted=false;m:Step(.05)
check(m.ready,'Unmuting lost valid calibration')
m:Calibrate();samples('quiet',.001);samples('voice',.001)
check(not m.ready and not m.model.calibrated,'Failed recalibration reused previous calibration')
m:Calibrate();samples('quiet',.001);samples('voice',.08)
for _,invalid in ipairs({0/0,math.huge,-.01}) do
 check(m:Begin(),'Invalid-signal fixture did not begin capture')
 m.analyzer.RmsLevel=invalid;m:Step(.05)
 check(not m.ready and m.power==0 and m.captureStarted==nil,'Invalid signal retained microphone readiness or capture')
 check(m.status=='Microphone signal unavailable. Check your input.','Invalid signal claimed live readiness')
 m.analyzer.RmsLevel=0;m:Step(.05)
 check(m.ready and m.model.calibrated,'Valid silence did not restore calibrated availability')
end
m:Calibrate();m.analyzer.RmsLevel=0/0;m:Step(.05)
check(m.phase==nil and not m.ready and #m.quiet==0 and #m.spoken==0,'Invalid signal retained partial calibration')
m.analyzer.RmsLevel=.001;m:Step(.05)
check(not m.ready,'Valid signal bypassed interrupted calibration')
check(m.status=='Microphone signal restored. Calibrate before attacking.','Signal recovery omitted fresh calibration guidance')
m:Calibrate();samples('quiet',.001);samples('voice',.08)
local old=m.analyzer
player.input.Parent=nil;player.input={Parent=true,Muted=false,Active=true};m:Step(.05)
check(old.destroyed and m.analyzer~=old and not m.ready and not m.model.calibrated,'Input replacement retained analyzer/calibration')
m:Calibrate();samples('quiet',.001);samples('voice',.08)
check(m:Begin(),'Legacy capture did not start after replacement calibration')
now+=.3;player.input.Muted=true;m:Step(.05)
check(m:Release()==0,'Muted capture returned stale energy')
player.input.Muted=false
for _,phase in ipairs({'quiet','voice'})do
 m:Calibrate()
 if phase=='voice' then samples('quiet',.001) end
 now+=.05;m.analyzer.RmsLevel=.08;m:Step(.05)
 player.input.Muted=true;m:Step(.05)
 check(m.phase==nil and #m.quiet==0 and #m.spoken==0,'Mute retained partial '..phase..' calibration')
 player.input.Muted=false;m:Step(.05)
 check(not m.ready and not m.model.calibrated,'Unmute completed interrupted '..phase..' calibration')
 check(m.status=='Microphone unmuted. Calibrate before attacking.','Interrupted calibration retained muted status after unmute')
end
m:Calibrate();samples('quiet',.001)
local disconnectedAnalyzer=m.analyzer
player.input.Parent=nil;player.input=nil;m:Step(.05)
check(m.phase==nil and #m.quiet==0 and #m.spoken==0 and not m.ready,'Disconnected input retained calibration samples')
check(disconnectedAnalyzer.destroyed and m.analyzer==nil,'Disconnect retained old analyzer')
player.input={Parent=true,Muted=false,Active=true};m:Step(.05)
check(not m.model.calibrated and not m.ready,'Reconnected input inherited calibration')
m:Calibrate();samples('quiet',.001);samples('voice',.08)
check(m.ready,'Fresh calibration after interrupted input failed')
local lostAnalyzer=m.analyzer
check(m:Begin(),'Analyzer-loss fixture could not begin capture')
lostAnalyzer:Destroy();m:Step(.05)
check(m.analyzer~=lostAnalyzer and m.analyzer.Parent==player,'Removed analyzer was not rebuilt')
check(not m.ready and not m.model.calibrated and m.captureStarted==nil and m.power==0,'Analyzer loss retained readiness or captured energy')
check(m.status=='Microphone input found. Calibrate before attacking.','Analyzer recovery retained stale readiness text')
check(m:Release()==0,'Analyzer loss released a stale capture')
m:Calibrate();samples('quiet',.001);samples('voice',.08)
check(m.ready,'Fresh calibration after analyzer replacement failed')
for _,breakLink in ipairs({
 function(wire)wire.Parent=nil end,
 function(wire)wire.SourceInstance={} end,
 function(wire)wire.TargetInstance={} end,
}) do
 local oldWire=instances[#instances];local oldMeter=m.analyzer
 check(m:Begin(),'Broken-wire fixture could not begin capture')
 breakLink(oldWire);m:Step(.05)
 check(m.analyzer~=oldMeter and oldMeter.destroyed,'Broken wire retained old meter')
 local wire=instances[#instances]
 check(wire.SourceInstance==player.input and wire.TargetInstance==m.analyzer and wire.Parent==m.analyzer,'Replacement wire endpoints invalid')
 check(oldWire.destroyed,'Detached old wire was not cleaned up')
 check(not m.ready and not m.model.calibrated and m.captureStarted==nil,'Broken wire retained capture readiness')
 check(m.status=='Microphone input found. Calibrate before attacking.','Wire recovery omitted calibration guidance')
 m:Calibrate();samples('quiet',.001);samples('voice',.08)
 check(m.ready,'Fresh calibration after wire repair failed')
end
local packets={}
local controls=Controls.new(Gate.new(),function(verb,arg)table.insert(packets,{verb,arg})end,function()return 1 end)
local function frames(n,rms)
 for _=1,n do
  now+=.05;m.analyzer.RmsLevel=rms;m:Step(.05)
  controls:ObserveAvailability(m.ready,true)
  local attack=controls.attack
  controls:Step(.05,now,m.power,true,true,attack~=nil,attack and attack.sequence)
 end
end
frames(15,0);frames(15,.08)
check(controls.attack~=nil and controls.attack.acknowledged,'Integrated mic/controller fixture did not start acknowledged attack')
frames(1,0/0)
check(not m.ready and not controls.armed and not controls.attack and packets[#packets][1]=='SustainedStop','Invalid microphone signal did not stop automatic attack')
local stopped=#packets
frames(5,math.huge)
check(#packets==stopped,'Continuing signal outage duplicated stop or sent pulses')
frames(20,.08);frames(15,0);frames(15,.08)
check(m.ready and not controls.armed and #packets==stopped,'Recovered microphone silently rearmed attack')
controls:SetArmed(true);frames(15,.08)
check(#packets==stopped,'Explicit resume bypassed quiet gate with held voice')
frames(15,0);frames(15,.08)
check(controls.attack and controls.attack.sequence==2 and controls.attack.acknowledged,'Fresh quiet and voice failed to recover attack')
controls:Destroy()
check(not controls.attack and packets[#packets][1]=='SustainedStop','Integrated controller cleanup left attack running')
local analyzer=m.analyzer;m.ready=true;m.power=1;m:Destroy()
check(disconnected and analyzer.destroyed,'Destroy leaked heartbeat/analyzer')
check(not m.ready and not m.eligible and m.power==0 and m.captureStarted==nil,'Destroyed microphone retained attack readiness')
local instanceCount=#instances
m:Step(.05);m:Check();m:Calibrate();m:Destroy()
check(#instances==instanceCount and m.analyzer==nil and m.input==nil,'Late callback recreated destroyed microphone resources')
check(not m:Begin() and m:FindInput()==nil and m:Release()==0,'Destroyed microphone accepted a new capture')
check(not m.model.calibrated and m.phase==nil,'Destroyed microphone retained calibration')
deferCheck=true
local late=Mic.new();local beforePendingCalibration=#instances
late:Calibrate()
check(late.status=='Checking Roblox voice access…' and late.checkPending,'Calibration replaced pending access guidance')
check(#instances==beforePendingCalibration and late.input==nil and late.phase==nil,'Pending access calibration created audio resources or started sampling')
late:Destroy()
for _,fn in ipairs(pending) do fn() end
check(not late.eligible,'Late eligibility check revived destroyed controller')
-- Simulate yielded access checks finishing out of order.
pending={};local racing=Mic.new();racing:Check()
check(#pending==2,'Retry did not create two pending checks')
voice.IsVoiceEnabledForUserIdAsync=function()return true end
pending[2]()
check(racing.eligible and not racing.checkPending,'Latest successful access result missing')
voice.IsVoiceEnabledForUserIdAsync=function()return false end
pending[1]()
check(racing.eligible,'Stale failed access check overwrote newest success')
pending={};racing:Check()
voice.IsVoiceEnabledForUserIdAsync=function()error('offline') end
pending[1]()
check(not racing.eligible and not racing.ready and not racing.checkPending,'Access error retained readiness')
racing:Destroy()
pending={};timeouts={}
local timed=Mic.new();local oldTimeout=timeouts[1]
timed:Check();oldTimeout()
check(timed.checkPending and timed.status=='Checking Roblox voice access…','Stale timeout changed newer retry status')
timeouts[2]()
check(timed.checkPending and not timed.ready and string.find(timed.status,'timed out',1,true),'Current timeout lacked retry guidance or allowed attacks')
voice.IsVoiceEnabledForUserIdAsync=function()return true end
pending[2]()
check(timed.eligible and not timed.checkPending,'Successful result after timeout failed to recover access')
local status=timed.status;timeouts[2]();oldTimeout()
check(timed.status==status and timed.eligible,'Late timeout overwrote completed success')
timed:Check();local afterDestroy=timeouts[#timeouts];timed:Destroy();status=timed.status;afterDestroy()
check(timed.status==status and not timed.eligible and not timed.ready,'Timeout changed destroyed controller')
print('PASS '..checks..' actual microphone lifecycle checks with mocked audio/time; no device evidence')
'''
with tempfile.NamedTemporaryFile(mode='w', suffix='.luau', prefix='.mic_', dir=root / 'tests', delete=False) as file:
    path = Path(file.name)
    file.write(setup + source + checks)
try:
    subprocess.run(['luau', str(path)], cwd=root, check=True)
finally:
    path.unlink()
