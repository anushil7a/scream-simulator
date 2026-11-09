# Automatic voice candidate — manual checks

Current candidate is local and unpublished. City Preview version 19 still uses hold/release. Build with `rojo build default.project.json -o build/AutomaticVoiceCandidate.rbxl`; for isolated temporary profiles, run `python3 tests/build_sustained_review.py` and open `build/SustainedLocalPlay.rbxl`. Never publish either disposable fixture.

## Human microphone checks (pending)

Use two voice-eligible accounts/devices when available. Calibrate with a comfortable strong voice; no need to physically shout. No audio recording/replay is stored by the game. The meter reflects normalized input energy, not physical decibels or proof of a human scream.

1. After calibration, stay quiet briefly. Aim and speak without pressing E: beam starts after sustained input, follows aim and stops when quiet. Maximum active duration is four seconds; cooldown is ten seconds after the end.
2. Speak throughout cooldown: it must not restart immediately on expiry. Become quiet, then speak again.
3. Tap E/VOICE to pause; speaking cannot attack. Tap again to resume, then quiet/voice must work. Muting, death or losing focus must stop attacks and require deliberate resume after they have been armed.
4. While talking, roll, open menus, talk to an NPC, focus text chat, or enter spawn protection. No attack damage should continue while blocked. Rolling itself must never trigger a scream.
   Also open Roblox’s Escape menu during an attack: damage and sprint must stop. Closing it must leave voice paused until E/VOICE, followed by fresh quiet and voice. Check on desktop and phone.
5. Test first-person mouse aim and phone center-screen aim, cover, PvP boundaries, increasing range with level, and louder calibrated voice within the maximum range.
6. Verify the other player hears live proximity voice near/far. The attacker need not hear their own microphone loopback.
7. Practice target should show feedback. Soccer and volleyball receive at most one successful impulse per scream. Crowd credits three different bots once per attack; dodge quest credit is bounded per attacker scream.
8. On a separately approved test-universe upload, earn normal progress, leave and rejoin. Confirm level/coins/unlocked styles persist. Never use test-tool mutations as proof of legitimate saves.

## City/NPC review (pending)

Compare street-height views at the waterfront, Born lanes and Eixample. Check that district color is readable and not excessively bright. Watch a resident pass a newly blocked route: it must stop/replan rather than skip waypoints. Check transitions between walking, work, sitting, applause and Nick's stumble. Test occupied benches and destroyed paths. No measured FPS claim has been made for this candidate.

Record commit/build, devices, exact reproduction steps and expected/observed behavior. Synthetic unit tests and prior native geometry fixtures do not establish microphone, device or visual passes.

- NPC grounding recovery: in a disposable Studio place, move a walking resident above the street. After recovery, confirm it returns to ground, abandons the prior route and resumes an ordinary activity without repeated snaps or working animations away from its workstation. Native check pending.

- Street-art pilot: review the seven courtyard murals on Casa_28, Casa_88, Casa_1690, Casa_1790, Casa_2210, Casa_2310 and Casa_2410. Check outward face orientation, wall overlap, readable sun/sea or flower design, 100-stud fade and no unwanted interaction/cover. Keep or revise only after native visual review.

- Animation lifecycle: in a disposable place, respawn repeatedly and move away from/return to residents with streaming enabled. Check running/roll/scream poses still work, Nick has one practice prop, and removed animators leave no frozen additive pose. Mocked lifecycle checks pass; native Animator/streaming behavior is pending.

- Health HUD: take sustained damage, heal, die/respawn and change level in a disposable place. Confirm the health number/fill tracks the character, never briefly reports full health while dead, and updates the maximum after respawn. Mocked display checks pass; real replication timing remains pending.

- KO recovery: knock out a moving/sprinting player and a player recovering from a car hit. At the safe hub, confirm no carried momentum/spin, ragdoll or stale roll animation, and no delayed car recovery repositioning. Protection must last five seconds; dodge cooldown/sprint charge must not reset as a reward for being knocked out. Mocked reset checks pass; native physics/ownership check pending.

- Dialogue interruption: start an automatic scream, then talk to a reachable resident. The server should stop the attack immediately and reject further attack pulses while the conversation is active. Close the conversation, become quiet and speak again after cooldown; combat should recover. Also verify leaving range and resident removal cannot permanently lock attacks. Mocked availability tests pass; native network/interaction check pending.

- Respawn state: reset during a scream, roll, car knockdown and NPC conversation. Confirm the old attack stops, the new avatar is upright with five-second protection, mic pause/resume works, no stale roll/knockdown animation remains, and duplicate initialization cannot refill health. Mocked server lifecycle tests pass; native reset/character-loading checks pending.

- Aimed-player readout: aim at another player in first/third person and on phone. Verify level/health, safe-area/protected/rolling/out-of-max-range labels, clearing when aiming away, and no display through solid cover. Check accessories resolve to their owning character and three lines fit. Text logic passes mocked checks; native ray/UI review pending.

