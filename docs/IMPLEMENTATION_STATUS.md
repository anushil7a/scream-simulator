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

- **Live Studio connection:** initial Roblox MCP discovery returned no connected Studio instances. Studio launched and reconnected; its native file picker currently leaves Open disabled for the valid Rojo build, and native UI has intermittently timed out. No place is open yet. Local source implementation and command-line tests can proceed. Need a connected Scream Simulator Studio session for runtime visual review and cloud publication; will attempt to restore it before requesting help.
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
