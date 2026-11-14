# High-tier beam clarity — November 13, 2026

Levels 80–100 now have a clear bright spine and one bright collar, with quieter supporting contours and a more transparent beam body. This reduces the white lattice and exposes more of the target and confirmed-hit burst in the matched native views. The large round L80 collar, L90 star and L100 counter-winding braid keep their authored shapes and scale. L70 is still brighter/busier than L80; this pass does not establish monotonic brightness or universal target visibility.

Only `BeamVisuals.luau` changes in production relative to saved `b76c94f`. Near, detailed high-tier outer/inner body transparency becomes .78/.70. Supporting collars are thinner, darker and translucent; ribbons and sparks use quieter SmoothPlastic surfaces. The first collar, hot spine, emitter/endpoint cores, all authored profile paths/counts and beam core widths, contacts, levels 1–79, Reduced/far rendering, shared 512-Part budget and gameplay remain intact. No new assets, screen flashes or camera shake. Vault guidance consulted before editing: `Escalation and Grandeur Without Clutter` §§1/6 and `VFX Readability and Value — Lessons from Blind Reviews` §§1/2/4/7.

## Matched native evidence

These are raw Studio captures, copied byte-for-byte. Each pair has the same camera, target, HUD, Gold aura, explicit beam/contact timestamps and fixture backdrop. Contact is injected in both modes, rather than supplied by a real hit event.

| Sample | Saved b76 baseline | Final renderer |
|---|---|---|
| L80 round, front, contact age .16s | [Before](images/high-tier-2026-11-13/80-hit-Before.jpg) | [After](images/high-tier-2026-11-13/80-hit-After.jpg) |
| L90 star, front, .16s | [Before](images/high-tier-2026-11-13/90-hit-Before.jpg) | [After](images/high-tier-2026-11-13/90-hit-After.jpg) |
| L100 braid, front, .16s | [Before](images/high-tier-2026-11-13/100-hit-Before.jpg) | [After](images/high-tier-2026-11-13/100-hit-After.jpg) |
| L100, expired contact .29s | [Before](images/high-tier-2026-11-13/100-clear-Before.jpg) | [After](images/high-tier-2026-11-13/100-clear-After.jpg) |
| L100, dark backdrop, oblique, .06s | [Before](images/high-tier-2026-11-13/100-dark-Before.jpg) | [After](images/high-tier-2026-11-13/100-dark-After.jpg) |
| L100 Reduced control, .16s | [Before](images/high-tier-2026-11-13/100-quiet-Before.jpg) | [After](images/high-tier-2026-11-13/100-quiet-After.jpg) |
| L70 control, .16s | [Before](images/high-tier-2026-11-13/70-control-Before.jpg) | [After](images/high-tier-2026-11-13/70-control-After.jpg) |

Root and independent Astra inspection accepted the scoped high-tier improvement. The dark torso/arm outline and hit tips read better, especially obliquely; supporting star/braid paths remain visible. The actual lock caption/button fit in all 14 observations, with marker and lock retained. Counts match each baseline: 67/77/77 core/tier Parts at L80/90/100, 55 at L70 and four in Reduced; contact adds 16/eight/zero Parts when regular/reduced/expired. Contact properties/positions match pairwise.

The final standalone-module control captures are **not pixel-identical**: L70's After spine looks brighter and Reduced After looks yellower. Tests establish unchanged source/property behavior for these paths, but the cause of the native appearance variance is unverified. Transparent-part composition/order is only a hypothesis. Do not use these images to claim visually identical controls. Reduced retains its existing frontal body masking.

## Provenance and checks

Final renderer SHA256: `cd708090ff3a504afee6e7cd99208cb7df13a0a566900d69cd07271f02ddf2e9`. Native execution used the previously opened disposable `HighTierReview-body-local.rbxl` (SHA256 `2cd3b6e303316f30d605802010117d443a4e3812ce670910303913df23ec90d5`) for actual City/HUD/lock/target setup, plus a separately verified 9,534-byte current renderer ModuleScript. Six loaded source bindings were independently reread before Play. Every test/control call checked local `GameId=0`, `PlaceId=0`.

The probe used b76 for Before; its exact renderer is now retained in the hash-checked [portable fixture](../tests/fixtures/nov13-contact-baseline/manifest.json). For After, it hides baseline visual Parts while preserving their cleanup ownership, then runs the exact current standalone renderer with identical inputs. Both pools and fixture are retired afterward. Allocation counters describe the active standalone renderer, not total hidden probe objects or measured performance. Full current bundle `879ce011a7ed397b159459700bfa45dd0eaa84c5874f615414e7935cd686444d` was built/compiled but was **not** the final native-loaded bundle: its direct-open process exposed no session/window. A 226,596-character bundled Source assignment exceeded Studio's 200,000 limit and left the old Source unchanged; no Play or permission change followed that failed assignment.

All **248 final local commands passed**, including 25 pure suites, 137 mocked suites, 64 production compiles and disposable builds. All **337 input hashes** were rechecked unchanged. Focused checks/negative controls: high-tier 136,713/11; contact renderer 102,647/14; silhouette 824/7; milestone silhouettes 4,487/8. Differential tests protect beam core geometry/physics, authored profile coordinates/counts, lower tiers, Reduced/far, exact contact properties and budget behavior, allowing only the explicit high-tier styling changes. Astra independently reviewed source, fixture/probe lifecycle and all final images. [Portable integration evidence](NOVEMBER13_INTEGRATION_REVIEW.md) records the published input hashes, portable baselines and integration checks. Full machine-local reports remain private.

The accepted final source and images are retained here. Earlier diagnostic prototypes remain local and are not the published candidate.

## Limits and cleanup

Frozen timestamps, fake microphone/remotes/level state, an opaque scripted target and contrast wall do not establish real hits, human voice, actual phone behavior, animation comfort, multiplayer or performance. Logical HUD allocation was 1280×640 with a native viewport about 1626×734. Dense effects, other avatar shapes and every camera angle remain untested. The pre-existing asset-type warning `203785492` remains; the official execute wrapper resets cleanup camera type to Scriptable, so persistent camera restoration is not claimed.

Native cleanup removed owned fixture/probe objects, unanchored the avatar and stopped Play. Genuine animated/device acceptance remains separate.

## Wave 2 contact cadence update

`src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau` (SHA256 `d0afeb914318a16dc210647d8a4d49c6153a47735b5c58fbb86ffd48b57bf3e0`) refines the regular confirmed-damage `rig.contact` burst (`ease = 1 - (1 - progress)^3`, hot-core onset `color:Lerp(white, 0.2 + 0.55 * (1 - progress)^2)`, thickness taper `0.20 -> 0.12` backing / `0.12 -> 0.05` core, and quadratic alpha decay `progress^2`) to improve separation against high-tier (`L80-L100`) beam bodies without modifying `rig.parts` (lines 79-129), part counts (`67/77/77` core/tier, `16/8/0` contact), or quiet/reduced/far behavior.

- `tests/high_tier_clarity.py --negative-controls` verifies `unchanged(old.parts, current.parts, highSpec)` and quiet/reduced/far `unchanged(old.contact.parts, current.contact.parts)` against `nov13-contact-baseline`, plus the refined regular contact curve at `0.07s` (`PASS 131673` assertions + 14 negative controls).
- `tools/beam_lookdev.py` (pinned to `d0afeb914318a16dc210647d8a4d49c6153a47735b5c58fbb86ffd48b57bf3e0`) verified `build/beam-lookdev/comparison.png` (`15/4/41/4/77/4` parts). Native Studio high-tier captures above predate this Wave 2 contact edit.
