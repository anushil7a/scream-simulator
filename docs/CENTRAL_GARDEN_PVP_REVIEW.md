# Central green PvP zone trial

Baseline: `b0334a2` full game's Map10, not the standalone Rambla review. The large olive terrace by the market consists of five green platforms with a y=16 walking surface. The existing west stadium is a separate tan floor; it remains PvP.

## Fixed gates and boundaries

| ID | Original evidence and player impact | Acceptance |
| --- | --- | --- |
| PVP-01 / MAJOR | Green terrace is outside the original stadium-only authority bounds, including the visible green strip next to the west ramp. Enlarging the stadium rectangle would incorrectly admit unconnected levels and traffic. | Follow the five green surfaces, including the original notches. Keep the visibly paved café spine and the Academy and Volcano connector ramp footprints safe; leave the west and coast ramp notches safe. All standard PvP protection, line of sight, dodge, ejection and rewards remain unchanged. |
| PVP-02 / MAJOR | The old map renders just one arena rectangle; desktop PvP status only knows Arena District. A second shape must not disagree with the authority boundary. | Map overlays and non-blocking outline use the same authored geometry. Both full map/minimap render the new shape without strip seams. HUD label responds at the actual boundary. Marker parts do not collide, contribute cover, or interrupt traversals. |
| PVP-03 / MAJOR | Café/Tinker share a pale path through the terrace. Broad height/plan extents can invade the upper Academy, the western coach, sports, or boss circuits. | Keep the quest/merchant path, spawn, coach, training areas, other districts and all five arena volumes protected; avoid vertical leakage. No new zone on the standalone art trials. |

Original policy checks both player endpoints and the existing cover test. Anyone standing on the safe path is protected; the path is not a wall between two active PvP players. Reference: vault MAP-10 v2.1 agent build instructions (walkable connections and collision budgets), the full map/current CompactLayout plus exact visual geometry. Retain the old user-approved map art and all quest content.

## Candidate and focused verification

Source commit `8fa16ce`. Normal playable `ScreamSimulatorCentralGardenPvP.rbxl` SHA-256 `0faaa1853bf2eba0b83be4b6c43be6f4c8d3323ba33ad4028da2a59656394c03`. Exact separate guarded QA place `CentralPvpLocalReview.rbxl` SHA-256 `66792f322832fce641584083f1192af17030a1a230203c0c55a44452ea4dbee4` and runtime source stamp `1493e59e384bb311b8cf80677540175ef7dab4d4021c995ba8596b63097e48f5`. Both compiled without publication.

- 15 disjoint rectangles, 24 shared exterior segments; geometry, marking and combat authority 716,177 assertions against authored source. Projection/HUD 14,868 assertions and two negative controls. Focused previous map contracts/grounding/repair, TTK, PvP reward, capture gates and TestFlight regressions pass.
- Independent critic reviewed both code paths, actual source checks, safe transition asymmetry and projection. It passed source review, not runtime validation. Core combat systems and balance are unchanged. Physical phones, live voice, live saves and the full-game quality gates are separate scopes.

Studio exact QA, two actual local Player instances, PlaceId/GameId 0/0: log `0.748.0.7481526_20261119T014203Z_Studio_72219_last.log`, 01:43:05.470 UTC. `CENTRAL_PVP_DONE true 8`: north/south garden and prior west stadium each accepted exactly 3 HP in a single sampled synthetic full-power server tick. Garden-to-safe, safe-to-garden, both-safe, above and below all did zero. This tests true two-client server authority and terrain/cover at the sampled points, not human voice or crossing during an already-active beam. The independent critic accepted the sampled authoritative boundary.

Observed on the same exact v2 QA client: after a disclosed start position, Player2's native Humanoid walked from (46,19.80,88.69) across the visible narrow ground line to z107.19 and back to z88.69. There was no boundary teleport; temporary server ownership for the movement check was restored to automatic. The status changed Garden PvP On → Safe PvP Off on café paving → Garden PvP On on return. The full map showed the split red overlay, cream gap, visible landmark/boss pins and exact help text; minimap showed the gap from both walk endpoints. This is one representative route, not blanket visual acceptance of all world edges.
