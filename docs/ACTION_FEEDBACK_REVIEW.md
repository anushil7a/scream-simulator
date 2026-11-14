# Action feedback audit

Historical suppression checkpoint. Its single-toast readability limitation is addressed in [the subsequent queue review](NOTIFICATION_QUEUE_REVIEW.md); the results below describe the earlier checkpoint only.

Base: `ad7b5fd9eef911a1b9b1e881faeb3f31e21abfb6`. The reference about visual feedback is an audit prompt, not evidence of retention impact.

## Reproduced defect and correction

The actual client State receiver suppressed every later `data.message` for six seconds after a new milestone. There was no queue or retry. With mocked UI/time and real server micro-speaker/quest-claim helpers, a milestone at t=100 hid an insufficient-coins rejection at t=100.1 and the quest reward confirmation at t=100.2. A server completion message at t=100.3 was also lost. The denied upgrade left coins/ownership unchanged; the successful quest still awarded 40 coins/100 XP once. This is lost feedback, not a server grant failure.

Removed the six-second suppression timer. A new milestone still displays once; subsequent authoritative messages immediately replace the toast. Repeated milestone-only state snapshots do not replay it. The same-packet level milestone retains its existing priority over the accompanying level-up message. No reward, purchase, entitlement, save, audio or progression behavior changed.

## Audit scope

- Earned-coin upgrade: server validates price and ownership before debit without yielding. The vendor path avoids a second debit; Style intentionally toggles already-owned equipment. No real purchase was performed.
- Tasks: claim marks the task claimed before invoking reward callbacks. Existing reentrant/duplicate claim coverage passes; the new test feeds the actual server helper messages into the actual client receiver and proves single reward/notice on repeated claim.
- Existing shop: inventory and timers come from server state. Receipt IDs and activation operation IDs guard ledger retries. Existing commerce tests cover lost responses/repeated receipts using a fake atomic store; IDs remain unconfigured. No new monetization design or claim of real purchase validation.
- Client: toasts and quest badges already exist. The concrete defect was a timer hiding authoritative messages, so no new feedback UI or speculative retention system was added.

## Checks and limits

`python tests/action_feedback.py --negative-controls`: 11 actual receiver/helper checks pass, with three targeted controls detecting restored suppression, repeated milestone notifications and removed claim deduplication. The baseline `--reproduce` mode passed against the original receiver before the change; normal assertions failed at `Milestone hid upgrade rejection`.

`python tests/verify_local.py --build`: 24 pure/synthetic suites, 57 mocked-service suites, 56 production compiles and all candidate/disposable builds pass. Separate implementing-agent self-review checked the three-line production diff, extraction boundaries, server guards, same-packet milestone behavior and mutation failures. No external reviewer claimed.

No new native Studio execution: this patch changes notification timing, not text or layout. UI/time/services are simulated; tests do not establish physical phone/accessibility behavior, real voice/proximity, internet/multiplayer or live saves/payment delivery. The existing single toast can still be replaced quickly by a burst of later messages; this fix does not promise queueing or minimum reading time.

At cleanup, native window enumeration listed only Codex. No disposable Studio/browser windows remained to close, and no processes were killed or unsaved documents discarded. No new app windows or tabs were opened this task. No publication, audio configuration, purchases or live DataStore access.

Exact outputs/hashes are in `tests/evidence/action-feedback-2026-11-10.json`.