- Sprint stamina: hold sprint while stationary, walking into a solid wall, jumping vertically, seated, rolling and recovering from a car hit. Charge must not drain without available horizontal movement. Moving sprint should last ten seconds before a five-second break; inspect start/stop responsiveness under replication. Fourteen synthetic helper checks pass; native physics and control feel remain pending.

- Roll interruption: in a disposable place, roll into a moving car and confirm the roll task does not restore turning/ownership during knockdown. Reset mid-roll and repeat premium rolls outside PvP; older tasks must not move or restore controls for a newer roll. Ten mocked cleanup checks pass; native physics/network-ownership transitions remain pending.

- Destruction level feedback: below level 26, aim an automatic scream at a small tree. Confirm one required-level message for the whole attack, no damage/reward, and no message flicker on subsequent ticks. Repeat after unlocking the tier and confirm normal damage. Synthetic response checks pass; native targeting/HUD behavior remains pending.

- Microphone teardown: in a disposable client, remove the gameplay client/controller during calibration or a ready microphone session; check its analyzer stays removed and no queued retry recreates it. Rejoining should create a fresh controller and require calibration. Twenty-two mocked lifecycle checks pass; hardware and native event ordering remain pending.

- Worker navigation: block a station approach in a disposable place and inspect workers near steps/gaps. They should stop/replan rather than walk the final direct segment after a jump-required waypoint. Confirm ordinary unobstructed arrivals still reach tools. Fifteen actual-coroutine checks use synthetic paths/time, not native pathfinding or physics.

- Controls help: review Settings on a 390-pixel-wide phone viewport and desktop. Check all three help cards wrap without clipping, automatic attack timings match config, and touch camera/shop/paused-voice labels contain no keyboard shortcuts. Source compilation/build is not visual validation.

- Sprint input: start via Shift, then toggle using the button; repeat on touch. Open Screams/Quests/dialogue, start typing, mute, lose focus, reset or get hit by a car. Sprint should stop and require fresh input after interruption. After KO/lifeguard rescue, one tap should start sprint rather than consume a stale toggle. Thirty-four mocked helper checks pass; device/events remain pending.

- Mic-dependent aim range: aim at a player or destructible between minimum and maximum range, then vary comfortable calibrated input. The readout should change between BEYOND CURRENT RANGE and normal target information; beyond the cap must remain OUT OF MAX RANGE. Server cover/hit rules remain authoritative. Twelve mocked player text checks pass; native distances and HUD fit pending.

- Fall/lifeguard rescue: fall below the world or leave the buoy area while rolling, sprinting or knocked down. Confirm safe relocation with no carried velocity/spin, stuck ragdoll or delayed car repositioning. Health and movement budgets should be preserved, with five-second protection and attacks blocked during it. Fourteen mocked movement reset/callback checks pass; native physics/ownership checks pending.

- Seated recovery: knock out a seated player in the arena and test a seated rescue in a disposable place. They must leave the seat before teleporting, without dragging furniture or affecting another occupant. Verify ordinary sitting works afterward. Sixteen mocked recovery checks pass, including ownership-scoped weld cleanup; native seating physics pending.

- Seated actions: press dodge while sitting and attempt extra jumps during seat/stand transitions. Neither action should move attached furniture or consume a dodge cooldown; standing normally should restore eligibility. Also test temporary ragdoll/anchored roots in a disposable fixture. Sixteen extracted guard checks pass with mocked state; native physics/input pending.

- Delayed input: use an isolated native fixture with simulated network delay to verify late begin/pulse/stop packets never revive expired attacks or bypass cooldown. Adapter coverage now includes 79 synthetic checks; actual Roblox transport latency and real mic behavior remain unverified.

- Resident social interruption: approach two chatting NPCs and start dialogue before the second replies; also interrupt with a scream. The old delayed reply must not overwrite player dialogue or reaction text. Ordinary uninterrupted replies should still occur. Ten mocked callback checks pass; native timing/speech-label review pending.

## Local server performance sampling (not yet executed)

Open `build/PerformanceReview.rbxl` as an unpublished local Studio file. It uses temporary profiles and contains no auto-running combat fixtures. Never publish this file. Start Server & Clients, then in the **server** Command Bar run `game.ServerStorage.RunServerSample:Invoke(30, "idle")`. Wait for `SERVER_SAMPLE` in Output. Repeat with labels such as `two-player-combat` and `destruction-repair` while clients perform the named activity.

Record commit, computer, player count, scenario and the complete JSON output. Compare mean/p95/max **server heartbeat intervals**, intervals over 50ms and before/after world instance/part counts under the same conditions. The sampler measures 10–120 seconds, rejects overlapping runs and caps stored intervals at 20,000. A capped run is incomplete. Counting instances occurs outside the timing window. Do not interpret these intervals as client FPS, CPU profiling, network latency, a live-server load test or real-voice verification. Use Roblox's native profiler separately to identify causes; do not optimize from an isolated noisy sample.

Seven synthetic statistics checks pass and the fixture compiles/builds. No engine sample or performance improvement is claimed.

- Resident attention/cover: approach a worker and a resident reacting to a scream; greetings must not interrupt their activity. Stand across a wall and watch nearby NPC pairs: greetings/social conversations should require clear sight. Unblocked idle greetings should retain their cooldown. Ten mocked greeting checks pass; native collision-group/raycast behavior remains pending.

