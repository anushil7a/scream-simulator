-- Append to Client. Synthetic local crowd poses exercise actual BillboardGuis.
task.spawn(function()
 task.wait(5)
 local template=game:GetService("CollectionService"):GetTagged("CityResident")[1];assert(template)
 local residents={};local checks=0;local camera=workspace.CurrentCamera;local saved=camera.CFrame
 local root=Instance.new("Part");root.Anchored=true;root.Position=Vector3.new(0,3,0)
 local function check(ok,message) assert(ok,message);checks+=1 end
 local function enabled(name)
  local n=0;for _,bot in ipairs(residents) do if bot.Head[name].Enabled then n+=1 end end;return n
 end
 local ok,err=xpcall(function()
  camera.CFrame=CFrame.lookAt(Vector3.new(0,5,20),Vector3.new(0,3,0))
  for i=1,3 do
   local bot=template:Clone();bot.Parent=workspace;bot.HumanoidRootPart.Anchored=true;bot:PivotTo(CFrame.new(i-2,3,-3-i*2));bot.Humanoid.Health=bot.Humanoid.MaxHealth
   bot.Head.SpeechBubble:FindFirstChildOfClass("TextLabel").Visible=true;table.insert(residents,bot)
  end
  check(refreshResidentLabels(root,camera,residents)==residents[1],"Wrong nearby target")
  check(enabled("Nameplate")==1,"Healthy crowd name clutter")
  check(enabled("SpeechBubble")==1,"Crowd speech overlap")
  residents[2].Humanoid.Health=30;refreshResidentLabels(root,camera,residents)
  check(enabled("Nameplate")==2 and residents[2].Head.Nameplate.Enabled,"Missing nearby damage label")
  residents[1]:PivotTo(CFrame.new(0,3,40))
  check(refreshResidentLabels(root,camera,residents)==residents[2],"Off-screen NPC stayed selected")
  check(not residents[1].Head.Nameplate.Enabled and not residents[1].Head.SpeechBubble.Enabled,"Off-screen labels visible")
  residents[2].Humanoid.Health=0
  check(refreshResidentLabels(root,camera,residents)==residents[3],"Dead NPC stayed selected")
  refreshResidentLabels(nil,camera,residents)
  check(enabled("Nameplate")==0 and enabled("SpeechBubble")==0,"Labels survive absent character")
 end,debug.traceback)
 camera.CFrame=saved;root:Destroy();for _,bot in ipairs(residents) do bot:Destroy() end
 workspace:SetAttribute("ResidentLabelsResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
 print("Resident label checks",ok,checks,err)
end)
