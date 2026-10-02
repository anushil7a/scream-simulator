# Scream Simulator — professional redesign development prompt

Prepared October 1, 2026. Status: ready-to-use implementation brief incorporating the owner’s five design answers. Numeric balance and device targets remain proposed defaults. This document specifies future work, not completed implementation or test results.

## Copyable implementation prompt

You are the lead Roblox gameplay engineer, environment designer, animator, and QA engineer for Scream Simulator. Transform the existing project into a polished microphone-powered city action game. Prioritize an excellent playable city and coherent game feel. Work through the milestones and evidence gates below. “Professional” means cohesive art, responsive controls, clear onboarding, purposeful activities, good performance, resilient multiplayer systems, and verified behavior. Do not promise literally zero bugs; reproduce reported defects, fix them, and provide concrete regression evidence.

### 1. Repository and current baseline

- Repository: https://github.com/anushil7a/scream-simulator
- Local project: `/Users/anushiladhikari/Documents/RobloxProjects/SoccerManagerTycoon/ScreamSimulator`
- Experience: https://www.roblox.com/games/122465114514497/Scream-Simulator
- Place ID: 122465114514497. Last previously verified publication: version 32; inspect current cloud state before changing it.
- `src/` is authoritative. Use the Rojo project to build `.rbxl` and `.rbxlx`; generated world edits must be reflected in source.
- Inspect repository instructions, current branch, incoming collaborator changes, live place, dependencies, existing saves, assets, and runtime logs before implementation. Preserve unrelated work. Do not overwrite collaborators' changes or reset player progress.
- Current source has max level 30, six predefined sound tiers, character-facing beams, per-tier cooldowns, procedural city geometry, 42 residents, and temporary public test tools. These are starting points, not proof that this redesign exists.
- `City.luau`: environment and quest positions. `World.luau`: residents and traffic. `Bootstrap.server.luau`: gameplay server. `CombatRules.luau`: targeting. `Config.luau`: balance. `Client.client.luau`: UI/input/effects. `RunAnimation.client.luau`: motion. `Profiles.luau`: persistence.
- Current input distinguishes E and Q, and the Dodge effect returns before the scream audio branch. Do not claim this disproves the reported dodge/scream bug. Reproduce it against the actual running build and inspect duplicate scripts, event listeners, mobile controls, animation sounds, event payloads, stale servers, and state races.

### 2. Confirmed owner decisions and remaining defaults

The owner confirmed all five core choices:

1. **Hold attack + use mic, release to fire.** Ordinary talking or a dodge grunt must never start an attack.
2. **Nearby players hear the actual live scream.** Use supported proximity voice routing with listener controls. The scream is heard as it happens during capture; releasing fires the gameplay beam. Do not record and replay the voice on release or promise network-synchronized audio with zero latency.
3. **Polished, colorful Barcelona-inspired city.** Preserve this setting and create a coherent art direction.
4. **Unlimited premium movement only outside PvP; cosmetics everywhere.** Standard movement and dodge rules apply in the arena.
5. **Destroyed props and damaged buildings repair automatically after a few minutes.** Start with 120 seconds for small props, 180 for medium props, 300 for building sections; tune and validate safe restoration.

Other initial defaults, which do not block planning: target 24 players, keyboard/mouse and touch; verify on an agreed desktop and midrange phone before performance sign-off. Add controller support only after confirming intended device microphone/input support. Interpret the “micro speaker” as an earnable handheld in-game amplifier. Use existing/original assets without purchasing anything. Prices, paid pass IDs and published badge IDs remain unconfigured until supplied. Owner-created badges and final purchase products require those real IDs; do not fabricate them.

Ask targeted follow-ups only when an unresolved detail actually blocks implementation. Reuse these confirmed decisions rather than asking again.

### 3. Highest priority: the city must be worth playing in

Design a connected place with authored landmarks and activity, rather than scaling up repeated buildings. Preserve the Barcelona inspiration unless the owner changes it: chamfered Eixample corners, courtyards, shaded pedestrian streets, balconies, warm plaster/stone, tiled roofs, old-town passages, markets, beach and waterfront.

