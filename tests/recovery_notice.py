"""Actual notice formatter and source wiring checks, not a native UI/layout test."""
from pathlib import Path
import subprocess,tempfile,sys
root=Path(__file__).resolve().parents[1]
client=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
server=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=client.index('local function saveStatus()');b=client.index('connectClient(remotes.State',a)
checks=r'''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
data={recoveryWarning=true,savingAvailable=true}
check(saveStatus()=='Recovered save\nRecent progress may be missing','Recovered writable profile omitted persistent warning')
data.savingDelayed=true
check(string.find(saveStatus(),'Save delayed',1,true)~=nil and string.find(saveStatus(),'Recent progress may be missing',1,true)~=nil,'Recovery warning masks autosave failure')
check(progressLabel(true)=='DELAYED · progress may be missing','Compact recovery warning masks autosave failure')
data.savingDelayed=false
check(saveStatus()=='Recovered save\nRecent progress may be missing','Saved retry lost recovery warning')
check(progressLabel(true)=='RECOVERED · progress may be missing','Compact saved retry lost recovery warning')
data.savingAvailable=false
check(saveStatus()=='TEMPORARY · recovered save\nRecent progress may be missing','Read-only fallback hid temporary status')
data.savingDelayed=true
check(string.find(saveStatus(),'Recent progress may be missing',1,true)~=nil,'Autosave update erased recovery warning')
data.testSession=true;check(saveStatus()=='TEST SESSION · progress is temporary','Developer mode lost temporary notice')
data={savingDelayed=true};check(saveStatus()=='Save delayed · retrying automatically','Ordinary retry status regressed')
data={savingAvailable=false};check(saveStatus()=='Temporary progress · saving unavailable','Ordinary temporary status regressed')
data={savingAvailable=true};check(saveStatus()=='','Normal profile received rollback warning')
-- Actual autosave helper transitions; state delivery is simulated, not a RemoteEvent.
local p={UserId=1,Parent=true};local profile={canSave=true,recoveryWarning=true,data={coins=100}}
sessions[p]=profile
saveResult=false;saveReason='retry';autosave(p,profile)
check(data.savingDelayed and saveStatus():find('Save delayed',1,true) and progressLabel(true):find('DELAYED',1,true),'Autosave failure did not reach both formatters')
check(saveStatus():find('progress may be missing',1,true),'Autosave failure hid recovery history')
saveResult=true;autosave(p,profile);state(p) -- ordinary subsequent replicated State
check(not data.savingDelayed and saveStatus():find('Recovered save',1,true),'Saved retry did not clear delayed status')
saveResult=false;saveReason='ownership';autosave(p,profile)
check(not data.savingAvailable and saveStatus():find('TEMPORARY',1,true) and progressLabel(true):find('UNSAVED',1,true),'Ownership loss implied writable recovery')
check(saveStatus():find('progress may be missing',1,true),'Ownership loss erased recovery warning')
print('PASS '..checks..' actual recovery notice formatter checks')
'''
autosave_start=server.index('local function autosave(p,s)')
autosave_end=server.index('task.spawn(function() while true do task.wait(60)',autosave_start)
server_setup=r'''
local sessions={};local saveResult,saveReason
local Profiles={Save=function()return saveResult,saveReason end}
local function state(p)
 local session=sessions[p]
 data={recoveryWarning=session.recoveryWarning,savingAvailable=session.canSave,savingDelayed=session.saveDelayed}
end
'''
def run(source,expected=None):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.recovery_notice_',dir=root/'tests',delete=False,encoding='utf-8') as f:
        path=Path(f.name);f.write('local data\n'+source+server_setup+server[autosave_start:autosave_end]+checks)
    try:
        result=subprocess.run(['luau',str(path)],cwd=root,text=True,capture_output=True)
        if expected:
            assert result.returncode!=0 and expected in result.stderr,result.stdout+result.stderr
            print('PASS negative control caught: '+expected)
        else:
            print(result.stdout,end='')
            assert result.returncode==0,result.stderr
    finally:path.unlink()
run(client[a:b])
if '--negative-controls' in sys.argv:
    for old,expected in [
        ('data.savingDelayed and "Save delayed · retrying" or ','Recovery warning masks autosave failure'),
        ('data.savingDelayed and "DELAYED" or ','Compact recovery warning masks autosave failure'),
    ]:
        assert client[a:b].count(old)==1
        run(client[a:b].replace(old,''),expected)
assert 'else data,save,loadMessage,recoveryWarning=Profiles.Load(p.UserId) end' in server
assert 'canSave=save,recoveryWarning=recoveryWarning' in server
assert 'recoveryWarning=s.recoveryWarning==true' in server
assert 'saveNotice.Text=saveStatus()' in client
print('PASS 4 recovery notice source wiring contracts; not remote/native execution')
