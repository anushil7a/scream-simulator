-- Server-owned entitlement cache. A zero ID disables purchases and paid benefits.
local Marketplace=game:GetService("MarketplaceService")
local Players=game:GetService("Players")
local Config=require(game.ReplicatedStorage.Shared.Config)
local Catalog=require(game.ReplicatedStorage.Shared.ShopCatalog)
local Entitlements={}
local spectrum={}
local owned={}
local testOwned={}
local refreshIdentity={}
local cosmeticPasses={"Encore","Afterimage","CityGlow","SignalDeck","CityCrest","PulseFrame","RouteLights","HarborBadge","SprintRibbon"}
-- Removal may precede Parent becoming nil; queued refreshes must stay invalid.
local departed=setmetatable({},{__mode="k"})
function Entitlements.SetStudioMovement(player,enabled)
 if not game:GetService("RunService"):IsStudio() then return false end
 testOwned[player]=enabled==true
 return true
end
function Entitlements.HasStudioMovement(player)
 return game:GetService("RunService"):IsStudio() and testOwned[player]==true
end
function Entitlements.Refresh(player)
 if not player.Parent or departed[player] then return false end
 -- Each request supersedes older yielding work without permanently latching ownership.
 local identity={};refreshIdentity[player]=identity
 local function current() return player.Parent~=nil and refreshIdentity[player]==identity end
 local spectrumId=Catalog.Get("Spectrum").id
 if spectrumId>0 then
  local success,result=pcall(Marketplace.UserOwnsGamePassAsync,Marketplace,player.UserId,spectrumId)
  if not current() then return false end
  if success then spectrum[player]=result==true end
 else spectrum[player]=false end
 local id=Config.MovementPassId
 if type(id)~="number" or id<=0 then owned[player]=false
 else
  local success,result=pcall(Marketplace.UserOwnsGamePassAsync,Marketplace,player.UserId,id)
  if not current() then return false end
  if success then owned[player]=result==true end
 end
 for _,key in ipairs(cosmeticPasses) do
  local passId=Catalog.Get(key).id
  if passId>0 then
   local success,result=pcall(Marketplace.UserOwnsGamePassAsync,Marketplace,player.UserId,passId)
   if not current() then return false end
   if success then player:SetAttribute(key.."Pass",result==true) end
  else player:SetAttribute(key.."Pass",false) end
 end
 return owned[player]==true
end
function Entitlements.HasSpectrum(player) return spectrum[player]==true end
function Entitlements.HasEncore(player) return not departed[player] and player:GetAttribute("EncorePass")==true end
function Entitlements.HasAfterimage(player) return not departed[player] and player:GetAttribute("AfterimagePass")==true end
function Entitlements.HasCityGlow(player) return not departed[player] and player:GetAttribute("CityGlowPass")==true end
function Entitlements.HasSignalDeck(player) return not departed[player] and player:GetAttribute("SignalDeckPass")==true end
function Entitlements.HasCityCrest(player) return not departed[player] and player:GetAttribute("CityCrestPass")==true end
function Entitlements.HasPulseFrame(player) return not departed[player] and player:GetAttribute("PulseFramePass")==true end
function Entitlements.HasRouteLights(player) return not departed[player] and player:GetAttribute("RouteLightsPass")==true end
function Entitlements.HasHarborBadge(player) return not departed[player] and player:GetAttribute("HarborBadgePass")==true end
function Entitlements.HasSprintRibbon(player) return not departed[player] and player:GetAttribute("SprintRibbonPass")==true end
function Entitlements.HasMovement(player)
 return owned[player]==true or Entitlements.HasStudioMovement(player)
end
function Entitlements.CanUseMovement(player,position)
 return Entitlements.HasMovement(player) and not Config.InArena(position)
end
Marketplace.PromptGamePassPurchaseFinished:Connect(function(player,id,purchased)
 if id>0 and (id==Config.MovementPassId or id==Catalog.Get("Spectrum").id or id==Catalog.Get("Encore").id or id==Catalog.Get("Afterimage").id or id==Catalog.Get("CityGlow").id or id==Catalog.Get("SignalDeck").id or id==Catalog.Get("CityCrest").id or id==Catalog.Get("PulseFrame").id or id==Catalog.Get("RouteLights").id or id==Catalog.Get("HarborBadge").id or id==Catalog.Get("SprintRibbon").id) and purchased then task.spawn(Entitlements.Refresh,player) end
end)
Players.PlayerRemoving:Connect(function(player) departed[player]=true;refreshIdentity[player]=nil;owned[player]=nil;testOwned[player]=nil;spectrum[player]=nil end)
return Entitlements
