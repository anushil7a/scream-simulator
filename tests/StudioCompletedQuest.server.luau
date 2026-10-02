-- Append to Bootstrap in a disposable Play session. Calls the actual prompt handler.
-- Synthetic session setup/positioning; not physical prompt input or race timing proof.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio(),"Local Studio only")
 local p
 repeat task.wait(.1);p=game.Players:GetPlayers()[1] until p and sessions[p] and parts(p)
 local s=sessions[p];assert(not s.canSave,"Temporary profile required")
 local checks=0
 local function check(v,msg) assert(v,msg);checks+=1 end
 local function prompt(kind)
  for _,o in workspace.ScreamSimulatorWorld:GetDescendants() do if o:IsA("ProximityPrompt") and o.Parent:GetAttribute("QuestAction")==kind then return o end end
  error("Missing prompt "..kind)
 end
 local function trigger(kind)
  local obj=prompt(kind);p.Character:PivotTo(CFrame.new(obj.Parent.Position+Vector3.new(0,3,0)));interactQuest(p,obj)
 end
 local ok,err=xpcall(function()
  for _,item in ipairs({{"delivery","Pickup"},{"sprint","RaceStart"},{"garden","Garden"},{"beach","Litter"}}) do
   local q=Config.GetQuest(item[1]);s.activeQuest=q.id;s.data.quests[q.id]={progress=q.goal,claimed=false};s.collected={};s.questDeadline=nil;s.raceStart=nil;s.carrying=false
   trigger(item[2])
   check(s.questDeadline==nil and s.raceStart==nil and not s.carrying,"Completed task restarted transient state")
   check(next(s.collected)==nil and s.data.quests[q.id].progress==q.goal,"Completed task consumed another object")
  end
  s.activeQuest="sprint";s.data.quests.sprint={progress=0,claimed=false};trigger("RaceStart")
  check(s.questDeadline and s.raceStart,"Unfinished race starts normally")
  s.raceStart=os.clock()-4;trigger("RaceFinish")
  check(s.data.quests.sprint.progress==1 and s.questDeadline==nil and s.raceStart==nil,"Race completes without stale timer")
  s.activeQuest="delivery";s.data.quests.delivery={progress=0,claimed=false};trigger("Pickup")
  check(s.carrying and s.questDeadline,"Unfinished delivery starts normally")
  trigger("Dropoff")
  check(s.data.quests.delivery.progress==1 and not s.carrying and s.questDeadline==nil,"Delivery completes without stale timer")
 end,debug.traceback)
 stopQuest(p);s.data.quests={};state(p)
 workspace:SetAttribute("CompletedQuestResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
 print("Completed quest regression",ok,checks,err)
end)
