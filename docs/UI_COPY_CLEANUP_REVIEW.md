# Interface copy cleanup, November 13

## Scope

The owner asked to remove unnecessary directions and text throughout the game, not only map directions. This bounded pass removes repetition, not useful safety, objectives or transactional terms.

- Beam collection: remove the repeated sound-style footer from every card and the generic training/challenge direction. Keep level unlocks, current/next stats and the single explanation of sound versus power/range. Cards shrink from 194 to 150 pixels in narrow layouts and 118 to 76 in wide layouts; the existing 37-pixel buttons and fonts are unchanged.
- Settings: microphone card contains current status rather than another attack tutorial. Default OFF is stated in automatic-mode controls only; legacy hold/release instructions and all voice-safety distinctions remain.
- Compact map: remove repeated coffee/training/race directions and pale-path prose. Preserve player/facing legend, PvP identification/boundary warning and active objective guidance. Original-map fallback is unchanged.
- Shop: shorten the hue-picker explanation that repeated its headline. Preserve yellow-base and saved-color information, product terms, activation/stacking and replacement warnings.

No server, combat, quest, save or purchase behavior is changed. This is not an exhaustive assertion that every remaining sentence is necessary.

## Vault basis

Targeted sections from `05 UI and UX/HUD Design`, `10 Game Design and Genres/First-Time User Experience and Onboarding`, and `42 Accessibility and Inclusive Design/Readable Text and UI Scale` informed removal of repetition while retaining clear actions and readable typography. Current source and native text measurements, not the reference material alone, determine acceptance. No assets or dependencies imported.

## Checks

- Actual extracted renderer/copy: 174 assertions and five negative controls across five widths and automatic/legacy modes.
- Compact map: 99 assertions/nine controls; shop: 100/twelve controls. Existing authority/lifetime cases remain in their suites.
- Retained beam readout: 1,180/five controls; microphone: 61/six controls/three source contracts.
- Final combined local run: 239 passing commands, 25 pure/synthetic and 128 mocked suites, 64 production compiles and all requested builds. All 325 selected input fingerprints and log hash were rechecked. This is local verification, not CI; default aggregate does not run optional negative controls.
- Independent Astra review covers the frozen source/diffs and relevant tests.

## Native evidence

A fresh disposable local Studio fixture was verified as PlaceId 0, GameId 0, with exact expected LocalScript source and zero server scripts before Play. It uses the actual bundled Client with fake microphone/remotes. Native rendering passed 196 checks across 16 rows: Beams/Settings, four synthetic allocations (320x568, 390x844, 844x390, 1280x720), and automatic/legacy-render-only states. Every collection row included all 11 sound cards. No checked text clipping, intra-card overlap or out-of-card allocation occurred. The legacy substitution is not a real gameplay mode transition.

[Beams overview](images/ui-copy-cleanup-2026-11-13/beams.jpg), [tightened cards](images/ui-copy-cleanup-2026-11-13/beam-cards.jpg), [Settings](images/ui-copy-cleanup-2026-11-13/settings.jpg). Desktop pictures were inspected separately. Partial cards at scrolling boundaries are normal clipping, not proof all content is simultaneously visible. Three asset-type warnings were present; their origin was not established. Play stopped and the verified task-owned Studio process was closed. The PC remains on.

Exact hashes, rows and report metadata: [evidence](../tests/evidence/ui-copy-cleanup-2026-11-13.json).

## Limits and next action

Native checks cover text allocation, not physical touch/gamepad, larger OS text preference, full-menu scroll discovery or real microphone/server input. Map/shop string cuts were source-tested, not separately native-tested. Existing button target sizes are not upgraded here. Real microphone sensitivity, multiplayer balance and older-server quest-writer compatibility remain release gates. No Roblox publication or live DataStore access.

The inspected collection still contains older sound descriptions promising specific visual shapes, while sound selection is audio-only and level controls the new silhouette. Review those descriptions separately against actual authored cues; do not invent audio or visual behavior.
