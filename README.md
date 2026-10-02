# Scream Simulator

Experience: **Scream Simulator** · Place `122465114514497` · Universe `10767534975`.

[Play Scream Simulator](https://www.roblox.com/games/122465114514497/Scream-Simulator)

**Published version 32**, confirmed by Roblox Studio on September 23, 2026 (02:59:54 UTC September 24), then verified by reopening the cloud place.

## Get started / help develop

**Repository:** https://github.com/anushil7a/scream-simulator

```sh
git clone https://github.com/anushil7a/scream-simulator.git
cd scream-simulator
```

Open `ScreamSimulator.rbxl` in Roblox Studio and press **Play**. The local place generates its city on startup. To modify the project, edit `src/` and rebuild with Rojo; see [Contributing](CONTRIBUTING.md) for the file guide, build commands, testing, and pull request workflow.

Report bugs and ideas in [Issues](https://github.com/anushil7a/scream-simulator/issues). Developers can fork the repository and submit pull requests. Roblox edit/publish access is managed separately by the experience owner.

## XP and combat redesign — September 23, 2026

- Compact health/XP HUD. The **SCREAMS** button or **B** opens and closes the collection menu. Scrollable tabs: Screams, Quests, Style, Map, Settings. Landscape phone layout keeps text readable and gameplay controls away from the joystick and jump button.
- XP levels rise incrementally through level 30. Starter scream at level 1; unlocks at 5, 10, 15, 20 and 25. Each tier has more damage, forward beam range and width, with visual effects. Five effect colors are available.
- Only the **960 × 720 stud central district** (40% of the 1440 × 1200 playable land rectangle) permits PvP. Both attacker and target must be inside it, within range, and have clear line of sight. The remainder of the city and coast is safe.
- Five seconds of protection after spawn or arena knockout. Protected players cannot attack or receive scream damage. Knockouts return players to the safe hub.
- Player knockouts award `50 + 12 × victim level` XP and 20 coins. The same victim has a 30-second reward cooldown. NPC hits/knockouts give smaller rewards, with distance, line-of-sight and reward cooldown checks.
- **Q** rolls for 0.6 seconds, with a 4-second cooldown. Collision checks limit the dash distance. Dodging avoids an incoming scream during its active window.
- Shields, purchased upgrade tracks, discovery points and City Passport boxes are removed. Existing coins and level are retained when older profiles load; obsolete fields are dropped.
- Health restores 20% of maximum health after 10 seconds without a damaging scream, repeating every 10 quiet seconds.

## City and coast

An original Barcelona-inspired city: chamfered Eixample blocks, courtyard gardens, warm plaster/stone facades, terracotta roofs, shutters and iron balconies; narrow Born lanes with café courts and festival pennants; lower maritime homes; a covered produce market; fountains and a shaded rambla. A basilica-inspired landmark and tapered glass tower give each side a recognizable skyline. The southern beach includes a promenade, palms, parasols, loungers, volleyball, lifeguard cabin, café and music stage. This is a stylized original layout, not a scale recreation.

42 seeded residents replace the previous 114. They use grounded humanoid movement, animated walking, local destinations, conversations and reactions. Resident collision groups prevent crowd stacking; ground checks recover stuck/airborne residents without jump spam.

Six moving cars and four parked cars have solid collision hulls. Moving impacts deal 15–35 damage based on speed, knock the player sideways, and recover after 1.3 seconds. Impacts have a 4-second damage cooldown and respect spawn protection.

Player health scales by 8 per level: 100 at level 1, 332 at level 30. Beams travel 30/42/56/72/90/112 studs and widen from 4 to 10 studs. Walls stop beams; characters behind or outside the beam receive no damage. Rolling uses a full-body joint animation while the collider stays upright and sweeps for obstacles.

## Quests

Accept one quest at a time in **Quests**, complete it, and claim its reward there. Progress and claimed rewards are saved. Timed delivery/race attempts restart each session. Each quest pays once per profile.

- **Leave Only Footprints:** collect six beach bottles with F; 100 XP / 50 coins.
- **Coffee Before the Encore:** collect an order at Coastal Coffee and deliver to the beach stage within 90 seconds; 120 XP / 60 coins.
- **Three's a Crowd:** hit three different NPCs in one scream; 100 XP / 40 coins.
- **Boardwalk Dash:** start beside the lifeguard tower and reach the east promenade marker within 25 seconds; 120 XP / 50 coins.
- **Can't Touch This:** evade three enemy player screams with a dodge in the arena; 160 XP / 70 coins.
- **Underdog:** knock out a player of equal or higher level; 180 XP / 80 coins.

## Controls and test tools

- E / SCREAM: fire a beam in the direction your character faces.
- Q / DODGE: roll.
- Hold Shift / tap SPRINT: up to 10 seconds of running, then a 5-second rest. Releasing early allows recharge.
- T / TALK: speak to a nearby resident.
- F: quest interactions.
- B / SCREAMS: toggle menu. M: map.

**TEST TOOLS remains available to everyone for friend testing**, as requested. `DeveloperAccess.PublicTestingEnabled = true` controls this. Commands add XP/coins, change level, heal, teleport to hub/arena/beach, or reset quests/NPCs. Any test command disables saving for the session, preventing test changes from replacing normal progress. Set the flag to false to restore owner-only authorization.

## Verification and limits

- All 10 Luau files compile; both Rojo builds pass.
- Live Studio beam test: front target 60→48 HP; rear and side targets stayed at 60. A wall stopped the beam at 9.5 studs and prevented damage. Supernova reached 112 studs and damaged a target 100 studs away, 60→12 HP.
- Moving car impact: 100→75 HP, visible physics knockdown, automatic recovery; no second immediate hit after sideways knockback fix.
- Roll joint animation inspected on the actual player rig; rolling toward a parked car stopped at its hull and set the four-second cooldown.
- NPC grounding sample: 672 samples, zero gaps above five studs; maximum root-to-ground gap 3.12 studs, 507 moving samples.
- Level 30 health and HUD verified at 332/332. PvP rectangle area verified as exactly 0.4 of playable land.
- City reviewed at street height and from above; desktop HUD visually reviewed. Relocated beach pickup and café-to-stage delivery tested through actual F prompts.
- No runtime errors observed other than expected Studio DataStore access warnings. Studio API access is disabled; these tests use temporary profiles. Full multiplayer and live persistence still need a friend session.
- Original audio still uses Roblox's built-in oof fallback with tier-dependent processing; approved custom audio IDs can be set in Config.
- Public access previously enabled for Roblox audience reach ages 16+ and trusted friends. Wider reach requires owner eligibility steps.

GitHub research and download review: [Barcelona plan](research/BARCELONA_PLAN.md). Rojo (1,747 stars) is reused. BlenderGIS (9,407 stars) was reviewed as plain-text source only and rejected for installation because its entry point disables default HTTPS certificate verification. No third-party runtime code or GIS imagery was imported.

## Source and builds

`City.luau` generates the city; `World.luau` generates residents and traffic. `Bootstrap.server.luau` handles progression, combat, quests, protection and test tools. `CombatRules.luau` contains shared server targeting/cast checks. `Client.client.luau` builds the HUD/menu and effects. `Profiles.luau` loads/saves sanitized profiles in `ScreamSimulator_v1`; failed loads never overwrite existing saves.

Local `.rbxl` and `.rbxlx` files contain scripts that build the world on Play. The published place also contains the generated map for Edit mode. Pre-redesign source is retained in `backups/pre-barcelona-redesign/src`.

```sh
rojo build default.project.json -o ScreamSimulator.rbxl
rojo build default.project.json -o ScreamSimulator.rbxlx
```
