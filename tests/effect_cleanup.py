"""Actual pooled particle cleanup and Effects.Render behavior with fake tweens/instances/vectors; no native rendering claim."""
from pathlib import Path
import argparse
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
src_path = root / 'src/StarterPlayer/StarterPlayerScripts/ScreamEffects.luau'

setup = r'''
local created={};local queue={};local tweens={}
local V={};local function vec(x,y,z)return setmetatable({X=x,Y=y,Z=z},V)end
V.__add=function(a,b)return vec(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
V.__sub=function(a,b)return vec(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
V.__mul=function(a,b)if type(a)=='number'then a,b=b,a end return vec(a.X*b,a.Y*b,a.Z*b)end
V.__div=function(a,b)return a*(1/b)end
V.__unm=function(a)return vec(-a.X,-a.Y,-a.Z)end
V.__index=function(a,k)
 if k=='Magnitude'then return math.sqrt(a.X*a.X+a.Y*a.Y+a.Z*a.Z)
 elseif k=='Unit'then return a/a.Magnitude end
end
local function cross(a,b)return vec(a.Y*b.Z-a.Z*b.Y,a.Z*b.X-a.X*b.Z,a.X*b.Y-a.Y*b.X)end
local Vector3={new=vec,zero=vec(0,0,0),yAxis=vec(0,1,0),zAxis=vec(0,0,1)}
local C={};C.__mul=function(a,b)return a end
local CFrame={
 lookAt=function(at,target,upHint)
  local look=(target-at).Unit
  local right=cross(look,upHint or Vector3.yAxis).Unit
  local up=cross(right,look).Unit
  return setmetatable({Position=at,Target=target,UpHint=upHint,RightVector=right,UpVector=up,LookVector=look},C)
 end,
 Angles=function(rx,ry,rz)return setmetatable({rx=rx,ry=ry,rz=rz},C)end
}
local Color3={fromRGB=function(r,g,b)return {R=r/255,G=g/255,B=b/255}end}
local Instance={new=function()local p={Destroy=function(self)self.destroyed=true;self.Parent=nil end};table.insert(created,p);return p end}
local Tween={Create=function(_,part,info,goal)local t={part=part,info=info,goal=goal,Play=function(self)self.played=true end,Cancel=function(self)self.canceled=true end};table.insert(tweens,t);return t end}
local game={GetService=function()return Tween end};local workspace={}
local task={delay=function(_,fn)table.insert(queue,fn)end}
local Enum={PartType={Block='block'},Material={Neon='neon'},EasingStyle={Quad='quad'},EasingDirection={Out='out'}}
local TweenInfo={new=function(lifetime)return {lifetime=lifetime}end}
'''

