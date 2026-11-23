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

### Travel-only Studio test pair

`python tests/build_world_travel.py` creates `CityTravelRehearsal.rbxl` and `HallTravelRehearsal.rbxl` under `build/world-travel`. The zero-ID files stage both inbound landings. City arrivals face north from Academy spawn and Hall arrivals start in the safe apron facing the arena. The banner clears when that character is removed, and portal interaction stays local. Full local verification rebuilds this pair. It uses the City base geometry with a test portal near Academy spawn and the Hall training arch, without game profiles, voice combat or commerce.

For an approved nonproduction experience, `python tests/build_world_travel.py --test-ids UNIVERSE CITY HALL` builds the counterpart `StudioTest` files with distinct destination IDs. Use Studio Test or Team Test and the configured place for each file. The gate checks Studio, universe and source place before obtaining Roblox TeleportService. The inbound landing runs once for an initial character when Roblox reports the configured peer universe and place through GetJoinData. Direct joins and respawns use their ordinary spawns. The manifest records artifact hashes and configured destinations. Exercise both directions and a failed transfer before adding persistence. A simulated transport check covers duplicate requests, immediate failures and matching delayed failures, while the two approved destinations are needed to verify actual transfer behavior. Keep these geometry-only files outside the Roblox release path.

### Playable zero-ID Studio travel rehearsal

Run `python tests/build_sustained_review.py --travel-local-qa` to create `CityPlayableTravelRehearsal.rbxl` and `HallPlayableTravelRehearsal.rbxl` in `build/`. The City uses the regular Academy training, quests and gameplay UI. The Hall uses the regular combat runtime, local PvP rules and safe apron. Follow the blue route to the Training City arch. The Hall's Rules tab explains the route and the Map tab is hidden. Open each file separately and use the portal prompt to verify its destination and local feedback.

The playable pair requires Studio with place and universe IDs zero. Each file uses temporary profiles, refuses configured commerce IDs and has no transport service access. Progress is local to the open file. Continue to use the separate travel-only test-ID pair for authorized cross-place checks. These playable builds do not exercise transfer, shared progression or real persistence.


## Owner's readiness bar

Pause development and notify the owner only after one identified candidate passes these checks:

- Real speech starts and sustains a beam in ordinary play, and another player takes server-confirmed damage. Two eligible participants should also verify that Beams OFF preserves ordinary proximity voice.
- Higher levels deal more beam damage and have more health. Deterministic checks and the local two-client Hall spot check cover the level 1 to 100 health increase from 100 to 480 and stronger high-level damage. Compare same- and mixed-level fights with real players to assess the intended balance, including that large level advantages matter.
- Testers can read the HUD, find training and the arena, and enjoy a continuous first-upgrade and PvP session. Check both visual quality and play feel on the actual reference devices.
- Each intended game pass grants its advertised entitlement through Roblox, and the shop shows accurate availability. The source catalog currently has 11 passes and two timed products, all with zero IDs. Local ownership and receipt simulations cover the code paths. Actual entitlements and receipts need owner-approved IDs and a separately authorized isolated test. If the timed boosts ship with the passes, verify delivery, rejoin and offline expiry too.

A local fixture or code check cannot stand in for the real-device or Roblox commerce results. Keep the current no-publication, no-live-persistence boundaries until separately authorized.


## Launch device coverage

