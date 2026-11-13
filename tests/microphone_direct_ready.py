"""Actual Microphone and Controls with fake audio/time; actual Client frame fragments. No hardware claim."""
from pathlib import Path
import subprocess,tempfile,sys
R=Path(__file__).resolve().parents[1]
m=(R/'src/StarterPlayer/StarterPlayerScripts/Microphone.luau').read_text()
c=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
old=(R/'tests/microphone_lifecycle.py').read_text()
setup=old.split("setup = r'''",1)[1].split("'''",1)[0]
epoch=c[c.index(' local micInterruption='):c.index(' if reportedReady~=')]
observe=next(x for x in c.splitlines() if 'sustainedControl:ObserveAvailability(' in x)
checks=r'''
end
local Mic=loadMicrophone();local count=0
local function check(x,message)assert(x,message);count+=1 end
local mic=Mic.new();mic:Step(.05)
check(mic.ready and not mic.model.calibrated,'Live input requires calibration')
check(mic.model.floor==.003 and mic.model.ceiling==.06,'Default thresholds changed')
local sends={};local gate=Gate.new()
local sustainedControl=Controls.new(gate,function(verb,value)table.insert(sends,{verb,value})end,function()return 1 end)
local observedMicInterruption=0;local alive=true;local data={voiceEligible=true}
local lockController=nil;local captureSource=nil
local action={FireServer=function(_,verb)table.insert(sends,{verb})end}
__CANCEL__
local function frame()
__EPOCH__
if sustainedControl then __OBSERVE__ end
end
frame();check(not sustainedControl.armed,'First readiness autoarmed')
sustainedControl:Step(.1,now,1,true,true,false,nil)
check(#sends==0,'Default OFF sent an attack')
local function armActive()
 sustainedControl:SetArmed(true);sustainedControl.attack={sequence=7};gate.active=true;mic.captureStarted=now
end
for _,kind in ipairs({'input','analyzer','wire','mute','inactive','invalid'})do
 armActive();local before=#sends;local revision=mic.interruptionEpoch
 if kind=='input'then player.input.Parent=nil;player.input={Parent=true,Muted=false,Active=true}
 elseif kind=='analyzer'then mic.analyzer.Parent=nil
 elseif kind=='wire'then mic.wire.Parent=nil
 elseif kind=='mute'then player.input.Muted=true
 elseif kind=='inactive'then player.input.Active=false
 else mic.analyzer.RmsLevel=0/0 end
 mic:Step(.05)
 check(mic.interruptionEpoch>revision,'Loss epoch missing '..kind)
 frame();check(not sustainedControl.armed and not sustainedControl.attack,'Loss did not disarm '..kind)
 check(#sends==before+1 and sends[#sends][1]=='SustainedStop','Loss stop not exactly once '..kind)
 check(gate.needsQuiet and gate.quiet==0,'Loss retained quiet rearm '..kind)
 player.input.Muted=false;player.input.Active=true;mic.analyzer.RmsLevel=0
 mic:Step(.05);frame();check(mic.ready and not sustainedControl.armed,'Recovery autoarmed '..kind)
 frame();check(#sends==before+1,'Repeated interruption amplified stops '..kind)
end
for _,rms in ipairs({-1,math.huge,0/0})do
 mic.analyzer.RmsLevel=rms;mic:Step(.05);check(not mic.ready and mic.power==0,'Invalid RMS ready')
 mic.analyzer.RmsLevel=0;mic:Step(.05);check(mic.ready,'Finite silence not ready')
end
player.input.Muted=true;check(not mic:Begin(),'Muted direct capture admitted');player.input.Muted=false;mic:Step(.05)
player.input.Active=false;check(not mic:Begin(),'Inactive direct capture admitted');player.input.Active=true;mic:Step(.05)
-- An accepted synchronous Check can hide its temporary unavailable state within one frame.
now=3;frame();armActive();local beforeCheck=#sends;local epochBefore=mic.interruptionEpoch
mic:Check();mic:Step(.05);frame()
check(mic.ready and not sustainedControl.armed and #sends==beforeCheck+1,'Fast Check recovery retained armed attack')
check(mic.interruptionEpoch==epochBefore+1,'Check interruption missing')
-- Actual legacy cancelCapture must not amplify an unplugged loss across polling frames.
local controller=sustainedControl;sustainedControl=nil;captureSource='keyboard'
local beforeLoss=#sends;player.input.Parent=nil;player.input=nil
for _=1,120 do mic:Step(.05);frame()end
check(#sends==beforeLoss+1 and sends[#sends][1]=='CancelCast','Unplugged legacy loss amplified cancellation')
check(not mic.ready and mic.input==nil and mic.analyzer==nil and mic.wire==nil,'Missing input retained graph')
local afterLoss=mic.interruptionEpoch
player.input={Parent=true,Muted=false,Active=true};mic:Step(.05);frame()
check(mic.ready and mic.model.floor==.003 and mic.model.ceiling==.06,'Replacement lost default readiness')
check(mic.interruptionEpoch==afterLoss,'Recovery fabricated another loss')
player.input.Parent=nil;player.input=nil;mic:Step(.05);frame()
check(#sends==beforeLoss+2,'Second loss episode was not distinct')
player.input={Parent=true,Muted=false,Active=true};mic:Step(.05);sustainedControl=controller;frame()
-- Error retry uses same actual bounded Check; pending clicks create no extra jobs.
now=6;deferCheck=true;voice.IsVoiceEnabledForUserIdAsync=function()error('synthetic unavailable')end
mic:Check();for _=1,120 do mic:Check()end
check(#pending==1 and mic.checkPending,'Retry queued concurrent access work')
pending[1]();table.clear(pending);check(not mic.eligible and not mic.ready,'Failed access ready')
mic:Check();check(#pending==0,'Immediate retry bypassed cooldown')
now=8;voice.IsVoiceEnabledForUserIdAsync=function()return true end;mic:Check();check(#pending==1,'Access retry unavailable')
pending[1]();table.clear(pending);mic:Step(.05);frame();check(mic.ready and not sustainedControl.armed,'Retry recovery autoarmed')
local allocated=#instances;mic:Destroy();mic:Destroy();mic:Step(.1);mic:Check()
check(disconnected and #instances==allocated and #pending==0 and not mic.ready,'Teardown created work')
print('PASS '..count..' direct-ready actual-module/Client-fragment assertions')
'''
def build(ms=m,cs=c):
 ep=cs[cs.index(' local micInterruption='):cs.index(' if reportedReady~=')]
 ob=next(x for x in cs.splitlines() if 'sustainedControl:ObserveAvailability(' in x)
 cancel=cs[cs.index('local function cancelCapture()'):cs.index('local function blocked()')]
 return setup+ms+'\n'+checks.replace('__EPOCH__',ep).replace('__OBSERVE__',ob).replace('__CANCEL__',cancel)
