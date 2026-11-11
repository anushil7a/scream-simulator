# Test-session combat reward isolation

Base: `1e14e91103f6855b77673784b022e603cec19ef6`. Astra's independent review identified temporary owner test levels leaking rewards to ordinary players. A separate focused worker reproduced it before editing production.

## Confirmed synthetic reproduction

Actual developer MaxLevel, payout/XP, autosave and Profiles code with real CombatCredit/Progression and a fake atomic store reproduced a test victim at level100 whose legitimate baseline was level1. An ordinary level1 recipient received **862 XP and25 coins**, reached level8, and saved the contaminated progression. The owner's own save correctly remained level1. A mixed training ledger with72 test-owner damage and8 normal-player damage also yielded4 XP and one training-challenge step to the normal participant. These are helper-level simulations, not a native exploit demonstration.

## Boundaries

- Sustained and legacy PvP target eligibility requires both current sessions to have the same test-mode status. The gate precedes damage and dodge/Evade progress. Test-to-test PvP remains available; normal-to-normal combat is unchanged.
- Test sessions cannot damage shared residents/training fighters, obtain their Crowd/reward effects, or globally reset bots outside the existing isolated local fixture. That exception requires Studio, PlaceId0 and the server-side LocalSustainedPrototype flag; joined profiles are temporary there. Ordinary Studio alone is insufficient because it can use a separate persistent Studio store.
- ResetBots rejects outside that fixture before freezing the player's legitimate save. Its live button is hidden. Ordinary Studio may still show it, but receives an explicit server rejection explaining the fixture requirement. Practice-target beams remain available.
- The first authorized test command cancels the active sustained/legacy attack and clears incoming victim credit before copying the legitimate baseline. Later test commands do not recapture that baseline. Existing autosave/departure/shutdown selection still saves the frozen baseline, not test data.
- Each new damage-credit entry is bound to its original session table and mode. A different session/mode cannot adopt it. A provenance change during the same inactivity-based streak permanently quarantines that entry until normal expiry creates a genuinely new entry. Continuous hits can extend quarantine; a KO consumes the ledger. Missing or untagged attribution fails closed.
- Payout snapshots attribution before CombatCredit.Split clears the ledger, then validates current source session/mode and finisher/victim mode. Excluded damage remains in the original split denominator, so it is not redistributed. Rejected recipient credit does not consume repeat-opponent eligibility. No combat pool, progression curve, cooldown, lease or save schema change.

This is **combat/reward isolation, not a private world or isolation of every interaction**. Avatar physics, visibility and sports/shared-world interactions remain outside this fix. It does not authenticate reported microphone readiness, aim or audio power; that separate client-trust limitation remains. Do not claim native exploitation or real-world audio authenticity.

## Related assist-copy correction

Team Effort no longer implies all qualifying damage must fall inside a rolling25-second window. The existing ledger refreshes cumulative credit while successive hits are no more than25 seconds apart. Its copy now explicitly says your damage credit expires after25 seconds without a hit. The exact10 damage at0,1 at24,1 at48,KO at49 regression qualifies as before; balance and CombatCredit are unchanged.

## Verification

- **56 isolation assertions and11 negative controls**, independently rerun. Actual helper/dev/autosave/Profile slices, four actual target predicates with mocked other eligibility, fake release/rejoin and full saved snapshots. Controls remove each sustained/legacy player/NPC gate, immutable provenance, payout identity, baseline freeze, transition cancellation and reset restriction. They fail intended behavior assertions rather than extraction failures.
- **173 combat-quest assertions/one source contract/six controls**, **19 PvP payout checks**, **94 developer checks/three source contracts**, **61 developer UI checks**, **431 quest renderer assertions**, and relevant target/healing/trainer/compact integration checks pass. Final independent review found no scoped blocker.
- One full checkpoint passed **25 pure/synthetic suites,82 mocked suites,59 production compiles and all candidate/disposable builds**. [Exact evidence](../tests/evidence/test-session-rewards-2026-11-11.json).

No native Studio execution, physical input, microphone, RemoteEvent/network, real persistence, sports isolation or multiplayer soak claim. The targeted gates are executed as extracted predicates, not a full engine raycast/damage pipeline. Engine context, geometry and text metrics are mocked. No apps/tabs opened, publication, live DataStores or product/audio configuration. Map development remains paused and original archive unchanged.

## Follow-up review caveat

Astra found no blocking isolation defect, but test-to-test KOs still update the server's shared repeat-opponent history. Two authorized test participants who rejoin normally in the same ordinary Studio server can therefore inherit a repeat-reward penalty. Outside Studio only the single verified owner is currently authorized, so two distinct live test players are not reachable under current access rules. This does not leak temporary level rewards into saves. Before expanding tester access, add an explicit mode-separated repeat-history regression and decide whether test history should be isolated. Not fixed or natively validated in the voice-eligibility batch.
