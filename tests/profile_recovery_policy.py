"""Actual persistence protocol with cloned in-memory records and controlled faults.
No Roblox services, live stores, network or engine deadline claims.
"""
from pathlib import Path
import subprocess,sys,tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/Profiles.luau').read_text()
lease=(root/'src/ReplicatedStorage/Shared/ProfileLease.luau').read_text()
setup=r'''
local Lease=(function()
__LEASE__
end)()
local function copy(v)
 if type(v)~='table' then return v end
 local r={};for k,value in pairs(v)do r[k]=copy(value)end;return r
end
local now=1000;local os={time=function()return now end,clock=function()return now end}
local records={};local beforeFailures,afterFailures,calls=0,0,0
local pauseNext=false;local yieldWait=false;local beforeHook,afterHook,retryHook
local callbacks={};local warnings={}
local store={UpdateAsync=function(_,key,transform)
 calls+=1;table.insert(callbacks,{key=key,transform=transform})
 if pauseNext then pauseNext=false;coroutine.yield('store') end
 if beforeHook then local hook=beforeHook;beforeHook=nil;hook() end
 if beforeFailures>0 then beforeFailures-=1;error('pre-commit outage') end
 local result=transform(copy(records[key]))
 if retryHook then local hook=retryHook;retryHook=nil;hook();result=transform(copy(records[key])) end
 if result~=nil then records[key]=copy(result) end
 if afterHook then local hook=afterHook;afterHook=nil;hook() end
 if afterFailures>0 then afterFailures-=1;error('lost response') end
 return copy(result)
end}
local config={Progression={Challenges={},Normalize=function(l,x)return l or 1,x or 0 end},Quests={},Auras={Gold=true},GetSound=function()return {id='TinyAah',level=1}end}
local guid=0
local services={DataStoreService={GetDataStore=function()return store end},ReplicatedStorage={Shared={Config='Config',ProfileLease='Lease'}},RunService={IsStudio=function()return true end},HttpService={GenerateGUID=function()guid+=1;return 'guid-'..guid end}}
local waits={};local task={wait=function(dt)
 table.insert(waits,dt);now+=dt;if yieldWait then coroutine.yield('wait') end
end}
local warn=function(...)table.insert(warnings,table.pack(...))end
local require=function(token)if token=='Config' then return config elseif token=='Lease' then return Lease end;error(token)end
local function loadModule(job)
 local game={JobId=job,GetService=function(_,name)return services[name]end}
'''
checks=r'''
end
local A,B,C=loadModule('A'),loadModule('B'),loadModule('A')
local checks=0
local function check(value,message)assert(value,message);checks+=1 end
local function load(api,id,coins)
 local d,ok=api.Load(id);assert(ok,'Setup load failed');d.coins=coins or 100;assert(api.Save(id,d));return d
end
local function step(co)local ok,v=coroutine.resume(co);assert(ok,v);return v end
local function failedRelease(api,id,d)
 d.coins=150;beforeFailures=3;local before=calls
 local ok,reason=api.Save(id,d,true)
 check(not ok and reason=='retry' and calls-before==3,'Final release did not exhaust exactly three attempts')
end
-- Retained final snapshot is isolated from caller mutation; one bounded retry on rejoin.
local d=load(A,1);failedRelease(A,1,d);d.coins=999
local before=calls;local recovered,ok,message,notice=A.Load(1)
check(ok and recovered.coins==150 and not message and not notice and calls-before==2,'Retained snapshot recovery failed or used mutated caller data')
recovered.coins=200;check(A.Save(1,recovered),'Recovered session cannot save')
check(not A.Save(1,d,true) and records.Player_1.coins==200,'Old handle overwrote newer acquisition')
-- Recovery exhausted, but authoritative acquisition succeeds: load last saved data and warn.
d=load(A,2);failedRelease(A,2,d);beforeFailures=3;before=calls
local fallback,canSave,msg,warned=A.Load(2)
check(canSave and fallback.coins==100 and warned and msg:find('Recent progress may be missing',1,true),'Bounded recovery did not fall back with warning')
check(calls-before==4,'Recovery exceeded three attempts before fallback acquisition')
fallback.coins=250;check(A.Save(2,fallback),'Fallback is not writable after a valid acquisition')
check(not A.Save(2,d,true) and records.Player_2.coins==250,'Retired snapshot revived after fallback')
-- Outage also blocks acquisition: cached CONFIRMED data is temporary, never writable defaults.
d=load(A,3);failedRelease(A,3,d);beforeFailures=6;before=calls
local temporary,writable,outage,missing=A.Load(3)
check(not writable and temporary.coins==100 and missing and outage:find('temporary',1,true),'Outage fallback lost confirmed snapshot or warning')
check(calls-before==6 and records.Player_3.coins==100,'Outage exceeded recovery/load attempt bounds')
check(not A.Save(3,temporary) and not A.Save(3,d),'Temporary/retired data became writable')
-- Fresh unknown data must never become a writable default after read errors.
beforeFailures=3;local unknown,unknownSave,unknownMessage=A.Load(4)
check(not unknownSave and unknown.coins==0 and unknownMessage:find('Could not confirm',1,true),'Read errors masqueraded as confirmed new data')
-- An in-flight slow request may exceed the deadline; no more recovery requests begin.
d=load(A,5);failedRelease(A,5,d);before=calls
beforeHook=function()now+=13;error('slow outage')end
local slow,slowSave,_,slowWarning=A.Load(5)
check(slowSave and slow.coins==100 and slowWarning and calls-before==2,'Recovery continued issuing requests past deadline')
-- Foreign takeover: never steal an active lease, never overlay old snapshot onto newer progress.
d=load(A,6);local expiry=records.Player_6._lease.expires;failedRelease(A,6,d)
now=expiry-1;local _,early=B.Load(6);check(not early,'Foreign acquisition admitted before expiry')
now=expiry;local other,otherSave,_,otherWarning=B.Load(6)
check(otherSave and other.coins==100 and otherWarning,'Expired takeover omitted rollback warning')
other.coins=300;check(B.Save(6,other),'New owner save failed')
before=calls;local seen,readOnly,_,seenWarning=A.Load(6)
check(not readOnly and seen.coins==300 and seenWarning and records.Player_6.coins==300,'Old recovery overwrote or stole newer owner save')
check(calls-before==2 and not A.Save(6,d,true),'Lost ownership was retried or stale data reopened')
check(B.Save(6,other,true),'New owner release failed')
local latest,latestSave=A.Load(6);check(latestSave and latest.coins==300,'Fallback missed latest durable checkpoint')
-- A same-job module is not the same acquisition; tokens, not only JobId, fence ownership.
d=load(A,7);local _,sameJob=C.Load(7)
check(not sameJob and records.Player_7._lease.owner=='A','Same-job distinct acquisition stole active lease')
-- Lost release response: recognize identical committed operation instead of rewriting.
d=load(A,8);d.coins=150;afterFailures=1;before=calls
check(A.Save(8,d,true) and calls-before==2 and records.Player_8._lease==nil,'Lost release response was not reconciled idempotently')
local released,releasedSave,_,releasedWarning=A.Load(8)
check(releasedSave and released.coins==150 and not releasedWarning,'Confirmed ambiguous release rolled back or falsely warned')
-- All three responses can fail after commit; pending recovery must still recognize it.
d=load(A,9);d.coins=150;afterFailures=3
check(not A.Save(9,d,true) and records.Player_9.coins==150,'Lost-response exhaustion setup failed')
local responseRecovered,responseOK,_,responseWarning=A.Load(9)
check(responseOK and responseRecovered.coins==150 and not responseWarning,'Recovery rewrote or abandoned an already committed release')
-- Another owner saves after the release commits but before its lost response is retried.
d=load(A,10);d.coins=150;afterFailures=1
afterHook=function()
 afterFailures=0
 local b,bOK=B.Load(10);assert(bOK);b.coins=400;assert(B.Save(10,b,true))
 afterFailures=1
end
local acknowledged,reason=A.Save(10,d,true)
check(not acknowledged and reason=='ownership' and records.Player_10.coins==400,'Ambiguous release retry overwrote newer save')
local moved,movedSave,_,movedWarning=A.Load(10)
check(movedSave and moved.coins==400 and movedWarning,'Ambiguous ownership loss did not load latest checkpoint with notice')
-- Lost autosave responses followed by a newer autosave; replay the OLD transform itself.
d=load(A,11);d.coins=150;afterFailures=3;local firstCallback=#callbacks+1
check(not A.Save(11,d),'Autosave lost-response setup failed')
local oldTransform=callbacks[firstCallback].transform
d.coins=500;check(A.Save(11,d),'New autosave failed after ambiguous previous save')
local replay=oldTransform(copy(records.Player_11))
check(replay==nil and records.Player_11.coins==500,'Old same-acquisition revision could overwrite newer save')
-- A transform delayed until AFTER fallback/reacquisition must recheck the exact token.
d=load(A,12);firstCallback=#callbacks+1;failedRelease(A,12,d)
oldTransform=callbacks[firstCallback].transform;beforeFailures=3
local new,newOK=A.Load(12);check(newOK,'Stale-transform fallback setup failed')
new.coins=600;check(A.Save(12,new),'Stale-transform new save failed')
check(oldTransform(copy(records.Player_12))==nil,'Old acquisition transform could overwrite newer save')
-- Roblox may invoke a callback again after contention; discard its earlier proposed result.
d=load(A,13);d.coins=150
retryHook=function()
 now=records.Player_13._lease.expires
 local b,bOK=B.Load(13);assert(bOK);b.coins=700;assert(B.Save(13,b))
end
local retryOK=A.Save(13,d,true)
check(not retryOK and records.Player_13.coins==700,'Reinvoked callback used stale ownership after contention')
-- Rejoin/load and stale autosave serialize with a yielding recovery call.
d=load(A,14);failedRelease(A,14,d);pauseNext=true
local recovered14,loaded14,duplicate14
local co=coroutine.create(function()recovered14,loaded14=A.Load(14)end)
check(step(co)=='store','Recovery fixture did not yield')
yieldWait=true
local duplicate=coroutine.create(function()duplicate14={A.Load(14)}end)
check(step(duplicate)=='wait','Concurrent rejoin bypassed recovery lock')
yieldWait=false;step(co);step(duplicate)
check(loaded14 and recovered14.coins==150 and not duplicate14[2],'Concurrent recovery admitted two writers')
check(not A.Save(14,d,true),'Old handle became writable after delayed recovery')
-- A sanctioned baseline copy retains its acquisition; unbound defaults cannot save.
d=load(A,15);local baseline=A.Sanitize(d);baseline.coins=900
check(A.Save(15,baseline) and records.Player_15.coins==900,'Developer baseline lost legitimate binding')
check(not A.Save(15,A.Default()),'Unbound default gained write access')
-- Acquisition itself can commit and lose its response; warning must survive retries.
records.Player_16={coins=90,_lease={owner='dead',token='expired',expires=now-1}}
afterFailures=1;local acquired,acquiredOK,_,acquiredWarning=A.Load(16)
check(acquiredOK and acquired.coins==90 and acquiredWarning,'Lost acquisition response erased recovery warning')
records.Player_17={coins=95};afterFailures=3
local readCheckpoint,readWritable,_,readWarning=A.Load(17)
check(not readWritable and readCheckpoint.coins==95 and readWarning,'Lost acquisition responses discarded observed confirmed checkpoint')
-- An identical operation may be acknowledged after a new owner acquires but
-- before its first save. Returning raw must not release/restamp that new lease.
d=load(A,18);d.coins=150;local b18,b18Token
afterHook=function()
 afterFailures=0 -- lose A's response, not B's nested acquisition response
 local acquiredOK;b18,acquiredOK=B.Load(18);assert(acquiredOK)
 b18Token=records.Player_18._lease.token
 afterFailures=1
end
afterFailures=1;before=calls
check(A.Save(18,d,true) and calls-before==3 and records.Player_18.coins==150 and records.Player_18._lease.token==b18Token,'Acknowledging committed release changed newer owner lease')
b18.coins=550;check(B.Save(18,b18),'New owner could not save after ambiguous acknowledgement')
-- Pause recovery before its atomic callback; a newer owner wins during the wait.
d=load(A,19);failedRelease(A,19,d);pauseNext=true
local delayedData,delayedWritable
co=coroutine.create(function()delayedData,delayedWritable=A.Load(19)end)
check(step(co)=='store','Delayed ownership recovery fixture did not yield')
now=records.Player_19._lease.expires
local b19,b19OK=B.Load(19);assert(b19OK);b19.coins=750;assert(B.Save(19,b19))
step(co)
check(not delayedWritable and delayedData.coins==750 and records.Player_19.coins==750 and records.Player_19._lease.owner=='B','Delayed recovery overwrote newly acquired save')
-- Recovery plus acquisition fail before commit: a later rejoin must retain only
-- exact-token admission authority, never retry the discarded final snapshot.
d=load(A,20);failedRelease(A,20,d);local terminal20=copy(records.Player_20._lease)
beforeFailures=6;local temp20,tempSave=A.Load(20)
check(not tempSave and temp20.coins==100 and records.Player_20._lease.token==terminal20.token,'Outage setup changed terminal lease')
temp20.coins=999 -- temporary gameplay must not become the reacquired checkpoint
before=calls;local back20,backSave,_,backWarning=A.Load(20)
check(backSave and back20.coins==100 and backWarning and calls-before==1 and now<terminal20.expires,'Terminal admission token forgotten after outage')
check(not A.Save(20,d,true) and not A.Save(20,temp20),'Old or temporary handle acquired fallback write authority')
-- A foreign owner wins after outage: neither its token, expiry nor save changes.
d=load(A,21);failedRelease(A,21,d);firstCallback=#callbacks+4
beforeFailures=6;A.Load(21);oldTransform=callbacks[firstCallback].transform
now=records.Player_21._lease.expires
local b21,b21OK=B.Load(21);assert(b21OK);b21.coins=810;assert(B.Save(21,b21))
local lease21=copy(records.Player_21._lease);before=calls
local read21,write21=A.Load(21)
check(not write21 and read21.coins==810 and calls-before==1,'Retained admission stole foreign ownership')
check(records.Player_21._lease.token==lease21.token and records.Player_21._lease.expires==lease21.expires and records.Player_21.coins==810,'Retained admission changed foreign lease or data')
check(oldTransform(copy(records.Player_21))==nil,'Retired acquisition callback accepted foreign lease')
-- Same JobId is insufficient: a distinct module/acquisition remains foreign.
d=load(A,22);failedRelease(A,22,d);beforeFailures=6;A.Load(22)
now=records.Player_22._lease.expires
local c22,c22OK=C.Load(22);assert(c22OK);c22.coins=820;assert(C.Save(22,c22))
local lease22=copy(records.Player_22._lease)
local read22,write22=A.Load(22)
check(not write22 and read22.coins==820 and records.Player_22._lease.token==lease22.token and records.Player_22._lease.expires==lease22.expires,'Terminal admission stole newer same-job acquisition')
-- All acquisition responses lost: retain and acknowledge that exact attempt,
-- without starting another final-snapshot recovery or extending the lease.
d=load(A,23);failedRelease(A,23,d);beforeFailures=3;afterFailures=3
local temp23,write23=A.Load(23);local lease23=copy(records.Player_23._lease)
check(not write23 and temp23.coins==100,'Ambiguous acquisition exposed writable data')
before=calls;local back23,back23OK,_,warning23=A.Load(23)
check(back23OK and back23.coins==100 and warning23 and calls-before==1 and records.Player_23._lease.token==lease23.token and records.Player_23._lease.expires==lease23.expires,'Ambiguous acquisition identity was lost or lease extended')
back23.coins=830;check(A.Save(23,back23) and not A.Save(23,temp23) and not A.Save(23,d,true),'Ambiguous recovery bound a stale handle')
-- Recovery times out, then acquisition fails. Retain admission, never re-run
-- the expired recovery budget on a later load.
d=load(A,24);failedRelease(A,24,d);before=calls
beforeHook=function()now+=13;beforeFailures=3;error('slow recovery failure')end
local temp24,write24=A.Load(24)
check(not write24 and temp24.coins==100 and calls-before==4,'Timeout/acquisition exhaustion exceeded bounds')
before=calls;local back24,back24OK,_,warning24=A.Load(24)
check(back24OK and back24.coins==100 and warning24 and calls-before==1,'Timed-out recovery restarted or lost admission')
-- Repeated outages retain the checkpoint but never repeat final-save recovery.
d=load(A,25);failedRelease(A,25,d);beforeFailures=6;A.Load(25)
beforeFailures=3;before=calls;local temp25,write25=A.Load(25)
check(not write25 and temp25.coins==100 and calls-before==3 and not A.Save(25,temp25),'Repeated outage revived snapshot or lost confirmed fallback')
before=calls;local back25,back25OK=A.Load(25)
check(back25OK and back25.coins==100 and calls-before==1,'Repeated outage prevented exact-token reacquisition')
-- Fresh acquisition with no predecessor also reconciles lost responses safely.
afterFailures=3;local temp26,write26=A.Load(26);local lease26=copy(records.Player_26._lease)
check(not write26 and not A.Save(26,temp26),'Fresh ambiguous acquisition enabled saving')
local back26,back26OK=A.Load(26)
check(back26OK and back26.coins==0 and records.Player_26._lease.token==lease26.token and records.Player_26._lease.expires==lease26.expires,'Fresh ambiguous acquisition was not reconciled')
-- Contention re-invokes a terminal takeover callback after a newer same-job save.
d=load(A,27);failedRelease(A,27,d);beforeFailures=6;A.Load(27)
local lease27
retryHook=function()
 now=records.Player_27._lease.expires
 local c,cOK=C.Load(27);assert(cOK);c.coins=870;assert(C.Save(27,c));lease27=copy(records.Player_27._lease)
end
local read27,write27=A.Load(27)
check(not write27 and read27.coins==870 and records.Player_27.coins==870 and records.Player_27._lease.token==lease27.token and records.Player_27._lease.expires==lease27.expires,'Reinvoked admission callback used stale terminal ownership')
-- Acquisition committed, response lost, then another owner saved: do not reuse
-- the retained identity to adopt or refresh the newer owner's session.
d=load(A,28);failedRelease(A,28,d);beforeFailures=3;local lease28
afterHook=function()
 now=records.Player_28._lease.expires
 local b,bOK=B.Load(28);assert(bOK);b.coins=880;assert(B.Save(28,b));lease28=copy(records.Player_28._lease)
 afterFailures=1
end
local read28,write28=A.Load(28)
check(not write28 and read28.coins==880 and records.Player_28.coins==880 and records.Player_28._lease.token==lease28.token and records.Player_28._lease.expires==lease28.expires,'Ambiguous acquisition retry changed foreign save or lease')
-- A yielding cached admission and another rejoin still admit only one writer.
d=load(A,29);failedRelease(A,29,d);beforeFailures=6;A.Load(29);pauseNext=true
local back29,write29,duplicate29
co=coroutine.create(function()back29,write29=A.Load(29)end)
check(step(co)=='store','Cached admission fixture did not yield')
yieldWait=true;duplicate=coroutine.create(function()duplicate29={A.Load(29)}end)
check(step(duplicate)=='wait','Concurrent load bypassed cached admission lock')
yieldWait=false;step(co);step(duplicate)
check(write29 and back29.coins==100 and not duplicate29[2] and not A.Save(29,d,true),'Concurrent cached admission created duplicate or stale writer')
print('PASS '..checks..' bounded recovery/ownership/replay checks; cloned simulated persistence only')
'''
def run(payload,expected=None):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.recovery_policy_',dir=root/'tests',delete=False) as f:
        path=Path(f.name);f.write(payload)
    try:
        result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True)
        if expected:
            assert result.returncode!=0 and expected in result.stderr,result.stdout+result.stderr
            print('PASS negative control caught: '+expected)
        else:
            print(result.stdout,end='')
            if result.returncode: print(result.stderr,file=sys.stderr)
            result.check_returncode()
    finally:path.unlink()
