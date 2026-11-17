# Coastal districts, standalone v2.1

`DistrictCoast.luau` returns `function(build,id,spec)` supporting string IDs `03` and `10`. It uses only the agreed `build:part` and `build:disk` APIs, with world positions derived from `spec.center`, default district sizes from layout.json. Every generated part requests solid collision/query through the builder. No remote meshes, runtime systems or production edits.

Z03: 63 pieces. NW walk-up DJ stage, speaker towers and canopy; NE open market counters; SE circular dance deck; SW boardwalk seats/lamps. Stage entry uses1.2-stud steps.

Z10: 59 pieces. NW shallow reef mosaic and cyan shrine; NE open shell arch; SW six-step lookout with telescope; SE branching coral grove. These are playable POIs on the root platform, not separated swim islands or a simulated ocean. No secret rewards, swimming, NPCs or quests are claimed.

Inspected actual IMG_1526 master blueprint plus repo vault-derived Map10 art/flow reviews and current roadmap. Original simplified coastal visual language; not claimed illustration-exact or final dress.

Validation: actual Luau execution through `check_coast.luau` checks unique names, all-positive sizes, solid request,150-part cap, conservative rotated footprints outside the44-stud cross and inside the32-stud perimeter interior for both actual district specs. Both pass (63/59); production module compiles with luau-compile. Initial test caught a signed step-depth size; corrected to absolute size while preserving direction. Native traversal, rendered appearance and collision/query behavior of the external builder remain unverified. Builder must honor solid=true as CanCollide/CanQuery; root owns platform/fences/gates. No apps left open.

## Deep art rebuild after owner blockout rejection

Reinspected both actual reference images and DEB21437… whole-map gap render. The flat platforms and four small scattered objects did not deliver the intended map density. Z03 is now193 pieces: continuous timber precincts, dressed pitched stage canopy and backfins, stage light rig, merchant goods and striped awnings, a palm/pergola promenade, and dance pylons. Z10 is now141 pieces: layered limestone atoll strata, tall fossil ribs framing the shell gate, a broken-roof observatory colonnade around the reachable lookout, and a clustered fossil coral garden. Existing1.2-stud access steps remain; new architectural bodies are solid/queryable through the builder.

Repeated actual-module checker passes both zones with the updated240-part ceiling, unchanged44-stud cross/32-stud inner edge clearance, positive dimensions and unique names. Module compiles. This improves architectural mass, silhouette and coastal identity, but is still an original low-poly interpretation, not proof of finished-map visual acceptance. Whole-map render and native player-height traversal are still required; this update alone does not claim those. No Zone05 or other runtime file changes.
