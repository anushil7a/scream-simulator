# v2.1 boss home placement (standalone)

Owner assignment: Metronome in blue-roof Academy; Golem in purple Neon Colosseum; Ignis in Magma Rift; Captain by lighthouse/Foundry; Conductor in Astral. Actual IMG_1526 master reference and current roadmap/district source reviewed. No production source or map geometry changes.

`BossHomes.luau` returns `{BossHomes={...}}`, suitable for staging as the existing catalog's Shared.CompactLayout adapter. Coordinates are ground height, NOT model root height. Captain keeps `leviathan` runtime ID, preserving encounter/reward identity.

| Encounter | District | Ground (x, y, z) | Conservative nearest solid |
|---|---|---|---:|
|Metronome|01 Academy|(-520,50,730)|43.38 studs, cloister column|
|Golem|06 Neon Colosseum|(120,115,760)|103.24 studs, arena cover|
|Ignis|07 Magma Rift|(980,175,60)|38.89 studs, forge anvil|
|Captain|05 Tidal Bell-Foundry|(420,48,-680)|69.34 studs, arena pillar|
|Conductor|08 Astral|(920,340,920)|49.50 studs, citadel footing|

Each declares a 22-stud engagement radius and a 4-stud patrol leash. Server combat must keep its fixed-home envelope; do not add patrol displacement to its range. The validated 36-stud check radius covers the 34-stud warning extent plus 2 studs of player clearance, and the inner moving boss/body envelope. Native clipping/server hit policy remains unchanged.

Metronome is 110 studs east of the blue-roof cloister and 282.3 studs from Academy spawn. Its ring is not under spawn. Ignis and Conductor use off-center forecourts outside the 44-stud center crossroads for the 22/26-stud playable envelope. Golem and Captain intentionally occupy their authored central arenas; public crossroads traverse these spaces, so retain opt-in combat/no attacks on passers-by. Captain is in the Foundry arena with lighthouse visible, NOT on the narrow lighthouse causeway/islet.

## Reproducible analytic evidence

`python prototypes/map10-v21/check_boss_homes.py --geometry build/map21/overworld-geometry.json`

The checker reads BossHomes directly and uses current exported geometry, existing optional NumPy OBB/ellipsoid/cylinder ray routines. It writes nothing. Each home has 1,009 samples on a 2-stud lattice within radius 36: 5,045 floor and 5,045 headroom checks total. Floor deviation ≤ 0.12 studs, floor ZoneId must match assigned district, vertical clearance ground + 0.5 through ground + 18. All passed against freshly exported 3,148-part geometry. Exact conservative rotated-AABB nearest-obstacle distances also exceed 36, proving no unprobed small horizontal obstacle within the disk at player/model height. Wedge boxes are conservative, not false-negative triangle tests.

Fresh export text SHA-256: 54bc1c578f1ab1721daf3cf24f1c0e0d17e1f600173cb0410abef2c69a2faf6c.

This is static geometry evidence, not native NPC pathfinding, streamed rendering, physical phone, attack-effect or multiplayer acceptance. The placement build checks native floor and headroom within 26 studs; clipping and nonparticipant safety during active fights remain full-game integration checks. No external actions/push/publish.

## Local placement build

From repository root, with Python, Luau CLI and Rojo:

```sh
python3 prototypes/map10-v21/build_overworld.py --bosses
python3 prototypes/map10-v21/check_boss_homes.py
```

Open `build/map21/Map10V21BossPlacementReview.rbxl` locally in Studio and press Play. This opt-in build stages unmodified boss service, catalog, geometry and visual controller against the placement adapter. Existing boss rigs, levels, directional patrol and range rings are shown. It does not enable attacks, audio, saves or character progression. The lightweight local review uses the same Studio + unpublished ID guard as the map-only preview. The map-only build still reproduces its previous artifact byte-for-byte.

- Exact candidate source stamp: `148630a70588b09af4a75b58a8b645f57e45292b0fea94d666475cdbdbfcd1cd`.
- Exact 85,731-byte candidate SHA-256: `447c1d5fcb81233d3ea1a6888219f2aebe1d9f38912029ab868a8c778e2c5888`.
- Independently rerun: all 75,674 route checks, 573 terrace envelopes, and three unmodified production boss fixture suites (service, visuals, pose) passed. The older `tests/boss_spatial.py` is for the compact map, not this build; unchanged standalone Luau path currently stops at unresolved `script.Parent` before spatial assertions. No production tests were modified.

## Exact Windows Studio Play

The exact 85,731-byte build and loaded source stamp above were confirmed. Startup passed 1,210 native boss floor/headroom probes and the existing 2,577 route floor plus 2,568 route headroom probes with zero failures. For each boss, the client was repositioned near the intended place to verify streaming (not a continuous walk between arenas). All five reported GeometryReady; model part counts were 274/291/269/343/417 in level order. Each authoritative Core and its client visual moved over the two-second sample, and the same local model persisted during patrol. No fight or combat-audio validation was performed; the build is placement-only.
