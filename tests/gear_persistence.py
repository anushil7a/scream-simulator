"""Actual Profiles/gear rules and test-session autosave, fake stores only."""
from pathlib import Path
import subprocess,tempfile
import profile_migration as fixture
import test_session_rewards as isolation
root=Path(__file__).resolve().parents[1]
checks=r'''
end
local P=loadProfiles();local G=config.Gear
local original=P.Sanitize({schemaVersion=4,level=100,coins=2500,amplifierOwned=true,amplifierEquipped=true,megaphoneOwned=true})
assert(G.Act(original,'CelestialOrgan',false))
assert(original.coins==700 and original.megaphoneOwned and original.amplifierOwned)
for _=1,5 do original=P.Sanitize(original);assert(G.Owned(original,'CelestialOrgan') and G.Selected(original).id=='CelestialOrgan' and original.coins==700) end
local snap=P.Sanitize(original)
assert(G.Act(original,'MosaicMic',false) and original.coins==400)
assert(not G.Owned(snap,'MosaicMic') and snap.coins==700,'Snapshot aliased live ownership')
local damaged=P.Sanitize({schemaVersion=4,level=1,coins=9,gearOwned={CelestialOrgan=true,Unknown=true},gearEquipped='CelestialOrgan'})
assert(damaged.gearOwned.CelestialOrgan and not damaged.gearOwned.Unknown and G.Selected(damaged)==nil)
print('PASS actual Profiles repeated gear migration and rollback snapshots')
'''
code=fixture.preamble+fixture.config+fixture.between+fixture.profiles+checks
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(code)
try:subprocess.run(['luau',str(path)],check=True,cwd=root)
finally:path.unlink()
code=isolation.build()
needle="local baseline=victim.testBaseline;dev(owner,'AddLevels');"
assert needle in code
code=code.replace(needle,"""victim.data.coins=10000
assert(Config.Gear.Act(victim.data,'CelestialOrgan',false))
assert(Config.Gear.Owned(victim.data,'CelestialOrgan'))
assert(not Config.Gear.Owned(victim.testBaseline,'CelestialOrgan') and victim.testBaseline.coins==0)
"""+needle)
needle="check(equal(ownerRejoin,victim.testBaseline)"
assert needle in code
code=code.replace(needle,"assert(not Config.Gear.Owned(ownerRejoin,'CelestialOrgan') and ownerRejoin.coins==0,'Sandbox gear purchase escaped baseline')\n"+needle)
r=isolation.run(code);print(r.stdout+r.stderr,end='');assert r.returncode==0
print('PASS gear purchase remains isolated across actual test-mode autosave/rejoin helpers')
