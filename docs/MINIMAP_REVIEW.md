# Regular-player minimap review

November 11, 2026. Base `b5ba1aad1106f30d62b393ed56acc98e9186b600`. Draft development branch only.

## Behavior and scope

- Ordinary players receive a north-up minimap in the upper-right test-tools slot. It reuses the existing CityMap projection, arena/road/beach/pier geometry and player heading. Compact mode omits the eight numbered landmark pins; the full Map tab keeps them and its legend.
- MAP opens the existing Map tab. The HUD map has a separate retained view; opening other tabs does not destroy or replace it. The map and marker are allocated once, not on every render.
- The visible marker updates at most ten times per second for the same character. Missing/detached roots or hidden UI immediately clear it; a new root and reopening update immediately rather than waiting on the old character's timer.
- Existing owner/Studio-only TEST TOOLS remain in that slot for authorized testers; their full map is still available through M/the Map tab. This batch does not move or widen developer access.
- The minimap hides during setup, menus, conversations, focus loss, and every displayed toast, so it cannot cover an urgent save warning. A cramped screen uses a 44-pixel-high MAP launcher instead of a tiny unreadable map. At widths below 280, touch heights below 315 or non-touch heights below 168, this extra launcher is hidden; the existing menu remains the map route. These are minimap layout limits, not claims that the whole game supports every tiny viewport.
- Independent review reproduced a tracker overlap at 430px width. The corrected map either ends above the tracker or starts to its right. A short-screen sweep also exposed overlap with combat controls; self-review then included the Talk button and raised the touch-height floor to keep it clear.
- Fixed the missed legacy Microphone.Release notice to "Capture expired. Start a new live beam." Its expired capture still returns zero power and resets capture; added an actual-source regression.
- No server/shared production files, save schemas, rewards, entitlements, map geometry or combat timings changed. The current map is preserved. No audio configuration, live stores or publication.

## Verification

The focused suite executes the actual CityMap module and actual client construction/layout/visibility snippets with fake GUI/vector/input objects. It covers full-versus-compact geometry, projection and heading, missing/replaced roots, cadence, independent views, menu callback, no repeated allocation, authorization, notifications, focus and responsive bounds. A width sweep uses every integer from 320 through 1280, selected portrait/landscape/extreme heights and both input modes. Bounds use actual client Shop/Quests, HUD, tracker, combat and Talk controls, not the transparent Navigation container.

Passed 100,333 cumulative synthetic assertions (including 146 module checks), eleven negative controls, nine existing marker checks and 111 microphone lifecycle checks. Full 25 pure/synthetic + 69 mocked suites, 57 production compiles and all builds pass. Independent review reran focused tests with no blocker. Final counts, mutations, aggregate results and source hashes are recorded in [evidence](../tests/evidence/minimap-2026-11-11.json). Baseline `--baseline` reproduces the absence of the minimap APIs. Existing map-marker and microphone lifecycle regressions remain part of the full suite. Independent review found and rechecked the intermediate-width correction.

`python tests/verify_local.py --build` compiles production, checks candidate/source correspondence and builds all disposable fixtures, including `build/MiniMapReview.rbxl`. The new native fixture audits layout rectangles, ordinary/developer states, opening/closing the full map, view identity and notification suppression using the actual client with fake microphone/remotes. It has only been built/compiled, **not executed in Studio**.

## Limits and cleanup

No native minimap appearance/readability, actual click/touch propagation over child frames, gamepad accessibility, phone, real microphone, live persistence or network validation is claimed. The many sweep assertions are deterministic synthetic geometry, not thousands of device playtests. Keep the candidate unpublished until relevant native/device checks and release authorization.

No programs, browser tabs or dialogs were opened this batch. The two previously inaccessible minimized Windows app-picker dialogs were not touched; their cleanup remains blocked by the exposed controls. Pre-existing work is preserved.

Current shop documentation is corrected to hue-only/Spectrum gating and automatic receipt activation with legacy saved-token support. PR #1's summary is to be refreshed from the verified draft checkpoint; historical detail remains in the repository roadmap and scoped evidence, not presented as current behavior.

