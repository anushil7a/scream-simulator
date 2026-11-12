"""Actual compact modules with mocked Instances plus static clearance reachability; not native pathfinding."""
from pathlib import Path
import argparse,subprocess,tempfile,math,collections,re
ROOT=Path(__file__).resolve().parents[1]
layout=(ROOT/'src/ReplicatedStorage/Shared/CompactLayout.luau').read_text();city=(ROOT/'src/ServerScriptService/CompactCity.luau').read_text()
setup=r'''
local checks=0;local function check(ok,msg)assert(ok,msg);checks+=1 end
local V={};V.__index=function(t,k)if k=='Magnitude' then return math.sqrt(t.X*t.X+t.Y*t.Y+t.Z*t.Z)else return V[k]end end
local Vector3={new=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},V)end}
V.__sub=function(a,b)return Vector3.new(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
local Color3={fromRGB=function(r,g,b)return {R=r,G=g,B=b}end}
local CFrame={new=function(p)return {Position=p}end}
local Enum={Material={SmoothPlastic=1},KeyCode={F=1},Font={GothamBold=1}}
local UDim2={fromOffset=function(x,y)return {X=x,Y=y}end,fromScale=function(x,y)return {X=x,Y=y}end}
local nodes={};local Instance={new=function(class)local n={ClassName=class,attributes={},Transparency=0};function n:SetAttribute(k,v)self.attributes[k]=v end;table.insert(nodes,n);return n end}
local Layout=(function()
'''
between=r'''
end)()
local game={GetService=function(_,name)assert(name=='ReplicatedStorage','Unexpected service');return {Shared={CompactLayout='layout'}}end}
local require=function(name)assert(name=='layout');return Layout end
local City=(function()
'''
bootstrap=(ROOT/'src/ServerScriptService/Bootstrap.server.luau').read_text();beam=bootstrap[bootstrap.index('local function beamObstruction('):bootstrap.index('local function ',bootstrap.index('local function beamObstruction(')+1)]
policy=re.search(r'params\.RespectCanCollide=(?:true|false)',beam)[0]
tests=r'''
end)()
local result=City.Build({});check(result.compact and result.traffic==false,'Wrong compact build mode')
check(result.spawn.Position==Layout.Spawn and Layout.Spawn.X==-270 and Layout.Spawn.Z==130,'Wrong compact spawn')
check(#result.jobs==7 and #result.seeds==4,'Missing residents')
local guidanceNames={RouteToPractice=true,RouteToTrainingTurn=true,RouteToTraining=true,RouteToArena=true,PracticeFrameNear=true,PracticeFrameFar=true,PracticeFrameCrown=true}
local guidanceFolder;local guidanceCount=0
for _,n in ipairs(nodes)do if n.Name=='FirstMinuteGuidance' then check(n.ClassName=='Folder' and guidanceFolder==nil,'Duplicate/wrong guidance folder');guidanceFolder=n end end
check(guidanceFolder~=nil,'First-minute guidance missing')
local byName={};local prompts={}
for _,n in ipairs(nodes)do
 if n.ClassName=='Part' then
  check(n.Anchored and (n.CanQuery or guidanceNames[n.Name] or n.Name=='PracticeWayfinding' or n.Name=='ArenaWayfinding' or n.Name=='StandLine' or n.Name=='SpawnWayfinding') and n.CanTouch==false,'Unsafe static geometry flags')
  check(n.attributes.DestructibleType==nil and n.attributes.ObjectId==nil and n.attributes.ObjectHealth==nil and n.attributes.RequiredLevel==nil and n.attributes.Destructible==nil and n.attributes.DestructionLevel==nil and n.attributes.Breakable==nil,'Compact geometry tagged for destruction')
  if guidanceNames[n.Name] then
   check(n.Parent==guidanceFolder and not byName[n.Name],'Guidance part ownership/uniqueness invalid')
   check(n.Anchored==true and n.CanCollide==false and n.CanTouch==false and n.CanQuery==false and n.CastShadow==false,'Guidance physics/query/shadow enabled')
   check(n.Transparency==0 and n.Material==Enum.Material.SmoothPlastic,'Guidance invisible or emissive')
   check(next(n.attributes)==nil,'Guidance carries gameplay attributes')
   guidanceCount+=1
  elseif n.Parent==guidanceFolder then error('Unexpected guidance part') end
  byName[n.Name]=n
  print(string.format('PART|%s|%.6f|%.6f|%.6f|%.6f|%.6f|%.6f|%s',n.Name,n.Position.X,n.Position.Y,n.Position.Z,n.Size.X,n.Size.Y,n.Size.Z,tostring(n.CanCollide)))
 elseif n.ClassName=='ProximityPrompt' then
  local parent=n.Parent;check(parent and parent.attributes.QuestAction and n.KeyboardKeyCode==Enum.KeyCode.F and n.MaxActivationDistance==10 and n.RequiresLineOfSight==false,'Malformed quest prompt')
  check(not prompts[parent.Name],'Duplicate prompt marker');prompts[parent.Name]=parent
  print(string.format('REACH|%s|%.6f|%.6f|%.6f|10',parent.Name,parent.Position.X,parent.Position.Y,parent.Position.Z))
 end
end
check(guidanceCount==7,'Expected exactly seven guidance parts')
for _,n in ipairs(nodes)do
 if n.Parent==guidanceFolder then check(n.ClassName=='Part' and guidanceNames[n.Name],'Unexpected guidance child') end
 if n.Parent and guidanceNames[n.Parent.Name] then error('Guidance has prompt/light/descendant') end
end
local arena=byName.RouteToArena;local training=byName.RouteToTraining
check(arena.Position.X+arena.Size.X/2==-125 and arena.Position.X+arena.Size.X/2<Layout.ZoneMin.X,'Route crosses PvP threshold')
check(training.Position.Z-training.Size.Z/2>=25 and training.Position.Z-training.Size.Z/2>Layout.TrainingHomes[1].z+32,'Route overlaps rookie eligibility pad')
local target=byName.PracticeTarget
for name in pairs(guidanceNames)do
 local g=byName[name];check(g~=nil,'Named guidance part missing')
 -- Axis-aligned source geometry: no decorative volume may cover the target face or westward shot corridor.
 local xOverlap=g.Position.X+g.Size.X/2>=target.Position.X-target.Size.X/2 and g.Position.X-g.Size.X/2<=Layout.Practice.position.X
 local yOverlap=g.Position.Y+g.Size.Y/2>target.Position.Y-target.Size.Y/2 and g.Position.Y-g.Size.Y/2<target.Position.Y+target.Size.Y/2
 local zOverlap=g.Position.Z+g.Size.Z/2>target.Position.Z-target.Size.Z/2 and g.Position.Z-g.Size.Z/2<target.Position.Z+target.Size.Z/2
 check(not(xOverlap and yOverlap and zOverlap),'Guidance obscures practice shot corridor')
end
local routes={byName.RouteToPractice,byName.RouteToTrainingTurn,byName.RouteToTraining,byName.RouteToArena}
local linked={}
for i=1,4 do linked[i]={} end
for i=1,4 do for j=i+1,4 do
 local a,b=routes[i],routes[j]
 local ox=math.min(a.Position.X+a.Size.X/2,b.Position.X+b.Size.X/2)-math.max(a.Position.X-a.Size.X/2,b.Position.X-b.Size.X/2)
 local oz=math.min(a.Position.Z+a.Size.Z/2,b.Position.Z+b.Size.Z/2)-math.max(a.Position.Z-a.Size.Z/2,b.Position.Z-b.Size.Z/2)
 check(not(ox>0 and oz>0),'Route rectangles have coplanar area overlap')
 if (ox==0 and oz>0) or (oz==0 and ox>0) then linked[i][j]=true;linked[j][i]=true end
end end
local reached={[1]=true}
for _=1,4 do for i=1,4 do if reached[i] then for j in pairs(linked[i])do reached[j]=true end end end end
for i=1,4 do check(reached[i],'Route network lacks shared-edge connectivity') end
local expectedGuidance={
 RouteToPractice={-270,.10,97,8,.02,86},RouteToTrainingTurn={-257.5,.10,50,33,.02,8},RouteToTraining={-245,.10,35.5,8,.02,21},RouteToArena={-183,.10,50,116,.02,8},
 PracticeFrameNear={-280.8,8,48,.3,16,1},PracticeFrameFar={-280.8,8,82,.3,16,1},PracticeFrameCrown={-280.8,16.4,65,.3,.8,35}}
for name,e in pairs(expectedGuidance)do
 local g=byName[name];check(g.Position.X==e[1] and g.Position.Y==e[2] and g.Position.Z==e[3] and g.Size.X==e[4] and g.Size.Y==e[5] and g.Size.Z==e[6],'Guidance source dimensions differ')
 local r,h,b=177,174,153;if name=='PracticeFrameCrown' then r,h,b=255,203,99 elseif string.find(name,'PracticeFrame',1,true)then r,h,b=221,209,175 end
 check(g.Color.R==r and g.Color.G==h and g.Color.B==b,'Guidance palette changed')
end
for _,pair in ipairs({{'Flowerbed228','Garden'},{'Flowerbed250','Garden'},{'Flowerbed272','Garden'},{'CoffeeOrder','Pickup'},{'BoardwalkStart','RaceStart'},{'PierFinish','RaceFinish'},{'StageDelivery','Dropoff'},{'LookoutDelivery','Dropoff'},{'PierDelivery','Dropoff'}})do
 check(prompts[pair[1]] and prompts[pair[1]].attributes.QuestAction==pair[2],'Legacy quest marker/action missing')
end
for i=1,6 do check(prompts['Bottle'..i] and prompts['Bottle'..i].attributes.QuestAction=='Litter','Litter marker missing')end
check(byName.PracticeTarget.attributes.MicPracticeTarget==true and byName.PracticeTarget.attributes.RestColor~=nil,'Practice target wiring missing')
local params={};__RAY_POLICY__
check(byName.PracticeTarget.CanQuery and (not params.RespectCanCollide or byName.PracticeTarget.CanCollide),'Practice target excluded by actual beam raycast policy')
check((byName.PracticeTarget.Position-Layout.Practice.position).Magnitude<=12,'Practice beyond starter minimum range')
check(Layout.Soccer.center.Y==1.2 and Layout.Soccer.origin.Y==1.2,'Soccer floor alignment changed')
for _,points in ipairs({Layout.Soccer.lost,Layout.Soccer.gates,Layout.Soccer.obstacles,Layout.Soccer.goals})do
 for _,point in ipairs(points)do check(point.Y==1.2,'Soccer object floats above compact floor')end
end
local net=byName.VolleyNet;local top=net.Position.Y+net.Size.Y/2;local bottom=net.Position.Y-net.Size.Y/2
check(top==8 and bottom==4,'Volley visual net height differs from compact court')
check(math.abs(Layout.Volley.minimumCrossingHeight-(top+1.1+.1))<.000001,'Volley crossing clearance disagrees with visual net and ball radius')
check(Layout.Volley.floorBallY==1.1 and Layout.Volley.serve.Y==3 and Layout.Volley.board.Y==4,'Volley floor/serve alignment changed')
for _,node in ipairs(nodes)do if node.Name=='VolleyPost' then check(node.Size.Y==9 and node.Position.Y==4.5,'Volley post elevation wrong')end end
local signs={}
for _,node in ipairs(nodes)do
 if node.ClassName=='BillboardGui' then
  check(node.MaxDistance==65 and node.Size.X==260 and node.Size.Y==60 and node.AlwaysOnTop==false,'Unbounded wayfinding GUI')
  check(node.Parent and not node.Parent.CanCollide and not node.Parent.CanQuery,'Wayfinding blocks gameplay raycasts')
 elseif node.ClassName=='TextLabel' then signs[node.Parent.Parent.Name]=node.Text;check(node.TextWrapped and node.TextSize==16,'Wayfinding text settings wrong')end
end
check(signs.SpawnWayfinding=='MIC PRACTICE: NORTH\nTraining pads are in the west courtyard','Spawn practice direction missing')
check(signs.PracticeWayfinding=='MIC PRACTICE / AIM WEST, SPEAK, GO QUIET','Practice onboarding sign missing')
check(signs.ArenaWayfinding=='BEAM ARENA / PVP INSIDE RED LINES','Arena warning sign missing')
local quests={};for _,job in ipairs(result.jobs)do
 for _,id in ipairs(job.quests or {})do check(not quests[id],'Duplicate quest giver mapping');quests[id]=true end
 for _,station in ipairs(job.stations)do
  check(station.position.Y==3,'Compact job root elevation wrong')
  print(string.format('REACH|%s|%.6f|%.6f|%.6f|0',job.name,station.position.X,station.position.Y,station.position.Z))
 end
end
for _,id in ipairs({'garden','beach','delivery','nick','crowd','sprint','dodge','arena'})do check(quests[id],'Saved quest has no giver')end
for i,p in ipairs(result.seeds)do print(string.format('REACH|Seed%d|%f|3|%f|0',i,p[1],p[2]))end
for i,p in ipairs(Layout.Soccer.lost)do print(string.format('REACH|Lost%d|%f|%f|%f|8',i,p.X,p.Y,p.Z))end
for _,list in ipairs({Layout.Soccer.gates,Layout.Soccer.obstacles,Layout.Soccer.goals})do
 for _,p in ipairs(list)do check(p.X>=Layout.Soccer.min.X and p.X<=Layout.Soccer.max.X and p.Z>=Layout.Soccer.min.Z and p.Z<=Layout.Soccer.max.Z,'Soccer active point outside court')end
end
for _,p in ipairs(result.walk)do check(p.Y==3,'Compact walk root elevation wrong')end
check(#Layout.TrainingHomes==3 and Layout.TrainingHomes[1].x==-245 and Layout.TrainingHomes[1].z==-15 and Layout.TrainingHomes[3].z==-185,'Training home migration changed')
local function objective(name,position,radius)
 print(string.format('REACH|%s|%f|3|%f|%f',name,position.X,position.Z,radius or 0))
end
for i,home in ipairs(Layout.TrainingHomes)do objective('TrainerHome'..i,Vector3.new(home.x,3,home.z),8)end
for _,surface in ipairs({byName.HubPaving,byName.RouteToPractice})do
 check(byName.StandLine.Position.Y-byName.StandLine.Size.Y/2>surface.Position.Y+surface.Size.Y/2,'Practice stand line buried under paving')
end
check(byName.StandLine.Position.X==Layout.Practice.position.X and byName.StandLine.Position.Z==Layout.Practice.position.Z and byName.StandLine.Position.Y==.14 and not byName.StandLine.CanCollide and not byName.StandLine.CanQuery,'StandLine is not safe/aligned')
objective('PracticeStand',byName.StandLine.Position);objective('ArenaEntrance',byName.ArenaWayfinding.Position)
objective('SoccerOrigin',Layout.Soccer.origin)
for i,pos in ipairs(Layout.Soccer.gates)do objective('SoccerGate'..i,pos)end
for i,pos in ipairs(Layout.Soccer.goals)do objective('SoccerGoal'..i,pos)end
objective('VolleyServe',Layout.Volley.serve);objective('VolleyReturn',Vector3.new(Layout.Volley.center.X,3,Layout.Volley.netZ+16))
print('PASS '..checks..' actual compact module construction assertions')
'''
def execute(code):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False)as f:f.write(code);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],text=True,capture_output=True)
 finally:path.unlink()
 assert r.returncode==0,r.stdout+r.stderr
 return r.stdout

