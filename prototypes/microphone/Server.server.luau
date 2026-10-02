-- Isolated feasibility lab: no saves, rewards, entitlements or purchases.
local Players=game:GetService("Players")
local RS=game:GetService("ReplicatedStorage")
local Rules=require(RS.Shared.VoiceCombat)
local remote=Instance.new("RemoteEvent");remote.Name="MicLab";remote.Parent=RS
local ground=Instance.new("Part");ground.Name="TestFloor";ground.Anchored=true;ground.Size=Vector3.new(80,1,180);ground.Position=Vector3.new(0,-.5,-60);ground.Color=Color3.fromRGB(48,72,78);ground.Parent=workspace
local spawn=Instance.new("SpawnLocation");spawn.Anchored=true;spawn.Size=Vector3.new(8,1,8);spawn.Position=Vector3.new(0,.5,8);spawn.Neutral=true;spawn.Parent=workspace
for _,distance in ipairs({0,10,25,50,100}) do
 local line=Instance.new("Part");line.Name=tostring(distance).."Studs";line.Anchored=true;line.CanCollide=false;line.Size=Vector3.new(70,.05,.3);line.Position=Vector3.new(0,.05,-distance);line.Color=Color3.fromRGB(255,205,111);line.Parent=workspace
 local plate=Instance.new("Part");plate.Name="DistanceLabel";plate.Anchored=true;plate.CanCollide=false;plate.Size=Vector3.new(16,.04,4);plate.Position=Vector3.new(-24,.06,-distance-3);plate.Color=Color3.fromRGB(32,47,54);plate.Parent=workspace
 local gui=Instance.new("SurfaceGui");gui.Face=Enum.NormalId.Top;gui.CanvasSize=Vector2.new(512,128);gui.Parent=plate
 local label=Instance.new("TextLabel");label.Size=UDim2.fromScale(1,1);label.BackgroundTransparency=1;label.TextColor3=Color3.new(1,1,1);label.TextSize=52;label.Text=distance==0 and "ORIGIN" or distance.." STUDS";label.Parent=gui
end
local sessions={}
local function added(p)
 sessions[p]={voice=Rules.New(),requests=0,window=0}
 p.CharacterRemoving:Connect(function() local s=sessions[p];if s then Rules.Cancel(s.voice) end end)
end
Players.PlayerAdded:Connect(added);for _,p in ipairs(Players:GetPlayers()) do added(p) end
Players.PlayerRemoving:Connect(function(p) sessions[p]=nil end)
remote.OnServerEvent:Connect(function(p,verb,sequence,power)
 local s=sessions[p];if not s then return end
 local now=os.clock();if now-s.window>=1 then s.window=now;s.requests=0 end
 s.requests+=1;if s.requests>20 then return end
 local h=p.Character and p.Character:FindFirstChildOfClass("Humanoid")
 local alive=h and h.Health>0
 if verb=="begin" then Rules.Begin(s.voice,now,sequence,alive==true)
 elseif verb=="cancel" then Rules.Cancel(s.voice)
 elseif verb=="release" then
  local accepted=Rules.Release(s.voice,now,sequence,power,alive==true)
  remote:FireClient(p,accepted and "Accepted" or "Rejected",accepted and power or 0,sequence)
 end
end)
