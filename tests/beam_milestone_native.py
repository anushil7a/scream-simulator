"""Execute actual template builders + sync/visibility with bounded Instance-tree doubles.
Not a native rendering, asset-permission, voice transport or GPU test.
"""
from pathlib import Path
import subprocess,tempfile
from xml.etree import ElementTree
import beam_silhouette as support
R=Path(__file__).resolve().parents[1]
P=R/'src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau'
hollow_asset=ElementTree.parse(R/'assets/vfx/HollowPurpleBeam.rbxmx')
central=next(item for item in hollow_asset.iter('Item')
             if item.findtext('Properties/string[@name="Name"]')=='Hollow Purple')
roles={item.findtext('Properties/string[@name="Name"]'): item.findtext('Properties/Content[@name="Texture"]/url')
       for item in central.iter('Item') if item.get('class')=='Beam'}
assert {name: texture for name,texture in roles.items() if name.startswith('Core')} == {
    'CoreSpine':'rbxassetid://107624017803706', 'CoreFlow':'rbxassetid://13135259077',
}, roles
ENV=r'''
local objects={}
local methods={}
local mt={__index=function(self,k)if k=='Parent' then return rawget(self,'_parent')end;return methods[k]end,
 __newindex=function(self,k,v)if k=='Parent' then rawset(self,'_parent',v)else rawset(self,k,v)end end}
function methods:IsA(c)return self.ClassName==c or c=='BasePart' and (self.ClassName=='Part' or self.ClassName=='MeshPart')end
function methods:GetChildren()local out={};for _,v in ipairs(objects)do if not v.dead and v.Parent==self then table.insert(out,v)end end;return out end
function methods:GetDescendants()local out={};for _,v in ipairs(self:GetChildren())do table.insert(out,v);for _,sub in ipairs(v:GetDescendants())do table.insert(out,sub)end end;return out end
function methods:FindFirstChild(n)for _,v in ipairs(self:GetChildren())do if v.Name==n then return v end end end
function methods:FindFirstChildOfClass(n)for _,v in ipairs(self:GetChildren())do if v:IsA(n)then return v end end end
function methods:Destroy()for _,v in ipairs(self:GetChildren())do v:Destroy()end;self.dead=true;self.Parent=nil end
function methods:ClearAllChildren()for _,v in ipairs(self:GetChildren())do v:Destroy()end end
function methods:Clear()self.clearCount=(self.clearCount or 0)+1 end
local function make(class,name,parent)
 local v=setmetatable({ClassName=class,Name=name or class},mt);table.insert(objects,v);v.Parent=parent
 return v
end
function methods:Clone()
 local v=make(self.ClassName,self.Name)
 for k,value in pairs(self)do if k~='_parent' and k~='dead' then v[k]=value end end
 for _,child in ipairs(self:GetChildren())do child:Clone().Parent=v end
 return v
end
Instance={new=function(class)return make(class)end}
CFrame.identity=CFrame.new(Vector3.zero)
local NumberSequenceKeypoint={new=function(t,v,e)return {Time=t,Value=v,Envelope=e or 0}end}
local NumberSequence={new=function(k)return {Keypoints=k}end}
local NumberRange={new=function(a,b)return {Min=a,Max=b or a}end}
local ColorSequence={new=function(c)return {Keypoints={{Value=c}}}end}
local authored=ColorSequence.new(Color3.fromRGB(130,54,204))
local templates=make('Folder','VfxTemplates',workspace)
local function beam(parent,width,name)
 local b=make('Beam',name or 'Filament',parent)
 b.Width0=width;b.Width1=width*.6;b.CurveSize0=0;b.CurveSize1=0;b.LightEmission=.2;b.TextureSpeed=2
 b.Color=authored
 return b
end
local function emitter(parent)
 local e=make('ParticleEmitter','Sparks',parent);e.LightEmission=.1;e.Rate=30;e.Enabled=true
 e.Color=authored
 e.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,1,0),NumberSequenceKeypoint.new(1,0,0)})
 e.Speed=NumberRange.new(1,3);return e
end
local starter=make('Folder','StarterBeam',templates)
local p=make('Part','Part',starter);beam(p,1.5);beam(p,.7)
local a=make('Attachment','Attachment',p);emitter(a)
local e=make('Part','Part1',starter);emitter(make('Attachment','Attachment',e))
local fire=make('Folder','FireBeam',templates)
local f=make('MeshPart','Beam',fire);beam(f,15);beam(f,8)
for i=1,4 do emitter(f) end
local hollow=make('Folder','HollowPurpleBeam',templates)
local h=make('Part','Hollow Purple',hollow)
-- A ribbon is first to exercise the engine's unspecified sibling order.
beam(h,13.6153802872);beam(h,2.2692313194,'CoreSpine');beam(h,3.4038450718)
beam(h,6.8076901436,'CoreFlow');beam(h,6.8076901436,'Beam1')
for i=1,4 do emitter(h)end
-- A side demo and unknown script must never become live Hollow Purple children.
beam(make('Part','Amplified',hollow),99);make('Script','Untrusted',h)
local game={GetService=function()return {FindFirstChild=function(_,n)if n=='VfxTemplates'then return templates end end}end}
local function typeof(x)if x==game then return 'Instance' elseif getmetatable(x)==V then return 'Vector3' else return type(x)end end
'''
CHECKS=r'''
local checks=0
local function check(v,m)assert(v,m);checks+=1 end
local function near(a,b)return math.abs(a-b)<.00001 end
local manager=B.new(Visuals.Create,Visuals.Update,Visuals.Destroy)
for _,width in ipairs({1,7})do
 local prior=0
 for _,level in ipairs({1,10,20,30,40,50,60,70,80,90,100})do
  -- Same actual manager update contract used for local and remote SustainedBeam.
  for _,id in ipairs({11,22})do
   manager:Update(id,0,Vector3.zero,Vector3.zAxis,40,width,color,level,false)
   local r=manager.entries[id].visual
   Visuals.Animate(r,r.born+.6,Vector3.zero,false,true,false)
   local v=r.vfx;check(v and v.styleId==StyleSource.StyleForLevel(level).id,'native family missing')
   local widest=0;for _,entry in ipairs(v.beams)do widest=math.max(widest,entry.inst.Width0,entry.inst.Width1)end
   check(near(widest,width*.6*StyleSource.WidthScale(level,false)),'native milestone width lost')
   if id==11 then check(widest>prior,'native decade did not grow');prior=widest end
   local spec=StyleSource.Detail(level,false,0)
   check(#r.parts==5+spec.rings*10+spec.strands*12+spec.sparks,'native part recipe mismatch')
   for i,part in ipairs(r.parts)do
    check(part.Shape~=Enum.PartType.Ball,'sphere returned')
    if i>5 then check(part.LocalTransparencyModifier==0,'native hides milestone decoration')end
   end
   for _,o in ipairs(v.root:GetDescendants())do check(not o:IsA('Script'),'script cloned')end
   if level>=80 then
    check(#v.beams==5 and #v.emitters==4,'wrong hollow demo selected')
    local cores={}
    for _,entry in ipairs(v.beams)do if entry.isCore then cores[entry.inst.Name]=true end end
    check(cores.CoreSpine and cores.CoreFlow and not cores.Filament and not cores.Beam1,
     'Hollow Purple chose core layers by sibling order')
   end
   local root=v.root
   local widths,sizes={},{}
   for i,entry in ipairs(v.beams)do widths[i]={entry.inst.Width0,entry.inst.Width1}end
   for i=1,5 do sizes[i]=r.parts[i].Size end
   Visuals.Animate(r,r.born+.6,Vector3.zero,false,true,false,true)
   check(#r.parts==5 and r.vfx.root==root,'Crowded mode lost the core rig or retained decoration')
   local crowdedScale=StyleSource.WidthScale(level,true)*.55/StyleSource.WidthScale(level,false)
   for i,entry in ipairs(v.beams)do
    check(entry.inst.Enabled==entry.isCore,'Crowded mode hid a core or kept a secondary template')
    check(near(entry.inst.Width0,widths[i][1]*crowdedScale) and near(entry.inst.Width1,widths[i][2]*crowdedScale),
     'Crowded native texture retained the broad firing width')
    check(entry.inst.TextureSpeed==entry.baseTextureSpeed,'Crowded mode changed core motion')
   end
   for i=1,5 do
    check(near(r.parts[i].Size.X,sizes[i].X) and near(r.parts[i].Size.Y,sizes[i].Y)
     and near(r.parts[i].Size.Z,sizes[i].Z),'Crowded mode changed pooled beam dimensions')
   end
   for _,entry in ipairs(v.emitters)do check(not entry.inst.Enabled,'Crowded mode kept particles')end
   check(r.parts[4].Transparency==.95,'Crowded mode retained the opaque endpoint lens')
   Visuals.Animate(r,r.born+.6,Vector3.zero,false,true,false)
   check(#r.parts>5 and r.parts[4].Transparency==.58,'Crowded mode did not restore after overlap')
   for i,entry in ipairs(v.beams)do
    check(near(entry.inst.Width0,widths[i][1]) and near(entry.inst.Width1,widths[i][2]),'Crowded texture width did not restore')
   end
   -- Each observer comfort source, far LOD, and restoration on the SAME rig.
   for _,mode in ipairs({{true,false,0},{false,true,0},{false,false,111}})do
    Visuals.Animate(r,r.born+.7,vec(0,0,mode[3]),mode[1],true,mode[2])
    check(#r.parts==4,'quiet native retained dynamic parts')
    if mode[3]==0 then
     check(root.Parent==nil and r.parts[2].LocalTransparencyModifier<1,'Quiet comfort retained template glare or hid the shaft')
    else
     check(root.Parent==workspace,'Distance LOD lost its template')
     for _,entry in ipairs(v.beams)do check(entry.inst.TextureSpeed==0 and entry.inst.Enabled==entry.isCore,'distance template motion')end
     for _,entry in ipairs(v.emitters)do check(not entry.inst.Enabled,'distance particles')end
     local widestFar=0;for _,entry in ipairs(v.beams)do if entry.inst.Enabled then widestFar=math.max(widestFar,entry.inst.Width0,entry.inst.Width1)end end
     check(near(widestFar,width*.6*StyleSource.WidthScale(level,true)),'distance milestone width lost')
    end
    local first=r.parts[1].Size.Y
    Visuals.Animate(r,r.born+1.4,vec(0,0,mode[3]),mode[1],true,mode[2])
    check(near(first,r.parts[1].Size.Y),'quiet silhouette pulses')
    Visuals.Animate(r,r.born+1.5,Vector3.zero,false,true,false)
    check(r.vfx.root==root and root.Parent==workspace and #r.parts>4,'restore rebuild/leak')
    for _,entry in ipairs(v.beams)do check(entry.inst.TextureSpeed==entry.baseTextureSpeed,'texture did not restore')end
   end
   for _,entry in ipairs(v.emitters)do
    check(not entry.inst.Enabled or entry.inst.Parent==v.midAnchor,'endpoint particle sphere returned')
   end
  end
 end
 manager:Clear()
end
local writes=0
local function countWrites(object,keys)
 local values,watched={},{}
 for _,key in ipairs(keys) do
  watched[key]=true;values[key]=object[key];rawset(object,key,nil)
 end
 local original=getmetatable(object)
 setmetatable(object,{
  __index=function(self,k)
   if watched[k] then return values[k] end
   return original.__index(self,k)
  end,
  __newindex=function(self,k,v)
   if watched[k] then writes+=1;values[k]=v else original.__newindex(self,k,v) end
  end,
 })
end
manager:Update(1,0,Vector3.zero,Vector3.zAxis,40,7,color,100,true)
local r=manager.entries[1].visual
Visuals.Animate(r,r.born+.59,Vector3.zero,false,false,false)
check(r.vfx==nil and #r.parts==4,'A quiet cast allocated an imported template at birth')
manager:Update(1,.6,Vector3.zero,Vector3.zAxis,40,7,color,100,false)
Visuals.Animate(r,r.born+.6,Vector3.zero,false,false,false)
local v=r.vfx
local initialClears=v.emitters[1].inst.clearCount or 0
for _,e in ipairs(v.beams) do countWrites(e.inst,{'Enabled','TextureSpeed'}) end
for _,e in ipairs(v.emitters) do countWrites(e.inst,{'Enabled','Rate'}) end
for _,mode in ipairs({{false,false},{false,true},{true,false},{false,false}}) do
 local reduced,crowded=table.unpack(mode)
 Visuals.Animate(r,r.born+.7,Vector3.zero,reduced,false,false,crowded)
 writes=0
 local clears=v.emitters[1].inst.clearCount
 Visuals.Animate(r,r.born+.8,Vector3.zero,reduced,false,false,crowded)
 check(writes==0,'Steady mode rewrote template properties')
 check(v.emitters[1].inst.clearCount==clears,'Steady mode cleared particles again')
end
check(v.emitters[1].inst.clearCount==initialClears+1 and v.emitters[1].inst.Enabled,'Particle transition failed to clear or restore')
local tint=Color3.fromRGB(32,235,88)
local base=Color3.fromRGB(255,203,99)
local light=tint:Lerp(Color3.fromRGB(245,252,255),.32)
local baseLight=base:Lerp(Color3.fromRGB(245,252,255),.32)
local function sameColor(a,b)return near(a.R,b.R) and near(a.G,b.G) and near(a.B,b.B) end
for _,level in ipairs({100,50,10}) do
 manager:Update(1,1,Vector3.zero,Vector3.zAxis,40,7,tint,level,false)
 Visuals.Animate(r,r.born+1,Vector3.zero,false,false,false)
 local tintedVfx=r.vfx
 for _,entry in ipairs(tintedVfx.beams)do
  check(sameColor(entry.inst.Color.Keypoints[1].Value,entry.isCore and tint or light),'Explicit tint did not reach the cloned beam')
  countWrites(entry.inst,{'Color'})
 end
 for _,entry in ipairs(tintedVfx.emitters)do
  check(sameColor(entry.inst.Color.Keypoints[1].Value,light),'Explicit tint did not reach the cloned particles')
  countWrites(entry.inst,{'Color'})
 end
 check(sameColor(r.parts[5].Color,tint),'Explicit tint did not reach pooled geometry')
 writes=0
 manager:Update(1,1.2,Vector3.zero,Vector3.zAxis,40,7,tint,level,false)
 Visuals.Animate(r,r.born+1.2,Vector3.zero,false,false,false)
 check(writes==0 and r.vfx==tintedVfx,'Steady tint rewrote or reallocated template')
 Visuals.Animate(r,r.born+1.3,Vector3.zero,true,false,false)
 check(tintedVfx.root.Parent==nil and sameColor(r.parts[2].Color,tint),'Reduced effects lost the selected color')
 manager:Update(1,1.4,Vector3.zero,Vector3.zAxis,40,7,base,level,false)
 Visuals.Animate(r,r.born+1.4,Vector3.zero,false,false,false)
 check(r.vfx==tintedVfx,'Restoring default rebuilt the template')
 for _,entry in ipairs(tintedVfx.beams)do
  check(sameColor(entry.inst.Color.Keypoints[1].Value,entry.isCore and base or baseLight),'Default yellow did not return across beam tiers')
 end
 for _,entry in ipairs(tintedVfx.emitters)do
  check(sameColor(entry.inst.Color.Keypoints[1].Value,baseLight),'Default yellow did not return to particles')
 end
end
manager:Update(1,1,Vector3.zero,Vector3.zAxis,40,7,color,50,false)
Visuals.Animate(r,r.born+1,Vector3.zero,false,false,false)
check(#r.vfx.emitters==4,'Rate cap case needs four FireBeam emitters')
for _,entry in ipairs(r.vfx.emitters) do
 check(entry.baseRate==18 and entry.inst.Rate==15,'Initial aggregate particle rate cap missing')
end
manager:Destroy();Visuals.Clear();check(Visuals.Budget()==0,'cleanup')
local spareRoots={}
for _,level in ipairs({10,50,100}) do
 local first=Visuals.Create()
 Visuals.Update(first,Vector3.zero,Vector3.zAxis,40,7,tint,level,false)
 Visuals.Animate(first,first.born+.6,Vector3.zero,false,true,false)
 local old=first.vfx
 local emitter=old.emitters[1].inst
 local cleared=emitter.clearCount or 0
 local second=Visuals.Create()
 Visuals.Update(second,Vector3.zero,Vector3.zAxis,40,7,tint,level,false)
 Visuals.Animate(second,second.born+.6,Vector3.zero,false,true,false)
 local overflow=second.vfx.root
 check(old.root~=overflow,'Two live casts shared an imported root')
 Visuals.Destroy(first)
 check(first.vfx==nil and old.root.Parent==nil and not old.root.dead,
  'Ended cast did not release a reusable detached root')
 check(emitter.clearCount==cleared+1,'Ending a cast retained old particles')
 Visuals.Destroy(second)
 check(overflow.dead,'Idle template cap retained a second spare of one style')
 local nextCast=Visuals.Create()
 Visuals.Update(nextCast,Vector3.zero,Vector3.zAxis,20,5,base,level,false)
 Visuals.Animate(nextCast,nextCast.born+.6,vec(0,0,125),false,true,false)
 check(nextCast.vfx==old and old.root.Parent==workspace,'New cast rebuilt its matching template')
 local widest=0
 for _,entry in ipairs(old.beams) do
  local b=entry.inst
  check(b.Enabled==entry.isCore and b.TextureSpeed==0,'Reused cast retained normal visibility or motion')
  check(sameColor(b.Color.Keypoints[1].Value,entry.isCore and base or baseLight),'Reused cast retained old tint')
  if b.Enabled then widest=math.max(widest,b.Width0,b.Width1) end
 end
 check(near(widest,5*.6*StyleSource.WidthScale(level,true)),'Reused cast retained old width')
 check(not emitter.Enabled,'Reused cast retained active particles at distance')
 Visuals.Destroy(nextCast)
 if level==100 then
  local sameWidth=Visuals.Create()
  Visuals.Update(sameWidth,Vector3.zero,Vector3.zAxis,30,5,base,level,false)
  Visuals.Animate(sameWidth,sameWidth.born+.6,vec(0,0,125),false,true,false)
  check(sameWidth.vfx==old and near(emitter.Speed.Max,old.emitters[1].baseSpeed.Max*30/44),
   'Reused cast retained old particle travel speed')
  Visuals.Destroy(sameWidth)
 end
 table.insert(spareRoots,old.root)
end
Visuals.Clear()
for _,root in ipairs(spareRoots) do check(root.dead,'Clear left an idle imported root') end
check(Visuals.Budget()==0,'Template reuse changed procedural cleanup')
print('PASS '..checks..' native-builder/manager milestone checks; Instance doubles, NOT native Studio')
'''
def run(source):
 old=support.CHECKS;support.CHECKS=''
 try:body=support.fixture(source)
 finally:support.CHECKS=old
 marker="local StyleSource=require('../src/ReplicatedStorage/Shared/BeamStyle')"
 body=body.replace(marker,ENV+marker)
 manager=(R/'src/StarterPlayer/StarterPlayerScripts/SustainedBeams.luau').read_text()
 body+='\nlocal B=(function()\n'+manager+'\nend)()\n'+CHECKS
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False)as f:f.write(body);path=Path(f.name)
 try:return subprocess.run(['luau',str(path)],capture_output=True,text=True)
 finally:path.unlink()
