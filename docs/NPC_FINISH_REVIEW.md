# NPC costume finishing · November 16

Appearance-only follow-up from `664b8ae`. Actual vault pixels reviewed: NPC-05 DJ Marina, NPC-07 Tinker Sparks, NPC-08 Lifeguard Kai, NPC-09 Archivist Lyra. Relevant vault guidance: Character and Creature Pipeline, Shape Language and Silhouette Testing, Modeling in Blender for Roblox. Stable skeleton, animation, root height and behavior are the contract; costume layers are the only change.

## Runtime result

- Marina: cyan jacket lapels/cuffs, inset dark pockets, side braid and central deck fader.
- Sparks: leather-tone harness webbing, brass buckles, utility pouches and dark inset goggle lenses. Existing twin speaker pack stays.
- Kai: dark vest straps and zipper, cream rescue buckles, brass whistle and teal short panels.
- Lyra: gold stole/borders, tuning clasp, split per-leg coat tails and pale book pages. Per-leg tails do not bridge hip joints.
- Rookie/Brawler/Elite: navy chest seams, ivory knee pads and boot welts, rank patch and inset belt buckle. Existing mint/coral/gold tier identity remains.

Support costume totals are exactly 15/19/14/15 Parts respectively. Trainer kit totals exactly 16 Parts plus 16 WeldConstraints each. Parts use established bounded, massless, unanchored, noncolliding/nonquery/nontouch accessory construction. No new scripts, loops, joints, hitboxes, random draws or remotes. Role IDs, routes, position mapping, quests, dialogue, faces and ordinary worker fallbacks unchanged. No UI or enemy-health change.

These are original native-part runtime costumes, not a claim that exported FBX files have been installed as live Roblox MeshParts. The runtime visual improvement does not depend on uploads or external asset IDs. SmoothPlastic retained deliberately: earlier project-native Fabric trial was rejected as muddy at gameplay distance.

## Preview and validation

`tools/supporting_npc_models.py` now extracts all seven actual costume definitions, with `tools/trainer_preview_geometry.py` extracting the production trainer function. Outputs in `build/supporting-npcs`: seven FBX/GLB look packages, SupportingResidents.blend, manifest.json, roster.png, roster-back.png. These are static costume previews with neutral body/head proxies (not full rigs, existing facial/headwear detail or animation). Small preview bevels and Blender lighting are not evidence of native Roblox shading. The original game rig/faces remain untouched. Front/back renders inspected for silhouette and attachment placement.

- Supporting roster/route/appearance: 262 mocked assertions plus append-only and quest-context contracts.
- Trainer constructor differential: 710,898 synthetic safety/property assertions and eight negative controls. All original noncosmetic hierarchy, RNG and behavior compared with prior baseline.
- Full `verify_local.py --build`: 26 pure/synthetic +147 mocked suites, production compiles and local guarded builds pass. Strengthened support signature/count check separately passes after aggregate.
- No Studio/live voice, representative phone, multiplayer, collision dynamics or native animation verification claimed. Next native gate: walk-up and rear three-quarter views, arm swing/dodge/recovery, Lyra coat/leg separation, deck clearance, role readability at 40 studs, all seven original faces intact.

No application window opened, no Roblox upload, no publication and no external push.

## Incremental authored-worker finish

A separate follow-up adds exactly two torso-welded details to each of seven existing authored job roles: cafe apron pocket/seam, sanitation reflective stripe/utility pocket, beach badge inset/pocket, busker guitar bridge/pick pocket, gardener seed pouch/flap, artist smock pocket/paint mark, and soccer jersey side piping. No worker faces, carried-tool geometry or animation state changes. Seeded ordinary residents without jobs, support Local/Vendor roles, and trainers receive none of this helper's geometry. Seven supported jobs add fourteen Parts and fourteen welds total.

Actual constructor differential now passes 714,218 assertions and eight existing negative controls; additional checks cover exact worker count, authored-job gating, dimensions, SmoothPlastic/Residents flags, massless noncollision and torso weld attachment. Production World compiles. This incremental pass has focused validation, not a new full aggregate/native visual claim; root integration should run its aggregate gate.
