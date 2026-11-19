"""Analytic Academy fit checks against the exported overworld, not native play evidence."""
import argparse
import itertools
import json
import re
from pathlib import Path
import numpy as np
from check_overworld import hits

BASE = Path(__file__).resolve().parent
VEC = r"\{\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\}"
DOWN = np.array([[0., -1., 0.]])

def coords(source, name):
    match = re.search(r"\b"+name+r"\s*=\s*"+VEC, source, re.I)
    assert match, f"Could not read runtime coordinate for {name}"
    return np.array(tuple(map(float, match.groups())))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometry",type=Path,default=BASE.parents[1]/"build/map21/academy-overworld-geometry.json")
    args=parser.parse_args()
    data=json.loads(args.geometry.read_text())
    parts=[p for p in data["parts"] if p["collidable"] and p["zone"]=="01"]
    source=(BASE/"AcademyRouteRules.luau").read_text()
    # Station vectors (spawn is at the same district center consumed by the overworld host).
    anchor={
        "spawn":np.array(data["districts"]["01"]["center"]),
        "target":coords(source,"AcademyTrainTarget"),
        "mentor":coords(source,"AcademyMentor"),
        "entry":coords(source,"AcademyMetronomeEntry"),
        "gear":coords(source,"AcademyGear"),
    }
    # Training target center is elevated; use the known Academy terrain plane.
    feet={name:np.array([p[0],anchor["spawn"][1],p[2]]) for name,p in anchor.items()}
    total=0
    for name,p in feet.items():
        start=np.array([p+[dx,4.,dz] for dx,dz in itertools.product((-2.,0.,2.),repeat=2)])
        ds=np.tile(DOWN,(len(start),1))
        best=np.full(len(start),np.inf)
        ceil=start-[0,3.5,0]
        for part in parts:
            ok,t=hits(part,start,ds,np.full(len(ds),8))
            best=np.where(ok,np.minimum(best,t),best)
            obstruction,_=hits(part,ceil,-ds,np.full(len(ds),8.))
            assert not any(obstruction), (name,"ceiling",part["id"])
        assert np.all(abs(best-4)<.15), (name,"floor",best)
        total+=2*len(start)
    lanes=[("spawn","target"),("spawn","mentor"),("mentor","entry"),("entry","mentor"),("mentor","gear")]
    for a,b in lanes:
        for h in (1.,2.75,5.25):
            d=feet[b]-feet[a]
            unit=d/np.linalg.norm(d)
            side=np.array([unit[2],0.,-unit[0]])
            origins=np.array([feet[a]+[0,h,0]+side*w for w in (-1.4,0.,1.4)])
            dirs=np.tile(unit,(len(origins),1))
            for p in parts:
                ok,_=hits(p,origins,dirs,np.full(len(origins),np.linalg.norm(d)))
                assert not any(ok),(a,b,h,"lane blocked",p["id"])
            total+=len(origins)
    entry=feet["entry"]
    boss=coords((BASE/"BossHomes.luau").read_text(),"metronome")
    assert np.linalg.norm(entry-boss)<=22.,("guide entry outside encounter",entry)
    target_delta=anchor["target"]-(anchor["spawn"]+[0.,4.5,0.])
    assert np.linalg.norm(target_delta)<=30.,target_delta
    assert np.linalg.norm(entry-boss)<=14.,("guide stopping margin below 8 studs",entry)
    print(f"PASS {total} Academy floor/headroom/lane probes; guide endpoint within the 22-stud Metronome ring")

if __name__=="__main__": main()
