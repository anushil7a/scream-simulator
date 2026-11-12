-- Location-bound scenery audio. Roblox handles live voice independently.
local Collection=game:GetService("CollectionService")
local Run=game:GetService("RunService")
local SoundService=game:GetService("SoundService")
local Content=game:GetService("ContentProvider")
local destroyed=false
-- Install terminal startup guard before dependency waits or a yielding require.
script.Destroying:Connect(function() destroyed=true end)
local replicated=game:GetService("ReplicatedStorage")
local shared=replicated:WaitForChild("Shared");if destroyed then return end
local configModule=shared:WaitForChild("Config");if destroyed then return end
local Config=require(configModule);if destroyed then return end
local assets={}
local group=Instance.new("SoundGroup");group.Name="CityAmbience";group.Volume=.55;group.Parent=SoundService
local folder=Instance.new("Folder");folder.Name="LocalCitySoundscape";folder.Parent=workspace
local function source(name,position,id,volume,near,far)
 local anchor=Instance.new("Part");anchor.Name=name;anchor.Size=Vector3.one;anchor.Position=position;anchor.Transparency=1;anchor.Anchored=true;anchor.CanCollide=false;anchor.CanQuery=false;anchor.CanTouch=false;anchor.CastShadow=false;anchor.Parent=folder
 local sound=Instance.new("Sound");sound.Name=name; sound.SoundId="rbxassetid://"..id;sound.Looped=true;sound.Volume=volume;sound.RollOffMode=Enum.RollOffMode.InverseTapered;sound.RollOffMinDistance=near;sound.RollOffMaxDistance=far;sound.SoundGroup=group;sound.Parent=anchor
 assets[id]=assets[id] or {};table.insert(assets[id],sound)
 return sound
end
local surfPositions=Config.CompactCity and Config.CityLayout.Ambience.surfPositions or {Vector3.new(-540,1,590),Vector3.new(-180,1,590),Vector3.new(180,1,590),Vector3.new(540,1,590)}
for _,position in ipairs(surfPositions) do source("CoastalSurf",position,"9119677305",.16,45,230) end
local stage=Config.CompactCity and Config.CityLayout.Ambience.buskerPosition or Vector3.new(150,5,426)
local guitar=source("BuskerGuitar",stage,"15675051846",0,8,70)
-- Load each shared asset once, then start its emitters together. A transient
-- CDN failure gets two retries; failed ambience never blocks gameplay or loops
-- requests forever. A pending load cannot restart audio after cleanup.
for _,sounds in pairs(assets) do
 task.spawn(function()
  local representative=sounds[1]
  for attempt=1,3 do
   if destroyed then return end
   representative:SetAttribute("LoadAttempts",attempt)
   pcall(function() Content:PreloadAsync({representative}) end)
   if destroyed then return end
   if representative.IsLoaded then
    for _,sound in sounds do sound:Play() end
    return
   end
   if attempt<3 then task.wait(attempt*2) end
  end
 end)
end
local performing=false;local elapsed=0
local heartbeat=Run.Heartbeat:Connect(function(dt)
 if destroyed then return end
 elapsed+=dt
 if elapsed>=.5 then
  elapsed=0;performing=false
  for _,model in Collection:GetTagged("CityResident") do
   local root=model:FindFirstChild("HumanoidRootPart");local humanoid=model:FindFirstChildOfClass("Humanoid")
   if model:IsDescendantOf(workspace) and model:GetAttribute("ResidentActive")~=false and model:GetAttribute("Role")=="Busker" and model:GetAttribute("Working") and root and humanoid and humanoid.Health>0 and (root.Position-stage).Magnitude<35 then performing=true;break end
  end
 end
 guitar.Volume+=((performing and .2 or 0)-guitar.Volume)*math.min(dt*3,1)
end)
local connection
script.Destroying:Connect(function() destroyed=true;heartbeat:Disconnect();if connection then connection:Disconnect() end;folder:Destroy();group:Destroy() end)
local remotes=game:GetService("ReplicatedStorage"):WaitForChild("ScreamRemotes")
if destroyed then return end
local state=remotes:WaitForChild("State")
if destroyed then return end
connection=state.OnClientEvent:Connect(function(data)
 if destroyed then return end
 local volume=type(data)=="table" and type(data.settings)=="table" and data.settings.volume
 if type(volume)=="number" and volume==volume then group.Volume=math.clamp(volume,0,1) end
end)
local action=remotes:WaitForChild("Action")
if destroyed then return end
action:FireServer("Sync")
