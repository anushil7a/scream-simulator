"""Actual remote reward, shutdown, join and Profiles paths with an in-memory store.
No Roblox DataStore, network or shutdown timing validation is claimed.
"""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
profiles=(root/'src/ServerScriptService/Profiles.luau').read_text()
def section(start,end):
    a=s.index(start);return s[a:s.index(end,a)]
setup=r'''
local Lease=require('../src/ReplicatedStorage/Shared/ProfileLease')
local now=0;local os={clock=function()return now end,time=function()return 1000+math.floor(now)end}
local sessions={};local closing=false;local joinsInFlight=0;local departuresInFlight=0
local records={};local duringSave;local pauseLoad=false
local store={UpdateAsync=function(_,key,transform)
 if pauseLoad then pauseLoad=false;coroutine.yield('load') end
 if duringSave and key=='Player_2' then local hook=duringSave;duringSave=nil;hook();coroutine.yield('save') end
 local result=transform(records[key]);if result~=nil then records[key]=result end;return result
end}
local Config={MaxLevel=100,XPToNext=function()return 1000 end,Sounds={},Auras={Gold=true},
 Quests={{id='garden',goal=3,coins=40,xp=100}},Progression={Challenges={},Normalize=function(l,x)return l or 1,x or 0 end},
 GetSound=function()return {id='TinyAah',level=1} end}
Config.GetQuest=function(id)for _,q in ipairs(Config.Quests)do if q.id==id then return q end end end
local services={DataStoreService={GetDataStore=function()return store end},ReplicatedStorage={Shared={Config='Config',ProfileLease='Lease'}},RunService={IsStudio=function()return false end},HttpService={GenerateGUID=function()return 'test-owner' end}}
local game={JobId='shutdown-test',GetService=function(_,name)return services[name]end}
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
-- Resume the pending acquisition after close; its owned profile must be released.
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
print('PASS '..checks..' actual shutdown/reward/join/profile race checks (synthetic store and scheduler)')
'''
code=setup+profiles+between+section('local function coins(','local function syncHealth(')+section('local function xp(','local function questProgress(')+section('action.OnServerEvent:Connect(function(p,verb,arg)','local function joined(p)')+section('local function joined(p)','Players.PlayerAdded:Connect(joinTracked)')+section('local function shutdown()','game:BindToClose(shutdown)')+checks
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.shutdown_race_',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(code)
try:subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:path.unlink()
