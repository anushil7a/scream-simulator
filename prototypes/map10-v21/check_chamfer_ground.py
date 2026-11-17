"""Reject grounded structures left over an intentionally removed terrace corner."""
import json
import numpy as np
from check_overworld import ROOT, rotation

source=json.loads((ROOT/"build/map21/overworld-geometry.json").read_text())
count=0
for key,spec in source["districts"].items():
    if key=="05":  # Foundry carries the pre-existing ramp notch and islet.
        continue
    _,y,_=spec["center"]
    sector=[p for p in source["parts"] if p["zone"]==key]
    ground=[p for p in sector if "/DistrictGround_" in p["id"]]
    assert len(ground)>=3, (key,"missing chamfer supports")
    for p in sector:
        flags=set(p["tags"])
        if not p["collidable"] or "SolidObstacle" not in flags or flags & {"GateRail","CliffReturn","CoastalCliff"}:
            continue
        px,py,pz=p["position"]
        ex,ey,ez=np.abs(rotation(p["rotation"])) @ (np.array(p["size"])/2)
        if py-ey>y+.8 or py+ey<y+.2:
            continue
        for cx,cz in [(px+ix*ex,pz+iz*ez) for ix in (-1,1) for iz in (-1,1)]:
            assert any(abs(cx-g["position"][0]) <= g["size"][0]/2+.1
                       and abs(cz-g["position"][2]) <= g["size"][2]/2+.1 for g in ground), p["id"]
        count+=1
print(f"PASS {count} grounded structure envelopes supported by clipped terrace floors.")
