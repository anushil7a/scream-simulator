# Lv70 Seagull Siren Captain art

Stable encounter/save key remains `leviathan`; gameplay name and patterns are integrated separately. Only this key's authored geometry changed. The four other geometry entries were compared byte-for-byte with base308de07 and are identical.

## Reference and construction

Inspected actual vault `Concepts/Boss/BOSS-02_Lv20_Seagull_Siren_Captain.jpg` directly, not a search thumbnail. The concept's Lv20 filename is reference provenance, not the game's intended unlock level. Also read the actual vault `45 Procedural Blender Assets/Matching a Concept Sheet - Boss Creature Case Study.md`: silhouette and continuous main mass before small repeated detail; separate visual geometry from collision.

Original Blender-authored low-poly interpretation: tapered navy coat, white angular gull head and hooked yellow beak, gold-edged tricorn/goggles, dual open brass megaphones with cyan drivers, chest anchor, cutlass, hook and asymmetric boot/peg leg. Geometry is authored by `tools/bosses/fidelity.py` and exported directly to upload-free BossVisualData. No borrowed mesh, texture, external asset ID or script import. Main coat/head use continuous surfaces; individual details remain intentionally simplified for native-part budget.

108 Blender objects,21 continuous surfaces, maximum343 native parts versus old435. Other bosses stay274/291/269/417. Appearance remains client-only noncollidable/nonqueryable and scale1.4 around the existing floor anchor. No server damage, progression, rewards, save fields or encounter IDs changed here.

BossPose keeps whole arm/tool groups together, positive foot lift only and a restrained paired-horn windup tilt. Existing authoritative root/state/shared timestamp, persistent model lifecycle, one-nearby cap,30Hz maximum and game/OS reduced-motion behavior remain. This is procedural assembly animation, not an uploaded skinned animation clip.

## Artifacts and verification

Run `BOSS_RENDER_ONLY=leviathan blender --background --python tools/bosses/fidelity.py` for the focused render and source. Local ignored build artifacts: `build/boss-fidelity/leviathan.png`, `leviathan_silhouette.png`, `leviathan.blend`, `manifest.json`. The editable blend retains the full original roster, but only the108 Captain meshes are visible in viewport/render on opening. `BossFidelity.blend` is the full lineup source. No desktop UI opened; background Blender processes exited.

Actual Blender color render was inspected and refined for visible horn drivers, a closed beak surface and feather silhouette. `tests/boss_pose.py`:40,156 numeric-CFrame/Instance-double assertions plus preference handoff and four negative controls, including actual authored geometry and streamed lifecycle. Explicit Captain signatures, budget, paired horns and reduced windup tested. Full `verify_local.py --build`:26 pure/synthetic and153 mocked-service suites plus compilation/build passed. Neither Blender nor mocked tests establish native Roblox appearance, skin deformation or phone performance. Native animated anatomy/telegraph acceptance remains an integration gate; no upload/publish performed.
