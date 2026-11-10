"""Actual notice formatter and source wiring checks, not a native UI/layout test."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
client=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
server=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=client.index('local function saveStatus()');b=client.index('local function progressLabel(',a)
checks=r'''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
data={recoveryWarning=true,savingAvailable=true}
check(saveStatus()=='Recovered save\nRecent progress may be missing','Recovered writable profile omitted persistent warning')
data.savingAvailable=false
check(saveStatus()=='TEMPORARY · recovered save\nRecent progress may be missing','Read-only fallback hid temporary status')
data.savingDelayed=true
check(string.find(saveStatus(),'Recent progress may be missing',1,true)~=nil,'Autosave update erased recovery warning')
data.testSession=true;check(saveStatus()=='TEST SESSION · progress is temporary','Developer mode lost temporary notice')
data={savingDelayed=true};check(saveStatus()=='Save delayed · retrying automatically','Ordinary retry status regressed')
data={savingAvailable=false};check(saveStatus()=='Temporary progress · saving unavailable','Ordinary temporary status regressed')
data={savingAvailable=true};check(saveStatus()=='','Normal profile received rollback warning')
print('PASS '..checks..' actual recovery notice formatter checks')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.recovery_notice_',dir=root/'tests',delete=False,encoding='utf-8') as f:
    path=Path(f.name);f.write('local data\n'+client[a:b]+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
assert 'else data,save,loadMessage,recoveryWarning=Profiles.Load(p.UserId) end' in server
assert 'canSave=save,recoveryWarning=recoveryWarning' in server
assert 'recoveryWarning=s.recoveryWarning==true' in server
assert 'saveNotice.Text=saveStatus()' in client
print('PASS 4 recovery notice source wiring contracts; not remote/native execution')
