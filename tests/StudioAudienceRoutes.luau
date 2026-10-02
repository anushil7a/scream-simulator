-- Run in the Server datamodel after a normal city build.
local results={}
for _,x in ipairs({140,150,160}) do
 local path=game:GetService("PathfindingService"):CreatePath({AgentRadius=2,AgentHeight=5,AgentCanJump=false,AgentCanClimb=false})
 path:ComputeAsync(Vector3.new(200,4,403),Vector3.new(x,4,415))
 table.insert(results,{x=x,status=path.Status.Name,waypoints=#path:GetWaypoints()})
 assert(path.Status==Enum.PathStatus.Success,"Inaccessible performance audience position")
 path:Destroy()
end
return results
