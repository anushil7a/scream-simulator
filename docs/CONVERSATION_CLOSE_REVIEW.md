# Dialogue close survives request saturation

Base: `c1a0673f188c831d2c7110794e0ebf243a11bd1c`. This is a conditional recovery fix, not a claim that ordinary play was observed saturating the request window.

## Reproduced consequence

The actual client close helper hides the NPC panel and sends EndConversation once. Previously, the actual server dispatcher could discard it after 30 ordinary requests in one second. The existing server conversation then continued reserving the NPC and blocking beam capture while the player remained within 14 studs, until its 20-second deadline or other cleanup. A synchronous actual-helper/dispatcher fixture reproduces the dropped close against the pinned base. Character geometry, voice eligibility and transport are mocked; no native incident is claimed.

## Minimal correction

Only nil EndConversation runs before the ordinary quota, and only an existing session conversation invokes the existing close helper. The helper clears the sender's session link and releases the NPC only when that sender owns it. Stale links cannot clear another player's reservation. Duplicate idle closes do not invoke cleanup, emit output or mutate quota. Malformed arguments retain ordinary admission and cannot close.

This path does no scan, allocation, parsing, yield, broadcast, reward or purchase. Request count/window and existing nextTalk, legacy nextCast and sustained nextStart values are retained. Talk, attack starts and purchases remain behind the original quota; no additional readiness or fresh action is granted. Client, maps, saves and world code are unchanged.

The existing nil protocol still means close the sender's current conversation. A delayed old close can therefore close a newer conversation belonging to the same sender, as before. This change does not introduce a conversation generation or claim a new ordering guarantee.

## Checks and independent review

- `python tests/conversation_stop_rate_limit.py --baseline`: intended historical failure reproduced.
- `python tests/conversation_stop_rate_limit.py --negative-controls`: 18 assertions and five exact negative controls independently passed. Controls remove the bypass, nil validation, idle skip, owner check, or ordinary quota. Each fails its intended assertion rather than a syntax error.
- Actual client close, full server dispatcher, server close helper and canCapture execute. Talk/Begin/vendor bodies are counters proving dispatcher admission only, not full action behavior. Preserved cooldown fields are asserted, not reimplemented.
- Retained conversation ownership 7, client dialogue 29 and voice-stop 89 checks pass. Fresh `python tests/verify_local.py --build` passes 25 pure/synthetic suites, 105 mocked-service suites, 63 production compiles and all local builds.
- No Studio/app launch, native network/input test, live DataStore, purchase, map edit or publication. See [exact hashes/evidence](../tests/evidence/conversation-close-2026-11-12.json).

## References and remaining gates

Consulted vault `03 Architecture and Networking/Remote Abuse Patterns and Rate Limiting in Practice.md` (order of operations) and `Rate Limiting and Abuse Prevention.md` (cooldown versus admission and bounded work). The narrow exception is constant-cost owner-scoped cleanup, not a general exemption from those budgets.

Native transport/ordinary-input saturation remains unverified. Full-warning keyboard/gamepad access and physical touch remain unrun: there are no explicit application paging bindings, but engine GUI navigation may provide access, so synthetic missing bindings alone do not prove native unreachability. Do not add speculative conflicting navigation without native evidence. Map approval, exact test-place isolation, mixed-writer rollout and other release gates remain.

Delivery: local checkpoint only, while the owner is being asked to confirm the existing GitHub draft push. Two earlier local checkpoints remain preserved. Last verified remote 0004c77; no push attempted in this task.
