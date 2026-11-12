# Readable short-screen notices

November 12, 2026. Local UI correction based on source/geometry reproductions. No native execution of this change.

## Established problem

The old full-width, bottom-anchored toast could overlap MAP, authorized Test Tools and nearby-NPC TALK at cramped touch sizes, including320x315 and640x360. Its35%-height cap could clip full warning text while queue lifetime continued. The earlier native minimap pass used only a short placeholder warning and did not establish full production-warning readability. This is not a claimed physical-device incident.

## Implemented behavior

- NoticeLayout reserves a lane below top navigation and left of MAP/tools in the existing safe-area GUI. Only overlapping passive HUD labels are temporarily hidden. One-line messages use a compact panel rather than the full lane.
- NoticeView keeps the complete string in a bounded scrolling viewport. Font size is not shrunk. Measured text is cached, with conservative adjustment when actual TextBounds grows. Position updates independently of the measurement cache.
- Overflow pauses normal queue dwell until its bottom has been exposed. Hover and recent input/scroll pause time too; new entries and layout changes do not immediately consume dwell. Entry identity resets exposure even when replacement text is identical. Existing queue priority, save coalescing/removal and eight-pending bound are unchanged.
- The entire44px-or-larger panel remains the scrolling target. The later measured-cue correction below places a wrapped header inside the scrolling content, so it cannot cover the last line. This is source/mock validation, not native touch pass-through proof.
- In the main menu, failed purchase/quest notices remain visible in a lane above modal Close/tabs. Redundant top launchers hide temporarily; modal navigation remains. Other setup/conversation/developer panels and focus/core-menu interruptions pause notices rather than spend hidden dwell.
- TALK moves only into a fitting top-navigation slot, never into the bottom-left thumbstick area. If a cramped nearby-NPC layout cannot accommodate the notice, it stays retained and the existing Quests launcher says NOTICE. Its unchanged callback opens the main menu and exposes the full retained message. The normal current unclaimed-quest count restores after disclosure/clear/resize.

No server, save, map/world, product or asset configuration changes. No new modal, copied queue, per-message jobs or imported assets.

## Review and verification

- Final focused actual modules plus Client-fragment tests:604 assertions,16 explicit mutation controls and3 source contracts. Uses exact93/85/142/114-character production warnings, synthetic GUI/text metrics and the actual queue. Separate Astra rerun in memory cleared all controls and final source hashes.
- Retained minimap suite:137 module prefix /987,778 combined geometry assertions and16 controls. Replaces obsolete fixed-toast arithmetic with actual NoticeLayout and the NoticeView panel-height expression; unavailable tiny cases are explicitly classified, not counted as visible passes. No CityMap edits.
- Retained beam integration:91 assertions/18 controls. Extraction now excludes unrelated resident/notice code inserted between the acknowledgement hook and feedback cadence, while preserving the actual hook and Step-versus-HUD-gate ordering. Independent rerun confirmed the moved-Step control still fails as intended.
- Final aggregate:25 pure/synthetic suites,103 mocked-service suites,63 production compiles and all disposable builds passed. Initial aggregate failed at the removed old toast-position extractor; a subsequent remaining-fixture sweep found the unrelated-fragment beam extraction issue. Both fixture adaptations are recorded, not production regressions concealed by removing checks.
- Independent review caught and corrected two candidate regressions before checkpoint: the per-frame default quest label erased unclaimed counts, and a separate hint footer reduced the actual scrolling target below44px. Corrective tests include actual receiver/launcher transitions and padded last-line clearance.
- Built/compiled NoticeLayoutReview exercises full strings across48 synthetic viewport/access/message cases, programmatic scrolling, focus pause, modal navigation separation and cached-width recentering. Retained native builders now use the visible viewport, not full offscreen text-canvas bounds. **These fixtures were not run in Studio.**

Commands actually run:

```text
python tests/notice_view.py --negative-controls
python tests/minimap.py --negative-controls
python tests/beam_screen_integration.py --negative-controls
python tests/build_notice_layout_review.py
python tests/verify_local.py --build
```

Exact source, fixture and log hashes: [notice-layout evidence](../tests/evidence/notice-layout-2026-11-12.json).

## Limits and next gate

Bottom exposure is not proof of reading. Ignored overflow may intentionally hold the active bounded queue indefinitely; higher-priority save warnings can still preempt and state recovery removes them. Normal bounded overflow policy still may discard lower-priority pending messages. Arbitrarily small viewports may not fit even the existing navigation; no universal accessibility claim. Actual font preferences, native cue/input pass-through, scrolling, safe areas, physical thumbstick reachability and user comprehension remain unverified. Complete native/device verification when a disposable Studio route is available without creating further orphan picker windows.

No Studio/apps opened for this batch, no live services/purchases or publication. Existing map approval, test-place identity and writer-fleet release gates remain.

## References actually consulted

- `vault/fwjelaa/fwjelaa vault/05 UI and UX/Notification and Toast Systems.md`, sections1/3: channel choice, bounded queues and readable lifetime. Reference guidance, not permission to replace the architecture.
- `vault/fwjelaa/fwjelaa vault/42 Accessibility and Inclusive Design/Readable Text and UI Scale.md`, sections1/2: preserve readable type and allow scrolling rather than silently shrinking content.
- `vault/fwjelaa/fwjelaa vault/05 UI and UX/Safe Areas and Insets.md`, sections1/2: interactive coordinates remain within the existing safe-area GUI.


## November 12 larger-text and input follow-up

