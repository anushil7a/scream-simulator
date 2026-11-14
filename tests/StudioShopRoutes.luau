-- Run on the server in a fresh disposable Play session after City/World builds.
-- Engine navigation evidence; does not replace physical player traversal tests.
return function(world)
 assert(game:GetService("RunService"):IsRunning() and game.PlaceId==0,"Local Play session required")
 local failures={};local count=0
 for _,shop in ipairs(world:GetDescendants()) do
  if shop:IsA("Model") and shop:GetAttribute("WalkableInterior") then
   local entrance=shop:GetAttribute("Entrance");local aisle=shop:GetAttribute("InteriorAisle")
   assert(entrance and aisle,"Missing shop route metadata: "..shop:GetFullName())
   local path=game:GetService("PathfindingService"):CreatePath({AgentRadius=2,AgentHeight=5,AgentCanJump=false,AgentCanClimb=false})
   local ok,err=pcall(function() path:ComputeAsync(entrance.Position+entrance.LookVector*8,aisle.Position) end)
   count+=1
   if not ok or path.Status~=Enum.PathStatus.Success then
    table.insert(failures,{shop=shop:GetFullName(),status=ok and path.Status.Name or tostring(err)})
   end
   path:Destroy()
  end
 end
 return {shops=count,failures=failures,passed=count>0 and #failures==0}
end
