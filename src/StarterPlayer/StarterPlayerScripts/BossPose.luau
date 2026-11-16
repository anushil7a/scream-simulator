-- Cosmetic pose over authoritative root/state. No Instances, hitboxes or remotes here.
local Motion={}
local legs={Boot=true,Greave=true,Knee=true,Trouser=true,Shoe=true}
local arms={Arm=true,ArmBrassBand=true,ArmWave=true,Gauntlet=true,Finger=true,SickleHandle=true,CrescentBlade=true,
 ArmCone=true,ArmDriver=true,ArmPiston=true,Fist=true,ForearmSpeaker=true,Knuckle=true,KnuckleEtch=true,
 UpperArm=true,CuffBand=true,ForkBridge=true,ForkGrip=true,TuningForkTine=true,MicHandle=true,MicHead=true,
 Sleeve=true,Glove=true,GloveCuff=true,GloveFinger=true}
local bells={BellGoldLip=true,BellDarkInterior=true,Clapper=true,BellCrown=true,BellRune=true}
function Motion.Group(id,name,x)
 if id=="leviathan" then
  if name=="CaptainBoot" or name=="CaptainLeg" or name=="CaptainPeg" or name=="CaptainToe" then return x<0 and "legL" or "legR" end
  if name=="CaptainArm" or name=="CaptainCuff" or name=="CaptainHand" or name=="CaptainHook" or string.sub(name,1,7)=="Cutlass" then return x<0 and "armL" or "armR" end
  if string.sub(name,1,5)=="Siren" then return "sirens" end
 elseif legs[name] then return x<0 and "legL" or "legR"
 elseif arms[name] then return x<0 and "armL" or "armR" end
 if id=="metronome" and (name=="Pendulum" or name=="PendulumTip") then return "pendulum" end
 if id=="ignis" and (name=="AzureFlame" or name=="FlameCore" or name=="HelmFlameCore") then return "flame" end
 if id=="conductor" and (bells[name] or string.sub(name,1,9)=="OrbitBell") then return "bells" end
 return nil
end
local function around(x,y,z,rx,ry,rz)
 return CFrame.new(x,y,z)*CFrame.Angles(rx,ry,rz)*CFrame.new(-x,-y,-z)
end
-- One small set of group transforms, not one allocation/model per body part.
function Motion.Pose(id,group,now,state,age,scale,reduced)
 if reduced or state=="Defeated" then return CFrame.identity end
 local moving=state=="Moving"
 local cast=state=="Windup" and math.clamp(age/.35,0,1) or 0
 local frequency=id=="golem" and 3 or id=="ignis" and 4.5 or 4
 local wave=math.sin(now*frequency)
 local sign=(group=="legL" or group=="armR") and 1 or -1
 if group=="legL" or group=="legR" then
  -- Translate complete lower-leg assemblies; feet lift, never sink or pitch.
  return moving and CFrame.new(0,math.max(0,wave*sign)*.13*scale,wave*sign*.16*scale) or CFrame.identity
 elseif group=="armL" or group=="armR" then
  local side=group=="armL" and -1 or 1
  local swing=moving and wave*sign*.055 or 0
  local lift=cast*(id=="golem" and -.22 or id=="conductor" and -.28 or id=="leviathan" and -.32 or -.14)
  return around(side*1.65*scale,(id=="leviathan" and 5.9 or 5.2)*scale,0,swing+lift,0,side*cast*.035)
 elseif group=="pendulum" then
  return around(0,4.35*scale,-1.3*scale,0,0,cast==0 and math.sin(now*2.4)*.14 or -.18*cast)
 elseif group=="flame" then
  return CFrame.new(0,(.035+.035*math.sin(now*2.7)+cast*.13)*scale,0)
 elseif group=="bells" then
  return CFrame.new(0,(.07+.07*math.sin(now*1.5)+cast*.22)*scale,0)
 elseif group=="sirens" then
  -- A single rigid pair of horns tilts to prepare; no warning/hit timing invented.
  return around(0,6.25*scale,0,-cast*.08,0,0)
 end
 return CFrame.identity
end
function Motion.new(model,id,center,scale)
 local anchor=CFrame.new(center)
 local self={model=model,id=id,scale=scale or 1,frame=anchor,groups={},stopped=false}
 model.WorldPivot=anchor
 for _,part in ipairs(model:GetDescendants()) do
  if part:IsA("BasePart") then
   local base=anchor:ToObjectSpace(part.CFrame)
   local key=Motion.Group(id,part.Name,base.Position.X)
   if key then
    local group=self.groups[key];if not group then group={};self.groups[key]=group end
    table.insert(group,{part=part,base=base})
   end
  end
 end
 function self:Step(target,state,now,dt,reduced,stateAt)
  if self.stopped or not self.model.Parent then return false end
  -- No extrapolation beyond server authority. Snap cast/recovery to frozen root.
  local alpha=state=="Moving" and (1-math.exp(-math.clamp(dt,0,.1)*16)) or 1
  self.frame=self.frame:Lerp(target,alpha)
  self.model:PivotTo(self.frame)
  local age=type(stateAt)=="number" and stateAt==stateAt and math.max(0,now-stateAt) or 1
  for key,entries in pairs(self.groups) do
   local pose=Motion.Pose(self.id,key,now,state,age,self.scale,reduced)
   for _,entry in ipairs(entries) do
    if entry.part.Parent then entry.part.CFrame=self.frame*pose*entry.base end
   end
  end
  return true
 end
 function self:Destroy()self.stopped=true;table.clear(self.groups)end
 return self
end
return Motion
