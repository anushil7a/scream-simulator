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
   local entry={player=adapter,added=added,removed=removed}
   table.insert(adapters,entry)
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
   local hand=model:FindFirstChild(kind=="R6" and "Right Arm" or "RightHand")
   local right=rig.joints[kind=="R6" and "Right Shoulder" or "RightShoulder"]
   local wrist=rig.joints.RightWrist
   -- R6 has no hand part. Measure its grip near the lower end of the arm.
   local function gripZ()
    local grip=kind=="R6" and hand.CFrame:PointToWorldSpace(Vector3.new(0,-hand.Size.Y/2+.15,0)) or hand.Position
    return rig.root.CFrame:PointToObjectSpace(grip).Z
   end
   local idleZ=gripZ()
   local gear=Instance.new("Model");gear.Name="ProgressionGear";gear:SetAttribute("MountKind","hand");gear.Parent=model
   attributes.SustainedActive=true;task.wait(.6)
   local heldZ=gripZ()
   local direction=rig.root.CFrame:VectorToObjectSpace(hand.CFrame.LookVector)
   results[kind].idleZ=idleZ;results[kind].heldZ=heldZ;results[kind].forward=-direction.Z;results[kind].vertical=direction.Y
   check(heldZ<idleZ-.4,kind.." held hand did not move forward")
   check(-direction.Z>.63 and math.abs(direction.Y)<(kind=="R6" and .72 or .42),kind.." held direction is not forward and level")
   local shoulderBasis=right:IsA("Motor6D") and right.C0.Rotation or right.Attachment0.CFrame.Rotation
   local swing=shoulderBasis:Inverse()*CFrame.Angles(-1.2,0,0)*shoulderBasis
   local competing=true
   entry.animation=Run.PreAnimation:Connect(function()
    right.Transform=competing and swing or CFrame.identity
   end)
   task.wait(.2)
   local movingDirection=rig.root.CFrame:VectorToObjectSpace(hand.CFrame.LookVector)
   results[kind].movingForward=-movingDirection.Z;results[kind].movingZ=gripZ()
   check(-movingDirection.Z>.63 and gripZ()<idleZ-.4,kind.." locomotion swing overrode the held pose")
   competing=false
   attributes.SustainedActive=false
   local now=workspace:GetServerTimeNow()
   attributes.DodgeStarted=now;attributes.DodgeEnds=now+Config.DodgeDuration
   task.wait(math.min(.08,Config.DodgeDuration/2))
   check(rig.charge==0 and model:GetAttribute("DodgeAnimationProgress")>=0,kind.." dodge retained the cast pose")
   attributes.DodgeStarted=nil;attributes.DodgeEnds=nil;task.wait(.2)
   local _,rightResidual=right.Transform:ToAxisAngle()
   local wristResidual=0
   if wrist then local _,angle=wrist.Transform:ToAxisAngle();wristResidual=angle end
   check(math.abs(rightResidual)<.002 and math.abs(wristResidual)<.002,kind.." dodge exit retained held shoulder or wrist")
   gear:Destroy()
   removed:Fire(model);task.wait()
   check(rigs[adapter]==nil,kind.." character removal retained rig")
  end
 end,debug.traceback)
 for _,entry in ipairs(adapters) do
  if entry.animation then entry.animation:Disconnect() end
  entry.removed:Fire(entry.player.Character);entry.added:Destroy();entry.removed:Destroy()
 end
 workspace:SetAttribute("RigPoseResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,rigs=results,error=not ok and tostring(err) or nil}))
 print("Rig pose regression",ok,checks,err)
end)
