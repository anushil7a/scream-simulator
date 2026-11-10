-- Cosmetic complexity only; never used to calculate damage or hitboxes.
local Style={MaxParts=512,FarDistance=110,DrawDistance=180,Step=1/30}
-- A short launch expansion keeps the hit visible immediately and settles smoothly.
function Style.LaunchScale(age, reduced)
 if reduced then return 1 end
 local progress=math.clamp(age/.12,0,1)
 return .55+.45*(1-(1-progress)^3)
end
function Style.Tier(level)
 if type(level)~="number" or level~=level then return 0 end
 return math.floor(math.clamp(level,1,100)/10)
end
function Style.Detail(level,reduced,distance)
 local tier=Style.Tier(level)
 if reduced or distance>Style.FarDistance then return {tier=tier,rings=0,strands=0,sparks=0} end
 return {tier=tier,rings=1+math.floor(tier/3),strands=tier>=4 and (tier>=8 and 2 or 1) or 0,sparks=tier>=2 and (tier>=7 and 8 or 4) or 0}
end
return Style
