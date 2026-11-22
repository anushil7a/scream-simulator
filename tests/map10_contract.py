"""Stdlib-only active Map10 contract checks. Geometry/engine QA is separate."""
import json,re,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];layout=(R/'src/ReplicatedStorage/Shared/CompactLayout.luau').read_text();old=(R/'prototypes/preserved-compact-city/CompactLayout.luau').read_text();geometry=json.loads((R/'prototypes/map10/geometry.json').read_text());parts=geometry['parts'];checks=0
def check(v,m):
 global checks
 assert v,m;checks+=1
check('MapId="Map10"' in layout,'active identity');check('require(script.Parent.Map10Geometry)' not in layout,'inline harness compatibility')
ids=lambda s:set(re.findall(r'id="([^"]+)",action=',s))
check(ids(layout)==ids(old),'quest IDs preserved')
check(len(parts)<1000,'static budget');check(len({p['id'] for p in parts})==len(parts),'unique geometry IDs')
for n,a,b,w in geometry['routes']:
 check(w>=26,n+' width');check(abs(a[1]-b[1])/math.hypot(a[0]-b[0],a[2]-b[2])<=.2,n+' grade')
for token in ['AcademyPavilion','ArenaTier','MusicTier','BranchLava','FloatingShrine','Chain','FootballLawn','DockMain','CliffFacet']:
 check(any(p['id'].startswith(token) for p in parts),'reference motif '+token)
check('Layout.ZoneMax=V(-240,14,210)' in layout,'safe upper terrace outside PvP')
check('position=V(-220,2,420)' in layout and 'position=V(220,2,420)' in layout,'unchanged440stud timed sprint')
for name,offset in [('Soccer',(25,54.5)),('Volley',(100,90))]:
 l=next(x for x in layout.splitlines() if x.startswith('Layout.'+name+'='));o=next(x for x in old.splitlines() if x.startswith('Layout.'+name+'='));vs=lambda t:[tuple(map(float,v.split(','))) for v in re.findall(r'V\(([^)]+)\)',t)];new=vs(l);prev=vs(o)
 check(len(new)==len(prev),name+' vectors preserved')
 for a,b in zip(new,prev):check(abs(a[0]-b[0]-offset[0])<.001 and a[1]==b[1] and abs(a[2]-b[2]-offset[1])<.001,name+' rigid relocation')
for q in parts:check(all(math.isfinite(v) for v in q['position']+q['size']+q['rotation']) and min(q['size'])>0,q['id']+' finite')
rules=(R/'src/ReplicatedStorage/Shared/TrainingRules.luau').read_text()
radius=int(re.search(r'local Training=\{Radius=(\d+)',rules).group(1))
homes=[tuple(map(int,m)) for m in re.findall(r'\{x=(-?\d+),y=(-?\d+),z=(-?\d+)\}',next(l for l in layout.splitlines() if l.startswith('Layout.TrainingHomes=')))]
by_id={part['id']:part for part in parts}
coast_ramp=by_id['GardenCoast']
west=by_id['CentralGardenTerrace0']
east=by_id['CentralGardenTerrace3']
west_edge=west['position'][0]+west['size'][0]/2
east_edge=east['position'][0]-east['size'][0]/2
ramp_x,_,_=coast_ramp['position']
half_width=coast_ramp['size'][0]/2
check(coast_ramp['collidable'] and coast_ramp['rotation'][1:]==[0,0]
      and (ramp_x-half_width,ramp_x+half_width)==(west_edge,east_edge),
      'Coast ramp leaves a lateral seam or overlaps its terrace walls')
for code in (layout,(R/'src/ReplicatedStorage/Shared/Map10Geometry.luau').read_text()):
 row=next(line for line in code.splitlines() if line.startswith('{id="GardenCoast"'))
 check('size=Vector3.new('+','.join(map(str,coast_ramp['size']))+')' in row
       and 'collidable=true' in row,'Coast ramp runtime and preview support differ')