payload=setup.replace('__LEASE__',lease)+source+checks
run(payload)
if '--negative-controls' in sys.argv:
    for old,new,expected in [
        ('if not Lease.Owns(raw,owner,session.token) then return nil end','-- omitted token guard','Old recovery overwrote or stole newer owner save'),
        ('saved.revision>=operation.revision','false','Old same-acquisition revision could overwrite newer save'),
        (' or bindings[data]~=session','','Old handle overwrote newer acquisition'),
        ('if deadline and os.clock()>=deadline then break end','-- omitted deadline','Recovery continued issuing requests past deadline'),
        ('if type(saved)=="table" and saved.token==session.token and saved.revision==operation.revision then return raw end','-- omitted committed-operation recognition','Lost release response was not reconciled idempotently'),
        ('lease.owner==owner and (token==nil or lease.token==token)','lease.owner==owner','Same-job distinct acquisition stole active lease'),
        ('snapshot=Profiles.Sanitize(data)','snapshot=data','Retained snapshot recovery failed or used mutated caller data'),
        ('local admission=admissions[userId]','local admission=nil','Terminal admission token forgotten after outage'),
        ('Lease.Owns(raw,owner,admission.terminalToken)','Lease.Owns(raw,owner)','Terminal admission stole newer same-job acquisition'),
        ('Lease.Owns(raw,owner,admission.terminalToken)','true','Old recovery overwrote or stole newer owner save'),
        ('if Lease.Owns(raw,owner,token) then return raw end','if Lease.Owns(raw,owner,token) then return Lease.Stamp(raw,owner,os.time(),token) end','Ambiguous acquisition identity was lost or lease extended'),
    ]:
        assert payload.count(old)==1,(old,payload.count(old))
        run(payload.replace(old,new),expected)
