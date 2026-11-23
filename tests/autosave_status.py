"""Actual autosave status helper with synthetic saves, including yielded completion."""
from pathlib import Path
import subprocess
import sys
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=s.index('local function autosave(p,s)');b=s.index('local function stepAutosaves(now)',a)
c=s.index('local function shutdown()',b)
assert 'nextAutosaveAt=save and os.clock()+30 or nil};sessions[p]=s' in s
setup='''
local sessions={};local messages={};local mode='error';local saved
local clock=0;local os={clock=function()return clock end}
local closing=false;local queued={};local loop
local task={spawn=function(worker)loop=coroutine.create(worker)end,
 defer=function(worker)table.insert(queued,worker)end,
 wait=function(seconds)coroutine.yield(seconds)end}
local function state(_,message,conversation,urgent)assert(urgent==true,"Save failure lost urgent metadata");table.insert(messages,message)end
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
scheduling=r'''
table.clear(sessions)
local function tick(at)
 clock=at
 local ok,delay=coroutine.resume(loop)
 check(ok and delay==.25,"Autosave loop did not pace scheduler ticks")
end
local function runQueued()
 local worker=assert(table.remove(queued,1))
 local job=coroutine.create(worker);local ok,message=coroutine.resume(job);assert(ok,message)
 return job
end
local function player(id,due)
 local p={UserId=id,Parent=true}
 local s={canSave=true,nextAutosaveAt=due,data={coins=id}}
 sessions[p]=s
 return p,s
end
local initialChecks=checks
local expected={}
for id=1,20 do
 local _,s=player(id,30)
 expected[s.data]=true
end
mode='ok';tick(0);tick(29.75)
check(#queued==0,'Autosave ran before the first deadline')
for i=0,19 do
 tick(30+i*.25)
 check(#queued==1,'Concurrent admissions burst or starved')
 runQueued()
 check(expected[saved],'A second write displaced an unwritten profile')
 expected[saved]=nil
end
check(next(expected)==nil,'A writable profile missed its first save')
tick(89.75);check(#queued==0,'Steady autosave ran before 60 seconds')
for i=0,19 do
 tick(90+i*.25);check(#queued==1,'Steady autosave cadence or quiet lease renewal failed')
 runQueued()
end
tick(94.99);check(#queued==0,'Current deadlines permitted an extra write')

table.clear(sessions)
local _,older=player(1,95)
local _,newer=player(2,96)
tick(100)
check(#queued==1 and older.autosaveInFlight and not newer.autosaveInFlight,'Overdue saves skipped the oldest deadline')
mode='yield';local busy=runQueued()
tick(100.25);check(#queued==1 and newer.autosaveInFlight,'One slow profile blocked another')
mode='ok';runQueued()
tick(161)
check(#queued==1 and newer.autosaveInFlight,'An in-flight write got a second pending autosave')
runQueued()
check(coroutine.resume(busy) and not older.autosaveInFlight,'In-flight flag did not clear')
tick(161.25)
check(#queued==1 and older.autosaveInFlight,'Slow profile did not resume after write completion')
runQueued()

table.clear(sessions)
local departed,retired=player(3,163)
tick(164);check(#queued==1,'Depart fixture did not schedule')
local replacement={canSave=true,nextAutosaveAt=180,data={coins=40}}
sessions[departed]=replacement
saved=nil;runQueued()
check(saved==nil and not retired.autosaveInFlight and replacement.canSave,'Deferred write touched a replaced session')
local p,shutdownProfile=player(4,164)
tick(165);check(#queued==1,'Shutdown fixture did not schedule')
closing=true;saved=nil;runQueued()
check(saved==nil and not shutdownProfile.autosaveInFlight,'Deferred autosave started after shutdown')
local ok=coroutine.resume(loop)
check(ok and coroutine.status(loop)=='dead' and #queued==0,'Autosave loop dispatched after shutdown')
print('PASS '..(checks-initialChecks)..' paced scheduler assertions with 20 isolated mock profiles')
'''
payload=setup+s[a:c]+checks+scheduling

def run(source, expected=None):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False,encoding='utf-8') as f:
        path=Path(f.name);f.write(source)
    try:
        result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True)
    finally:
        path.unlink()
    if expected:
        assert result.returncode and expected in result.stderr, result.stdout+result.stderr
        print('PASS negative control:',expected)
    else:
        assert result.returncode==0,result.stdout+result.stderr
        print(result.stdout,end='')

run(payload)
if '--negative-controls' in sys.argv:
    for old,new,expected in (
        ('and not s.autosaveInFlight','', 'An in-flight write got a second pending autosave'),
        ('session.nextAutosaveAt=now+60','session.nextAutosaveAt=now+59','Steady autosave ran before 60 seconds'),
        ('sessions[player]==session','sessions[player]~=nil','Deferred write touched a replaced session'),
        ('if not closing and sessions[player]','if sessions[player]','Deferred autosave started after shutdown'),
    ):
        assert old in payload
        run(payload.replace(old,new,1),expected)
