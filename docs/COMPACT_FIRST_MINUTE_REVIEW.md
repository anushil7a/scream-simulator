# Compact city: first-minute readability pass

## Scope

The owner resumed map work on November 12 and requested the vault before each task. This is a small readability pass on the existing 720 x 600 compact candidate, not a replacement map, completed art pass or release. The original city archive is unchanged.

- The authoritative training pads previously covered the three intended compact tier colors with the same green. Their actual construction now uses the matching existing shared color. The inactive original-map branch retains its old green.
- The practice stand line's former top was 0.07 studs, below the existing paving top at 0.08. Its new bottom is 0.12, above the paving and the new route top at 0.11. This is a source-geometry finding, not an observed Roblox screenshot defect. The line remains noncolliding and non-querying.
- Four subdued stone rectangles connect spawn, practice, the Rookie approach and the arena entrance. Three thin trim pieces frame the existing practice backstop. They are original Parts under `FirstMinuteGuidance`, anchored, noncolliding, non-touching, non-querying and shadowless. There are no lights, imported assets, prompts, destruction tags or per-frame work.
- Routes are edge-to-edge rather than overlapping coplanar surfaces. They stop before the trainer pad and before the actual red PvP threshold. Their color is not a safe-zone promise; the existing red arena boundary/sign remains authoritative guidance.

Existing collidable world geometry, spawn, quest/marker IDs, station locations, map projection, sports bounds, training eligibility, rewards, progression and save behavior are unchanged. The physical training-pad dimensions/material/locations remain unchanged. No live DataStore, purchase, product configuration, upload or publication occurred.

## Vault use and art direction

Used the already-reviewed vault context rather than re-auditing its contents:

- `World Composition and Set Dressing - Designed, Not Scattered`, sections 1-4, Common mistakes and Checklist: macro-to-micro, negative space, leading lines and camera comparisons before extra props.
- `Level Design Principles - Flow Sightlines and Landmarks`, sections 1-3: short readable introductory routes and landmarks rather than text alone.
- `fwjelaa-worldbuilding`, brief/composition workflow, and `Roblox-Maps-by-fwjelaa` guide: keep a coherent restrained style and validate the walkable blockout first.

Reference guidance by fwjelaa informed the pass. No imported generator, MCP installer, asset pack, texture or new dependency was executed or incorporated. Imported example budgets are not this project's measured performance.

## Verification

Exact final commands, hashes and counts are recorded in `tests/evidence/compact-guidance-2026-11-12.json`. Focused tests execute actual constructor/spawn-loop fragments with mocked engine objects. They cover the seven-part inventory, physics/query flags, unchanged pad geometry and original-map fallback, route endpoints/connectivity/overlap, target clearance and visible stand-line elevation. Negative controls must fail their intended assertions. The existing static reachability probe still covers 48 actual markers/stations/objectives; it is not native pathfinding.

The local native compact fixture now contains 20 additional geometry/flag/color checks. It was built and compiled, not run. Real camera controls, collision/walking, NPC motion, phone text/controls, color-blind/grayscale readability and multiplayer combat remain native/device gates.

## Bounded Blender comparison

`tools/compact_city_lookdev.py` exports actual `CompactCity.Build` and the actual World trainer-construction fragment through mocked Instances. It uses the already-installed signed Blender 5.2 headlessly, eight CPU samples, four threads, four 800 x 450 views and a 240-second subprocess timeout. It does not modify production source or launch a visible application.

The BEFORE snapshot contains 157 Parts and already includes the pad-color correction; it is only the baseline for route/frame/stand-line changes. AFTER contains 164 Parts. Overview, spawn, practice and arena views plus geometry/source/output hashes are under `build/compact-city-lookdev/{before,after}`. The new path and target frame are visible in this proxy. Initial route intersections produced black proxy artifacts; tiling the rectangles removed those new intersections. Other pre-existing thin-slab proxy artifacts remain. This is not evidence that Roblox renders black surfaces.

The proxy omits NPCs, billboard text, HUD, prompts, other World runtime details and native lighting. It approximates axis-aligned cubes/materials, not Roblox rendering or performance. It does not establish FPS, draw calls, physical traversal, native readability, exact camera behavior or a quality score. Headless processes exited; no Studio or additional picker was opened.

## Preservation and next gate

The archived original commit remains `72c886cb6f8a60ab26dff962e28da77e4b2d4609`; source ZIP SHA256 remains `a67c1e1af4f1cf4387a1bd0cb61a8ce84986290f10913e164fc8719c8877b19a`. This preserves repository-generated content, not unknown unsaved Studio work or external asset contents.

Next useful validation is the current compact map's actual spawn -> practice -> Rookie -> arena walk and player-camera views, followed by phone/accessibility and multiplayer checks. Do not decorate around an unverified route or call this native acceptance. GitHub push remains held for the pending direct confirmation; this checkpoint is local only. Existing real-voice, commerce and mixed-version quest-writer release gates remain unchanged.
