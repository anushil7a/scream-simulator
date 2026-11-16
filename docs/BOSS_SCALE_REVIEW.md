# Ground-aligned larger boss presentation

November 16; isolated from b2d6cc1. Read the actual vault `45 Procedural Blender Assets/Matching a Concept Sheet - Boss Creature Case Study.md` before editing: preserve silhouette/main mass, separate rendering from combat geometry, and keep changes individually reviewable. Existing five authored references and geometry from BOSS_FIDELITY_REVIEW remain unchanged.

Client-only adoption of the coordinated Catalog `scale=1.4` and `aimHeight=7` contract:
- Normal streamed BossVisuals resolves ground as Core.Position minus the catalog aim height, rather than the old hardcoded five studs.
- Controller passes scale through its cancellable build and rebuilds if the same streamed source changes scale or ground center.
- BossAppearance applies a uniform factor to source-local primitive sizes/positions and triangle dimensions/positions. Ground world coordinates are never scaled. Triangle decomposition happens in original asset coordinates before transformation, avoiding floating-point ties selecting different wedge splits at different elevations/scales. Thin wedge thickness remains .015 to avoid broader seams.
- Public Build keeps its original five arguments and accepts optional sixth `visualScale`; omitted/invalid values default to1 and finite values clamp1..2. Old catalog entries without fields retain scale1/aimHeight5. GeometryReady/part count remain; new `VisualScale` diagnostic records applied factor.

No asset vertices, signatures, colors, materials, mesh count, appearance parts, animations or glow were added. Counts remain Metronome274, Golem291, Ignis269, Leviathan435, Conductor417 under450, single-nearest appearance,32-part construction batches. No boss HP UI, wayfinding, server hitbox, attack, reward or telegraph changes in this track. Server gameplay and themed ground tells are owned by the coordinated combat track.

Tests: actual renderer/controller execution with vector/instance doubles passes40,219 assertions plus four negative controls (lost primitive scaling, lost surface-position scaling, hardcoded ground offset, omitted controller scale). Checks cover all five models at ground heights0/16/32/64, count/signature/material/physics preservation, exact relative coordinates and wedge bases, bounded inputs and replacement cancellation. Existing service/callback172 checks pass. Full `verify_local.py --build` passes26 pure/synthetic +148 mocked suites, production compilation and guarded disposable builds.

Integration requires the combat track's Catalog scale/aimHeight changes to activate1.4 in the normal game. Direct older visual harness calls intentionally remain scale1 unless passed sixth argument1.4. Native silhouette, raised aim/proximity prompt placement, wedge seams and target readability still require Studio review. No native/phone performance claim, Studio UI, upload, publication or push.
