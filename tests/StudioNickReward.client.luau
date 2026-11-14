-- Append to actual Client with the server-side StudioSoccerCompletion driver.
-- Disposable local Play only. Driver shoots the real course with synthetic aim.
task.spawn(function()
 assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0,"Local Studio only")
 task.wait(3)
 assert(data.savingAvailable==false,"Temporary profile required")
 p.Character:PivotTo(CFrame.new(647,5,547));task.wait(2)
 local nick
 for _,m in workspace.ScreamSimulatorWorld:GetChildren() do if m:GetAttribute("DisplayName")=="Nick Booty" then nick=m;break end end
 assert(nick,"Nick not loaded")
 p.Character:PivotTo(nick.HumanoidRootPart.CFrame*CFrame.new(0,0,5));task.wait(.4)
 action:FireServer("Talk",nick:GetAttribute("NpcId"));task.wait(.4);closeConversation();task.wait(.3);action:FireServer("AcceptQuest","nick")
 local deadline=os.clock()+220
 while not workspace:GetAttribute("SoccerLiveDriverResult") and os.clock()<deadline do task.wait(.5) end
 assert(workspace:GetAttribute("SoccerLiveDriverResult"),"Course driver timed out")
 action:FireServer("Sync");task.wait(.4)
 local beforeCoins=data.coins;local beforeLevel=data.level;local beforeXp=data.xp
 assert(data.quests.nick and data.quests.nick.progress==1,"Challenge did not mark quest complete")
 action:FireServer("ClaimQuest","nick");task.wait(.4)
 assert(data.coins==beforeCoins+1200 and data.achievements.NickChampion and data.quests.nick.claimed,"Reward/achievement missing")
 local coins,level,xp=data.coins,data.level,data.xp
 action:FireServer("ClaimQuest","nick");task.wait(.4)
 assert(data.coins==coins and data.level==level and data.xp==xp,"Duplicate reward")
 p:SetAttribute("NickRewardRegression",game:GetService("HttpService"):JSONEncode({passed=true,coinsAwarded=1200,levelBefore=beforeLevel,xpBefore=beforeXp,levelAfter=level,xpAfter=xp}))
end)
