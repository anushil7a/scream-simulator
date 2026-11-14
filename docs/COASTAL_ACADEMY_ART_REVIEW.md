# Coastal academy art pass, November 13

## Intent and source use

The owner requested substantial visible map/model improvements rather than more technical-only work. The actual local-game baseline (`build/visual-spawn-before.jpg`) showed a sparse, flat courtyard, box crowns, plain façades and a guidance billboard over the avatar. This pass uses original Roblox geometry, not imported third-party art or asset IDs.

Targeted vault sources consulted:
- `fwjelaa/fwjelaa vault/06 World Building and Art/Zone and Biome Art Direction.md`, sections 1–3: a coherent silhouette/material/accent hierarchy, not unrelated zone colors.
- `fwjelaa/skills/make-map/research/04-stylized-and-level-design.md`, sections 3.2–3.4 (around lines 421–475): visible landmarks, route framing, quieter ground and restrained focal contrast.

These are reference principles, not permission to install tools or publish. No global lighting, live place, asset upload, audio or save changes.

## Implementation

`CompactCity.academyArt` creates exactly 304 static cosmetic Parts in one `CoastalAcademyArt` folder. They are anchored, noncolliding, nonquery, nontouch, shadowless and carry no gameplay attributes. There are no per-frame updates, emitters or lights. The constructor has a 350-piece ceiling.

- Eight layered original tree crowns and planter rims. Existing opaque solid tree crowns remain, so their collision does not become invisible.
- Five market façades with cornices, sills, pilasters and striped awnings, plus four articulated old-town façades.
- Twin raised tower crowns for a recognizable distant skyline.
- Slate/gold practice header and side framing, leaving the target face and standing-to-target shot corridor unobscured.
- Arena portal framing and dressing on the existing solid cover. Cover dressing stays within 0.08 studs of the existing solid silhouette; it is not new cover.
- Calm courtyard/promenade paving joints and a more coherent ground/cover value palette.
- The existing spawn guidance anchor moves 18 studs left and 5 studs back. Text, maximum distance and non-AlwaysOnTop behavior are retained; native readability is a separate acceptance step.

No Layout, World, original archive, target attributes, spawn, quest station, sports, trainer, PvP boundary or physical route was changed. Colors are presentation changes. The authoritative target's color/state remains untouched.

## Focused verification before native acceptance

- `python tests/coastal_art.py --negative-controls --baseline`: 1,854 real-constructor assertions, eight rejected mutations, and a pinned `dda67e3` original Part inventory fingerprint match. The fingerprint covers positions, dimensions, ownership parent names, anchored/collision/query/touch flags and attributes; it intentionally excludes colors and normalizes the specifically permitted nonphysical spawn-sign relocation.
- `python tests/compact_world.py --negative-controls`: 1,159 constructor checks, all 19 mutation controls and 48 static clearance/reachability targets.
- `python tests/compact_integration.py --negative-controls`: 122 assertions, 11 controls and retained source contract.
- `python tests/compact_guidance.py --negative-controls`: 81 assertions and four controls.
- Current CompactCity compiles. Raw byte diff: `build/coastal-art-review.diff`.

This is mocked geometry/source evidence, not native rendering, real pathfinding, device performance or player comprehension. The static reachability grid has the same 24,571 connected cells because no physical geometry changed. The extra 304 Parts have an actual rendering/replication cost; no speedup or negligible-cost claim is made. Native before/after inspection and independent review are pending at this document's creation. The parent will record their actual outcomes before the checkpoint.

## Native-driven refinement

The parent captured the first native spawn/practice/arena views. I inspected all three JPEGs: the inherited practice billboard still covered the yellow target, so that candidate was not accepted visually. The practice guide is now a fixed SurfaceGui on a transparent 0.2×4×36 anchor at the existing upper header (+X face), rather than a camera-facing billboard at target height. Meaning and distance remain unchanged. Its anchor geometry is explicitly checked then normalized only for the original-part fingerprint. A single tall, spawn-facing signal badge replaces the five tiny header bars, improving the side-on landmark silhouette with nine parts instead of many scattered props. Total art is304. Original solids and shot corridor remain unchanged.

Refinement diff: `build/coastal-art-refinement.diff`; full raw diff refreshed. New focused regression rejects moving the practice guide back over the target. Native text sizing, legibility and final framing must be evaluated again; no visual acceptance claimed from mocked geometry.

### Final sign legibility refinement

