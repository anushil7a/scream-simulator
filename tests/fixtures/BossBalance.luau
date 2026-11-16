local Catalog=require('../src/ReplicatedStorage/Shared/BossCatalog')
local Combat=require('../src/ReplicatedStorage/Shared/VoiceCombat')
local Attack=require('../src/ReplicatedStorage/Shared/SustainedAttack')
local duty=Attack.MaxDuration/(Attack.MaxDuration+Attack.Cooldown)
local previous
for _,b in ipairs(Catalog.Entries) do
 if previous then
  assert(b.level>previous.level and b.health>previous.health,'ordered progression')
  assert(b.coins>previous.coins and b.xp>previous.xp,'smooth increasing reward pots')
 end
 previous=b
 local stats=Combat.Stats(b.level,1,false,false)
 local full=b.health/(stats.maxDps*duty)
 local quiet=b.health/(stats.maxDps*(.45+.55*.35)*duty)
 assert(full>=30 and full<=65,'full-power fight outside 30–65s target')
 assert(quiet/full<1.6,'lower amplitude unreasonable wall')
 assert(b.damage/stats.health<.16,'one hit too punishing')
 assert(b.windup>=1.5 and b.interval-b.windup>=2,'insufficient warning/recovery')
 assert(b.radius==22 and b.engageHeight==12,"explicit engagement limits")
 print(string.format('%s: %.1fs full / %.1fs 35%% amplitude, %.1f%% HP per strike (ideal sustained duty cycle; not playtest)',b.id,full,quiet,100*b.damage/stats.health))
end
