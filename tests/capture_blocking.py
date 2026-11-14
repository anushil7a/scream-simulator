"""Actual client capture gate with mocked avatar, UI, microphone and time."""
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
source=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
a=source.index('local function blocked()')
b=source.index('local function beginCapture(',a)
setup='''
local workspace={GetServerTimeNow=function()return 10 end}
local GuiService={MenuIsOpen=false}
local typing=false
local UIS={GetFocusedTextBox=function()return typing and {} or nil end}
local conversationPanel={Visible=false};local modal={Visible=false};local devPanel={Visible=false}
local mic={ready=true};local micPanel={Visible=false};local data={voiceEligible=true}
local humanoid={Health=100,PlatformStand=false}
local character={FindFirstChildOfClass=function()return humanoid end}
local attrs={}
local p={Character=character,GetAttribute=function(_,name)return attrs[name] end}
'''
checks='''
local checks=0
local function check(value,message)assert(value,message);checks+=1 end
check(not beamBlocked(),'Healthy available character blocked')
humanoid.PlatformStand=true;check(beamBlocked(),'Ragdoll accepted capture')
humanoid.PlatformStand=false;check(not beamBlocked(),'Ragdoll recovery remained blocked')
humanoid.Health=0;check(beamBlocked(),'Dead character accepted capture');humanoid.Health=100
p.Character=nil;check(beamBlocked(),'Missing character accepted capture');p.Character=character
local saved=humanoid;humanoid=nil;check(beamBlocked(),'Missing humanoid accepted capture');humanoid=saved
for _,name in ipairs({'ProtectionEnds','DodgeEnds','KnockdownEnds'})do
 attrs[name]=11;check(beamBlocked(),'Active interruption accepted: '..name)
 attrs[name]=10;check(not beamBlocked(),'Expired interruption remained: '..name)
end
for _,panel in ipairs({conversationPanel,modal,devPanel})do
 panel.Visible=true;check(beamBlocked(),'Open panel accepted capture');panel.Visible=false
end
GuiService.MenuIsOpen=true;check(beamBlocked(),'Roblox menu accepted capture');GuiService.MenuIsOpen=false
typing=true;check(beamBlocked(),'Typing accepted capture');typing=false
mic.ready=false;check(beamBlocked(),'Missing microphone accepted capture');check(not blocked(),'Mic loss blocked ordinary movement')
mic.ready=true;data.voiceEligible=false;check(beamBlocked(),'Unverified account accepted capture');check(not blocked(),'Voice eligibility blocked ordinary movement')
print('PASS '..checks..' actual capture gate checks with mocked avatar/UI')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+source[a:b]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
