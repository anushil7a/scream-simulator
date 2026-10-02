-- Append to Bootstrap in disposable PlaceId-zero Studio; no duration overrides.
-- Actual service/timers on isolated tagged models, not combat or late-join coverage.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio(),"Local Studio only")
 local specs=require(game.ReplicatedStorage.Shared.DestructionRules).Types
 local collection=game:GetService("CollectionService")
 local folder=Instance.new("Folder");folder.Name="RepairTimerFixture";folder.Parent=workspace.ScreamSimulatorWorld
 local fixtures={};local observations={};local checks=0;local started=os.clock()
 local function check(v,message) assert(v,message);checks+=1 end
 local function publish(state,err)
  workspace:SetAttribute("RepairTimerResult",game:GetService("HttpService"):JSONEncode({state=state,elapsed=math.floor(os.clock()-started),checks=checks,observations=observations,error=err}))
 end
 local blocker=Instance.new("Model");blocker.Name="FixtureResident";blocker.Parent=folder;collection:AddTag(blocker,"CityResident")
 local torso=Instance.new("Part");torso.Anchored=true;torso.CanQuery=false;torso.Size=Vector3.new(2,2,1);torso.Parent=blocker
 local ok,err=xpcall(function()
  local index=0
  for kind,spec in specs do for _,destroy in ipairs({false,true}) do
   index+=1
   local model=Instance.new("Model");model.Name=kind..(destroy and "Destroyed" or "Partial");model:SetAttribute("DestructibleType",kind);model.Parent=folder
   local body=Instance.new("Part");body.Anchored=true;body.Size=Vector3.new(4,2,2);body.CFrame=CFrame.new(index*12,1000,0);body.Color=Color3.fromRGB(150,190,130);body.Parent=model
   local prompt=Instance.new("ProximityPrompt");prompt.Parent=body
   collection:AddTag(model,"CityDestructible");Destruction.Register(model)
   if destroy then
    while model:GetAttribute("ObjectHealth")>0 do Destruction.Damage(body,300,math.min(48,model:GetAttribute("ObjectHealth"))) end
   else Destruction.Damage(body,300,24) end
   local record={model=model,body=body,prompt=prompt,kind=kind,destroy=destroy,deadline=os.clock()+spec.repair,health=model:GetAttribute("ObjectHealth"),done=false}
   table.insert(fixtures,record)
   check(math.abs(model:GetAttribute("RepairAt")-workspace:GetServerTimeNow()-spec.repair)<1,"Incorrect repair deadline "..model.Name)
   if kind=="Bench" and destroy then record.blocked=true;torso.CFrame=body.CFrame end
  end end
  publish("running")
  local refreshed=false;local released=false
  while os.clock()-started<330 do
   local elapsed=os.clock()-started
   if elapsed>=10 and not refreshed then
    refreshed=true
    for _,r in fixtures do if r.kind=="Bench" and not r.destroy then Destruction.Damage(r.body,300,1);r.health-=1;r.deadline=os.clock()+specs.Bench.repair end end
   end
   if elapsed>=123 and not released then
    for _,r in fixtures do if r.blocked then check(r.model:GetAttribute("Destroyed"),"Occupied object repaired early");check(r.model:GetAttribute("RepairAt")>workspace:GetServerTimeNow(),"Occupied repair not deferred") end end
    torso.Position+=Vector3.new(0,30,0);released=true
   end
   local allDone=true
   for _,r in fixtures do if not r.done then
    allDone=false
    if os.clock()<r.deadline-.2 then assert(r.model:GetAttribute("ObjectHealth")==r.health,"Repaired before latest deadline: "..r.model.Name)
    elseif r.model:GetAttribute("ObjectHealth")==specs[r.kind].health then
     check(not r.model:GetAttribute("Destroyed") and r.model:GetAttribute("DamageStage")==0,"Repair state incorrect")
     check(r.body.CanCollide and r.body.CanQuery and r.body.Transparency==0 and r.prompt.Enabled,"Repair properties incorrect")
     check(r.model:GetAttribute("RepairAt")==0 and r.body.Color==Color3.fromRGB(150,190,130),"Repair metadata/color incorrect")
     observations[r.model.Name]=math.floor(elapsed);r.done=true
    elseif os.clock()>r.deadline+(r.blocked and 10 or 5) then error("Repair overdue: "..r.model.Name) end
   end end
   publish("running")
   if allDone then break end
   task.wait(.5)
  end
  for _,r in fixtures do check(r.done,"Repair never completed: "..r.model.Name) end
 end,debug.traceback)
 folder:Destroy();publish(ok and "complete" or "failed",not ok and tostring(err) or nil)
 print("Real repair timers",ok,checks,err)
end)
