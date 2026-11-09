-- Candidate economy; pacing assumptions live in tests/ProgressionPacing.luau.
local Progression={MaxLevel=100}
function Progression.Level(level)
 if type(level)~="number" or level~=level or math.abs(level)==math.huge then return 1 end
 return math.clamp(math.floor(level),1,Progression.MaxLevel)
end
function Progression.XPToNext(level)
 local l=Progression.Level(level)
 return math.floor(65+6*l+.6*l*l+.009*l*l*l)
end
function Progression.PlayerKOXP(level)
 return math.floor(90+6*Progression.Level(level))
end
function Progression.RewardFactor(attackerLevel,targetLevel)
 local gap=Progression.Level(attackerLevel)-Progression.Level(targetLevel)
 if gap<=-10 then return 1.25 end
 if gap<=10 then return 1 end
 if gap<=20 then return .5 end
 if gap<=30 then return .2 end
 return .05
end
Progression.Challenges={
 {id="fighters",name="Defeat 3 training fighters",goal=3},
 {id="cover",name="Destroy 5 eligible cover objects",goal=5},
 {id="elite",name="Help defeat 2 elite fighters",goal=2},
}
function Progression.ChallengeXP(level)
 return math.min(200,30+2*Progression.Level(level))
end
function Progression.Advance(challenges,id,level)
 for _,spec in ipairs(Progression.Challenges) do
  if spec.id==id then
   local count=math.clamp(math.floor(challenges[id] or 0),0,spec.goal-1)+1
   challenges[id]=count==spec.goal and 0 or count
   return count==spec.goal and Progression.ChallengeXP(level) or 0,spec.name
  end
 end
 return 0
end
function Progression.Normalize(level,xp)
 local l=Progression.Level(level)
 local value=type(xp)=="number" and xp==xp and math.abs(xp)<math.huge and math.clamp(math.floor(xp),0,1e9) or 0
 while l<Progression.MaxLevel and value>=Progression.XPToNext(l) do value-=Progression.XPToNext(l);l+=1 end
 return l,l==Progression.MaxLevel and 0 or value
end
return Progression
