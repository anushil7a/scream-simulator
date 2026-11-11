"""Actual CityMap and CompactLayout under synthetic GUI; no native render/input claims."""
from pathlib import Path
import ast,argparse,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--negative-controls',action='store_true');args=parser.parse_args()
# Reuse only the explicit GUI mock definitions, never execute another test module.
tree=ast.parse((root/'tests/minimap.py').read_text())
setup=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='setup' for t in n.targets))
setup=setup[:setup.index('local Config=')]
layout=(root/'src/ReplicatedStorage/Shared/CompactLayout.luau').read_text()
source=(root/'src/StarterPlayer/StarterPlayerScripts/CityMap.luau').read_text()
pre=r'''
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local Layout=(function()
'''
bridge=r'''
end)()
local Config={CompactCity=true,MapMin=Layout.BoundsMin,MapMax=Layout.BoundsMax,ZoneMin=Layout.ZoneMin,ZoneMax=Layout.ZoneMax}
local node={};function node:WaitForChild(name)return name=='Shared' and self or name end
local game={GetService=function()return node end}
local function require(name)if name=='Config' then return Config elseif name=='CompactLayout' then return Layout else error('Unexpected import')end end
local CityMap=(function()
'''
tests=r'''
end)()
local function find(parent,name)for _,o in ipairs(objects)do if o.Parent==parent and o.Name==name then return o end end end
local full=CityMap.create({});local mini=CityMap.create({},true)
check(near(CityMap.aspectRatio,1.2),'Compact aspect ratio wrong')
check(CityMap.arenaPercent==24,'Compact arena fraction wrong')
local min,max=Layout.BoundsMin,Layout.BoundsMax
local points={{-360,-300,0,0},{360,300,1,1},{0,0,.5,.5},{-270,130,.125,430/600},{-245,-185,115/720,115/600},{-999,999,0,1}}
for _,v in ipairs(Layout.MapLandmarks)do table.insert(points,{v.x,v.z,(v.x+360)/720,(v.z+300)/600})end
local r={Parent={},Position={X=0,Z=0},CFrame={LookVector={X=0,Z=-1}}}
for _,v in ipairs(points)do
 local projected=CityMap.Project(v[1],v[2]);check(near(projected.X.Scale,v[3]) and near(projected.Y.Scale,v[4]),'Compact projection wrong')
 for _,view in ipairs({full,mini})do
  r.Position={X=v[1],Z=v[2]};CityMap.update(view,r)
  check(view.dot.Visible and near(view.dot.Position.X.Scale,v[3]) and near(view.dot.Position.Y.Scale,v[4]),'Map marker disagrees with projection')
 end
end
for _,heading in ipairs({{0,-1,0},{1,0,90},{0,1,180},{-1,0,-90},{1,-1,45},{-1,1,-135}})do
 r.CFrame.LookVector={X=heading[1],Z=heading[2]};CityMap.update(full,r)
 check(near(full.arrow.Rotation,heading[3]),'Compact facing direction wrong')
end
for i,v in ipairs(Layout.MapLandmarks)do
 local pin=find(full.map,'Landmark'..i);local projected=CityMap.Project(v.x,v.z)
 check(pin and near(pin.Position.X.Scale,projected.X.Scale) and near(pin.Position.Y.Scale,projected.Y.Scale),'Compact landmark misplaced')
 check(not find(mini.map,'Landmark'..i),'Minimap landmark clutter')
 check(string.find(CityMap.legend,v.name,1,true)~=nil,'Legend omits compact landmark')
end
for _,road in ipairs(Layout.MapRoads)do
 local projected=CityMap.Project(road.x-road.width/2,road.z-road.depth/2)
 for _,view in ipairs({full,mini})do
  local b=find(view.map,road.name)
  check(b and near(b.Position.X.Scale,projected.X.Scale) and near(b.Position.Y.Scale,projected.Y.Scale),'Compact road misplaced')
  check(near(b.Size.X.Scale,road.width/720) and near(b.Size.Y.Scale,road.depth/600),'Compact road scale wrong')
 end
end
local beachSpec;for _,part in ipairs(Layout.PartSpecs)do if part.id=='Beach' then beachSpec=part end end
check(beachSpec~=nil,'Shared beach absent')
for _,view in ipairs({full,mini})do
 local beach=find(view.map,'Beach');local start=CityMap.Project(beachSpec.position.X-beachSpec.size.X/2,beachSpec.position.Z-beachSpec.size.Z/2)
 check(beach and near(beach.Position.X.Scale,start.X.Scale) and near(beach.Position.Y.Scale,start.Y.Scale),'Compact beach misplaced')
 check(near(beach.Size.X.Scale,beachSpec.size.X/720) and near(beach.Size.Y.Scale,beachSpec.size.Z/600),'Compact beach scale wrong')
end
local arena=find(full.map,'Arena')
check(near(arena.Position.X.Scale,240/720) and near(arena.Position.Y.Scale,120/600),'Arena origin wrong')
check(near(arena.Size.X.Scale,320/720) and near(arena.Size.Y.Scale,320/600),'Arena bounds wrong')
check(not find(full.map,'TimberPier') and not find(full.map,'Avenue'),'Legacy city geometry leaked into compact map')
CityMap.MiniUpdate(mini,r,0,true);r.Parent=nil;CityMap.MiniUpdate(mini,r,.01,true);check(not mini.dot.Visible,'Detached root marker retained')
local replacement={Parent={},Position={X=-270,Z=130},CFrame={LookVector={X=-1,Z=0}}}
CityMap.MiniUpdate(mini,replacement,.02,true);check(mini.dot.Visible and near(mini.dot.Position.X.Scale,.125) and mini.arrow.Rotation==-90,'Respawn marker not immediate')
local nextRoot={Parent={},Position={X=0,Z=0},CFrame={LookVector={X=1,Z=0}}};CityMap.MiniUpdate(mini,nextRoot,.025,true);check(near(mini.dot.Position.X.Scale,.5) and mini.arrow.Rotation==90,'Respawn marker not immediate')
CityMap.MiniUpdate(mini,replacement,.03,false);check(not mini.dot.Visible and mini.lastRoot==nil,'Hidden marker retained')
print('PASS '..checks..' compact CityMap projection/render/lifecycle assertions; mocked GUI only')
'''
def run(body,error=None):
 code=setup+pre+layout+bridge+body+tests
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False,encoding='utf-8')as f:f.write(code);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],text=True,capture_output=True)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS negative control:',error)
 else:assert r.returncode==0,out;print(out.strip())
run(source)
if args.negative_controls:
 for old,new,error in [
  ('(x-minX)/width','(x+720)/1440','Compact arena fraction wrong'),
  ('(z-minZ)/depth','(z+600)/1200','Compact arena fraction wrong'),
  ('math.atan2(look.X,-look.Z)','math.atan2(-look.X,-look.Z)','Compact facing direction wrong'),
  ('road.width/width','road.width/1440','Compact road scale wrong'),
  ('part.id=="Beach"','part.id=="NotBeach"','Compact beach misplaced'),
  ('ipairs(compact and {} or landmarks)','ipairs(landmarks)','Minimap landmark clutter'),
  ('view.lastRoot==root and view.nextUpdate','view.nextUpdate','Respawn marker not immediate')]:
  changed=source.replace(old,new);assert changed!=source,old;run(changed,error)