The next native practice view cleared the target but made the single-line header too small. Both practice and arena now use attached outward-facing SurfaceGui headers with600×100 canvases and36px text in two explicit lines. Practice reads “MIC PRACTICE / Aim west, speak, then go quiet”; arena reads “BEAM ARENA / PVP INSIDE RED LINES.” The arena anchor is(-122.6,13.5,50), its3×39 face aligned to the existing west-facing fascia, above the entrance. Its old billboard could cover the coach/portal. Both deliberate nonphysical anchor changes are explicitly checked before fingerprint normalization; the authoritative geometry fingerprint still matches the pinned baseline. The static reachability target remains the actual walkable gate approach(-137,3,50), not the elevated sign anchor. Final native fit is still to be checked by the parent.

## Final native inspection (November13)

Coordinator inspected `visual-practice-approved.jpg` and `visual-arena-header.jpg`: headers are readable at the sampled approach distances; the practice target, coach and gate are unobscured. Both actual labels report TextFits=true. The farther arena capture was outside the unchanged65-stud sign distance; closer capture shows both lines without changing source. After moving the actual avatar near the arena, surrounding facades streamed in and the earlier camera-only floating-cornice appearance disappeared. No global streaming policy was changed. This remains an early coherent coastal art pass with broad open foreground, not a finished dense city or measured first-player navigation result. Original archive is untouched. See [evidence](../tests/evidence/visual-lock-checkpoint-2026-11-13.json).

## Foreground & promenade dressing pass (November 13, 309 -> 347 parts)

Starting from the 309-part `CoastalAcademyArt` baseline (which includes the 18 `Academy*` overhead landmark parts added after the initial 304-part pass and the retirement of the 13 `Practice*` / `StandLine` parts), `CompactCity.academyArt` adds 38 static cosmetic `Foreground*` Parts inside `CoastalAcademyArt`, bringing the total to **347** parts (strictly `<= 348` and under the 350-piece ceiling):

- **Spawn-to-Arena & Training Lantern Bollards (16 parts):** `ForegroundBollardPost1..8` (`slate`) and `ForegroundBollardLantern1..8` (`gold`) flanking `RouteFromSpawn` (`X=-280/-260, Z=114/74`), the training approach (`X=-255/-235, Z=28`), and the arena avenue (`X=-156, Z=40/60`), staying outside all 8-stud route strips and below `Y=5.13`.
- **Spawn Plaza & Promenade Curb Trim (10 parts):** Flush terracotta/ivory spawn plaza framing (`ForegroundPlazaTrimW/E/S`, `ForegroundPlazaAccentS`) outside `RouteFromSpawn`, plus four low promenade north-edge curbs (`ForegroundPromenadeCurb1..4`) and two threshold inlays (`ForegroundPromenadeInlay1..2`) leaving `WestWalk` and `EastWalk` unobstructed.
- **Courtyard Planter Islands (8 parts):** Two low sculptural terracotta/ivory/olive planter islands (`ForegroundPlanterBase1..2`, `ForegroundPlanterRim1..2`, `ForegroundPlanterFoliage1..2`, `ForegroundPlanterAccent1..2`) centered at `X=-304` and `X=-230`, `Z=92` (`Y<=3.05`), giving midground mass without crossing routes or sightlines.
- **Hub Gateway Pilasters (4 parts):** Paired ivory/terracotta gateway pillars (`ForegroundGatewayPillarN/S`, `ForegroundGatewayCapN/S`) at `X=-196, Z=34/66` (`Y<=9.48`), framing the `RouteToArena` approach without any overhead span or obstruction to the `Y>=12` `ArenaWayfinding` and `AcademyNameplate` headers.

All 38 `Foreground*` parts are `Anchored=true`, `CanCollide=false`, `CanQuery=false`, `CanTouch=false`, `CastShadow=false`, `Transparency=0`, with zero gameplay attributes, zero lights/emitters, and zero per-frame updates. No physical geometry, spawn, training pads, NPC stations, shot corridors, or the 24,581-cell static reachability grid changed.

### Post-edit verification (mocked constructors & compilation; not native Studio render)
- `luau-compile src/ServerScriptService/CompactCity.luau`: compiled cleanly (exit 0).
- `python tests/coastal_art.py --negative-controls --baseline`: 2,601 assertions pass, 347 static cosmetic parts (38 `Foreground*`), pinned `09e0996` / `EXPECTED` original-part inventory fingerprint matches, and all 9 negative controls rejected.
- `python tests/academy_landmark.py --negative-controls`: 751 assertions pass (347 parts, 18 `Academy*` parts, 38 `Foreground*` parts, 1-for-1 `5622daa` hierarchy differential preserved), and all 8 negative controls rejected.
- `python tests/compact_world.py --negative-controls`: 1,710 constructor assertions, 47 targets over 24,581 connected clearance cells, and all 16 negative controls pass.
- `python tests/compact_integration.py --negative-controls`: 122 integration assertions and all 11 negative controls pass.
- `python tests/compact_guidance.py --negative-controls`: 81 navigation-copy assertions and all 4 negative controls pass.
