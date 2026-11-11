# Quiet beam mix comparison baseline

Exact Git blob bytes copied from repository commit `47f3d46`, before the NORMAL/LOW/OFF change. These test-only originals are not production dependencies. The regression verifies their SHA-256 hashes before execution, allowing normal tests to work in shallow/exported checkouts. Only the optional `--baseline` reproducer uses Git history.

- `AttackAudioConfig.luau`: `5dbba1850546d8732c3d998be33f2013718c53c3c8a023a5aeb017ba711bf2fc`
- `BeamAudioMix.luau`: `f6a05600323921af36578107915ec4dd08b6178a99e664533bf3e306b2a1153d`

Source paths: `src/ReplicatedStorage/Shared/AttackAudioConfig.luau` and `src/StarterPlayer/StarterPlayerScripts/BeamAudioMix.luau`.
