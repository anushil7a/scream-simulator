# Confirmed beam contact — November 13, 2026

Accepted sustained damage now adds a short outward contact burst around the first damaged player or NPC's captured root position. Dark backing keeps the colored stroke readable against coastal stone; the open center preserves the target and lock-on caption. This is a damaged-target cue, not an exact surface intersection or a marker on every damaged target. A range/obstruction endpoint remains a different visual.

The existing damage message previously carried no position. The server now snapshots a finite, attached root before KO/ejection and fills that unused slot only after actual damage increases. All original damage, aim, hit selection, reward, quest, cooldown and healing calculations remain unchanged. Legacy nil anchors and unsupported object anchors omit the world cue while retaining damage text, sound and existing screen feedback. The packet count and damage-total fields are unchanged; old clients ignore its formerly unused position.

The client requires its current acknowledged attack, matching active server sequence and a live unexpired local beam. Old/future accepted totals, missing anchors and ended/disarmed/blocked attempts cannot place a cue on a different beam. The existing feedback is independent of this extra world-visual gate.

## Appearance and bounds

- Regular: eight short dark-backed outward strokes, 16 optional pooled Parts, expanding and fading for at most 0.28s. A cue cannot extend or refresh before 0.4s.
- Reduced Effects, platform reduced motion and distant views: four static dark-backed diagonal strokes, eight optional Parts. Their position/orientation stay captured rather than following later beam steering. No new camera offset, shake, FOV, full-screen flash, light, asset or animation connection.
- The optional contact array shares the existing 512-Part pool and cannot consume the five core slots reserved for each of 24 attackers. Existing tier profiles, beam body/ribbons/collars, endpoint lens and lock UI are preserved. At budget pressure, optional cues may be omitted.
- Contact state retires on expiry, presentation blocking, culling, rig destruction, attack end/timeout and client cleanup. Returning from cull does not replay it.

Vault sources consulted before design: `82 Scream Simulator Research/notes/beam-readability-and-phone-performance.md` (endpoint/end-state information and matched captures), `07 Lighting VFX and Audio/VFX Design Playbook.md` (value hierarchy, dark contrast and readability budgets), and `08 Animation/05 Systems/Camera Shake and Camera FX.md` (Reduced motion). These are design guidance; no imported numeric budget is treated as device proof.

## Verification

Server differential against the byte-identical published `5622daa` baseline: 94 assertions across 24 cases, one byte-text damage/reward contract and six negative controls. Renderer differential: 107,687 original-property/pool/geometry assertions and 14 controls. Actual Client/control/hit/manager/renderer integration: 261 assertions and 15 controls. Existing 88 screen-feedback integration assertions and 18 controls remain active. Audio retains 26 adapter/six source contracts; its old single-line hookup assertion was scoped to the expanded accepted-hit branch. Retained 117,904 pool-composition and 4,034 milestone checks pass.

All 247 commands in `verify_local.py --build` pass: 25 pure/synthetic suites, 136 mocked suites, 64 production compiles and disposable builds. All 335 inputs were unchanged during the final run and rechecked afterward. An earlier run stopped at the outdated one-line audio source assertion; its failed report is retained. The successful V1 aggregate predates the visual refinement and is not the final tested-source claim.

## Matched native views

The exact V2 disposable artifact SHA-256 is `5a042e430ee8db010765f5667a57cb28b8c8f1ffa54c2803f7cf2ec2fbcca283`. Before each Play, Studio/GameId=0/PlaceId=0, stopped state, a distant fixture spawn and five loaded-source length/checksum bindings were verified. The declared spawn Position exported as native `(0,0,0)`, about 245 studs from the target; a pre-Play exact-position guard caught that discrepancy before any Play. The revised reviewed guard uses the observed origin plus safe clearance. No hosted place was used.

The fixture combines actual current Client HUD/lock code, actual City and baseline/candidate renderers with a scripted opaque humanoid and ivory/slate contrast wall. Microphone, remotes, UI state, contact injection and time are simulated. Timestamps are frozen at onset, 0.06s, 0.16s and expired 0.29s; this validates native composition and expiry states rather than real server hits or animated comfort. Both sides of each comparison use identical geometry, camera, level, timestamp and logical 1280×640 allocation. The physical native viewport was about 1626×734.

