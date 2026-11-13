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
 local rig={parts={},contact={parts={},used=0},born=os.clock(),used=0};live[rig]=true;return rig
end
function Visuals.Update(rig,origin,direction,length,width,color,level,reduced)
 if direction.Magnitude<.01 or length<.01 then return end
 rig.origin=origin;rig.direction=direction.Unit;rig.length=math.clamp(length,.01,110)
 rig.width=math.clamp(width,1,7);rig.color=color;rig.level=level;rig.reduced=reduced
end
-- Accepted damage supplies a target anchor; a beam endpoint alone is not a hit.
function Visuals.Contact(rig,position,now,sequence)
 if not live[rig] or not rig.origin or typeof(position)~="Vector3" or type(now)~="number" or now~=now or math.abs(now)==math.huge then return false end
 for _,n in ipairs({position.X,position.Y,position.Z})do if n~=n or math.abs(n)==math.huge then return false end end
 if (position-rig.origin).Magnitude>Style.DrawDistance or now<(rig.nextContact or -math.huge) then return false end
 rig.contactPosition=position;rig.contactBorn=now;rig.nextContact=now+.4;rig.contactSequence=sequence
 rig.contactDirection=rig.direction
 rig.contactBasis=CFrame.lookAt(position,position+rig.direction,math.abs(rig.direction.Y)>.98 and Vector3.zAxis or Vector3.yAxis)
 return true
end
local function draw(rig,shape,size,cf,color,alpha,material,detail)
 rig.used+=1
 local part=rig.parts[rig.used]
 if not part then part=take(detail or rig.used>5);if not part then return end;rig.parts[rig.used]=part end
 -- A pooled slot may previously have been a non-emissive shell or a Neon detail.
 part.Material=material or Enum.Material.Neon
 part.Shape=shape;part.Size=size;part.CFrame=cf;part.Color=color;part.Transparency=alpha;part.Parent=workspace
end
local function line(rig,a,b,thickness,color,alpha,material,detail)
 local delta=b-a;local length=delta.Magnitude;if length<.001 then return end
 local direction=delta/length
 draw(rig,Enum.PartType.Cylinder,Vector3.new(length,thickness,thickness),
  CFrame.lookAt((a+b)*.5,b,math.abs(direction.Y)>.98 and Vector3.zAxis or Vector3.yAxis)*CFrame.Angles(0,math.pi/2,0),color,alpha,material,detail)
