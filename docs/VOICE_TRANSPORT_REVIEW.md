# Automatic-voice transport review

Run `python tests/verify_local.py --build` with the repository Luau/Rojo tools on PATH. Open `build/VoiceTransportReview.rbxl` as a local file in Studio and press Play. Keep the client viewport focused and do not interact during the run. Allow up to 90 seconds for startup and the real cooldown waits. Inspect Output for `VOICE_TRANSPORT_NATIVE` and `VOICE_TRANSPORT_CLIENT`, with `passed: true` and matching `sourceSha256`. Stop Play afterward. Never publish this fixture.

## What runs

The builder appends test code to the real Client and Bootstrap scripts in a separate guarded place. The normal client RenderStepped callback calls the actual SustainedControls scheduler. Its original send callback fires Action; the real OnServerEvent handler validates each request. The normal server loop resolves the authored practice target. Actual State events and replicated acknowledgement/cooldown attributes feed the client.

The fixture replaces microphone acquisition with explicitly synthetic readiness/power, supplies a fixed aim, and sets initial focus. Server setup uses a temporary level-one profile, anchors the avatar at the practice line, and clears spawn protection. A local-only RemoteFunction sets up/restores that state and reads snapshots; it never accepts or advances test attacks. Unlike the earlier adapter fixture, cooldowns and pulse scheduling use elapsed runtime rather than injected timestamps.

## Covered behavior

- Malformed begin payloads and invalid sequence/power values arrive through Action in a confirmed eligible server context, without creating an attack or practice hit.
- A consumed sequence is rejected; the client waits for acknowledgement, sends one stop with no pulses, and recovers after fresh quiet/onset.
- Acknowledged attacks schedule increasing pulse samples with bounded cadence, reach the practice target, and avoid duplicate completion feedback.
- Replayed begin/pulse, malformed sample, and stale stop do not mutate the active attack. A fresh pulse with nonfinite aim cancels it.
- A new sequence cannot bypass server cooldown. Held synthetic voice does not restart at expiry. Fresh quiet/onset recovers after a consumed cooldown sequence.
- Synthetic availability loss traverses the actual MicReady/Stop path and disarms. Restoring readiness does not auto-resume; manual resume still requires fresh quiet. Quiet-stop reaches the server and stops feedback.

## Scope limits

This is one local Studio client/server transport test. It is not real microphone acquisition/calibration, voice-chat proximity transport, physical keyboard/phone interaction, internet latency/loss, multiplayer contention, or live datastore validation. The test microphone stays unavailable after completion; restart the disposable session for another run. Snapshot calls add test-only traffic, so this is not a performance benchmark. No audio or product configuration is changed.

Build identity and observed results are recorded in `tests/evidence/voice-transport-2026-11-10.json`. The production candidate includes neither the appended fixture code nor its probe remote.
