-- Append to LandmarkVisuals in an unpublished Studio city copy.
-- Real content loading plus local texture failure/tag re-entry; not a network streaming test.
task.spawn(function()
 assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0)
 local world=workspace:WaitForChild("ScreamSimulatorWorld",20)
 local m=world:WaitForChild("Plaça del Sol",20):WaitForChild("MosaicFountain",20)
 local checks=0;local mesh=m.DetailedVisual:FindFirstChildWhichIsA("MeshPart",true);local original=mesh.TextureID
 local function check(value,message) assert(value,message);checks+=1 end
 local function awaitStatus(status)
  local deadline=os.clock()+15
  repeat task.wait(.1) until m:GetAttribute("LocalVisualStatus")==status or os.clock()>deadline
  check(m:GetAttribute("LocalVisualStatus")==status,"Expected "..status)
 end
 local function visible(group)
  local n=0;for _,part in group:GetDescendants() do if part:IsA("BasePart") and part.LocalTransparencyModifier==0 then n+=1 end end;return n
 end
 local function reload(texture)
  Collection:RemoveTag(m,"OptionalLandmarkVisual");m:SetAttribute("LocalVisualStatus",nil)
  mesh.TextureID=texture;Collection:AddTag(m,"OptionalLandmarkVisual")
 end
 local ok,err=xpcall(function()
  awaitStatus("Detailed")
  check(visible(m.DetailedVisual)==3 and visible(m.FallbackVisual)==0,"Detailed selection incorrect")
  reload("rbxassetid://0");awaitStatus("Fallback")
  check(visible(m.DetailedVisual)==0 and visible(m.FallbackVisual)==28,"Fallback failed after re-entry")
  reload(original);awaitStatus("Detailed")
  check(visible(m.DetailedVisual)==3 and visible(m.FallbackVisual)==0,"Detailed recovery failed")
  local solids=0;for _,part in m:GetDescendants() do if part:IsA("BasePart") and part.CanCollide then solids+=1 end end
  check(solids==3,"Visual selection changed authoritative collision")
 end,debug.traceback)
 if mesh.TextureID~=original then reload(original) end
 workspace:SetAttribute("LandmarkFallbackResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
end)
