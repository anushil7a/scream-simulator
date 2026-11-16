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
-- Every ten levels gains visible width and a stronger lightning/corona recipe.
-- Cosmetic only: never feed these widths back to combat or contact placement.
local profiles={
 [0]={widthScale=1.00,rings=1,strands=0,sparks=0},
 [1]={widthScale=1.22,rings=1,strands=1,sparks=0},
 [2]={widthScale=1.46,rings=1,strands=1,sparks=2},
 [3]={widthScale=1.72,rings=1,strands=1,sparks=4},
 [4]={widthScale=2.00,rings=1,strands=2,sparks=4},
 [5]={widthScale=2.30,rings=1,strands=2,sparks=6},
 [6]={widthScale=2.62,rings=1,strands=2,sparks=8},
 [7]={widthScale=2.96,rings=2,strands=3,sparks=8},
 [8]={widthScale=3.32,rings=2,strands=3,sparks=10},
 [9]={widthScale=3.70,rings=2,strands=3,sparks=12},
 [10]={widthScale=4.10,rings=2,strands=3,sparks=16},
}
function Style.WidthScale(level,quiet)
 local scale=profiles[Style.Tier(level)].widthScale
 -- Static quiet silhouettes still identify the milestone, without huge coverage.
 return quiet and 1+(scale-1)*.18 or scale
end
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
 return {tier=tier,rings=profile.rings,strands=profile.strands,sparks=profile.sparks,
  collar=tier>=8 and "star" or tier>=1 and "diamond" or "round",
  ribbon="lightning",turns=1.5+tier*.2,style=styleId}
end
return Style
