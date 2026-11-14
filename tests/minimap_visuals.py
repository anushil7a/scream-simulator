"""World-derived map art and tiny-marker checks. Mock geometry, not native visual proof."""
from pathlib import Path
import ast,argparse,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');args=p.parse_args()
source=(ROOT/'src/StarterPlayer/StarterPlayerScripts/CityMap.luau').read_text(encoding='utf-8');source=source[source.index('local CityMap={}'):]
layout=(ROOT/'src/ReplicatedStorage/Shared/CompactLayout.luau').read_text(encoding='utf-8')
tree=ast.parse((ROOT/'tests/minimap.py').read_text(encoding='utf-8'))
setup=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='setup' for t in n.targets))
setup=setup[:setup.index('local Config=')]+"local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}\nlocal Layout=(function()\n"
bridge=r'''
end)()
local Config={CompactCity=true,MapMin=Layout.BoundsMin,MapMax=Layout.BoundsMax,ZoneMin=Layout.ZoneMin,ZoneMax=Layout.ZoneMax}
local shared={WaitForChild=function(_,name)return name end}
local game={GetService=function()return {WaitForChild=function()return shared end}end}
local require=function(name)assert(name=='CompactLayout');return Layout end
local CityMap=(function()
'''
checks=r'''
end)()
local function find(parent,name)for _,o in ipairs(objects)do if o.Parent==parent and o.Name==name then return o end end end
local full=CityMap.create({});local mini=CityMap.create({},true)
local expected=0
for _,spec in ipairs(Layout.PartSpecs)do
 local selected=spec.id:match('^MarketHouse') or spec.id:match('^OldTownHouse') or spec.id:match('^Basilica') or spec.id:match('^GardenBed') or spec.id:match('^TrainingPad') or spec.kind=='cover' or spec.id=='Court'
 for _,view in ipairs({full,mini})do
  local f=find(view.map,'Footprint_'..spec.id)
  check((f~=nil)==(selected and true or false),'Static footprint selection mismatch')
  if f then
   check(f.ClassName=='Frame' and f.BorderSizePixel==0,'Footprint is interactive or bordered')
   local pos=CityMap.Project(spec.position.X-spec.size.X/2,spec.position.Z-spec.size.Z/2)
   check(near(f.Position.X.Scale,pos.X.Scale) and near(f.Position.Y.Scale,pos.Y.Scale),'Footprint position drift')
   check(near(f.Size.X.Scale,spec.size.X/720) and near(f.Size.Y.Scale,spec.size.Z/600),'Footprint dimensions drift')
  end
 end
 if selected then expected+=1 end
end
check(expected==36,'Unexpected static footprint count')
for _,route in ipairs(Layout.GuidanceSpecs)do
 for _,view in ipairs({full,mini})do
  local f=find(view.map,'Route_'..route.id)
  check((f~=nil)==(route.id:match('^Route')~=nil),'Route missing or target-frame added')
  if f then
   local pos=CityMap.Project(route.position.X-route.size.X/2,route.position.Z-route.size.Z/2)
   check(near(f.Position.X.Scale,pos.X.Scale) and near(f.Position.Y.Scale,pos.Y.Scale),'Route position drift')
   check(near(f.Size.X.Scale,route.size.X/720) and near(f.Size.Y.Scale,route.size.Z/600),'Route dimensions drift')
  end
 end
end
check(mini.dot.Size.X.Offset==8 and mini.dot.Size.Y.Offset==8,'Mini marker hides map')
check(full.dot.Size.X.Offset==18 and full.arrow and not mini.arrow,'Modal/mini arrow policy changed')
check(not find(mini.map,'North') and not find(mini.map,'Landmark1'),'Compact decoration clutter')
local outline;for _,o in ipairs(objects)do if o.ClassName=='UIStroke' and o.Parent==mini.dot then outline=o end end
check(outline and outline.Thickness==2,'Marker contrast outline missing')
local function indexOf(obj)for idx,o in ipairs(objects)do if o==obj then return idx end end end
local hubSpec,courtSpec
for _,spec in ipairs(Layout.PartSpecs)do
 if spec.id=='HubPaving' then hubSpec=spec elseif spec.id=='Court' then courtSpec=spec end
end
check(hubSpec~=nil and courtSpec~=nil,'Required courtyard/court specs missing')
for _,view in ipairs({full,mini})do
 local corner,border
 for _,o in ipairs(objects)do
  if o.Parent==view.map and o.ClassName=='UICorner' then corner=o end
  if o.Parent==view.map and o.ClassName=='UIStroke' and o.Name=='MapBorder' then border=o end
 end
 check(corner and corner.CornerRadius.Offset==4,'Map frame corner radius missing')
 check(border and border.Thickness==1 and near(border.Transparency,.35),'Map border stroke missing')
 local courtyard=find(view.map,'Courtyard')
 check(courtyard~=nil,'Courtyard plaza zone missing')
 local hubPos=CityMap.Project(hubSpec.position.X-hubSpec.size.X/2,hubSpec.position.Z-hubSpec.size.Z/2)
 check(near(courtyard.Position.X.Scale,hubPos.X.Scale) and near(courtyard.Position.Y.Scale,hubPos.Y.Scale),'Courtyard position drift')
 check(near(courtyard.Size.X.Scale,hubSpec.size.X/720) and near(courtyard.Size.Y.Scale,hubSpec.size.Z/600),'Courtyard dimensions drift')
 local beach=find(view.map,'Beach');local shore=find(view.map,'Shoreline');local court=find(view.map,'Footprint_Court')
 check(beach~=nil and shore~=nil and court~=nil,'Shoreline surf accent missing')
 check(indexOf(courtyard)<indexOf(beach),'Courtyard rendered above beach')
 check(near(shore.Position.X.Scale,beach.Position.X.Scale) and near(shore.Size.X.Scale,beach.Size.X.Scale),'Shoreline width drift')
 check(shore.Position.Y.Scale>court.Position.Y.Scale+court.Size.Y.Scale,'Shoreline overlaps coastal court')
 check(near(shore.Size.Y.Scale,9/600) and near(shore.Position.Y.Scale+shore.Size.Y.Scale,1),'Shoreline not flush with south coast')
end
for i,v in ipairs(Layout.MapLandmarks)do
 if v.name~='2 Training' then
  local pin=find(full.map,'Landmark'..i)
  local rim;for _,o in ipairs(objects)do if o.Parent==pin and o.ClassName=='UIStroke' then rim=o end end
  check(rim and rim.Thickness==1 and near(rim.Transparency,.35),'Landmark pin rim missing')
 end
end
local count=#objects
for i=1,100 do CityMap.MiniUpdate(mini,{Parent={},Position={X=-270,Z=130},CFrame={LookVector={X=0,Z=-1}}},i,true)end
check(#objects==count,'Map art rebuilt during updates')
for _,o in ipairs(objects)do check(o.ClassName~='ViewportFrame' and o.ClassName~='ImageLabel' and o.ClassName~='TextButton','Map requires assets, extra renderer or hidden inputs')end
print('PASS '..checks..' world-derived map art assertions; mocked only')
'''
def run(s,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False) as f:f.write(setup+layout+bridge+s+checks);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],text=True,capture_output=True)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if expected:assert r.returncode and expected in out,out;print('PASS negative control:',expected)
 else:assert r.returncode==0,out;print(out.strip())
