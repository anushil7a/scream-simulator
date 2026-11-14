# Quest writer compatibility and restart disclosure

Base: `af8c27723d173b1274b217853526c4d2fc3ca2cd`. No production persistence/schema, quest identity/reward, map or live setting changes.

## Confirmed mixed-writer release blocker

The historical pre-additive writer `7a0b044276a368c506a08ee2ce2c13b41067cb5c` knows eight quest IDs. Its actual `Profiles.Load` sanitizes and writes the acquired record atomically. It drops unknown additive quest progress and claims **during acquisition**, before autosave. Reward currency is retained. Sequential valid ownership is enough; no concurrent lease exploit is required.

The isolated fake-store reproduction executes pinned historical Profiles/Lease/catalog source, actual current claim helpers and current acquisition/release logic:

- Controlled Beams: claim yields25 coins/60 XP callback total; old acquisition deletes claim while retaining25 coins; after release, the next current session can earn/claim again, ending50 coins/120 XP callback total.
- Team Effort: same sequence yields50 then100 coins,120 then240 XP callback total.
- Current-to-current reload retains claims and blocks repeated reward; legacy garden claim remains. XP is a callback total here, not persisted XP. Noncatalog historical configuration is substituted with current fixture methods. This is not a full historical-server/native execution or a live incident claim.

A new schema field, token or compatibility flag in the same record cannot constrain already-deployed code that ignores it. A separate claim store introduces cross-record reward atomicity/migration risk and is not added speculatively. Runtime backward compatibility is **not fixed** by this batch.

## Explicit local guard, not deployment authority

`build_candidate.py` now includes `releaseGates.questWriters` with status `BLOCKED_UNVERIFIED_WRITER_FLEET` in every normal-candidate provenance sidecar. The sidecar records required serving/rollback inventory, exclusion/cutover evidence and limits. It never declares the candidate release-ready.

`python tools/quest_writer_preflight.py --inventory <reviewed-local-inventory.json>` verifies the candidate binary, current production source, project and referenced-file hashes. It requires a candidate-bound UTC inventory with explicit completeness/exclusion declarations, evidence references, serving commit IDs and either rollback commit IDs or explicit disabled rollback. Only immutable full local Git commit IDs are accepted; there is no fetch/authentication or Roblox access. Missing evidence/history and unsupported source structures fail closed.

For every declared serving **and rollback** writer, the tool runs its exact catalog block and full Profiles/Lease code with current noncatalog configuration mocks over isolated simulated storage. Each current ID is probed in four named states: partial, completed-but-unclaimed, claimed, and discovery-only without a quest entry. Each must survive acquisition, release and current reload; discovery-only must not fabricate a quest entry. Each subprocess has a10-second cap; an error/timeout is incompatible, not a pass. This is a necessary finite regression check, not a general proof of arbitrary historical writer behavior.

Example inventory shape (placeholders, **not evidence**):

```json
{
  "candidateArtifactSha256": "<exact rebuilt artifact hash>",
  "observedAtUtc": "<UTC time of operational observation>",
  "inventoryComplete": true,
  "incompatibleWritersExcluded": true,
  "inventoryEvidence": "<reviewed record identifying all possible writers>",
  "cutoverEvidence": "<reviewed completed drain/cutover observation>",
  "rollbackEvidence": "<reviewed rollback-floor or disabled-rollback record>",
  "servingCommits": ["<40-character verified commit>"],
  "rollbackCommits": [],
  "rollbackDisabled": true
}
```

Declarations and evidence-reference strings are **not independently verified fleet telemetry**. Even exit0 means only the declared writers passed a finite simulation. Output still says release blocked pending operational review and other gates. Reverify the actual possible writers immediately before any separately authorized rollout. The tool cannot prevent manual publication, inspect an omitted writer, repair already-lost flags or grant publication permission.

### Required rollout/rollback boundary

