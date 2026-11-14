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
-- Authored silhouettes, not damage tiers. Counts stay within the existing budget.
local profiles={
 [0]={collar="round",ribbon="helix",turns=1.5},
 [1]={collar="diamond",ribbon="helix",turns=1.5},
 [2]={collar="diamond",ribbon="helix",turns=1.5},
 [3]={collar="round",ribbon="helix",turns=1.5},
 [4]={collar="round",ribbon="helix",turns=1.5},
 [5]={collar="round",ribbon="zigzag",turns=1.5},
 [6]={collar="round",ribbon="helix",turns=1.5},
 [7]={collar="round",ribbon="helix",turns=1.5},
 [8]={collar="round",ribbon="helix",turns=1.5},
 [9]={collar="star",ribbon="helix",turns=2.5},
 [10]={collar="star",ribbon="braid",turns=3.5},
}
function Style.Detail(level,reduced,distance)
 local tier=Style.Tier(level)
 if reduced or distance>Style.FarDistance then return {tier=tier,rings=0,strands=0,sparks=0} end
 local profile=profiles[tier]
 return {tier=tier,rings=1+math.floor(tier/3),strands=tier>=4 and (tier>=8 and 2 or 1) or 0,sparks=tier>=2 and (tier>=7 and 8 or 4) or 0,collar=profile.collar,ribbon=profile.ribbon,turns=profile.turns}
end
return Style
