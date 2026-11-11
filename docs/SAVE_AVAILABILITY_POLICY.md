# Save availability and ordinary play policy

Owner decision, November 11, 2026: **Keep playing.** The choice offered was ordinary play versus temporarily preventing players with unavailable saving from affecting other players' saved combat rewards. The owner chose ordinary play.

## Intended behavior

- A normal player whose save is unavailable or who loses profile ownership may continue normal gameplay/combat and reward interaction. Do not silently isolate that player, disable their combat, suppress another player's legitimate reward, or put them into developer-test mode solely because saving is unavailable.
- Keep the existing clear saving-unavailable/temporary-progress warning and last-confirmed-checkpoint recovery policy. Do not imply temporary progress was saved or guarantee recovery after process exit.
- Existing paid-purchase and durable-delivery availability checks remain unchanged; this choice concerns ordinary play and combat rewards, not buying unavailable products.
- Preserve acquisition/write ownership fencing: never overwrite another owner's profile. This decision does not relax persistence correctness, authorize live DataStore tests or grant publishing permission.
- Developer-test sessions remain a distinct policy. Their temporary edited levels/rewards must stay isolated from ordinary persistent combat rewards, with the frozen legitimate save baseline preserved.

## Supporting audit and tradeoff

A simulated persistence/reward audit used a normal saved level 1 baseline, an ownership-loss response, and three ordinary Rookie KO awards through the current reward helpers. Temporary progression reached level 3. A writable level 1 opponent's eligible KO then yielded 108 XP instead of 96 against the original level 1 victim, with 20 coins either way. Fake-store saves retained level 2/37 XP versus level 2/25 XP for the recipient; the foreign-owned victim checkpoint remained level 1.

This illustrates that ordinary temporary progression can influence another player's durable rewards. It did not bypass ownership fences or establish corruption, a live incident, or a real farming rate. Actual fights/geometry and storage were mocked; qualifying combat, repeat-opponent limits and diminishing rewards still apply. The owner's normal-play decision retains these reward interactions rather than introducing save-status combat isolation. This audit example is engineering evidence, not a claim that the owner reviewed its exact numbers.

No runtime change was required to implement this decision. Native saves, real network/combat, and the separate mixed-version quest writer rollout gate still require their own evidence. The current no-publication and paused-map boundaries remain in force.
