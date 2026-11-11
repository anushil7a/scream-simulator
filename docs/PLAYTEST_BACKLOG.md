# Owner playtest batches — November 11, 2026

Latest owner directions supersede earlier conflicting plans. Keep reviewable batches, reproduce before behavior fixes, preserve concurrent work/entitlements and push verified work to existing draft PR #1 when GitHub authentication is available. No publication or live DataStore access. This is a backlog, not a claim of completion or scheduled background work.

| Request | Status and next evidence |
| --- | --- |
| 1. Sprint spam exploit | Implemented locally: charge granted intervals, delayed partial refill, flood-safe release, respawn reset. Full simulated checks pass. Native full-server movement/input validation remains. See CORE_CONTROLS_REVIEW.md. |
| 2. Remove first person | Implemented locally; V/view controls removed, Classic camera/minimum six-stud zoom. Native synthetic V/zoom and layout checks pass; obstruction/physical-device checks remain. |
| 3. Remove dodge yellow box | Blocked on actual screenshot inspection. Library ID `libfile_db9651cc29948191991127d06dc7f194` has not been materialized here; available Library capabilities require a page context, not this standalone ID. Obtain a supported local attachment/materialization, inspect it, then identify the real effect. No image-dependent change made. |
| 4. +10 levels and minimap | Pending. Gate test tools against ordinary production players on the server; add +10 level test action with cap/entitlement checks. Put real-player minimap in the test-tools button location and validate touch layouts. |
| 5. Beam audio/stat readouts | Readout corrected locally: attack-description timing removed; single current-level full-power summary, 68 DPS /54.75 nominal studs at100; synthetic authoritative and native text-fit checks pass. Audio remains pending: trace LOW/OFF and gain/mixing before changing loudness. Asset loading/audibility require actual playback; no audio fix claimed. |
| 6. Smaller map | Pending. Preserve current map as a recoverable named draft before redesign. Keep spawn/training/PvP and navigation/quest dependencies coherent. |
| 7. Beams naming/style | Pending. Rename player-facing Screams to Beams; hue-only style controls, remove saturation/brightness/top bar and free color choices, yellow base. Preserve legitimate acquired entitlements and existing data. |
| 8. Microphone/profanity notice | Pending official current Roblox policy research before wording. Describe only implemented behavior; do not imply custom profanity detection, recording or moderation. |
| 9. Five-second beam cooldown | Implemented locally: five seconds after automatic attack end, four-second maximum duration. Authoritative boundary/interruption/replay and UI regressions pass; native transport and real-device timing remain gates. See BEAM_COOLDOWN_READOUT_REVIEW.md. |
| 10. Quests/training enemies | Pending. Audit actual duplicate objectives, remove destruction quests safely, make quests relevant and add roaming trainers with authoritative combat/reward checks. |
| 11. Boosts on purchase | Implemented locally: atomic receipt-deduplicated activation on durable delivery, absolute offline expiry and preserved legacy tokens. Actual-handler/pure/UI simulations, negative controls and full builds pass. Product IDs stay zero; real delivery/native readability remain unverified. See BOOST_PURCHASE_REVIEW.md. |

Delivery update: main boost/description checkpoint `c1d700a` pushed non-force and verified remotely, including `736a82f` and `f0dc1e7`. A tested copy-only follow-up removes unwanted offline-timer wording; verify that follow-up commit separately.
