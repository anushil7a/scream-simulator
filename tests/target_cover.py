"""Actual client/server ray setup with mock vectors/raycast; no engine geometry evidence."""
from pathlib import Path
import subprocess
import sys
import tempfile
root=Path(__file__).resolve().parents[1]
c=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text();c=c[c.index('local function previewAttackOrigin('):c.index('local function playerTargetInfo(')]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=s[s.index('local function audible('):s.index('local function canCapture(')]
o=s[s.index('local function attackOrigin('):s.index('local function beamObstruction(')]
setup='''
local mt={};local function v(x,y,z)return setmetatable({X=x,Y=y,Z=z},mt)end
mt.__add=function(a,b)return v(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
mt.__sub=function(a,b)return v(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
mt.__index=function(a,key)
 if key=='Magnitude' then return math.sqrt(a.X*a.X+a.Y*a.Y+a.Z*a.Z) end
 if key=='Unit' then local m=a.Magnitude;return v(a.X/m,a.Y/m,a.Z/m) end
 if key=='Dot' then return function(x,y)return x.X*y.X+x.Y*y.Y+x.Z*y.Z end end
end
local Vector3={new=v};local RaycastParams={new=function()return {}end};local Enum={RaycastFilterType={Exclude='exclude'}}
local head;local character={FindFirstChild=function()return head end};local p={Character=character}
local root={Position=v(0,0,0)};local target={Position=v(10,2,0)};local model={}
local blocked=false;local calls={}
local workspace={Raycast=function(_,origin,direction,params)table.insert(calls,{origin=origin,direction=direction,params=params});return blocked and {} or nil end}
local function equal(a,b)return a.X==b.X and a.Y==b.Y and a.Z==b.Z end
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
for _,case in ipairs({{distance=2,part=true},{distance=4.99,part=true},{distance=5,part=true},{distance=20,part=true},{distance=2,part=false},{missing=true}})do
 head=not case.missing and {Position=v(0,case.distance,0),IsA=function()return case.part end} or nil
 for _,obstructed in ipairs({false,true})do
  blocked=obstructed;calls={}
  local covered=targetCovered(previewAttackOrigin(root),target,model)
  local clear=audible(character,attackOrigin(character,root),target.Position,model)
  check(covered==obstructed and clear==not obstructed,'Cover interpretation disagreed')
  check(equal(calls[1].origin,calls[2].origin) and equal(calls[1].direction,calls[2].direction),'Client/server origin or endpoint diverged')
  local expected=head and case.part and case.distance<5 and head.Position or v(0,1,0)
  check(equal(calls[1].origin,expected),'Invalid head origin accepted')
  for _,call in calls do
   check(call.params.RespectCanCollide==true and call.params.FilterType=='exclude' and call.params.FilterDescendantsInstances[1]==character and call.params.FilterDescendantsInstances[2]==model,'Ray filters diverged')
  end
 end
end
head=nil
local aim=v(28,1,0)
local stats={range=21,maxRange=30}
for _,pvp in ipairs({false,true})do
 local far,current=beamTargetRange(root,{Position=v(31,1,0)},aim,stats,pvp)
 check(far and current,'HUD advertised reach past the true endpoint')
 far,current=beamTargetRange(root,{Position=v(30,1,0)},aim,stats,pvp)
 check(not far and current,'Exact full-power endpoint was rejected')
 far,current=beamTargetRange(root,{Position=v(21.05,1,0)},aim,stats,pvp)
 check(not far and current,'Current beam endpoint inherited the root allowance')
 far,current=beamTargetRange(root,{Position=v(21,1,0)},aim,stats,pvp)
 check(not far and not current,'Exact current endpoint was rejected')
end
local wideTarget={Position=v(20.99,1,13)}
local far,current=beamTargetRange(root,wideTarget,aim,stats,false)
check(not far and not current,'Resident used radial distance in place of beam travel')
far,current=beamTargetRange(root,wideTarget,aim,stats,true)
check(not far and current,'PvP lost its separate root-distance guard')
far=beamTargetRange(root,{Position=v(-5,1,0)},aim,stats,false)
check(far,'Target behind the beam was marked reachable')
far=beamTargetRange(root,target,previewAttackOrigin(root),stats,false)
check(far,'Degenerate aim was marked reachable')
head={Position=v(2,3,0),IsA=function()return true end}
local _,_,origin=beamTargetRange(root,target,target.Position,stats,true)
check(equal(origin,head.Position),'Beam travel did not share cover origin')
print('PASS '..checks..' client/server cover and endpoint checks with mocked vectors and rays')
'''
def run(client, expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
  path=Path(f.name);f.write(setup+client+a+o+checks)
 try: result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True)
 finally: path.unlink()
 if expected:
  assert result.returncode and expected in result.stderr,result.stderr
  print('PASS control:',expected)
 else:
  assert result.returncode==0,result.stderr
  print(result.stdout.strip())

run(c)
if '--negative-controls' in sys.argv:
 for old,new,expected in [
  ('projection>stats.maxRange','projection>stats.maxRange+2','HUD advertised reach past the true endpoint'),
  ('projection>stats.range','projection>stats.range+2','Current beam endpoint inherited the root allowance'),
  ('pvp and (targetRoot.Position-root.Position).Magnitude or 0','0','PvP lost its separate root-distance guard'),
 ]:
  assert c.count(old)==1,old
  run(c.replace(old,new),expected)
