# Cosmetic dodge effect review - November 11, 2026

Base `078dbb1ddac9e4e07a05d3c643a5994334fc7e96`, fetched and clean. The recovered reference shows a yellow world-space box near dodge onset, disappearing before the roll finishes. Source inspection and an actual-branch reproduction identify the client cosmetic: an anchored Neon Part sized 2x3x2 at the event position, transparency0.3, tweening to5x1x5/transparency1 over0.35 seconds. Default aura makes it yellow. This is not the server Blockcast collision query.

## Narrow change

Only one production line changes: Dodge still requests `playGameplayCue("Dodge",pos)` and returns, but creates no cosmetic Part/tween. All colors lose the same box. No replacement flash or new effect was added.

Server roll movement, collision queries, eligibility,0.6-second duration, cooldown/protection attributes, sustained-attack cancellation and RunAnimation stay byte-for-byte unchanged. Existing range/missing-root guards remain. The shared fxPart helper remains for Break chips; other beam, hit and end effects retain their paths.

The cue hook and audio modules are preserved, not newly configured or audibly validated. Dodge AssetId is still empty. A configured spatial cue may create its own invisible audio emitter; “no box” does not mean no audio-emitter allocation.

## Verification

- Before patch, actual Dodge branch reproduced one cosmetic block, one tween and one cue request. Full callback baseline test against078dbb1 fails “Dodge allocated cosmetic Part.”
- `python tests/dodge_effect.py --negative-controls --scope-check`:127 actual Effect callback assertions in deterministic mocks;25 protected server/animation/config/audio source-equality checks against the base;4 controls restore the box, remove the cue, remove early return or remove the180-stud gate.
- Default test runs only127 behavioral assertions. Equality checks are opt-in one-time scope evidence, not a permanent prohibition on future authorized changes.
- Tests cover all aura/direct colors, reduced effects, missing root/character, exact180 range boundary, Break's six-chip lifecycle/cue, ordinary and sustained effects. No native rendering, physics or audio claim.
- Existing roll-cleanup10, animation-lifecycle32+14, gameplay audio26+6 source hooks and pooled-effect cleanup9 checks pass. Full25 pure/synthetic suites,67 mocked suites,57 production compiles and every candidate/disposable build pass.
- Independent review cleared the one-line production change, reran focused assertions/controls and confirmed every non-Client production file matches the base.

## Limits and cleanup

Native visual comparison after the edit, physical input, real audio and network behavior were not rerun. No live saves, audio asset configuration, map changes or Roblox publication. No apps/tabs were opened in this batch. Studio remains closed; the previous minimized Windows “Pick an app” dialog remains inaccessible to supported restore/close controls and was not blindly closed.

Next: inspect the disappearance during a later authorized native playtest, then continue the remaining minimap, Beams/style, audio and gameplay backlog in separate reviewed batches.
