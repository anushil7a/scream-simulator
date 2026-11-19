# Test Tools launcher flashing over Shop

## Root cause and change

The old State callback showed the launcher whenever `devAccess` was true.
The frame callback separately hid it over the modal. State refreshes could
therefore show the launcher at a higher Z-index while Shop remained open.
The launcher now uses the same current eligibility for visibility and
activation. It updates synchronously on modal changes, including the
conversation handoff. A stale click cannot open tools or close Shop.
Server authorization, commands, shop prices and minimap policy are unchanged.

## Evidence (local Windows Studio, not a release)

- Original exact guarded place `8e188b74…` flashed the launcher over a
  settled Shop at about 0.5–1 second intervals, for about 1–8 observed
  frames at 60fps, even without a launcher click or viewport resize.
- Exact fixed place SHA-256
  `48588345ba5e93f1bbbc62f946e1e3335cad01d85e945ab5da1978cf64d06f66`;
  runtime source `c8bfaf218b174e047ea7424c55573c204840e52e8ba5ad6cd4f7979f4a870bda`,
  Studio / GameId / PlaceId = 1 / 0 / 0. At 2042×912, initial Shop held
  and scrolled 875 frames (14.57 s) through 26 actual State packets
  with zero overlap. Shop↔Quests and top-toggle checks reached 1,310
  modal frames and 39 modal packets with zero overlap. Tools opened and
  closed normally outside Shop, and the minimap reappeared after close.
- Final comparable trace: 4,210 total PreRender frames, 3,607 modal
  frames (~60.1 s), and 108 authentic State packets while modal, with
  **zero Test Tools overlap**. All eight raw visibility edges belonged
  to normal hide/show on open/close. Also verified X, quick reopen,
  scrolling, top toggle, Shop↔Quests, and opening Shop with the
  authorized Test Tools panel already open. A short minimap-only
  handoff occurred entering menus; its policy was not changed and
  this test does not certify all menu-layer flicker. No mobile run.
- 7,502 mock transition and stale-input assertions, six negative
  controls (including actual old State writer), 15 focused suites and
  the notice fragment's 629 assertions/controls passed. All 93
  production scripts compiled. The wider comparison still has six
  known unavailable historical Git baselines; no full aggregate pass.
- No physical-device input, live purchases, publication or gameplay
  release inferred. This full-game Shop build is separate from the
  Academy artwork and shoreline trials.

Exact local Windows file:
`Downloads/Scream Simulator - Shop Flash Fix/ScreamSimulatorShopFlashFix.rbxl`.
The checked Studio session closed without saving; the file hash was unchanged.
