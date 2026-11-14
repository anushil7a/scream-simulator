# Original gameplay audio

Four locally synthesized, voice-first one-shot cues. No external recordings, samples,
libraries, downloaded code, or franchise audio are used. The generator uses only the
Python standard library and fixed seeds. These files do not replace the owner's
equipped-scream audio. All WAVs are mono 44,100 Hz, 16-bit PCM.

## Assets

| File | Duration | Peak | RMS | Intended event |
| --- | --- | --- | --- | --- |
| hit-confirm.wav | 0.09 s | -14.00 dBFS | -27.81 dBFS | Tight rounded tick for a confirmed hit; rate-limit sustained-hit playback. |
| dodge-whoosh.wav | 0.25 s | -16.00 dBFS | -30.45 dBFS | Soft filtered-air sweep for a confirmed roll/dodge. |
| prop-break.wav | 0.40 s | -13.50 dBFS | -35.53 dBFS | Muted material crack with restrained debris for an actual prop break. |
| level-up.wav | 0.65 s | -15.50 dBFS | -24.74 dBFS | Gentle rising three-tone reward for an actual level increase. |

## Audition

Play `gameplay-preview.wav` at a low, comfortable device volume. The preview
uses the exact asset PCM without extra gain. Labels are listed below rather
than spoken into the file; no voice samples are present.

| Cue | Start | End |
| --- | --- | --- |
| hit-confirm | 0.35 s | 0.44 s |
| dodge-whoosh | 1.04 s | 1.29 s |
| prop-break | 1.89 s | 2.29 s |
| level-up | 2.89 s | 3.54 s |

## Regenerate and verify

From the repository root, run `python tools/make_gameplay_audio.py` to rebuild this
folder. Run `python tools/make_gameplay_audio.py --check` to regenerate in memory
and compare every WAV, this README, and the JSON manifest byte-for-byte without
writing. The manifest contains file SHA-256 hashes, the generator hash, PCM
levels, boundary/DC checks, durations, and the preview cue frames.

The generator validates actual exported PCM headers/payloads, duration, non-silence,
zero-valued start/end samples, modest peak/RMS bounds, DC, and absence of clipping.
Determinism was checked with the installed Python runtime; math-library changes
on other systems may affect rounding near a quantization boundary.

## Integration and remaining checks

These are local candidate assets, not uploaded Roblox IDs. No asset access, runtime
playback, publication, or human-listening approval is implied. Upload the four
individual cues only after the owner approves upload and intended experience
access, then configure the returned IDs. Do not upload the combined preview.

Use quiet runtime gain, bounded simultaneous sources, event throttling, voice
ducking, calibration silence, and a user off control. Do not retrigger the hit
cue every damage tick or the level cue for each intermediate level in one reward.
Check actual repeated-hit/dodge/destruction/reward flows, cleanup and mute, then
listen with headphones and speakers alongside player voice and equipped-scream
audio. Loudness, intelligibility and microphone-feedback comfort still require
human/device testing. Numerical dBFS is not a hearing-safety guarantee or LUFS.

Asset provenance is the original generator here. No legal conclusion about
copyright ownership or a third-party library license is asserted.
