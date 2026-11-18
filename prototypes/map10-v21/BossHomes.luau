-- Standalone v2.1 placement adapter. Ground heights; no production layout changes.
-- Captain preserves the existing encounter ID 'leviathan' for reward/save continuity.
local homes={
 metronome={x=-520,y=50,z=730,district="01",radius=22,patrolRadius=4},
 golem={x=120,y=115,z=760,district="06",radius=22,patrolRadius=4},
 ignis={x=980,y=175,z=60,district="07",radius=22,patrolRadius=4},
 leviathan={x=420,y=48,z=-680,district="05",radius=22,patrolRadius=4},
 conductor={x=920,y=340,z=920,district="08",radius=22,patrolRadius=4},
}

-- The Academy build compresses the scenery but keeps full-size characters and attack radii.
-- Place the same encounters on open district floors with space to dodge on every side.
local academy=script and script.Parent:FindFirstChild("AcademyWorldScale")
if academy then
 local compact={
  metronome={-214,20,248}, golem={48,46,304}, ignis={346,70,26},
  leviathan={168,19.2,-272}, conductor={346,136,354},
 }
 for id,point in pairs(compact) do
  local home=homes[id]
  home.x,home.y,home.z=table.unpack(point)
 end
end
return {BossHomes=homes}
