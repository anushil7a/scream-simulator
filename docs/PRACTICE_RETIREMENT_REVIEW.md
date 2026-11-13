# Mic practice area and objective retirement

November13,2026. Owner explicitly requested removing mic testing, its area and all related objectives. Implemented only in the isolated resume worktree; original checkout/contributor edits and archived map remain untouched. No publication, live store operation or native acceptance claim.

## Scope

- Removed compact practice backstop/target, stand line, frames, header/beacon and mic tutorial signs. Removed the legacy runtime City's MicPracticeLane block too. Preserved all59 original archive files byte-for-byte and archive ZIP hash.
- Kept the same useful spawn-to-training/arena route as RouteFromSpawn. Removed the practice minimap landmark and footprint; seven display-only landmarks remain. No NPC training, Nick soccer practice, quest station, PvP bounds, movement or reward tuning was removed.
- Removed both sustained and legacy production MicPracticeTarget branches, including practice pulse, quest progress, achievement writes and hit/tutorial notices. Physical obstruction and actual combat handling remain.
- `practice_beams` remains a permanent Config tombstone: `retired=true`, original goal3,60XP,25coins, original ID/event. No objective description/menu availability. AcceptQuest and questProgress reject it. ClaimQuest keeps its existing authoritative flag-before-grant path so previously completed-unclaimed rewards remain collectible. No automatic completion, refund, ID reuse or conversion.
- Profiles was deliberately not modified: its existing catalog-based sanitizer preserves dormant progress, discovery and claimed state because the definition remains known. Historical FirstBeam achievement remains inert. ActiveQuest is session-only, not saved.
- Client claim-only display and calibration removal are a separate coordinated worker's scope. Native FirstBeam/CastFeedback/VoiceTransport adapters are separately owned; they must not retain a hidden production practice target.

## Evidence

- New `tests/practice_retirement.py`:227 assertions using actual Config, Profiles, ProfileLease, extracted production Accept/Progress/Claim and production coin/XP helpers with actual Progression. Seven controls reject missing retirement, acceptance/progress bypass, repeated payout, lost counters/discovery and achievement loss. Pinned53d6213 baseline lacks the tombstone as expected. Isolated in-memory UpdateAsync only, not Roblox services.
- States absent/discovered-only/zero/partial1/partial2/complete/claimed survive repeated sanitization, acquire/save/release/reload. Only completed-unclaimed earns25coins/60XP once, including reentrant multiplier callback and post-save rejoin. Unrelated active garden/economy remain unchanged. Reward multipliers are fixed1 in this fixture; no live purchase/network claim.
- Retained combat_quests:169 assertions/seven controls, including actual assist/reward paths and save preservation. Legacy practice-progress assertions were replaced with retirement assertions, not silently kept against a synthetic hidden target.
- Current/historical writer compatibility:46 assertions plus11 controls/probes pass. Historical7a writer still drops unknown practice/assist state. Retired practice cannot be newly completed after the loss; active arena_assist replay remains reproduced. This retirement is NOT a mixed-version fleet fix. Existing release gate stays blocked.
- compact_world:1534 constructor checks,47 static reachability targets and16 controls. PracticeStand is the one deliberately removed target; all others retained. Static clearance cells rise24571->24581 after removing the backstop.
- coastal_art:1946 checks/six controls,291 static art pieces. Surviving original inventory matches pinned09e0996 after filtering only eight explicit removed objects and normalizing the route rename. Fingerprint derived from the pinned original constructor, not copied from the candidate. Colors are outside that earlier geometry fingerprint.
- compact integration122/11; compact map97/7; minimap visuals630/4; compact guidance81/4. Existing isolated draft geometry remains historical and unchanged, not the current runtime.
- practice_lane now checks retirement source contracts, retained training/soccer and exact archive; pinned fallback comparison proves only the original MicPracticeLane block was removed. Two source-token controls are deliberately static checks, not runtime proof.

## Vault and acceptance limits

Consulted existing vault Quests and Objectives permanent-ID/persistence guidance and current vault/AGENTS targeted retrieval rules. Removed user-unwanted onboarding rather than adding replacement systems. Native map/claim UI and automatic-microphone behavior need composed local testing. Full aggregate/build and independent exact-diff review are coordinator gates; neither is claimed here. No CI claim.

- Explicit requested presentation cleanup: removed remaining full-map North symbol and both “North is up” help sentences; minimap already omitted that symbol. Projection, full-map facing arrow and meaningful PvP/activity guidance remain. Focused minimap tests include an injected-N rejection and orientation-copy absence assertion. No native visual claim from these mocks.

- Retained quest_catalog_ui: 1683 actual-renderer assertions and 12 negative controls. Both widths cover absent/zero/partial/earned/claimed retirement states with discovery and stale active flags, claim-only earned card, hidden retired active objective, unchanged catalog/state, exact remaining group ordering, and retained discovery/restart/claim behavior. Synthetic UI only, not native fit/input or server reward verification.
