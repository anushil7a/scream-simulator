-- Standalone arena and portal-layout playtest.
assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0 and game.GameId==0,
 "Open the unpublished Resonance Arena draft in Studio")

local Lighting=game:GetService("Lighting")
Lighting.ClockTime=16.6
Lighting.Brightness=2.1
Lighting.Ambient=Color3.fromRGB(113,119,141)
Lighting.OutdoorAmbient=Color3.fromRGB(143,153,173)

local world=Instance.new("Folder")
world.Name="ResonanceArena"
local ink=Color3.fromRGB(26,34,47)
local slate=Color3.fromRGB(48,62,79)
local deck=Color3.fromRGB(89,101,117)
local trim=Color3.fromRGB(114,128,150)
local gold=Color3.fromRGB(255,203,99)
local blue=Color3.fromRGB(81,221,214)
local paper=Color3.fromRGB(239,249,248)
local plastic=Enum.Material.SmoothPlastic
local neon=Enum.Material.Neon

local function block(parent,name,size,cf,color,solid,material)
 local part=Instance.new("Part")
 part.Name=name
 part.Size=size
 part.CFrame=cf
 part.Color=color
 part.Material=material or plastic
 part.Anchored=true
 part.CanCollide=solid
 part.CanQuery=solid
 part.CanTouch=false
 part.CastShadow=solid
 part.Parent=parent
 return part
end

local function box(parent,name,x,y,z,w,h,d,color,solid,material)
 return block(parent,name,Vector3.new(w,h,d),CFrame.new(x,y,z),color,solid,material)
end

local function disk(parent,name,position,diameter,height,color)
 local part=block(parent,name,Vector3.new(height,diameter,diameter),CFrame.new(position)*CFrame.Angles(0,0,math.pi/2),color,false)
 part.Shape=Enum.PartType.Cylinder
end

local function sign(parent,name,x,y,z,w,h,title,body,accent,face)
 local plate=box(parent,name,x,y,z,w,h,.45,ink,false)
 local gui=Instance.new("SurfaceGui")
 gui.Face=face or Enum.NormalId.Front
 gui.SizingMode=Enum.SurfaceGuiSizingMode.PixelsPerStud
 gui.PixelsPerStud=40
 gui.LightInfluence=0
 gui.Parent=plate
 local header=Instance.new("TextLabel")
 header.Size=UDim2.fromScale(.94,.58)
 header.Position=UDim2.fromScale(.03,.05)
 header.BackgroundTransparency=1
 header.TextColor3=accent
 header.Font=Enum.Font.GothamBold
 header.TextScaled=true
 header.Text=title
 header.Parent=gui
 local sub=header:Clone()
 sub.Size=UDim2.fromScale(.94,.25)
 sub.Position=UDim2.fromScale(.03,.67)
 sub.TextColor3=paper
 sub.Text=body
 sub.Parent=gui
end

local function speaker(parent,x,z,face,wide)
 local depth=wide and 7 or 5
 local height=wide and 12 or 10
 box(parent,"SpeakerCover",x,height/2,z,wide and 16 or 13,height,depth,ink,true)
 local front=z+face*(depth/2+.06)
 -- The visible baffles are flush with the solid cover and never catch the player.
 box(parent,"Baffle",x,height/2,front,wide and 14 or 11,height-1.1,.12,slate,false)
 for _,y in ipairs({height*.31,height*.69}) do
  local cone=block(parent,"SpeakerCone",Vector3.new(.16,height*.33,height*.33),
   CFrame.new(x,y,front+face*.15)*CFrame.Angles(0,math.pi/2,0),trim,false)
  cone.Shape=Enum.PartType.Cylinder
  local center=block(parent,"DustCap",Vector3.new(.19,height*.2,height*.2),
   CFrame.new(x,y,front+face*.28)*CFrame.Angles(0,math.pi/2,0),ink,false)
  center.Shape=Enum.PartType.Cylinder
 end
 box(parent,"SpeakerHeader",x,height-.65,front+face*.19,wide and 11 or 8,.26,.16,gold,false,neon)
end

local function portal(parent,name,position,title,body,action,travelTo)
 local x,y,z=position.X,position.Y,position.Z
 box(parent,name.."Deck",x,y+.03,z-3,19,.06,22,slate,false)
 for _,side in ipairs({-1,1}) do
  box(parent,name.."Pillar",x+side*8,y+7,z,2.3,14,3,ink,true)
  box(parent,name.."VerticalLight",x+side*7,y+6,z-1.55,.45,12,.16,blue,false,neon)
  box(parent,name.."ApproachRail",x+side*4,y+.08,z-9,.3,.06,12,blue,false)
 end
 box(parent,name.."Header",x,y+14,z,18.3,2,3,ink,true)
 box(parent,name.."Light",x,y+13.25,z-1.56,15,.24,.18,blue,false,neon)
 box(parent,name.."Threshold",x,y+.09,z-1,14,.1,1.1,blue,false,neon)
 local field=box(parent,name.."Field",x,y+6.5,z+.6,13.6,12.9,.13,blue,false,neon)
 field.Transparency=.77
 for i,height in ipairs({1.1,2.4,4.4,7.1,4.4,2.4,1.1}) do
  box(parent,name.."Wave",x+(i-4)*1.12,y+6.5,z+.48,.32,height,.14,blue,false,neon)
 end
 sign(parent,name.."Sign",x,y+17.6,z-1.55,29,5.8,title,body,blue)
 local anchor=box(parent,name.."PromptAnchor",x,y+3.2,z-3,1,1,1,ink,false)
 anchor.Transparency=1
 local prompt=Instance.new("ProximityPrompt")
 prompt.Name=name
 prompt.ActionText=action
 prompt.ObjectText=title
 prompt.HoldDuration=.25
 prompt.MaxActivationDistance=10
 prompt.RequiresLineOfSight=false
 prompt.Parent=anchor
 prompt.Triggered:Connect(function(player)
  local character=player.Character
  local root=character and character:FindFirstChild("HumanoidRootPart")
  local humanoid=character and character:FindFirstChildOfClass("Humanoid")
  if not root or not humanoid or humanoid.Health<=0 or (root.Position-anchor.Position).Magnitude>prompt.MaxActivationDistance then return end
  character:PivotTo(travelTo)
  root.AssemblyLinearVelocity=Vector3.zero
  root.AssemblyAngularVelocity=Vector3.zero
 end)
