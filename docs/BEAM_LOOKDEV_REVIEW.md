# Bounded Blender beam look-development review

November 12, 2026. Original offline proxy of the current cosmetic beam formulas, not a new asset imported into the game.

## Result and files

`tools/beam_lookdev.py` ran the installed signed Blender 5.2 headlessly with factory startup and automatic file-script execution disabled. Exit code was zero. Outputs in ignored `build/beam-lookdev/`:

- `comparison.png`: six labeled previews, levels 1/50/100, regular/reduced.
- `level-{1,50,100}-{regular,reduced}.blend` and matching PNG files.
- `geometry.json`: exact generated primitive inputs and polygon counts.
- `provenance.json`: pinned source/script/artifact SHA256 hashes, fixed inputs, render limits and elapsed time.
- `blender.log`: local render output.

The contact sheet was visually inspected. An initial Blender-only rotation-mode ordering mistake made cylinders vertical. It was corrected before the accepted previews, with an explicit cylinder-axis alignment assertion. This was not a Roblox defect. Any `.blend1` backups from that initial scratch evaluation are not accepted artifacts; only files listed by final provenance are current.

## Reproduction and limits

Run the installed Python 3.13 interpreter with `tools/beam_lookdev.py`. Pillow is used only for local contact-sheet assembly. No third-party generator is imported. The script refuses changed BeamStyle/BeamVisuals hashes until its translation is reviewed and deliberately repinned.

Six cases use identical illustrative length 24, width 3, age 0.6 seconds, yellow color, and near-viewer detail. These are comparison inputs, not each level's actual combat range, width or damage. Source-derived primitive counts are 15/4, 41/4, and 77/4 for regular/reduced. Cylinders use 12 sides; endpoint spheres use 16 segments and 8 rings. The object limit is 78 including the camera per scene. CPU Cycles renders 640×280, eight samples and four threads, under a 240-second outer timeout. No visible application windows were opened; the headless process exited.

## Useful observations

- The sampled low/mid/high silhouettes communicate increasing decorative complexity: one ring at level 1, rings plus a strand at level 50, and denser rings/two strands/corona at level 100.
- Reduced mode removes decorative rings/strands/corona and the origin ball, retaining the three core cylinders and endpoint ball. Tier-dependent thickness remains, matching the source.
- From this camera, side-on to the beam axis with an elevated view, rings can read as thin crossbars and high-level strands overlap the bright core. That is useful for planning another native viewing-angle check, not evidence that the game's material or geometry needs changing.
- This exercise validates the installed Blender toolchain for small original geometry comparisons. No additional modeling stack or generated asset library was needed.

Cycles emission/transparency is only an approximation of Roblox Neon and its blending. There is no bloom, native renderer parity, temporal animation validation, multiplayer pool pressure, mobile performance, camera/aim accuracy or authentic gameplay measurement. No imported textures, meshes, uploads, purchases, cloud calls, map changes, production changes or publication occurred. The preview cannot justify replacing the existing game renderer without native comparison.

Recorded artifact hashes: [beam-lookdev evidence](../tests/evidence/beam-lookdev-2026-11-12.json). The local generated .blend/PNG files are reproducible review artifacts, not runtime Roblox assets. No new full gameplay-suite run was needed for this isolated tooling/documentation change; b165525 remains the last production verification.

Independent read-only review confirmed all 14 artifact hashes, both source hashes, exact generated geometry for all six fixed cases, signed bounded headless execution and the preview limitations.


## Native audit clock correction, November 12

A source review found that `StudioBeamVisuals.client.luau` sampled absolute times1/2/3 even though each rig records `born=os.clock()`. For example, a rig born at10 receives negative age at the first sample and uses launch scale0.55, not settled geometry. This does not invalidate the earlier part-count, physics-flag, reduced-mode, distance-culling or cleanup assertions; they did not assert settled width. The subsequent animated showcase already uses os.clock correctly. No production bug or perpetual frozen animation is claimed.

The three audit samples now use `rig.born + .6/.7/.8`. A new native assertion checks the second, non-pulsed core cylinder's settled thickness. Existing core reservation protects it from decorative pool exhaustion. Independent source review and Luau compilation pass; existing pure beam style/launch tests pass. A bounded arithmetic check verified positive post-launch relative ages at clock origins0/10/10000. `python tests/build_shop_review.py` rebuilt ShopReviewVerified and BeamReview without launching either. The new native assertion is **not executed**; no new full gameplay-suite run is claimed because production is unchanged.

Useful next tool step remains actual Roblox rendering/input verification, not more tooling. The targeted vault `14 3D Modeling/Blender Workflow for Roblox Creators.md` scene-unit/axis/export guidance is relevant when an original mesh is needed, but current beams use Roblox Parts. The already-installed bounded Blender proxy suffices for offline comparisons; no community MCP, installer, mesh import/upload or dependency was added. Native renderer/material parity and device performance remain open.

Corrected BeamReview.rbxl SHA256: `7205d901c7cb5da9d0991e5d087d33058b7f7f3b1e94ad04bf9eebb825602021`. Audit source SHA256: `0a2119505a9fa00d58873afc0c66c4fe760a2599579b68d4fb84559dc215e91d`.


## Bounded native measurement fixture (November 12)

