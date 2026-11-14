# Quest cleanup review - November11,2026

Base `36cfb69def30db533e480b78adcb223c239df6f7`; branch fetched and clean before work. Scope follows the owner request to remove destruction objectives and redundant tasks. No publication, live store access, map redesign or new reward system.

## Concrete changes

- Retire “Destroy5 eligible cover objects” and “Help defeat2 elite fighters.” Elite kills previously advanced both the fighter and Elite objectives. Keep one “Help defeat3 eligible training fighters” objective with its existing goal/reward.
- Remove the old cover-credit cache/function and both automatic/legacy destruction-progress calls, including the unused Demolition event. Object damage, destruction visuals, repair and level eligibility remain.
- Keep all8 existing city quests and their definitions/claim semantics. Broader city-quest relevance and roaming training enemies remain backlog items, not completed by this narrow cleanup.
- Keep original `combatChallenges.cover` and `.elite` partial counters as bounded dormant data. Sanitize retains their old bounds4 and1, alongside active fighters0..2. No ID reuse, conversion, reset, retroactive reward or compensation. Existing earned XP, coins, level, style, quest completions, achievements and entitlements stay intact.
- Current Advance iterates active definitions only. UI renders active definitions only. Retired counters cannot advance/pay through current rules, even if a caller requests those IDs. Old-server or rollback code can resume old objectives; this is not a cross-version retirement fence. Actual mixed-version rollout remains a release concern.
- Help text now accurately says the player may be no more than20 levels above the fighter's reward band. Meaningful lower-level attackers still qualify. Server rules are unchanged.

## Reward consequence, not a new balance claim

At level60 a full-credit Elite KO with both old counters ready previously paid420 base +150 fighter +150 Elite =720XP. It now pays420 +150 =570XP. Base KO coins/XP remain unchanged; future duplicate bonus is intentionally removed, not already earned progress.

The deterministic recommended-training model changed level100 from steady666.0 to745.1 minutes, learning1013.4 to1134.0, efficient470.8 to527.0;1220 rather than1095 KOs. Levels10/25/50 are unchanged. These are synthetic assumptions, not live telemetry or time promises. No other rewards were increased to hide the effect. See PROGRESSION_BALANCE.md.

## Verification

- Before patch: actual payout regression failed “Elite assist advanced duplicate retired challenge”; baseline retirement test failed active-retirement assertion.
- `tests/challenge_retirement.py --negative-controls`:135 assertions using actual Progression/Config/Profiles, with isolated fake atomic storage for Load/autosave/release/same-server/new-module rejoin. Three controls reactivate cover, reactivate Elite and drop dormant preservation.
- `tests/quest_catalog_ui.py --negative-controls`:50 actual renderer/catalog assertions with synthetic UI; two controls expose retired cards or hidden undiscovered city quest. All8 city-quest claim/claimed states preserved.
- `tests/pvp_rewards.py`:19 actual helper/handler checks, including exactly one challenge per eligible KO, retired no-op reward calls and lower/upper reward-band boundaries.
- Existing profile migration374 checks pass. Full25 pure/synthetic suites,66 mocked-service suites,57 production compiles and all candidate/disposable fixture builds pass.
- Independent review reran135+3controls,19 payouts,50UI+2controls,374 migration and whitespace; no code/integrity blocker. Copy correction described above was incorporated.

No native Studio/device/RemoteEvent execution or live persistence was claimed. Built fixtures are not native evidence. No programs/tabs opened; command sessions finished. Next validate actual quest presentation and isolated native training reward behavior, then continue remaining authorized backlog without publishing.