end
function Visuals.Animate(rig,now,viewer,reduced,contactAllowed,contactReduced)
 if not rig.origin then return end
 local distance=(viewer-rig.origin).Magnitude
 rig.used=0
 rig.contact.used=0
 if contactAllowed==false or distance>Style.DrawDistance or rig.contactBorn and now>=rig.contactBorn+.28 then rig.contactPosition=nil end
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
  local detailed=not quiet and distance<=Style.FarDistance
  local high=tier>=8
  -- Quiet mode retains its simple silhouette. Regular energy has a slim hot spine
  -- inside a non-emissive tinted body: Neon is reserved for the thin spine/details.
  line(rig,origin,finish,radius*(detailed and 1.35 or 1.65)*pulse,detailed and color:Lerp(Color3.fromRGB(0,0,0),.35) or color,quiet and .72 or detailed and (high and .78 or .55) or .68,detailed and Enum.Material.SmoothPlastic or nil)
  line(rig,origin,finish,radius*.85,color,quiet and .32 or detailed and (high and .7 or .18) or .12,detailed and Enum.Material.SmoothPlastic or nil)
  line(rig,origin,finish,radius*(detailed and .10 or .28),detailed and color:Lerp(white,.72) or white,quiet and .45 or .08)
  if quiet or distance>Style.FarDistance then
   draw(rig,Enum.PartType.Ball,Vector3.one*math.min(length,radius*1.5),CFrame.new(finish),color,.3)
  else
   -- An energy termination lens, not a hit-confirmation flash. Stay within range.
   local depth=math.min(length,radius*.22)
   line(rig,finish-dir*depth,finish,radius*1.25,color,.18,Enum.Material.SmoothPlastic)
  end
  if not quiet and distance<=Style.FarDistance then
   draw(rig,Enum.PartType.Ball,Vector3.one*radius*.72,CFrame.new(origin),color,.18,Enum.Material.SmoothPlastic)
   local function offset(angle,r) return (right*math.cos(angle)+up*math.sin(angle))*r end
   local function collarOffset(angle,r)
    if spec.collar=="diamond" then r/=math.abs(math.cos(angle))+math.abs(math.sin(angle))
    elseif spec.collar=="star" then r*=.72+.28*(.5+.5*math.cos(angle*5)) end
    local sweep=spec.collar=="diamond" and math.cos(angle)*r*.75 or 0
    return offset(angle,r)+dir*sweep
   end
   for ring=1,spec.rings do
    local travel=(age*(.6+tier*.025)+ring/spec.rings)%1
    local center=origin+dir*(travel*length)
    local r=radius*(.85+.2*math.sin(travel*math.pi))*(tier>=1 and 1.25 or 1)
    local offset=collarOffset
    for i=1,10 do
     local phase=age*.9+ring*.6
     -- Broken collars leave clear channels instead of stacking opaque hoops.
     -- One bright collar carries high tiers; supporting contours stay readable
     -- without stacking luminous hoops over the target and contact burst.
     local support=high and ring>1
     line(rig,center+offset((i-1)*math.pi/5+phase,r),center+offset((i-.28)*math.pi/5+phase,r),support and .1 or .16+tier*.012,support and color:Lerp(Color3.fromRGB(0,0,0),.2) or color,support and .6+travel*.25 or .26+travel*.32,support and Enum.Material.SmoothPlastic or nil)
    end
   end
   for strand=1,spec.strands do
    local previous=origin
    for i=1,12 do
     local t=i/12
     local winding=spec.ribbon=="braid" and (strand==1 and 1 or -1) or 1
     local phase=t*math.pi*2*spec.turns*winding-age*5+strand*math.pi
     local radial=radius*.95*math.sin(t*math.pi)
     if spec.ribbon=="zigzag" then phase=age*.35+strand*math.pi;radial*=i%2==0 and -1 or 1 end
     local point=origin+dir*(length*t)+offset(phase,radial)
     line(rig,previous,point,.065+tier*.006,color:Lerp(white,high and .12 or .4),high and .42 or .25,high and Enum.Material.SmoothPlastic or nil);previous=point
    end
   end
   for i=1,spec.sparks do
    local phase=i*math.pi*2/spec.sparks+age*(i%2==0 and .6 or -.6)
    -- Endpoint corona stays inside the authoritative beam width.
    local back=math.min(length*.15,radius*.8)
    line(rig,finish+offset(phase,radius*.25),finish-dir*back+offset(phase,width*.42),.08+tier*.006,color,high and .55 or .3,high and Enum.Material.SmoothPlastic or nil)
   end
  end
  if rig.contactPosition then
   local quietContact=quiet or contactReduced or distance>Style.FarDistance
   local progress=math.clamp((now-rig.contactBorn)/.28,0,1)
   local extent=math.min(width*.48,quietContact and 1.8 or 1.65+progress*.75)
   local inner=extent*(quietContact and .72 or .58+progress*.12)
   local count=quietContact and 4 or 8
   local contactDir=rig.contactDirection
   local contactRight,contactUp=rig.contactBasis.RightVector,rig.contactBasis.UpVector
   local center=rig.contactPosition-contactDir*.7
   -- Short outward strokes differ from traveling collars. Offset them from the
   -- root's body depth; quiet strokes stay still without screen/camera effects.
   for i=1,count do
    local angle=(i-.5)*math.pi*2/count
    local radial=contactRight*math.cos(angle)+contactUp*math.sin(angle)
    local from=center+radial*inner;local to=center+radial*extent
    line(rig.contact,from,to,.18,color:Lerp(Color3.fromRGB(0,0,0),.8),quietContact and .15 or .15+progress*.75,Enum.Material.SmoothPlastic,true)
    line(rig.contact,from-contactDir*.12,to-contactDir*.12,.1,color:Lerp(white,.3),quietContact and .3 or .1+progress*.85,Enum.Material.Neon,true)
   end
  end
 end
 for i=#rig.parts,rig.used+1,-1 do release(rig.parts[i]);rig.parts[i]=nil end
 for i=#rig.contact.parts,rig.contact.used+1,-1 do release(rig.contact.parts[i]);rig.contact.parts[i]=nil end
end
function Visuals.Destroy(rig)
 if not live[rig] then return end
 live[rig]=nil
 for _,part in ipairs(rig.parts) do release(part) end
 for _,part in ipairs(rig.contact.parts) do release(part) end
 table.clear(rig.parts)
 table.clear(rig.contact.parts);rig.contactPosition=nil
end
function Visuals.Clear()
 for rig in pairs(live) do Visuals.Destroy(rig) end
 for _,part in ipairs(pool) do part:Destroy() end
 table.clear(pool);allocated=0
end
function Visuals.Budget() return allocated,#pool end
return Visuals
