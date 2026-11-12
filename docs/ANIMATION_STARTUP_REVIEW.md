# Player animation startup lifetime review

## Reproduction and bounded correction

A targeted vault-guided review found that RunAnimation loaded Shared and Config before registering its terminal listener. The whole historical script was paused independently during Shared lookup, Config lookup and require; after a mocked Destroying event and resumption, initialization continued into player, frame and character subscriptions. This is a conditional coroutine reproduction, not an observed native player-session leak.

The correction registers the terminal flag before any dependency yield and checks it immediately after each of those three operations. Ordinary dependency order, animation poses, default Animator composition, character watching and existing final cleanup remain unchanged. The standalone debug harness accepts only the exact new RunAnimation binding and preserves the terminal guard after substituting its bundled Config.

## Validation

- Actual whole-script tests: 15 startup assertions, 10 harness resolver contracts and four explicit controls (each dependency fence and the early terminal hook). The pinned 927ee47 baseline fails all three interrupted stages.
- Existing 32 player and 14 resident animation lifecycle checks pass.
- Astra independently reviewed the exact source/builder diff, confirmed the unchanged normal animation body, reran startup/controls/baseline and resolver cases. Review caught a test-only variable-shadowing error; the final test preserves valid input for wrong-file and missing-Config rejection cases.
- Final full integration: 25 pure/synthetic suites, 113 mocked suites, 63 production compiles and all disposable builds passed; 223 child commands in 25.83 seconds. 309 selected inputs match before/after and were rechecked after the run. Optional controls ran separately, not implicitly in the aggregate.
- [Exact evidence](../tests/evidence/animation-startup-2026-11-12.json). The full local log is unredacted and not committed. Both release gates remain BLOCKED. No native app was opened; the existing Studio sign-in window is left available.

## Important scope limits

The tests explicitly deliver Destroying and then resume initialization. They do not prove that Roblox will resume a destroyed LocalScript, that its own callback will run in every signal mode, or that Studio manual deletion uses Destroy(). Roblox documents that an own-script Destroying callback can be skipped with Deferred signals and that manual Studio deletion can instead unparent an instance. The change is deliberately not a broader lifetime-manager rewrite, a deferred/unparent guarantee, a native cleanup result, or a performance improvement claim.

A separate read-only main-client prefix probe found a similar conditional construction-after-teardown risk. No main-client change is included here; broader initialization ownership requires separate review and native lifetime validation.

## References actually used

- vault/fwjelaa/fwjelaa vault/56 Field Notes/ipairs Stops at the First nil - Cleanup Tables That Leak.md: inspect real cleanup ownership and optional resources rather than assuming completion.
- vault/fwjelaa/fwjelaa vault/81 Verified Roblox Resources/knowledge/gameplay-systems/round-lifecycle-and-cleanup.md: entity-scoped lifecycle, scheduled callbacks and deterministic transition tests.
- [Roblox Instance.Destroying](https://create.roblox.com/docs/reference/engine/classes/Instance#Destroying) and [deferred engine events](https://create.roblox.com/docs/scripting/events/deferred), checked November 12, 2026: native signal and deletion semantics above.
