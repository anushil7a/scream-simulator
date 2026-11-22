"""Original Map10 island geometry. No third-party mesh/script imports."""
import math,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'prototypes/map10';O.mkdir(parents=True,exist_ok=True)
p=[]
sand=[209,173,118];cream=[239,219,172];rock=[156,119,80];teal=[58,158,145];grass=[104,153,69];dark=[44,40,57];purple=[119,62,167];gold=[242,173,68];water=[39,162,181]
def box(n,pos,size,c,solid=True,rot=None,material='SmoothPlastic',shape=None):
 p.append(dict(id=n,position=pos,size=size,color=c,collidable=solid,rotation=rot or [0,0,0],material=material,shape=shape))
def disk(n,x,y,z,r,h,c,solid=True):box(n,[x,y,z],[h,r*2,r*2],c,solid,[0,0,90],shape='Cylinder')
def octagon(n,x,z,r,y,h,c):
 disk(n,x,y-h/2,z,r,h,c)
def ramp(n,a,b,width=32,c=cream):
 dx,dy,dz=[b[i]-a[i] for i in range(3)];h=math.hypot(dx,dz);l=math.sqrt(h*h+dy*dy)
 # Offset by the transformed top normal: the TOP face, not its center,
 # meets both endpoint floors exactly. No protruding slope extension/lip.
 normal=[-dy*dx/(l*h),h/l,-dy*dz/(l*h)]
 center=[(a[i]+b[i])/2-normal[i] for i in range(3)]
 if abs(dy)<1e-8:center[1]+=.08 # reveal flat bridge surface above coplanar land
 box(n,center,[width,2,l],c,True,[-math.degrees(math.atan2(dy,h)),math.degrees(math.atan2(dx,dz)),0])
def ring(n,x,z,r,y,h,c,gaps=(),width=8,foundation=None):
 for i in range(8):
  if i in gaps:continue
  a=i*math.pi/4
  center_y=y+h/2+i*.007
  height=h
  if foundation is not None:
   height=center_y+h/2-foundation
   center_y=foundation+height/2
  box(n+str(i),[x+math.sin(a)*r,center_y,z+math.cos(a)*r],
      [2*r*math.tan(math.pi/8)+2,height,width],c,True,[0,math.degrees(a),0])
def pavilion(n,x,z,y,w=45):
 box(n+'Plinth',[x,y+.3,z],[w+6,.6,w+6],cream)
 for dx in [-w*.36,w*.36]:
  for dz in [-w*.36,w*.36]:box(n+f'Column{dx}{dz}',[x+dx,y+13,z+dz],[3,26,3],cream)
 box(n+'Roof',[x,y+28,z],[w+9,4,w+9],teal)
 for side in [-1,1]:box(n+'RoofSlope'+str(side),[x+side*w*.22,y+34,z],[w*.59,2,w+10],teal,True,[0,0,-side*22])
def tree(n,x,z,y,s=1):
 box(n+'Trunk',[x,y+8*s,z],[2.5*s,16*s,2.5*s],[115,83,48])
 for i in range(5):
  a=i*math.tau/5;box(n+'Palm'+str(i),[x+math.cos(a)*5*s,y+16*s,z+math.sin(a)*5*s],[15*s,2*s,4*s],grass,False,[0,-math.degrees(a),-12])
# Irregular contiguous island and visible stratified cliff silhouette, sea outside.
box('Sea',[0,-104,40],[1380,5,1440],water,False)
# Non-overlapping strips form an irregular shoreline. Deep offset facets sit below top.
for i,(l,r,north,south) in enumerate([(-550,-470,-450,430),(-470,-350,-520,480),(-350,-150,-540,510),(-150,80,-520,525),(80,300,-500,510),(300,460,-500,480),(460,530,-430,430)]):
 x=(l+r)/2;z=(north+south)/2
 box('IslandCore'+str(i),[x,-48,z],[r-l,96,south-north],sand)
 # Visible shoreline cliffs below traversal surface, faceted at different rotations.
 for j in range(int((r-l)/35)+1):
  cx=l+18+j*35
  for edge in [north,south]:
   box(f'CliffFacet{i}_{j}_{edge}',[cx,-50+(j%3)*3,edge],[39,87,29],rock if j%3==0 else sand,True,[0,(-1 if edge==north else 1)*(8+j%3*7),0])
