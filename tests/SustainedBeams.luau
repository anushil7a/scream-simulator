local Beams=require("../src/StarterPlayer/StarterPlayerScripts/SustainedBeams")
local created,destroyed=0,0
local beams=Beams.new(function()
 created+=1;return {}
end,function(visual,aim)
 visual.aim=aim
end,function(visual)
 assert(not visual.destroyed,"Double destruction")
 visual.destroyed=true;destroyed+=1
end)
assert(beams:Update(1,0,"first"))
local first=beams.entries[1].visual
for i=1,20 do assert(beams:Update(1,i*.2,i)) end
assert(created==1 and beams.count==1 and first.aim==20,"Repeated ticks allocated new effects")
beams:Expire(4.49)
assert(not first.destroyed,"Beam expired before its refreshed deadline")
beams:Expire(4.5)
assert(first.destroyed and beams.count==0,"Missing updates left a stale beam")
for i=1,Beams.Limit do assert(beams:Update(i,5,i)) end
assert(not beams:Update(99,5,"overflow") and beams.count==Beams.Limit,"Visual cap exceeded")
beams:Remove(1);beams:Remove(1)
assert(beams:Update(99,5.1,"replacement") and beams.count==Beams.Limit,"Explicit end did not free a slot")
assert(beams:Update(100,5.6,"after expiry") and beams.count==1,"Expired entries blocked new attackers")
beams:Clear()
assert(beams.count==0 and next(beams.entries)==nil and created==destroyed,"Cleanup leaked effects")
assert(beams:Update(101,6,"after clear"),"Clear unexpectedly disabled reusable manager")
beams:Destroy()
local countAtDestroy=created
beams:Destroy();beams:Clear();beams:Remove(101);beams:Expire(7)
assert(not beams:Update(102,7,"late callback"),"Late callback recreated destroyed manager")
assert(created==countAtDestroy and destroyed==created and beams.count==0,"Teardown leaked or recreated beam visuals")
print("PASS sustained beam reuse, capacity, stop, timeout and terminal teardown checks (mock visuals)")
