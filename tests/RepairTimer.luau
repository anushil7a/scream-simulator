local Timer=require("../src/ServerScriptService/RepairTimer")
local now,scheduled,peak,repairs,retries,checks=0,0,0,0,0,0
local queue={};local valid=true;local occupied=false
local function check(v,msg) assert(v,msg);checks+=1 end
local timer=Timer.new(function() return now end,function(delay,fn)
 scheduled+=1;table.insert(queue,{at=now+delay,fn=fn});peak=math.max(peak,#queue)
end,function() return valid end,function()
 if occupied then return false end
 repairs+=1;return true
end,function(delay) assert(delay==5);retries+=1 end)
local function advance(t)
 while true do
  table.sort(queue,function(a,b) return a.at<b.at end)
  if not queue[1] or queue[1].at>t then break end
  local next=table.remove(queue,1);now=next.at;next.fn()
 end
 now=t
end
for i=0,599 do advance(i*.2);timer:Touch(120) end
check(peak==1 and scheduled==1,"Repeated hits accumulated repair callbacks")
advance(120)
check(repairs==0 and #queue==1,"Old deadline repaired through later hits")
advance(239.8)
check(repairs==1 and not timer.pending,"Latest deadline failed to repair")
check(scheduled==2,"600 hits should need two scheduled wakeups")
occupied=true;timer:Touch(10);advance(249.8)
check(retries==1 and repairs==1 and #queue==1,"Occupied repair did not defer")
timer:Touch(20);advance(254.8)
check(repairs==1 and #queue==1,"New damage during occupied retry lost its deadline")
occupied=false;advance(269.8)
check(repairs==2 and not timer.pending,"Object did not repair after occupant left")
timer:Touch(10);valid=false;advance(279.8)
check(not timer.pending and #queue==0 and repairs==2,"Removed object retained timer")
print("PASS "..checks.." simulated repair scheduling checks; 600 hits -> 2 wakeups, peak pending 1; no engine timing/FPS claim")
