# Scream Simulator development roadmap

Updated November 8, 2026. Owner direction in this document supersedes older 300-level/hold-E specifications. Current local baseline: `83d716b`; connected City Preview reports version 15. November 8 owner follow-up authorizes the current update to the main Roblox game after verification and ongoing tested GitHub development-branch pushes. Publication is still blocked by native Studio access; later releases need approval.

## Product direction

The loop is: aim, scream into the mic, fight for space, earn XP and unlock more destructive screams. The city should create interesting combat routes, cover and breakable opportunities. Side activities support that loop. Build fair, readable, responsive combat before paid products or cosmetic breadth.

## Operating policy

- Usage policy updated by owner November 8: continue while allowance remains; check usage at task boundaries and keep work checkpointed. The former 20%-remaining cutoff is superseded.
- Work locally in focused commits and disposable Studio copies. Publishing requires fresh owner approval. Preserve externally changed cloud state and existing saves.
- Maintain completed evidence, known failures and the next concrete action here. Actual audio, hardware and multiplayer gates stay open until observed.

## Ordered backlog

### P0 — progression foundation (implemented locally; native review pending)

- Cap progression/combat at level 100, with a base scream at level 1 and unlocks at 10, 20, …, 100.
- Keep level-specific damage/range/health bounded; preserve old progress/style data when loading 300-level saves.
- Verify unlock boundaries, overflow XP, retired styles, idempotent migration and reload. Produce a local build; do not publish.
- Why first: continuous damage and destruction need a coherent level/balance model, and a cap change must not erase progress.

### P0 — voice-triggered continuous combat (local client/server prototype wired; beam feedback wired; native verification pending)

- Replace hold/release as the default attack trigger. Sustained calibrated voice starts an attack, aiming tracks during the scream, quiet/mute stops it.
- Prototype 4 seconds maximum active time, then 10 seconds cooldown from attack end. Compare with shorter active windows in timed playtests; keep tuning data-driven.
- Use an explicit armed/paused state and clear indicator so calibration, menus, NPC dialogue, typing, spawn protection, rolls, knockdown, death and lost focus cannot attack. Ordinary conversation/background noise is a detection limitation; test a calibrated onset threshold/hysteresis and clear local arm/pause control without requiring E per attack.
- Server owns start/end deadlines, tick rate, damage budget, range/cover/PvP and reward limits. One sustained scream must not become repeated full-damage casts, per-tick XP farming or unlimited destruction. Reject stale/replayed pulses, missing stop messages and aim/power abuse; use server expiry even if the client disappears.
- Rework beam effects as one updated bounded effect per attacker rather than creating an entire old burst every tick. Rework feedback, mic controller and server acknowledgement together.
- Re-test mouse/first-person/touch aim, rolling interruption, short noises, noise during cooldown, reconnect, respawn and silence. Prototype locally before requesting real-mic friend tests.
- Pure modules and integration contract: [SUSTAINED_ATTACK_PROTOCOL.md](SUSTAINED_ATTACK_PROTOCOL.md). The disposable local prototype has client/server wiring, but native Studio and real microphones are unverified.

### P1 — destruction as combat design

- Existing destructibles: bins/benches, trees/bikes and approved building facades. Auto-repair and occupied-repair guards exist.
- Retune health/time-to-break against sustained damage and the 100-level cap. Level unlocks should change tactics, not permit unrestricted whole-map collapse.
- Put useful breakable cover/flanking routes in the arena. Preserve road surfaces, essential buildings, spawn and quest dependencies.
- Verify replication, late joins, occupied repairs, NPC recovery and memory/effect budgets in multiplayer.

### P1 — PvP readability and fair progression

- Keep optional first person, rolls, sprint and visible central arena boundaries.
- Measure time-to-knockout at low/mid/high levels, new-player survivability and damage-per-active-second versus the full attack/cooldown cycle.
- Add readable enemy health/hit confirmation, clear beam/cover feedback and concise combat onboarding where needed.
- Review rewards so player combat/objectives outweigh farming harmless workers. Recommend separating training/fighter targets from occupational residents; implement after reward/quest impact review.
- Consider a simple arena objective (capture/hold a plaza or moving contested zone) only after basic combat is enjoyable; avoid adding multiple modes immediately.

### P1 — bugs, performance and saves