def run(code):
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(code);path=Path(f.name)
 try:return subprocess.run(['luau',str(path)],capture_output=True,text=True,timeout=15)
 finally:path.unlink()
if '--baseline' in sys.argv:
 historical=subprocess.check_output(['git','show','53d6213:src/StarterPlayer/StarterPlayerScripts/Microphone.luau'],text=True)
 out=run(build(historical,c));assert out.returncode and 'Live input requires calibration' in out.stderr,out.stderr
 print('PASS pinned historical actual-Microphone reproduction: live input requires calibration');sys.exit(0)
out=run(build());print(out.stdout,end='');assert out.returncode==0,out.stderr
assert 'micPanel' not in c and 'FirstBeamGuide' not in c and ':Calibrate()' not in c
assert 'RETRY VOICE ACCESS' in c and 'normal speech can attack' in c and 'VOICE SAFETY' in c
assert 'micStatus=mic.status' in c
print('PASS 3 no-wall/status source contracts')
if '--negative-controls' in sys.argv:
 controls=[(m.replace('else self.ready=true;', 'elseif self.model.calibrated then self.ready=true;'),c,'Live input requires calibration'),(m,c.replace('data.voiceEligible==true,false)','data.voiceEligible==true,true)'),'First readiness autoarmed'),(m.replace('self.interruptionEpoch+=1','self.interruptionEpoch+=0'),c,'Loss epoch missing'),(m,c.replace('observedMicInterruption=micInterruption\n  if sustainedControl then sustainedControl:SetArmed(false) end','observedMicInterruption=micInterruption'),'Loss did not disarm')]
 controls.extend([(m.replace(' self:Interrupt()\n self.generation+=1',' self.generation+=1'),c,'Fast Check recovery retained armed attack'),(m.replace(' self.input=nil\n self:Cancel();',' self:Cancel();'),c,'Unplugged legacy loss amplified cancellation')])
 for ms,cs,message in controls:
  out=run(build(ms,cs));assert out.returncode and message in out.stderr,(message,out.stdout,out.stderr)
 print('PASS 6 direct-ready negative controls')
