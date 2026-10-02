-- Run in normal Studio Play on the server after city construction.
-- Tests navigation geometry, not actual player input or a crowd soak.
local V=Vector3.new
local cases={
 {"lookout balcony",V(-240,4,427),V(-240,6.3,452)},
 {"lookout cabin",V(-240,4,427),V(-240,6.3,462)},
 {"pier",V(525,4,403),V(525,5,580)},
}
for i=1,18,3 do
 local x=-660+(i-1)*77;local z=470+(i%3)*25
 table.insert(cases,{"beach rest "..i,V(x+4,4,403),V(x+4,4,z-2)})
end
local results={}
for _,case in cases do
 local path=game:GetService("PathfindingService"):CreatePath({AgentRadius=2,AgentHeight=5,AgentCanJump=false,AgentCanClimb=false})
 local ok,message=pcall(function() path:ComputeAsync(case[2],case[3]) end)
 local status=path.Status.Name;local count=#path:GetWaypoints();path:Destroy()
 table.insert(results,{name=case[1],passed=ok and status=="Success",status=status,waypoints=count,error=not ok and tostring(message) or nil})
end
local seats=0
for _,item in workspace.ScreamSimulatorWorld:GetDescendants() do
 if item:IsA("Seat") and item.Name=="BeachSeat" then
  seats+=1
  assert(item:FindFirstChildOfClass("ProximityPrompt"),"Beach seat missing interaction")
 end
end
assert(seats==18,"Expected eighteen usable beach loungers")
return {routes=results,beachSeats=seats}
