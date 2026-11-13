# Challenge cap copy review

## Scope and evidence

Against `b402c3f`, only the Client quest challenge card changes: at level 100 it now says `MAX LEVEL · no XP awarded`, while retaining the counter and automatic-renewal explanation. Below the cap the existing nominal XP text is unchanged. No server helper, reward amount, challenge identity, counter, renewal or persistence behavior changed.

The historical actual renderer promises +200 XP at level 100, while the authoritative `xp` helper returns zero. The pinned baseline mode reproduces that mismatch. This is a cap-only correction: below-cap copy remains a nominal reward, not a preview of the actual amount after boosts or truncation on reaching the cap.

## Targeted guidance

Consulted `vault/AGENTS.md`, then queried the vault index for BrawlDev GUI Review. Current source: `vault/Source transcripts/BrawlDev - GUI Review.md`, lesson 07 (lines 53–57, scrolling/canvas and last-row reachability), lesson 09 (65–69, live health/max-health refresh), and lesson 15 (101–105, sizing and long-label constraints). These guided the bounded UI audit; the cap mismatch is established by current project source, not by tutorial authority.

## Verification

- `python tests/challenge_cap_copy.py --negative-controls`: 23 actual challenge-card/completion assertions and four targeted controls pass. Covers levels 1/60/99/100, capped and ordinary renewal, boosted near-cap truncation and the subsequent capped card. Uses actual extracted renderer loop and server helpers plus real Progression/TrainingRules with fake UI/session state.
- `python tests/challenge_cap_copy.py --baseline`: pinned `b402c3f` fails the intended capped-XP-promise assertion.
- `python tests/quest_catalog_ui.py --negative-controls`: 479 retained renderer assertions and nine controls pass.
- Client Luau compilation and `git diff --check` pass.
- Independent reviewer reran 23 assertions/four controls and compilation at the hashes below and found no blocker. Exact baseline diff is supplied separately for scope verification.

Raw file SHA256:
- Client: `af4abeaaa544ac07d57481c0d8dbe11c931c60a8ca2194e4080af3eda3cbb4b9`
- Focused test: `1a8533c032f0cea0e7298bfd513ea786e15feb4ee716b2cecc120c1b28258449`

The initial focused attempt lacked the TrainingRules dependency used by actual level-up code; it was corrected to load that real module before the passing reruns. No native text-fit, real multiplayer, live persistence, publication or CI result is claimed. The default focused run does not run mutation controls unless explicitly requested.

Final exact-diff independent clearance received. Integrated checkpoint:25 pure/synthetic and116 mocked suites,63 production compiles and all disposable builds pass;226 commands,36.57s,312 selected input hashes unchanged/rechecked. See `tests/evidence/cap-native-checkpoint-2026-11-13.json`. This is local evidence, not CI.
