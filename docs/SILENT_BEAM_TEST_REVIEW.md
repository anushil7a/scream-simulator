# Silent Beam and Fly Test Tools

Scope: an unpublished local Studio test only. No published place, Robux,
persistent progression, or live voice behavior is changed by the new controls.

## Full-game local review

Open `TestToolsLocalPlay.rbxl` in Studio and press Play. Open **Test Tools**.
**Fly on / off** is the existing server-owned flight control for authorized
testers; use WASD, Space up, Ctrl down, or the touch controls. Turning it off
returns the avatar to the point where flight began.

For **Beam Test**, choose 0–100% with the buttons, aim with the gold center
crosshair, then click **Test Beam**.
No mouse hold or microphone is needed. The preview stops on request, on leaving
the panel or losing focus, or after at most four seconds. Zero does not emit a
beam. This full-game fixture previews the existing geometry and visual effects
without Beam sound, damage, or rewards. Other game audio is not globally muted.
Turn Fly off before testing the Beam.

The server independently requires Studio, zero GameId and PlaceId, the local
fixture flag, developer authorization and a temporary session. Its distinct
preview packets do not enter the attack audio or damage/reward path. The normal
game's microphone controls and published project are not part of this test.

## MAP-10 Academy review

The Academy review is also disposable and has its own **Test Tools** controls.
Fly uses the existing server module against Academy map bounds, and cannot be
used to trigger progress. Choose a silent Beam power before practice or the
Metronome fight and click **Fire test** once, or hold the normal Beam input.
The Academy build uses the selected power in the temporary
course's actual server damage and range; do not infer live progression balance
or mic input from this test. The other four bosses remain patrol-only.

## Build

```sh
python3 tests/build_sustained_review.py --test-tools-local
python3 prototypes/map10-v21/build_overworld.py --academy
```

The full-game local build uses procedural fallback for two pre-existing legacy
beam template binaries (FireBeam and StarterBeam) which available Rojo versions
cannot parse. It keeps the compatible HollowPurple template, makes no asset
file or production project change and does not imply the exact native effect
appearance was visually accepted. The Academy build does not need those assets.

Native follow-up: on the delivered hashes, close/reopen Test Tools, compare
0/10/50/100%, test the mouse and touch controls, confirm no microphone permission
or Beam SFX is needed, exercise Fly wall/edge/return, and look for a stuck beam
after stop, focus loss, respawn and repeated clicks. Full mobile and Studio
validation are separate from compile/mocked checks.

## Verification on the review sources

Focused checks passed: 223 main Beam module/dispatcher assertions, 39 main mock
UI checks, 32 controller assertions, 39 shared-flight assertions and 13 mock
flight-input checks. Academy passed its rule, dispatcher, client, sequencing,
collision-fit and integration checks. Both guarded places compiled and built.
The aggregate could not finish in the shallow review checkout because the
historical BeamVisuals comparison commit is absent. Native Studio play,
audio, and physical-device controls remain to be verified.
