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
remote.OnServerEvent:Connect(function(p,verb,sequence,power,target)
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
  if accepted then
   local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
   if not root then return end
   local origin=root.Position+Vector3.new(0,1,0)
   local direction=root.CFrame.LookVector
   if typeof(target)=="Vector3" and Rules.IsFinite(target.X) and Rules.IsFinite(target.Y) and Rules.IsFinite(target.Z) then
    local delta=target-origin
    if delta.Magnitude>.01 and delta.Magnitude<100000 then direction=delta.Unit end
   end
   local length=Rules.Stats(1,power,false).range
   local params=RaycastParams.new();params.FilterDescendantsInstances={p.Character};params.RespectCanCollide=true
   local hit=workspace:Raycast(origin,direction*length,params)
   if hit then length=(hit.Position-origin).Magnitude end
   if length>.01 then
    local pulse=Instance.new("Part");pulse.Name="LiveMicTestPulse";pulse.Anchored=true;pulse.CanCollide=false;pulse.CanQuery=false;pulse.CanTouch=false
    pulse.Material=Enum.Material.Neon;pulse.Color=Color3.fromRGB(75,224,235);pulse.Transparency=.25
    pulse.Size=Vector3.new(.5,.5,length);pulse.CFrame=CFrame.lookAt(origin+direction*length/2,origin+direction*length)
    pulse.Parent=workspace;game:GetService("Debris"):AddItem(pulse,.3)
   end
  end
 end
end)
