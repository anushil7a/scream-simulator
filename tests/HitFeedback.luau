local Feedback=require('../src/StarterPlayer/StarterPlayerScripts/HitFeedback')
local f=Feedback.new();local checks=0
local function check(v,msg)assert(v,msg);checks+=1 end
check(f:Read(0)==nil,'Feedback visible before a hit')
check(f:Accept(1,3,1) and f:Read(1)==3,'Confirmed hit missing')
check(not f:Accept(1,3,1.5) and f:Read(1.71)==nil,'Duplicate refreshed expired feedback')
check(f:Accept(1,8,2) and f:Read(2)==8,'Cumulative damage did not update')
check(not f:Accept(1,5,2.1) and f:Read(2.1)==8,'Older total replaced damage')
check(f:Accept(2,2,3) and f:Read(3)==2,'New scream did not reset total')
check(not f:Accept(1,100,3.1) and f:Read(3.1)==2,'Previous scream replaced current')
for _,args in ipairs({{0,2,4},{2,0,4},{2,-1,4},{2,math.huge,4},{2,0/0,4},{2,32769,4},{2,3,0/0}})do
 check(not f:Accept(table.unpack(args)),'Invalid payload accepted')
end
check(f:DiscardThrough(4) and f:Read(3.2)==nil,'Respawn did not clear displayed damage')
check(not f:Accept(3,20,4) and not f:Accept(4,30,4),'Pre-respawn delayed attack revived feedback')
check(f:Accept(5,2,5) and f:Read(5)==2,'New attack after respawn lost feedback')
check(f:DiscardThrough(1) and not f:Accept(5,10,6),'Stale discard allowed current attack feedback to revive')
check(not f:DiscardThrough(0/0) and not f:DiscardThrough(-1) and not f:DiscardThrough(1.5),'Invalid discard accepted')
check(f:Accept(6,3,7) and f:Read(7)==3,'Repeated respawn blocked fresh sequence')
print('PASS '..checks..' pure server-confirmed hit presentation checks')
