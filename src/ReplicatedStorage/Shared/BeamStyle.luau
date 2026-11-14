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
Style.Styles={
 starter={
  id="starter",
  minLevel=1,
  maxLevel=39,
  primary={255,220,90},
  secondary={245,252,255},
 },
 firebeam={
  id="firebeam",
  sourceAsset="FIREBEAM.rbxm",
  minLevel=40,
  maxLevel=79,
  primary={93,171,255},
  secondary={130,195,255},
  sheath={59,163,255},
  ember={78,134,255},
 },
 hollow_purple={
  id="hollow_purple",
  sourceAsset="hollow purple beam ig.rbxm",
  minLevel=80,
  maxLevel=100,
  primary={164,6,255},
  secondary={70,46,255},
  amplified={33,102,185},
  reversal={255,38,42},
  arc={156,75,255},
 },
}
Style.SpecialBeams={
 ChargingBeam={
  id="charging_beam",
  name="Charging Beam",
  status="reserved",
  sourceAsset="Charging Beam.rbxm",
  primaryColor={82,143,255},
  emitterCount=48,
 },
}
function Style.StyleForLevel(level)
 local tier=Style.Tier(level)
 if tier>=8 then
  return Style.Styles.hollow_purple
 elseif tier>=4 then
  return Style.Styles.firebeam
 end
 return Style.Styles.starter
end
function Style.Detail(level,reduced,distance)
 local tier=Style.Tier(level)
 local styleId=Style.StyleForLevel(level).id
 if reduced or distance>Style.FarDistance then return {tier=tier,rings=0,strands=0,sparks=0,style=styleId} end
 local profile=profiles[tier]
 return {tier=tier,rings=1+math.floor(tier/3),strands=tier>=4 and (tier>=8 and 2 or 1) or 0,sparks=tier>=2 and (tier>=7 and 8 or 4) or 0,collar=profile.collar,ribbon=profile.ribbon,turns=profile.turns,style=styleId}
end
return Style
