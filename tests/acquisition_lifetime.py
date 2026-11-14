"""Actual acquisition protocol, cloned simulated persistence and controlled time.
No native Roblox, live DataStore or real network evidence.
"""
import argparse
from profile_recovery_policy import setup, source, lease, run

common=r'''
end
local A,B,C=loadModule('A'),loadModule('B'),loadModule('A')
local checks=0
local function check(v,message)assert(v,message);checks+=1 end
local function ambiguous()
 records.Player_101={coins=100}
 afterFailures=3
 local data,writable=A.Load(101)
 check(not writable and data.coins==100,'Lost acquisition responses granted write access')
 return data,copy(records.Player_101._lease)
end
local function exclusive(data)
 local before=copy(records.Player_101._lease)
 local _,other=B.Load(101)
 check(not other and records.Player_101._lease.token==before.token and records.Player_101._lease.expires==before.expires,'Competitor acquired or changed admitted lease')
 data.coins=150
 check(A.Save(101,data) and records.Player_101.coins==150,'Admitted progress could not save')
 check(A.Save(101,data,true),'Admitted profile could not release')
 local nextData,nextOK=B.Load(101)
 check(nextOK and nextData.coins==150,'Subsequent owner lost saved progress')
end
'''
scenarios={
 'expired':r'''
local temporary,old=ambiguous();now=old.expires+1
local data,writable=A.Load(101)
check(writable and records.Player_101._lease.expires-now>=120,'Expired acquisition did not obtain usable lease lifetime')
check(records.Player_101._lease.token==old.token and data.coins==100 and not A.Save(101,temporary),'Expired reacquisition changed identity/data or bound temporary handle')
exclusive(data)
''',
 'near':r'''
local temporary,old=ambiguous();now=old.expires-1
local data,writable=A.Load(101)
check(writable and records.Player_101._lease.expires-now>=120,'Near-expiry acquisition did not obtain usable lease lifetime')
check(records.Player_101._lease.token==old.token and not A.Save(101,temporary),'Near-expiry admission changed token or bound temporary handle')
now+=60 -- first ordinary autosave opportunity
exclusive(data)
''',
 'response_expired':r'''
records.Player_101={coins=100};afterHook=function()now+=181 end
local before=calls;local data,writable=A.Load(101)
check(writable and records.Player_101._lease.expires-now>=120 and calls-before==2,'Expired response granted writable admission')
exclusive(data)
''',
 'response_near':r'''
records.Player_101={coins=100};afterHook=function()now+=61 end
local before=calls;local data,writable=A.Load(101)
check(writable and records.Player_101._lease.expires-now>=120 and calls-before==2,'Short-lifetime response granted writable admission')
exclusive(data)
''',
 'renewal_outage':r'''
local temporary,old=ambiguous();now=old.expires+1;beforeFailures=3
local before=calls;local fallback,writable=A.Load(101)
check(not writable and fallback.coins==100 and calls-before==3 and records.Player_101._lease.expires==old.expires,'Renewal outage claimed admission or changed lease')
check(not A.Save(101,temporary) and not A.Save(101,fallback),'Renewal outage granted temporary write authority')
local data,ok=A.Load(101);check(ok and records.Player_101._lease.expires-now>=120,'Renewal did not recover after outage')
exclusive(data)
''',
 'renewal_lost':r'''
local temporary,old=ambiguous();now=old.expires-1;afterFailures=3
local fallback,writable=A.Load(101)
check(not writable and fallback.coins==100 and records.Player_101._lease.expires>old.expires,'Lost renewal responses claimed admission or failed to renew')
local data,ok=A.Load(101)
check(ok and records.Player_101._lease.expires-now>=120 and records.Player_101._lease.token==old.token,'Lost renewal response could not reconcile exact token')
check(not A.Save(101,fallback) and not A.Save(101,temporary),'Lost renewal response bound stale data')
exclusive(data)
''',
 'foreign_race':r'''
local temporary,old=ambiguous();now=old.expires+1
local winner,won
retryHook=function()
 local ok;winner,ok=B.Load(101);assert(ok);winner.coins=500;assert(B.Save(101,winner));won=copy(records.Player_101._lease)
end
local fallback,writable=A.Load(101)
check(not writable and fallback.coins==500 and records.Player_101.coins==500 and records.Player_101._lease.token==won.token and records.Player_101._lease.expires==won.expires,'Renewal callback overwrote or adopted foreign ownership')
check(not A.Save(101,temporary) and not A.Save(101,fallback),'Losing renewal acquired write authority')
winner.coins=600;check(B.Save(101,winner) and records.Player_101.coins==600,'Foreign winner could not save after rejected renewal')
''',
 'same_job_race':r'''
local temporary,old=ambiguous();now=old.expires+1
local winner,won
retryHook=function()
 local ok;winner,ok=C.Load(101);assert(ok);winner.coins=500;assert(C.Save(101,winner));won=copy(records.Player_101._lease)
end
local fallback,writable=A.Load(101)
check(not writable and fallback.coins==500 and records.Player_101.coins==500 and records.Player_101._lease.token==won.token and records.Player_101._lease.expires==won.expires,'Renewal callback adopted newer same-job token')
check(not A.Save(101,temporary) and not A.Save(101,fallback),'Same-job loser acquired write authority')
winner.coins=600;check(C.Save(101,winner) and records.Player_101.coins==600,'Same-job winner could not save after rejected renewal')
''',
 'foreign_during_response':r'''
local temporary,old=ambiguous();now=old.expires-1
local winner,won
afterHook=function()
 now=records.Player_101._lease.expires+1
 local ok;winner,ok=B.Load(101);assert(ok);winner.coins=500;assert(B.Save(101,winner));won=copy(records.Player_101._lease)
end
local fallback,writable=A.Load(101)
check(not writable and fallback.coins==500 and records.Player_101.coins==500 and records.Player_101._lease.token==won.token and records.Player_101._lease.expires==won.expires,'Stale acquisition response admitted after foreign takeover')
check(not A.Save(101,temporary) and not A.Save(101,fallback),'Stale response created writable handle')
winner.coins=600;check(B.Save(101,winner) and records.Player_101.coins==600,'Response-race winner lost save authority')
''',
 'slow_exhaustion':r'''
records.Player_101={coins=100}
local function delay()now+=181;afterHook=delay end
afterHook=delay;local before=calls
local fallback,writable=A.Load(101);afterHook=nil
check(not writable and fallback.coins==100 and calls-before==3,'Slow acquisition responses exceeded bound or admitted expired lease')
check(not A.Save(101,fallback),'Slow exhausted response enabled saving')
local data,ok=A.Load(101);check(ok and records.Player_101._lease.expires-now>=120,'Slow-response recovery failed')
exclusive(data)
''',
 'boundary':r'''
local _,old=ambiguous();now=old.expires-120
local data,writable=A.Load(101)
check(writable and records.Player_101._lease.expires==old.expires,'Sufficient-lifetime acknowledgement unnecessarily renewed or failed')
now+=60;exclusive(data)
''',
 'checkpoint_metadata':r'''
records.Player_101={coins=100,_lease={owner='prior',token='prior-token',expires=now-1},_save={token='prior-token',revision=7}}
afterFailures=3;local temporary,writable,_,warning=A.Load(101)
check(not writable and temporary.coins==100 and warning,'Ambiguous recovered checkpoint setup failed')
now=records.Player_101._lease.expires+1
local data,ok,_,recovered=A.Load(101)
check(ok and recovered and data.coins==100 and records.Player_101._save.token=='prior-token' and records.Player_101._save.revision==7,'Exact-token renewal changed checkpoint or recovery metadata')
exclusive(data)
''',
 'renewal_lost_foreign':r'''
local temporary,old=ambiguous();now=old.expires-1
local winner,won
afterHook=function()
 now=records.Player_101._lease.expires+1
 local ok;winner,ok=B.Load(101);assert(ok);winner.coins=500;assert(B.Save(101,winner));won=copy(records.Player_101._lease)
 afterFailures=1 -- lose only A's renewal response, after B's successful save
end
local fallback,writable=A.Load(101)
check(not writable and fallback.coins==500 and records.Player_101.coins==500 and records.Player_101._lease.token==won.token and records.Player_101._lease.expires==won.expires,'Lost renewal response replaced newer foreign lease or save')
check(not A.Save(101,temporary) and not A.Save(101,fallback),'Lost renewal response adopted foreign write authority')
winner.coins=600;check(B.Save(101,winner) and records.Player_101.coins==600,'Foreign winner could not save after lost renewal response')
''',
}

