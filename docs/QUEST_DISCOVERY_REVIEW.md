# Quest discovery presentation - November11,2026

Base `32cced3bf9f098711988ed42672a72c72338ee7e`, fetched and clean. The prior cleanup retired destruction/overlapping Elite challenges, but did not fix the named Soler cards appearing duplicate. This follow-up fixes that actual presentation defect without replacing saved objectives.

## Behavior

Undiscovered “A Little More Color” and “Leave Only Footprints” previously showed the same generic instruction to meet Mar Soler. They now show their distinct original objectives: water three raised garden beds, or collect six washed-up beach bottles. Each then gives the correct same giver and Talk unlock instruction. Their MEET NPC action remains locked, including stale completed-but-undiscovered packets; exposing a description does not grant the quest.

The existing Crowd/Evade/Underdog tasks render first under BEAM COMBAT TASKS. Other existing activities are labeled OPTIONAL CITY ACTIVITIES. An active task still has its separate tracking/claim card first. Hidden Nick stays undisclosed until discovery. Each visible catalog quest appears once; grouping does not reorder or mutate Config.Quests or player save state.

No ID, goal, reward, event, server behavior, save schema, map, NPC placement or quest completion changed. Existing accept/track/abandon/claim/claimed controls keep their guards. Cards measure the full objective plus unlock text for height. This makes relevance explicit, not a claim that optional city objectives were redesigned into combat missions.

## Verification

- Baseline32cced3: actual garden/beach card description strings are identical generic text; neither includes its real objective. Regression fails as expected.
- `python tests/quest_catalog_ui.py --negative-controls`:361 actual renderer/catalog assertions in narrow/wide synthetic UI, six controls for retired cards, hidden disclosure, generic objective text, reversed groups, unlock bypass and claimed reward replay.
- Existing actual acceptance8, claim8, profile migration374 and retirement/fake-store135 assertions pass.
- `python tests/verify_local.py --build`:25 pure/synthetic suites,66 mocked suites,57 production compiles, exact-source candidate and all disposable fixture builds pass.
- Independent review cleared exactly-once partitioning, discovery/action guards and data compatibility; independently reran361 assertions and all six negative controls.

## Native fixture and limits

`python tests/build_quest_cards_review.py` builds `build/QuestCardsReview.rbxl`. It contains the actual client with synthetic microphone/remotes, an empty floor and no real profile server. It tests undiscovered/known cards at390x844,844x390,1280x720; verifies native TextFits, ordering, visible counts and distinct Soler descriptions. `QUEST_CARDS_RESULT` reports actual result. Never publish this fixture.

Native Studio execution of the earlier fixture passed117 checks across six cases with zero clipped card text. Studio was stopped and closed. That run preceded the final shorter subtitle and added title/subtitle assertions; the final129-check fixture was compiled but not rerun. Do not claim final subtitle native fit or an exact executed artifact hash without separately captured evidence. A task-created minimized Windows “Pick an app” dialog remains: supported inspection rejects minimized windows and exposes no restore/activate method. No blind close or process kill was attempted. Studio is closed and preexisting ChatGPT preserved; no approval is pending. These checks do not validate physical phone input, accessibility, real voice, server networking or live saves. Existing migration behavior is unchanged; no live store operation is authorized by this test.

Native Output also reported an asset203785492 type mismatch. No matching ID exists in current src; its cause is unverified and it did not fail the quest assertions.

Next: verify draft-branch delivery, then investigate the recovered world-space yellow dodge-box evidence. The leftover minimized chooser needs a supported restore/close route or manual close. Wider city-quest redesign and roaming trainers remain separate backlog work.
