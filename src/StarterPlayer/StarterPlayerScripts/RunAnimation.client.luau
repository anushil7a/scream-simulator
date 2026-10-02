-- Additive locomotion and combat poses. Inputs never originate in this animation layer.
-- Default Roblox locomotion remains underneath; offsets are removed before each animation step.
local Players=game:GetService("Players")
local Run=game:GetService("RunService")
local Config=require(game.ReplicatedStorage.Shared.Config)
local rigs={}
local function watch(player)
 local function added(character)
  local humanoid=character:WaitForChild("Humanoid",10);local root=character:WaitForChild("HumanoidRootPart",10)
  if not humanoid or not root or player.Character~=character then return end
  local rig={character=character,humanoid=humanoid,root=root,joints={},offsets={},phase=0,blend=0,airborne=false,landing=0,charge=0,connections={}};rigs[player]=rig
  local function collect(item)
   if item:IsA("Motor6D") or item:IsA("AnimationConstraint") then
    rig.joints[item.Name]=item
    if item:IsA("Motor6D") and item.Part0==root or item:IsA("AnimationConstraint") and item.Attachment0 and item.Attachment0.Parent==root then rig.rootJoint=item end
   end
  end
  for _,item in ipairs(character:GetDescendants()) do collect(item) end
  table.insert(rig.connections,character.DescendantAdded:Connect(collect))
 end
 player.CharacterRemoving:Connect(function(character)
  local rig=rigs[player];if rig and rig.character==character then
   for _,connection in ipairs(rig.connections) do connection:Disconnect() end
   rigs[player]=nil
  end
 end)
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
   local j=rig.joints[name];if j and j.Parent then j.Transform=j.Transform*offset;rig.offsets[j]=(rig.offsets[j] or CFrame.identity)*offset end
  end
  local now=workspace:GetServerTimeNow();local ends=player:GetAttribute("DodgeEnds") or 0;local started=player:GetAttribute("DodgeStarted") or 0
  local grounded=rig.humanoid.FloorMaterial~=Enum.Material.Air
  if rig.airborne and grounded then rig.landing=now end
  rig.airborne=not grounded
  if rig.humanoid.Health<=0 or rig.humanoid.Sit or now<(player:GetAttribute("KnockdownEnds") or 0) then rig.charge=0;rig.blend=0;continue end
  if now<ends and started>0 then
   rig.charge=0
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
  -- Charge/release is driven solely by accepted server state, independent of E/Q.
  local charging=(player:GetAttribute("CaptureStarted") or 0)>0
  rig.charge+=((charging and 1 or 0)-rig.charge)*math.min(dt*14,1)
  local released=player:GetAttribute("ScreamReleased") or 0
  local age=now-released
  local recoil=age>=0 and age<.38 and math.sin(age/.38*math.pi) or 0
  local charge=rig.charge
  for _,name in ipairs({"Left Shoulder","LeftShoulder"}) do pose(name,CFrame.Angles(-.65*charge-.9*recoil,0,-.32*charge)) end
  for _,name in ipairs({"Right Shoulder","RightShoulder"}) do pose(name,CFrame.Angles(-.65*charge-.9*recoil,0,.32*charge)) end
  pose("Waist",CFrame.Angles(.12*charge-.28*recoil,0,0))
  pose("Neck",CFrame.Angles(-.12*charge+.1*recoil,0,0))
  if not grounded then
   local rising=v.Y>1
   local bend=rising and .26 or -.13
   for _,name in ipairs({"Left Hip","LeftHip","Right Hip","RightHip"}) do pose(name,CFrame.Angles(bend,0,0)) end
   pose("LeftKnee",CFrame.Angles(rising and -.5 or -.15,0,0))
   pose("RightKnee",CFrame.Angles(rising and -.3 or -.2,0,0))
  else
   local elapsed=now-rig.landing
   local compress=elapsed>=0 and elapsed<.22 and math.sin(elapsed/.22*math.pi) or 0
   pose("Waist",CFrame.Angles(-.13*compress,0,0))
   pose("LeftKnee",CFrame.Angles(-.35*compress,0,0));pose("RightKnee",CFrame.Angles(-.35*compress,0,0))
  end
  if rig.blend<.01 then continue end
  rig.phase+=dt*13;local swing=math.sin(rig.phase)*.32*rig.blend
  for _,spec in ipairs({{"Left Shoulder",swing},{"Right Shoulder",-swing},{"Left Hip",-swing},{"Right Hip",swing},{"LeftShoulder",swing},{"RightShoulder",-swing},{"LeftHip",-swing},{"RightHip",swing},{"LeftKnee",math.max(0,swing)*.7},{"RightKnee",math.max(0,-swing)*.7}}) do pose(spec[1],CFrame.Angles(spec[2],0,0)) end
  pose("Waist",CFrame.Angles(-.14*rig.blend,math.sin(rig.phase)*.04*rig.blend,0));rig.character:SetAttribute("SprintAnimationBlend",rig.blend)
 end
end)
