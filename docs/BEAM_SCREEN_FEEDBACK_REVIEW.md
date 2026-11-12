# Beam screen feedback

## Native follow-up at b165525

A later disposable Studio run passed **218 assertions / five cases** at 04:42:55.782 UTC. Actual feedback and reticle centers matched; native module alpha/expiry/geometry/cleanup checks passed using synthetic times and four synthetic sizes. The complete result summary and center row are retained; four detailed geometry rows were truncated by Studio logging and are **not** fully reconstructed. Independent review verified summaries and disk/source correspondence. This does not validate Client acknowledgement flow, real transport, animation quality, full gameplay HUD overlap, physical devices or performance. Earlier build-only statements below describe the initial checkpoint and are superseded only within this narrow native scope. [Native evidence](../tests/evidence/beam-minimap-native-2026-11-12.json).

Both disposable Studio sessions were stopped and closed without saving, with closure verified. Background Studio warnings and close-dialog errors remain. Launch/open created two further minimized app-picker dialogs; four remain inaccessible through supported restore controls. No process kill or user-program closure. No production or fixture edits were needed; full-suite results remain those from b165525, not a repeated run.

## Scope and behavior

Original, local-only presentation now adds eight subtle peripheral launch lines and four small confirmed-hit marks. The fixed pool is 13 Frames plus one owning ScreenGui. It uses no image/audio assets, scheduled workers, camera motion, FOV change, blur or full-screen flash. The feedback GUI uses `ScreenInsets=None`, matching the existing aiming GUI, and `DisplayOrder=-1`, below existing HUD/reticle layers. The center is not intentionally filled; actual device rendering is still a release check.

Launch follows the current local `SustainedControls` attack acknowledgement, with the replicated active flag and sequence required to match. It does not depend on the arrival order of world-beam visual packets. Each sequence is consumed once, including hidden starts. Launch fades over 0.45 seconds with at most 0.12 opacity and a fixed yellow color; this is not a claim that selected beam styles have unique geometry or screen effects.

Confirmed hits reuse the existing `HitFeedback:Accept` result. Duplicate/stale totals cannot trigger the new effect. Hit marks fade over 0.25 seconds, reach at most 0.4 opacity, and cannot retrigger for 0.35 seconds. Intermediate sustained hits do not extend the expiry. Existing damage text and audio behavior remain.

Focus loss, menu opening, character removal, local beam end and destruction clear the effect. Existing blocked/readiness/eligibility/armed-state gates also suppress it. The saved REDUCED EFFECTS option and a guarded read of Roblox's `GuiService.ReducedMotionEnabled` disable it; an unreadable preference fails quiet. No claim of clinical comfort or universal accessibility is made.

A local End consumes the current local attempt before clearing. The End message has no sequence payload, so a delayed old End overlapping a new attempt can suppress that attempt's decorative cue. This is preferable to launching after a known stop; it does not alter attacks. If a matching acknowledgement is never observed while the current local attack exists, no launch is inferred. Native transport incidence is unknown.

## Review-driven corrections

Independent review reproduced a missing launch when a visual packet preceded acknowledgement attributes, and identified the original default-inset feedback parent as potentially offset from the None-inset reticle. The per-frame acknowledgement hook and matching explicit inset policy address those cases. The owner-End-before-first-render ordering was also fenced. These are synthetic/source-derived findings, not observed live incidents.

The existing gameplay-audio source contract was updated to recognize the unchanged accepted-hit cue followed by the new visual request. Its actual audio adapter tests were not replaced. The first aggregate run stopped on this old exact-line expectation; the failed log is retained separately from the final run. A second aggregate exposed an existing voice-notice fixture whose end anchor searched before its function start after a new focus callback was added. Its extraction now searches after the function start; actual lifecycle assertions and negative controls remain.

## Validation

Final full verification passed **25 pure/synthetic suites, 102 mocked-service suites, 61 production compiles and all builds**. Module **94 assertions / 9 controls** and integration **91 assertions / 18 controls** passed independently. Retained voice-notice **1,217 / 2 controls** and Dodge **127 / 4 controls** passed after fixture-only context updates. The Dodge fixture labels the new decorative dependency as a no-op while preserving its existing audio/world assertions; the new integration suite executes the real feedback modules. A third initial aggregate stopped on that missing dependency before correction.

Validation results and hashes are recorded in [the evidence file](../tests/evidence/beam-screen-feedback-2026-11-12.json). Explicit mutation-control runs are separate from the aggregate default.

- `python tests/beam_screen_feedback.py --negative-controls`: actual module with mocked GUI properties/time, fixed pool, deduplication, bounded fades, suppression, teardown and 10,000-event allocation check.
- `python tests/beam_screen_integration.py --negative-controls`: actual Client registrations/helpers/frame slices with real feedback and sustained-control modules, synthetic events and mocked geometry/audio. It is not a complete native client/server run.
- `python tests/verify_local.py --build`: regression suite, production compilation and disposable builds.
- `python tests/build_beam_screen_review.py`: builds/compiles a guarded unpublished-Studio fixture only. Runtime checks compare actual feedback/reticle absolute centers across inset policies, then exercise four synthetic viewport geometries and cleanup. **The fixture has not been run in Studio.** A generated place is not screenshot or native-render evidence.

No apps were opened in this batch. Earlier minimized app-picker cleanup limitations remain; they were not bypassed. Native appearance, actual HUD overlap, platform preference access, physical touch, phone rendering, visual comfort, multiplayer/transport ordering and measured GPU performance remain unverified. Fixed allocations and mocked geometry are not performance/device proofs. No map/world, server combat, save, reward, entitlement, product/audio configuration or live publication changes.

## Vault and reference provenance

Targeted guidance was read from the local **fwjelaa vault**:

- `42 Accessibility and Inclusive Design/Motion Sensitivity and Camera Comfort.md`: predictable optional decoration and clear view.
- `07 Lighting VFX and Audio/Screen Damage Effects - Hit Flash, Low-Health Vignette and Blur.md`: bounded feedback ownership, cleanup and accessibility.
- `08 Animation/05 Systems/Camera Shake and Camera FX.md`: finite envelopes and reduced motion. Camera shake/FOV/flash suggestions were deliberately not adopted because aiming depends on the camera.
- `Hit-Stop and Screen Shake Tuning by Numbers` and `Impact Frames`: restrained feedback timing, not imported behavior or a safety guarantee.

Vault notes/renders carry CC BY 4.0 credit requirements; credit: **fwjelaa vault**. No third-party render, clip or asset was imported; implementation is original. Current API reference checked: https://create.roblox.com/docs/reference/engine/classes/GuiService#ReducedMotionEnabled and GuiObject Active/Interactable documentation. Documentation availability is not proof of native access in this place.

Four supplied clips were inspected through eight timestamped visual samples each, not full-motion/audio transcription: `IMG_1397.mov` (visual feedback advice), `IMG_1399.mov` (Roblox tips), `v15044gf0000dbo19lnog65vnfi98ekg.mov` (thumbnail psychology), and `IMG_1400.mov` (tool demonstration with world-space glyph/aura examples). **No exact beam screen-overlay reference was established.** This is restrained vault-informed feedback, not a reproduction or claimed fidelity match.

All-test-player tools access still waits for the intended server-bound test-place identity. Map development remains paused, the final minimap native correction and short-screen long-notice overlap remain open, and real voice/live-service/writer-fleet release gates are unchanged.