Prioritize common phone, tablet and desktop sizes for launch. Use phone references around 360 × 800 and 414 × 896, an iPad-class 768 × 1024 and a 1280 × 800 tablet, plus 1366 × 768 and 1920 × 1080 desktop windows. Check supported phone/tablet orientations. These are representative sizes selected using worldwide web screen statistics. Measure the actual Studio safe area as well as the nominal preset and keep additional viewport tuning for a later update. [Phone sizes](https://gs.statcounter.com/screen-resolution-stats/mobile/worldwide) · [Tablet sizes](https://gs.statcounter.com/screen-resolution-stats/tablet/worldwide) · [Desktop sizes](https://gs.statcounter.com/screen-resolution-stats/desktop/worldwide)

Use Studio for HUD bounds, text fit, button actions and scroll checks. Verify the opening Guide and Talk, Beams/Dodge/Sprint, menu and shop closure, health and notices, and Hall combat and portal prompts where available. Physical touch, on-device performance and real microphone behavior require actual devices. [Roblox Device Simulator](https://create.roblox.com/docs/studio/device-simulator)

The current City candidate opened and closed the actual Menu on the following Studio presets near Rookie Training. The landscape checks also sampled the visible HUD controls for fit and overlap. Sizes are measured usable HUD pixels after Studio insets.

| Preset | Usable HUD |
| --- | --- |
| Galaxy A16 landscape | 685 × 280 |
| iPhone XR landscape | 801 × 355 |
| iPhone 16 Pro Max landscape | 830 × 381 |
| iPhone 16 portrait | 391 × 700 |
| iPad 9 landscape | 1080 × 752 |
| Average Windows laptop | 1365 × 710 |
| Full HD desktop | 1919 × 1021 |

Emulated phone taps activated the real Menu and Close controls after mapping the Studio input offset to the HUD coordinate space. Tablet and desktop used the native pointer. The evidence is in `build/resident_labels_native/native-device-matrix.json`. The remaining launch pass should include Hall interactions, full shop and quest paths, sustained play and physical devices. Keep work on less common sizes for a later update.


### Console is a launch requirement

Verify Xbox and PlayStation before the readiness pause. Roblox offers in-experience voice chat to eligible users on both console families. Real microphone input for this experience still needs separate verification on each platform. [Xbox voice](https://en.help.roblox.com/hc/en-us/articles/205355430-Xbox-App-Voice-Chat) · [PlayStation voice](https://en.help.roblox.com/hc/en-us/articles/41326172881300-PlayStation-App-Voice-Chat)

The left stick walks with the camera following the avatar. The right stick aims the beam by turning the camera and centered reticle. RB/R1 toggles Beams, LB/L1 dodges, holding L3 sprints, LT/L2 talks to a nearby resident, and Y/Triangle opens the menu. B/Circle closes an open game menu or conversation, or leaves game HUD selection so the left stick can move the avatar. The D-pad moves selection and A/Cross activates the selected control. Roblox's own controls continue to handle portal prompts.

Settings shows the bindings for the current input. In the local Hall replay, the open Settings panel updated from keyboard to Xbox controller instructions at the same viewport size.

In Gear, use the D-pad to reach either arrow beside the hue strip and A/Cross to step the color preview. Equip Color applies the preview for Spectrum owners. The locked preview is available without the pass.

The local two-client Hall check used the defender's Controller Emulator window. Select Xbox in the widget and click its left bumper directly. The mapped keyboard shortcut arrived as keyboard input in the earlier replay. The genuine Gamepad1 press produced a server dodge during an active beam, with damage resuming after the roll. See [the Hall controller evidence](ROADMAP.md#verify-controller-dodge-against-a-player-beam-in-hall).

The same local Hall scenario also passed with 100 ms of simulated delay in each direction and no simulated jitter or packet loss. See [the Hall latency evidence](ROADMAP.md#verify-hall-dodge-with-simulated-network-latency) and [Roblox Network Simulator](https://create.roblox.com/docs/studio/network-simulator).

A separate two-client replay at the same simulated latency used RB to disable an active beam through the normal client. The server stopped that sequence, and continued synthetic loudness past cooldown produced no restart. A final damage confirmation arrived after RB, but the server had already applied that hit before the local OFF state. See [the Hall Beams OFF evidence](ROADMAP.md#verify-controller-beams-off-against-a-player-at-simulated-latency).

On each physical console, verify sustained stick movement, TV safe areas, headset-triggered damage while aiming, ordinary voice while Beams are off, and controller-only access to the Guide, Talk, portal, and shop. Check commerce in an approved test environment. Console access settings require separate approval. [Roblox gamepad input](https://create.roblox.com/docs/input/gamepad)

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

The staged 30-minute Hall run verified repeated overlap and effect cleanup in three local Studio clients. City art acceptance, representative desktop and phone performance, and a human multiplayer soak remain pending. [Hall soak results](ROADMAP.md#soak-overlapping-hall-beams-for-30-minutes) Cosmetics, pass/badge configuration and monetization come after core gameplay. The candidate grants Test Tools to the matching owner and local Studio. Ordinary live players use normal progression, including in City Preview. The former all-tester policy is exercised only in isolated tests. Test entry still freezes the legitimate save baseline and isolates test combat rewards. Global trainer reset requires the strict disposable local fixture. The prelaunch-tools result verifies local source. The deployed server configuration and quest-writer cutover still need separate evidence and approval.

Historical publication evidence remains in [QA_REPORT.md](QA_REPORT.md) and [RELEASE_32_NOTES.md](RELEASE_32_NOTES.md); older recovery instructions and authorizations are superseded by this handoff.
