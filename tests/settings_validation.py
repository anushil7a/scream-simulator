"""Actual settings mutation branch with mocked session/state; no saves or transport."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=s.index(' elseif verb=="SetSettings" and type(arg)=="table" then')
b=s.index('\n end\nend)',a)
branch=s[a+len(' elseif verb=="SetSettings" and type(arg)=="table" then'):b]
setup='''
local p={};local updates=0
local s={data={level=42,coins=123,settings={volume=.55,reducedShake=false}}}
local function state()updates+=1 end
local function apply(arg)
 if type(arg)~='table' then return end
'''
checks='''
end
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
apply({volume=.25,reducedShake=true})
check(s.data.settings.volume==.25 and s.data.settings.reducedShake,'Valid settings rejected')
for _,value in ipairs({0/0,'loud',false,{}})do
 apply({volume=value,reducedShake='yes'})
 check(s.data.settings.volume==.25 and s.data.settings.reducedShake,'Invalid settings changed stored values')
end
apply({volume=-5});check(s.data.settings.volume==0,'Lower volume bound missing')
apply({volume=5});check(s.data.settings.volume==1,'Upper volume bound missing')
apply({volume=math.huge});check(s.data.settings.volume==1,'Positive infinity not normalized')
apply({volume=-math.huge});check(s.data.settings.volume==0,'Negative infinity not normalized')
apply({level=100,coins=999999,settings={volume=.8},reducedShake=false})
check(s.data.level==42 and s.data.coins==123 and s.data.settings.volume==0 and not s.data.settings.reducedShake,'Settings payload overwrote unrelated profile data')
local before=updates
for _,value in ipairs({false,'settings',42})do apply(value)end
check(updates==before,'Non-table settings reached mutation branch')
apply({});check(s.data.settings.volume==0 and not s.data.settings.reducedShake,'Empty update changed settings')
print('PASS '..checks..' actual settings validation checks with mocked session')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(setup+branch+checks)
try: subprocess.run(['/opt/homebrew/bin/luau',str(path)],cwd=root,check=True)
finally: path.unlink()
