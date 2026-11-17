# MAP-10 v2.1 • Full overworld review

## Open in Studio
1. Unzip and open **Map10V21OverworldReview.rbxl** as a local place. Do not publish it.
2. Press **Play** to build the districts and spawn at Coastal Grand Academy. Follow the names above each bridge entrance. No console is needed to explore.
3. Open **Overworld-Layout.svg** for the transit layout. The images are Blender readbacks of the authored geometry, not Roblox screenshots.

Nine districts are present: Grand Academy, SoundBowl, Boardwalk/DJ Stage, Rambla, Bell-Foundry, Neon Colosseum, Magma Rift, Astral Citadel and Outer Reef. Zone 09 is the physical transit network: 11 bidirectional bridges forming overlapping loops. Five elevation bands, from the coastal districts up to the Y340 Astral Citadel, are accessible on foot. This is a first complete environment pass, not final art, and does not contain the production game's combat, quests, NPCs or saves.

### Collision and bugs addressed
- Walkable bridge decks, major architecture, walls, cover, reachable props and railings have anchored colliders and can be hit by queries. They don't run touch handlers. The sea, paint/inlays, purely cosmetic trim, light markers and soft surface effects are intentional exceptions; walking through a building is not.
- The Foundry–Magma bridge originally placed a support through a dock ramp. The support was moved out of the pedestrian clearance budget. The audit also found three sloping bridge rails jutting into turn pads. Rails are trimmed around turns and capped with solid posts instead of passing through the swept corridor.
- The Boardwalk–Foundry portal clears solid cliff masses rather than leaving a decorative slab that players walk through.
- Guard rails on the arterial bridges and district edges reduce accidental drops. The local test place respawns players at the Academy after falling through the nonphysical ocean.
- Each major arterial is 32 studs wide, with grade under 32°. Shorter local overlook walks are narrower. Geometry positions are the baseline; gate signs and actual links are not the old diagram's center-to-center lines.

### Performance decisions and limits
Parts are grouped by sector for streaming. Most details are anchored, non-touch, and small details avoid shadow casting; no map-wide per-frame loop or replacement collision polling runs. The simple geometry needs no mesh or texture upload. The current preview uses the requested experimental 256/896 stud streaming configuration. No frame rate, mobile memory or multiplayer scalability claim follows from part counts. Do not migrate boss reach, quest timing, or streaming values to the live place without targeted testing.

### Reproduce
From the repository root, with Rojo, Luau CLI and Python/NumPy:

```sh
python3 prototypes/map10-v21/build_overworld.py
python3 prototypes/map10-v21/check_overworld.py
python3 prototypes/map10-v21/draw_layout.py --built
blender -b -P prototypes/map10-v21/render_readback.py -- build/map21 --overworld
```

The offline audit exercises route width/grade, both district endpoints for each edge, connected paths, floor support and headroom. Studio reports `ReviewSourceSha256`, `ReviewNativeRayProbes`, `ReviewNativeFailures`, `ReviewPartCount`, and `ReviewSolidCount` on Workspace. Check the included QA record for the exact native run and tested scope. No publishing, external uploads of Roblox assets, changes to live place, or GitHub push were performed.

### Exact Windows Studio results (November 17, 2026)

- **Before the cliff addition**: artifact SHA-256 `45a29d17d6b61193e00549b33384872ee8ef39937512685e9baa34eea49a5d38`. All 2,577 native floor rays passed. All nine district arrival probes settled the client on the intended ground. Actual avatar traversed Academy → SoundBowl (five steps) and Magma → Astral gate (13 steps). An attempted move through a bridge rail stopped the avatar at X345.395 before the rail center at X346.65, as expected.
- **Final delivered revision**: artifact SHA-256 `80580dff3873f15f28a23c85f27f9bc52f9259152ab204030777ccebc4b08a5c`; loaded source hash `f0eb1f3834b55c22933a3b21b834806730af0c9011217dda831b30549ad4a787`. All 2,577 native rays passed; 1,603 geometry parts, 1,285 solid. Actual Academy spawn and 40-stud promenade walk/return passed. No authored runtime error was observed. The two long crossings were **not** repeated on the final revision. Both owned local sessions were closed; nothing published.

## Reference-led art rebuild

The first environment pass was a route blockout, not the visual target. This revision expands the teal-domed Academy into a campus, makes the sandstone Bowl and neon Colosseum district-scale structures, adds a broad asymmetric volcano and fortress, and gives Astral a floating keel, arch and taller satellites. The boardwalk and reef now have distinct occupied spaces; the Foundry has deeper gantries, a casting yard, masonry bays and a rebuilt cyan lens. Mainland geology joins several neighboring terraces, while the piers, reef and Astral still read as separate sites. The look is stylized Roblox geometry, not a pixel match to the supplied illustration.

All nine districts and 11 links remain. Several originally square terraces now have clipped corners and physically supported diagonal guard walls. Solid architecture, rock and bridge supports collide. Flush paving, visual ocean/spray, small lenses and indicators remain nonphysical by intent. Players that come to rest on tagged off-route rock can return to the Academy instead of having to jump into the ocean. The local guard samples active players twice per second, does not scan parts per frame, and ignores regular road/floor parts.

Development caught three sloped decorative support ribs cutting into Sky headroom. Their endpoints now follow the slope. The first shaped revision then failed 14 native floor probes at exact edges of three bridge-to-terrace seams missed by the offline checker. A narrow physical threshold at each district gate provides continuous support; the maximum rise over the native gate elevation is 0.10 studs. Collapsing visually redundant paver stripes and replacing 144 old bell shell parts with 24 ringing profiles helped keep the authored part count under the 3,200 review limit. This is not a mobile or multiplayer performance guarantee.

- Final artifact SHA-256 `04d5bea0b984b30629bf1d4507d1470e2ee1d2574fc030cf08474ee38f64896a`; loaded source SHA-256 `53727f07c23a4927dc59079a4be37cac5034c2bc7b26c734c9fd255642d5071a`.
- 3,148 geometry parts; 2,594 solid. 75,674 analytic checks across 106 segments, with effective 16-stud headroom checks on main/arterial routes. 573 grounded structure envelopes checked after clipping corner pads. Wedges may conservatively count as obstructions but cannot satisfy analytic floor support.
- Earlier art revision `39b8bc5…` passed 2,577 native floor and 2,568 headroom probes, all nine streamed arrivals, short low and upper bridge traversals, a physically blocking rail and automatic Academy return from a tagged under-map drop. The arrived-at-district tests used a test reposition, not continuous walking of every bridge.
- **Final corrected, exact native Play**: loaded source fingerprint verified; 2,577 native floor probes and 2,568 headroom probes, zero failures. Native Humanoid crossed the repaired Academy–SoundBowl seam (X−920, Z160→140→120→100) and Colosseum–Sky seam (X260, Z1060→1080→1100→1060), with health intact. No authored runtime error observed. The earlier longer traversal and cliff return checks belong to their separately named art revision.
