# Supporting residents, November 16

Original compact-city adaptations after reading actual vault NPC-05 DJ Marina, NPC-07 Tinker Sparks, NPC-08 Lifeguard Kai, and NPC-09 Archivist Lyra concept images, plus NPC AI and Behaviour / Character and Creature Pipeline guidance. No third-party model or image incorporated.

| Resident | Stable ID | X, Z | Purpose |
|---|---|---|---|
| DJ Marina | Bot901 | -90, 190 | Comfortable voice / reactive meter coaching; points to Eric's existing crowd task |
| Tinker Sparks | Bot902 | 70, -225 | Existing Vendor shop; upgrade advice and Pau delivery referral |
| Lifeguard Kai | Bot903 | -205, 210 | Promenade/court directions, existing sprint/coach referrals |
| Archivist Lyra | Bot904 | -290, 65 | Training/style progression and boss directions |

All spawn after pre-existing trainers, with fixed one-station jobs using the existing interrupted-route/recovery lifecycle. Existing workers, quest ownership, IDs, saves and combat logic are unchanged. No new task rewards or purchases introduced. Cosmetics are welded noncolliding original native-part fallback interpretations, not imported Blender assets or claimed final artwork. The NPCs use normal existing conversational ownership/cooldown/range gates. Context-specific quest text remains higher priority than authored idle dialogue. No screen HUD changes.

Validation: actual roster/outfit mock execution (133 assertions), actual compact geometry construction and 51 clearance targets (includes all four new homes), existing constructor differential (702,258 assertions), root integration (577). These establish code/geometry contracts, not native pathfinding or final appearance. Native Studio walk-up, dialogue readability, body collision, respawn, multiplayer conversation and performance still require playtesting. Full aggregate passes 25 pure/synthetic +142 mocked suites and all local builds (before return-fix; constructor regression rerun after fix). A deliberately removed constructor return is now rejected by a negative control.

`tools/supporting_npc_models.py` generates four original static block-model looks from the actual tested cosmetic geometry: per-resident FBX/GLB, `SupportingResidents.blend`, JSON manifest and `roster.png`. Preview inspected. These are unrigged import-ready look assets, not production mesh integration or reference-quality final art. Existing R6 animation/hitboxes remain in game; native import/rig fit must be checked before swapping looks. No Blender application window was opened (background process exited).
