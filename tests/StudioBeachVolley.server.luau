-- Append to Bootstrap in disposable Studio. Scripted validated-hit adapter;
-- this tests real server ball motion, not physical mic or two-person usability.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio())
 local player=game.Players:GetPlayers()[1] or game.Players.PlayerAdded:Wait()
 while not player.Character or not player.Character:FindFirstChild("HumanoidRootPart") do task.wait(.1) end
 local root=player.Character.HumanoidRootPart;local model=workspace.ScreamSimulatorWorld.BeachVolley
 local ball=model.VolleyBall;local checks=0
 while not sessions[player] do task.wait(.1) end
 local session=sessions[player];local oldReady,oldProtection=session.micReady,session.protectedUntil
 local function check(value,message) assert(value,message);checks+=1 end
 local function hit(from,power)
  root.CFrame=CFrame.new(from);root.AssemblyLinearVelocity=Vector3.zero
  local origin=from+Vector3.new(0,1,0)
  return BeachVolley.Hit(player,origin,(ball.Position-origin).Unit,30,4,power)
 end
 local function waitFor(predicate,seconds)
  local deadline=os.clock()+seconds
  repeat if predicate() then return true end;task.wait(.03) until os.clock()>deadline
  return false
 end
 local ok,err=xpcall(function()
  check(model:GetAttribute("Phase")=="Ready","Court not ready")
  check(not hit(Vector3.new(-100,4,482),1),"Outside court hit accepted")
  root.CFrame=CFrame.new(-50,4,482)
  check(not BeachVolley.Hit(player,root.Position,Vector3.xAxis,30,4,1),"Missed beam hit ball")
  check(not BeachVolley.Hit(player,root.Position,Vector3.zAxis,2,4,1),"Occluded short beam hit ball")
  check(hit(Vector3.new(-50,4,482),1),"Serve failed")
  check(waitFor(function() return model:GetAttribute("Rally")==1 end,2.5),"Serve did not cross net")
  check(waitFor(function() return ball.Position.Z>=518 end,2),"Ball did not reach other side")
  check(hit(Vector3.new(-50,4,525),.5),"Return failed")
  check(waitFor(function() return model:GetAttribute("Rally")==2 end,3),"Return did not cross net")
  check(waitFor(function() return model:GetAttribute("Phase")=="Resetting" end,5),"Miss did not finish rally")
  check(not hit(Vector3.new(-50,4,483),1),"Cast during reset accepted")
  check(waitFor(function() return model:GetAttribute("Phase")=="Ready" end,4),"Automatic serve reset failed")
  check(model:GetAttribute("BestRally")==2 and model:GetAttribute("Rally")==0,"Best rally not retained")
  check((ball.Position-Vector3.new(-50,4,489)).Magnitude<.01,"Serve position incorrect")
  -- Exercise the actual cast entry point using a synthetic ready microphone.
  root.CFrame=CFrame.new(-50,4,482);root.AssemblyLinearVelocity=Vector3.zero
  session.micReady=true;session.protectedUntil=0
  check(VoiceCombat.Begin(session.voice,os.clock()-.35,1,canCapture(player,session,os.clock())),"Capture rejected")
  -- Synthetic capture duration; do not yield to the real denied-mic client.
  cast(player,{sequence=1,power=1,aim=ball.Position})
  check(model:GetAttribute("Phase")=="Playing","Accepted scream did not serve")
 end,debug.traceback)
 session.micReady=oldReady;session.protectedUntil=oldProtection
 root.CFrame=World.SafeSpawn
 workspace:SetAttribute("BeachVolleyResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
 print("Beach volley regression",ok,checks,err)
end)
