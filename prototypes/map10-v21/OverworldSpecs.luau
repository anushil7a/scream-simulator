local here=script and script.Parent
local Builder=require(here and here.OverworldBuilder or "./OverworldBuilder")
local Layout=require(here and here.OverworldLayout or "./OverworldLayout")
local Geometry=require(here and here.OverworldGeometry or "./OverworldGeometry")
local Arteries=require(here and here.OverworldArteries or "./OverworldArteries")
local West=require(here and here.DistrictWest or "./DistrictWest")
local Coast=require(here and here.DistrictCoast or "./DistrictCoast")
local East=require(here and here.DistrictEast or "./DistrictEast")
local Foundry=require(here and here.Zone05Geometry or "./Zone05Geometry")
local Cliffs=require(here and here.OverworldCliffs or "./OverworldCliffs")
local Harbor=require(here and here.FoundryHarborArt or "./FoundryHarborArt")
local Ridge=require(here and here.MainlandRidge or "./MainlandRidge")
return function(compact)
 local b=Builder.new()
 b.compact=compact
 local groups=Geometry.Compose(b,Layout,Arteries,West,Coast,East,Foundry)
 Harbor(b)
 Cliffs(b,Layout)
 Ridge(b)
 return b,groups,Layout
end
