"""Actual flight input/UI block with mocked controls, not native device evidence."""
from pathlib import Path
import tempfile,subprocess
r=Path(__file__).resolve().parents[1]
s=(r/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
a=s.index('local flightUp=false;');b=s.index('-- Everyone sees the same navigation',a)
setup=r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local now=1;local os={clock=function()return now end};local active=false;local keys={};local textFocus=false
local signals={};local cleanup;local buttons={};local sent={}
local p={GetAttribute=function()return active end};local gui={};local gold={}
local UDim2={fromOffset=function()return {}end,new=function()return {}end}
local function label()return {}end
local function button(_,name,_,_,_,fn)local b={call=fn};buttons[name]=b;return b end
local function connectClient(signal,fn)signals[signal]=fn end
local function ownClient(fn)cleanup=fn end
local UIS={WindowFocusReleased='blur',WindowFocused='focus',TouchEnabled=false,
 GetFocusedTextBox=function()return textFocus end,IsKeyDown=function(_,key)return keys[key]==true end}
local Run={Heartbeat='tick'};local GuiService={MenuIsOpen=false}
local Enum={KeyCode={W='W',A='A',S='S',D='D',Space='Space',LeftControl='Ctrl'}}
local action={FireServer=function(_,verb,arg)table.insert(sent,{verb,arg})end}
local move={x=0,z=0,Dot=function(self,axis)return axis=='right' and self.x or self.z end}
local root={CFrame={RightVector='right',LookVector='forward'}}
p.Character={FindFirstChildOfClass=function()return {MoveDirection=move}end,FindFirstChild=function()return root end}
'''
checks=r'''
local function tick()now+=.11;signals.tick()end
signals.tick();check(#sent==0 and not buttons.FlightUp.Visible,'Inactive input sent')
active=true;keys={W=true,Space=true};tick();local arg=sent[#sent][2];check(arg.z==1 and arg.y==1 and arg.x==0,'Keyboard forward/up')
local before=#sent;signals.tick();check(#sent==before,'Client sent above10Hz')
keys={A=true,S=true,Ctrl=true};tick();arg=sent[#sent][2];check(arg.x==-1 and arg.z==-1 and arg.y==-1,'Keyboard back/left/down')
textFocus=true;tick();arg=sent[#sent][2];check(arg.x==0 and arg.z==0 and arg.y==0,'Text focus kept movement');textFocus=false
keys={};UIS.TouchEnabled=true;move.x=1;buttons.FlightUp.call();tick();arg=sent[#sent][2];check(arg.x==1 and arg.y==1 and buttons.FlightUp.Visible,'Joystick/touch up')
buttons.FlightDown.call();tick();check(sent[#sent][2].y==-1,'Touch down switch');buttons.FlightDown.call();tick();check(sent[#sent][2].y==0,'Touch toggle stop')
buttons.FlightUp.call();signals.blur();tick();arg=sent[#sent][2];check(arg.x==0 and arg.y==0,'Focus-loss hover failed');signals.focus();move.x=0;tick();check(sent[#sent][2].y==0,'Latched ascent resumed')
GuiService.MenuIsOpen=true;keys={W=true};tick();check(sent[#sent][2].z==0,'Menu hover failed')
cleanup();check(sent[#sent][1]=='FlightStop','Client cleanup did not stop')
active=false;before=#sent;tick();cleanup();check(#sent==before and not buttons.FlightDown.Visible,'Inactive cleanup/input leaked')
print('PASS '..n..' actual flight input/UI checks with mocked controls')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=r/'tests',delete=False) as f:f.write(setup+s[a:b]+checks);p=Path(f.name)
try:subprocess.run(['luau',str(p)],check=True,cwd=r)
finally:p.unlink()
