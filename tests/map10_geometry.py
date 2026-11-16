"""Conservative static heightfield; no native Studio/clearance claim."""
import json,math,collections
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];data=json.loads((R/'prototypes/map10/geometry.json').read_text());parts=data['parts']
xs=np.arange(-600,601,5);zs=np.arange(-600,661,5);xx,zz=np.meshgrid(xs,zs,indexing='ij');orig=[xx.ravel(),np.full(xx.size,250.),zz.ravel()];height=np.full(xx.size,-1000.);normal=np.zeros(xx.size)
for q in parts:
 if not q['collidable']:continue
 a,b,c=np.radians(q['rotation']);Rx=np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]]);Ry=np.array([[np.cos(b),0,np.sin(b)],[0,1,0],[-np.sin(b),0,np.cos(b)]]);Rz=np.array([[np.cos(c),-np.sin(c),0],[np.sin(c),np.cos(c),0],[0,0,1]]);rot=Ry@Rx@Rz
 o=[sum((orig[j]-q['position'][j])*rot[j,i] for j in range(3)) for i in range(3)];d=-rot[1,:];half=np.array(q['size'])/2
 lo=np.full(xx.size,-1e8);hi=np.full(xx.size,1e8);valid=np.ones(xx.size,bool);axis=np.zeros(xx.size,int)
 for i in range(3):
  if abs(d[i])<1e-8:valid&=abs(o[i])<=half[i]
  else:
   t1=(-half[i]-o[i])/d[i];t2=(half[i]-o[i])/d[i];n=np.minimum(t1,t2);f=np.maximum(t1,t2);axis=np.where(n>lo,i,axis);lo=np.maximum(lo,n);hi=np.minimum(hi,f)
 y=250-lo;mask=valid&(lo<=hi)&(hi>=0)&(y>height)
 height[mask]=y[mask];normal[mask]=abs(rot[1,axis[mask]])
h=height.reshape(xx.shape);norm=normal.reshape(xx.shape)
def ij(x,z):return round((x+600)/5),round((z+600)/5)
def at(x,z):return float(h[ij(x,z)])
start=ij(-300,-260);seen={start:0};queue=collections.deque([start])
while queue:
 a,b=queue.popleft()
 for c,d in [(a+1,b),(a-1,b),(a,b+1),(a,b-1)]:
  if not(0<=c<len(xs) and 0<=d<len(zs)) or (c,d) in seen:continue
  if norm[c,d]<.7 or h[c,d]<-.5 or abs(h[c,d]-h[a,b])>2.5:continue
  seen[(c,d)]=seen[(a,b)]+5;queue.append((c,d))
targets={'spawn':(-300,32,-260),'trainer1':(-420,32,-400),'trainer2':(-300,32,-400),'trainer3':(-180,32,-400),'garden':(-460,32,-160),'market':(-40,16,120),'arena':(-330,0,120),'coast':(-220,0,420),'football':(310,0,300),'volley':(80,0,340),'pier':(180,0,610),'amphitheatre':(90,32,-330),'metronome':(-450,32,-300),'golem':(-440,0,350),'ignis':(350,32,-80),'leviathan':(420,0,420),'conductor':(350,64,-420),'DJ':(55,32,-190),'Tinker':(-40,16,118),'Kai':(350,0,390),'Lyra':(-150,32,-300)}
for n,a,b,w in data['routes']:
 for j,point in enumerate([a,b]):targets[n+str(j)]=tuple(point)
results={n:{'ground':round(at(x,z),2),'expected':y,'reachable':ij(x,z) in seen,'routeStuds':seen.get(ij(x,z))} for n,(x,y,z) in targets.items()}
print(json.dumps(results,indent=2));(R/'prototypes/map10/static_walk_checks.json').write_text(json.dumps({'method':'5stud OBB heightfield,step<=2.5,normalsY>=.7; no native or avatar radius proof','parts':len(parts),'reachableCells':len(seen),'targets':results},indent=2))
assert all(t['reachable'] and abs(t['ground']-t['expected'])<1 for t in results.values()),'Unreachable or misgrounded destination'
assert len(parts)<1000 and len({q['id'] for q in parts})==len(parts)
print('MAP10_STATIC_PASS')
