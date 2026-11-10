# Bounded save-warning priority

Base: clean local/fetched `bd6b80b7ec0197814ba614352ef3e2630d977cb8`. Remote was checked before edits and again before push. This follows the [notification queue review](NOTIFICATION_QUEUE_REVIEW.md).

## Call-site audit and reproduction

| Existing call sites | Severity and treatment |
| --- | --- |
| Autosave delayed / saving unavailable | Progress at risk; now classified with the single `save` key and highest priority. Existing save results, eligibility and retry behavior unchanged. |
| Insufficient upgrade coins, vendor access rejection | Recoverable action errors; remain ordinary urgent notices. Shortage text varies with the authoritative balance, so exact-text deduplication cannot bound distinct messages alone. |
| Purchase unavailable, coming soon, loading, capacity, prompt error, failed boost activation | Remain ordinary urgent. Product IDs are still unconfigured. No purchases or product setup performed. |
| Local voice setup/capture failures | Remain ordinary urgent with existing state coalescing/lifecycle invalidation. |
| Milestones, rewards, completion and ordinary guidance | Remain normal FIFO below urgent notices. |
| Initial profile-load/recovery message and persistent save HUD | Existing behavior retained. Initial load messages are not newly promoted; the persistent temporary/delayed/recovery status remains the ongoing source of truth. |

The new integration test executes the real autosave helper, real State payload builder, real insufficient-coins helper, actual client receiver and actual queue. UI objects, save responses, frame time and changing coin balances are simulated. With an urgent setup notice active, a save failure then eight distinct shortage responses interleaved with routine reward messages evicted the save warning. Draining the queue never returned its text on any simulated display frame: `Save warning evicted before any displayed frame`.

This is a deterministic player-feedback loss in the actual modules, not a native/network reproduction or proof of how often real players produce this burst. The simulated balance changes exercise real parameterized error messages, not actual earned rewards or purchases. Two initial fixture runs omitted required session timestamps; those stub errors were corrected before the accepted baseline failure and before production edits.

## Focused policy

- Exactly one current save-category notice: delayed and unavailable warnings coalesce using the same key. No growing error history or separate unbounded queue.
- Save priority 2, ordinary urgent 1, normal 0. A save warning preempts either lower class. Its interrupted notice resumes with the existing full dwell policy; equal-priority messages otherwise retain FIFO.
- The same eight pending plus one active maximum remains. Overflow removes the oldest entry at the lowest pending priority. Lower-priority traffic cannot evict or preempt the current classified save warning.
- Server State accepts only the explicit `save` category; only the two autosave warning sites pass it. The receiver forwards that recognized category, rather than guessing severity from message text or promoting every message while saves are unavailable.
- A newer save warning replaces the old state. Repeated identical active/pending messages do not extend dwell. A subsequent authoritative snapshot with saving available and no delay removes obsolete save guidance. No success toast or claim that progress was saved is added.

This is a bounded presentation guarantee for the latest classified warning after delivery to this client. It is **not** guaranteed human reading, reliable network delivery, a sticky warning, or protection of every urgent message. A healthy snapshot or newer save state may intentionally retire a notice before its full interval. Ordinary urgent/normal traffic may still overflow; a continuing higher-priority stream may delay lower messages. Existing persistent save status is unchanged. Initial load messages and server/client version mismatch without the new category are outside this new priority guarantee.

## Checks and limits

- `python tests/save_notification_priority.py --negative-controls`: 210 actual-path assertions; seven controls detect downgraded priority, removed autosave category, stripped State category, ignored client category, missing healthy-state clearing, removed queue bound and disabled save coalescing.
- Burst/drain reproduction; 100 mixed urgent/normal/voice rounds; bound and save precedence; delayed-to-unavailable replacement; no stale save guidance after recovery; interrupted reward resumption; duplicate/no-op snapshots do not reset dwell; finite expiry.
- Existing queue: 1,661 assertions/five controls. Voice lifecycle: 1,217 assertions/two controls. Action feedback: 14 checks/four controls. These retain previous ordering, stop/invalidation and duplicate protections.
- Full `python tests/verify_local.py --build`: 25 pure/synthetic + 59 mocked suites, 57 production compiles, exact-source candidate checks and all builds pass.
- Separate implementing-agent self-review checked server callback compatibility, explicit classification, priority ordering after preemption/coalescing, active/pending capacity, recovery clearing, scope and test mutations. No blocker found; no independent reviewer claimed.

No native Studio session was run for this correction. Fixtures were rebuilt/compiled only; previous native evidence does not validate the new save classification. Native display timing, real-player comprehension, physical touch/accessibility, real voice/network/multiplayer and persistence remain separate gates. No publication, audio configuration, purchases or live DataStore access occurred. No programs, tabs or test windows were opened, so nothing new needed closing; pre-existing work was untouched.

[Exact reproduction, outputs and hashes](../tests/evidence/save-notification-priority-2026-11-10.json).
