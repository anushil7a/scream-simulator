# Microphone notice policy review

Checked November 11, 2026 against official Roblox pages. Research and proposed wording only: no notice implementation, moderation feature, rating/settings change or publication in this checkpoint.

## Verified distinction

- Roblox's [Community Standards](https://about.roblox.com/community-standards) prohibit profanity generally and explicitly refer Restricted games to a separate policy. A blanket claim that every swear always causes a ban would be inaccurate.
- The [Age-Restricted Content Policy](https://en.help.roblox.com/hc/en-us/articles/15869919570708-Age-Restricted-Content-on-Roblox) has a strong-language exception for Restricted games, while abusive, discriminatory and sexual uses remain prohibited. Do not infer this game's rating or permitted language from its voice feature.
- The [Voice FAQ](https://en.help.roblox.com/hc/en-us/articles/4405807645972-Voice-FAQ) says voice interactions are subject to recording and moderation. Game-code recording claims must not imply Roblox itself does not record. The [Voice setup guide](https://en.help.roblox.com/hc/en-us/articles/34506487801364-How-do-I-turn-on-Voice-Chat) says rule violations may lead to voice restrictions and account moderation; it does not promise an automatic penalty for each word.
- Current [content-rating guidance](https://create.roblox.com/docs/production/promotion/content-ratings) makes the game's assigned rating a Creator Dashboard/main-details-page property. No age rating is proven by local source. Official documentation snapshots differed on the configure-games strong-language subsection, so the proposed copy does not depend on its toggle wording.

## Project audit and rating limit

At `2978fc2`, `Microphone.luau` consumes `AudioAnalyzer.RmsLevel`, stores short-lived numeric calibration samples, and supplies power to the beam controller. There is no beam word recognition/profanity detector. The game preserves Roblox voice routing and platform controls. Existing setup says this game saves no recordings but does not explain Roblox recording/moderation.

The public City Preview page for place `90337242377543` was inaccessible to the read-only web tool, and exact-ID searches did not surface its rating. The rating and strong-language setting remain **unverified**, not assumed Minimal, Moderate, Restricted or unrated. No account/settings changes were attempted. Before any release, inspect the actual game's Content ratings in Creator Dashboard and recheck that disclosures match the new content. Rating changes are not authorized by this note.

## Proposed rating-neutral copy

Setup, automatic mode (retain the separate control warning):

> BEAMS ON: speech can attack. OFF does not mute voice. Roblox records and moderates voice; follow its rules.

Settings detail:

> Keep voice respectful. Profanity rules depend on the game's rating and settings. Harassment, threats and hate speech are not allowed. Roblox records voice for moderation. The beam mechanic reads volume, not words; this game saves no recordings. BEAMS OFF stops attacks, not voice chat. Mute using Roblox's mic control.

For the inactive hold/release mode, keep its microphone/voice-access instruction instead of claiming automatic ON attacks. Do not add new enforcement, recording, transcription or consent behavior. Keep Roblox report/block/mute controls intact and do not claim BEAMS OFF mutes the microphone.

## Implementation gate

Do not silently replace strings while compact-map Client review is in progress. Once coordinated, use the existing scrollable Settings info cards and verify text height against actual card width. The setup panel is currently fixed-height text with responsive button relocation: copying a longer paragraph into it is not safe without sizing checks. Test narrow/landscape layouts, mode-specific instructions and interruption/ON-OFF guidance. A source or mocked sizing test is not native TextFits, physical touch, or real voice validation.
