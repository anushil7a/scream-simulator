"""Actual voice toggle helper with mocked availability; no UI/device evidence."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text();a=s.index('local function toggleVoice()');b=s.index('local function releaseCapture(',a)
setup='''
local unavailable=false;local windowFocused=true
local blocked=function()return unavailable end
local calls=0;local sustainedControl={armed=false}
function sustainedControl:SetArmed(v)self.armed=v;calls+=1 end
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
print('PASS '..checks..' actual voice toggle checks with mocked availability')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.voice_toggle_',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+s[a:b]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
