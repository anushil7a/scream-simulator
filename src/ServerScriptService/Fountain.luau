-- Shared collision and water with a client-selected mesh or built-in fallback.
local Install={}
function Install.create(template,parent,origin)
 local m=Instance.new("Model");m.Name="MosaicFountain";m.ModelStreamingMode=Enum.ModelStreamingMode.Atomic
 local visual=template:Clone();visual.Name="DetailedVisual";visual.Parent=m
 for _,item in visual:GetDescendants() do
  if item:IsA("LuaSourceContainer") or item:IsA("PackageLink") then item:Destroy()
  elseif item:IsA("BasePart") then
   item.Anchored=true;item.CanCollide=false;item.CanTouch=false;item.CanQuery=false
  end
 end
 visual:ScaleTo(2)
 local box,size=visual:GetBoundingBox()
 visual:PivotTo(CFrame.new(origin+Vector3.new(0,size.Y/2,0))*box:ToObjectSpace(visual:GetPivot()))
 local fallback=Instance.new("Model");fallback.Name="FallbackVisual";fallback.Parent=m
 local function disk(name,radius,height,y,color,solid)
  local p=Instance.new("Part")
  p.Name=name;p.Shape=Enum.PartType.Cylinder
  p.Size=Vector3.new(height,radius*2,radius*2)
  p.CFrame=CFrame.new(origin+Vector3.new(0,y,0))*CFrame.Angles(0,0,math.pi/2)
  p.Anchored=true;p.CanCollide=solid;p.CanTouch=false;p.CanQuery=solid
  p.Color=color;p.CastShadow=false;p.Parent=m
  return p
 end
 -- One stable obstacle inside the original 32-stud navigation exclusion.
 -- Render meshes never use generated convex-hull collisions.
 local collider=disk("FountainCollision",14,5,2.5,Color3.new(),true)
 collider.Transparency=1
 local column=disk("ColumnCollision",2.5,14,10,Color3.new(),true);column.Transparency=1
 local bowl=disk("BowlCollision",5.5,1,18,Color3.new(),true);bowl.Transparency=1
 local stone=Color3.fromRGB(207,191,159)
 local function fallbackDisk(name,radius,height,y,color)
  local p=disk(name,radius,height,y,color,false);p.Material=Enum.Material.Limestone;p.CastShadow=true;p.Parent=fallback
 end
 fallbackDisk("BasinBase",14,.8,.4,stone)
 fallbackDisk("PedestalFoot",3.2,1.2,1.4,stone)
 fallbackDisk("Pedestal",2.2,14.7,9.3,stone)
 fallbackDisk("Bowl",5.5,1.1,17.9,stone)
 -- Separate rim segments leave the shared water visible in the fallback.
 for i=0,11 do
  local a=i*math.pi/6
  local rim=Instance.new("Part");rim.Name="StoneRim";rim.Size=Vector3.new(7.2,4.2,1.4)
  rim.CFrame=CFrame.new(origin+Vector3.new(math.sin(a)*12.9,2.8,math.cos(a)*12.9))*CFrame.Angles(0,a,0)
  rim.Anchored=true;rim.CanCollide=false;rim.CanTouch=false;rim.CanQuery=false;rim.Material=Enum.Material.Limestone;rim.Color=stone;rim.Parent=fallback
  local tile=rim:Clone();tile.Name="MosaicBand";tile.Size=Vector3.new(6.7,1.6,.05)
  tile.CFrame=rim.CFrame*CFrame.new(0,0,.73);tile.Color=i%2==0 and Color3.fromRGB(40,125,150) or Color3.fromRGB(53,85,143);tile.Material=Enum.Material.CeramicTiles;tile.Parent=fallback
 end
 local water=disk("BasinWater",11.35,.12,3.45,Color3.fromRGB(63,169,184),false)
 water.Material=Enum.Material.Glass;water.Transparency=.25;water.Reflectance=.12
 local upper=disk("BowlWater",2.3,.1,18.4,Color3.fromRGB(91,189,204),false)
 upper.Material=Enum.Material.Glass;upper.Transparency=.25
 -- Curved continuous streams; no physics droplets or per-frame script.
 for i=0,3 do
  local a=i*math.pi/2
  local radial=Vector3.new(math.cos(a),0,math.sin(a))
  local start=Instance.new("Attachment");start.Name="Spout"..i
  start.Parent=collider
  start.WorldCFrame=CFrame.fromMatrix(origin+radial*5+Vector3.new(0,18.2,0),radial,Vector3.yAxis)
  local finish=Instance.new("Attachment");finish.Name="Splash"..i;finish.Parent=collider
  finish.WorldCFrame=CFrame.fromMatrix(origin+radial*9+Vector3.new(0,3.5,0),-Vector3.yAxis,radial)
  local stream=Instance.new("Beam");stream.Name="WaterStream"..i
  stream.Attachment0=start;stream.Attachment1=finish
  stream.Width0=.16;stream.Width1=.24;stream.CurveSize0=2;stream.CurveSize1=7
  stream.Segments=12;stream.FaceCamera=true
  stream.Color=ColorSequence.new(Color3.fromRGB(156,225,234))
  stream.Transparency=NumberSequence.new(.3);stream.LightInfluence=.7;stream.Parent=collider
 end
 m.Parent=parent
 game:GetService("CollectionService"):AddTag(m,"OptionalLandmarkVisual")
 return m
end
return Install
