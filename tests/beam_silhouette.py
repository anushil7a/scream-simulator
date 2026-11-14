"""Actual BeamVisuals/BeamStyle with vector/Part doubles; no native rendering/GPU claim."""
from pathlib import Path
import ast,argparse,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau'
def fixture(source):
 tree=ast.parse((ROOT/'tests/beam_pool_composition.py').read_text())
 pre=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PRE' for t in n.targets))
 pre=pre.replace('local function cf()return setmetatable({RightVector=vec(1,0,0),UpVector=vec(0,1,0)},C)end','local function cf(position,target)return setmetatable({Position=position,Target=target,RightVector=vec(1,0,0),UpVector=vec(0,1,0)},C)end')
 pre=pre.replace('local color={};function color:Lerp()return self end\nlocal Color3={fromRGB=function()return color end}', '''local Colors={};Colors.__index=Colors
local function rgb(r,g,b)return setmetatable({R=r/255,G=g/255,B=b/255},Colors)end
function Colors:Lerp(b,t)return rgb((self.R+(b.R-self.R)*t)*255,(self.G+(b.G-self.G)*t)*255,(self.B+(b.B-self.B)*t)*255)end
local Color3={fromRGB=rgb};local color=rgb(255,203,99)''')
 pre=pre.replace('Material={Neon=1}', 'Material={Neon=1,SmoothPlastic=2}')
 source=source.replace('require(game:GetService("ReplicatedStorage").Shared.BeamStyle)','StyleSource')
 return pre+"\nlocal StyleSource=require('../src/ReplicatedStorage/Shared/BeamStyle')\nlocal Visuals=(function()\n"+source+'\nend)()\n'+CHECKS
