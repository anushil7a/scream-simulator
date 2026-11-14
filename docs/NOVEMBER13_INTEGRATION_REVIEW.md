# November 13 completed visual integration

This development checkpoint combines the completed training-map, narrow-map spacing, lock feedback, academy entrance, confirmed beam contact and high-tier clarity work. The five production files match the independently reviewed local source exactly. No gameplay balance, new asset, Roblox publication or release merge is part of this integration.

Accepted before/after images and the limits of each native fixture remain in the linked reviews from [ROADMAP](ROADMAP.md). The 53 retained images contain fixture gameplay or offline comparisons only; JPEGs have only JFIF metadata and PNGs contain only image chunks. Full machine-local command logs, raw observations and discarded diagnostic prototypes remain private.

## Portable regression baselines

The earlier tests referenced unpublished local commits. Their exact baseline bytes are now available without those Git objects:

| Consumers | Baseline available in a normal clone |
|---|---|
| Academy constructor test and review builder | Published `5622daa54424e639e7d3f671b2e453ff377b2cb6`: CompactCity and CompactLayout match the original pre-academy baseline byte-for-byte |
| Contact server/renderer tests and review builder | Published `5622daa54424e639e7d3f671b2e453ff377b2cb6`: Bootstrap, BeamVisuals and BeamStyle match the original pre-contact baseline byte-for-byte |
| High-tier differential and review builder | Exact 9,006-byte pre-styling renderer in the [fixture manifest](../tests/fixtures/nov13-contact-baseline/manifest.json); unchanged BeamStyle comes from published `5622daa` |

The fixture originates from the reviewed local contact checkpoint and is test-only. `review_baseline.py` validates its origin, file name, byte length and pinned SHA-256 before either consumer uses it. An LF checkout rule preserves those bytes on Windows. The contact builder no longer requires an ignored, rejected-prototype directory merely to record provenance.

Final production renderer SHA-256: `cd708090ff3a504afee6e7cd99208cb7df13a0a566900d69cd07271f02ddf2e9`.

## Verification scope

An independent single-branch clone passed all **248 aggregate/build commands** in 70.96 seconds: 25 pure/synthetic suites, 137 mocked-service suites and 64 production compiles, with **339 selected input hashes unchanged and rechecked**. All seven focused mutation-control suites and all three new review builders also passed in that clone. [Portable machine-readable summary and exact input/image hashes](../tests/evidence/nov13-github-integration-2026-11-13.json).

The clone used `--no-local --no-hardlinks --single-branch` and had no alternate object store. Before execution, Git could not resolve the unpublished contact, high-tier, academy, native-validation or early-prototype commits. This proves these checks/builders do not rely on the shared worktree's hidden local history. Production matches the reviewed source; the original local checkpoint chain remains preserved. This is local verification, not GitHub CI.

Historical native captures validate the sampled static layout, font and composition states. They use disposable local place/universe 0 fixtures, fake microphone/remotes, scripted avatar/target states and, for VFX, frozen timestamps. Final high-tier execution used the exact separately verified renderer with the reviewed City/HUD fixture; the rebuilt complete bundle was build-only. Lower-tier/Reduced captures vary visually despite unchanged source/property behavior, so pixel-identical controls are not claimed.

Real eligible voice, actual phones/touch/controllers/OS text settings, animated comfort, representative multiplayer/overdraw/frame time and isolated persistence remain unverified. Mixed-version quest-writer and temporary-test-access release gates remain open. Reproduce the source checks with `python tests/verify_local.py --build`; opt-in mutation controls and the three new review builders run separately.
