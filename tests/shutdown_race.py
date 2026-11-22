"""Actual remote reward, shutdown, join and Profiles paths with an in-memory store.
No Roblox DataStore, network or shutdown timing validation is claimed.
"""
from pathlib import Path
import subprocess,sys,tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
profiles=(root/'src/ServerScriptService/Profiles.luau').read_text()
def section(start,end):
    a=s.index(start);return s[a:s.index(end,a)]
setup=r'''
local Lease=require('../src/ReplicatedStorage/Shared/ProfileLease')
local now=0;local os={clock=function()return now end,time=function()return 1000+math.floor(now)end}
local sessions={};local closing=false;local shutdownSaveDeadline;local joinsInFlight=0;local departuresInFlight=0
local records={};local duringSave;local pauseLoad=false;local pauseWrite={}
local delayRelease,failRelease,releaseAttempts={},{},{}
local loseCommittedRelease={}
local store={UpdateAsync=function(_,key,transform)
 if pauseLoad then pauseLoad=false;coroutine.yield('load') end
 if pauseWrite[key] then pauseWrite[key]=nil;coroutine.yield('write') end
 if duringSave and key=='Player_2' then local hook=duringSave;duringSave=nil;hook();coroutine.yield('save') end
 local result=transform(records[key])
 if result and result._lease==nil and records[key] and records[key]._lease then
  releaseAttempts[key]=(releaseAttempts[key] or 0)+1
  if delayRelease[key] then delayRelease[key]=nil;coroutine.yield('release') end
  if (failRelease[key] or 0)>0 then failRelease[key]-=1;error('injected release write failure') end
  if loseCommittedRelease[key] then
   loseCommittedRelease[key]=nil;records[key]=result;error('injected lost response after commit')
  end
 end
 if result~=nil then records[key]=result end;return result
end}
local Config={Gear=require("../src/ReplicatedStorage/Shared/GearCatalog"),MaxLevel=100,XPToNext=function()return 1000 end,Sounds={},Auras={Gold=true},
 Quests={{id='garden',name='Garden',goal=3,coins=40,xp=100}},Progression={Challenges={},Normalize=function(l,x)return l or 1,x or 0 end},
 GetSound=function()return {id='TinyAah',level=1} end}
Config.GetQuest=function(id)for _,q in ipairs(Config.Quests)do if q.id==id then return q end end end
local services={DataStoreService={GetDataStore=function()return store end},ReplicatedStorage={Shared={Config='Config',ProfileLease='Lease'}},RunService={IsStudio=function()return false end},HttpService={GenerateGUID=function()return 'test-owner' end}}
local game={GameId=0,JobId='shutdown-test',GetService=function(_,name)return services[name]end}
local require=function(token)if token=='Config' then return Config elseif token=='Lease' then return Lease end;error(token)end
local queue={};local task={spawn=function(fn,...)local args=table.pack(...);table.insert(queue,coroutine.create(function()fn(table.unpack(args,1,args.n))end))end,wait=function(dt)coroutine.yield(dt)end}
local warnings={};local warn=function(...)table.insert(warnings,table.pack(...))end
local function step(co)local ok,result=coroutine.resume(co);assert(ok,result);return result end
local function drive(co)
 local ticks=0
 while coroutine.status(co)~='dead' or #queue>0 do
  ticks+=1;assert(ticks<300,'Scheduler failed to terminate');now+=.1
  if coroutine.status(co)~='dead' then step(co) end
  local pending=queue;queue={}
  for _,job in ipairs(pending)do step(job);if coroutine.status(job)~='dead' then table.insert(queue,job)end end
 end
end
local function loadProfiles()
'''
between=r'''
end
local Profiles=loadProfiles()
local Commerce={Multiplier=function()return 1 end}
local Entitlements={Refresh=function()end}
local notices={};local cancels=0
local function state(p,message)table.insert(notices,{p=p,message=message})end
local function syncHealth()end;local function stopQuest()end;local function closeConversation()end
local function cancelSustained()cancels+=1 end
local VoiceCombat={Cancel=function()end}
local handler;local action={OnServerEvent={Connect=function(_,fn)handler=fn end}}
'''
checks=r'''
local checks=0;local function check(value,message)assert(value,message);checks+=1 end
local function player(id)
 local p={UserId=id,Parent=true}
 local data,canSave=Profiles.Load(id);assert(canSave)
 data.coins=10;data.quests.garden={progress=3,claimed=false}
 local s={canSave=true,data=data,nextAction=0};sessions[p]=s;return p,s
end
local p,first=player(1)
handler(p,'ClaimQuest','garden')
check(first.data.coins==50 and first.data.xp==100 and first.data.quests.garden.claimed,'Pre-shutdown claim did not succeed')
local late,second=player(2)
local beforeNotices=#notices
-- A load already in flight when shutdown starts must not recreate gameplay.
pauseLoad=true
local joining={UserId=3,Parent=true}
local loadThread=coroutine.create(function()joinTracked(joining)end)
check(step(loadThread)=='load' and joinsInFlight==1,'Join did not yield in actual profile load')
duringSave=function()
 handler(late,'ClaimQuest','garden')
 coins(late,7);xp(late,9) -- also exercise late combat reward helpers
end
local closeThread=coroutine.create(shutdown)
check(step(closeThread)==.1,'Shutdown did not wait for pending persistence')
check(closing and next(sessions)==nil and cancels==2,'Shutdown retained gameplay/attack ownership')
local pending=queue;queue={}
for _,job in ipairs(pending)do step(job);if coroutine.status(job)~='dead' then table.insert(queue,job)end end
check(second.data.coins==10 and second.data.xp==0 and not second.data.quests.garden.claimed and #notices==beforeNotices,'Shutdown accepted an unsavable reward after final snapshot')
-- Finish every active-player save while the acquisition remains suspended.
pending=queue;queue={};for _,job in ipairs(pending)do step(job);check(coroutine.status(job)=='dead','Final save did not finish')end
check(step(closeThread)==.1 and coroutine.status(closeThread)=='suspended','Shutdown returned before the in-flight profile acquisition released')
-- The release itself can yield after acquisition completes. Stay tracked until it returns.
delayRelease.Player_3=true
check(step(loadThread)=='release','Late release did not reach delayed UpdateAsync')
check(joinsInFlight==1 and sessions[joining]==nil and records.Player_3._lease~=nil,'Delayed release was treated as completed')
check(step(closeThread)==.1 and coroutine.status(closeThread)=='suspended','Shutdown returned during delayed late release')
check(#warnings==0,'Delayed successful release emitted a premature failure')
step(loadThread)
check(joinsInFlight==0 and sessions[joining]==nil,'Late load reopened gameplay or leaked join count')
check(records.Player_3 and records.Player_3._lease==nil,'Late load did not release its acquired lease')
drive(closeThread)
check(records.Player_1.coins==50 and records.Player_1.xp==100 and records.Player_1.quests.garden.claimed and not records.Player_1._lease,'Accepted pre-close reward was not persisted/released')
check(records.Player_2.coins==10 and records.Player_2.xp==0 and not records.Player_2.quests.garden.claimed and not records.Player_2._lease,'Late rejected claim changed saved profile')
joinTracked({UserId=4,Parent=true});check(records.Player_4==nil and joinsInFlight==0,'New join acquired a profile after shutdown')
local reloaded,ok=Profiles.Load(2);check(ok and reloaded.coins==10 and not reloaded.quests.garden.claimed,'Rejected claim was lost rather than remaining claimable')
check(#warnings==0,'Unexpected save/join warning')
-- Track exceptions too, so BindToClose cannot wait forever on a failed load.
closing=false;local originalLoad=Profiles.Load;Profiles.Load=function()error('injected load failure')end
joinTracked({UserId=5,Parent=true});check(joinsInFlight==0 and #warnings==1,'Failed load leaked tracked join')
Profiles.Load=originalLoad
local function lateJoin(id,departed)
 closing=false;shutdownSaveDeadline=nil;pauseLoad=true
 local p={UserId=id,Parent=true};local co=coroutine.create(function()joinTracked(p)end)
 check(step(co)=='load' and joinsInFlight==1,'Late-release fixture did not suspend acquisition')
 if departed then p.Parent=nil else closing=true end
 return p,co
end
local function releaseWarnings(from)
 local found={}
 for i=from+1,#warnings do if warnings[i][1]=='ScreamSimulator late profile release failed' then table.insert(found,warnings[i]) end end
 return found
end
-- Actual Profiles.Save exhausts its own three attempts; the caller must surface false/retry.
for _,departed in ipairs({false,true})do
 local id=departed and 7 or 6;local key='Player_'..id
 local p,co=lateJoin(id,departed);local before=#warnings
 failRelease[key]=3
 check(step(co)==1 and joinsInFlight==1 and records[key]._lease~=nil,'Release retry stopped tracking or claimed success early')
 check(#releaseWarnings(before)==0,'Release retry emitted final failure before attempts finished')
 repeat step(co) until coroutine.status(co)=='dead'
 check(releaseAttempts[key]==3 and records[key]._lease~=nil,'Failed release unexpectedly committed or skipped retries')
 check(joinsInFlight==0 and sessions[p]==nil,'Failed release reopened gameplay or leaked tracked work')
 local logged=releaseWarnings(before)
 check(#logged==1 and logged[1][2]==id and logged[1][3]=='retry','Late release false/retry was not logged with player and reason')
end
-- An unexpected Save exception must use the same failure path, without claiming success.
local p,co=lateJoin(8,false);local before=#warnings;local originalSave=Profiles.Save
Profiles.Save=function()error('injected late release exception')end
step(co);Profiles.Save=originalSave
local logged=releaseWarnings(before)
check(#logged==1 and logged[1][2]==8 and tostring(logged[1][3]):find('injected late release exception',1,true),'Late release exception was not logged consistently')
check(joinsInFlight==0 and sessions[p]==nil and records.Player_8._lease~=nil,'Exception claimed release or leaked gameplay/tracking')
for _,job in ipairs(queue)do step(job)end;table.clear(queue)
closing=false
local queuedPlayer=player(9)
local queuedClose=coroutine.create(shutdown)
check(step(queuedClose)==.1 and #queue==1 and not sessions[queuedPlayer],'Final release was not queued after gameplay froze')
local queuedJob=table.remove(queue)
now+=25.1
step(queuedClose)
check(coroutine.status(queuedClose)=='dead','Shutdown callback still waited past its deadline')
local queuedWarnings=#warnings
step(queuedJob)
check(not releaseAttempts.Player_9 and records.Player_9._lease~=nil,'Final worker started a new write after shutdown deadline')
check(#warnings==queuedWarnings+1 and warnings[#warnings][2]=='deadline','Expired final release did not log deadline')

-- Waiting on an already-started autosave must not start a final write after its deadline.
local lockedPlayer,locked=player(10)
pauseWrite.Player_10=true
local autosaveThread=coroutine.create(function()assert(Profiles.Save(10,locked.data))end)
check(step(autosaveThread)=='write','Lock test did not suspend the in-flight autosave')
locked.data.coins=70
local lockDeadline=now+.03
local lockOK,lockReason
local lockWaiter=coroutine.create(function()lockOK,lockReason=Profiles.Save(10,locked.data,true,lockDeadline)end)
local sleep=step(lockWaiter)
check(math.abs(sleep-.03)<.001,'Lock wait did not cap its sleep at the deadline')
now=lockDeadline
step(lockWaiter)
check(lockOK==false and lockReason=='deadline' and not releaseAttempts.Player_10,'Expired waiter attempted a release under a busy lock')
step(autosaveThread)
check(records.Player_10.coins==10 and records.Player_10._lease~=nil,'Deadline disturbed the earlier autosave or its lease')
check(Profiles.Save(10,locked.data,true) and records.Player_10.coins==70 and not records.Player_10._lease,'Deadline damaged later legitimate write ownership')
sessions[lockedPlayer]=nil

local failingPlayer,failing=player(11)
delayRelease.Player_11=true;failRelease.Player_11=1
local retryDeadline=now+.2
local retryOK,retryReason
local retryJob=coroutine.create(function()retryOK,retryReason=Profiles.Save(11,failing.data,true,retryDeadline)end)
check(step(retryJob)=='release','Failure fixture did not suspend the first write')
now=retryDeadline
step(retryJob)
check(retryOK==false and retryReason=='deadline' and releaseAttempts.Player_11==1 and records.Player_11._lease,'Late failure started another write or claimed release')
sessions[failingPlayer]=nil

local pendingPlayer,pending=player(12)
delayRelease.Player_12=true
local successDeadline=now+.2
local finished
local successJob=coroutine.create(function()finished=Profiles.Save(12,pending.data,true,successDeadline)end)
check(step(successJob)=='release','Success fixture did not suspend its write')
now=successDeadline+.2
step(successJob)
check(finished and records.Player_12.coins==10 and not records.Player_12._lease,'Late successful release was discarded or not durable')
sessions[pendingPlayer]=nil

local slowJoin,slowLoad=lateJoin(13,false)
shutdownSaveDeadline=now
local lateWarnings=#warnings
step(slowLoad)
local loggedAfterDeadline=releaseWarnings(lateWarnings)
check(joinsInFlight==0 and not sessions[slowJoin] and not releaseAttempts.Player_13 and records.Player_13._lease,'Late acquisition caused a new release after deadline')
check(#loggedAfterDeadline==1 and loggedAfterDeadline[1][3]=='deadline','Late acquisition missed the shutdown deadline reason')

local ambiguousPlayer,ambiguous=player(14)
delayRelease.Player_14=true;loseCommittedRelease.Player_14=true
local ambiguousDeadline=now+.2
local ambiguousOK,ambiguousReason
local ambiguousJob=coroutine.create(function()ambiguousOK,ambiguousReason=Profiles.Save(14,ambiguous.data,true,ambiguousDeadline)end)
check(step(ambiguousJob)=='release','Ambiguous response fixture did not suspend write')
now=ambiguousDeadline+.2
step(ambiguousJob)
check(ambiguousOK==false and ambiguousReason=='deadline' and not records.Player_14._lease
 and releaseAttempts.Player_14==1,'Lost response claimed success or attempted a second release')
local recovered,admitted=Profiles.Load(14)
check(admitted and recovered.coins==10 and records.Player_14._lease~=nil
 and releaseAttempts.Player_14==1,'Recovery did not recognize the already committed release')
sessions[ambiguousPlayer]=nil
print('PASS '..checks..' actual shutdown/reward/join/profile race checks (synthetic store and scheduler)')
'''
code=setup+profiles+between+section('local function disconnectSessionSignals(','local function beamColor(')+section('local function coins(','local function syncHealth(')+section('local function xp(','local function questProgress(')+section('action.OnServerEvent:Connect(function(p,verb,arg)','local function joined(p)')+section('local function joined(p)','Players.PlayerAdded:Connect(joinTracked)')+section('local function shutdown()','game:BindToClose(shutdown)')+checks
def run(source,expected=None):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.shutdown_race_',dir=root/'tests',encoding='utf-8',delete=False) as f:
        path=Path(f.name);f.write(source)
    try:
        result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True)
    finally:
        path.unlink()
    if expected:
        assert result.returncode and expected in result.stderr,result.stdout+result.stderr
        print('PASS negative control:',expected)
    else:
        assert result.returncode==0,result.stdout+result.stderr
        print(result.stdout,end='')

run(code)
if '--negative-controls' in sys.argv:
    for old,new,expected in (
        ('s.testBaseline or s.data,true,deadline','s.testBaseline or s.data,true','Final worker started a new write after shutdown deadline'),
        ('task.wait(remaining and math.min(.05,remaining) or .05)','task.wait(.05)','Lock wait did not cap its sleep at the deadline'),
        ('commit(userId,session,operation,deadline)\n    if release','commit(userId,session,operation)\n    if release','Late failure started another write or claimed release'),
        ('p.UserId,data,true,shutdownSaveDeadline','p.UserId,data,true','Late acquisition caused a new release after deadline'),
        ('if success then\n            if result==nil','if success then\n            if deadline and os.clock()>=deadline then return false,"deadline" end\n            if result==nil','Late successful release was discarded or not durable'),
    ):
        assert code.count(old)==1,old
        run(code.replace(old,new,1),expected)
