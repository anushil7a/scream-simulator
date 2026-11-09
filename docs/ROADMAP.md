# Scream Simulator development roadmap

Updated November 8, 2026. City Preview version 19 is published and verified; its completed release still uses hold/release. The current unpublished candidate defaults to automatic voice, with NPC, animation, district-color and repair scheduling refinements. GitHub development pushes remain authorized; another Roblox upload requires fresh approval. Studio runtime control currently times out; owner permits continuing independent work while recording pending manual checks.

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

Check usage and current tree. Continue bounded automatic-voice integration review, destruction/progression balance, and measured performance; inspect district color and NPC pose/path changes when Studio becomes available. Use build/AutomaticVoiceCandidate.rbxl for the normal-profile candidate or build/SustainedLocalPlay.rbxl for isolated temporary-profile tests. Do not retry the same Studio timeout repeatedly. Human/device checks are listed in docs/AUTOMATIC_VOICE_PLAYTEST.md and may remain pending while independent work proceeds. Version 19 is already published; do not upload again without approval.

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

- November 8 23:15 owner completed publishing handoff. Reopened cloud City Preview reports place 90337242377543, universe 10769005350, version 19. All 36 source lengths/rolling fingerprints match current local production sources; Config.MaxLevel is 100. All four native serialized configuration checks pass (modern chat, default commands/channels, Audio API/default voice, streaming), and prototype opt-in is absent. Current authorized upload completed via owner UI handoff and agent cloud verification; no standing authorization for repeated releases. Live real-mic gameplay/save/soak evidence remains open; published mode still uses hold/release, sustained mode remains local-only. Next: live microphone validation and bounded combat/progression review before enabling sustained mode; then city/NPC/animation readability and measured performance.

- November 8 automatic-voice candidate: Config.AutomaticVoice now enables sustained combat in normal local builds while local fixture isolation alone selects temporary profiles. Client auto-arms after first calibration behind quiet/onset gating; pauses/mute/death do not silently re-arm. Updated mode-neutral mic guidance, retained one impulse per attack for soccer/volleyball, practice feedback and bounded Crowd/Evade quest credit. Passed 17 synthetic controls, 9,094 pure rules, 28 mocked adapter checks; all 36 production sources compile and disposable builds succeed. New native interaction and real-mic checks pending; owner permits moving to independent work when human tests are unavailable. Version 19 remains unchanged. Next: review interaction regressions/normal-profile runtime and create a dedicated real-mic checklist, then city/NPC/animation/UI tasks.

- NPC route/pose refinement: ignore path-block notifications behind the active waypoint; timed-out waypoints now abort and stop instead of skipping ahead through obstacles. Resident work/gesture/rest/walk and stumble transforms blend exponentially at existing distance-based update rates. Changed scripts compile; automatic-voice candidate and native fixtures build. Native review attempt hit Studio timeout after closing the verified cloud view; owner requested proceeding to independent work rather than waiting. Visual/obstacle reroute verification remains pending; no performance gain claimed.

- City color refinement: refined frontages now use district-specific palettes with deterministic per-building shade variation rather than the same four paints throughout the entire city. Maritime blocks use sea-green/blue shutters; Born stays warm plaster, Modernista includes muted greens/rose, Eixample remains sunlit stone. No geometry, roads, collision or NPC destinations changed. City compiles and candidate builds; visual acceptance pending because Studio control is unavailable.

- Automatic voice HUD: added a server-derived active-attack deadline so players see remaining speaking time, not just a generic attacking label; cleared on end and initial join. Touch voice button no longer advertises the E key. Compiles and candidate builds; physical-device/UI verification pending.

- Added AutomaticVoiceFlow.luau: nine simulated calibrated-RMS → onset → client transport → server adapter/damage checks pass, including background suppression, four-second stop/budget, no restart from voice held throughout cooldown, fresh quiet rearm, UI cancellation, missing-pulse expiry and mic reconnect pause. This uses synchronous fake transport/scalar geometry, not real voice/network. Updated native first-person fixture to test camera-switch cancellation in either combat mode; compile only. Reviewed aiming against Roblox official laser tutorial; existing GetMouseLocation/ViewportPointToRay pairing is correct and unchanged.

- Sustained-destruction scheduling: replaced one delayed repair task per accepted hit with one pending repair timer per object that follows the latest hit deadline, retries occupied repairs after five seconds and exits when object is removed. Maintenance can finish while timer waits without restoring twice. Eight injected-clock tests pass: 600 hits produced two total wakeups and at most one pending callback (synthetic scheduling evidence, not measured FPS/server time). Destruction compiles and candidate builds; native occupied-repair/maintenance regression remains pending.

- Aim lifecycle hardening: camera-ray lookup now returns no aim while CurrentCamera is absent or its viewport is not initialized; both automatic and legacy callers cancel/skip rather than indexing a missing ray. This protects spawn/camera replacement transitions. Client compilation and automatic control/flow checks pass; engine camera-replacement reproduction remains pending.

