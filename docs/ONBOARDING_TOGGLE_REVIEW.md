# First-session scream toggle clarity

Base: `54e3df2ebaf8ae97ca4f5219af15cfc38ac12720`. Production changes are explanatory text only; input thresholds, initial auto-arm, cooldown, OFF cancellation, respawn behavior and voice routing are unchanged.

## Reproduced issue

The disposable native Studio baseline used actual client UI/controller code with a synthetic ready/power source, mocked action/state delivery and a level-one profile. First readiness auto-armed the toggle. Setup and the idle ON HUD did not explicitly say normal speech can fire attacks. The baseline produced 15 complete observation rows; all relevant warning flags were false, despite synthetic above-threshold input issuing a begin. This establishes missing guidance, not a real speech-classification or microphone test.

The 144x44 SCREAMS toggle remained visible, selectable and reachable by native GUI hit-testing on portrait and landscape touch-sized frames. OFF sent the explicit stop, displayed TALK FREELY and left synthetic microphone readiness true. An OS mouse click on the touch-layout button also turned it OFF. No touch-control behavior bug was established, so no layout or input behavior was changed.

## Focused correction

- Mic setup explains that normal speech can fire attacks when ON and that OFF leaves nearby voice on. Legacy hold/release setup keeps its existing message.
- Idle armed HUD says normal speech can attack. Quiet-gate, attack, cooldown and interruption messages retain priority.
- Turning ON explains the risk and how to talk freely. Settings and README use the same distinction.

## Reproduce locally

Run `python tests/verify_local.py --build`, then open the disposable `build/OnboardingReview.rbxl` and start Play. The fixture emits numbered `ONBOARDING_CHUNK` lines: join all numbered chunks for each row before parsing JSON. Complete rows are required; Settings output exceeded Studio's single-line limit during review, so partial earlier output was not accepted as evidence. The fixture ends at a portrait ON state for mouse/E interaction. Stop Play after review; never publish this fixture.

The fixture forces readiness, power, focus and touch-layout selection, substitutes remotes/ack attributes, and has no server persistence scripts. It does not exercise real calibration, network transport, full combat acceptance, proximity voice audio or phone touch hardware. A synthetic attack starts from injected power; it is not a recording or a real scream.

## Validation and limits

The final native run produced 20 complete rows: 17 scripted observations and three OS-input observations (mouse OFF, E ON, E OFF). Setup, first-ready, idle ON and Settings showed the normal-speech warning across the three selected frames; visible labels reported no clipping. Gameplay toggle hit tests remained reachable at 144x44. Each synthetic-active/OFF pair recorded a begin followed by an explicit stop, with synthetic mic readiness still true. Setup and Settings intentionally hide the gameplay controls. All disposable sessions were stopped in Edit mode.

Exact final native rows, hashes, complete test output and review findings are recorded in `tests/evidence/onboarding-toggle-2026-11-10.json`. Full local verification covers 24 pure/synthetic suites, 56 mocked-service suites, 56 production compiles and all builds. Toggle coverage includes 29 actual helper/controller/adapter checks and two negative controls for missing explicit stop and accidental re-arm.

Separate implementing-agent self-review checks wording against activation behavior, legacy wording, visible text fit, unchanged voice/control source, fixture isolation and evidence completeness. No external review is claimed. Human comprehension, real microphone/proximity conversation, physical phone safe areas/input, accessibility navigation and representative multiplayer remain release gates. No live DataStores, publication or audio configuration.
