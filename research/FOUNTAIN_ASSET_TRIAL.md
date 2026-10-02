# Spawn fountain asset trial

## Purpose

Test whether an original textured mesh can improve the spawn plaza's visual focal point over the current cylinder-built fountain. Keep the current procedural fountain until the candidate passes visual, navigation and reproducible-build checks.

## Completed generation

- Tool: Roblox Studio `generate_mesh`, asynchronous.
- Job: `3739ffe8-ef80-4e2f-a1a5-f7878702b27d`.
- Studio: `14656c25-2681-45fb-8f33-3c1c91c53980` (`MicrophoneCity.rbxl`, disposable development copy).
- Requested maximum: 4,500 triangles; bounding size 28×10×28 studs.
- Prompt: original Mediterranean octagonal limestone fountain, scalloped bowl, small fish spouts, turquoise/cobalt/ochre mosaic bands, empty basin for separately rendered water, no surrounding scene or lettering.
- Job completed successfully after two bounded waits timed out. It is terminal; do not poll or restart it.
- Generation ID: `02378a40-876c-4f75-8309-e87c60ac53b7`. The generation tool returned published model asset `93795363493053`; this is an art asset upload, not publication of the game.
- Actual generated bounding size is approximately 14.13×10×14.13 studs, smaller in width than the requested box. Three MeshParts, three textures, no scripts. Actual triangle count remains unmeasured.

## Acceptance checks

1. Inspect the generated geometry/materials at player eye height and from the plaza entry. Reject malformed or visually noisy detail.
2. Inspect actual triangle/instance counts and asset identifiers. The prompt's requested triangle budget is not a measured result.
3. Preserve pedestrian clearance and fountain navigation exclusion. Decoration must not introduce oversized convex-hull collision or new obstacles on the approach.
4. Confirm the asset can be saved into the repository/build, including texture references and any asset permissions. A Studio-only preview is insufficient.
5. Keep a working procedural fallback if render assets cannot load; verify the candidate in an actual local build before replacing the default.
6. Record the outcome. A failed candidate does not justify leaving an unavailable asset dependency in production.

No generated asset has been accepted into production source yet. This trial does not change the pending real-device performance, full art review or microphone release gates.

## Review result and reproducible candidate

The native Studio screenshot showed a coherent octagonal mosaic basin, slender stone pedestal and scalloped upper bowl. The fish detail is subdued; this is a candidate, not final art approval.

- Basin: mesh `103166964215779`, texture `82765873112510`.
- Pedestal: mesh `107051600752930`, texture `139740124241106`.
- Bowl: mesh `95455806342406`, texture `110660724238333`.

`assets/review/MosaicFountain.rbxmx` preserves measured sizes, original texture tint and transforms normalized to ground origin. All three meshes are anchored and non-colliding/non-querying/non-touching. `fountain-review.project.json` builds a separate review place in both formats. XML inspection confirms three meshes and no scripts; it does not prove asset rendering/permissions in a newly opened build. The main project does not reference this candidate yet.

The generated Studio object is retained as `Workspace.REVIEW_ONLY_MosaicFountain` in the disposable MicrophoneCity copy, moved to Y−1000 with collisions/queries/touches disabled. It is absent from the main Rojo build. Do not confuse that local review object with shipped geometry. Next steps: native review-build import/render, triangle/permission validation, then deliberate scaling, separate water surface and path-preserving collision integration.

## Saved-asset reload and assembled plaza review

