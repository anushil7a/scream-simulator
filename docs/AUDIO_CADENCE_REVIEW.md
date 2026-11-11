# Beam audio frame-cadence correction

## Reproduced issue

At `327e1dd`, the RenderStepped callback updated the beam mixer below the 0.15-second HUD gate while passing only the current frame delta. The actual-source synthetic fixture at 30 Hz produced six mixer calls and supplied 0.2 seconds of delta during one elapsed second. The mix uses delta for exponential duck/recovery smoothing, so it ran too slowly and voice/calibration changes waited for the HUD gate. A source-schedule calculation at 60 Hz over the first 0.15 seconds gives duck 0.763918 instead of the frame-driven 0.406665. Those are mix scalars, not measured loudness.

## Narrow correction

Move the existing `attackAudio:Step` call immediately above the HUD throttle, alongside gameplay audio. It now executes once per rendered frame using that frame's delta and current mic state. Leave the HUD throttle, mixer formula and its 0.25-second stall clamp unchanged. Fade/lifetime decisions still use the current clock. At most four active/fading beam emitters remain allowed. No asset, pitch, budget, server, combat, microphone capture, map or save changes.

Calibration zero gain and the detected-voice budget cap now apply on the next rendered mixer update rather than the next HUD tick. This does not eliminate microphone detection/render stalls or certify feedback prevention, comfortable volume or safe SPL. No native listening or real-device audio run was performed.

## Verification

- `tests/beam_audio_cadence.py --negative-controls`: 344 assertions and three controls. Actual callback slice and real mixer/settings under synthetic 30/60/144 Hz, jitter and stall schedules; exactly-once calls and original dt, calibration/voice state on a non-HUD-threshold frame, recovery, fade and timeout cleanup.
- Controls restore the old gate, duplicate the mixer call, or replace frame delta with 0.15. Each fails its intended assertion.
- Historical `--baseline` reproduces missing per-frame updates.
- Independent review reran focused checks and cleared the production correction. The fixture does not execute the complete UI callback or Roblox sound engine.
- Full 25 pure/synthetic + 72 mocked suites, 57 production compiles and all candidate/disposable builds pass. See `tests/evidence/audio-cadence-2026-11-11.json`.

No apps opened, publication, live DataStores or audio configuration. The three earlier inaccessible minimized app-picker dialogs were not touched. Map preservation/redesign is a separate checkpoint.