- Inspect the version-15 cloud/source difference before any integration; do not overwrite collaborator edits.
- Reproduce reported failures, add focused regression coverage and measure before optimization.
- Profile server startup/streaming, NPC pathfinding, combat effects and destruction under representative attack/player load. The ~50k-part city and prior early render stall are risk indicators, not proven bottlenecks.
- Real test-universe migration/save contention/rejoin; physical desktop/phone controls and 30-minute multiplayer soak remain required.

### P2 — city supporting the fight

- Keep Barcelona identity, beach, landmark sightlines, authored courtyards and purposeful worker activity.
- Favor denser playable routes and cover over increasing the empty map footprint or NPC count. Limit work to representative blocks/arena spaces and compare street-height before/after views.
- De-emphasize delivery/gardening UI during PvP. Keep Nick as an optional discovery; do not expand side-quest systems before core combat.

### Later — cosmetics and monetization

- Existing style/aura/entitlement scaffolding may remain, but no new cosmetic catalog, badge configuration or paid pass work is prioritized now.
- Review any premium movement only after fairness testing; no paid combat advantage.

## Review findings and recommendations

- **Change:** old hold-E/release flow is mechanically awkward for a microphone game. Continuous voice should be immediate and visibly armed, with bounded server simulation.
- **Change:** old 300-level / 5-level style cadence is spread across Config, Progression, VoiceCombat, UI and profile normalization. A one-constant change would leave inconsistent caps and saves.
- **Keep/refine:** level-gated facade/prop destruction, timed repair, cover and central PvP support the concept. Existing essential-route protection is valuable.
- **Reduce priority:** civilian farming, routine delivery/gardening and cosmetic breadth compete with PvP development. Retain working content while testing a clearer combat reward loop.
- **Performance risk:** blindly firing the existing burst effect and reward handler every frame would multiply VFX, remote traffic, NPC rewards and destruction. Build a dedicated sustained-attack budget.
- **Balance risk:** four seconds active plus ten seconds off is a 14-second full cycle. Test encounter pacing and positioning; do not simply apply four seconds of current per-cast damage every update.
- **Validation gaps:** source/unit/Studio passes do not establish live voice audibility, real-device comfort, saved-data safety or representative multiplayer load.

## Session log

- November 7: management policy and priorities established; owner clarified the cutoff as 20% remaining. Repository clean at review start. Studio in Edit, City Preview version 15 / 30 sources. No cloud writes or publication performed.
- November 7: all 30 version-15 cloud sources match the verified version-14 source record; no collaborator script difference detected. Local progression now caps at 100 and provides 11 styles (base + ten unlocks). Profile schema 4 retains a validated level/XP/style archive and resolves retired style IDs without equipping locked tiers.
- Background continuation configured: active thread heartbeat `scream-simulator-development`, every four hours. It reads this roadmap, checks usage before new tasks, makes local reviewable progress, requires fresh approval for publishing/external pushes, and stays quiet on unchanged blockers or usage cutoff. No manual cron or hidden loop was installed.
- Verification: 508 progression assertions, 1,419 combat/mic/destruction assertions, 370 actual-Config/Profiles migration checks with mocked engine services, 13 actual-Profiles concurrency checks with mocked store; all production sources compile. Both `build/Level100Review.rbxl` and `.rbxlx` build. Progression estimates still model the old 4-second burst cadence and are not forecasts for the proposed sustained attack.
- Native review blocked: Studio connector can inspect the existing cloud place, but native window controls timed out twice. Did not modify that cloud place or restart/discard owner work. Local opening/play and real save migration remain unverified; use the separate Level100Review build when native controls recover. Usage recheck remained 27% used / 73% remaining.
- November 7 heartbeat: usage 30% used / 70% remaining at task start. Working tree was clean. Added independent VoiceActivation and SustainedAttack modules: onset/quiet gating, state cancellation, four-second maximum, ten-second end-based cooldown, input expiry/rate limits, per-target fractional damage and bounded target tracking. All 9,094 pure tests passed; all 32 production sources compile; binary/XML SustainedRulesReview builds succeed. No entry point/remote/VFX integration or real audio test is claimed. No cloud writes, uploads or external pushes.
- New balance finding: the existing ten-second quiet-time healing matches the proposed ten-second attack cooldown. Test regeneration between bursts before choosing final DPS/cooldown; no healing change made in this task.

