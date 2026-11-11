# Automatic boost purchase delivery and attack-description correction

November 11, 2026. Local base: `736a82f08b5f14afe02bf73c493d40fe62054888`. Preserve that checkpoint and `f0dc1e7664a6786cd9586db43e7d12a7576b882c`. No map, combat formula, cooldown, product ID, profile or entitlement changes.

## Reproduction and behavior

The actual `Commerce.ProcessReceipt` handler, executed with a fake atomic store, failed the new regression with `Receipt did not activate immediately`: it only added inventory. New configured XP/coin product receipts now record the receipt ID and extend that reward type's absolute expiry together in one `UpdateAsync` transformation. The extension is 30 minutes after the later of current server time or existing expiry. Multiplier remains 2x, not additive. A duplicate or historical receipt does not add inventory, extend time or restart an expired boost.

Activation starts on the first durable receipt processing, not the purchase-window click or a client event. Unknown/unconfigured products, missing player, unavailable/test profiles, malformed receipt IDs, capacity overflow and failed writes remain unacknowledged. Roblox can retry them later. Repeated callback evaluation and competing receipt transforms use the latest atomic record. A committed-but-lost response can be retried without adding time twice. If all responses fail, no local entitlement is inferred; a later confirmed retry/reload reads the durable deadline. The timer still runs while offline or while an ambiguous result is unresolved, so delay can consume boost time. No compensation or guaranteed delivery latency is promised.

Old inventory and already-recorded receipts remain intact. Players with saved boosts retain a separate USE SAVED action; new purchases do not consume those tokens. With no saved inventory the manual activation button is absent and purchase uses the row width. Shop text describes automatic confirmed delivery without the unwanted offline-timer wording in cards, footer or saved-boost success notice, and a confirmed expired boost says Not active. Missing/unconfirmed ledger state instead says Boost status unavailable; it must not claim inactivity when a response could have been lost. Receipt confirmation uses neutral wording that does not falsely claim a duplicate added another 30 minutes.

The collection's attack description no longer includes max attack duration or cooldown text, including legacy-mode text. Its single current-level full-power stat summary and accuracy explanations remain. Live cooldown HUD/bar, Settings help, five-second automatic cooldown and four-second maximum duration are unchanged.

## Verification

- Before the production change, the actual-handler auto-activation regression failed as expected.
- `tests/commerce.py --negative-controls`: 46 actual-handler assertions; five controls detect inventory-only delivery, missing deduplication, premature acknowledgement, retained ambiguous cache and ignored expiry.
- `tests/boost_ledger.luau`: 41 pure transaction assertions, including caps/invalid timestamps and legacy preservation.
- `tests/boost_purchase_ui.py --negative-controls`: 26 actual fragment/timer assertions; five controls detect unnecessary activation controls, ungated legacy activation incorrect inactive status, falsely treating unknown status as inactive and reintroducing unwanted offline-timer copy. Layout objects/time are synthetic.
- `tests/beam_readout.py --negative-controls`: 1,180 actual renderer/adapter/deadline assertions; five controls cover restored description timing, cooldown changes, early server admission, false range and incorrect bar denominator.
- Full `python tests/verify_local.py --build`: all 25 pure/synthetic and 62 mocked-service suites, 57 production compilations and all exact-source candidate/disposable fixture builds passed. `git diff --check` passed.
- Independent review found and reproduced the unknown-status wording defect above, which was corrected. The reviewer independently reran 24 UI assertions/four controls, 45 receipt assertions/five controls and whitespace checks; no remaining blocker. The earlier review also reran the 41 ledger and 1,180 beam assertions/five beam controls. These checks are not native Studio, real purchase, real microphone/device/network or live DataStore evidence. Product IDs remain zero. Native shop readability and actual Roblox receipt redelivery remain release gates.

## Delivery and cleanup

The main boost/description checkpoint `c1d700a8ff7ba0b4180f5329f3c65277113c06d0` was pushed non-force and its exact remote head verified, including prior `736a82f` and `f0dc1e7`. A narrow follow-up removes the unwanted offline-timer wording from cards/footer and saved-boost confirmation, with unchanged expiry semantics. Its 26 UI assertions/five controls and 46 receipt assertions/five controls pass; all full local checks/builds are rerun. Verify the follow-up commit delivery separately. Earlier authentication failures did not overwrite or discard work. No credentials changed. No Roblox publication, live stores or purchases. No app windows/tabs/test sessions were opened for this batch; pre-existing activity was left alone.

[Machine-readable evidence](../tests/evidence/boost-purchase-2026-11-11.json).
