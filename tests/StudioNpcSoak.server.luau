-- Append to ordinary Bootstrap in a disposable local place. Leaves Play running.
-- One-client NPC lifecycle observation, not a multiplayer/device performance gate.
task.spawn(function()
 assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0,"Disposable Studio only")
 local runId=script:GetAttribute("NpcSoakRunId") or "CityNpcSoak-local"
 local duration=script:GetAttribute("NpcSoakDuration") or 1800
 local started=os.clock();local nextSample=0;local previous={};local motion={};local mismatchSince={};local samples={}
 local worstSeatMismatch=0
 workspace:SetAttribute("NpcSoakRunId",runId);workspace:SetAttribute("NpcSoakState","running")
 workspace:SetAttribute("NpcSoakStarted",workspace:GetServerTimeNow())
 local ok,message=xpcall(function()
  while true do
   local now=os.clock();local elapsed=now-started
   local moving,working,seated,alive,high,stranded=0,0,0,0,0,0
   local persistentSeats,walkingStalls={},{}
   local capture=elapsed>=nextSample or elapsed>=duration
   for _,bot in World.Bots do
    if bot.alive and bot.root.Parent then
     alive+=1
     local position=bot.root.Position
     local last=motion[bot]
     if not last or (position-last.position).Magnitude>2 then motion[bot]={position=position,time=now};last=motion[bot] end
     if capture then
      if previous[bot] and (position-previous[bot]).Magnitude>2 then moving+=1 end
      previous[bot]=position
     end
     if bot.model:GetAttribute("Working")==true then working+=1 end
     if bot.humanoid.SeatPart then
      seated+=1
      if not bot.model:GetAttribute("Resting") then
       stranded+=1;mismatchSince[bot]=mismatchSince[bot] or now
       local age=now-mismatchSince[bot];worstSeatMismatch=math.max(worstSeatMismatch,age)
       if age>3 then table.insert(persistentSeats,{id=bot.id,seconds=math.floor(age)}) end
      else mismatchSince[bot]=nil end
     else mismatchSince[bot]=nil end
     if not bot.humanoid.SeatPart and not bot.working and now-(last.time or now)>30
      and (bot.humanoid.WalkToPoint-position).Magnitude>3 and (bot.socialUntil or 0)<=now and not bot.watchingPerformer then
      table.insert(walkingStalls,{id=bot.id,seconds=math.floor(now-last.time),activity=bot.model:GetAttribute("Activity")})
     end
     if position.Y>20 then high+=1 end
    else mismatchSince[bot]=nil end
   end
   if capture then
    local sample={elapsed=math.floor(elapsed),luaKB=math.floor(gcinfo()),worldInstances=#workspace.ScreamSimulatorWorld:GetDescendants(),alive=alive,movedSinceLast=moving,working=working,seated=seated,strandedSeats=stranded,above20Studs=high,persistentSeatMismatches=persistentSeats,walkingStalls=walkingStalls,worstSeatMismatchSeconds=math.floor(worstSeatMismatch)}
    table.insert(samples,sample)
    workspace:SetAttribute("NpcSoakLatest",game:GetService("HttpService"):JSONEncode(sample))
    workspace:SetAttribute("NpcSoakSamples",game:GetService("HttpService"):JSONEncode(samples))
    nextSample=elapsed+30
   end
   if elapsed>=duration then break end
   task.wait(1)
  end
 end,debug.traceback)
 workspace:SetAttribute("NpcSoakState",ok and "complete" or "failed")
 workspace:SetAttribute("NpcSoakError",ok and "" or tostring(message))
 print("NPC soak",runId,ok,#samples,message)
end)
