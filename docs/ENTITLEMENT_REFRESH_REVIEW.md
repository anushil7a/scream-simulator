# Entitlement refresh response fencing

Base: `670948dd6da0cba85672e71f8d0f294005864202`. This is a narrow server-cache correction, not product activation or a purchase-delivery change. Production pass/product IDs remain zero.

## Reproduction

Actual `Entitlements.Refresh` with controlled yielding ownership calls reproduced an older false result overwriting a newer confirmed true. The inverse also let an older true overwrite a newer false. Refresh can be started by join and the registered successful purchase-finished callback. Existing tests covered disabled IDs and Studio movement but not overlapping requests. This is a latent defect before pass configuration, not evidence of a live paid-user incident.

## Correction

- Every refresh receives a fresh opaque identity keyed by the Player object. After each yielding ownership API, only the latest identity for a still-parented Player may write its cache or continue to the second call.
- PlayerRemoving invalidates the identity and clears paid/Studio caches. A weak-key departure marker rejects already-queued refreshes even while Parent still exists during removal. A new Player object with the same UserId remains independent.
- Successful current false results can still revoke ownership. API failures retain the last confirmed cache; true is not permanently latched. Disabled IDs do not query the service or grant paid benefits, and the separate Studio override/arena boundary remain.
- The original purchase-finished callback still treats the event only as a reason to query authoritative ownership, not as proof of purchase entitlement.

Superseded calls may finish remotely but cannot apply stale results; this does not cancel Roblox requests, introduce retry scheduling or prove native collection. If the latest check fails before ownership was ever confirmed, access remains unavailable until a later refresh/rejoin. Real ownership-service failures and purchase UX remain release gates before product configuration. No new persistent data, credentials, commerce ledger changes or live calls.

## Verification

```text
python tests/entitlement_refresh.py --baseline
python tests/entitlement_refresh.py --negative-controls
python tests/entitlements.py
python tests/commerce.py --negative-controls
python tests/verify_local.py --build
```

Focused tests run the actual module with coroutine-controlled ownership responses. They cover both stale response directions at both yields, stopping the second query after supersession/removal, removal before Parent clears, queued callbacks, a new Player with the same ID, last-good errors, legitimate revocation, disabled IDs, Studio and arena restrictions, and the registered purchase callback. Negative controls remove the individual fences/cleanup/entry checks and permit permanent true latching. All use simulated services, not native networking, Roblox ownership, actual purchases or replication.

Original2daa39e results:40 actual coroutine assertions/seven controls and the expected historical failure; nine existing entitlement checks;46 commerce assertions/five controls; full25 pure/synthetic +92 mocked suites,60 production compiles and all builds pass. [Exact commands and hashes](../tests/evidence/entitlement-refresh-2026-11-11.json). Independent review reruns the production correction and focused regressions. No apps opened, map work, live DataStores, product/audio configuration, Roblox publication or release merge. The mixed-version quest writer rollout gate remains unresolved and unchanged.

## Astra follow-up: confirmed cleanup and purchase authority

Astra independently cleared the production correction but found two missing test paths: removal after movement ownership was already confirmed true, and a successful purchase-finished event before/without a true authoritative ownership response. The earlier suite could miss deleting the owned-cache cleanup or directly granting from the purchase callback. These are corrected test blind spots, not newly found production behavior defects.

The final suite has55 assertions and nine negative controls, independently rerun. It confirms paid caches clear on removal while Parent remains present, and both pass-ID purchase events grant no fresh ownership while pending or after false/error responses. Exact missing-cleanup and direct-grant mutations fail at the intended assertions. Existing last-good error behavior remains separately tested. The expected historical failure and nine legacy checks pass again.

Only tests/documentation changed after701a52e. Runtime source/builders remain exactly2daa39e; its25 pure/synthetic +92 mocked suites,60 compiles/all-build checkpoint is historical, not an additional full/native run. [Follow-up evidence](../tests/evidence/entitlement-authority-tests-2026-11-11.json). Product IDs remain zero; no live API, purchase, collection or replication claim.
