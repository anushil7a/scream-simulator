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
