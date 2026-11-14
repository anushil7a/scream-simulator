-- Append to Client only in disposable Studio Play; restore source afterward.
-- Exercises ordinary remotes and actual dialogue using a non-saving test profile.
task.spawn(function()
 assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0,"Local Studio only")
 local player=game.Players.LocalPlayer
 local latest,conversation,checks
 checks=0
 local connection=remotes.State.OnClientEvent:Connect(function(s) latest=s;if s.conversation then conversation=s.conversation end end)
 local function send(verb,arg) action:FireServer(verb,arg);task.wait(.35) end
 local function check(value,message) assert(value,message);checks+=1 end
 local ok,err=xpcall(function()
  task.wait(3);send("Sync")
  check(latest and latest.savingAvailable==false and not latest.amplifierOwned,"Fresh temporary profile required")
  player.Character:PivotTo(CFrame.new(85,5,-47));task.wait(2)
  local vendor
  for _,model in workspace.ScreamSimulatorWorld:GetChildren() do
   if model:GetAttribute("DisplayName")=="Pau Vidal" then vendor=model;break end
  end
  check(vendor~=nil,"Vendor streamed")
  local root=vendor.HumanoidRootPart
  local item={npc=vendor:GetAttribute("NpcId"),product="MicroSpeaker"}
  send("VendorPurchase",item)
  check(not latest.amplifierOwned,"Conversation required")
  player.Character:PivotTo(root.CFrame*CFrame.new(0,0,5));task.wait(.4);send("Talk",item.npc)
  check(conversation and conversation.products and conversation.products[1].price==Config.MicroSpeakerPrice,"Server offer has current price")
  check(conversationPanel.Visible,"Actual vendor dialogue visible")
  send("VendorPurchase",item)
  check(not latest.amplifierOwned and latest.coins==0,"Insufficient balance rejected without debit")
  send("DevCommand","Coins");send("DevCommand","Coins")
  check(latest.testSession==true and latest.coins==2000,"Test funds are temporary")
  send("VendorPurchase",{npc=item.npc,product="Unknown"})
  check(not latest.amplifierOwned and latest.coins==2000,"Unknown product rejected")
  player.Character:PivotTo(CFrame.new(150,5,-47));task.wait(.4);send("VendorPurchase",item)
  check(not latest.amplifierOwned and latest.coins==2000,"Distant purchase rejected")
  task.wait(2.1);player.Character:PivotTo(root.CFrame*CFrame.new(0,0,5));task.wait(.4);send("Talk",item.npc)
  send("VendorPurchase",item)
  check(latest.amplifierOwned and latest.amplifierEquipped and latest.coins==500,"Purchase charged once and equipped: "..tostring(latest.message).." / coins "..latest.coins)
  send("VendorPurchase",item)
  check(latest.coins==500 and latest.amplifierEquipped,"Duplicate request neither charges nor toggles")
  closeConversation();task.wait(2.1);player.Character:PivotTo(root.CFrame*CFrame.new(0,0,5));task.wait(.4);send("Talk",item.npc)
  check(conversation.products[1].owned==true,"Return visit reports ownership")
 end,debug.traceback)
 closeConversation();connection:Disconnect()
 player:SetAttribute("VendorRegressionPassed",ok);player:SetAttribute("VendorRegressionChecks",checks);player:SetAttribute("VendorRegressionError",ok and "" or tostring(err))
 print(ok and ("PASS "..checks.." vendor checks") or ("FAIL vendor regression: "..tostring(err)))
end)
