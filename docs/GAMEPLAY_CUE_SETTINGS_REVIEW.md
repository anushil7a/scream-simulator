# Gameplay sound settings and native UI validation

Base: `5ce93ad4f575c6eaed1b906ebbb4ac8c8e1b47e5`. Map development remains paused. No audio assets, gain levels, microphone transport, server combat or save behavior changed.

## Reproduced defect and correction

With all four gameplay cue asset IDs empty, Settings always displayed PENDING UPLOAD even after disabling cues. The actual old helper reproduces this hidden-OFF defect. Give the selected OFF state precedence; enabled cues show LOW, with a compact PENDING qualifier when no cue is configured. Ready still means any configured cue, not all four. Asset IDs remain unchanged and owner configuration remains pending.

An initial native run exposed clipping of the longer LOW (PENDING UPLOAD) label at 320 pixels. That run passed its functional assertions but is not final readability evidence. Shortened the qualifier to LOW (PENDING), added strict native TextFits checks for all allocated Settings text and both audio buttons during cycles/reopen, and reran successfully.

## Verification and fixture repairs

- `python tests/gameplay_cue_settings.py --baseline` restores the exact old helper and reproduces the defect. `python tests/gameplay_cue_settings.py --negative-controls` passes **42 actual-helper/mixer assertions and three explicit controls**, independently rerun. Empty/partial/all asset configuration, callback toggling/reopening, fake-handle cleanup and unchanged IDs are covered. Controls restore old precedence, prevent disabling, and force an incorrect OFF label after enabling.
- UI fixtures had become stale after the server eligibility gate: their synthetic state omitted voiceEligible/voiceStatus. Added explicit synthetic state. Onboarding now uses the actual state receiver, not forced SetArmed shortcuts; checks delayed initial eligibility, active denial/unavailability, one stop, no automatic restart and deliberate resume. It captures actual Settings callbacks and checks NORMAL/LOW/OFF plus cue state across rerender. Attack waits are bounded.
- Rebuilt client-only OnboardingReview ran in native Studio: **161 checks, 31 detailed stages**, no clipped allocated text in the final rows. Synthetic frame sizes: 320x568,390x844,844x390,1280x720. Three beam-readout rows fit and report the current five-second cooldown. Final result and source/artifact hashes are in the [evidence](../tests/evidence/ui-settings-native-2026-11-11.json).
- Additional supported native mouse input opened Shop/Settings, scrolled to sound controls, cycled beam NORMAL -> LOW -> OFF -> NORMAL and cues OFF -> LOW (PENDING) -> OFF. Reopening/scrolling showed NORMAL/OFF retained. Screenshots were inspected; this is desktop automation, not human/phone input or audio listening.
- `python tests/verify_local.py --build`: **25 pure/synthetic suites,87 mocked-service suites,60 production compiles and all candidate/disposable builds pass**. The new assertion test is registered; its three opt-in mutations were run by the explicit separate command above, not by default aggregation.
- Release handoff corrected stale ten-second cooldown and public test-tools wording to current five-second and owner/Studio access, baseline isolation and strict-fixture reset facts. Historical published settings are not inferred.

## Limits and cleanup

The native fixture uses synthetic microphone power, focus, callbacks and server state. It has no server scripts, real eligibility API or persistence path. Native text metrics establish allocated text fit only: a synthetic frame can extend outside Studio's actual viewport, so recorded hit-test false values are not phone reachability evidence. Real calibration, acoustic feedback/balance, proximity voice, physical touch/accessibility, network/service verification, multiplayer, commerce delivery and live save tests remain open. No four-cue audio upload/configuration was attempted.

Studio was stopped and closed, discarding only the generated disposable test session. Its launch created one minimized Windows Pick an app dialog; supported control could not restore/capture it after a refresh/retry, so it remains. No process kill, preexisting-window closure, map edit, live DataStore, publication or release merge occurred.
