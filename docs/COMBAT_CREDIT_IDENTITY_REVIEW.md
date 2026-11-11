# Opaque combat-credit session identity

Base: `a503c5ed49747900f740d98362a5bea6a3771467`. This is a reference-lifetime correction, not a reward-balance or persistence change. Map development remains paused.

## Confirmed reference path

Actual Bootstrap recordCredit and CombatCredit code stored an entire session table in each new contribution. In a deliberately idle victim ledger, the departed attacker's session and nested profile remained reachable at simulated100,000 seconds. The25-second window controls eligibility, not automatic removal: a subsequent positive Add prunes expired entries; Split consumes the ledger at a KO. This reproduces a Lua reference edge, not a native memory leak or measured collection failure.

## Change and preserved behavior

- Every joined session receives a dedicated fresh empty rewardIdentity table. It contains no Player, profile or session pointer and is independent of voice eligibility. It is runtime-only and never saved or transmitted.
- Recording requires a table identity; missing, false, numeric/string/boolean identities fail closed. Only a genuinely new entry receives the current token and test-mode flag. An existing missing, quarantined, different-session or different-mode entry cannot be adopted; it stays quarantined false until the actual Credit.Add expiry creates a new entry.
- Payout requires the current recipient's table identity to match the entry, plus the existing mode gates. Rejected contributions remain in the original denominator and do not spend repeat-opponent history. Current session acquisition semantics remain; respawn does not create a new session token, while rejoining does.
- Pure CombatCredit, windows, damage limits, XP/coins/challenge rules, repeat-opponent policy, cleanup cadence and saved profile schema are unchanged. Stale ledger entries may still exist until normal cleanup, but this provenance field no longer points into the old profile/session.

This removes one explicit reference edge only. Already-running callbacks, saves, other runtime fields or engine/service references may retain objects. No native GC, memory bound, full collectability, multiplayer or real persistence claim is made.

## Verification

- `python tests/combat_credit_identity.py --negative-controls`: **96 assertions and six controls**, independently rerun. Actual helpers and joined constructor cover empty unique tokens, no profile backreference, missing/malformed/legacy/quarantined attribution, fresh rejoin identities, test-mode changes, exact expiry behavior, no repeat-history consumption for rejected sources, original denominators and numeric payout parity. Controls restore the session reference, repair quarantine, remove recipient comparison, permit missing recorder identity, permit malformed payout identity, and put profile data inside the joined token.
- Explicit compatibility mutation commands: `python tests/test_session_rewards.py --negative-controls` passes **56 assertions/11 controls**; `python tests/combat_quests.py --negative-controls` passes **173 assertions/six controls/one contract**. `python tests/pvp_rewards.py` passes **19 checks**. All independently rerun. Three fixtures gained explicit fresh synthetic identity tokens and corresponding mutation targets; production reward rules did not change.
- `python tests/combat_credit_identity.py --baseline` reproduces the old retained-session edge against a503c5e. `python tests/verify_local.py --build` passes **25 pure/synthetic suites,86 mocked suites,60 production compiles and all candidate/disposable builds**. Default identity execution runs assertions, not its opt-in controls; those are the separate commands above.
- [Exact source, artifact and explicit-command evidence](../tests/evidence/combat-credit-identity-2026-11-11.json).

No native GC, measured memory saving, microphone/network, live persistence or full collectability claim. No apps, publication, settings, live stores or map edits.
