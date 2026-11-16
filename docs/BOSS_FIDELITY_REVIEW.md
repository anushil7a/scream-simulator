# Five boss appearances: visible local candidate

November 16, 2026. Addresses the owner's screenshot of the cyan rectangular Metronome, not just a loose mesh export.

## Reference and process

Viewed actual vault BOSS-01 Whispering Metronome, BOSS-03 Decibel Golem, BOSS-04 Pyro-Tenor Ignis, BOSS-06 Leviathan Sub-Bass and approved BOSS-09 Eclipse Conductor images. Read `45 Procedural Blender Assets/Matching a Concept Sheet - Boss Creature Case Study.md`: silhouette first, continuous mass instead of disconnected primitive stacks, compare front silhouettes, keep visual geometry separate from hitboxes. User-requested encounter levels 10/30/50/70/95 retained.

`tools/bosses/fidelity.py` authors original geometry in Blender, saves `build/boss-fidelity/BossFidelity.blend`, renders each model plus front silhouettes and lineup, and exports the same vertices/material palette into `ReplicatedStorage/Shared/BossVisualData.luau`. Coarsened continuous surfaces preserve the large shapes; thin concave flame/blade panels use proper tessellation, not triangle fans crossing the silhouette. This is an original low-poly interpretation, not imported reference-image geometry.

- Metronome: tall tapering brass clock case, inset teal face, rounded brass/teal shoulders, exposed gears, pendulum, waveform panels, cyan sickle.
- Golem: squat stone armor, skull-like face, four ear-speaker cabinets, chest subwoofer, speaker forearms and fists.
- Ignis: narrow armored figure, split orange skirt, pipe shoulders, cyan crest/flames, tuning fork and microphone.
- Leviathan: continuous low-poly coil rising into a horizontal open toothed jaw, sonar throat rings, short forelimbs, fins and coral.
- Conductor: slender split coat, long trousers, gold lapels/fringe, horned crown and exactly six flared bells.

## Actually visible runtime path

`BossService` retains the original combat Core size/position (now invisible) and ring/telegraph rules. It no longer creates the wrong generic six-part figure. Center honors `spec.y or 0` for elevated map homes. World labels gain 260x96 space, still no enemy HP readout.

`BossVisuals.client.luau` discovers streamed `BossEncounters/<id>/Core` anchors every 0.5s. It builds one nearest appearance within 180 studs under local workspace `BossVisual_<id>`. `BossAppearance` maps primitive data directly and continuous Blender triangles to exact thin wedge pairs. No upload, asset ID, private configuration, network request, plugin, Mesh/Image API permission or template is needed. This path is automatically included in normal Rojo places. `StudioBossVisualHarness.luau` is additionally generated for disposable native inspection.

At most one visual is active. Construction yields every 32 parts and generation tokens cancel stale work on replacement, streaming removal, character loss or script destruction. Counts: Metronome261, Golem231, Ignis255, Leviathan450, Conductor444. These are still substantial local instance counts, not mobile-performance approval. Distant bosses are intentionally culled rather than replaced by the rejected cyan box. Source geometry is static; no per-frame animation or per-frame allocations added.

## Evidence and gaps

Actual renderer/controller mocked execution passes 6,264 assertions covering part/physics limits, triangle area preservation, orthonormal wedge bases, cancellation, repeated activation, nearest-only selection and stream-out/respawn/teardown cleanup. Existing boss mechanics tests remain; explicit elevated-anchor/invisible-proxy assertions added. All mechanics, levels, rewards, opt-in gates and health HUD policy remain unchanged.

Blender actual-geometry renders inspected, including lineup and silhouettes. Native Roblox surface orientation, lighting, text fit and real device enter-frame timing still need the separate native smoke pass. Thin wedge surfaces can show seams and differ in shading from Blender. These low-poly silhouettes are materially closer to references but do not reproduce painterly textures, organic sculpt detail, flame motion, coat cloth or rigged animation. Do not describe them as final reference parity or live/published art.

EditableMesh was investigated but deliberately not required: Roblox's official EditableMesh documentation states published-game APIs are disabled by default and need a security toggle; no such setting was changed. Source: https://create.roblox.com/docs/reference/engine/classes/EditableMesh .

Final local gate: 27 pure/synthetic suites, 151 mocked suites, production compilation and all disposable builds passed. No native execution by this worker. Native-ready marker is `GeometryReady=true` with `GeometryPartCount` on each local `BossVisual_<id>`.
