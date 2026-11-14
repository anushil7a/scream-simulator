-- Append to Client in a disposable local Play session. Synthetic aim/mic readiness.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio(),"Local Studio only")
 repeat task.wait(.1) until p.Character and p.Character:FindFirstChild("HumanoidRootPart")
 local originalAim=aimRay;local originalReady=mic.ready
 local object=Instance.new("Model");object.Name="RepairReadoutFixture";object.Parent=workspace
 local body=Instance.new("Part");body.Anchored=true;body.CanCollide=false;body.Transparency=1;body.Position=p.Character.HumanoidRootPart.Position+Vector3.new(0,0,-20);body.Parent=object
 object:SetAttribute("RequiredLevel",100);object:SetAttribute("ObjectName","Apartment frontage")
 object:SetAttribute("ObjectHealth",202);object:SetAttribute("ObjectMaxHealth",250);object:SetAttribute("RepairAt",workspace:GetServerTimeNow()+300)
 aimRay=function() return body.Position,{Instance=body,Position=body.Position} end
 Run:BindToRenderStep("RepairReadoutFixture",-100,function() mic.ready=true end)
 local ok,err=xpcall(function()
  task.wait(.8)
  assert(aimInfo.Visible and string.find(aimInfo.Text,"Repair in",1,true),"Repair countdown missing")
  assert(aimInfo.TextFits,"Repair countdown clipped")
  object:SetAttribute("RepairAt",0);object:SetAttribute("ObjectHealth",250)
  task.wait(.3)
  assert(not string.find(aimInfo.Text,"Repair in",1,true),"Repair countdown remained after restoration")
 end,debug.traceback)
 Run:UnbindFromRenderStep("RepairReadoutFixture");aimRay=originalAim;mic.ready=originalReady;object:Destroy()
 workspace:SetAttribute("RepairReadoutResult",game:GetService("HttpService"):JSONEncode({passed=ok,error=not ok and tostring(err) or nil,checks=ok and 3 or nil}))
 print("Repair readout",ok,err)
end)
