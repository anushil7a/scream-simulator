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
print('PASS '..checks..' notification frame/dwell/order/priority/coalescing assertions')
