# Scream Simulator — microphone city redesign

**Combat progression:** health / full-power DPS at levels 1, 25, 50, 75 and 100 are **100/15, 150/23, 225/34, 325/49 and 450/68**, interpolated between levels. Large level gaps intentionally favor the stronger player; equal-level perfect-aim simulations take two attacks. Healing restores 20% after 12 seconds without dealing or taking damage, then every 12 quiet seconds. [Balance evidence](tests/evidence/level-progression-2026-11-09.json).

**Attack audio:** [owner-selected tier effects](assets/audio/README.md) now map levels 10 through 100 to the ten supplied Roblox IDs, with original pitch, quiet mixing and local-mic ducking. All ten loaded in a silent local Studio check; gameplay listening and City Preview access remain unverified. Level 1 stays voice-only. Attack duration stays four seconds.

**Current direction (November 9):** see [the prioritized roadmap](docs/ROADMAP.md). City Preview version 19 has level cap 100 and still uses hold/release. The next unpublished local candidate defaults to automatic live-mic attacks (4 seconds maximum, 5 seconds cooldown), preserving normal profiles. Calibrate once, stay quiet briefly, then aim and speak; E/VOICE pauses/resumes. Reconnecting a mic or respawning requires explicit resume. Real-voice playtesting remains pending. GitHub development pushes are authorized; Roblox publication requires approval. Continue development while Codex allowance remains.

