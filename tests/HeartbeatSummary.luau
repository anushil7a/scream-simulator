local summarize=require('./support/HeartbeatSummary')
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
check(summarize({}).samples==0,'Empty sample fabricated timing')
local one=summarize({.02});check(one.samples==1 and one.meanMs==20 and one.p95Ms==20 and one.maxMs==20,'Single interval incorrect')
local values={};for i=1,100 do values[i]=i/1000 end
local result=summarize(values)
check(result.samples==100 and math.abs(result.meanMs-50.5)<1e-6,'Mean/count incorrect')
check(result.p95Ms==95 and result.maxMs==100,'Nearest-rank percentile incorrect')
check(result.over50ms==50,'Slow interval threshold incorrect')
check(values[1]==.001 and values[100]==.1,'Summary mutated source sample')
local filtered=summarize({0,-1,0/0,math.huge,'bad',.05})
check(filtered.samples==1 and filtered.over50ms==0,'Invalid intervals counted or 50ms threshold wrong')
print('PASS '..checks..' synthetic heartbeat summary checks; no engine performance measurement')
