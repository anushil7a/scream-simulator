-- Independent server-owned balls: another player's attacks cannot advance your challenge.
local Players=game:GetService("Players")
local Run=game:GetService("RunService")
local Rules=require(script.Parent.CombatRules)
local Soccer={}
local runs={}
local V=Vector3.new
local origin=V(615,2.2,550)
local goals={V(664,2.2,550),V(606,2.2,518),V(690,2.2,517),V(617,2.2,576),V(686,2.2,575)}
local function ball(parent,name,size,color)
 local p=Instance.new("Part");p.Name=name;p.Shape=Enum.PartType.Ball;p.Size=V(size,size,size);p.Color=color;p.Material=Enum.Material.SmoothPlastic;p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.Parent=parent;return p
end
local function target(run,now)
 local p=goals[run.stage]
 return p+(run.stage>=4 and V(math.sin((now-run.started)*1.5)*5,0,0) or Vector3.zero)
end
function Soccer.Cancel(player)
 local run=runs[player];if run then run.model:Destroy();runs[player]=nil end
end
function Soccer.Start(player,notify,complete)
 Soccer.Cancel(player)
 local model=Instance.new("Model");model.Name="SoccerAttempt_"..player.UserId;model.Parent=workspace.ScreamSimulatorWorld
 local run={model=model,ball=ball(model,"ChallengeBall",2.2,Color3.fromRGB(242,233,211)),goal=ball(model,"Target",7,Color3.fromRGB(96,224,176)),position=origin,velocity=Vector3.zero,stage=1,started=os.clock(),notify=notify,complete=complete}
 run.goal.Transparency=.65;run.goal.Material=Enum.Material.Neon
 run.ball.Position=origin;run.goal.Position=goals[1]
 local gui=Instance.new("BillboardGui");gui.Size=UDim2.fromOffset(190,38);gui.StudsOffset=V(0,3,0);gui.MaxDistance=65;gui.Parent=run.ball
 local label=Instance.new("TextLabel");label.BackgroundTransparency=1;label.Size=UDim2.fromScale(1,1);label.Font=Enum.Font.GothamBold;label.TextSize=14;label.TextColor3=Color3.new(1,1,1);label.TextStrokeTransparency=.3;label.Text=player.DisplayName.." · Nick's challenge";label.Parent=gui
 runs[player]=run
 notify("Nick: Five targets, 120 seconds! Aim your mic beam at your ball. Final targets move. Stay inside the court!")
end
function Soccer.Hit(player,beamOrigin,direction,length,width,power)
 local run=runs[player];if not run then return end
 if (run.position-beamOrigin).Magnitude>35 or not Rules.InBeam(beamOrigin,direction,run.position,length,width,1.1) then return end
 local flat=V(direction.X,0,direction.Z);if flat.Magnitude<.05 then return end
 -- Stronger shots roll farther; friction allows soft controlled passes.
 run.velocity=flat.Unit*(12+power*34)
end
Players.PlayerRemoving:Connect(Soccer.Cancel)
Run.Heartbeat:Connect(function(dt)
 dt=math.min(dt,.1);local now=os.clock()
 for player,run in pairs(runs) do
  local root=player.Character and player.Character:FindFirstChild("HumanoidRootPart")
  if not root or now-run.started>120 or (root.Position-V(647,4,547)).Magnitude>130 then
   run.notify("Nick: We can try again. Come back to the court and restart the quest!");Soccer.Cancel(player);continue
  end
  local goal=target(run,now);run.goal.Position=goal
  local old=run.position;local step=run.velocity*dt;local nextPosition=old+step
  if nextPosition.X<592 or nextPosition.X>704 or nextPosition.Z<502 or nextPosition.Z>587 then
   run.position=origin;run.velocity=Vector3.zero;run.notify("Out of bounds! Ball reset; the timer keeps running.")
  else
   run.position=nextPosition;run.velocity*=math.exp(-1.05*dt)
   local alpha=step.Magnitude>.001 and math.clamp((goal-old):Dot(step)/step:Dot(step),0,1) or 0
   local radius=run.stage>=4 and 3.5 or 4.5
   if run.velocity.Magnitude>1 and (old+step*alpha-goal).Magnitude<radius then
    run.stage+=1
    if run.stage>#goals then
     local complete=run.complete;Soccer.Cancel(player);complete();continue
    end
    run.velocity*=.3;run.notify("Target "..(run.stage-1).." / 5! "..math.ceil(120-(now-run.started)).." seconds left.")
   end
  end
  run.ball.CFrame=CFrame.new(run.position)*CFrame.Angles(0,0,now*run.velocity.Magnitude*.25)
 end
end)
return Soccer
