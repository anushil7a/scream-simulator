# Scream Simulator development management

Read `docs/ROADMAP.md` at the start of work; update its status, evidence and next action before finishing.

- Core concept: microphone-powered PvP with level-based, bounded map destruction. Existing features may change when evidence improves the game.
- Prioritize combat feel, correctness/security, progression/destruction balance, player readability and measured performance. Cosmetics, Robux products and badge configuration come later.
- Current direction: voice-triggered sustained attacks, prototype a maximum four-second attack and ten-second cooldown; level cap 100; one new scream style every ten levels. These timings require playtesting, not a claim of final balance.
- Do not publish/upload to Roblox, change live access/settings, merge a release, or push externally without explicit current approval for that action. Earlier blanket publishing authorization is revoked. Build/test in disposable local places; preserve collaborator changes and player progress.
- Check account Codex usage before each new task and at task boundaries. Stop starting tasks when any applicable Codex allowance is at least 80% used (20% remaining). Finish and verify only the already-started bounded task, update the roadmap, then stop. If usage is unavailable, do not start autonomous feature work; record the limitation.
- Work in small reviewable tasks. Prefer fixing reproduced failures over adding unrelated content. Protect navigation/quest dependencies during destruction; keep real voice transport and client-reported power limitations explicit.
- Do not discard old level/XP/style data when lowering the cap. Preserve a validated legacy snapshot and test migration/reload behavior before release.
- Tests must match their claims. Synthetic microphone/Studio tests do not establish human voice, actual phone behavior, real saves or multiplayer performance. Never store recordings or credentials.
- Between conversations, use only the configured thread follow-up automation. Do not claim work continues when no scheduler is active. Notify the owner for a completed meaningful change, blocker or approval-ready build; stay quiet on unchanged checks.

