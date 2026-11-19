# City Preview tester tools

The owner asked to keep testers' tools until explicitly told otherwise. This change does not publish a Roblox place, change who can join it, or make it public.

## Scope

- Keep the existing **Test Tools** launcher and ordinary commands. In the known City Preview tester place (90337242377543, universe 10769005350), the existing prelaunch tester switch also enables **Fly** and the adjustable **Test Beam** click preview. Existing isolated local Studio testing remains available.
- The extra tools are unavailable in another place or universe, under a different creator, or when the online tester flag is off. The client only draws them when the server advertises the mode and passively reconciles per-player access; this is not a grant of server permission.
- Click **Test Beam** to preview an aimed beam, then adjust 0–100% power as before. This is silent and deals no damage, gives no rewards, and is not a bypass for the real microphone attack. Fly is server-bounded and returns to its start when stopped. Standard input, saves and rewards outside the test-tool path retain their existing behavior.
- Roblox access remains an external requirement. Keep City Preview limited to testers, and disable the prelaunch tools before any future public release. The flag and allowlist do not make an experience private.

## Acceptance

Use actual guard tests for exact identity, wrong place, wrong game, revoked flag, local fixture, and denial before gameplay effects. Recheck guarded local fixture regression, compiled regular place contents, and isolated save/reward behavior. A mocked published-context gate is not an online Roblox playtest. Do not publish for verification without separate authorization.

Fly uses the existing temporary tester profile: legitimate progress is frozen while using the test profile, which lasts until rejoining. Silent Test Beam alone does not switch profiles. The online gate has no effect on other local-only QA tools, including global trainer reset. The public-release check still blocks with the current tester flag enabled; its reviewed exact flag-off hash was refreshed without loosening the check.

## Verified in this change

- Mocked exact source: 109 developer access/temporary profile, 237 silent preview and action routing, 52 flight/revocation/movement, 57 reward isolation, 40 save/access isolation, and 15 release gate assertions. These are synthetic engine checks, not Roblox online tests.
- The regular Roblox place source audit matched all 98 production scripts. The separate standalone Academy playtest still builds using local-only flight. No Roblox publication or visibility change was performed.
