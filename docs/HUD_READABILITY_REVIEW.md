# Compact status-panel hierarchy

The status panel gives level, coins and health separate visual roles. Level has a gold badge, coins retain their exact right-aligned value, and health has a larger number above a full-width green track. The quieter XP track remains below its existing XP/save-status text.

The panel remains 242×94. Its external placement, visibility, Humanoid health precedence, missing-character value retention, XP calculations, save-warning wording and update cadence are preserved. The change adds no assets, events, animation or health thresholds.

This addresses flat visual hierarchy seen in the prior native reference; no clipping defect was established from that image.

## Reference used

Targeted local vault reading: `05 UI and UX/HUD Design.md`, sections 1–2 (grouped status and overlap); `Responsive UI for Phone Tablet Console and PC.md`, TLDR (legible type and measured layouts); `UI Design Systems.md`, section 1 (semantic roles, type and spacing). These references guided the existing navy, gold and green panel rather than changing the project architecture.

## Verification

- The focused actual-source comparison passes 1,157 assertions and 11 negative controls. Its published `5622daa` baseline has identical scoped HUD/update/placement excerpts; this is not whole-Client equality. Existing health and warning checks pass. Two State fixtures now give the new coin label its own namespace, preserving their server reward helpers and assertions. Presentation mutations are scoped to the actual helper they exercise.
- All 250 aggregate/build commands pass: 25 pure/synthetic suites, 139 mocked suites and 64 production compiles. All 343 selected input hashes were unchanged and rechecked. The small native unit builder was created afterward and separately compiled and reviewed. [Portable evidence](../tests/evidence/hud-readability-2026-11-13.json).
- Local Studio verified GameId=0 and PlaceId=0, reread all three installed source payloads, and produced six matched viewport images. All 12 After text fields in these main samples fit, including `450/450` and the deliberately large exact coin value. Ten additional snapshots cover death, missing-character retention and save-warning states. Astra independently reviewed source, tests, fixtures, results and images.
- The native unit deliberately places the actual HUD excerpts at a fixed visible position. Logical widths are not physical-device or responsive-placement acceptance. A larger full-Client comparison place was built and reviewed, but its direct launch exposed no new window or MCP session during this pass; it was not played. The native images retain faint older-fixture HUD context behind the partially transparent panel.
- The long `RECOVERED` warning reports `TextFits=false` in both Before and After with its unchanged 204×19 allocation. Other sampled XP/temporary/delayed states fit. This existing warning limitation remains open.
- New/old fixture runtime cleanup was verified, Play stopped, and the three injected owned sources were removed. Existing minimized review windows were preserved. A new task-launched Studio process exposed no window/session and was left intact rather than forcibly terminated. Physical devices, real microphones, multiplayer, persistence and live services remain unverified.

| Sample | Before | After |
|---|---|---|
| Low health, logical width 320 | [Before](images/hud-readability-2026-11-13/320-low-Before.jpg) | [After](images/hud-readability-2026-11-13/320-low-After.jpg) |
| Level 100 and large exact coins, logical width 390 | [Before](images/hud-readability-2026-11-13/390-large-Before.jpg) | [After](images/hud-readability-2026-11-13/390-large-After.jpg) |
| Full health, logical width 1280 | [Before](images/hud-readability-2026-11-13/1280-full-Before.jpg) | [After](images/hud-readability-2026-11-13/1280-full-After.jpg) |

The production Client normalized SHA256 is `8584ef00d84a3b9a14ff232aa09a81419f72a7b7abb73751a4540182ffbc6674`. No Roblox publication or release merge occurred. The preceding approved shop checkpoint and this change remain local while the standard GitHub push cannot resolve `github.com`.
