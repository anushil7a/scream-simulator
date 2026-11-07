# Scream Simulator development roadmap

Updated November 7, 2026. Owner direction in this document supersedes older 300-level/hold-E specifications. Current local baseline: `83d716b`; connected City Preview reports version 15. No publication is authorized by this management request.

## Product direction

The loop is: aim, scream into the mic, fight for space, earn XP and unlock more destructive screams. The city should create interesting combat routes, cover and breakable opportunities. Side activities support that loop. Build fair, readable, responsive combat before paid products or cosmetic breadth.

## Operating policy

- Usage ceiling: finish the current bounded task, then start nothing new once an applicable Codex window reaches 80% used. Initial check: 27% used / 73% remaining.
- Work locally in focused commits and disposable Studio copies. Publishing requires fresh owner approval. Preserve externally changed cloud state and existing saves.
- Maintain completed evidence, known failures and the next concrete action here. Actual audio, hardware and multiplayer gates stay open until observed.

## Ordered backlog

### P0 — progression foundation (implemented locally; native review pending)

- Cap progression/combat at level 100, with a base scream at level 1 and unlocks at 10, 20, …, 100.
- Keep level-specific damage/range/health bounded; preserve old progress/style data when loading 300-level saves.
- Verify unlock boundaries, overflow XP, retired styles, idempotent migration and reload. Produce a local build; do not publish.
- Why first: continuous damage and destruction need a coherent level/balance model, and a cap change must not erase progress.

### P0 — voice-triggered continuous combat (next)

- Replace hold/release as the default attack trigger. Sustained calibrated voice starts an attack, aiming tracks during the scream, quiet/mute stops it.
- Prototype 4 seconds maximum active time, then 10 seconds cooldown from attack end. Compare with shorter active windows in timed playtests; keep tuning data-driven.
- Use an explicit armed/paused state and clear indicator so calibration, menus, NPC dialogue, typing, spawn protection, rolls, knockdown, death and lost focus cannot attack. Ordinary conversation/background noise is a detection limitation; test a calibrated onset threshold/hysteresis and clear local arm/pause control without requiring E per attack.
- Server owns start/end deadlines, tick rate, damage budget, range/cover/PvP and reward limits. One sustained scream must not become repeated full-damage casts, per-tick XP farming or unlimited destruction. Reject stale/replayed pulses, missing stop messages and aim/power abuse; use server expiry even if the client disappears.
- Rework beam effects as one updated bounded effect per attacker rather than creating an entire old burst every tick. Rework feedback, mic controller and server acknowledgement together.
- Re-test mouse/first-person/touch aim, rolling interruption, short noises, noise during cooldown, reconnect, respawn and silence. Prototype locally before requesting real-mic friend tests.

### P1 — destruction as combat design

- Existing destructibles: bins/benches, trees/bikes and approved building facades. Auto-repair and occupied-repair guards exist.
- Retune health/time-to-break against sustained damage and the 100-level cap. Level unlocks should change tactics, not permit unrestricted whole-map collapse.
- Put useful breakable cover/flanking routes in the arena. Preserve road surfaces, essential buildings, spawn and quest dependencies.
- Verify replication, late joins, occupied repairs, NPC recovery and memory/effect budgets in multiplayer.

### P1 — PvP readability and fair progression

- Keep optional first person, rolls, sprint and visible central arena boundaries.
- Measure time-to-knockout at low/mid/high levels, new-player survivability and damage-per-active-second versus the full attack/cooldown cycle.
- Add readable enemy health/hit confirmation, clear beam/cover feedback and concise combat onboarding where needed.
- Review rewards so player combat/objectives outweigh farming harmless workers. Recommend separating training/fighter targets from occupational residents; implement after reward/quest impact review.
- Consider a simple arena objective (capture/hold a plaza or moving contested zone) only after basic combat is enjoyable; avoid adding multiple modes immediately.

### P1 — bugs, performance and saves

