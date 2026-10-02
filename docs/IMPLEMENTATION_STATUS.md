# Microphone city redesign — implementation status

Approved scope: [development brief](PROFESSIONAL_REDESIGN_PROMPT.md). Started October 1, 2026. This is an active implementation, not a release completion report.

## Work sequence

- [ ] Audit/reproduce existing defects and profile live baseline.
- [ ] Microphone calibration, power meter, hold/release capture, live proximity audio.
- [ ] Server-validated mouse aim, level 300 balance, four-second cooldown, independent action states.
- [ ] Authored city sample and layout/style/traversal plan.
- [ ] Occupational NPCs, ordinary quest givers, Nick discovery and difficult soccer quest.
- [ ] Tiered destruction, repair, equipment, premium entitlement hooks.
- [ ] Scream/roll/run/jump/landing animation and input regression fixes.
- [ ] Save migration, device/multiplayer/performance checks, builds, handoff and release verification.

## Items requiring owner / external assistance

- **Normal build loading:** Studio now has a disposable local Place1 open. Map generation and NPC behavior were tested through temporary source harnesses. The native file dialog still fails to open the built file reliably. MCP rejects Script insertion and RemoteEvent firing because of execution capabilities. Owner assistance opening `build/MicrophoneCity.rbxl` normally is still needed for full gameplay testing; do not disable security protections to work around this.
- **Real microphone validation:** real eligible accounts, permitted microphones, and a second human/device are needed to prove proximity voice, calibration differences, permission failures and multiplayer behavior. Simulated numeric samples are not evidence of real microphone operation.
- **Paid products and Roblox badges:** actual pass IDs, prices, badge IDs and any asset purchasing budget remain unconfigured. Implement in-game achievements and entitlement interfaces; do not fabricate IDs or launch purchases.
- **Device/load sign-off:** physical phone testing and a representative multiplayer soak require actual devices/players. Record unverified cases instead of claiming they passed.

## Evidence log

- Baseline repository inspected at commit `ed336cf`; working tree initially clean. Current source is still level 30 with prerecorded audio fallback; prior version-32 tests do not validate this redesign.
- Existing E/Q handlers and Dodge effect branch are separate. User-reported dodge/scream issue is not reproduced yet; root cause remains open.

## Current implementation checkpoint

- New pure VoiceCombat rules implement 300-level stats, four-second cooldown, sequence/replay validation, capture expiry and cancellation. New MicPower normalizes calibrated energy and rejects isolated spikes.
- 3,925 assertions passed in `luau tests/VoiceCombat.luau`: full 1–300 range progression/caps, power monotonicity, amplifier cap, capture replay/cooldown/invalid values, roll cancellation, silence, expired capture and synthetic calibration samples. This is rule evidence only.
- Client microphone adapter, setup UI, power meter, hold/release mouse aim and server begin/cancel/release flow implemented. Recorded attack playback removed. Real microphone and runtime UI behavior not verified yet.
- Local Rojo build succeeds with Audio API and default proximity voice configured; experience-level eligibility/voice settings remain to be checked in a published test place.

- Destruction service added: tagged grouped benches/bins, small trees/bikes, and building facade sections; level gates, bounded damage, replicated health/stages, timed repair and occupied-volume repair delay. Seats release occupants and disable sitting/prompts while destroyed. Requires Studio runtime verification.
- Rule suite expanded to 4,003 assertions including destruction unlock boundaries and damage rejection. All source compiles; isolated `build/MicrophoneCity.rbxl` builds. Live game and main-branch release remain unchanged.

## Additional source work (October 1)

- Confirmed all five owner choices: hold/release microphone attack; actual proximity voice; colorful Barcelona-inspired city; premium movement outside PvP; timed world repair.
- Charge/release, airborne and landing poses added to the existing additive run/roll layer. Rejected casts, spawn protection, cancelled captures and expired captures now clear charging state. Animation stacking now removes the full composed offset each frame. These poses still need visual R6/R15 testing.
- Added three authored work sites and residents: Mar Soler waters Rambla flowerbeds, Laia Costa paints a coastal scene, Pau Vidal arranges market produce. Work is interrupted by conversation or scream reactions. Pathfinding and grounded appearance require runtime review.
- Added a gardening task and selected resident quest unlocks. Existing saved quests retain access during migration. Three flowerbeds have interaction prompts; ordinary tasks now identify their giver in the menu.
- Added scream visual style unlocks every five levels through 300, retaining previous save IDs. Stats remain bounded by the shared level/power rules.
- Added a 1,500-coin micro-speaker with persistent ownership/equip state, capped power bonus and UI. Added server-owned movement-pass checking, safe-area extra jumps/consecutive rolls and arena cooldown restoration. Pass ID is zero; purchases remain unavailable until configured.
- Requested owner help cancelling Studio's unresponsive file dialog and opening a disposable Baseplate; source work continues. Latest CUA retry also timed out.
- Remaining: broader authored map and interaction/clearance audit, richer effect differentiation, save concurrency, physical equipment visual, complete premium UI once IDs exist, runtime regression/performance/device/voice tests, release/handoff. Compilation and pure-rule checks do not prove these runtime requirements.

## Persistence and hidden court checkpoint

