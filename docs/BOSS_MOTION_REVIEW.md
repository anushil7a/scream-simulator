# Boss presentation motion

Source context: prior implementation applied the vault's Boss Animation and Phases/Enemy Animation State Protocol. This pass reviewed the local expanded Master Vault's Blender/Rigging and MAP-10 notes, the November 17 Vault Research and Upgrade Plan, and the actual authored boss geometry. No asset IDs, newly imported assets, humanoid rig claims or damage authority in the client.

## Contract

The server owns the Core pose and committed attack timelines. Ground remains Core.Position minus Catalog aimHeight; only Moving interpolates between authoritative roots; Windup/Recovery keep server facing. One nearby appearance persists across movement and construction. Stream-out releases appearance and batches; stream-in samples the server clock instead of restarting the tell. Matching impact serial and phase time admit the release. Canceled tells relax to rest, with no fake attack release.

Five gaits use distinct cadence/lift/sway and grounded foot travel; Captain's peg swings lower. Ten authored assembly profiles have different held anticipation and releases: Metronome's pendulum sweep and kick; Golem's fault-line brace and two-arm slam; Ignis's microphone/organ cast and backdraft stomp; Captain's paired siren recoil and cutlass; Conductor's six independent ringing bells and sweeping glove. Whole weapon and bell assemblies stay together even when the mesh crosses a centerline. These are procedural clips over exact Blender-derived surfaces, not rigged locomotion or IK. Feet are never translated down through the floor.

No new instances. One bounded native BulkMoveTo per visual frame (up to the existing 450-part cap, one boss at a time; 30 Hz maximum; no physical device benchmark). The existing saved and OS reduced-motion preferences suppress cosmetic pose; server movement, hazards and combat are unchanged by the preference. Existing impact accents/audio consume the same committed marker and serial contract.

## Evidence and limits

`tests/boss_pose.py` executes actual appearance, pose and controller with numeric CFrame/vector and Instance/BulkMoveTo doubles. Checks all five part budgets at 2× previous visual scale, positive foot clearance, no instance allocation while animating, streamed and reduced modes, all ten held tell/hit/recovery transitions, serial-matched impact, canceled early/late tells, comfort setting selection, and stale/pairing negative controls. `tests/boss_attack_effects.py` verifies the existing independent themed accent contract.

No Studio opened, no upload/publish, no native visual/device acceptance claimed. Check anatomy seams at peak poses from front and back, tell readability while fighting, synchronization at varying latency, reduced mode, sightlines and low-end frame cost on the combined fixture before release.
