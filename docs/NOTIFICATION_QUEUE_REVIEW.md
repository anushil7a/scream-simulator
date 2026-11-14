# Readable notification bursts

Current save-warning overflow policy is documented in [Bounded save-warning priority](SAVE_NOTIFICATION_REVIEW.md). It supersedes the historical overflow limitation below for explicitly classified autosave warnings only; ordinary urgent notices remain bounded and may be dropped.

## Voice guidance lifecycle correction

Base: clean local/fetched `92f7988464e41b43f5243ee8e26862bbd5d7d961`. Actual client constructor/toggle/CharacterRemoving callback plus actual controller/queue reproduced ON guidance remaining queued after the removal callback disarmed attacks (`respawn: stale queued voice notice`). This was executed before changing production. The guidance could outlive the state it described while waiting behind a critical notice.

The controller now accepts an optional armed-state-change callback. The client uses it only to remove active/pending `voice` guidance when armed state actually changes. It runs after the existing cancellation, so explicit stop behavior stays intact. The manual toggle then queues the fresh state notice as before. Queue removal shares the existing coalescing logic and promotes waiting work, retaining the previous priority fix. No-op availability checks retain valid notices. Other warnings/rewards, ordinary proximity voice, server validation, cooldown and persistence are unchanged. This withdraws obsolete guidance; it does not add automatic rearming or a new notification on every disarm.

Checks: 1,217 new actual-wiring/controller/queue lifecycle assertions, with two negative controls (disconnect client invalidation; remove controller dispatch). Existing 1,661 queue assertions/five controls, 29 toggle checks/two controls and 14 action-feedback checks/four controls pass. Full verification passes 25 pure/synthetic + 58 mocked suites, 57 production compiles, candidate correspondence checks and all builds. Separate implementing-agent self-review found no blocker in optional callback compatibility, no-op/initial-arm behavior, stop-before-invalidation, queued/active removal, unrelated notice preservation and pending priority. No independent reviewer claimed.

Native Studio `0.747.0.7471481` executed the rebuilt UI-only fixture, log `0.747.0.7471481_20261110T234407Z_Studio_C1E37_last.log`. Previous keyed-priority interaction passed: save warning visible and TextFits true for 241 checked frames over at least four seconds, then ON guidance followed. All three new lifecycle cases passed: simulated mic unavailability, direct suspension-handler invocation, and locally setting/restoring `Player.Character` to induce exactly one native CharacterRemoving signal. Each retained the save warning, removed queued ON, and remained blank after the warning expired. This is not a complete server-driven death/respawn, OS-focus test, real microphone or network test.

The existing burst/layout audit also passed in 23.50 seconds across three viewports: critical warning 250 frames/4.23 seconds; resumed milestone/reward/completion/Flowers watered 241–242 frames/about 4.02–4.03 seconds. Zero TextFits clipping, stable-frame control overlap or review-script errors; shop hit test places Notification above the modal. Synthetic state, readiness, power and viewport selection remain explicit. Human comprehension, physical touch/accessibility, real voice/proximity, multiplayer and persistence remain release gates.

Overflow audit also reproduced the documented policy: with one active urgent and nine distinct pending urgent messages, the oldest pending urgent is dropped to retain the eight-entry bound. The active warning remains protected; a newly queued normal message does not evict pending urgent messages. No capacity policy changed in this focused correction. Recommendation: preserve persistent save status and evaluate semantic replacement/priority among critical categories before changing overload behavior; unbounded storage or blanket protection of every urgent notice merely moves the failure to memory growth/starvation. This remains a known delivery limitation, not a claim that all urgent messages are guaranteed readable.

One disposable Studio window was stopped, saved locally as `build/NotificationLifecycle.rbxl`, and closed. Final window inventory contained only pre-existing Codex; no other activity or unsaved work was discarded. No browser tabs, publication, purchases, audio configuration or live DataStores. [Exact evidence](../tests/evidence/voice-notice-lifecycle-2026-11-10.json) records the executed pre-save artifact hash separately from saved/generated artifacts.

## Keyed replacement priority correction

Follow-up base: `3022fe7c27f2f896974be380322c52fd55891cfc`, clean local/fetched shared head. Executing the reviewer's exact three-message sequence against the actual Queue module in Luau reproduced `Keyed normal replacement bypassed waiting critical warning`: an active urgent voice status was removed by its normal replacement, which occupied the empty active slot ahead of the pending save warning. This was an executed deterministic regression, not source tracing alone.

When coalescing removes the active keyed entry, promote the oldest already queued entry before processing its replacement. Existing urgency insertion/preemption then applies normally. The save warning now displays next, retains its reading interval, and is followed by the latest voice status. Urgent replacements respect waiting critical order; subsequent toggles coalesce pending status without interrupting/resetting the active warning. Routine-only pending work retains FIFO. The production change is one assignment plus an explanatory comment; no message text, UI layout, dwell policy, gameplay, server or save behavior changed.

Validation: all 1,661 queue assertions pass (247 added), including the exact sequence, warning dwell, repeated toggles, urgent replacement and routine FIFO. Five queue negative controls pass; the new control restores the old assignment and fails at the reported priority regression. All 25 pure/synthetic + 57 mocked suites, 57 production compiles, candidate correspondence checks and all builds pass. Action receiver/helper tests retain 14 checks/four controls. Separate implementing-agent self-review covered the empty slot, pending urgency ordering, same-key removal, existing preemption/resumption and overflow behavior; no blocker found, no independent reviewer claimed.