Produce a top-down layout, district palette, landmark silhouettes, street cross sections, pedestrian/vehicle routes, combat sightlines, prop rules, and a traversal plan before expanding geometry. Show a finished representative block at street height before propagating its quality across the city. Reusable components are encouraged; repeated complete blocks without deliberate variation are not.

Required districts and purposes:

- Safe arrival plaza: readable mic setup/tutorial, practice lane, equipment kiosk, nearby quest giver; clear routes into the city.
- Central PvP district: approximately 40% of usable map land, with visible boundaries, open fighting spaces, cover, flanking routes, entrances from several directions, and escape routes. Both attacker and target must be inside PvP for player damage.
- Old town and market: narrow but navigable passages, changing frontage, shop interiors or convincing usable thresholds, vendors, deliveries, conversations and hidden clues.
- Residential gardens: courtyard routes, gardener tasks, benches, planters, shaded rest spots, destructible props and repair activity.
- Waterfront and beach: connected promenade, playable beach, pier, sports, café, music stage, scenic views and quests. Give this district multiple activities rather than only decorative furniture.
- Hidden soccer court: environmental clues lead to Nick Booty. His area must feel discovered, not be marked by an obvious global quest icon.

Quality and interaction requirements:

- Authored height/footprint/material variation, convincing scale, doors, awnings, signage, lamps, curb cuts, crosswalks, street markings, outdoor seating and purposeful props. Landmark sightlines help orientation.
- No trees, bins, upgrade kiosks, signs or café furniture in active vehicle lanes. Define road/sidewalk/building exclusion volumes and check them automatically; also inspect visually and drive/walk the routes.
- Roads, sidewalks, courtyards, beach and building entrances must connect without snagging, invisible walls, abrupt holes, impossible stairs or decorative collision traps.
- At least one meaningful activity or discovery on each main traversal segment; target roughly 15–30 seconds between points of interest, adjusted through playtesting. Avoid increasing empty travel just to claim a bigger map.
- Include at least six working interaction families: usable seating, vendor transactions, quest deliveries, gardening help, soccer challenges, and destruction/repair. Add playground or beach sport interactions where performance permits.
- Livelihood comes from activities, traffic, player events, animation and soundscape. Do not solve it by spawning hundreds of idle NPCs.
- Cohesive lighting, ocean/sky treatment, restrained effects and readable silhouettes. Avoid visual clutter, excessive bloom, giant nameplates, repeated shop signs and inconsistent asset styles.
- Use reviewed assets with appropriate rights. Inspect imported models for embedded scripts and unexpected network behavior; no blind toolbox insertion. Do not install previously rejected BlenderGIS code merely to improve scenery.

### 4. Microphone is required for gameplay

Replace recorded attack screams with the player's actual microphone input. Decorative world audio and non-voice feedback can remain; no prerecorded scream substitute for attack activation.

Start with a small published mic feasibility prototype, using eligible real accounts and real microphones. Check current official APIs and account/experience requirements. Configure supported `AudioDeviceInput` / `Wire` / `AudioAnalyzer` routing and the experience's audio/voice settings. Do not assume restricted properties are script-writable or that an ordinary Studio solo test proves live voice behavior.

Provide a compact setup flow: eligibility, permission instructions, device check, quiet-room baseline, comfortable voice sample, calibration confirmation, and a live power meter. Ineligible or denied users see an explanatory non-playing setup screen; do not quietly substitute keyboard attacks. Disconnecting/muting a mic cancels capture and explains how to reconnect. Eligibility errors must not hang the UI.

Meter and processing:

- Label the meter **Scream Power: 0–100%**, not measured physical decibels.
- Normalize relative to the calibrated noise floor and comfortable vocal level. Smooth RMS readings, reject short spikes, add onset/offset hysteresis, and use a short sustained sample rather than a single peak.
- Cap power. Once full, shouting harder gives no additional benefit. Calibration should accommodate different mic gains and comfortable voices.
- Show input availability, calibration, capture state, power, predicted range, and the four-second cooldown. Distinguish physical input activity from permission eligibility; a zero sample alone is not reliable proof that a mic is absent.
- Measure before gameplay amplification/playback processing so speakers or the micro-speaker item do not create a feedback exploit.
- Do not store recordings or send raw audio to custom services. Use Roblox-supported audio transport; preserve mute, block, volume controls and moderation behavior. Since actual screams are audible, use proximity attenuation and bounded playback levels, not unrestricted amplification.
- Do not classify a noise as a genuine human scream without evidence: loudness alone can be spoofed by software, background sounds, or modified clients.

