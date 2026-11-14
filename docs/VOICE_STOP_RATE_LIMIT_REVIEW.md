# Voice stop priority under request saturation

Base: `909dcebc356f8207b4b27cee21c80c5ebe16f50c`. Parallel read-only controls audit identified the gap; a separate test worker reproduced it before production editing, and an independent reviewer inspected/reran the fix.

## Reproduction and scope

The Action handler admitted at most 30 ordinary messages per player per second. Only Sprint(false) bypassed that quota. The controller sent one SustainedStop then cleared local attack ownership, while the dispatcher could drop that stop or MicReady(false) after saturation.

The baseline test executes the actual Action dispatcher, end/cancel helpers, SustainedAttack adapter/protocol and client cancellation paths. Begin plus 29 filler requests fills the window. OFF, focus loss, mic loss, or explicit MicReady(false) at 0.01 seconds is dropped; protocol Steps at 0.2/0.4 emit two damage resolutions totaling 5 synthetic damage. Timeout at 0.501 ends the attack. This is a synchronous scalar-geometry simulation, not a live player injury or full native damage-pipeline measurement.

## Narrow correction

- A SustainedStop bypasses quota only while an active attack exists and its current sequence equals the supplied value. Existing Stop and end helpers retain expiration semantics, cooldown, intent cleanup and one end broadcast. Prechecking matters because Stop can expire state before validating its sequence.
- Explicit boolean MicReady(false) disables readiness and clears active sustained/legacy capture before ordinary quota. An already-false but still-active/capturing session is cleaned too. Fully idle duplicate false packets do not repeat cancellation or attribute writes.
- Stale/malformed/idle stop packets, readiness true, starts, pulses and other actions retain the existing quota/validation path. No new action, power, readiness, movement or reward is granted. Session ownership remains the authenticated event sender's session.
- No client, map, save, geometry, cooldown duration or attack-budget production change.

## Verification

Corrected four cancellation cases emit zero later protocol damage/resolutions and exactly one end broadcast. 89 assertions and 4 negative controls pass independently. Cases include malformed/stale sequences, a newer attack, expired matching/mismatched stops, timeout-derived cooldown, one-thousand duplicate stop/false packets, fresh quota windows, readiness true/starts/pulses remaining limited, legacy capture, inconsistent false+active state, two players with identical sequence values and ordinary unsaturated stops.

Existing sprint dispatcher 184 assertions/four controls and voice-toggle 29 assertions/two controls pass. Full 25 pure/synthetic  + 80 mocked suites, 59 production compiles, candidate source audit and all disposable builds pass. [Exact evidence](../tests/evidence/voice-stop-rate-limit-2026-11-11.json).

Transport is synchronous and geometry/context are mocked; legacy Cancel is a counted equivalent. This does not prove native RemoteEvent delivery, real microphone/focus behavior, physical-device timing, network latency/loss or the full health pipeline. Packets already in transit and damage applied before the server processes a stop are not undone. No native execution, publication, live DataStores or new apps. Map work remains paused pending owner approval.
