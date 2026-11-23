# Scream Simulator release handoff

Updated November 13, 2026. Development branch: `feature/microphone-city-redesign`. Use [ROADMAP.md](ROADMAP.md) for current work and [AUTOMATIC_VOICE_PLAYTEST.md](AUTOMATIC_VOICE_PLAYTEST.md) for pending device/native checks.

## Last recorded publication

City Preview, place **90337242377543**, universe **10769005350**, was reopened and verified at **version 19** on November 8. The recorded verification covered 36 production source fingerprints and four place-configuration checks. Level cap 100 is present; that published build still uses hold/release attacks. Real microphone, save round trips and representative multiplayer soak remain unverified.

That release authorization is complete. **Another Roblox upload/publication requires fresh owner approval.** GitHub development pushes do not authorize uploads, live settings/access changes, or release merges. The separate original place **122465114514497** was not overwritten; its historical version 32 is not City Preview version 19.

## Current local candidate and fixtures

Run `python3 tests/verify_local.py --build` from the repository root with Luau tools and Rojo installed. Generated `build/` outputs are ignored by Git.

- `AutomaticVoiceCandidate.rbxl`: current automatic-voice candidate. A local Studio file with both universe and place IDs zero uses temporary profiles and skips DataStore initialization. The `.provenance.json` sidecar identifies source and build hashes. Upload requires separate approval.
- `SustainedLocalPlay.rbxl`: disposable, local-only temporary profiles for manual gameplay review.
- `SustainedNativeFixture.rbxl`: disposable local place with synthetic combat checks; these do not establish real microphone behavior.
- `PerformanceReview.rbxl`: disposable local place with the manual server heartbeat collector. It does not automatically measure performance.

Never publish a disposable fixture. Older root-level or `CityPreviewLatest` binaries may be stale; rebuild from checked-out source. The city generates during Play, so an empty Edit viewport is expected. Native Studio control is available: specific synthetic transport and UI runs are recorded in the roadmap. Those named checks do not establish real microphone, phone, live save or multiplayer readiness; compilation alone is not native execution.

## Resonance Hall and the two-world goal

Full local verification also builds `ResonanceArenaLocalDraft.rbxl` (geometry and portals) and `ResonanceCombatLocalReview.rbxl` (guarded combat). Both are Studio-only. The Hall uses the 176 × 152 stud sound-themed arena and a separate, local 72 × 48 stud training landing. The blue route and actual prompts take a player from the Hall to the landing and back within the same file. The City remains the current training world and release priority.

The requested playable connection still needs two deployment-shaped builds for an approved nonproduction experience. The Hall review guard requires Studio and zero place/universe IDs, and its profile store is disabled. For the future shared-save contract, the Hall's generated configuration now retains the canonical City quest catalog for profile sanitization and keeps its active quest catalog empty. Hall state packets omit City quest progress and discoveries. An isolated profile test preserved partial, completed-unclaimed, claimed and discovered-only City state through Hall acquisition, release and City reload. Removing the retained catalog reproduced the previous loss while keeping economy values. This verifies the configured catalog boundary in simulation. It does not exercise real cross-place persistence or clear the historical writer-fleet gate.

