# MAP-10 v2.1 Academy first-playable route

Opt-in disposable Studio artifact; not the production integration of all MAP-10 quests.
The existing map-only and boss-placement targets are unchanged. Only this variant adds
a local prototype course. It requires Studio and an unpublished place (GameId and PlaceId both zero).

## Play it

1. Open `Map10V21AcademyRouteReview.rbxl` locally in Roblox Studio and click **Play**.
   At Academy spawn, put the center crosshair on the glowing cyan training resonator.
   Hold left mouse, R2, or the touch **Hold Beam** button until the training step completes.
   This is held-input testing, not microphone capture. Each hold is capped at four seconds,
   followed by a five-second cooldown and a fresh press.
2. Walk to Marina and use her Academy encounter prompt. The course temporarily sets level 10
   so the first optional boss can be tested without grinding in this fixture.
3. Use **Guide: Metronome** if desired, then walk to the yellow/pale Academy boss route.
   Guidance is opt-in and can be cleared; it does not move the avatar. Get inside the
   22-stud ring, aim at the boss body, and move off the colored ground before attacks land.
4. Once credited with the Metronome defeat, the preview grants 35 boss coins plus 65
   temporary course coins. Guide back to gear if desired. Use Tinker's 100-coin prompt to
   buy and equip the original handheld Academy Megaphone. Respawn preserves the session
   result. A fresh Studio server resets it. Neither coins nor gear touch live saves or Robux.

The original boss assets, five placements, service, attack warnings, and gear catalog are
reused. Only Metronome accepts hits; other bosses remain patrol-only here. The little mentor
and gear stations are native-part proof-of-flow props, not final NPC migration or imports.
Held proxy power is saturated; visual equip is testable but microphone gain is not.
No other MAP-10 quest, production music/VFX rewrite, analytics, paid product, or publication
is included. Native audiovisual, mobile, and multiplayer tests have separate acceptance gates.

## Reproduce the local build

From the repository root, with Python, Rojo and Luau CLI on PATH:

```sh
python3 prototypes/map10-v21/build_overworld.py --academy
python3 prototypes/map10-v21/check_academy_route.py
luau prototypes/map10-v21/check_academy_rules.luau
python3 tests/boss_service.py
python3 tests/navigation_guide.py
python3 tests/gear_equipment.py
```

Exact file/source fingerprints are exported to
`build/map21/academy-route-provenance.json`. The placement-only variant can be independently
rebuilt with `--bosses`.

Validation layers: the offline geometry check samples feet/headroom and three player-width
lanes connecting the course stations. It is not collision or pathfinding proof with live
Humanoids. The Luau check exercises actual route state, hold/release/cooldown, reward-once,
shared beam stats and shared gear purchase in isolation. Existing service suites use mocks;
a successful build is not a native Studio run.

## First integrated checkpoint evidence

- Academy artifact rebuilt byte-for-byte, SHA-256
  `ed3c3fed20efce8cbc5df6527cbdd9f83f309778a8f037ce0a07edd2f294a965`.
  Loaded-source stamp to verify in Studio:
  `ea10522b9a5b11c819c20c1274c7d121934face31d46e219d1394ba2f51a9645`.
- 135 Academy analytic probes, 75,674 preexisting-world analytic route probes, 109 actual
  Luau state/gear/hold assertions, 8,129 mocked BossService assertions plus callback checks,
  38 mocked guide lifecycle checks and mocked equipment tests passed.
- The earlier map-only and boss-placement artifacts rebuilt byte-identically.
- Native playthrough not run: the approved file transfer did not place the artifact on
  the Windows Studio machine. The attached ZIP can be downloaded and extracted there to
  unblock native validation. Do not infer that the new fight and purchase were played.