- November 7 heartbeat: usage 34% used at start and finish. Added a server adapter and Roblox aim validator. The adapter latches server-derived level/amplifier and character identity, rejects stale sample IDs, and resolves targets only on eligible damage ticks using the current origin. Passed 28 adapter checks with mocked geometry and 9,094 pure rules checks. Changed modules compile and `build/SustainedAdapterReview.rbxl` builds. Bootstrap is unchanged; no live or local runtime behavior changed. No publication or push.

- November 8 heartbeat: added opt-in local server wiring. Sustained hits use current server raycasts, PvP/roll/protection checks, level-gated destruction, and bounded NPC and knockout rewards. The prototype rejects legacy cast remotes and uses temporary profiles without loading saves. Adapter (28), sustained rules (9,094), and legacy combat/mic/destruction (1,419) checks passed. Bootstrap and the native fixture compile; `build/SustainedServerReview.rbxl` builds. The fixture was not executed in Studio; no live or external writes.

- November 8 heartbeat: connected the opt-in microphone onset gate to server begin/pulse/stop. Voice starts paused; E or the action button arms it. The HUD reports pending, attacking and cooldown states. Controls wait for the matching server acknowledgement before sending aim updates, stop on blocked input and disarm on focus loss, respawn or unavailable mic. Passed 13 synthetic client checks, 9,094 rules checks and 28 mocked adapter checks. Changed scripts compile and `build/SustainedClientReview.rbxl` builds. No native Studio, real microphone or published behavior verified.

- November 8 heartbeat: added server-driven sustained beams for nearby viewers using the same raycast length as damage. Client updates reuse one part per attacker, capped at 24, with explicit stop/disconnect cleanup and a half-second expiry fallback. Mocked visual lifecycle, adapter and synthetic control tests passed. Changed scripts compile and `build/SustainedBeamReview.rbxl` builds. No Studio rendering or multiplayer performance was measured. Usage was 46% at both boundaries; nothing published or pushed.

## Next action

Check usage, then prepare real-microphone review and inspect current cloud/collaborator state before the authorized City Preview release (90337242377543). The owner screenshot confirms NATIVE_PVP_RESULT true 13 using two local players and synthetic voice, plus SUSTAINED_DESTRUCTION_NATIVE true 11. No repeat of the server-window handoff is needed. Real voice, real save round trips and representative performance remain open. Normal mode stays on legacy combat until review; never publish the disposable fixture.

- November 8 owner follow-up: usage 49% used. Authorized tested GitHub development-branch pushes and requested the current update in the main Roblox game. Native Studio access again returned timeoutReached; no Roblox publication attempted. Sustained combat remains local-only pending engine verification. Future work includes city color/readability, purposeful NPC activity and animations after combat gates.

- November 8 follow-up: pushed commits through `45d5c89` to the authorized GitHub development branch. Re-ran progression (508), combat/destruction (1,419), sustained rules (9,094), adapter (28), controls (13), beam lifecycle, mocked migration (370) and mocked profile concurrency (13); all passed. Added `tests/build_sustained_review.py` and built guarded local play/fixture artifacts. Native execution and publication remain blocked; requested owner restart Studio after saving work.

- November 8 animation follow-up: sustained accepted attacks now hold the existing braced scream pose and blend out on stop; rolls/knockdown still override it. Rig replacement/removal disconnects joint listeners and removes additive offsets. Expanded the native Animator fixture for sustained hold/stop; compiled only, not executed. Native access briefly recovered using `com.Roblox.RobloxStudio`, but the local-file dialog kept Open disabled and subsequently timed out. Owner asked to open the disposable fixture manually.

- November 8 native review recovered after owner opened the fixture. Actual engine server fixture passed six assertions; repeated synthetic remote beam updates yielded one noncolliding/nonquery client part and zero after stop. Native Config/Profiles sanitize passed 28 checks without DataStore round trips. R15 sustained hold/stop and three synthetic roll cycles passed with base Animator preserved. Local microphone remained unavailable; no real audio/multiplayer claim. Test session stopped and animation appendix removed. Next: native PvP/destruction coverage, then clean release build and live voice review before enabling sustained combat outside local mode.

- November 8: added reproducible native sustained destruction fixture and included it in the guarded builder. Native equivalent passed 11 checks for prop damage/break, level25/26 tree gate, spawn protection and roll interruption. Compile/build passed. Release destination clarification pending (original versus City Preview); next native check is two-player arena protection/KO/reward behavior.

