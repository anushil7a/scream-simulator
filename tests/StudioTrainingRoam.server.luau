-- Guarded local-only Bootstrap appendix. Real humanoid/world physics; synthetic
-- combat context and helper calls, not microphone/RemoteEvent/network testing.
task.spawn(function()
 local count=0;local function check(value,message)assert(value,message);count+=1 end
 local trainers={};for _,bot in ipairs(World.Bots) do if bot.training then table.insert(trainers,bot) end end
 local sampled={};local p,s,c,r,h,old
 local ok,err=xpcall(function()
  check(localFixture,"Refuse persistent training test")
  check(#trainers==3,"Expected three training tiers")
  for _,bot in ipairs(trainers) do
   restoreBot(bot)
   sampled[bot.id]={start=bot.root.Position,maxDistance=0,maxTravel=0,samples=0}
   check(not bot.root.Anchored and bot.humanoid.WalkSpeed==TrainingRules.RoamSpeed,"Trainer cannot walk")
   check(bot.root:GetNetworkOwner()==nil,"Trainer is not server-owned")
  end
  local deadline=os.clock()+12
  repeat
   RunService.Heartbeat:Wait()
   for _,bot in ipairs(trainers) do
    local row=sampled[bot.id];local d=bot.root.Position-bot.start
    row.maxDistance=math.max(row.maxDistance,Vector3.new(d.X,0,d.Z).Magnitude)
    local moved=bot.root.Position-row.start
    row.maxTravel=math.max(row.maxTravel,Vector3.new(moved.X,0,moved.Z).Magnitude);row.samples+=1
   end
  until os.clock()>=deadline
  for _,bot in ipairs(trainers) do
   local row=sampled[bot.id]
   check(row.maxTravel>6,"Trainer did not physically roam: "..bot.id)
   check(row.maxDistance<=TrainingRules.RoamLeash+1,"Trainer escaped pad during idle sample")
  end
  p=Players:GetPlayers()[1];s=p and sessions[p]
  if p then c,r,h=parts(p) end
  check(s and not s.canSave and c and r and h,"Local synthetic player unavailable")
  old={frame=c:GetPivot(),anchor=r.Anchored,mic=s.micReady,protected=s.protectedUntil,knock=s.knockedUntil,level=s.data.level}
  s.micReady=true;s.protectedUntil=0;s.knockedUntil=0;r.Anchored=true
  local bot=trainers[1]
  c:PivotTo(CFrame.new(bot.start+Vector3.new(0,0,15)))
  deadline=os.clock()+7
  repeat RunService.Heartbeat:Wait() until (bot.trainingDestination and Vector3.new(bot.root.AssemblyLinearVelocity.X,0,bot.root.AssemblyLinearVelocity.Z).Magnitude>1) or os.clock()>deadline
  check(bot.trainingDestination~=nil and Vector3.new(bot.root.AssemblyLinearVelocity.X,0,bot.root.AssemblyLinearVelocity.Z).Magnitude>1,"No active walk before windup")
  bot.trainingTarget=p;bot.lastTrainingHit=os.clock();bot.strike={at=os.clock()+30,position=bot.start}
  task.wait(.6);check(bot.strike~=nil and s.micReady,"Synthetic strike was cancelled before measurement");local stopped=bot.root.Position;task.wait(.8)
  check(bot.strike~=nil,"Synthetic strike did not remain active")
  check((bot.root.Position-stopped).Magnitude<1,"Trainer kept walking during windup")
  bot.strike=nil;bot.socialUntil=os.clock()+30;task.wait(.6);stopped=bot.root.Position;task.wait(.8)
  check((bot.root.Position-stopped).Magnitude<1,"Trainer kept walking during conversation")
  bot.socialUntil=0
  bot.health=bot.maxHealth-10;bot.credit={fixture={damage=10}}
  local credit=bot.credit;bot.model:PivotTo(CFrame.new(bot.start+Vector3.new(26,0,0)))
  World.StepTrainingRoam(bot,os.clock())
  check((bot.root.Position-bot.start).Magnitude<.01,"Displaced trainer did not recover home")
  check(bot.health==bot.maxHealth-10 and bot.credit==credit,"Leash recovery changed health or credit")
  check(bot.lastGrounded==bot.start and bot.airSince==nil,"Leash retained stale grounding")
  restoreBot(bot);check(not bot.root.Anchored and bot.health==bot.maxHealth,"Full reset reanchored trainer")
  bot.health=0;knockOutBot(bot);World.UpdateBot(bot)
  check(not bot.alive and bot.root.Anchored and bot.root.Position.Y< -90,"KO did not hide trainer")
  deadline=os.clock()+Config.BotRespawnSeconds+3
  repeat task.wait(.1) until bot.alive or os.clock()>deadline
  check(bot.alive and bot.health==bot.maxHealth and not bot.root.Anchored,"Delayed respawn failed")
  local revived=bot.root.Position;task.wait(3)
  local afterRevive=bot.root.Position-revived
  check(Vector3.new(afterRevive.X,0,afterRevive.Z).Magnitude>3,"Respawned trainer did not resume walking")
  -- Actual sustained resolver at the original pad edge, even with trainer moved.
  s.data.level=100
  bot.strike={at=os.clock()+30,position=bot.start};bot.model:PivotTo(CFrame.new(bot.start+Vector3.new(18,0,0)))
  local function resolved(offset)
   c:PivotTo(CFrame.new(bot.start+Vector3.new(offset,0,0)))
   local ctx=sustainedContext(p,s,os.clock());local stats=VoiceCombat.Stats(100,1,false)
   local _,details=resolveSustained(ctx,(bot.root.Position-ctx.origin).Unit,stats,os.clock())
   return details["bot:"..bot.id]~=nil
  end
  check(resolved(31.9),"Just-inside original pad cannot hit roaming trainer")
  check(not resolved(32.1),"Just-outside original pad hit nearby roaming trainer")
 end,debug.traceback)
 if old then c:PivotTo(old.frame);r.Anchored=old.anchor;s.micReady=old.mic;s.protectedUntil=old.protected;s.knockedUntil=old.knock;s.data.level=old.level end
 for _,bot in ipairs(trainers) do restoreBot(bot);bot.lastTrainingHit=nil;bot.nextStrike=nil end
 for _,row in pairs(sampled) do row.start={row.start.X,row.start.Y,row.start.Z} end
 local result=game:GetService("HttpService"):JSONEncode({passed=ok,checks=count,samples=sampled,error=not ok and tostring(err) or nil})
 workspace:SetAttribute("TrainingRoamResult",result);print("NATIVE_TRAINING_ROAM_RESULT",result)
end)
