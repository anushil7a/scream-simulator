-- Cosmetic pass visuals are local and restricted to the City safe areas.
local Players=game:GetService("Players")
local RunService=game:GetService("RunService")
local GuiService=game:GetService("GuiService")
local Storage=game:GetService("ReplicatedStorage")
local shared=Storage:WaitForChild("Shared")
local Config=require(shared:WaitForChild("Config"))
if not Config.CompactCity or Config.ResonanceLayout then return end
local Catalog=require(shared:WaitForChild("ShopCatalog"))
local localFixture=RunService:IsStudio() and game.PlaceId==0 and game.GameId==0 and workspace:GetAttribute("LocalSustainedPrototype")==true
if not localFixture and Catalog.Get("Encore").id<=0 and Catalog.Get("Afterimage").id<=0 and Catalog.Get("CityGlow").id<=0 then return end

local localPlayer=Players.LocalPlayer
local gui=localPlayer:WaitForChild("PlayerGui")
local effect=Storage:WaitForChild("ScreamRemotes"):WaitForChild("Effect")
local titles,trails={},{}
local glow
local violet=Color3.fromRGB(179,151,255)
local mint=Color3.fromRGB(125,242,255)

local function safeRoot(player)
 local character=player.Character
 local root=character and character:FindFirstChild("HumanoidRootPart")
 local humanoid=character and character:FindFirstChildOfClass("Humanoid")
 if root and humanoid and humanoid.Health>0 and not Config.InArena(root.Position) then return root end
end

local function clearTitle(player)
 local plate=titles[player]
 if plate then plate:Destroy();titles[player]=nil end
end

local function clearTrail(player)
 local record=trails[player]
 if not record then return end
 record.trail:Destroy();record.bottom:Destroy();record.top:Destroy();trails[player]=nil
end

local function addTitle(player,head)
 local plate=Instance.new("BillboardGui")
 plate.Name="EncorePassTitle";plate.Adornee=head;plate.Size=UDim2.fromOffset(96,21)
 plate.StudsOffsetWorldSpace=Vector3.new(0,2.2,0);plate.MaxDistance=42;plate.AlwaysOnTop=false
 local label=Instance.new("TextLabel")
 label.Name="Title";label.Size=UDim2.fromScale(1,1);label.BackgroundColor3=Color3.fromRGB(17,20,45)
 label.BackgroundTransparency=.15;label.Text="ENCORE";label.TextColor3=violet
 label.TextSize=11;label.Font=Enum.Font.GothamBold;label.Parent=plate
 local corners=Instance.new("UICorner");corners.CornerRadius=UDim.new(0,7);corners.Parent=label
 local edge=Instance.new("UIStroke");edge.Color=violet;edge.Transparency=.56;edge.Parent=label
 plate.Parent=gui;titles[player]=plate
end

local effectConnection=effect.OnClientEvent:Connect(function(kind,origin,userId)
 if kind~="Dodge" or typeof(origin)~="Vector3" or type(userId)~="number" or Config.InArena(origin) then return end
 if GuiService.ReducedMotionEnabled then return end
 local player=Players:GetPlayerByUserId(userId)
 if not player or player:GetAttribute("AfterimagePass")~=true then return end
 local root,viewer=safeRoot(player),safeRoot(localPlayer)
 if not root or not viewer or (viewer.Position-origin).Magnitude>55 then return end
 clearTrail(player)
 local bottom=Instance.new("Attachment");bottom.Name="AfterimageBottom";bottom.Position=Vector3.new(0,-.7,.55);bottom.Parent=root
 local top=Instance.new("Attachment");top.Name="AfterimageTop";top.Position=Vector3.new(0,.7,.55);top.Parent=root
 local trail=Instance.new("Trail");trail.Name="AfterimagePassTrail";trail.Attachment0=bottom;trail.Attachment1=top
 trail.Color=ColorSequence.new(mint,violet);trail.Lifetime=.18;trail.LightEmission=.45;trail.FaceCamera=true
 trail.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.38),NumberSequenceKeypoint.new(1,1)})
 trail.WidthScale=NumberSequence.new({NumberSequenceKeypoint.new(0,.8),NumberSequenceKeypoint.new(1,0)})
 trail.Parent=root
 local now=os.clock();trails[player]={trail=trail,top=top,bottom=bottom,root=root,stopAt=now+.25,endAt=now+.44}
end)

local function updateGlow(viewer)
 local character=viewer and localPlayer:GetAttribute("CityGlowPass")==true and localPlayer.Character
 if glow and glow.Adornee~=character then glow:Destroy();glow=nil end
 if not character or glow then return end
 glow=Instance.new("Highlight")
 glow.Name="CityGlowPassOutline"
 glow.Adornee=character
 glow.DepthMode=Enum.HighlightDepthMode.Occluded
 glow.FillTransparency=1
 glow.OutlineColor=Color3.fromRGB(255,209,111)
 glow.OutlineTransparency=.48
 glow.Parent=character
end

local nextTitleUpdate=0
local heartbeat=RunService.Heartbeat:Connect(function()
 local now=os.clock()
 local viewer=safeRoot(localPlayer)
 updateGlow(viewer)
 for player,record in pairs(trails) do
  if not viewer or GuiService.ReducedMotionEnabled or safeRoot(player)~=record.root or player:GetAttribute("AfterimagePass")~=true or now>=record.endAt then clearTrail(player)
  elseif now>=record.stopAt then record.trail.Enabled=false end
 end
 if not viewer then
  for player in pairs(titles) do clearTitle(player) end
  return
 end
 for player,plate in pairs(titles) do
  local root=player:GetAttribute("EncorePass")==true and safeRoot(player)
  if not root or player.Character:FindFirstChild("Head")~=plate.Adornee then clearTitle(player) end
 end
 if now<nextTitleUpdate then return end
 nextTitleUpdate=now+.15
 for _,player in ipairs(Players:GetPlayers()) do
  local root=player:GetAttribute("EncorePass")==true and safeRoot(player)
  local head=root and (root.Position-viewer.Position).Magnitude<=42 and player.Character:FindFirstChild("Head")
  if not head then clearTitle(player)
  elseif not titles[player] or titles[player].Adornee~=head then clearTitle(player);addTitle(player,head) end
 end
end)
local removing=Players.PlayerRemoving:Connect(function(player) clearTitle(player);clearTrail(player) end)
script.Destroying:Connect(function()
 effectConnection:Disconnect();heartbeat:Disconnect();removing:Disconnect()
 updateGlow(nil)
 for player in pairs(titles) do clearTitle(player) end
 for player in pairs(trails) do clearTrail(player) end
end)