Security limitation: analyzer measurements are client-side. Treat reported power as untrusted. Server validation can limit consequences but cannot certify the microphone's true loudness. State that limitation honestly; do not claim perfect anti-cheat or server-authoritative mic measurement.

### 5. Mouse aim, combat, progression and initial balance

Confirmed: maximum level **300**, one accepted scream at most every **4 seconds**, stronger voice increases damage and travel distance, and every level increases maximum range. These replace the old level cap and tier cooldowns. Existing five-second spawn protection remains and prevents attacks while active.

Proposed initial tuning, to be tested rather than treated as final balance:

- Let `L = clamp(level, 1, 300)` and `P = clamp(calibratedPower, 0, 1)`.
- Maximum range: `Rmax = 30 + 0.25 * (L - 1)` studs. Level 1 = 30; level 25 = 36; level 50 = 42.25; level 100 = 54.75; level 300 = 104.75. Every level adds 0.25 studs, with an absolute server ceiling of 110 for future effects.
- Valid audible casts use `range = Rmax * (0.40 + 0.60 * P)`. Silence/below-threshold input produces no cast or reward.
- Maximum base damage: `Dmax = 18 + 0.10 * (L - 1)`. Damage: `round(Dmax * (0.45 + 0.55 * P))`; level 300 at full power is about 48. Apply a hard total damage ceiling after every modifier.
- Beam width starts at 4 studs and rises gradually to 7 at level 300; avoid long-range room-clearing beams.
- Proposed health: `round(100 + 0.35 * (L - 1))`, approximately 100–205. Replace the current +8/level formula rather than accidentally creating 2,492 HP at level 300. This rebalance must include PvP time-to-knockout testing.
- Quiet-time regeneration remains 20% of maximum health after ten seconds without damage. Preserve protections against repeated victim/reward farming.
- Rework XP curves for 300 levels with explicit time-to-level targets; simulate new player, average player and skilled player progression. Do not stretch the old level-30 curve blindly.
- Preserve the idea of a new unlock every five levels, but reinterpret unlocks as live-voice visual styles, animations or bounded utility, not 60 recorded screams. List all planned unlocks and implementation coverage honestly.

Aim at the mouse position using a camera ray and a world target. Reconstruct the attack from the character's valid mouth/head origin on the server; the camera must not let shots emerge through cover. Validate finite vectors, distance, timestamps/sequence, state and bounded direction. Resolve terrain, static and dynamic cover and streamed-out objects server-side. Touch uses an intentional aim reticle/drag and dedicated attack control; do not assume mobile has a mouse.

Damage must match the visible directed beam, including edge width, wall occlusion and maximum travel. Do not use an invisible sphere. Process one attack once per target; report confirmed hits and misses clearly.

The server owns cooldown, level, health, equipment ownership, PvP eligibility, hit resolution, destruction, quest progress and rewards. Never accept client-selected damage, XP, targets, building deletion, level or cooldown. Validate malformed, non-finite, repeated, stale and excessive requests. Clamp reported loudness and rate-limit messages; suspicious reports cannot exceed legal maximum output.

Use a proposed capture window of 0.25–1.25 seconds: releasing after a valid sample requests one shot; reaching the time limit freezes the charge until release, without silently auto-firing. Cancelling, losing focus, or rolling discards the sample. Never reuse a previous loudness sample. Four seconds is the minimum between accepted shots across all input sources and equipment. Switching styles, respawning, re-equipping, remote spam or premium ownership must not bypass it. Define charging/cancel behavior explicitly. Roll, knockdown, death, protection, menus and lost focus cancel attack capture without firing it.

### 6. Animations and the dodge/scream regression

Create coherent idle, walk, run, jump, fall, landing, scream anticipation/release/recovery, and full-body roll animations with proper priority, blending and cancellation. Use supported ownership and asset permissions; never ship inaccessible animation IDs. Handle the actual avatar rig(s) and body proportions in the experience.

