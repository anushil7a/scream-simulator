# City Preview tester tools

The owner asked to keep testers' tools until explicitly told otherwise. This change does not publish a Roblox place, change who can join it, or make it public.

## Scope

- Keep the existing **Test Tools** launcher and ordinary commands. In the known City Preview tester place (90337242377543, universe 10769005350), the existing prelaunch tester switch also enables **Fly** and the adjustable **Test Beam** click attack. Existing isolated local Studio testing remains available.
- The extra tools are unavailable in another place or universe, under a different creator, or when the online tester flag is off. The client only draws them when the server advertises the mode and passively reconciles per-player access; this is not a grant of server permission.
- Click **Test Beam** to fire a silent aimed beam, then adjust 0–100% power as before. It takes real HP from other opted-in testers inside PvP using the existing damage and cover rules. It does not hit ordinary players, bosses or NPCs, and it does not give rewards. Fly is server-bounded and returns to its start when stopped. Standard input, saves and rewards outside the test-tool path retain their existing behavior.
- Roblox access remains an external requirement. Keep City Preview limited to testers, and disable the prelaunch tools before any future public release. The flag and allowlist do not make an experience private.

## Acceptance

Use actual guard tests for exact identity, wrong place, wrong game, revoked flag, local fixture, and denial before gameplay effects. Recheck guarded local fixture regression, compiled regular place contents, and isolated save/reward behavior. A mocked published-context gate is not an online Roblox playtest. Do not publish for verification without separate authorization.

Fly uses the existing temporary tester profile: legitimate progress is frozen while using the test profile, which lasts until rejoining. A successful Test Beam start now enters that same temporary, test-only profile. Both players must enter a test session (each can click Test Beam once or use an existing test command). The online gate has no effect on other local-only QA tools, including global trainer reset. The public-release check still blocks with the current tester flag enabled; its reviewed exact flag-off hash was refreshed without loosening the check.

## Prior feature verification

- Mocked exact source: 109 developer access/temporary profile, 237 silent preview and action routing, 52 flight/revocation/movement, 57 reward isolation, 40 save/access isolation, and 15 release gate assertions. These are synthetic engine checks, not Roblox online tests.
- The regular Roblox place source audit matched all 98 production scripts. The separate standalone Academy playtest still builds using local-only flight. No Roblox publication or visibility change was performed.

## Damaging click test, November 19

Before the actual player launch, remove tester shortcuts and verify the public build. Do not treat tester-phase adjustments as final progression tuning.

Compile and test the exact local Test Beam damage review artifact as two Studio clients. A fresh mixed-mode target must take no damage; after both opt in and cooldown permits, the target must lose real HP from the click. Confirm the no-reward contract with the dedicated server resolver tests. Online City Preview was not published or exercised.
