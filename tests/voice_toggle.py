"""Actual voice toggle helper with mocked availability; no UI/device evidence."""
from pathlib import Path
import subprocess
import sys
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text();a=s.index('local function toggleVoice()');b=s.index('local function releaseCapture(',a)
respawn_line=next(line for line in s.splitlines() if line.startswith('connectClient(p.CharacterRemoving,function() hitFeedback:DiscardThrough'))
setup='''
local unavailable=false;local windowFocused=true
local blocked=function()return unavailable end
local calls=0;local sustainedControl={armed=false}
function sustainedControl:SetArmed(v)self.armed=v;calls+=1 end
local notices={};local function notify(message)table.insert(notices,message)end
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
toggleVoice();check(sustainedControl.armed and calls==1,'Available gameplay could not arm')
unavailable=true;toggleVoice();check(not sustainedControl.armed and calls==2,'Unavailable gameplay prevented pause')
toggleVoice();check(not sustainedControl.armed and calls==2,'Menu/protection/mic block allowed hidden arming')
unavailable=false;windowFocused=false;toggleVoice();check(not sustainedControl.armed and calls==2,'Unfocused toggle armed voice')
windowFocused=true;toggleVoice();check(sustainedControl.armed and calls==3,'Fresh available action did not arm')
windowFocused=false;toggleVoice();check(not sustainedControl.armed and calls==4,'Unfocused pause was rejected')
sustainedControl=nil;toggleVoice();check(calls==4,'Legacy mode attempted automatic toggle')
for _,touch in ipairs({false,true}) do
 check(string.find(screamToggleLabel(true,touch),'SCREAMS: ON',1,true)~=nil,'Missing explicit ON status')
 check(string.find(screamToggleLabel(false,touch),'SCREAMS: OFF',1,true)~=nil,'Missing explicit OFF status')
 check(string.find(screamToggleLabel(false,touch),touch and 'Tap to turn on' or '[E] to turn on',1,true)~=nil,'Missing toggle action hint')
end
check(string.find(notices[#notices],'Voice chat is unchanged',1,true)~=nil,'Pause notice implies voice mute')
-- Use the actual toggle helper, controller, gate and server adapter together.
local Gate=require('../src/ReplicatedStorage/Shared/VoiceActivation')
local Controls=require('../src/StarterPlayer/StarterPlayerScripts/SustainedControls')
local Adapter=require('../src/ServerScriptService/SustainedAttackAdapter')
local api=Adapter.new(require('../src/ReplicatedStorage/Shared/SustainedAttack'),require('../src/ReplicatedStorage/Shared/VoiceCombat'),function()return 1 end)
local server=api.New();local now=0;local sent={};local mic={ready=true,power=0}
local context={origin=0,character={},level=1,amplifier=false}
sustainedControl=Controls.new(Gate.new(),function(verb,arg)
 table.insert(sent,verb)
 if verb=='SustainedBegin' then api.Begin(server,now,arg,context)
 elseif verb=='SustainedPulse' then api.Pulse(server,now,arg,context)
 elseif verb=='SustainedStop' then api.Stop(server,now,arg) end
end,function()return 20 end)
local function advance(seconds,power)
 mic.power=power
 for _=1,math.floor(seconds/.05+.5) do
  now+=.05;local active=server.protocol.active
  sustainedControl:Step(.05,now,mic.power,true,now>=server.protocol.nextStart,active~=nil,active and active.sequence)
  api.Step(server,now,context,function()return {},{} end)
 end
end
windowFocused=true;sustainedControl:ObserveAvailability(true)
advance(.4,0);advance(.4,.8)
check(server.protocol.active~=nil,'Toggle fixture did not start an attack')
toggleVoice()
check(not sustainedControl.armed and not sustainedControl.attack and not server.protocol.active and sent[#sent]=='SustainedStop','OFF did not explicitly stop the active attack')
check(mic.ready and mic.power==.8,'OFF changed microphone readiness or input')
local readyAt=server.protocol.nextStart;local pausedCount=#sent
check(readyAt>now,'OFF bypassed cooldown')
advance(.4,0);advance(.4,.8)
check(#sent==pausedCount,'OFF emitted combat messages')
toggleVoice();advance(.4,0);advance(.4,.8)
check(not server.protocol.active and #sent==pausedCount and server.protocol.nextStart==readyAt,'ON bypassed cooldown')
toggleVoice();sustainedControl:ObserveAvailability(false);sustainedControl:ObserveAvailability(true)
advance(11,0);advance(.4,.8)
check(not sustainedControl.armed and #sent==pausedCount,'Availability/respawn-like recovery re-enabled OFF')
toggleVoice();advance(.4,.8)
check(not server.protocol.active,'ON while speaking bypassed fresh quiet')
advance(.4,0);advance(.4,.8)
check(server.protocol.active~=nil,'ON failed after cooldown and fresh quiet')
toggleVoice();local finalCount=#sent;advance(1,.8)
check(#sent==finalCount and not server.protocol.active,'OFF repeatedly stopped or restarted')
-- Dispatch the actual CharacterRemoving callback with mocked character services.
local removalCallback;local p={CharacterRemoving={}}
local function connectClient(_,callback)removalCallback=callback end
local hitFeedback={DiscardThrough=function()end}
local function setSprint()end;local function cancelCapture()end;local closeConversation=nil
__RESPAWN_CALLBACK__
removalCallback();sustainedControl:ObserveAvailability(false);sustainedControl:ObserveAvailability(true)
advance(.4,0);advance(.4,.8)
check(not sustainedControl.armed and #sent==finalCount,'Actual removal callback lost OFF choice on respawn-like recovery')
advance(11,0);toggleVoice();advance(.4,0);advance(.4,.8)
check(server.protocol.active~=nil,'Removal setup did not start an attack')
removalCallback()
check(not sustainedControl.armed and not server.protocol.active and sent[#sent]=='SustainedStop','Actual removal callback did not stop and disarm')
sustainedControl:ObserveAvailability(false);sustainedControl:ObserveAvailability(true)
advance(11,0);advance(.4,.8)
check(not sustainedControl.armed and not server.protocol.active and mic.ready,'Respawn-like recovery resumed attacks or disabled mic')
print('PASS '..checks..' actual voice toggle checks with mocked availability')
'''
checks=checks.replace('__RESPAWN_CALLBACK__',respawn_line)
def run(payload, expected_failure=None):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.voice_toggle_',dir=root/'tests',delete=False) as f:
        path=Path(f.name);f.write(payload)
    try:
        result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True)
        if expected_failure:
            assert result.returncode!=0 and expected_failure in result.stderr, result.stdout+result.stderr
            print('PASS negative control caught: '+expected_failure)
        else:
            print(result.stdout,end='');result.check_returncode()
    finally:
        path.unlink()

payload=setup+s[a:b]+checks
run(payload)
if '--negative-controls' in sys.argv:
    # Isolated fault injection into actual controller instances; production files untouched.
    needle="toggleVoice()\ncheck(not sustainedControl.armed and not sustainedControl.attack"
    assert payload.count(needle)==1
    run(payload.replace(needle,"sustainedControl.Cancel=function()end\n"+needle),
        'OFF did not explicitly stop the active attack')
    needle="advance(11,0);advance(.4,.8)\ncheck(not sustainedControl.armed and #sent==pausedCount"
    assert payload.count(needle)==1
    run(payload.replace(needle,'sustainedControl:SetArmed(true)\n'+needle),
        'Availability/respawn-like recovery re-enabled OFF')
