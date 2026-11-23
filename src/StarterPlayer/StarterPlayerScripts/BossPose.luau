-- Local assembly animation. The server still owns the root, attack timing and hitboxes.
local Motion={}
local left,right="armL","armR"
local legs={Boot=true,Greave=true,Knee=true,Trouser=true,Shoe=true,CaptainBoot=true,CaptainLeg=true,CaptainPeg=true,CaptainToe=true}
local arms={
 Arm=true,ArmBrassBand=true,ArmWave=true,Gauntlet=true,Finger=true,RoundPauldron=true,TealShoulderEnamel=true,ShoulderWave=true,
 ArmCone=true,ArmDriver=true,ArmPiston=true,Fist=true,ForearmSpeaker=true,Knuckle=true,KnuckleEtch=true,
 ShoulderCabinet=true,ShoulderGrille=true,ShoulderGrilleSlat=true,
 ShoulderArmor=true,ShoulderInset=true,ShoulderMusicStaff=true,StaffLine=true,ShoulderNote=true,OrganPipe=true,PipeMouth=true,
 UpperArm=true,CuffBand=true,ForkBridge=true,ForkGrip=true,TuningForkTine=true,MicHandle=true,MicHead=true,
 Sleeve=true,Glove=true,GloveCuff=true,GloveFinger=true,Epaulette=true,EpauletteFringe=true,
 CaptainArm=true,CaptainCuff=true,CaptainHand=true,CaptainHook=true,CaptainEpaulette=true,CaptainFringe=true,
}
local bells={BellGoldLip=true,BellDarkInterior=true,Clapper=true,BellCrown=true,BellRune=true}
function Motion.Group(id,name,x,y)
 if legs[name] then return x<0 and "legL" or "legR" end
 -- The crescent's tip crosses the centerline, but the whole blade belongs to the left hand.
 if name=="SickleHandle" or name=="CrescentBlade" or string.sub(name,1,7)=="Cutlass" then return left end
 if arms[name] then return x<0 and left or right end
 if id=="metronome" and (name=="Pendulum" or name=="PendulumTip") then return "pendulum" end
 if id=="golem" and name=="ChestSubwoofer" then return "woofer" end
 if id=="ignis" then
  if name=="FlameCore" or (name=="AzureFlame" and math.abs(x)>1) then return x<0 and left or right end
  if name=="AzureFlame" or name=="HelmFlameCore" then return "flame" end
 end
 if id=="leviathan" and string.sub(name,1,5)=="Siren" then return "sirens" end
 if id=="conductor" and (bells[name] or string.sub(name,1,9)=="OrbitBell") then
  -- Each bell's shell, lip, crown, rune and clapper travel together.
  y=y or 7.8
  local tier=y>=7.08 and 1 or y>=5.62 and 2 or 3
  return "bell"..(2*tier-(x<0 and 1 or 0))
 end
 return "body"
end
-- Pivots, stride period, travel and swing lift, in original unscaled anatomy units.
local actors={
 metronome={shoulderX=2.12,shoulderY=6.35,hip=3.5,beat=.79,stride=.28,lift=.22,swing=.13,sway=.045,default="PendulumSweep"},
 golem={shoulderX=2.1,shoulderY=6.05,hip=3.45,beat=1.06,stride=.34,lift=.17,swing=.11,sway=.055,default="FaultLine"},
 ignis={shoulderX=1.55,shoulderY=5.9,hip=3.1,beat=.73,stride=.27,lift=.20,swing=.16,sway=.038,default="OrganFlames"},
 leviathan={shoulderX=1.8,shoulderY=5.9,hip=2.7,beat=.93,stride=.33,lift=.27,swing=.17,sway=.060,default="TwinSirens"},
 conductor={shoulderX=.90,shoulderY=5.9,hip=3.3,beat=.84,stride=.29,lift=.20,swing=.17,sway=.048,default="BellCascade"},
}
-- Keyframes are assemblies, not cosmetic hitboxes. Rotations in degrees, followed by optional
-- xyz offsets. Each attack has a clear held anticipation and its own contact/settle silhouette.
local actions={
 PendulumSweep={id="metronome",
  tell={body={5,15,-5},armL={-24,-35,-15},armR={23,0,11},pendulum={0,0,-38}},
  hit={body={-9,-18,3},armL={54,38,-9},armR={-19,0,15},pendulum={0,0,38}}},
 ResonanceKick={id="metronome",
  tell={body={8,-12,5},legL={0,0,0,0,.30,.29},armL={16,-15,-13},armR={21,0,12},pendulum={0,0,26}},
  hit={body={-9,7,-7},legL={0,0,0,0,.63,-1.15},armL={-17,-12,-18},armR={-24,8,15},pendulum={0,0,-28}}},
 FaultLine={id="golem",
  tell={body={11,0,0,0,-.09,0},armL={57,0,-27},armR={57,0,27},woofer={0,0,0,0,0,.12}},
  hit={body={-10,0,0,0,-.12,0},armL={19,5,-30},armR={19,-5,30},woofer={0,0,0,0,0,-.28}}},
 WooferSlam={id="golem",
  tell={body={13,0,0},armL={118,-4,-9},armR={118,4,9},woofer={0,0,0,0,0,.1}},
  hit={body={-21,0,0,0,-.29,-.13},armL={22,5,-16},armR={22,-5,16},woofer={0,0,0,0,0,-.22}}},
 OrganFlames={id="ignis",
  tell={body={8,-10,-3},armL={18,-18,-21},armR={86,-15,8},flame={0,0,4,0,.13,0}},
  hit={body={-10,8,3},armL={23,-7,-23},armR={64,-13,7},flame={0,0,-7,0,.24,-.10}}},
 Backdraft={id="ignis",
  tell={body={7,21,5},armL={-25,-22,-17},armR={51,-18,18},legR={0,0,0,0,.62,.18},flame={0,0,-8,0,.11,0}},
  hit={body={-16,-19,-4},armL={63,32,-9},armR={-20,-11,17},legR={0,0,0,0,0,-.52},flame={0,0,12,0,.22,-.10}}},
 TwinSirens={id="leviathan",
  tell={body={9,0,-4},armL={17,-5,-22},armR={62,-34,13},sirens={11,0,0}},
  hit={body={5,0,3,0,0,.07},armL={16,0,-12},armR={39,-14,12},sirens={-4,0,0,0,0,.14}}},
 CutlassBroadside={id="leviathan",
  tell={body={7,22,-6},armL={28,-52,-25},armR={28,6,22}},
  hit={body={-11,-20,5},armL={57,49,-10},armR={-16,-8,19}}},
 BellCascade={id="conductor",
  tell={body={4,0,0},armL={105,10,-27},armR={105,-10,27}},
  hit={body={-12,0,0},armL={38,2,-16},armR={38,-2,16}}},
 BatonSweep={id="conductor",
  tell={body={5,-22,6},armL={26,5,-19},armR={62,-49,33}},
  hit={body={-9,21,-5},armL={-14,0,-19},armR={61,50,9}}},
}
local radians=math.pi/180
local zero={0,0,0}
local function ease(x)
 x=math.clamp(x,0,1);return x*x*(3-2*x)
