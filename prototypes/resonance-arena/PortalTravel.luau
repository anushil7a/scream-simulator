-- Shared by the guarded combat preview and its geometry-only sibling.
local shared=game:GetService("ReplicatedStorage").Shared
local combatPreview=shared:FindFirstChild("Config")~=nil
local Travel={}
local prepare

function Travel.SetPreparation(callback)
 assert(combatPreview and not prepare,"Unexpected Resonance portal setup")
 prepare=callback
end

function Travel.Move(player,anchor,distance,destination)
 local character=player.Character
 local root=character and character:FindFirstChild("HumanoidRootPart")
 local humanoid=character and character:FindFirstChildOfClass("Humanoid")
 local function ready()
  return root and root.Parent==character and humanoid and humanoid.Parent==character and humanoid.Health>0
   and player.Character==character and (root.Position-anchor.Position).Magnitude<=distance
 end
 if not ready() then return false end
 if combatPreview and (not prepare or not prepare(player,character) or not ready()) then return false end
 character:PivotTo(destination)
 root.AssemblyLinearVelocity=Vector3.zero
 root.AssemblyAngularVelocity=Vector3.zero
 return true
end

return Travel
