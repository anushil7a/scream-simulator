-- Append to Client only in a disposable local Studio build, then restore original Source.
-- Synthetic MicReady/power requests test server integration, NOT real audio or physical input.
task.spawn(function()
 local Run=game:GetService("RunService")
 assert(Run:IsStudio() and game.PlaceId==0,"Disposable Studio place only")
 local player=game.Players.LocalPlayer
 local remotes=game.ReplicatedStorage:WaitForChild("ScreamRemotes")
 local action=remotes:WaitForChild("Action")
 local actualMic=mic
 local simulatedMic={ready=false,power=.6,status="SYNTHETIC TEST — no live audio",Cancel=function() end,Begin=function() return false end,Release=function() return 0 end,Check=function() end,Calibrate=function() end}
 local checks=0;local screams=0;local dodges=0;local latest
 local stateConnection=remotes.State.OnClientEvent:Connect(function(s) latest=s end)
 local effectConnection=remotes.Effect.OnClientEvent:Connect(function(kind) if kind=="Scream" then screams+=1 elseif kind=="Dodge" then dodges+=1 end end)
 local function check(value,message) assert(value,message);checks+=1 end
 local function send(verb,arg) action:FireServer(verb,arg) end
 local function sync() send("Sync");task.wait(.25);return latest end
 local ok,err=xpcall(function()
  task.wait(2);sync()
  check(latest~=nil and latest.savingAvailable==false,"Test requires temporary profiles; abort before mutations")
  send("DevCommand","Hub");task.wait(.3);mic=simulatedMic;simulatedMic.ready=true;send("MicReady",true)
  send("BeginCast",1);task.wait(.35)
  send("Cast",{sequence=1,power=1,aim=player.Character.Head.Position+Vector3.new(0,100,0)})
  task.wait(.25);check(screams==0,"Spawn protection must reject attack")
  task.wait(5)
  send("BeginCast",2);task.wait(.35)
  check((player:GetAttribute("CaptureStarted") or 0)>0,"Capture accepted after protection")
  local aim=player.Character.Head.Position+Vector3.new(0,100,0)
  send("Cast",{sequence=2,power=.6,aim=aim});task.wait(.3)
  check(screams==1,"Valid release must emit exactly one scream")
  send("Cast",{sequence=2,power=1,aim=aim});send("BeginCast",3);task.wait(.35)
  send("Cast",{sequence=3,power=1,aim=aim});task.wait(.25)
  check(screams==1,"Replay and cooldown requests must not emit another scream")
  task.wait(4)
  send("BeginCast",4);task.wait(.35)
  check((player:GetAttribute("CaptureStarted") or 0)>0,"Second capture accepted after cooldown")
  send("Dodge");task.wait(.25)
  check(dodges==1,"Grounded dodge accepted")
  check((player:GetAttribute("CaptureStarted") or 0)==0,"Dodge cancels capture")
  send("Cast",{sequence=4,power=1,aim=aim});send("Dodge");task.wait(.35)
  check(screams==1,"Releasing cancelled capture after dodge cannot scream")
  check(dodges==1,"Dodge cooldown rejects repeat")
  simulatedMic.ready=false;send("MicReady",false);task.wait(.25);send("BeginCast",5);task.wait(.35)
  send("Cast",{sequence=5,power=1,aim=aim});task.wait(.25)
  check(screams==1,"Missing microphone readiness blocks attack")
  check((player:GetAttribute("CaptureStarted") or 0)==0,"No capture remains after mic loss")
 end,debug.traceback)
 mic=actualMic
 send("CancelCast");send("MicReady",false)
 stateConnection:Disconnect();effectConnection:Disconnect()
 player:SetAttribute("ActionRegressionPassed",ok)
 player:SetAttribute("ActionRegressionChecks",checks)
 player:SetAttribute("ActionRegressionError",ok and "" or tostring(err))
 print(ok and ("PASS "..checks.." synthetic integrated action checks") or ("FAIL synthetic action regression: "..tostring(err)))
end)
