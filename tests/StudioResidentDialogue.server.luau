-- Append to Bootstrap in disposable Play. Synthetic task state and direct server talk callback.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio())
 local p;repeat task.wait(.1);p=game.Players:GetPlayers()[1] until p and sessions[p] and parts(p)
 local s=sessions[p];assert(not s.canSave,"Temporary profile required")
 local bot;for _,b in World.Bots do if b.role=="Gardener" then bot=b;break end end
 local checks=0;local original=p.Character:GetPivot()
 local ok,err=xpcall(function()
  assert(bot,"Gardener missing")
  local previous
  for _=1,12 do local line=World.Talk(bot);if previous then assert(line~=previous,"Consecutive role line repeated");checks+=1 end;previous=line end
  p.Character:PivotTo(CFrame.new(bot.root.Position+Vector3.new(4,0,0)))
  s.activeQuest="garden";s.data.quests.garden={progress=1,claimed=false};s.nextTalk=0;talk(p,bot.id)
  assert(string.find(bot.speech.Text,"Water flowerbeds",1,true),"Active task direction missing");checks+=1
  s.data.quests.garden.progress=3;s.nextTalk=0;talk(p,bot.id)
  assert(string.find(bot.speech.Text,"reward is waiting",1,true),"Completed reward reminder missing");checks+=1
  s.data.quests.garden.claimed=true;s.nextTalk=0;talk(p,bot.id)
  assert(not string.find(bot.speech.Text,"reward is waiting",1,true),"Claimed reward still offered");checks+=1
 end,debug.traceback)
 closeConversation(p);stopQuest(p);s.data.quests={};p.Character:PivotTo(original);state(p)
 workspace:SetAttribute("ResidentDialogueResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
 print("Resident dialogue",ok,checks,err)
end)
