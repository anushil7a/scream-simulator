# Scream Simulator release handoff

Updated November 9, 2026. Development branch: `feature/microphone-city-redesign`. Use [ROADMAP.md](ROADMAP.md) for current work and [AUTOMATIC_VOICE_PLAYTEST.md](AUTOMATIC_VOICE_PLAYTEST.md) for pending device/native checks.

## Last recorded publication

City Preview, place **90337242377543**, universe **10769005350**, was reopened and verified at **version 19** on November 8. The recorded verification covered 36 production source fingerprints and four place-configuration checks. Level cap 100 is present; that published build still uses hold/release attacks. Real microphone, save round trips and representative multiplayer soak remain unverified.

That release authorization is complete. **Another Roblox upload/publication requires fresh owner approval.** GitHub development pushes do not authorize uploads, live settings/access changes, or release merges. The separate original place **122465114514497** was not overwritten; its historical version 32 is not City Preview version 19.

## Current local candidate and fixtures

Run `python3 tests/verify_local.py --build` from the repository root with Luau tools and Rojo installed. Generated `build/` outputs are ignored by Git.

- `AutomaticVoiceCandidate.rbxl`: current automatic-voice candidate with normal profile handling. Its `.provenance.json` sidecar identifies source/build hashes. No upload is approved.
- `SustainedLocalPlay.rbxl`: disposable, local-only temporary profiles for manual gameplay review.
- `SustainedNativeFixture.rbxl`: disposable local place with synthetic combat checks; these do not establish real microphone behavior.
- `PerformanceReview.rbxl`: disposable local place with the manual server heartbeat collector. It does not automatically measure performance.

Never publish a disposable fixture. Older root-level or `CityPreviewLatest` binaries may be stale; rebuild from checked-out source. The city generates during Play, so an empty Edit viewport is expected. Native Studio control remains blocked in the latest recorded workflow; do not treat successful compilation as Studio execution.

## Before requesting the next release

1. Record the exact commit and candidate provenance. Preserve collaborators' work and inspect the current cloud source/configuration before planning an overwrite.
2. Run focused source checks and relevant disposable native tests. Record failures and unavailable tests honestly. Follow the automatic-voice playtest plan rather than historical hold/release lab instructions for this candidate.
3. Complete real voice/listener, physical input, multiplayer and save migration/rejoin checks in an explicitly approved test environment. Use legitimate progress for persistence evidence, not test-tool mutations. Do not experiment on production player keys.
4. Present the concrete candidate, outstanding risks and target to the owner for new upload/publication approval. Do not change live access/settings as part of that action without authorization.
5. After an approved publication, reopen the cloud place, record the new version, compare source/configuration against that candidate and check a fresh-server startup. Mark that authorization complete; do not reuse it for later releases.

City art acceptance, representative desktop/phone performance and a 30-minute multiplayer soak remain pending. Cosmetics, pass/badge configuration and monetization come after core gameplay. Public test tools remain enabled at the owner's request, with test mutations separated from legitimate saves.

Historical publication evidence remains in [QA_REPORT.md](QA_REPORT.md) and [RELEASE_32_NOTES.md](RELEASE_32_NOTES.md); older recovery instructions and authorizations are superseded by this handoff.
