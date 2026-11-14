# Compact navigation copy correction

Base: `2978fc2c48c562a765c38d754cce40f51b82692e`. Independent compact-map review found unlock guidance still naming the original districts and the race start still directing players to a nonexistent compact pier.

## Narrow fix

For the compact layout only, crowd guidance names Eric Sol in the west courtyard, sprint names the Boardwalk runner on the west promenade, and dodge/arena name the Arena coach at the west arena gate. Names match the actual CompactCity jobs. Inactive legacy-layout giver labels remain unchanged.

The race-start message now tells players to follow the promenade east to the finish. Marker ID `PierFinish` is intentionally retained for compatibility; it is not a claim that a pier exists. Quest IDs, events, objectives, rewards, discovery/progress fields, 25-second deadline and repeated-start guard are unchanged. No geometry, save or combat edit.

## Evidence

- Before production editing, the new actual Config/CompactCity regression failed on a stale compact giver at the base checkpoint.
- Corrected actual modules and race-start snippet: 69 assertions and four negative controls. Controls restore old crowd, sprint, coach and pier wording; each fails as intended. Assertions preserve all eight quest identities/goals/events/rewards/descriptions, legacy giver fallback and race deadline/idempotence.
- Existing actual quest renderer: 361 assertions and six controls; profile migration: 374 assertions.
- Full local verification: 25 pure/synthetic suites, 78 mocked-service suites, 59 production compiles, candidate source audit and all disposable builds pass.
- Independent reviewer inspected the exact production diff and reran guidance/controls, renderer/controls and migration; no blocker. [Source/build evidence](../tests/evidence/compact-guidance-2026-11-11.json).
- Native compact fixture rebuilt/source audited only. Text readability, physical navigation and player comprehension remain untested. No publication/live stores or apps opened; archived original unchanged.

Microphone-policy research was completed in parallel without editing production UI. See [policy review and proposed copy](MICROPHONE_POLICY_REVIEW.md). Its rating/settings verification and UI implementation remain pending.
