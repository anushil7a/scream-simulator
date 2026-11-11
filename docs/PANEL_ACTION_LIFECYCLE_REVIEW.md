# Rendered panel action lifecycle

## Reproduced risk and scope

Explicitly invoking retained Style callbacks after the actual menu X-close still submitted actions. With the actual server helper/branch in a disposable mock, MicroSpeaker spent 1,500 earned coins (2,000 to 500) and equipped the amplifier; BaseColor replaced a grandfathered Blue selection with Gold. This establishes the conditional callback consequence, not native Roblox event-queue reachability, a reported user incident or a live transaction.

The actual AbandonQuest branch and stopQuest/QuestLifecycle.Clear also reset a newer practice task (2/3) when an old menu callback runs. An old NPC AcceptQuest choice similarly clears the newer task and starts its old task. NPC choices belong to a separate replaceable conversation. Merely guarding tab selection does not invalidate those card callbacks. Server claim completion/discovery/deduplication rules remain intact; this is not a server authorization bypass.

## Narrow client correction

- Each actual menu render captures its existing renderRevision. A render-local button wrapper checks that revision, modal visibility and client lifetime before forwarding callback arguments and return values. This covers that render's cards and the button factory passed into ShopUI; it does not replace the global button helper or HUD gameplay controls.
- closeMenu already increments renderRevision and invalidates the render key. Replacement renders increment the revision before building new cards. Old cards therefore remain inert even after a later reopen; current visible cards retain their existing commands.
- NPC choices capture an independent conversationRevision. Every close and replacement advances it. The choice helper checks that revision, conversation visibility and client lifetime before executing the original callback, including vendor and quest actions.
- Revision locals are initialized before their controls are registered. Callback wrappers do not yield and do not change server authorization, prices, save policy, quests, equipment or reward semantics.

## Evidence and limits

- Independently reviewed and rerun: 38 actual registered card/tab/choice callback assertions and six separate lifetime/visibility/generation negative controls. Historical edc9442 probes separately reproduce menu reset, NPC reset, earned-coin spend and legacy-color replacement. Current actions, claims, repeated calls, hidden/closed/replaced/reopened panels, client destruction and argument/return forwarding are covered.
- The panel fixture uses actual closeMenu/closeConversation helpers, a mocked menu key/snapshots and synthetic GUI/session state. Actual X/B/same-tab registration is covered separately by retained shop_modal_lifecycle (120 assertions/twelve controls), not claimed from the new helper-level checks. Settings invokes the actual Recalibrate callback with effect counters, not real microphone/controller integration.
- The old NPC renderer fixture needed its newly introduced revision and client lifetime initialized; its 97 assertions/four controls remain. Retained microphone_notice 402/four controls/three contracts and existing Style/shop tests remain covered.
- Initial full integration passed all 25 pure/synthetic and 97 mocked suites plus 60 compiles, then correctly stopped because onboarding-builder instrumentation matched both button signatures. The builder now anchors only the unindented global constructor, preserving the render-local guard in captured callbacks. This is fixture compatibility, not a production workaround. Final full 25 pure/synthetic and 97 mocked suites, 60 production compiles and all builds pass; exact hashes are recorded in the checkpoint evidence.
- Explicit commands: python tests/panel_action_lifecycle.py --negative-controls; python tests/panel_action_lifecycle.py --baseline; python tests/quest_dialogue_restart.py --negative-controls; python tests/verify_local.py --build. The aggregate default does not run opt-in mutation controls.
- [Exact checkpoint evidence](../tests/evidence/panel-action-lifecycle-2026-11-11.json).

No apps, native input, live APIs/stores, purchases, map changes or publication were used. Tests invoke retained callbacks deliberately; they do not measure how often Roblox queues such events. No global callback cancellation, server rollback or protection against a malicious client is claimed. The change scopes rendered card and conversation actions, not every HUD button or possible third-party GUI mutation.
