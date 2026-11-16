# Compact-city optional boss encounters

November 16, 2026 local candidate. Not uploaded, published or played in Studio.

Vault consulted read-only: project/vault AGENTS, Concepts/concept-art-catalog.md (canonical boss descriptions/levels), and `10 Game Design and Genres/Boss Fight Design Patterns.md` (telegraphs, arena leashes, contribution and cooldown guidance). Existing roadmap read. No vault originals modified.

## Roster

| Boss | Minimum level | X,Z | HP | Damage | Base coin / XP pot |
|---|---:|---|---:|---:|---:|
| Whispering Metronome | 10 | -325,-55 | 320 | 12 | 35 / 100 |
| Decibel Golem | 30 | 285,125 | 580 | 20 | 65 / 200 |
| Pyro-Tenor Ignis | 50 | -180,-270 | 960 | 28 | 80 / 270 |
| Leviathan Sub-Bass | 70 | 205,-265 | 1280 | 36 | 95 / 340 |
| Eclipse Conductor | 95 | 135,260 | 1900 | 45 | 110 / 420 |

BossCatalog.Entries is the single shared coordinate source. All encounters have an 18-stud boundary, stationary 8x8 proxy body, no chase. Spatial review against compact geometry passed without migrating the large-map preview. No enemy-health HUD/nameplate added. Name, minimum level, join instruction, attack warning and respawn timer only. Current runtime models are simple Part proxies; separate original Blender boss art is not imported or claimed runtime-ready. Manual beam aim works; boss lock-on targeting is not implemented.

Metronome alternates 3/5-stud pendulum pulses, 1.5s tell and 4.5s interval. Golem alternates 6/8-stud bass quakes, 2s tell and 6s interval. Conductor alternates 4/7-stud bell strikes, 1.5s tell and 4s interval. Target point locks at tell start and full hazard disk is clipped within the encounter ring. Move out, dodge, or leave the encounter to avoid damage. Passers-by never take damage; only current session-bound contributors are targets. Existing protection/ejection/healing behavior reused.

## Lifecycle and rewards

Authoritative beam geometry and line-of-sight checks admit damage only from level-qualified players inside the ring and within 12 vertical studs. Bosses do not join World.Bots, preventing resident rewards, crowd quest credit or training KO paths. Shared live tester mutations are blocked, while the existing isolated save-disabled Studio fixture can exercise higher levels. Toggling the mic off does not cancel retaliation after opting in.

Respawn 90s after KO; quiet reset after 20s; current-session contribution expires after 20s or leaving the encounter. At least 5% max-HP actual damage required. Overkill is capped. Each eligible share is actual damage / max HP, rounded down against the fixed reward pot, with no redistribution or finisher bonus. Expired/invalid shares are lost. Per-user/per-boss 300s reward cooldown survives reconnect within this server, but is not persisted across servers. Existing commerce multipliers apply after splitting. No save schema changes. No loss rewards or progress gates.

## Evidence and limits

`tests/boss_service.py`: 144 actual-service assertions, 10 actual Bootstrap callback assertions plus sustained/legacy/loop source wiring contracts. Covers level/zone/vertical gates, nonfinite inputs, overkill, assist pot bounds, no repeated KO rewards, cooldown, respawn/reset, fixed aim and movement escape, participant-only damage, edge clipping, identity/credit expiry, protected/dodge states, test-session isolation, safe ejection and reward rounding. The beam contact historical test still checks old NPC/PvP branches unchanged, exempting only the exact new boss dispatch.

`tests/BossBalance.luau`: actual combat progression and four-on/five-off duty cycle estimate 40.0/51.8/43.7 seconds at full amplitude; 62.3/80.6/68.0 seconds at 35% amplitude. Individual strike 10.1/12.1/10.6% of minimum-level health. These are ideal solo sustained estimates without dodging/healing/aim loss, not human playtests. Legacy burst mode takes longer. Fixed HP is intentionally bounded first-pass tuning, not group scaling or final balance.

Native placement/walkability, actual microphone controls, physics, phone telegraph readability, multiplayer performance, model import and group TTK remain pending. No release readiness claimed.

## Requested level-50 / level-70 extension

Latest owner direction adds exact level 50 and 70 encounters without removing the original three. Reconsulted the actual vault catalog and verified `Concepts/Boss/BOSS-04_Lv45_Pyro-Tenor_Ignis.jpg` and `BOSS-06_Lv65_Leviathan_Sub-Bass.jpg`. Their canonical names/designs are retained while the older reference levels 45/65 are deliberately superseded by requested runtime levels 50/70. No vault files changed.

Ignis: 4/6/3-stud Azure Overture sequence, 1.75s fixed warning and 5s interval. Leviathan: 5/8/6-stud Sonar Surge sequence, 2.25s warning and 5.75s interval. Same stationary opt-in envelope and conservative reward lifecycle as the existing three. Map QA identified northwestern/northeastern off-path pockets, minimum solid clearances 28/33 studs, spawn BFS routes 490/870 studs; native movement remains untested. Though the Leviathan concept is coastal, this compact-map review places its optional encounter in the safe northern pocket rather than crowding the coast's existing sports and boss activities.

Minimum-level ideal sustained solo TTK is 63.5/62.6s at full amplitude, 98.9/97.4s at 35% amplitude. Strikes remove 12.4/11.8% max health. HP and fixed reward pots increase between L30 and L95; no final-balance claim. Tests now find bosses by ID, assert exact level-50/70 roster entries, derive respawn from catalog and execute every boss's full telegraph footprint sequence. Focused service tests: 144 assertions plus 10 actual Bootstrap callbacks; all five balance estimates pass. Runtime originals remain separate Blender assets pending import.
