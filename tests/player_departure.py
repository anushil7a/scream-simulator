"""Actual departure helper with a yielding fake save; no DataStore evidence."""
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=source.index('local departuresInFlight=0')
b=source.index('Players.PlayerRemoving:Connect(leaving)',a)
setup='''
local sessions={};local closes,cancels,legacy,saves=0,0,0,0
local warnings=0;local warn=function()warnings+=1 end
local savedData,savedRelease
local function closeConversation(p)closes+=1;if sessions[p] then sessions[p].conversationBot=nil end end
local function cancelSustained()cancels+=1 end
local VoiceCombat={Cancel=function()legacy+=1 end}
local Profiles={Save=function(id,data,release)
 saves+=1;savedData=data;savedRelease=release;coroutine.yield('saving')
end}
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local p={UserId=7};local data={coins=31}
local original={data=data,canSave=true,voice={},conversationBot={}}
sessions[p]=original
local thread=coroutine.create(function()leaving(p)end)
local ok,result=coroutine.resume(thread)
check(ok and result=='saving','Save fixture did not yield')
check(sessions[p]==nil and departuresInFlight==1,'Departing session remained active or shutdown lost pending save')
check(original.conversationBot==nil and cancels==1 and legacy==1,'Departure retained dialogue/capture')
check(savedData==data and savedRelease==true,'Legitimate profile/release changed')
leaving(p);check(saves==1,'Duplicate departure repeated save')
local replacement={data={coins=90}};sessions[p]=replacement
check(coroutine.resume(thread),'Save completion failed')
check(sessions[p]==replacement and departuresInFlight==0,'Old save completion removed replacement or leaked shutdown wait')
local baseline={coins=5}
sessions[p]={canSave=true,data={coins=9999},testBaseline=baseline,voice={}}
thread=coroutine.create(function()leaving(p)end);check(coroutine.resume(thread),'Baseline departure failed')
check(savedData==baseline,'Developer test progress replaced legitimate baseline')
check(coroutine.resume(thread),'Baseline save completion failed')
local before=saves
sessions[p]={canSave=false,data={},voice={}}
leaving(p)
check(sessions[p]==nil and saves==before,'Temporary profile was saved or retained')
Profiles.Save=function()error('fake save failure')end
sessions[p]={canSave=true,data={},voice={}}
leaving(p)
check(sessions[p]==nil and departuresInFlight==0 and warnings==1,'Save exception leaked departing session/shutdown counter')
print('PASS '..checks..' actual departure checks with mocked yielding save')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+source[a:b]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
