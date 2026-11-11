# Bounded shop price requests

## Reproduction and change

The previous actual `purchaseButton` starts a new `GetProductInfoAsync` on every render until a successful response is cached. A coroutine mock reproduces 120 rerenders creating 120 pending requests for one configured product. Current catalog IDs remain zero, so this is a latent readiness issue, not an observed live purchase incident.

The correction keeps one current record per fixed catalog item/configured ID. No request queue is retained. At most four actual calls are in flight across items. Rerendering reuses pending state. The yielding worker receives only a record and scalar ID/type; current UI callbacks live separately and `Shop.Clear` removes them. Existing `Shop.Tick` updates current buttons and retries without requiring a modal reopen. An obsolete record cannot cache or apply a result after an ID change, including an ID roundtrip.

Successful validated metadata lasts 60 seconds. Failed/malformed calls retry no sooner than 10 seconds after completion. Results arriving at or beyond eight seconds are rejected. A hung call still occupies its slot until it returns; timing out does not cancel Roblox work or permit unlimited replacement calls. Four permanently hung calls therefore leave price lookup unavailable until a call returns or the client session ends. No catch-up queue or backend-cancellation guarantee is added.

Only a table with boolean `IsForSale` and, when for sale, finite nonnegative integer `PriceInRobux` can enable the current button. Zero is accepted. Expired/unknown/failed prices cannot enable it. An unsavable snapshot remains unavailable. The standard server purchase prompt/confirmation remains authoritative; no purchase, ownership grant, ID configuration, microphone, reward, map or persistence behavior changed.

## Focused verification

- `python tests/shop_price_requests.py --baseline`: actual historical `15df683` helper reproduces 120 pending calls.
- `python tests/shop_price_requests.py --negative-controls`: 51 actual price-path assertions and seven controls. Includes narrow/wide full-Render 120-rerender smoke, synchronous success, rerenders, current vs obsolete GUI, close/reopen, TTL expiry, retry while open, four hung slots, late capacity release, ID roundtrip/out-of-order results, malformed responses, zero price, unavailable saving and disabled IDs.
- Explicit controls remove immediate synchronous cache application, single-flight, global capacity, retry delay, response deadline, view cleanup and obsolete-record fence. One source contract checks that the yielding worker has no GUI/apply/snapshot reference; this is not a native garbage-collection proof.
- `python tests/boost_purchase_ui.py --negative-controls`: 26 assertions/five controls unchanged; only empty `priceViews` setup added to its timer extraction.
- `python tests/style_controls.py --negative-controls`: 261 mixer/server,35 profile and40 renderer assertions/11 controls unchanged; only empty `priceViews` setup added to its Clear extraction.
- `luau-compile src/StarterPlayer/StarterPlayerScripts/ShopUI.luau`: passes.

Tests execute actual production prefix/helper/Render/Tick/Clear with coroutine service and GUI mocks. No live Roblox calls, purchases, native timing/replication, physical input, layout validation or memory profiling were performed. The four catalog entries bound the intended production view/record set; this is not a general arbitrary-catalog scheduler. Serving-fleet release gate and existing native-device gates remain unresolved. Map work remains paused.

Only ShopUI, the new regression/review, and the two explicitly authorized fixture setup lines changed in this assignment. Parent coordinates aggregate verification, integration evidence and any commit. No applications opened.

The immediate synchronous-result check is helper-level deterministic robustness: full Render already ends in Tick, so this is not claimed as an observed visible transient defect.

## Integration checkpoint

Independently reviewed and rerun focused checks above; full `python tests/verify_local.py --build` passes 25 pure/synthetic suites, 94 mocked-service suites, 60 production compiles and all disposable builds. The aggregate log includes the final 51 shop assertions; seven explicit controls were also separately rerun. This is offline execution, not native Roblox. [Exact commands and working-tree/artifact hashes](../tests/evidence/client-availability-2026-11-11.json). No apps or live services were used.

## Astra integration and identity follow-up

The original 0619103 tests explicitly invoked `Shop.Clear`; they did not prove actual client modal close routes called it. Astra found X, B/toggle and same-tab close only hid the modal, retaining views and retry activity. Simply clearing would also leave unchanged-key reopen short-circuited. The coordinated client correction and actual callback/render-cache tests are documented in [modal lifecycle review](SHOP_MODAL_LIFECYCLE_REVIEW.md). Prior claims that actual closes cleared views were too broad.

Astra also found a disabled-ID identity gap: 102 -> 0 -> 102 could reuse an old pending result because the disabled card returned before invalidation. The correction invalidates an observed disabled/malformed configuration or changed configured key before the owned/disabled early return. Neither invalidation nor timeout releases an actual pending-call slot. Cached and pending results, invalid values, owned-card transitions and four occupied slots are covered. Final price suite passes 88 assertions, nine explicit negative controls and one source contract; `--disabled-baseline` reproduces the 0619103 gap. Product IDs remain zero; this is latent configuration robustness, not an observed live price failure.

## Deferred purchase callback follow-up

Astra invoked an actual previously priced callback after Shop.Clear and observed ShopPurchase being sent with zero views. The callback now captures its generation before construction and checks current generation, attached button and available price before sending. The button local is declared before assigning the UI constructor, so the closure captures that local rather than an unintended outer/global name. Current reopened callbacks still work; old callbacks after Clear/rerender/detachment do not send.

Final price suite passes 96 assertions, 11 controls and one source contract; `--callback-baseline` reproduces 74c7763's stale send. Actual-callback mocks do not prove native queued-event delivery, show a real purchase, or change server/Roblox purchase authorization. No product configuration or live prompt occurred.

Deferred-callback integration: independently reviewed focused checks and final25 pure/synthetic +96 mocked suites,60 compiles/all builds pass. The first aggregate exposed the Settings fixture trying to select a tab after closing the modal; its explicit visible precondition was restored without changing assertions. [Exact failed/final evidence and hashes](../tests/evidence/deferred-shop-callbacks-2026-11-11.json). No native session or live service was used.
