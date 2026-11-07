-- Location-bound scenery audio. Roblox handles live voice independently.
local Collection=game:GetService("CollectionService")
local Run=game:GetService("RunService")
local SoundService=game:GetService("SoundService")
local group=Instance.new("SoundGroup");group.Name="CityAmbience";group.Volume=.55;group.Parent=SoundService
local folder=Instance.new("Folder");folder.Name="LocalCitySoundscape";folder.Parent=workspace
local function source(name,position,id,volume,near,far)
 local anchor=Instance.new("Part");anchor.Name=name;anchor.Size=Vector3.one;anchor.Position=position;anchor.Transparency=1;anchor.Anchored=true;anchor.CanCollide=false;anchor.CanQuery=false;anchor.CanTouch=false;anchor.CastShadow=false;anchor.Parent=folder
 local sound=Instance.new("Sound");sound.Name=name; sound.SoundId="rbxassetid://"..id;sound.Looped=true;sound.Volume=volume;sound.RollOffMode=Enum.RollOffMode.InverseTapered;sound.RollOffMinDistance=near;sound.RollOffMaxDistance=far;sound.SoundGroup=group;sound.Parent=anchor;sound:Play()
 return sound
end
for _,x in ipairs({-540,-180,180,540}) do source("CoastalSurf",Vector3.new(x,1,590),"9119677305",.16,45,230) end
local stage=Vector3.new(150,5,426)
local guitar=source("BuskerGuitar",stage,"15675051846",0,8,70)
local performing=false;local elapsed=0
local heartbeat=Run.Heartbeat:Connect(function(dt)
 elapsed+=dt
 if elapsed>=.5 then
  elapsed=0;performing=false
  for _,model in Collection:GetTagged("CityResident") do
   local root=model:FindFirstChild("HumanoidRootPart");local humanoid=model:FindFirstChildOfClass("Humanoid")
   if model:GetAttribute("Role")=="Busker" and model:GetAttribute("Working") and root and humanoid and humanoid.Health>0 and (root.Position-stage).Magnitude<35 then performing=true;break end
  end
 end
 guitar.Volume+=((performing and .2 or 0)-guitar.Volume)*math.min(dt*3,1)
end)
local connection;local destroyed=false
script.Destroying:Connect(function() destroyed=true;heartbeat:Disconnect();if connection then connection:Disconnect() end;folder:Destroy();group:Destroy() end)
local remotes=game:GetService("ReplicatedStorage"):WaitForChild("ScreamRemotes")
local state=remotes:WaitForChild("State")
if destroyed then return end
connection=state.OnClientEvent:Connect(function(data)
 local volume=type(data)=="table" and type(data.settings)=="table" and data.settings.volume
 if type(volume)=="number" and volume==volume then group.Volume=math.clamp(volume,0,1) end
end)
remotes:WaitForChild("Action"):FireServer("Sync")