checks = r'''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local function near(a,b)return math.abs(a-b)<1e-5 end
local function isNaN(x)return x~=x end
local function isNaNVec(v)return isNaN(v.X) or isNaN(v.Y) or isNaN(v.Z)end

-- Preserve all 9 existing pool cleanup assertions
particle('core',{}, {}, {},nil,.2);particle('detail',{}, {}, {},nil,.2)
check(Effects.Budget().core==1 and Effects.Budget().detail==1,'Fixture did not allocate particles')
queue[1]();check(Effects.Budget().cachedCore==1 and Effects.Budget().core==0,'Normal expiry did not pool particle')
Effects.Clear()
check(created[1].destroyed and created[2].destroyed and tweens[2].canceled,'Cleanup retained cached/live particles or tween')
local b=Effects.Budget();check(b.core==0 and b.detail==0 and b.cachedCore==0 and b.cachedDetail==0,'Cleanup retained budget/pool')
queue[2]();Effects.Clear()
b=Effects.Budget();check(b.detail==0 and b.cachedDetail==0,'Late expiry revived destroyed pool or underflowed budget')
particle('detail',{}, {}, {},nil,.2)
check(#created==3 and Effects.Budget().detail==1,'Reusable cleanup prevented later rendering')
queue[2]();check(Effects.Budget().detail==1,'Old expiry changed new effect budget')
queue[3]();check(Effects.Budget().detail==0 and Effects.Budget().cachedDetail==1,'New effect failed normal expiry')
Effects.Clear();check(created[3].destroyed,'Second lifecycle retained cached part')

-- Non-mutation of caller goal tables
local callerGoal={Position=Vector3.new(1,2,3)}
particle('detail',{},Vector3.new(1,1,1),Color3.fromRGB(255,255,255),nil,.2,callerGoal)
check(callerGoal.Transparency==nil and callerGoal.Position.X==1,'Caller goal table was mutated')
check(tweens[#tweens].goal~=callerGoal and tweens[#tweens].goal.Transparency==1 and tweens[#tweens].goal.Position==callerGoal.Position,'Tween goal did not preserve caller fields and Transparency=1')
Effects.Clear()

-- Direct line segment thickness taper (45%)
local linePartIdx=#created+1;local lineTweenIdx=#tweens+1
line('detail',Vector3.new(0,0,0),Vector3.new(0,0,10),.4,Color3.fromRGB(100,200,255),.3)
check(#created==linePartIdx,'Line did not emit particle')
check(near(created[linePartIdx].Size.X,.4) and near(created[linePartIdx].Size.Y,.4) and near(created[linePartIdx].Size.Z,10),'Line initial size mismatch')
check(tweens[lineTweenIdx].goal.Transparency==1 and tweens[lineTweenIdx].goal.Size~=nil,'Line segment did not taper')
check(near(tweens[lineTweenIdx].goal.Size.X,.4*.45) and near(tweens[lineTweenIdx].goal.Size.Y,.4*.45) and near(tweens[lineTweenIdx].goal.Size.Z,10),'Line segment taper ratio mismatch')
Effects.Clear()

-- Effects.Render across all 6 families, reduced=true/false, horizontal & vertical aim
local expectedDetails={Pulse=8,Echo=24,Feathers=8,Quake=10,Storm=14,Nova=16}
local families={'Pulse','Echo','Feathers','Quake','Storm','Nova'}
local tint=Color3.fromRGB(80,170,255)
local aims={{'horizontal',Vector3.zAxis},{'vertical',Vector3.yAxis}}

for _,aim in ipairs(aims) do
 local aimName,aimDir=aim[1],aim[2]
 for _,family in ipairs(families) do
  -- reduced=true
  local beforeParts,beforeTweens=#created,#tweens
  Effects.Render(family,Vector3.zero,aimDir,40,4,tint,true,3)
  local rb=Effects.Budget()
  check(rb.core==2 and rb.detail==0,'Reduced mode emitted detail particles or wrong core count')
  local rSheath,rSheathTween=created[beforeParts+1],tweens[beforeTweens+1]
  local rSpine,rSpineTween=created[beforeParts+2],tweens[beforeTweens+2]
  if aimName=='vertical' then
   check(rSheath.CFrame.UpHint==Vector3.zAxis and not isNaNVec(rSheath.CFrame.RightVector) and not isNaNVec(rSheath.CFrame.UpVector),'Vertical aim produced invalid basis')
   check(near(rSheath.CFrame.RightVector.Magnitude,1) and near(rSheath.CFrame.UpVector.Magnitude,1),'Vertical aim basis vectors not unit')
  end
  check(rSheathTween.goal.Size~=nil and near(rSheathTween.goal.Size.X,4*.56) and near(rSheathTween.goal.Size.Y,4*.56) and near(rSheathTween.goal.Size.Z,40),'Outer core sheath did not expand')
  check(rSpineTween.goal.Size~=nil and near(rSpineTween.goal.Size.X,.08) and near(rSpineTween.goal.Size.Y,.08) and near(rSpineTween.goal.Size.Z,40),'Inner core spine did not taper')
  Effects.Clear()

  -- reduced=false
  beforeParts,beforeTweens=#created,#tweens
  Effects.Render(family,Vector3.zero,aimDir,40,4,tint,false,3)
  local fb=Effects.Budget()
  check(fb.core==2 and fb.detail==expectedDetails[family],'Unexpected particle count for '..family..' ('..aimName..')')
  local sheath,sheathTween=created[beforeParts+1],tweens[beforeTweens+1]
  local spine,spineTween=created[beforeParts+2],tweens[beforeTweens+2]
  check(near(sheath.Size.X,4*.42) and near(sheath.Size.Y,4*.42) and near(sheath.Size.Z,40) and sheath.Color==tint and sheath.Transparency==.55,'Outer core sheath initial properties mismatch')
  check(sheathTween.goal.Transparency==1 and sheathTween.goal.Size~=nil and near(sheathTween.goal.Size.X,4*.56) and near(sheathTween.goal.Size.Y,4*.56) and near(sheathTween.goal.Size.Z,40),'Outer core sheath did not expand')
  check(near(spine.Size.X,.18) and near(spine.Size.Y,.18) and near(spine.Size.Z,40) and near(spine.Color.R,1) and near(spine.Color.G,240/255) and near(spine.Color.B,203/255) and spine.Transparency==.55,'Inner core spine initial properties mismatch')
  check(spineTween.goal.Transparency==1 and spineTween.goal.Size~=nil and near(spineTween.goal.Size.X,.08) and near(spineTween.goal.Size.Y,.08) and near(spineTween.goal.Size.Z,40),'Inner core spine did not taper')
  if aimName=='vertical' then
   check(sheath.CFrame.UpHint==Vector3.zAxis and not isNaNVec(sheath.CFrame.RightVector) and not isNaNVec(sheath.CFrame.UpVector),'Vertical aim produced invalid basis')
  end
  for i=3,2+expectedDetails[family] do
   local p,tw=created[beforeParts+i],tweens[beforeTweens+i]
   check(not isNaNVec(p.Size) and p.Size.X>0 and p.Size.Y>0 and p.Size.Z>0,'Detail particle has invalid size')
   check(tw.goal.Transparency==1,'Detail tween missing Transparency=1')
   if family=='Feathers' then
    check(tw.goal.Position~=nil and tw.goal.Orientation~=nil,'Feather particle missing motion goal')
   else
    check(tw.goal.Size~=nil,'Line segment did not taper')
    check(near(tw.goal.Size.X,p.Size.X*.45) and near(tw.goal.Size.Y,p.Size.Y*.45) and near(tw.goal.Size.Z,p.Size.Z),'Line segment taper ratio mismatch')
   end
  end
  Effects.Clear()
 end
end

-- Pool budget limits preserved
for i=1,35 do
 Effects.Render('Echo',Vector3.zero,Vector3.zAxis,40,4,tint,false,3)
end
local cap=Effects.Budget()
check(cap.core==64 and cap.detail==144 and cap.coreLimit==64 and cap.detailLimit==144,'Pool budget limits changed')
Effects.Clear()
local cleared=Effects.Budget()
check(cleared.core==0 and cleared.detail==0 and cleared.cachedCore==0 and cleared.cachedDetail==0,'Final Effects.Clear did not reset budgets')

print('PASS '..checks..' actual effect pool cleanup and render checks with mocked tweens')
'''


