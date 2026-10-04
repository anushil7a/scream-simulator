-- Append to Client in disposable Studio. Calibration lifecycle and timeout bookkeeping only.
-- No real microphone capture/permission/disconnection claim.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio())
 local Microphone=require(script.Parent.Microphone)
 local test=Microphone.new();test.connection:Disconnect()
 local checks=0
 local function check(v,message) assert(v,message);checks+=1 end
 local ok,err=xpcall(function()
  test.phase="voice";test.phaseStarted=os.clock()-1;test.quiet={.01};test.spoken={.2};test.ready=true;test.captureStarted=os.clock()
  test:Check()
  check(test.phase==nil and test.phaseStarted==nil and #test.quiet==0 and #test.spoken==0,"Retry retained calibration samples")
  check(not test.ready and test.captureStarted==nil,"Retry retained attack readiness")
  local stale=Instance.new("Folder");stale:Destroy();test.input=stale
  test.phase="voice";test.phaseStarted=os.clock()-1;test.quiet={.01};test.spoken={.2};test.ready=true;test.captureStarted=os.clock()
  test:FindInput()
  check(test.phase==nil and test.phaseStarted==nil and #test.quiet==0 and #test.spoken==0,"Lost device retained calibration samples")
  check(not test.ready and test.captureStarted==nil,"Lost device retained attack readiness")
  -- Mark this check resolved; delayed timeout must respect resolution independently of eligibility.
  test.checkPending=false;test.eligible=false;test.status="Resolved voice check"
  task.wait(10.2)
  check(not string.find(test.status,"timed out",1,true),"Resolved check became a timeout")
 end,debug.traceback)
 test:Destroy()
 workspace:SetAttribute("MicLifecycleResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
 print("Mic lifecycle",ok,checks,err)
end)
