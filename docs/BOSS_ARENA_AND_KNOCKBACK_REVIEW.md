# Expanded boss arenas and close-range knockback

Read the relevant vault MAP-10 v2.1 build guidance (solid queryable floors and cover) and the recorded vault boss-pattern and phase guidance in the existing themed encounter and motion reviews. Existing production home coordinates, five encounter IDs, levels, health, rewards, cooldowns, attack damage and tell durations are unchanged. No enemy health HUD, save/progression schema or map geometry change.

| Boss | Arena radius (was 22) | Extended ranged warning | Close warning | Maximum shove |
| --- | ---: | --- | --- | ---: |
| Whispering Metronome | 38 studs | Alternating aimed Pendulum Sweep | Resonance Kick | 4 studs |
| Decibel Golem | 38 studs | Crossing Fault-Line Quake | Woofer Slam | 6.5 studs |
| Pyro-Tenor Ignis | 38 studs | Three aimed parallel Organ Flame lanes | Backdraft Stomp | 5 studs |
| Seagull Siren Captain | 38 studs | Aimed Twin Sirens with a center escape gap | Cutlass Broadside | 5.5 studs |
| Eclipse Conductor | 25 studs | Rotating Six-Bell Cascade | Baton Sweep | 6 studs |

The Shrine's first solid tier begins at radius 28. A radius of 26 touches that tier when reserving two studs for avatars. The 25-stud radius keeps the margin clear without landscaping changes. Exact source tests probe 23,081 floor/headroom points around all five sites, including that two-stud margin. Marked intervals stay within roughly six studs; stationary home and 12-stud vertical eligibility are authoritative. A smaller ring override in a separately authored QA layout dynamically shortens ranged markers.

Ranged and melee cadence slots alternate; a melee slot checks the rotated participant list for a reachable target. If no participant is in that move's footprint, the boss uses its ranged move. One visible geometry definition determines both the warning and damage. Melee markers are brighter. Per the later owner request, the world plate shows only the boss name and level, including during melee and defeat; motion, visible ground shapes and existing sound remain. Named move, attack kind, committed pose, times and serial are shared with animation. A cancel does not signal impact. Warnings do not follow targets; a late join, bystander, protected/dodging player, lost participant or wall-blocked target cannot take damage.

Only a valid grounded survivor of a resolved melee attack can be shoved, not a ranged victim or a player being ejected after a knockout. The server checks substeps with the existing avatar-width dodge sweep, support rays and slope limits. The movement stops before obstacles, unsupported floor, the arena edge, map boundaries or a dedicated PvP zone. No physics impulse, upward launch, lasting effect, repeat knockback or client-supplied motion. The nameplate is raised above the doubled visuals; no HP display has been added.

## Verification and next action

- 8,172 actual-service assertions, 14 actual Bootstrap callbacks, and 169 actual knockback/dodge geometry assertions passed with doubles. Cases include ranged reach, distinct melee, rotation fallback, one hit per cast, wall and edge stop, safe floors/slopes, invalid participants, block by cover, air immunity to displacement, and existing ejection.
- 23,081 analytic production layout floor/headroom samples passed with avatar margin; production world, sports/PvP and boss arena separation passed. All touched Luau combat modules compiled. Existing audio, VFX and balance suites passed. These are code and geometry checks, not native walking, replication, timing or game-feel claims.
- Exact v4 local Studio solo diagnostic passed 15/15. See the quality review log for actual damage/displacement and label fit. Next overall gates: human input/latency, multiplayer boundary and simultaneous reward checks, mobile performance and close-zoom animation framing. No publish, release or save changes.