CHECKS='''
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local function near(a,b)return math.abs(a-b)<.00001 end
local function same(a,b)return near(a.R,b.R) and near(a.G,b.G) and near(a.B,b.B)end
local white=Color3.fromRGB(245,252,255)
for _,level in ipairs({1,40,100})do
 for _,tint in ipairs({color,Color3.fromRGB(90,70,220),Color3.fromRGB(22,150,100)})do
  local r=Visuals.Create();Visuals.Update(r,Vector3.zero,Vector3.zAxis,40,7,tint,level,false)
  local age=.6;local radius=7*(.24+StyleSource.Tier(level)*.012);local pulse=1+.035*math.sin(age*9)
  Visuals.Animate(r,r.born+age,Vector3.zero,false)
  local spec=StyleSource.Detail(level,false,0)
  check(r.parts[1].Material==Enum.Material.SmoothPlastic and r.parts[2].Material==Enum.Material.SmoothPlastic and r.parts[4].Material==Enum.Material.SmoothPlastic and r.parts[5].Material==Enum.Material.SmoothPlastic,'Wide regular body still emissive')
  check(r.parts[3].Material==Enum.Material.Neon and r.parts[6].Material==Enum.Material.Neon,'Fine energy detail not emissive')
  if level>=80 then
   for i=6,5+spec.rings*10 do
    check(r.parts[i].Material==(i<=15 and Enum.Material.Neon or Enum.Material.SmoothPlastic),'High-tier collar hierarchy changed')
   end
  end
  check(#r.parts==5+spec.rings*10+spec.strands*12+spec.sparks,'Part budget/detail count changed')
  check(near(r.parts[1].Size.Y,radius*1.35*pulse) and r.parts[1].Transparency==(level>=80 and .78 or .55),'Regular body not slim/quiet')
  check(same(r.parts[2].Color,tint) and near(r.parts[2].Size.Y,radius*.85),'Semantic body tint/diameter changed')
  check(r.parts[2].Transparency==(level>=80 and .7 or .18),'Body transparency tier boundary changed')
  check(near(r.parts[3].Size.Y,radius*.1) and same(r.parts[3].Color,tint:Lerp(white,.72)),'Hot spine lost hierarchy/tint')
  check(r.parts[4].Shape==Enum.PartType.Cylinder and near(r.parts[4].Size.X,radius*.22) and near(r.parts[4].Size.Y,radius*1.25),'Termination lens missing')
  check(near(r.parts[4].CFrame.Position.Z,40-radius*.11) and near(r.parts[4].CFrame.Target.Z,40),'Lens exceeds endpoint')
  check(near(r.parts[5].Size.X,radius*.72) and same(r.parts[5].Color,tint),'Emitter obscures origin')
  local travel=(age*(.6+spec.tier*.025)+1/spec.rings)%1;local rr=radius*(.85+.2*math.sin(travel*math.pi))*(spec.tier>=1 and 1.25 or 1)
  local angleA=age*.9+.6;local angleB=.72*math.pi/5+angleA
  local function collarRadius(angle)
   if spec.collar=='diamond' then return rr/(math.abs(math.cos(angle))+math.abs(math.sin(angle)))
   elseif spec.collar=='star' then return rr*(.72+.28*(.5+.5*math.cos(angle*5))) end
   return rr
  end
  local ra,rb=collarRadius(angleA),collarRadius(angleB)
  local axial=spec.collar=='diamond' and .75*(math.cos(angleB)*rb-math.cos(angleA)*ra) or 0
  check(near(r.parts[6].Size.X,math.sqrt(ra*ra+rb*rb-2*ra*rb*math.cos(angleB-angleA)+axial*axial)),'Collar has no open channel')
  if spec.sparks>0 then
   for i=#r.parts-spec.sparks+1,#r.parts do
    check(r.parts[i].CFrame.Target.Z<40 and r.parts[i].CFrame.Target.Z>=0,'Flare not directed back within beam')
    check(math.sqrt(r.parts[i].CFrame.Target.X^2+r.parts[i].CFrame.Target.Y^2)<=7*.42+.0001,'Flare exceeds width')
   end
  end
  for _,v in ipairs(r.parts)do check(not v.CanQuery and not v.CanCollide and not v.CanTouch and not v.CastShadow,'Cosmetic physics changed')end
  Visuals.Animate(r,r.born+age,Vector3.zero,true)
  for _,v in ipairs(r.parts)do check(v.Material==Enum.Material.Neon,'Reused quiet/far material not reset')end
  check(#r.parts==4 and near(r.parts[1].Size.Y,radius*1.65) and r.parts[1].Transparency==.72,'Reduced body changed')
  check(near(r.parts[3].Size.Y,radius*.28) and same(r.parts[3].Color,white) and r.parts[3].Transparency==.45,'Reduced spine changed')
  check(r.parts[4].Shape==Enum.PartType.Ball and near(r.parts[4].Size.X,radius*1.5),'Reduced endpoint changed')
  Visuals.Animate(r,r.born+age,vec(0,0,111),false)
  for _,v in ipairs(r.parts)do check(v.Material==Enum.Material.Neon,'Reused quiet/far material not reset')end
  check(#r.parts==4 and near(r.parts[1].Size.Y,radius*1.65*pulse) and r.parts[1].Transparency==.68,'Far body changed')
  check(r.parts[4].Shape==Enum.PartType.Ball and same(r.parts[3].Color,white),'Far silhouette changed')
  Visuals.Animate(r,r.born+age,vec(0,0,181),false);check(#r.parts==0,'Cull retained parts')
  Visuals.Destroy(r)
 end
end
for _,length in ipairs({.01,.1,2})do
 local short=Visuals.Create();Visuals.Update(short,Vector3.zero,Vector3.zAxis,length,7,color,100,false);Visuals.Animate(short,short.born+.6,Vector3.zero,false)
 local lens=short.parts[4]
 check(lens.Size.X<=length and near(lens.CFrame.Target.Z,length) and lens.CFrame.Position.Z>=0,'Short beam lens escapes range')
 Visuals.Destroy(short)
end
local reused=Visuals.Create();Visuals.Update(reused,Vector3.zero,Vector3.zAxis,40,7,color,100,true);Visuals.Animate(reused,reused.born+.6,Vector3.zero,true)
for _,v in ipairs(reused.parts)do check(v.Material==Enum.Material.Neon,'Cross-rig pooled material not reset')end
Visuals.Destroy(reused)
Visuals.Clear();local allocated,cached=Visuals.Budget();check(allocated==0 and cached==0,'Terminal cleanup failed')
print('PASS '..checks..' actual beam silhouette/tint/lifecycle checks; orientation mocked')
'''
def run(source):
 with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',suffix='.luau',prefix='tmp_beam_style_',dir=ROOT/'tests',delete=False)as f:p=Path(f.name);f.write(fixture(source))
 try:return subprocess.run(['luau',str(p)],cwd=ROOT,capture_output=True,text=True)
 finally:p.unlink()
def main():
 p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');a=p.parse_args();s=PATH.read_text();r=run(s);assert r.returncode==0,r.stdout+r.stderr;print(r.stdout.strip())
 if a.negative_controls:
  cases=[('detailed and 1.35 or 1.65','detailed and 1.65 or 1.65','Regular body not slim'),('color:Lerp(white,.72)','white','Hot spine lost'),('finish-dir*depth,finish','finish,finish+dir*depth','Lens exceeds endpoint'),('(i-.28)*math.pi/5','i*math.pi/5','Collar has no open channel')]
  cases=cases+[('detailed and .10 or .28','detailed and .10 or .20','Reduced spine changed')]
  for old,new,diagnostic in cases:
   assert s.count(old)==1,old;r=run(s.replace(old,new));assert r.returncode and diagnostic in r.stderr,r.stdout+r.stderr
  for old,new,diagnostic in [('part.Material=material or Enum.Material.Neon','part.Material=Enum.Material.Neon','Wide regular body still emissive'),('part.Material=material or Enum.Material.Neon','if material then part.Material=material end','Reused quiet/far material not reset')]:
   assert s.count(old)==1;r=run(s.replace(old,new));assert r.returncode and diagnostic in r.stderr,r.stdout+r.stderr
  print('PASS 7 targeted negative controls')
if __name__=='__main__':main()
