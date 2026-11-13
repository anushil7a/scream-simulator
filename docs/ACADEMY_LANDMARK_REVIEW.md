# Academy gate identity — November 13, 2026

The existing coastal academy entrance now has an original gold/slate voice crest and an ivory **SCREAM ACADEMY** title on both faces. The familiar palette and one bold silhouette identify the destination without adding props to the walking lane. This is one environmental art pass; the map and lock-on UI are unchanged.

The 21-line production insertion in `CompactCity.academyArt` adds 18 static cosmetic Parts and two SurfaceGui/TextLabel pairs. Total coastal art rises from 291 to 309, below the existing 350 cap. All new Parts are anchored, noncolliding, nonqueryable, nontouching and shadow-free, with no gameplay attributes. Supports begin at y=14; the title occupies y=17–21 and the crest y=21–31. Original geometry, gate opening, warning sign, route, spawn, constructor outputs and gameplay code are preserved by actual-constructor differential tests against the byte-identical published `5622daa` baseline.

Vault guidance consulted before authoring: `fwjelaa/fwjelaa vault/14 3D Modeling/Low-Poly and Stylized Modeling.md` (shape, thick trim and one focal feature), `Roblox-Maps-by-fwjelaa/research/04-stylized-and-level-design.md` (primitive signs and contrasting world text), and the audit's `Level Design Principles` landmark section. These are design references; their numeric suggestions are not device validation.

## Native comparison

`python tests/build_academy_review.py` builds only exact baseline/candidate CompactCity modules, exact CompactLayout and a guarded local client review script. There is no Bootstrap, profile/save service, combat, voice or production client. Only the exact `AcademyReview-final.rbxl` session was played, after native Studio/GameId=0/PlaceId=0 and loaded-source length/checksum verification. Artifact SHA-256: `77fcbfd01bbd1550819dbaf34fd37730a64a2c2a518c954655e35af939033e59`.

| View | Baseline | Candidate | Observation |
|---|---|---|---|
| West approach, 55 studs | [Before](images/academy-landmark-2026-11-13/BeforeCity-west.jpg) | [After](images/academy-landmark-2026-11-13/AfterCity-west.jpg) | Upright crest/title; existing warning remains readable below; open lane |
| East approach, 55 studs | [Before](images/academy-landmark-2026-11-13/BeforeCity-east.jpg) | [After](images/academy-landmark-2026-11-13/AfterCity-east.jpg) | Reverse title/crest read correctly; warning remains west-facing as before |
| Spawn approach, about 170 studs | [Before](images/academy-landmark-2026-11-13/BeforeCity-spawn.jpg) | [After](images/academy-landmark-2026-11-13/AfterCity-spawn.jpg) | Stronger crest silhouette; title intentionally outside its 140-stud display range |

All six images are unedited native captures. Both title labels report TextFits=true: native bounds 420.8×49.6 in a 600×72 canvas. The physical native viewport was approximately 1626×734; this does not establish phone rendering, dense-world/HUD/combat overlap, night lighting or performance.

The pre-existing asset-type warning `203785492` remains outside this art pass.

## Checks and review

- New academy constructor differential: 598 assertions, one unchanged-layout source contract and seven negative controls. Retained coastal-art 2,058/six controls and compact-world 1,596/47 reachability targets/16 controls pass.
- Full `verify_local.py --build`: 244 commands pass, including 25 pure/synthetic suites, 133 mocked suites, 64 production compiles and disposable builds. All 331 recorded inputs were unchanged during the run and rechecked afterward.
- Astra independently reran the focused checks, added 33 geometry checks/two mutants and cleared production, fixture lifecycle and all final views. Final review checks 418 evidence/integrity assertions, including all 331 input fingerprints. [Portable integration evidence](NOVEMBER13_INTEGRATION_REVIEW.md).

Native Play was stopped and owned fixture objects were removed. Real device/performance acceptance remains separate.
