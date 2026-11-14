# Local verification evidence

`python tests/verify_local.py --build --report build/checkpoint.json` optionally writes a machine-readable local run record and a unique child-output log. Existing invocations without `--report` retain the previous console workflow. No CI workflow or service is configured by this change.

The JSON starts as RUNNING, then records each exact command, start/end time, elapsed duration, exit code and status. Normal completion distinguishes PASSED, FAILED, INTERRUPTED, ERROR and INPUTS_CHANGED. A killed process may leave RUNNING; that is incomplete, not success. Changed selected inputs or finalization failure after otherwise-passing tests make the reporting invocation fail. Original command failures remain failures even if finalization also fails.

Before/after snapshots do not detect a transient change that was restored between snapshots. The SHA256 maps cover the declared source/test/tool/project scope, excluding hidden files, transient tmp files, vault, generated build output and evidence JSON. This is path selection, not secret detection or redaction. Read the scope field: this is not a complete operating-system, dependency, toolchain or transitive-input fingerprint. The log combines child stdout/stderr, including quiet compiler output, and is hash-bound. The log is unredacted, so review it before sharing. It is local build output, not an automatically shared artifact.

Git HEAD is recorded as baseCommit with a dirty-state boolean, never as testedCommit. Merely committing after a run does not prove file correspondence. Before describing a commit as matching the run, compare the included content fingerprints against the final files and inspect any changes outside scope.

Candidate provenance and selected native/test evidence are referenced by exact path and SHA256, not reinterpreted as current test success. Native records remain historical and scoped. A regenerated fixture differing from a native record means that prior run does not verify the new bytes; it is not automatically a failure of local source tests. Default aggregate execution does not imply optional negative controls ran. Build success is not Studio execution, real-device validation, CI success or release approval.

Both quest-writer and temporary-test-tools release gates remain separate and BLOCKED until their operational/review conditions are met. The reporter never clears them. Run records stay under ignored build/, while checked-in evidence can reference their hashes and accurately summarize results.


## First integrated run

The November 12 dirty working tree based on 4c23fce passed 222 child commands in 25.03 seconds: 25 pure/synthetic suites, 112 mocked suites, 63 production compiles and all disposable builds. All 308 selected input fingerprints matched before/after and were rechecked against the final files. The complete local child log is about 5.65 MB; its hash matches the JSON. No log contents were pushed.

Focused reporter tests passed 36 assertions. Independent review checked the exact runner diff/registrations and 33 actual state/output/error cases in memory; it did not rerun the full filesystem suite. Beam fixture review independently passed 264 assertions and five controls with all source/generated/binary hashes recomputed. Both release gates remained BLOCKED. See [checkpoint summary](../tests/evidence/local-verification-2026-11-12.json); the report does not claim an immutable tested commit or new native performance measurement.
