"""Actual server destruction hint logic; synthetic responses, no UI rendering."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
start=source.index('local function destructionHint(')
end=source.index('local function stepSustained(',start)
checks='''
local count=0
local function check(v,msg)assert(v,msg);count+=1 end
local intent={}
check(destructionHint(intent,nil)==nil,'Missing result produced hint')
check(destructionHint(intent,{health=20})==nil,'Successful damage produced lock hint')
check(destructionHint(intent,{reason='destroyed'})==nil,'Destroyed object produced level hint')
check(not intent.destructionHintShown,'Non-level outcome consumed hint')
check(destructionHint(intent,{reason='level',required=26})=='This object needs scream level 26 to damage','Unlock level not explained')
for i=1,20 do check(destructionHint(intent,{reason='level',required=51})==nil,'Continuous damage spammed hint') end
check(destructionHint({}, {reason='level',required=51})=='This object needs scream level 51 to damage','Next attack did not reset hint')
print('PASS '..count..' actual destruction hint checks with synthetic responses')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.hint_',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(source[start:end]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
