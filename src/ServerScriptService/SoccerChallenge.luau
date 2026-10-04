-- Personal server-owned challenge state; other players cannot collect or shoot your balls.
local Players=game:GetService("Players")
local Run=game:GetService("RunService")
local Rules=require(script.Parent.CombatRules)
local Soccer={}
local runs={}
local V=Vector3.new
local origin=V(615,2.2,550)
local lost={V(590,2.2,460),V(552,2.2,563),V(683,2.2,482)}
local gates={V(638,2.2,530),V(653,2.2,555),V(633,2.2,578),V(676,2.2,559)}
local obstacles={V(625,2.2,540),V(645,2.2,541),V(643,2.2,568),V(655,2.2,571)}
local goals={V(664,2.2,550),V(606,2.2,518),V(690,2.2,517),V(617,2.2,576),V(686,2.2,575)}
local function sphere(parent,name,size,color)
 local p=Instance.new("Part");p.Name=name;p.Shape=Enum.PartType.Ball;p.Size=V(size,size,size);p.Color=color;p.Material=Enum.Material.SmoothPlastic;p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.Parent=parent;return p
end
local function caption(part,text)
 local gui=Instance.new("BillboardGui");gui.Size=UDim2.fromOffset(190,38);gui.StudsOffset=V(0,3,0);gui.MaxDistance=35;gui.Parent=part
 local label=Instance.new("TextLabel");label.BackgroundTransparency=1;label.Size=UDim2.fromScale(1,1);label.Font=Enum.Font.GothamBold;label.TextSize=13;label.TextColor3=Color3.new(1,1,1);label.TextStrokeTransparency=.3;label.Text=text;label.Parent=gui
end
local function target(run,now)
 if run.phase=="Dribble" then return gates[run.stage] end
 local p=goals[run.stage]
 return p+(run.stage>=4 and V(math.sin((now-run.phaseStarted)*1.5)*5,0,0) or Vector3.zero)
end
function Soccer.Cancel(player)
 local run=runs[player];if run then runs[player]=nil;run.model:Destroy() end
end
function Soccer.Status(player)
 local run=runs[player];if not run then return nil end
 local detail=run.phase=="Find" and ("Find balls "..run.found.."/3") or run.phase=="Dribble" and ("Dribble gates "..(run.stage-1).."/4") or ("Moving targets "..(run.stage-1).."/5")
 return {phase=run.phase,detail=detail,remaining=math.max(0,math.ceil(run.deadline-os.clock()))}
end
local function setPhase(run,phase,seconds)
 run.phase=phase;run.phaseStarted=os.clock();run.deadline=run.phaseStarted+seconds;run.stage=1;run.position=origin;run.velocity=Vector3.zero
 run.model:SetAttribute("Phase",phase);run.ball.Position=origin;run.goal.Position=origin
 if phase~="Find" then
  run.ball.Transparency=0;run.goal.Transparency=.65;run.ball.Position=origin;run.goal.Position=target(run,os.clock())
 end
end
function Soccer.Collect(player,index)
 local run=runs[player];local point=type(index)=="number" and lost[index]
 local h=player.Character and player.Character:FindFirstChildOfClass("Humanoid")
 local root=player.Character and player.Character:FindFirstChild("HumanoidRootPart")
 if not run or run.phase~="Find" or not point or run.collected[index] or not root or not h or h.Health<=0 or os.clock()>run.deadline or (root.Position-point).Magnitude>10 then return false end
 run.collected[index]=true;run.found+=1;run.lostParts[index]:Destroy()
 if run.found==3 then
  setPhase(run,"Dribble",90)
  for _,position in ipairs(obstacles) do
   for tier=1,3 do
    local cone=sphere(run.cones,"TrainingCone",2-tier*.4,Color3.fromRGB(238,141,63));cone.Shape=Enum.PartType.Cylinder;cone.Size=V(.7,2-tier*.4,2-tier*.4);cone.CFrame=CFrame.new(position.X,1.35+tier*.6,position.Z)*CFrame.Angles(0,0,math.pi/2)
   end
  end
  run.notify("Nick: Found them! Return to the court. Four dribble gates in 90 seconds—steer around the orange cones. Soft mic shots help!")
 else run.notify("Training ball "..run.found.."/3. Clues: north beach loungers, the pier's east side, and the path north of the court.") end
 return true
