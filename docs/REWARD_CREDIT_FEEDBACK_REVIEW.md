# Reward notices report credited amounts

## Reproduction and narrow correction

Against `b0099a0113d8ae0fc96c512d36a34b622c85a0b0`, actual reward helpers and the ClaimQuest fragment reproduced a level-100 player at 999,999,990 coins receiving zero XP and ten coins while the notice advertised 120 XP and fifty coins. This was a presentation discrepancy, not newly lost progression or an exploit.

`coins` now returns the actual balance increase after the existing cap. `xp` returns XP accepted toward progression, including XP spent crossing levels and excluding the existing overflow discarded when level 100 is reached. Missing sessions and capped XP return zero. All existing grant formulas, multipliers, rounding, thresholds, caps, health/milestone updates and resulting saved-state fields are unchanged.

Quest, Found Nick, combat-challenge and KO/assist confirmations consume those returned amounts rather than multiplying nominal rewards again. The challenge helper retains its nominal first return and adds credited XP as a second return. This keeps completion/renewal messaging intact even if the credited bonus is zero. KO eligibility, underdog timing, repeat-opponent accounting, contribution ledger consumption, quest events and claim-before-grant guards are unchanged. A capped claim is still consumed as before; zero credited XP is not treated as a failed claim or repeat-opponent restriction.

The owner's normal-play choice for temporary save failure remains unchanged. Feedback describes current-session credit, not a durable-save guarantee. Test-session isolation, persistence, receipt processing and product configuration are untouched. Quest cards may still show configured base rewards; this change concerns actual grant confirmations.

## Vault and verification

Consulted the vault before the task: *Economies and Currencies* transaction/duplication/pitfall/checklist guidance, currency presentation guidance, and *Menu Archetypes - Shop Settings Codes Rewards* button-state, quest-board, Common mistakes and Checklist sections. Used their server-authoritative, nonduplicate and truthful-feedback principles without importing code or adding a new reward system.

`tests/reward_credit_feedback.py` executes actual Bootstrap helpers and ClaimQuest/FoundNick/KO call-site fragments with real Progression, CombatCredit and TrainingRules modules. Players, service boundaries and state notifications are mocked. It covers near/full coin caps, level-99 overflow, multi-level XP, fractional multiplier rounding, boost state changing after the grant, cap-reaching KO followed by a zero-XP challenge, retained underdog events, duplicate claims/achievements, ordinary `canSave=false` play and separate test-baseline helper behavior. It is not the whole dispatcher, persistence integration, real commerce or native UI execution.

- 29 focused assertions, five negative controls and the pinned historical discrepancy pass. The final three assertions retain the independently identified KO boost-expiry case.
- Existing action-feedback, combat-identity, combat-quest, panel-lifecycle, PvP and claim fixtures now return numeric grant amounts from their stubs. Their original grant/guard assertions remain; this is a return-contract adaptation, not a weakened oracle.
- Full verification passes 25 pure/synthetic suites, 106 mocked-service suites, 63 production compiles and all configured local candidate/disposable builds. This aggregate preceded the final three test-only assertions; the final 29/five focused run passed separately and production was unchanged.
- Exact commands, hashes and independent review are recorded in `tests/evidence/reward-credit-feedback-2026-11-12.json`.

No Roblox launch/publication, live persistence, purchase or GitHub push occurred. Native display readability remains unverified. The local checkpoint remains behind the explicit push-confirmation hold; other release gates are unchanged.
