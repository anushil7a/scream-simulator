-- One animated rig per attacker. Parts are pooled across attacks, never per pulse.
local Style=require(game:GetService("ReplicatedStorage").Shared.BeamStyle)
local Visuals={}
local pool,live={},{}
local allocated=0
-- Reserve five core Parts per admitted beam and one local confirmed-hit burst.
local coreLimit,contactLimit=24*5,16
local limits={core=coreLimit,contact=contactLimit,detail=Style.MaxParts-coreLimit-contactLimit}
local inUse={core=0,contact=0,detail=0}
local partKind={}
local white=Color3.fromRGB(245,252,255)
local isRoblox=typeof(game)=="Instance"
local cachedTemplatesFolder=nil
local function getVfxTemplates()
 if not isRoblox then return nil end
 if cachedTemplatesFolder and cachedTemplatesFolder.Parent then return cachedTemplatesFolder end
 local rs=game:GetService("ReplicatedStorage")
 cachedTemplatesFolder=rs and rs:FindFirstChild("VfxTemplates") or nil
 return cachedTemplatesFolder
end
local function styleColor(rgb,fallback)
 if not rgb then return fallback end
 return Color3.fromRGB(rgb[1],rgb[2],rgb[3])
end
local function makeAnchorPart(name)
 local p=Instance.new("Part")
 p.Name=name;p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.CastShadow=false
 p.Transparency=1;p.Size=Vector3.new(.2,.2,.2)
 return p
end
local function disablePhysics(inst)
 if inst:IsA("BasePart") then
  inst.Anchored=true;inst.CanCollide=false;inst.CanTouch=false;inst.CanQuery=false;inst.CastShadow=false
 end
