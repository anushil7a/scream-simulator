-- Supply the actual Soccer service from ordinary Bootstrap in disposable Play.
-- Synthetic aim/actor positioning at >=4-second shot intervals, not live mic/input proof.
return function(Soccer,livePlayer,isComplete)
 local V=Vector3.new
 local actor=livePlayer and livePlayer.Character or Instance.new("Model")
 local original=livePlayer and actor:GetPivot()
 local root
 if livePlayer then root=actor.HumanoidRootPart else
  actor.Name="SoccerCompletionActor";actor.Parent=workspace
  root=Instance.new("Part");root.Name="HumanoidRootPart";root.Anchored=true;root.CanCollide=false;root.Position=V(647,4,547);root.Parent=actor
  local humanoid=Instance.new("Humanoid");humanoid.Parent=actor
 end
 local player=livePlayer or {UserId=-903,DisplayName="Completion audit",Character=actor}
 local attemptName="SoccerAttempt_"..player.UserId
 local completed,failed,shots=0,0,0
 local messages={}
 local detours={{V(615,2.2,530)},{V(653,2.2,530)},{V(633,2.2,555)},{V(676,2.2,578)}}
 local phase,stage,detourIndex=nil,nil,1
 local ok,err=xpcall(function()
  if not livePlayer then Soccer.Start(player,function(message) table.insert(messages,message);workspace:SetAttribute("SoccerCompletionProgress",message) end,function() completed+=1 end,function() failed+=1 end) end
  for i,point in ipairs({V(590,4,460),V(552,4,563),V(683,4,482)}) do actor:PivotTo(CFrame.new(point));assert(Soccer.Collect(player,i),"Collection failed") end
  actor:PivotTo(CFrame.new(647,4,547))
  local deadline=os.clock()+200
  while Soccer.Status(player) and os.clock()<deadline do
   local status=Soccer.Status(player)
   local model=workspace.ScreamSimulatorWorld:FindFirstChild(attemptName)
   assert(model,"Active attempt missing")
   local currentStage=tonumber(status.detail:match("(%d+)/"))+1
   if phase~=status.phase or stage~=currentStage then phase=status.phase;stage=currentStage;detourIndex=1 end
   local ball=model.ChallengeBall.Position
   local destination=model.Target.Position
   if phase=="Dribble" then
    local route=detours[stage]
    while route and route[detourIndex] and (route[detourIndex]-ball).Magnitude<6 do detourIndex+=1 end
    destination=route and route[detourIndex] or destination
   end
   local delta=destination-ball
   if delta.Magnitude>.01 then
    local direction=delta.Unit
    local power=math.clamp((delta.Magnitude*1.07-12)/34,.08,1)
    Soccer.Hit(player,ball-direction*5,direction,30,4,power);shots+=1
   end
   task.wait(4.05)
  end
  if livePlayer then completed=isComplete() and 1 or 0 end
  assert(completed==1 and failed==0,"Course did not complete: completed="..completed..", failed="..failed)
  assert(Soccer.Status(player)==nil and not workspace.ScreamSimulatorWorld:FindFirstChild(attemptName),"Completed attempt leaked")
  Soccer.Hit(player,V(615,2.2,550),V(1,0,0),30,4,1);task.wait(.2)
  assert(completed==1,"Completion repeated")
 end,debug.traceback)
 Soccer.Cancel(player);if livePlayer then actor:PivotTo(original);root.AssemblyLinearVelocity=Vector3.zero else actor:Destroy() end
 return {passed=ok,error=not ok and tostring(err) or nil,completed=completed,failed=failed,shots=shots,messages=messages}
end
