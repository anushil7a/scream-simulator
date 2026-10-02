-- Append to RunAnimation in disposable Studio. Native R6/R15 rigs with disabled
-- default Animate and synthetic state adapters; verifies joint bases and cleanup,
-- not physical input, full Animator blending, or multiplayer avatar replication.
task.spawn(function()
 assert(game.PlaceId==0 and Run:IsStudio())
 local checks=0;local adapters={};local results={}
 local function check(value,message) assert(value,message);checks+=1 end
 local ok,err=xpcall(function()
  for _,kind in ipairs({"R6","R15"}) do
   local model=workspace:WaitForChild("PoseRig"..kind,20);assert(model,"Missing native rig")
   local added=Instance.new("BindableEvent");local removed=Instance.new("BindableEvent")
   local attributes={CaptureStarted=workspace:GetServerTimeNow()}
   local adapter={Character=model,CharacterAdded=added.Event,CharacterRemoving=removed.Event,GetAttribute=function(_,name) return attributes[name] end}
   table.insert(adapters,{player=adapter,added=added,removed=removed})
   watch(adapter)
   local shoulder=kind=="R6" and "Left Shoulder" or "LeftShoulder"
   local deadline=os.clock()+12
   repeat task.wait(.1) until (rigs[adapter] and rigs[adapter].joints[shoulder]) or os.clock()>deadline
   task.wait(.6)
   local rig=assert(rigs[adapter],"Rig did not finish streaming");local joint=assert(rig.joints[shoulder],"Shoulder did not stream")
   local basis=joint:IsA("Motor6D") and joint.C0.Rotation or joint.Attachment0.CFrame.Rotation
   local expected=CFrame.Angles(-.65*rig.charge,0,-.32*rig.charge)
   local actual=basis*joint.Transform*basis:Inverse()
   local _,errorAngle=expected:ToObjectSpace(actual):ToAxisAngle()
   results[kind]={axisError=errorAngle}
   check(math.abs(errorAngle)<.002,kind.." shoulder motion uses wrong axes")
   attributes.CaptureStarted=0;task.wait(.8)
   local _,residual=joint.Transform:ToAxisAngle()
   check(math.abs(residual)<.002,kind.." charge pose failed to recover")
   results[kind].residual=residual
   removed:Fire(model);task.wait()
   check(rigs[adapter]==nil,kind.." character removal retained rig")
  end
 end,debug.traceback)
 for _,entry in ipairs(adapters) do entry.removed:Fire(entry.player.Character);entry.added:Destroy();entry.removed:Destroy() end
 workspace:SetAttribute("RigPoseResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,rigs=results,error=not ok and tostring(err) or nil}))
 print("Rig pose regression",ok,checks,err)
end)
