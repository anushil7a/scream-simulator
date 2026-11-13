# Optional microphone setup removed

## Behavior

The owner asked to remove microphone testing and its area/objectives. Automatic play no longer opens a calibration panel or requires a quiet/loud test. The existing input normalization defaults remain .003/.06; this is a bounded baseline, not a guarantee of suitable sensitivity for every microphone or noisy room. Existing internal calibration methods remain unused for compatibility.

A valid, active, unmuted input graph and finite RMS can become locally ready without calibration. Roblox voice eligibility and the server's readiness, cooldown, cover, protection and input-timeout checks remain separate and authoritative. Beams start OFF and require a deliberate toggle. OFF does not mute ordinary voice chat. The Settings page retains voice-safety information and an error-only, bounded access retry.

A latched input-interruption epoch makes an input/analyzer/wire replacement visible to the Client even when the new graph becomes ready within the same step. It cancels/disarms and resets the quiet gate before recovery. Independent review caught two issues and they were fixed: missing input ownership is cleared once rather than generating a cancellation every poll, and an accepted access Check latches its interruption before a fast successful response. A 120-poll unplugged legacy case now emits one cancellation; a distinct later loss emits another.

## Practice retirement and copy

The runtime mic-testing area, target, tutorial, related objective and practice hit callbacks are removed. The permanent `practice_beams` quest ID remains as a retired tombstone so saved progress, discovery and claimed flags survive sanitization and save/reload. Only a previously earned, completed-unclaimed reward remains visible and claimable once. No automatic completion, refund or ID reuse. Training enemies, soccer, arena activity and the archived original map are preserved. Full-map North labels and “North is up” text were also removed; useful activity and PvP information remains. See [retirement review](PRACTICE_RETIREMENT_REVIEW.md).

## Verification scope

- Actual Microphone, Controls and selected Client fragments: 61 assertions, three contracts and six negative controls, including historical failure.
- Actual persistence/claim helpers with simulated storage: 227 assertions and seven controls; retired-card renderer: 1,683 assertions and twelve controls.
- Whole current Client startup: 336 boundary scenarios, 19 ownership cases and twelve controls. Removed exactly the obsolete FirstBeamGuide dependency boundaries, not arbitrary guards.
- Retained lifecycle, retry, inactivity, safety, shop/panel, sprint, eligibility and map suites remain covered. Native transport/feedback fixture changes have separate [harness evidence](MIC_TEST_REMOVAL_HARNESS_REVIEW.md).
- Final composed local suite: 25 pure/synthetic suites, 127 mocked-service suites, 64 production compiles and all disposable builds, 238 commands. All 324 selected input fingerprints unchanged and rechecked. This is local verification, not CI.

## Native local startup

The stopped task-owned Studio place had no targetable Windows window, so its 64 mapped scripts were backed up and synchronized through official Studio MCP. The local-only Bootstrap guard was retained and strengthened with GameId zero. Exact loaded source text was verified, with an explicit source-injected review label. This is not a claim that the rebuilt binary itself was opened.

In the verified place0/game0 session, the actual HUD appeared without a setup wall, displayed BEAMS OFF, and had no MicPanel. Server active was false; WalkSpeed was16 and JumpHeight7.2. No MicPracticeTarget remained. [Startup image](images/mic-removal-2026-11-13/startup.jpg). These are native UI/state observations, not physical keyboard/touch movement or real microphone validation. Three asset-type warnings and the expected temporary-save warning were present; no origin inference. Play was stopped after the smoke check.

## Remaining limits

Real microphone sensitivity/noise, device disconnect timing, physical phone/gamepad controls and multiplayer/PvP are unverified. The current automatic-mode Settings wording still mentions turning beams ON in retained legacy mode; local input errors are mainly visible in Settings while the OFF meter has priority. Historical older writers can still lose newer quest state, so the existing mixed-version release gate remains blocked. No publication, live DataStore writes, purchases or audio configuration.

Vault guidance consulted for this task: skippable onboarding/first-time experience, voice-safety boundaries, permanent quest IDs and persistence migration. Removing an onboarding wall does not prove audio authenticity or bypass Roblox eligibility.

## Native transport

A second source-injected local fixture passed51 checks in31.866 seconds through the actual native Client frame scheduler, RemoteEvent handler, protocol and server loop, with microphone readiness/power and aim explicitly replaced by synthetic values. It exercised initial OFF, explicit arming, malformed/replayed input, acknowledgement, pulse scheduling, interruption/recovery, quiet stop and toggle OFF. Immediate replay snapshots were unchanged, and both explicit stops arrived before the0.5-second input timeout with exactly five seconds of cooldown. Saving was disabled; fixture cover removal, restored unanchored root and inactive attack were observed before stopping Play.

An initial source-readback response exceeded the tool's output length. That Play attempt was immediately stopped and no result accepted; a fresh run began only after bounded exact-source equality checks passed. [Detailed evidence](../tests/evidence/mic-removal-2026-11-13.json). This does not validate real microphone sensitivity, internet latency, cross-device or multiplayer behavior.


The two existing native negative controls were rerun after adaptation: dropping the explicit quiet stop failed at the missing-stop oracle; accepting a replay mutation failed at the immediate server-state comparison. These are intended failures of disposable mutants, not current game failures. Each session stopped; exact production Client/Adapter and a plain locally guarded Bootstrap were restored. The task-owned hidden Studio process was then closed after identity verification. Files/evidence remain saved and the PC stays on.