end
local function around(x,y,z,rx,ry,rz)
 return CFrame.new(x,y,z)*CFrame.Angles(rx,ry,rz)*CFrame.new(-x,-y,-z)
end
local function finite(x)
 return type(x)=="number" and x==x and math.abs(x)<math.huge
end
local function attackTimes(state,now,stateAt,attack)
 local age=finite(stateAt) and math.max(0,now-stateAt) or 1
 if state=="Windup" then
  local progress=ease(age/.65)
  if attack and finite(attack.startAt) and finite(attack.attackAt) and attack.attackAt>attack.startAt then
   -- A new state may arrive before all of its attributes replicate. Don't apply an old cast.
   if finite(stateAt) and math.abs(stateAt-attack.startAt)>.15 then return age,0,0 end
   progress=ease((now-attack.startAt)/(.72*(attack.attackAt-attack.startAt)))
  end
  return age,progress,0
 end
 if state=="Recovery" then
  local duration=attack and attack.recovery or .6
  if not finite(duration) or duration<=0 then duration=.6 end
  local impact=attack and finite(attack.serial) and attack.serial>0 and attack.serial==attack.impactSerial
   and finite(attack.impactAt) and finite(stateAt) and math.abs(attack.impactAt-stateAt)<.15
  if impact then
   -- Match confirmed impact serial. A canceled cast relaxes instead of striking.
   local elapsed=math.max(0,now-attack.impactAt)
   local drive=math.min(.105,duration*.23)
   local follow=ease(elapsed/drive)
   local settle=1-ease((elapsed-drive)/(duration-drive))
   return age,(1-follow)*settle,follow*settle
  end
  local prepared=1
  if attack and finite(attack.startAt) and finite(attack.attackAt) and finite(stateAt) and attack.attackAt>attack.startAt then
   prepared=ease((stateAt-attack.startAt)/(.72*(attack.attackAt-attack.startAt)))
  end
  return age,prepared*(1-ease(age/math.min(duration,.32))),0
 end
 return age,0,0
