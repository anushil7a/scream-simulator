# Opt-in local route renderer

Local candidate, November 16. `NavigationGuide` accepts an explicitly chosen world position. It creates eighteen small static gold ground markers, no GUI controls, arrows through walls, lights, pulsing, character movement, remotes or save fields. Existing decorative city guidance is untouched. Static presentation is also the reduced-motion presentation.

`new(ownerGui)`, `SetTarget({position,label})`, `Clear()`, `Step(root,now,visible)`, `Destroy()`. `GetStatus()` returns status text, distance in studs, and cardinal bearing (world north = -Z). The owning UI supplies selection and clear controls. Arrival hides the trail without changing the user's choice.

Successful paths alone produce dots. Async requests are single-flight with generation guards, three-second minimum retries, eight-second route age and twenty-stud deviation invalidation. Current streamed geometry is ray checked on each displayed segment at most every 150ms; missing ground stops the visible trail. Failed or incomplete paths show honest unavailable status and distance/bearing, not a fabricated straight path. Character replacement, owner destruction, stale completion and path blockage are handled locally.

Relevant guidance: project AGENTS/ROADMAP, carried vault map-marker and small-screen guidance in SMALL_SCREEN_MAP_REVIEW, and COMPACT_GUIDANCE_REVIEW. Existing quest/world coordinates are supplied by the separate catalog. Creator Hub pathfinding documents StreamingEnabled client limitations: https://create.roblox.com/docs/characters/pathfinding . Client computation can fail for distant streamed-out goals; distance/bearing is informational, not a guaranteed traversable direction.

Evidence: 29 deterministic production-module tests with Roblox service/vector doubles; production Luau compile. Tests cover no default target, async supersession, failure, blocked wall, missing ground, root replacement, owner destruction, allocation bound, arrival, invalid input, throttling, stable path retention, expiry and deviation. This does not establish native pathfinding success or actual collision/streaming behavior. Before release: disposable Studio walk-through with obstacles, distant streaming, respawn, phone/touch and both accessibility settings. No upload/publication or external push.

## Import/playtest QA follow-up

Three targeted production-module regressions were reproduced before fixing them:

- Deferred path computation lasting over eight seconds immediately expired on the next frame because route age started at request time. Age now starts at the latest observed client frame at completion; the normal eight-second refresh remains.
- A newly streamed low barrier between dots was invisible to the original chest-height segment ray. A second, foot-height ray now rejects that trail. This is conservative point-ray clearance, not a native humanoid/capsule collision proof; stairs/uneven terrain still require Studio acceptance.
- The identical exclusion list was rebuilt every draw. It now changes only when the character identity changes (and resets on clear). Draw cadence remains 150ms with eighteen markers and at most 54 rays per full draw, including floor checks. No native performance speedup is claimed.

Evidence: 38 production-module mocked checks, 20 actual selection lifecycle checks, catalog checks and production Luau compile pass. Deferred computation, low-wall and filter-reuse tests each failed before their fixes. Existing corner, supersession, clear, respawn and no-default-selection checks remain passing. No desktop session, upload, publication or external push.

Remaining UI finding passed to integration owner: touch landscape 844×390 hides the selected-guide HUD because `trackedY+118=278` exceeds the reserved bottom boundary `390-260=130`. On a failed distant route this also hides distance/bearing; users can still clear/change via the full Map. No Client layout was changed in this route-only patch. Next: provide non-overlapping short-viewport feedback and validate real streamed corners/stairs with native Studio.
