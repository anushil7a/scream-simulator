-- Append to Bootstrap in disposable Studio. Synthetic quest state, actual State remote/HUD.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio())
 local p;repeat task.wait(.1);p=game.Players:GetPlayers()[1] until p and sessions[p] and parts(p)
 local s=sessions[p];assert(not s.canSave,"Temporary profile required")
 task.wait(3)
 for _,q in Config.Quests do
  s.activeQuest=q.id;s.data.quests[q.id]={progress=0,claimed=false};s.carrying=false;s.raceStart=nil
  state(p);task.wait(.5)
  s.data.quests[q.id].progress=q.goal;state(p);task.wait(.5)
 end
 s.activeQuest="delivery";s.data.quests.delivery.progress=0;s.carrying=true;state(p);task.wait(.5)
 s.activeQuest="sprint";s.data.quests.sprint.progress=0;s.carrying=false;s.raceStart=os.clock();state(p);task.wait(.5)
 stopQuest(p);s.data.quests={};state(p)
 workspace:SetAttribute("QuestGuideFixtureDone",true)
end)