end
function Soccer.Start(player,notify,complete,failed)
 Soccer.Cancel(player)
 local model=Instance.new("Model");model.Name="SoccerAttempt_"..player.UserId;model:SetAttribute("OwnerUserId",player.UserId);model.Parent=workspace.ScreamSimulatorWorld
 local cones=Instance.new("Folder");cones.Name="CourseCones";cones.Parent=model
 local run={model=model,cones=cones,ball=sphere(model,"ChallengeBall",2.2,Color3.fromRGB(242,233,211)),goal=sphere(model,"Target",7,Color3.fromRGB(96,224,176)),found=0,collected={},lostParts={},notify=notify,complete=complete,failed=failed}
 run.ball.Transparency=1;run.goal.Transparency=1;run.goal.Material=Enum.Material.Neon
 caption(run.ball,player.DisplayName.." · Nick's challenge")
 setPhase(run,"Find",120);runs[player]=run
 for i,pos in ipairs(lost) do
  local part=sphere(model,"LostTrainingBall"..i,2.2,Color3.fromRGB(239,213,140));part.Position=pos;run.lostParts[i]=part
  caption(part,player.DisplayName.." · training ball")
  local prompt=Instance.new("ProximityPrompt");prompt.ActionText="Recover ball";prompt.ObjectText="Nick's lost training ball";prompt.KeyboardKeyCode=Enum.KeyCode.F;prompt.HoldDuration=.5;prompt.MaxActivationDistance=8;prompt.Parent=part
  prompt.Triggered:Connect(function(actor) if actor==player and runs[player]==run then Soccer.Collect(player,i) end end)
 end
 notify("Nick: I lost THREE balls. You have 120 seconds! Check the north beach loungers, east of the pier, and the path north of this court. Hold F nearby.")
end
function Soccer.Hit(player,beamOrigin,direction,length,width,power)
 local run=runs[player];if not run or run.phase=="Find" then return end
 if (run.position-beamOrigin).Magnitude>35 or not Rules.InBeam(beamOrigin,direction,run.position,length,width,1.1) then return end
 local flat=V(direction.X,0,direction.Z);if flat.Magnitude<.05 then return end
 run.velocity=flat.Unit*(12+math.clamp(power,0,1)*34)
end
local function segmentDistance(a,step,point)
 local denominator=step:Dot(step);local alpha=denominator>.000001 and math.clamp((point-a):Dot(step)/denominator,0,1) or 0
 return (a+step*alpha-point).Magnitude
end
Players.PlayerRemoving:Connect(Soccer.Cancel)
Run.Heartbeat:Connect(function(dt)
 dt=math.min(dt,.1);local now=os.clock()
 for player,run in pairs(runs) do
  local root=player.Character and player.Character:FindFirstChild("HumanoidRootPart")
  local h=player.Character and player.Character:FindFirstChildOfClass("Humanoid")
  if not root or not h or h.Health<=0 or now>run.deadline or (root.Position-V(647,4,547)).Magnitude>150 then
   local failed=run.failed;Soccer.Cancel(player)
   if failed then failed() else run.notify("Nick: Let's retry at the court!") end
   continue
  end
  if run.phase=="Find" then continue end
  local goal=target(run,now);run.goal.Position=goal
  local old=run.position;local step=run.velocity*dt;local nextPosition=old+step
  local blocked=false
  if run.phase=="Dribble" and run.velocity.Magnitude>1 then
   for _,cone in ipairs(obstacles) do if segmentDistance(old,step,cone)<2 then
    run.velocity=-run.velocity*.25;blocked=true
    if now>(run.nextConePenalty or 0) then run.deadline-=3;run.nextConePenalty=now+2;run.notify("Cone clipped! -3 seconds. Use softer shots around it.") end
    break
   end end
  end
  if nextPosition.X<592 or nextPosition.X>704 or nextPosition.Z<502 or nextPosition.Z>587 then
   run.position=origin;run.velocity=Vector3.zero;run.notify("Out of bounds! Ball reset; your completed gates remain, but the timer keeps running.")
  elseif not blocked then
   run.position=nextPosition;run.velocity*=math.exp(-1.05*dt)
   local radius=run.phase=="Dribble" and 4.5 or run.stage>=4 and 3.5 or 4.5
   if run.velocity.Magnitude>1 and segmentDistance(old,step,goal)<radius then
    run.stage+=1
    if run.phase=="Dribble" and run.stage>#gates then
     run.cones:ClearAllChildren();setPhase(run,"Targets",120)
     run.notify("Checkpoint! Five shots in 120 seconds. The last two targets move—and watch out for my terrible assist!")
    elseif run.phase=="Targets" and run.stage>#goals then
     local complete=run.complete;Soccer.Cancel(player);complete();continue
    else
     run.velocity*=.3
     if run.phase=="Targets" and run.stage==4 then run.velocity+=V(6,0,0);run.notify("Nick: My assist drifts RIGHT! Compensate before the moving target.")
     else run.notify((run.phase=="Dribble" and "Gate " or "Target ")..(run.stage-1).." cleared · "..math.ceil(run.deadline-now).."s left") end
    end
   end
  end
  run.ball.CFrame=CFrame.new(run.position)*CFrame.Angles(0,0,now*run.velocity.Magnitude*.25)
 end
end)
return Soccer
