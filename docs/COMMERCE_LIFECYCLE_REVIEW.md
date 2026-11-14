# Commerce player lifetime fencing

## Reproduced condition

An actual-module coroutine audit fired PlayerRemoving while UpdateAsync was suspended, with Parent temporarily still present. A successful return could recreate the departed Player's purchase cache and call the changed callback after removal cleanup. Bootstrap already drops state for an absent session; the audit did not establish economic corruption, a live incident or native memory leakage. A separate waiting receipt continued polling behind a held same-user lock after departure, without starting its own write.

## Narrow correction

Commerce uses a weak-key departed marker, consistent with the existing entitlement lifecycle fence. PlayerRemoving sets it before clearing cached purchase data and per-Player cooldowns. Parent presence alone no longer admits that Player object after removal.

- Load, Activate, Prompt and receipt admission reject departed objects. A queued public call cannot recreate their cooldown/cache state while Parent remains present.
- A transaction waiting for another transaction's same-user-ID lock exits if its Player is departed or no longer allowed. It does not release the owning transaction's lock. Admission is checked again before acquiring an available lock.
- Once UpdateAsync starts, the existing bounded three-attempt retry loop and transform semantics remain intact, even if the Player departs. Durable writes are not canceled or rolled back. The lock remains owned until the existing operation returns.
- Successful departed operations do not repopulate cache or emit changed notifications. Failed purchase-prompt returns likewise do not notify departed objects. Status/Multiplier expose no departed cached boost. Busy preserves the original per-user-ID lock truth, including a departed owner while its write remains active. A new Player object with the same user ID remains independent and still respects the shared transaction lock.
- A successful durable receipt still returns PurchaseGranted after departure. A not-yet-started rejected transaction returns false and the receipt remains NotProcessedYet. Receipt deduplication, activation operation IDs, lost-response retries and ledger schema are unchanged.

## Evidence and limits

- Independently reviewed/rerun `python tests/commerce_lifecycle.py --negative-controls`: 60 assertions and twelve controls. Test-only private cache membership observation prevents neutral public accessors from masking retention. Receipt/load/activation success, three-error departed activation with both tokens preserved, all-lost/partly-lost responses, same-ID distinct Player reconnect, prompt failure, queued admission and active-owner versus waiting-caller lock truth are covered.
- `python tests/commerce_lifecycle.py --baseline` separately reproduces both 03efe28 conditions: cache/changed resurrection and 100 departed lock polls without another write. A mocked removal event is deliberately delivered while Parent remains present; no native timing frequency is claimed.
- `python tests/commerce.py --negative-controls` retains 46 assertions/five controls for atomic receipt authority, ambiguity and deduplication. Main review retained the original Busy query after noticing that hiding a departed owner's live lock could weaken its existing caller fence; a specific negative control now rejects that change.
- Final `python tests/verify_local.py --build` passes all 25 pure/synthetic and 98 mocked suites, 60 production compiles and all builds. Aggregate default does not execute opt-in controls. Candidate source/project/reference/binary hashes match final production.
- [Commands, source and artifact hashes](../tests/evidence/commerce-lifecycle-2026-11-11.json).

The weak marker is not a full garbage-collection proof. An already-running hung API call may retain its arguments and lock indefinitely; this change does not promise cancellation or eliminate all runtime references. A waiting caller observes invalidation on its next existing polling resume, not through native cancellation. The test model is a fake atomic store and deterministic coroutine scheduling, not Roblox network, native lifetime or persistence validation.

No live DataStore/API calls, purchases, product configuration, publication, map changes or apps are involved. Ordinary unsavable gameplay remains unchanged. The correction does not expand purchase permission or alter server receipt authority.
