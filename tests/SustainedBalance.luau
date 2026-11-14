local Healing=require("../src/ReplicatedStorage/Shared/Healing")
-- Deterministic combat scenarios: actual protocol/stats/destruction rules with
-- perfect aim and synthetic pulses. No geometry, human voice or network claims.
local Attack=require("../src/ReplicatedStorage/Shared/SustainedAttack")
local Combat=require("../src/ReplicatedStorage/Shared/VoiceCombat")
local Rules=require("../src/ReplicatedStorage/Shared/DestructionRules")
local checks=0
local function check(v,message) assert(v,message);checks+=1 end
local function scenario(level,power,health,kind,healing)
 local s=Attack.New()
 local now,casts,total,nextHeal=0,0,0,math.huge
 local initial=health
 for _=1,6000 do
  now+=.05
  if not s.active and now>=s.nextStart+.3 then
   casts+=1
   assert(Attack.Begin(s,now,casts,Combat.Stats(level,1,false).maxDps,power,true))
  end
  if s.active and now-s.active.lastPulse>=.125 then Attack.Pulse(s,now,s.active.sequence,power,true) end
  local hits=Attack.Step(s,now,true,{"target"})
  for _,hit in ipairs(hits) do
   local before=health
   if kind then health=Rules.Hit(kind,level,health,hit.damage) else health=math.max(0,health-hit.damage) end
   total+=before-health
   if health<before then nextHeal=now+Healing.QuietSeconds end
  end
  if health<=0 then return {casts=casts,time=now,damage=total} end
  -- Execute the same regeneration rule as the authoritative server.
  if healing then health,nextHeal=Healing.Step(health,initial,nextHeal,now) end
 end
 return {casts=casts,time=math.huge,damage=total}
end
local matchups={}
for _,attacker in ipairs({1,25,50,75,100}) do
 for _,defender in ipairs({1,25,50,75,100}) do
  local outcome=scenario(attacker,1,Combat.Stats(defender,1,false).health,nil,true)
  matchups[attacker..":"..defender]=outcome
  check(outcome.time<150,"Full-power matchup failed to finish")
  if attacker==defender then check(outcome.casts==2,"Equal-level fight should take two full-power attacks") end
  print(string.format("MATCHUP,%d,%d,%d,%.2f",attacker,defender,outcome.casts,outcome.time))
 end
end
check(matchups["100:1"].casts==1 and matchups["100:1"].time<2,"Level 100 should overwhelm level 1")
check(matchups["100:50"].casts==1 and matchups["100:50"].time<4,"Level 100 should defeat level 50 within one beam")
check(matchups["1:100"].casts==8,"Level 1 should need eight full attacks against level 100")
local weak=scenario(1,.35,Combat.Stats(100,1,false).health,nil,true)
check(weak.time<300,"Low-level onset-strength attack cannot overcome regeneration")
for kind,spec in pairs(Rules.Types) do
 local atUnlock=scenario(spec.level,1,spec.health,kind,false)
 local atCap=scenario(100,1,spec.health,kind,false)
 check(atUnlock.time<spec.repair,"Object repairs before a solo player can destroy it")
 check(atCap.casts<=atUnlock.casts,"Higher levels made destruction slower")
 local blocked=scenario(spec.level-1,1,spec.health,kind,false)
 if spec.level>1 then check(blocked.damage==0,"Locked destruction tier took damage") end
 print(string.format("%s: %d attacks at unlock, %d at cap (perfect aim/full calibrated power)",kind,atUnlock.casts,atCap.casts))
end
print(string.format("Level 1 vs 100 at onset-strength power: %d attacks, %.1fs with quiet healing",weak.casts,weak.time))
print("PASS "..checks.." synthetic sustained balance checks; timings are not playtest results")