- Two-player fixture prepared and compiled, not executed. Native UI coordinate actions return `noWindowsAvailable` for the inaccessible client-count control even though menu/command-bar accessibility works. Requested owner set Server & Clients to 2 and start the disposable session. `_G.RunSustainedPvp()` is ready in its server context. Current fixture copy contains test appendices and must never be published.

- Owner confirmed the current release destination: City Preview `90337242377543`. Usage 52% used. Two-client count is visibly 2, but the connected Studio window reports Edit mode, zero players and no runtime helper; requested launch or foreground of the actual server window. No PvP pass or publication claimed.

- November 8 late heartbeat: usage 53% used, working tree clean at entry. Owner-command handoff remains pending after a fresh connection still selected the editor; no new runtime result, publication or feature change. Updated next action to avoid repeating completed tests or asking the owner to foreground the same window again.

- November 8 server screenshot confirms the owner executed the command in Server context, but `_G.RunSustainedPvp` was nil. This is a missing test entry point, not a PvP failure; stale fixture versus Command Bar global isolation is not yet distinguished. Added a server-only BindableFunction entry point and explicit NATIVE_PVP_READY marker to the disposable fixture, with concurrent invocation guard. Combined script compilation and both local builds pass; rebuilt fixture has not been executed. Reopen build/SustainedNativeFixture.rbxl before starting two clients. Usage 53% used; no production changes or publication.

- November 8 22:49 owner-provided Studio Output screenshot: NATIVE_PVP_READY appeared; server BindableFunction invocation returned NATIVE_PVP_RESULT true 13, two local players with synthetic voice. This verifies arena damage, safe-area rejection, protected/rolling targets, KO ejection/heal/protection and repeat-KO reward suppression in the native fixture. The same screenshot shows SUSTAINED_DESTRUCTION_NATIVE true 11. Temporary-profile warning is expected for this isolated fixture; no real save/voice verification or publication claimed. Test entry-point fix is now native-verified. Usage remains 53% used.

- November 8 release follow-up: owner again authorized publication of the current code to City Preview and continued improvements/GitHub pushes. Studio native End Session, Recent City Preview and Open from Roblox actions returned unchanged fixture UI; no release attempted. Asked owner to end the local session and open cloud City Preview for collaborator comparison. Clean CityPreviewLatest binary/XML rebuilt from default.project.json and checked to exclude native fixture appendices. Sustained remains local-only; production build retains hold/release controls.
- Combat HUD refinement: sustained-mode button no longer overwrites spawn protection; meter explains protection, roll, recovery and typing suppression, with green accepted-attack and muted paused/cooldown colors. Client compiles, clean build succeeds and 13 synthetic controls checks pass. Native visual inspection is pending; no real-voice or new publication claim. Usage 53% used at entry. Next: inspect owner-opened cloud copy, preserve collaborator differences, verify production candidate and publish authorized update; separately validate live voice before enabling sustained mode outside the fixture.

- Release XML audit correction: Rojo emits Source as string rather than ProtectedString; repeated audit across all 36 actual source properties with a nonempty-script assertion confirms no disposable fixture markers. Initial zero-source scan was not valid evidence.

- November 8 23:00 release retry after owner closed all tabs: opened cloud City Preview successfully. Read-only native command confirmed place 90337242377543, universe 10769005350, version 17, Edit mode. All 30 script lengths and rolling fingerprints match baseline 55563b3 (including City/World); no script collaborator changes found. Attempted Download a Copy backup: native Save remained disabled after filename entry, coordinate click returned noWindowsAvailable, Cancel and Escape timed out. No backup completion, source modification or publication claimed. Owner action needed only to dismiss native Download a Copy dialog; latest clean release is build/CityPreviewLatest.rbxl.

- November 8 restart retry: successfully opened build/CityPreviewLatest.rbxl through Recent. Native preflight passed: PlaceId 0, 36 production sources, MaxLevel 100, no LocalSustainedPrototype attribute or fixture markers, modern chat/default commands/channels, Audio API/default voice and streaming radius 512. Opened Publish As; destination picker remained loading and coordinate interaction returned noWindowsAvailable. No upload confirmation or new cloud version observed. Current owner handoff can select existing City Preview and overwrite once picker loads; never create a new experience. Usage 55% used.
