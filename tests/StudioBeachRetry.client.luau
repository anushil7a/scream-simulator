-- Append to Client with an ordinary-server interactQuest fixture in local Play.
-- Synthetic interactions and object reappearance; not physical F or real streaming proof.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio(),"Local Studio only")
 local checks=0
 local function check(v,msg) assert(v,msg);checks+=1 end
 local function waitFor(f,msg)
  local deadline=os.clock()+15
  repeat if f() then return end;task.wait(.1) until os.clock()>deadline
  error(msg)
 end
 local function send(v,a) action:FireServer(v,a);task.wait(.4) end
 local ok,err=xpcall(function()
  task.wait(3);check(data.savingAvailable==false,"Temporary profile required")
  p.Character:PivotTo(CFrame.new(-414,5,250));task.wait(2)
  local mar
  for _,m in workspace.ScreamSimulatorWorld:GetChildren() do if m:GetAttribute("DisplayName")=="Mar Soler" then mar=m end end
  check(mar~=nil,"Gardener loaded")
  p.Character:PivotTo(mar.HumanoidRootPart.CFrame*CFrame.new(0,0,5));task.wait(.4);send("Talk",mar:GetAttribute("NpcId"));closeConversation();task.wait(.3)
  check(data.availableQuests.beach==true,"Gardener unlocked beach quest")
  send("AcceptQuest","beach")
  waitFor(function() return data.quests.beach and data.quests.beach.progress==1 end,"First collection missing")
  local name=workspace:GetAttribute("BeachRetryObject")
  local objects=workspace.ScreamSimulatorWorld:WaitForChild("QuestObjects")
  local bottle=objects:WaitForChild(name,10);check(bottle~=nil,"Bottle streamed")
  task.wait(.7)
  check(bottle.LocalTransparencyModifier==1 and not bottle:FindFirstChildOfClass("ProximityPrompt").Enabled,"Collected bottle hidden")
  local clone=bottle:Clone();clone.LocalTransparencyModifier=0;clone:FindFirstChildOfClass("ProximityPrompt").Enabled=true;clone.Parent=objects
  task.wait(.8);check(clone.LocalTransparencyModifier==1 and not clone:FindFirstChildOfClass("ProximityPrompt").Enabled,"Newly appearing collected bottle resynchronized");clone:Destroy()
  send("AbandonQuest")
  check(data.activeQuest==nil and data.quests.beach.progress==0,"Abandon cleared progress")
  check(bottle.LocalTransparencyModifier==0 and bottle:FindFirstChildOfClass("ProximityPrompt").Enabled,"Abandon restored bottle")
  send("AcceptQuest","beach")
  waitFor(function() return data.quests.beach.progress==1 end,"Retry did not collect same bottle")
  task.wait(.7);check(data.quests.beach.progress==1,"Duplicate collection rejected")
  send("AcceptQuest","garden")
  check(data.activeQuest=="garden" and data.quests.beach.progress==0,"Switch reset beach attempt")
  check(bottle.LocalTransparencyModifier==0 and bottle:FindFirstChildOfClass("ProximityPrompt").Enabled,"Switch restored bottle")
 end,debug.traceback)
 closeConversation()
 p:SetAttribute("BeachRetryResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
 print("Beach retry regression",ok,checks,err)
end)
