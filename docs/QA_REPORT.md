# Redesign QA and release readiness

Updated October 2, 2026. Full source-suite and native route baseline: **48bf91e** on `feature/microphone-city-redesign`.

**Not ready for production publication.** The source/build is available for developer review in [draft PR #1](https://github.com/anushil7a/scream-simulator/pull/1). The live experience was last verified at version 32; this redesign has not been published over it.

This is a concise current handoff. [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) contains the chronological experiments, failures, corrections, exact Studio contexts and active-run cleanup instructions. The [development brief](PROFESSIONAL_REDESIGN_PROMPT.md) remains the full scope; this report does not reduce it.

## Fresh source/build verification

Executed against `48bf91e`:

- All **26** `src/**/*.luau` files compile with `luau-compile`.
- `luau tests/VoiceCombat.luau`: **4,007** combat, microphone-processing and destruction rule assertions.
- `luau tests/Progression.luau`: **1,506** progression/migration assertions. Printed leveling times are mathematical estimates, not player-playtest results.
- `luau tests/ProfileLease.luau`: **12** lease assertions.
- `luau tests/QuestLifecycle.luau`: **5** lifecycle scenarios.
- `python3 tests/profile_race.py`: **13** checks using actual Profiles source with a mocked store and coroutine scheduling. This is not Roblox DataStore contention evidence.
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

**Current handoff — private full-city preview:** the full city at466bcc1 is open in Studio and all28 native script hashes/lengths match repository source, with no extra scripts in the game script services. The imported template's PackageLink was removed. Native File→Publish to Roblox opens the **new-experience Basic Info form**, but coordinate input fails with `noWindowsAvailable` and Tab did not focus its controls. No create/publish submission occurred. The form is intentionally left open for the owner: name **Scream Simulator City Preview**, click Create, keep Private, and provide its link/confirmation. Do not overwrite the live Scream Simulator or either mic lab. Actual mic success details/two-listener audibility remain unconfirmed after the owner's “it works” message.

October2 update after owner reported “it works”: Studio UI access recovered and the current MicrophoneCity.rbxl opened natively. The connected `screm test` place is102529270037263 (different from the first lab88993310833821). Its client reports microphone-ready; observed result text still showed an earlier insufficient-input release, so “it works” is recorded as owner confirmation without inferring successful attack or two-person audibility. Asked which stage passed. The older UI-access blocker below is historical; real-audio, device, multiplayer and art-review gates remain open.

Full city HUD now labels its meter as live input, shows the first1.25-second sampling countdown and release phase, and cancels held captures after8seconds. Eight native HUD checks passed with synthetic UI state in the newly opened local city. No real microphone attack was inferred from that fixture; fixture removed and clean client restored.

Latest continuation checkpoint (after `cbfed76`): native Studio access again returned `timeoutReached` on a fresh app binding. The Studio connector still lists only MicrophoneCity, Place1 and the untouched unnamed instance; no standalone lab instance is verified. No publication was attempted in this checkpoint. The previous turn made progress through the Animator recovery test; this checkpoint is blocked on the same UI/real-test inputs. Additional synthetic checks cannot close the outstanding real-audio, physical-device, multiplayer or owner art-review requirements.

Concrete next action: open `build/MicrophoneFeasibility.rbxl` manually in Studio and follow `prototypes/microphone/README.md` to create a **new private** mic lab. Supply its link and two voice-eligible testers using separate microphones/devices. Keep the production experience unchanged. Also open `build/FountainReview.rbxl` for the pending saved-file asset review. Resume implementation from actual failures or review feedback; do not claim either gate passed from the earlier in-session previews.

- Two voice-eligible accounts and separate real microphones/devices for the existing private mic lab and forthcoming separate city preview. The current mic lab is102529270037263; its existence and owner-observed meter input do not prove multiplayer audio. Do not connect experiments to production saves or publish WIP over the current experience.
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
