"""Actual manager/visual/style composition; mock Parts and vector arithmetic only.
CFrame orientation/rendering/physics, native scheduling, FPS and GPU costs are NOT tested.
No Roblox APIs or apps. Temporary Luau fixture removed even when a control fails.
"""
from pathlib import Path
import argparse, hashlib, subprocess, tempfile
R=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--negative-controls',action='store_true');args=a.parse_args()
paths={k:R/'src'/v for k,v in {
 'visual':'StarterPlayer/StarterPlayerScripts/BeamVisuals.luau',
 'manager':'StarterPlayer/StarterPlayerScripts/SustainedBeams.luau',
 'style':'ReplicatedStorage/Shared/BeamStyle.luau'}.items()}
source={k:p.read_text(encoding='utf-8-sig') for k,p in paths.items()}
PRE=r'''local V={};local function vec(x,y,z)return setmetatable({X=x,Y=y,Z=z},V)end
V.__add=function(a,b)return vec(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
V.__sub=function(a,b)return vec(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
V.__mul=function(a,b)if type(a)=='number'then a,b=b,a end return vec(a.X*b,a.Y*b,a.Z*b)end
V.__div=function(a,b)return a*(1/b)end
V.__index=function(a,k)if k=='Magnitude'then return math.sqrt(a.X*a.X+a.Y*a.Y+a.Z*a.Z)elseif k=='Unit'then return a/a.Magnitude end end
local Vector3={new=vec,one=vec(1,1,1),zero=vec(0,0,0),yAxis=vec(0,1,0),zAxis=vec(0,0,1)}
-- Orientation is deliberately a stub; this is allocation/lifecycle, not geometry fidelity.
local C={};C.__mul=function(a,b)return a end
local function cf()return setmetatable({RightVector=vec(1,0,0),UpVector=vec(0,1,0)},C)end
local CFrame={new=cf,lookAt=cf,Angles=cf}
local color={};function color:Lerp()return self end
local Color3={fromRGB=function()return color end}
local Enum={Material={Neon=1},SurfaceType={Smooth=1},PartType={Cylinder=1,Ball=2}}
local workspace={};local made=0;local dead=0;local all={}
local Instance={new=function()made+=1;local p={};function p:Destroy()assert(not self.dead,'double destruction');self.dead=true;self.Parent=nil;dead+=1 end;table.insert(all,p);return p end}
'''
CHECKS=r'''
local b=B.new(Visuals.Create,Visuals.Update,Visuals.Destroy)
local now=0;local checks=0
local function check(x,m)assert(x,m);checks+=1 end
local function update(id)return b:Update(id,now,Vector3.zero,Vector3.yAxis,40,7,color,100,false)end
local function audit(reduced,viewer)
 local seen={};local n=0
 for _,entry in pairs(b.entries)do
  local r=entry.visual;Visuals.Animate(r,r.born+.6,viewer,reduced)
  check(#r.parts>=(viewer.Magnitude>180 and 0 or reduced and 4 or viewer.Magnitude>110 and 4 or 5),'core starved')
  if reduced or viewer.Magnitude>110 and viewer.Magnitude<=180 then check(#r.parts==4,'decoration retained')end
  if viewer.Magnitude>180 then check(#r.parts==0,'cull retained')end
  for _,p in ipairs(r.parts)do
   check(not seen[p] and not p.dead and p.Parent==workspace,'duplicate or stale part');seen[p]=true;n+=1
   check(p.Anchored and not p.CanCollide and not p.CanTouch and not p.CanQuery and not p.CastShadow,'cosmetic physics changed')
   check(p.Color==color and p.Transparency>=0 and p.Transparency<=1 and p.Size.X>0,'reuse properties not initialized')
  end
 end
 if not reduced and viewer.Magnitude<=110 and b.count==24 then check(n==512,'released detail budget not reusable')end
 local allocated,pooled=Visuals.Budget();check(allocated<=512 and allocated==made-dead,'cap/accounting');check(n+pooled==allocated,'pool leak or orphan')
end
for i=1,24 do check(update(i),'admit24')end
check(not update(25),'manager overflow');audit(false,Vector3.zero)
local peak=Visuals.Budget();check(peak==512,'unexpected peak')
-- Direct extra rig exercises the visual module hard cap independently of manager admission.
-- This is defensive API coverage, not a claim that production admits a 25th attacker.
local extra=Visuals.Create();Visuals.Update(extra,Vector3.zero,Vector3.yAxis,40,7,color,100,false)
Visuals.Animate(extra,extra.born+.6,Vector3.zero,false)
check(Visuals.Budget()<=512 and #extra.parts==0,'hard cap exceeded');Visuals.Destroy(extra)
for cycle=1,50 do
 now+=.2;for id in pairs(b.entries)do update(id)end
 audit(true,Vector3.zero);audit(false,vec(0,0,111));audit(false,vec(0,0,181));audit(false,Vector3.zero)
 check(Visuals.Budget()==peak,'allocation grew after peak')
end
now+=.3;for id=1,12 do update(id)end
now+=.2;b:Expire(now);check(b.count==12,'expiry boundary');for id=25,36 do check(update(id),'replacement')end
audit(false,Vector3.zero);b:Clear();local x,y=Visuals.Budget();check(x==y,'clear leaked')
check(update(99),'reusable clear');audit(false,Vector3.zero);b:Destroy()
local before=made;check(not update(100) and made==before,'terminal manager recreated');b:Destroy()
Visuals.Clear();check(Visuals.Budget()==0 and dead==made,'final destruction');Visuals.Clear()
print('PASS',checks,'composed assertions; peak',peak,'created',made,'destroyed',dead)
'''
def run(s,expected=None):
 v=s['visual'];old='require(game:GetService("ReplicatedStorage").Shared.BeamStyle)';assert v.count(old)==1
 v=v.replace(old,'StyleSource')
 text=PRE+'\nlocal StyleSource=(function()\n'+s['style']+'\nend)()\nlocal Visuals=(function()\n'+v+'\nend)()\nlocal B=(function()\n'+s['manager']+'\nend)()\n'+CHECKS
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.beam_pool_',dir=R/'tests',encoding='utf8',delete=False)as f:f.write(text);p=Path(f.name)
 try:r=subprocess.run(['luau',str(p)],capture_output=True,text=True,timeout=30)
 finally:p.unlink()
 out=r.stdout+r.stderr
 if expected:assert r.returncode!=0 and expected in out,out;print('PASS control:',expected)
 else:assert r.returncode==0,out;print(out.strip())
run(source)
if args.negative_controls:
 for file,old,new,expected in [
  ('visual','if allocated>=Style.MaxParts then return end','if false then return end','hard cap exceeded'),
  ('visual','if detail and detailCount>=Style.MaxParts-24*5 then return end','if false then return end','core starved'),
  ('visual','part.Parent=nil;table.insert(pool,part)','part.Parent=nil','pool leak or orphan'),
  ('visual','decoration[part]=nil;detailCount-=1','decoration[part]=nil','released detail budget not reusable'),
  ('manager','if now>=entry.expires then','if now>entry.expires then','expiry boundary'),
  ('manager','if self.destroyed then return false end','if false then return false end','terminal manager recreated'),
  ('visual','for _,part in ipairs(pool) do part:Destroy() end','for _,part in ipairs(pool) do end','final destruction'),
 ]:
  assert source[file].count(old)==1,old
  s=dict(source);s[file]=s[file].replace(old,new);run(s,expected)
for k,p in paths.items():print('SHA256',k,hashlib.sha256(p.read_bytes()).hexdigest())
