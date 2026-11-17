# Foundry preview sound placeholders

Read repo vault-derived COMPACT_AMBIENCE_REVIEW and BOSS_AUDIO_REVIEW (spatial audio/mixing, verified installed Studio packaged paths) and actual IMG_1527.jpeg reference before implementation.

Standalone client script requires Studio, GameId/PlaceId0 and ReviewBuildName=Map10V21FoundryReview. Waits at most10seconds for review readiness. No production imports or combat/voice changes. Finds tagged FoundryAmbienceAnchor BaseParts with Cue Dock or Lighthouse; maximum one of each. Reconciles tags once per second, releasing removed/replaced sources before allocation; late streamed anchors are discovered without waits. Root builder supplies placements.

Dock uses quiet, sparse `impact_water.mp3`; lighthouse uses sparse `volume_slider.ogg`. These are generic packaged placeholders, NOT bespoke surf, gulls, bells or foghorn recordings. No uploads or invented asset IDs. Each is preloaded once and used only on confirmed success; missing files remain silent. Nearby living-player camera gate90studs; native inverse-tapered positional rolloff10–90. Per-source volume.025, at most2voices, one-shots capped3seconds, intervals8/14seconds. Preview-only local mute button stops both immediately. Character loss, distance, destroyed script and review-guard removal suppress/clean audio. An in-flight preload cannot be canceled but is fenced after return.

Actual script compilation and19 mocked guard/preload/budget/mute/distance/cleanup/late-anchor/replacement checks pass. No native audio listening, asset decoding, mobile packaging or microphone-feedback safety claim. Next: listen at the two anchors in disposable review, check mute/range, and replace placeholders only with approved authored audio if desired.
