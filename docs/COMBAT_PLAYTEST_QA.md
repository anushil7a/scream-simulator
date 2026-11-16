# Combat integration QA, November 16

Read current roadmap, boss encounter review, supporting NPC review and actual Equipment/Boss source. Reused previously consulted actual vault Boss Fight Design Patterns and canonical boss/gear/NPC guidance; no new concepts or balance changes introduced.

## Reproduced and fixed

Actual-source `tests/boss_service.py` instrumentation counted 500 label Text assignments for five idle bosses over 100 scheduled ticks. New failing assertion caught this baseline. Cached static label strings, change-only property assignments, second-granularity countdown strings and reusable per-boss target arrays reduce this to five initial assignments for the same trace. Five arrays replace 500 empty table allocations; fully idle encounters skip target work. KO clears the retained arrays to release player/context references. No timings, damage, reward, opt-in or geometry rules changed.

Focused service/callback tests now pass 170 assertions plus combat wiring contracts. Existing catalog/assist/overkill/session/escape/dodge/protection/reset/respawn tests preserved. Actual Equipment template/fallback/weld/respawn tests and 133 support NPC model/route assertions passed; no additional concrete defect found in that bounded review. This is not exhaustive validation.

Full local verification: 27 pure/synthetic +149 mocked suites, production compilation and disposable builds. Native Studio, mesh import, real microphone, phone and multiplayer performance remain outside this QA. Reduced property-write/allocation counts are deterministic mock evidence, not measured Roblox network or frame-time savings.