Use a clear action state machine: Idle/Locomotion, MicCapture, ScreamRecovery, Rolling, Airborne, KnockedDown, Protected, Dead. Separate movement and attack actions; do not reuse attack input callbacks for dodge. Give one system ownership of each animation layer and avoid accumulating transforms or duplicate listeners after respawn.

The dodge fix must prove: Q, the dodge button and equivalent controller input trigger only a roll—no attack request, beam, scream sound, damage, XP, destruction or microphone auto-cast. Test simultaneous inputs, pressing attack during roll, rolling during capture, holding keys, repeated respawns, opening/closing menus, focus changes, latency and touch multitouch. Noise during/after a roll must not leak into a delayed attack; the owner selected manual hold/release activation.

Preserve solid cars, collision-safe rolling, brief impact knockdowns, sprint exhaustion/recovery and predictable jump landing. Do not rotate the physical collider through the ground merely to show a tumble. Avoid camera clipping, foot sliding, floating, double sounds and attacks from dead characters.

### 7. NPCs with occupations and selected quest givers

Use activity/state-driven NPCs with randomized but coherent appearance, schedules, nearby destinations, interaction reservations and recovery. Animation must match what the NPC is actually doing.

Required examples: gardener waters/prunes planted areas; vendor arranges goods and serves; café worker prepares and carries orders; sanitation worker sweeps and repairs/restocks damaged props; busker plays with audience reactions; beach worker manages equipment; Nick practices bad soccer. Ordinary residents can sit, browse, chat, react and walk between activities.

No floating/root teleport wandering, pathfinding jump spam, crowd stacking, synchronized movement or competing NPCs occupying one work slot. Handle blocked routes and destroyed workstations. Use bounded path requests, distance-based update frequency and sensible NPC limits.

Only selected NPCs give quests. Provide dialogue choices, animation cues, objective tracking, meaningful rewards, abandonment/retry behavior and cooldowns. Include non-combat multi-step quests, branching or randomized objectives and cooperative opportunities. Quest rewards and purchases are server validated and idempotent. Avoid repetitive “hit the same bot” filler.

### 8. Hidden Nick Booty soccer quest

Create an original fictional NPC named **Nick Booty**. He thinks he is a star but whiffs kicks, trips over the ball, celebrates misses and occasionally scores an own goal. Make him charming and recognizably animated, not a text label on a stationary rig.

Separate discovery from completion:

- Finding and interacting with him unlocks a hidden discovery achievement and small one-time reward.
- He offers a difficult optional multi-stage quest with a larger completion reward and distinct achievement. If a Roblox badge is desired, use an owner-created valid badge ID and verified server award; an in-game achievement is not a published Roblox badge.

Proposed challenge: find three lost training balls using environmental clues, complete a timed obstacle dribble, then land a sequence of aimed mic-powered shots through moving goal targets while compensating for Nick's terrible assists. Make the challenge skill-based and deterministic enough to learn, not dependent on extreme volume, premium movement, maximum level, lag or rare RNG. Define difficulty, checkpoints, reset conditions, hints, a quit/retry path and reward before implementation. Use a constrained or per-player quest ball so other players cannot steal/reset progress.

Suggested reward theme: “Nick's Number Zero” cosmetic and a moderate one-time XP/coin reward appropriate to the quest's level band. Final values are tunable proposals. Prevent duplicate awards across reconnects, retry requests and concurrent servers.

### 9. Destruction that supports a functioning city

Use bounded, authored damage states and tagged destructible models rather than unrestricted destruction of every physics part. Make thresholds visible when aiming at an object.

Confirmed unlock bands:

- Levels 1–25: benches, trash cans and similar small props. Higher levels need fewer screams.
- Levels 26–50: additionally small trees, bikes and similar medium props.
- Levels 51–100: additionally building damage; larger buildings become damageable as level rises.
- Levels 101–300: proposal—expand approved structural/facade damage and bigger designated targets gradually, subject to later tuning. Do not invent permanent city-wide collapse as a confirmed requirement.

