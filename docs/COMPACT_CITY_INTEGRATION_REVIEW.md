# Compact city gameplay integration

## Scope and preserved original

Current unpublished candidate selects the 720 x 600 compact city. The exact original runtime source at `72c886cb6f8a60ab26dff962e28da77e4b2d4609` remains in `assets/drafts/original-city-2026-11-11/`, with byte-checked source ZIP, guarded local place files and restore instructions. No archived source/artifact was edited. This is preservation of repository-generated content, not live/unsaved Studio work or external asset contents.

`CompactLayout.luau` is the shared runtime coordinate source. The historical `prototypes/compact-city/layout.json` and its geometry-only project remain a design preview, not a second runtime configuration. Runtime refinements include accessible garden prompts, closer practice target, explicit wayfinding, full-sized Nick court and relocated lifeguard lookout.

## Coordinated behavior

- Current Config selects compact map/arena bounds. City delegates to the compact generator. Spawn, four general residents, seven workers/quest givers and three copied trainer tiers use compact locations; original tier rewards/health/levels are unchanged. No old traffic or parked cars are created in this pedestrian layout.
- Training pads retain the original 32-stud 3D eligibility, 18-stud roaming, 22-stud recovery, strike/reward/reset/respawn rules. Actual floor-height offsets are adjusted to the compact ground, without mutating the shared tier definitions.
- Full map and minimap use the compact projection, actual shared roads/beach/landmarks and Config arena bounds. Marker direction, lifecycle clearing and update throttling remain. Old projection is retained only for the inactive original-city branch.
- Eight saved quest IDs, marker IDs and delivery IDs are preserved. Garden prompts stand in front of their beds rather than inside raised geometry. Coffee pickup is at the market; race begins beside the relocated lookout and ends 440 studs east. Timers/rewards remain 25 seconds for race and 90 for deliveries. The race is shorter than its former 480-stud route; its difficulty is not claimed identical.
- Nick's 112 x 85 authoritative court dimensions and relative gates/cones/targets are translated intact. Soccer lost balls, active-distance checks, bounds and hints match the new world. Volleyball dimensions, net checks, player eligibility and serve location match the new court. Ball/net heights are lowered with the one-stud ground change; speeds, gravity, timers and rewards remain unchanged.
- Compact out-of-bounds rescue clears the avatar's own seat weld and movement state, zeroes velocities, restores automatic network ownership where applicable, then returns to protected spawn. It does not erase charge/cooldown budgets.
- Practice target is collidable because authoritative beam raycasts respect collision. The stand line lies within the conservative starter range; target feedback/FirstBeam achievement use existing server logic. Bounded practice, spawn and arena signs supply actual wayfinding.

## Object destruction is excluded

The latest owner direction supersedes earlier map-destruction plans. Config disables object destruction. Bootstrap does not start/register the destruction service, offer object targets, damage obstruction objects or perform maintenance. Compact geometry has no destruction tags/health attributes. The collection UI no longer advertises destruction tiers. Static walls/cover continue to stop beams. Legacy code and the exact original archive remain for history, not an enabled feature; no repair or destruction objective is reintroduced.

## Checks and limitations

Final local verification passes 25 pure/synthetic suites, 77 mocked-service suites, 59 production compiles and all candidate/disposable builds. Focused checks pass 450 world-construction, 102 CityMap, 110 integration and 19 fixture-cleanup assertions, plus 48 static reachability targets and 29 negative controls. Independent review found no production blocker. It corrected native-fixture path policy/elevation and cleanup weaknesses before build; this does not substitute for native execution.

Actual modules are executed with mocked engine objects; corridor/interaction reachability uses instantiated geometry and explicit clearance. These are not native pathfinding or physical walking results. Tests preserve profile/quest data and exercise matched client/server spatial rules, movement reset and disabled-destruction guards with targeted negative controls. Final counts/source hashes and native fixture build status are in `tests/evidence/compact-city-integration-2026-11-11.json`.

A separate local-only native fixture is prepared using actual Bootstrap and geometry, temporary profiles and synthetic server helper inputs. Its compilation/build alone does not validate execution. The ordinary source candidate has normal profiles and must not be used as a save sandbox; `SustainedLocalPlay` and the dedicated compact fixture are guarded local-only artifacts.

At the current access check Studio was closed, with the same three prior minimized app-picker windows. Supported control refused the picker as minimized and exposed no restore operation; no additional app was launched. Native geometry/collision/pathfinding, visible label/map readability, player input, real voice, live saves, sports difficulty, multiplayer pushing/combat and representative performance remain unverified. No publication, audio/product configuration, live DataStore activity or external release occurred.
