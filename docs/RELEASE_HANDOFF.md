# Scream Simulator release handoff

Updated November 13, 2026. Development branch: `feature/microphone-city-redesign`. Use [ROADMAP.md](ROADMAP.md) for current work and [AUTOMATIC_VOICE_PLAYTEST.md](AUTOMATIC_VOICE_PLAYTEST.md) for pending device/native checks.

## Last recorded publication

City Preview, place **90337242377543**, universe **10769005350**, was reopened and verified at **version 19** on November 8. The recorded verification covered 36 production source fingerprints and four place-configuration checks. Level cap 100 is present; that published build still uses hold/release attacks. Real microphone, save round trips and representative multiplayer soak remain unverified.

That release authorization is complete. **Another Roblox upload/publication requires fresh owner approval.** GitHub development pushes do not authorize uploads, live settings/access changes, or release merges. The separate original place **122465114514497** was not overwritten; its historical version 32 is not City Preview version 19.

## Current local candidate and fixtures

Run `python3 tests/verify_local.py --build` from the repository root with Luau tools and Rojo installed. Generated `build/` outputs are ignored by Git.

- `AutomaticVoiceCandidate.rbxl`: current automatic-voice candidate with normal profile handling. Its `.provenance.json` sidecar identifies source/build hashes. No upload is approved.
- `SustainedLocalPlay.rbxl`: disposable, local-only temporary profiles for manual gameplay review.
- `SustainedNativeFixture.rbxl`: disposable local place with synthetic combat checks; these do not establish real microphone behavior.
- `PerformanceReview.rbxl`: disposable local place with the manual server heartbeat collector. It does not automatically measure performance.

Never publish a disposable fixture. Older root-level or `CityPreviewLatest` binaries may be stale; rebuild from checked-out source. The city generates during Play, so an empty Edit viewport is expected. Native Studio control is available: specific synthetic transport and UI runs are recorded in the roadmap. Those named checks do not establish real microphone, phone, live save or multiplayer readiness; compilation alone is not native execution.

## Highest remaining release gates

1. **Real microphone and ordinary conversation:** no accepted evidence yet for the complete real-input path in this candidate. The owner/testers need two voice-eligible accounts/devices, ideally desktop plus a physical phone, in an explicitly approved isolated environment containing the exact candidate. Verify beams start OFF with no calibration or mic-testing panel/area, deliberately turn ON, then test comfortable speech and ON onset/quiet-stop, four-second cap/five-second cooldown, then OFF during attack while the other device confirms ordinary proximity conversation remains audible and no damage/restart occurs. Normal speech may trigger attacks while ON; OFF must leave microphone/proximity voice unchanged. Test mute, focus, death/respawn and deliberate resume. Actual microphone sensitivity remains unverified. The retired Controlled Beams objective must not appear for new/partial/claimed records; only an existing earned, unclaimed reward remains claimable. Record build/commit, devices and observed results without recordings or credentials. Synthetic power, local UI signals and Studio layout emulation cannot close this gate. Any required upload or environment change needs separate owner authorization; none is performed by this handoff.
2. **Real persistence and ownership transitions:** protocol tests use isolated simulated storage, not real DataStore contention, response loss or shutdown. A separately authorized test environment with isolated test keys and legitimate progress must verify save/rejoin/migration, simultaneous ownership attempts and unavailable/recovered warnings against durable data. Never use production keys or enable live APIs just to turn a failed test green.
3. **Representative gameplay/devices:** physical touch/accessibility, real-player comprehension, audio listening balance, representative multiplayer/performance soak and visual acceptance remain pending. Follow the existing scenario list; do not convert a synthetic/native fixture pass into an all-game release claim.

Keep the PR draft until these gates have matching evidence and the owner approves a concrete release candidate. There is no newly established production defect requiring speculative gameplay changes merely because these external gates remain open.

## Quest writer cutover gate

The additive quest candidate also has an explicit **BLOCKED, unverified writer-fleet** gate in its provenance. Older servers can erase new claim flags on acquisition while retaining rewards, allowing a later repeat reward. Before release, complete the [writer/rollback inventory and offline preflight](QUEST_WRITER_ROLLOUT_REVIEW.md), then independently review the actual operational cutover evidence. Publishing or scheduling a restart is not proof that old writers are gone, and DataStore history is not a transaction-by-transaction reward undo. A passing declared-writer simulation cannot close fleet/native/approval gates. No runtime compatibility fix or live cutover was performed.

## Before requesting the next release

1. Disable and review temporary all-tester access, then require the prelaunch-tools check to pass for the reviewed disabled source. This local check does not replace fleet or publication approval. Record the exact commit and candidate provenance. Preserve collaborators' work and inspect the current cloud source/configuration before planning an overwrite.
2. Run focused source checks and relevant disposable native tests. Record failures and unavailable tests honestly. Begin with the “Start here” smoke test in the automatic-voice playtest plan, then complete relevant detailed checks rather than historical hold/release lab instructions for this candidate.
3. Complete real voice/listener, physical input, multiplayer and save migration/rejoin checks in an explicitly approved test environment. Use legitimate progress for persistence evidence, not test-tool mutations. Do not experiment on production player keys.
4. Present the concrete candidate, outstanding risks and target to the owner for new upload/publication approval. Do not change live access/settings as part of that action without authorization.
5. After an approved publication, reopen the cloud place, record the new version, compare source/configuration against that candidate and check a fresh-server startup. Mark that authorization complete; do not reuse it for later releases.

City art acceptance, representative desktop/phone performance and a 30-minute multiplayer soak remain pending. Cosmetics, pass/badge configuration and monetization come after core gameplay. The current candidate temporarily permits testers in the allowlisted City Preview universe (10769005350) with matching creator, plus retained owner/Studio access. It freezes the legitimate save baseline after test entry and isolates test combat rewards. The local prelaunch-tools release gate is BLOCKED until this temporary access is disabled and independently reviewed; it does not enforce manual publication or verify deployed servers. Global trainer reset requires the strict disposable local fixture. This describes current source, not the historical published build's settings.

Historical publication evidence remains in [QA_REPORT.md](QA_REPORT.md) and [RELEASE_32_NOTES.md](RELEASE_32_NOTES.md); older recovery instructions and authorizations are superseded by this handoff.
