# Scream Simulator — microphone city redesign

[GitHub repository](https://github.com/anushil7a/scream-simulator) · [Roblox experience](https://www.roblox.com/games/122465114514497/Scream-Simulator)

[Draft redesign review and developer handoff](https://github.com/anushil7a/scream-simulator/pull/1) — includes build instructions, scoped test evidence and remaining release gates.

**Active development, not a completed release.** Current work is on `feature/microphone-city-redesign`. The live experience was last verified at version 32; this branch has not been published over it. [Historical release notes](docs/RELEASE_32_NOTES.md) describe that older build.

## Build the current source

```sh
git clone --branch feature/microphone-city-redesign https://github.com/anushil7a/scream-simulator.git
cd scream-simulator
mkdir -p build
rojo build default.project.json -o build/MicrophoneCity.rbxl
rojo build default.project.json -o build/MicrophoneCity.rbxlx
```

Open `build/MicrophoneCity.rbxl` in Roblox Studio and press Play. The city is generated on startup; an empty Edit viewport is expected. Build from `src/` rather than assuming older root-level place files contain this redesign. Rojo 7.7 was used. Generated `build/` outputs are ignored by Git.

Read the [development brief](docs/PROFESSIONAL_REDESIGN_PROMPT.md), [implementation evidence and remaining work](docs/IMPLEMENTATION_STATUS.md), [asset inventory](docs/ASSET_INVENTORY.md), and [contributor guide](CONTRIBUTING.md).

## Implemented in this branch

- Hold attack, use microphone, release an aimed beam. Client calibration/power processing and server bounds/cooldowns are implemented; real microphone/proximity-voice validation remains outstanding.
- Levels 1–300, four-second cast cooldown, bounded power/level scaling, visual style unlocks every five levels, compact menus, mouse aim and touch controls.
- Central PvP district, safe city surroundings, spawn protection, separate dodge, sprint stamina, level-scaled health and quiet-time healing.
- Barcelona-inspired city with courtyards, enterable shops, market, beach, usable seating, pier, lookout, swimming area and lifeguard boundary recovery. Art and performance are still being refined.
- 46 residents with grounded navigation, conversations, work activities, reading/resting and reactions. Nick has practice routines and a multi-stage optional soccer quest.
- Selected NPC quest givers, vendor equipment purchases, tiered destruction/repair, earnable micro-speaker and unconfigured premium entitlement hooks.
- Versioned profiles, session leases and temporary test progress separated from legitimate saved progress.

These are source/integration milestones, not blanket verification of every device, multiplayer case or saved-data path. The detailed status log distinguishes observed behavior from untested requirements.

## Controls

- Hold **E** / **HOLD SCREAM**, use your mic, then release to fire toward the aim point.
- **Q** / **DODGE**: roll with cooldown; dodge cancels an unfinished attack capture.
- Hold **Shift** / tap **SPRINT**: up to ten seconds of sprint, then five seconds of recovery.
- **T** / **TALK**: nearby NPC dialogue. **F**: world interactions.
- **B** / **SCREAMS**: toggle collection. **M**: map. Quests, Style and Settings are menu tabs.

A microphone and Roblox voice eligibility are required for gameplay. Studio setup without usable voice may remain on the microphone panel. Synthetic fixtures in `tests/` can exercise selected mechanics, but are not a substitute for live voice validation and must never be appended to production source.

## Friend testing and release limits

Public test tools remain enabled at the owner's request (`DeveloperAccess.PublicTestingEnabled = true`). The first test mutation freezes legitimate progress; test changes use a temporary copy and are not saved. Owner/product configuration is still needed for real pass and badge IDs.

Outstanding release gates include real microphones and eligible accounts, physical device/multiplayer input and performance tests, live save contention/migration checks, completed city art review and a production backup/old-server drain. **Do not publish this branch as a finished release based on compilation or synthetic tests.** See the status log for active test runs and their exact source versions.

## Quick source checks

```sh
luau tests/VoiceCombat.luau
luau tests/Progression.luau
luau tests/ProfileLease.luau
luau tests/QuestLifecycle.luau
python3 tests/profile_race.py
```

Compile changed scripts with `luau-compile`, build both place formats, then run the relevant native Studio regression. Document failures and untested cases. [Report an issue](https://github.com/anushil7a/scream-simulator/issues) with reproduction steps, build/commit, device and expected behavior.
