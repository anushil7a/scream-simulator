# Bounded Blender beam look-development review

November 12, 2026. Original offline proxy of the current cosmetic beam formulas, not a new asset imported into the game.

## Result and files

`tools/beam_lookdev.py` ran the installed signed Blender 5.2 headlessly with factory startup and automatic file-script execution disabled. Exit code was zero. Outputs in ignored `build/beam-lookdev/`:

- `comparison.png`: six labeled previews, levels 1/50/100, regular/reduced.
- `level-{1,50,100}-{regular,reduced}.blend` and matching PNG files.
- `geometry.json`: exact generated primitive inputs and polygon counts.
- `provenance.json`: pinned source/script/artifact SHA256 hashes, fixed inputs, render limits and elapsed time.
- `blender.log`: local render output.

The contact sheet was visually inspected. An initial Blender-only rotation-mode ordering mistake made cylinders vertical. It was corrected before the accepted previews, with an explicit cylinder-axis alignment assertion. This was not a Roblox defect. Any `.blend1` backups from that initial scratch evaluation are not accepted artifacts; only files listed by final provenance are current.

## Reproduction and limits

Run the installed Python 3.13 interpreter with `tools/beam_lookdev.py`. Pillow is used only for local contact-sheet assembly. No third-party generator is imported. The script refuses changed BeamStyle/BeamVisuals hashes until its translation is reviewed and deliberately repinned.

Six cases use identical illustrative length 24, width 3, age 0.6 seconds, yellow color, and near-viewer detail. These are comparison inputs, not each level's actual combat range, width or damage. Source-derived primitive counts are 15/4, 41/4, and 77/4 for regular/reduced. Cylinders use 12 sides; endpoint spheres use 16 segments and 8 rings. The object limit is 78 including the camera per scene. CPU Cycles renders 640×280, eight samples and four threads, under a 240-second outer timeout. No visible application windows were opened; the headless process exited.

## Useful observations

- The sampled low/mid/high silhouettes communicate increasing decorative complexity: one ring at level 1, rings plus a strand at level 50, and denser rings/two strands/corona at level 100.
- Reduced mode removes decorative rings/strands/corona and the origin ball, retaining the three core cylinders and endpoint ball. Tier-dependent thickness remains, matching the source.
- From this camera, side-on to the beam axis with an elevated view, rings can read as thin crossbars and high-level strands overlap the bright core. That is useful for planning another native viewing-angle check, not evidence that the game's material or geometry needs changing.
- This exercise validates the installed Blender toolchain for small original geometry comparisons. No additional modeling stack or generated asset library was needed.

Cycles emission/transparency is only an approximation of Roblox Neon and its blending. There is no bloom, native renderer parity, temporal animation validation, multiplayer pool pressure, mobile performance, camera/aim accuracy or authentic gameplay measurement. No imported textures, meshes, uploads, purchases, cloud calls, map changes, production changes or publication occurred. The preview cannot justify replacing the existing game renderer without native comparison.

Recorded artifact hashes: [beam-lookdev evidence](../tests/evidence/beam-lookdev-2026-11-12.json). The local generated .blend/PNG files are reproducible review artifacts, not runtime Roblox assets. No new full gameplay-suite run was needed for this isolated tooling/documentation change; b165525 remains the last production verification.

Independent read-only review confirmed all 14 artifact hashes, both source hashes, exact generated geometry for all six fixed cases, signed bounded headless execution and the preview limitations.
