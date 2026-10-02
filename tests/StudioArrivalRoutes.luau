-- Native pathfinding across new arrival features and existing spawn exits.
local results={}
for _,destination in ipairs({Vector3.new(-664,4,167),Vector3.new(-664,4,183),Vector3.new(-536,4,175),Vector3.new(-600,4,145),Vector3.new(-497,4,240),Vector3.new(-600,4,333)}) do
 local path=game:GetService("PathfindingService"):CreatePath({AgentRadius=2,AgentHeight=5,AgentCanJump=false,AgentCanClimb=false,Costs={Fountain=math.huge}})
 path:ComputeAsync(Vector3.new(-600,4,210),destination)
 table.insert(results,{x=destination.X,z=destination.Z,status=path.Status.Name,waypoints=#path:GetWaypoints()})
 assert(path.Status==Enum.PathStatus.Success,"Arrival route inaccessible")
 path:Destroy()
end
return results
