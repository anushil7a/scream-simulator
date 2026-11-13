# Max-level sustained damage, 2026-11-13

User reports a max-level beam needs more than one full attack against level1 and requests roughly1–2 seconds. This change raises only the level100 sustained-DPS anchor and protocol cap from68 to110. Levels1/25/50/75 anchors, health, range, legacy damage, duration, cooldown, protections, cover, test-mode isolation and rewards are unchanged. Existing interpolation means levels76–99 also increase. No client damage authority is added.

## Deterministic results, not a live-microphone diagnosis

Actual Bootstrap context/resolver/step, adapter, protocol and geometry rules execute with synthetic characters/raycast and scheduling. At level100 against100HP, accepted power1/.5/.08 gives baseline1.6/2.2/3.0 seconds, candidate1.0/1.4/2.0 seconds. A921-power (.080–1.000 by.001) ×4 server-phase sweep reaches candidate worst2.025 seconds, 25ms above2s in that sampled grid. Historical worst is3.075 seconds. An additional off-grid.0375-second phase reaches2.0375s. A100-phase minimum-power sweep from0 through.099 seconds at.001 spacing observes candidate worst2.040s (phase.040), baseline3.099s. These are observed synthetic timings, not a universal25ms tolerance, continuous phase proof or latency guarantee.

The actual trainer resolver and bot-health branch run too, with knockout scheduling/rewards stubbed. Full/half/min power candidate times: Rookie.8/1.2/1.6s; Brawler2/2.8/9.4s; Elite9.2/10.6/18.2s. Baseline: Rookie1.2/1.8/2.4; Brawler3.4/9.8/11.8; Elite11.4/19/28.2. Pulse-before-step at exactly4s expires the attack before a final tick, so420HP Elite narrowly needs another cast even at110DPS. These repeated-cast results depend on event ordering, and exclude human quiet/rearm delay. Real training strike/roam/respawn is not simulated.

Owner MaxLevel activates test mode. Mixed test/ordinary players cannot damage each other; both-test can. Missing pulses stop damage after.5s, power affects DPS and range, and the caster level is captured at Begin. These are concrete potential explanations to inspect in the reported session, not a proven diagnosis. Server-accepted power is not proof of real microphone amplitude. Health/range/LOS, arming and real-network conditions remain native multiplayer validation gates.

## Focused verification

- `python tests/sustained_ttk.py --negative-controls --report`:7618 assertions,3 controls (mixed-mode gate, protection gate, old DPS restoration).
- `python tests/sustained_ttk.py --baseline`: pinned09e0996 modules,7618 checks; preserves historical results.
- `luau tests/VoiceCombat.luau`:1630 combined checks.
- `luau tests/SustainedAttack.luau`:9094 checks, including per-target budgeting and caps.
- `luau tests/SustainedAttackAdapter.luau`:104 checks, including forged client level/damage and captured server budget.
- `luau tests/SustainedBalance.luau`:53 synthetic scenarios.

Levels75–100 are sampled at three powers. No balance change to lower anchors or legacy attack. Geometry/audio/network/real microphone, live reward/save behavior, real concurrent players and actual trainer movement were not validated here. No publication or live DataStore writes.

Vault reference consulted first: `10 Game Design and Genres/Time-to-Kill Math and a Weapon Balance Sheet.md`, including pitfalls/checklist. It distinguishes discrete damage breakpoints and effective TTK from paperDPS and requires audience/device playtesting. User requested this balance change; ideal synthetic timing alone does not resolve the reported real-session mismatch.