def payload(name,production=source):
    return setup.replace('__LEASE__',lease)+production+common+scenarios[name]+"\nprint('PASS '..checks..' acquisition lifetime checks: "+name+"')\n"

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario',choices=scenarios)
    parser.add_argument('--negative-controls',action='store_true')
    args=parser.parse_args()
    for name in ([args.scenario] if args.scenario else scenarios):run(payload(name))
    if args.negative_controls:
        for name,old,new,expected in [
            ('expired','return Lease.Stamp(raw,owner,os.time(),token)','return raw','Expired acquisition did not obtain usable lease lifetime'),
            ('near','local MIN_ADMISSION_LIFETIME=120','local MIN_ADMISSION_LIFETIME=0','Near-expiry acquisition did not obtain usable lease lifetime'),
            ('response_expired','if usableAcquisition(result,token) then','if true then','Expired response granted writable admission'),
            ('foreign_race','if not Lease.CanAcquire(raw,owner,os.time(),token) then','if false then','Renewal callback overwrote or adopted foreign ownership'),
            ('same_job_race','Lease.CanAcquire(raw,owner,os.time(),token)','Lease.CanAcquire(raw,owner,os.time())','Renewal callback adopted newer same-job token'),
        ]:
            assert source.count(old)==1,(old,source.count(old))
            run(payload(name,source.replace(old,new)),expected)
