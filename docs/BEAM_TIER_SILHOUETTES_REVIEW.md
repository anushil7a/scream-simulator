# Authored ten-level beam evolution

Regular nearby profiles now change every ten levels: starter round collar;10 diamond;20 diamond+four spokes;30 paired round collars;40 helix;50 zigzag;60 triple collars+helix;70 eight-spoke crown;80 double helix;90 star collars;100 stars with a tighter counter-wound braid. Existing per-level part counts remain unchanged. Custom colors, body/core formulas, reduced/far behavior,512 cap, five-part reservation, pooling, cleanup and caller cadence are preserved. No gameplay/audio/server changes or assets/lights/Client hooks.

## Contributor preservation

Work is isolated in scream-simulator-resume-20261113 at base 09e0996. The contributor's pre-existing collar fade is excluded here: this worktree retains the committed travel-alpha behavior. The primary workspace modules were restored byte-for-byte from pre-task snapshots, preserving that contributor fade; only our primary test/docs copies were removed after verified transfer. Raw baseline snapshots and the original our-only patch remain in the primary build/beam-tier-baseline and build/beam-tier-owned.patch. No contributor edits are included in this candidate.

## Guidance

Consulted roblox-vfx LOCAL and targeted vault query VFX progression escalation tiers. Source: vault/fwjelaa/fwjelaa vault/07 Lighting VFX and Audio/Escalation and Grandeur Without Clutter.md, sections1–2 and6: distinguish repeated silhouettes, trade layers instead of stacking, keep budget bounded. These are art-direction recommendations, not native proof.

## Focused verification

- python tests/beam_tier_silhouettes.py --negative-controls:4034 actual profile/renderer assertions +eight controls; same checks pass without local fade. Levels1,9,10,19,20,...99,100; malformed/clamped tiers; gold/purple/green; equal geometry/time; authored collars/ribbons; reduced/far and cleanup. CFrame orientation/engine rendering mocked.
- python tests/beam_silhouette.py --negative-controls:695 retained assertions/seven controls. Only the chord oracle adapts to noncircular collars; prior core/tint/material/reuse controls remain.
- python tests/beam_pool_composition.py --negative-controls:117904 composed assertions/seven controls;512 peak and512 destroyed.
- Existing beam_style.luau monotonic bounded counts and both module compiles pass.

## Native gate

Compare every adjacent tier at identical camera/length/width/time, side and end-on, multiple colors and reduced/far. Numeric differences are not visual acceptance. Decorations remain best-effort under shared budget pressure;24 attackers are not promised full detailed silhouettes simultaneously. No phone/GPU performance result, live service or publication. The implementation worker did not operate Studio; coordinator native observations are recorded below.

## Native-informed readability revision

The first three native gallery pages showed early thin collars nearly disappearing side-on. The candidate now expands non-starter regular-near collar radius by 25%, uses line thickness .16+tier*.012, and sweeps diamond collars axially by cos(angle)*radius*.75. This reuses the same segments and preserves body/core, reduced/far and part budgets. Axial collar ornaments can extend slightly beyond the beam endpoint during their travel; these remain nonquery cosmetic parts, not hit geometry. Geometry/control checks pass; the same-camera comparison below was independently accepted as a bounded visual improvement. A single selected rig is needed for end-view evaluation; the four-rig purple image overlaps and is not acceptance evidence.

## Recorded native comparison

A private copy of the exact modules above was inserted into a verified local place0/game0, not a cloud experience. Four equal-width, equal-length rigs at fixed age0.6 were captured through Studio's supported explicit camera capture. The first gallery showed early collars disappearing side-on and prompted the refinement. Revised pages show the diamond envelope at10/20, extra collars at30/60, and increasingly structured ribbons/crowns through100. Some middle-tier differences remain modest from certain angles; this is not a promise that every tier is instantly identifiable in combat. Reduced effects intentionally keep their previous simple look.

[Levels1-30](images/beam-tiers-2026-11-13/page1.jpg), [40-70](images/beam-tiers-2026-11-13/page2.jpg), [80-100 and reduced](images/beam-tiers-2026-11-13/page3.jpg), [isolated purple100 end view](images/beam-tiers-2026-11-13/end.jpg). Labels list rows top-to-bottom. The earlier overlapping end image was rejected, not used as acceptance evidence.

Gallery/label removal and Game Stopped were verified. Three asset-type warnings were present; their origin was not established. No real attack, native movement/animation timing, multiplayer, phone/GPU or combat-target visibility validation. The final focused4034/8,695/7 and117904/7 checks were rerun after refinement. The earlier composed full235-command run predates the collar refinement; it is not a final-refinement aggregate claim. [Exact evidence](../tests/evidence/beam-tiers-2026-11-13.json).
