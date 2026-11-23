-- Only the explicitly built travel rehearsal includes this module and its settings.
local settings=require(script.Parent.TravelSettings)
local studio=game:GetService("RunService"):IsStudio()
local rehearsal=settings.rehearsal
assert(studio and (rehearsal and game.GameId==0 and game.PlaceId==0
 or not rehearsal and game.GameId==settings.universe and game.PlaceId==settings.source),
 "Open this travel-only build in its configured Studio test place")
local players=game:GetService("Players")
local transporter=not rehearsal and game:GetService("TeleportService") or nil
local pending={}
local serial=0
local Travel={}

local function failed(player,attempt,message)
 if pending[player]~=attempt then return end
 pending[player]=nil
 player:SetAttribute("TravelStatus",message)
end

if transporter then
 transporter.TeleportInitFailed:Connect(function(player,_,_,destination,options)
  if not pending[player] or destination~=settings.destination or not options then return end
  local data=options:GetTeleportData()
  if type(data)=="table" then
   failed(player,data.travelAttempt,"Travel failed. You can try the portal again.")
  end
 end)
end
players.PlayerRemoving:Connect(function(player)pending[player]=nil end)

function Travel.Bind(prompt)
 prompt.KeyboardKeyCode=Enum.KeyCode.F
 prompt.Triggered:Connect(function(player)
  if player.Parent~=players or pending[player] or not prompt.Enabled or not prompt.Parent then return end
  local character=player.Character
  local root=character and character:FindFirstChild("HumanoidRootPart")
  local human=character and character:FindFirstChildOfClass("Humanoid")
  if not root or not human or human.Health<=0 or (root.Position-prompt.Parent.Position).Magnitude>prompt.MaxActivationDistance then return end
  if rehearsal then
   player:SetAttribute("TravelStatus","Portal reached. This local rehearsal stays in the same place.")
   return
  end
  serial+=1
  local attempt=serial
  pending[player]=attempt
  player:SetAttribute("TravelStatus","Opening the other world...")
  local ok=pcall(function()
   local options=Instance.new("TeleportOptions")
   options:SetTeleportData({travelAttempt=attempt})
   transporter:TeleportAsync(settings.destination,{player},options)
  end)
  if not ok then failed(player,attempt,"Travel failed. You can try the portal again.") end
 end)
end
return Travel
