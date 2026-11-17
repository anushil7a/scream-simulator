"""Analytic geometry checks against exported authoring specs (not Roblox physics)."""
from collections import Counter
import json
from math import atan2, degrees, dist, hypot
from pathlib import Path
import numpy as np

data = json.loads((Path(__file__).resolve().parents[2]/"build/map21/geometry.json").read_text())
parts, routes = data["parts"], data["routes"]
by_id={p["id"]:p for p in parts}
solids = []
for p in parts:
    if not p["collidable"]:
        continue
    a,b,c = np.radians(p["rotation"])
    ax,bx,cx=np.cos([a,b,c])
    ay,by,cy=np.sin([a,b,c])
    rot=np.array([[bx,0,by],[0,1,0],[-by,0,bx]]) @ np.array([[1,0,0],[0,ax,-ay],[0,ay,ax]]) @ np.array([[cx,-cy,0],[cy,cx,0],[0,0,1]])
    solids.append((np.array(p["position"]), np.array(p["size"])/2, rot, p))

def ray(start, direction, length):
    start=np.array(start);direction=np.array(direction);winner=None
    closest=length
    for position,half,rot,p in solids:
        local=rot.T @ (start-position); step=rot.T @ direction
        lo,hi=0,closest
        axes = (0,) if p["shape"]=="Cylinder" else range(3)
        for axis in axes:
            if abs(step[axis]) < 1e-9:
                if abs(local[axis]) > half[axis]+1e-7:
                    lo,hi=1,0
                    break
            else:
                hits=sorted([(-half[axis]-local[axis])/step[axis],(half[axis]-local[axis])/step[axis]])
                lo,hi=max(lo,hits[0]),min(hi,hits[1])
        if lo>hi+1e-7:
            continue
        if p["shape"]=="Cylinder":
            d=step[1:]/half[1:];o=local[1:]/half[1:]
            a,b,c=d@d,2*d@o,o@o-1
            if a<1e-10:
                if c>1e-7:
                    continue
            else:
                disc=b*b-4*a*c
                if disc<0:
                    continue
                root=disc**.5
                lo,hi=max(lo,(-b-root)/(2*a)),min(hi,(-b+root)/(2*a))
        if lo<=hi+1e-7 and lo<closest:
            winner=p["id"];closest=lo
    return (closest,winner) if winner else None

rays = 0
def floor_at(x,y,z,tolerance=.18):
    global rays
    rays+=1
    answer=ray((x,y+6,z),(0,-1,0),12)
    assert answer and abs(6-answer[0])<=tolerance, (x,y,z,answer)

floor_at(420,48,-545)
floor_at(420,48,-680)
for r in routes:
    start,end=r["a"],r["b"]
    dx, dy, dz=np.subtract(end,start)
    horizontal=hypot(dx,dz)
    length=dist(start,end)
    assert r["width"] >= (8 if r["id"].startswith("LighthouseLoop") else 24) and degrees(atan2(abs(dy),horizontal))<=32
    across=np.array([dz/horizontal,0,-dx/horizontal])
    for t in np.linspace(0,1,max(2,int(length/2))):
        center=np.array(start)+t*np.array([dx,dy,dz])
        for offset in (-r["width"]/2+2,0,r["width"]/2-2):
            floor_at(*(center+offset*across))
    print(f"{r['id']}: {length:.1f} studs, {degrees(atan2(abs(dy),horizontal)):.1f}°, {r['width']:.0f} wide")

pillars=[p for p in parts if "ArenaPillar" in p["tags"]]
assert len(pillars)==8
for p in pillars:
    x,y,z=p["position"]
    assert abs(hypot(x-420,z+680)-75)<.001 and y==58
    assert p["collidable"] and p["shape"]=="Cylinder" and p["size"]==[20,8,8]
    direction=((x-420)/75,0,(z+680)/75)
    for elevation in (49,55,67):
        rays+=1
        hit=ray((420,elevation,-680),direction,85)
        assert hit and hit[1]==p["id"] and abs(hit[0]-71)<.01, (hit,p["id"])
    rays+=1
    assert ray((420,69,-680),direction,83) is None
assert len([p for p in parts if "ResonanceBell" in p["tags"]])==3
assert len(by_id)==len(parts) and len(parts)<=750
print(f"PASS: {rays} analytic width/floor/cover probes; {len(parts)} parts; {len(solids)} solid/queryable.")
