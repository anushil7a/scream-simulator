# Compact ambience emitter alignment

## Reproduced mismatch and correction

At `435aeba7eed36924708df3bc2c2584fc85f10763`, actual Ambience construction left surf at Z590. Any listener position within the compact layout bounds was at least 290 studs away, beyond the configured 230-stud maximum. The guitar remained at `(150, 5, 426)` while the compact working busker was at `(-300, 3, 125)`, outside the 35-stud performance gate. The historical actual construction/Heartbeat fixture reproduces these source-level mismatches. This does not establish every possible camera position or native audio playback.

`CompactLayout.Ambience` now defines four surf anchors along the compact south coast and the courtyard busker position. CompactCity consumes the same busker X/Z; his station position, Y3, facing, quest and work behavior are unchanged. Ambience selects shared compact positions only in compact mode; the original map's four surf coordinates and guitar position remain exact fallbacks.

Existing asset IDs, four surf/one guitar count, gains, sound group, rolloff mode/distances, performance gate, smoothing, volume setting and three-attempt-per-asset loading limit are unchanged. No new asset, audio upload, product configuration, voice routing or combat sound behavior is introduced. The original city archive is untouched.

Config loading has a terminal destruction hook before the new waits/require and a fence after each. Destruction during dependencies cannot allocate emitters or continue initialization. Existing cleanup and post-load/state/frame fences remain; tests exercise queued work and a genuinely yielded mocked preload resumed after destruction. This is synthetic scheduling, not native thread teardown evidence. An in-progress PreloadAsync is fenced when it returns, not cancelled; a hung call can remain pending.

## Vault and checks

Consulted the already-reviewed `07 Lighting VFX and Audio/Spatial Audio and Mixing.md`: attenuation, camera listener, loudness targets, Common mistakes and Checklist. Used positional-source and explicit-distance guidance without importing code, changing mix levels or adopting reference-project loudness values.

- `tests/compact_ambience.py --negative-controls`: 199 assertions and eight controls pass. Actual script construction/Heartbeat run against mocked services, configuration, sounds and scheduler; vectors are simulated.
- Pinned historical source reproduces both location mismatches. Current compact/legacy branches, source properties, work/inactive/dead/distant gates, settings, bounded loading, dependency interruptions, pending-preload teardown and retained callbacks are covered.
- Coast samples establish geometric distance coverage, not audible output, engine attenuation or physical device behavior.
- Full verification passes 25 pure/synthetic suites, 108 mocked-service suites, 63 production compiles and all configured local candidate/disposable builds.
- Independent review cleared the exact diff, reran 199/eight checks, reproduced the historical mismatch, and separately confirmed actual CompactCity busker position/facing/quest alignment. Exact source/log hashes and review status are in `tests/evidence/compact-ambience-2026-11-12.json`.

## Remaining validation

Unchanged gains and emitter count do not prove unchanged perceived loudness or headroom: compact spacing is 180 rather than 360 studs, permitting up to three configured surf ranges to overlap and placing the courtyard within range. Mix approval/tuning is deferred until native listening; no loudness or microphone-safety guarantee is made. Asset availability/permissions, actual listener position, playback/attenuation, phone/headphone mix, native performance and real-microphone feedback interactions remain unverified. Walk the coast/courtyard with ambience enabled and muted, check work start/stop and listener motion, and test the real microphone before release. Do not infer feedback safety from these tests.

No Studio launch, new visible application, live persistence, purchase, publication or GitHub push occurred. The existing explicit push-confirmation hold and other native/mixed-version writer release gates remain.