- Reloaded model asset93795363493053 through Studio's supported insertion tool into ServerStorage.MosaicFountainReloadReview. It contains three MeshParts, nested models and a PackageLink, with no scripts. Play-time assembly strips the package link and keeps meshes anchored, non-colliding, non-touching and non-querying.
- At scale2, measured bounds are28.226×20×28.249studs. At origin(-600,1,240), the candidate fits inside the existing32-stud fountain navigation exclusion. Native screenshot confirms the textured basin, tall pedestal, scalloped bowl and four curved water streams in Plaça del Sol.
- `prototypes/fountain/Install.luau` adds two water surfaces, four Beam streams and one invisible radius14×height5 cylindrical collision proxy. No per-frame script or physics droplets. The separate review project now assembles this in a small ground-level plaza with a spawn point; it remains outside the main project.
- SceneAnalysisService in an isolated client camera view measured **4,376 opaque triangles, three opaque draw calls**. With the same candidate hidden, the view reported zero opaque geometry. This is measured rendered geometry for that view/LOD, not an exhaustive mesh-topology or device-performance claim. The full plaza view before water assembly reported31,710opaque triangles/40draw calls.
- ContentProvider.PreloadAsync returned Success for all six mesh/texture IDs in this Studio session. This does not prove permissions in the published destination experience.
- Existing six StudioArrivalRoutes all passed with the assembled trial present:24/20/20/22/29/36waypoints. An exploratory radius42 route probe initially returned NoPath because its endpoints landed on the eight existing bench seats; raycasts identified the seats, and the established walkable arrival-route fixture was then used. No pathfinding source change was made.
- Both review sources compile; binary/XML review builds succeed. Exact rebuilt-file native import remains unverified because the native file-opening UI is unavailable. The successful render used the saved Roblox model reload plus the actual repository installer source.

Main map source/default project remain unchanged. Accepting the asset into the main map still requires the native build-loading check, fallback behavior and destination permissions. The local review template remains in the disposable editor's ServerStorage; no trial scene remains after stopping Play.

## Native rebuilt-file verification completed

After Studio file controls recovered, opened `build/FountainReview.rbxl` through the native file picker. Although the final UI observation timed out, the connector confirmed a new FountainReview instance1a662539-4904-4648-bc18-60e9021c75b5. Started that exact build: installer assembled the three mesh parts, water and streams; measured bounds28.2263×20×28.2494. ContentProvider reported Success on all six IDs. Native screenshot confirms textured octagonal mosaic basin, pedestal, bowl and water streams rendering from the repository-built file. Console had only the assistant camera-reset notice. Stopped Play after verification.

This supersedes the earlier **native rebuilt-file import** blocker. Main map adoption, fallback behavior and actual destination publication permissions remain open; Studio content success does not prove cloud client permissions.

## Adopted in development city with fallback

The main project now embeds the reviewed template in ServerStorage and uses `src/ServerScriptService/Fountain.luau` for Plaça del Sol only. Other squares retain their existing fountain designs. The review project shares this module; the old duplicate prototype installer was removed.

Shared water/streams and three simple collision proxies are authoritative. Detailed meshes and28 built-in fallback parts have no collisions/queries/touches. The atomic landmark model carries OptionalLandmarkVisual; the client preloads all mesh/texture dependencies and shows the detail only after every callback reports Success. Otherwise, it keeps the tiled stone fallback. An instance-specific ticket prevents an outdated asynchronous load from changing a re-entered model.

Native integration: three detailed meshes visible, all28 fallback parts hidden, three solid proxies. Six arrival routes passed(24/20/21/22/29/36waypoints). A local clone with texture0 selected the visible fallback, confirmed by screenshot. A subsequent tag-removal/re-add failure exposed a bug where previously hidden fallback stayed hidden; fixed by resetting fallback visibility before every load. `StudioLandmarkFallback.client.luau` then passed seven checks for detailed success, missing-texture fallback after re-entry, valid-texture recovery and unchanged collision count. This is local tag lifecycle testing, not an actual network stream-out/in test.

All28 production sources compile, and city/review binary and XML builds succeed. Native integrated screenshot confirms the mosaic fountain in the plaza. Temporary failure clones/fixture/camera/UI changes were removed by stopping Play and restoring clean source. Published destination asset permissions and real-device performance remain release gates; no public game publication occurred.