Start with travel-only testing. Roblox documents `TeleportAsync` in Studio Test and Team Test for two places with the same `GameId`. Use approved City and Hall test place IDs and keep Studio API access disabled or inject temporary profiles for this pass. The current profile code can attempt the Studio store when connected to nonzero IDs. Verify intended arrivals both ways. Verify failed initialization leaves the avatar in the source place and the prompt can be used again. Record the source and destination builds and join metadata. Studio teleport support does not make the zero-ID preview a two-place build. [Roblox teleport testing](https://create.roblox.com/docs/projects/teleport#test-teleports-in-studio)

In a separately authorized persistence pass, use only that nonproduction experience and test profiles. Verify legitimate earned City progress survives City-to-Hall-to-City and rejoin. Verify one-time claims and discoveries survive, arrival during a pending departure waits for writable ownership or displays the temporary-progress warning, and failed travel retains the current source profile. Roblox data stores are shared across places in one experience, so a second place in the production experience would still use its store. [Roblox DataStores](https://create.roblox.com/docs/cloud-services/data-stores)

## Highest remaining release gates

1. **Real microphone and ordinary conversation:** no accepted evidence yet for the complete real-input path in this candidate. The owner/testers need two voice-eligible accounts/devices, ideally desktop plus a physical phone, in an explicitly approved isolated environment containing the exact candidate. Verify beams start OFF with no calibration or mic-testing panel/area, deliberately turn ON, then test comfortable speech and ON onset/quiet-stop, four-second cap/five-second cooldown, then OFF during attack while the other device confirms ordinary proximity conversation remains audible and no damage/restart occurs. Normal speech may trigger attacks while ON; OFF must leave microphone/proximity voice unchanged. Test mute, focus, death/respawn and deliberate resume. Actual microphone sensitivity remains unverified. The retired Controlled Beams objective must not appear for new/partial/claimed records; only an existing earned, unclaimed reward remains claimable. Record build/commit, devices and observed results without recordings or credentials. Synthetic power, local UI signals and Studio layout emulation cannot close this gate. Any required upload or environment change needs separate owner authorization; none is performed by this handoff.
2. **Real persistence and ownership transitions:** protocol tests use isolated simulated storage, not real DataStore contention, response loss or shutdown. A separately authorized test environment with isolated test keys and legitimate progress must verify save/rejoin/migration, simultaneous ownership attempts and unavailable/recovered warnings against durable data. Never use production keys or enable live APIs just to turn a failed test green.
3. **Representative gameplay/devices:** physical touch/accessibility, real-player comprehension, audio listening balance, representative multiplayer/performance soak and visual acceptance remain pending. Follow the existing scenario list; do not convert a synthetic/native fixture pass into an all-game release claim.

Keep the PR draft until these gates have matching evidence and the owner approves a concrete release candidate. There is no newly established production defect requiring speculative gameplay changes merely because these external gates remain open.

## Quest writer cutover gate

The additive quest candidate also has an explicit **BLOCKED, unverified writer-fleet** gate in its provenance. Older servers can erase new claim flags on acquisition while retaining rewards, allowing a later repeat reward. Before release, complete the [writer/rollback inventory and offline preflight](QUEST_WRITER_ROLLOUT_REVIEW.md), then independently review the actual operational cutover evidence. Publishing or scheduling a restart is not proof that old writers are gone, and DataStore history is not a transaction-by-transaction reward undo. A passing declared-writer simulation cannot close fleet/native/approval gates. No runtime compatibility fix or live cutover was performed.

## Before requesting the next release

1. Require `python tools/developer_access_preflight.py` to pass for the exact candidate source. The branch now uses the reviewed disabled configuration. Preserve collaborators' work and inspect the current cloud source and configuration before planning an overwrite. Record the exact commit and candidate provenance.
2. Run focused source checks and relevant disposable native tests. Record failures and unavailable tests honestly. Begin with the “Start here” smoke test in the automatic-voice playtest plan, then complete relevant detailed checks rather than historical hold/release lab instructions for this candidate.
3. Complete real voice/listener, physical input, multiplayer and save migration/rejoin checks in an explicitly approved test environment. Use legitimate progress for persistence evidence, not test-tool mutations. Do not experiment on production player keys.
4. Present the concrete candidate, outstanding risks and target to the owner for new upload/publication approval. Do not change live access/settings as part of that action without authorization.
5. After an approved publication, reopen the cloud place, record the new version, compare source/configuration against that candidate and check a fresh-server startup. Mark that authorization complete; do not reuse it for later releases.

City art acceptance, representative desktop/phone performance and a 30-minute multiplayer soak remain pending. Cosmetics, pass/badge configuration and monetization come after core gameplay. The candidate grants Test Tools to the matching owner and local Studio. Ordinary live players use normal progression, including in City Preview. The former all-tester policy is exercised only in isolated tests. Test entry still freezes the legitimate save baseline and isolates test combat rewards. Global trainer reset requires the strict disposable local fixture. The prelaunch-tools result verifies local source. The deployed server configuration and quest-writer cutover still need separate evidence and approval.

Historical publication evidence remains in [QA_REPORT.md](QA_REPORT.md) and [RELEASE_32_NOTES.md](RELEASE_32_NOTES.md); older recovery instructions and authorizations are superseded by this handoff.