Every object has a stable ID, minimum level, health, damage stages, reward rules, collision states and repair timer. Gate by level, then use validated attack damage to reduce health. Define example tuning and simulate screams-to-break at low/mid/high eligible levels; do not choose object health independently of the four-second cast interval.

Protect spawn, main roads, bridges, essential navigation, active quest dependencies and economy systems from griefing. Damageable houses can lose approved facade sections, shutters, rooftop props or designated structural sections while retaining a safe navigable shell. If a task requires a damaged object, provide repair/replacement or alternative objectives.

Server owns state changes; clients render capped debris and effects. Pool/clean up fragments, limit concurrent effects and avoid hundreds of server-simulated debris bodies. Late joiners receive current damage state. Repairs cannot trap a player inside restored geometry; defer or safely reposition. Guard against repeated destruction rewards and farming one's own rebuilds.

### 10. Micro speaker and future game passes

Proposed micro speaker: an earnable, equipable handheld amplifier with visible model and activation animation. It makes a quieter input more effective using `P_effective = min(1, 1.12 * P)` while respecting the same level-based range/damage caps and four-second cooldown. It never lets silence fire, increases the required physical loudness, bypasses mic eligibility, or raises actual audio output without bounds. No stacking exploit. Treat this as the starting equipment proposal, and clarify only if the owner intended different behavior.

Prepare a clean entitlement interface for cosmetic skins and the owner's proposed unlimited jumps/rolls. Keep prices and IDs unconfigured until supplied; do not create paid products or purchases silently. Verify ownership server-side through the supported Roblox purchase APIs; use a separate test entitlement path outside production.

The confirmed safe-zone-only “unlimited” movement must have an explicit definition: unlimited repeated availability is not infinite events per frame, permanent invulnerability or unlimited height. Safe-zone-only premium movement still has animation/recovery and rate limits; arena entry restores standard rules and cannot carry over invulnerability. Do not enable premium movement advantages in PvP; the owner explicitly chose safe-zone-only movement. Cosmetic skins must not hide hitboxes or grant stealth advantages.

### 11. Architecture, performance, saves and UI

Split the current large scripts into focused services/controllers as needed, without an unnecessary rewrite. Suggested boundaries: Input/ActionState, Microphone, Aim, Combat, Movement, Animation, NPCActivities, Quests, Destruction, Equipment, Entitlements, ProfileMigration and HUD. Keep balance and object definitions in data modules.

Persist levels up to 300, XP, cosmetics, equipment and achievements with schema migration, load-failure protection and idempotent rewards. Preserve old coins/levels/quests where appropriate. Do not store microphone recordings. Test disconnect/rejoin and concurrent reward requests. Keep temporary public test tools isolated from saving; confirm the production flag before release rather than silently changing the owner's testing policy.

Use district streaming/LOD, sensible mesh reuse, simplified collisions, NPC simulation budgets, pooled effects, bounded networking and cleanup on respawn/disconnect. Do not make the whole city one persistently loaded model. Profile before optimizing, including the current roughly 45k-descendant procedural world. Consider baking static geometry and incremental loading instead of rebuilding a dense city on every server startup.

Proposed performance targets: smooth 60 FPS on an agreed desktop and at least 30 FPS on an agreed midrange phone at target player count, including multiple simultaneous attacks, NPC activity and destruction. Record actual devices, player count, frame-time percentiles, memory growth and server costs. A desktop simulator is not proof of phone performance.

Keep HUD compact: level/XP, health, mic power, cooldown, aim feedback and current objective. Expand shop/quests on demand. Show unreachable/locked targets and mic problems clearly. Test menus with long localized text, narrow displays, safe areas and touch controls. No world-sized labels, unreadable contrast or overlapping tap targets.

### 12. Work phases and release evidence

