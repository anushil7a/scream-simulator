# Four-way lightning dodge

Unpublished local implementation, November 16 2026. No Studio sessions or cloud assets opened by this change.

## Reference and intentional interpretation

Read the actual vault `Concepts/VFX/VFX-02_Lightning_Dash_Warp.jpg` and relevant `roblox-vfx/SKILL.md` / `LOCAL.md`. The image shows an upright leaning character, two translucent cyan body echoes, jagged cyan lightning, and thin gold ground sparks, not a tumble. This implementation uses actual avatar geometry, real sampled positions, angular Beam filaments and small gold foot strokes. No general asset-library generation, texture harvesting, demo combat code, yellow block, light flash or camera shake.

## Controls and authority

Q/touch DODGE remains the trigger. W forward, S back, A left, D right choose a cardinal direction relative to the character's current facing. Forward/back wins diagonal key ties; opposite keys cancel. Without net keyboard intent, joystick/controller MoveDirection is projected onto character forward/right; the larger absolute projection wins, forward/back wins exact diagonal ties. A .1 deadzone suppresses drift. Neutral defaults right, preserving the previous behavior.

The client sends only one token: `Forward`, `Back`, `Left` or `Right`. The server derives the unit axis from its own character facing, accepts legacy ±1 side tokens, and falls back to server movement/default-right for all malformed payloads. No client world-vector, magnitude, duration, cooldown or teleport is accepted. Facing and existing ground/seat/ragdoll/health/cooldown/entitlement admission are preserved. No mic-readiness dependency introduced.

14-stud maximum/.6-second duration and immunity/cooldown policy unchanged; cancellation on collision ends the active dodge state early without refunding cooldown. Each movement increment is subdivided to <=.5 studs, checks supporting ground, rejects rises/drops over .65 studs and slopes steeper than min(Humanoid.MaxSlopeAngle,45 degrees), then blockcasts. Geometry tests are mocked; avatar edge footprint, moving platforms and native terrain must still be exercised.

Signed `DodgeSide`/`DodgeForward` attributes select the pose. The pose is an upright shallow lean with bent arms/legs, not a rotation through 360 degrees. Facing is not spun toward the dodge. `DodgeAnimationProgress` tracks the new pose; legacy `RollAnimationProgress` remains inactive.

## Visual ownership/performance

Only accepted server Dodge events start effects. Existing 180-stud receive guard retained. Two actual pose samples separated by .16 seconds; each fades over .34 seconds, cast hard lifetime .60 seconds, <=16 body parts/echo and four simultaneous casts per client. Only whitelisted direct avatar body parts are cloned, all children stripped before parenting. All copies are anchored/noncollidable/nontouchable/nonqueryable. One lazy Heartbeat disconnects when empty. Expiry, removed character, eviction and Client destruction retire instances. Reduced effects/platform reduced motion suppress new casts; an already-started burst finishes within .60 seconds. No external assets or gameplay hitboxes.

## Verification and remaining native gate

- `tests/sideways_dodge.py`: executes actual motion module against mocked vector/geometry, plus actual client dodge function for all four keys, joystick directions, opposite-key cancellation, diagonal ties, deadzone, default and blocking. Tests flat/ramp/wall/drop/steep/step in all four travel axes, zero-step, rotated character facing and malformed intent.
- `tests/dodge_visuals_lifecycle.py`: 59 actual-module mocked checks; `dodge_visuals_contract.py`: 22 structural gates.
- Existing movement admission, microphone-independent movement, stale cleanup and whole-client startup suites remain in aggregate.
- `PATH=../tool-bin:$PATH HOME=../test-home python tests/verify_local.py --build`: local synthetic/mocked checks, compile and disposable fixtures. Not a native rendering/gameplay claim.

Next native checks: W/A/S/D and touch/controller forward/back/left/right/default while facing forward, camera turned, wall/corner stopping, .5-stud stair and ramp, steep slope/drop refusal, character respawn during dodge, cooldown spam, reduced motion, visible two separated cyan silhouettes against light/dark ground. No publish implied by passing these checks.
