-- Additive animation layer on every client: running and a grounded forward roll.
local Players=game:GetService("Players")
local Run=game:GetService("RunService")
local Config=require(game.ReplicatedStorage.Shared.Config)
local rigs={}
local function watch(player)
 local function added(character)
  local humanoid=character:WaitForChild("Humanoid");local root=character:WaitForChild("HumanoidRootPart")
  local rig={character=character,humanoid=humanoid,root=root,joints={},offsets={},phase=0,blend=0};rigs[player]=rig
  local function collect(item)
   if item:IsA("Motor6D") or item:IsA("AnimationConstraint") then
    rig.joints[item.Name]=item
    if item:IsA("Motor6D") and item.Part0==root or item:IsA("AnimationConstraint") and item.Attachment0 and item.Attachment0.Parent==root then rig.rootJoint=item end
   end
  end
  for _,item in ipairs(character:GetDescendants()) do collect(item) end
  character.DescendantAdded:Connect(collect)
 end
 player.CharacterAdded:Connect(added);if player.Character then task.spawn(added,player.Character) end
end
for _,p in ipairs(Players:GetPlayers()) do watch(p) end;Players.PlayerAdded:Connect(watch);Players.PlayerRemoving:Connect(function(p) rigs[p]=nil end)
Run.PreAnimation:Connect(function()
 for _,rig in pairs(rigs) do for joint,offset in pairs(rig.offsets) do if joint.Parent then joint.Transform=joint.Transform*offset:Inverse() end end;table.clear(rig.offsets) end
end)
Run.PreSimulation:Connect(function(dt)
 for player,rig in pairs(rigs) do
  if not rig.character.Parent then continue end
  local function pose(name,offset)
   local j=rig.joints[name];if j then j.Transform=j.Transform*offset;rig.offsets[j]=offset end
  end
  local now=workspace:GetServerTimeNow();local ends=player:GetAttribute("DodgeEnds") or 0;local started=player:GetAttribute("DodgeStarted") or 0
  if now<ends and started>0 then
   local t=math.clamp((now-started)/Config.DodgeDuration,0,1);local tuck=math.sin(t*math.pi)
   local rootJoint=rig.rootJoint or rig.joints.RootJoint or rig.joints.Root or rig.joints.RootMotor
   if rootJoint then
    local roll=CFrame.new(0,-1.1*tuck,0)*CFrame.Angles(-math.pi*2*t,0,0)
    local basis=rootJoint:IsA("Motor6D") and rootJoint.C0 or rootJoint.Attachment0 and rootJoint.Attachment0.CFrame or CFrame.identity
    local offset=basis:Inverse()*roll*basis
    pose(rootJoint.Name,offset)
   end
   for _,name in ipairs({"Left Shoulder","Right Shoulder","LeftShoulder","RightShoulder"}) do pose(name,CFrame.Angles(-1.4*tuck,0,0)) end
   for _,name in ipairs({"Left Hip","Right Hip","LeftHip","RightHip"}) do pose(name,CFrame.Angles(1.2*tuck,0,0)) end
   for _,name in ipairs({"LeftKnee","RightKnee"}) do pose(name,CFrame.Angles(-1.6*tuck,0,0)) end
   pose("Waist",CFrame.Angles(-.4*tuck,0,0))
   rig.character:SetAttribute("RollAnimationProgress",t)
   continue
  end
  rig.character:SetAttribute("RollAnimationProgress",-1)
  local v=rig.root.AssemblyLinearVelocity;local speed=Vector3.new(v.X,0,v.Z).Magnitude
  local sprinting=player:GetAttribute("Sprinting") and speed>3 and rig.humanoid.FloorMaterial~=Enum.Material.Air and now>=(player:GetAttribute("KnockdownEnds") or 0)
  rig.blend+=((sprinting and 1 or 0)-rig.blend)*math.min(dt*12,1)
  if rig.blend<.01 then continue end
  rig.phase+=dt*13;local swing=math.sin(rig.phase)*.32*rig.blend
  for _,spec in ipairs({{"Left Shoulder",swing},{"Right Shoulder",-swing},{"Left Hip",-swing},{"Right Hip",swing},{"LeftShoulder",swing},{"RightShoulder",-swing},{"LeftHip",-swing},{"RightHip",swing},{"LeftKnee",math.max(0,swing)*.7},{"RightKnee",math.max(0,-swing)*.7}}) do pose(spec[1],CFrame.Angles(spec[2],0,0)) end
  pose("Waist",CFrame.Angles(-.14*rig.blend,math.sin(rig.phase)*.04*rig.blend,0));rig.character:SetAttribute("SprintAnimationBlend",rig.blend)
 end
end)
