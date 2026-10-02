-- Server-owned entitlement cache. A zero ID disables purchases and paid benefits.
local Marketplace=game:GetService("MarketplaceService")
local Players=game:GetService("Players")
local Config=require(game.ReplicatedStorage.Shared.Config)
local Entitlements={}
local owned={}
function Entitlements.Refresh(player)
 local id=Config.MovementPassId
 if type(id)~="number" or id<=0 then owned[player]=false;return false end
 local success,result=pcall(Marketplace.UserOwnsGamePassAsync,Marketplace,player.UserId,id)
 if player.Parent and success then owned[player]=result==true end
 return owned[player]==true
end
function Entitlements.HasMovement(player)
 return owned[player]==true
end
function Entitlements.CanUseMovement(player,position)
 return Entitlements.HasMovement(player) and not Config.InArena(position)
end
Marketplace.PromptGamePassPurchaseFinished:Connect(function(player,id,purchased)
 if id==Config.MovementPassId and purchased then task.spawn(Entitlements.Refresh,player) end
end)
Players.PlayerRemoving:Connect(function(player) owned[player]=nil end)
return Entitlements
