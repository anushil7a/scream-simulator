-- Local authored boss appearance, <=450 parts; one active, 32-part construction batches.
local stopped=false
local controller
local heartbeat
script.Destroying:Connect(function() stopped=true;if heartbeat then heartbeat:Disconnect() end;if controller then controller:Destroy() end end)
local Appearance=require(script.Parent:WaitForChild("BossAppearance"))
if stopped then return end
local Controller=require(script.Parent:WaitForChild("BossVisualController"))
if stopped then return end
local Catalog=require(game:GetService("ReplicatedStorage"):WaitForChild("Shared"):WaitForChild("BossCatalog"))
if stopped then return end
local specs={};for _,spec in ipairs(Catalog.Entries) do specs[spec.id]=spec end
local Motion=require(script.Parent:WaitForChild("BossPose"))
if stopped then return end
local Players=game:GetService("Players")
local Run=game:GetService("RunService")
local Gui=game:GetService("GuiService")
local function comfort()
 local ok,value=pcall(function()return Gui.ReducedMotionEnabled end)
 return Players.LocalPlayer:GetAttribute("BossReducedEffects")~=false or not ok or value==true
end
local attack={}
local function bulkMove(parts,frames)
 workspace:BulkMoveTo(parts,frames,Enum.BulkMoveMode.FireCFrameChanged)
end
controller=Controller.new({
 create=function(id)local model=Instance.new("Model");model.Name="BossVisual_"..id;model.Parent=workspace;return model end,
 spawn=task.spawn,pause=task.wait,build=Appearance.Build,
 prepare=function(model,id,center,scale)return Motion.new(model,id,center,scale,bulkMove)end,
 animate=function(current,now,dt,reduced)
  local candidate=current.candidate;local core=candidate.core
  if not core or not core.Parent then return false end
  local ground=Appearance.FromCore(core.Position,specs[current.id])
  local look=core.CFrame.LookVector;local flat=Vector3.new(look.X,0,look.Z)
  if flat.Magnitude<.001 then flat=Vector3.new(0,0,-1) end
  local target=CFrame.lookAt(ground,ground+flat)
  local source=current.source
  local state=source:GetAttribute("BossState") or "Idle"
  local stateAt=source:GetAttribute("BossStateAt")
  local timing
  if state=="Windup" or state=="Recovery" then
   attack.style=source:GetAttribute("BossAttackStyle")
   attack.serial=source:GetAttribute("BossAttackSerial")
   attack.startAt=source:GetAttribute("BossAttackStartAt") or (state=="Windup" and stateAt)
   attack.attackAt=source:GetAttribute("BossAttackAt")
   attack.impactSerial=source:GetAttribute("BossAttackImpactSerial")
   attack.impactAt=source:GetAttribute("BossAttackImpactAt")
   attack.recovery=specs[current.id].recovery
   timing=attack
  end
  return current.motion:Step(target,state,now,dt,reduced,stateAt,timing)
 end,
})
local elapsed=0
heartbeat=Run.Heartbeat:Connect(function(dt)
 elapsed+=dt
 if elapsed>=1/30 then
  local step=math.min(elapsed,.1);elapsed=0
  controller:Animate(workspace:GetServerTimeNow(),step,comfort())
 end
end)
while not stopped do
 local character=Players.LocalPlayer.Character;local root=character and character:FindFirstChild("HumanoidRootPart")
 local world=workspace:FindFirstChild("ScreamSimulatorWorld");local folder=world and world:FindFirstChild("BossEncounters")
 local candidates={}
 if folder then
  for _,model in ipairs(folder:GetChildren()) do
   local core=model:FindFirstChild("Core")
   if core and core:IsA("BasePart") then
    local center,scale=Appearance.FromCore(core.Position,specs[model.Name])
    local spec=specs[model.Name]
    local home=spec and Vector3.new(spec.x,spec.y or 0,spec.z) or center
    table.insert(candidates,{id=model.Name,source=model,center=center,scale=scale,core=core,home=home})
   end
  end
 end
 controller:Step(root and root.Position,candidates)
 task.wait(.5)
end
