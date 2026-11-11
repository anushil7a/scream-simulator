# Shop modal subscription lifecycle

## Reproduced integration gap

Historical Client `0619103` hides the menu on X without calling ShopUI.Clear. With actual Shop price loading and per-frame Tick, the closed menu retains views and can retry failed price calls. A Clear-only fix would lose subscriptions on an unchanged-key reopen because the Client render cache returns early.

## Correction

A common closeMenu helper hides the modal, clears ShopUI subscriptions/timers/views, clears the cached render key and advances the deferred-render revision. It preserves renderedTab and current CanvasPosition so reopening the same tab rebuilds subscriptions while restoring scroll. The helper and its state are defined before the X callback is registered, avoiding an initialization window across later yielding requires.

Runtime X, B/toggle, same-tab toggle, developer-panel opening, recalibration and NPC conversation all use the helper. Main-GUI destruction uses it too; the earlier independent ShopUI destruction cleanup remains. Tab changes still render normally. This changes no product IDs, purchase permissions, cached-price authority, microphone policy, quests, map or saves.

## Verification

- `python tests/shop_modal_lifecycle.py --baseline`: historical actual Client X path retains subscriptions, as expected.
- `python tests/shop_modal_lifecycle.py --negative-controls`: **86 assertions and ten controls**. Uses actual close callbacks, registered B-input callback with processed/menu/text-focus guards, render-key prologue, deferred-scroll callback, current full ShopUI renderer/price Tick and Style mixer. GUI/services/time are mocked; unrelated Client rendering branches are not executed. Early X is invoked before render/toggle initialization, with a source-order assertion that helper definition precedes registration.
- Covers each hide route, late error and successful completion while closed, no hidden retries, unchanged-key reopen, cached-price reopen, deferred-scroll fencing, preserved same-tab scroll, Style connection cleanup/reconnect and destruction ordering. Hung work remains bounded by the separate price loader; closing does not pretend to cancel backend calls.
- Controls omit actual B/X/toggle/same-tab/dev/recalibration/conversation wiring, cached-key invalidation, scroll revision invalidation and destruction invalidation. The destruction case includes the pre-existing independent ShopUI.Clear callback, rather than falsely attributing all cleanup to the new helper.
- `python tests/menu_cleanup.py`: five existing assertions pass after its source extraction was adapted to the hoisted helper.
- `python tests/microphone_notice.py --negative-controls`: 402 existing assertions, four controls and three contracts pass. Extraction now includes the real close helper used by recalibration; assertions are unchanged.
- Client compiles with `luau-compile`; whitespace diff check passes.

No application, real price API, purchase, native UI/event ordering, physical input or memory/GC measurement was used. The source-level and coroutine tests do not establish native reachability or actual Roblox call cancellation. Parent coordinates aggregate verification and release evidence. No commit or publication performed by this worker.

## Integration and independent review

Independent reviewers reran the final 86/ten controls and baseline, plus the separate price 88/nine controls/one contract. The initial aggregate exposed a test-fixture dependency: quest_dialogue_restart.py extracts the NPC renderer and needed a labeled closeMenu mock. Its 97 assertions/four controls are unchanged and pass; the real helper is exercised by this lifecycle suite. Final `python tests/verify_local.py --build` passes 25 pure/synthetic +95 mocked suites, 60 compiles and all builds. No native run occurred. [Exact evidence, including the failed-then-corrected aggregate](../tests/evidence/shop-modal-lifecycle-2026-11-11.json).