- NPC recovery/reset: knock out a bot, use Reset bots before its recovery, damage/knock it out again and wait past the original deadline. It must keep the new damage or remain down until its own later recovery. Verify the test session remains non-saving. Nine mocked callback checks pass; native timing pending.

- First calibration in background: during the first successful calibration, switch away from the window or open Roblox's menu. After returning, voice attacks must remain paused until ARM VOICE/E and a fresh quiet period. Twenty synthetic control checks pass; real microphone/focus/menu event testing pending.

- Recalibration from Settings: with a ready mic, open Settings and select RECALIBRATE MICROPHONE. Confirm attacks/sprint stop, the live calibration panel opens, and completion leaves attacks paused until ARM VOICE/E. Try failed calibration and retry as well. Existing mocked calibration checks pass; actual input quality and phone/desktop UI fit remain pending.

- Noncolliding occupants: in a disposable fixture, keep a queryable character part with CanCollide=false inside a damaged object's repair bounds at its deadline. Repair must defer until clear; also recheck ordinary players/residents. Eighteen mocked service checks model the documented query behavior; actual Roblox geometry remains pending.

- Shared regeneration rule: after scream/car damage, verify no healing before ten quiet seconds, then 20% of current max health with no overheal. Repeated hits restart the deadline; death cannot regenerate. Compare level 1 and level 100. Eight pure rule checks and 70 synthetic balance scenarios pass; native timing remains pending. Future tuning belongs in Shared.Healing so simulation and runtime stay aligned.

- Hidden voice toggle: pause voice, open Settings/Quests or NPC dialogue, press E and close the panel. Voice must remain paused until a fresh available E/ARM VOICE action. Also verify E can still pause an armed mic while a panel is open. Seven mocked toggle checks pass; native input/menu checks pending.

- Build identification: `python3 tests/verify_local.py --build` now creates `build/AutomaticVoiceCandidate.provenance.json` alongside the normal candidate. Record its artifact/source hashes with test results. This confirms build contents only; it does not mean a build passed native tests or is approved for publication. Disposable fixtures remain separately named and must never be published.

- Menu navigation: open Settings then press M; Map should appear, and a second M should close it. SCREAMS/QUESTS should open their matching tab from any tab and close on repeat. B should still close any open menu. Open a menu during NPC dialogue and confirm dialogue closes, freeing the resident. Native keyboard/touch behavior remains pending.

- NPC work interruptions: interrupt gardening/maintenance with dialogue, attacks and grounding recovery. Verify watering/work poses stop promptly, residents resume appropriate activity, and canceled maintenance does not repair the target, including near the end of the routine. Local mocked clock/activity tests cover cancellation; real animation/navigation remains pending.

- Dialogue death/respawn: while speaking to a resident, reset your character or have the resident knocked out. Verify the panel closes immediately, stays closed through respawn, and automatic voice still respects protection and fresh onset. Mocked character/UI tests pass; native input/event ordering remains unverified.

- Ragdoll animation: on R6 and R15, enter PlatformStand while screaming, sprinting or rolling. Verify additive poses yield, recovery has no stale roll or landing snap, and normal locomotion resumes. Mocked frame-hook tests cover state clearing only; real Animator/physics blending remains pending.

- Ragdoll combat: enter PlatformStand during a sustained scream with no active KnockdownEnds timer, then recover. Verify the beam/damage stops, attempts while ragdolled fail, and recovery still requires normal cooldown and quiet/new onset. Repeat with a moving-car hit and actual microphone. Client/server eligibility is mocked-tested; native replication and real voice remain unverified.

- Maintenance safety: occupy a damaged bench repair volume with a character while a worker finishes, then leave and verify later repair succeeds. Verify renewed damage interrupts maintenance and repeated screams at an already-destroyed prop do not postpone its repair. Service-level mock regressions cover state/deadline invariants; actual overlap geometry remains pending.

- Voice meter clarity: verify respawn, window-focus loss, PlatformStand recovery and mic-ready synchronization show the corresponding status rather than an armed instruction. Check desktop/mobile text fit and return to cooldown/quiet/onset messages. Source/build checks pass; visual/device verification remains pending.

- Delayed acknowledgement/stop: test automatic voice under Studio network emulation or a real higher-latency connection. Observe starting/timeout feedback, cooldown, quiet-before-retry and beam expiry on disconnect. Selectively suppressed fake acknowledgements/stops pass local flow tests, but do not establish Roblox packet timing or real-network behavior.

- Expired NPC conversations: allow player dialogue to expire, then observe that resident talking to another NPC, including the delayed reply. Closing the old player panel must not interrupt the new conversation. Active player conversations must remain exclusive. Full function mocked tests pass; native social timing remains pending.

- Calibration recovery: mute midway through quiet sampling and midway through voice sampling; unmute and verify calibration must restart. Disconnect/reconnect the microphone during voice sampling and complete a fresh calibration. Retry access after a transient failure. The controller passes mocked lifecycle regressions; actual audio-device/permission behavior remains pending.
