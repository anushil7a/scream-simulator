# Explicit session signal cleanup

Base: `7ae5149168f0671cfa63c35b3b0b05572d14c3fe`. Astra identified an indirect retention path, not a demonstrated native leak: an in-flight voice request retains Player, whose registered CharacterAdded/CharacterRemoving handlers close over the session. If Player destruction is disabled or delayed, those handlers can retain the profile despite the worker having no direct session local.

## Reproduction and correction

Actual join registration plus actual leaving/shutdown code reproduced two callbacks still registered on a deliberately retained mock Player after the session was detached. This proves the modeled reference edges, not native garbage-collector behavior.

Bootstrap now stores both RBXScriptConnection handles on the owning session. An idempotent helper clears the stored handles and disconnects both before departure/shutdown detaches the session or starts any save yield. Cleanup also applies to temporary/read-only sessions. Saves, baseline selection, pending-save accounting, identity fencing and normal character behavior are unchanged. Completion of an old save does not disconnect a replacement session.

Disconnecting a signal does not cancel a callback that has already started. The existing post-WaitForChild session/player/character guards remain; a running spawn callback can retain its session while waiting for Humanoid (existing ten-second timeout). Save callbacks intentionally retain data until completion. Combat-credit entries also deliberately retain `rewardSession` until their normal pruning, reset or KO consumption; that separate attribution path is unchanged. Other engine/service references may exist. The eight-call bound and held-slot policy remain, and this change does not establish full profile or Player collectability, bounded native memory, or zero leaks.

## Separate readiness documentation audit

Corrected obsolete public test-tools instructions to the actual configured owner/user-owned-experience or Studio authorization and frozen-baseline behavior. Clarified that ordinary Studio is not a persistence sandbox. Reconciled current source pointers and excluded historical traffic/destruction checks without editing maps; map development remains paused. Added the two additive combat tasks to README and marked old verification counts in IMPLEMENTATION_STATUS as historical, pointing current work to ROADMAP and draft PR evidence. No rollout, settings or gameplay change accompanies these copy corrections.

## Verification

- **22 focused lifecycle assertions and four negative controls**, independently rerun. Actual join registration, departure and shutdown code with retained mock Player signals verifies both handles removed before save yields, temporary/read-only cleanup, partial registrations, duplicate cleanup, replacement sessions after old save completion, normal respawn and already-running stale callback guards. Controls omit each signal Disconnect and each leave/shutdown cleanup call and fail intended behavior assertions.
- Existing respawn13, departure23, shutdown11, shutdown-race34 and unchanged profile-recovery83 checks pass. Four lifecycle fixtures were adapted to include the actual new helper or registration syntax; original assertions remain.
- Final aggregate: **25 pure/synthetic suites,85 mocked suites,60 production compiles and all candidate/disposable builds pass**. Historical7ae5149 reference-edge reproduction rerun separately. [Exact source/artifact evidence](../tests/evidence/session-connections-2026-11-11.json).

No native memory/GC or service/network claims. Mocked signal registration/disconnection establishes this reference-path cleanup, not actual Roblox collection. No apps, live stores, publication or map source edits.
