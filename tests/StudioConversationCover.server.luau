-- Append to Bootstrap in disposable Studio: actual conversation handler plus
-- shared visibility rules, with controlled cover and character placement.
task.spawn(function()
 task.wait(4)
 local player=game.Players:GetPlayers()[1];local s=sessions[player];assert(s and not s.canSave)
 local bot=World.Bots[1];local npcPose=bot.model:GetPivot();local playerPose=player.Character:GetPivot()
 local wall=Instance.new("Part");wall.Name="ConversationCoverFixture";wall.Anchored=true;wall.Size=Vector3.new(1,12,12);wall.Position=Vector3.new(-595,6,210);wall.Parent=workspace
 local checks=0
 local function check(value,message) assert(value,message);checks+=1 end
 local ok,err=xpcall(function()
  closeConversation(player);World.Talk(bot);bot.socialUntil=os.clock()+30
  task.wait(.3)
  bot.model:PivotTo(CFrame.new(-590,4,210));bot.lastGrounded=bot.root.Position;bot.root.AssemblyLinearVelocity=Vector3.zero
  player.Character:PivotTo(CFrame.new(-600,4,210))
  s.nextTalk=0
  check(not InteractionRules.CanReachNpc(player.Character,bot.model,14),"Wall did not block shared rule")
  talk(player,bot.id);check(s.conversationBot==nil,"Server conversation crossed wall")
  wall.CanCollide=false
  check(InteractionRules.CanReachNpc(player.Character,bot.model,14),"Decoration blocked conversation")
  talk(player,bot.id);check(s.conversationBot==bot,"Clear conversation rejected")
  closeConversation(player);s.nextTalk=0
  bot.model:PivotTo(CFrame.new(-580,4,210))
  check(not InteractionRules.CanReachNpc(player.Character,bot.model,14),"Out-of-range rule accepted")
  talk(player,bot.id);check(s.conversationBot==nil,"Out-of-range server conversation accepted")
 end,debug.traceback)
 closeConversation(player);wall:Destroy();bot.model:PivotTo(npcPose);bot.lastGrounded=bot.root.Position;bot.socialUntil=os.clock()+1
 player.Character:PivotTo(playerPose)
 workspace:SetAttribute("ConversationCoverResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
 print("Conversation cover",ok,checks,err)
end)
