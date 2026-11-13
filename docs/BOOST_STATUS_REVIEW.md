# Boost-card readability - November 13, 2026

XP and Coins boost cards now have filled purple/gold 2x tiles and a separate, readable status band. Active boosts show a green countdown with a state marker; inactive and unavailable states retain their explicit text on a neutral backing. The 14px bold status sits above the existing purchase/saved-boost buttons with a 14px gap. This makes the multiplier, current state and action easier to scan.

Only `ShopUI.luau` changes in production relative to the reviewed previous checkpoint. Timer arithmetic and wording, catalog IDs, product lookup/cache, purchases, saved-boost activation, ownership, callbacks and cleanup gates remain unchanged. The hue-only picker and its removed preview controls remain untouched. The passive band and marker accept no input. Cards grow by 18px narrow /32px wide to preserve spacing, so the full shop requires slightly more scrolling.

Vault references used before implementation: `05 UI and UX/UI Design Systems.md`, section 1 (role colors/type/components/states); `UI Style Directions - A Visual Vocabulary for Briefs.md`, sections 1/3 (existing visual language and matched comparisons); `Responsive UI for Phone Tablet Console and PC.md`, TLDR (readable text, 44px controls and explicit narrow checks). Existing project primitives/palette remain; no assets, motion or permissions added.

## Native comparisons

Raw captures are copied byte-for-byte. Each pair uses the same scripted local inventory/readiness/countdown state and logical width. Native fonts render the actual Shop module and actual Client card/frame/label/button factories. Both full Render calls run, with non-boost cards hidden for the comparison.

| Sample | Previous | Updated |
|---|---|---|
| 390 wide, active XP /inactive Coins | [Before](images/boost-status-2026-11-13/390-mixed-Before.jpg) | [After](images/boost-status-2026-11-13/390-mixed-After.jpg) |
| 320 wide, status unavailable | [Before](images/boost-status-2026-11-13/320-unavailable-Before.jpg) | [After](images/boost-status-2026-11-13/320-unavailable-After.jpg) |
| 320 wide, saved XP boost | [Before](images/boost-status-2026-11-13/320-saved-Before.jpg) | [After](images/boost-status-2026-11-13/320-saved-After.jpg) |
| 320 wide, scrolled saved Coins boost | [Before](images/boost-status-2026-11-13/320-saved-coins-Before.jpg) | [After](images/boost-status-2026-11-13/320-saved-coins-After.jpg) |
| 1280 wide, both complete cards | [Before](images/boost-status-2026-11-13/1280-mixed-Before.jpg) | [After](images/boost-status-2026-11-13/1280-mixed-After.jpg) |

Root and independent Astra inspection accepted the stronger multiplier hierarchy and distinct active/neutral status treatment. All 64 After label/button TextFits observations pass. Narrow saved buttons are visible in the respective XP/Coins views; normal scrolling clips the other card at the viewport edge. A separate actual 2.1-second expiry check changes ACTIVE to Not active and restores both neutral text and band colors.

## Checks and provenance

- New actual Render/Tick/Clear differential: 29,879 assertions and 11 negative controls. It compares complete API/cache/action behavior and unrelated UI against the exact prior module, allowing only the intended boost styling/layout changes. Retained boost, pricing, modal lifecycle and style controls pass.
- Final local aggregate/build: all 249 commands pass, including 25 pure/synthetic suites, 138 mocked suites and 64 production compiles. All 339 selected inputs were unchanged and independently rehashed. Astra independently reran the focused suite and audited aggregate results, current inputs, all 10 native images, five loaded source bindings, expiry and cleanup.
- Production Windows working-file SHA256: `6d4325ff143995ccddbf9084be33b25a609d1eda6350d0ec370abab890444b4e`; normalized-LF source SHA256: `186278f330a91104fa047482a839139d4e22bd62b28d22b06f67c88745cb22e4`. Prior normalized ShopUI: `32df0b37035ff7c9d29bdde7b5fa8fd474ccf852dbd499d7f66d31679156c4d4`. Native source bindings normalize line endings before comparison.
- The existing disposable local 0/0 place provided unchanged Config/Catalog. Three small owned sources (BeforeShop, AfterShop and fixture LocalScript) were independently reread before Play. The sole Shop source substitution forbids Marketplace requests; unchanged zero IDs yielded zero lookup calls and zero actions. The separately built boost place was build-only, not the binary opened for these images.

[Portable evidence and image/input hashes](../tests/evidence/boost-status-2026-11-13.json) preserve the exact local verification scope without publishing machine paths or raw logs. The initial pre-Play source-assignment failure and the later cropped-viewport capture run remain private diagnostics; these are the accepted maximized-window images.

## GitHub integration verification

The completed source was integrated above published `e66624a`. The test and review builder now read published `5622daa` for Before: its ShopUI bytes exactly match the reviewed local baseline (`32df0b37...`). Only those two baseline constants change in the portable readers; production remains identical to the reviewed source.

A fresh `--no-local --no-hardlinks --single-branch` clone passed **249 aggregate/build commands in 65.22 seconds**, with **341 input hashes unchanged and rechecked**, plus the boost's **29,879 assertions/11 negative controls** and standalone review builder. The clone had no alternate object store and could not resolve either local source checkpoint before execution. The extra two selected inputs are the previously published renderer-baseline helper and fixture; the original native/local evidence above remains a separate **339-input** historical result. [Integrated source/input/image hashes](../tests/evidence/boost-status-github-integration-2026-11-13.json). No additional native execution or CI result is claimed by this integration.

## Limits and cleanup

This validates the fixture's boost cards, not the complete Shop modal, actual phone/touch/gamepad input, OS text scaling/notches, real commerce/receipt delivery, live inventory, persistence or performance. Logical widths are synthetic allocations in the native renderer. The older world/HUD behind the comparison is fixture context only.

Play stopped; new GUI/control and all three owned source instances were removed, the older fixture cleaned and avatar unanchored. The existing unsaved review window was preserved and minimization verified. No new app window, user-app change, hosted test, Roblox publication, upload, permissions change or shutdown. The completed visual source is suitable for the authorized GitHub draft workflow; device and real-commerce acceptance remain separate.
