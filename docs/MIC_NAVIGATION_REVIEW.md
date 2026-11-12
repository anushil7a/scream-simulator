# Microphone setup and HUD navigation

## Result and boundaries

Microphone setup can be dismissed and reopened from Settings. Closing cancels unfinished calibration, not completed calibration. A readiness edge can finish setup; input loss no longer forces a dismissed panel open. Opening setup stops capture, automatic beams and sprint. Hidden/destroyed CALIBRATE and CHECK ACCESS callbacks are ignored; a later deliberate reopening permits current actions. Native stale-event ordering across a close/reopen cycle is not claimed.

Ordinary walking, jump, sprint, dodge and conversation no longer require a ready microphone. The visible setup panel still blocks relevant client actions. Server stamina, movement eligibility, cooldown, protection and entitlement rules remain. Beams still require microphone readiness and server eligibility; this does not prove authentic audio amplitude or change ordinary voice chat.

The minimap no longer disappears for a beam-status notification or authorized tester. Compact N/facing-arrow decorations are removed, retaining the position dot and full-map orientation. Authorized Test Tools appears below MAP. Narrow-screen tool/HUD/Talk allocation is tested; at320x315 the corrected tools and Talk rectangles meet without overlap, not with an8px gap.

Native review caught an expanded minimap overlapping an urgent notice at640x360 touch. Expansion now reserves the existing bottom-anchored toast's capped height plus optional tools. Cramped layouts retain a44px MAP button. **Long capped notices can still overlap collapsed controls on very short screens.** Tests intentionally do not claim non-overlap where that stack cannot fit. Final native rerun of this minimap correction remains pending.

No world geometry, map projection, progression, save data, reward rules, developer authorization or ordinary voice settings changed. Map development remains paused.

## Tests and independent review

Final `python tests/verify_local.py --build` passed25 pure/synthetic suites,100 mocked-service suites,60 production compiles and all builds. Opt-in mutation controls below are separate from the aggregate default.

- `python tests/mic_setup_navigation.py --negative-controls`:35 assertions/10 controls. Actual setup callbacks and frame fragments, real sustained controls/activation. Actual calibration reset was reproduced before adding hidden/destroyed callback guards. `--baseline` reproduces forced setup/navigation loss atb60dada.
- `python tests/microphone_movement.py --negative-controls`:58 assertions/10 controls/two source contracts. Actual dispatcher, spawn/periodic movement assignments and sprint helper with mocked avatars/time. Dodge coverage is admission, not roll physics. `--baseline` reproduces unready-spawn immobilization.
- `python tests/minimap.py --negative-controls`:137 module and406,617 combined client/layout assertions/16 controls. Extracts actual Client tool sizing and toast position/size/anchor, including expanded-map overlap control. Fewer expanded layouts reduce branch-dependent module counts from145 to137; no assertion removed for that count change.
- `python tests/microphone_check_requests.py --negative-controls`:53 assertions/nine controls/one contract. Current hidden/destroyed Retry is inert; visible reopening works. Historical121-call flood still reproduces. The legacy fixture was updated after the first post-guard aggregate exposed missing panel context.
- Retained focused checks include movement16; sprint183/four controls; sprint input49; sprint recovery54/five controls; session connections22/five controls; microphone notice402/four controls/three contracts; modal120/twelve controls; panel actions38/six controls; capture blocking22; compact map103/seven controls. Only corresponding changed readiness/context expectations were adjusted.

Separate reviewers reran the focused suites and exact mutation controls. Astra independently checked the three production files, callback correction, all final minimap controls and additional respawn/capture probes. No remaining blocker was found within that scope. It confirmed the long-notice layout limitation above. Synthetic services, geometry and callback invocation are not native network/input/queue proofs.

## Native evidence

Final disposable OnboardingReview ran in Studio against the corrected source:172 assertions,33 scripted rows/212 chunks and three beam readouts. All reported allocated-text clipping lists were empty. It covers dismissing unready setup, reopening from Settings, calibrated input loss without popup, manual recovery, synthetic eligibility interruption, beam OFF and audio-setting cycles. Four synthetic frame sizes were used:320x568,390x844,844x390,1280x720.

The first minimap native attempt checked visibility before the existing0.15-second HUD gate; its fixture now waits three frames plus0.2seconds. The next run found the real640x360 notice overlap. The conservative correction passed simulation and independent review, but was not rerun natively after Studio windows disappeared from supported inventory. No cause for their disappearance is asserted.

[Exact results, source hashes and limits](../tests/evidence/mic-navigation-2026-11-12.json). Filtered test-only chunks and reconstructed rows remain in ignored `build/mic-navigation-native-final.*`. Native asset-type warnings referenced203785492; origin is unestablished. No warning-free or successful-audio claim. Synthetic frames may exceed the actual Studio viewport; TextFits is label allocation, not physical-phone reachability.

The final supported inventory showed neither disposable Studio window. Two launch-created minimized Pick an app dialogs could not be bound: the tool requested restore operations not exposed by its documented API. They remain; no shell UI/process-kill workaround was used. Preexisting ChatGPT/Settings were preserved. No live DataStores/purchases, product/audio configuration or publication.

## Vault and remaining work

Consulted targeted original vault notes: `15 AI Tools/AI Pitfalls - UI and Input` (touch targets, processed input, multi-viewport checks); `05 UI and UX/Settings Menu Design for Roblox - Layout, Controls and Motion` (explicit control state/navigation); and `05 UI and UX/Minimap and World Map UI - Projection, Rotation and Fog of War` (shared projection and bounded marker updates), under `fwjelaa/fwjelaa vault/`. A separate access audit read `46 Resource Library/16 Tools and Workflow/Links - Testing` and `23 Debugging Deep Dives/Debugging Live Servers` section3.1. Notes are guidance, not identity/runtime evidence; no third-party assets were imported.

All-player Test Tools is **deferred** until the intended test place is identified and server-bound safely. A historical City Preview identity alone does not establish the requested current test destination. DeveloperAccess and test-save/reward isolation remain unchanged.

Remaining gates: final native minimap rerun; long-notice cramped-screen layout; actual phone/touch/accessibility, real eligible microphone/ordinary speech while OFF, server movement physics/network/multiplayer and services. The writer-fleet release gate and empty cue/product IDs remain. Owner resumed development after the prior pause; continue only authorized non-map work, without claiming scheduled continuation.