- Inspect the version-15 cloud/source difference before any integration; do not overwrite collaborator edits.
- Reproduce reported failures, add focused regression coverage and measure before optimization.
- Profile server startup/streaming, NPC pathfinding, combat effects and destruction under representative attack/player load. The ~50k-part city and prior early render stall are risk indicators, not proven bottlenecks.
- Real test-universe migration/save contention/rejoin; physical desktop/phone controls and 30-minute multiplayer soak remain required.

### P2 — city supporting the fight

- Keep Barcelona identity, beach, landmark sightlines, authored courtyards and purposeful worker activity.
- Favor denser playable routes and cover over increasing the empty map footprint or NPC count. Limit work to representative blocks/arena spaces and compare street-height before/after views.
- De-emphasize delivery/gardening UI during PvP. Keep Nick as an optional discovery; do not expand side-quest systems before core combat.

### Later — cosmetics and monetization

- Existing style/aura/entitlement scaffolding may remain, but no new cosmetic catalog, badge configuration or paid pass work is prioritized now.
- Review any premium movement only after fairness testing; no paid combat advantage.

## Review findings and recommendations

- **Change:** old hold-E/release flow is mechanically awkward for a microphone game. Continuous voice should be immediate and visibly armed, with bounded server simulation.
- **Change:** old 300-level / 5-level style cadence is spread across Config, Progression, VoiceCombat, UI and profile normalization. A one-constant change would leave inconsistent caps and saves.
- **Keep/refine:** level-gated facade/prop destruction, timed repair, cover and central PvP support the concept. Existing essential-route protection is valuable.
- **Reduce priority:** civilian farming, routine delivery/gardening and cosmetic breadth compete with PvP development. Retain working content while testing a clearer combat reward loop.
- **Performance risk:** blindly firing the existing burst effect and reward handler every frame would multiply VFX, remote traffic, NPC rewards and destruction. Build a dedicated sustained-attack budget.
- **Balance risk:** four seconds active plus ten seconds off is a 14-second full cycle. Test encounter pacing and positioning; do not simply apply four seconds of current per-cast damage every update.
- **Validation gaps:** source/unit/Studio passes do not establish live voice audibility, real-device comfort, saved-data safety or representative multiplayer load.

## Session log

- November 7: management policy and priorities established; owner clarified the cutoff as 20% remaining. Repository clean at review start. Studio in Edit, City Preview version 15 / 30 sources. No cloud writes or publication performed.
- November 7: all 30 version-15 cloud sources match the verified version-14 source record; no collaborator script difference detected. Local progression now caps at 100 and provides 11 styles (base + ten unlocks). Profile schema 4 retains a validated level/XP/style archive and resolves retired style IDs without equipping locked tiers.
- Background continuation configured: active thread heartbeat `scream-simulator-development`, every four hours. It reads this roadmap, checks usage before new tasks, makes local reviewable progress, requires fresh approval for publishing/external pushes, and stays quiet on unchanged blockers or usage cutoff. No manual cron or hidden loop was installed.
- Verification: 508 progression assertions, 1,419 combat/mic/destruction assertions, 370 actual-Config/Profiles migration checks with mocked engine services, 13 actual-Profiles concurrency checks with mocked store; all production sources compile. Both `build/Level100Review.rbxl` and `.rbxlx` build. Progression estimates still model the old 4-second burst cadence and are not forecasts for the proposed sustained attack.
- Native review blocked: Studio connector can inspect the existing cloud place, but native window controls timed out twice. Did not modify that cloud place or restart/discard owner work. Local opening/play and real save migration remain unverified; use the separate Level100Review build when native controls recover. Usage recheck remained 27% used / 73% remaining.

## Next action

Finish native review of Level100Review when Studio controls recover. While that is blocked, implement/test the independent sustained-attack rule/state machine and voice onset/cancellation in source, before integrating it into a local city. Check usage before starting that next task. No publication or external push without owner approval.
