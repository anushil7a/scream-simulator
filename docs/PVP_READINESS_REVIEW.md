# Native PvP reward validation

Started from clean local/fetched `44e310427a45667f2babaa21677e31c39b5f3d30`. The current server combat/reward path had mocked checks but the recorded two-client native pass predated current tuning. Reused the existing guarded `SustainedNativeFixture` rather than adding a new framework. No production behavior changed.

## Reproduced test weakness

The native repeat-KO check reduced its victim to one HP after ejection had cleared the damage ledger. That single finishing point can round XP to zero even with repeat suppression disabled, making unchanged XP/coins a false positive. A Luau CLI reproduction using the actual payout helpers, CombatCredit and progression formula confirmed one mutation call but zero reward with the old setup. With 99 prior credited damage plus the finishing point, the same disabled limiter paid 96 XP and 20 coins. This reproduces a test weakness, not a production reward exploit.

The fixture now seeds eligible credit for the second life just as it already did for the first, asserts the second KO actually landed/ejected/healed, and checks level as well as XP/coins for unwanted rewards. Its optional `repeat-limit-disabled` negative control patches Bootstrap's actual module table, counts calls and restores the function immediately after the protected test body. The server-only runner retains its local-place and temporary-profile guards. A preliminary Command Bar module mutation was inconclusive and is not accepted negative-control evidence; module-cache identity was not established there.

## Reproduce locally

Build with `python tests/verify_local.py --build`, open `build/SustainedNativeFixture.rbxl` locally, select Server & Clients with **2** clients, and wait for the existing first-beam/progression fixtures to finish. Never publish this file. In the **server** Command Bar:

```lua
local run = game.ServerStorage.RunSustainedPvp
print("PVP_BASELINE", run:Invoke())
print("PVP_NEGATIVE", run:Invoke("repeat-limit-disabled"))
print("PVP_RESTORED", run:Invoke())
```

Normal/restored runs must pass 14 checks; the negative run must fail specifically at `Repeat KO reward farm` after 13 completed checks and log two `repeatCalls`. A generic error or zero mutation calls is not a valid control. Stop all local server/clients afterward; save and close the disposable files.

## Scope and next gates

Native engine avatars, raycasts, arena/protection/dodge checks, health, KO ejection and reward helpers are exercised. Attack power, aim, anchored positions, eligibility timestamps and pre-KO damage credit are injected; the helper calls the adapter directly, bypassing client pulse scheduling/RemoteEvent transport. This is not real-voice input, physical dodge timing, internet latency, mixed-level balance, real saves or a representative multiplayer soak. The airborne arena test geometry is intentional isolation, not authored ground-cover validation.

The minimum remaining core-input check is two people using two voice-eligible accounts/devices (desktop plus physical phone preferred), with microphones/headphones and an explicitly authorized isolated environment containing the exact candidate. Verify calibrated speech and quiet-stop, four-second cap/ten-second cooldown, OFF mid-attack preserving audible proximity conversation, then mute/focus/respawn and deliberate rearm. Real persistence needs separate authorization and isolated keys/environment; no live DataStore access is needed or permitted for this fixture. Native performance sampling remains a separate useful offline task, not evidence supplied by this combat test.

## Actual November 10 results and review

Roblox Studio `0.747.0.7471481`, unpublished PlaceId 0, one local server and two local clients: final baseline **14 passed**, internal `repeat-limit-disabled` control **failed at Repeat KO reward farm after 13 checks with two mutation calls**, restored baseline **14 passed**. Runtime source stamp `db68cfcd39dd112c54fe19952861515b01b9224cd823fdedb64a139266e7fafb` matches the final generated fixture; generated artifact SHA-256 `5f8bff0788d819d561cc934884da26ed8b05c60094e8517af6587f7a4dc018b9`. See [filtered evidence](../tests/evidence/pvp-readiness-2026-11-10.json). The assertions execute rapidly with injected eligibility, not elapsed real-player combat timing.

`python tests/verify_local.py --build` passed all 25 pure/synthetic and 59 mocked-service suites, compiled 57 production scripts, checked all 57 candidate sources and rebuilt every review fixture. The build tool's generic native-untested statement describes its own build-only scope; only the runtime cases explicitly recorded here were subsequently exercised. `git diff --check` passed.

Separate implementing-agent self-review checked the test-only diff, existing local-place/temporary-profile/reentry guards, the mutation's actual invocation count, restoration after the protected body, the landed-KO assertion, and XP/coin/level invariants. No blocking issue found; this is self-review, not independent reviewer approval. Production source is unchanged. Do not infer comprehensive production correctness from these bounded checks.

All task-created local servers/clients were stopped and disposable editor changes saved locally before closing. Final window inventory contained only pre-existing Codex; no browser tabs were opened, unsaved work discarded, or unrelated processes terminated. No publication, audio configuration, purchases or live DataStore access occurred.
