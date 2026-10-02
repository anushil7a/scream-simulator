-- Initial 300-level economy. Simulation assumptions are recorded in tests/Progression.luau.
local Progression={MaxLevel=300}
function Progression.Level(level)
 if type(level)~="number" or level~=level or math.abs(level)==math.huge then return 1 end
 return math.clamp(math.floor(level),1,300)
end
function Progression.XPToNext(level)
 local l=Progression.Level(level)
 return math.floor(80+16*l+.012*l*l)
end
function Progression.PlayerKOXP(level)
 return math.floor(50+8*Progression.Level(level)^.7)
end
function Progression.Normalize(level,xp)
 local l=Progression.Level(level)
 local value=type(xp)=="number" and xp==xp and math.abs(xp)<math.huge and math.clamp(math.floor(xp),0,1e9) or 0
 while l<300 and value>=Progression.XPToNext(l) do value-=Progression.XPToNext(l);l+=1 end
 return l,l==300 and 0 or value
end
return Progression
