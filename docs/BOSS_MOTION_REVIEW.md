# Boss presentation motion

Source guidance read from the actual vault: `08 Animation/05 Systems/Boss Animation and Phases.md` and `Enemy Animation State Protocol.md`. Applied separation of authoritative state/root and cosmetic animation, readable cast anticipation, and shared timestamp continuity on stream-in. No animation clips or third-party assets imported.

## Contract

Server owns Core.CFrame and model BossState/BossStateAt. Ground remains Core.Position minus Catalog aimHeight. Client follows the live flattened facing, smoothing only Moving; Windup/Recovery snap to the frozen authoritative pose. Fixed Catalog home controls 180-stud LOD. One nearby appearance persists across movement, including asynchronous construction. Stream-out clears pose/model; stream-in derives pose from the shared clock, not a restarted clip.

BossPose adds no instances and retains scaled silhouette counts (274/291/269/435/417). Named assemblies provide restrained foot lifts/arm anticipation, metronome pendulum, conductor bells, leviathan jaw/fins, and Ignis flame motion. Feet never receive a downward offset. These are procedural assembly poses, not rigged walk cycles or IK. Render updates are capped at 30 Hz; there are at most 284 grouped part writes plus one model PivotTo per update. Physical phone/native frame timing is not measured.

Persisted game reducedShake is copied locally by the existing State handler to BossReducedEffects. Absent preference, OS reduced motion, and unavailable OS preference all suppress extra pose; authoritative location still follows the boss. No new remotes, health HUD, hitbox changes, camera shake, lights, or damage timing.

## Evidence and limits

`tests/boss_pose.py` executes actual appearance, pose and controller with numeric CFrame/vector and Instance doubles. Covers all five part budgets, movement without rebuilds, positive foot clearance, frozen cast alignment, no instance creation during frames, reduced/defeated rest, stream-out cleanup, timestamp-matched cast resume, and local/OS preference handling. Four negative controls detect movement-triggered rebuild, ignored reduced effects, below-ground lift, and live-root rather than home LOD. Existing aggregate and Rojo builds should also run during integration with server movement.

No Studio opened, no native visual/device acceptance claimed, no upload/publish. Native follow-up should inspect anatomy seams and front/back poses, cast warning alignment, reduced mode, overlap and low-end frame cost. Root integration owns combined server movement validation.
