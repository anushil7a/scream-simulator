# Coastal academy HUD / mic presentation candidate

## Scope

Client-only presentation pass against `dda67e3`: deep ink/slate surfaces, warm ivory text and restrained beam-gold accents replace the flat navy/cyan palette. Selected HUD, navigation and action surfaces gain subtle top-light gradients and one-pixel borders. Original waveform, health and progression glyphs are drawn with small noninteractive Frames, not images/assets. The compact HUD has icon-led rows; mic setup has a waveform header, secondary calibration heading and inset status well. Live mic status retains its previous width/height. Top-center zone/save status now has dark backing within its unchanged label rectangles for contrast over bright sky. Primary beam state coloring still comes from the existing state logic, not a blanket gold override.

No new module/dependency, subscriptions, animations or standalone lifetime. Decorations belong to existing owned GUI trees. Existing outer layout rectangles, mic close/calibrate/retry controls, touch sizing, controller calls, readiness gates, stop handling, notice layout and modal behavior are unchanged. Compact HUD internal text positions/font emphasis changed and require native inspection, including large coin balances. No lock-on control is added in this task.

## Guidance used

- `roblox-ui/SKILL.md`, `LOCAL.md`: selected local tools only, preserve controllers, native screenshots remain ground truth; no imports/uploads or upstream orchestration.
- `roblox-ui/references/ui-recipes.md`, sections 1–2: identity and depth. Applied a restrained one-pixel treatment rather than copying the reference's heavy five-pixel strokes onto small text.
- `vault/AGENTS.md`, targeted query `HUD visual hierarchy`; `vault/fwjelaa/fwjelaa vault/05 UI and UX/HUD Design.md`, sections 1–2: existing screen zones, clear central gameplay area, actual placement rather than copied layouts. No replacement layout system imported.
- Read `build/visual-spawn-before.jpg` as the baseline. No new native screenshot captured by this worker.

## Focused verification

- `python tests/hud_presentation.py --negative-controls`: 69 actual decorator assertions, eight authored geometry/status contracts, four intended-failure controls. Tests bounded geometric icons, in-bounds/noninteractive children, parent ownership and preservation of existing control properties. Mock GUI only.
- Actual Client startup: 320 boundary scenarios +18 ownership scenarios /12 controls.
- Mic setup navigation:35 /10 controls; microphone notices:402 /4 controls +3 contracts.
- Beam screen integration:91 /18 controls; NoticeView:622 /23 controls +3 contracts; HUD health:9 checks.
- Client Luau compilation passes. UI-only Onboarding builder passed; final source should be rebuilt for visual evaluation because a later equivalent XP-glyph creation-line relocation preserved the unchanged health test extraction.

Initial HUD health extraction included the added XP glyph because it sits immediately before the existing xpText anchor. Moving this decorative call after the XP fill restored the original exact health fragment; no retained assertion was removed.

## Pending visual gates

Native desktop/phone text fit, actual screenshot art direction, large balances, mic denial/calibration messages and physical touch behavior remain pending. Synthetic object/geometry tests establish neither aesthetics nor native font rendering. No server, map, saves, live services, publication or Studio operation performed here.

## Integrated native follow-through (November13)

Coordinator inspected actual desktop mic setup, HUD and status in the local place0 preview. Backed zone/save text has visibly better contrast; actual close control works. Three cloned actual HUD labels passed native font fit, including LEVEL100 with1000000000 coins:188x12 text in194x22. These are isolated layout samples, not live balance or phone validation. Integrated Client also includes separately reviewed lock-on; its final ownership matrix is352 boundary scenarios/19 ownership cases/12 controls. Physical touch, large OS text, all denial strings and gamepad navigation remain gates. See [checkpoint evidence](../tests/evidence/visual-lock-checkpoint-2026-11-13.json).
