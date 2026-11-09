"""Actual autosave status helper with synthetic saves, including yielded completion."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=s.index('local function autosave(p,s)');b=s.index('task.spawn(function() while true do task.wait(60)',a)
setup='''
local sessions={};local messages={};local mode='error';local saved
local function state(_,message)table.insert(messages,message)end
local Profiles={Save=function(_,data)
 saved=data
 if mode=='error' then error('synthetic exception') end
 if mode=='yield' then coroutine.yield();return true end
 if mode=='ok' then return true end
 return false,mode
end}
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local p={UserId=1,Parent=true};local s={canSave=true,data={coins=10}};sessions[p]=s
autosave(p,s)
check(s.saveDelayed and s.canSave and #messages==1,'Exception failed to show delayed state')
autosave(p,s);check(#messages==1,'Repeated exception spammed notices')
mode='ok';autosave(p,s);check(not s.saveDelayed and s.canSave,'Successful retry did not clear delay')
mode='transient';autosave(p,s);check(s.saveDelayed and #messages==2,'Normal failure lost delayed notice')
for _,reason in ipairs({'ownership','unavailable'})do
 mode=reason;s.canSave=true;autosave(p,s)
 check(not s.canSave and not s.saveDelayed,'Permanent saving failure retained eligibility')
end
s.canSave=true;s.testBaseline={coins=3};mode='ok';autosave(p,s)
check(saved==s.testBaseline,'Autosave persisted developer mutations')
s.saveDelayed=true;mode='yield'
local thread=coroutine.create(function()autosave(p,s)end);check(coroutine.resume(thread),'Yielding fixture failed')
local replacement={saveDelayed=true};sessions[p]=replacement;local before=#messages
check(coroutine.resume(thread),'Delayed completion failed')
check(s.saveDelayed and replacement.saveDelayed and #messages==before,'Stale completion changed status after session replacement')
sessions[p]=s;p.Parent=nil;mode='error';autosave(p,s)
check(#messages==before,'Departed player received failure notice')
print('PASS '..checks..' actual autosave status checks with mocked saves')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+s[a:b]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