`python tests/build_beam_performance_review.py` builds `build/BeamPerformanceReview.rbxl` without launching it. Open from Studio's File > Open from File, verify local place/universe 0, then Play. This file is disposable and must not be saved to Roblox. Studio currently requests sign-in before the next native check, so **no timing or native result is reported for this fixture**.

The fixture uses the actual SustainedBeams manager, BeamVisuals renderer and BeamStyle. It compares an empty baseline, 24 overlapping level-100 regular beams, then the same 24 in reduced mode. Each phase requests two seconds of warmup and five seconds of sampling; output includes actual sample span, summed frame intervals and p50/p95/p99/max milliseconds. Animation matches Client's accumulated-dt >= 1/30 then reset-zero cadence, checked by the builder. Synthetic pulses refresh at 0.2 seconds. This is no microphone, server combat, network or audio test.

The pool stays allocated across the regular-to-reduced transition, as in production. Visible reduced geometry is checked at 96 parts; lower visible count must not be described as immediate memory reclamation. Admission rejects attacker 25, allocation stays at most 512, physics/query/touch flags stay disabled, and final pulse expiry empties the manager. Terminal cleanup separately attempts manager destruction, pool clearing and each camera property restoration, collecting failures rather than skipping later cleanup. The scheduler watchdog is 35 seconds, not a hard wall-clock guarantee while Studio is paused.

A safe off-camera spawn prevents avoidable falling/respawn noise. Changed camera identity/type/CFrame/FOV or viewport invalidates the comparison. SavedQualityLevel is recorded only as a user preference; actual renderer quality remains uncontrolled. Frame intervals and locally timed script work are not GPU timings, transparency draw-call measurements or phone performance. Fully overlapping beams are a synthetic pressure case, not a representative match. Background activity, Studio overhead and Automatic quality may confound comparisons; do not infer a production speedup from these samples alone.

Build/compile and 264 actual-terminal-function mocked cleanup/interruption assertions plus five rejection controls pass. Runtime START/ROW/RESULT carry a source-bound build identity; the builder separately records original and generated source hashes. The watchdog control runs its actual callback in a coroutine and catches self-cancellation. Independent review cleared the exact sources, generated fixture and binary hashes, and independently reran all 264 assertions and five controls. No production behavior changes. Vault references used: `12 Performance Testing and Debugging/Performance Fundamentals.md` (frame time versus fps, averages versus spikes) and `MicroProfiler Guide.md` (Studio overhead and device-specific profiling). Existing native visual-audit clock correction remains separately unexecuted; no pending test is promoted by this build.


## Native startup readiness correction (November 13)

The first native measurement attempt correctly aborted with viewport `[1,1]` at START, then `Viewport changed; comparison invalid`, zero completed rows, `disconnected=true` and no cleanup errors. This is an incomplete measurement, not performance evidence. See local `build/beam-native-console-2026-11-13.json`.

The test fixture now waits on its existing RenderStepped connection for an actual camera and viewport of at least 64 by 64 pixels, unchanged for 0.5 seconds. It does not fix the camera, print START, start the phase clock, or collect samples before readiness. Missing/small/changing viewport for five scheduler seconds aborts without measurement. The existing 35-second watchdog and terminal destruction cleanup remain. After admission, any viewport or camera identity/type/CFrame/FOV drift still invalidates comparison; no hardcoded viewport or production behavior was added.

`python tests/beam_performance_cleanup.py` passes the retained 264 cleanup assertions and five controls, plus 54 assertions executing the actual readiness helper/callback preamble and five readiness controls. These use synthetic camera/frame delivery, not a full performance run or native input. Nil camera, initial 1x1 viewport, resizing/replacement during settling, timeout, cancellation, and post-start drift are covered. `python tests/build_beam_performance_review.py` compiled and rebuilt the isolated fixture. Independent final review and exact aggregate are recorded in the follow-up below; generated build provenance still intentionally says `nativeExecuted=false`, while separate native evidence records execution. Vault consulted: updated BrawlDev Advanced Scripting Review lessons 1 and 24 (readiness after yields, frame lifetime and delta time).


## Completed native Studio sample (November 13)

Corrected fixture identity `2c6263383c5cc30fd533b3e13db7aaffbeba826f47e1895874411b1f185f7cb2` ran in verified local place/universe 0 with no server scripts. All three phases completed, 5,384 runtime assertions passed, cleanup disconnected with no errors, and Play was stopped. See [native evidence](../tests/evidence/beam-native-2026-11-13.json), including the earlier correctly rejected 1x1 attempt. No production renderer change was made.

Observed frame p95: baseline17.29ms, regular24 17.75ms, reduced24 17.93ms; instrumented script-section p95:0.0001ms,2.974ms,0.1462ms respectively. Active geometry was0/512/96; the reduced phase retained512allocated and416cached. This single fixed-order desktop Studio sample does not establish a frame-time improvement, GPU cost, transparency draw calls, memory saving, real-match or phone performance. Automatic rendering quality and background activity are uncontrolled. Three asset-type warnings were present.

Final independent review reran264 cleanup +54 readiness assertions and all10 controls; the two initially missed readiness mutations now fail. Exact sources/build identity, complete native records and all312 final aggregate input hashes were independently checked. Final local aggregate:25/116 suites,63 compiles,allbuilds,226commands36.57s. No blocker found within this scope.