def reachability(output):
 parts=[];targets=[]
 for line in output.splitlines():
  items=line.split('|')
  if items[0]=='PART':parts.append((items[1],*[float(v)for v in items[2:8]],items[8]=='true'))
  elif items[0]=='REACH':targets.append((items[1],*[float(v)for v in items[2:]]))
 obstacles=[]
 for name,x,y,z,w,h,d,solid in parts:
  if solid and y+h/2>.6 and y-h/2<5.5:obstacles.append((x-w/2-1.5,x+w/2+1.5,z-d/2-1.5,z+d/2+1.5))
 def clear(x,z):return not any(a<=x<=b and c<=z<=d for a,b,c,d in obstacles)
 def segment_clear(x,z,xx,zz):
  for a,b,c,d in obstacles:
   low,high=0.,1.
   for origin,delta,minimum,maximum in ((x,xx-x,a,b),(z,zz-z,c,d)):
    if abs(delta)<1e-10:
     if origin<minimum or origin>maximum:low=2;break
    else:
     first,last=sorted(((minimum-origin)/delta,(maximum-origin)/delta));low=max(low,first);high=min(high,last)
   if low<=high:return False
  return True
 step=4;nx=180;nz=150
 free={(i,j) for i in range(nx)for j in range(nz)if clear(-358+i*step,-298+j*step)}
 start=(22,107);assert start in free,'Spawn blocked'
 visited={start};queue=collections.deque([start])
 while queue:
  i,j=queue.popleft()
  for node in ((i-1,j),(i+1,j),(i,j-1),(i,j+1)):
   if node in free and node not in visited and segment_clear(-358+i*step,-298+j*step,-358+node[0]*step,-298+node[1]*step):visited.add(node);queue.append(node)
 for name,x,y,z,radius in targets:
  reachable=False
  for i,j in visited:
   px,pz=-358+i*step,-298+j*step
   if math.dist((px,3,pz),(x,y,z))<=max(radius,3) and (radius or (clear(x,z) and segment_clear(px,pz,x,z))):
    reachable=True;break
  assert reachable,'Interactable/station unreachable in static clearance grid: '+name
 print('PASS',len(targets),'actual marker/station/lost-ball reachability targets over',len(visited),'connected clearance cells; not native pathfinding')
 return len(targets)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');p.add_argument('--baseline',action='store_true');args=p.parse_args()
 if args.baseline:
  layout=subprocess.check_output(['git','show','232b89285640fe601ca68d3626b85df142bda3c9:src/ReplicatedStorage/Shared/CompactLayout.luau'],text=True,cwd=ROOT)
  city=subprocess.check_output(['git','show','232b89285640fe601ca68d3626b85df142bda3c9:src/ServerScriptService/CompactCity.luau'],text=True,cwd=ROOT)
 assert 'CollectionService' not in city and 'CityDestructible' not in city,'Compact city imports destruction tagging'
 code=setup+layout+between+city+tests.replace('__RAY_POLICY__',policy)
 if args.baseline:
  try:execute(code)
  except AssertionError as e:assert 'First-minute guidance missing' in str(e);print('PASS expected baseline: first-minute guidance absent');raise SystemExit(0)
  raise AssertionError('Baseline unexpectedly has guidance')
 output=execute(code)
 print('\n'.join(line for line in output.splitlines()if line.startswith('PASS')));reachability(output)
 if args.negative_controls:
  for old,new,message in [
   ('position=V(-270,.10,97),size=V(8,.02,86)','position=V(-270,.10,95),size=V(8,.02,90)','Route rectangles have coplanar area overlap'),
   ('size=V(33,.02,8)','size=V(24,.02,8)','Route network lacks shared-edge connectivity'),
   ('p.CanQuery=false;p.CastShadow=false','p.CanQuery=true;p.CastShadow=false','Guidance physics/query/shadow enabled'),
   ('p.CanQuery=false;p.CastShadow=false','p.CanQuery=false;p.CastShadow=false;p.CanCollide=true','Guidance physics/query/shadow enabled'),
   ('p.CanQuery=false;p.CastShadow=false;p.Transparency=0','p.CanQuery=false;p.CastShadow=false;p.Transparency=1','Guidance invisible or emissive'),
   ('p.CanQuery=false;p.CastShadow=false','p.CanQuery=false;p.CastShadow=false;p:SetAttribute("QuestAction","Garden")','Guidance carries gameplay attributes'),
   ('position=V(-280.8,8,48)','position=V(-280.8,8,65)','Guidance obscures practice shot corridor'),
   ('position=V(-183,.10,50)','position=V(-175,.10,50)','Route crosses PvP threshold'),
   ('position=V(-245,.10,35.5)','position=V(-245,.10,27.5)','Route overlaps rookie eligibility pad'),
   ('V(Layout.Practice.position.X,.14,Layout.Practice.position.Z)','V(Layout.Practice.position.X,.05,Layout.Practice.position.Z)','Practice stand line buried under paving')]:
   assert code.count(old)==1,old
   try:execute(code.replace(old,new))
   except AssertionError as e:assert message in str(e),str(e);print('PASS negative control:',message)
   else:raise AssertionError('Guidance mutation accepted')
  for old,new,message in [('p:SetAttribute("MicPracticeTarget",true)','p:SetAttribute("WrongPractice",true)','Practice target wiring missing'),('position=V(x,3,z)','position=V(x,4,z)','Compact job root elevation wrong'),('p.Material=Enum.Material.SmoothPlastic','p:SetAttribute("DestructibleType","Test");p.Material=Enum.Material.SmoothPlastic','Compact geometry tagged for destruction'),('gui.MaxDistance=65','gui.MaxDistance=100000','Unbounded wayfinding GUI'),('minimumCrossingHeight=9.2','minimumCrossingHeight=10.2','Volley crossing clearance disagrees with visual net and ball radius'),('center=V(285,1.2,245.5)','center=V(285,2.2,245.5)','Soccer floor alignment changed'),('p.CanCollide=true;p:SetAttribute("MicPracticeTarget"','p.CanCollide=false;p:SetAttribute("MicPracticeTarget"','Practice target excluded by actual beam raycast policy')]:
   assert old in code
   try:execute(code.replace(old,new))
   except AssertionError as e:assert message in str(e);print('PASS negative control:',message)
   else:raise AssertionError('Mutation accepted')
  try:reachability(output+'\nPART|InjectedBarrier|-270|4|130|20|8|20|true')
  except AssertionError as e:assert 'Spawn blocked' in str(e);print('PASS negative control: blocked spawn')
  else:raise AssertionError('Blocked spawn accepted')

  try:reachability(output+'\nPART|InjectedTrainerBlock|-245|4|-15|24|8|24|true')
  except AssertionError as e:assert 'TrainerHome1' in str(e),str(e);print('PASS negative control: trainer approach blocked')
  else:raise AssertionError('Blocked trainer objective accepted')
