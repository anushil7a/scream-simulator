# Microphone notice policy review

Checked November 11, 2026 against official Roblox pages. The unpublished candidate now includes the requested warning in microphone setup and Settings. This is explanatory copy only: no moderation feature, voice routing, recording, rating/settings change or publication.

## Verified distinction

- Roblox's [Community Standards](https://about.roblox.com/community-standards) prohibit profanity generally and explicitly refer Restricted games to a separate policy. A blanket claim that every swear always causes a ban would be inaccurate.
- The [Age-Restricted Content Policy](https://en.help.roblox.com/hc/en-us/articles/15869919570708-Age-Restricted-Content-on-Roblox) has a strong-language exception for Restricted games, while abusive, discriminatory and sexual uses remain prohibited. Do not infer this game's rating or permitted language from its voice feature.
- The [Voice FAQ](https://en.help.roblox.com/hc/en-us/articles/4405807645972-Voice-FAQ) says voice interactions are subject to recording and moderation. Game-code recording claims must not imply Roblox itself does not record. The [Voice setup guide](https://en.help.roblox.com/hc/en-us/articles/34506487801364-How-do-I-turn-on-Voice-Chat) says rule violations may lead to voice restrictions and account moderation; it does not promise an automatic penalty for each word.
- Current [content-rating guidance](https://create.roblox.com/docs/production/promotion/content-ratings) makes the game's assigned rating a Creator Dashboard/main-details-page property. No age rating is proven by local source. Official documentation snapshots differed on the configure-games strong-language subsection, so the notice does not depend on its toggle wording.

## Project audit and rating limit

At `2978fc2`, `Microphone.luau` consumes `AudioAnalyzer.RmsLevel`, stores short-lived numeric calibration samples, and supplies power to the beam controller. There is no beam word recognition/profanity detector. The game preserves Roblox voice routing and platform controls. The old setup said this game saves no recordings but did not explain Roblox recording/moderation. The new copy removes that game-wide guarantee, identifies Roblox separately, and describes only the beam meter behavior verified in source.

The public City Preview page for place `90337242377543` was inaccessible to the read-only web tool, and exact-ID searches did not surface its rating. The rating and strong-language setting remain **unverified**, not assumed Minimal, Moderate, Restricted or unrated. No account/settings changes were attempted. Before any release, inspect the actual game's Content ratings in Creator Dashboard and recheck that disclosures match the new content. Rating changes are not authorized by this note.

## Implemented rating-neutral copy

Automatic setup:

> BEAMS ON: normal speech can attack. OFF does not mute voice. Avoid profanity. Roblox records and moderates voice.

Inactive hold/release setup:

> Roblox voice access required. Nearby players may hear you. Avoid profanity. Roblox records and moderates voice.

Settings detail:

> VOICE SAFETY
> Avoid profanity. Roblox's profanity rules depend on the game's rating and settings; harassment, threats and hate speech are not allowed. Rule violations may restrict voice or your account.
> Roblox records voice for moderation. The beam mechanic reads volume, not words. Stopping attacks does not mute voice. Use Roblox's mic control to mute, or Report Abuse for violations.

"Avoid profanity" is conservative player guidance, not an invented automatic-ban rule or a claim that City Preview has a particular rating. The detail preserves the Restricted-policy qualification and describes possible rule-violation consequences, not a guaranteed penalty. No custom word detection, recording, reporting, consent or enforcement is added.

## Layout and verification boundaries

The two setup strings remain in the existing wrapped50px/12pt label; both are shorter than their replaced text. Panel/buttons/controls are unchanged. Settings uses the existing TextService-measured info card inside the automatic scrolling list, rather than squeezing this paragraph into setup. Verify actual native TextFits, screen readability and physical input before release; synthetic measurements do not prove them.

The native onboarding fixture is built only unless separate execution evidence is recorded. Studio remains closed with the earlier inaccessible minimized app-picker dialogs; no new window is opened for this copy change. Exact test results/source hashes are recorded in tests/evidence/microphone-notice-2026-11-11.json.

## Verification results

Independent review reran402 actual-slice assertions,3 source contracts and4 negative controls. The previous899b0b8 setup fails the new warning requirement. Tests exercise automatic/legacy setup, Settings at320/390/844/1280 widths with touch/desktop flags, synthetic measured-height growth, unchanged controls, cached/repeated renders, tab/scroll restoration and recalibration disarm. Existing voice29/two controls, microphone111 and audio2629/nine controls pass. Full25 pure/synthetic +79 mocked suites,59 production compiles and all builds pass.

These checks do not measure actual Roblox glyphs, scrollbar reachability, human comprehension, assistive technology or physical touch. Native fixture assertions will check allocated label fit when run, not visibility inside the scrolled viewport. No native execution was performed.
