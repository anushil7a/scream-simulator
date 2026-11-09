# Scream Simulator development roadmap

Updated November 9, 2026. Working branch: `codex/microphone-combat`. This document supersedes conflicting requirements in the earlier professional redesign brief.

## Contributor coordination

This branch is a focused prototype based on `main` at `ed336cf`. A separate, substantially broader redesign is already under review in [PR #1](https://github.com/anushil7a/scream-simulator/pull/1), branch `feature/microphone-city-redesign` (observed at `8814d76` on November 9). That branch has its own microphone controls, progression, city, tests and roadmap. This prototype does not replace that work and must not be merged wholesale over it. Compare both implementations and reconcile overlapping code before integration. Before each new task, fetch contributor updates and inspect that PR to avoid duplicating completed work. The verification below applies only to this prototype.

## Owner decisions

- Core game: microphone-triggered scream-to-attack PvP. No E-key attack. Damage happens while the voice is active, up to **5 seconds** per attack.
- Initial cooldown: 10 seconds after an attack ends, including early cancellation. Tune through playtesting.
- Level cap: 100. Starter scream at level 1, then one unlock every 10 levels through 100.
- Prioritize combat, bugs, performance, progression and testing. Cosmetics and Robux monetization come later.
- Implement and test locally, then update GitHub so contributors stay caught up. Push tested source, rebuilt place files, tests and roadmap changes to a feature branch and maintain a pull request with verification and known limitations. This standing GitHub authorization was granted November 9, 2026. Publishing or uploading the experience to Roblox still requires owner approval.
- Stop starting new tasks when 50% or less of the Codex allowance remains; finish the task already underway. Check actual account usage before each new milestone. Missing usage data is not permission to assume capacity.

## Current local milestone

Implemented: calibrated microphone onset/release detection; server-controlled attack duration, damage ticks and cooldown; cancellation on silence, dodge, knockdown, respawn, protection and equip changes; client pause during menus and loss of focus. The server rejects old Cast requests and malformed, stale or excessive voice values. Client amplitude is untrusted: the server bounds damage and timing but cannot prove a real person produced the sound.

The microphone setup samples quiet room noise and a comfortable voice. Players need not strain their voice. Audio amplitude is measured locally with Roblox AudioAnalyzer; this code does not record audio or send it to an outside service. Roblox's existing default voice behavior remains enabled.

Progression includes 11 tiers, with existing sound IDs retained. Existing earned unlocks are preserved when old profiles migrate. Health, range and damage per second are provisional balance values, not final PvP balance. Max health is 204 at level 100. Effects reuse the existing visual families; original sound design remains future work.

## Verification

- Standalone Luau timing suite: 29 assertions pass, covering five-second maximum, bounded cumulative damage time, cooldown, heartbeat loss, malformed input, stale sequences, silence and fresh-voice onset.
- All 13 source Luau files compile. Both `.rbxl` and `.rbxlx` builds succeed; `git diff --check` passes.
- Local Studio prototype opens and generates the city. Level 100 and 204/204 health were observed in the HUD.
- Profile migration assertions passed inside Studio: retained coins, old unlocks and equipped scream; repeated sanitization; new-profile restrictions; cap 100; all 11 unlock levels.
- Live microphone capture is **not verified**. The unpublished local place reports microphone access unavailable. Real voice and two-player combat acceptance remain open.
- Synthetic server integration uses a separate disposable build with Studio-only eligibility injection. It must never be shipped; the actual project retains Roblox voice eligibility checks.
- Synthetic client/server integration passed in Studio: malformed and legacy requests rejected, duration enforced, restart blocked during cooldown, restart accepted afterward, and dodge cancels with cooldown. Log marker: `SCREAM_INTEGRATION_PASS`, November 9 at 21:30:47 UTC. The initial fixture raced character spawn; rerunning after spawn/protection completed passed. The fixture preparation now explicitly waits for the protection attribute to exist and expire.
- Existing public TEST TOOLS remain enabled by the owner's previous choice and disable saves on use. This is a local prototype, not a production readiness claim.

## Next work, in order

1. Validate real microphone input in an owner-approved voice-enabled test experience: setup, quiet room, background noise, mute/unmute, device changes, silence release, five-second hold, ten-second cooldown, menu focus and dodge. Publishing the test experience needs separate approval.
2. Run two-player targeting tests: front/side/rear, walls, range, safe zones, protection, dodge and knockout. Test delay and dropped heartbeat recovery. Verify quest and reward behavior under sustained attacks.
3. Measure desktop/mobile frame time, city startup, NPC updates and effect/remote traffic. Optimize measured bottlenecks. Test portrait and landscape HUD and microphone status readability.
4. Review save concurrency and failure recovery before live progression tests. Existing UpdateAsync snapshot saving needs a multi-server/session review. Retry transient voice eligibility failures and improve unavailable-microphone onboarding.
5. Tune damage, health, XP curve and progression through friend playtests; test full quest flow and persistent migration in an isolated test store.
6. Only after the core loop is reliable: unique audio/visual identities, cosmetics and monetization.

## Working practices and commands

Reuse the existing local checkout and inspect its status before changing files. Do not overwrite unrelated edits. Maintain this roadmap with completed work, test evidence and remaining limitations after each bounded task. Read CONTRIBUTING.md before rebuilding.

A daily 10:00 AM development follow-up is active in the current Codex chat, with the same usage cutoff and approval boundaries. Automation ID: `continue-scream-simulator-development`. It selects one bounded task per run; execution depends on the Codex host being available.

```powershell
luau tests/combat-timing.luau
rojo build default.project.json -o ScreamSimulator.rbxl
rojo build default.project.json -o ScreamSimulator.rbxlx
```

Compile changed Luau files with `luau-compile`. Tool binaries are installed in `%LOCALAPPDATA%/Programs/ScreamSimulatorTools/bin` (Rojo 7.7.1, Luau 0.746, StyLua 2.6.0). Roblox Studio, Blender, Audacity and Krita are available. No additional runtime framework is needed for this milestone.

Relevant Roblox references: [VoiceChatService](https://create.roblox.com/docs/reference/engine/classes/VoiceChatService), [AudioDeviceInput](https://create.roblox.com/docs/reference/engine/classes/AudioDeviceInput), [AudioAnalyzer](https://create.roblox.com/docs/reference/engine/classes/AudioAnalyzer).
