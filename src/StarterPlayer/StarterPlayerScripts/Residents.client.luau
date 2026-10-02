-- Local visual animation avoids replicating every resident's joints each frame.
local Collection=game:GetService("CollectionService")
local Run=game:GetService("RunService")
local rigs={}
local jointNames={"Left Shoulder","Right Shoulder","Left Hip","Right Hip"}
local function makePracticeBall()
 local model=Instance.new("Model");model.Name="NickPracticeVisual"
 local function piece(name,size,cf)
  local p=Instance.new("Part");p.Name=name;p.Shape=Enum.PartType.Ball;p.Size=size;p.CFrame=cf;p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.CastShadow=false;p.Transparency=1;p.Color=name=="Ball" and Color3.fromRGB(241,232,210) or Color3.fromRGB(43,54,60);p.Parent=model;return p
 end
 model.PrimaryPart=piece("Ball",Vector3.new(1.5,1.5,1.5),CFrame.identity)
 for _,axis in ipairs({Vector3.xAxis,-Vector3.xAxis,Vector3.yAxis,-Vector3.yAxis,Vector3.zAxis,-Vector3.zAxis}) do
  piece("Panel",Vector3.new(.4,.035,.4),CFrame.lookAt(axis*.745,axis*2,math.abs(axis.Y)>.98 and Vector3.zAxis or Vector3.yAxis)*CFrame.Angles(math.pi/2,0,0))
 end
 model.Parent=workspace;return model
end
local function register(model)
 if rigs[model] then return end
 rigs[model]={model=model,joints={},phase=(model:GetAttribute("AnimationSeed") or 1)*.71,blend=0,elapsed=0}
 if model:GetAttribute("DisplayName")=="Nick Booty" then rigs[model].practiceBall=makePracticeBall() end
end
for _,model in ipairs(Collection:GetTagged("CityResident")) do register(model) end
Collection:GetInstanceAddedSignal("CityResident"):Connect(register)
Collection:GetInstanceRemovedSignal("CityResident"):Connect(function(model) local rig=rigs[model];if rig and rig.practiceBall then rig.practiceBall:Destroy() end;rigs[model]=nil end)
Run.PreSimulation:Connect(function(dt)
 local camera=workspace.CurrentCamera;if not camera then return end
 for model,rig in pairs(rigs) do
  if not model:IsDescendantOf(workspace) then continue end
  local root=model:FindFirstChild("HumanoidRootPart");local torso=model:FindFirstChild("Torso")
  local humanoid=model:FindFirstChildOfClass("Humanoid")
  if not root or not torso or not humanoid then continue end -- streaming may deliver limbs later
  local distance=(root.Position-camera.CFrame.Position).Magnitude
  rig.elapsed+=dt
  local interval=distance<70 and 0 or distance<160 and 1/20 or 1/5
  if rig.elapsed<interval then continue end
  local elapsed=math.min(rig.elapsed,.2);rig.elapsed=0
  local speed=Vector3.new(root.AssemblyLinearVelocity.X,0,root.AssemblyLinearVelocity.Z).Magnitude
  local seated=humanoid.SeatPart~=nil
  local moving=not seated and humanoid.Health>0 and speed>.4 and humanoid.FloorMaterial~=Enum.Material.Air
  rig.blend+=((moving and 1 or 0)-rig.blend)*math.min(elapsed*10,1)
  rig.phase+=elapsed*math.max(6,speed*1.2)
  local swing=math.sin(rig.phase)*.42*rig.blend
  local now=workspace:GetServerTimeNow();local role=model:GetAttribute("Role")
  local working=model:GetAttribute("Working") and humanoid.Health>0 and not moving
  local workAge=(now-(model:GetAttribute("WorkStarted") or now))%5
  if rig.practiceBall then
   local visible=working and distance<180
   if rig.ballVisible~=visible then
    rig.ballVisible=visible
    for _,piece in ipairs(rig.practiceBall:GetChildren()) do piece.Transparency=visible and 0 or 1 end
   end
   if visible then
    local forward=Vector3.new(root.CFrame.LookVector.X,0,root.CFrame.LookVector.Z)
    if forward.Magnitude>.01 then forward=forward.Unit end
    -- The boot visibly misses: the ball remains on the ground at his feet.
    local position=root.Position-Vector3.new(0,2.25,0)+forward*1.65
    rig.practiceBall:PivotTo(CFrame.new(position))
   end
  end
  for i,name in ipairs(jointNames) do
   local joint=rig.joints[i]
   if not joint or not joint.Parent then joint=torso:FindFirstChild(name);rig.joints[i]=joint end
   if not joint then continue end
   local angle=(i==1 or i==4) and swing or -swing
   if distance<180 and not moving then
    if model:GetAttribute("Gesturing") and i==1 then angle=-.8+math.sin(now*5)*.15 end
    if model:GetAttribute("Working") then
     if role=="CafeWorker" and i<=2 then angle=-.8+(i==2 and math.sin(now*3)*.15 or 0)
     elseif role=="Sanitation" and i==2 then angle=-.15+math.sin(now*2)*.3
     elseif role=="BeachWorker" and i==2 then angle=-.7+math.sin(now*2.5)*.2
     elseif role=="Busker" and i<=2 then angle=-.6+(i==2 and math.sin(now*8)*.13 or 0)
     elseif role=="Soccer" then
      if workAge<1 and i==4 then angle=.6*math.sin(workAge*math.pi/2)
      elseif workAge<1.5 and i==4 then angle=-1.1*math.sin((workAge-1)*math.pi*2)
      elseif workAge>=1.5 and workAge<3 and i<=2 then angle=-2.5
      elseif workAge>=3 and workAge<4.2 and i==2 then angle=-2.1 end
     elseif role=="Gardener" and i==2 then angle=-.9+math.sin(now*1.6)*.12
     elseif role=="Artist" and i==2 then angle=-1.2+math.sin(now*3)*.18
     elseif role=="Artist" and i==1 then angle=-.7
     elseif role=="Vendor" and i<=2 then angle=-.6+math.sin(now*2+i)*.3 end
    end
   end
   if role=="CafeWorker" and model:GetAttribute("WorkStep")==2 and i==1 then angle=-.8 end
   if seated then
    if i>=3 then angle=-math.pi/2 elseif model:GetAttribute("Reading") and i==1 then angle=-1.15 else angle=-.15 end
   end
   -- These custom R6 joints have no rotated basis: positive X bends toward -Z.
   joint.Transform=CFrame.Angles(-angle,0,0)
  end
 end
end)
