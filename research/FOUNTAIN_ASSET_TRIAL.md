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
