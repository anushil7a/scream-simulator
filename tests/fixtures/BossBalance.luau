local Catalog=require('../src/ReplicatedStorage/Shared/BossCatalog')
local Combat=require('../src/ReplicatedStorage/Shared/VoiceCombat')
local Attack=require('../src/ReplicatedStorage/Shared/SustainedAttack')
local Rules=require('../src/ReplicatedStorage/Shared/BossRules')
local POSITIVE=1e-6

local function simulate(spec,power,contactPeriod,dodgePeriod,missFirst,missLast,durationPulse)
 local stats=Combat.Stats(spec.level,power,false,false)
 local beam=Attack.New()
 local boss=Rules.New(spec)
 local identity={}
 local at=0
 local resets=0
 local function observe(now)
  if boss.health<spec.health and now-boss.lastHit>Catalog.ResetAfter then
   Rules.Reset(boss,spec,now);resets+=1
  end
 end
 local function tick(now,targets)
  observe(now)
  local hits,ended=Attack.Step(beam,now,true,targets)
  for _,hit in ipairs(hits) do Rules.Hit(boss,spec,1,identity,hit.damage,now) end
  return ended
 end
 for sequence=1,60 do
  assert(Attack.Begin(beam,at,sequence,stats.maxDps,power,true))
  local stopEarly=dodgePeriod and sequence%dodgePeriod==0
  local finish=stopEarly and 2.6 or Attack.MaxDuration
  local miss=missFirst and sequence>=missFirst and sequence<=missLast
  -- Protocol refreshes are intentionally offset from the damage ticks:
  -- last pulse is safe at the deadline, but checked separately as both
  -- expiry orders can occur in automatic voice dispatch.
  local ended
  for i=1,math.floor(finish/Attack.TickInterval+POSITIVE) do
   local now=at+i*Attack.TickInterval
   assert(Attack.Pulse(beam,now-.01,sequence,power,true))
   if durationPulse and not stopEarly and i*Attack.TickInterval>=Attack.MaxDuration-POSITIVE then
    local _,_,expiry=Attack.Pulse(beam,now,sequence,power,true)
    ended=expiry -- this order advances the deadline before damage observation
    observe(now)
   else
    ended=tick(now,(miss or (contactPeriod and i%contactPeriod==0)) and {} or {1})
   end
   if boss.health<=0 then return now,sequence,resets end
  end
  if stopEarly then ended=Attack.Cancel(beam,at+finish) end
  assert(ended and math.abs(ended.nextStart-(at+finish+Attack.Cooldown))<POSITIVE,"end-based beam cooldown")
  at=ended.nextStart
 end
 error("boss never defeated: "..spec.id)
end

assert(Attack.MaxDuration==4 and Attack.Cooldown==5 and Attack.TickInterval==.2,"keep game cadence")
assert(Catalog.ResetAfter==20 and Catalog.CreditExpiry==20,"keep reset and reward credit timeout")
local previous
local expectedRewards={
 metronome={35,100},golem={65,200},ignis={80,270},leviathan={95,340},conductor={110,420},
}
for _,b in ipairs(Catalog.Entries) do
 if previous then
  assert(b.level>previous.level and b.health>previous.health,"ordered progression")
  assert(b.damage>previous.damage and b.meleeDamage>previous.meleeDamage,"ordered retaliation")
 end
 previous=b
 local stats=Combat.Stats(b.level,1,false,false)
 local full,bursts=simulate(b,1)
 local fullPulseFirst,shortBursts=simulate(b,1,nil,nil,nil,nil,true)
 local steady=simulate(b,.8,4,3)
 local quiet=simulate(b,.35,4)
 local learn=simulate(b,.65,3,2)
 local recovery,_,oneReset=simulate(b,.8,4,3,2,2)
 local _,_,twoReset=simulate(b,.8,4,3,2,3)
 local rangedFraction,meleeFraction=b.damage/stats.health,b.meleeDamage/stats.health
 assert(bursts>=3 and bursts<=7 and shortBursts>=3 and shortBursts<=7,"ideal fight in three to seven casts")
 assert(b.id~="metronome" or math.max(full,fullPulseFirst)<45,"starter ideal less than 45s")
 assert(steady>full and learn>=steady and quiet>full and quiet<=100,"moderate quiet accuracy remains viable")
 assert(recovery>steady and oneReset==0 and twoReset==1,"one full miss recoverable; two trigger quiet reset")
 assert(rangedFraction>=.125 and rangedFraction<=.16 and meleeFraction>=.169 and meleeFraction<=.191,"bounded unlock health fractions")
 assert(b.windup>=1.5 and b.interval-b.windup>=2,"sufficient warning/recovery")
 assert(b.radius==(b.id=="conductor" and 25 or 38) and b.engageHeight==12,"explicit engagement limits")
 local reward=expectedRewards[b.id]
 assert(reward and b.coins==reward[1] and b.xp==reward[2],"fixed reward pots")
 -- Pure model, not guaranteed player outcomes. Estimate incoming strike
 -- opportunities beginning after first hit; phases vary with cadence/spacing.
 local strikes=math.max(0,1+math.floor((steady-.2-b.windup)/b.interval))
 print(string.format("%s: ideal %.1fs (%d casts), pulse-first %.1fs, steady %.1fs, learning %.1fs, .35 power/75%% aim %.1fs, one missed cast %.1fs; %d steady retaliation opportunities, %.1f%%/%.1f%% HP ranged/melee",
  b.id,full,bursts,fullPulseFirst,steady,learn,quiet,recovery,strikes,100*rangedFraction,100*meleeFraction))
end
