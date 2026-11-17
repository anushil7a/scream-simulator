"""Static master-plan checks. Links describe topology, not authored bridge geometry."""
import json
from itertools import combinations
from math import hypot, radians, tan
from pathlib import Path

ROOT = Path(__file__).resolve().parent
layout = json.loads((ROOT / "layout.json").read_text())
zones = layout["districts"]
links = layout["plannedZone09Links"]
bounds = layout["boundsXZ"]
assert bounds == [-1600, 1600, -1600, 1600]
assert set(zones) == {f"{n:02}" for n in range(1, 11) if n != 9}
assert layout["arteryWidth"] == 32
edges = {frozenset(e) for e in links}
assert len(edges) == len(links) and all(len(e) == 2 and e <= zones.keys() for e in edges)

def extent(spec):
    x, y, z = spec["center"]
    w, d = spec["size"]
    assert w > 0 and d > 0 and 0 <= y <= 340
    return x-w/2, x+w/2, z-d/2, z+d/2

def connected(vertices, available_edges):
    seen = {next(iter(vertices))}
    while True:
        expanded = seen | {v for e in available_edges if e & seen for v in e}
        if expanded == seen:
            return expanded == vertices
        seen = expanded

extents = {key:extent(value) for key,value in zones.items()}
for (x0, x1, z0, z1) in extents.values():
    assert bounds[0] <= x0 < x1 <= bounds[1]
    assert bounds[2] <= z0 < z1 <= bounds[3]
for a,b in combinations(extents,2):
    x0,x1,z0,z1 = extents[a]
    u0,u1,v0,v1 = extents[b]
    assert min(x1,u1) <= max(x0,u0) or min(z1,v1) <= max(z0,v0), (a,b)
for edge in edges:
    assert connected(set(zones), edges - {edge}), f"Single point of failure: {edge}"

print("Nine district footprints in bounds; no pairwise footprint overlap.")
print("Zone 09 planning graph stays connected with any one link removed.")
print("Zone  Link   Center distance | Approx. walk time | Minimum rise run")
for a,b in links:
    x,y,z = zones[a]["center"]
    u,v,w = zones[b]["center"]
    steps = hypot(x-u,z-w)
    rise = abs(y-v) / tan(radians(layout["rampLimitDegrees"]))
    print(f"{a:>4}  {b:>4}      {steps:>7.1f} studs       {steps/16:>5.1f} sec             {rise:>5.1f} studs")
print("Center-distance timing is a lower bound, not a playable route measurement.")
