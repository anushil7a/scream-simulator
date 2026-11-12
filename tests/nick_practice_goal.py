"""Actual cosmetic branch and compact constructor; mock vectors/Instances, not native animation/scoring."""
from pathlib import Path
import ast,importlib.util,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location('cw',R/'tests/compact_world.py');cw=importlib.util.module_from_spec(sp);sp.loader.exec_module(cw)
resident=(R/'src/StarterPlayer/StarterPlayerScripts/Residents.client.luau').read_text()
layout=cw.layout;city=cw.city
BASE='0c68c05'
GOALS=r'''
local result=City.Build({});local goalNames={NickPracticeGoalLeft=true,NickPracticeGoalRight=true,NickPracticeGoalCrossbar=true};local goalCount=0
local byName={};for _,n in ipairs(nodes)do if n.Name then byName[n.Name]=n end end
check(Layout.Soccer.practiceGoal.X==265 and Layout.Soccer.practiceGoal.Y==1.05 and Layout.Soccer.practiceGoal.Z==287,'Compact endpoint changed')
for name in pairs(goalNames)do
 local n=byName[name];check(n~=nil,'Decorative practice goal missing');goalCount+=1
 check(n.ClassName=='Part' and n.Anchored==true and n.CanCollide==false and n.CanQuery==false and n.CanTouch==false and n.CastShadow==false,'Goal changes physics/query')
 check(next(n.attributes)==nil,'Goal has gameplay tags')
 for _,child in ipairs(nodes)do check(child.Parent~=n,'Goal has prompt/light child')end
 check(n.Position.Z==286,'Goal plane not one stud before endpoint')
end
check(goalCount==3,'Goal inventory wrong')
local l,r,c=byName.NickPracticeGoalLeft,byName.NickPracticeGoalRight,byName.NickPracticeGoalCrossbar
check(l.Position.X==257 and r.Position.X==273 and l.Position.Y==3.5 and r.Position.Y==3.5,'Goal post placement wrong')
check(l.Size.X==.35 and l.Size.Y==7 and l.Size.Z==.35 and r.Size.X==.35 and r.Size.Y==7 and r.Size.Z==.35,'Goal post dimensions wrong')
check(c.Position.X==265 and c.Position.Y==7 and c.Size.X==16 and c.Size.Y==.35 and c.Size.Z==.35,'Goal crossbar wrong')
local found=false;for _,job in ipairs(result.jobs)do if job.role=='Soccer' then
 local station=job.stations[1];check(station.position.X==239 and station.position.Y==3 and station.position.Z==281,'Nick station moved')
 check(station.lookAt.X==265 and station.lookAt.Z==286 and job.quests[1]=='nick','Nick aim/quest changed');found=true
end end;check(found,'Nick missing')
'''
MATH=r'''
V.__add=function(a,b)return Vector3.new(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
V.__mul=function(a,b)if type(a)=='number'then a,b=b,a end;return Vector3.new(a.X*b,a.Y*b,a.Z*b)end
local oldIndex=V.__index;V.__index=function(v,k)if k=='Unit'then local m=v.Magnitude;return Vector3.new(v.X/m,v.Y/m,v.Z/m)end;return oldIndex(v,k)end
function V:Lerp(b,t)return self+(b-self)*t end
local CF={};CF.__mul=function(a,b)return a end
CFrame.new=function(v)return setmetatable({Position=v},CF)end;CFrame.Angles=function()return {}end
'''
CHECKS=r'''
for _,compact in ipairs({true,false})do
 local animate,rig,root=make(compact)
 local dest=compact and Vector3.new(265,1.05,287) or Vector3.new(628,2.05,586)
 local start=root.Position-Vector3.new(0,1.9,0)+root.CFrame.LookVector*1.65
 for _,age in ipairs({0,1.2,2,3.7,6.49})do
  animate(true,10,'OwnGoal',age)
  local t=math.clamp((age-1.2)/2.5,0,1);local expected=start:Lerp(dest,1-(1-t)^2)
  check((rig.practiceBall.last.Position-expected).Magnitude<1e-8,'OwnGoal endpoint/timeline incorrect')
  if compact then
   local point=rig.practiceBall.last.Position
   check(point.X-.75>=Layout.Soccer.min.X and point.X+.75<=Layout.Soccer.max.X and point.Z-.75>=Layout.Soccer.min.Z and point.Z+.75<=Layout.Soccer.max.Z,'Compact ball leaves court')
  end
 end
 if compact then
  local cross=start:Lerp(dest,(286-start.Z)/(dest.Z-start.Z))
  check(cross.X-.75>257+.175 and cross.X+.75<273-.175 and cross.Y+.75<7-.175 and cross.Y-.75>0,'Ball path intersects goal frame or ground')
  check(dest.X-239==26 and dest.Z-281==6,'Original station-relative endpoint changed')
  local hit=rig.practiceBall.last.Position;check(hit.X>257+.175+.75 and hit.X<273-.175-.75 and hit.Y+.75<7-.175 and hit.Z>286,'Ball does not finish through open goal')
 end
 for _,condition in ipairs({'inactive','far'})do
  animate(true,10,'OwnGoal',2);local count=rig.practiceBall.calls
  animate(condition~='inactive',condition=='far' and 180 or 10,'OwnGoal',3.7)
  check(rig.ballVisible==false and rig.practiceBall.piece.Transparency==1 and rig.practiceBall.calls==count,'Interrupted/distant visual not hidden')
 end
 animate(true,10,'OwnGoal',3.7);check(rig.ballVisible and rig.practiceBall.piece.Transparency==0,'Current visual did not recover')
 animate(true,10,'Miss',3);check((rig.practiceBall.last.Position-start).Magnitude<1e-8,'Miss routine changed')
 animate(true,10,'Trip',1.3);check((rig.practiceBall.last.Position-start).Magnitude<1e-8,'Trip timing changed')
 animate(true,10,'Trip',2.8);check((rig.practiceBall.last.Position-(start+root.CFrame.LookVector*2.2)).Magnitude<1e-8,'Trip movement changed')
end
print('PASS '..checks..' actual Nick goal construction/animation assertions; mock Instances/vectors only')
'''
def build(resident,layout,city,baseline=False):
 a=resident.index('  if rig.practiceBall then',resident.index('local workAge='));b=resident.index('  for i,name in ipairs(jointNames)',a);branch=resident[a:b]
 goal=next((l for l in resident.splitlines()if l.startswith('local practiceGoal=')),'local practiceGoal=nil')
 return cw.setup+layout+cw.between+city+'\nend)()\n'+('' if baseline else GOALS)+MATH+'''\nlocal function make(compact)
local Config={CompactCity=compact,CityLayout=Layout}
'''+goal+'''
local origin=compact and Vector3.new(239,3,281) or Vector3.new(602,4,580)
local toward=Vector3.new(26,0,5).Unit
local root={Position=origin,CFrame={LookVector=toward}}
local ball={calls=0,piece={Transparency=1}};function ball:GetChildren()return {self.piece}end;function ball:PivotTo(cf)self.last=cf;self.calls+=1 end
local rig={practiceBall=ball,ballVisible=false}
local function animate(working,distance,routine,workAge)
'''+branch+'\nend\nreturn animate,rig,root\nend\n'+CHECKS

