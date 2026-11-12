# Temporary game-specific Test Tools review (November 12, 2026)

The owner requested Test Tools for anyone currently joining this developer-tested game, with removal before launch. This draft implements that request only for City Preview universe `10769005350`, retaining creator `11499795799`/User validation. Historical native cloud-reopen evidence maps place `90337242377543` to that universe (version 10/12/14 records and version 19 handoff); the fresh public API lookup was unavailable. Newly saved `idk`, `gmae` and `game` disposable copies are not substituted for this identity.

## Boundary and save protection

- Both the State visibility snapshot and each test command pass server `game.GameId` into DeveloperAccess. A non-owner needs the exact true prelaunch flag, exact true allowlist entry, valid positive integer universe ID and matching creator. Original owner/Studio access is unchanged. Client flags cannot grant access.
- A valid test command freezes a sanitized legitimate baseline and creates separate temporary working data before mutation. Existing purchase-in-flight barrier, mixed test/normal PvP isolation, NPC/reset restrictions and save/release baseline paths remain. The owner's Keep Playing choice for ordinary save failures is unchanged.
- Test-to-test repeat-opponent history is now separate from ordinary history. Each retains the existing 4,096-pair bound and expiry. This avoids temporary test fights penalizing later ordinary sessions without an unbounded ledger.
- `python tools/developer_access_preflight.py` returns BLOCKED/exit 2 while enabled. The draft build records that status. Disabling the flag passes only for the exact reviewed disabled-module fingerprint; any source drift needs review. This is a local CLI/provenance gate, NOT enforcement against manual publication, proof about deployed servers or publication approval. Disable and review before public release.

## Verification

- `python tests/developer_tools.py --negative-controls`: 94 assertions, four controls and retained source contracts.
- `python tests/test_session_rewards.py --negative-controls`: 56 assertions, 11 controls.
- `python tests/prelaunch_test_isolation.py --negative-controls`: 40 assertions, four controls, actual authorization/dev/payout/autosave helpers and Profiles with fake stores. Reads actual Bootstrap history declarations; retained controls cover table alias, history selector, baseline copying and save selection. Independent review separately removed the real history declaration and caught contamination.
- `python tests/prelaunch_release_gate.py`: 14 assertions, including changed universe and removed universe guard in disabled-source drift.
- `python tests/verify_local.py --build`: 25 pure/synthetic suites, 110 mocked-service suites, 63 production compiles and disposable builds passed. These do not run Studio.
- Independent review additionally exercised 20,736 authorization combinations and history saturation/expiry. Final narrow-scope review cleared the exact production diff, both actual server callers, final 40-assertion/four-control integration matrix and release gate; it does not authorize publication.

The save fixture manually models release/rejoin with actual Profiles and fake storage, not full native transport or real persistence. Native smoke checks separately used the earlier local full-game source fingerprint 19a71e16963c7e246301cbf54978db7a6416fff11a0965d4f2b2c4cbed733a73, NOT this new tester-access candidate. No live DataStore, purchase, permission-setting change, Roblox upload or publication occurred.
