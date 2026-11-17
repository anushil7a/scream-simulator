# Tidal Foundry modular prop studies

Original Blender geometry for MAP-10 v2.1's first development slice. Inspected owner's IMG_1527.jpeg (MAP-05 Tidal Bell-Foundry & Acoustic Lighthouse Docks) and repo vault-derived MAP10_REVIEW / MAP10_ART_FINISH notes. This is a small modular art pack, not the finished map or reference-exact architecture.

- LighthouseCrystalCage: 992 triangles; 6×6×7.4 source units, cyan faceted crystal / open dark iron cage / cream socket.
- FoundryBell: 1,140 triangles; 5×5×4.18, genuinely hollow bronze shell, skirt and shoulder beads, iron clapper and crown.
- GantryBay: 204 triangles; 9×1.2×7.535, timber structure, knee braces, iron straps, stone feet.
- DockCapstan: 700 triangles; 4.5×4.5×1.9, eight-spoke wheel, iron base / bronze hub.

Dimensions above are Blender XYZ, Z up. Exports convert to standard glTF Y up. Intended one source unit per Roblox stud, but verify Studio importer units before using. Each GLB has base-centered origin, no display offset, editable named mesh nodes and material colors. The native .blend groups separately editable parts in named collections with horizontal display offsets only. Preview PNG is a Blender art render, NOT Studio or game evidence.

For the planned beacon: scale crystal cage uniformly by 10/7.4 for 10-stud height. For planned bells Ø24/32/40, uniform scales4.8/6.4/8 respectively. Do not nonuniformly distort bells; adapt suspension heights to their resulting20.064/26.752/33.44-stud heights. Giant runtime gantries are separate geometry; this modular bay is a detail study, not a drop-in collision replacement.

Validation: Blender4.3.2 exported and reimported all four GLBs; exact object counts/triangle counts, dimensions to.001, zero base Z, material presence and SHA256 checks passed. Each asset is capped below4,000 triangles (pack3,036). Preview visually inspected for silhouette/material separation. First render encountered unavailable denoiser; generator now disables it and rendered successfully. No textures, animation, external assets, scripts, asset IDs, uploads or runtime edits. Native Studio scale/material/emission/permission/performance remain UNVERIFIED. Keep decorative meshes noncolliding/nonqueryable when integrated; preserve map's existing collision and routes.

Reproduce from repository root:
```
blender -b --python tools/map21_props_blender.py
blender -b --python tools/validate_map21_props.py
```
