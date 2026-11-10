"""Diagnose actual Profiles recovery boundaries with two simulated servers.
Characterization evidence, not an endorsement of failed-release recovery policy.
No network, real DataStore, native shutdown or concurrent Roblox servers are used.
"""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/Profiles.luau').read_text()
setup=r'''
local Lease=require('../src/ReplicatedStorage/Shared/ProfileLease')
local now=1000;local os={time=function()return now end}
local records={};local beforeFailures,afterFailures,calls=0,0,0
local store={UpdateAsync=function(_,key,transform)
 calls+=1
 if beforeFailures>0 then beforeFailures-=1;error('pre-commit outage') end
 local result=transform(records[key]);if result~=nil then records[key]=result end
 if afterFailures>0 then afterFailures-=1;error('ambiguous response after commit') end
 return result
end}
local config={Progression={Challenges={},Normalize=function(l,x)return l or 1,x or 0 end},Quests={},Auras={Gold=true},GetSound=function()return {id='TinyAah',level=1}end}
local services={DataStoreService={GetDataStore=function()return store end},ReplicatedStorage={Shared={Config='Config',ProfileLease='Lease'}},RunService={IsStudio=function()return true end},HttpService={GenerateGUID=function()return 'unused' end}}
local waits={};local task={wait=function(dt)table.insert(waits,dt);now+=dt end}
local warnings=0;local warn=function()warnings+=1 end
local require=function(token)if token=='Config' then return config elseif token=='Lease' then return Lease end;error(token)end
local function loadActualProfiles(job)
 local game={JobId=job,GetService=function(_,name)return services[name]end}
'''
checks=r'''
end
local A,B=loadActualProfiles('A'),loadActualProfiles('B');local checks=0
local function check(value,message)assert(value,message);checks+=1 end
local data,ok=A.Load(42);check(ok,'Initial profile acquisition failed')
data.coins=100;check(A.Save(42,data),'Initial durable save failed')
local expiry=records.Player_42._lease.expires;data.coins=150
beforeFailures=3;local started=now;local beforeCalls=calls
local saved,reason=A.Save(42,data,true)
check(not saved and reason=='retry','Exhausted release did not report retry')
check(calls-beforeCalls==3 and now-started==6 and waits[#waits-2]==1 and waits[#waits-1]==2 and waits[#waits]==3,'Existing retry schedule changed')
check(records.Player_42.coins==100 and records.Player_42._lease.owner=='A','Failed release changed stored progress or lease')
local read,sameOwner,message=A.Load(42)
check(not sameOwner and read.coins==0 and message:find('previous session is still saving',1,true),'Same-server failure behavior changed')
now=expiry-1;local _,otherBefore=B.Load(42);check(not otherBefore,'Foreign owner acquired before expiry')
now=expiry;beforeCalls=calls
local _,sameAfter=A.Load(42);check(not sameAfter and calls==beforeCalls,'Same-server owned marker no longer blocks after expiry')
local other,otherOK=B.Load(42)
check(otherOK and other.coins==100 and records.Player_42._lease.owner=='B','Expired lease did not load last durable progress for another owner')
other.coins=200;check(B.Save(42,other,true),'New owner could not save/release its progress')
now+=3600;beforeCalls=calls
local _,stillBlocked=A.Load(42);check(not stillBlocked and calls==beforeCalls,'Old local ownership marker unexpectedly recovered itself')
-- An explicit stale save observes lost ownership and clears A locally without overwriting B.
local stale,staleReason=A.Save(42,data,true)
check(not stale and staleReason=='ownership' and records.Player_42.coins==200,'Stale snapshot overwrote newer owner progress')
local latest,latestOK=A.Load(42);check(latestOK and latest.coins==200,'Ownership rejection did not permit a later clean load')
print('RECOVERY failed-release: attempts=3 waits=1,2,3 durableCoins=100 unsavedCoins=150; same-server blocked at expiry and +3600s; other-server loads 100 at expiry; stale write preserves 200')
-- If the final snapshot is explicitly retained, retrying while still owner can recover it.
local retained,retainedOK=A.Load(43);check(retainedOK,'Retained-snapshot setup failed')
retained.coins=80;beforeFailures=3
check(not A.Save(43,retained,true),'Injected retained-snapshot release succeeded')
check(A.Save(43,retained,true),'Explicit retry while still owner did not recover')
local recovered,recoveredOK=B.Load(43);check(recoveredOK and recovered.coins==80,'Recovered release did not persist final snapshot')
print('RECOVERY retained-snapshot: explicit retry while owner persists 80; current lifecycle has no such automatic retry')
-- A response error does not imply the write failed: release may already be durable.
local ambiguous,ambiguousOK=A.Load(44);check(ambiguousOK,'Ambiguous-write setup failed')
ambiguous.coins=90;afterFailures=1;beforeCalls=calls
local ambiguousSave,ambiguousReason=A.Save(44,ambiguous,true)
check(not ambiguousSave and ambiguousReason=='ownership' and calls-beforeCalls==2,'Ambiguous release result changed')
check(records.Player_44.coins==90 and records.Player_44._lease==nil,'Committed release was lost after response error')
local reread,rereadOK=A.Load(44);check(rereadOK and reread.coins==90,'Committed ambiguous release could not be reloaded')
print('RECOVERY ambiguous-response: Save returns false/ownership after committed release; durableCoins=90 and rejoin succeeds')
print('PASS '..checks..' actual Profiles recovery characterization checks (two simulated owners, in-memory store)')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.profile_recovery_',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+source+checks)
try:subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:path.unlink()
