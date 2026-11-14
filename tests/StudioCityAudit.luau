-- Run against the generated city in a disposable Studio place. This is engine evidence,
-- Moving residents do not count as static road/door obstructions.
-- not a replacement for walking/driving routes or measuring device frame times.
return function(world)
 local params=OverlapParams.new();params.FilterType=Enum.RaycastFilterType.Include;params.FilterDescendantsInstances={world};params.RespectCanCollide=true
 local seen,obstructions,doorways,aisles={}, {}, {}, {}
 local parts,solid,interiors=0,0,0
 for _,object in ipairs(world:GetDescendants()) do
  if object:IsA("BasePart") then parts+=1;if object.CanCollide then solid+=1 end end
  if object:IsA("Model") and object:GetAttribute("WalkableInterior") then
   interiors+=1
   local aisle=object:GetAttribute("InteriorAisle");local aisleSize=object:GetAttribute("InteriorAisleSize")
   if aisle and aisleSize then for _,part in ipairs(workspace:GetPartBoundsInBox(aisle,aisleSize,params)) do
    if part.CanCollide and part.Anchored then table.insert(aisles,part:GetFullName()) end
   end end
   local entrance=object:GetAttribute("Entrance")
   if entrance then for _,part in ipairs(workspace:GetPartBoundsInBox(entrance,Vector3.new(2.5,4,7),params)) do
    if part.CanCollide and part.Anchored then table.insert(doorways,part:GetFullName()) end
   end end
  end
 end
 for _,road in ipairs(world.Boulevards:GetChildren()) do
  if road.Name=="TrafficAvenue" or road.Name=="TrafficStreet" then
   local size=Vector3.new(road.Size.X-1,5,road.Size.Z-1)
   for _,part in ipairs(workspace:GetPartBoundsInBox(road.CFrame+Vector3.new(0,3.5,0),size,params)) do
    local vehicle=part:FindFirstAncestorOfClass("Model")
    if part.CanCollide and part.Anchored and part.Name~="MapEdge" and not part:IsDescendantOf(world.Boulevards) and not (vehicle and vehicle:GetAttribute("Vehicle")) and not seen[part] then
     seen[part]=true;table.insert(obstructions,part:GetFullName())
    end
   end
  end
 end
 return {parts=parts,solid=solid,interiors=interiors,roadObstructions=obstructions,blockedDoorways=doorways,blockedAisles=aisles,passed=#obstructions==0 and #doorways==0 and #aisles==0 and interiors>0}
end
