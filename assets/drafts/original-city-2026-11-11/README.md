# Original city source preservation

This folder preserves the repository-generated city, not a published Roblox place, live player data, or unsaved Studio edits. The completed snapshot is `72c886cb6f8a60ab26dff962e28da77e4b2d4609/`: 59 exact runtime files, 57 compiled sources, normal/guarded source audits and independent byte verification passed. Its ZIP SHA-256 is `a67c1e1af4f1cf4387a1bd0cb61a8ce84986290f10913e164fc8719c8877b19a`. Guarded artifacts were built, not run in Studio. A forced Windows-autocrlf checkout retained exact artifact bytes.

After the owner-coordinated reviewed commit is final, run:

    python tools/preserve_city_draft.py --commit FULL_40_CHARACTER_COMMIT

The tool reads only tracked blobs from that exact commit: `src/**/*.luau`, `default.project.json`, and the referenced `assets/review/MosaicFountain.rbxmx`. It excludes `.git`, untracked files, credentials, previous place builds and unrelated audio/research. New source types or project references require review. Existing commit snapshot directories are never overwritten. A failed run retains an `incomplete` manifest; do not treat it as a verified snapshot or delete it automatically. After fixing a verification-only failure, `--verify-existing --commit FULL_COMMIT` verifies the existing incomplete manifest and ZIP against the exact commit, refuses existing draft artifacts, and resumes only compilation/build verification without replacing the source archive. Verification uses a short, bounded `.scream-preserve-temp` directory under the user workspace to avoid Windows path limits; only its generated child temporary directory is removed.

## Verification and artifacts

Each full-commit subfolder contains a deterministic, uncompressed `original-city-source.zip`, per-file byte lengths/SHA-256 hashes and ZIP hash in `manifest.json`, and separately derived `OriginalCity-LOCAL-ONLY.rbxl` / `.rbxlx` files. Before marking complete, the tool extracts into a bounded workspace temporary directory, verifies every hash, compiles preserved Luau and audits the serialized normal build's exact script-source multiset. The ordinary unguarded audit place is temporary and is not retained. The guarded build is audited with only the documented Bootstrap prefix difference.

Only open the LOCAL-ONLY artifact as a local file in Studio. Never publish it. Its Bootstrap asserts Studio and `PlaceId == 0`, enables `LocalSustainedPrototype`, and disables profile Load/Save defensively. The original production archive is unchanged. These guards are not a substitute for inspecting future source changes or disabling API access. Builds/compiles do not prove native execution, real audio, microphone behavior, or live persistence.

## Restore source without overwriting current work

1. Choose a snapshot whose manifest status is complete. Check `zipSha256` and each file's `sha256`/`bytes` before use.
2. Restore into a **new empty directory**, not the working checkout. Use the preservation tool's `extract_checked` helper with the manifest `files` mapping (or an equivalent safe extractor that rejects traversal/duplicate paths and verifies every hash).
3. The extracted `default.project.json`, `src/`, and referenced fountain asset rebuild the original repository-generated city with official Rojo. Building is offline; an ordinary source restore does **not** include the LOCAL-ONLY guard. Do not play/publish that normal build or connect it to live saves without separate approval.
4. For inspecting the preserved draft, use the already guarded LOCAL-ONLY artifact. To restore the game repository, compare/review files first and commit approved changes on the existing development branch. Do not force-push, reset other work, or copy `.git`.

Tool requirements: Python 3, local Git history for the chosen commit, official `rojo` and `luau-compile` on PATH. No sign-in, network fetch, tagging, push or Roblox upload is performed.
