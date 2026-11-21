"""Actual aimed-player text helper with mocked replicated state; no raycast/UI evidence."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
start=source.index('local function playerTargetInfo(')
end=source.index('local sprintButton=',start)
checks='''
local attrs={ScreamLevel=100};local target={DisplayName='Test Player',GetAttribute=function(_,key)return attrs[key] end}
local h={Health=72.5,MaxHealth=135};local checks=0
local function check(v,msg)assert(v,msg);checks+=1 end
local text,ready=playerTargetInfo(target,h,true,true,false,10)
check(ready and text=='Test Player · LV 100\\nARENA OPPONENT','Opponent name/level/status text incorrect')
text,ready=playerTargetInfo(target,h,false,false,false,10)
check(not ready and string.find(text,'BOTH OUTSIDE PvP',1,true),'Safe opponent labeled attackable')
text,ready=playerTargetInfo(target,h,true,false,false,10)
check(not ready and text=='Test Player · LV 100\\nTARGET OUTSIDE PvP','Target endpoint did not explain the PvP restriction')
attrs.ProtectionEnds=12
text,ready=playerTargetInfo(target,h,false,true,true,10,true,true)
check(not ready and text=='Test Player · LV 100\\nYOU ARE OUTSIDE PvP','Local endpoint restriction lost priority')
attrs.ProtectionEnds=12;text,ready=playerTargetInfo(target,h,true,true,false,10)
check(not ready and string.find(text,'PROTECTED · 2.0s',1,true),'Protection not displayed')
attrs.DodgeEnds=11;text,ready=playerTargetInfo(target,h,true,true,false,10)
check(not ready and string.find(text,'PROTECTED',1,true),'Roll hid protection')
attrs.ProtectionEnds=10;text,ready=playerTargetInfo(target,h,true,true,false,10)
check(not ready and string.find(text,'DODGING',1,true),'Roll not displayed at protection expiry')
attrs.DodgeEnds=10;text,ready=playerTargetInfo(target,h,true,true,true,10)
check(not ready and string.find(text,'OUT OF MAX RANGE',1,true),'Distant target labeled reachable')
text,ready=playerTargetInfo(target,h,true,true,false,10)
check(ready,'Expired protection/roll retained stale status')
attrs.ScreamLevel=nil;text=playerTargetInfo(target,h,true,true,false,10)
check(not string.find(text,'LV',1,true),'Unreplicated level was fabricated')
text,ready=playerTargetInfo(target,h,true,true,false,10,true)
check(not ready and string.find(text,'BEYOND CURRENT RANGE',1,true),'Low-power range displayed as reachable')
text,ready=playerTargetInfo(target,h,true,true,true,10,true)
check(not ready and string.find(text,'OUT OF MAX RANGE',1,true),'Current range hid absolute cap')
text,ready=playerTargetInfo(target,h,true,true,false,10,false)
check(ready and string.find(text,'ARENA OPPONENT',1,true),'In-range target stayed unavailable')
h.Health=0;text,ready=playerTargetInfo(target,h,true,true,false,10)
check(text==nil and not ready,'Dead target retained health readout')
local residentActive=true
local resident={Name='Fallback',GetAttribute=function(_,key)if key=='ResidentActive' then return residentActive end;return key=='DisplayName' and 'Gardener' or nil end}
h.Health=40;h.MaxHealth=60
text,ready=residentTargetInfo(resident,h,false,false)
check(ready and text=='Gardener\\nTRAINING RESIDENT','Resident name/status missing')
text,ready=residentTargetInfo(resident,h,true,true)
check(not ready and string.find(text,'OUT OF MAX RANGE',1,true),'Resident maximum range ignored')
text,ready=residentTargetInfo(resident,h,false,true)
check(not ready and string.find(text,'BEYOND CURRENT RANGE',1,true),'Resident current range ignored')
residentActive=false;text,ready=residentTargetInfo(resident,h,false,false)
check(text==nil and not ready,'Recovering resident with live Humanoid retained readout')
residentActive=true
h.Health=0;text,ready=residentTargetInfo(resident,h,false,false)
check(text==nil and not ready,'Dead resident retained readout')
text,ready=residentTargetInfo(resident,nil,false,false)
check(text==nil and not ready,'Missing resident humanoid retained readout')
h.Health=40
text,ready=residentTargetInfo(resident,h,false,false,true)
check(not ready and string.find(text,'BEHIND COVER',1,true),'Covered resident labeled available')
text,ready=playerTargetInfo(target,h,true,true,false,10,false,true)
check(not ready and string.find(text,'BEHIND COVER',1,true),'Covered player labeled available')
text,ready=playerTargetInfo(target,h,false,false,false,10,false,true)
check(not ready and string.find(text,'BOTH OUTSIDE PvP',1,true),'Cover hid safe-zone restriction')
text,ready=playerTargetInfo(target,h,true,true,true,10,true,true)
check(not ready and string.find(text,'OUT OF MAX RANGE',1,true),'Cover hid maximum range')
text,ready=playerTargetInfo(target,h,true,true,false,10,false,false)
check(ready,'Cleared cover retained unavailable status')
print('PASS '..checks..' actual target readout checks with mocked replicated state')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.target_',dir=root/'tests',delete=False) as file:
    path=Path(file.name);file.write(source[start:end]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
