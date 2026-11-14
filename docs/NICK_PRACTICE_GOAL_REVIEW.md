# Compact Nick practice goal correction

## Reproduction and scope

The actual Residents OwnGoal branch at `0c68c0540eab9a7d098f2f8cfd51437137de7b59` still interpolated Nick's local practice ball to `(628, 2.05, 586)`, outside the compact court. CompactCity moved Nick's station but omitted the original decorative goal and aimed him away from the corresponding endpoint. The pinned historical branch fails the compact endpoint regression. This is source/mocked evidence, not an observed native playtest.

A shared `CompactLayout.Soccer.practiceGoal` now places the endpoint at `(265, 1.05, 287)`. Nick's station remains `(239, 3, 281)` and faces the decorative goal. The original station-relative X/Z offset is retained; original-map mode still uses the exact old endpoint. Three static cosmetic goal Parts mark the new endpoint. They are anchored, noncolliding, nonquery, nontouch and shadowless, with no gameplay descendants or attributes.

OwnGoal duration/interpolation/spin, Miss/Trip routines, distance and activity gates remain unchanged. Personal soccer challenge geometry, scoring, rewards, quest IDs, save data, NPC routes and the archived original map are untouched. The local practice ball is not an authoritative challenge ball and never awards progress. Nominal station-derived trajectory checks include the ball's radius and clearance through the posts/crossbar and within the court, not physical collisions or all possible engine-driven NPC positions.

## Interrupted initialization

Review caught a new lifetime issue from adding Config loading: destruction during either WaitForChild or require could resume into subscriptions because teardown was installed too late. The existing single Destroying hookup now precedes these yields, and each wait/require is followed by a destroyed fence. A stopped script does not continue dependency work or install resident/frame subscriptions. Normal startup and existing teardown remain intact. This is a reproduced coroutine/mock scheduling consequence, not proof the native scheduler exhibits it.

## Vault and verification

Used the already-reviewed vault's `08 Animation/02 Rigging and Importing/Custom Rigs - Weapons and Props.md`, section 7, Common mistakes and Checklist: local world props, range gating and avoiding unnecessary collision/query effects. No imported asset, generator or new dependency was used.

- `tests/nick_practice_goal.py --negative-controls`: 602 actual constructor/animation assertions plus 19 whole-script interrupted/normal startup assertions; all 12 mutation controls pass.
- `tests/nick_practice_goal.py --baseline`: pinned old actual animation branch fails on the compact endpoint as expected.
- Independent review reran those checks and controls, 14 retained Residents lifecycle checks, constructor-derived facing and three-part inventory. Earlier 553 compact construction assertions, 48 static reachability targets and controls remain applicable.
- The standalone debug harness builder now accepts only the exact audited Residents Config-binding chain at the exact source path. It resolves Config synchronously from the bundle rather than requiring external Shared/Config instances. Ten resolver contracts, including seven rejected bindings, pass and were independently rerun; the generated animation bundle matches a fresh independent assembly. Unknown or altered forms still fail closed; this harness cannot prove normal dependency loading.
- After correcting that builder compatibility failure, the final full aggregate passes 25 pure/synthetic suites, 107 mocked suites, 63 production compiles and all configured local builds. Exact commands, hashes and scope are in `tests/evidence/nick-practice-goal-2026-11-12.json`.

No Studio launch/native rendering, physics or user route-comprehension validation occurred. Real microphone, multiplayer, device and mixed-version writer gates remain open. No live DataStore, purchase, audio configuration, publication or GitHub push occurred. The local checkpoint remains subject to the existing explicit push-confirmation hold.
