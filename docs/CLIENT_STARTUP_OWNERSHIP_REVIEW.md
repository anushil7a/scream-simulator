# Main-client interrupted startup ownership

## Concrete reproduction

The actual Client script at 76ded0b was paused independently at its 36 legacy / 44 automatic-voice startup dependency boundaries. Delivering Destroying, directly unparenting the script, or detaching its ancestor and then resuming initialization could continue construction, remote Sync or frame subscription, or error on the way. All 240 terminal historical cases reproduce a consequence; 80 valid in-DataModel reparent controls still complete. This is mocked coroutine evidence, not an observed native leak.

A targeted vault ownership inventory through EOF supported a bounded correction rather than a new global lifecycle framework.

## Correction and ownership boundary

- Register one terminal, idempotent owner before the first dependency operation. Check liveness after each existing startup wait/require and before final Sync, preserving load order and direct-lookup versus waiting semantics.
- Retire registered resources in reverse order, attempt each cleanup independently, and immediately dispose a resource returned after cancellation. Cleanup failure emits a generic diagnostic without exposing an exception payload.
- Disconnect tracked external signals and terminal-guard their retained callbacks and global button-activation callbacks. Actual SustainedControls cancellation retains its one owned SustainedStop; teardown is not permission for new Sync/Begin/Pulse/UI work.
- Register camera/touch restoration before mutation. Restore only values still equal to this client's last write, preserving differing replacement values.
- Do not Clear shared ShopUI/effect/beam state merely because its module was loaded. Track first actual use; invalidate terminal menu callbacks separately from the single owned Shop Clear. Destroy the owned beam manager before clearing its used pool.
- Keep runtime behavior otherwise unchanged: no permanent AncestryChanged policy, no ancestry polling in every frame/callback, no camera-generation framework, and no new third-party dependency.

## Verification

- Actual whole Client source: 320 dependency-boundary scenarios, pinned expected boundary identities, 18 ownership/late-constructor/used-singleton/actual Controls cancellation cases and twelve explicit negative controls, including exact touch-write restoration and differing replacement values.
- Historical 76ded0b: 320 matching cases, including 240 conditional continuation failures and 80 valid reparent controls.
- The whole-script harness uses actual SustainedControls, but other dependencies, engine Instances, signals, scheduling and constructors are doubles. It does not simulate normal gameplay frames.
- Retained focused checks include beam integration 91/18 controls, voice notices 1,217/2, modal 120/12, panel 38/6, camera 6/2, menu 5, client connections 6 and microphone notice 402/4 plus three contracts.
- Independent review caught a missing legacy-effects use marker and duplicate terminal Shop Clear. Both were fixed and retained actual-callback cases added.
- Astra independently reran 320 current and 320 historical boundary cases, 18 ownership cases and all twelve controls, checked exact source/builder diff identities and generated correspondence, and passed all 17 builder contracts plus an extra captured-guard mutation.
- Final full local integration passed: 25 pure/synthetic suites, 115 mocked suites, 63 production compiles, all disposable builds; 225 commands in 37.08 seconds. All 311 selected inputs were unchanged before/after and rechecked afterward. Earlier attempts correctly stopped at obsolete source-fragment/builder adapters; the final adapters preserve the terminal guard.
- [Exact evidence](../tests/evidence/client-startup-2026-11-12.json). Full local logs remain unredacted and unshared; this is not CI or native execution.

Commands (negative controls are separate from the default aggregate):

    python tests/client_startup_lifecycle.py --negative-controls
    python tests/client_startup_lifecycle.py --baseline
    python tests/client_startup_builder.py
    python tests/beam_screen_integration.py --negative-controls
    python tests/voice_notice_lifecycle.py --negative-controls
    python tests/shop_modal_lifecycle.py --negative-controls
    python tests/panel_action_lifecycle.py --negative-controls
    python tests/third_person.py --negative-controls
    python tests/microphone_notice.py --negative-controls
    python tests/verify_local.py --build --report build/client-startup-final-3-2026-11-12.json

## Explicit limits and next native check

This hardens initialization that actually resumes after an observed terminal event or detached-ancestry checkpoint. It does not guarantee cleanup of a permanently terminated thread or arbitrary initialization exception. Roblox documents that an own-script Destroying callback can be skipped under Deferred signals and manual Studio deletion can unparent instead of destroy. A detach-and-reattach interval entirely between checks is not detected; no broader post-startup detachment behavior is added.

Camera/touch restoration is best effort. Differing replacement values are protected; same-valued overlapping clients and shared singleton pools after actual use are not isolated. The design retains the project's single-active-Client assumption.

Standalone builders resolve bundled dependencies synchronously and therefore cannot prove production wait interruption. They retain the real in-DataModel LocalScript requirement, not a command-context bypass. Mocked tests do not prove native GC, engine scheduling, actual UI/voice, performance or phone behavior.

When Studio sign-in is available, use a disposable local-only place with a real LocalScript, record SignalBehavior and source identity, then exercise each actual dependency interruption, normal startup, terminal active-attack stop, camera/touch restoration and UI teardown. Do not change the live game or rely on this checkpoint as release approval.

Both existing release gates remain BLOCKED: unverified older quest-writer fleet and enabled temporary tester tools. No native app, live service, Roblox publication, credential or security-setting action occurred in this task.

## References used

- vault/fwjelaa/fwjelaa vault/81 Verified Roblox Resources/knowledge/gameplay-systems/round-lifecycle-and-cleanup.md: entity-scoped ownership and deterministic transition/callback checks.
- vault/fwjelaa/fwjelaa vault/56 Field Notes/ipairs Stops at the First nil - Cleanup Tables That Leak.md: dense owned-resource cleanup lists.
- [Instance.Destroying](https://create.roblox.com/docs/reference/engine/classes/Instance#Destroying) and [deferred engine events](https://create.roblox.com/docs/scripting/events/deferred), checked November 12, 2026.
