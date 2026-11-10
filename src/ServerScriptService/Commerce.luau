-- Separate atomic purchase ledger: gameplay profile snapshots never write it.
local Marketplace=game:GetService("MarketplaceService")
local Players=game:GetService("Players")
local Run=game:GetService("RunService")
local Http=game:GetService("HttpService")
local Catalog=require(game:GetService("ReplicatedStorage").Shared.ShopCatalog)
local Ledger=require(game:GetService("ReplicatedStorage").Shared.BoostLedger)
local Config=require(game:GetService("ReplicatedStorage").Shared.Config)
local Entitlements=require(script.Parent.Entitlements)
local Commerce={}
local cache,locks,promptAt={},{},{}
local loadAt,activateAt={},{}
local allowed,changed,store
local function database()
 if Run:IsStudio() then return end
 if not store then
  local ok,value=pcall(function() return game:GetService("DataStoreService"):GetDataStore("ScreamSimulator_Purchases_v1") end)
  if ok then store=value end
 end
 return store
end
local function transact(player,transform)
 local db=database();if not db then return false end
 local id=player.UserId
 while locks[id] do task.wait(.05) end
 -- A leave, unavailable profile or test command may have happened while waiting.
 if not player.Parent or not allowed(player) then return false end
 locks[id]=true
 local success,result
 for attempt=1,3 do
  success,result=pcall(function() return db:UpdateAsync("Player_"..id,transform) end)
  if success then break end
  task.wait(attempt)
 end
 if success and result then
  if player.Parent then cache[player]=Ledger.Normalize(result) end
 elseif not success then cache[player]=nil end -- never grant from an ambiguous write
 locks[id]=nil
 return success and result~=nil
end
function Commerce.Load(player)
 if not database() or not allowed(player) then return end
 if os.clock()<(loadAt[player] or 0) or locks[player.UserId] then return end
 loadAt[player]=os.clock()+15
 local ok=transact(player,Ledger.Normalize)
 if ok and player.Parent then changed(player) end
end
function Commerce.Status(player)
 local d=cache[player]
 return {ready=d~=nil and allowed(player),inventory=d and d.inventory or {xp=0,coins=0},ends=d and d.ends or {xp=0,coins=0},serverNow=os.time()}
end
function Commerce.Multiplier(player,kind) return Ledger.Multiplier(cache[player],kind,os.time()) end
function Commerce.Busy(player) return locks[player.UserId]==true end
function Commerce.Activate(player,kind)
 if (kind~="xp" and kind~="coins") or not allowed(player) or not cache[player] then return end
 if os.clock()<(activateAt[player] or 0) or locks[player.UserId] then return end
 activateAt[player]=os.clock()+2
 local operation=Http:GenerateGUID(false);local started=os.time()
 local ok=transact(player,function(raw)
  local data=Ledger.Activate(raw,kind,operation,started,os.time())
  return data -- UpdateAsync's second return is user IDs, not a status string.
 end)
 if player.Parent then changed(player,ok and "Boost activated · 30 minutes added · continues offline" or "Boost not activated. Check your inventory and try again.") end
end
function Commerce.Prompt(player,key)
 local item=Catalog.Get(key)
 if not item or Run:IsStudio() or not allowed(player) then changed(player,"Purchases are unavailable in this session.");return end
 local id=item.key=="Movement" and Config.MovementPassId or item.id
 if type(id)~="number" or id<=0 then changed(player,"This unlock is coming soon.");return end
 if os.clock()<(promptAt[player] or 0) then return end
 promptAt[player]=os.clock()+3
 if item.kind=="product" and not cache[player] then changed(player,"Loading your purchases. Please try again.");task.spawn(Commerce.Load,player);return end
 if item.kind=="product" then
  local count=0;for _ in pairs(cache[player].receipts) do count+=1 end
  if Catalog.Product(id)~=item or count>=Ledger.ReceiptLimit or cache[player].inventory[item.boost]>=1000000 then
   changed(player,"This purchase is currently unavailable.");return
  end
 end
 if item.key=="Spectrum" and Entitlements.HasSpectrum(player) or item.key=="Movement" and Entitlements.HasMovement(player) then return end
 local ok=pcall(function()
  if item.kind=="pass" then Marketplace:PromptGamePassPurchase(player,id)
  else Marketplace:PromptProductPurchase(player,id) end
 end)
 if not ok then changed(player,"Roblox could not open this purchase. Please try again.") end
end
function Commerce.Start(canPurchase,onChanged)
 assert(not allowed,"Commerce already started")
 allowed=canPurchase;changed=onChanged
 Marketplace.ProcessReceipt=function(receipt)
  local item=Catalog.Product(receipt.ProductId)
  local player=Players:GetPlayerByUserId(receipt.PlayerId)
  if not item or not player or Run:IsStudio() or not allowed(player) then return Enum.ProductPurchaseDecision.NotProcessedYet end
  local ok=transact(player,function(raw)
   local data=Ledger.Grant(raw,tostring(receipt.PurchaseId),item.boost)
   return data
  end)
  if not ok then return Enum.ProductPurchaseDecision.NotProcessedYet end
  if player.Parent then changed(player,"Boost added to inventory · activate it in the shop") end
  return Enum.ProductPurchaseDecision.PurchaseGranted
 end
 Players.PlayerRemoving:Connect(function(player) cache[player]=nil;promptAt[player]=nil;loadAt[player]=nil;activateAt[player]=nil end)
end
return Commerce
