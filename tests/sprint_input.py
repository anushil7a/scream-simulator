"""Actual client control callbacks with mocked UI, character and input events."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
start=s.index('local sprinting=false');end=s.index('local function playerTargetInfo(',start)
setup='''
local h={Health=100};local attrs={};local character={FindFirstChildOfClass=function()return h end}
local p={Character=character,GetAttribute=function(_,k)return attrs[k]end}
local windowFocused=true;local mic={ready=true};local GuiService={MenuIsOpen=false}
local typing=false;local UIS={GetFocusedTextBox=function()return typing and {} or nil end}
local micPanel={Visible=false};local modal={Visible=false};local devPanel={Visible=false};local conversationPanel={Visible=false}
local workspace={GetServerTimeNow=function()return 10 end}
local academy={}
local began,ended,disconnected
local keys={LeftShift='shift',V='v',ButtonY='y',ButtonB='b',ButtonR1='r1',ButtonL1='l1',ButtonL2='l2',ButtonL3='l3'}
local Enum={KeyCode=keys};UIS.InputBegan={};UIS.InputEnded={};UIS.GamepadDisconnected={}
local function connectClient(signal,fn)
 if signal==UIS.InputBegan then began=fn elseif signal==UIS.InputEnded then ended=fn else disconnected=fn end
end
local captureSource;local sustainedControl={armed=false,SetArmed=function(self,armed)self.armed=armed end};local actions={}
local function toggle()table.insert(actions,'menu')end
local function toggleVoice()sustainedControl:SetArmed(not sustainedControl.armed);table.insert(actions,'voice')end
local function requestTalk()table.insert(actions,'talk')end
local function dodge()table.insert(actions,'dodge')end
local function closeMenu()modal.Visible=false end
local function closeConversation()conversationPanel.Visible=false end
local function beginCapture(source)captureSource=source end
local function releaseCapture(source)if captureSource==source then captureSource=nil;table.insert(actions,'release') end end
local function cancelCapture()captureSource=nil;table.insert(actions,'cancel')end
local messages={};local action={FireServer=function(_,verb,arg)assert(verb=='Sprint');table.insert(messages,arg)end}
'''
dispatch=s[s.index('connectClient(UIS.InputBegan,'):s.index('connectClient(p.CharacterRemoving,',s.index('connectClient(UIS.InputBegan,'))]
disconnect=s[s.index('connectClient(UIS.GamepadDisconnected,'):s.index('\ndo\n local scope,previous')]
checks='''
local count=0;local function check(v,msg)assert(v,msg);count+=1 end
setSprint(true);check(sprinting and #messages==1 and messages[1],'Start was not transmitted')
setSprint(true);check(#messages==1,'Unchanged request spammed server')
setSprint(false);check(not sprinting and #messages==2 and messages[2]==false,'Release did not stop sprint')
local cases={
 function(v)windowFocused=not v end,
 function(v)GuiService.MenuIsOpen=v end,function(v)typing=v end,
 function(v)modal.Visible=v end,function(v)devPanel.Visible=v end,
 function(v)conversationPanel.Visible=v end,function(v)h.Health=v and 0 or 100 end,
 function(v)if v then p.Character=nil else p.Character=character end end,
 function(v)attrs.KnockdownEnds=v and 11 or 0 end,
 function(v)h.PlatformStand=v end,function(v)h.Sit=v end,
 function(v)h.SeatPart=v and {} or nil end,
}
for i,block in ipairs(cases) do
 setSprint(true);block(true);setSprint(true)
 check(not sprinting and messages[#messages]==false,'Interruption retained sprint '..i)
 local before=#messages;setSprint(true)
 check(#messages==before,'Blocked retry sent a start '..i)
 block(false);check(not sprinting,'Clearing block silently resumed sprint '..i)
end
mic.ready=false;setSprint(true);check(sprinting,'Unready microphone blocked dismissed-setup sprint');setSprint(false);mic.ready=true
setSprint(true);setSprint(not sprinting)
check(not sprinting,'Button toggle disagreed with keyboard start')
local shift={KeyCode=Enum.KeyCode.LeftShift}
began(shift,false);local sent=#messages;began(shift,false)
check(sprinting and #messages==sent,'Held key repeated requests')
ended(shift);check(not sprinting and messages[#messages]==false,'Actual key release retained sprint')
for i=1,20 do began(shift,false);ended(shift) end
check(not sprinting and #messages==sent+41,'Tap dispatch lost starts/stops')
began(shift,true);check(not sprinting,'Processed key started sprint')
began({KeyCode=Enum.KeyCode.V},false);check(not sprinting,'Removed view key changed sprint')
local primary={Name='Gamepad1'}
local secondary={Name='Gamepad2'}
local keyboard={Name='Keyboard'}
local function press(key,device,processed)
 began({KeyCode=key,UserInputType=device or primary},processed or false)
end
press(keys.ButtonY,keyboard)
press(keys.ButtonY,primary,true)
windowFocused=false;press(keys.ButtonY);windowFocused=true
GuiService.MenuIsOpen=true;press(keys.ButtonY);GuiService.MenuIsOpen=false
typing=true;press(keys.ButtonY);typing=false
check(#actions==0,'Blocked or non-gamepad input activated an action')
press(keys.ButtonY);press(keys.ButtonR1);press(keys.ButtonL1);press(keys.ButtonL2)
check(table.concat(actions,',')=='menu,voice,dodge,talk','Controller actions were not dispatched')
check(sustainedControl.armed,'Controller did not arm the voice double')
disconnected(secondary);check(sustainedControl.armed,'An unrelated controller disarmed voice')
disconnected(primary);check(not sustainedControl.armed,'Arming controller disconnect left voice armed')
modal.Visible=true;press(keys.ButtonB);check(not modal.Visible,'Controller back left Menu open')
conversationPanel.Visible=true;press(keys.ButtonB);check(not conversationPanel.Visible,'Controller back left conversation open')
press(keys.ButtonL3);local padSent=#messages
check(sprinting and academy.sprintController==primary,'Controller did not start sprint')
press(keys.ButtonL3)
ended({KeyCode=keys.ButtonL3,UserInputType=secondary})
disconnected(secondary)
check(sprinting and #messages==padSent,'Another controller interrupted sprint or repeat sent another start')
ended({KeyCode=keys.ButtonL3,UserInputType=primary})
check(not sprinting and messages[#messages]==false,'Controller release left sprint active')
press(keys.ButtonL3);disconnected(primary)
check(not sprinting and not academy.sprintController,'Controller disconnect left sprint active')
press(keys.ButtonL3);windowFocused=false;setSprint(true);windowFocused=true
check(not sprinting and not academy.sprintController,'Interruption kept stale sprint controller')
press(keys.ButtonL3);check(sprinting,'New press after interruption did not recover')
setSprint(false)
sustainedControl=nil
press(keys.ButtonR1);check(captureSource==primary,'Legacy capture did not start on controller')
ended({KeyCode=keys.ButtonR1,UserInputType=secondary})
check(captureSource==primary,'Secondary controller released legacy capture')
disconnected(primary);check(not captureSource and actions[#actions]=='cancel','Disconnect fired or retained legacy capture')
press(keys.ButtonR1);ended({KeyCode=keys.ButtonR1,UserInputType=primary})
check(not captureSource and actions[#actions]=='release','Controller release failed for legacy capture')
print('PASS '..count..' actual sprint and controller input checks with mocked UI/character state')
'''
def run(handler,disconnect_handler=disconnect):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.sprint_input_',dir=root/'tests',delete=False) as f:
        path=Path(f.name);f.write(setup+s[start:end]+handler+disconnect_handler+checks)
    try:
        return subprocess.run(['luau',str(path)],cwd=root,text=True,capture_output=True)
    finally:
        path.unlink()

result=run(dispatch)
assert result.returncode==0,result.stdout+result.stderr
print(result.stdout.strip())
for wrong,correct,failure in (
    ('k==Enum.KeyCode.ButtonY then toggle()', 'k==Enum.KeyCode.ButtonY then return', 'Controller actions were not dispatched'),
    ('academy.sprintController==input.UserInputType', 'academy.sprintController~=input.UserInputType', 'Another controller interrupted sprint'),
    ('academy.beamController==inputType', 'academy.beamController~=inputType', 'An unrelated controller disarmed voice'),
):
    assert (dispatch+disconnect).count(wrong)==1,wrong
    result=run(dispatch.replace(wrong,correct),disconnect.replace(wrong,correct))
    assert result.returncode!=0 and failure in result.stderr,result.stdout+result.stderr
print('PASS 3 controller input negative controls')
