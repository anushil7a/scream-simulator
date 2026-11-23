-- Run in the Server DataModel of the unpublished Hall draft during Play.
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

local markedSpawns=0
local markedRoutes=0
local lineCount=0
for _,part in world.Hall:GetChildren() do
 if part.Name=="TrainingLane" or part.Name=="TrainingTurn" then
  lineCount+=1
  assert(not part.CanQuery and not part.CanCollide and part.Material~=Enum.Material.Neon,
   "Training line looks like the safe apron or alters combat geometry")
 end
end
assert(lineCount==4,"Missing the continuous training route")
for _,side in ipairs({-1,1}) do
 local lane=Vector3.new(side*69,3.5,0)
 local corner=Vector3.new(side*69,3.5,55)
 local portalApproach=Vector3.new(side*2,3.5,55)
 local start=Vector3.new(side*69,3.5,-55)
 for _,leg in ipairs({{start,lane},{lane,corner},{corner,portalApproach}}) do
  assert(not cast(leg[1],leg[2]-leg[1]),"Training route is obstructed")
  for sample=0,8 do floorAt(leg[1]:Lerp(leg[2],sample/8),"ArenaFloor") end
  markedRoutes+=1
 end
end
for _,sx in ipairs({-1,1}) do
 for _,sz in ipairs({-1,1}) do
  local spawn=world.Hall["Spawn_"..sx.."_"..sz]
  local start=Vector3.new(spawn.Position.X,3.5,spawn.Position.Z)
  floorAt(start,"ArenaFloor")
  local board=assert(world.Hall:FindFirstChild("TrainingDirection_"..sx.."_"..sz),"Missing training directions")
  local head=start+Vector3.yAxis*2
  assert(not board.CanCollide and not board.CanQuery and board.CFrame.LookVector:Dot((head-board.Position).Unit)>.85,
   "Training direction board collides or faces away from its spawn")
  for _,x in ipairs({-.44,0,.44}) do
   for _,y in ipairs({-.38,0,.38}) do
    local textPoint=board.Position+board.CFrame.RightVector*(x*board.Size.X)+Vector3.yAxis*(y*board.Size.Y)
    assert(not cast(head,textPoint-head),"Training directions hidden by cover")
   end
  end
  local walkDirection=sz==-1 and Vector3.zAxis or Vector3.new(-sx,0,0)
  local arrow=spawn.CFrame.RightVector:Dot(walkDirection)<0 and "←" or "→"
  local matchingArrow,safeFirst=false,false
  for _,label in board:GetDescendants() do
   if label:IsA("TextLabel") and label.Text:find("TRAINING CITY",1,true) then
    matchingArrow=label.Text:find(arrow,1,true)==1
   elseif label:IsA("TextLabel") then
    safeFirst=label.Text:find("SAFE AT PORTAL",1,true)==1
   end
  end
  assert(matchingArrow and safeFirst,"Training sign must lead with its exit arrow and safe threshold")
  markedSpawns+=1
 end
end
local speed=humanoid.WalkSpeed
local jumping=humanoid:GetStateEnabled(Enum.HumanoidStateType.Jumping)
humanoid.WalkSpeed=16
humanoid:SetStateEnabled(Enum.HumanoidStateType.Jumping,false)
local travelOwner=root:GetNetworkOwner()
root:SetNetworkOwner(nil)
character:PivotTo(CFrame.new(69,3.5,-55))
root.AssemblyLinearVelocity=Vector3.zero
humanoid:MoveTo(root.Position)
task.wait(.2)
local trainingWalkStarted=os.clock()
for _,waypoint in ipairs({Vector3.new(69,3.5,0),Vector3.new(69,3.5,55),Vector3.new(0,3.5,55)}) do
 humanoid:MoveTo(waypoint)
 local deadline=os.clock()+6
 repeat task.wait(.05) until (root.Position-waypoint).Magnitude<2 or os.clock()>=deadline
 assert((root.Position-waypoint).Magnitude<2,"Humanoid left the signed training route")
end
assert(layout.IsSafeApron(root.Position) and (root.Position-prompt.Parent.Position).Magnitude<prompt.MaxActivationDistance,
 "Signed route did not reach the protected portal")
local trainingWalkSeconds=os.clock()-trainingWalkStarted
root:SetNetworkOwner(travelOwner)
humanoid.WalkSpeed=speed
humanoid:SetStateEnabled(Enum.HumanoidStateType.Jumping,jumping)
return {parts=parts,solid=solid,markedSpawns=markedSpawns,markedRouteLegs=markedRoutes,trainingWalkSeconds=trainingWalkSeconds}
