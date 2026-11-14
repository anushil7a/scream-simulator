# Sprint and third-person review — November 11, 2026

Base: `93bca5be876fbf421640c39f81c016089035f344`, clean local and fetched shared branch `feature/microphone-city-redesign`. No unfinished Git operation was present. A final fetch still matched that base. This is a focused first batch of the latest playtest directions; remaining work is in [PLAYTEST_BACKLOG.md](PLAYTEST_BACKLOG.md).

## Reproduced defects and correction

The old actual `stepSprint` helper, under 1,200 alternating 0.1-second request ticks, granted approximately 60 sprint seconds across 120 simulated seconds while ending with all 10 stamina seconds and no exhaustion lock. The last request determined whether the already elapsed interval was charged or regenerated. Tapping could therefore avoid exhaustion.

The server now charges the interval for which it previously granted sprint speed, including release/interruption and delayed ticks. Partial refill begins after one second without granted sprint, at two stamina seconds per second. Maximum stamina remains 10 seconds; full exhaustion retains its five-second recovery. The same alternating test now reaches exhaustion/recovery repeatedly, grants approximately 50 sprint seconds, and ends empty. This is not a lifetime sprint cap: deliberate rest still regenerates stamina.

Independent review reproduced a second issue in the actual RemoteEvent handler: flooding the request window could discard `Sprint,false`, leaving the request latched and able to restart after exhaustion. An idempotent false-only stop now clears the request before the flood gate. It cannot grant speed; start requests retain validation/rate limits. Respawn resets granted-running state, refill deadline, charge and the billing timestamp.

First-person controls, V binding and Settings entry were removed. The project and client select Classic camera with a minimum six-stud zoom, reapplied on character creation. Desktop aiming remains mouse-based; touch uses view center. Client teardown restores the original properties. Camera obstruction behavior still needs representative-map/device testing.

## Verification

- `python tests/sprint_state.py --negative-controls`: 184 assertions, four negative controls. Actual server request handler and sprint helper with simulated clock, player, velocity and services; covers holds, taps, releases, exhaustion, regeneration boundary, malformed/start flooding, flood-stop, eligibility interruptions and delayed ticks.
- Mutations caught: remove flood-safe stop; bill current request instead of previously granted interval; remove refill delay; cap billed time at 0.25 seconds. The capped-time mutation fails at the earlier one-second flood-release billing assertion, before the separate delayed-tick case.
- `python tests/sprint_input.py`: 48 assertions on extracted client input helpers/callbacks. `python tests/respawn_state.py`: 13 checks on actual spawn/removal source with mocked services.
- `python tests/third_person.py --negative-controls`: four assertions, two negative controls (remove minimum zoom; remove respawn callback).
- `python tests/verify_local.py --build`: all 25 pure/synthetic suites and 60 mocked-service suites pass; all 57 production Luau sources compile; exact-source candidate and review fixtures build successfully. `tests/StudioThirdPerson.client.luau` also compiles separately. That standalone fixture was not executed natively.
- Independent reviewer `review_core_controls` reran sprint, input, respawn, camera and mutation tests, plus an additional actual-handler flood-release/recovery probe. No blocking issue remained after the stop correction. The subsequent camera-test change adds a named missing-callback assertion; production code did not change afterward. Final self-review and whitespace checks completed.

## Native Studio evidence and limits

Studio MCP was initially disconnected, then verified against a disposable local `OnboardingReview.rbxl`, Studio 0.747.0.7471481, PlaceId 0, not persisted to cloud. Its source inventory contains review client/shared code and no production Bootstrap/DataStore path. The fixture uses synthetic microphone state, remotes and viewport selection.

The actual client UI produced 17 complete sampled rows across portrait, landscape and desktop layouts, with no reported clipped text. Settings showed third-person camera and the one-second refill delay; old view controls were absent. Native property query returned Classic mode, minimum zoom 6, maximum 400 and camera distance 12.5. After a tool-injected V press and 15 zoom-in events, mode stayed Classic and camera distance was 6.000000476837158. These are native-engine observations with synthetic input, not physical input tests.

The native fixture was built before the final server-only flooded-stop correction; its client source matches the final client. It does not validate actual server sprint movement or RemoteEvent transport. Full final builds were rerun afterward. Evidence summary: [core-controls-2026-11-11.json](../tests/evidence/core-controls-2026-11-11.json). Local verbose outputs are under ignored `build/core-controls-*`.

Remaining gates: native full-server sprint movement and respawn under real input/network conditions; physical touch/gamepad and camera obstruction; real microphones/proximity voice; multiplayer latency and isolated persistence. No live DataStores, purchases, audio configuration or Roblox publication were performed.

## Delivery and cleanup

GitHub push is blocked on this host: the GitHub plugin reports installed=false, `gh` is absent, and Git has no usable noninteractive credential. A push dry-run failed before authentication. Reconnect the GitHub integration or authenticate local Git, then fetch/reconcile and push the verified local commit to the existing draft PR #1; never force-push. No remote update is claimed.

The disposable play session was stopped, its place saved locally, and its Studio window closed. No browser tabs were opened. Pre-existing Codex was preserved. A task-created minimized Windows “Pick an app” window remains: supported CUA binding rejected the minimized window, so it could not be dismissed through the exposed controls. No unsaved work was discarded.
