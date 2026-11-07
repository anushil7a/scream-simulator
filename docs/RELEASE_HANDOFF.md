# Resume the microphone city release

Updated November 6, 2026. Gameplay source: `8f0bb60`, branch `feature/microphone-city-redesign`.

**Latest update:** City Preview version **14** now matches gameplay commit `55563b3` (optional first-person aiming). All 30 cloud sources and four place-configuration checks pass; startup includes the view toggle and crosshair. Source and README remaining-work list are pushed. The older version/source details below are historical.

## Current state

**Publication recovered:** after the owner restarted Studio, the latest build was uploaded to the existing City Preview and reopened at **version 12**. All 30 sources match `8f0bb60`; all four place configuration checks pass. UI, modern chat and five loaded/playing ambience sources passed the Studio startup check. The publishing blocker below is historical; human/external evidence gates remain open. See `docs/QA_REPORT.md` for the current publication record.

- Latest source is pushed to [GitHub](https://github.com/anushil7a/scream-simulator/tree/feature/microphone-city-redesign); review remains in [draft PR #1](https://github.com/anushil7a/scream-simulator/pull/1).
- Rebuilt local files: `build/MicrophoneCity.rbxl`, `build/MicrophoneCity.rbxlx`, and `build/CityPreviewLatest.rbxl`. These generated files are ignored by Git; README has reproducible build commands.
- Last verified cloud copy: [City Preview](https://www.roblox.com/games/90337242377543/Scream-Simulator-City-Preview), place **90337242377543**, universe **10769005350**, version **10**, source `229a137`. Modern chat/typing cancellation and ambience changes are newer than that verification.
- Latest local Studio copy is in Edit with clean production Ambience source restored. No fixture should be published. The original production experience has not been overwritten.
- Native Studio controls repeatedly time out across three consecutive goal turns. The Studio connector can inspect/test local copies but has no publishing command. No new cloud upload is claimed.

## Recover publishing

1. Save any unrelated Studio work, recover or restart Studio, and open the rebuilt `build/CityPreviewLatest.rbxl` from this repository. The empty Edit viewport is expected: the city generates during Play.
2. Tell the agent Studio is responsive. The existing authorization covers publishing the update to City Preview; no repeat approval is needed for that upload.
3. Publish the rebuilt place to the existing **City Preview** place listed above. Verify the destination ID before overwriting. Keep the original production place separate until its release gates pass.
4. Freshly reopen the cloud place. Record its new version; compare all 30 production source lengths/hashes with the checked-out commit and run `tests/StudioPlaceConfig.luau` in Edit. Run a fresh-server startup smoke. A successful local build or upload click does not establish publication.

## Human and external evidence still needed

- **Real voice:** two eligible accounts, two actual microphones/devices. Follow `prototypes/microphone/README.md`: hold/use voice/release, near/far listening, silence, normal conversation, mute/denial/disconnection/retry, comfortable-volume calibration and latency. Owner-reported meter activity does not establish another listener hearing live voice.
- **Physical input and multiplayer:** keyboard/mouse and phone touch, combined roll/attack inputs, animation blending, car collision/recovery, arena transitions, simultaneous attacks, quest completion and repair occupancy/late joins. Record exact place version and device. Do not substitute synthetic mic values for this pass.
- **Persistence:** use dedicated test accounts in the separate preview universe. Check legitimate progress through leave/rejoin and concurrent session/reward cases; do not use test mutations as save evidence. Studio uses `ScreamSimulator_Studio_v2`; published places use `ScreamSimulator_v1` within their own universe. Never conduct destructive experiments against production player keys.
- **Performance and city acceptance:** owner reviews street-height routes, activity density, interactions and overall art/game feel. Measure the agreed desktop/phone and target-player load, including the required representative 30-minute multiplayer soak. Existing one-client samples do not establish those targets. Investigate a reproducible cold-join stall if it appears in that run.
- **Optional configured products:** valid owner pass/badge IDs are still absent. Hooks and in-game achievements exist; no published badge or real purchase verification is claimed. Public friend-test tools remain enabled as requested, with test progress isolated from legitimate saves.

Keep results and reproducible defects in `docs/QA_REPORT.md`. Resume implementation for any observed failures; do not call the full redesign complete until the brief's evidence gates are met.