- Added local resident secondary animation: subtle footfall body motion, idle breathing/glances, reading head tilt and work lean. These reuse existing custom R6 root/neck joints and distance-based update frequency, with no new replicated instances or per-frame server messages. Residents compiles and candidate rebuilds; appearance/rig blending still awaits native visual review.

- Scheduled continuation updated in place (existing active four-hour heartbeat): recognizes completed version-19 release, unpublished automatic candidate, pending manual tests and permission to continue independent work. No duplicate automation or background process installed. All current work pushed; generated candidate and disposable fixtures rebuilt from current source.

- Immediate continuation requested by owner (not waiting for scheduled heartbeat). Added 16 actual Destruction service checks with mocked engine objects/scheduler: restores collision/seat/prompt originals, defers occupied repair, respects subsequent-hit deadlines, removal and maintenance interactions. Added server-confirmed cumulative damage feedback for sustained attacks; counts only applied damage (not blocked/level-rejected hits), rounds fractional finishing health for display and sends one update per damaging tick to the attacker. Fourteen pure presentation checks cover expiry, duplicates, out-of-order totals/sequences and invalid data. Scripts compile and candidate builds; native HUD review pending.

- Escape-menu interruption fix: Roblox CoreGui menu now blocks attack/input, immediately disarms voice and stops sprint; closing it requires explicit resume and fresh quiet. Shared focus/menu suspension path avoids divergent behavior. Five added simulated mic-to-server interruption checks pass (14 total); client compiles. Real CoreGui event/device verification is pending in the manual checklist.

- Added 70 deterministic sustained-balance checks using actual attack/stats/destruction rules with perfect aim and synthetic pulses. Representative full-power player matchups require 2–5 attacks and overcome current quiet healing; destructible tiers take 1–5 full attacks at unlock and remain level-gated. Important tuning concern: level 1 attacking level 100 at onset-strength power (.35) took 16 attacks / 218.8 seconds with current 20%-per-ten-quiet-seconds healing. These are simulation assumptions, not playtest times; do not call the 4s/10s cadence balanced yet. Next balance review should compare comfortable calibrated power, mixed-level matches and healing/cooldown together before changing live tuning.

- NPC grounding recovery now invalidates the old route and clears working/audience/seat state before returning an airborne resident to its last grounded position. Previously the still-running route coroutine could resume toward its pre-recovery waypoint. World compiles; candidate and both disposable fixtures rebuild. Native forced-fall/route-recovery observation remains pending; no claim of an executed physics test.

- Verification workflow repair: reproduced legacy UI harness build failure from unsupported requires and stale module lists. Bundler now resolves repository literal dependencies transitively, rejecting unknown/circular/ambiguous modules; UI fake remotes advertise automatic mode. Added `python3 tests/verify_local.py --build`: all 13 pure/synthetic suites and four mocked-service suites pass; all 38 production scripts compile; local/native/UI harnesses generate and compile. This command performs no Studio execution or publication. README now documents the unified check.

- Collection/control readability: scream cards now show automatic-mode DPS, maximum duration and actual cooldown rather than legacy burst damage/4s cooldown. Shared DamageScale drives both adapter and readout (no tuning change); two-line cards have more vertical space, collection subtitle resets after visiting other tabs, and touch dodge/sprint labels omit keyboard keys. Unified local verification/build passes; phone/desktop visual fit still pending.

- Camera/menu UI lifecycle: resident label selection now handles missing CurrentCamera by clearing labels/target instead of calling a method on nil during camera replacement. Added two native fixture assertions (compiled, not executed). Talk and zone overlays now follow the same gameplay visibility as the rest of the HUD, including Roblox menu interruptions. Client/fixture compilation passes; native camera replacement remains pending.

- City art pilot: seven selected rear courtyard walls now receive original asset-free sun/sea or neighborhood-flower murals, with maritime and inland motifs. Each adds one non-colliding/non-query decorative panel and a distance-limited SurfaceGui; no road, entrance, window, navigation or destructible collision changes. Source compiles and candidate builds. This is a small art pilot, not a claim that the city has passed visual/performance review; street-height composition and device rendering remain pending.

- Fixed sustained NPC KO rewards: later damage ticks can now top up an already-paid hit to the existing full KO reward (total 5 coins/16 XP), rather than losing the KO bonus because firstHit was false. Shared pure budget retains five paid victims per attack, victim cooldowns and duplicate-KO rejection; no new reward amounts. 27 focused reward checks pass. Unified verification now passes 14 pure/synthetic suites, four mocked-service suites, compilation of 40 production scripts and review fixture builds. Native KO integration remains pending.

- Microphone lifecycle coverage/cleanup: actual Microphone controller passes 18 mocked audio/time checks covering calibration, failed retry, mute cancellation, input replacement, teardown and late eligibility responses. Main client now calls Microphone.Destroy on teardown, removing the analyzer and heartbeat listener. Unified check passes 14 pure/synthetic suites, five mocked-service suites, 40 script compilations and fixture builds. No actual microphone/device/voice-transport result is inferred.