def run(r=resident,l=layout,c=city,baseline=False):
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(build(r,l,c,baseline));p=Path(f.name)
 try:return subprocess.run(['luau',str(p)],capture_output=True,text=True,timeout=20)
 finally:p.unlink()
def startup(source):
 # Reuse only the literal event mock; execute the entire actual Residents script in a paused coroutine.
 tree=ast.parse((R/'tests/animation_lifecycle.py').read_text())
 setup=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='setup' for t in n.targets))
 for stage in (1,2,3,0):
  before=r'''
local stage=__STAGE__;local calls=0
local function dependency(value)calls+=1;if calls==stage then coroutine.yield('dependency')end;return value end
local module={};local sharedMock={WaitForChild=function(_,name)assert(name=='Config');return dependency(module)end}
services.ReplicatedStorage.WaitForChild=function(_,name)assert(name=='Shared');return dependency(sharedMock)end
require=function(m)assert(m==module);return dependency({CompactCity=true,CityLayout={Soccer={practiceGoal=Vector3.new(265,1.05,287)}}})end
local co=coroutine.create(function()
'''.replace('__STAGE__',str(stage))
  after=r'''
end)
local ok,err=coroutine.resume(co);assert(ok,err)
if stage~=0 then
 check(coroutine.status(co)=='suspended' and calls==stage,'Startup did not pause at requested dependency')
 script.Destroying:Fire()
 ok,err=coroutine.resume(co);assert(ok,err)
 check(coroutine.status(co)=='dead','Destroyed startup did not terminate')
 check(calls==stage,'Stopped startup continued dependency work')
 check(collection.added:Count()==0 and collection.removed:Count()==0 and run.PreSimulation:Count()==0,'Stopped startup installed subscriptions')
else
 check(coroutine.status(co)=='dead' and calls==3,'Normal startup failed')
 check(collection.added:Count()==1 and collection.removed:Count()==1 and run.PreSimulation:Count()==1,'Normal subscriptions missing')
 script.Destroying:Fire()
 check(collection.added:Count()==0 and collection.removed:Count()==0 and run.PreSimulation:Count()==0,'Normal teardown leaked subscriptions')
end
check(script.Destroying:Count()==1,'Duplicate or missing teardown hook')
print('PASS '..checks..' actual paused startup assertions')
'''
  with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(setup+before+source+after);path=Path(f.name)
  try:r=subprocess.run(['luau',str(path)],capture_output=True,text=True,timeout=20)
  finally:path.unlink()
  if r.returncode:return r
 return r

