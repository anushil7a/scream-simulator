# Owner-selected attack audio

The owner supplied these Roblox audio IDs on November 9, 2026 for the corresponding equipped scream tiers. `Shared/AttackAudioConfig.AssetsByLevel` is the runtime mapping. Level 1 stays voice-only because no starter effect was supplied.

| Scream unlock level | Roblox audio asset ID | Loaded duration |
| --- | --- | --- |
| 10 | `112589551277234` | 2.112 s |
| 20 | `71125574109613` | 4.113 s |
| 30 | `72820033812084` | 4.272 s |
| 40 | `116444869617367` | 3.323 s |
| 50 | `110531388862916` | 3.077 s |
| 60 | `72657289722275` | 2.824 s |
| 70 | `8899285496` | 5.400 s |
| 80 | `102380291908556` | 5.784 s |
| 90 | `80523108386394` | 4.215 s |
| 100 | `79853512837585` | 4.232 s |

All ten returned `Success` and `IsLoaded=true` in a silent local Studio check (place/universe 0). See [asset-load evidence](../../tests/evidence/attack-audio-assets-2026-11-09.json). This verifies local asset loading, not access in City Preview, actual gameplay playback or listening balance. These are owner-selected external Roblox audio references; no third-party recordings are downloaded or bundled here, and creator/licensing metadata has not been independently reviewed.

## Playback and selectable beam mix

The server latches the equipped scream style when it accepts an attack and sends that style with beam updates. Each listener resolves the attacker's tier, independently of their own level. One sound plays once per active attacker at its original pitch (`PlaybackSpeed=1`, `Looped=false`); updates move its emitter without restarting the recording. Short clips finish naturally. Longer clips fade when the attack ends, with a 0.16-second cosmetic tail. Combat remains capped at four seconds with a five-second cooldown after attack end.

Up to four active/fading sounds share a combined Sound.Volume budget: NORMAL (default) is 0.40 and LOW retains the original 0.24, multiplied by a dedicated 0.65 SoundGroup. The nominal non-speaking aggregate ceilings before EQ/spatial attenuation are 0.26 and 0.156. This is not a measured sound-pressure level or perceived-loudness guarantee. Local attacks retain a further 0.7 multiplier. When the existing voice-active flag is true at a mix update, NORMAL is capped back to the LOW budget before existing ducking toward 0.4, preserving the previous voice-active ceiling rather than making local speech-triggered effects stronger. EQ still reduces low/mid/high bands by 3/3/4 dB. Calibration applies zero at the next mix update. No player voice gain, recording or transport changes are introduced.

Fade-in is 0.12 seconds; missing beam updates expire after 0.5 seconds; an independent 4.5-second lifetime protects cleanup if end messages are lost. Spatial range is 70 studs. Settings has a session-only BEAM SFX NORMAL/LOW/OFF cycle, separate from CITY AUDIO, gameplay cues and Roblox voice controls. OFF stops and destroys current emitters immediately; re-enabling waits for a fresh valid beam pulse. The original scheduled mix update (roughly every 0.15 seconds, given the current frame loop) remains, so mode gain/ducking/calibration are not instantaneous and cannot guarantee feedback prevention. Level 1 still has no assigned beam effect. See [level-control review](../../docs/BEAM_AUDIO_LEVELS_REVIEW.md).

## Remaining checks

Use the disposable current-source build to check all equipped tiers, interrupted attacks, repeated attacks after cooldown, mute, respawn, departure and near/far playback. Compare one and four attackers with headphones and speakers; confirm voices stay intelligible and speakers do not retrigger microphone attacks. Verify destination experience access before a release. GitHub integration is authorized; Roblox publication still requires owner approval.

## Superseded synthesized draft

`energy-beam-loop.wav`, `energy-beam-preview.wav`, `audio-audit.json` and `tools/make_energy_audio.py` preserve the earlier original synthesized draft for history. They are not used by the current runtime. Their peak/RMS measurements do not describe the owner-selected Roblox assets. No upload of these drafts is needed for this implementation.


## Original gameplay feedback candidates (November 10)

The separate [gameplay pack](gameplay/README.md) adds an original hit-confirm tick,
dodge whoosh, restrained prop-break/debris cue and gentle level-up reward. Its
reproducible generator, WAVs, acoustic audit and combined audition are local.
The ten owner-selected equipped-scream assets above are unchanged.

`Shared/GameplayAudioConfig` maps the four new cues. All IDs are currently empty,
so these cues are intentionally silent in-game until their original WAVs are
uploaded and permitted for City Preview (universe 10769005350). The Settings
control shows `GAMEPLAY SFX: PENDING UPLOAD` while no asset is configured.
Importing audio assets is separate from publishing a place. No experience
publication is authorized by this sound-design work.

The client hooks existing server-confirmed hit, dodge and destruction events.
A level increase cues once, excluding first profile sync, repeated state,
level reductions and temporary test sessions. Cosmetic behavior does not modify
combat rules, rewards, saves or voice transport.

Up to six one-shots share total volume 0.12 through a 0.5 SoundGroup; voice ducks
them to 35% of that level. Calibration/not-ready microphone state clears and
suppresses cues. Hit/dodge/break rate limits are 0.16/0.15/0.12 seconds; level-up
is limited to once per second. Dodge/break are spatial within 50 studs; hit and
level-up are local. Short bounded lifetimes, mute, character removal and script
teardown clean every emitter. This is an additional quiet SFX budget beside the
existing attack mix, not a change to that mix.

Local evidence: 55 pure mixer checks, 26 mocked actual-adapter checks and six
source hookup checks. Full repository validation passed 24 pure/synthetic suites,
51 mocked suites, 56 production compiles and all current candidate/disposable
builds. These are not native playback, audibility, human preference, physical
phone, multiplayer or speaker-feedback results. Audition and test with real
microphones before release. See `tests/evidence/gameplay-audio-2026-11-10.json`.

Upload remains pending after the earlier browser URL verification blocker. The supported next step is for the owner to import the four individual WAVs through Roblox Studio Asset Manager or a verified Creator Dashboard, grant the intended experience access, and supply the returned IDs. Then configure and test playback in a disposable local place. See https://create.roblox.com/docs/audio/assets.