[GitHub repository](https://github.com/anushil7a/scream-simulator) · [City Preview](https://www.roblox.com/games/90337242377543/Scream-Simulator-City-Preview) · [Separate original experience](https://www.roblox.com/games/122465114514497/Scream-Simulator)

[Draft redesign review and developer handoff](https://github.com/anushil7a/scream-simulator/pull/1) — includes build instructions, scoped test evidence and remaining release gates.

**Active development, not a completed release.** Current work is on `feature/microphone-city-redesign`. The last recorded City Preview release is version 19; subsequent automatic-voice changes are unpublished. Original-experience version numbers are separate. [Historical release notes](docs/RELEASE_32_NOTES.md) describe that older build.

## Build the current source

```sh
git clone --branch feature/microphone-city-redesign https://github.com/anushil7a/scream-simulator.git
cd scream-simulator
mkdir -p build
rojo build default.project.json -o build/MicrophoneCity.rbxl
rojo build default.project.json -o build/MicrophoneCity.rbxlx
```

Open `build/MicrophoneCity.rbxl` in Roblox Studio and press Play. The city is generated on startup; an empty Edit viewport is expected. Build from `src/` rather than assuming older root-level place files contain this redesign. Rojo 7.7 was used. Generated `build/` outputs are ignored by Git.

For isolated local gameplay review, run `python3 tests/verify_local.py --build` and open `build/SustainedLocalPlay.rbxl`. It uses temporary profiles and must never be published. `build/SustainedNativeFixture.rbxl` adds synthetic checks; `build/PerformanceReview.rbxl` adds the manual performance collector. The same command builds `build/AutomaticVoiceCandidate.rbxl` with normal profile handling and a provenance sidecar; it is not a disposable save sandbox and is not approved for upload. See the [manual test plan](docs/AUTOMATIC_VOICE_PLAYTEST.md).

Read the [current QA report and release gates](docs/QA_REPORT.md), [development brief](docs/PROFESSIONAL_REDESIGN_PROMPT.md), [implementation evidence and remaining work](docs/IMPLEMENTATION_STATUS.md), [asset inventory](docs/ASSET_INVENTORY.md), and [contributor guide](CONTRIBUTING.md).

The [release handoff](docs/RELEASE_HANDOFF.md) records the latest local build, last verified playable preview, publishing recovery steps and human test requirements.

## Implemented in this branch

- Automatic live-mic attacks: calibrate, allow a brief quiet interval, then aim and speak. Sustained beams follow aim for up to four seconds, followed by five seconds cooldown from attack end. E/VOICE arms or pauses; real microphone/proximity-voice validation remains outstanding.
- Levels 1–100, bounded power/level scaling, visual style unlocks every ten levels, compact menus, mouse aim and touch controls. City Preview version 19 already has the 100-level cap but retains hold/release combat.
- Central PvP district, safe city surroundings, spawn protection, separate dodge, sprint stamina, level-scaled health and quiet-time healing.
- Barcelona-inspired city with courtyards, enterable shops, market, beach, usable seating, pier, lookout, swimming area and lifeguard boundary recovery. Art and performance are still being refined.
- 46 residents with grounded navigation, conversations, work activities, reading/resting and reactions. Nick has practice routines and a multi-stage optional soccer quest.
- Selected NPC quest givers, vendor equipment purchases, tiered destruction/repair, earnable micro-speaker and unconfigured premium entitlement hooks.
- Versioned profiles, session leases and temporary test progress separated from legitimate saved progress.

These are source/integration milestones, not blanket verification of every device, multiplayer case or saved-data path. The detailed status log distinguishes observed behavior from untested requirements.

## Controls

- Current local candidate: aim and use your calibrated mic to attack. **Normal speech can trigger attacks while screams are ON.** **E** / **SCREAMS ON/OFF** toggles attack activation; it is not required for each scream. **OFF** stops an active attack and lets you talk without attacking, leaving microphone/proximity voice unchanged. After respawn or microphone/focus loss, deliberately turn screams back on; cooldown and fresh-quiet requirements still apply. The choice lasts for this session. City Preview version 19 still uses hold/use mic/release.
- **Q** / **DODGE**: roll with cooldown; dodge cancels the active voice attack.
- Hold **Shift** / tap **SPRINT**: up to ten seconds of sprint, then five seconds of recovery.
- **T** / **TALK**: nearby NPC dialogue. Use world interaction prompts (**F** on keyboard; on-screen prompts on touch).
- **B** / **SCREAMS**: toggle collection. **M**: map. Quests, Style and Settings are menu tabs.
- **Camera**: third person only, with a six-stud minimum wheel/pinch zoom. Desktop aims at the mouse; touch aims at the centered reticle. There is no V/view toggle.

A microphone and Roblox voice eligibility are required for gameplay. Studio setup without usable voice may remain on the microphone panel. Synthetic fixtures in `tests/` can exercise selected mechanics, but are not a substitute for live voice validation and must never be appended to production source.

## Boost delivery (unpublished local candidate)

Configured boost purchases activate on confirmed server receipt delivery, extending the current expiry by 30 minutes once per receipt. They stack time at 2x; time continues offline. Old saved boosts remain separately usable. Product IDs are not configured, and real receipt delivery is unverified. See [behavior, simulated evidence and limitations](docs/BOOST_PURCHASE_REVIEW.md).

**Combat objectives:** one repeating challenge for three eligible training KOs/assists. The destruction and overlapping Elite challenges are retired; their partial saved counters are preserved but inactive. Eight existing city quests and previously earned rewards are unchanged. See [quest cleanup and pacing impact](docs/QUEST_CLEANUP_REVIEW.md).

## Friend testing and release limits

The unpublished candidate restricts TEST TOOLS to local Studio players or the verified owner in that owner's user-owned experience. Ordinary live players are rejected on the server even if they submit the command directly. This supersedes the candidate's earlier public friend-test flag; the published preview is unchanged. **+10 levels** adds ten test levels up to100, keeps XP below the cap and clears XP at100. It does not equip another style or grant paid entitlements. The first test mutation freezes legitimate progress; test changes use a temporary copy and are not saved. See [test-tool review](docs/DEVELOPER_TOOLS_REVIEW.md). Owner/product configuration is still needed for real pass and badge IDs.

Outstanding release gates include real microphones and eligible accounts, physical device/multiplayer input and performance tests, live save contention/migration checks, completed city art review and a production backup/old-server drain. **Do not publish this branch as a finished release based on compilation or synthetic tests.** See the status log for active test runs and their exact source versions.

### Still unfinished

- Real paid game passes and published Roblox badges: product/badge IDs and ownership/award verification are not configured. Cosmetic options, entitlement hooks, Studio movement testing and in-game Nick achievements exist.
- Two-account live voice listening, permission/reconnect behavior and comfortable-volume calibration across actual microphones.
- Physical phone/touch and multiplayer combat, roll/attack cancellation, traffic impacts, quests and destruction/repair playtests.
- Live test-universe save/rejoin, migration and concurrent-session verification.
- Final city art/game-feel acceptance and measured desktop/phone performance at the intended player count, including a representative 30-minute multiplayer soak.
- Final production rollout/rollback and old-server drain. City Preview is a test publication; the original experience remains separate.

## Quick source checks

```sh
python3 tests/verify_local.py
# Also generate and compile disposable Studio review fixtures:
python3 tests/verify_local.py --build
```

Requires local `luau` and `luau-compile`, plus `rojo` for `--build`. This runs pure/synthetic and mocked-service suites and compiles production scripts; it does not execute Studio, access real saves, upload, or publish. Follow it with the relevant native Studio regression and [manual microphone/device checks](docs/AUTOMATIC_VOICE_PLAYTEST.md). Document failures and untested cases. [Report an issue](https://github.com/anushil7a/scream-simulator/issues) with reproduction steps, build/commit, device and expected behavior.

### Studio movement-pass testing

In local Studio Play, open **TEST TOOLS**, scroll to **Test movement**, and toggle it on. The normal microphone requirement still applies. This grants a temporary movement entitlement only in Studio; safe-area movement limits and arena cooldowns remain enforced. Toggle again to remove it. The server rejects this command outside Studio, including for the owner. No purchase is prompted, and legitimate save progress is frozen before the test mutation. Real pass IDs remain unconfigured.

### Standalone microphone feasibility lab

Build the five-script isolated place with `rojo build mic-prototype.project.json -o build/MicrophoneFeasibility.rbxl`. It shares the production microphone/rule modules but contains no city, saves, rewards or purchases. See [the lab test procedure](prototypes/microphone/README.md). A privately published, two-account real-mic pass remains required; local compile/build results do not prove voice transport.
