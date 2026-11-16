# Boss appearance polish pass

November 16, 2026; based on integrated local tree 664b8ae. Appearance only: no map coordinates, encounter levels, damage, rewards, input, HUD or visibility-controller changes.

The five actual vault boss concept images and prior Blender/runtime silhouettes remain the visual references (paths and matching limitations in BOSS_FIDELITY_REVIEW.md). Read the vault's Boss Creature Case Study guidance already consulted for this work: coherent main shapes before repeated small details, clear material/value hierarchy, direct render/silhouette comparison, separated visual and combat geometry.

## Changes that reach the game

The Blender export now carries authored material type and reflectance into BossAppearance. Brass/armor uses Metal with restrained 0.055 reflectance, stone uses Slate, Conductor cloth uses Fabric, other enamel/skin retains SmoothPlastic. Only existing focal emissive colors use Neon, with zero reflectance. Blender palette values are converted from authored sRGB to linear for more representative renders; stone/cloth use subtle procedural preview grain, and native sphere/cylinder render smoothness is matched. Built-in Roblox material texture and Blender procedural preview are analogous, not pixel-identical.

- Metronome: stronger brass/enamel separation, dimensional visor brow/cheeks and restrained clock engravings, preserving large clock-case silhouette.
- Golem: tapered continuous shoulder cabinets instead of squared blocks, chest conduits, inset grille lines and stone cheek definition.
- Ignis: dimensional mask brow, breastplate ribs, cuff bands and layered cyan flame cores to clarify the opera-armor face/chest hierarchy.
- Leviathan: continuous chamfered jaw, directional brows, inset nostrils and cheek armor. One hidden-back coil span traded for those visible facial forms.
- Conductor: rounded octagonal bell flares with dark undersides rather than squared bells, continuous chamfered skin-tone face instead of metal block, cuff and glove shaping, lapel piping and restrained coat seams.

Native visual counts are 274/291/269/435/417 (Metronome/Golem/Ignis/Leviathan/Conductor). All remain under 450; the most expensive two became cheaper. Existing single-active appearance, batched build, cancellation and GeometryReady completion semantics are unchanged.

## Reproducibility and evidence

Fixed exporter compatibility: this installed Blender tessellator returns integer triangle indices, whereas the prior script assumed Vector objects. Both forms are now accepted. Regeneration completed with explicit per-boss <=450 export assertions. Original Blender source, lineup, individual views and front silhouettes are generated at build/boss-fidelity; no borrowed assets or uploads.

Focused actual renderer/controller tests: 8,068 assertions, including material presence and reflectance bounds; existing boss service/callback tests:172 assertions plus wiring. Full verify_local.py --build passed26 pure/synthetic +147 mocked suites, production compilation and disposable builds. Tests are synthetic/mocked, not Studio play or mobile GPU measurements.

This is a cohesive low-poly polish pass, not a claim of finished sculpted/painted concept parity. Organic stone detail, cloth motion and character animation remain simplified; wedge seams and native material lighting still require user/native review. No Studio GUI, external settings, push or publication performed.
