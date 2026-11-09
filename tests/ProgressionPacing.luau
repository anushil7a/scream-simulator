-- Deterministic solo training model, not a measured session or promise.
local P=require('../src/ReplicatedStorage/Shared/Progression')
local T=require('../src/ReplicatedStorage/Shared/TrainingRules')
local V=require('../src/ReplicatedStorage/Shared/VoiceCombat')
local A=require('../src/ReplicatedStorage/Shared/SustainedAttack')
for _,cohort in ipairs({{name='learning',accuracy=.55,power=.65,travel=15},{name='steady',accuracy=.75,power=.8,travel=8},{name='efficient',accuracy=.9,power=1,travel=4}}) do
 local level,xp,seconds,kills=1,0,0,0;local objectives={};local milestones={10,25,50,100};local nextMark=1
 while level<100 do
  local tier=T.Recommended(level)
  local damage=V.Stats(level,1,false).maxDps*(.45+.55*cohort.power)*A.MaxDuration*cohort.accuracy
  local casts=math.ceil(tier.health/damage)
  seconds+=casts*(A.MaxDuration+A.Cooldown)+cohort.travel
  local factor=P.RewardFactor(level,T.RewardLevel(tier,level))
  local reward=math.floor(tier.xp*factor)
  if factor>=.5 then
   reward+=P.Advance(objectives,'fighters',level)
   if tier.id=='elite' then reward+=P.Advance(objectives,'elite',level) end
  end
  level,xp=P.Normalize(level,xp+reward);kills+=1
  if level>=milestones[nextMark] then
   print(string.format('PACING %s level %d: %.1f minutes (%d KOs)',cohort.name,milestones[nextMark],seconds/60,kills));nextMark+=1
  end
  assert(kills<100000,'Progression stalled')
 end
end