1. Audit/reproduce: inspect current source and live version; reproduce dodge/scream; document actual baseline bugs and performance. Back up/version work.
2. Feasibility gate: published mic prototype with real eligible accounts, two different microphones, mute/denial/disconnection, selected audio routing, measured latency and power behavior. Do not redesign all combat around an unproven API assumption.
3. Finished sample: one beautiful playable city block with working occupational NPC, interaction, damage/repair and final-quality movement. Review its screenshots and gameplay before expanding.
4. Core systems: mouse/touch aim, mic capture, four-second cooldown, 300-level tuning, migration, health, action states, animations and security tests.
5. World expansion: connected districts, activity coverage, quest givers, Nick's quest, destructible bands, equipment and planned entitlement hooks.
6. Regression and stress: actual multiplayer, streaming, device and soak tests; resolve reproducible defects. Re-test changed behavior after every fix.
7. Handoff/release: build both place formats, update README/contributor instructions, provide reviewed commit/PR and QA report. Publish only when current authorization and release gates permit; otherwise leave a reproducible tested build. After publishing, reopen the cloud place and verify version/source and a fresh-server smoke test. Keep a rollback version.

Required evidence checklist:

- Real mic quiet/medium/full input produces monotonic bounded power, damage and range; silence and lost permission cannot cast; no recorded scream fallback.
- Server rejects cooldown bypass, excessive power, invalid aim, stale/replayed actions, wrong PvP state, unauthorized rewards and invalid destructible IDs.
- Mouse aim tracks expected world targets; cover blocks mouth-to-target line even if the camera sees around it; exact max-range boundaries tested.
- Q/touch roll never emits a scream event or causes damage/reward. Test combined inputs, audio during rolling, respawns and latency. Verify scream/run/jump/land/roll blend and cancel on actual supported rigs.
- Level boundaries 1, 25, 26, 50, 51, 100, 101 and 300 validated for range, damage, health, XP and destruction permissions.
- Road clearance and pedestrian connectivity verified geometrically and through actual traversal. NPC work loops and interrupted/destroyed stations recover. No floating NPCs or vehicle collision failures.
- Nick discovery and difficult completion tested separately; rewards awarded once; failure/retry/reconnect paths work. Selected ordinary NPC quests tested end-to-end.
- Destruction replicates to other/late-joining players, repairs safely, preserves routes and does not create sustained debris/memory growth.
- Premium movement restrictions, equip swaps and arena transitions tested; no purchase prompts until configured/authorized. No unintended paid combat advantage.
- Include a 30-minute representative multiplayer soak at the agreed player target or explicitly report why it could not be run. Do not substitute fake clients for real voice/device testing without labeling the gap.
- Save migration and failed-load behavior checked in isolated test data, never by destructive experimentation on production saves.
- Report executed tests, exact builds/devices, results, known issues and untested areas. Separate screenshots, source inspection, unit tests and live multiplayer evidence. Do not call the game bug-free or claim completion while required gates remain unverified.

### 13. Deliverables

Provide the authored map/layout and style guide; implementation source and reproducible place builds; configured/accessible animations and asset inventory; mic feasibility findings; balance data/simulations; test cases and evidence; migration/rollback notes; developer handoff; and a published version/link only when publication actually succeeds. Keep a concrete remaining-work list if an account, asset, device or owner decision blocks a requirement.

## Research supporting the prompt

Checked October 1, 2026; recheck before implementation because Roblox capabilities change.

- [AudioAnalyzer](https://create.roblox.com/docs/reference/engine/classes/AudioAnalyzer?mobile-app=true&theme=dark): RMS/peak measurements are not replicated, server measurements are zero/empty, and microphone input does not supply a usable spectrum through GetSpectrum. This supports local loudness measurement, not server proof of a genuine scream.
- [AudioDeviceInput](https://create.roblox.com/docs/reference/engine/classes/AudioDeviceInput): supported microphone object and push-to-talk example. Respect property security rather than assuming Active/IsReady are freely usable by experience scripts.
- [Voice Chat](https://create.roblox.com/docs/chat/voice-chat): eligibility/opt-in restrictions, experience settings, audio API routing, and the documented 100-player voice limit. Eligibility is separate from this experience's audience settings.
- [Client/server boundary](https://create.roblox.com/docs/scripting/security/client-server-boundary): validate client requests on the server and limit the consequences of untrusted input.
- [Instance streaming](https://create.roblox.com/docs/workspace/streaming): consider streamed world behavior when designing a large interactive map.
- Existing Barcelona references and prior source-download review: `research/BARCELONA_PLAN.md`. Do not confuse the prior redesign's passing tests with verification of this new scope.
