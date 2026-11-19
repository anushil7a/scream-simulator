# Boss combat balance pass

Unpublished local candidate. Consulted the vault development guide and recorded boss-pattern guidance, the progression and arena reviews, and the exact v4 Studio diagnostic findings (one scripted instance of each boss's melee, ranged, and dodge immunity; not a human clear-time sample). This pass changes boss max health and damage per impact, not boss names, order, placements, admission, movement, weapon geometry, reward pots, health display, cast/recovery duration, dodge displacement, or save/progression records. The Academy's existing 35 boss coins plus 65 fixed starter-bonus arrangement is unchanged.

| Encounter (unlock level) | HP old → new | Ranged damage | Melee damage | Ideal | Steady | Quiet 75% aim | One missed cast |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Whispering Metronome (10) | 320 → 265 | 19 | 23 | 29.6s | 51.6s | 65.2s | 60.6s |
| Decibel Golem (30) | 580 → 435 | 26 | 31 | 36.2s | 54.0s | 73.4s | 63.0s |
| Pyro-Tenor Ignis (50) | 960 → 700 | 35 | 43 | 37.6s | 61.2s | 81.4s | 70.2s |
| Seagull Siren Captain (70) | 1,280 → 1,100 | 47 | 59 | 39.0s | 63.2s | 84.4s | 77.2s |
| Eclipse Conductor (95) | 1,900 → 1,570 | 58 | 77 | 30.8s | 53.2s | 72.6s | 62.2s |

These estimates use actual unlock-level player stats, the sustained adapter's 0.2-second damage ticks and integer rounding, and the boss's health/credit rules. No paid gear benefit assumed. Ideal means full power/continuous contact; pulse-before-final-damage ordering raises ideal to 30.2/37.0/38.4/39.8/36.6 seconds (still 4–5 casts). Steady means 80% power, three out of four eligible contacts, and a dodge cancelling every third cast at 2.6s; cooldown starts when casting stops. Quiet means 35% power and the same contact ratio with full-length casts. A separate learning scenario (65% power, two out of three contacts, every other cast cancelled by dodge) needs 61.0–83.8 seconds.

Under these timing assumptions, one whole missed cast prolongs the fight but does not reset it. Two consecutive full misses after landing prior damage cross the unchanged 20-second idle reset and credit timeout. This is not a guarantee for additional scattered misses, leaving the arena, or any particular microphone/controller. Recorded times exclude any loss/retry and are not human playtime forecasts.

Ranged hits account for about 13–16% of unlock health and melee about 17–19%. The final boss trades a smaller fraction per hit for its faster four-second attack cadence: approximate steady-cast retaliation opportunities range from nine (Golem) to thirteen (Conductor). These are tells emitted on cadence, not unavoidable hits. Player healing requires 12 seconds without dealing or receiving damage; repeated beam contact and missed dodges can prevent it. The shorter clears reduce sustained exposure but standing in every warning is not intended to succeed.

## Verification and next action

Actual model tests passed both final-tick orders, no-gear 35% input at 75% contact under 100s, full-power 3–7 cast requirement, existing 20s reset behavior, larger melee versus ranged damage, and exact fixed reward pots. Actual service tests (8,197 assertions) verify exactly one impact and the authored amount for all ten boss/cast pairs; 14 Bootstrap and 169 knockback/geometry double checks, production compile, and 23,081 existing arena geometry samples passed. No Studio balance or multiplayer test is established by these results. Next: verify these exact authored impact amounts using the disposable diagnostic, then measure unlock-level solo time and failures with human input.