def builder_contract():
 # Extract actual resolver only; importing the builder would emit unrelated harnesses.
 tree=ast.parse((R/'tests/build_studio_harness.py').read_text())
 function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='inline')
 regex=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REQUIRE' for t in n.targets))
 import re
 ns={'re':re,'client':R/'src/StarterPlayer/StarterPlayerScripts','MODULES':{'Config':R/'src/ReplicatedStorage/Shared/Config.luau'}}
 exec(compile(ast.Module(body=[regex,function],type_ignores=[]),'actual_harness_resolver','exec'),ns)
 class Input:
  def __init__(self,text,name='Residents.client.luau'):self.text=text;self.name=name
  def read_text(self):return self.text
  def resolve(self):return (ns['client']/self.name).resolve()
 result=ns['inline'](Input(resident))
 assert 'local Config=modules.Config' in result and 'require(' not in result
 assert 'WaitForChild("Shared")' not in result and 'WaitForChild("Config")' not in result
 assert result.index('script.Destroying:Connect')<result.index('local Config=modules.Config')
 invalid=[resident.replace('WaitForChild("Shared")','WaitForChild("Wrong")'),resident.replace('WaitForChild("Config")','WaitForChild("Other")'),resident.replace('require(configModule)','require(otherModule)'),resident.replace('local configModule=shared:','local configModule=elsewhere:'),resident.replace('local Config=require(configModule)','configModule=other;local Config=require(configModule)')]
 for source in invalid:
  try:ns['inline'](Input(source))
  except RuntimeError:pass
  else:raise AssertionError('Unknown alias binding accepted')
 try:ns['inline'](Input(resident,'Other.client.luau'))
 except RuntimeError:pass
 else:raise AssertionError('Alias exception escaped Residents')
 ns['MODULES']={}
 try:ns['inline'](Input(resident))
 except RuntimeError:pass
 else:raise AssertionError('Missing bundled Config accepted')
 print('PASS 10 actual harness resolver contract assertions (including seven rejected bindings)')

if __name__=='__main__':
 if '--baseline' in sys.argv:
  old=subprocess.check_output(['git','show',BASE+':src/StarterPlayer/StarterPlayerScripts/Residents.client.luau'],cwd=R,text=True)
  r=run(r=old,baseline=True);assert r.returncode and 'OwnGoal endpoint/timeline incorrect' in r.stderr,r.stdout+r.stderr;print('PASS historical actual branch: compact OwnGoal uses old-world endpoint')
 else:
  r=run();assert r.returncode==0,r.stdout+r.stderr;print(r.stdout,end='')
  builder_contract()
  r=startup(resident);assert r.returncode==0,r.stdout+r.stderr;print('PASS 19 actual paused startup/normal lifecycle assertions')
  if '--negative-controls' in sys.argv:
   muts=[('r','position:Lerp(practiceGoal,','position:Lerp(Vector3.new(628,2.05,586),','OwnGoal endpoint/timeline incorrect'),('r','(workAge-1.2)/2.5','(workAge-1.2)/1.5','OwnGoal endpoint/timeline incorrect'),('r','local visible=working and distance<180','local visible=distance<180','Interrupted/distant visual not hidden'),('r','local visible=working and distance<180','local visible=working','Interrupted/distant visual not hidden'),('c','goal.CanQuery=false','goal.CanQuery=true','Goal changes physics/query'),('c','goal.CanTouch=false','goal.CanTouch=true','Goal changes physics/query'),('c','goal.CastShadow=false','goal.CastShadow=false;goal.CanCollide=true','Goal changes physics/query'),('c','station(239,281,practiceGoal.X,practiceGoal.Z-1','station(239,281,252,251','Nick aim/quest changed')]
   for which,old,new,error in muts:
    source={'r':resident,'l':layout,'c':city}[which];assert source.count(old)==1,old
    r=run(**{which:source.replace(old,new)});assert r.returncode and error in r.stderr,r.stdout+r.stderr
    print('PASS negative control:',error)

  if '--negative-controls' in sys.argv and '--baseline' not in sys.argv:
   for old in ['local shared=game:GetService("ReplicatedStorage"):WaitForChild("Shared")\nif destroyed then return end', 'local configModule=shared:WaitForChild("Config")\nif destroyed then return end', 'local Config=require(configModule)\nif destroyed then return end']:
    assert resident.count(old)==1
    r=startup(resident.replace(old,old.replace('\nif destroyed then return end','')))
    assert r.returncode and ('Stopped startup continued dependency work' in r.stderr or 'Stopped startup installed subscriptions' in r.stderr),r.stdout+r.stderr
    print('PASS startup negative control: dependency lifetime fence')
   hook=resident[resident.index('script.Destroying:Connect(function()'):resident.index('-- Install teardown before')]
   delayed=resident.replace(hook,'')+'\n'+hook
   r=startup(delayed);assert r.returncode and 'Stopped startup continued dependency work' in r.stderr,r.stdout+r.stderr
   print('PASS startup negative control: late teardown registration')
