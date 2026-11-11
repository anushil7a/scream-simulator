-- Appended to guarded production Bootstrap. Synthetic server helper inputs only.
-- No real microphone, RemoteEvent, human traversal, save or publication validation.
task.spawn(function()
 local count=0;local paths={};local started=os.clock();local finished=false
 local player,session,character,root,old
 local activePaths={}
 local sessionFields={"data","activeQuest","sustained","micReady","protectedUntil","dodgingUntil","knockedUntil","collected","carrying","deliveryStop","raceStart","questDeadline"}
 local function cleanup()
  local failures={}
  local function safely(label,fn)local ok,err=pcall(fn);if not ok then table.insert(failures,label..": "..tostring(err))end end
  for path in pairs(activePaths)do safely("Path cleanup",function()path:Destroy()end);activePaths[path]=nil end
  if session and old then
   safely("Cancel synthetic beam",function()cancelSustained(player,session,os.clock())end)
   safely("Restore session",function()for _,key in ipairs(sessionFields)do session[key]=old.session[key]end end)
   safely("Restore character position",function()if character and character.Parent then character:PivotTo(old.frame)end end)
   safely("Restore character anchoring",function()if root and root.Parent then root.Anchored=old.anchor end end)
  end
  for _,bot in ipairs(World.Bots)do if bot.training then safely("Restore trainer",function()restoreBot(bot)end)end end
  return #failures==0,table.concat(failures,"; ")
 end
 local function check(ok,message)assert(ok,message);count+=1 end
 local function report(ok,err)
  if finished then return end;finished=true
  local result=game:GetService("HttpService"):JSONEncode({passed=ok,checks=count,paths=paths,seconds=os.clock()-started,error=err,
   limits="Synthetic server-helper input; native PathfindingService and geometry only. Not real microphone, RemoteEvent, physical traversal, live saves or multiplayer."})
  workspace:SetAttribute("CompactCityResult",result);print("NATIVE_COMPACT_CITY_RESULT",result)
 end
 local worker=coroutine.running()
 task.delay(210,function()
  if not finished then
   task.cancel(worker) -- stop mutation before restoring shared fixture state
   local clean,detail=cleanup()
   report(false,"Fixture exceeded 210-second bound"..(clean and "" or "; cleanup failed: "..detail))
  end
 end)
 local ok,err=xpcall(function()
  check(game:GetService("RunService"):IsStudio() and game.PlaceId==0 and localFixture,"Unsafe review environment")
  local deadline=os.clock()+40
  repeat task.wait(.1);player=Players:GetPlayers()[1];session=player and sessions[player];if player then character,root=parts(player)end until session and root or os.clock()>deadline
  check(session and root,"Player/session did not initialize")
  check(not session.canSave,"Review session allows persistence")
  local Layout=require(ReplicatedStorage.Shared.CompactLayout)
  local world=workspace:WaitForChild("ScreamSimulatorWorld")
  old={session={},frame=character:GetPivot(),anchor=root.Anchored}
  for _,key in ipairs(sessionFields)do old.session[key]=session[key]end
  root.Anchored=true;session.micReady=true;session.protectedUntil=0;session.dodgingUntil=0;session.knockedUntil=0
  session.data=Profiles.Default();session.data.level=1
  local excluded={character};for _,bot in ipairs(World.Bots)do table.insert(excluded,bot.model)end
  local ray=RaycastParams.new();ray.FilterType=Enum.RaycastFilterType.Exclude;ray.FilterDescendantsInstances=excluded;ray.RespectCanCollide=true
  local pathService=game:GetService("PathfindingService")
  local spawn=Layout.Spawn;local approachByMarker={}
  local function reachable(name,target,radius,npc)
   check(os.clock()-started<180,"Pathfinding budget exhausted")
   local offsets=radius>0 and {Vector3.zero,Vector3.new(0,0,6),Vector3.new(0,0,-6),Vector3.new(6,0,0),Vector3.new(-6,0,0)} or {Vector3.zero}
   for _,offset in ipairs(offsets)do
    local candidate=target+offset
    local floor=workspace:Raycast(candidate+Vector3.new(0,15,0),Vector3.new(0,-40,0),ray)
    if floor then
     local goal=floor.Position+Vector3.new(0,3,0)
     local delta=goal-target
     -- Exact stations cannot silently become roof destinations. NPC roots use
     -- a tighter vertical tolerance; player markers can sit at floor/ball height.
     local exact=Vector3.new(delta.X,0,delta.Z).Magnitude<=.25 and math.abs(delta.Y)<=(npc and 1 or 3)
     if (radius==0 and exact) or (radius>0 and delta.Magnitude<=radius) then
      local path=pathService:CreatePath({AgentRadius=2,AgentHeight=5,AgentCanJump=not npc,AgentCanClimb=false,WaypointSpacing=npc and 5 or 4,Costs=npc and {Fountain=math.huge,Asphalt=8} or nil})
      activePaths[path]=true
      local computed,waypoints=pcall(function()
       path:ComputeAsync(spawn,goal)
       if path.Status==Enum.PathStatus.Success then return path:GetWaypoints() end
      end)
      path:Destroy();activePaths[path]=nil -- timeout cleanup owns paths still computing
      if computed and waypoints then
       check(#waypoints>=2,"Empty successful path")
       paths[#paths+1]={name=name,waypoints=#waypoints,agentCanJump=not npc,start={spawn.X,spawn.Y,spawn.Z},goal={goal.X,goal.Y,goal.Z}};return goal
      end
     end
    end
   end
   error("No native path from spawn to "..name)
  end
  local prompts={}
  for _,item in ipairs(world:GetDescendants())do
   if item:IsA("ProximityPrompt") and item.Parent:GetAttribute("QuestAction") then
    prompts[item.Parent.Name]=item;approachByMarker[item.Parent.Name]=reachable(item.Parent.Name,item.Parent.Position,item.MaxActivationDistance)
   end
  end
  for _,bot in ipairs(World.Bots)do
   if bot.training then reachable("Trainer:"..bot.training.id,bot.start,10,true)
   elseif bot.job then for i,station in ipairs(bot.job.stations)do reachable("Job:"..bot.name..":"..i,station.position,0,true)end
   else reachable("Resident:"..bot.id,bot.start,0,true)end
  end
  for i,position in ipairs(Layout.Soccer.lost)do reachable("LostBall:"..i,position,8)end
  local target=assert(world:FindFirstChild("PracticeTarget",true));local line=assert(target.Parent:FindFirstChild("StandLine"))
  reachable("PracticeStand",line.Position,0)
  reachable("ArenaEntrance",assert(world:FindFirstChild("ArenaWayfinding",true)).Position,0)
  reachable("SoccerOrigin",Layout.Soccer.origin,0)
  for i,pos in ipairs(Layout.Soccer.gates)do reachable("SoccerGate:"..i,pos,0)end
  for i,pos in ipairs(Layout.Soccer.goals)do reachable("SoccerGoal:"..i,pos,0)end
  reachable("VolleyServe",Layout.Volley.serve,0)
  reachable("VolleyReturn",Vector3.new(Layout.Volley.center.X,3,Layout.Volley.netZ+16),0)

  check(target:GetAttribute("MicPracticeTarget")==true and target.CanCollide,"Practice target cannot be hit by actual beam ray policy")
  local Gate=require(ReplicatedStorage.Shared.VoiceActivation)
  for _,power in ipairs({Gate.OnPower,Gate.OffPower+.001})do
   session.data.achievements.FirstBeam=nil;session.sustained=sustained.New()
   character:PivotTo(CFrame.lookAt(line.Position+Vector3.new(0,3,0),target.Position))
   local now=os.clock()
   check(sustained.Begin(session.sustained,now,{sequence=1,power=power,aim=target.Position},sustainedContext(player,session,now)),"Synthetic practice begin rejected")
   stepSustained(player,session,now+.2)
   check(session.data.achievements.FirstBeam==true,"Actual practice ray missed at tested low power")
   cancelSustained(player,session,now+.21)
  end
  local function activate(id)
   session.activeQuest=id;session.data.availableQuests[id]=true;session.data.quests[id]={progress=0,claimed=false};session.collected={}
   session.carrying=false;session.deliveryStop=nil;session.raceStart=nil;session.questDeadline=nil
  end
  local function interact(name)
   local prompt=assert(prompts[name],"Missing quest marker:"..name)
   character:PivotTo(CFrame.new(approachByMarker[name]));interactQuest(player,prompt)
  end
  for _,q in ipairs({{id="garden",names={"Flowerbed228","Flowerbed250","Flowerbed272"},goal=3},{id="beach",names={"Bottle1","Bottle2","Bottle3","Bottle4","Bottle5","Bottle6"},goal=6}})do
   activate(q.id)
   for _,name in ipairs(q.names)do
    local before=session.data.quests[q.id].progress;interact(name);check(session.data.quests[q.id].progress==before+1,"Quest marker did not progress:"..name)
    interact(name);check(session.data.quests[q.id].progress==before+1,"Duplicate quest marker progressed:"..name)
   end
   check(session.data.quests[q.id].progress==q.goal,"Quest goal mismatch")
  end
  activate("delivery");interact("CoffeeOrder");check(session.carrying and session.deliveryStop~=nil,"Pickup failed")
  local destination,deadline=session.deliveryStop,session.questDeadline;interact("CoffeeOrder")
  check(session.deliveryStop==destination and session.questDeadline==deadline,"Duplicate pickup rerolled order")
  for _,stop in ipairs(Config.DeliveryStops)do if stop.id~=destination then interact(stop.id);check(session.carrying and session.data.quests.delivery.progress==0,"Wrong delivery accepted");break end end
  interact(destination);check(session.data.quests.delivery.progress==1 and not session.carrying,"Assigned delivery failed")
  interact(destination);check(session.data.quests.delivery.progress==1,"Duplicate delivery progressed")
  activate("sprint");interact("BoardwalkStart");local race=session.raceStart;check(race~=nil,"Race start failed")
  interact("BoardwalkStart");check(session.raceStart==race,"Duplicate race start reset timer")
  interact("PierFinish");check(session.data.quests.sprint.progress==0,"Race accepted impossible immediate finish")
  session.raceStart=os.clock()-3.1;session.questDeadline=os.clock()+20 -- synthetic elapsed time, not traversal proof
  interact("PierFinish");check(session.data.quests.sprint.progress==1,"Valid synthetic race finish failed")
  interact("PierFinish");check(session.data.quests.sprint.progress==1,"Duplicate race finish progressed")
  local trainer
  for _,bot in ipairs(World.Bots)do if bot.training then
   check(not Config.InArena(bot.start),"Trainer home in PvP");trainer=trainer or bot
  end end
  check(trainer~=nil,"No trainers")
  trainer.root.Anchored=true;trainer.model:PivotTo(CFrame.new(trainer.start+Vector3.new(18,0,0)))
  session.data.level=100
  local function resolves(offset)
   character:PivotTo(CFrame.new(trainer.start+Vector3.new(offset,0,0)))
   local context=sustainedContext(player,session,os.clock());local stats=VoiceCombat.Stats(100,1,false)
   local _,details=resolveSustained(context,(trainer.root.Position-context.origin).Unit,stats,os.clock())
   return details["bot:"..trainer.id]~=nil
  end
  check(resolves(31.9),"Inside home pad cannot hit roaming trainer");check(not resolves(32.1),"Outside home pad hit roaming trainer")
  trainer.health=trainer.maxHealth-10;trainer.credit={fixture={damage=10}};trainer.lastTrainingHit=os.clock()-26
  stepTraining(os.clock());check(trainer.health==trainer.maxHealth and next(trainer.credit)==nil and not trainer.root.Anchored,"Quiet trainer reset failed")
  check(not session.canSave and workspace:GetAttribute("CompactProfileCalls")==0,"Persistence path reached")
 end,debug.traceback)
 local clean,detail=cleanup()
 if not clean then ok=false;err=(err and tostring(err).."; " or "").."cleanup failed: "..detail end
 report(ok,not ok and tostring(err) or nil)
end)
