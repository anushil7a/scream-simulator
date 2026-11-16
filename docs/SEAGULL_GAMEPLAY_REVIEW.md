# Seagull Siren Captain gameplay replacement

Selected replacement from the owner’s vault: white seabird pirate captain with cutlass/hook/peg leg and twin brass shoulder megaphones. Uses the existing reviewed vault boss telegraph guidance: readable fixed footprints, full committed warning and recovery, no attacks against nonparticipants. Geometry and anatomy pose changes are a separate coordinated art commit.

## Preserved encounter contract
Stable internal id `leviathan`; exact level70, home(420,0,420), ring22, health1280, damage36, coins95, XP340, tell2.25s, interval5.75s, scale1.4, patrol4studs. No save/migration, reward, arena, respawn, admission or HUD changes. Name is now Seagull Siren Captain; warning/boundary color is warm brass. Existing world nameplate, navigation list and guide resolve their public name from BossCatalog, so no duplicated name strings require editing. Internal old key intentionally remains private plumbing.

## Two alternating patterns
1. Cutlass broadside:24stud transverse width ×5stud depth, centered8studs in front of captured aim. Retreat or sidestep outside the visible bar. No sweep that follows the player.
2. Twin sirens: two4×24 lanes centered6studs left/right of captured aim.8stud center gap is safe, as is beyond the lane ends. This differs from Ignis's three fixed-axis lanes: the captain aims two shoulder channels around the captured direction and explicitly offers a central safe corridor.

Both commit at the original tell start, translated once from frozen boss ground position; every true corner plus4stud patrol leash stays within22. At most2 temporary hazard parts, at most one damage application per participant. Existing fixed participant snapshot, late-join protection, cancellation and recovery are unchanged.

## Evidence
8129 actual-source service/motion assertions +10 Bootstrap callback checks passed (lower than previous suite because the16-segment sonar attack is removed). New tests check exact preserved balance/location, name, distinct shapes, broadside hit/retreat, and siren lane/gap/outer escape at four aim angles. Boss balance estimates, actual boss aim/cover checks, and navigation catalog checks passed; navigation explicitly verifies public Captain name with stable old selection key. Native shape readability/animation/playtest remains pending. No upload/push/publication.
