# Redesign QA and release readiness

Updated November 6, 2026. Current source-suite baseline: **229a137** on `feature/microphone-city-redesign`. Historical full-city route baseline: **48bf91e**, with newer scoped route checks recorded below.

**Latest preview: version 14**, gameplay commit **55563b3**. Native Publish As updated the existing City Preview; the freshly opened cloud place reports ID 90337242377543 / universe 10769005350. All 30 source lengths/hashes match; all four serialized configuration checks pass. Startup loaded the camera toggle and crosshair with default Classic view. Play stopped afterward. A non-binding Studio lighting-migration notice was dismissed during cloud opening. [Verification](../tests/evidence/city-preview-version14-2026-11-06.json). This supersedes the version 12 publication record below; human/device/multiplayer gates remain open.

**Not ready for production publication.** The source/build is available for developer review in [draft PR #1](https://github.com/anushil7a/scream-simulator/pull/1). The live experience was last verified at version 32; this redesign has not been published over it.

**Current playable preview:** [Scream Simulator City Preview](https://www.roblox.com/games/90337242377543/Scream-Simulator-City-Preview) was published and reopened at **version 12** after the owner restarted Studio. All **30** source lengths/hashes match gameplay commit **8f0bb60**, and all four serialized place-configuration checks pass. This includes modern chat/typing cancellation and bounded ambience loading retries. Studio startup loaded ScreamUI, RBXGeneral and all five loaded/playing ambience sources; the client observed 25 streamed residents. Play was stopped afterward. [Verification record](../tests/evidence/city-preview-version12-2026-11-06.json). Earlier publication-pending notes below are historical and superseded. Real Roblox-client voice, saves, devices and representative multiplayer gates remain open.

This is a concise current handoff. [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) contains the chronological experiments, failures, corrections, exact Studio contexts and active-run cleanup instructions. The [development brief](PROFESSIONAL_REDESIGN_PROMPT.md) remains the full scope; this report does not reduce it.

## Fresh source/build verification

### Optional first-person aiming — November 6, 2026

Added session-local V/view-button/Settings toggles using Roblox's first-person camera. First-person and touch aim use the camera-center ray; a fullscreen crosshair shares that center. Desktop third-person rays now use raw screen mouse coordinates with ViewportPointToRay, removing the old GUI-inset subtraction. Switching view cancels capture; returning to third person restores normal zoom limits after leaving the close zoom. Visible overlay buttons release the cursor through GuiButton.Modal. Camera preferences restore on controller destruction; this is not a saved profile setting.

Thirteen native unpublished-city checks in `StudioFirstPerson.client.luau` passed with synthetic microphone readiness: camera mode, capture cancellation, HUD, centered ray/crosshair, overlay cursor flags, menu hiding, Settings refresh, zoom-limit restoration and rapid switching. The first fixture compared GUI absolute coordinates directly with viewport coordinates and failed; correcting the comparison to subtract the fullscreen ScreenGui origin resolved that fixture error. Native CUA V key presses additionally switched to LockFirstPerson at about 0.5-stud focus distance and back to Classic. No real microphone attack, physical phone touch, human aiming-quality assessment or multiplayer camera pass is claimed. Fixture removed and Play stopped before publication.

### Resident observation and ambience recovery — November 6, 2026

On the clean `93698b4` local city, 30 one-second post-startup server snapshots observed 46 living residents. All eight occupational roles had working samples; no unseated airborne samples appeared among 1,380 observations. Moving roles accumulated physical travel; Nick and the painter worked at their stationary stations. [Raw samples](../tests/evidence/resident-30-second-93698b4-2026-11-06.json). This is a short unloaded Studio observation, not a multiplayer soak or proof against transient floating.

The same startup exposed real HTTP timeouts for all four surf emitters; the guitar loaded. Ambience now preloads each of its two shared assets once and retries at most twice (2/4-second delays), then starts the corresponding emitters. Loading never blocks the gameplay controller. Native checks on a disposable copy established:

- Injected first-call failure, then actual ContentProvider: both representatives reached attempt 2; all five emitters were loaded and playing.
- Persistent injected failure with unloaded fixture IDs: exactly two representatives reached attempt 3; all five sounds remained stopped, with no fourth attempt after two additional seconds. The initial version of this test used cached production IDs and failed its stopped assertion because already-loaded sounds correctly played; it did not simulate unavailable assets.
- Destroying the controller 0.2 seconds into a delayed load removed the soundscape and SoundGroup. The delayed callback was canceled by Studio script destruction, so this establishes cleanup, not execution of the post-load guard. Console contained only the expected temporary-profile warning.

All injected providers/IDs and destruction code were removed, Play stopped, and the clean source restored. Human listening, actual CDN recovery timing, live voice mixing and destination asset access remain open. The updated ambience is still pending cloud publication.

### Latest preview upload attempt — November 6, 2026

Rebuilt `build/CityPreviewLatest.rbxl` from `93698b4` and opened it in Studio. All **30** production script lengths/hashes match the repository; `tests/StudioPlaceConfig.luau` passed all **4** serialized chat, live-voice and streaming checks. The clean local `ChatReview.rbxl` copy also has all current scripts and passed the configuration checks. Neither local copy is evidence of a cloud publication.

Studio's native window controls repeatedly returned `timeoutReached` after opening the latest build. No new upload or cloud reopen was confirmed. **Version 10 remains the last verified public preview**; modern chat/typing fixes and coastal/stage ambience are still pending publication. The feature branch at `93698b4` was verified against GitHub's remote head. To resume publication, recover the Studio window, publish the latest built place over **City Preview / place 90337242377543**, then freshly reopen and compare all 30 sources plus serialized settings. Do not select the original production place.

Executed against `229a137`:

- All **29** `src/**/*.luau` files compile with `luau-compile`.
- `luau tests/VoiceCombat.luau`: **4,017** combat, microphone-processing and destruction rule assertions.
- `luau tests/Progression.luau`: **1,506** progression/migration assertions. Printed leveling times are mathematical estimates, not player-playtest results.
- `luau tests/ProfileLease.luau`: **12** lease assertions.
- `luau tests/QuestLifecycle.luau`: **5** lifecycle scenarios.
- `luau tests/QuestGuide.luau`: **9** delivery guide checks.
- `python3 tests/profile_race.py`: **13** checks using actual Profiles source with a mocked store and coroutine scheduling. This is not Roblox DataStore contention evidence.
- `python3 tests/entitlements.py`: **9** actual-source entitlement checks using mocked services.
- Both Rojo place formats build: `build/MicrophoneCity.rbxl` and `.rbxlx`. Generated files are ignored; use README commands to reproduce them.

Counts describe coverage in these suites, not a probability of a bug-free game. No synthetic suite validates physical microphones, real phones or a representative multiplayer population.

## Current implementation and scoped runtime evidence

### Microphone and attacks

Implemented: mic-required setup, quiet/voice calibration, power meter, explicit hold/release capture, mouse/touch aim, four-second server cast limit, level 300 caps, cover checks and five-second spawn protection. Input power is client-reported and bounded; it cannot be certified as genuine human speech.

Evidence includes native synthetic Action/State/Effect integration, engine-injected E/Q/menu interactions, rule boundary/replay tests, microphone lifecycle tests and six native recalibration-controller checks. The most recent fix prevents failed recalibration from restoring old readiness.

**Open:** published two-account real-audio feasibility; comfortable-volume power behavior across different microphones; mute/permission denial/disconnect/reconnect; nearby listener attenuation and controls; measured voice/attack latency. No live-voice pass is claimed.

### Movement and avatars

Implemented: separate roll, collision checks, sprint exhaustion/recovery, jump/landing and scream poses. The R6 joint-axis correction passed six focused checks on native R6/R15 rigs; the old code failed the same R6 assertion. Default Animate was disabled in that focused check.

**Open:** physical keyboard and touch/multitouch play, default Animator blending, varied avatar proportions/accessories, micro-speaker grip through full movement, respawns under latency, vehicle impact/recovery and premium boundary transitions in actual multiplayer. The focused joint test does not close these requirements.

Follow-up on `87bfcec`: `StudioAnimatorBlend.client.luau` passed43 checks on the current R15 avatar with default Animate enabled. Eight synthetic charge→roll→release/recovery cycles retained two playing base animation tracks and ended with zero measured additive translation/angle. This narrows the default-Animator gap to a successful current-avatar recovery check; it does not cover moving R6/R15 rigs, physical input, all proportions, visual quality, latency or multiplayer replication. [Raw result](../tests/evidence/animator-blend-87bfcec-2026-10-02.json). Fixture removed and clean production animation source restored after stopping Play.

### Map, residents and activities

Implemented: Barcelona-inspired district layout, 40% central PvP land, safe surroundings, 31 enterable shops, 13 varied courtyards, market, beach, pier/lookout, swimming boundary, seating, selected quest givers and 46 residents. Additions include performance audiences, microphone beach volley, active street-furniture maintenance and distinct worker uniforms.

On `48bf91e`, native checks passed all **78** route cases: 31 shops, 26 courtyard passages, 12 coastal destinations, 3 audience positions and 6 arrival-plaza routes. The static audit found zero road, doorway or interior-aisle obstructions. [Current raw results](../tests/evidence/city-routes-48bf91e-2026-10-02.json) retain the run context. The inspected world contained 50,390 parts / 3,489 solid parts and 31 enterable shops. These results cover the new arrival-plaza geometry; they do not replace physical traversal, city-wide art review or load/device profiling.

Scoped tests: audience behavior: 12 checks; volley: 16 scripted checks including a synthetic cast through Bootstrap; maintenance: 13 checks including a real quiet interval, actual worker navigation and player occupancy. None is a human two-player usability test.

**Open:** final city-wide art/activity review at street height, physical traversal/driving, crowd behavior under player load, obstacle/destruction recovery across all occupations, volleyball timing with two real microphones and additional iteration based on playtests. Current screenshots and route checks do not prove the requested final visual quality or fun.

### Completed local NPC soak

Run `CityNpcSoak-20261002-70a4cf5` completed **1,800 seconds with 61 snapshots**. All 46 residents remained alive; 34–43 moved between post-startup snapshots and 3–7 were working. No persistent seat mismatches, walking-target stalls or above-20-stud residents were recorded in the samples. World descendants stayed within 53,563–53,573; post-startup Luau heap samples ranged from 2,455–4,145 KB and ended at 2,555 KB. These observations do not prove the absence of every transient fault or memory leak.

[Raw samples](../tests/evidence/npc-current-soak-2026-10-02.json) retain the exact source/run identity. Console output contained the expected unavailable-save warning and the successful observer completion. Play was stopped, observer source/attributes were removed, and the newer Microphone, MicPower, RunAnimation and City sources were synchronized. Both known disposable test copies are now stopped with clean current source.

This run had one Studio client without real microphone/combat load. Secondary Studio experiments also ran during portions of the interval. It does **not** satisfy the representative 24-player, 30-minute soak or physical-device frame-rate targets.

### Quests, progression, destruction and persistence

Implemented: selected NPC tasks, Nick discovery and staged soccer challenge, one-time rewards, level-based destruction, safe timed repairs, earnable amplifier and test-session save isolation. Native fixtures cover the scripted Nick course, quest lifecycle/reward paths, vendor purchase, damage/repair timers, seats and local maintenance; check the detailed log for the exact fixture scope and revision.

**Open:** full quests with human mic input; disconnect/rejoin and concurrent rewards on real services; destruction seen by other/late-joining players; occupied repairs with real multiplayer timing; live profile migration/leases/backups and old-server shutdown. Mocked store checks do not prove live persistence safety.

## Owner/external inputs needed

**Location-bound city audio, 2026-11-06:** Added four quiet, bounded surf sources and one stage guitar loop. Guitar fades in only for a living working busker within the stage area, and fades out when the performer stops. CityAmbience is a separate local SoundGroup; existing per-player volume settings now control it, labeled CITY AUDIO. Roblox voice routing/listener controls are untouched. Corrected the Map tab's old fixed-stage coffee directions to reference the assigned objective.

Free Creator Store audio was inspected as Sound-only assets with no children; native preload succeeded for surf 9119677305 (40.224 seconds, ProSoundEffects) and acoustic guitar 15675051846 (~11.971 seconds, Roblox). Asset provenance/use scope is in ASSET_INVENTORY.md. Eight native checks passed for temporary-profile safety, five-source routing/range bounds, asset loading, actual server settings mute/volume, working/stopped/dead synthetic performer gating. Two additional cleanup checks confirmed script destruction removes the local source folder and SoundGroup. Removed test appendix/review Sounds and stopped Play. Both city formats build; this audio addition is not yet published. Human listening, real voice balance and destination access remain open.

**CPU trace follow-up:** A 30-frame Studio snapshot did not reproduce the earlier startup outlier. Its longest complete frame was 17.463 ms (regular frame 28, absolute frame 27956). Inclusive per-thread scopes were inspected, not treated as critical-path attribution; no startup cause or fix is inferred from this short capture. Session/iterator resources were disposed, profiler disabled, and Play stopped. The cold-start stall remains open.

**Streaming-aware district samples, 2026-11-06:** Moved the test character as well as the camera to arrival, market and waterfront in the unpublished ChatReview build. Loaded world-part counts were 15,758 / 43,637 / 29,113. Each street view sampled 120 rendered frames after a two-second settle. Median frame times were 17.33 / 15.95 / 16.68 ms. Arrival included a 1,134.98 ms maximum and 71.48 ms p95; market/waterfront p95 were 18.64 / 18.84 ms. Render snapshots remain view-dependent, with streaming and warmup limitations. Shadows are separate in the raw pass data.

A separate fresh arrival session with ten-second warmup and 300 frames measured median 16.67 ms, p95 18.11 ms, maximum 33.49 ms; streamed parts changed from 15,812 to 15,808. This is evidence of a transient early stall, not proof of its cause or a startup fix. A cold-join CPU/asset/streaming trace remains needed before changing startup or claiming an optimization. No scenery was removed based on part count. These single-client Studio measurements at 1281x702 do not replace real-device or target-player-count gates. [Raw evidence and procedure](../tests/evidence/district-render-2026-11-06.json). Stopped Play after observations, removing temporary cameras and anchored test placement.

**Current chat and typing cancellation, 2026-11-06:** Scene inspection found LegacyChatService enabled in the built place, with legacy ChatScript/BubbleChat and server ChatServiceRunner. The Rojo project now serializes TextChatService mode with default channels/commands. A separately imported ChatReview.rbxl reports the new mode, RBXGeneral, nine commands, enabled input/window, no legacy runner/client scripts, and ScreamUI loaded. Engine-injected slash focused Roblox's CoreGui chat TextBox; no chat message was sent. Four serialized configuration checks also verify live voice defaults and streaming.

Opening a text field now blocks/cancels microphone capture, including immediate release before the render callback. Six native checks passed with actual TextBox focus and synthetic mic readiness: no sample release, cast effect or new capture while typing, and recovery afterward. Removed fixture and stopped Play. Both place formats rebuilt. This config/input change is pushed in source but not yet published; the linked preview still has legacy chat at version 10. Native property-control attempts did not apply the migration. Confirm chat configuration as well as source hashes on the next cloud publish/reopen. Two-person text/voice behavior and physical touch remain open.

The scene baseline contained 50,543 world parts / 3,509 solid parts. Memory queries showed legacy chat modules; no memory or FPS reduction is claimed from the migration. Preliminary render views moved only the camera while streaming followed the spawn character, so the market/waterfront readings do not establish fully loaded district budgets. Future render profiling must move the player/streaming focus as well. Scene queries and temporary cameras were confined to the disposable local city and removed by stopping Play.

**Varied café deliveries, 2026-11-06:** The existing delivery quest/save ID now assigns one of three server-selected waterfront stops: music stage, lifeguard lookout, or timber-pier end. The objective and vendor dialogue name the assigned stop. Repeated coffee pickup retains the original route/deadline; wrong-stop and expired dropoffs cannot complete it. Completion/abandonment clears transient destination state. Quest rewards and claim rules retain their existing values.

Twenty-four native unpublished-city checks passed across deterministic selections of all three routes: assignment, directions, duplicate pickup, wrong destination, completion, duplicate dropoff, expiry and abandonment. These use actual quest handlers with synthetic session setup/placement and temporarily constrained route config, restored after testing. The 12 completed-quest regression checks also pass. Three no-jump paths from the café succeeded (241/637/1,044 studs; estimated normal walking 16/40/66 seconds versus 90 allowed). These are navigation estimates, not timed human playtests. Five pure lifecycle scenarios, nine guide checks and all 4,017 combat/mic/destruction assertions pass. Both place builds succeed. Removed appended fixtures and stopped Play; not published yet.

**Waterfront rinse stations, 2026-11-06:** Added two original blue-and-white tiled stations beside the promenade at X +/-350, Z446. Metal columns, tap handles, low backs and grated drains give the beach usable facilities. F activates six bounded Beam streams for five seconds; the server checks a living nearby player and ignores activation while running. Automatic shutoff rearms the prompt. No audio, physics debris, rewards or persistent state added.

Native unpublished-city check passed 11 assertions: two atomic stations, initial water state, promenade clearance, four no-jump approach/through routes, engine-injected F activation, six enabled streams, prompt debounce and timed shutoff/rearm. Reviewed dry and active water renders. All 12 existing coastal routes still passed; all 18 beach seats retained prompts. Stopped Play, removing runtime observers/camera/character changes, and confirmed no appended client/server fixtures. Source/fixture compile and both city builds pass. Actual touch, multiplayer replication and device performance remain unverified; this addition is not yet published.

**Cast feedback, 2026-11-06:** Accepted screams now report server-resolved hits, misses, cover, dodges and destructible damage; knockout reward and practice readouts take priority where applicable. Five native checks passed in the unpublished local city for open-air miss, wall cover, practice target, resident hit text and matching 18-point resident damage. The first fixture attempt raced character spawn; the fixture now waits for the character. Uses synthetic accepted requests and controlled positions, not real voice or multiplayer. Removed the appended fixture and stopped Play. All 4,017 pure combat/mic/destruction checks pass and both place formats build. Multiplayer dodge/knockout feedback still requires two-player testing; this change is not yet published.

**Publication follow-up:** Captured-power fix a5be001 is pushed and both local builds contain it, but its second preview publication is pending. Studio native app binding and screenshot observation timed out repeatedly after the clean regression run; MCP still confirms the unpublished local copy has the fix and no fixture. Do not infer a new cloud version from this local check. The last verified published build remains City Preview version 8 (gameplay 1ed4a8a).

**Captured-power HUD correction, 2026-11-06:** Capture now displays the same sustained sample strength used on release, rather than changing with live input after the sampling window. Seven additional pure checks cover preview/release agreement, non-consuming reads, silence after sampling, cancellation and spike rejection (4,017 combat/mic/destruction assertions total). The unpublished local city passed 11 native HUD assertions using synthetic microphone state, including frozen power and fill after live input becomes zero. Fixture removed and Play stopped. Both place formats rebuilt. This does not establish real-microphone acceptance or multiplayer audibility.

**2026-11-06 update:** The owner-requested City Preview publish is complete. Studio reopened place 90337242377543 at version 8, with all 29 script lengths/hashes matching gameplay commit 1ed4a8a on GitHub. Studio's destination selector shows Public access. The city, 46 residents, practice target, character, ScreamUI and CityMap loaded in a subsequent Studio smoke test. Play was stopped. The prior private/version-2 handoff below is historical; real microphone, multiplayer, live-save and physical-device gates remain open. Publication is not evidence that those gates passed.

**Current handoff — published private city preview:** [Scream Simulator City Preview](https://www.roblox.com/games/90337242377543/Scream-Simulator-City-Preview) is now present in the owner's account (place90337242377543, universe10769005350). Creator Dashboard confirms Private access and Private audience reach. The owner cleared its Updated Agreements dialog. The game page reports Voice Chat Supported. Studio's linked Edit place reported version2 and its28 source hashes/lengths match repository466bcc1. A fresh cloud reopen or Roblox-client join has not yet verified the published payload.

Studio Play loaded the full city,46 residents and the detailed fountain. Its mic UI currently requests unmute then calibration. Studio API access is disabled, so profile loading falls back to temporary progress after the expected three failures; this is not a successful live DataStore test. No security settings were changed. Clicking Play on the Roblox page in the in-app browser reached a Download Roblox prompt without launching a client. Asked the owner to join the linked preview from their usual browser and report a real hold/speak/release beam. Actual accepted mic input and two-listener audibility remain unconfirmed; the earlier “it works” response did not identify which stage passed.

Full city HUD now labels its meter as live input, shows the first1.25-second sampling countdown and release phase, and cancels held captures after8seconds. Eight native HUD checks passed with synthetic UI state in the newly opened local city. No real microphone attack was inferred from that fixture; fixture removed and clean client restored.

- Two voice-eligible accounts and separate real microphones/devices for the existing private mic lab and published separate city preview. The current mic lab is102529270037263; its existence and owner-observed meter input do not prove multiplayer audio. Do not connect experiments to production saves or publish WIP over the current experience.
- Named desktop and physical phone targets, plus testers for representative multiplayer load. The working default is 24 players, 60 FPS desktop and 30 FPS phone; no final device result exists.
- Real badge/pass IDs and prices if those products are to launch. IDs remain 0; do not invent IDs or trigger purchases. In-game achievements and entitlement hooks exist independently.
- Review of the representative city block and broader world against the owner’s visual/playability expectations.

The owner requested that blocked items be recorded while independent work continues. These items remain open; their presence is not authorization to omit them or declare the goal complete.

## Release sequence once gates can be exercised

1. Build an isolated private test experience from a reviewed commit. Confirm all fixture appendices are absent and production source matches that commit.
2. Prove real microphone/voice feasibility first. Resolve failures before relying on combat/balance playtests.
3. Run the physical input/avatar, two-player combat/quest/destruction and actual-device cases above. Preserve failures and exact hardware/account/build context.
4. Run isolated live-store migration/contention/reconnect tests and representative multiplayer/load/soak tests. Verify no test mutations enter legitimate saves.
5. Review city art/activity, balance, entitlement configuration and the final public-test-tools policy. Public test tools are currently enabled as requested; do not silently change that policy.
6. Back up the current published version and data, record rollback steps, and plan old-server draining before changing save schema in production. No live backup/migration completion is asserted here.
7. Publish only after the applicable gates pass. Reopen the cloud place, verify published version/source and smoke-test a fresh server. Keep the prior rollback version.

## Where to work next

Development fountain integration follow-up: Plaça del Sol now uses the reviewed mosaic fountain with common collision/water and a28-part built-in fallback. Seven native asset-selection/re-entry/recovery checks and six plaza path cases passed. All28 production sources compile; city and review builds succeed. Main native view shows the detailed asset; simulated missing texture shows the fallback. Published destination permissions, actual network streaming and real-device frame rates remain unverified. See `research/FOUNTAIN_ASSET_TRIAL.md` for the failure found and corrected during this check.

- Run representative multiplayer/device checks once the required participants and hardware are available; the completed local NPC observation covers a narrower scope.
- Continue final map/activity/animation polish and fix concrete defects found by playtests.
- Coordinate the real microphone/device test inputs; synthetic evidence cannot replace them.
- Update this report after each release-relevant result rather than treating the chronological log as a final sign-off.

## Additional menu regression check — 2026-10-02

Nine native Studio checks passed for tab-specific refresh and scroll preservation in `StudioMenuRefresh.client.luau`. Synthetic XP/quest changes retained scream card instances; level changes rebuilt them while retaining scroll; settings changes refreshed their tab. No claim of physical-device input or frame-time improvement is made. Fixture removed after the run.

## Traffic yielding regression — 2026-10-02

Cars now brake for residents in their lane and resume gradually; stationary cars do not emit impact callbacks. `StudioTraffic.server.luau` passed 1,330 per-step assertions in controlled native Studio movement for both directions, sudden crossing clearance, stop/no-impact and recovery. This uses positioned test parts, not an autonomous NPC crossing or live multiplayer player-hit test. Those physical tests remain required.

## Physical NPC crossing — 2026-10-02

`StudioTrafficCrossing.server.luau` passed ten checks on `a6be978`: an existing resident used actual Humanoid walking across a road while the production Heartbeat advanced an isolated car, repeated in both directions. Cars reached zero speed, then resumed 24 studs/s after the crossing cleared. Recorded sideways displacement was zero; maximum root height was 3.44 studs; the NPC crossed from Z104 to Z127.10. Other traffic was temporarily paused and the NPC destination was scripted. This closes the focused native pedestrian-crossing case, not autonomous citywide routing or player-hit/multiplayer testing. [Raw results](../tests/evidence/traffic-crossing-a6be978-2026-10-02.json).

A subsequent street-height view from the spawn plaza showed that broad paved areas still read sparse despite the surrounding facade detail. Final city art/activity review remains open; do not treat the route/traffic passes as visual sign-off.

## Spawn-plaza visual pass — 2026-10-02

Added a flower kiosk with cosmetic bouquet interaction, pergola with two usable benches, ceramic paving and three resident destinations. Six focused native no-jump arrival routes passed. Engine-injected F activated the actual prompt and changed bouquet colors. Visual review corrected sign direction/height. Adds 105 parts / 21 solid parts. This is incremental plaza refinement; final city-wide art approval, physical touch testing and representative device/load profiling remain open. The prior full-map route and NPC soak runs predate this addition.

## Crowd label refinement — 2026-10-02

Healthy NPC nameplates omit full-health counters. Client limits names to the on-screen talk target plus one nearby injured resident, and speech to one nearby speaker. Eight native checks with controlled local clones passed for these limits, off-screen/dead target exclusion and absent-character cleanup. This does not prove physical mobile legibility or line-of-sight interaction filtering.

## Conversation cover correction — 2026-10-02

Client targeting and server conversation/vendor access now share living-character, range and solid-cover checks. Six native assertions passed for actual conversation rejection through a wall, acceptance past non-solid decoration and out-of-range rejection. Eight crowd-label checks also passed with this rule. The older label section's missing line-of-sight filtering is superseded by this change. Vendor purchase with newly introduced cover and multiplayer timing remain untested in this focused fixture. The full source-suite baseline above has since been refreshed to this revision.

## UI layout work reduction — 2026-10-02

Fixed layout dimensions now recompute on viewport/touch-mode changes. Nine menu regression checks passed. Native iPhone 17 Pro simulation confirmed the open menu and five tab buttons remained in bounds after portrait/landscape changes (401×720 and 750×303 GUI viewports). This removes repeated calculations but is not a measured real-device FPS result.

## Studio-only movement entitlement — 2026-10-02

Added the brief's separate test entitlement, exposed only in Studio's TEST TOOLS panel and server-gated by IsStudio. Nine native checks passed for safe-area premium rolls, save-baseline isolation and arena-entry cooldown/immunity restoration using synthetic mic readiness/scripted placement. Nine actual-source mocked-service checks passed for non-Studio grant denial and player cleanup. No real paid ownership, purchase, microphone or multiplayer entitlement pass is claimed.

## Isolated microphone lab — 2026-10-02

A standalone [mic feasibility project and two-person procedure](../prototypes/microphone/README.md) now exists. Both scripts compile and both place formats build with exactly five scripts/modules and no persistence or purchase code. Real audio/runtime verification is still open. Studio publishing controls could be read but coordinate actions failed; the dialog was closed without publication. A later local file-open action and UI rechecks timed out; no new lab instance appeared in the Studio connector, so its open outcome is unverified. A new private test experience and real-microphone participants remain required.

## Mic-lab native startup follow-up — 2026-10-02

The lab scripts booted in the existing disposable Studio copy with unrelated automatic scripts disabled: GUI, remote and floor appeared, no city was built, console was empty, and missing mic input stayed not-ready. Original game scripts/enabled states were restored and Play stopped. This narrows the earlier runtime gap to a successful startup check; published real-audio capture remains unverified. Code also blocks overlapping acknowledgement requests; ground labels replace overlapping billboards. Those final refinements compile/build but have no additional live-mic/network evidence.

## Navigation map follow-up — 2026-10-02

CityMap now replaces broad zone blocks with actual road positions, beach extent, six numbered landmarks, a destination legend and correctly centered position/heading arrow. Preserves world aspect ratio and hides stale player position during respawn. Twelve synthetic native UI checks at648/270holder widths passed; wide/narrow renders reviewed in disposable FountainReview, then fixtures removed and Play stopped. Both city builds succeed;29production sources now. This addition has not been synced/published to the private city preview and does not establish physical-device usability or frame rate.
