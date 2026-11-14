# Voice eligibility recovery and resource bounds

Base: `dbb459c501b78d0f4971251614d76f7351393231`. Astra found no new integrity blocker but identified terminal error exhaustion and conditional retention/concurrency risk. Map is paused; no publication, native service experiment or live persistence.

## Reproduced before correction

- A timely true followed by three refresh errors exhausted the old checker forever. Even after simulated service recovery, Poll produced no request through100,000 seconds and the valid player's cached eligibility expired.
- In legacy mode, BeginCast plus29 other requests saturated the window. CancelCast(nil) was dropped; actual VoiceCombat.Release at0.3 seconds still accepted the capture. This is source-derived dispatcher/protocol execution, not native input/network evidence.

## Correction and tradeoffs

The [current design](VOICE_ELIGIBILITY_REVIEW.md) now uses server-scheduled recovery bursts: three serial attempts,2/5-second short backoff, then30/60/120-second capped recovery with0–10-second deterministic spread. Timely false is still authoritative and revokes immediately, but rechecks after120 seconds plus spread. Positive cache lifetime remains fixed120 seconds with60-second refresh; failures never extend it. Recovery requires deliberate arming.

Global capacity is eight actual calls, paced by at least0.25 seconds between starts. The oldest due current session wins, with deterministic tie-break; no persistent retry queue or accumulated departed roster. Calls retain Player and independent opaque identity/request tokens, not a profile/session local across yielding. Slots release only when a call really returns, including stale/departed calls. Jobs delayed beyond their acceptance deadline skip the API and schedule bounded recovery. No timeout pretends to cancel Roblox work.

This necessarily trades availability for bounded resource use: if all eight engine calls never return, checks cannot resume in that server. Rejoining that same server does not free those slots. Cached positives eventually expire and fail closed. We do not claim a hard total recovery time, zero platform throttling or native cancellation. Once a real call returns, eligible waiting work can proceed under pacing; old results cannot authorize a replacement session.

Nil CancelCast is now quota-independent only in legacy mode and clears an existing capture once. Automatic current-sequence stop and explicit readiness-false behavior remain. Malformed/mismatched stop packets, starts and readiness-true keep the ordinary quota. Neither local retry buttons nor remote spam can schedule eligibility checks. Calibrated movement and ordinary voice transport remain independent.

## Verification

- New recovery suite: **934 assertions** (49 retry/backoff,876 actual scheduler/coroutine API,9 actual legacy dispatcher), **12 negative controls and three source contracts**. Covers eight suspended calls, departed/rejoined identities retaining slots until actual return, fairness against new arrivals/retries, no queued-worker accumulation, spacing under an800-step error storm, deadline-before-start API skip, later slot recovery, current/replacement ownership and quota-safe cancellation with duplicate/malformed/automatic-mode cases.
- Adapted original eligibility suite: **117 assertions,12 negative controls and four source contracts**. Its superseded terminal-retry expectations now assert bounded future recovery; other authentication, timing, cancellation and client rearming protections remain. Both suites independently rerun and cleared. Original two dbb459c failures rerun separately.
- Final full checkpoint passed **25 pure/synthetic suites,84 mocked-service suites,60 production compiles and all candidate/disposable builds**. No production changes after that checkpoint. [Exact tested source and build evidence](../tests/evidence/voice-eligibility-recovery-2026-11-11.json).
- Memory retention is source-reviewed through worker arguments and placement of session lookup after the yielding call, not a forced-GC or native memory measurement. Coroutine API mocks test real Luau scheduling/yield behavior but not Roblox service implementation or network throttling.

No native API, true microphone/amplitude, UI text-fit, Roblox network or live store claim. No apps/tabs were opened. Map/source archive unchanged; no publication or settings changes.
