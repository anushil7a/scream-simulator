"""Stdlib geometry regressions; not native physics/render acceptance.
Pass --baseline to measure pre-repair ce6902e, without writing shared source.
"""
import json,math,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
baseline='--baseline' in sys.argv
raw=subprocess.check_output(['git','show','ce6902e:prototypes/map10/geometry.json'],cwd=R,text=True) if baseline else (R/'prototypes/map10/geometry.json').read_text()
data=json.loads(raw);parts={p['id']:p for p in data['parts']}
def mat(q):
 a,b,c=map(math.radians,q['rotation']);ca,sa,cb,sb,cc,sc=math.cos(a),math.sin(a),math.cos(b),math.sin(b),math.cos(c),math.sin(c)
 return [[cb*cc+sb*sa*sc,-cb*sc+sb*sa*cc,sb*ca],[ca*sc,ca*cc,-sa],[-sb*cc+cb*sa*sc,sb*sc+cb*sa*cc,cb*ca]]
def point(q,v):
 m=mat(q);return [q['position'][i]+sum(m[i][j]*v[j] for j in range(3)) for i in range(3)]
checks=[]
def check(name,ok,detail):checks.append((name,bool(ok),detail))
for n,a,b,w in data['routes']:
 q=parts[n];h=q['size'][1]/2;l=q['size'][2]/2
 ends=[point(q,[0,h,-l]),point(q,[0,h,l])]
 # Flat bridge tops intentionally .08 above underlying plane to avoid z-fighting.
 lift=.08 if a[1]==b[1] else 0
 error=max(math.dist(actual,[target[0],target[1]+lift,target[2]]) for actual,target in zip(ends,[a,b]))
 check(n+' endpoint error',error<1e-6,round(error,6))
q=parts['GardenSpine'];left=q['position'][0]-q['size'][0]/2
check('No floating GardenSpine over descending ramp',left>=-190,left)
deck=[q for n,q in parts.items() if n in ('DockMain','DockCross','DockMainTail','DockCrossWestSeam','DockShelterPlatform')]
def rect(q):return (q['position'][0]-q['size'][0]/2,q['position'][0]+q['size'][0]/2,q['position'][2]-q['size'][2]/2,q['position'][2]+q['size'][2]/2)
overlap=0
for i,q in enumerate(deck):
 a,b,c,d=rect(q)
 for r in deck[:i]:
  e,f,g,h=rect(r);overlap+=max(0,min(b,f)-max(a,e))*max(0,min(d,h)-max(c,g))
check('Dock coplanar overlap area',overlap==0,overlap)
# District slab top faces must not occupy the same32-stud plane.
slabs=[q for n,q in parts.items() if n.startswith(('AcademyPlateau','AmphitheatrePlateau','VolcanoPlateau'))]
area=0
for i,q in enumerate(slabs):
 a,b,c,d=rect(q)
 for other in slabs[:i]:
  e,f,g,h=rect(other);area+=max(0,min(b,f)-max(a,e))*max(0,min(d,h)-max(c,g))
check('District coplanar slab overlap area',area==0,area)
old=[(-236,-204,420,630),(-235,195,594,626),(-280,-220,515,555)]
contains=lambda rects,x,z:any(a<=x<=b and c<=z<=d for a,b,c,d in rects)
changed=sum(contains(old,x+.5,z+.5)!=contains(list(map(rect,deck)),x+.5,z+.5) for x in range(-281,196) for z in range(419,631))
check('Dock walkable union preserved',changed==0,changed)
check('Dock shelter red roof, cream columns',all(q['color']==[180,79,61] for n,q in parts.items() if n.startswith('DockShelterRoof')) and all(q['color']==[239,219,172] for n,q in parts.items() if n.startswith('DockShelterColumn')),True)
# Vertical ray/OBB support on dense polar samples. Cylindrical shrine support
# uses its TRUE circular cross-section, not the old checker bounding rectangle.
solids=[(q,mat(q)) for q in parts.values() if q['collidable']]
def ground(x,z):
 top=-1e6
 for q,m in solids:
  pos=q['position'];half=[s/2 for s in q['size']]
  o=[sum((v-pos[j])*m[j][i] for j,v in enumerate((x,200,z))) for i in range(3)];dv=[-m[1][i] for i in range(3)]
  lo,hi=-1e9,1e9;valid=True
  for i in range(3):
   if abs(dv[i])<1e-8:
    if abs(o[i])>half[i]+1e-7:valid=False;break
   else:
    t1=(-half[i]-o[i])/dv[i];t2=(half[i]-o[i])/dv[i];lo=max(lo,min(t1,t2));hi=min(hi,max(t1,t2))
  if not valid or lo>hi+1e-7:continue
  if q.get('shape')=='Cylinder':
   hit=[o[i]+lo*dv[i] for i in range(3)]
   if (hit[1]/half[1])**2+(hit[2]/half[2])**2>1+1e-7:continue
  top=max(top,200-lo)
 return top
homes={'metronome':(-450,32,-300),'golem':(-440,0,350),'ignis':(350,32,-80),'leviathan':(420,0,420),'conductor':(350,64,-420)}
for n,(x,y,z) in homes.items():
 # 24=22 ring plus2-stud avatar margin. Central samples include moving body.
 bad=[];count=0
 for r in range(0,25,2):
  for angle in range(0,360,10):
   a=math.radians(angle);h=ground(x+r*math.cos(a),z+r*math.sin(a));count+=1
   if abs(h-y)>.5:bad.append((r,angle,round(h-y,3)))
 check(n+' radius22+2 floor support',not bad,{'samples':count,'failures':bad[:5]})
for name,ok,detail in checks:print(('PASS' if ok else 'FAIL'),name,detail)
if not baseline:assert all(c[1] for c in checks),'Map repair regression'
print(sum(ok for _,ok,_ in checks),'/',len(checks),'passed')