run(source)
if args.negative_controls:
 for a,b,e in [
  ("if architecture or training or cover or court then","if false then","Static footprint selection mismatch"),
  ("part.size.X/width,part.size.Z/depth,color","part.size.X/depth,part.size.Z/width,color","Footprint dimensions drift"),
  ("if route.id:match('^Route') then","if false then","Route missing or target-frame added"),
  ("compact and 8 or 18","18","Mini marker hides map"),
  ("local mapBorder=Instance.new('UIStroke');mapBorder.Name='MapBorder';mapBorder.Color=Color3.fromRGB(115,148,148);mapBorder.Thickness=1;mapBorder.Transparency=.35;mapBorder.Parent=map","","Map border stroke missing"),
  ("if part.id==\"HubPaving\" or part.id==\"Beach\" then","if part.id==\"Beach\" then","Courtyard plaza zone missing"),
  ("box(map,'Shoreline',shore.X.Scale,shore.Y.Scale,part.size.X/width,9/depth,Color3.fromRGB(64,134,152))","","Shoreline surf accent missing"),
  ("Config.MapMax.Z-9","Config.MapMax.Z-8","Shoreline not flush with south coast"),
  ("shore.X.Scale,shore.Y.Scale,part.size.X/width,9/depth","shore.X.Scale,shore.Y.Scale-6/depth,part.size.X/width,15/depth","Shoreline overlaps coastal court"),
  ("local pinStroke=Instance.new('UIStroke');pinStroke.Color=Color3.fromRGB(168,186,184);pinStroke.Thickness=1;pinStroke.Transparency=.35;pinStroke.Parent=pin","","Landmark pin rim missing"),
 ]:
  assert a in source;run(source.replace(a,b),e)