end

local arena=Instance.new("Folder")
arena.Name="Hall"
arena.Parent=world
box(arena,"ArenaFloor",0,-1.5,0,176,3,152,deck,true,Enum.Material.Concrete)
for _,side in ipairs({-1,1}) do
 box(arena,"BackWall",0,8,side*75,176,16,2,ink,true)
 box(arena,"SideWall",side*87,8,0,2,16,150,ink,true)
 box(arena,"SideTrack",side*78,.035,0,.5,.06,121,gold,false)
 box(arena,"WallLight",side*85.94,12,0,.11,.35,112,trim,false)
 for index=1,7 do
  local barHeight=2+math.sin(index*1.1)^2*6
  box(arena,"Equalizer",side*85.8,6,index*6-24,.2,barHeight,2,index%2==0 and gold or trim,false)
 end
end

disk(arena,"RecordOuter",Vector3.new(0,.035,0),67,.06,slate)
disk(arena,"RecordGroove",Vector3.new(0,.067,0),55,.06,trim)
disk(arena,"RecordInner",Vector3.new(0,.099,0),53.5,.06,slate)
disk(arena,"RecordLabel",Vector3.new(0,.131,0),20,.06,deck)
box(arena,"MixingDesk",0,4.5,0,28,9,8,ink,true)
box(arena,"ConsoleShell",0,8.15,0,29.5,1,8.5,trim,false)
for _,side in ipairs({-1,1}) do
 for i=1,8 do
  local h=1+(i%3)*.63
  box(arena,"ChannelMeter",i*2.6-11.7,5.7,side*4.05,.5,h,.14,gold,false)
 end
end
sign(arena,"HallSign",0,13.3,-73.6,32,5,"RESONANCE HALL","PVP ARENA",gold,Enum.NormalId.Back)
for _,side in ipairs({-1,1}) do
 for i,height in ipairs({1.4,3.2,5.6,8.9,6.5,4.3,2.6}) do
  box(arena,"StageWave",side*(19+i*2.3),7,-73.8,1.15,height,.25,trim,false)
 end
end

for _,xSide in ipairs({-1,1}) do
 for _,zSide in ipairs({-1,1}) do
  local x,z=xSide*69,zSide*55
  speaker(arena,xSide*53,zSide*42,zSide,true)
  speaker(arena,xSide*27,zSide*24,zSide,false)
  disk(arena,"SpawnMark",Vector3.new(x,.031,z),11,.06,slate)
  disk(arena,"SpawnRing",Vector3.new(x,.063,z),8,.06,gold)
  disk(arena,"SpawnCenter",Vector3.new(x,.095,z),7,.06,slate)
  local spawn=Instance.new("SpawnLocation")
  spawn.Name="Spawn_"..xSide.."_"..zSide
  spawn.Size=Vector3.new(5,.2,5)
  spawn.CFrame=CFrame.lookAt(Vector3.new(x,.1,z),Vector3.new(x-xSide*10,.1,z-zSide*10))
  spawn.Transparency=1
  spawn.Anchored=true
  spawn.CanCollide=false
  spawn.CanTouch=false
  spawn.CanQuery=false
  spawn.Duration=0
  spawn.Parent=arena
 end
end

local training=Instance.new("Folder")
training.Name="TrainingPreview"
training.Parent=world
box(training,"TrainingDeck",0,-1.5,248,72,3,48,deck,true)
for _,side in ipairs({-1,1}) do
 box(training,"SideRail",side*35,3,248,2,6,46,ink,true)
 box(training,"EndRail",0,3,248+side*23,70,6,2,ink,true)
end
sign(training,"ArrivalSign",-20,10,258,25,4.8,"TRAINING CITY","LOCAL PREVIEW",blue)
portal(arena,"TrainingPortal",Vector3.new(0,0,65),"TRAINING CITY","RETURN TO PRACTICE","Return to training",
 CFrame.lookAt(Vector3.new(0,3.5,240),Vector3.new(0,3.5,263)))
portal(training,"ArenaPortal",Vector3.new(0,0,265),"RESONANCE HALL","RETURN TO THE ARENA","Return to arena",
 CFrame.lookAt(Vector3.new(0,3.5,51),Vector3.new(0,3.5,0)))
world.Parent=workspace
