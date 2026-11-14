-- Append to the actual Client in a disposable local Studio place, then restore it.
-- Exercises ordinary remotes with a temporary profile; no live microphone evidence.
task.spawn(function()
 assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0,"Local Studio only")
 local player=game.Players.LocalPlayer
 local latest,conversation,checks=nil,nil,0
 local connection=remotes.State.OnClientEvent:Connect(function(s) latest=s;if s.conversation then conversation=s.conversation end end)
 local function send(verb,arg) action:FireServer(verb,arg);task.wait(.35) end
 local function check(value,message) assert(value,message);checks+=1 end
 local ok,err=xpcall(function()
  task.wait(3);send("Sync")
  check(latest and latest.savingAvailable==false,"Temporary profile required")
  send("DevCommand","Beach")
  player.Character:PivotTo(CFrame.new(647,5,547));task.wait(2)
  local nick
  for _,model in ipairs(workspace.ScreamSimulatorWorld:GetDescendants()) do
   if model:IsA("Model") and model:GetAttribute("DisplayName")=="Nick Booty" then nick=model;break end
  end
  check(nick~=nil,"Nick streamed at court")
  local root=nick:FindFirstChild("HumanoidRootPart")
  player.Character:PivotTo(root.CFrame*CFrame.new(0,0,5));task.wait(.3)
  send("Talk",nick:GetAttribute("NpcId"))
  check(conversation and conversation.name=="Nick Booty","Dialogue payload received")
  check(conversationPanel.Visible,"Actual dialogue panel opened")
  check(latest.achievements.FoundNick==true and latest.availableQuests.nick==true,"Discovery unlocks achievement and quest")
  local coins=latest.coins
  closeConversation();task.wait(2.1)
  player.Character:PivotTo(root.CFrame*CFrame.new(0,0,5));send("Talk",nick:GetAttribute("NpcId"))
  check(latest.coins==coins,"Discovery reward cannot repeat")
  closeConversation();send("AcceptQuest","nick")
  check(latest.activeQuest=="nick" and latest.questTime>0,"Nick stage and timer active")
  local attemptName="SoccerAttempt_"..player.UserId
  check(workspace.ScreamSimulatorWorld:FindFirstChild(attemptName)~=nil,"Personal attempt replicated")
  send("AbandonQuest")
  check(latest.activeQuest==nil and latest.questTime==0,"Abandon clears tracked timer")
  check(workspace.ScreamSimulatorWorld:FindFirstChild(attemptName)==nil,"Abandon destroys actual soccer attempt")
  send("AcceptQuest","nick");send("DevCommand","ResetQuests")
  check(latest.activeQuest==nil and workspace.ScreamSimulatorWorld:FindFirstChild(attemptName)==nil,"Dev reset clears live attempt")
  send("ClaimQuest","nick")
  check(latest.coins==coins and not latest.achievements.NickChampion,"Incomplete task cannot grant reward")
 end,debug.traceback)
 closeConversation();connection:Disconnect()
 player:SetAttribute("QuestRegressionPassed",ok);player:SetAttribute("QuestRegressionChecks",checks);player:SetAttribute("QuestRegressionError",ok and "" or tostring(err))
 print(ok and ("PASS "..checks.." integrated quest checks") or ("FAIL quest regression: "..tostring(err)))
end)