for i,z in enumerate(range(-400,421,65)):
 for x in [-540,520]:box(f'SideCliff{x}_{i}',[x,-48,z],[36,90,70],sand if i%2 else rock,True,[0,(-1 if x<0 else 1)*(10+i%3*8),0])
def terrace(n,x0,x1,z0,z1,y,c,holes=()):
 rects=[(x0,x1,z0,z1)]
 for a,b,c0,d in holes:
  nxt=[]
  for l,r,t,u in rects:
   al,ar,at,au=max(l,a),min(r,b),max(t,c0),min(u,d)
   if al>=ar or at>=au:nxt.append((l,r,t,u));continue
   for q in [(l,al,t,u),(ar,r,t,u),(al,ar,t,at),(al,ar,au,u)]:
    if q[0]<q[1] and q[2]<q[3]:nxt.append(q)
  rects=nxt
 for i,(l,r,t,u) in enumerate(rects):box(n+str(i),[(l+r)/2,y/2,(t+u)/2],[r-l,y,u-t],c)
# Full terraces, not retained compact-city geometry.
terrace('AcademyPlateau',-520,-60,-500,-100,32,sand,[(-112,-68,-170,-100)])
# Sandstone plateau itself is walkable; no sheet over ramp notch.
terrace('CentralGardenTerrace',-250,190,-180,210,16,grass,[(58,102,150,210),(-250,-190,90,130)])
# Partition same-height district contacts instead of layering coplanar slabs.
terrace('AmphitheatrePlateau',-65,245,-495,-165,32,dark,[(-65,-60,-495,-165),(200,245,-275,-165)])
terrace('VolcanoPlateau',200,510,-275,135,32,dark,[(200,300,23,57)])
# Main gentle routes connect all terrace levels, exact endpoints used by QA.
routes=[('AcademyGarden',[-90,32,-170],[-90,16,-70],36),('GardenCoast',[80,16,150],[80,0,250],40),('GardenArena',[-190,16,110],[-290,0,110],36),('AcademyAmphitheatre',[-70,32,-330],[90,32,-330],32),('VolcanoBridgeNorth',[90,32,-190],[300,32,-180],28),('VolcanoBridgeSouth',[170,16,40],[300,32,40],30),('ShrineAscent',[450,32,-250],[450,64,-420],26),('ShrineApproach',[450,64,-420],[350,64,-420],28)]
for n,a,b,w in routes:ramp(n,a,b,w)
# Road ribbons and central switchback with planted islands.
for n,pos,sz in [('AcademySpine',[-300,32.13,-260],[350,.2,26]),('AcademyTraining',[-300,32.14,-400],[360,.2,26]),('GardenSpine',[-10,16.13,110],[360,.2,30]),('GardenNorth',[-30,16.14,-60],[320,.2,28]),('GardenWest',[-90,16.15,20],[28,.2,180]),('GardenEast',[100,16.16,25],[28,.2,180]),('CoastalWalk',[0,.12,420],[960,.2,36]),('CoastArena',[-430,.13,260],[30,.2,280]),('SportsApproach',[300,.14,240],[30,.2,320])]:box(n,pos,sz,cream,False)
# Academy open pavilions with readable fountain and training clear pads.
for i,(x,z,w) in enumerate([(-450,-460,44),(-300,-460,58),(-140,-460,44),(-490,-180,36)]):pavilion('AcademyPavilion'+str(i),x,z,32,w)
# Raise the sparring circles over the cream road and under the Rookie trail.
for i,x in enumerate([-420,-300,-180]):disk('TrainingPad'+str(i+1),x,32.185,-400,32,.15,[148,181,145],False)
disk('FountainBasin',-300,33,-300,19,2,cream);disk('FountainWater',-300,34.1,-300,16,.2,water,False);disk('FountainPedestal',-300,37,-300,3,6,cream);disk('FountainBowl',-300,40,-300,9,2,cream)
# Stadium: octagonal bowl, east entrance, clear central PvP square and static cover.
for k in range(5):ring('ArenaTier'+str(k),-330,120,112+k*7,k*3,3,[166+k*9,166+k*8,145+k*7],gaps=(2,))
box('ArenaFloor',[-330,.08,120],[180,.16,180],[190,178,141],False)
for n,pos,sz in [('N',[-330,.2,30],[180,.15,2]),('S',[-330,.2,210],[180,.15,2]),('W',[-420,.2,120],[2,.15,180]),('E',[-240,.2,120],[2,.15,180])]:box('PvPBoundary'+n,pos,sz,[191,80,67],False)
for i,(x,z) in enumerate([(-380,70),(-280,70),(-380,170),(-280,170)]):box('ArenaCover'+str(i),[x,3,z],[12,6,12],[126,120,102])
# The southern opening and the Academy bridge both reach the stage.
# Solid risers sit on the existing deck under the original seat tops.
for k,color in enumerate(([92,68,114],[99,73,123],[106,78,132],[113,83,140],[120,88,148])):
 ring('MusicTier'+str(k),90,-330,84+k*8,32+k*3,3,color,gaps=(0,6),foundation=32)
