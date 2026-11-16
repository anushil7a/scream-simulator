# Wider moving boss encounter candidate

## Intent and references
Applied the actual vault `Boss Fight Design Patterns` and `Boss Animation and Phases` notes already read from Sameer-PC: readable committed tells, no last-moment tracking, a punish/recovery window, authoritative combat separate from cosmetic motion, and sufficient space for large bodies. No new imported assets or animations are required by the server.

## Authoritative contract
- All five catalog radii are22studs; level, health, damage, reward, cooldown and respawn values unchanged. Fixed home is Catalog x/y/z. Horizontal admission is measured from this home, never the moving Core. Height tolerance remains±12. Visible boundary and world text use the same22 value. No enemy-health HUD.
- Catalog `moveLeash=4`, `moveSpeed=2`, `recovery=.6`. Pure `BossMotion` follows eight deterministic waypoints with straight chords inside the4stud disk. The server's10Hz step caps elapsed movement time at.25seconds so a delayed tick cannot teleport or catch up through players.
- Core.CFrame carries actual root position and heading. Ground pose is Core.Position minus aimHeight(7); scale remains1.4. Invisible Core remains anchored, noncolliding and nonqueryable; it does not push or damage casual passersby. Targeting still uses the actual Core/body aim samples.
- During a cast the boss faces its selected participant once, stops and holds position/yaw for the entire tell and0.6second recovery. There is no pursuit or continuously tracked aim.
- Attack shapes are generated relative to the frozen body ground position and translated once to fixed-home coordinates. Their rendered geometry and authoritative hit math remain identical. The largest true pattern extent plus4stud movement fits22. Floor markers do not follow subsequent root/player motion.
- Model attributes: `BossState` = Idle/Moving/Windup/Recovery/Defeated; `BossStateAt` = shared server time at transition; `BossWindupUntil` = shared deadline during Windup, otherwise0. Attributes only change on transitions. Client presentation is a separately coordinated change.
- KO immediately enters Defeated and cancels warning; corpse does not patrol. Respawn resets the motion state and pose to home. Quiet reset clears combat normally; idle patrol resumes without teleporting. No contributors means no attack; departure/identity/range rules and late-join protection remain intact.

## Spatial and regression evidence
Map QA reported468 polar floor samples per boss from center throughradius24 (22 plus2stud avatar margin), all flat within.5stud. Inner10stud visual volume clear. Nearest shrine solid begins28studs from home, leaving6studs outside the new ring. Existing homes need no movement. This is source geometry QA, not native character/camera proof.

Actual-source tests cover deterministic500-step paths per boss, leash and speed limits, stalled-tick cap, every translated hazard corner/disk, fixed home admission while moving, frozen root and markers, recovery/resume, dead freeze and clean respawn.8313 service/motion assertions +10 Bootstrap callback checks pass. Five balance estimates unchanged. Full local gate passed26 pure/synthetic +149 mocked suites, production compilation and disposable builds. Native walk/aim, multiplayer replication/interpolation, animation appearance, phone performance and camera review remain required; no native claim, upload, push or publication.
