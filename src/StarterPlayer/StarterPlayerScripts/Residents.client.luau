-- Local visual animation avoids replicating every resident's joints each frame.
local Collection=game:GetService("CollectionService")
local Run=game:GetService("RunService")
local rigs={}
local jointNames={"Left Shoulder","Right Shoulder","Left Hip","Right Hip"}
local function register(model)
 if rigs[model] then return end
 rigs[model]={model=model,joints={},phase=(model:GetAttribute("AnimationSeed") or 1)*.71,blend=0,elapsed=0}
end
for _,model in ipairs(Collection:GetTagged("CityResident")) do register(model) end
Collection:GetInstanceAddedSignal("CityResident"):Connect(register)
Collection:GetInstanceRemovedSignal("CityResident"):Connect(function(model) rigs[model]=nil end)
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
  local moving=humanoid.Health>0 and speed>.4 and humanoid.FloorMaterial~=Enum.Material.Air
  rig.blend+=((moving and 1 or 0)-rig.blend)*math.min(elapsed*10,1)
  rig.phase+=elapsed*math.max(6,speed*1.2)
  local swing=math.sin(rig.phase)*.42*rig.blend
  local now=workspace:GetServerTimeNow();local role=model:GetAttribute("Role")
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
     elseif role=="Soccer" and i==4 then angle=math.sin(now*2)*.9
     elseif role=="Gardener" and i==2 then angle=-.9+math.sin(now*1.6)*.12
     elseif role=="Artist" and i==2 then angle=-1.2+math.sin(now*3)*.18
     elseif role=="Artist" and i==1 then angle=-.7
     elseif role=="Vendor" and i<=2 then angle=-.6+math.sin(now*2+i)*.3 end
    end
   end
   if role=="CafeWorker" and model:GetAttribute("WorkStep")==2 and i==1 then angle=-.8 end
   joint.Transform=CFrame.Angles(angle,0,0)
  end
 end
end)
