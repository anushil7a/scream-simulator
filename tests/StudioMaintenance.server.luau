-- Disposable Studio fixture: real 45-second quiet interval and actual worker
-- path/work loop, with scripted damage and a player occupancy check.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio())
 task.wait(3)
 local worker
 for _,bot in ipairs(World.Bots) do if bot.role=="Sanitation" and bot.job then worker=bot;break end end
 local checks=0;local sawRepair=false;local elapsed=0
 local function check(value,message) assert(value,message);checks+=1 end
 local ok,err=xpcall(function()
  assert(worker)
  World.Talk(worker);worker.socialUntil=os.clock()+52
  worker.model:PivotTo(CFrame.new(262,4,403));worker.humanoid:MoveTo(worker.root.Position)
  local target,object,distance
  for model,o in pairs(Destruction.objects) do
   local d=(o.box.Position-Vector3.new(262,2,412)).Magnitude
   if o.kind=="Bin" and (not distance or d<distance) then target,object,distance=model,o,d end
  end
  assert(target and distance<5)
  local result=Destruction.Damage(target,1,48);check(result and result.destroyed,"Bin not destroyed")
  local started=os.clock()
  check(Destruction.MaintenanceTarget(worker.root.Position,80)==nil,"Worker repaired fresh damage")
  task.wait(45.2)
  local station=Destruction.MaintenanceTarget(worker.root.Position,80)
  check(station and station.maintenanceModel==target,"Mature damage not offered")
  check(not Destruction.FinishMaintenance(station,Vector3.new(0,4,0)),"Remote repair accepted")
  local validVersion=station.maintenanceVersion;station.maintenanceVersion-=1
  check(not Destruction.FinishMaintenance(station,station.position),"Stale work restored newer damage")
  station.maintenanceVersion=validVersion
  local player=game.Players:GetPlayers()[1];local root=player and player.Character and player.Character:FindFirstChild("HumanoidRootPart")
  assert(root);local saved=root.CFrame
  root.CFrame=CFrame.new(object.box.Position+Vector3.new(0,2,0));task.wait(.1)
  check(not Destruction.FinishMaintenance(station,station.position),"Restored through player")
  root.CFrame=saved
  worker.socialUntil=0;worker.nextMaintenance=0
  local deadline=os.clock()+35
  repeat
   if not sawRepair and worker.model:GetAttribute("Repairing")==true then
    sawRepair=true
    task.wait(.1) -- allow the shared tool visibility heartbeat to run
    check(worker.model.RepairHammer.Transparency==0 and worker.model.BroomHead.Transparency==1,"Maintenance tools did not switch")
   end
   if sawRepair and target:GetAttribute("ObjectHealth")==target:GetAttribute("ObjectMaxHealth") then break end
   task.wait(.1)
  until os.clock()>deadline
  elapsed=os.clock()-started
  check(sawRepair,"Worker never began maintenance")
  check(target:GetAttribute("ObjectHealth")==target:GetAttribute("ObjectMaxHealth"),"Worker failed to restore bin")
  check(elapsed<120,"Only automatic timer repaired object")
  check(target:GetAttribute("RepairAt")==0 and not target:GetAttribute("Destroyed"),"Repair state remained stale")
  for part,original in pairs(object.parts) do
   check(part.CanCollide==original.collide and part.Transparency==original.transparency,"Restored part differs from original")
  end
 end,debug.traceback)
 workspace:SetAttribute("MaintenanceResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,sawRepair=sawRepair,elapsed=elapsed,error=not ok and tostring(err) or nil}))
 print("Maintenance regression",ok,checks,elapsed,err)
end)