end
local function sample(id,actor,group,now,state,age,tell,hit,scale,action)
 local a=action.tell[group] or zero
 local b=action.hit[group] or zero
 local rx,ry,rz=(a[1]*tell+b[1]*hit)*radians,(a[2]*tell+b[2]*hit)*radians,(a[3]*tell+b[3]*hit)*radians
 local x=((a[4] or 0)*tell+(b[4] or 0)*hit)*scale
 local y=((a[5] or 0)*tell+(b[5] or 0)*hit)*scale
 local z=((a[6] or 0)*tell+(b[6] or 0)*hit)*scale
 local gait=state=="Moving" and ease(age/.26) or 0
 local phase=age/actor.beat*2*math.pi
 local swing=math.sin(phase)
 local side=(group=="armL" or group=="legL") and -1 or 1
 local idle=1-math.min(1,tell+hit)
 if group=="legL" or group=="legR" then
  local step=swing*side
  local lift=actor.lift
  if id=="leviathan" and side==1 then lift*=.58 end -- the peg follows a lower swing arc
  return CFrame.new(x,y+math.max(0,step)*lift*scale*gait,z-math.cos(phase)*side*actor.stride*scale*gait)
 elseif group=="body" then
  return CFrame.new(x,y,z)*around(0,actor.hip*scale,0,rx+math.cos(phase*2)*.03*gait,ry+swing*.07*gait,rz+swing*actor.sway*gait)
 elseif group==left or group==right then
  return around(side*actor.shoulderX*scale,actor.shoulderY*scale,0,rx-swing*side*actor.swing*gait,ry,rz)
 elseif group=="pendulum" then
  return around(0,4.35*scale,-1.3*scale,rx,ry,rz+math.sin(now*3.6)*.23*idle)
 elseif group=="flame" then
  -- Rotate around the bases so the crests don't float off the body.
  return CFrame.new(x,y,z)*around(0,7.55*scale,0,rx,ry,rz+math.sin(now*3)*.045*idle)
 elseif group=="woofer" then
  return CFrame.new(x,y,z)
 elseif group=="sirens" then
  return CFrame.new(x,y,z)*around(0,6.25*scale,.05*scale,rx,ry,rz)
 elseif string.sub(group,1,4)=="bell" then
  local index=tonumber(string.sub(group,5));local row=math.ceil(index/2)
  local s=index%2==1 and -1 or 1
  local bellX=row==1 and 2.05 or row==2 and 2.65 or 2.8
  local bellY=7.8-(row-1)*1.45
  local chord=action==actions.BellCascade
  return CFrame.new(s*(tell*(chord and .44 or .09)+hit*.12)*scale,
   (.11*math.sin(now*2.2+index*.85)*idle+tell*(chord and .44+(3-row)*.11 or .15)-hit*.17)*scale,0)
   *around(s*bellX*scale,bellY*scale,.3*scale,0,0,
    .11*math.sin(now*2.2+index*.85)*idle+s*(tell*.24-hit*.33))
 end
 return CFrame.identity
end
local function choose(id,actor,style)
 local action=actions[style]
 return action and action.id==id and action or actions[actor.default]
end
function Motion.Pose(id,group,now,state,age,scale,reduced,attack)
 local actor=actors[id]
 if reduced or state=="Defeated" or not actor then return CFrame.identity end
 local sAt=now-age
 local _,tell,hit=attackTimes(state,now,sAt,attack)
 local action=choose(id,actor,attack and attack.style)
 local pose=sample(id,actor,group,now,state,age,tell,hit,scale,action)
 if group=="body" or group=="legL" or group=="legR" then return pose end
 return sample(id,actor,"body",now,state,age,tell,hit,scale,action)*pose
end
function Motion.new(model,id,center,scale,bulkMove)
 local anchor=CFrame.new(center)
 local self={model=model,id=id,scale=scale or 1,frame=anchor,groups={},stopped=false,parts={},frames={}}
 model.WorldPivot=anchor
 for _,part in ipairs(model:GetDescendants()) do
  if part:IsA("BasePart") then
   local base=anchor:ToObjectSpace(part.CFrame)
   local p=base.Position
   local key=Motion.Group(id,part.Name,p.X/self.scale,p.Y/self.scale)
   local group=self.groups[key];if not group then group={};self.groups[key]=group end
   table.insert(group,{part=part,base=base})
  end
 end
 function self:Step(target,state,now,dt,reduced,stateAt,attack)
  if self.stopped or not self.model.Parent then return false end
  local actor=actors[self.id]
  if not actor then return false end
  -- No root offset or extrapolation. Windup and recovery follow the committed server facing.
  local alpha=state=="Moving" and (1-math.exp(-math.clamp(dt,0,.1)*16)) or 1
  self.frame=self.frame:Lerp(target,alpha)
  local quiet=reduced or state=="Defeated"
  local age,tell,hit=attackTimes(state,now,stateAt,attack)
  local action=choose(self.id,actor,attack and attack.style)
  local body=quiet and CFrame.identity or sample(self.id,actor,"body",now,state,age,tell,hit,self.scale,action)
  local parts,frames=self.parts,self.frames
  table.clear(parts);table.clear(frames)
  for key,entries in pairs(self.groups) do
   local pose=key=="body" and body or quiet and CFrame.identity or sample(self.id,actor,key,now,state,age,tell,hit,self.scale,action)
   if not quiet and key~="body" and key~="legL" and key~="legR" then pose=body*pose end
   local world=self.frame*pose
   for _,entry in ipairs(entries) do
    if entry.part.Parent then
     if bulkMove then
      table.insert(parts,entry.part);table.insert(frames,world*entry.base)
     else
      entry.part.CFrame=world*entry.base
     end
    end
   end
  end
  if bulkMove and #parts>0 then bulkMove(parts,frames) end
  return true
 end
 function self:Destroy()
  self.stopped=true;table.clear(self.groups);table.clear(self.parts);table.clear(self.frames)
 end
 return self
end
return Motion
