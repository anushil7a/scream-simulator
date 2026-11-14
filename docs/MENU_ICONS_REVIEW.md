# Original menu icon set, November 13

Shop, Beams, Quests, Style, Map and Settings now have distinct original navy/gold/cool-blue symbols beside their existing labels: coin stack, beam emitter, checklist, color swatches, folded map and sliders. Static Roblox GUI primitives provide crisp facets and highlights without uploaded images or third-party assets.

The existing button instances, callbacks, selection colors, fonts, focus eligibility and 44-pixel targets remain. Measured text width decides whether the 20-pixel icon fits with its six-pixel text gap and side margins. If not, only the icon hides and the original label centers. No smaller type, icon-only controls, new event handler, loop, dependency or per-layout allocation.

Vault consultation: `21 fwjelaa UI Design System/Glossy Icon Style - Owner Reference` (recipe and pitfalls), `UI Icon Pack - Third-Party Icons` (reference/licensing guidance) and responsive UI guidance. This is an original crisp faceted interpretation, not a claim of matching raster gloss. No unlicensed pack art was imported.

## Visual evidence

- [Before](images/menu-icons-2026-11-13/before.jpg) is the preserved prior native sound-card capture at the exact unchanged pre-icon Client source, not a newly rerun baseline.
- [Desktop after](images/menu-icons-2026-11-13/desktop.jpg) and [390-pixel allocation](images/menu-icons-2026-11-13/allocated-390.jpg) show all six distinct icons, readable labels and retained selection contrast.
- [320-pixel allocation](images/menu-icons-2026-11-13/allocated-320.jpg) intentionally uses text-only Beams, Quests and Settings tabs; remaining icons fit without reducing text size. These are desktop window allocations, not phone screenshots. Settings content still scrolls as before.

## Verification

- 471 focused actual-helper/registration/layout/selection assertions and seven negative controls pass, including rotated primitive containment, six-pixel text gap, narrow fallback, passive decorations, real callback guards and no repeated-layout allocation.
- Review caught subpixel rotated overhang in the first design; one-pixel group translations fixed it. Restoring the old emitter position fails the strengthened oracle.
- Three existing snippet fixtures needed a documented passive decoration double; their real tab callbacks remain. One now extracts the complete multiline registration instead of only its first line. Retained microphone notice 386/3 controls, panel lifecycle 38/6, shop lifecycle 110/11 pass. The actual decorator has its own focused tests.
- Final local aggregate passes 241 commands: 25 pure/synthetic suites, 130 mocked suites, 64 production compiles and requested builds. All 327 input fingerprints and log hash were rechecked. This is not CI.
- Exact-source local Studio fixture passes 5,943 checks over 24 viewport/selection rows, inspecting all six tabs each time. Checks include real TextBounds/TextFits, rotated glyph corner bounds, button/sibling/text containment, 44-pixel targets, passive descendants and selected palette. Detailed rows were retrieved separately after console truncation. Rendering/selection is synthetic with fake mic/remotes; no server scripts, real purchase or gameplay.

[Machine-readable evidence](../tests/evidence/menu-icons-2026-11-13.json). The disposable PlaceId 0/GameId 0 fixture was stopped and its verified task process closed. PC left on, no cloud save or publication. Physical input, OS text preferences and performance remain unverified; existing microphone/multiplayer and mixed-version release gates remain open.
