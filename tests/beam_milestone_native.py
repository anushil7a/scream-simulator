"""Execute actual template builders + sync/visibility with bounded Instance-tree doubles.
Not a native rendering, asset-permission, voice transport or GPU test.
"""
from pathlib import Path
import subprocess,tempfile
import beam_silhouette as support
R=Path(__file__).resolve().parents[1]
P=R/'src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau'
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
local templates=make('Folder','VfxTemplates',workspace)
local function beam(parent,width,core)
 local b=make('Beam','Filament',parent)
 b.Width0=width;b.Width1=width*.6;b.CurveSize0=0;b.CurveSize1=0;b.LightEmission=.2;b.TextureSpeed=2
 return b
end
local function emitter(parent)
 local e=make('ParticleEmitter','Sparks',parent);e.LightEmission=.1;e.Rate=30;e.Enabled=true
 e.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,1,0),NumberSequenceKeypoint.new(1,0,0)})
 e.Speed=NumberRange.new(1,3);return e
end
local starter=make('Folder','StarterBeam',templates)
local p=make('Part','Part',starter);beam(p,1.5);beam(p,.7)
local a=make('Attachment','Attachment',p);emitter(a)
local e=make('Part','Part1',starter);emitter(make('Attachment','Attachment',e))
local fire=make('Folder','FireBeam',templates)
local f=make('MeshPart','Beam',fire);beam(f,15);beam(f,8);emitter(f)
local hollow=make('Folder','HollowPurpleBeam',templates)
local h=make('Part','Hollow Purple',hollow)
-- Actual selected XML width sequence (two tapered cores, three outer ribbons).
for _,w in ipairs({2.2692313194,6.8076901436,6.8076901436,3.4038450718,13.6153802872})do beam(h,w)end
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
   if level>=80 then check(#v.beams==5 and #v.emitters==4,'wrong hollow demo selected')end
   local root=v.root
   local widths,sizes={},{}
   for i,entry in ipairs(v.beams)do widths[i]={entry.inst.Width0,entry.inst.Width1}end
   for i=1,5 do sizes[i]=r.parts[i].Size end
   Visuals.Animate(r,r.born+.6,Vector3.zero,false,true,false,true)
   check(#r.parts==5 and r.vfx.root==root,'Crowded mode lost the core rig or retained decoration')
   for i,entry in ipairs(v.beams)do
    check(entry.inst.Enabled==entry.isCore,'Crowded mode hid a core or kept a secondary template')
    check(near(entry.inst.Width0,widths[i][1]) and near(entry.inst.Width1,widths[i][2])
     and entry.inst.TextureSpeed==entry.baseTextureSpeed,'Crowded mode changed core width or motion')
   end
   for i=1,5 do
    check(near(r.parts[i].Size.X,sizes[i].X) and near(r.parts[i].Size.Y,sizes[i].Y)
     and near(r.parts[i].Size.Z,sizes[i].Z),'Crowded mode changed pooled beam dimensions')
   end
   for _,entry in ipairs(v.emitters)do check(not entry.inst.Enabled,'Crowded mode kept particles')end
   check(r.parts[4].Transparency==.95,'Crowded mode retained the opaque endpoint lens')
   Visuals.Animate(r,r.born+.6,Vector3.zero,false,true,false)
   check(#r.parts>5 and r.parts[4].Transparency==.18,'Crowded mode did not restore after overlap')
   -- Each observer comfort source, far LOD, and restoration on the SAME rig.
   for _,mode in ipairs({{true,false,0},{false,true,0},{false,false,111}})do
    Visuals.Animate(r,r.born+.7,vec(0,0,mode[3]),mode[1],true,mode[2])
    check(#r.parts==4,'quiet native retained dynamic parts')
    for _,entry in ipairs(v.beams)do check(entry.inst.TextureSpeed==0 and entry.inst.Enabled==entry.isCore,'quiet template motion')end
    for _,entry in ipairs(v.emitters)do check(not entry.inst.Enabled,'quiet particles')end
    local widestQuiet=0;for _,entry in ipairs(v.beams)do if entry.inst.Enabled then widestQuiet=math.max(widestQuiet,entry.inst.Width0,entry.inst.Width1)end end
    check(near(widestQuiet,width*.6*StyleSource.WidthScale(level,true)),'quiet milestone width lost')
    local first=r.parts[1].Size.Y
    Visuals.Animate(r,r.born+1.4,vec(0,0,mode[3]),mode[1],true,mode[2])
    check(near(first,r.parts[1].Size.Y),'quiet silhouette pulses')
    Visuals.Animate(r,r.born+1.5,Vector3.zero,false,true,false)
    check(r.vfx.root==root and #r.parts>4,'restore rebuild/leak')
    for _,entry in ipairs(v.beams)do check(entry.inst.TextureSpeed==entry.baseTextureSpeed,'texture did not restore')end
   end
   for _,entry in ipairs(v.emitters)do
    check(not entry.inst.Enabled or entry.inst.Parent==v.midAnchor,'endpoint particle sphere returned')
   end
  end
 end
 manager:Clear()
end
manager:Destroy();Visuals.Clear();check(Visuals.Budget()==0,'cleanup')
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
 ('if i==1 or (i==2 and hasVfx) then','if i==1 or partKind[p]=="detail" or (i==2 and hasVfx) then','native hides milestone decoration'),
 ('wScale=width*.6*scale/widest','wScale=width*.6/widest','native milestone width lost'),
 ('local quiet=reduced or rig.reduced or contactReduced','local quiet=reduced or rig.reduced','quiet native retained dynamic parts'),
 ('b.TextureSpeed=far and 0 or entry.baseTextureSpeed','b.TextureSpeed=entry.baseTextureSpeed','quiet template motion'),
 ('local showSecondary=not far and not suppressSecondary','local showSecondary=not far','Crowded mode kept particles'),
 ('local endAlpha=suppressSecondary and .95 or rig.contactPosition and .86 or .18','local endAlpha=.18','Crowded mode retained the opaque endpoint lens'),
]:
 assert old in s
 result=run(s.replace(old,new));assert result.returncode and message in result.stderr,result.stdout+result.stderr
print('PASS 6 native-path negative controls (progression, scale, motion and crowded secondary effects)')