Before any new one-time rewards go live, establish that every writer a player can reach preserves their IDs and that rollback cannot reintroduce an incompatible writer. A compatible bridge may retain inactive quest definitions without exposing objectives, but no bridge deployment is attempted here. Drain/exclude all incompatible instances, verify the cutover actually completed, then retain a reviewed compatible rollback floor. Preserve all existing IDs/progress and normal ownership fencing. If this cannot be established, do not release this candidate.

Roblox's [update guidance](https://create.roblox.com/docs/projects/update-games) says publishing leaves existing servers running; delayed/scheduled restarts can still admit joins before restart. A publication or scheduled restart alone is not verified exclusion. [DataStore version history](https://create.roblox.com/docs/cloud-services/data-stores/versioning-listing-and-caching) captures the first write per key per UTC hour rather than every intermediate write; it is not an automatic transaction-by-transaction undo for duplicated rewards. No rollback or store repair is performed.

## NPC restart disclosure

Astra found the earlier menu-only fix did not cover the NPC dialogue route. The actual `showConversation` renderer now labels an inactive partial quest `Restart:` and appends the same explicit unfinished-progress reset warning. It uses the current profile snapshot and canonical goal because the dialogue payload omits progress/goal. Active, completed, claimed and absent/locked choices retain behavior; callbacks still send the same AcceptQuest/ClaimQuest commands. No progression semantics changed.

## Evidence and limits

Focused commands (negative controls are explicit, not implicit in aggregation):

```text
python tests/quest_dialogue_restart.py --baseline
python tests/quest_dialogue_restart.py --negative-controls
python tests/quest_writer_compatibility.py --negative-controls
python tests/quest_writer_preflight.py --negative-controls
python tests/verify_local.py --build
python tools/quest_writer_preflight.py
```

Original670948d focused results:97 dialogue assertions/four controls plus the expected baseline failure;47 replay assertions, all-ID current/historical lifecycle probes and nine controls;36 preflight assertions/four controls. Full25 pure/synthetic +91 mocked suites,60 production compiles and all builds passed. After integration, only the new probe test was hardened against shared expected-data mutation; its final controls and preflight/CLI checks were rerun without changing production or builders. Independent review reproduced the alias false positive, then verified the independent expected snapshot and destructive-writer negative control.

The last command is expected to exit2 with the unresolved inventory gate, not succeed. Synthetic CLI inventories confirmed compatible local writers exit0 but remain release-BLOCKED, and the historical incompatible rollback writer exits2. They are explicitly not operational evidence. See the batch evidence JSON for exact commands, counts, logs and final hashes. Pinned historical files include full source/slice hashes and LF attributes for cross-platform reproducibility; their bytes were independently compared with the named Git commit.

No Roblox fleet, native DataStore, real microphone/network/phone or new native layout test was performed. No app opened, map edit, live service access, product/audio configuration, publication or release merge. Map remains paused pending owner approval. This batch makes the blocker explicit and reproducible; it does not erase it.

## Four-state oracle correction after 2daa39e

Astra independently showed that the original probe could miss two destructive mutations. Every discovered ID also had a quest record, so Sanitize could reconstruct discovery even if its availability-only preservation loop was deleted. It also seeded unclaimed progress only below goal, missing a writer that zeros completed-but-unclaimed progress. Current production passed Astra's additional probes; these were test false-positive risks, not established production data-loss defects.

The final probe now independently seeds partial, completed-unclaimed, claimed and discovery-only for every current quest ID, and checks an immutable expected snapshot across writer acquisition/release and current reload/final release. Discovery-only explicitly requires the quest entry to remain absent. Exact loop-removal and completed-unclaimed-zeroing controls fail as expected. Forty-seven original replay assertions, the current/historical probes and all eleven compatibility controls pass independently. The36 preflight assertions/four controls and synthetic CLI compatible/incompatible cases were rerun; release output remains BLOCKED.

