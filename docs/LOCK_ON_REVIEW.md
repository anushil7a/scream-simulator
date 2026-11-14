# Optional target lock review — November 13, 2026

## Scope and behavior

Original local aim assistance for eligible arena players and training fighters, explicitly requested by the owner. It does not arm beams, start an attack, move the camera, grant hits, change damage, or introduce a server command. Existing mouse/touch free aiming is unchanged when unlocked. No imported lock-on scripts or assets were executed or copied.

R on keyboard, right-stick click (R3) on gamepad, or the 88×44 LOCK button toggles selection. The button occupies the existing lower-left action-row space; acquisition instructions say AIM CENTER. Acquisition picks the nearest eligible projected target within a center-screen radius of35% of the smaller viewport dimension. It does not select under the desktop mouse. Acquisition attempts are debounced by0.2 seconds; unlocking is immediate. There is no automatic retargeting.

The selected target's position supplies the existing automatic Begin/Pulse aim callback and legacy release aim. Legacy release uses its captured power when computing range. A LOCKED marker follows that same target in the existing no-inset aim GUI, matching WorldToViewportPoint coordinates. It is advisory targeting feedback, not confirmation of damage.

## Contracts and authority

`LockOn.new(options)` exposes `Toggle(context)`, `Resolve(context)`, `Clear()` and `Destroy()`. The controller owns no frame loop, connections, Instances, camera state or remotes. Client registers its destructor immediately through the existing startup owner. Explicit acquisition scans Players and tagged CityResidents; subsequent resolution checks only the retained target.

A target must remain alive, attached, on screen, within current power-dependent range, and unobstructed from both camera and the player's head-derived attack origin. Exact target model/root/humanoid and local character identity are retained. Player targets require both positions in the arena and no active replicated protection/dodge window. NPC targets must be tagged CityResident with a known TrainingTier, active, and the player must remain within the authoritative32-stud fixed-home radius. Harmless residents are excluded. Training home elevations mirror World: compact3.2, legacy4.2.

Cancellation covers explicit unlock, beam OFF, eligibility revocation, capture cancellation, focus/menu/setup interruption, death/respawn, obstruction/range/identity loss and Client destruction. The frame path updates validation and marker before the slow HUD gate; every submitted aim also revalidates. Losing selection falls back to ordinary free aim, not another automatically selected target.

Server obstruction, per-target line of sight, range, beam width, cooldown, readiness, arena/protection, training and reward checks remain unchanged. Other players' session/test-baseline identity is not replicated: client selection cannot promise server test-mode eligibility. Existing server sameCombatMode and bot-isolation checks remain authoritative. The controller supports an optional advisory canSelect callback, but Client does not invent unavailable counterpart state.

## Verified local checks

- `python tests/lock_on.py --negative-controls`:558 assertions and6 controls using the actual controller with mocked Instances, projections and raycasts.
- `python tests/lock_on_integration.py --negative-controls`:65 actual-source Client fragment assertions, marker parent/inset contract and6 controls. Covers R/R3 registration, processed/typing/menu rejection, debounce, exact selected aim, OFF fallback, cancellation, eligibility loss, cover and captured legacy power. These are not physical input or rendered-position tests.
- `python tests/client_startup_lifecycle.py --negative-controls`:352 whole-script boundary scenarios (40 legacy/48 automatic dependency boundaries),19 ownership/late-constructor cases and12 controls. New LockOn/TrainingRules dependencies are explicitly enumerated; no startup bypass.
- Client/module Luau compilation and `python tests/build_studio_harness.py` pass. Retained voice/eligibility/navigation/notice fixtures received only narrow dependency or extraction adaptations, preserving their assertions.
- Independent Astra review cleared exact Client SHA256 `0943b307f7c7a9943c47f3eb2bb3a4604c2fb64df8eafdd71426a8d2d9def278` and independently reran65/6 and352/19/12. The isolated patch against the released HUD snapshot is `build/lock-client-review.diff`.

Coordinator reports native OFF-key/button and inset checks in a disposable local place0. Positive armed interaction was blocked by microphone-not-ready state. A separate native engine-controller check with a synthetic allowed context is planned, not claimed complete here. Real microphone behavior, physical touch/R3/controller ergonomics, native target-marker alignment during combat, and live multiplayer/PvP behavior remain unverified. No auto-hit, real save, publication or performance claim follows from these tests. Final aggregate evidence is coordinator-owned and separate.

## Vault references consulted

- `vault/AGENTS.md`: targeted current-source retrieval and imported-reference boundaries.
- `vault/External Roblox References/2026-11-12/Reference notes.md`: CustomLockOnSystemV2 is preserved as an unexecuted reference with unverified license/source; it was not adopted.
- `vault/fwjelaa/fwjelaa vault/58 Player QoL and Game Tweaks/Camera Settings - FOV Shake Sensitivity and Shift-Lock.md`, shift-lock/options, mistakes and checklist: deliberate controls, camera ownership, input conflicts and comfort. Existing third-person-only owner direction is preserved.
- `vault/fwjelaa/fwjelaa vault/09 Gameplay Systems/Hitboxes and Hit Detection.md`, techniques and checklist: local presentation is not hit authority; range, geometry, dodge and server validation must stay independent.

## Final native sample and pause (November13)

The planned isolated engine check completed seven assertions using the actual controller and a synthetic allowed context. It acquired/resolved the actual rookie trainer, cleared on a temporary collidable obstruction, reacquired after removal, and destroyed cleanly while target health remained80 and the player attack state stayed false. It did not send an attack remote. Actual full-Client R input while beams OFF safely kept selection empty. Positive armed full-Client behavior remained blocked by microphone-not-ready state, so real voice, rendered locked-marker alignment during combat, physical touch/R3 and multiplayer/PvP remain unverified. No automatic firing or server authority was added. [Evidence](../tests/evidence/visual-lock-checkpoint-2026-11-13.json).
