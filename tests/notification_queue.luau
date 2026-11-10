local Queue=require('../src/StarterPlayer/StarterPlayerScripts/NotificationQueue')
local checks=0
local function check(ok,message)assert(ok,message);checks+=1 end
local q=Queue.new()
local function frame(dt,visible)return q:Step(dt or 1/60,visible~=false)end
local function hold(text,seconds)
 for _=1,math.floor(seconds*60) do check(frame()==text,'Notice overwritten before readable dwell: '..text) end
end
q:Push('LEVEL 10');q:Push('Reward');q:Push('Complete');q:Push('Flowers watered')
check(frame()=='LEVEL 10','Same-frame milestone lost')
hold('LEVEL 10',3.9)
for _=1,12 do frame()end
check(frame()=='Reward','Reward order lost');hold('Reward',3.7)
for _=1,30 do frame()end
check(frame()=='Complete','Completion order lost');hold('Complete',3.5)
for _=1,50 do frame()end
check(frame()=='Flowers watered','Garden follow-up order lost')
q=Queue.new();q:Push('Milestone');frame();hold('Milestone',1)
q:Push('Reward');q:Push('Save failed',true)
check(frame()=='Save failed','Critical failure queued behind routine notice')
q:Push('Second error',true);q:Push('Save failed',true)
hold('Save failed',3.9)
for _=1,12 do frame()end
check(frame()=='Second error','Distinct critical error overwritten')
for _=1,250 do frame()end
check(frame()=='Milestone','Interrupted milestone lost');hold('Milestone',3.6)
q=Queue.new();q:Push('Unique');frame()
for _=1,600 do q:Push('Unique');frame()end
check(#q.pending==0,'Duplicate spam grew queue')
q=Queue.new();q:Push('Paused');frame();q:Step(999,false)
check(frame()=='Paused','Unfocused time consumed notice')
q:Step(999,true);hold('Paused',3.7)
q=Queue.new();q:Push('ON',false,'voice');frame();q:Push('OFF',false,'voice')
check(frame()=='OFF' and #q.pending==0,'Obsolete voice status replayed')
for _=1,250 do frame()end
check(frame()=='','Expired voice status replayed')
q=Queue.new();q:Push('Critical',true)
for i=1,100 do q:Push('Routine '..i)end
check(#q.pending==Queue.Limit and frame()=='Critical','Overflow displaced critical active notice or exceeded bound')
check(q.pending[#q.pending].text=='Routine 100','Newest routine missing after overflow')
q=Queue.new();q:Push('x');q:Push('x');check(#q.pending==0,'Active duplicate queued')
q:Push('y');q:Push('y');check(#q.pending==1,'Pending duplicate queued')
q:Push(nil);q:Push('');check(#q.pending==1,'Invalid notice queued')
-- Replacing an active keyed notice must not jump past waiting failures.
local off='Screams stay OFF. Finish mic setup or wait for gameplay to be ready, then turn them on.'
local saving='Saving is unavailable. Progress from here is temporary; rejoin before continuing progression.'
local on='Screams ON. Normal speech can fire attacks. Go quiet, then speak. Turn OFF to talk freely; voice chat is unchanged.'
q=Queue.new();q:Push(off,true,'voice');frame();q:Push(saving,true);q:Push(on,false,'voice')
check(frame()==saving,'Keyed normal replacement bypassed waiting critical warning')
check(#q.pending==1 and q.pending[1].text==on,'Voice replacement lost or obsolete OFF survived')
hold(saving,4)
for _=1,30 do frame()end
check(frame()==on,'Voice replacement did not follow critical warning')
-- Further toggles coalesce pending voice state without interrupting the warning.
q=Queue.new();q:Push(off,true,'voice');frame();q:Push(saving,true);q:Push('Second error',true)
q:Push(on,false,'voice');frame();local remaining=q.active.remaining
q:Push('Screams OFF',false,'voice');q:Push(on,false,'voice')
check(q.active.text==saving and q.active.remaining==remaining,'Voice toggles changed active critical dwell')
check(#q.pending==2 and q.pending[1].text=='Second error' and q.pending[2].text==on,'Voice coalescing reordered critical FIFO')
-- Urgent replacement also respects an already waiting urgent notice.
q=Queue.new();q:Push(off,true,'voice');frame();q:Push(saving,true);q:Push('New setup failure',true,'voice')
check(frame()==saving and q.pending[1].text=='New setup failure','Keyed urgent replacement bypassed waiting critical warning')
-- With only routine pending work, preserve FIFO rather than promoting fresh status.
q=Queue.new();q:Push('ON',false,'voice');frame();q:Push('Reward');q:Push('OFF',false,'voice')
check(frame()=='Reward' and q.pending[1].text=='OFF','Keyed replacement bypassed waiting routine notice')
print('PASS '..checks..' notification frame/dwell/order/priority/coalescing assertions')