This is finite coverage of four named positive states, not exhaustive validation of every absent/false/malformed profile or arbitrary writer. There is no production/schema/save behavior change. The full25/92/60 build checkpoint is2daa39e; this test/documentation-only follow-up reran affected probes/preflight rather than pretending another native or aggregate build ran. [Follow-up evidence](../tests/evidence/quest-writer-states-2026-11-11.json). The actual writer-fleet rollout gate stays unresolved.


## November 12 operational rollout decision

Rechecked at `0004c77`: the existing fake-store replay still reproduces both duplicate-reward paths, while the current writer preserves the four tested states for all ten IDs. The 47 replay assertions/11 controls and 36 preflight checks/four controls pass. No new persistence defect, migration or production change is claimed.

**Preferred next step: establish the real writer boundary, not add a second save mechanism.** Current Profiles uses `ScreamSimulator_v1` outside Studio, with no explicit scope argument. Roblox data stores are shared between places in the same experience. Inventory must therefore identify the universe, every reachable place/version, public/private/reserved instances, rollback artifacts, and any administrative/Open Cloud writer touching the same store/key space. A familiar place name, one recent join, an empty public-server list, or the absence of recent errors is not a complete inventory. No live inventory has been collected here.

A separately authorized maintenance cutover can be considered only with all of these gates:

1. Bind candidate and compatible rollback artifacts to exact source/bytes. Every possible writer must preserve the canonical ten quest IDs, goals, discovery-only, partial, completed-unclaimed and claimed state, plus the existing economy and lease semantics. Run the declared-writer preflight; its pass is necessary but not operational proof.
2. Arrange and verify a controlled join/write boundary across the affected experience and tools before additive gameplay can run. Any access restriction, restart, publication or live inspection needs separate authorization. Do not assume the current candidate can safely serve during old-server bleed-off.
3. Exclude/drain incompatible instances and verify completion, including invite/teleport/private/reserved paths and external writers. A scheduled restart time, publication success, or one empty server does not prove exclusion. If the supported controls cannot establish this boundary, stop the rollout.
4. Admit players only to the verified compatible candidate after that boundary. Keep a compatible rollback floor; never roll back to the eight-ID writer after additive state exists. An emergency that cannot retain compatibility requires another controlled stop, not an unreviewed older save writer.
5. Review actual runtime/save health under a separately approved test/release plan. This document does not authorize that work and does not declare a release ready.

A preservation-only bridge is an alternative when an exact deployed source is identified: retain all ten canonical quest states through acquisition/sanitize/save, but do not expose or accept the new objectives/rewards. It can establish a compatible rollback floor. It **does not** constrain still-running older code, remove the initial exclusion requirement, or reconstruct already-erased claims. No bridge artifact is generated against a guessed published version. A direct controlled cutover is simpler if a compatible rollback artifact and complete boundary can be established.

Rejected shortcuts: a new marker/schema/lease that deployed code ignores; changing the DataStore name or defaulting profiles; copying an old whole-place version over newer saves; blanket claim/reward grants; and a separate claim ledger without a reviewed cross-record reward transaction. Saved-version history is not evidence for reconstructing every lost claim. Keep the current runtime unchanged until the operational facts support a concrete safe step.

References checked November 12: [Roblox data-store scope and Studio warning](https://create.roblox.com/docs/cloud-services/data-stores), [update/restart behavior](https://create.roblox.com/docs/projects/update-games). Targeted vault reading: `04 Data and Persistence/Schema Migrations - Worked Case Studies.md`, Case 6; `41 Multiplayer Services/Server Shutdowns Soft Updates and Migration.md`, sections 1-3. Their newer-reader guidance cannot be retrofitted into already-running old writers.

Review outcome: independent source/design review agrees this is an operational release blocker. No schema/namespace, live data, game access, map, publication or rollback action changed. Exact rerun evidence is in `tests/evidence/quest-writer-revisit-2026-11-12.json`.
