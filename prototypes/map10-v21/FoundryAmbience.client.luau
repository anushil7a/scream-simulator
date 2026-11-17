-- Standalone Studio review only. Generic packaged placeholders, not authored surf/horns.
local Run=game:GetService("RunService")
if not Run:IsStudio() or game.GameId~=0 or game.PlaceId~=0 then return end
local Players=game:GetService("Players")
local Content=game:GetService("ContentProvider")
local Collection=game:GetService("CollectionService")
local stopped=false
local connections={};local voices={};local ui
local function stop()
 if stopped then return end;stopped=true
 for _,connection in ipairs(connections) do connection:Disconnect() end
 for _,voice in ipairs(voices) do voice.sound:Destroy() end
 if ui then ui:Destroy() end
end
table.insert(connections,script.Destroying:Connect(stop))
-- Bounded readiness wait; never enables itself in an ordinary game/place.
for _=1,100 do
 if stopped then return end
 if workspace:GetAttribute("ReviewBuildName")=="Map10V21FoundryReview" then break end
 task.wait(.1)
end
if stopped then return end
if workspace:GetAttribute("ReviewBuildName")~="Map10V21FoundryReview" then stop();return end
local cues={
 Dock={path="rbxasset://sounds/impact_water.mp3",gap=8,pitch=.8},
 Lighthouse={path="rbxasset://sounds/volume_slider.ogg",gap=14,pitch=.7},
}
-- Both paths were inventoried in official Studio content/sounds; availability still
-- varies. One bounded attempt per path. A missing asset stays entirely silent.
local ready={}
for kind,cue in pairs(cues) do
 local loaded=false
 pcall(function() Content:PreloadAsync({cue.path},function(_,status)
  if status==Enum.AssetFetchStatus.Success then loaded=true end
 end) end)
 if stopped then return end
 ready[kind]=loaded
end
local player=Players.LocalPlayer
local gui=player and player:FindFirstChildOfClass("PlayerGui")
if not gui or (not ready.Dock and not ready.Lighthouse) then stop();return end
local muted=false
ui=Instance.new("ScreenGui");ui.Name="FoundryPreviewSound";ui.ResetOnSpawn=false;ui.Parent=gui
local button=Instance.new("TextButton");button.Name="Mute";button.Size=UDim2.fromOffset(240,36);button.Position=UDim2.new(0,12,1,-48)
button.BackgroundColor3=Color3.fromRGB(20,35,42);button.TextColor3=Color3.fromRGB(225,234,231);button.TextSize=14
button.Text="Preview sound: ON (placeholders)";button.Parent=ui
local function silence()
 for _,voice in ipairs(voices) do voice.sound:Stop();voice.ends=0 end
end
table.insert(connections,button.Activated:Connect(function()
 muted=not muted;button.Text=muted and "Preview sound: MUTED" or "Preview sound: ON (placeholders)"
 if muted then silence() end
end))
local scanAt=0
local elapsed=0
local clock=0
local function tick(dt)
 if stopped then return end
 if workspace:GetAttribute("ReviewBuildName")~="Map10V21FoundryReview" then stop();return end
 clock+=dt;elapsed+=dt;if elapsed<.25 then return end;elapsed=0
 if clock>=scanAt then
  scanAt=clock+1
  local candidates={}
  for _,anchor in ipairs(Collection:GetTagged("FoundryAmbienceAnchor")) do
   local kind=anchor:GetAttribute("Cue")
   if cues[kind] and ready[kind] and anchor:IsA("BasePart") and anchor:IsDescendantOf(workspace) then
    candidates[kind]=candidates[kind] or anchor
   end
  end
  -- Release old sources before allocating replacements: never more than two.
  for i=#voices,1,-1 do
   local voice=voices[i]
   if candidates[voice.kind]~=voice.anchor then
    voice.sound:Stop();voice.sound:Destroy();table.remove(voices,i)
   else candidates[voice.kind]=nil end
  end
  for kind,anchor in pairs(candidates) do
   local cue=cues[kind]
   local sound=Instance.new("Sound");sound.Name="LocalFoundry"..kind;sound.SoundId=cue.path
   sound.Volume=.025;sound.PlaybackSpeed=cue.pitch;sound.Looped=false
   sound.RollOffMode=Enum.RollOffMode.InverseTapered;sound.RollOffMinDistance=10;sound.RollOffMaxDistance=90
   sound.Parent=anchor
   table.insert(voices,{kind=kind,sound=sound,anchor=anchor,cue=cue,next=clock+2,ends=0})
  end
 end
 local camera=workspace.CurrentCamera
 local character=player.Character;local humanoid=character and character:FindFirstChildOfClass("Humanoid")
 if muted or not camera or not humanoid or humanoid.Health<=0 then silence();return end
 for _,voice in ipairs(voices) do
  local near=voice.anchor:IsDescendantOf(workspace) and (camera.CFrame.Position-voice.anchor.Position).Magnitude<=90
  if not near then voice.sound:Stop();voice.ends=0
  elseif voice.ends>0 and clock>=voice.ends then voice.sound:Stop();voice.ends=0
  elseif voice.ends==0 and clock>=voice.next then
   voice.next=clock+voice.cue.gap;voice.ends=clock+3
   pcall(function()voice.sound:Play()end)
  end
 end
end
table.insert(connections,Run.Heartbeat:Connect(tick))
