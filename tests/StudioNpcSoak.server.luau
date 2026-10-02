-- Append to ordinary Bootstrap in a disposable local place. Leaves Play running.
-- One-client NPC lifecycle observation, not a multiplayer/device performance gate.
task.spawn(function()
 assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0,"Disposable Studio only")
 local runId=script:GetAttribute("NpcSoakRunId") or "CityNpcSoak-20261002-7d54864"
 local duration=script:GetAttribute("NpcSoakDuration") or 1800
 local started=os.clock();local previous={};local samples={}
 workspace:SetAttribute("NpcSoakRunId",runId);workspace:SetAttribute("NpcSoakState","running")
 local ok,message=xpcall(function()
  while os.clock()-started<=duration do
   local moving,working,seated,alive,high,stranded=0,0,0,0,0,0
   for _,bot in World.Bots do
    if bot.alive and bot.root.Parent then
     alive+=1
     if previous[bot] and (bot.root.Position-previous[bot]).Magnitude>2 then moving+=1 end
     previous[bot]=bot.root.Position
     if bot.model:GetAttribute("Working")==true then working+=1 end
     if bot.humanoid.SeatPart then seated+=1;if not bot.model:GetAttribute("Resting") then stranded+=1 end end
     if bot.root.Position.Y>20 then high+=1 end
    end
   end
   local sample={elapsed=math.floor(os.clock()-started),luaKB=math.floor(gcinfo()),worldInstances=#workspace.ScreamSimulatorWorld:GetDescendants(),alive=alive,movedSinceLast=moving,working=working,seated=seated,strandedSeats=stranded,above20Studs=high}
   table.insert(samples,sample)
   workspace:SetAttribute("NpcSoakLatest",game:GetService("HttpService"):JSONEncode(sample))
   workspace:SetAttribute("NpcSoakSamples",game:GetService("HttpService"):JSONEncode(samples))
   task.wait(30)
  end
 end,debug.traceback)
 workspace:SetAttribute("NpcSoakState",ok and "complete" or "failed")
 workspace:SetAttribute("NpcSoakError",ok and "" or tostring(message))
 print("NPC soak",runId,ok,#samples,message)
end)