s=P.read_text();result=run(s);assert result.returncode==0,result.stdout+result.stderr;print(result.stdout.strip())
for old,new,message in [
 ('if vfx and not spareVfx[vfx.styleId] then','if vfx and false then','Ended cast did not release a reusable detached root'),
 ('if vfx and not spareVfx[vfx.styleId] then','if vfx then','Idle template cap retained a second spare'),
 ('  vfx.lastBucket=nil','  vfx.lastBucket=vfx.lastBucket','Reused cast retained old particle travel speed'),
 ('for _,entry in ipairs(vfx.emitters) do entry.inst:Clear() end','for _,entry in ipairs(vfx.emitters) do end','Ending a cast retained old particles'),
 ('for _,vfx in pairs(spareVfx) do vfx.root:Destroy() end','for _,vfx in pairs(spareVfx) do end','Clear left an idle imported root'),
 ('source.Name=="CoreSpine" or source.Name=="CoreFlow"','#vfx.beams<2','Hollow Purple chose core layers by sibling order'),
 ('if i==1 or (i==2 and hasVfx) then','if i==1 or partKind[p]=="detail" or (i==2 and hasVfx) then','native hides milestone decoration'),
 ('wScale=width*.6*scale/widest','wScale=width*.6/widest','native milestone width lost'),
 ('local quiet=reduced or rig.reduced or contactReduced','local quiet=reduced or rig.reduced','quiet native retained dynamic parts'),
 ('b.TextureSpeed=far and 0 or entry.baseTextureSpeed','b.TextureSpeed=entry.baseTextureSpeed','distance template motion'),
 ('if rig.vfx and rig.vfx.root.Parent then rig.vfx.root.Parent=nil end','if false then end','Quiet comfort retained template glare'),
 ('local hasVfx=not quiet and rig.vfx~=nil','local hasVfx=rig.vfx~=nil','Quiet comfort retained template glare'),
 ('local showSecondary=not far and not suppressSecondary','local showSecondary=not far','Crowded mode kept particles'),
 ('local crowded=not far and suppressSecondary','local crowded=false','Crowded native texture retained the broad firing width'),
 ('local endAlpha=suppressSecondary and .95 or rig.contactPosition and .86 or .58','local endAlpha=.58','Crowded mode retained the opaque endpoint lens'),
 ('local visibilityChanged=vfx.showSecondary~=showSecondary','local visibilityChanged=true','Steady mode rewrote template properties'),
 ('math.min(entry.baseRate,60/#vfx.emitters)','entry.baseRate','Initial aggregate particle rate cap missing'),
 ('entry.inst.Color=entry.isCore and core or accent','entry.inst.Color=entry.inst.Color','Explicit tint did not reach the cloned beam'),
 ('entry.inst.Color=accent','entry.inst.Color=entry.inst.Color','Explicit tint did not reach the cloned particles'),
 ('p.Color=color;p.LocalTransparencyModifier=.2','p.Color=styleColor(styleSpec.primary,color);p.LocalTransparencyModifier=.2','Explicit tint did not reach pooled geometry'),
 ('if vfx.tint==tint then return end','if false then return end','Steady tint rewrote or reallocated template'),
 ('vfx.tint=tint','if vfx.tint and tint.R==1 then return end;vfx.tint=tint','Default yellow did not return across beam tiers'),
]:
 assert old in s
 result=run(s.replace(old,new));assert result.returncode and message in result.stderr,result.stdout+result.stderr
print('PASS 22 native-path negative controls (reuse, core selection, progression, scale, crowding, rate, tint and redundant writes)')