def run(source, expected=None):
 body = source.rsplit('return Effects', 1)[0]
 with tempfile.NamedTemporaryFile(mode='w', suffix='.luau', dir=root / 'tests', encoding='utf-8', delete=False) as f:
  path = Path(f.name)
  f.write(setup + body + checks)
 try:
  res = subprocess.run(['luau', str(path)], cwd=root, capture_output=True, text=True)
 finally:
  path.unlink()
 out = res.stdout + res.stderr
 if expected:
  assert res.returncode != 0 and expected in out, f'Expected failure {expected!r}, got rc={res.returncode}: {out}'
  print('PASS expected failure: ' + expected)
 else:
  assert res.returncode == 0, out
  print(res.stdout.strip())


def main():
 parser = argparse.ArgumentParser()
 parser.add_argument('--negative-controls', action='store_true')
 args = parser.parse_args()

 source = src_path.read_text(encoding='utf-8')
 run(source)

 if args.negative_controls:
  controls = [
   (
    'local target={Transparency=1};if goal then for k,v in pairs(goal) do target[k]=v end end',
    'local target=goal or {};target.Transparency=1',
    'Caller goal table was mutated',
   ),
   (
    'particle(kind,facing((a+b)/2,b),Vector3.new(thickness,thickness,distance),color,nil,lifetime,{Size=Vector3.new(thickness*.45,thickness*.45,distance)})',
    'particle(kind,facing((a+b)/2,b),Vector3.new(thickness,thickness,distance),color,nil,lifetime)',
    'Line segment did not taper',
   ),
   (
    'Vector3.new(width*.56,width*.56,length)',
    'Vector3.new(width*.42,width*.42,length)',
    'Outer core sheath did not expand',
   ),
   (
    'Vector3.new(.08,.08,length)',
    'Vector3.new(.18,.18,length)',
    'Inner core spine did not taper',
   ),
   (
    'if reduced then return end',
    'if false then return end',
    'Reduced mode emitted detail particles',
   ),
   (
    'math.abs(direction.Y)>.98 and Vector3.zAxis or Vector3.yAxis',
    'Vector3.yAxis',
    'Vertical aim produced invalid basis',
   ),
   (
    'live[p]=nil;p.Parent=nil;active[kind]-=1;table.insert(pools[kind],p)',
    'live[p]=nil;p.Parent=nil;active[kind]-=1',
    'Normal expiry did not pool particle',
   ),
  ]
  for old, new, expected in controls:
   assert source.count(old) == 1, f'Missing control target: {old!r}'
   run(source.replace(old, new), expected)
  print(f'PASS {len(controls)} targeted negative controls')


if __name__ == '__main__':
 main()
