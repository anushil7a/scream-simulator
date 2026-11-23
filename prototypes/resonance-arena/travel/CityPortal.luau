-- Place the Hall entrance beside the existing Academy spawn.
local travel=require(script.Parent.TravelGate)
local function bind(world,spawnPosition)
 local ray=RaycastParams.new()
 ray.FilterType=Enum.RaycastFilterType.Include
 ray.FilterDescendantsInstances={world}
 ray.RespectCanCollide=true
 local point=spawnPosition+Vector3.new(8,0,0)
 local ground=assert(workspace:Raycast(point+Vector3.new(0,8,0),Vector3.new(0,-26,0),ray),"Missing Academy portal ground")
 local groundPosition=ground.Position
 -- The Academy paving is cosmetic and sits just above the collidable plateau.
 local paving=world:FindFirstChild("AcademySpine")
 local floorY=paving and paving.Position.Y+paving.Size.Y/2-groundPosition.Y or 0
 local gateway=Instance.new("Model")
 gateway.Name="HallGateway"
 gateway.ModelStreamingMode=Enum.ModelStreamingMode.Atomic
 local ink=Color3.fromRGB(27,44,55)
 local cyan=Color3.fromRGB(50,168,173)
 local gold=Color3.fromRGB(241,198,112)
 local amberLight=Color3.fromRGB(195,143,74)
 local function piece(name,size,offset,color,material)
  local part=Instance.new("Part")
  part.Name=name;part.Size=size;part.Position=groundPosition+offset
  part.Anchored=true;part.CanCollide=false;part.CanQuery=false;part.CanTouch=false;part.CastShadow=false
  part.Color=color;part.Material=material;part.Parent=gateway
  return part
 end
 local portal=piece("HallPortalAnchor",Vector3.new(1,6,8),Vector3.new(0,3,0),cyan,Enum.Material.SmoothPlastic)
 portal.Transparency=1
 -- Thin projected rails frame the opening without placing a barrier in the plaza.
 for _,side in ipairs({-1,1}) do
  local z=side*4.2
  piece("LightRail",Vector3.new(.3,7.1,.25),Vector3.new(0,3.63,z),cyan,Enum.Material.Neon)
  piece("RailFoot",Vector3.new(1.6,.048,1.55),Vector3.new(0,floorY+.032,z),ink,Enum.Material.SmoothPlastic)
 end
 piece("Threshold",Vector3.new(2.8,.04,7.8),Vector3.new(0,floorY+.028,0),ink,Enum.Material.SmoothPlastic)
 for _,x in ipairs({-1.1,1.1}) do
  piece("ThresholdLight",Vector3.new(.10,.03,7.8),Vector3.new(x,floorY+.065,0),cyan,Enum.Material.Neon)
 end
 piece("SoundBar",Vector3.new(.4,.22,8.7),Vector3.new(0,7.22,0),cyan,Enum.Material.Neon)
 for i,height in ipairs({.28,.48,.78,.48,.28}) do
  piece("Wave",Vector3.new(.26,height,.2),Vector3.new(0,7.35+height/2,(i-3)*.7),amberLight,Enum.Material.Neon)
 end
 local sign=piece("Destination",Vector3.new(5.3,1.55,.18),Vector3.new(-1.55,8.52,0),ink,Enum.Material.SmoothPlastic)
 sign.CFrame=CFrame.lookAt(sign.Position,sign.Position+Vector3.new(-1,0,1))
 local function face(part,name)
  local surface=Instance.new("SurfaceGui")
  surface.Name=name;surface.Face=Enum.NormalId.Front
  surface.SizingMode=Enum.SurfaceGuiSizingMode.PixelsPerStud;surface.PixelsPerStud=36
  surface.LightInfluence=.25;surface.Parent=part
  return surface
 end
 local function label(surface,text,y,height,color)
  local line=Instance.new("TextLabel")
  line.Text=text;line.Font=Enum.Font.GothamBold;line.TextColor3=color;line.TextScaled=true
  line.Position=UDim2.fromScale(.04,y);line.Size=UDim2.fromScale(.92,height)
  line.BackgroundTransparency=1;line.Parent=surface
 end
 local hallFace=face(sign,"HallSign")
 label(hallFace,"RESONANCE HALL",.08,.5,Color3.fromRGB(247,245,222))
 label(hallFace,"PVP ARENA",.62,.29,gold)
 -- The close plaque is often behind compact HUD controls. Join the Academy
 -- boards on their lower row where players can still see both directions.
 local marquee=world:FindFirstChild("NorthAcademyMarqueePostL",true)
 if marquee then
  local offset=marquee.Position-groundPosition+Vector3.new(-4.45,5.6,.45)
  local direction=piece("ArenaDirection",Vector3.new(8.9,1.65,.2),offset,ink,Enum.Material.SmoothPlastic)
  direction.CFrame=CFrame.lookAt(direction.Position,direction.Position+Vector3.zAxis)
  label(face(direction,"ArenaWayfinding"),"PVP ARENA →",.08,.84,gold)
 end
 gateway.Parent=world
 local prompt=Instance.new("ProximityPrompt")
 prompt.ActionText="Enter arena";prompt.ObjectText="Resonance Hall";prompt.HoldDuration=.25
 prompt.RequiresLineOfSight=false;prompt.MaxActivationDistance=10;prompt.Parent=portal
 travel.Bind(prompt)
 local arrival=groundPosition+Vector3.new(-8,3.8,0)
 travel.BindArrival(CFrame.lookAt(arrival,arrival-Vector3.zAxis),
  "Academy arrival. Find the training courts to the north.")
 return groundPosition
end
return bind
