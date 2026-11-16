-- Server attack metadata only. Independent of reduced visual effects; no remotes/voice capture.
local stopped=false;local heartbeat;local audio;local events
script.Destroying:Connect(function()
 stopped=true;if heartbeat then heartbeat:Disconnect() end
 if events then events:Clear() end;if audio then audio:Destroy() end
end)
local Adapter=require(script.Parent:WaitForChild('BossAudio'));if stopped then return end
local Gates=require(script.Parent:WaitForChild('BossAudioEvents'));if stopped then return end
local Settings=require(game:GetService('ReplicatedStorage'):WaitForChild('Shared'):WaitForChild('BossAudioConfig'));if stopped then return end
local player=game:GetService('Players').LocalPlayer
local Run=game:GetService('RunService')
audio=Adapter.new();if stopped then audio:Destroy();return end
local function play(id,stage,serial,position,now)
 local key=Settings.Key(id,stage,serial);if key then audio:Play(key,now,position)end
end
events=Gates.new(play,function(id,all)audio:CancelTell(id,all)end)
local elapsed=0
heartbeat=Run.Heartbeat:Connect(function(dt)
 local enabled=player:GetAttribute('BossAudioEnabled')==true
 local suppressed=player:GetAttribute('BossAudioSuppressed')~=false
 audio:SetEnabled(enabled);audio:SetContext(player:GetAttribute('BossAudioVoiceActive')==true,suppressed)
 local now=workspace:GetServerTimeNow();audio:Step(now,dt)
 elapsed+=dt;if elapsed<.05 then return end;elapsed=0
 local character=player.Character;local root=character and character:FindFirstChild('HumanoidRootPart')
 if not root then audio:Clear() end
 local world=workspace:FindFirstChild('ScreamSimulatorWorld');local folder=world and world:FindFirstChild('BossEncounters')
 local present={}
 if folder then
  for _,model in ipairs(folder:GetChildren())do
   local id=model.Name
   if Settings.Themes[id] then
    present[id]=true
    local core=model:FindFirstChild('Core')
    local eligible=enabled and not suppressed and root~=nil and core~=nil and core:IsA('BasePart') and (core.Position-root.Position).Magnitude<=Settings.Range
    events:Step(model,id,model:GetAttribute('BossAttackSerial'),model:GetAttribute('BossAttackAt'),model:GetAttribute('BossAttackImpactSerial'),model:GetAttribute('BossAttackImpactAt'),model:GetAttribute('BossState'),now,core and core:IsA('BasePart') and core.Position or nil,eligible)
   end
  end
 end
 events:RemoveAbsent(present)
end)
