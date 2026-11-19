-- Upload-free exact Blender surfaces. No external assets or editable-mesh permissions.
local Data=require(game:GetService("ReplicatedStorage").Shared.BossVisualData)
local Appearance={MaxParts=450}
-- Bounded presentation values; old callers retain the original scale/anchor.
function Appearance.Scale(value)
 if type(value)~="number" or value~=value or math.abs(value)==math.huge then return 1 end
 return math.clamp(value,1,2.8)
end
function Appearance.FromCore(position,spec)
 local height=spec and spec.aimHeight
 if type(height)~="number" or height~=height or math.abs(height)==math.huge then height=5 end
 return position-Vector3.new(0,math.clamp(height,0,20),0),Appearance.Scale(spec and spec.scale)
end
local function configure(p,parent,color,glow,style)
 p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.CastShadow=not glow
 p.Material=glow and Enum.Material.Neon or Enum.Material[style.material];p.Color=color
 p.Reflectance=glow and 0 or style.reflectance
 p.TopSurface=Enum.SurfaceType.Smooth;p.BottomSurface=Enum.SurfaceType.Smooth;p.Parent=parent
end
local function triangle(parent,name,a,b,c,color,glow,style,center,scale)
 local ab,ac,bc=b-a,c-a,c-b
 if ab:Dot(ab)>ac:Dot(ac) and ab:Dot(ab)>bc:Dot(bc) then c,a=a,c elseif ac:Dot(ac)>bc:Dot(bc) then a,b=b,a end
 ab,ac,bc=b-a,c-a,c-b
 local normal=ac:Cross(ab)
 if normal.Magnitude<1e-6 or bc.Magnitude<1e-6 then return 0 end
 local right=normal.Unit;local back=bc.Unit;local up=bc:Cross(right).Unit
 local height=math.abs(ab:Dot(up));local count=0
 for _,v in ipairs({{(a+b)/2,right,back,math.abs(ab:Dot(back))},{(a+c)/2,-right,-back,math.abs(ac:Dot(back))}}) do
  if v[4]>1e-5 and height>1e-5 then
   local p=Instance.new("WedgePart");p.Name=name;p.Size=Vector3.new(.015*math.max(1,scale/1.4),height*scale,v[4]*scale)
   p.CFrame=CFrame.fromMatrix(center+v[1]*scale,v[2],up,v[3]);configure(p,parent,color,glow,style);count+=1
  end
 end
 return count
end
function Appearance.Build(parent,id,center,alive,pause,visualScale)
 local scale=Appearance.Scale(visualScale)
 local entries=Data[id];if not entries then return false,"unknown" end
 local count,sinceYield=0,0
 for _,entry in ipairs(entries) do
  if not alive() then return false,"canceled" end
  local color=Color3.fromRGB(table.unpack(entry.color))
  if entry.kind=="Surface" then
   for _,face in ipairs(entry.triangles) do
    if not alive() then return false,"canceled" end
    local a=Vector3.new(table.unpack(entry.vertices[face[1]+1]))
    local b=Vector3.new(table.unpack(entry.vertices[face[2]+1]))
    local c=Vector3.new(table.unpack(entry.vertices[face[3]+1]))
    local added=triangle(parent,entry.name,a,b,c,color,entry.glow,entry,center,scale);count+=added;sinceYield+=added
    assert(count<=Appearance.MaxParts,"Boss visual part budget exceeded")
    if sinceYield>=32 then sinceYield=0;pause() end
   end
  else
   local p=Instance.new("Part");p.Name=entry.name;p.Size=Vector3.new(table.unpack(entry.size))*scale;p.Shape=Enum.PartType[entry.kind]
   p.CFrame=CFrame.new(center+Vector3.new(table.unpack(entry.position))*scale)*CFrame.new(0,0,0,table.unpack(entry.rotation))
   configure(p,parent,color,entry.glow,entry);count+=1;sinceYield+=1
   assert(count<=Appearance.MaxParts,"Boss visual part budget exceeded")
   if sinceYield>=32 then sinceYield=0;pause() end
  end
 end
 if not alive() then return false,"canceled" end
 parent:SetAttribute("VisualScale",scale);parent:SetAttribute("GeometryPartCount",count);parent:SetAttribute("GeometryReady",true)
 return true,count
end
return Appearance
