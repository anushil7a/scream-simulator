# Redesign QA and release readiness

Updated October 2, 2026. Source verification: **7b8f065** on `feature/microphone-city-redesign`.

**Not ready for production publication.** The source/build is available for developer review in [draft PR #1](https://github.com/anushil7a/scream-simulator/pull/1). The live experience was last verified at version 32; this redesign has not been published over it.

This is a concise current handoff. [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) contains the chronological experiments, failures, corrections, exact Studio contexts and active-run cleanup instructions. The [development brief](PROFESSIONAL_REDESIGN_PROMPT.md) remains the full scope; this report does not reduce it.

## Fresh source/build verification

Executed against `7b8f065`:

- All **25** `src/**/*.luau` files compile with `luau-compile`.
- `luau tests/VoiceCombat.luau`: **4,007** combat, microphone-processing and destruction rule assertions.
- `luau tests/Progression.luau`: **1,506** progression/migration assertions. Printed leveling times are mathematical estimates, not player-playtest results.
- `luau tests/ProfileLease.luau`: **12** lease assertions.
- `luau tests/QuestLifecycle.luau`: **5** lifecycle scenarios.
- `python3 tests/profile_race.py`: **13** checks using actual Profiles source with a mocked store and coroutine scheduling. This is not Roblox DataStore contention evidence.
- Both Rojo place formats build: `build/MicrophoneCity.rbxl` and `.rbxlx`. Generated files are ignored; use README commands to reproduce them.

Counts describe coverage in these suites, not a probability of a bug-free game. No synthetic suite validates physical microphones, real phones or a representative multiplayer population.

## Current implementation and scoped runtime evidence

### Microphone and attacks

Implemented: mic-required setup, quiet/voice calibration, power meter, explicit hold/release capture, mouse/touch aim, four-second server cast limit, level 300 caps, cover checks and five-second spawn protection. Input power is client-reported and bounded; it cannot be certified as genuine human speech.

Evidence includes native synthetic Action/State/Effect integration, engine-injected E/Q/menu interactions, rule boundary/replay tests, microphone lifecycle tests and six native recalibration-controller checks. The most recent fix prevents failed recalibration from restoring old readiness.

**Open:** published two-account real-audio feasibility; comfortable-volume power behavior across different microphones; mute/permission denial/disconnect/reconnect; nearby listener attenuation and controls; measured voice/attack latency. No live-voice pass is claimed.

### Movement and avatars

Implemented: separate roll, collision checks, sprint exhaustion/recovery, jump/landing and scream poses. The R6 joint-axis correction passed six focused checks on native R6/R15 rigs; the old code failed the same R6 assertion. Default Animate was disabled in that focused check.

**Open:** physical keyboard and touch/multitouch play, default Animator blending, varied avatar proportions/accessories, micro-speaker grip through full movement, respawns under latency, vehicle impact/recovery and premium boundary transitions in actual multiplayer. The focused joint test does not close these requirements.

### Map, residents and activities

Implemented: Barcelona-inspired district layout, 40% central PvP land, safe surroundings, 31 enterable shops, 13 varied courtyards, market, beach, pier/lookout, swimming boundary, seating, selected quest givers and 46 residents. Additions include performance audiences, microphone beach volley, active street-furniture maintenance and distinct worker uniforms.

On `70a4cf5`, native checks passed all **72** route cases and found zero static road, doorway or interior-aisle obstructions. Source geometry has since changed only the distant sea backdrop color; the newer mic/animation changes are separate. The raw route results are in [city-routes-70a4cf5-2026-10-02.json](../tests/evidence/city-routes-70a4cf5-2026-10-02.json). That inspected world contained 50,285 parts / 3,468 solid parts, which still warrants load/device profiling.

Scoped tests: audience behavior: 12 checks; volley: 16 scripted checks including a synthetic cast through Bootstrap; maintenance: 13 checks including a real quiet interval, actual worker navigation and player occupancy. None is a human two-player usability test.

**Open:** final city-wide art/activity review at street height, physical traversal/driving, crowd behavior under player load, obstacle/destruction recovery across all occupations, volleyball timing with two real microphones and additional iteration based on playtests. Current screenshots and route checks do not prove the requested final visual quality or fun.

### NPC soak in progress

Run `CityNpcSoak-20261002-70a4cf5` is active in **Place1**, Studio ID `d388915b-0dc8-4725-92c0-83fbcae49c6a`, for 1,800 seconds. At 1,397 seconds: 46 alive, 36 moved since the previous snapshot, 5 working, 2 seated; no recorded persistent seat mismatches, walking-target stalls or residents above 20 studs. This is an interim observation, not a pass.

Do not restart or stop the run solely because an observation times out. Query its exact workspace run/state/sample attributes. On completion, export all samples, review behavior and console output, stop Play, restore clean Bootstrap/remove probe attributes, and resync the newer Microphone, MicPower, RunAnimation and City sources. See the detailed log for exact cleanup instructions.

This run has one Studio client without real microphone/combat load. Even successful completion does not satisfy the requested representative 24-player, 30-minute soak or physical-device frame-rate targets.

### Quests, progression, destruction and persistence

Implemented: selected NPC tasks, Nick discovery and staged soccer challenge, one-time rewards, level-based destruction, safe timed repairs, earnable amplifier and test-session save isolation. Native fixtures cover the scripted Nick course, quest lifecycle/reward paths, vendor purchase, damage/repair timers, seats and local maintenance; check the detailed log for the exact fixture scope and revision.

**Open:** full quests with human mic input; disconnect/rejoin and concurrent rewards on real services; destruction seen by other/late-joining players; occupied repairs with real multiplayer timing; live profile migration/leases/backups and old-server shutdown. Mocked store checks do not prove live persistence safety.

## Owner/external inputs needed

- Two voice-eligible accounts and separate real microphones/devices for the published mic feasibility test. A developer must create/use an isolated private test experience with voice/audio settings enabled. Do not connect experiments to production saves or publish WIP over the current experience.
- Named desktop and physical phone targets, plus testers for representative multiplayer load. The working default is 24 players, 60 FPS desktop and 30 FPS phone; no final device result exists.
- Real badge/pass IDs and prices if those products are to launch. IDs remain 0; do not invent IDs or trigger purchases. In-game achievements and entitlement hooks exist independently.
- Review of the representative city block and broader world against the owner’s visual/playability expectations.

The owner requested that blocked items be recorded while independent work continues. These items remain open; their presence is not authorization to omit them or declare the goal complete.

## Release sequence once gates can be exercised

1. Build an isolated private test experience from a reviewed commit. Confirm all fixture appendices are absent and production source matches that commit.
2. Prove real microphone/voice feasibility first. Resolve failures before relying on combat/balance playtests.
3. Run the physical input/avatar, two-player combat/quest/destruction and actual-device cases above. Preserve failures and exact hardware/account/build context.
4. Run isolated live-store migration/contention/reconnect tests and representative multiplayer/load/soak tests. Verify no test mutations enter legitimate saves.
5. Review city art/activity, balance, entitlement configuration and the final public-test-tools policy. Public test tools are currently enabled as requested; do not silently change that policy.
6. Back up the current published version and data, record rollback steps, and plan old-server draining before changing save schema in production. No live backup/migration completion is asserted here.
7. Publish only after the applicable gates pass. Reopen the cloud place, verify published version/source and smoke-test a fresh server. Keep the prior rollback version.

## Where to work next

- Finish/export the already-running NPC observation; preserve its scope and any failures.
- Continue final map/activity/animation polish and fix concrete defects found by playtests.
- Coordinate the real microphone/device test inputs; synthetic evidence cannot replace them.
- Update this report after each release-relevant result rather than treating the chronological log as a final sign-off.