This follow-up has **no native Studio execution**. All new results are actual-module Luau execution with synthetic frame timing; the earlier native evidence below describes the preceding checkpoint, not native validation of this interaction. Real-player comprehension, physical touch/accessibility, voice/network/multiplayer and persistence gates remain. No programs, tabs or test windows were opened for this correction, so there was nothing new to close; pre-existing activity was untouched. No publication, purchases, audio configuration or live DataStores. [Exact follow-up evidence](../tests/evidence/notification-priority-2026-11-10.json).

## Original queue checkpoint

Base: `5ec4827397df054a4dac46ebbdc7218349b419f1`, fetched before editing and again before preparing this checkpoint. This follows the narrow suppression correction in [the previous audit](ACTION_FEEDBACK_REVIEW.md).

## Reproduction and correction

Executing the baseline client's actual `notify` function in a Luau CLI fixture reproduced both same-frame overwrites: milestone then reward left only reward, and quest completion then Flowers watered left only Flowers watered. This reproduction uses actual source with a fake label/clock; it was not a native baseline run.

The client now owns a bounded queue, with eight pending notices plus the active notice. Normal messages retain arrival order and get 4–12 seconds of displayed time based on text length. Exact active/pending duplicates coalesce. Local voice/capture state keys replace obsolete status, so rapid ON/OFF changes do not replay stale guidance. Timers pause while unfocused or the Roblox menu is open, and a long frame can consume at most 0.1 seconds.

Explicit save, purchase/boost and upgrade failures carry presentation-only urgency metadata. Local setup/capture errors are also urgent. An urgent notice interrupts a normal notice immediately on the next render; the interrupted notice resumes with a full reading interval. Distinct urgent notices are ordered ahead of routine messages; an already displayed urgent notice keeps its interval. A new milestone cannot hide an urgent message in the same State packet. No grant, price, cooldown, microphone routing, persistence or ownership behavior changed.

Under overload the oldest pending normal notice is dropped first; if all pending notices are urgent, the oldest pending urgent is dropped. The active notice is never evicted by overflow. This is deliberately bounded feedback, not a durable notification history or a promise to display every event during unlimited spam. Existing persistent save status remains available.

## Native display evidence

The disposable UI-only Studio fixture uses the actual client receiver, RenderStepped handler and TextLabel, with synthetic State delivery, readiness, power and viewport/touch selection. It contains no server scripts or persistence. No purchases were clicked.

Native inspection reproduced a second issue: the Shop panel at ZIndex 10 covered the toast at ZIndex 1. The corrected toast has ZIndex 30 and a dark background; the engine's GUI hit test identifies Notification as the top object at its center. A screenshot then exposed overlap with landscape action buttons. Moving the toast above those targets corrected it; stable-frame rectangle checks reported no overlap in the final run.

Final production native run: Studio `0.747.0.7471481`, log `0.747.0.7471481_20261110T232034Z_Studio_DD595_last.log`, 23.498833 seconds, six nonempty segments. Rotated through 390x844, 844x390 and 1280x720:

| Segment | Frames | Measured display time |
| --- | ---: | ---: |
| Initial milestone, interrupted | 30 | 0.501 s |
| Critical save warning | 254 | 4.233 s |
| Resumed milestone | 241 | 4.017 s |
| Quest reward | 241 | 4.017 s |
| Quest complete | 242 | 4.032 s |
| Flowers watered | 242 | 4.034 s |

All segments had zero TextFits clipping. The shop warning was above the modal and not clipped. The log contains no review-script errors or control-overlap failures. These are native rendered-label duration/layout measurements, not human comprehension, physical-phone or real service validation.

Initial diagnostic runs exposed fixture bookkeeping errors (initial blank segment and a residual shop-warning frame) and the actual menu/controls display defects above. Those diagnostic runs were not accepted as passing evidence. After the successful final production run, the fixture's overlap assertion was moved from the event callback to an accumulated count checked by the outer completion path. This hardened fixture was rebuilt/compiled but not rerun natively. The executed version's full log was separately checked for callback errors, so the final production result does not rely solely on its PASS marker. Production source did not change after that run.

## Automated checks and review

- `python tests/verify_local.py --build`: all 25 pure/synthetic and 57 mocked-service suites, 57 production compiles, exact-source candidate checks and all disposable builds pass.
- Queue suite: 1,414 frame/dwell/order/priority/coalescing assertions. Four mutation controls detect normal-message overwrite, disabled urgent preemption, too-short dwell and missing pending deduplication.
- Actual action feedback receiver/helpers: 14 checks and four controls, including same-packet critical warning suppression. Existing duplicate claims still award once. Commerce: 13 mocked checks; autosave status: 11 checks, including urgent metadata.
- Separate implementing-agent self-review checked queue bounds, priority and interrupted resumption, state coalescing, same-packet ordering, server callback signatures, source/build inclusion, render timing, fixture false-positive risks and cleanup. No blocking defect found; no independent reviewer claimed.

Exact outputs, native rows and artifact/source hashes: [evidence](../tests/evidence/notification-queue-2026-11-10.json). The executed artifact hash was recorded before Studio saved local edit metadata; regenerated artifacts are separately hashed and are not claimed to be byte-identical native executions.

## Remaining gates and cleanup

Real-player reading/comprehension, physical touch and assistive navigation remain untested. Real microphone/proximity voice, multiplayer/network, payment delivery and persistence validation remain separate gates. This work makes no retention claim. No publication, audio configuration, purchases or live DataStore access occurred.

All four disposable Studio sessions were stopped, saved locally and closed. The original fixture's saved file is preserved separately before regeneration. Two app-picker dialogs created during Studio startup disappeared during cleanup. Final native inventory contained only the pre-existing Codex window; no browser tabs were opened, no processes killed and no unsaved work discarded.
