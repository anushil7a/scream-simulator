# Client voice access request bounds

The actual Microphone module and actual CHECK ACCESS callback reproduced 121 concurrent simulated API invocations and 121 timeout closures after construction plus 120 clicks against historical `0619103`. This is conditional coroutine evidence, not proof of Roblox network request counts or a hardware incident.

## Narrow behavior change

- One actual request per Microphone instance remains pending until its API call returns. Repeated clicks do not change generation, cancel calibration again, enqueue jobs, or allocate timeout callbacks.
- The existing heartbeat Step shows a pending/rejoin notice after ten seconds. This is a notice threshold, not cancellation or a result expiry. There are no separate timeout callbacks to race a newer request.
- A late true/false/error result is accepted for the same live instance, including exactly ten seconds. Only exact true permits local eligibility. Server eligibility remains separately required and unchanged.
- A two-second monotonic cooldown starts on completion, including synchronous success/failure. Clicking during it preserves confirmed eligibility/readiness; unavailable users receive wait guidance. A new accepted check temporarily clears readiness and capture but retains previously validated calibration.
- Destroy fences queued work before the API and yielded work after return. It cannot cancel an already running Roblox API call. A permanently hung call blocks further checks in that instance; wait or leave/rejoin. This bound does not claim cross-instance cancellation, native memory collection, or authentication of voice/power.

## Verification

- `python tests/microphone_check_requests.py --negative-controls`: 49 actual-source assertions, seven explicit controls, one source contract.
- `python tests/microphone_check_requests.py --baseline`: historical 121-call/121-timeout-closure reproduction.
- `python tests/microphone_lifecycle.py`: 111 retained actual-module lifecycle checks, updated from overlapping retries to serial retry/cooldown and heartbeat notice semantics.
- `python tests/microphone_active.py --negative-controls`: existing inactive-input checks remain independent.

The focused harness executes the extracted production Retry callback and complete Microphone module with real MicPower, fake clock/audio instances and coroutine API responses. It checks synchronous and delayed true/false/error, malformed truthy results, repeated clicks, exact cooldown and notice boundaries, preserved calibration, queued/running destruction and late completion. Negative controls remove single-flight/cooldown, alter completion cooldown, advance timeout, retain pending after return, remove completion fences, and remove the pre-call fence separately. No device Active/Muted writes or restricted IsReady reads are added. Tests do not establish physical microphone behavior, Roblox scheduling, network limits, native accessibility or real account eligibility.

No product configuration, map, server gate, publishing, live API calls or device settings changed.

## Integration

Final offline `python tests/verify_local.py --build` passes25 pure/synthetic +96 mocked suites,60 production compiles and all builds. Explicit negative controls are separately run, not implied by the default aggregate. [Commands and exact working-tree/artifact evidence](../tests/evidence/microphone-check-requests-2026-11-11.json). No native/app session was opened.
