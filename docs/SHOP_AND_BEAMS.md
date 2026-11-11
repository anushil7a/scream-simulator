# Shop, color pass and level-based beam effects

Implemented locally on the shared development branch. Nothing in this change publishes a Roblox place or creates a live product.

## Owner-approved behavior

- One permanent Spectrum pass unlocks the hue-only beam-color picker. Yellow is the new/default base; retired free preset choices are no longer selectable. Existing saved legacy auras and exact custom shades are preserved. Explicit hue edits use full saturation/brightness; simply opening Style does not normalize saved colors. Ownership is checked on the server before equipping or broadcasting a custom color; a saved selection alone grants no entitlement.
- Double XP and Double Coins are separate repeatable developer products. Each new confirmed receipt atomically activates 30 minutes from the later of current time or existing expiry, including time offline. Duplicate receipts do not add more time. Previously saved inventory tokens remain manually usable; the multiplier stays 2x. XP and coin timers are independent.
- Freerunner exposes the existing movement pass: extra jumps and consecutive rolls in safe areas; standard arena movement remains.
- The Amplifier shop, six-tab menu, and HUD use a navy/cyan energy theme. Purchases without configured IDs say Coming soon. Configured prices come from the client's Roblox product metadata; no fixed Robux price is presented as live.

## Configuration before release

Create these products in the intended experience only after owner approval. Suggested starting prices are design proposals, not configured prices: Spectrum 199 Robux, 30-minute XP 49, 30-minute coins 39, Freerunner 149. Actual prices and regional prices are set in Creator Hub and loaded dynamically.

Set Spectrum, XP and Coins IDs in `src/ReplicatedStorage/Shared/ShopCatalog.luau`. Set the existing movement pass ID in `src/ReplicatedStorage/Shared/Config.luau` (`MovementPassId`); the Movement catalog entry delegates to that field. Keep product IDs unique. Never repurpose an old developer-product ID, because unresolved receipts can arrive later.

Before enabling sales, use an approved test experience to verify pass ownership, regional price display, a real purchase receipt, activation, leave/rejoin and unavailable-data retries. Local mocks do not verify Roblox payment delivery or real datastores. Products remain disabled in Studio, disposable fixtures, temporary profiles and developer test sessions.

## Purchase persistence

`Commerce` is the only ProcessReceipt owner. It returns PurchaseGranted only after an atomic UpdateAsync both extends the absolute boost expiry and records its receipt ID (without minting a new inventory token). Failed or unknown receipts remain NotProcessedYet. Prompt close events never grant products. All transforms are retry-safe, including a write that succeeds while its response is lost.

Paid inventory, expiry timestamps and receipt IDs use `ScreamSimulator_Purchases_v1`, separate from gameplay saves. Normal profile autosaves and the test-session baseline cannot overwrite purchases. Legacy saved-token activations atomically consume a token and extend expiry; temporary operation IDs prevent retries from consuming it twice. Per-user locks, prompt/activation/refresh limits and server eligibility checks bound requests. Gameplay progress retains its existing session lease.

Receipt IDs are never pruned. At 8,000 receipts per user, new prompts/grants fail closed pending a reviewed ledger migration; duplicates still acknowledge safely. There is no background job or schedule. A datastore error invalidates the local purchase cache; reopening the shop retries loading (15-second throttle). Already stored purchases remain in the ledger.

## Beam presentation and performance limits

The sustained attack now uses an animated rig instead of a single thin line. White cores sit inside translucent colored cylinders. Traveling rings increase with level; level 40 adds a spiral, level 80 a second strand, and level 90 increases the spiral winding and ring count. The endpoint corona gains rays at levels 20 and 70. Width and core size grow between these milestones. Level comes from the server's latched attack, independent of the selected sound.

Combat damage, target geometry, 4-second duration and the owner's quiet beam SFX are unchanged. The November 11 core-game batch changes the automatic beam cooldown to five seconds after attack end. Rings/coronas are cosmetic and stay within beam width. There is no added camera shake, flashing light or extra audio. Reduced effects retain the core and endpoint only; distant attacks drop decoration beyond 110 studs and stop rendering beyond 180.

The existing manager caps attackers at 24 and expires stale pulses after 0.5 seconds. Rigs reuse parts across pulses and attacks. Allocation is capped at 512 Parts; decoration reserves five core slots per attacker. Animation updates at most 30 Hz before the slower HUD query throttle. These are bounded allocations, not a measured FPS improvement or a multiplayer performance claim.

## Reproduce local checks

Run `python tests/verify_local.py --build` with Luau and Rojo on PATH. Open `build/SustainedLocalPlay.rbxl` for the current game; press Play. Open `build/BeamReview.rbxl` for the six-tier showcase and geometry/pool audit. Open `build/ShopReviewVerified.rbxl` for the mocked UI layout audit at portrait 390x844, landscape 844x390 and desktop 1280x720. Preview purchase buttons send no real purchase requests. None of these review fixtures should be published.

Useful later cosmetic ideas: KO finishers, spawn trails, player titles and saved color presets. They are not sold or implemented in this change. Avoid paid direct damage/health purchases while validating the existing level advantage.

Roblox references: [developer product receipt handling](https://create.roblox.com/docs/production/monetization/developer-products), [purchase data persistence](https://create.roblox.com/docs/cloud-services/data-stores/player-data-purchasing), [regional pricing](https://create.roblox.com/docs/production/monetization/regional-pricing).

Current behavior and limits: [boost delivery](BOOST_PURCHASE_REVIEW.md), [hue-only controls](BEAMS_STYLE_REVIEW.md). Historical HSV/manual-token claims are superseded.
