# Readable notification bursts

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
