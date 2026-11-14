# Honest automatic sound cards, November 13

The collection still described three echo rings, feather-shaped sparks and other visuals. Actual automatic rendering selects its silhouette using attack level; the chosen sound style affects audio only. Legacy rendering still uses the configured effect. This was a copy mismatch, not a broken visual implementation.

Automatic-mode cards now show only name, unlock level and equip state. Their empty space shrinks to 108 pixels narrow / 64 wide. Legacy descriptions and 150/76-pixel layout remain unchanged, as do Config, unlocks, equip callbacks, level-based geometry, audio and shared power/range explanations. No audio characteristics are invented from names; the starter style has no extra owner-selected SFX.

Vault consultation used current HUD/readability guidance and `07 Lighting VFX and Audio/Combat Sound Design and Feedback` (TL;DR lines 6-16), then verified the actual Client, BeamVisuals, AttackAudio and legacy ScreamEffects paths. No imported assets or dependencies.

## Verification

- 406 actual-renderer assertions and six negative controls cover both modes, five widths, retained descriptions, locked/unlocked/equipped states and callbacks. Retained beam-readout checks pass 1,180 assertions/five controls. Independent review added exact command/payload checks.
- Full local verification passes 239 commands: 25 pure/synthetic and 128 mocked suites, 64 production compiles and requested builds. All 325 input fingerprints and aggregate log hash were rechecked. This is not CI.
- Separate native fixture verified exact source, PlaceId 0, GameId 0 and no server scripts before Play. It passed 332 checks over 16 Beams/Settings render cases across four synthetic viewport allocations and automatic/legacy-render-only states. All 11 sound cards were inspected per collection case, with no checked clipping, overlap or out-of-card allocation.
- [Desktop card screenshot](images/sound-card-copy-2026-11-13/automatic.jpg) inspected: readable names/levels and equip states without unsupported visual promises. Three asset-type warnings were present; their origin was not established. Play stopped and the task-owned Studio process closed; PC left on.
- [Exact evidence](../tests/evidence/sound-card-copy-2026-11-13.json).

Native checks use fake microphone/remotes and allocated UI sizes, not physical phones/gamepads, OS text preferences, real mode transitions or real audio. Existing 37-pixel buttons remain. No gameplay authority or save behavior change, publication or live DataStore access. Real microphone/multiplayer and mixed-version quest-writer release gates stay open.
