-- Append to Bootstrap in an unpublished Studio copy. Calls the actual quest
-- handler with controlled positions; not human traversal or real prompt input.
task.spawn(function()
 assert(game.PlaceId==0 and RunService:IsStudio())
 local p
 repeat task.wait(.1);p=Players:GetPlayers()[1] until p and sessions[p] and parts(p)
 local s=sessions[p];assert(not s.canSave,"Temporary profile required")
 local stops=Config.DeliveryStops;local oldFrame=p.Character:GetPivot();local checks=0
 local function check(v,message) assert(v,message);checks+=1 end
 local objects=workspace.ScreamSimulatorWorld.QuestObjects
 local function trigger(marker)
  p.Character:PivotTo(CFrame.new(marker.Position+Vector3.new(0,3,0)))
  interactQuest(p,marker.ProximityPrompt)
 end
 local ok,err=xpcall(function()
  for i,stop in ipairs(stops) do
   stopQuest(p);s.activeQuest="delivery";s.data.quests.delivery={progress=0,claimed=false}
   -- A singleton config makes each server-selected route deterministic in this test.
   Config.DeliveryStops={stop}
   trigger(objects.CoffeeOrder)
   check(s.carrying and s.deliveryStop==stop.id,"Wrong server-assigned stop")
   check(QuestGuide.Step(Config.GetQuest('delivery'),0,true,false,nil,Config.GetDeliveryStop(s.deliveryStop).name)=="Deliver to the "..stop.name,"Directions mismatch")
   local deadline=s.questDeadline
   trigger(objects.CoffeeOrder)
   check(s.questDeadline==deadline and s.deliveryStop==stop.id,"Repeated pickup changed timer or route")
   trigger(objects[stops[i%#stops+1].id])
   check(s.data.quests.delivery.progress==0 and s.carrying,"Wrong destination consumed order")
   trigger(objects[stop.id])
   check(s.data.quests.delivery.progress==1 and not s.carrying and not s.questDeadline and not s.deliveryStop,"Correct delivery did not clear attempt")
   trigger(objects[stop.id])
   check(s.data.quests.delivery.progress==1,"Repeated delivery changed completion")
   stopQuest(p);s.activeQuest="delivery";s.data.quests.delivery={progress=0,claimed=false}
   trigger(objects.CoffeeOrder);s.questDeadline=os.clock()-1
   trigger(objects[stop.id])
   check(s.data.quests.delivery.progress==0,"Expired order completed")
   stopQuest(p)
   check(not s.carrying and not s.deliveryStop and not s.questDeadline,"Abandon retained route")
  end
 end,debug.traceback)
 Config.DeliveryStops=stops;stopQuest(p);s.data.quests.delivery=nil;p.Character:PivotTo(oldFrame);state(p)
 workspace:SetAttribute("DeliveryRoutesResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
end)
