# Quiet energy-beam attack audio

Second audio draft: original synthesis targeting the sharp rushing roar, electric flutter and rising whine of classic Dragon Ball-style beams. The owner rejected the earlier soft-hum direction; this stronger draft still needs audition approval. No Dragon Ball samples, character voices, music, recordings or downloaded third-party audio are used. Regenerate with `python tools/make_energy_audio.py` (Python standard library only). This generator and these outputs are authored for this game.

- `energy-beam-loop.wav`: upload source; seamless 2-second mono PCM16, 44.1 kHz. Master peak -9 dBFS, RMS approximately -16.7 dBFS.
- `energy-beam-preview.wav`: 4.16-second audition with a rising onset, four-second attack and short falling release. Louder than the proposed in-game mix for review; not the upload source.
- `audio-audit.json`: deterministic hashes and measured sample peak/RMS/boundary continuity. These measurements do not establish listening quality or relative loudness against live players.

## Integration status

Playback is wired to accepted sustained-beam messages. One loop is reused per attacker, up to four simultaneous/fading sounds. The combined Sound.Volume budget is 0.24, multiplied by a dedicated 0.65 SoundGroup. Local attacks are quieter again (0.7 multiplier); detected local voice ducks the SFX toward 0.4 of the current mix. EQ reduces low/mid/high bands by 3/3/4 dB. No gain is applied to player voice, and no voice is recorded or rerouted. Calibration silences attack SFX. Native speech intelligibility, speaker feedback and two-player listening still require testing.

The effect rises in pitch for 0.22 seconds at attack onset, then sustains. End messages fade/drop pitch over 0.16 seconds. Missing updates expire after 0.5 seconds; total lifetime is capped independently. Spatial range is 70 studs. Settings has a session-only ATTACK SFX LOW/OFF switch, separate from CITY AUDIO and Roblox voice controls.

**Not uploaded or audible in the game yet.** `Shared/AttackAudioConfig.LoopAssetId` is deliberately empty. After owner approval, upload only `energy-beam-loop.wav` privately under the experience's owner/group, grant the intended test experience permission, and set its returned `rbxassetid://...` in that configuration. Do not invent an ID or substitute an unreviewed asset. Rebuild and verify preload, actual playback, interruption/cleanup, near/far balance and two-person voice clarity before requesting a game release.

Owner approval is required for the Roblox upload. Updating this repository does not upload the asset or publish the game.

References: [Roblox audio assets](https://create.roblox.com/docs/audio/assets), [sound groups](https://create.roblox.com/docs/sound/groups), [Sound](https://create.roblox.com/docs/reference/engine/classes/Sound).