| Sample | Before | After | Accepted observation |
|---|---|---|---|
| L1, regular onset, light | [Before](images/beam-contact-2026-11-13/low-onset-Before.jpg) | [After](images/beam-contact-2026-11-13/low-onset-After.jpg) | Distinct outward strokes at the opaque target |
| L1, Reduced Effects, light | [Before](images/beam-contact-2026-11-13/low-quiet-Before.jpg) | [After](images/beam-contact-2026-11-13/low-quiet-After.jpg) | Restrained static diagonal ticks |
| L50, oblique, dark | [Before](images/beam-contact-2026-11-13/mid-dark-Before.jpg) | [After](images/beam-contact-2026-11-13/mid-dark-After.jpg) | Contact is separate from the foreground traveling collar |
| L100, regular, light | [Before](images/beam-contact-2026-11-13/high-bright-Before.jpg) | [After](images/beam-contact-2026-11-13/high-bright-After.jpg) | Existing tier detail remains; contact is harder to distinguish |
| L100, Reduced Effects, dark | [Before](images/beam-contact-2026-11-13/high-quiet-dark-Before.jpg) | [After](images/beam-contact-2026-11-13/high-quiet-dark-After.jpg) | Static ticks remain subtle against the bright existing core |
| L100, expired | [Before](images/beam-contact-2026-11-13/high-expired-Before.jpg) | [After](images/beam-contact-2026-11-13/high-expired-After.jpg) | No residual contact geometry |

All 12 images are raw unedited native JPEGs. Core/tier counts remain 15/41/77 at levels 1/50/100, or four in Reduced Effects. Active contact adds 16 regular/eight quiet optional Parts; the expired sample adds zero. The real lock caption fits and remains readable in all samples. Highest sampled total allocation is 93, within the unchanged shared 512 cap; this is not a performance result.

Astra independently cleared source, tests, final fixture and all 12 images; it verified the 247 command states, 335 current input hashes, fixture/loaded-source/image hashes and cleanup. [Portable integration evidence](NOVEMBER13_INTEGRATION_REVIEW.md). High-tier clutter, multi-attacker overlap, actual phones, real voice/server transport, wider avatar sizes, motion comfort and GPU/FPS remain unverified. The pre-existing asset-type warning `203785492` remains unresolved.

Native Play stopped and owned scene/control/GUI objects were removed. Genuine device, animated comfort and multiplayer acceptance remain separate.

## Wave 2 contact burst cadence refinement

In `src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau` (SHA256 `d0afeb914318a16dc210647d8a4d49c6153a47735b5c58fbb86ffd48b57bf3e0`), the regular confirmed-damage contact burst (`rig.contactPosition`, 16 optional pooled Parts over the `0.28s` lifetime) now uses a nonlinear onset/decay envelope while keeping the `512`-Part pool, `24*5` core reservation, open center, target front-plane clearance (`0.7` / `0.82` studs), `rig.parts` core/tier silhouette geometry, and static `quietContact` (Reduced Effects / OS reduced motion / far view, 8 Parts) behavior unchanged:

- **Radial snap & taper:** cubic ease-out `ease = 1 - (1 - progress)^3` expands `extent` from `1.65` to `2.40` (capped at `width * 0.48`) and shifts `inner` from `0.52` to `0.76 * extent`, sharpening the stroke span as it travels outward.
- **Hot-core onset flash:** `heat = (1 - progress)^2` flashes the Neon core from `color:Lerp(white, 0.75)` at onset down toward `color:Lerp(white, 0.20)` at tail, framed by dark `SmoothPlastic` backing (`color:Lerp(black, 0.8)`).
- **Thickness taper & quadratic decay:** backing/core thicknesses taper linearly (`0.20 -> 0.12` and `0.12 -> 0.05`) while transparency accelerates along `fade = progress^2` (`0.10 -> 0.92` backing, `0.05 -> 0.95` Neon core).

### Wave 2 verification (mocked Parts/vectors & Blender look-dev proxy)

- `tests/beam_contact_visuals.py --negative-controls`: `PASS 102715` checks + 20 negative controls.
- `tests/beam_contact_integration.py --negative-controls`: `PASS 261` checks + 15 controls.
- `tests/high_tier_clarity.py --negative-controls`: `PASS 131673` checks + 14 controls.
- `tests/beam_pool_composition.py --negative-controls`: `PASS 117904` checks + 7 controls (peak `512`).
- `tests/beam_performance_cleanup.py --negative-controls`: `PASS 264` + `54` checks + 10 controls.
- `tests/beam_silhouette.py --negative-controls` (`824` checks / 7 controls) and `tests/beam_tier_silhouettes.py --negative-controls` (`4487` checks / 8 controls): `PASS`.
- `tools/beam_lookdev.py` (re-pinned `BeamVisuals.luau` SHA256, Blender 5.2 CPU Cycles): `PASS` (6 previews + `build/beam-lookdev/comparison.png`, `15/4/41/4/77/4` parts unchanged). Native Studio captures from November 13 predate this Wave 2 contact-cadence edit.
