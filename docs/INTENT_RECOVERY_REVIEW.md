# Quest restart disclosure and bounded sprint recovery

Base: `44f1f605f9409781676770a71e7a529c23f97a73`. Two independent client-only corrections. No map, server behavior, reward/reset policy, profile schema, audio configuration or live service changes.

## Explicit quest restart

Reproduction: Controlled Beams is saved at 2/3. The current session model does not restore an active task on rejoin, so its card shows 2/3 and ACCEPT. The actual acceptance path clears that counter to zero without telling the player beforehand. Partial garden counters have the same existing restart semantics; delivery has goal one, so there is no valid integer partial-delivery counter.

Preserve existing semantics rather than silently making quests resumable. For unlocked, unclaimed, inactive tasks with progress strictly between zero and the goal, show RESTART and append "Restarting resets this unfinished progress." before measuring card height. The callback remains AcceptQuest. MEET NPC, CLAIMED, CLAIM and TRACKING keep their original precedence; zero progress still says ACCEPT. Explicit abandonment, switching, completion, claims and saves are unchanged.

- `python tests/quest_catalog_ui.py --negative-controls`: **479 assertions and nine controls**, independently rerun. Actual renderer/catalog with mocked text metrics, narrow/wide layouts, partial practice/garden, zero-progress delivery, locked/active/completed/claimed states and unchanged command IDs. Two new controls independently remove RESTART and its reset disclosure. These are not native TextFits or human readability tests.
- `python tests/combat_quests.py --negative-controls`: **189 assertions, six controls and one source contract**, independently rerun. The combined case uses actual Profiles with an isolated fake store, builds a mocked inactive rejoined session, and calls actual acceptance/claim/QuestLifecycle helpers. It checks partial counters survive storage until explicit restart, active duplicate acceptance does not reset, completed rewards remain claimable, claimed tasks cannot replay, and claiming an earlier reward preserves the current task. This is not execution of the complete joined pipeline or live persistence.

## Bounded held-sprint recovery

Historical actual client helper plus actual dispatcher reproduces a quota-rejected Sprint(true): the client retains true while the server remains false. After the one-second action window expires, 120 held-input updates over two seconds send no retry. Release/repress recovers. Saturation was injected using unknown requests, so normal-player frequency is not established.

While current local intent remains true and eligible, resend the existing Sprint(true) at most every 0.5 seconds. No catch-up bursts. Changed true/false transitions stay immediate; duplicate OFF stays silent. Existing per-frame/callback eligibility cancellation clears the same local intent, so this adds no separate desired state that can re-arm after interruption. The server quota, idempotent boolean assignment, sprint speed, charge billing, refill and lockout are unchanged. Steady holding adds at most two retries per second; interval endpoints can contain three sends. It does not guarantee acceptance during continuous saturation or network failure.

- `python tests/sprint_recovery.py --baseline` reproduces the historical44f1f60 failure against the actual current dispatcher.
- `python tests/sprint_recovery.py --negative-controls`: **53 assertions and five controls**, independently rerun. Covers quota-expiry recovery, retry spacing, immediate OFF/fresh ON, 13 local blockers, no automatic resume, and unchanged server charge accounting under repeated true packets. Controls remove retry, remove its rate bound, throttle OFF, throttle fresh ON, and retain blocked intent. Synthetic clocks/UI/players and synchronous calls are not native transport or physical input evidence.
- Existing sprint input48, server sprint184, toggle29/two controls, acceptance8 and claim8 checks were also rerun; all remain in the full checkpoint.

## Integration and remaining gates

`python tests/verify_local.py --build` passes **25 pure/synthetic suites,88 mocked-service suites,60 production compiles and all builds**. New sprint assertions are registered. Opt-in mutations above were run explicitly; default aggregation is not claimed to run them. [Exact source/artifact/command evidence](../tests/evidence/intent-recovery-2026-11-11.json).

No app was opened. No new native execution, live save, purchase, publication or map change occurred. Previous native161-check evidence belongs to44f1f60 and does not validate these new quest strings or network recovery. Physical-device input, actual latency/focus/respawn sequencing, user comprehension and the established release gates remain. The pre-existing minimized picker limitation is unchanged. Owner backlog now accurately separates completed native allocation checks from still-unverified real microphone/audio/service and physical-device behavior.

Follow-up: Astra identified the separate NPC dialogue route still said Accept on partial inactive tasks. The [next batch](QUEST_WRITER_ROLLOUT_REVIEW.md) adds matching Restart/reset disclosure there, without changing quest semantics.
