"""Diagnose actual Profiles recovery boundaries with two simulated servers.
Characterization evidence, not an endorsement of failed-release recovery policy.
No network, real DataStore, native shutdown or concurrent Roblox servers are used.
"""
from pathlib import Path
import subprocess,tempfile,sys
root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/Profiles.luau').read_text()
bootstrap=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=bootstrap.index('local departuresInFlight=0');b=bootstrap.index('Players.PlayerRemoving:Connect(leaving)',a)
setup=r'''
local Lease=require('../src/ReplicatedStorage/Shared/ProfileLease')
local now=1000;local os={time=function()return now end,clock=function()return now end}
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
local warnings={};local warn=function(...)table.insert(warnings,table.pack(...))end
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
-- Exercise the ordinary departure consumer against actual Profiles failures.
local Profiles=A;local sessions={}
local function closeConversation()end;local function cancelSustained()end
local VoiceCombat={Cancel=function()end}
__DEPARTURE_HELPER__
local function finalWarning(userId,reason)
 local count=0
 for _,entry in ipairs(warnings) do
  if entry[1]=='ScreamSimulator departure save failed' then
   count+=1;assert(entry[2]==userId and entry[3]==reason,'Departure warning lost UserId/reason')
  end
 end
 return count
end
local departing,departingOK=A.Load(45);check(departingOK,'Departure setup failed')
departing.coins=100;check(A.Save(45,departing),'Departure durable setup failed')
departing.coins=150;local p={UserId=45};sessions[p]={canSave=true,data=departing,voice={}}
beforeFailures=3;warnings={};beforeCalls=calls;leaving(p)
check(calls-beforeCalls==3 and sessions[p]==nil and departuresInFlight==0,'Ordinary failed departure changed retries or retained gameplay/counter')
check(finalWarning(45,'retry')==1,'Actual failed departure omitted final retry warning')
check(records.Player_45.coins==100 and records.Player_45._lease.owner=='A','Diagnostic correction altered failed-release persistence')
local _,blockedAfterDeparture=A.Load(45);check(not blockedAfterDeparture,'Diagnostic correction silently unlocked unresolved release')
local ambiguousDeparture,loaded=A.Load(46);check(loaded,'Ambiguous departure setup failed')
ambiguousDeparture.coins=90;p={UserId=46};sessions[p]={canSave=true,data=ambiguousDeparture,voice={}}
afterFailures=1;warnings={};leaving(p)
check(finalWarning(46,'ownership')==1 and departuresInFlight==0,'Ambiguous departure omitted ownership warning')
check(records.Player_46.coins==90 and records.Player_46._lease==nil,'Ambiguous departure diagnostic changed committed data')
print('RECOVERY ordinary-departure: actual retry exhaustion warns once with UserId/retry, still retains lease; ambiguous committed release warns ownership without claiming rollback')
print('PASS '..checks..' actual Profiles recovery characterization checks (two simulated owners, in-memory store)')
'''
checks=checks.replace('__DEPARTURE_HELPER__',bootstrap[a:b])
def run(payload, expected_failure=None):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.profile_recovery_',dir=root/'tests',delete=False) as f:
        path=Path(f.name);f.write(payload)
    try:
        result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True)
        if expected_failure:
            assert result.returncode!=0 and expected_failure in result.stderr, result.stdout+result.stderr
            print('PASS negative control caught: '+expected_failure)
        else:
            print(result.stdout,end='')
            if result.returncode: print(result.stderr,file=sys.stderr)
            result.check_returncode()
    finally:path.unlink()

payload=setup+source+checks
run(payload)
if '--negative-controls' in sys.argv:
    for original,replacement,expected in [
        ('if not Lease.Owns(raw,owner) then return nil end','-- omitted save owner check','Stale snapshot overwrote newer owner progress'),
        ('if not Lease.CanAcquire(raw,owner,os.time()) then return nil end','-- omitted acquisition check','Foreign owner acquired before expiry'),
        ('if not completed or not ok then warn("ScreamSimulator departure save failed"','if not completed then warn("ScreamSimulator departure save failed"','Actual failed departure omitted final retry warning'),
        ('p.UserId,completed and reason or ok','p.UserId','Departure warning lost UserId/reason'),
    ]:
        assert payload.count(original)==1
        run(payload.replace(original,replacement),expected)