sea=by_id['Sea']
water=[p for p in parts if p['id']=='Sea' or p['id'].startswith('SeaHorizon')]
check(len(water)==9,'Pier sea ends at the inner tile')
for tile in water:
 check(not tile['collidable'] and tile['position'][1]==sea['position'][1]
       and tile['size'][1]==sea['size'][1] and tile['color']==sea['color'],'Sea tile changes shoreline or collision')
 check(tile['size'][0]<=2048 and tile['size'][2]<=2048,'Sea tile exceeds native part size limit')
def water_at(x,z):
 return any(abs(x-p['position'][0])<=p['size'][0]/2 and abs(z-p['position'][2])<=p['size'][2]/2 for p in water)
for x in (-2600,-690.001,-690,-689.999,689.999,690,690.001,2600):
 for z in (-2600,-680.001,-680,-679.999,759.999,760,760.001,2600):
  check(water_at(x,z),'Gap between sea tiles')
finish=json.loads((R/'prototypes/map10/finish_geometry.json').read_text())
cap=next(p for p in finish['parts'] if p['id']=='CoastPileCap12')
pile=by_id['DockPile12']
check(cap['position'][::2]==pile['position'][::2] and not cap['collidable'],
      'Outside pier cap must sit on its support without blocking the route')
pile_top=pile['position'][1]+pile['size'][1]/2
check(-.5<=cap['position'][1]-cap['size'][1]/2-pile_top<=0,
      'Outside pier cap must meet the top of its support')
for index,(x,y,z) in enumerate(homes,1):
 name=f'TrainingPad{index}'
 part=by_id[name]
 check(part['shape']=='Cylinder' and part['rotation']==[0,0,90] and part['size'][1:]==[2*radius,2*radius],name+' must show the sparring circle')
 check(part['position'][0]==x and part['position'][2]==z and not part['collidable'],name+' art moved or changed collision')
 top=part['position'][1]+part['size'][0]/2
 road=by_id['AcademyTraining']
 check(road['position'][1]+road['size'][1]/2<top<y+.285,name+' needs clearance between paving and Rookie trail')
 for source in (layout,(R/'src/ReplicatedStorage/Shared/Map10Geometry.luau').read_text()):
  row=next(line for line in source.splitlines() if line.startswith('{id="'+name+'"'))
  check('shape="Cylinder"' in row and 'size=Vector3.new('+','.join(map(str,part['size']))+')' in row,name+' runtime and preview differ')
tiers={part['id']:part for part in parts if part['id'].startswith('MusicTier')}
check(set(tiers)=={f'MusicTier{row}{segment}' for row in range(5) for segment in (1,2,3,4,5,7)},
      'Amphitheatre must leave the west and south bays open')
runtime=(R/'src/ReplicatedStorage/Shared/Map10Geometry.luau').read_text()
for name,part in tiers.items():
 row,segment=map(int,name[-2:])
 x,y,z=part['position']
 width,height,depth=part['size']
 yaw=math.radians(part['rotation'][1])
 check(part['collidable'] and math.isclose(y-height/2,32,abs_tol=1e-6),name+' must meet the deck')
 check(math.isclose(y+height/2,35+row*3+segment*.007,abs_tol=1e-6),name+' seat height changed')
 yaw_x=abs(math.cos(yaw))*width/2+abs(math.sin(yaw))*depth/2
 yaw_z=abs(math.sin(yaw))*width/2+abs(math.cos(yaw))*depth/2
 check(x+yaw_x<-70 or x-yaw_x>90 or z+yaw_z<-346 or z-yaw_z>-314,
       name+' blocks the Academy bridge')
 for code in (layout,runtime):
  text=next(line for line in code.splitlines() if line.startswith('{id="'+name+'"'))
  check('position=Vector3.new('+','.join(map(str,part['position']))+')' in text and
        'size=Vector3.new('+','.join(map(str,part['size']))+')' in text,name+' runtime and preview differ')
for code in (layout,runtime):
 check(not re.search(r'id="MusicTier[0-4][06]"',code),'runtime Amphitheatre entrance blocked')
