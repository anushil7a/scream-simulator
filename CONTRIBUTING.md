# Contributing to Scream Simulator

## Start here

1. Fork this repository on GitHub and clone your fork.
2. Check out `feature/microphone-city-redesign`, run `python3 tests/verify_local.py --build`, then open the disposable `build/SustainedLocalPlay.rbxl` in Roblox Studio and press **Play**. The city generates when play starts; an empty Edit viewport in the local build is expected.
3. For code changes, edit the files in `src/`. Rojo 7.7.0 was used for the included builds.
4. Rebuild from the repository root:

```sh
mkdir -p build
rojo build default.project.json -o build/MicrophoneCity.rbxl
rojo build default.project.json -o build/MicrophoneCity.rbxlx
```

The `src/` files are the source of truth. Rebuild place files locally; generated `build/` files are ignored. Submit source changes and test evidence, not only binary place edits. The current compact candidate uses `CompactCity.luau` and shared `CompactLayout.luau`, selected by Config; `City.luau` is the legacy path. Map development is paused pending owner approval. Do not modify the exact original archive.

## Main files

- `src/ServerScriptService/CompactCity.luau` and `src/ReplicatedStorage/Shared/CompactLayout.luau`: selected compact layout; owner approval is required before further map work. `City.luau` retains the legacy layout.
- `src/ServerScriptService/World.luau`: residents, movement, traffic, lighting.
- `src/ServerScriptService/Bootstrap.server.luau`: server combat, progression, quests, sprint and dodge.
- `src/ServerScriptService/CombatRules.luau`: targeting and collision calculations.
- `src/ReplicatedStorage/Shared/Config.luau`: balance, scream tiers, health, arena bounds.
- `src/StarterPlayer/StarterPlayerScripts/Client.client.luau`: menus, HUD and effects.
- `src/StarterPlayer/StarterPlayerScripts/RunAnimation.client.luau`: running and rolling animations.
- `src/ServerScriptService/Profiles.luau`: sanitized player persistence.

## Test your change

Use a separate local or private test place. Read `docs/IMPLEMENTATION_STATUS.md` before stopping any ongoing test run. Never commit temporary fixture appendices to production scripts. Real microphone, multi-touch and multiplayer checks must be labeled separately from synthetic fixtures.

Use the explicitly guarded disposable local fixtures for temporary profiles. Normal candidate builds retain normal profile handling; do not assume every Studio build is a save sandbox. Never publish disposable fixtures or connect experiments to production player data.

Test tools are server-authorized only in Studio or for the configured owner in that same user-owned experience. There is no public-testing switch. The first test mutation freezes the legitimate baseline; saves retain that baseline, not temporary test progress. Combat credit is fenced to session/mode; this is not isolation of shared sports or physics. Test-session NPC damage and ResetBots require the guarded save-disabled local fixture. Ordinary Studio alone is not a persistence sandbox. See `DeveloperAccess.luau` and `docs/TEST_SESSION_REWARDS_REVIEW.md`.

For relevant gameplay changes check:

- Automatic mic onset starts sustained beams; quiet/interruption ends them, with fresh onset required after cooldown. Aim, cover, safe areas and spawn protection remain server-controlled. E pauses/resumes rather than firing each attack.
- Rolling preserves cooldown and collision behavior against current static cover.
- Traffic and destruction/repair belong to historical layouts, not the pedestrian compact candidate; do not reintroduce them.
- Residents remain grounded and walk through usable routes.
- Menus remain readable on desktop and phone; quests can still be completed.

If `luau-compile` is installed, compile each changed Luau file. Build both place formats and playtest before submitting.

## Submit work

Create a feature branch, commit a focused change, and open a pull request against `feature/microphone-city-redesign` for this redesign. Keep release changes to `main` separate until release gates pass. Describe what changed, how you tested it, and include screenshots or a short clip for map, UI, or animation work. Use GitHub Issues for bugs and ideas, with reproduction steps and expected behavior.

Publishing the live experience remains the owner's responsibility. GitHub access does not grant Roblox Studio collaboration permissions. Never commit account cookies, API keys, credentials, or player saves.
