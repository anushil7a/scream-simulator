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
- A sixth scheduled attack exercises the actual SCREAMS toggle helper. OFF sends one matching accepted stop before either expiry deadline, leaving synthetic mic input and server readiness intact. ON cannot bypass/reset cooldown; OFF stays off through cooldown expiry and fresh quiet/speech. This invokes the helper directly, not a physical button gesture.

## Stop and replay evidence

The fixture wraps the actual server adapter calls without yielding, forwarding arguments and returns unchanged. It copies state immediately before and after each call. Five replay/malformed requests must return the expected rejection and leave active sequence, power, aim, sample, pulse timestamp, start time, cooldown and consumed sequence unchanged. Later valid client pulses cannot overwrite these recorded copies.

The sequence-5 quiet transition and sequence-6 toggle OFF must each schedule exactly one matching stop and produce an accepted server Stop with end reason `stop`. Their server timestamps must precede both the input-timeout and maximum-duration deadlines. Waiting for an inactive attack alone is insufficient.

Studio truncates long output lines. The complete server report is also printed as ordered `VOICE_TRANSPORT_EVIDENCE <index> <count> <chunk>` records, with at most 700 JSON characters per chunk. Concatenate chunks in index order before parsing; require all chunks. The report includes the five replay snapshots and the explicit-stop snapshot.

The toggle checkpoint's complete report, layout cases and limits are in `tests/evidence/scream-toggle-2026-11-10.json`. Run `python tests/voice_toggle.py --negative-controls` for isolated helper/controller/adapter and actual CharacterRemoving-callback checks with mocked services. It also proves the active-stop and OFF-recovery assertions reject deliberately broken controller instances; these are synthetic negative controls, not new native mutation runs.

Build and run these intentionally broken disposable variants separately, using the same Play procedure:

```
python tests/build_sustained_review.py --transport-mutation drop-stop
python tests/build_sustained_review.py --transport-mutation corrupt-replay
```

- `VoiceTransportDropStop.rbxl` drops only the final sequence-5 scheduled stop. It must fail with `No explicit quiet SustainedStop reached the server`, even if the attack subsequently times out.
- `VoiceTransportCorruptReplay.rbxl` changes power/aim on a rejected repeated sample. It must fail with `Replay mutated immediate server state: power`, even though later normal pulses can repair that state.

Mutations affect generated temporary files only; production sources and the regular candidate are untouched. Each mode has a distinct source fingerprint and provenance sidecar. A mutation run passing, or failing earlier for a different reason, does not validate the negative control.

## Scope limits

This is one local Studio client/server transport test. It is not real microphone acquisition/calibration, voice-chat proximity transport, physical keyboard/phone interaction, internet latency/loss, multiplayer contention, or live datastore validation. The test microphone stays unavailable after completion; restart the disposable session for another run. Snapshot calls add test-only traffic, so this is not a performance benchmark. No audio or product configuration is changed.

The original transport run is recorded in `tests/evidence/voice-transport-2026-11-10.json`; its quiet-stop/replay assertions had masking risks. The tightened assertions and negative-control results are recorded in `tests/evidence/transport-assertions-2026-11-10.json`. The production candidate includes neither the appended fixture code nor its probe remote.
