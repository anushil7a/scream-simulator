# Test-level tool review - November11,2026

## Scope and behavior

Base: `4e37a4480c7bffd79884b31369fe4cd6a9900df8`, fetched and clean. Owner requested a +10 level test tool and a future production minimap in the test-tools location. This batch implements only the level tool and required production access gate. No map, combat values, quests, minimap, live access settings or publication changes.

- `AddLevels` is a fixed server command, not a client-supplied amount. Add10 levels up to100; retain current XP below100 and clear it at100. Repeated uses remain capped.
- Keep current style, color, amplifier/paid entitlements and coins. Existing level/health synchronization refreshes the test profile. Newly eligible styles remain selectable through existing gates, not automatically equipped.
- Authorize a nonnil Studio player using server RunService, or the configured owner11499795799 only when CreatorType.User and CreatorId match. Client visibility is informational; the server rechecks every command. No public-testing flag remains in this unpublished candidate. Group-owned experiences do not inherit this individual owner's authority.
- First accepted test mutation freezes a sanitized deep copy of legitimate progress, and makes a separate temporary profile. Later commands retain that first baseline. Existing session autosave, departure and shutdown callers save the baseline, not test progression. Pre-session late-load release legitimately saves its own loaded data. Busy purchases block test mutation; receipt eligibility excludes test sessions.
- +10 button uses the existing scrollable test panel with98x44 targets and dynamic canvas rows. Native readability, physical touch and input activation have not been rerun.

The earlier public friend-test behavior was intentional historically. Restricting the candidate does not modify the already published preview. Any future public test-mode design must keep production authority and test progression isolated; this batch does not introduce one.

## Reproduction and verification

Before edits: actual original Access module admitted an ordinary live player; the new UI regression failed at missing +10. `python tests/developer_tools.py --baseline` also reproduces both original authorization and missing-command failures from4e37a44.

- `python tests/developer_tools.py --negative-controls`:94 actual Access/dev/Profiles.Sanitize assertions; source-only baseline-save and visibility contracts;4 controls for public access, missing cap, recaptured baseline and aliasing.
- `python tests/developer_tools_ui.py --negative-controls`:61 assertions using actual button-list/visibility code with synthetic UI geometry/events;3 controls for missing command, clipped canvas and truthy nonboolean access.
- `python tests/verify_local.py --build`:25 pure/synthetic suites,64 mocked-service suites,57 production script compiles, exact-source candidate audit and every disposable fixture build pass.
- Initial full run exposed a missing RunService mock in the old notification test. Updated that isolated mock, then reran the whole suite successfully.
- Independent review cleared the scoped change after correcting the test save-call counting error; independently reran94 developer assertions/4 controls,61 UI assertions/3 controls and whitespace checks. No native Studio, real network, live DataStore, purchase or real-device proof. No disposable programs/tabs were opened; command processes completed.

## Remaining work

Use an isolated disposable local fixture to verify actual button activation, scroll reachability and state feedback on keyboard/touch layouts. Live save isolation still needs expressly authorized test-environment validation; synthetic tests are not a release approval. Minimap remains a separate task. Preserve the current map before any redesign.

The supplied dodge reference could not be visually inspected: it resolves to a video filename, and the supported Windows transfer failed applying metadata (os.setxattr unavailable). No effect was removed based on a guess. Obtain the correct readable attachment before that image-dependent edit.
