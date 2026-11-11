"""Actual sprint input helper with mocked UI/character state; no physical inputs."""
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
local modal={Visible=false};local devPanel={Visible=false};local conversationPanel={Visible=false}
local workspace={GetServerTimeNow=function()return 10 end}
local began,ended;local Enum={KeyCode={LeftShift='shift',V='v'}};UIS.InputBegan={};UIS.InputEnded={}
local function connectClient(signal,fn)if signal==UIS.InputBegan then began=fn else ended=fn end end
local function releaseCapture()end;local captureSource=nil
local messages={};local action={FireServer=function(_,verb,arg)assert(verb=='Sprint');table.insert(messages,arg)end}
'''
dispatch=s[s.index('connectClient(UIS.InputBegan,'):s.index('connectClient(p.CharacterRemoving,',s.index('connectClient(UIS.InputBegan,'))]
checks='''
local count=0;local function check(v,msg)assert(v,msg);count+=1 end
setSprint(true);check(sprinting and #messages==1 and messages[1],'Start was not transmitted')
setSprint(true);check(#messages==1,'Unchanged request spammed server')
setSprint(false);check(not sprinting and #messages==2 and messages[2]==false,'Release did not stop sprint')
local cases={
 function(v)windowFocused=not v end,function(v)mic.ready=not v end,
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
print('PASS '..count..' actual sprint input checks with mocked UI/character state')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.sprint_input_',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+s[start:end]+dispatch+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
