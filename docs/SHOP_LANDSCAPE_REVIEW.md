# Bounded Shop landscape trial

Baseline: exact guarded desktop minimap build in iPhone 13 landscape Studio emulation, reported safe camera 749×388. The shop scroll frame was 132 px tall against a 1,024 px canvas; the first 260 px feature put its 44 px action at y206. Most of the first feature and all purchase availability were below the opening fold. Across both orientations, operator reports 59 TextFits passes and close visible, so this does not address alleged clipping.

Candidate: Shop-only breakpoint on actual modal ScreenGui width ≥644 px and height 326–430 px. Spectrum card 124 px tall, unchanged brand, heading, copy, preview and product action; two columns put the preview and same 44 px button on the right, ending at local y110. Other product cards, scrolling, shared modal, portrait and full-height desktop unaffected. Cache key and height-only layout path distinguish this breakpoint. No price, entitlement or purchase changes.

Guarded local artifact build/SustainedLocalPlay.rbxl SHA-256 cbe58089e677f4d69b33cc9b514a0113a2f3f8960c8fc1a82b97d0c7cd815547. All original beam templates kept. 116 Shop price/geometry assertions in coroutine mocks, 102 modal lifecycle and 18,400 minimap transition assertions, plus Client/ShopUI compile pass; no Studio testing here.

Native acceptance: reset scroll at Shop open and compare exact two builds in measured iPhone 13 landscape. Spectrum title, both supporting lines, beam and full status/button should be visible, not hidden by shell, cutout or scrollbar. X remains 44 px; tabs and opening/closing/reset/shop restoration unchanged. Rerun at portrait and ordinary desktop, including rotation while open; measure TextFits/default text and keep largest-text and physical input explicitly unverified unless exercised. Verify footer and later items still scrollable without purchase. Require independent critique before accepting. No publication.

Native acceptance: exact guarded trial SHA-256
`cbe58089e677f4d69b33cc9b514a0113a2f3f8960c8fc1a82b97d0c7cd815547`,
Studio IDs 0/0, log `212127Z_Studio_E5ACD`. At Studio iPhone 13
landscape safe viewport 749×388, the full first card and existing 44px
Coming Soon status fit without scrolling. All 29 sampled texts fit;
canvas 1024→888px and last CTA remained reachable. In-play rotate to
portrait retained old stacked geometry (320×400, 1148px canvas);
nonemulated desktop also matched original (676×464, 1024px canvas).
Both had 30/30 TextFits. Separate critic accepted this landscape layout
scope only. Same-width height breakpoint, larger text, physical touch
and live commerce were not validated. Owned test windows closed without
save; nothing published.
