# Native PvP reward validation

## November 22 two-client Action and notice check

- Source `aaa7268aa280dea02eeabb26942d4e721fb67c58`, guarded local Studio place `CityKONoticeTransportReview.rbxl`, one local server and two local clients. The fixture staged level-1 avatars in Coastal Arena with an eight-stud clear beam path, used synthetic ready/focus and sent standard beam actions through `ScreamRemotes.Action`. The server determined damage, credit, protection, ejection and the reward. Both local clients displayed the production notification view. The first attempt acknowledged a cast but never damaged the defender while the mic controller still ran alongside synthetic input. The scoped rerun disconnected microphone input in the disposable clients before injecting readiness and beam power.
- First KO: defender began at 100 HP, reached an observed 3 HP, then returned to the safe hub with 100 HP and spawn protection. The attacker received and displayed **KO · +96 XP · +20 coins** and went from level 1, 0 XP, 0 coins to level 2, 25 XP, 20 coins. The defender received and displayed **Knocked out · back at the safe hub**.
- Repeat KO: after natural protection and normal attacks on the same defender within the reward cooldown, the defender reached an observed 1 HP, then returned to the hub at 100 HP under protection. The attacker received and displayed **KO · no reward awarded**. Level, XP and coins did not change. The defender again displayed the hub notice. Neither client received the other player's KO notice. Each fight used two acknowledged casts and took about 12.1 seconds after staging, with 51 and 52 pulse requests respectively.
- Local fixture source is under `build/ko_transport/`. Studio version `0.748.0.7481526` ran the guarded test with `StudioTestService:ExecuteMultiplayerTestAsync(2, "CityKONoticeTransportReview")`. The local server and both clients were stopped, and the test editor was closed. The retained runner log excerpt is truncated, so the full round results above are from the native tool return.
- This verifies native local RemoteEvent delivery, server outcomes and visible toasts for a staged pair. The check did not timestamp notice arrival against intermediate health. Actual microphone onset, the normal pulse scheduler, physical input, cross-place transfer, a representative multiplayer soak and actual saves remain unverified.

## Earlier resolver fixture

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

The minimum remaining core-input check is two people using two voice-eligible accounts/devices (desktop plus physical phone preferred), with microphones/headphones and an explicitly authorized isolated environment containing the exact candidate. Start with Beams OFF, opt in, then check comfortable speech and quiet-stop without calibration, the four-second cap and five-second cooldown. Turn beams OFF mid-attack and confirm the other player can still hear ordinary proximity conversation. Test mute, focus, respawn and deliberate rearm. Real persistence needs separate authorization and isolated keys. Measure native performance separately from this combat test.

## Actual November 10 results and review

Roblox Studio `0.747.0.7471481`, unpublished PlaceId 0, one local server and two local clients: final baseline **14 passed**, internal `repeat-limit-disabled` control **failed at Repeat KO reward farm after 13 checks with two mutation calls**, restored baseline **14 passed**. Runtime source stamp `db68cfcd39dd112c54fe19952861515b01b9224cd823fdedb64a139266e7fafb` matches the final generated fixture; generated artifact SHA-256 `5f8bff0788d819d561cc934884da26ed8b05c60094e8517af6587f7a4dc018b9`. See [filtered evidence](../tests/evidence/pvp-readiness-2026-11-10.json). The assertions execute rapidly with injected eligibility, not elapsed real-player combat timing.

`python tests/verify_local.py --build` passed all 25 pure/synthetic and 59 mocked-service suites, compiled 57 production scripts, checked all 57 candidate sources and rebuilt every review fixture. The build tool's generic native-untested statement describes its own build-only scope; only the runtime cases explicitly recorded here were subsequently exercised. `git diff --check` passed.

Separate implementing-agent self-review checked the test-only diff, existing local-place/temporary-profile/reentry guards, the mutation's actual invocation count, restoration after the protected body, the landed-KO assertion, and XP/coin/level invariants. No blocking issue found; this is self-review, not independent reviewer approval. Production source is unchanged. Do not infer comprehensive production correctness from these bounded checks.

All task-created local servers/clients were stopped and disposable editor changes saved locally before closing. Final window inventory contained only pre-existing Codex; no browser tabs were opened, unsaved work discarded, or unrelated processes terminated. No publication, audio configuration, purchases or live DataStore access occurred.
