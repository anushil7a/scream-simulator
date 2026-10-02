-- Review-only assembly. Keep outside the main project until asset loading is verified.
local Install={}
function Install.create(template,parent,origin)
 local m=template:Clone()
 m.Name="MosaicFountain"
 for _,item in m:GetDescendants() do
  if item:IsA("LuaSourceContainer") or item:IsA("PackageLink") then item:Destroy()
  elseif item:IsA("BasePart") then
   item.Anchored=true;item.CanCollide=false;item.CanTouch=false;item.CanQuery=false
  end
 end
 m:ScaleTo(2)
 local box,size=m:GetBoundingBox()
 m:PivotTo(CFrame.new(origin+Vector3.new(0,size.Y/2,0))*box:ToObjectSpace(m:GetPivot()))
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
 return m
end
return Install
