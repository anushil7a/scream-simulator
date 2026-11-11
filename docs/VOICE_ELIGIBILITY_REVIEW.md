# Server voice eligibility gate

Base: `e977040ed6656948f2cff920ab102f1009ec705c`. Map work remains paused. No Roblox publication, setting changes or live persistence.

## Reproduced trust gap

The actual Action dispatcher and canCapture helper accepted a client-supplied MicReady(true) without server voice-eligibility evidence. With synthetic power1, the automatic protocol produced3 simulated damage at0.2 seconds, and the legacy Begin/Release path also accepted. Engine geometry and transport were mocked: this is not a native network exploit demonstration.

## Scope and authoritative limits

Roblox documents server `VoiceChatService:IsVoiceEnabledForUserIdAsync` for players currently in that server. It yields and can throw an HTTP error. The result establishes account voice-enabled status, not current speech, connection, mute state or trustworthy amplitude. Server-side AudioAnalyzer processing is disabled; its volume properties return zero. This change does not authenticate the client's power or prevent an eligible client from fabricating it. Existing server cooldown, duration, geometry, targeting, progression and damage limits remain essential.

Official references checked November11,2026:
- https://create.roblox.com/docs/reference/engine/classes/VoiceChatService.md
- https://create.roblox.com/docs/reference/engine/classes/AudioAnalyzer.md
- https://create.roblox.com/docs/reference/engine/classes/AudioDeviceInput.md
- https://create.roblox.com/docs/scripting/security/client-server-boundary

No Chat&Voice Groups API, new terms, account identifiers sent to an unrelated service, voice recording, moderation, audio product or experience configuration is introduced. Only the documented Roblox service checks the present player's UserId.

## Design

- A server-only pure state machine owns eligibility. Client readiness stays separate, preserving calibrated movement, dodge/jump and other nonattack flows. Ordinary proximity voice is untouched.
- Initial checks are pending/failclosed. Only exact boolean true from a timely successful API call permits beams. Both automatic begin/pulse/tick and legacy begin/release use the same canCapture gate.
- Each accepted positive is cached for120 seconds from its timely response, with refresh due after60 seconds. A timely authoritative false revokes immediately. Errors never extend the old expiry; known positives remain usable only until that fixed deadline. Cached eligibility is not continuous platform verification and can become stale before expiry.
- Each refresh allows at most three serial attempts, with2/5-second backoff. An eight-second deadline stops accepting that request's result, not the underlying yielding API call. If the call hangs, there is no overlapping retry. A late return is discarded before a remaining bounded retry can be scheduled. A permanently hung call remains one pending worker for that session until the platform call returns; departure prevents its result from affecting gameplay.
- False and exhausted failures require rejoining to restart verification. Existing local CHECK ACCESS and calibration do not restart this server budget. This deliberate availability tradeoff fails closed rather than trusting the client or allowing request spam to amplify API calls.
- Requests are polled by the existing server tick, not attack remotes. Both sides of the async call check the exact session object, player presence and shutdown flag. Old session callbacks cannot authorize a replacement session. Missing state fails closed.
- Expiry/revocation cancels active sustained and legacy capture. Explicit stop/microphone-false handling stays ahead of action throttling and never waits for eligibility. Existing cooldown semantics remain.
- The only bypass is the existing strict local fixture: Studio AND PlaceId0 AND server LocalSustainedPrototype flag, where every profile is temporary. Ordinary Studio, owner privilege and testBaseline alone do not bypass eligibility.
- Client beam gating is separate from the movement gate. Every received ineligible State update immediately disarms/cancels, even if recovery arrives before the next rendered frame. Recovery requires deliberate arming. The normal initial successful calibration retains its existing automatic onboarding behavior; an initial unavailable/denied state suppresses that automatic arming.
- Compact persistent two-line meter guidance distinguishes checking, denied and unavailable/rejoin. Attempting to arm explains that ordinary voice is unchanged. This is source/layout intent, not native readability or accessibility proof.

## Review and verification

Independent review caught and corrected shared dodge gating and frame-only disarm before commit. It also found a false-positive callback contract and missing actual cache-expiry cancellation coverage; both tests were tightened and mutation-checked.

- **117 focused assertions**:71 state-machine timing checks,30 actual dispatcher/capture/async-helper checks,16 actual client-transition checks. **13 negative controls and four source contracts**, independently rerun and cleared. Historical e977040 spoof reproduction was rerun separately.
- Source-derived fixtures exercise both protocol gates, exact8-second and120-second boundaries, no overlap while a call hangs, bounded retry, stale tokens, distinct pre/post-yield session fences, departure/shutdown, authoritative denial, expiry cancellation, saturated stops, deliberate rearming and false/true updates before a rendered frame.
- Existing availability17, toggle29/two controls, action-feedback14/four controls, notification lifecycle1,217/two controls, save-priority210/seven controls and shutdown34 pass. Five fixtures received only the new dependency stubs or explicit simulated eligibility needed to retain their original scopes.
- Final aggregate: **25 pure/synthetic suites,83 mocked suites,60 production compiles and all candidate/disposable builds pass**. The runner now excludes reserved tmp*.luau generated fixture files so concurrent focused reviews cannot race standalone-suite discovery. An initial run hit that discovery race; the next caught missing old fixture dependencies; neither failed run is represented as a pass.
- [Exact source/build hashes and evidence](../tests/evidence/voice-eligibility-2026-11-11.json).

Native Roblox API behavior, actual throttling, real microphone, network replication, physical input and text fit remain release gates. Simulated tests do not establish those properties. The guarded disposable fixtures deliberately bypass real eligibility and cannot validate the API. Account-level verification must be exercised separately in a permitted native Roblox session with appropriate test accounts before release; no new publication or live service experiment was performed. No apps/tabs opened or closed.
