# Larger themed boss encounters: local candidate

Read relevant vault sources on Sameer-PC before implementation: `10 Game Design and Genres/Boss Fight Design Patterns.md` and `08 Animation/05 Systems/Boss Animation and Phases.md`. Applied fixed committed tells, readable ground shapes, recovery and bounded hazard lifetime. Five reference identities retained. This change does not implement rigs, animation clips, health phases or group scaling.

## Shared contract

Catalog `scale=1.4`, `aimHeight=7`, `engageHeight=12`, `radius=18`. Visual scaling is a separate coordinated client commit. Core is invisible/noncolliding; its ground offset and size follow the same fields. World labels sit above the enlarged body, display18-stud admission, and never show health. Map agent confirmed all five existing homes fit unchanged.

Server `Valid` uses actual character position, horizontal squared distance from fixed home <=18² and absolute height delta <=12; NaN/Infinity cannot pass. Both existing sustained and legacy paths call `CanHit`, and `Hit` independently rechecks. A long beam crossing the model from outside the ring does not authorize damage. Root owns broader central-body aim samples with unchanged admission/cover checks.

## Patterns

All coordinates are ground-relative. `BossPatterns.Build(id,turn,x,z)` returns `{name,shapes}`. `Contains` and `Hits` use the identical shape dimensions/orientation used for markers.

- Metronome: one4×30 pendulum bar; alternate perpendicular beats.1.5s tell/4.5s interval.
- Golem: radius10 woofer slam, then two5×30 crossing fault lines.2s/6s.
- Ignis: three3×26 flame lanes with8-stud center spacing, alternating axes.1.75s/5s.
- Leviathan: sixteen short rectangular sonar-ring segments centered at radius11, then radius7 aimed undertow pool whose center is clipped at10.2.25s/5.75s. No forced movement/debuff.
- Conductor: six radius4 bell disks around radius11, alternating30-degree phase.1.5s/4s.

All real corners/disks stay within18. A safe response exists without leaving the encounter. Each cast applies at most one unchanged damage amount per participant even at overlapping shapes. No tracking after tell creation, no repeated damage ticks, no strobing. Static translucent theme-colored ground warnings + action text. Maximum16 temporary parts per boss,80 across five simultaneous encounters, destroyed on impact, KO, quiet reset or loss of every participant. No permanent attack objects or async damage tasks.

Participant identity is snapshotted at tell start. New opt-ins during a tell cannot be hit by it. Departure/range exit/identity change/expired credit invalidates damage and credit. No proximity aggression, unchanged reward pots, respawn, health, levels and save schema.

## Evidence and limits

- Actual-source mocked service:635 assertions +10 Bootstrap callbacks; covers all five patterns, every corner boundary, invalid/exact admission, direct damage bypass attempts, KO cancellation, early empty-encounter cancellation, late join protection, bystanders, overlaps, identity/expiry/reward lifecycle.
- Five balance estimates unchanged:40–63.5s ideal full-power duty-cycle TTK; these are mathematical estimates, not human balance evidence.
- Full local gate:26 pure/synthetic +148 mocked suites, production compilation and disposable builds passed.
- Native warning orientation/ground readability, phone latency and enlarged camera/aim feel still require Studio/player checks. No native claims, uploads, push or publication.
