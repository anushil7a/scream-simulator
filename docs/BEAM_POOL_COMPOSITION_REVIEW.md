# Beam pool composition review - November 12, 2026

## Scope and result

Test-only coverage of the actual `SustainedBeams`, `BeamVisuals` and `BeamStyle` modules together. No production changes. The author and an independent reviewer ran:

```
python tests/beam_pool_composition.py --negative-controls
```

Both runs passed 117,904 assertions and seven negative controls. Peak allocation, total created and total destroyed were each 512 mocked Parts. The high assertion count includes repeated per-Part checks across 50 cycles, not 117,904 distinct scenarios.

Coverage includes 24 admitted attackers and manager rejection of a 25th, normal/reduced/far/culled cycling, unique live ownership, core reservation, released detail-budget reuse, refreshed survivors and exact expiry, replacements, reusable Clear, terminal Destroy and final pool destruction. A direct extra rig separately checks the renderer hard cap; it is defensive API coverage, not production admission of a 25th attacker.

Controls remove the hard cap, core reservation, pool insertion, detail-budget decrement, inclusive expiry, terminal guard and pooled destruction. Each fails its intended assertion, not source extraction or syntax.

## Limits and retained evidence

Parts are table-backed mocks. CFrame orientation is stubbed; Color3 and Lerp share a placeholder, so the color assertion does not prove color correctness. Actual module allocation/lifetime logic executes, but Roblox Instance hierarchy, geometry rendering, native event scheduling, GPU cost, frame time/FPS and transparency overdraw are not measured. No apps, live services or publication.

The suite is registered once in `verify_local.py`. Python syntax was checked without creating pycache. The prior d5cc5d5 aggregate of 25 pure/synthetic suites, 103 mocked suites, 63 production compiles and builds is retained historical evidence only. No fresh aggregate of 104 mocked suites is claimed.

Next useful evidence is native actual-instance composition and warmed baseline/normal/reduced overlapping-attack frame-time and transparency measurements under controlled camera/view conditions; desktop results would not establish phone or live multiplayer performance.

Exact source/test hashes and independent rerun results are in `tests/evidence/beam-pool-composition-2026-11-12.json`.
