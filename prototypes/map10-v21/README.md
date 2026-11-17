# MAP-10 v2.1 | Tidal Bell-Foundry test slice

## Enter the preview

Open `Map10V21FoundryReview.rbxl` as a **local Roblox Studio file**, then press **Play**. The district is generated at Play startup. This is a walkable environment review, not a copy of the live game; it has no real progression, saves, quests, beam controls or active boss. Nothing in `src/` references it.

- **Spawn / arena:** Start on the Y48 plaza. Straight ahead is a Ø190 arena with eight solid Ø8 × 20-stud cover pillars, on a 75-stud radius. The center is a reserved boss pad, not an active boss. Cross the arena before projecting a fight: the current production beam reaches only 30–54.75 studs, and boss range is independently gated. Larger combat reach is not implied.
- **Lighthouse:** Head east toward the cyan spire. The arched 32-stud causeway crosses to its own rocky islet. Walk around the tower base rather than through it. The 180-stud silhouette is measured from the Y48 floor. The crystal is fixed in the current preview; treat rotation as a later cosmetic polish item.
- **Foundry:** The north end holds three bronze gantries with hanging bells. The bells are tagged markers and decorative art, not functioning beam targets yet. Avoid adding invisible gameplay blockers merely to make placeholder bells shootable.
- **Dock:** Head south from the plaza to the pier. The two 40-stud ramp lanes descend Y48 → Y36 → Y24; both are about 14°. The foundation reaches down to Y14, not a walkable Y14 tier. This preview's piers turn back within the district; outward links are part of the master network plan, not built geometry.
- **Sound:** Quiet dock/lighthouse cues are positional packaged placeholders, only enabled if the client loads them. The local control mutes them. The clip design and actual audibility are not established by script checks alone.
- **Props:** The separate editable Blender file and four GLBs are original optional replacements. Roblox-native primitive art is currently in the walkable place, not uploaded or remotely dependent. The GLBs have individually validated triangle counts under 1,500.

## Layout and tradeoffs

`layout.json` records the owner's 3,200-stud envelope, nine district footprints and a proposed loop network; the network is the tenth zone. Main elevation bands: coast (Y0–22), raised city (Y48–65), colosseum (Y115), rift (Y175), sky (Y340). The current draft does not yet contain the other districts in Studio.

The rectangular district envelopes do not overlap. Most neighboring **centers** exceed the intended 450–650-stud pacing, so cut route checks at actual gates and add sightline cues or meaningful sub-POIs during the next walk. The current game is 16 studs/sec walking, 25 sprinting with a 10-second sprint budget; a 450–650 stud walk is roughly 28–41 seconds before detours. Do not commit to new speeds or quest times to hit a paper target.

The 256/896 streaming radii are deliberate **preview test settings**, not production or mobile recommendations. [Roblox streaming guidance](https://create.roblox.com/docs/workspace/streaming/techniques) recommends a smaller baseline for scalability; compare hotspot arrival, memory, and route seams with the existing 64/512 baseline on actual devices. [Roblox performance guidance](https://create.roblox.com/docs/performance-optimization/improve) describes conditional mesh instancing; triangle budgets and object counts alone do not establish frame rate. Streaming is place configuration. Water and decoration are non-queryable so the water sheet is not an unintended walkable floor.

## Rebuild and verify locally

From the repository root with Luau CLI, Rojo, Python and NumPy:

```sh
python3 prototypes/map10-v21/check_layout.py
python3 prototypes/map10-v21/build_review.py
python3 prototypes/map10-v21/check_geometry.py
python3 tests/map21_foundry_ambience.py
blender -b -P prototypes/map10-v21/render_readback.py -- build/map21
```

The readback renders reconstruct the authored Lua part specifications in Blender; they are **not** Studio screenshots. The test place prints native ray coverage at Play startup and stamps its source fingerprint on Workspace. Static width/cover sampling cannot prove actual avatar travel, real multiplayer combat, streaming reliability, or actual audio. When integrating, settle which live boss uses the Foundry (the blueprint label BOSS-03 is not itself a current runtime boss ID), ensure cover blocks the actual production server beam path, and preserve current unlocks, navigation binding and save schema. Apply the same short check loop to the next districts before replacing the live map.

### Verification limits for this package

The desktop Library helper failed to materialize the file on Windows (the helper calls an unsupported extended-attributes API), so Studio was not opened for this slice. The production aggregate also encountered an unavailable historical fixture path, and the untouched production place build was blocked by a Rojo 7.6.1 incompatibility with an existing binary beam template. The standalone Foundry build does not depend on that template and passed its own build and static checks. No browser or Roblox sessions were opened for the final package.
