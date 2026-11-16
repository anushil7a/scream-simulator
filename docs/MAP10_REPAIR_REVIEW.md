# Map10 concrete placement repairs (local candidate)

Base ce6902e; original Map10 blueprint and prior vault make-map/flow/arena guidance applied. No boss homes, quest destinations, guide IDs, sport dimensions, saved state or archived original changed. No upload/publication.

## Reproduced / corrected

- Academy/amphitheatre and amphitheatre/volcano slabs duplicated6600square studs of visible Y32 top faces. Partitioned the amphitheatre slabs around the other two districts; identical walkable union, no coplanar overlap.
- Dock Main/Cross/Shelter top faces duplicated1632square studs. Partitioned into abutting rectangles, including the original one-stud west edge and four-stud southern tail. The exact original deck union is retained at Y.1.. Piles, shelter, lanterns and joints retained.
- GardenSpine flat road extended40studs west across the descending arena ramp notch, appearing to float above walkers. Shortened the cosmetic ribbon to the ramp's exact upper endpointX-190; actual collision route unchanged.
- Ramp generation centered a two-stud slab at-.92Y and added3studs of length. Thus top endpoints protruded1.5–1.67studs beyond intended endpoints and sloped transitions had a small step. New placement subtracts the transformed top-face normal and uses exact segment length. Sloped top endpoints now match specified points; flat bridges retain deliberate .08stud reveal to avoid coplanarity where crossing district slabs.
- Dock shelter recoloring accidentally selected a COLUMN rather than roof. All three roof pieces now original-reference terracotta; columns restoredcream.

604 base geometry parts, unchanged1028 cosmetic finish parts. Collision changes are bounded slab partitioning and corrected ramp contacts, not global flattening or removed structures. The shoreline remains an elevated cliff with safe existing deck connection, not a newly accessible sea-level beach; no false walkable water surface introduced.

## Evidence

`python tests/map10_repairs.py --baseline` measures ce6902e:6/18checks pass (floor/union checks already passed),12 reproduce defects. Current18/18pass. Saved outputs `prototypes/map10/repair_before.txt` / `repair_after.txt`.

- Exact transformed endpoint tests, coplanar slab/deck overlap area, original deck union comparison at1stud cells.
- Radius22 plus2stud margin:468polar floor samples per boss,2340total, all flat within.5stud. Actual cylindrical shrine support is used rather than a bounding rectangle. Combined with prior rotated footprint audit (closest shrine solid28studs away), inner≤4stud patrol plus≤10stud total visual envelope fits unchanged homes. Engagement limits must remain HOME-centered, not moving-core-centered.
-671Map10 contracts;10actual grounding decisions;1028finish props check;5stud static walk/endpoint checker pass.

Static geometry/synthetic checks do not establish continuous avatar pathfinding, streaming, physical device performance or native visual acceptance. Next: disposable Studio checks of garden ramp, academy/amphitheatre seam, diagonal volcano bridges, shrine turn and dock shelter deck, plus boss patrol/attack boundaries at22. Blender review renders, if produced, are proxies, not Roblox evidence.

Blender quick review: `build/map10-finish/RepairGarden.png` and `RepairDock.png` personally inspected; garden road now meets ramp without floating extension, dock roof is terracotta and deck connection remains continuous. Paired `BeforeGarden.png`/`BeforeDock.png` use the same cameras with base geometry. These are static Cycles proxies with low-sample noise; no native rendering claim.
