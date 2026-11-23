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

-- Stage the same landing in zero-ID rehearsal. Actual test places require the
-- engine's peer IDs; teleport payloads never select a destination or reward.
function Travel.BindArrival(destination,message)
 local seen={}
 local function joined(player)
  if player.Parent~=players or seen[player] then return end
  if not rehearsal then
   local from=player:GetJoinData()
   if from.SourceGameId~=settings.universe or from.SourcePlaceId~=settings.destination then return end
  end
  seen[player]=true
  local function land(character)
   if player.Parent~=players or player.Character~=character then return end
   local root=character:WaitForChild("HumanoidRootPart",5)
   local deadline=os.clock()+5
   while root and not character:IsDescendantOf(workspace) and os.clock()<deadline
    and player.Parent==players and player.Character==character do task.wait() end
   local humanoid=character:FindFirstChildOfClass("Humanoid")
   if not root or root.Parent~=character or not humanoid or humanoid.Health<=0
    or player.Parent~=players or player.Character~=character or not character:IsDescendantOf(workspace) then return end
   character:PivotTo(destination)
   root.AssemblyLinearVelocity=Vector3.zero;root.AssemblyAngularVelocity=Vector3.zero
   local arrivalStatus=(rehearsal and "Arrival rehearsal. " or "")..message
   player:SetAttribute("TravelStatus",arrivalStatus)
   player.CharacterRemoving:Once(function(removed)
    if removed==character and player:GetAttribute("TravelStatus")==arrivalStatus then
     player:SetAttribute("TravelStatus",nil)
    end
   end)
  end
  if player.Character then task.defer(land,player.Character)
  else player.CharacterAdded:Once(land) end
 end
 players.PlayerRemoving:Connect(function(player)seen[player]=nil end)
 players.PlayerAdded:Connect(joined)
 for _,player in ipairs(players:GetPlayers()) do joined(player) end
end

function Travel.Bind(prompt)
 prompt.KeyboardKeyCode=Enum.KeyCode.F
 if rehearsal then prompt.ActionText="Preview portal" end
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
