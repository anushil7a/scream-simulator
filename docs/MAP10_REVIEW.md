# Map10 full replacement, local staged candidate

Actual reference viewed: `MAP-10_Master_Overworld_Blueprint.jpg` in the approved vault Map concepts. This is not a reskin or the earlier wide coastal preview. Original procedural geometry replaces the active compact city: northwest teal pavilion academy/fountain; southwest octagonal PvP stadium; north purple speaker amphitheatre; central garden/market terrace; eastern volcanic district with bridges and branching cosmetic lava; northeast tethered floating crystal shrine; southeast palm football grove; southern waterfront and dock. Reference contains no unambiguous numeric world dimensions; this implementation uses original gameplay-scaled proportions, not claimed exact dimensions.

Consulted vault make-map skill, simulator style and QA guide, plus level-flow/arena notes through reference reviewer. Used readable landmarks, looped routes, wide ramps, separated opt-in boss pads, restrained static part budget. No third-party models/scripts/textures imported; no destruction, publishing or asset uploads.

## Coordinates and compatibility
`CompactLayout`/`CompactCity` names remain compatibility entrypoints; their contents now describe Map10. All prior compact runtime source is preserved exactly in `prototypes/preserved-compact-city/`; the older original city/archive is unchanged.

- Terrain levels0/16/32, shrine64; spawn(-300,36,-260). BoundsX[-600,600],Z[-600,660]. Current streaming64min/512target remains configured, not measured.
- BossHomes supply x/groundY/z; runtime BossService must consume optional y (separate integration track). SupportHomes keyed901–904; World calls supporting AtHome adapter (separate integration track).
- Trainer and seed placement now use ground height. World grounding decision uses real ground gap and Map10 maximum height instead of incorrectly recovering everyone aboveY8. Legacy map behavior preserved.
- Quest IDs and assignments preserved. Soccer rigid translation(+25,+54.5); volley(+100,+90), all relative distances/heights retained. Timed sprint remains440studs along a clear coastal lane. Delivery stops remain below90-second walking budget by static route distance, pending native timing.
- Place/boss guide targets use elevation; minimap regions/roads reflect island. PvP square atX[-420,-240],Z[30,210],Ymax14 so elevated garden fringe cannot silently become PvP.

## Evidence and limits
- `tests/map10_contract.py`: stdlib-only668checks of source/IDs/rigid sports migration/route widths/grades/budget.
- `tests/map10_grounding.py`:10actual grounding-decision checks with mocked positions, including ground16/32/64 and legacy branch.
- `tests/map10_geometry.py`: optional NumPy static5-stud OBB heightfield, max2.5step, upward normal>=.7. Passes21destinations plus16ramp/bridge endpoints including shrine. This is conservative top-surface routing, not native navigation or avatar-radius proof. `prototypes/map10/static_walk_checks.json` holds results.
-601original static geometry parts; Luau compilation and Rojo build pass. `build/Map10LocalCandidate.rbxl` is an unpublished local build, not a native-play claim; final integration must include root's save-isolation guard and elevation adapters.
- `tools/render_map10.py` creates Blender geometry-proxy hero/top-down/spawn renders and editable composition. Not native Studio screenshots. Actual Roblox rendering/materials and streaming remain unverified.

Staged acceptance gaps: native two-round screenshot/rubric and walk-through (especially narrow joins, shore recovery, shrine route), radius/collision probes, NPC real paths,90sdelivery/25ssprint timing, sports and two-client encounters, phone/streaming performance. Current original art is a low-poly interpretation with simplified roofs/rock/crystals and straight route segments, not reference-exact finished environmental art. Hero review caught/fixed broad coplanar coastal sheets, shrine overlap and a blocked volcanic landing. No claim of full visual/native acceptance.