end
local function scaleNumberSequence(seq,factor)
 local kps=seq.Keypoints
 local out=table.create(#kps)
 for i,kp in ipairs(kps) do
  out[i]=NumberSequenceKeypoint.new(kp.Time,kp.Value*factor,kp.Envelope*factor)
 end
 return NumberSequence.new(out)
end
local function scaleNumberRange(rng,factor)
 return NumberRange.new(rng.Min*factor,rng.Max*factor)
end
local function destroyVfx(rig)
 local vfx=rig.vfx
 if not vfx then return end
 rig.vfx=nil
 if vfx.root then vfx.root:Destroy() end
end
local function trackBeam(vfx,beam,isCore,minLightEmission)
 beam.LightEmission=math.max(beam.LightEmission,minLightEmission or 0)
 table.insert(vfx.beams,{
  inst=beam,
  baseW0=beam.Width0,
  baseW1=beam.Width1,
  baseCurve0=beam.CurveSize0,
  baseCurve1=beam.CurveSize1,
  baseTextureSpeed=beam.TextureSpeed,
  isCore=isCore,
 })
end
local function trackEmitter(vfx,emitter,isCore,minLightEmission,maxRate)
 if minLightEmission then emitter.LightEmission=math.max(emitter.LightEmission,minLightEmission) end
 local rate=maxRate and math.min(emitter.Rate,maxRate) or emitter.Rate
 emitter.Rate=rate
 table.insert(vfx.emitters,{
  inst=emitter,
  baseSize=emitter.Size,
  baseSpeed=emitter.Speed,
  baseRate=rate,
  isCore=isCore,
 })
end
local function buildStarterVfx(template)
 local clone=template:Clone()
 local root=Instance.new("Model");root.Name="BeamVfx_starter"
 local startAnchor=makeAnchorPart("StartAnchor");startAnchor.Parent=root
 local endAnchor=makeAnchorPart("EndAnchor");endAnchor.Parent=root
 local startAtt=Instance.new("Attachment");startAtt.Name="StartAtt";startAtt.Parent=startAnchor
 local endAtt=Instance.new("Attachment");endAtt.Name="EndAtt";endAtt.Parent=endAnchor
 local vfx={styleId="starter",root=root,startAnchor=startAnchor,endAnchor=endAnchor,beams={},emitters={},meshes={},attOffsets={}}
 local srcPart=clone:FindFirstChild("Part")
 local srcEnd=clone:FindFirstChild("Part1")
 if srcPart then
  local att=srcPart:FindFirstChildOfClass("Attachment")
  if att then
   att.CFrame=CFrame.identity;att.Parent=startAnchor
   for _,em in ipairs(att:GetChildren()) do
    if em:IsA("ParticleEmitter") then trackEmitter(vfx,em,false) end
   end
  end
  local beamIdx=0
  for _,ch in ipairs(srcPart:GetChildren()) do
   if ch:IsA("Beam") then
    beamIdx+=1
    ch.Attachment0=startAtt;ch.Attachment1=endAtt;ch.Parent=startAnchor
    trackBeam(vfx,ch,beamIdx<=2,.7)
   end
  end
 end
 if srcEnd then
  local att=srcEnd:FindFirstChildOfClass("Attachment")
  if att then
   att.CFrame=CFrame.identity;att.Parent=endAnchor
   for _,em in ipairs(att:GetChildren()) do
    if em:IsA("ParticleEmitter") then trackEmitter(vfx,em,false) end
   end
  end
 end
 clone:Destroy()
 return vfx
end
local function buildFireBeamVfx(template)
 local clone=template:Clone()
 local root=Instance.new("Model");root.Name="BeamVfx_firebeam"
 local startAnchor=makeAnchorPart("StartAnchor");startAnchor.Parent=root
 local endAnchor=makeAnchorPart("EndAnchor");endAnchor.Parent=root
 local midAnchor=makeAnchorPart("MidAnchor");midAnchor.Parent=root
 local startAtt=Instance.new("Attachment");startAtt.Name="StartAtt";startAtt.Parent=startAnchor
 local endAtt=Instance.new("Attachment");endAtt.Name="EndAtt";endAtt.Parent=endAnchor
 local vfx={styleId="firebeam",root=root,startAnchor=startAnchor,endAnchor=endAnchor,midAnchor=midAnchor,beams={},emitters={},meshes={},attOffsets={}}
 local outerMesh=clone:FindFirstChild("Beam")
 local innerMesh=outerMesh and outerMesh:FindFirstChild("Beam")
 local rotXtoNegZ=CFrame.Angles(0,math.pi/2,0)
 if outerMesh then
  local beamIdx=0
  for _,ch in ipairs(outerMesh:GetChildren()) do
   if ch:IsA("Beam") then
    beamIdx+=1
    ch.Attachment0=startAtt;ch.Attachment1=endAtt;ch.Parent=startAnchor
    trackBeam(vfx,ch,beamIdx<=2,.45)
   elseif ch:IsA("ParticleEmitter") then
    ch.Parent=midAnchor
    trackEmitter(vfx,ch,false,.15,18)
   elseif ch:IsA("Attachment") and ch.Name=="Start" then
    for _,sub in ipairs(ch:GetChildren()) do
     if sub:IsA("Attachment") then
      sub.CFrame=rotXtoNegZ;sub.Parent=startAnchor
      for _,em in ipairs(sub:GetChildren()) do
       if em:IsA("ParticleEmitter") then trackEmitter(vfx,em,false,.1,18) end
      end
     elseif sub:IsA("ParticleEmitter") then
      local muzzleAtt=Instance.new("Attachment");muzzleAtt.CFrame=rotXtoNegZ;muzzleAtt.Parent=startAnchor
      sub.Parent=muzzleAtt
      trackEmitter(vfx,sub,false,.1,14)
     end
    end
   end
  end
 end
 if innerMesh then
  local windHolder=innerMesh:FindFirstChild("WindBeamHolder")
  if windHolder then
   local a1,a2=windHolder:FindFirstChild("a1"),windHolder:FindFirstChild("a2")
   local a3,a4=windHolder:FindFirstChild("a3"),windHolder:FindFirstChild("a4")
   if a1 and a3 then
    a1.Parent=startAnchor;a3.Parent=endAnchor
    table.insert(vfx.attOffsets,{att=a1,side=-.55})
    table.insert(vfx.attOffsets,{att=a3,side=-.28})
    for _,b in ipairs(a1:GetChildren()) do
     if b:IsA("Beam") then b.Attachment0=a1;b.Attachment1=a3;b.Parent=startAnchor;trackBeam(vfx,b,false,.25) end
    end
   end
   if a2 and a4 then
    a2.Parent=startAnchor;a4.Parent=endAnchor
    table.insert(vfx.attOffsets,{att=a2,side=.55})
    table.insert(vfx.attOffsets,{att=a4,side=.28})
    for _,b in ipairs(a2:GetChildren()) do
     if b:IsA("Beam") then b.Attachment0=a2;b.Attachment1=a4;b.Parent=startAnchor;trackBeam(vfx,b,false,.25) end
    end
   end
  end
  local slashIdx=0
  for _,ch in ipairs(innerMesh:GetChildren()) do
   if ch:IsA("Attachment") and ch.Name=="Left" then
    for _,b in ipairs(ch:GetChildren()) do
     if b:IsA("Beam") and b.Attachment1 and b.Attachment1:IsA("Attachment") then
      slashIdx+=1
      local aL=Instance.new("Attachment");local aR=Instance.new("Attachment")
      local frac=math.clamp(.22+(slashIdx%3)*.26,.15,.85)
      local sign=slashIdx%2==0 and 1 or -1
      aL.Parent=midAnchor;aR.Parent=midAnchor
      table.insert(vfx.attOffsets,{att=aL,midFrac=frac-.08,side=-.48*sign,ySide=.32*sign})
      table.insert(vfx.attOffsets,{att=aR,midFrac=frac+.08,side=.48*sign,ySide=-.32*sign})
      b.Attachment0=aL;b.Attachment1=aR;b.Parent=midAnchor
      trackBeam(vfx,b,false,.35)
     end
    end
   end
  end
  for _,ch in ipairs(innerMesh:GetChildren()) do
   if ch:IsA("Attachment") or ch:IsA("ParticleEmitter") or ch:IsA("Model") or ch:IsA("BasePart") then
    if not ch:IsA("Attachment") then ch:Destroy() end
   end
  end
  disablePhysics(innerMesh)
  innerMesh.Transparency=.42;innerMesh.Material=Enum.Material.Neon
  innerMesh.Color=styleColor(Style.Styles.firebeam.primary,white)
  innerMesh.Parent=root
  table.insert(vfx.meshes,{inst=innerMesh,role="sheath",baseTrans=.42})
 end
 local strat=clone:FindFirstChild("strat")
 if strat then
  local st=strat:FindFirstChild("Start")
  if st then
   for _,sub in ipairs(st:GetChildren()) do
    if sub:IsA("Attachment") then
     sub.CFrame=rotXtoNegZ;sub.Parent=startAnchor
     for _,em in ipairs(sub:GetChildren()) do
      if em:IsA("ParticleEmitter") then trackEmitter(vfx,em,false,.15,14) end
     end
    end
   end
  end
 end
 clone:Destroy()
 return vfx
end
-- The reference contains three separate demonstrations, not three layers of one beam.
-- Preserve only the central violet Hollow Purple recipe; Amplified and Reversal
-- are blue/red alternatives. Combining them made the previous result a rainbow.
local function buildHollowPurpleVfx(template)
 local holder=template:FindFirstChild("Hollow Purple")
 if not holder then return nil end
 local root=Instance.new("Model");root.Name="BeamVfx_hollow_purple"
 local startAnchor=makeAnchorPart("StartAnchor");startAnchor.Parent=root
 local endAnchor=makeAnchorPart("EndAnchor");endAnchor.Parent=root
 local midAnchor=makeAnchorPart("MidAnchor");midAnchor.Parent=root
 local startAtt=Instance.new("Attachment");startAtt.Parent=startAnchor
 local endAtt=Instance.new("Attachment");endAtt.Parent=endAnchor
 local vfx={styleId="hollow_purple",root=root,startAnchor=startAnchor,endAnchor=endAnchor,
  midAnchor=midAnchor,beams={},emitters={},meshes={},attOffsets={}}
 for _,source in ipairs(holder:GetDescendants()) do
  -- Clone only reviewed visual primitives. No scripts or unknown descendants run.
  if source:IsA("Beam") and #vfx.beams<5 then
   local beam=source:Clone();beam:ClearAllChildren()
   beam.Attachment0=startAtt;beam.Attachment1=endAtt;beam.Parent=startAnchor
   -- Keep source colors, width ratios, curves and emission. Do not bleach violet.
   trackBeam(vfx,beam,#vfx.beams<2)
  elseif source:IsA("ParticleEmitter") and #vfx.emitters<4 then
   local emitter=source:Clone();emitter:ClearAllChildren();emitter.Parent=midAnchor
   trackEmitter(vfx,emitter,false,nil,12)
  end
 end
 -- No invented opaque pink muzzle/travel balls: the source is a tapered violet
 -- energy column, with texture/sparks providing its silhouette instead.
 return vfx
end
local function buildVfxForStyle(styleId)
 local templates=getVfxTemplates()
 if not templates then return nil end
 if styleId=="hollow_purple" then
  local t=templates:FindFirstChild("HollowPurpleBeam")
  return t and buildHollowPurpleVfx(t) or nil
 elseif styleId=="firebeam" then
  local t=templates:FindFirstChild("FireBeam")
  return t and buildFireBeamVfx(t) or nil
 end
 local t=templates:FindFirstChild("StarterBeam")
 return t and buildStarterVfx(t) or nil
end
local function syncVfx(rig,origin,finish,dir,basis,length,width,radius,age,quiet,distance,spec,suppressSecondary)
 local styleId=spec.id
 local vfx=rig.vfx
 if vfx and vfx.styleId~=styleId then destroyVfx(rig);vfx=nil end
 if not vfx then
  vfx=buildVfxForStyle(styleId)
  if not vfx then return end
  rig.vfx=vfx
 end
 if vfx.root.Parent~=workspace then vfx.root.Parent=workspace end
 local up=math.abs(dir.Y)>.98 and Vector3.zAxis or Vector3.yAxis
 local mid=(origin+finish)*.5
 vfx.startAnchor.CFrame=CFrame.lookAt(origin,finish,up)
 vfx.endAnchor.CFrame=CFrame.lookAt(finish,finish+dir,up)
 if vfx.midAnchor then
  if styleId=="firebeam" then
   vfx.midAnchor.Size=Vector3.new(math.max(1,length*.9),math.max(.8,width*.55),math.max(.8,width*.55))
   vfx.midAnchor.CFrame=CFrame.lookAt(mid,finish,up)*CFrame.Angles(0,math.pi/2,0)
  else
   vfx.midAnchor.Size=Vector3.new(math.max(.6,width*.4),math.max(.6,width*.4),math.max(1,length*.9))
   vfx.midAnchor.CFrame=CFrame.lookAt(mid,finish,up)
  end
 end
 local wScale,pScale,sScale
 if styleId=="hollow_purple" then
  wScale=math.clamp((width*.80)/13.61538,.08,.42)
  pScale=math.clamp(width/13.61538,.08,.52)
  sScale=math.clamp(length/44,.05,1.5)
  if vfx.ampAtt then vfx.ampAtt.Position=Vector3.new(-width*.45,0,0) end
  if vfx.revAtt then vfx.revAtt.Position=Vector3.new(width*.45,0,0) end
 elseif styleId=="firebeam" then
  wScale=math.clamp((width*.48)/15,.08,.30)
  pScale=wScale*1.3
  sScale=wScale*1.3
 else
  wScale=math.clamp((width*.42)/1.5,.45,2.2)
  pScale=math.clamp(wScale*.85,.45,1.6)
  sScale=pScale
 end
 local far=quiet or distance>Style.FarDistance
 local showSecondary=not far and not suppressSecondary
 local scale=Style.WidthScale(rig.level,far)
 -- Normalize against the actual selected recipe, not a guessed pack width.
 -- Family switches at 40/80 must not shrink a newly earned milestone.
 local widest=.001
 for _,entry in ipairs(vfx.beams) do
  if not far or entry.isCore then widest=math.max(widest,entry.baseW0,entry.baseW1) end
 end
 wScale=width*.6*scale/widest
 pScale*=math.min(scale,1.5)
 local bucket=wScale
 local rescale=vfx.lastBucket~=bucket
 if rescale then vfx.lastBucket=bucket end
 for _,entry in ipairs(vfx.beams) do
  local b=entry.inst
  b.Enabled=showSecondary or entry.isCore
   b.TextureSpeed=far and 0 or entry.baseTextureSpeed
  if rescale then
   local factor=entry.isCore and wScale or (styleId=="hollow_purple" and entry.baseCurve0~=0 and wScale*.58 or wScale)
   b.Width0=entry.baseW0*factor
   b.Width1=entry.baseW1*factor
  end
 end
 for _,entry in ipairs(vfx.emitters) do
  local em=entry.inst
  if not showSecondary and em.Enabled then em:Clear() end
   -- Endpoint particle clusters read as the rejected firing spheres. Only
   -- reviewed column emitters remain; lightning is original pooled geometry.
   em.Enabled=showSecondary and vfx.midAnchor~=nil and em.Parent==vfx.midAnchor
   em.Rate=math.min(entry.baseRate,60/math.max(1,#vfx.emitters))
  if rescale then
   em.Size=scaleNumberSequence(entry.baseSize,pScale)
   em.Speed=scaleNumberRange(entry.baseSpeed,sScale)
  end
 end
 for _,off in ipairs(vfx.attOffsets) do
  if off.midFrac then
   off.att.Position=Vector3.new((off.midFrac-.5)*length,width*(off.ySide or 0),width*(off.side or 0))
  else
   off.att.Position=Vector3.new(width*(off.side or 0),0,0)
  end
 end
 for _,m in ipairs(vfx.meshes) do
  local mesh=m.inst
  mesh.Transparency=1 -- No imported mesh bulbs on the firing path.
  if not far then
   local d=math.max(.8,width*.68)
   mesh.Size=Vector3.new(length,d,d)
   mesh.CFrame=CFrame.lookAt(mid,finish,up)*CFrame.Angles(0,math.pi/2,0)
  end
 end

end
local function take(kind)
 if inUse[kind]>=limits[kind] then return end
 local part=table.remove(pool)
 if not part then
  if allocated>=Style.MaxParts then return end
  part=Instance.new("Part");allocated+=1
  part.Name="VoiceEnergy";part.Anchored=true;part.CanCollide=false
  part.CanTouch=false;part.CanQuery=false;part.CastShadow=false
  part.Material=Enum.Material.Neon;part.TopSurface=Enum.SurfaceType.Smooth;part.BottomSurface=Enum.SurfaceType.Smooth
 end
 partKind[part]=kind;inUse[kind]+=1
 return part
end
local function release(part)
 local kind=partKind[part]
 partKind[part]=nil;inUse[kind]-=1
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
local function draw(rig,shape,size,cf,color,alpha,material,kind)
 local nextIndex=rig.used+1
 local part=rig.parts[nextIndex]
 if not part then part=take(kind or (nextIndex>5 and "detail" or "core"));if not part then return end;rig.parts[nextIndex]=part end
 -- Count successful allocations only. Native tint/contact loops must never visit holes.
 rig.used=nextIndex
 -- A pooled slot may previously have been a non-emissive shell or a Neon detail.
 part.Material=material or Enum.Material.Neon
 if isRoblox then part.LocalTransparencyModifier=0 end
 part.Shape=shape;part.Size=size;part.CFrame=cf;part.Color=color;part.Transparency=alpha;part.Parent=workspace
end
local function line(rig,a,b,thickness,color,alpha,material,kind)
 local delta=b-a;local length=delta.Magnitude;if length<.001 then return end
 local direction=delta/length
 draw(rig,Enum.PartType.Cylinder,Vector3.new(length,thickness,thickness),
  CFrame.lookAt((a+b)*.5,b,math.abs(direction.Y)>.98 and Vector3.zAxis or Vector3.yAxis)*CFrame.Angles(0,math.pi/2,0),color,alpha,material,kind)
end
function Visuals.IsCrowded(entries,viewer)
 local nearby=0
 for _,entry in pairs(entries) do
  local origin=entry.visual.origin
  if origin and (viewer-origin).Magnitude<=Style.FarDistance then
   nearby+=1
   if nearby==3 then return true end
  end
 end
 return false
end
function Visuals.Animate(rig,now,viewer,reduced,contactAllowed,contactReduced,suppressSecondary)
 if not rig.origin then return end
 local distance=(viewer-rig.origin).Magnitude
 rig.used=0
 rig.contact.used=0
 if contactAllowed==false or distance>Style.DrawDistance or rig.contactBorn and now>=rig.contactBorn+.28 then rig.contactPosition=nil end
 if distance<=Style.DrawDistance then
  local spec=Style.Detail(rig.level,reduced or rig.reduced or contactReduced,distance)
  local origin,dir,length,width,color=rig.origin,rig.direction,rig.length,rig.width,rig.color
  local basis=CFrame.lookAt(origin,origin+dir,math.abs(dir.Y)>.98 and Vector3.zAxis or Vector3.yAxis)
  local right,up=basis.RightVector,basis.UpVector
  local age=now-rig.born;local tier=spec.tier
  local quiet=reduced or rig.reduced or contactReduced
  local radius=width*(.24+tier*.012)*Style.WidthScale(rig.level,quiet or distance>Style.FarDistance)*Style.LaunchScale(age,quiet or distance>Style.FarDistance)
  local finish=origin+dir*length
  -- Smooth low-amplitude breathing; no screen flash, camera shake or lights.
  local pulse=(quiet or distance>Style.FarDistance) and 1 or 1+.035*math.sin(age*9)
  local detailed=not quiet and distance<=Style.FarDistance
  local high=tier>=8
  -- Quiet mode retains its simple silhouette. Regular energy has a slim hot spine
  -- inside a non-emissive tinted body: Neon is reserved for the thin spine/details.
  line(rig,origin,finish,radius*(detailed and 1.35 or 1.65)*pulse,detailed and color:Lerp(Color3.fromRGB(0,0,0),.35) or color,quiet and .72 or detailed and (high and .78 or .55) or .68,detailed and Enum.Material.SmoothPlastic or nil)
  line(rig,origin,finish,radius*.85,color,quiet and .32 or detailed and (high and .7 or .18) or .12,detailed and Enum.Material.SmoothPlastic or nil)
  line(rig,origin,finish,radius*(detailed and .10 or .28),detailed and color:Lerp(white,.72) or white,quiet and .45 or .08)
  if quiet or distance>Style.FarDistance then
   line(rig,finish-dir*math.min(length,.12),finish,radius*.8,color,.55)
  else
   -- An energy termination lens, not a hit-confirmation flash. Stay within range.
   local depth=math.min(length,radius*.22)
   local endAlpha=suppressSecondary and .95 or rig.contactPosition and .86 or .18
   line(rig,finish-dir*depth,finish,radius*1.25,color,endAlpha,Enum.Material.SmoothPlastic)
  end
  if not quiet and distance<=Style.FarDistance then
   -- Thin axial ignition streak, never a launch sphere.
   line(rig,origin,origin+dir*math.min(length,1.5),radius*.12,color,.18,Enum.Material.SmoothPlastic)
  end
  if detailed and not suppressSecondary then
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
     -- Angular, continuous electric filaments from VFX-02, not rotating beads.
     -- Low-amplitude drift keeps crisp bends without random/strobing flashes.
     local phase=strand*math.pi*2/spec.strands+t*spec.turns+age*.35
     local radial=radius*(i%2==0 and .95 or .48)*math.sin(t*math.pi)
     local point=origin+dir*(length*t)+offset(phase,radial)
     line(rig,previous,point,.075+tier*.012,color:Lerp(white,.35),.22,Enum.Material.Neon);previous=point
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
   local quietContact=quiet or distance>Style.FarDistance
   local progress=math.clamp((now-rig.contactBorn)/.28,0,1)
   local ease=1-(1-progress)^3
   local heat=(1-progress)^2
   local fade=progress*progress
   local extent=math.min(width*.48,quietContact and 1.8 or 1.65+ease*.75)
   local inner=extent*(quietContact and .72 or .52+ease*.24)
   local count=quietContact and 4 or 8
   local contactDir=rig.contactDirection
   local contactRight,contactUp=rig.contactBasis.RightVector,rig.contactBasis.UpVector
   local center=rig.contactPosition-contactDir*.7
   local backThickness=quietContact and .18 or .2-.08*progress
   local coreThickness=quietContact and .1 or .12-.07*progress
   local coreColor=color:Lerp(white,quietContact and .3 or .2+.55*heat)
   -- Short outward strokes differ from traveling collars. Offset them from the
   -- root's body depth; quiet strokes stay still without screen/camera effects.
   for i=1,count do
    local angle=(i-.5)*math.pi*2/count
    local radial=contactRight*math.cos(angle)+contactUp*math.sin(angle)
    local from=center+radial*inner;local to=center+radial*extent
    line(rig.contact,from,to,backThickness,color:Lerp(Color3.fromRGB(0,0,0),.8),quietContact and .15 or .1+fade*.82,Enum.Material.SmoothPlastic,"contact")
    line(rig.contact,from-contactDir*.12,to-contactDir*.12,coreThickness,coreColor,quietContact and .3 or .05+fade*.9,Enum.Material.Neon,"contact")
   end
  end
  if isRoblox then
   local styleSpec=Style.StyleForLevel(rig.level)
   local pCol=styleColor(styleSpec.primary,color)
   local sCol=styleColor(styleSpec.secondary,white)
   syncVfx(rig,origin,finish,dir,basis,length,width,radius,age,quiet or contactReduced,distance,styleSpec,suppressSecondary)
   local hasVfx=rig.vfx~=nil
   for i=1,rig.used do
    local p=rig.parts[i]
    if i==1 or (i==2 and hasVfx) then
     p.LocalTransparencyModifier=1
    elseif partKind[p]=="detail" then
     -- Native templates must not erase the ten-level lightning progression.
     p.Color=pCol:Lerp(sCol,.35);p.LocalTransparencyModifier=0
    elseif i==2 then
     p.Color=pCol;p.LocalTransparencyModifier=.35
    elseif i==3 then
     p.Color=pCol:Lerp(white,.55);p.LocalTransparencyModifier=hasVfx and .25 or .1
    elseif i==4 then
     p.Color=sCol;p.LocalTransparencyModifier=.2
    elseif i==5 then
     p.Color=pCol;p.LocalTransparencyModifier=.2
    end
   end
   for i=1,rig.contact.used do
    local cp=rig.contact.parts[i]
    cp.LocalTransparencyModifier=0
    cp.Color=i%2==1 and pCol:Lerp(Color3.fromRGB(0,0,0),.8) or pCol:Lerp(white,.45)
   end
  end
 elseif isRoblox then
  destroyVfx(rig)
 end
 for i=#rig.parts,rig.used+1,-1 do release(rig.parts[i]);rig.parts[i]=nil end
 for i=#rig.contact.parts,rig.contact.used+1,-1 do release(rig.contact.parts[i]);rig.contact.parts[i]=nil end
end
function Visuals.Destroy(rig)
 if not live[rig] then return end
 live[rig]=nil
 if isRoblox then destroyVfx(rig) end
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
