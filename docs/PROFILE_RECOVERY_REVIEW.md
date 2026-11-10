# Failed-release recovery review

Inspected production head `39beb403e382277b3d3a6dbcd4d01c96ebb0744f`. No production recovery behavior was changed. Run `python tests/profile_recovery.py` with Luau on PATH to reproduce the characterization using actual Profiles/ProfileLease code and two simulated owners sharing an in-memory store. This diagnostic is separate from the default regression suite: it records current failure behavior, not desired future recovery policy.

## Observed boundaries

1. `Profiles.Save(..., true)` attempts UpdateAsync three times, waiting 1, 2 and 3 seconds after failures (six simulated seconds total, excluding store latency). Exhaustion returns `false, "retry"`. The local owned marker remains, and the failed snapshot is not retained by Profiles for background recovery. Detached Bootstrap sessions are no longer visited by autosave; the release callers do not schedule another attempt.
2. With 100 coins last saved and 150 coins in the failed final snapshot, the store stays at 100. Same-server Load returns a temporary default profile plus the previous-session warning. It checks the local owned marker before contacting the store. It still rejects at lease expiry and an additional simulated hour later, including after another owner has saved and released the record. The wording "still saving" does not establish that any save is running.
3. The lease expires 180 seconds after its last successful stamp, not 180 seconds after the failed release. A different owner is rejected just before expiry and can acquire at expiry, receiving the last durable 100 coins. After that owner saves 200 coins, an explicit stale Save from the old owner is rejected and preserves 200. That explicit rejection clears the old local marker, but the normal detached lifecycle does not make this call automatically.
4. Retaining the final snapshot explicitly and retrying while still owner can recover it after the simulated outage. This proves a limited safe retry opportunity; it is not current automatic behavior and cannot recover memory after the server exits.
5. A committed release followed by an injected response error produces a different outcome: the retry sees no owned lease and returns `false, "ownership"`, although all 90 coins were committed and the lease was removed. Rejoin then succeeds. A false return alone therefore cannot identify rollback, persistence failure, or a still-held lease.

## Why no automatic recovery patch

Clearing the local marker alone can reopen an older durable profile and abandon unsaved progress. Blindly retrying a retained snapshot after another owner has written would overwrite newer progress. The two negative controls confirm the current guards matter: removing the save ownership check overwrites the newer snapshot, and removing the acquisition check admits another owner before expiry.

Recovery needs a stated policy for unsaved progress after ownership changes or the originating server disappears. This review does not choose to merge divergent coin/XP/quest snapshots, extend leases indefinitely, or erase ownership checks. The ordinary departure caller also still ignores a returned false/reason (it logs exceptions); the late-load and shutdown paths now report both. That diagnostic inconsistency is separate from recovery and does not establish that retrying is safe.

## Recommendation and decision

Recommend bounded retry of a retained, immutable final snapshot while an atomic ownership check still permits it. Keep that snapshot tied to its acquisition identity and serialize recovery with save/load calls. Reconcile ambiguous responses from authoritative stored state; never interpret an exception or false return as proof of a failed write. Preserve the shutdown deadline and do not promise recovery after process exit.

The owner should choose the fallback when ownership has moved and unsaved progress cannot safely be applied: load the latest durable checkpoint with a clear rollback notice, or block progression pending recovery/support. My recommendation is the latest durable checkpoint with explicit notice, while never applying the stale snapshot over newer data. A durable recovery journal and automatic merging would be a separate design with its own idempotency, storage and retention requirements.

Before implementation/release, specify retry duration, admission/progression behavior during recovery, and what the player sees after rollback. Then test competing acquisition, delayed callbacks, response ambiguity, repeated retries and shutdown deadlines in simulation. Live validation later needs an isolated non-production datastore and explicit authorization; none was accessed here.

## Evidence limits

Twenty-one characterization checks pass. Both ownership-guard omission controls fail at the intended assertions. The full existing check/build command passes 24 pure/synthetic suites, 53 mocked-service suites and 56 production compiles, plus all builds. Exact results are in `tests/evidence/profile-recovery-2026-11-10.json`.

These are serialized in-memory atomic callbacks, injected clock/waits and two module instances with different owner IDs. They do not establish real Roblox concurrent scheduling, throttling, outage behavior, eventual visibility, shutdown timing or successful live persistence. No native Studio execution, live DataStore writes, publication or audio/product configuration occurred.