disk('MusicStage',90,32.3,-330,50,.6,[51,43,72]);disk('MusicNeonRing',90,32.65,-330,26,.1,[179,105,240],False)
for i,(x,z) in enumerate([(-30,-410),(90,-470),(210,-410)]):
 box('SpeakerTower'+str(i),[x,64,z],[28,64,18],dark)
 for h in [46,70,86]:disk('Speaker'+str(i)+str(h),x,h,z-9.3,8,1,purple,False);p[-1]['rotation']=[90,0,0]
for i in range(12):box('Equalizer'+str(i),[18+i*12,58+(i%4)*3,-456],[5,12+(i%4)*6,2],teal,False)
# Lava crust with safe18-radius boss center reserved; cosmetic lava is not damage.
for i in range(12):
 if i in (4,5):continue # Open southwest bridge gate, no rock over its landing.
 a=i*math.tau/12;x=355+math.cos(a)*125;z=-70+math.sin(a)*164
 box('VolcanicRidge'+str(i),[x,47+(i%3)*7,z],[40,40+(i%3)*14,40],[[39,35,45],[58,43,54],[72,49,53]][i%3],True,[i%3*9,math.degrees(a),-10+i%4*7])
for i,(x,z,sx,sz) in enumerate([(290,-100,14,100),(400,-15,14,130),(355,70,130,12),(330,-195,110,10)]):box('LavaFissure'+str(i),[x,32.2,z],[sx,.3,sz],[255,116,30],False,material='Neon')
disk('IgnisCraterPad',350,32.15,-80,32,.3,[69,57,64])
# Floating crystal shrine, connected elevated approach.
octagon('FloatingShrine',350,-420,68,64,14,[101,71,132])
for k in range(3):ring('ShrineTier'+str(k),350,-420,48-k*8,64+k*3,3,[152,104,187],gaps=(2,))
for i,(x,z,h) in enumerate([(350,-450,32),(307,-440,18),(385,-450,20)]):
 box('Crystal'+str(i),[x,78+h/2,z],[12,h,12],[179,102,223],False,[0,25,12],material='Neon')
# Market stalls and gardens not located on main corridor.
for i,(x,z) in enumerate([(-100,150),(-40,150),(20,150),(-150,-20)]):
 box('StallCounter'+str(i),[x,20,z],[22,8,10],rock)
 for dx in [-12,12]:box('StallPost'+str(i)+str(dx),[x+dx,24,z],[2,16,2],cream)
 box('StallCanopy'+str(i),[x,33,z],[28,3,18],[74,135,157])
for i,(x,z) in enumerate([(-490,-140),(-460,-140),(-430,-140)]):box('GardenBed'+str(i),[x,33.5,z],[20,3,22],[135,96,66]);box('Flowers'+str(i),[x,35.2,z],[17,.4,18],[213,139,162],False)
for i,(x,z,y) in enumerate([(-20,-10,16),(45,-5,16),(0,65,16),(150,95,16),(-470,250,0),(-460,410,0),(235,270,0),(390,260,0),(400,340,0),(230,355,0)]):tree('Palm'+str(i),x,z,y,1+(i%3)*.2)
# Lower sports lawn and southern beach/dock: local challenge dimensions preserved.
box('FootballLawn',[310,.08,300],[150,.16,120],grass,False)
for n,pos,sz in [('N',[310,.2,257.5],[112,.1,1]),('S',[310,.2,342.5],[112,.1,1]),('W',[254,.2,300],[1,.1,85]),('E',[366,.2,300],[1,.1,85]),('Half',[310,.2,300],[112,.1,1])]:box('PitchLine'+n,pos,sz,cream,False)
# A non-overlapping deck partition keeps the same union/approach/endpoints.
box('DockMain',[-220,-1.9,507],[32,4,174],rock) # z420..594
box('DockCross',[-20,-1.9,610],[430,4,32],rock) # z594..626
box('DockMainTail',[-220,-1.9,628],[32,4,4],rock) # original tail626..630
box('DockCrossWestSeam',[-235.5,-1.9,610],[1,4,32],rock) # main's1stud wider west edge
for i,x in enumerate(range(-220,211,35)):box('DockPile'+str(i),[x,-15,610],[5,30,5],rock)
box('DockShelterPlatform',[-258,-1.9,535],[44,4,40],rock) # remainder outside main x-280..-236
pavilion('DockShelter',-260,535,0,24)
for part in p:
 if part['id'].startswith('DockShelterRoof'):part['color']=[180,79,61]
