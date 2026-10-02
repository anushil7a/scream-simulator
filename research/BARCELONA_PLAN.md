# Barcelona redesign plan

## Spatial design

Playable land: x -720..720, z -600..600 (1440 × 1200). Central PvP district: x -480..480, z -360..360 (960 × 720): exactly 40% of the land rectangle. Remaining 60% is safe. Decorative ocean is excluded. Safe spawn in the southwest neighborhood, outside traffic lanes. PvP borders follow broad avenues, indicated with paving accents and sidewalk signs; no road-spanning signs or upgrade objects.

Distinct destinations: chamfered Eixample perimeter blocks with interior gardens; shaded rambla pedestrian promenade; old-town alleys and covered market; a civic square with fountain; a basilica-inspired skyline landmark; Mediterranean beachfront, café terraces, volleyball, pier and lifeguard station. Warm stone/plaster, terracotta roofs, narrow balconies, shutters, arcades, wrought-iron details, patterned paving. Tall landmarks form a skyline instead of a continuous wall of identical skyscrapers. Traffic stays on outer boulevards. Streets and plazas get different building footprints, heights, shopfronts and gathering activities.

## Gameplay

- Six forward beams with increasing travel distance and width, wall occlusion, no rear/radial damage. Server chooses origin/facing and validates victims. Effects match the hit volume.
- Grounded 0.6s forward tumble with curled limbs and 4s cooldown. Collision sweeps remain active throughout movement.
- Cars have solid simplified hulls. Swept impact detection applies bounded damage and temporary knockdown with recovery/cooldown; protection and incapacitation respected.
- Health grows 8 per level: 100 at level 1, 332 at level 30. Heal restores 20% of current max. UI reflects actual maximum.
- Reduce residents from 114 to 42. Noncolliding NPC groups avoid crowd stacking; ground sampling and recovery prevent floating. Walking uses horizontal velocity, stable feet, no repeated jump recovery. NPCs choose local activities and conversations.
- Preserve XP, quests, compact menus, five-second protection and temporary public test tools. Relocate quest objects and update map/directions.

## Verification

Compile all scripts, build place files, inspect city from above and at player height, verify clear street lanes, sample NPC grounding/movement over time, test beam front/behind/width/range/wall behavior, level health, rolling/cooldown/collision, parked car blocking and moving car damage/knockdown/recovery. Exercise representative quests after relocation. Test desktop and phone UI. Publish only after fixes, reopen cloud place and verify new source/version.

## Sources and download review

- https://bid.barcelonaturisme.com/wv3/en/page/19/eixample.html — chamfered grid, modernista architecture, promenades.
- https://www.barcelonaturisme.com/wv3/fr/page/2213/la-barceloneta.html — maritime quarter, low buildings, narrow streets, balconies, beachfront.
- https://www.lapedrera.com/en/casa-mila/architecture/ — sculptural stone facades, wrought-iron balconies, roofscape (search excerpt; direct fetch timed out).
- https://github.com/rojo-rbx/rojo — 1,747 stars via GitHub API 2026-09-23, MPL-2.0; existing local build tool reused. No new executable download.
- https://github.com/domlysz/BlenderGIS — 9,407 stars; four plain-text reference/source files downloaded over verified HTTPS at commit 2add45ffec547f419cc77563a7fe976fd6c8f0c4. Entry-point lines 131–134 replace the default HTTPS context with an unverified context. Not installed or executed. A partial source review is not a whole-repository safety guarantee. No third-party code is imported into the Roblox game.
- NevermoreEngine (612), Roblox creator-docs (839), and RbxUtil (462 in fetched GitHub page) do not meet the requested >1,000-star threshold.

The Roblox city is original procedural geometry inspired by these references, not copied GIS imagery or a scale reproduction.

## Completion audit — published v32

Roblox Studio reported PublishSuccessful at 2026-09-24 02:59:54 UTC. Closed the place and reopened the cloud Recent entry; game.PlaceId=122465114514497 and game.PlaceVersion=32. The fresh cloud source contains TorreLlumQuarter, the roll animation, the four-second vehicle impact cooldown, level-30 health 332, beam range 112, and central arena bounds (-480,-360)..(480,360). Generated world has 45,741 descendants, including 42 humanoid residents. HTTP requests are disabled after source synchronization.

Actual Studio checks: directional beam front hit / rear and side miss; wall occlusion; 100-stud target hit with top tier; health scaling; full-body roll joint transforms; roll stopped by parked-car hull; moving impact damage/knockdown/recovery; 672 NPC ground samples without floating; relocated beach and delivery prompts. All ten scripts compile and both local place builds succeed. City views inspected at street height and overhead. Road signs are facade or pedestrian-corner mounted; old upgrade/discovery objects were removed with the previous city generator. No third-party executable code was installed.

Limits: visual quality is a stylized Barcelona-inspired interpretation. Multiplayer balance, low-end device performance, and live data persistence still benefit from a friend playtest. Studio persistence was not enabled merely for testing.
