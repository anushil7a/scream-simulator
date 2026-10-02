-- Shared targeting rule; the server repeats it before granting conversation access.
local Rules={}
function Rules.CanReachNpc(character,npc,maxDistance)
 local root=character and character:FindFirstChild("HumanoidRootPart")
 local target=npc and npc:FindFirstChild("HumanoidRootPart")
 local humanoid=character and character:FindFirstChildOfClass("Humanoid")
 local resident=npc and npc:FindFirstChildOfClass("Humanoid")
 if not root or not target or not humanoid or not resident or humanoid.Health<=0 or resident.Health<=0
  or (root.Position-target.Position).Magnitude>maxDistance then return false end
 local origin=(character:FindFirstChild("Head") or root).Position
 local destination=(npc:FindFirstChild("Head") or target).Position
 local ray=RaycastParams.new();ray.FilterType=Enum.RaycastFilterType.Exclude
 ray.FilterDescendantsInstances={character,npc};ray.RespectCanCollide=true
 -- Residents do not collide with one another; a passing crowd should not
 -- prevent conversation, but walls, vehicles and other solid cover should.
 ray.CollisionGroup="Residents"
 return workspace:Raycast(origin,destination-origin,ray)==nil
end
return Rules
