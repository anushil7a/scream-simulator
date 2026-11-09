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

## Playback and quiet mix

The server latches the equipped scream style when it accepts an attack and sends that style with beam updates. Each listener resolves the attacker's tier, independently of their own level. One sound plays once per active attacker at its original pitch (`PlaybackSpeed=1`, `Looped=false`); updates move its emitter without restarting the recording. Short clips finish naturally. Longer clips fade when the attack ends, with a 0.16-second cosmetic tail. Combat remains capped at four seconds with a ten-second cooldown.

Up to four active/fading sounds share a combined Sound.Volume budget of 0.24, multiplied by a dedicated 0.65 SoundGroup. Local attacks receive a further 0.7 multiplier; detected local voice ducks SFX toward 0.4 of the current mix. EQ reduces low/mid/high bands by 3/3/4 dB. Calibration silences attack SFX. No player voice gain, recording or transport changes are introduced.

Fade-in is 0.12 seconds; missing beam updates expire after 0.5 seconds; an independent 4.5-second lifetime protects cleanup if end messages are lost. Spatial range is 70 studs. Settings has a session-only ATTACK SFX LOW/OFF switch, separate from CITY AUDIO and Roblox voice controls.

## Remaining checks

Use the disposable current-source build to check all equipped tiers, interrupted attacks, repeated attacks after cooldown, mute, respawn, departure and near/far playback. Compare one and four attackers with headphones and speakers; confirm voices stay intelligible and speakers do not retrigger microphone attacks. Verify destination experience access before a release. GitHub integration is authorized; Roblox publication still requires owner approval.

## Superseded synthesized draft

`energy-beam-loop.wav`, `energy-beam-preview.wav`, `audio-audit.json` and `tools/make_energy_audio.py` preserve the earlier original synthesized draft for history. They are not used by the current runtime. Their peak/RMS measurements do not describe the owner-selected Roblox assets. No upload of these drafts is needed for this implementation.
