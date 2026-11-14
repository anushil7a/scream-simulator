# Beams terminology and hue-only style review

November 11, 2026. Base: `d4cf66804f2a409dda39ac78c254aedb68b05a06`. Draft branch only; no publication or live DataStore access.

## Owner request and behavior

- Player-facing attack/toggle/collection/help, quest, volley and NPC wording now says **Beams**. Internal tab key `Screams`, sound IDs, effect verbs, attributes, remotes, world names and DataStore keys stay compatible. This does not rename the Roblox experience or repository.
- Style has one 44-pixel hue control and an Equip button. Saturation/brightness sliders, the preview strip above hue and editable hex entry are removed. The remaining color code is read-only. Explicit hue edits produce full-saturation/full-brightness colors.
- Opening or reopening Style does not alter a saved custom shade. Its exact hex remains until a deliberate hue edit/equip. The Spectrum entitlement and server hex validation remain required. Product IDs are still zero; no purchase/configuration was performed.
- New players retain the existing warm-yellow Gold base (`#FFCB63`). The five free preset buttons are replaced by an explicit **USE YELLOW** reset. Server `SetAura` accepts Gold only, so hiding the palette cannot be bypassed by requesting Mint/Violet/Ice/Coral.
- Existing selected legacy aura colors are grandfathered, not wiped or normalized. A notice explains that choosing yellow replaces that old selection and the retired free palette cannot be reselected. Existing custom hex remains stored even when yellow is chosen, and an entitled owner may re-equip it. `Config.Auras`, Profiles and Entitlements are preserved; no schema migration is needed.
- No combat timing, physics, progression, map geometry, audio asset or paid ownership behavior changed. World changes are dialogue strings only.

## Verification

`python tests/style_controls.py --negative-controls` passes **336 assertions**: 261 actual mixer/server color-branch/beam-color checks, 35 actual Profiles fake-store save/rejoin checks, and 40 actual Style renderer checks. Eleven mutations fail at their intended assertions. `--baseline` reproduces the original extra sliders.

Coverage includes exact dark/desaturated saved shades, preview-only locked input, entitled/invalid hex, forged free colors, yellow reset, second-pointer rejection, release, Clear/disconnect, stale callback and reopen behavior. These are synthetic input signals and fake atomic persistence, not physical-device, RemoteEvent transport or live ownership tests. Independent review reran all 336 checks and eleven controls with no blocker. Existing migration and entitlement suites also pass.

Full final command: `python tests/verify_local.py --build`. Passed all 25 pure/synthetic and 68 mocked suites, 57 production compiles and candidate/disposable builds. Final rebuilt native fixture hashes match the executed files. The final result and source hashes are in [evidence](../tests/evidence/beams-style-2026-11-11.json). Naming expectations in current toggle/guide/notification fixtures were updated, including anti-stale-notice comparisons, without changing notification behavior.

## Native observation

The exact generated `StyleReview.rbxl` was opened and played in disposable Studio on November 11. Output reported **687 checks, 15 cases**, with zero clipped style text measured by each label's `TextFits`. Cases were new locked, legacy free selection, saved custom, inactive custom and new pass owner at 390x844, 844x390 and 1280x720. Each hue control was 44 pixels high. Saved dark `#0A2F53` and desaturated `#A0B0C0` displayed exactly. The inspected desktop screenshot showed BEAMS and the single hue control, with no old preview strip or extra sliders.

This executes the actual client layout with synthetic state/microphone/remotes and an empty floor. It does **not** establish physical mouse/touch input, gamepad/keyboard slider accessibility, real purchase/pass services, live saves or multiplayer. TextFits is not proof against ancestor clipping/occlusion or of scrolling reachability. Native title/subtitle fit and all other menu layouts were not comprehensively checked. The independent reviewer inspected the fixture but did not rerun Studio.

A pre-existing Studio asset warning for `203785492` appeared before/at play: "Asset type does not match requested type". The fixture completed; the warning's source is not established and is not attributed to this change.

## Cleanup and next gates

Studio was stopped and closed without saving disposable runtime changes. Pre-existing ChatGPT was preserved. One new minimized Windows app-picker dialog appeared during launch, alongside the earlier one. Both cannot currently be restored/closed through the exposed supported controls (`window is minimized`; suggested restore APIs are not exposed). No approval is pending; no process-kill workaround was used. No browser tabs were opened.

Next: verify draft-branch delivery, then continue the requested minimap/audio or other bounded gameplay batch. Real voice/touch/purchase/persistence and release authorization gates remain. Do not publish this candidate.

## Wave 2 style-customization polish

- `Shop.ColorMixer` (`ShopUI.luau`) now renders a passive `24x24` `ColorSwatch` chip at `(16, 186)` with `Active = false`, `Selectable = false`, `Interactable = false`, and an `ink` `UIStroke` border, updating `swatch.BackgroundColor3 = color` live inside `update()` alongside `SelectedColor` (nudged to X offset `48`, width `UDim2.new(1, -64, 0, 24)`). Saved custom shades remain preserved on open without HSV normalization, and no editable hex or extra sliders were added.
- `tests/style_controls.py --negative-controls` now passes **317** actual mixer/server branch checks (plus 35 Profiles checks and 40 Style renderer assertions) and **12** negative controls (10 mixer/server/swatch + 2 Style renderer), verifying `ColorSwatch` sizing, passive input flags, border stroke, non-overlap with `SelectedColor`, saved-shade preservation, and live hue/touch/locked-preview tracking. Native Studio `TextFits` re-measurement for the updated `ColorMixer` layout was not rerun in this pass.
