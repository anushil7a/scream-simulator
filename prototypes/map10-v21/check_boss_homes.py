"""Read-only; reuses the project optional NumPy geometry checker. No files written."""
import sys,json,math,re,argparse,numpy as np
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from check_overworld import hits,rotation
parser=argparse.ArgumentParser(description="Analytic boss placement checks, not native physics")
parser.add_argument('--geometry',type=Path,default=BASE.parents[1]/'build/map21/overworld-geometry.json')
args=parser.parse_args();P=json.loads(args.geometry.read_text())['parts']
H={m[0]:(float(m[1]),float(m[2]),float(m[3]),m[4])for m in re.findall(r'(\w+)=\{x=(-?[\d.]+),y=(-?[\d.]+),z=(-?[\d.]+),district="(\d+)"', (BASE/'BossHomes.luau').read_text())}
assert set(H)=={'metronome','golem','ignis','leviathan','conductor'}
results={}
for n,(x,y,z,zone)in H.items():
 pts=np.array([(x+a,y+.5,z+b)for a in range(-36,37,2)for b in range(-36,37,2)if a*a+b*b<=36**2],float)
 dirs=np.tile([0.,-1,0],(len(pts),1));nearest=np.full(len(pts),np.inf);floorzones=np.full(len(pts),'',dtype=object);block=[];dist=[]
 for p in P:
  if not p['collidable']:continue
  ex=np.abs(rotation(p['rotation']))@(np.array(p['size'])/2);lo=np.array(p['position'])-ex;hi=np.array(p['position'])+ex
  if hi[1]>y+.5 and lo[1]<y+18:
   dist.append((math.hypot(max(lo[0]-x,0,x-hi[0]),max(lo[2]-z,0,z-hi[2])),p['id']))
  if hi[0]<x-37 or lo[0]>x+37 or hi[2]<z-37 or lo[2]>z+37:continue
  hit,t=hits(p,pts,dirs,np.full(len(pts),2));take=hit&(t<nearest);nearest[take]=t[take];floorzones[take]=p.get('zone',p['id'].split('/')[0])
  hit,t=hits(p,pts,-dirs,np.full(len(pts),17.5))
  if hit.any():block.append(p['id'])
 bad=np.where(~np.isfinite(nearest)|(abs(nearest-.5)>.12)|(floorzones!=zone))[0]
 results[n]={'home':[x,y,z],'district':zone,'radiusSampled':36,'floorSamples':len(pts),'badFloor':len(bad),'headroomBlockers':block,'nearestConservativeSolid':min(dist)}
 assert not len(bad) and not block and min(dist)[0]>=36,(n,results[n])
print(json.dumps(results,indent=2))
print('PASS 5045 same-district floor/headroom samples, radius36, current BossHomes data')
