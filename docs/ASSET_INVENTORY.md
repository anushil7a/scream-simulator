# Redesign asset inventory

Source inspection: October 2, 2026. Applies to `feature/microphone-city-redesign`, not the historical published version 32.

## Authored geometry and visuals

- `src/ServerScriptService/City.luau`: city buildings, storefronts, courtyards, roads, promenade, beach furniture, lookout, pier, soccer court, terrain water and coastal backdrop. Geometry is generated from Roblox primitives and built-in materials. No imported city mesh pack is referenced by current source.
- `src/ServerScriptService/World.luau`: resident rigs, clothing geometry, work props, vehicles and lighting. Residents use generated character geometry; variation is driven by source configuration and seeded choices.
- Resident faces use Roblox's bundled `rbxasset://textures/face.png` texture. This is a platform dependency, not an authored face or uploaded external texture.
- `src/ServerScriptService/Equipment.luau`: original micro-speaker assembled from welded primitive parts. Separate R6/R15 hand selection exists; both final avatar presentations still need physical-device review.
- `src/ServerScriptService/SoccerChallenge.luau`: personal challenge props and targets. `Residents.client.luau` supplies Nick's non-gameplay practice ball visual.
- `src/StarterPlayer/StarterPlayerScripts/ScreamEffects.luau`: generated beam ribbons, rings, strands and particles with bounded pools. These are visual effects, not uploaded audio or animation assets.
- `src/StarterPlayer/StarterPlayerScripts/Client.client.luau`: native Roblox UI, fonts, color styling and transient dodge/destruction effects.

## Animation ownership and dependencies

- `RunAnimation.client.luau` applies authored additive joint poses for player movement and combat. It relies on Roblox's normal character animation underneath. There is no custom uploaded AnimationId in current source.
- `Residents.client.luau` implements local joint animation for generated resident rigs, occupational routines, reading/resting and Nick's practice behavior. Work/action timing comes from server attributes.
- The absence of custom animation IDs avoids a missing-upload dependency; it does **not** establish finished animation quality or compatibility with every avatar. R6/R15 physical controls, blending, interruption and equipment grips remain release checks.
- Player avatars and Roblox's injected character scripts may reference platform assets at runtime. A source-only scan does not inventory each player's accessories or the platform's default animation assets.

## Audio

- November 9: [original quiet energy-beam loop and audition](../assets/audio/README.md), produced by the repository's deterministic Python oscillator generator, with no external samples or voice recordings. Source WAVs, hashes and peak/RMS measurements are included. `AttackAudio`/`BeamAudioMix` provide separate quiet spatial playback, overlap budgeting, local-mic ducking, calibration silence and lifecycle cleanup. Roblox asset ID remains empty pending owner-approved upload and experience permission; actual playback/listening is not verified. This is synthetic energy SFX layered beneath live voice, not a prerecorded scream replacement.

- Added November 6, 2026: location-bound scenery audio in `Ambience.client.luau`, independent of microphone capture and Roblox proximity voice. Four shoreline sources share surf asset 9119677305; the stage uses guitar asset 15675051846 only while a living nearby busker is working. Both are looped with bounded volume/range and routed through the local CityAmbience group. CITY AUDIO changes this group only.
- [Surf Ocean Wave Impact On Zuma Beach 4 (SFX)](https://create.roblox.com/store/asset/9119677305), publisher ProSoundEffects, courtesy of Pro Sound Effects. Free Creator Store audio result; permitted use is through Roblox under applicable Creator Store/platform terms, not an assertion of unrestricted off-platform licensing. Audio-only insertion yielded a Sound with zero children. Native client preload succeeded; duration 40.224 seconds.
- [Roblox_UI_Loop_Guitar_Acoustic](https://create.roblox.com/store/asset/15675051846), publisher Roblox. Free Creator Store audio result. Same platform-use scope; no downloaded model or embedded scripts. Native client preload succeeded; duration approximately 11.971 seconds. Creator Store lookup used the verified-creator filter for both candidates.
- Temporary review Sound instances were removed. Source defines the runtime objects. Published destination asset access, human listening balance and coexistence with two-person live voice remain unverified. These sounds never activate attacks or replay recorded screams.

- `Microphone.luau` uses Roblox audio objects and analyzer readings. The Rojo project enables Audio API/default voice settings. Actual account eligibility, input permissions and two-account proximity voice behavior remain unverified release gates.
- Current `src/` contains no literal uploaded SoundId, TextureId, MeshId, AnimationId or `rbxassetid` references found by the October 2 source scan. This is scoped to repository source, not a claim about all runtime-injected assets.
- No prerecorded attack-scream pack is bundled. Live microphone audio must remain on Roblox-supported transport; do not introduce custom recording storage as an asset pipeline.

## External references and additions

- `research/BARCELONA_PLAN.md` and `research/github-review.json` record earlier design/reference and repository review work. References are not installed dependencies or ownership grants for downloadable art.
- Current generated geometry does not require a downloaded city package. Any future imported mesh, texture, sound or animation must record its source, creator/license, platform ID, ownership/access status, permitted use and script inspection here before being included in a release build.
- Game-pass and badge identifiers remain owner configuration work. They are not substitute placeholder asset IDs and should not be represented as purchasable/redeemable content until configured and tested.

## Release handoff

Build from source using the root README. Generated place files under `build/` are not committed assets. Before publication, verify actual experience ownership/access for any newly added asset IDs, inspect runtime dependencies, and complete the device, animation and live-audio checks in `IMPLEMENTATION_STATUS.md`.
