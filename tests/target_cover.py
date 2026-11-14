"""Actual client/server ray setup with mock vectors/raycast; no engine geometry evidence."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
c=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text();c=c[c.index('local function targetCovered('):c.index('local function playerTargetInfo(')]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=s[s.index('local function audible('):s.index('local function canCapture(')]
o=s[s.index('local function attackOrigin('):s.index('local function beamObstruction(')]
setup='''
local mt={};local function v(x,y,z)return setmetatable({X=x,Y=y,Z=z},mt)end
mt.__add=function(a,b)return v(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
mt.__sub=function(a,b)return v(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
mt.__index=function(a,key)if key=='Magnitude' then return math.sqrt(a.X*a.X+a.Y*a.Y+a.Z*a.Z) end end
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
  local covered=targetCovered(root,target,model)
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
print('PASS '..checks..' client/server cover setup checks with mocked raycast; no geometry verification')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(setup+c+a+o+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
