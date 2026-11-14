# Scream Simulator development management

Read `docs/ROADMAP.md` at the start of work; update its status, evidence and next action before finishing.

Use `feature/microphone-city-redesign` as the shared development branch and update its existing PR #1 after completed, tested changes. The owner confirmed this branch on November 9; the separate `codex/microphone-combat` prototype/PR #2 is superseded and should not be merged wholesale. Fetch and preserve contributor updates before starting work; never force-push.

- Core concept: microphone-powered PvP with level-based progression. Latest owner direction excludes object destruction from the compact replacement; do not reintroduce destruction or repair objectives/systems. Preserve the archived original exactly.
- Prioritize combat feel, correctness/security, progression balance, player readability and measured performance. Cosmetics, Robux products and badge configuration come later.
- Current direction: voice-triggered sustained attacks, target a maximum four-second attack and five-second cooldown per the latest November 11 playtest direction; level cap 100; one new scream style every ten levels. These timings require playtesting, not a claim of final balance.
- Do not publish/upload to Roblox, change live access/settings, merge a release, or push externally without explicit current approval for that action. Earlier blanket publishing authorization is revoked. Build/test in disposable local places; preserve collaborator changes and player progress.
- Latest owner instruction (November 11): continue authorized work without repeated allowance checks or percentage requests. The owner will say when usage is low or work should stop. Respect actual hard limits, keep tasks small/checkpointed, and pause for an issue requiring owner help. This supersedes the earlier usage-check requirement.
- Current owner approval: push completed tested changes to the existing GitHub development branch (no force push or release merge). The owner confirmed the current release destination as City Preview, place 90337242377543 (not original place 122465114514497); verify collaborator state, saves and native runtime before publication. Record completion; this is not blanket approval for later releases.
- Work in small reviewable tasks. Prefer fixing reproduced failures over adding unrelated content. Protect navigation and quest dependencies during map changes; keep real voice transport and client-reported power limitations explicit.
- Do not discard old level/XP/style data when lowering the cap. Preserve a validated legacy snapshot and test migration/reload behavior before release.
- Tests must match their claims. Synthetic microphone/Studio tests do not establish human voice, actual phone behavior, real saves or multiplayer performance. Never store recordings or credentials.
- The owner removed the current chat's scheduled development follow-up on November 9. Work on request; do not recreate a schedule without a new request or claim background work continues. Notify the owner for a completed meaningful change, blocker or approval-ready build; stay quiet on unchanged checks.

