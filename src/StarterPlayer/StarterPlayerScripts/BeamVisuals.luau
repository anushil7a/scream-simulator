-- One animated rig per attacker. Parts are pooled across attacks, never per pulse.
local Style=require(game:GetService("ReplicatedStorage").Shared.BeamStyle)
local Visuals={}
local pool,live={},{}
local allocated=0
local detailCount=0
local decoration={}
local white=Color3.fromRGB(245,252,255)
local function take(detail)
 if detail and detailCount>=Style.MaxParts-24*5 then return end
 local part=table.remove(pool)
 if not part then
  if allocated>=Style.MaxParts then return end
  part=Instance.new("Part");allocated+=1
  part.Name="VoiceEnergy";part.Anchored=true;part.CanCollide=false
  part.CanTouch=false;part.CanQuery=false;part.CastShadow=false
  part.Material=Enum.Material.Neon;part.TopSurface=Enum.SurfaceType.Smooth;part.BottomSurface=Enum.SurfaceType.Smooth
 end
 if detail then decoration[part]=true;detailCount+=1 end
 return part
end
local function release(part)
 if decoration[part] then decoration[part]=nil;detailCount-=1 end
 part.Parent=nil;table.insert(pool,part)
end
function Visuals.Create()
 local rig={parts={},born=os.clock(),used=0};live[rig]=true;return rig
end
function Visuals.Update(rig,origin,direction,length,width,color,level,reduced)
 if direction.Magnitude<.01 or length<.01 then return end
 rig.origin=origin;rig.direction=direction.Unit;rig.length=math.clamp(length,.01,110)
 rig.width=math.clamp(width,1,7);rig.color=color;rig.level=level;rig.reduced=reduced
end
local function draw(rig,shape,size,cf,color,alpha)
 rig.used+=1
 local part=rig.parts[rig.used]
 if not part then part=take(rig.used>5);if not part then return end;rig.parts[rig.used]=part end
 part.Shape=shape;part.Size=size;part.CFrame=cf;part.Color=color;part.Transparency=alpha;part.Parent=workspace
end
local function line(rig,a,b,thickness,color,alpha)
 local delta=b-a;local length=delta.Magnitude;if length<.001 then return end
 local direction=delta/length
 draw(rig,Enum.PartType.Cylinder,Vector3.new(length,thickness,thickness),
  CFrame.lookAt((a+b)*.5,b,math.abs(direction.Y)>.98 and Vector3.zAxis or Vector3.yAxis)*CFrame.Angles(0,math.pi/2,0),color,alpha)
end
function Visuals.Animate(rig,now,viewer,reduced)
 if not rig.origin then return end
 local distance=(viewer-rig.origin).Magnitude
 rig.used=0
 if distance<=Style.DrawDistance then
  local spec=Style.Detail(rig.level,reduced or rig.reduced,distance)
  local origin,dir,length,width,color=rig.origin,rig.direction,rig.length,rig.width,rig.color
  local basis=CFrame.lookAt(origin,origin+dir,math.abs(dir.Y)>.98 and Vector3.zAxis or Vector3.yAxis)
  local right,up=basis.RightVector,basis.UpVector
  local age=now-rig.born;local tier=spec.tier
  local quiet=reduced or rig.reduced
  local radius=width*(.24+tier*.012)*Style.LaunchScale(age,quiet)
  local finish=origin+dir*length
  -- Smooth low-amplitude breathing; no screen flash, camera shake or lights.
  local pulse=quiet and 1 or 1+.035*math.sin(age*9)
  line(rig,origin,finish,radius*1.65*pulse,color,quiet and .72 or .68)
  line(rig,origin,finish,radius*.85,color,quiet and .32 or .12)
  line(rig,origin,finish,radius*.28,white,quiet and .45 or .08)
  draw(rig,Enum.PartType.Ball,Vector3.one*math.min(length,radius*1.5),CFrame.new(finish),color,.3)
  if not quiet and distance<=Style.FarDistance then
   draw(rig,Enum.PartType.Ball,Vector3.one*radius*1.15,CFrame.new(origin),white,.18)
   local function offset(angle,r) return (right*math.cos(angle)+up*math.sin(angle))*r end
   for ring=1,spec.rings do
    local travel=(age*(.6+tier*.025)+ring/spec.rings)%1
    local center=origin+dir*(travel*length)
    local r=radius*(.85+.2*math.sin(travel*math.pi))
    for i=1,10 do
     local phase=age*.9+ring*.6
     line(rig,center+offset((i-1)*math.pi/5+phase,r),center+offset(i*math.pi/5+phase,r),.055+tier*.008,color,.22+travel*.28)
    end
   end
   for strand=1,spec.strands do
    local previous=origin
    for i=1,12 do
     local t=i/12;local phase=t*math.pi*(tier>=9 and 5 or 3)-age*5+strand*math.pi
     local point=origin+dir*(length*t)+offset(phase,radius*.95*math.sin(t*math.pi))
     line(rig,previous,point,.065+tier*.006,color:Lerp(white,.4),.25);previous=point
    end
   end
   for i=1,spec.sparks do
    local phase=i*math.pi*2/spec.sparks+age*(i%2==0 and .6 or -.6)
    -- Endpoint corona stays inside the authoritative beam width.
    line(rig,finish+offset(phase,radius*.35),finish+offset(phase,width*.47),.08+tier*.006,color,.3)
   end
  end
 end
 for i=#rig.parts,rig.used+1,-1 do release(rig.parts[i]);rig.parts[i]=nil end
end
function Visuals.Destroy(rig)
 if not live[rig] then return end
 live[rig]=nil
 for _,part in ipairs(rig.parts) do release(part) end
 table.clear(rig.parts)
end
function Visuals.Clear()
 for rig in pairs(live) do Visuals.Destroy(rig) end
 for _,part in ipairs(pool) do part:Destroy() end
 table.clear(pool);allocated=0
end
function Visuals.Budget() return allocated,#pool end
return Visuals
