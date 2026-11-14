# Selectable beam sound levels

November 11, 2026. Based on clean/fetched `47f3d46`. No map changes, new audio asset IDs, purchases, live saves or publication.

## Reproduced gap and behavior

The actual Settings button only offered ATTACK SFX: LOW/OFF, and the shared beam mix was hard-coded to 0.24. The owner requested louder beams and questioned those options. The new session-only button cycles **BEAM SFX: NORMAL -> LOW -> OFF -> NORMAL** and retains its level across menu rerenders, respawn/clear and ordinary attack cleanup. A new client session starts at NORMAL; no profile migration or save field is added.

NORMAL's shared Sound.Volume budget is 0.40; LOW is the original 0.24. Both retain the 0.65 group gain, original pitch, existing EQ, 0.7 local multiplier, spatial range, four-entry limit and fade/lifetime cleanup. The same budget is divided across every active or fading entry, not granted to each attacker. Before EQ/spatial attenuation the non-speaking aggregate ceiling is 0.26 for NORMAL versus 0.156 for LOW, a 1.667x nominal gain increase, not a measured SPL or audibility claim.

When the existing voice-active flag reaches a mixer update, NORMAL is capped back to 0.24 before the existing smoothing toward 0.4 duck. Thus this change intentionally does not raise the old voice-active ceiling. Calibration still gives zero at a mix update. OFF stops/destroys all emitters immediately and rejects new pulses; re-enable does not replay old entries and needs a fresh valid pulse. Invalid modes are rejected. Legacy SetEnabled(true/false) maps to NORMAL/OFF; destroyed mixers cannot be reconfigured or recreated.

The UI explicitly notes the starter beam has no SFX, and that the choice does not change microphone/proximity chat. Existing owner-selected tier 10-100 recordings and the still-unconfigured four gameplay cue IDs are untouched. Gain cannot make unavailable assets audible.

## Timing and validation limits

This batch does not refactor the existing client cadence: attack audio updates after an approximately 0.15-second frame accumulator, using the current frame dt. Non-OFF level changes take effect at the next mix update. Voice detection, attenuation and calibration therefore have scheduling/detection lag; this is not feedback prevention or evidence of comfortable loudness. Real headphones/speakers, all tier assets, one/four attackers and real mic retrigger behavior remain release checks.

No Studio, browser or other app was opened for this batch. The three already-inaccessible minimized app-picker dialogs are unchanged. Do not reopen Studio merely to claim an audio test: a genuine listening/device test is still needed. Native playback and physical Settings readability/input were not rerun.

## Verified checks

- 481 actual module/settings/UI-callback assertions plus 2,148 comparisons against the preserved `47f3d46` LOW mixer sequence: **2,629 synthetic assertions**. Includes mixed local/remote active/fading entries, all levels and invalid requests, immediate OFF cleanup, fresh-pulse re-enable, preserved asset IDs/pitch, voice-active ceiling at Step, recovery/calibration, timeout/lifetime and narrow/wide branch callbacks/reopens.
- Nine targeted negative controls reject missing NORMAL, missing voice cap, per-entry instead of aggregate budget, missing OFF cleanup, altered pitch, missing calibration suppression, wrong cycle, missing LOW budget and non-equivalent baseline mixing. Historical `--baseline` reproduces the old missing NORMAL. The normal baseline-comparison test uses preserved source fixtures so it does not require Git history in a shallow/exported checkout.
- Existing 31 mixer, 12 owner-ID/unassigned-tier and 15 actual-adapter checks pass. Full `python tests/verify_local.py --build`: **25 pure/synthetic suites, 71 mocked suites, 57 production compiles**, source-audited candidate and all disposable builds pass. No generated fixture was executed natively this batch.
- Independent review reran the focused checks and negative controls and found no production blocker. The Settings tests execute actual callback code against fake controls; they do not measure rendered text fit or physical input.

[Machine-readable evidence](../tests/evidence/beam-audio-levels-2026-11-11.json) records production identities, scopes and limitations.

Packaging follow-up: Git warned that Windows autocrlf could alter raw-byte baseline hashes. Explicit `eol=lf` attributes now protect both historical Luau fixtures. A fresh `checkout-index` with `core.autocrlf=true` retained both exact hashes and no CRLF; temporary output was cleaned. Production and test logic are unchanged.
