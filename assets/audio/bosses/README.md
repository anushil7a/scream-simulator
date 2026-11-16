# Original boss warning and impact cues

Ten original procedural mono 16-bit PCM WAVs, 24 kHz. Generated entirely with
Python standard-library oscillators and seeded noise, without downloaded samples,
recordings, speech, or borrowed melodies. Each warning has a visually paired runtime
cue; sound must never be the only attack warning. Tell/impact distinction comes from
rhythm, spectrum and envelope rather than higher volume. The `leviathan` routing key
is the Seagull Siren Captain: maritime horn/cutlass identity, not a sea monster.

Peak <= 0.46 full scale, tapered starts/ends, near-zero DC. Peak-safe source files do
not establish safe playback loudness or good game mixing. Runtime warning priority,
concurrency caps, spatial attenuation, cleanup and actual-device listening remain
integration responsibilities. No Roblox asset IDs assigned and no uploads performed.
These WAVs are delivery sources, not yet audible custom Roblox assets; keep approved
runtime fallback until the owner authorizes import/upload and the IDs are verified.

Rebuild: python tools/make_boss_audio.py
Verify deterministic bytes and audits: python tools/make_boss_audio.py --check
