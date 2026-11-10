# Bounded profile recovery

Implemented from `a13abf7eefdefccf81d7a2948e891d4347b2b4cf` after the owner approved last-confirmed-save fallback and a recent-progress warning. Earlier investigations are preserved in Git history and `tests/evidence/profile-recovery-2026-11-10.json` / `departure-release-2026-11-10.json`.

## Recovery and player behavior

Normal saves retain their existing three-attempt policy. A terminal failed release retains one detached final snapshot, its acquisition identity, operation revision and last confirmed checkpoint in server memory. Gameplay stays detached. Recovery runs when that user rejoins the same server: at most three additional attempts, with 1/2-second backoff and a 12-second deadline for starting further recovery attempts. It is serialized with saves and acquisition. The existing shutdown deadline is unchanged; there is no untracked background writer.

After recovery, the loader atomically reads/acquires the stored record. On failure to recover, it uses that latest durable checkpoint and warns: **Loaded the last confirmed save. Recent progress may be missing.** It can replace only its own exact terminal acquisition before lease expiry. It never steals another active acquisition. An expired foreign lease can be acquired under the existing 180-second rule, also with a conservative warning. Successful recovery of the final snapshot does not report rollback.

If a foreign lease is still active, the observed checkpoint is temporary/read-only. If storage also fails, a locally confirmed or callback-observed checkpoint is temporary/read-only; without any confirmed checkpoint, defaults remain explicitly unconfirmed and unsavable. Read failure never grants ownership or enables writing defaults. Players must rejoin to try obtaining a writable session later. Temporary gameplay is not persisted.

A persistent HUD warning complements the load message. Desktop shows `Recent progress may be missing`; compact HUDs show `RECOVERED` or `UNSAVED` with `progress may be missing`. The recovery flag survives ordinary State updates for that session. Test sessions retain their temporary-progress status.

## Why stale recovery cannot replace newer protocol saves

- Each acquisition uses JobId, a module GUID and a monotonic acquisition counter. Every write checks the exact token, not just JobId. The terminal local takeover checks the exact previous token as well.
- Returned profile tables and sanctioned Sanitize baseline copies are bound in memory to their acquisition. A stale handle cannot borrow a newer local session's write authority, including calls made after rejoin.
- A save captures a detached snapshot and increments a per-acquisition revision. Stored `_save` metadata identifies the committed token/revision. An identical retry returns the current record unchanged; it does not restamp or release the newer owner's lease. A later same-acquisition revision blocks an older operation.
- Every UpdateAsync callback rechecks the actual record it receives. No cached ownership decision is reused when Roblox re-invokes a callback. A lost response therefore either reconciles the already committed operation, or falls back to current data without overwriting a newer owner/save.
- Acquisition preserves the last operation marker and its recovery-warning flag across ambiguous responses. Sanitize excludes persisted protocol metadata from gameplay data.

These checks follow Roblox's documented [UpdateAsync callback retry/cancellation behavior](https://create.roblox.com/docs/reference/engine/classes/GlobalDataStore). The safety guarantees apply to saves using this protocol; arbitrary manual store edits or older external writers must be excluded during release migration.

## Verification

`python tests/profile_recovery.py --negative-controls` passes 53 cloned-store checks and rejects seven targeted mutations: removed ownership fence, revision fence, profile binding, recovery deadline, committed-operation recognition, same-job acquisition fence, and detached snapshot copying. Cases cover transient/permanent outage, recovery exhaustion, cached fallback, foreign expiry/takeover, same-server reacquisition, delayed/concurrent rejoin, old callback replay, callback reinvocation after contention, lost release/autosave/acquisition responses and sanctioned developer baselines. The old characterization entry point now runs the current policy regression; it is part of the default suite.

`python tests/verify_local.py --build` passes 24 pure/synthetic suites, 55 mocked-service suites, 56 production compiles and all candidate/disposable builds. Notice verification includes seven actual formatter assertions, eleven progress-label assertions and four source-wiring contracts. The disposable UI-only Studio fixture passes 33 layout cases, including six recovery-warning states across 390x844, 844x390 and 1280x720. This UI fixture has mocked profiles/remotes and no persistence service.

Separate post-implementation self-review checked the ownership/revision invariants, ambiguity handling, lock ordering, shutdown tracking, baseline compatibility, callback replay tests and notice behavior. It caught and corrected two gaps before the final run: narrow screens lacked a persistent warning, and failed acquisition responses could discard a checkpoint already observed by the callback. No separate reviewer is claimed. Exact results, build/source hashes and UI rows are in `tests/evidence/bounded-recovery-2026-11-10.json`.

## Limits and release gates

The 12-second deadline stops new recovery requests; an already yielding engine call cannot be cancelled and can take longer. Normal acquisition still has its separate three attempts. Per-user lock waits also depend on earlier requests completing. No hard wall-clock join/shutdown guarantee is made.

Pending snapshots are in memory, one per failed profile, until rejoin or server exit; they are not a durable journal and cannot recover unsaved progress after process loss. A different server has only the stored checkpoint. An acquisition that commits but loses every response can leave a lease until expiry; the fallback stays read-only rather than guessing ownership. Notices say progress *may* be missing because ambiguity does not prove rollback.

Persistence evidence uses cloned in-memory records, controlled time, callbacks and coroutines, not real DataStore traffic, engine throttling, internet failures, concurrent Roblox servers or shutdown deadlines. Native testing here covers UI layout only. Physical devices, real microphone, multiplayer, live save/migration and mixed-version drain remain unverified. No live DataStore was accessed, no game published and no audio configured. Before publication, validate in an explicitly authorized isolated store and drain incompatible older servers.
