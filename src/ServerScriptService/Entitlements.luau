-- Server-owned entitlement cache. A zero ID disables purchases and paid benefits.
local Marketplace=game:GetService("MarketplaceService")
local Players=game:GetService("Players")
local Config=require(game.ReplicatedStorage.Shared.Config)
local Entitlements={}
local owned={}
local testOwned={}
function Entitlements.SetStudioMovement(player,enabled)
 if not game:GetService("RunService"):IsStudio() then return false end
 testOwned[player]=enabled==true
 return true
end
function Entitlements.HasStudioMovement(player)
 return game:GetService("RunService"):IsStudio() and testOwned[player]==true
end
function Entitlements.Refresh(player)
 local id=Config.MovementPassId
 if type(id)~="number" or id<=0 then owned[player]=false;return false end
 local success,result=pcall(Marketplace.UserOwnsGamePassAsync,Marketplace,player.UserId,id)
 if player.Parent and success then owned[player]=result==true end
 return owned[player]==true
end
function Entitlements.HasMovement(player)
 return owned[player]==true or Entitlements.HasStudioMovement(player)
end
function Entitlements.CanUseMovement(player,position)
 return Entitlements.HasMovement(player) and not Config.InArena(position)
end
Marketplace.PromptGamePassPurchaseFinished:Connect(function(player,id,purchased)
 if id==Config.MovementPassId and purchased then task.spawn(Entitlements.Refresh,player) end
end)
Players.PlayerRemoving:Connect(function(player) owned[player]=nil;testOwned[player]=nil end)
return Entitlements
