"""Actual progress-label selection with mocked profile/layout state."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
a=s.index('local function progressLabel(');b=s.index('connectClient(remotes.State',a)
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
check(progressLabel(true)=='30 / 103 XP','Normal compact XP missing')
data.savingDelayed=true
check(progressLabel(true)=='SAVE DELAYED • retrying','Delayed save notice missing')
check(progressLabel(false)=='30 / 103 XP','Wide layout retained compact save override')
data.savingAvailable=false
check(progressLabel(true)=='TEMPORARY PROGRESS • not saved','Temporary status did not override delayed status')
data.savingAvailable=true;data.savingDelayed=false;data.testSession=true
check(progressLabel(true)=='TEMPORARY PROGRESS • not saved','Test session missing temporary status')
data.level=100
check(progressLabel(false)=='MAX LEVEL','Wide cap label missing')
data.testSession=false
check(progressLabel(true)=='MAX LEVEL','Recovered compact cap label missing')
data.level=1
check(progressLabel(true)=='30 / 103 XP','Normal XP did not recover')
data.recoveryWarning=true
check(progressLabel(true)=='RECOVERED · progress may be missing','Compact recovery warning missing')
data.savingAvailable=false
check(progressLabel(true)=='UNSAVED · progress may be missing','Temporary compact recovery warning missing')
data.testSession=true
check(progressLabel(true)=='TEMPORARY PROGRESS • not saved','Developer status lost priority')
print('PASS '..checks..' actual progress label checks with mocked state')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write('local Config={MaxLevel=100};local data={level=1,xp=30,xpNext=103}\n'+s[a:b]+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
