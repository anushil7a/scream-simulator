# Earned gear candidate, November 16, 2026

Not published. New Blender exports are real authored meshes, but are **not imported into Roblox**. Runtime intentionally uses a marked temporary old Micro-speaker/megaphone visual when no verified template exists. Do not call the fallback the Blender model.

| Gear | Minimum level | Earned coins | Input amplification |
|---|---:|---:|---:|
| Academy Megaphone | 1 | 100 | 6% |
| Micro-speaker | 1 | 200 | 12% |
| Mosaic Studio Mic | 15 | 300 | 18% |
| Street Boombox | 35 | 600 | 23% |
| Parabolic Sonic Cannon | 65 | 1200 | 28% |
| Celestial Organ Pack | 90 | 1800 | 32% |

One active bonus, normalized power capped at 1. Existing full-power DPS/range, health, raw capture threshold constants and cooldown unchanged. The bounded bonus substitutes for, never multiplies with, legacy flags. At .35/.55/.75 raw input, the top item produces .462/.726/.99 normalized input, translating to 9.59%/12.86%/15.30% sustained DPS improvement vs bare gear at the same input. Full power remains identical. Top gear saturates at ~.758 raw input. These are mechanical comparisons, not proof of PvP fairness; test equal-level gear/no-gear duels.

## Pacing evidence
`tests/GearProgression.luau`: deterministic steady solo training model uses actual trainer health/XP/challenges/level requirements, 5 coins per eligible KO, .8 input, .75 accuracy, full 4s attacks + 5s cooldown, 8s travel. Buys all pieces sequentially; no boosts or one-time quest coins, and conservatively no gear acceleration. Price-only old starter was 100 KOs; candidate is 20. Modeled purchases:

- Megaphone: level 10, 8.7 minutes / 20 KOs
- Micro-speaker: level 19, 26.0 minutes / 60 KOs
- Mosaic Mic: level 29, 56.8 minutes / 120 KOs
- Boombox: level 45, 132.7 minutes / 240 KOs
- Cannon: level 65, 296.8 minutes / 508 KOs
- Organ: level 90, 566.8 minutes / 940 KOs

Level gates are minimum eligibility, not promises of instant affordability. Early city quests pay ~40–80 coins once, making first purchase available materially earlier. Players can skip intermediate items. No Robux product or entitlement changes. Previous purchases retain ownership, not a retroactive refund; earned currency balances are never reset.

## Persistence and rollback
`gearOwned` is a validated allowlist; `gearEquipped` must be owned and meet its level to affect combat. Legacy `amplifierOwned`/`megaphoneOwned` stay intact. A dual-equipped legacy save uses the stronger single Micro-speaker bonus without deleting either purchase. Intentional switching clears legacy equipped flags, not ownership. New purchases atomically check eligibility/coins/ownership before debiting, without yields; repeated vendor purchases cannot charge again. Style toggles owned gear for free. Current attacks snapshot the server bonus at Begin; re-equipping does not change it mid-beam.

Actual Profiles sanitize/repeated reload/snapshot and actual test-mode autosave/rejoin helpers run against fake stores in `tests/gear_persistence.py`. Test-mode gear purchases do not escape the frozen saved baseline. Save failure behavior remains existing confirmed-snapshot policy: this does not promise a failed unsaved purchase survives restart.

**Release blocker:** schema remains 4 for compatibility with current cap migration. Older schema-4 writers omit the new gear fields and can erase new ownership on save. A profile lease does not solve rolling-version compatibility. Before any publication: drain older writers, back up confirmed records, establish a forward-compatible rollback build preserving the new fields, and run isolated native save/rejoin/fault tests. Never roll live players back to the pre-gear writer after new gear purchases. No live datastore test performed.

## Authored art and import gate
Source: `tools/progression_gear_blender.py`; generated `build/Progression-Gear-Blender.zip`. Vault approved-concepts GEAR-02, 03, 07 and 09 reviewed as actual images; Blender Workflow for Roblox Creators and Exporting and Validating Models for Roblox consulted. Mesh material groups and UVs validated; FBX/GLB both reimported in Blender. Per-piece native `.blend`, FBX, GLB, renders and validation included. Blender render is not Roblox evidence.

A future authorized local Studio test imports with Upload to Roblox OFF, Add to Workspace ON, Package OFF into a disposable place. Stop if upload is required. Inspect warnings, actual stud scale, normals, shading and axes. Copy verified Models to `ServerStorage/GearTemplates` named `MosaicMic`, `StreetBoombox`, `SonicCannon`, `CelestialOrgan`; original replacement names `AcademyMegaphoneAccessory` and `MicroSpeakerAccessory`. Loader clones named template, pivots hand models to palm or Organ to torso back, then sets noncolliding/massless and welds parts. Source model origins are artist-defined; actual R6/R15 grip offsets still need native fitting. No manifest asset path until a verified local import exists.

Test equip/unequip/swap, respawn, R6/R15, template missing, multiple purchases/remote spam, low coins/locked tiers, phone card scrolling, two clients and physical microphone. Confirm asset/material ownership/load and performance before considering removal of fallback geometry. No Studio, upload, publish, GitHub push or desktop checkout change in this pass.
