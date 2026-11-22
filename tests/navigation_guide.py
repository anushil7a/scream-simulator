"""NavigationGuide production-module lifecycle tests with deterministic Roblox doubles.
Not native pathfinding, collision, streaming or visual evidence.
"""
from pathlib import Path
import argparse,subprocess,tempfile
R=Path(__file__).resolve().parents[1]
source=(R/'src/StarterPlayer/StarterPlayerScripts/NavigationGuide.luau').read_text()
setup=r'''
local V={};V.__index=function(t,k)if k=='Magnitude' then return math.sqrt(t.X*t.X+t.Y*t.Y+t.Z*t.Z) elseif k=='Unit' then return t/t.Magnitude else return V[k] end end
V.__add=function(a,b)return Vector3.new(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
V.__sub=function(a,b)return Vector3.new(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
V.__mul=function(a,b)return Vector3.new(a.X*b,a.Y*b,a.Z*b)end
V.__div=function(a,b)return Vector3.new(a.X/b,a.Y/b,a.Z/b)end
function V:Dot(b)return self.X*b.X+self.Y*b.Y+self.Z*b.Z end
Vector3={new=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},V)end}
local nativeType=typeof;typeof=function(v)return getmetatable(v)==V and 'Vector3' or nativeType(v)end
local function signal() local s={};function s:Connect(fn)self.fn=fn;return {Disconnect=function()s.fn=nil end}end;return s end
local objects={};Instance={new=function(class)local o={ClassName=class,Destroying=signal()};function o:Destroy()self.destroyed=true;if self.Destroying.fn then self.Destroying.fn() end end;table.insert(objects,o);return o end}
Color3={fromRGB=function(...)return {...}end};Enum={RaycastFilterType={Exclude=1},Material={SmoothPlastic=1},PathStatus={Success=1}}
RaycastParams={new=function()return {}end}
local tasks={};task={spawn=function(fn)table.insert(tasks,fn)end}
local paths={};local corner=nil;local fail=false;local wall=false;local ground=true;local lowWall=false;local laterWall;local rayCount=0
local world={};function world:Raycast(origin,direction,params)
 rayCount+=1
 -- Newly streamed vertical barrier at X=2, from floor to 1.5 studs high.
 if lowWall and origin.Y<1.5 and direction.X>0 and origin.X<2 and origin.X+direction.X>=2 then return {} end
 if laterWall and origin.Y<1.5 and direction.X>0 and origin.X<laterWall and origin.X+direction.X>=laterWall then return {} end
 if direction.Y==-9 then if ground then return {Position=Vector3.new(origin.X,0,origin.Z),Normal=Vector3.new(0,1,0)} end
 elseif wall then return {} end
 return nil
end
local service={};function service:CreatePath(options)
 assert(options.AgentCanJump==false)
 local p={Blocked=signal()};function p:ComputeAsync(a,b)self.start=a;self.goal=b;self.Status=fail and 0 or 1 end
 function p:GetWaypoints()return corner or {{Position=self.start-Vector3.new(0,2.5,0)},{Position=self.goal}}end
 function p:Destroy()self.destroyed=true end
 table.insert(paths,p);return p
end
game={GetService=function(_,name)return name=='Workspace' and world or service end}
local Guide=(function()
'''
checks=r'''
end)()
local count=0;local function check(v,s)assert(v,s);count+=1 end
local function flush()local q=tasks;tasks={};for _,fn in ipairs(q)do fn()end end
local root={Position=Vector3.new(0,2.5,0),Parent={}}
local owner={Destroying=signal()};local g=Guide.new(owner)
check(#g.dots==18,'bounded marker allocation');check(#objects==19,'no HUD controls')
g:Step(root,0,true);check(#tasks==0,'no automatic target')
g:SetTarget({position=Vector3.new(100,0,0),label='Boss'});g:Step(root,0,true)
check(#tasks==1,'first computation');g:Step(root,1,true);check(#tasks==1,'single in-flight');flush()
g:Step(root,1.2,true);check(g.dots[1].Transparency<1,'route shown');check(g.status=='Follow the markers','route status')
local lowestEdge=g.dots[1].Position.Y-g.dots[1].Size.Y/2
check(lowestEdge>.3375 and g.dots[1].Position.Y<.6,'Guide dot intersects low paving or floats above the route')
g:Step(root,1.4,false);check(g.dots[1].Transparency==1,'modal hide')
wall=true;g:Step(root,1.6,true);check(g.points==nil and g.dots[1].Transparency==1,'new wall fails closed');wall=false
g:Step(root,2,true);check(#tasks==0,'retry throttle');g:Step(root,3,true);check(#tasks==1,'retry after throttle')
g:SetTarget({position=Vector3.new(0,0,100)});flush();check(g.points==nil,'old goal result ignored')
g:Step(root,3.2,true);fail=true;flush();check(g.status=='Route unavailable' and g.points==nil,'failure never produces straight trail')
check(g.distance>100,'distance preserved');local _,_,bearing=g:GetStatus();check(bearing=='S','honest fallback bearing');fail=false
g:Step(root,7,true);g:Clear();flush();check(g.target==nil and g.points==nil,'clear during asynchronous work')
g:SetTarget({position=Vector3.new(100,0,0)});g:Step(root,8,true);local root2={Position=Vector3.new(5,2.5,0),Parent={}}
g:Step(root2,8.2,true);flush();check(g.points==nil,'respawn discards old result');g:Step(root2,8.4,true);flush()
check(g.points~=nil,'respawn re-routes');g:Step(root2,8.6,true);local p=g.path
p.Blocked.fn(2);check(g.points==nil and p.destroyed,'blocked cleanup')
g:Step(root2,12,true);flush();ground=false;g:Step(root2,12.2,true)
check(g.dots[1].Transparency==1 and g.status=='Route unavailable','unstreamed ground omitted');ground=true
root2.Position=Vector3.new(100,2.5,0);g:Step(root2,12.4,true);check(g.status=='Arrived' and g.target~=nil,'arrival preserves choice')
check(#objects==19,'no per-frame instances')
g:SetTarget({position=Vector3.new(0/0,0,0)});check(g.target==nil,'reject NaN')
g:SetTarget({position=Vector3.new(math.huge,0,0)});check(g.target==nil,'reject infinity')
g:SetTarget({position=Vector3.new(20,0,0)});g:Step(root2,20,true);owner.Destroying.fn();flush()
check(g.destroyed and g.folder.destroyed and g.points==nil,'owner and pending task cleanup');g:Destroy();g:Step(root2,21,true)
check(owner.Destroying.fn==nil,'owner connection disconnected')
local stable=Guide.new(nil);local r={Position=Vector3.new(0,2.5,0),Parent={}}
stable:SetTarget({position=Vector3.new(100,0,0)});stable:Step(r,0,true);flush()
stable:Step(r,4,true);check(#tasks==0,'healthy route not recalculated each throttle period')
stable:Step(r,9,true);check(#tasks==1,'old routes revalidated');flush()
r.Position=Vector3.new(0,2.5,40);stable:Step(r,12,true);check(#tasks==1 and stable.points==nil,'off-route invalidation');flush()
stable:Destroy()
local moving=Guide.new(nil)
moving:SetTarget({position=Vector3.new(28,0,0)});moving:Step(root,0,true)
moving:SetTarget({position=Vector3.new(32,0,0)},true);flush()
check(moving.points and moving.path.goal.X==28,'Small moving target update cleared a compatible route')
moving:Step(root,.2,true);check(#tasks==0,'Moving destination bypassed the path retry limit')
check(moving.visibleDots>0,'Compatible moving route has no drawn breadcrumbs')
moving:Step(root,3,true);check(#tasks==1,'Moving destination did not retry')
check(moving.points and moving.path.goal.X==28,'Guide dropped before a replacement was ready')
flush();check(moving.path.goal.X==32,'Retry aimed at stale destination')
moving:SetTarget({position=Vector3.new(36,0,0)},true)
moving:Step(root,6,true);fail=true;flush();fail=false
check(moving.path and moving.path.goal.X==32,'Failed replacement destroyed a compatible route')
moving:SetTarget({position=Vector3.new(44,0,0)},true)
check(not moving.points,'A large move kept a stale route')
corner={{Position=Vector3.new(0,0,0)},{Position=Vector3.new(50,0,0)}}
moving:Step(root,9,true)
moving:SetTarget({position=Vector3.new(56,0,0)},true);flush()
check(not moving.points,'A large move admitted an old in-flight route')
corner=nil
moving:Step(root,12,true);flush()
check(moving.path.goal.X==56,'Guide did not recover after large target movement')
moving:SetTarget({position=Vector3.new(60,0,0),label='Mar work area'},true)
check(not moving.points,'Different destination identity kept old markers')
moving:Destroy()
local offset=Guide.new(nil)
corner={{Position=Vector3.new(0,0,0)},{Position=Vector3.new(21,0,0)}}
offset:SetTarget({position=Vector3.new(28,0,0)});offset:Step(root,0,true)
offset:SetTarget({position=Vector3.new(35,0,0)},true);flush()
check(not offset.points,'A replacement endpoint too far from live Mar was accepted')
offset:SetTarget({position=Vector3.new(28,0,0)},true);offset:Step(root,3,true);flush()
check(offset.path and offset.path.goal.X==28,'A valid offset endpoint was rejected')
offset:SetTarget({position=Vector3.new(35,0,0)},true)
check(not offset.points,'A retained endpoint too far from live Mar was left visible')
offset:Destroy()
local bend=Guide.new(nil);local bendRoot={Position=Vector3.new(0,2.5,0),Parent={}}
corner={{Position=Vector3.new(0,0,0)},{Position=Vector3.new(5,0,0)},{Position=Vector3.new(5,0,-15)}}
bend:SetTarget({position=Vector3.new(5,0,-15)});bend:Step(bendRoot,0,true);flush()
bend:Step(bendRoot,.2,true);check(bend.cursor==2,'nearby corner skipped');check(bend.dots[1].Position.X==5 and bend.dots[1].Position.Z==0,'route cut corner')
bendRoot.Position=Vector3.new(4,2.5,0);bend:Step(bendRoot,.4,true);check(bend.cursor==3,'corner fails to progress when reached');bend:Destroy()
corner=nil
local slow=Guide.new(nil);local slowRoot={Position=Vector3.new(0,2.5,0),Parent={}}
slow:SetTarget({position=Vector3.new(100,0,0)});slow:Step(slowRoot,0,true)
slow:Step(slowRoot,9,true);flush();slow:Step(slowRoot,9.2,true)
check(slow.points~=nil and #tasks==0,'slow successful computation immediately expired')
slow:Step(slowRoot,17.2,true);check(#tasks==1,'completed slow route never expires');flush();slow:Destroy()
local obstacle=Guide.new(nil)
obstacle:SetTarget({position=Vector3.new(100,0,0)});obstacle:Step(slowRoot,0,true);flush()
lowWall=true;obstacle:Step(slowRoot,.2,true)
check(obstacle.points==nil and obstacle.visibleDots==0,'trail crosses a newly streamed low wall')
lowWall=false;obstacle:Destroy()
local prefix=Guide.new(nil)
prefix:SetTarget({position=Vector3.new(100,0,0)});prefix:Step(slowRoot,0,true);flush()
laterWall=12;prefix:Step(slowRoot,.2,true)
check(prefix.points and prefix.visibleDots==2 and prefix.dots[3].Transparency==1,'A later obstacle hid the checked-clear path or showed a dot past it')
slowRoot.Position=Vector3.new(10,2.5,0);prefix:Step(slowRoot,.4,true)
check(not prefix.points and prefix.visibleDots==0,'An immediate obstacle did not invalidate the remaining path')
laterWall=nil;slowRoot.Position=Vector3.new(0,2.5,0);prefix:Destroy()
local cadence=Guide.new(nil)
cadence:SetTarget({position=Vector3.new(100,0,0)});cadence:Step(slowRoot,0,true);flush()
rayCount=0;cadence:Step(slowRoot,.2,true);check(rayCount<=54,'ray work exceeds bounded two-height checks')
local filter=cadence.raycast.FilterDescendantsInstances
local previousRays=rayCount;cadence:Step(slowRoot,.25,true);check(rayCount==previousRays,'ray work escaped 150ms cadence')
cadence:Step(slowRoot,.4,true);check(filter==cadence.raycast.FilterDescendantsInstances,'filter reallocated with unchanged character')
cadence:Destroy()
print('PASS '..count..' NavigationGuide mocked lifecycle checks; native pathfinding/streaming unverified')
'''
def run(module):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=R/'tests',delete=False) as f:
  f.write(setup+module+checks);p=Path(f.name)
 try:return subprocess.run(['luau',str(p)],cwd=R,capture_output=True,text=True)
 finally:p.unlink()

