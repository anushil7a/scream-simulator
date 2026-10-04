-- Keep authored fallback geometry visible unless every required mesh and texture loads.
local Collection=game:GetService("CollectionService")
local Content=game:GetService("ContentProvider")
local pending=setmetatable({},{__mode="k"})
local function apply(model)
 if pending[model] then return end
 local detail=model:FindFirstChild("DetailedVisual")
 local fallback=model:FindFirstChild("FallbackVisual")
 if not detail or not fallback then return end
 local ticket={};pending[model]=ticket
 -- Re-entry may reuse an instance whose fallback was hidden on a prior load.
 for _,part in fallback:GetDescendants() do if part:IsA("BasePart") then part.LocalTransparencyModifier=0 end end
 local meshes={};local expected={}
 for _,part in detail:GetDescendants() do
  if part:IsA("BasePart") then part.LocalTransparencyModifier=1 end
  if part:IsA("MeshPart") then
   table.insert(meshes,part)
   for _,id in {part.MeshId,part.TextureID} do if id~="" then expected[id]=false end end
  end
 end
 task.spawn(function()
  local ok=pcall(function()
   Content:PreloadAsync(meshes,function(id,status)
    if expected[id]~=nil then expected[id]=status==Enum.AssetFetchStatus.Success end
   end)
  end)
  if pending[model]~=ticket then return end
  if not model:IsDescendantOf(workspace) then pending[model]=nil;return end
  local loaded=ok and #meshes>0
  for _,success in expected do if not success then loaded=false end end
  if loaded then
   for _,part in fallback:GetDescendants() do if part:IsA("BasePart") then part.LocalTransparencyModifier=1 end end
   for _,part in detail:GetDescendants() do if part:IsA("BasePart") then part.LocalTransparencyModifier=0 end end
  end
  model:SetAttribute("LocalVisualStatus",loaded and "Detailed" or "Fallback")
 end)
end
Collection:GetInstanceAddedSignal("OptionalLandmarkVisual"):Connect(apply)
Collection:GetInstanceRemovedSignal("OptionalLandmarkVisual"):Connect(function(model) pending[model]=nil end)
for _,model in Collection:GetTagged("OptionalLandmarkVisual") do apply(model) end
