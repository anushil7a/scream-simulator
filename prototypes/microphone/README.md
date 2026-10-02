# Real microphone feasibility lab

This is a small standalone place that reuses the production `Microphone`, `MicPower` and `VoiceCombat` modules. It is for two-account real-audio testing before release. It has no DataStore, rewards, passes, purchases, custom audio upload, speech transcription or recording. The city is intentionally absent so voice issues can be isolated.

## Build and publish privately

From the repository root:

```sh
rojo build mic-prototype.project.json -o build/MicrophoneFeasibility.rbxl
```

Open that file in Studio. Choose **File → Publish to Roblox As → Create new experience** and name it **Scream Simulator Mic Lab**. Verify the new experience remains private and record its place/universe IDs. Do not overwrite Scream Simulator or add this lab as a place in its production universe. Configure voice access for the new test experience through Roblox's supported settings, and give only the intended testers play access. No lab cloud place has been created or verified by this task yet.

The project sets `VoiceChatService.UseAudioApi = Enabled` and `EnableDefaultVoice = true`; experience/account eligibility and permissions still need verification. Roblox supplies default proximity voice for eligible players. See [official voice documentation](https://create.roblox.com/docs/chat/voice-chat) and [AudioDeviceInput](https://create.roblox.com/docs/reference/engine/classes/AudioDeviceInput). Rechecked October 2, 2026. The lab does not use restricted Active/IsReady properties.

## Two-person test

1. Use two eligible accounts on separate real devices/microphones, preferably headphones. Record device/model, OS, Roblox client version, place version and date manually.
2. Retry access, unmute through Roblox, then calibrate: two quiet seconds followed by two seconds of a comfortable strong voice. Confirm input status and power respond. Power is normalized, not measured decibels.
3. Hold E or the capture button **before** speaking. Speak immediately during the displayed1.25-second window, then release. Valid capture shows Accepted and a short cyan test pulse aimed at the mouse. This lab pulse has no damage or rewards. The live meter also moves outside an attack, which does not mean that voice is armed for a shot. Repeated releases within four seconds must not be accepted. Silent/too-short capture must not submit a valid attack.
4. The displayed milliseconds measure release-to-server-acknowledgement only. Measure perceived voice delay separately; this readout is not voice latency.
5. Have the listener stand at the marked distances. Confirm live voice is audible nearby and attenuates with distance. Check Roblox mute/block/volume controls; do not assume that a server acceptance proves audio was heard.
6. Mute during capture, deny permission, disconnect/reconnect a microphone, retry, lose window focus, and respawn. Confirm capture is canceled and setup remains recoverable. Record actual behavior and failures; hardware support is not proven by a zero meter alone.
7. Repeat with different gains and comfortable voice levels. Check background sound does not trivially keep power at maximum; client-reported power cannot be certified as genuine human speech.
8. Repeat capture on phone touch, including releasing outside the capture button. The panel scrolls on short screens.

Keep human observations in a dated note. Do not record other players' speech. A successful lab pass is a prerequisite, not a substitute for the full game's multiplayer, movement, persistence, and device-performance gates.

## October2 user test and fix

The owner opened/published `scream test` (place88993310833821), saw microphone-ready and reported the meter reaching100%, but received no valid voice on release. This confirms owner-observed local input, not successful attacks or another listener hearing audio. Capture timing was not observed, so the specific rejection cause is unproven.

Added a visible sampling countdown, explicit hold-first instructions, release failure reasons, automatic capture expiry, and an accepted-attack pulse. Resetting the smoothing filter at each new capture prevents speech before the button press leaking into a silent attack. Numbers measuring loudness are consumed once; no audio is recorded, saved or replayed by the game. External audio played into a mic cannot be reliably identified as a recording by this energy meter.

A native restart exposed a module-arrival race; the lab now waits for Microphone before requiring it. Native scripted request checking (not human audio) produced one accepted75% pulse, length25.5, non-colliding, with an empty console. Temporary fixture removed before leaving the lab ready to retry. Local source is updated; no cloud republish is claimed. A second eligible account is still needed to verify actual proximity audibility.

## Current verification and blocker

Both lab scripts compile; Rojo builds binary/XML places containing exactly five scripts/modules and no Profiles code. Native startup was checked by temporarily replacing the two entry scripts in the existing disposable Studio copy and disabling its unrelated automatic scripts. The lab panel and remote loaded, no city was generated, console output was empty, and the real controller correctly waited for missing Roblox mic input. The full game scripts/enabled states were restored and Play stopped afterward. This is not a clean-file opening or real-audio pass. Real-audio testing has **not** passed. Studio's publish dialog displayed the existing public game and Create new experience, but native coordinate actions failed with `noWindowsAvailable`; it was closed without publishing. Opening the local lab through the file dialog later timed out; a second inspection and fresh app binding also timed out. The Studio connector continued to list only the three prior instances, with no new lab instance. The file-open outcome is unverified; do not repeat publication assuming an earlier action succeeded. Do not infer publication from either attempt.
