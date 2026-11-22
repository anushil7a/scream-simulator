"""Actual aimed-player text helper with mocked replicated state; no raycast/UI evidence."""
from pathlib import Path
import subprocess
import sys
import tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
start=source.index('local function playerTargetInfo(')
end=source.index('local sprintButton=',start)
setup='''
local academy={TrainingRules=require('../src/ReplicatedStorage/Shared/TrainingRules')}
local vectorMeta={__sub=function(a,b)return {Magnitude=vector.magnitude(a.value-b.value)}end}
local function position(x,y,z)return setmetatable({value=vector.create(x,y,z)},vectorMeta)end
local function typeof(v)return type(v)=='table' and getmetatable(v)==vectorMeta and 'Vector3' or type(v)end
'''
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
local residentActive=true;local trainingHome,trainingTier
local resident={Name='Fallback',GetAttribute=function(_,key)if key=='ResidentActive' then return residentActive end;if key=='TrainingHome' then return trainingHome end;if key=='TrainingTier' then return trainingTier end;return key=='DisplayName' and 'Gardener' or nil end}
h.Health=40;h.MaxHealth=60
text,ready=residentTargetInfo(resident,h,false,false)
check(ready and text=='Gardener\\nCITY RESIDENT','Ordinary resident presented as a training fighter')
text,ready=residentTargetInfo(resident,h,true,true)
check(not ready and string.find(text,'OUT OF MAX RANGE',1,true),'Resident maximum range ignored')
text,ready=residentTargetInfo(resident,h,false,true)
check(not ready and string.find(text,'BEYOND CURRENT RANGE',1,true),'Resident current range ignored')
trainingTier='rookie'
text,ready=residentTargetInfo(resident,h,false,false,false,position(10,5,-8))
check(ready and string.find(text,'TRAINING FIGHTER',1,true),'Training tier did not identify a fighter')
trainingHome=position(10,5,-8)
text,ready=residentTargetInfo(resident,h,false,false,false,position(42.01,5,-8))
check(not ready and string.find(text,'MOVE TOWARD PAD CENTER',1,true),'Outside the sparring pad looked attackable')
text,ready=residentTargetInfo(resident,h,false,false,false,position(42,5,-8))
check(ready and string.find(text,'TRAINING FIGHTER',1,true),'Exact sparring radius did not match server')
text,ready=residentTargetInfo(resident,h,false,false,false,position(42,6,-8))
check(not ready and string.find(text,'MOVE TOWARD PAD CENTER',1,true),'Training pad check ignored height')
text,ready=residentTargetInfo(resident,h,false,false,true,position(10,5,-8))
check(not ready and string.find(text,'BEHIND COVER',1,true),'Pad admission masked cover')
trainingHome=nil;trainingTier=nil
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
def run(fragment, expected=None):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.target_',dir=root/'tests',delete=False) as file:
        path=Path(file.name);file.write(setup+fragment+checks)
    try:
        result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True)
    finally:
        path.unlink()
    if expected:
        assert result.returncode and expected in result.stderr, result.stderr
        print('PASS control:', expected)
    else:
        assert result.returncode==0, result.stderr
        print(result.stdout.strip())


readout=source[start:end]
run(readout)
if '--negative-controls' in sys.argv:
    for old,new,expected in [
        ('(model:GetAttribute("TrainingTier")~=nil and "TRAINING FIGHTER" or "CITY RESIDENT")', '"TRAINING RESIDENT"', 'Ordinary resident presented as a training fighter'),
        ('model:GetAttribute("TrainingTier")~=nil', 'false', 'Training tier did not identify a fighter'),
        ('typeof(home)=="Vector3" and (position-home).Magnitude>academy.TrainingRules.Radius', 'false', 'Outside the sparring pad looked attackable'),
        ('Magnitude>academy.TrainingRules.Radius', 'Magnitude>=academy.TrainingRules.Radius', 'Exact sparring radius did not match server'),
    ]:
        assert readout.count(old)==1
        run(readout.replace(old,new),expected)