box('BeachVolleySand',[80,.08,340],[70,.16,80],cream,False)

# Branching lava network deliberately outside the boss's clear eighteen-stud disk.
for i,(a,b) in enumerate([((290,-180),(315,-115)),((315,-115),(310,-40)),((310,-40),(280,25)),((310,-40),(335,0)),((335,0),(355,75)),((355,75),(415,90)),((415,90),(405,5)),((405,5),(393,-75)),((393,-75),(420,-135)),((420,-135),(395,-185))]):
 dx=b[0]-a[0];dz=b[1]-a[1]
 box('BranchLava'+str(i),[(a[0]+b[0])/2,32.45+i*.002,(a[1]+b[1])/2],[8,.35,math.hypot(dx,dz)+2],[255,99,12],False,[0,math.degrees(math.atan2(dx,dz)),0],material='Neon')
# Floating island's tapered dark mass and two hanging chain tethers.
for k in range(5):box('ShrineUnderFacet'+str(k),[350,46-k*6,-420],[88-k*14,6,88-k*14],[94-k*5,64-k*4,123-k*5],False,[0,45 if k%2 else 0,0])
for chain,(a,b) in enumerate([((205,51,-400),(302,62,-420)),((400,58,-225),(390,62,-370))]):
 for i in range(16):
  t=i/15;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t-math.sin(t*math.pi)*13;z=a[2]+(b[2]-a[2])*t
  for side in [-1,1]:
   box(f'Chain{chain}_{i}A{side}',[x+side*2.7,y,z],[1,1,7],dark,False)
   box(f'Chain{chain}_{i}B{side}',[x,y+.015,z+side*3],[6,1,1],dark,False)
# Organic garden islands edge the switchback without closing the route.
for i,(x,z) in enumerate([(-25,-20),(35,30),(-10,70),(140,-30)]):
 disk('GardenIsland'+str(i),x,16.3,z,21,.6,[121,166,79]);tree('GardenTree'+str(i),x,z,16.6,.7)

# Safe perimeter scenery, avoid invisible barriers. Coast recovery handled by existing bounds.
data={'parts':p,'routes':routes,'reference':'MAP-10_Master_Overworld_Blueprint.jpg','scope':'Original island replacement; no imported source geometry'}
(O/'geometry.json').write_text(json.dumps(data,indent=2))
lines=['-- Generated original Map10 geometry. Rebuild with tools/build_map10.py.','return {']
for q in p:
 vals=[f'id="{q["id"]}"',f'position=Vector3.new({",".join(map(str,q["position"]))})',f'size=Vector3.new({",".join(map(str,q["size"]))})',f'color=Color3.fromRGB({",".join(map(str,q["color"]))})',f'collidable={str(q["collidable"]).lower()}',f'rotation=Vector3.new({",".join(map(str,q["rotation"]))})',f'material="{q["material"]}"']
 if q['shape']:vals.append(f'shape="{q["shape"]}"')
 lines.append('{'+','.join(vals)+'},')
lines.append('}');(R/'src/ReplicatedStorage/Shared/Map10Geometry.luau').write_text('\n'.join(lines)+'\n')
print('Map10 original parts',len(p))
f=R/'src/ReplicatedStorage/Shared/CompactLayout.luau'
s=f.read_text();inline='-- MAP10_PARTS_BEGIN\nLayout.PartSpecs={\n'+'\n'.join(lines[2:-1])+'\n}\n-- MAP10_PARTS_END'
if '-- MAP10_PARTS_BEGIN' in s:s=re.sub(r'-- MAP10_PARTS_BEGIN.*?-- MAP10_PARTS_END',lambda _:inline,s,flags=re.S)
else:s=s.replace('Layout.PartSpecs=require(script.Parent.Map10Geometry)',inline)
f.write_text(s)