parser=argparse.ArgumentParser()
parser.add_argument('--negative-controls',action='store_true')
result=run(source)
assert result.returncode==0,result.stderr
print(result.stdout.strip())
if parser.parse_args().negative_controls:
 for old,new,message in (
  ('if keepThrottle and valid and self.target and self.target.label==label then','if false then','Small moving target update cleared a compatible route'),
  ('if self.points and ((self.pathGoal-target.position).Magnitude>MAX_TARGET_DRIFT\n   or (self.points[#self.points].Position-target.position).Magnitude>MAX_TARGET_DRIFT) then','if false then','A large move kept a stale route'),
  ('or (self.target.position-destination).Magnitude>MAX_TARGET_DRIFT then','then','A large move admitted an old in-flight route'),
  ('or (points[#points].Position-self.target.position).Magnitude>MAX_TARGET_DRIFT then','then','A replacement endpoint too far from live Mar was accepted'),
  ('or (self.points[#self.points].Position-target.position).Magnitude>MAX_TARGET_DRIFT) then',') then','A retained endpoint too far from live Mar was left visible'),
  ('if count>0 then break end','', 'A later obstacle hid the checked-clear path or showed a dot past it'),
 ):
  assert source.count(old)==1,old
  result=run(source.replace(old,new))
  assert result.returncode and message in result.stderr,result.stdout+result.stderr
  print('PASS negative control:',message)
