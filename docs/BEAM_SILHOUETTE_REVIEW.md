# Regular beam silhouette candidate

## Intent and scope

Refine the existing sustained beam rather than add another effect system. Nearby regular beams retain a saturated semantic-color body, a thinner tinted-hot spine, interrupted travelling collars, a smaller emitter and a shallow terminal energy lens with backward-directed flare spokes. The termination lens is NOT evidence of a confirmed hit: the renderer has endpoint geometry, not authoritative damage confirmation. No new Client hook or hit burst is claimed.

All reduced-effects and far-distance core formulas remain unchanged. Same five-part regular core reservation/four-part reduced or far core, ring/strand/spark counts, 512-part cap, pooling, cleanup and caller animation cadence. No assets, emitters, lights, camera effects, physical queries, gameplay, level scaling, damage or server edits. Paid/custom colors are retained; coastal gold is not forced on other tints.

The regular envelope changes from1.65 to1.35 radius with a darkened semantic tint; the hot spine narrows from.28 to.10 radius. Wide regular shell/body/lens/emitter surfaces now use non-emissive SmoothPlastic; the thin spine and fine decorations remain Neon. Every draw sets Material explicitly so pooled reuse and regular-to-reduced/far transitions cannot retain the wrong material. A shallow lens replaces the endpoint sphere, the emitter shrinks, and ten existing segments per collar leave gaps. These are authored visual changes, not measured GPU/overdraw improvements. Native rendering decides whether they look better.

## References actually consulted

- `roblox-vfx/SKILL.md` selected-use policy and `LOCAL.md`: preserve server-authoritative systems, use original local work, no asset harvesting/upload or upstream orchestration.
- Vault targeted query `beam core impact readability`.
- `vault/fwjelaa/fwjelaa vault/07 Lighting VFX and Audio/Projectile VFX - Muzzle, Travel and Impact.md`, sections1–3: distinct emitter/body/termination hierarchy. Projectile hit timing is not transferred to this sustained endpoint renderer.
- `vault/fwjelaa/fwjelaa vault/07 Lighting VFX and Audio/VFX Readability and Value - Lessons from Blind Reviews.md`, sections1–5: narrow hot core, saturated body, less repetitive clutter, avoid broad character-obscuring washes. Recommendations are art guidance, not verified results for this game.

## Local checks

- `python tests/beam_silhouette.py --negative-controls`:695 actual BeamVisuals/BeamStyle assertions +seven controls. Three levels and three tints; core/lens/spoke geometry, semantic tint, count, reduced/far preservation, culling and terminal cleanup. Includes same-rig and cross-rig material reset plus .01/.1/2-stud lens bounds. Vector math is real in the fixture, CFrame orientation/Roblox drawing are mocked. Existing composed fixture setup is read as an AST literal, not executed/imported.
- `python tests/beam_pool_composition.py --negative-controls`:117,904 actual manager/visual/style composition checks +seven controls; peak512 allocated,512 destroyed. This is resource/lifecycle evidence, not native FPS or GPU proof.
- BeamVisuals Luau compilation passes.

Source SHA256: `e558aa5980dd24ae4e8b70180f876c54ce30cbf4cdee9c7dda6081bc75f4780b`.

## Native feedback used for refinement

Viewed parent-captured `build/beam-art-before.jpg` and `build/beam-art-after.jpg` for the first geometry-only candidate (0907ca01). Difference was modest: the broad emissive body still washed the thin core/lens hierarchy toward white. This was not called a major upgrade. Parent's `build/visual-streaming-and-bloom.json` reports an empty BloomEffect list; no claim is made that a configured BloomEffect caused the wash. Material hierarchy was refined locally in response, without touching global Lighting. New material candidate still needs the matching native comparison.

## Native acceptance pending

Compare low/mid/high levels from side and along-axis views against light and dark backgrounds; include custom purple/green tints and24 attackers. Confirm endpoint lens does not read as guaranteed damage or hide targets. Reduced/far retain prior rendering but still need native transition checks. Existing historical benchmark timings do not transfer automatically to changed visuals. No Studio or live service was operated by this worker.

## Final native sample (November13)

Coordinator compared the actual final renderer against the prior look, using a disposable cosmetic-only local probe: gold side and along-axis, custom blue, and reduced mode. The broad white wash is reduced; the tinted body, narrow hot spine and endpoint structure read separately in those captures. No attack remote or health mutation was used; the probe cleaned its rig/module and reported pool0/0. These samples do not clear the remaining low/mid/high-level, multiple-background,24-attacker, physical-phone or native GPU/overdraw gates. Historical timings do not cover this changed material look. [Evidence](../tests/evidence/visual-lock-checkpoint-2026-11-13.json).
