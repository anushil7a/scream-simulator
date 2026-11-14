# Combat progression candidate — November 9, 2026

Local implementation for `feature/microphone-city-redesign`; not published to Roblox.

## Player loop

Train on the west-beach pads (map marker 8), complete automatically renewing combat challenges, and fight players in the central arena. One main level and XP bar remain. Screams unlock every ten levels through 100. The collection shows next-unlock health/DPS; milestone messages stay visible through subsequent reward notifications.

| Training fighter | Recommended levels | Health | Counterattack damage | Base KO XP |
| --- | --- | ---: | ---: | ---: |
| Rookie | 1–24 | 80 | 8 | 48 |
| Brawler | 25–59 | 220 | 18 | 180 |
| Elite | 60–100 | 420 | 32 | 420 |

Fighters retaliate only after being hit. Stay within 32 studs of their pad center to fight. A red, fixed-position warning lasts 1.1 seconds; moving more than four studs from it or dodging avoids the strike. Strikes have four-second spacing, respect protection and cover, and stop when the opponent leaves. Fighters reset health and credit after 25 seconds without a hit and recover six seconds after a KO. Ordinary residents retain their existing roles/quests; their XP is reduced to one per eligible hit, topped up to three for a KO.

## Rewards and safeguards

PvP base KO XP is `90 + 6 × victimLevel`. Actual recent damage divides one reward pool; overkill adds no credit. Assists require at least 10% of the target's maximum health. A finisher below that threshold can receive a small damage-proportional share but cannot use that exception for challenge progress. Credit expires after 25 seconds without another contribution and is consumed on KO. Offline contributors and expired/excluded damage do not transfer their shares to the finisher. The denominator is at least the target's full maximum health; repeated damage after healing cannot inflate the total above one pool.

For PvP, a victim within ten levels below the recipient pays the normal share. A victim 11–20 levels below pays 50%, 21–30 below pays 20%, and more than 30 below pays 5%. Defeating someone at least ten levels above pays 125%. Training uses the same scale relative to the tier's level band, so Elite remains rewarding through level 100. Combat strength itself is unchanged: high levels retain the approved health/damage advantage.

Each attacker/victim pair has a 60-second reward cooldown. Within ten minutes, eligible successive KOs/assists pay 100%, 50%, 25%, then zero. The bounded history lives outside player sessions, so reconnecting to the same server does not reset it. It is server-local: coordinated farming across different servers is not prevented by this first implementation.

One training challenge now renews automatically: contribute meaningfully to three eligible training KOs. Each completion gives `min(200, 30 + 2 x level)` XP. Training stops counting after the recipient outgrows the tier's reward band by more than twenty levels; lower-level players can still qualify through meaningful damage. The November11 cleanup retires the destruction objective and overlapping Elite objective. Their bounded partial counters remain dormant under original saved IDs; they do not display, advance or pay in this candidate. Base KO XP/coins and already earned progress are unchanged. Older servers/rollback code can resume those retired counters, so this is not a cross-version retirement fence.

## XP curve and preservation

XP to the next level is `floor(65 + 6L + 0.6L² + 0.009L³)`. Existing earned levels and banked XP are retained and normalized against the new thresholds; an old balance above a lowered threshold can advance a level. There is no level reset. The existing level-300 archive, style migration, session lease and temporary-test save protections remain. New costs can change the fraction of the current level's bar represented by the same banked XP.

The approved HP/DPS curves and four-second maximum attack remain unchanged. The November 11 candidate uses the requested five-second end-based cooldown. Healing still waits twelve seconds after dealing or receiving damage.

## Pacing model, not measured playtime

`tests/ProgressionPacing.luau` uses the actual rules and simulates solo training at the recommended tier, integer attack counts, four-second attacks plus five-second cooldowns, travel/retarget delay, and the single fighter challenge. It carries overflow XP. It excludes city quest/PvP bonuses, player defeats, contention, microphone failures and menus; it therefore cannot predict an individual player's session.

| Cumulative milestone | Learning | Steady | Efficient |
| --- | ---: | ---: | ---: |
| Level 10 | 12.9 min | 7.8 min | 6.6 min |
| Level 25 | 71.8 min | 45.1 min | 35.4 min |
| Level 50 | 254.6 min | 164.2 min | 121.9 min |
| Level 100 | 1134.0 min | 745.1 min | 527.0 min |

Rerun November11 after retiring the duplicate Elite bonus. Compared with the prior five-second-cooldown model, level100 takes longer (steady745.1 versus666.0 minutes;1220 versus1095 KOs). Lower milestones are unchanged. This is the explicit reward consequence of removing a redundant challenge, not a measured playtime or an automatic balance recommendation.

Assumptions: learning 55% aim uptime / 65% power / 15s retarget delay; steady 75% / 80% / 8s; efficient 90% / 100% / 4s. These are tuning scenarios, not player telemetry or targets guaranteed by tests.

## Verification and next playtest

Full local verification: 20 pure/synthetic suites, 48 mocked-service suites, 46 production sources compiled, normal candidate audited and disposable Studio builds generated. The progression native fixture checks real training rigs and geometry using synthetic attack input. See `tests/evidence/progression-redesign-2026-11-09.json` for the loaded build identity and observed results.

Next: real-microphone solo and two-player sessions at levels 1, 25, 60 and 100; measure KOs/minute, deaths, shared rewards, tier changes and minutes per level. Confirm repeat-opponent limits feel reasonable in a small friend server, validate real saves in an approved private environment, and test challenge/collection/map readability on physical phones. Publication requires the owner's approval.
