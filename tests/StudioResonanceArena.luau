-- Run in the Server DataModel of the local Resonance Arena place during Play.
assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0 and game.GameId==0)
local world=workspace:FindFirstChild("ScreamSimulatorWorld") or workspace:WaitForChild("ResonanceArena",5)
assert(world and world.Hall and world.TrainingPreview)
local player=assert(game.Players:GetPlayers()[1])
local character=assert(player.Character)
local humanoid=assert(character:FindFirstChildOfClass("Humanoid"))
local root=character:WaitForChild("HumanoidRootPart",5)
local ray=RaycastParams.new()
ray.FilterType=Enum.RaycastFilterType.Include
ray.FilterDescendantsInstances={world}
ray.RespectCanCollide=true
local function cast(origin,direction)
 return workspace:Raycast(origin,direction,ray)
end
local function floorAt(point,name)
 local hit=cast(point+Vector3.yAxis*10,Vector3.new(0,-25,0))
 assert(hit and hit.Instance.Name==name and math.abs(hit.Position.Y)<.01,"Missing or uneven walking surface")
end
local parts,solid=0,0
for _,item in ipairs(world:GetDescendants()) do
 if item:IsA("BasePart") then
  parts+=1
  if item.CanCollide then solid+=1 end
  assert(item.Anchored and not item.CanTouch and item.CanCollide==item.CanQuery,"Unexpected contact/query flags")
 end
end
assert(parts<=200 and solid<=28,"The draft exceeded its simple geometry budget")
assert(world.Hall.ArenaFloor.Size==Vector3.new(176,3,152))
local layout=require(game.ReplicatedStorage.Shared.ResonanceLayout)
local apron=world.Hall.TrainingPortalDeck
local threshold=world.Hall.SafeApronThreshold
assert(math.abs(apron.Position.Z-apron.Size.Z/2-layout.Apron.startZ)<.01 and apron.Size.X==layout.Apron.halfWidth*2)
assert(math.abs(threshold.Position.Z-threshold.Size.Z/2-layout.Apron.startZ)<.01 and threshold.Size.X==apron.Size.X)
local edges=0
for _,part in ipairs(world.Hall:GetChildren()) do
 if part.Name=="SafeApronEdge" then
  assert(math.abs(math.abs(part.Position.X)+part.Size.X/2-layout.Apron.halfWidth)<.01)
  assert(not part.CanCollide and not part.CanQuery and not part.CastShadow)
  edges+=1
 end
end
assert(edges==2 and not threshold.CanCollide and not threshold.CanQuery)
local prompt=assert(world.Hall:FindFirstChild("TrainingPortal",true))
local entry=Vector3.new(layout.HallEntry.x,3.8,layout.HallEntry.z)
assert((entry-prompt.Parent.Position).Magnitude<prompt.MaxActivationDistance and layout.IsSafeApron(entry))
floorAt(entry,"ArenaFloor")

local cover=cast(Vector3.new(0,3.5,-25),Vector3.new(0,0,50))
assert(cover and cover.Instance.Name=="MixingDesk","Central obstacle does not block chest-height line of sight")
for _,side in ipairs({-1,1}) do
 assert(not cast(Vector3.new(side*18,3.5,-24),Vector3.new(0,0,48)),"Central flank obstructed")
end
floorAt(Vector3.new(0,3.5,51),"ArenaFloor")
floorAt(Vector3.new(0,3.5,240),"TrainingDeck")
local limit=54.75
local exits={}
for _,sx in ipairs({-1,1}) do
 for _,sz in ipairs({-1,1}) do
  local spawn=world.Hall["Spawn_"..sx.."_"..sz]
  local start=Vector3.new(spawn.Position.X,3.5,spawn.Position.Z)
  floorAt(start,"ArenaFloor")
  local combatPeek=Vector3.new(sx*34,3.5,sz*20)
  local line=start-combatPeek
  local shelter=cast(combatPeek,line)
  assert(line.Magnitude<limit and shelter and shelter.Instance.Name=="SpeakerCover","An in-range lane sees into the spawn")
  for _,finish in ipairs({Vector3.new(sx*69,3.5,sz*23),Vector3.new(sx*33,3.5,sz*55)}) do
   local offset=finish-start
   for _,margin in ipairs({-2,0,2}) do
    local pad=offset.Unit:Cross(Vector3.yAxis)*margin
    assert(not cast(start+pad,offset),"A spawn exit is obstructed")
    for step=0,4 do floorAt(start+pad+offset*(step/4),"ArenaFloor") end
   end
   exits[#exits+1]={start,finish}
  end
 end
end
-- Each movement leg is independent; no jump or teleport through its corridor.
local walkSpeed=humanoid.WalkSpeed
local previousJump=humanoid:GetStateEnabled(Enum.HumanoidStateType.Jumping)
humanoid.WalkSpeed=16
humanoid:SetStateEnabled(Enum.HumanoidStateType.Jumping,false)
for i,exit in ipairs(exits) do
 character:PivotTo(CFrame.new(exit[1]))
 root.AssemblyLinearVelocity=Vector3.zero
 task.wait(.15)
 humanoid:MoveTo(exit[2])
 local deadline=os.clock()+5
 repeat task.wait(.05) until (root.Position-exit[2]).Magnitude<2 or os.clock()>=deadline
 assert((root.Position-exit[2]).Magnitude<2,"Humanoid failed to walk spawn exit "..i)
end
humanoid.WalkSpeed=walkSpeed
humanoid:SetStateEnabled(Enum.HumanoidStateType.Jumping,previousJump)
local practice=layout.Practice
local rails={
 {28,248,45,248}, {29,248,45,248}, {31,248,45,248}, {32,248,45,248},
 {-29,248,-45,248}, {20,230,20,215}, {20,265,20,282}, {29,265,44,281},
}
local before=character:GetPivot()
local originalOwner=root:GetNetworkOwner()
root:SetNetworkOwner(nil)
local checked=0
local failed
for i,leg in ipairs(rails) do
 local x,z,targetX,targetZ=table.unpack(leg)
 character:PivotTo(CFrame.new(x,3.8,z))
 root.AssemblyLinearVelocity=Vector3.zero
 humanoid:MoveTo(root.Position)
 task.wait(.3)
 local settled=os.clock()+.7
 repeat task.wait() until humanoid.FloorMaterial~=Enum.Material.Air or os.clock()>=settled
 local origin=root.Position
 humanoid:MoveTo(Vector3.new(targetX,origin.Y,targetZ))
 humanoid.Jump=true
 local deadline=os.clock()+1.4
 local jumped=false
 repeat
  task.wait()
  local position=root.Position
  jumped=jumped or position.Y>origin.Y+3
  if not layout.Contains(practice,position) or position.Y<0 then
   failed="Jump bypassed practice rail on leg "..i.." at "..tostring(position)
   break
  end
 until os.clock()>=deadline
 if failed then break end
 if not jumped then failed="No jump occurred on practice leg "..i;break end
 checked+=1
end
humanoid:MoveTo(root.Position)
character:PivotTo(before)
root.AssemblyLinearVelocity=Vector3.zero
root:SetNetworkOwner(originalOwner)
assert(not failed,failed)
return {parts=parts,solid=solid,walked=#exits,railJumps=checked,normalRange=limit}
