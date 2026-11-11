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

For every declared serving **and rollback** writer, the tool runs its exact catalog block and full Profiles/Lease code with current noncatalog configuration mocks over isolated simulated storage. All current IDs' partial/claimed/discovery states must survive acquisition, release and current reload. Each subprocess has a10-second cap; an error/timeout is incompatible, not a pass. This is a necessary finite regression check, not a general proof of arbitrary historical writer behavior.

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

Final focused results:97 dialogue assertions/four controls plus the expected baseline failure;47 replay assertions, all-ID current/historical lifecycle probes and nine controls;36 preflight assertions/four controls. Full25 pure/synthetic +91 mocked suites,60 production compiles and all builds passed. After integration, only the new probe test was hardened against shared expected-data mutation; its final controls and preflight/CLI checks were rerun without changing production or builders. Independent review reproduced the alias false positive, then verified the independent expected snapshot and destructive-writer negative control.

The last command is expected to exit2 with the unresolved inventory gate, not succeed. Synthetic CLI inventories confirmed compatible local writers exit0 but remain release-BLOCKED, and the historical incompatible rollback writer exits2. They are explicitly not operational evidence. See the batch evidence JSON for exact commands, counts, logs and final hashes. Pinned historical files include full source/slice hashes and LF attributes for cross-platform reproducibility; their bytes were independently compared with the named Git commit.

No Roblox fleet, native DataStore, real microphone/network/phone or new native layout test was performed. No app opened, map edit, live service access, product/audio configuration, publication or release merge. Map remains paused pending owner approval. This batch makes the blocker explicit and reproducible; it does not erase it.
