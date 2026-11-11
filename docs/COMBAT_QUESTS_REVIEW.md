# Additive combat quests

Base: `7a0b044276a368c506a08ee2ce2c13b41067cb5c`. This small non-map batch implements the owner's request for relevant, nonduplicate beam tasks. All eight previous quest IDs, goals, rewards, events and saved claim meanings remain. No map geometry, NPC assignments, combat timing, save protocol or product settings changed.

## Player behavior

- Three's a Crowd now explicitly means three different NPCs (residents or training fighters) during one beam. The existing sustained attack counts distinct first-hit targets over its lifetime, not simultaneous alignment. This is a description/guide correction, not a new completion rule.
- **Controlled Beams**, new ID `practice_beams`: accept in Quests, then hit the mic practice target with three separate beams. One-time base reward: 60 XP and 25 coins. A sustained beam counts at most once at the existing server-resolved practice-obstruction hook; ordinary pulses cannot add progress. Legacy accepted casts use their existing practice hit hook. FirstBeam history does not retroactively complete the task.
- **Team Effort**, new ID `arena_assist`: while active, earn meaningful assist credit on an equal/higher-level arena player's KO without the finishing hit. One-time base reward: 120 XP and 50 coins. The existing server credit ledger must award positive reward, include at least 10% maximum-health contribution in its inactivity-based credit entry (expires after25 seconds without a new hit, not a rolling damage window), and pass repeat-opponent reward eligibility. Compare target level with the contributor before awarding KO XP. Training NPCs, finishing hits, expired/tiny credit and suppressed repeats do not qualify.
- The two new tasks are explicitly menu-available from server-owned catalog metadata. Existing NPC discovery locks are unchanged. Both appear with combat tasks and keep their current-step tracker visible in the arena. Existing one-active-task, abandon/reset, completed-unclaimed preservation and claim-once rules apply. Existing multipliers still apply to reward amounts.

## Save compatibility and release gate

No ID was repurposed, deleted or migrated into a different objective. Current Profiles sanitation recognizes additive IDs and preserves old progress/claims. There is no live persistence exercise here.

**Do not claim mixed-version or rollback safety.** An older server whose catalog lacks the new IDs discards those entries when sanitizing. A player who moves through such a server can lose new progress or claims, potentially allowing the new one-time reward again. Before release, ensure all serving versions recognize the additive IDs or implement/review a compatible rollout/rollback plan. This draft is not published and does not establish that deployment gate.

## Verification

The missing-feature baseline fails at the absent additive IDs. Final focused checks pass 171 actual-source assertions, one source-order contract and six mutation controls. The renderer passes 431 assertions and seven controls with mocked text metrics. Coverage includes once-per-intent and acceptance-mid-beam behavior, nonpractice/no-beam/ended results, eligible/ineligible/expired/repeat-suppressed assists, exact credit thresholds, consumed ledgers, old discovery locks, claim reentrancy, new claimed-state save/reload/rejoin without reward replay, all old quest identities and current-version sanitation. The rollback test deliberately shows new IDs being dropped by an old catalog.

Independent source/test review found no scoped blocker. The reviewer requested and independently verified new-claim reload and expired-credit test hardening, rerunning the final171 assertions/one contract/six controls and the431 renderer assertions/seven controls.

Existing regressions pass: 374 migration checks, 19 PvP payout checks, 8 accept, 8 claim, 23 prompt, 81 compact guidance, 89 saturated-stop assertions, and the unchanged lifecycle/guide suites. Aggregate checkpoint: **25 pure/synthetic suites, 81 mocked suites, 59 production compiles and all candidate/disposable builds**. After that checkpoint, only test coverage was extended from 152 to 171 assertions; the final focused suite and its six controls were rerun, with no production or builder change. [Exact evidence](../tests/evidence/combat-quests-2026-11-11.json). Test engines use synthetic services and data. Native quest-card fixture checks are prepared and built only, not executed. This does not establish real microphone recognition, actual network/physical input, human readability, multiplayer balance or real DataStore behavior. The practice mechanic reads volume, not spoken words.

Map development remains paused for owner approval. No new apps/tabs, publication, live stores, purchases or audio configuration.

Follow-up: the exact chained-hit regression and clarified Team Effort wording are covered by173 assertions in [test-session isolation review](TEST_SESSION_REWARDS_REVIEW.md). Original171-assertion checkpoint evidence above remains historical.