- Owner-requested immediate continuation: existing heartbeat updated from four-hour to five-minute follow-ups in this same thread, with explicit pause on exhausted allowance and no paid credits/resets. Current batch completed and pushed through microphone lifecycle cleanup; candidate and fixtures remain unpublished. Next: inspect player/NPC animation teardown and streaming transitions, then a representative native city/UI review when Studio control becomes available; keep real-mic and mixed-level balance gates open. Latest account check was 59% used, so allowance remains.

- November 9 animation lifecycle: player animation now disconnects player/character/frame listeners, removes its additive joint offsets on teardown, avoids duplicate watches and rejects delayed rig registration after departure/destruction. Resident animation now resets owned joint transforms and removes local practice props on tag removal/teardown. Eighteen checks execute the actual scripts against mocked events/rigs (11 player, 7 resident); they cover respawn, departure, queued registration, duplicate tags, cleanup and stream-out-style tag removal. This is lifecycle evidence, not Animator/physics/visual validation. Next: native animation/streaming review when accessible; independently inspect combat UI/state synchronization.

- November 9 combat HUD: health now follows the replicated character Humanoid instead of waiting for periodic full-state packets. It keeps the last observed value during character gaps, handles death/respawn/max-health changes, clamps fill and avoids rewriting unchanged values. Nine checks run the actual display function with mocked replicated/UI values; no real network latency claim. Also removed a competing collection subtitle assignment that alternated text on state refresh. Next: native damage/respawn HUD check and continued combat-state review.

- November 9 knockout recovery: ejection now clears linear/angular momentum, knockdown/roll/sprint state and animation attributes, restores upright control and automatic network ownership, while preserving dodge cooldown and sprint budget. Vehicle recovery callbacks reject canceled knockdowns, replaced sessions and replaced characters, preventing an old car timer from moving the avatar again after KO. Eleven tests execute the actual reset/callback against mocked character/session state; no physics/network-ownership runtime claim. Next: native car-hit → PvP KO interaction test and continued authoritative combat-state review.

- November 9 authoritative dialogue interruption: accepting NPC dialogue now cancels sustained/legacy attacks on the server, and capture eligibility rejects attacks during a valid nearby conversation. Expired, distant, removed/dead or reassigned NPC conversations do not leave combat locked. Fourteen tests run actual server eligibility with mocked character/dialogue state. Native delayed-stop/dialogue integration remains pending. Next: native dialogue interruption and independent session/respawn state review.

- November 9 server respawn lifecycle: character removal immediately cancels attacks and closes dialogue; new characters clear stale knockdown/roll/sprint attributes while preserving the existing dodge deadline. Spawn handlers reject departed/replaced sessions and obsolete characters, and duplicate initialization cannot heal/reprotect the same avatar. Twelve checks execute the actual handlers with mocked characters/events; native reset/respawn remains pending. Next: native full respawn sequence and inspect streaming-dependent UI/interaction behavior independently.

- November 9 PvP target readability: aiming at a player now uses the existing central readout to show their server-published level, replicated health and safe/protected/dodging/out-of-maximum-range status. It only follows the existing cursor/center ray hit, adds no floating crowd labels and leaves server targeting unchanged. Nine actual text-helper checks pass with mocked state; source compiles. Native avatar/accessory ray targeting and phone text fit remain pending. Next: native targeted-player UI/cover review; independently inspect movement and interaction synchronization.

- November 9 sprint stamina: server now drains stamina only during horizontal movement with sprint requested and movement available. Standing still, vertical-only motion, seated/ragdoll states, rolls, knockdown and unavailable mic no longer consume sprint charge. Preserved ten-second capacity and five-second exhaustion recovery using shared config. Fourteen actual-helper checks use synthetic velocity/time; native movement responsiveness and replication remain pending. Next: disposable sprint/roll/car interaction playtest and continued combat integration review.

- November 9 roll interruption: roll movement now rejects replaced sessions and newer roll generations. Cleanup no longer restores automatic rotation/network ownership during a car knockdown, ragdoll, death or replaced character/session; anchored/removed roots skip ownership changes. Ten actual cleanup checks pass with mocked lifecycle state. Native roll-to-car-hit and rapid premium-roll transitions remain pending. Next: native movement interaction review when accessible; continue independent combat correctness checks.

- November 9 destruction readability: automatic attacks now explain the required scream level when a destructible rejects damage. The message appears at most once per attack, avoiding repeated full-state/HUD updates on every damage tick; successful damage and already-destroyed responses produce no lock message. Twenty-six actual-helper checks pass with synthetic responses. Native object targeting/message visibility remains pending. Next: test locked/unlocked props in the candidate and continue combat/destruction integration review.

- November 9 microphone teardown: destroying the controller now clears readiness, energy, capture and calibration, and becomes idempotent. Late Step/retry/calibrate/find-input calls cannot recreate audio instances or restart capture. Expanded actual-controller mocked audio/time coverage to 22 checks. No hardware or Roblox scheduling result is inferred. Next: device reconnect/client teardown playtest when available; continue automatic-voice integration review.
