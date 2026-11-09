# Sustained voice prototype contract

November 8, 2026. The client and server are wired in the disposable local prototype; native Studio behavior and real microphones have not been verified. Normal gameplay still uses hold/release.

## Local voice activation

`Shared.VoiceActivation` consumes normalized calibrated power and explicit armed, allowed and ready flags. It returns a single `start` or `stop` transition, not attacks per frame.

- Require 0.2 seconds quiet before arming/rearming, then 0.25 seconds at or above 35% power to start.
- While active, power at/below 18% for 0.2 seconds stops the attack. Hysteresis tolerates short dips; an isolated pop cannot start one.
- Menus/dialogue, typing, calibration, lost focus, mute/disconnect, protection, roll, knockdown, death and cooldown must set appropriate flags or call `Cancel`. The caller must cancel on server denial or the maximum-duration limit too.
- A cancellation requires fresh quiet and fresh voice; speech during a blocked state cannot be queued into a later attack.
- Large frame deltas contribute at most 0.1 seconds of onset/quiet. The module stores only timers, never recordings.
- Thresholds are initial proposals for comfortable calibrated voice, not physical decibels or reliable classification of human screams. Real-microphone tuning remains required.

## Server attack protocol

`Shared.SustainedAttack` consumes **server time**, a sequence number, trusted server-derived DPS, normalized reported power and an allowed-state flag. Clients cannot select the DPS, targets, hit geometry or time.

- Begin: consumes increasing integer sequences, rejects illegal state/power/budget, an active attack or cooldown. A repeated begin never refreshes an active deadline.
- Pulse: accept at most ten samples per second for the active sequence. Too-fast pulses do not refresh the input timeout. Missing input expires at 0.5 seconds; low/invalid power or forbidden state stops damage.
- Step: resolve at most one damage quantum per 0.2 seconds, using current server-filtered target IDs. Never backfill multiple damage ticks after a stall; each step accounts for at most 0.25 seconds.
- Duration: at most four seconds from accepted begin. Cooldown is ten seconds from the actual stop/earliest expiry time, even if expiry is observed late.
- Damage: accumulate fractional damage separately per target while it is present. Late entrants do not inherit earlier damage; duplicate target IDs or steps cannot duplicate damage. Target tracking is bounded to 128 identities per attack and cleared at end.
- `firstHit` is emitted once per target when positive damage first applies. The adapter must retain normal reward/KO guards; it must not pay per tick. The pure module does not award XP/coins, apply Humanoid damage or destroy anything.
- Current hard DPS ceiling is 24. Proposed adapter budget: `VoiceCombat.Stats(level, 1, false).damage * 0.75`, giving 13.5–21 full-power DPS across levels 1–100, with `(0.45 + 0.55 * effectivePower)` scaling. This is initial tuning, not a balanced live result.

The adapter must supply unique stable IDs for players, bots and destructible objects, after reconstructing origin/aim/range/width/cover/PvP/protection/dodge eligibility on the server. Re-evaluate permission each tick; preserve exact whole damage and per-object eligibility when applying returned budgets. Do not trust client lists of targets or damage.

## Server adapter seam

`ServerScriptService.SustainedAttackAdapter` is ready for Bootstrap wiring. Supply the two rules modules and `SustainedAim` to its factory. Begin/pulse take a server context with current character identity and origin, or nil when gameplay state forbids an attack. Begin also reads the server level and amplifier flag, which remain fixed for that attack. Each pulse carries an increasing per-attack `sample` integer in addition to its attack `sequence`. Fresh but rate-rejected samples are consumed; only accepted pulses update aim.

Step rechecks character identity and reconstructs direction from the current origin. Its resolver callback is invoked only for a due damage tick with fresh input. Return server-selected target IDs, an ID-to-target detail map and optional beam metadata. Apply returned damage only to those resolved details. Begin and pulse may also return expiry metadata even when the new request is rejected. The opt-in Bootstrap path now supplies the network handlers, target resolver and damage application. Sustained beam visuals use the resolved server geometry.

`luau tests/SustainedAttackAdapter.luau` passes 28 checks with mocked geometry, including client-forged fields, aim reconstruction after movement, sample replay, respawn, expiration and duplicate ticks. Roblox raycasts and gameplay remain untested.

## Disposable server prototype

