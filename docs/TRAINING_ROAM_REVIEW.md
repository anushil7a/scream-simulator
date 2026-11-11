# Bounded roaming training enemies

November 11, 2026. Based on clean/fetched `44ee830`; unpublished draft branch only.

## Behavior

The Rookie, Brawler and Elite now use server-owned humanoid movement at seven studs/second. Deterministic waypoints stay within 18 horizontal studs of each original pad home. Waypoint decisions are limited to four per second, each movement attempt expires after five seconds, and arrival/timeout pauses for 1.25 seconds. No city path coroutine, pursuit, new enemy, or map geometry is added.

An active windup, conversation/reaction, anchoring, seating or PlatformStand cancels the pending MoveTo before the waypoint cadence check. After interruption, movement waits another half second. Counterstrikes still aim at the original fixed point and preserve dodge/protection rules.

Displacement beyond 22 horizontal studs recovers the trainer to its own home, clears stale grounding and velocity, and pauses. This is a recovery leash, not a guarantee against transient physics displacement. It does not heal, erase damage credit, reset attacks or award anything. At defeat the existing hidden/anchored recovery state remains. Full-health reset/respawn clears pending movement and returns a mobile, server-owned trainer home. The old recovery-version guard still prevents stale callbacks reviving a newer life.

Both player attack paths and counterstrike eligibility still measure the player from the original home using the existing 32-stud 3D radius, not distance from the roaming trainer. A player outside that boundary cannot gain a hit just because the trainer is nearby. Health, damage, rewards, protection, reset/respawn timings, progression and all save code are unchanged; Bootstrap is byte-unchanged.

## Reproduction and checks

Before editing, the baseline explicitly anchored trainers with zero walk speed; full-health restoration reanchored them. `tests/training_roam.py --baseline` reproduces all three missing/mobile-state expectations. Current suite runs extracted production movement, stop/reset, delayed-revival, automatic quiet-reset and all three fixed-home predicates with fake humanoids/clock.

- 1,292 assertions pass, including 300 waypoints, stuck timeout/rest, all interruption branches, detached objects, damage without teleport, leash impulse/credit preservation, defeat/reset/stale callback/respawn and pad/vertical boundaries.
- Eleven negative controls fail at their intended assertions: widened waypoint radius, omitted cadence/deadline, omitted strike/PlatformStand pause, reanchored restore, stale callback guard, uncleared KO movement, target-relative combat gate, missing quiet reset and inclusive early reset.
- Full 25 pure/synthetic suites, 70 mocked suites, 57 production compiles and all candidate/disposable builds pass. Independent review reran focused tests and controls, found no production blocker, and corrected the fixture issues below.

## Native Studio evidence

`build/TrainingRoamReview.rbxl` is guarded to unpublished local Studio, uses temporary profiles and omits the main live microphone client. It retains the actual World/Bootstrap and resident/animation clients. Its appended test uses synthetic readiness/positions and server helper calls, not RemoteEvents or real voice.

The corrected run passed **29 checks** at **2026-11-11T17:20:45.492Z**. During 564 heartbeat samples over twelve seconds, all three trainers moved horizontally: Rookie 14.081, Brawler 16.253, Elite 16.729 studs maximum from home. The active-walk precondition and persistent synthetic strike both passed, followed by stopping during windup. Displacement recovery preserved health/credit; full reset, hidden defeat, delayed respawn and renewed horizontal movement passed. The actual sustained resolver accepted 31.9 and rejected 32.1 studs from original home with the trainer moved eighteen studs toward the player.

The first run is explicitly excluded: the builder reused a project mutated by the transport fixture, leaking its synthetic Client. It failed the windup assertion and later emitted a transport assertion. Each build now gets a deep copy, the trainer fixture explicitly omits the main Client, and movement assertions use horizontal distance with an active-walking precondition. No production workaround was made for that fixture failure.

Exact native artifact SHA-256: `94cd5bfcd5d58a1bf6e24f272b785a1c143a0aa6cb57d9fbef720318b188ffa0`. Source fingerprint: `5f7e53f5e4957b9bbb5a109cdfcdba44e8b6b697ed76c889efc54e33ded36cbd`. [Machine-readable evidence](../tests/evidence/training-roam-2026-11-11.json) retains both outcomes and production hashes.

## Limits and cleanup

No native mutation control, live microphone, physical touch, internet transport, multi-player pushing, representative performance/soak or live-save test. The native social interval stayed stationary but did not independently isolate conversation as its cause; the synthetic test does. Player/obstacle pushing, falling, streaming and visual movement quality remain release checks. The local run logged the existing asset203785492 type mismatch and avatar mesh access warnings; their origin is not established as a production defect.

Studio was stopped and closed; no publication, live persistence, purchases or audio configuration. Launching installed Studio created another minimized app-picker dialog. Three such dialogs now remain inaccessible to supported control; no process kill or blind close was attempted. Preexisting work is untouched. Avoid further launches until that cleanup limitation is resolved or a native check justifies it.
