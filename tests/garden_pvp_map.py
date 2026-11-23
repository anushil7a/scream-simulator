"""Actual Map10 shape/projection and local zone cue with GUI doubles; no native/device claim."""
from pathlib import Path
import subprocess,tempfile,argparse
R=Path(__file__).resolve().parents[1]
layout=(R/'src/ReplicatedStorage/Shared/CompactLayout.luau').read_text()
config=(R/'src/ReplicatedStorage/Shared/Config.luau').read_text()
config='\n'.join(line for line in config.splitlines() if line.startswith(('function Config.HasGardenPvp(', 'function Config.InGardenPvp(', 'function Config.InArena(')))
source=(R/'src/StarterPlayer/StarterPlayerScripts/CityMap.luau').read_text()
client=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
zone=client[client.index('function academy.refreshZone()'):client.index('\nlocal ',client.index('function academy.layoutZone('))]
# End on the next top-level block after both exact helper bodies.
zone=zone[:zone.index('\nend',zone.index('function academy.layoutZone('))+4]
guide_start=client.index('academy.guide=academy.NavigationGuide.new(gui,function(ground)')
guide=client[guide_start:client.index('\nownClient(',guide_start)]
PRE=r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local function near(a,b)return math.abs(a-b)<1e-8 end
local Vector3={}
local vector={__add=function(a,b)return Vector3.new(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end}
function Vector3.new(x,y,z)return setmetatable({X=x,Y=y,Z=z},vector)end
local Vector2={new=function(x,y)return {X=x,Y=y}end}
local UDim2={new=function(x,ox,y,oy)return {X={Scale=x,Offset=ox},Y={Scale=y,Offset=oy}}end,fromScale=function(x,y)return {X={Scale=x,Offset=0},Y={Scale=y,Offset=0}}end,fromOffset=function(x,y)return {X={Scale=0,Offset=x},Y={Scale=0,Offset=y}}end}
local UDim={new=function(s,o)return {Scale=s,Offset=o}end}
local Color3={fromRGB=function(r,g,b)return {r,g,b}end}
local Enum={Font={GothamBold=1},AspectType={FitWithinMaxSize=1}}
local objects={};local Instance={new=function(c)local o={ClassName=c};table.insert(objects,o);return o end}
local Layout=(function()
'''
BRIDGE=r'''
end)()
local Config={CompactCity=true,MapMin=Layout.BoundsMin,MapMax=Layout.BoundsMax,ZoneMin=Layout.ZoneMin,ZoneMax=Layout.ZoneMax}
local CompactLayout=Layout
'''
BRIDGE2=r'''
local BossCatalog={Entries={}} -- Preserve pin construction path without replacing tested map geometry.
local node={};function node:WaitForChild(name)return name=='Shared' and self or name end
local game={GetService=function()return node end}
local TrainingRules=require('../src/ReplicatedStorage/Shared/TrainingRules')
local function require(name)if name=='Config'then return Config elseif name=='CompactLayout'then return Layout elseif name=='BossCatalog'then return BossCatalog else error(name)end end
local CityMap=(function()
'''
POST=r'''
end)()
local function find(parent,name)for _,o in ipairs(objects)do if o.Parent==parent and o.Name==name then return o end end end
local full=CityMap.create({});local mini=CityMap.create({},true)
check(#Layout.GardenPvpRects>5 and #Layout.GardenPvpEdges>0,'Clipped canonical footprint absent')
check(full.arrow and not mini.arrow,'Existing modal/mini marker policy changed')
for i in ipairs(Layout.MapLandmarks)do
 local pin=find(full.map,'Landmark'..i)
 if pin then check(pin.ZIndex>2,'Map labels covered by territory fill')end
end
check(CityMap.mapHelp:find('Red: PvP',1,true) and not CityMap.mapHelp:find('North',1,true),'Legend/compass policy wrong')
for _,view in ipairs({full,mini})do
 for i,home in ipairs(Layout.TrainingHomes)do
  local mark=find(view.map,'Footprint_TrainingPad'..i);check(mark~=nil,'Sparring map footprint missing')
  local a,b=CityMap.Project(home.x-32,home.z-32),CityMap.Project(home.x+32,home.z+32)
  check(near(mark.Position.X.Scale,a.X.Scale) and near(mark.Position.Y.Scale,a.Y.Scale)
   and near(mark.Size.X.Scale,b.X.Scale-a.X.Scale) and near(mark.Size.Y.Scale,b.Y.Scale-a.Y.Scale),'Sparring circle projection lost its diameter')
  local rounded=false
  for _,o in ipairs(objects)do if o.Parent==mark and o.ClassName=='UICorner' and o.CornerRadius.Scale==.5 then rounded=true end end
  check(rounded,'Sparring map still shows a square')
 end
 for i,r in ipairs(Layout.GardenPvpRects)do
  local f=find(view.map,'GardenPvp_'..i);check(f~=nil,'Missing canonical rect')
  local a,b=CityMap.Project(r.minX,r.minZ),CityMap.Project(r.maxX,r.maxZ)
  check(near(f.Position.X.Scale,a.X.Scale)and near(f.Position.Y.Scale,a.Y.Scale),'PvP rect translated from world shape')
  check(near(f.Size.X.Scale,b.X.Scale-a.X.Scale)and near(f.Size.Y.Scale,b.Y.Scale-a.Y.Scale),'PvP rect dimensions changed')
  check(f.BackgroundTransparency>0 and f.BackgroundTransparency<1 and not f.Active and not f.Selectable and not f.Interactable,'PvP fill not passive/translucent')
  for _,o in ipairs(objects)do check(not(o.Parent==f and o.ClassName=='UIStroke'),'Individual rect seam drawn')end
 end
 for i,e in ipairs(Layout.GardenPvpEdges)do
  local f=find(view.map,'GardenPvpEdge_'..i);check(f~=nil,'Missing exterior segment')
  local a=CityMap.Project(math.min(e.x1,e.x2),math.min(e.z1,e.z2))
  local b=CityMap.Project(math.max(e.x1,e.x2),math.max(e.z1,e.z2))
  check(near(f.Position.X.Scale,a.X.Scale)and near(f.Position.Y.Scale,a.Y.Scale),'Exterior edge shifted')
  check(near(f.Size.X.Scale,b.X.Scale-a.X.Scale)and near(f.Size.Y.Scale,b.Y.Scale-a.Y.Scale),'Exterior edge distorted')
  local mx,mz=(e.x1+e.x2)/2,(e.z1+e.z2)/2
  check(Layout.InGardenPvpXZ(mx+e.inX*.01,mz+e.inZ*.01)~=Layout.InGardenPvpXZ(mx-e.inX*.01,mz-e.inZ*.01),'False interior seam')
 end
 local stadium=find(view.map,'ArenaBoundary');local a,b=CityMap.Project(Config.ZoneMin.X,Config.ZoneMin.Z),CityMap.Project(Config.ZoneMax.X,Config.ZoneMax.Z)
 check(near(stadium.Position.X.Scale,a.X.Scale)and near(stadium.Position.Y.Scale,a.Y.Scale)and near(stadium.Size.X.Scale,b.X.Scale-a.X.Scale)and near(stadium.Size.Y.Scale,b.Y.Scale-a.Y.Scale),'Existing stadium outline changed')
end
local w,d=Config.MapMax.X-Config.MapMin.X,Config.MapMax.Z-Config.MapMin.Z
for x=-320,320,5 do for z=-180,190,5 do
 local projected=CityMap.Project(x,z)
 local painted=false
 for i,r in ipairs(Layout.GardenPvpRects)do
  local f=find(full.map,'GardenPvp_'..i)
  if projected.X.Scale>=f.Position.X.Scale-1e-8 and projected.X.Scale<=f.Position.X.Scale+f.Size.X.Scale+1e-8 and projected.Y.Scale>=f.Position.Y.Scale-1e-8 and projected.Y.Scale<=f.Position.Y.Scale+f.Size.Y.Scale+1e-8 then painted=true end
 end
 if x~=-190 and x~=170 and z~=95 and z~=125 and x~=-108 and x~=-72 and z~=-170 and z~=-70 and x~=300 and z~=25 and z~=55 then
  check(painted==Config.InGardenPvp(Vector3.new(x,20,z)),'Projected PvP fill diverged from canonical server function')
 end
end end
local zoneValues={Text=''};local zoneWrites=0
local zone=setmetatable({},{__index=zoneValues,__newindex=function(_,key,value)zoneWrites+=1;zoneValues[key]=value end});local white,gold='white','gold';local academy={TrainingRules=TrainingRules};local root={Position=Vector3.new(0,20,0)}
local bossHint
local attributes={};local humanoid={Health=100}
local character={FindFirstChild=function()return root end,FindFirstChildOfClass=function()return humanoid end,GetAttribute=function(_,key)return attributes[key]end}
local p={Character=character,GetAttribute=function()return bossHint end}
local now=10
local workspace={GetServerTimeNow=function()return now end}
local function typeof(value)return type(value)=='table' and 'Vector3' or type(value)end
local data,gui={},{}
local ahead,classified,allowsRouteLights
academy.NavigationGuide={new=function(_,classifier,allowsLights)
 classified=classifier;allowsRouteLights=allowsLights
 return {HasPvPAhead=function()return ahead==true end}
end}
'''
POST2=r'''
academy.refreshZone();check(zone.Text=='GARDEN • PvP ON','Current local garden cue missing')
bossHint='Step off the circles';academy.refreshZone();check(zone.Text=='GARDEN • PvP ON','Boss hint must not obscure active PvP')
root.Position=Vector3.new(0,20,110);academy.refreshZone()
check(zone.Text==bossHint and zone.TextColor3==gold,'Boss hint did not use existing safe status lane')
bossHint=nil
attributes.TrainingStrikeAt=11;attributes.TrainingStrikeCenter=Vector3.new(0,17,110)
academy.refreshZone();check(zone.Text=='MOVE OR DODGE','Targeted strike did not reach the status lane')
root.Position=Vector3.new(4,20,110);academy.refreshZone();check(zone.Text=='MOVE OR DODGE','Warning ended on the inclusive strike edge')
root.Position=Vector3.new(4.1,20,110);academy.refreshZone();check(zone.Text=='SAFE • PvP OFF','Leaving the circle retained the training cue')
root.Position=Vector3.new(0,23.01,110);academy.refreshZone();check(zone.Text=='SAFE • PvP OFF','Ground warning retained above the damage band')
root.Position=Vector3.new(0,20,110);academy.refreshZone();check(zone.Text=='MOVE OR DODGE','Crossing back into the circle missed the warning')
humanoid.Health=0;academy.refreshZone();check(zone.Text=='SAFE • PvP OFF','Dead character retained the training cue')
humanoid.Health=100
bossHint='Step off the circles';academy.refreshZone();check(zone.Text==bossHint,'Training cue displaced the boss cue')
bossHint=nil
now=11;academy.refreshZone();check(zone.Text=='SAFE • PvP OFF','Expired training cue retained')
root.Position=Vector3.new(0,20,110);academy.refreshZone();check(zone.Text=='SAFE • PvP OFF','Cafe path HUD unsafe')
root.Position=Vector3.new(0,35,0);academy.refreshZone();check(zone.Text=='SAFE • PvP OFF','HUD ignores height band')
root.Position=Vector3.new((Layout.ZoneMin.X+Layout.ZoneMax.X)/2,(Layout.ZoneMin.Y+Layout.ZoneMax.Y)/2,(Layout.ZoneMin.Z+Layout.ZoneMax.Z)/2)
academy.refreshZone();check(zone.Text=='ARENA • PvP ON','Existing stadium cue mislabeled')
p.Character=nil;academy.refreshZone();check(zone.Text=='SAFE • PvP OFF','Missing character shows stale PvP')
local prior=zoneWrites;for _=1,1000 do academy.refreshZone()end;check(zoneWrites==prior,'Unchanged zone writes UI every frame')
p.Character=character;root.Position=Vector3.new(51,19.8,113)
local terrace=Vector3.new(80,16,126)
data.activeQuest='delivery';academy.guideSelection={kind='quest',id='delivery'}
check(classified(terrace),'Non-Beach route failed to classify a verified PvP terrace')
ahead=true;academy.refreshZone()
check(zone.Text=='SAFE • PvP AHEAD' and zone.TextColor3==gold,'Approach did not distinguish safe now from upcoming PvP')
data.activeQuest=nil
for _,selection in ipairs({{kind='place',id='coast'},{kind='boss',id='metronome'}}) do
 academy.guideSelection=selection
 check(classified(terrace),'Public guide without a quest failed to classify Garden PvP')
 academy.refreshZone()
 check(zone.Text=='SAFE • PvP AHEAD','Public guide without a quest lost the HUD warning')
end
data.activeQuest='beach';academy.guideSelection={kind='quest',id='beach'}
check(classified(terrace),'Beach route stopped flagging Garden PvP')
local cafe=Vector3.new(80,16,125)
local stadium=Vector3.new((Layout.ZoneMin.X+Layout.ZoneMax.X)/2,0,(Layout.ZoneMin.Z+Layout.ZoneMax.Z)/2)
check(classified(stadium),'Stadium route failed to classify PvP')
check(not classified(cafe),'Safe café edge marked PvP')
check(not classified(Vector3.new(80,32,126)) and not classified(Vector3.new(80,10,126)),'Route warning ignored garden height band')
check(not allowsRouteLights(terrace) and not allowsRouteLights(stadium) and allowsRouteLights(cafe),'Route Lights cannot tint known PvP ground')
Config.ResonanceLayout={Contains=function()return false end}
academy.refreshZone()
check(not classified(terrace) and zone.Text=='SAFE • PvP OFF','City route warning leaked into Resonance Hall')
Config.ResonanceLayout=nil
root.Position=Vector3.new(80,19.8,126);academy.refreshZone()
check(zone.Text=='GARDEN • PvP ON','Advance warning displaced live Garden PvP')
root.Position=Vector3.new(51,19.8,113);bossHint='Step off the circles';academy.refreshZone()
check(zone.Text==bossHint,'Advance warning displaced an active boss warning')
bossHint=nil;attributes.TrainingStrikeAt=12;attributes.TrainingStrikeCenter=Vector3.new(51,17,113);academy.refreshZone()
check(zone.Text=='MOVE OR DODGE','Advance warning displaced an active training warning')
attributes.TrainingStrikeAt=nil;ahead=false;academy.refreshZone()
check(zone.Text=='SAFE • PvP OFF','Advance warning remained after dangerous markers cleared')
for _,viewport in ipairs({{X=320,Y=568},{X=390,Y=844},{X=844,Y=390},{X=1280,Y=720}})do
 for _,touch in ipairs({false,true})do
  academy.layoutZone(viewport,touch)
  local x=viewport.X*zone.Position.X.Scale+zone.Position.X.Offset
  local y=viewport.Y*zone.Position.Y.Scale+zone.Position.Y.Offset
  check(x>=0 and x+zone.Size.X.Offset<=viewport.X and y>=0 and y+zone.Size.Y.Offset<=viewport.Y,'Zone outside viewport')
  if touch or viewport.X<820 then
   check(y-48>=1 and 64-y-zone.Size.Y.Offset>=1 and x+zone.Size.X.Offset<=viewport.X-120,'Compact zone overlaps existing top buttons/HUD/right launcher lane')
   check(160-y-zone.Size.Y.Offset>=97,'Compact zone intrudes quest lane')
  else check(40-y-zone.Size.Y.Offset>=4,'Desktop zone touches save status')end
 end
end
print('PASS '..n..' actual Map10 canonical fill/edge/projection + local zone cue assertions; mocked GUI, native/mobile still required')
'''
def code(s,hud,route):return PRE+layout+'\n'+BRIDGE+config+'\n'+BRIDGE2+s+'\n'+POST+'\n'+route+'\n'+hud+'\n'+POST2
def run(s,negative=False,hud=zone,route=guide):
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False)as f:f.write(code(s,hud,route));p=Path(f.name)
 try:
  r=subprocess.run(['luau',str(p)],capture_output=True,text=True);out=r.stdout+r.stderr
  if negative:
   assert r.returncode and (negative is True or negative in out),out
   print('PASS negative control:',out.splitlines()[0])
  else:assert not r.returncode,out;print(out,end='')
 finally:p.unlink()
if __name__=='__main__':
 assert 'UDim2.fromOffset(125,36)' in client and 'UDim2.fromOffset(95,36)' in client
 assert 'UDim2.new(.5,-125,0,40)' in client and 'or 64)' in client
 assert 'Arena District: %d%% PvP' not in client
 p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');a=p.parse_args();run(source)
 if a.negative_controls:
  run(source.replace('local spanX=roundPad and part.size.Y or part.size.X','local spanX=part.size.X'),'Sparring circle projection lost its diameter')
  run(source.replace('if roundPad then','if false then'),'Sparring map still shows a square')
  run(source.replace('finish.X.Scale-start.X.Scale,finish.Y.Scale-start.Y.Scale','1,1',1),True)
  run(source.replace('CityMap.GardenPvp(map,compact)','CityMap.NoGardenPvp(map,compact)',1).replace(' CityMap.GardenPvp(map,compact)','',1),True)
  for old,new,expected in [
   ('academy.TrainingRules.ContainsStrike(center,position)','true','Leaving the circle retained the training cue'),
   ('academy.TrainingRules.ContainsStrike(center,position)','academy.TrainingRules.ContainsStrike(center,Vector3.new(position.X,center.Y+3,position.Z))','Ground warning retained above the damage band'),
   ('workspace:GetServerTimeNow()<strikeAt','true','Expired training cue retained'),
   ('or pvpAhead and "SAFE • PvP AHEAD"', 'or false and "SAFE • PvP AHEAD"', 'Approach did not distinguish safe now from upcoming PvP'),
  ]:
   assert zone.count(old)==1
   run(source,expected,zone.replace(old,new))
  run(source,'Non-Beach route failed to classify a verified PvP terrace',
      route=guide.replace('not Config.ResonanceLayout and Config.InArena','data.activeQuest=="beach" and Config.InArena',1))
  run(source,'Approach did not distinguish safe now from upcoming PvP',
      hud=zone.replace('academy.guide and academy.guide:HasPvPAhead()', 'academy.guide and data.activeQuest=="beach" and academy.guide:HasPvPAhead()'))
  run(source,'Stadium route failed to classify PvP',route=guide.replace('and Config.InArena','and Config.InGardenPvp',1))
  run(source,'Safe café edge marked PvP',route=guide.replace('and Config.InArena(ground+Vector3.new(0,3,0))','and true',1))
  run(source,'City route warning leaked into Resonance Hall',
      route=guide.replace('not Config.ResonanceLayout and Config.InArena','Config.InArena',1))