## Visual hierarchy and contrast polish (November 13)

- Added static, zero-runtime-loop visual framing inside `CityMap.create` when `CompactLayout` is active (`src/StarterPlayer/StarterPlayerScripts/CityMap.luau`), keeping legacy `CompactCity = false` construction, landmark pin positions, training tier badges, player marker geometry, and projection/update math unchanged:
  - `UICorner` (`CornerRadius = 4`) and `MapBorder` `UIStroke` (`Color3.fromRGB(115, 148, 148)`, `Thickness = 1`, `Transparency = 0.35`) on `CityMap` to frame both the compact minimap and full map against dark panel containers.
  - World-derived `Courtyard` tone (`Color3.fromRGB(61, 86, 85)`) from `CompactLayout.PartSpecs` (`HubPaving`), drawn beneath `Beach`, roads, footprints, and guidance routes to separate the safe west spawn/training hub.
  - Coastal `Shoreline` water accent (`Color3.fromRGB(64, 134, 152)`, `9` studs along `Config.MapMax.Z - 9` aligned to `Beach` width and clear of `Footprint_Court`).
  - `UIStroke` rim (`Color3.fromRGB(168, 186, 184)`, `Thickness = 1`, `Transparency = 0.35`) on full-map `Landmark` pins for contrast over dark terrain and arena fills.
- Updated `tests/minimap_visuals.py` with positive assertions and 6 new negative controls (10 total).
- Post-edit mocked/compiled checks (`git` via VS2019 BuildTools on `PATH`):
  - `luau-compile --null src/StarterPlayer/StarterPlayerScripts/CityMap.luau`: exit=0 (11 KB bytecode)
  - `python tests/minimap_visuals.py --negative-controls`: `PASS 684 world-derived map art assertions; mocked only`, 10/10 negative controls PASS
  - `python tests/minimap.py --negative-controls`: `PASS 138 actual CityMap construction/projection/controller assertions; mocked only`, `PASS 987779 actual minimap module/client assertions; synthetic layout/input only`, 16/16 negative controls PASS
  - `python tests/training_map.py --negative-controls`: `PASS 2 unchanged projection/layout/update source contracts`, `PASS 754 actual training-map/legacy assertions; mock UI only`, `PASS 11 training-map negative controls`
  - `python tests/compact_city_map.py --negative-controls`: `PASS 102 compact CityMap projection/render/lifecycle assertions; mocked GUI only`, 10/10 negative controls PASS
  - `python tests/city_map_marker.py`: `PASS 9 actual map marker checks with mocked GUI`
  - `python tests/notice_view.py`: `PASS 629 notice module/Client assertions; mock text metrics/GUI, no native access claim`, `PASS source contracts: neutral peek, render cadence, teardown`
  - Native `Roblox_Studio` MCP validation (disposable `build/SaveNoticeReview.rbxl`, `GameId=0`, `PlaceId=0`, Play `Client` mode with current `CityMap.luau` + `CompactLayout.luau` + `Config.luau`):
    - Full map (`220×183.33`) and compact minimap (`160×133.33`) rendered `UICorner` (`4`), `MapBorder` (`Thickness=1`, `Transparency=0.35`, `Color=115,148,148`), `Courtyard` (`Color=61,86,85`, `55×119.17` full / `40×86.67` compact), and `Shoreline` (`Color=64,134,152`, `213.89×2.75` full / `155.56×2.0` compact, positioned below `Footprint_Court` bottom `280.76 < 280.92` full and `431.56 < 431.67` compact).
    - Full map rendered `6` landmarks with `UIStroke` on `Landmark1`; compact minimap rendered `0` landmarks; `CityMap.MiniLayout(Vector2.new(390, 844), true, false)` returned `{available=true, expanded=true, width=112, height=132}`.
    - Disposable preview captured in `build/studio-validation/wave2-ui-preview.jpg` (SHA256 `9e5ba9888f7527f4c5699a0ece4eb5a499d14afbbcdb6482d93703512715d66a`); Play stopped, temporary instances removed, and task-spawned Studio closed. `tests/small_screen_map.py` is not present in the repository.
