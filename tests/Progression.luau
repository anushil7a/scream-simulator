local P=require("../src/ReplicatedStorage/Shared/Progression")
local checks=0
local function expect(v) checks+=1;assert(v) end
local previous=0;local previousKO=0
for l=1,P.MaxLevel do
 local required=P.XPToNext(l);local ko=P.PlayerKOXP(l)
 expect(required>previous);expect(ko>=previousKO);expect(ko<=690)
 previous,previousKO=required,ko
 local normalized,xp=P.Normalize(l,required)
 expect(normalized==math.min(P.MaxLevel,l+1));expect(xp==0)
end
for _,invalid in ipairs({-5,math.huge,0/0,"broken"}) do local l,xp=P.Normalize(invalid,invalid);expect(l==1 and xp==0) end
local level,xp=P.Normalize(1,P.XPToNext(1)+P.XPToNext(2)+17)
expect(level==3 and xp==17) -- migration carries XP, rather than dropping it at a new threshold
local cap,overflow=P.Normalize(99,1e9);expect(cap==100 and overflow==0)
expect(P.MaxLevel==100)
local legacy,legacyXP=P.Normalize(300,500);expect(legacy==100 and legacyXP==0)
print("PASS "..checks.." progression/migration rule checks")
