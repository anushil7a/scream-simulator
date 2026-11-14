-- GEOMETRY-ONLY LOCAL DRAFT. Never publish or attach live gameplay to this artifact.
assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0,
 "Compact city draft requires an unpublished local Studio file")
local city=workspace:WaitForChild("CompactCity")
assert(city:FindFirstChild("Ground") and city:FindFirstChild("Spawn"),"Draft geometry incomplete")
local count=0
for _,object in ipairs(city:GetDescendants()) do
 if object:IsA("BasePart") then
  assert(object.Anchored,"Static draft contains an unanchored part")
  count+=1
 end
end
assert(count==146,"Unexpected compact draft geometry count")
print("COMPACT_CITY_DRAFT: 146 anchored parts loaded. Geometry only; no gameplay or persistence.")