housing=by_id['EqualizerHousing']
face=by_id['EqualizerFace']
stage=by_id['MusicStage']
check(housing['collidable'] and not face['collidable'],'Only the housing should be solid')
deck=stage['position'][1]+stage['size'][0]/2
x,y,z=housing['position']
width,height,depth=housing['size']
check(math.isclose(y-height/2,deck,abs_tol=1e-6),'Equalizer housing must sit on the stage')
check(z+depth/2<-346,'Equalizer housing blocks the west approach')
for dx in (-width/2,width/2):
 for dz in (-depth/2,depth/2):
  check(math.hypot(x+dx-stage['position'][0],z+dz-stage['position'][2])<stage['size'][1]/2,
        'Equalizer corner hangs off the stage')
fx,fy,fz=face['position']
fw,fh,fd=face['size']
check(math.isclose(fz-fd/2,z+depth/2,abs_tol=1e-6),'Equalizer face is detached from its housing')
check({p['id'] for p in parts if p['id'].startswith('Equalizer')}==
      {'EqualizerHousing','EqualizerFace',*(f'EqualizerBar{i}' for i in range(12))},
      'Unexpected equalizer geometry')
for i in range(12):
 name=f'EqualizerBar{i}'
 bar=by_id[name]
 bx,by,bz=bar['position']
 bw,bh,bd=bar['size']
 check(not bar['collidable'] and math.isclose(bz-bd/2,fz+fd/2,abs_tol=1e-6),name+' is solid or floating')
 check(abs(bx-fx)+bw/2<fw/2 and abs(by-fy)+bh/2<fh/2,name+' exceeds its display face')
for source in (layout,runtime):
 for part in (housing,face,*(by_id[f'EqualizerBar{i}'] for i in range(12))):
  entry=next(line for line in source.splitlines() if line.startswith('{id="'+part['id']+'"'))
  check('position=Vector3.new('+','.join(map(str,part['position']))+')' in entry and
        'size=Vector3.new('+','.join(map(str,part['size']))+')' in entry and
        'collidable='+str(part['collidable']).lower() in entry,part['id']+' runtime and preview differ')
for tower_index in range(3):
 tower=by_id[f'SpeakerTower{tower_index}']
 tower_x,_,tower_z=tower['position']
 front_z=tower_z+tower['size'][2]/2
 for height in (46,70,86):
  name=f'Speaker{tower_index}{height}'
  cone=by_id[name]
  x,y,z=cone['position']
  depth,width,rim_height=cone['size']
  check(cone['shape']=='Cylinder' and not cone['collidable'],name+' is decorative cylinder')
  check(cone['rotation']==[0,-90,0],name+' axis must face the audience (+Z)')
  check(x==tower_x and y==height and width==rim_height==16 and depth==1,name+' silhouette changed')
  check(math.isclose(z-depth/2,front_z-.1,abs_tol=1e-6),name+' is recessed or floating away from tower')
  for source in (layout,runtime):
   entry=next(line for line in source.splitlines() if line.startswith('{id="'+name+'"'))
   for field in ('position','size','rotation'):
    check(field+'=Vector3.new('+','.join(map(str,cone[field]))+')' in entry,name+' runtime and preview '+field+' differ')
   check('shape="Cylinder"' in entry and 'collidable=false' in entry,name+' runtime flags differ')
world=(R/'src/ServerScriptService/World.luau').read_text();check('(training.y or 0)+3.2' in world,'trainer grounding');check('nil,nil,spot.y' in world,'seed elevation');check('SupportingNPCs.AtHome' in world,'support placement adapter')
nav=(R/'src/ReplicatedStorage/Shared/NavigationCatalog.luau').read_text();check('(boss.y or 0)+3' in nav and '(landmark.y or 0)+3' in nav,'elevated guides')
check('home=Layout.BossHomes' in (R/'src/ReplicatedStorage/Shared/BossCatalog.luau').read_text(),'boss bindings')
print('PASS',checks,'Map10 contract checks (no native claims)')
