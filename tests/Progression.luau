local P=require("../src/ReplicatedStorage/Shared/Progression")
local checks=0
local function expect(v) checks+=1;assert(v) end
local previous=0;local previousKO=0
for l=1,300 do
 local required=P.XPToNext(l);local ko=P.PlayerKOXP(l)
 expect(required>previous);expect(ko>=previousKO);expect(ko<500)
 previous,previousKO=required,ko
 local normalized,xp=P.Normalize(l,required)
 expect(normalized==math.min(300,l+1));expect(xp==0)
end
for _,invalid in ipairs({-5,math.huge,0/0,"broken"}) do local l,xp=P.Normalize(invalid,invalid);expect(l==1 and xp==0) end
local level,xp=P.Normalize(1,P.XPToNext(1)+P.XPToNext(2)+17)
expect(level==3 and xp==17) -- migration carries XP, rather than dropping it at a new threshold
local cap,overflow=P.Normalize(299,1e9);expect(cap==300 and overflow==0)
print("PASS "..checks.." progression/migration rule checks")
-- Estimates only: continuous active play, legal 4s casts; downtime absorbed in hit rate.
-- KO probability approximates the mix of normal hits and last hits, not a measured player cohort.
local cohorts={
 {name="New player",accuracy=.4,knockoutShare=.2,pvpPerMinute=.03,questXPPerMinute=8},
 {name="Average player",accuracy=.65,knockoutShare=.3,pvpPerMinute=.18,questXPPerMinute=12},
 {name="Skilled player",accuracy=.85,knockoutShare=.4,pvpPerMinute=.55,questXPPerMinute=15},
}
for _,c in ipairs(cohorts) do
 local minutes=0
 for l=1,299 do
  local npc=15*c.accuracy*(5*(1-c.knockoutShare)+16*c.knockoutShare)
  local rate=npc+c.pvpPerMinute*P.PlayerKOXP(l)+c.questXPPerMinute
  minutes+=P.XPToNext(l)/rate
  if l+1==25 or l+1==50 or l+1==100 or l+1==300 then
   print(string.format("ESTIMATE %s -> level %d: %.1f active hours",c.name,l+1,minutes/60))
  end
 end
end