Open a local build with PlaceId 0 and set the boolean Workspace attribute `LocalSustainedPrototype` to true **before** Play. The server reads it once at startup. This mode uses temporary profiles and rejects legacy begin/cast/cancel requests. Normal places ignore the opt-in.

Send `SustainedBegin` and `SustainedPulse` on the existing Action remote with aim, power, sequence and (for pulses) an increasing sample ID. Send `SustainedStop` with the sequence number. Player attributes `SustainedActive`, `SustainedSequence` and `SustainedReadyAt` expose accepted attack and cooldown state. Server ticks use raycasts and the existing cover/PvP eligibility rules. NPC hit rewards are limited to first damage per target and five paid targets per attack; knockout cooldown and destruction level checks are retained. Practice targets, soccer, volleyball, and crowd/evade quest updates remain legacy-only pending design and testing.

`tests/StudioSustainedDamage.server.luau` can be appended to Bootstrap in the disposable copy to check cover, tick damage, first-hit rewards and stale input. It compiled but was not run natively. Do not publish that fixture or infer verified engine behavior from the build.

## Disposable client controls

In the same opt-in place, calibrate the microphone, then press E or tap **ARM VOICE**. Aim and speak after a short quiet interval. The HUD displays pending start, active attack and server cooldown. E or **PAUSE VOICE** cancels immediately. Menus, dialogue, typing, and movement/protection states suppress attacks; focus loss, unavailable microphone and character removal disarm voice. The client waits for the matching server sequence before sending pulses, sends at most eight pulses per second, and stops waiting after 0.4 seconds. Voice transport remains Roblox proximity audio.

`luau tests/SustainedControls.luau` exercises the controller with synthetic power, time, aim and acknowledgements. It does not execute the Studio UI or remote transport. `build/SustainedClientReview.rbxl` requires the Workspace opt-in attribute before Play.

## Integration still required

1. Verify arm/pause, microphone onset, cancellation, and acknowledgement in a local Studio session.
2. Verify the wired adapter in Studio, including cover, PvP, destruction, legacy remote rejection and expiry.
3. Verify beam rendering, cleanup and measured replication rate in Studio. The local renderer reuses one part per attacker, caps visuals at 24, and expires missing updates after 0.5 seconds plus the cleanup poll interval. Server updates are limited to due damage ticks (at most five per second per attacker) and viewers within 180 studs. These bounds are design limits, not measured performance.
4. Keep NPC/KO/destruction rewards bounded per sustained attack. Review existing soccer/volley handlers separately: calling them on every damage tick would change their difficulty and ball physics.
5. Revisit healing: current 20% regeneration begins ten seconds after damage, matching the proposed cooldown. Measure how much healing happens between bursts and how that changes time-to-knockout.
6. Verify in a disposable local city, then request owner-approved real mic/multiplayer testing. No cloud edits or publication are authorized.

## Evidence

`luau tests/SustainedAttack.luau` passes **9,094** pure assertions across all 100 levels, deadline/cooldown boundaries, stale and spammed messages, interruptions, late targets, fractional budgets, resource caps and voice onset/quiet/cancellation. All 32 production sources compile, and binary/XML `SustainedRulesReview` builds succeed. These tests have no remote transport, geometry, humanoids, real microphones, devices or multiplayer participants; they cannot establish those behaviors.

## Reproducible native review builds

Run `python3 tests/build_sustained_review.py`. This builds two **DO NOT PUBLISH** local places with normal ModuleScript loading and a startup guard requiring Studio and PlaceId 0:

- `build/SustainedLocalPlay.rbxl`: prototype enabled before server startup; use for manual client/server and real-microphone review.
- `build/SustainedNativeFixture.rbxl`: additionally appends synthetic server fixtures; press Play and inspect Workspace `SustainedDamageResult` and `SustainedDestructionResult` for JSON results. This checks server cover/damage/rewards/expiry with synthetic power, not real audio.

Both use temporary profiles through the existing prototype guard. The normal project and production Bootstrap source are unchanged by the builder. Do not publish either artifact. Successful assembly/compilation is not native execution evidence.

### Two-player local arena check

The native fixture build also provides `_G.RunSustainedPvp()` in the server context. Start **Server & Clients** with two local players, wait for both avatars and startup fixtures, then execute it from the **server** command bar. It uses temporary profiles and synthetic voice to check protected/rolling targets, arena-only damage, KO ejection, protection/rewards and repeat-KO reward suppression. It does not establish real microphones or multiplayer performance. Native execution pending.
