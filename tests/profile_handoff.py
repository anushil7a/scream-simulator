"""Same-experience profile arrivals, using actual Profiles and an isolated simulated store."""
from pathlib import Path
import sys

from profile_recovery_policy import lease, run, setup, source

checks=r'''
end
local A,B,C=loadModule('A'),loadModule('B'),loadModule('C')
local count=0
local function check(value,reason)assert(value,reason);count+=1 end
local function step(thread)
 local ok,result=coroutine.resume(thread)
 assert(ok,result)
 return result
end
local function saved(id)
 local data,writable=A.Load(id)
 assert(writable);data.coins=100;assert(A.Save(id,data))
 return data
end

local departing=saved(31)
departing.coins=160
local before=calls
local result
local arriving=coroutine.create(function()result={B.Load(31,true)}end)
yieldWait=true
check(step(arriving)=='wait','Destination accepted temporary play before the final release could finish')
check(calls-before==1 and records.Player_31.coins==100 and records.Player_31._lease.owner=='A','First contention modified the source save')
yieldWait=false
check(A.Save(31,departing,true),'Source could not release')
step(arriving)
check(result[2] and result[1].coins==160 and not result[3] and not result[4],'Arrival missed a newly released checkpoint or warned unnecessarily')
check(calls-before==3 and records.Player_31._lease.owner=='B','Arrival did not use one bounded retry')
check(not A.Save(31,departing,true),'Departed profile could still write')

local held=saved(32)
local foreignLease=copy(records.Player_32._lease)
before=calls
local fallback,writable,warning=B.Load(32,true)
check(not writable and fallback.coins==100 and warning:find('temporary',1,true) and calls-before==3,'Persistent conflict did not exhaust with the saved checkpoint read-only')
local recorded=records.Player_32._lease
check(recorded.owner==foreignLease.owner and recorded.token==foreignLease.token and recorded.expires==foreignLease.expires,'Arrival replaced or extended another lease')
check(not B.Save(32,fallback),'Temporary arrival obtained write access')
held.coins=121;check(A.Save(32,held),'Foreign owner could no longer save')
before=calls
local direct,directWritable=B.Load(32,false)
check(not directWritable and direct.coins==121 and calls-before==1,'Direct join changed its contention behavior')

local lostSource=saved(33)
lostSource.coins=260
before=calls
arriving=coroutine.create(function()result={B.Load(33,true)}end)
yieldWait=true
check(step(arriving)=='wait','Lost response scenario missed the contention wait')
yieldWait=false
check(A.Save(33,lostSource,true),'Lost response scenario source release failed')
afterFailures=1
step(arriving)
check(result[2] and result[1].coins==260 and records.Player_33._lease.owner=='B' and calls-before==4,'Lost response did not acknowledge only the admitted token')
check(not A.Save(33,lostSource),'Late source write became valid after ambiguous destination response')
local outlet=saved(34)
outlet.coins=410
retryHook=function()assert(A.Save(34,outlet,true))end
before=calls
local rerun,writable=B.Load(34,true)
check(writable and rerun.coins==410 and calls-before==2,'Reinvoked acquisition callback failed to use the released checkpoint')

local interrupted=saved(35)
arriving=coroutine.create(function()result={B.Load(35,true)}end)
yieldWait=true
check(step(arriving)=='wait','Outage scenario did not wait for the source')
yieldWait=false
beforeFailures=2
step(arriving)
check(not result[2] and result[1].coins==100 and result[3]:find('temporary',1,true) and not B.Save(35,result[1]),
 'Read outage after contention did not retain a temporary confirmed fallback')
check(A.Save(35,interrupted,true),'Failed destination load changed source ownership')
local racing=saved(36)
racing.coins=205
arriving=coroutine.create(function()result={B.Load(36,true)}end)
yieldWait=true
check(step(arriving)=='wait','Competing-owner scenario never reached the backoff')
yieldWait=false
check(A.Save(36,racing,true),'Source release failed in competing-owner scenario')
local winner,won=C.Load(36)
assert(won);winner.coins=530;assert(C.Save(36,winner))
local winnerLease=copy(records.Player_36._lease)
step(arriving)
check(not result[2] and result[1].coins==530 and records.Player_36._lease.token==winnerLease.token
 and records.Player_36._lease.expires==winnerLease.expires,'Retry replaced the newer server lease or checkpoint')
check(not B.Save(36,result[1]) and not A.Save(36,racing),'A former candidate retained write access')
print('PASS '..count..' actual cross-server profile handoff assertions; simulated store')
'''


def payload(production=source):
    return setup.replace('__LEASE__',lease)+production+checks


if __name__=='__main__':
    run(payload())

    bootstrap=(Path(__file__).resolve().parents[1]/'src/ServerScriptService/Bootstrap.server.luau').read_text()
    start=bootstrap.index('local function arrivedFromAnotherPlace(')
    gate=bootstrap[start:bootstrap.index('local function joined(',start)]
    run(setup.replace('__LEASE__',lease)+source+"\nend\n"+r"""
local game={GameId=5,PlaceId=8}
local cases={
 {{SourceGameId=5,SourcePlaceId=12},true},
 {{SourceGameId=6,SourcePlaceId=12},false},
 {{SourceGameId=5,SourcePlaceId=8},false},
 {{SourceGameId=5,SourcePlaceId=0},false},
 {{SourceGameId=5,SourcePlaceId="12"},false},
 {{},false},
 {{TeleportData={SourceGameId=5,SourcePlaceId=12}},false},
}
"""+gate+r"""
for _,case in ipairs(cases)do
 local p={GetJoinData=function()return case[1]end}
 assert(arrivedFromAnotherPlace(p)==case[2],"Unexpected transfer classification")
end
game.GameId=0
assert(not arrivedFromAnotherPlace({}),"Unpublished place inspected join provenance")
print("PASS 8 actual arrival classification assertions")
""")
    if '--negative-controls' in sys.argv:
        for old,new,reason in [
            ('elseif fromOtherPlace~=true or not contended or attempt==3 then','else','Destination accepted temporary play before the final release could finish'),
            ('elseif fromOtherPlace~=true or not contended or attempt==3 then','elseif not contended or attempt==3 then','Direct join changed its contention behavior'),
        ]:
            assert source.count(old)==1,old
            run(payload(source.replace(old,new)),reason)
