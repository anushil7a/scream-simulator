# Beam milestone candidate, November 16

## Reference and runtime diagnosis

Read the actual Sameer-PC vault `82 Scream Simulator Research/notes/beam-style-progression.md`, selected `roblox-vfx/LOCAL.md` and `SKILL.md`, and viewed actual `Concepts/VFX/VFX-01_Charging_Beam_Overdrive.jpg` and `VFX-02_Lightning_Dash_Warp.jpg` pixels. VFX-01 contributes elongated sweeping ribbons and sparse bright sparks; VFX-02 contributes angular electric filaments. The user's latest no-spheres instruction overrides the hand-charge ball in VFX-01. The existing Hollow Purple XML retains only the central violet demonstration, not adjacent Amplified/Reversal examples. No asset acquisition, upload, harvesting or new texture dependencies.

The production automatic-voice path is server `sustainedContext` (profile level), `SustainedAttackAdapter` (captured intent level), `Bootstrap.stepSustained` (SustainedBeam packet to nearby observers), Client event handler (attackLevel), `SustainedBeams.Update`, then `BeamVisuals.Update/Animate`. Equipped audio-style level does not choose visual progression. Previously native `Animate` hid **every** pooled decoration after generating it; native packs only changed families at 40 and 80. Thus decade geometry tested by mock-only paths was invisible in the actual native path.

## Candidate

Native templates and fallback geometry now share every-ten-level cosmetic width growth. Width ratios for L1,10,...100: **1, 1.22, 1.46, 1.72, 2, 2.30, 2.62, 2.96, 3.32, 3.70, 4.10**. Native widest enabled ribbon is normalized from actual source widths to `gameplayWidth * .6 * ratio`, so switching families does not shrink a milestone. This is presentation only; damage, hitbox, packet dimensions, range and timings are unchanged.

Visible jagged lightning strands by milestone: **0,1,1,1,2,2,2,3,3,3,3**. Corona strokes: **0,0,2,4,4,6,8,8,10,12,16**. One open collar becomes two at 70; high violet tiers use star contours. Width, winding and/or counts change at every milestone, including 100. Native pooled decoration is no longer hidden by template availability.

All spherical Part draws and dormant native sphere-sync code are removed. The near muzzle is a thin axial streak; the endpoint is a thin termination lens, including quiet/far views. Imported mesh bulbs are hidden; endpoint ParticleEmitters are disabled. Only existing column emitters can run, with aggregate per-rig rate capped at 60/sec (Hollow's existing 48/sec cap remains lower). No camera/light flashes added.

Observer game reduced effects, rig reduced effects and OS Reduce Motion all disable pooled dynamic decorations and template particle motion. Far LOD also stays static. Quiet width retains a modest milestone signature `1 + .18*(ratio-1)`, normalized among enabled core ribbons. Texture scrolling stops, particles clear/disable, then normal behavior restores without rebuilding the rig. The existing contact presentation is not enlarged with cosmetic width.

## Tests and limits

- `beam_milestone_native.py`: 6,275 actual builder/sync/manager assertions using Instance-tree doubles across all 11 milestones, gameplay widths 1/7, local/remote IDs, all template families, reduced/OS/far transitions and restoration. Four negative controls reproduce hidden native decorations, lost width scaling, ignored OS reduction and scrolling quiet textures. These are structural API doubles, **not Studio, GPU, asset-load or real voice proof**.
- Actual Client event-slice test: 305 checks plus 15 negative controls, all milestone levels/local and remote IDs, with audioStyleId held TinyAah; original gameplay width/range retained.
- Existing pool composition: 117,904 checks and seven controls, 512 peak created/destroyed; saturation native path regression retained.
- Contact: 110,035 checks and 20 controls. High-tier hierarchy/contact: 102,333 checks and 14 controls. Their frozen visual baselines intentionally advance to production commit `760b257` because spheres and old milestone profiles are no longer desired. Contact values/authority do not change.
- Silhouette: 818 checks/seven controls; tier geometry: 5,243 checks/seven controls.
- `verify_local.py --build`: **27 pure/synthetic suites, 150 mocked-service suites, production compilation and disposable builds passed**. New native milestone test additionally passes separately; integration owner registers it in the shared aggregate gate.

Pool remains 512 total and at most 77 regular geometry parts for one near high-level rig. Source template objects remain outside this legacy pool, as before; no claim that 512 bounds all render resources. Template instance counts do not grow per milestone. No physical-phone or overlap GPU measurement performed.

Native evaluation remains required at matched camera/lighting, start/mid/end and overlapping attacks: widest decorative glow must not be mistaken for damage width, violet must not bleach to white, actual asset loading must work, spheres must remain absent and hit cues readable. Existing template texture permissions/provenance remain unresolved from prior review. No Studio session, desktop UI, GitHub push or Roblox publication was performed by this track. Root owns aggregate registration/roadmap/native review integration.
