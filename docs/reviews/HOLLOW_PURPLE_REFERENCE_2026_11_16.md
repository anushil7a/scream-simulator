# Hollow Purple reference rebuild, 2026-11-16

## Reference and diagnosis

Targeted project vault sources consulted before editing:
- `vault/AGENTS.md` and selected `roblox-vfx/SKILL.md` + `LOCAL.md`.
- `vault/fwjelaa/fwjelaa vault/82 Scream Simulator Research/notes/beam-style-progression.md` (owner-selected high-level reference and Wave 6 intake).
- The supplied `hollow purple beam ig.rbxm` is held in that research folder's `assets/rovfx-static-reviewed/`. Its tracked XML conversion is `assets/vfx/HollowPurpleBeam.rbxmx`.
- Prior native image `build/beam-lookdev/wave7-level100-hollow-purple.jpg` in the desktop hud-pass worktree was visually inspected. It shows a pink solid muzzle ball and overlapping cyan/pink/red column, not solely the violet source.

The XML contains three separate example roots: Hollow Purple (5 beams, 4 emitters), Amplified (4 beams, 1 emitter), Reversal (5 beams, 2 emitters). These are separate color demonstrations positioned side by side, not components to collapse onto the same axis. Wave 7 combined all three and added three opaque balls absent from the reference.

## Change

Only the central Hollow Purple visual recipe is selected. Its five violet color sequences, texture layers, tapered width ratios, and emission are retained. No imported script or arbitrary child is cloned: only Beam and ParticleEmitter primitives, with cloned children cleared. Four emitters are capped at 12 emissions/sec each. Maximum widest layer is 80% of the authoritative width, with smaller-scale clamping for low widths. Invented muzzle/shell/travel spheres and blue/red demo overlays are no longer built. Gameplay timing, range, damage, progression and server logic are unchanged.

Reduced/far effects (including the observer OS reduced-motion argument) stop texture scrolling, disable non-core beams, disable and clear particles on entry, and restore original scroll speeds in normal view. The legacy pool now counts only successful allocations, preventing native-only tint/contact loops dereferencing holes when detail allocation refuses.

## Verification

- `tests/beam_native_budget.py`: native-only code path executed with API doubles for 25 saturated attackers, contact, reduced transition and cleanup. Reinstating the old allocation ordering reproduces a nil error. Not a native Studio run.
- `tests/beam_pool_composition.py --negative-controls`: 117,904 assertions and 7 negative controls.
- `tests/beam_silhouette.py --negative-controls`: 824 assertions and 7 controls.
- `tests/beam_contact_visuals.py --negative-controls`: 102,715 assertions and 20 controls.
- `tests/verify_local.py --build`: 25 pure/synthetic suites, 139 mocked-service suites, all production compilation and disposable builds pass.

## Open gates

Existing Roblox texture dependencies remain. Vault explicitly does not establish reuse rights or City Preview loading permissions. No newly acquired assets, texture uploads, or Roblox publication occurred. These dependencies must be cleared or replaced with approved original textures before release. Source/script-free inspection is not a licensing or security guarantee.

Native before/after visual parity, texture loading, reduced-mode transition in Studio, real-device/multiplayer performance and actual play remain unverified. The new VFX instances remain outside the legacy 512-part pool accounting; do not claim 512 bounds all rendering resources. Use the guarded disposable playtest with matching source provenance. Review the violet column at comparable side, head-on and elevated views, both normal and reduced, and keep confirmed-hit cues visible. No Studio session was opened by this task.
