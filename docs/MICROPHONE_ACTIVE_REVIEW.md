# Inactive microphone input availability

## Reproduction and scope

The actual Microphone/MicPower/SustainedControls modules with fake audio instances reproduce a calibrated input transitioning to `Active=false`, `Muted=false`, RMS zero while still reporting ready/live input, retaining a legacy capture and leaving automatic controls armed. This is a synthetic property transition, not proof of a hardware-disconnection incident. Historical baseline `15df683` also permits calibration while inactive.

Official Roblox creator-docs source distinguishes the properties:
https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine/classes/AudioDeviceInput.yaml

`Active` has read security None, write security RobloxScriptSecurity; its description permits user-script reads. `IsReady` has RobloxScriptSecurity for reads and writes and is not accessed. Creator Hub summary security labels do not distinguish these cases clearly.

## Narrow correction

Read `Active` in calibration entry, direct legacy Begin/Release, and each microphone step. Direct entries also revalidate input wiring and mute state, so they do not depend on the next heartbeat. An explicit false cancels capture and incomplete calibration, resets sampled/smoothed energy, zeros power and clears readiness with inactive-input guidance. Preserve successfully validated calibration, like existing mute handling. Reactivation restores calibrated availability, but the existing controls disarm on an observed readiness loss and require deliberate rearming, quiet and then fresh voice. Input replacement continues to require new calibration.

No assignment to Active/Muted, audio routing, voice communication, eligibility policy or server combat changes. Inactive is not asserted to mean unplugged hardware. The module observes state on its existing heartbeat; a transition not observed by the controller is not claimed covered.

## Focused evidence

- `python tests/microphone_active.py --baseline`: expected historical failure, inactive calibration permitted.
- `python tests/microphone_active.py --negative-controls`: 33 actual-module/controller assertions and seven explicit controls. Covers initial inactive input, quiet/voice calibration interruption, capture/armed loss, repeated inactivity, active recovery/manual quiet gate, mute and replacement. Voice-phase setup is synthetic; this does not measure real calibration timing or speech.
- `python tests/microphone_lifecycle.py`: 111 existing assertions pass with fake inputs explicitly Active=true.
- `luau-compile src/StarterPlayer/StarterPlayerScripts/Microphone.luau`: passes.

No native/device/transport validation, app launch, live API, recording, publishing, map or persistence changes. Real-device behavior and ordinary voice preservation remain native release gates. Parent coordinates aggregate tests, independent review and evidence/checkpointing.

## Integration checkpoint

Independently reviewed and rerun focused checks above; full `python tests/verify_local.py --build` passes 25 pure/synthetic suites, 94 mocked-service suites, 60 production compiles and all disposable builds. This is offline execution, not native Roblox. [Exact commands and working-tree/artifact hashes](../tests/evidence/client-availability-2026-11-11.json). No apps or live services were used.
