# Bounded profile recovery

Initial policy implemented from `a13abf7eefdefccf81d7a2948e891d4347b2b4cf`; admission/notice correction starts from `10489aa486f32e1d18131725c46d34066151c3ed`. The owner approved last-confirmed-save fallback and a recent-progress warning. Earlier investigations are preserved in Git history and `tests/evidence/profile-recovery-2026-11-10.json` / `departure-release-2026-11-10.json`.

## Recovery and player behavior

Normal saves retain their existing three-attempt policy. A terminal failed release retains one detached final snapshot, its acquisition identity, operation revision and last confirmed checkpoint in server memory. Gameplay stays detached. Recovery runs when that user rejoins the same server: at most three additional attempts, with 1/2-second backoff and a 12-second deadline for starting further recovery attempts. It is serialized with saves and acquisition. The existing shutdown deadline is unchanged; there is no untracked background writer.

After recovery, the loader atomically reads/acquires the stored record. On failure to recover, it uses that latest durable checkpoint and warns: **Loaded the last confirmed save. Recent progress may be missing.** It can replace only its own exact terminal acquisition before lease expiry. It never steals another active acquisition. An expired foreign lease can be acquired under the existing 180-second rule, also with a conservative warning. Successful recovery of the final snapshot does not report rollback.

If a foreign lease is still active, the observed checkpoint is temporary/read-only. If storage also fails, a locally confirmed or callback-observed checkpoint is temporary/read-only; without any confirmed checkpoint, defaults remain explicitly unconfirmed and unsavable. Read failure never grants ownership or enables writing defaults. Players must rejoin to try obtaining a writable session later. Temporary gameplay is not persisted.

If both recovery and acquisition exhaust, a small in-memory admission record retains the exact terminal token, the acquisition-attempt token and the last confirmed checkpoint. A later same-server rejoin retries acquisition only: it never repeats the abandoned final-snapshot recovery. The callback may replace only the exact terminal token or acknowledge its own exact acquisition token unchanged. A newer active token, including one with the same JobId, is rejected without changing data or lease expiry. Successful acquisition or confirmed foreign rejection clears this record; errors retain it. Temporary profile handles never gain save authority. Lost acquisition responses can therefore be reconciled before expiry without refreshing an already acquired lease.

A persistent HUD warning complements the load message. Desktop shows `Recent progress may be missing`; compact HUDs show `RECOVERED` or `UNSAVED` with `progress may be missing`. A subsequent autosave failure shows `Save delayed · retrying` (compact `DELAYED`) alongside the missing-progress warning. A successful retry clears only the delayed status; ownership loss keeps temporary/unsaved status highest priority. The recovery flag survives ordinary State updates for that session. Test sessions retain their temporary-progress status.

## Why stale recovery cannot replace newer protocol saves

- Each acquisition uses JobId, a module GUID and a monotonic acquisition counter. Every write checks the exact token, not just JobId. The terminal local takeover checks the exact previous token as well.
- Returned profile tables and sanctioned Sanitize baseline copies are bound in memory to their acquisition. A stale handle cannot borrow a newer local session's write authority, including calls made after rejoin.
- A save captures a detached snapshot and increments a per-acquisition revision. Stored `_save` metadata identifies the committed token/revision. An identical retry returns the current record unchanged; it does not restamp or release the newer owner's lease. A later same-acquisition revision blocks an older operation.
- Every UpdateAsync callback rechecks the actual record it receives. No cached ownership decision is reused when Roblox re-invokes a callback. A lost response therefore either reconciles the already committed operation, or falls back to current data without overwriting a newer owner/save.
- Acquisition preserves the last operation marker and its recovery-warning flag across ambiguous responses. Sanitize excludes persisted protocol metadata from gameplay data.

These checks follow Roblox's documented [UpdateAsync callback retry/cancellation behavior](https://create.roblox.com/docs/reference/engine/classes/GlobalDataStore). The safety guarantees apply to saves using this protocol; arbitrary manual store edits or older external writers must be excluded during release migration.

## Reproduction and verification

On unchanged `10489aa`, new regressions failed with `Terminal admission token forgotten after outage` and `Recovery warning masks autosave failure`. The store simulation first confirmed 100 coins, failed a 150-coin terminal release, exhausted recovery and acquisition before commit, then restored storage before the original lease expired. Rejoin remained read-only. The notice formatter also omitted a later save delay whenever recoveryWarning was set.

The correction passes **83 actual Profiles/ProfileLease assertions** with cloned in-memory records and **11 negative controls**, including dropped admission identity, same-job-only ownership, foreign takeover and lease extension during ambiguous acknowledgement. Tests cover pre-commit failures, repeated outages, timeout, foreign/same-job ownership changes, callback replay/reinvocation, lost successful responses, temporary/stale handles and simultaneous cached-admission loads. The previous seven controls remain.

Notice tests pass **16 formatter/autosave-transition assertions**, **two negative controls**, and **four source-wiring contracts**. They execute the actual autosave helper with simulated Save/state delivery, not a real RemoteEvent. Progress labels pass **13 assertions**. Full `python tests/verify_local.py --build` passes 24 pure/synthetic suites, 55 mocked-service suites, 56 production compiles and all candidate/disposable builds.

The UI-only fixture now contains 36 layout cases, including three additional delayed-recovery states. It was rebuilt/compiled, **not run natively for this correction**. The 33 native UI results in the preceding bounded-recovery evidence belong to `10489aa`, not the modified fixture. New wording uses the existing dimensions; physical fit and accessibility still need native/device confirmation.

A separate implementing-agent self-review checked lock serialization, callback re-evaluation, exact-token admission replacement, ambiguous-response acknowledgement without restamping, retirement of the final snapshot, temporary-handle rejection, cache cleanup and status priority. No blocking issue found; no external reviewer claimed. Exact reproduction/results and hashes: `tests/evidence/recovery-admission-2026-11-10.json`. Historical initial-policy evidence: `tests/evidence/bounded-recovery-2026-11-10.json`.

## Limits and release gates

The 12-second deadline stops new recovery requests; an already yielding engine call cannot be cancelled and can take longer. Normal acquisition still has its separate three attempts. Per-user lock waits also depend on earlier requests completing. No hard wall-clock join/shutdown guarantee is made.

Pending snapshots remain in memory until bounded recovery on rejoin or server exit. Afterwards only admission identity and a confirmed checkpoint survive unresolved acquisition errors, at most one record per affected user until acquisition, foreign rejection or server exit. These are not a durable journal and cannot recover unsaved progress after process loss. A different server has only the stored checkpoint. An acquisition that commits but loses every response remains read-only until an atomic acknowledgement succeeds; a different server/process may still have to wait for lease expiry. Notices say progress *may* be missing because ambiguity does not prove rollback.

Persistence evidence uses cloned in-memory records, controlled time, callbacks and coroutines, not real DataStore traffic, engine throttling, internet failures, concurrent Roblox servers or shutdown deadlines. The preceding native testing covered UI layout only; no new native run is claimed for this correction. Physical devices, real microphone, multiplayer, live save/migration and mixed-version drain remain unverified. No live DataStore was accessed, no game published and no audio configured. Before publication, validate in an explicitly authorized isolated store and drain incompatible older servers.