- Added session leases around atomic profile load/save, serialized in-process saves, lease release on leave/shutdown, and separate `ScreamSimulator_Studio_v2` storage for Studio. Twelve pure lease checks pass; real DataStore contention/failure tests remain outstanding.
- Deployment must restart/drain old version-32 servers: those versions do not honor leases and could otherwise overwrite redesign saves. Take a production backup and verify migration in test storage before rollout. Do not publish this checkpoint over the live game.
- Nick Booty is a hidden occupational resident on a coastal court. First conversation grants a persisted discovery achievement and 50 coins. His quest creates a personal, server-controlled ball: five sequential targets in 120 seconds, moving final targets, microphone-powered shots, out-of-bounds reset. Completion is separately claimable once for 1,800 XP/1,200 coins and a saved achievement. Difficulty, multiplayer independence and reward reconnect paths need runtime tests.
- Selected buildings now have actual open ground-floor shells, six-stud entrance aisles, displays and lighting geometry. Collision/traversal and appearance remain unverified in Studio.
- Server rule/compilation evidence is a development checkpoint only. Map polish, runtime behavior, real voice, performance and publication gates remain open.

## Engine evidence and fixes — continued October 1

- Opened disposable local Studio `Place1`, place ID 0, instance `d388915b-0dc8-4725-92c0-83fbcae49c6a`. No live place changed. Generated actual City source geometry in Edit mode and inspected aerial/street screenshots.
- First collision-volume audit found **87 road obstructions**. Corrected block perimeter lamps/trees from ±110 to ±102 studs, moved courtyard cafés away from roads, and corrected pedestrian route points from ±109 to ±101. Rebuilt and reran `tests/StudioCityAudit.luau`: **zero road obstructions, zero blocked shop entrances, 30 enterable interiors**. Map has 43,758 parts / 2,955 solid parts before the final navigation-only volumes; this count merits device/streaming profiling.
- Pathfinding with a two-stud radius, five-stud height and no jumping succeeded for hub→promenade, hub→gardens, promenade→Nick and north street→courtyard. Market→delivery initially failed. Isolated the blocked endpoint beside a parked bicycle; moved delivery to the promenade center and verified the full route succeeds (126 waypoints).
- Moved resident joint animation off server C0 replication into a streaming-aware client layer with distance-based update frequency. Conversation and scream reaction cancel stale path commands. Residents pause for conversations before resuming work.
- Ran source in a disposable Play session via `tests/build_studio_harness.py`. A five-second NPC sample observed **46 residents, 36 moving more than two studs, zero airborne at sample end, and all four occupational residents working**. This is a short sample, not a floating/stuck regression soak. Client animation harness executed without a reported error; visual animation review remains required.
- Full server/client integration was blocked by MCP capability errors when firing Action/State RemoteEvents. Stopped the test session. No combat/UI/microphone pass is claimed from this harness, and normal Script delivery remains untested.
- Added fountain navigation exclusion and increased road traversal cost after observing NPCs standing on fountain water surfaces. This final route-cost change still needs a fresh runtime check. Uses Roblox's documented [pathfinding modifiers](https://create.roblox.com/docs/characters/pathfinding).
- Added original wearable micro-speaker geometry. Repair overlap checks now include residents, preserve Seat.Disabled state, and abandon stale repair callbacks after tag removal. These changes require runtime checks.
- Fresh final geometry audit after navigation changes passes: no road blockers or blocked entrances. The first path query immediately after rebuilding returned NoPath; fountain avoidance is not yet verified. Investigating this result before claiming a route pass.
- Follow-up fountain investigation: Edit-mode queries after stopping/rebuilding returned NoPath; a fresh Play session computed a route but initially ignored the volume. `CanQuery=false` on the navigation part prevented the modifier from affecting the route. Set CanQuery=true; the next server path query succeeded with 23 waypoints and **no waypoint inside the fountain volume**. Audio occlusion now explicitly respects physical collision, so the invisible navigation region does not block sound.

## Progression, test tools, premium limits, and responsive UI

- Fixed NPC reward suppression: the per-target reward interval now matches the validated four-second cast interval, so a legal knockout hit is not denied solely because the previous cast was four seconds earlier.
- Added pure Progression rules for the 300-level curve: `floor(80 + 16L + .012L²)` XP per level; player KO XP still rises with victim level but uses `floor(50 + 8L^.7)` to bound farming impact. Schema 3 carries saved XP across new level thresholds instead of dropping overflow. 1,506 progression/migration checks pass.
- `tests/Progression.luau` documents assumptions and prints estimates, not measured player outcomes. Average-cohort estimates: level 25 about 1.0 active hour, 50 about 3.4, 100 about 11.9, 300 about 89.4. New-player and skilled-cohort cap estimates are 227.2 and 42.6 hours. This wide spread requires actual balance playtesting; these values are initial tuning.
- Test commands now freeze a sanitized pre-test profile snapshot while the test session uses a separate copy. Autosave/leave/shutdown renew/release the original profile lease and save only that snapshot. This preserves pre-test progress and prevents test rewards from persisting. Real DataStore concurrency remains unverified.
- Premium extra jumps are limited to 24 studs above the last grounded height, with bounded launch velocity. Entering the arena cancels a premium roll and restores ordinary cooldown; premium rolls do not provide arena damage immunity. Gameplay boundary tests still require normal RemoteEvent execution.
- Responsive menus no longer scale all text down on phones. Cards reflow, quest descriptions use measured text height, tabs wrap on the narrowest screens, and the mic setup uses stacked full-width buttons. Moved Talk above the power meter and separated narrow top-navigation buttons.
- Added a clearly isolated UI fixture (`tests/build_ui_preview.py`) with fake microphone readiness and fake network callbacks solely for layout measurement. Native Studio TextFits/AbsoluteSize checks passed all five menus at 390×844, 320×568 and 844×390 during this turn; final 320×568 run also includes the mic permission-error panel. No horizontal overflow or menu text below 12px in checked layouts. These are synthetic layouts, not physical phone, real microphone, touch multitouch or full gameplay tests.
- Public testing remains enabled as the owner requested. Pass ID and published badge IDs remain unset. The local game was stopped after testing; no cloud publication occurred.
