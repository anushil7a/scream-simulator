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