A read-only audit found two limits not resolved by the earlier geometry checks. The main notice can expand from observed TextBounds, but the passive scroll cue and end padding are fixed at16px and never measure the cue's own bounds. If a preferred font/text setting makes that cue taller, it can clip; this has not been observed on a native preference setting. FullNotice sets Active but has no explicit selectable/focus or keyboard/gamepad scrolling path. Do not infer either failure or accessibility success from undocumented default properties. Existing fixtures set CanvasPosition directly, so they prove bottom-exposure handling, not input discoverability/reachability.

Native acceptance checklist, still **not run**:

- Use the actual full93/85/142/114-character warnings at640x360 and320x315 safe-area sizes, with and without Test Tools and nearby TALK. Repeat with the largest supported text preference and change it while a notice is visible. Check the complete body/cue TextBounds and TextFits, no control overlap, and reset/reflow on replacement/resize.
- Touch: discover the overflow cue, drag beginning on body and cue, reach the last line, revisit the beginning, and verify queue dwell pauses during input without blocking nearby movement/action controls. Use a physical phone for thumbstick/cutout reachability; a frame resize is not a phone test.
- Keyboard: without mouse scrolling, discover the NOTICE/Quests fallback and reachable full text, scroll to the end, and return focus to the existing menu/gameplay controls. Verify typing/menu bindings are not stolen.
- Gamepad: use native selection navigation to discover/reach the notice, scroll to the end and leave it. Verify visible focus, no trapped selection, no unintended attacks, and current-menu navigation. Programmatically selecting a GUI or setting CanvasPosition is not a substitute.
- Interrupt with main menu/setup/focus loss/respawn and an urgent replacement; confirm no hidden dwell, stale text/focus or lost critical warning.

A future correction should preserve the44px actual scroll target and avoid growing an overlay until it covers the warning. Native text preference, cue pass-through and keyboard/controller completion remain release-test gaps, not passed tests. No application or setting was changed for this audit. References checked: [GuiObject selection semantics](https://create.roblox.com/docs/reference/engine/classes/GuiObject.md), [ScrollingFrame](https://create.roblox.com/docs/reference/engine/classes/ScrollingFrame.md), [TextService](https://create.roblox.com/docs/reference/engine/classes/TextService.md).


## Measured in-content cue correction

The fixed16px overlay/padding concern above is now corrected in source: a wrapped, measured cue sits before the body inside the same scrolling content. It scrolls away instead of covering the last line. The full viewport remains the scrolling target, at least44px in the supported cases. Cue/body height grows from actual TextBounds, cached measurement is invalidated, and bottom exposure resets after growth or resize. Constant cue wording avoids geometry churn. A new entry resets offsets and prior maxima. Shrinking text may conservatively leave spare canvas until replacement; this is source-reviewed, not an explicitly tested shrink case.

Only NoticeView production code changes. Client/Layout/queue/server/map and input/navigation behavior are unchanged. The old actual module fails the new header-placement regression; this reproduces the design omission with mocked metrics, not a native preference incident. Final615 assertions/19 targeted controls/3 source contracts pass independently, including80px cue metrics,900px body metrics, narrow target, bottom exposure, cache and replacement. Full25 pure/synthetic suites,104 mocked suites,63 production compiles and all disposable builds pass. The native builder now tests the last line against the actual viewport rather than subtracting a nonexistent overlay; it was rebuilt/compiled, not executed.

The touch/keyboard/gamepad and largest-text native checklist above remains open. In particular, programmatic CanvasPosition does not prove input access, and this patch adds no selection navigation. No Studio/application was opened, no live services or map changes occurred. See `tests/evidence/notice-header-2026-11-12.json` for exact hashes/results. GitHub delivery is pending an authorization-tool blocker; local preservation is not a remote push claim.


## Manual native entry point, prepared November 12

Open `build/NoticeInputReview.rbxl` **from within Roblox Studio**, using File > Open from File. Do not double-click the file through an unknown Windows association. This is a separate disposable local place, not City Preview or the actual map. Leave other user places untouched. Use **Play**, not Run, because the review is a LocalScript; Output should print `NOTICE_INPUT_READY`. That marker means initialization only, not a passed input test. Stop when finished; do not publish or overwrite the real game. If the Studio/place0 assertion fails, stop rather than removing it.

The default is a synthetic320x315 frame with touch layout, Test Tools visible, and the actual142-character recovery/foreign-owner warning. Inspect `StarterPlayer > StarterPlayerScripts > Review` while stopped to change its first constants: `reviewWidth,reviewHeight` (e.g.640,360), `reviewTouch`, `reviewTestTools`, or `reviewWarning`. Keep the rest untouched. Stop/Play resets the warning. There is no automatic scroll, forced selection, extra paging handler, perpetual refresh or frozen queue; once text has been exposed, normal queue dwell can remove it. Its actual overflow and input behavior must be observed, not inferred from the synthetic size.

Start with desktop pointer scrolling on the body/cue and verify complete text, end-of-text clearance, queue pause/consumption and unrelated control access. Then test keyboard-only native navigation without programmatic focus/CanvasPosition, and an actual gamepad if available. Repeat at640x360 and with available larger text preferences. Record exact input, rendered size/preference, last-line visibility, focus return and failures. Fixed-frame touch layout is not a physical touch, thumbstick, cutout or controller-reachability test. There is no nearby NPC/world simulation in this manual entry point; nearby-TALK fallback remains separate.

`python tests/build_notice_input_review.py` was built/compiled and independently rebuilt/reviewed. The strict Studio/place0 assertion runs before embedded modules; the place contains one Review client and a floor, no server scripts. Mic and remotes are mocked, marketplace calls blocked, and current NoticeView embedded with only dependency resolution changed. No native execution or successful input claim. See [manual fixture hashes](../tests/evidence/notice-input-fixture-2026-11-12.json). The older NoticeLayoutReview remains useful for automated geometry assertions, but it programmatically scrolls/cycles/clears and is not the manual input fixture.
