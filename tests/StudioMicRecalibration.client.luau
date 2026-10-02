-- Append to Client in a disposable Studio copy. Real calibration controller with
-- synthetic RMS/readiness; not hardware, voice eligibility or live audio evidence.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio())
 local Microphone=require(script.Parent.Microphone)
 local test=Microphone.new();test.connection:Disconnect();test.generation+=1;test.checkPending=false;test.eligible=true
 test.FindInput=function() return {Muted=false} end
 test.analyzer={RmsLevel=.002,Destroy=function() end}
 local checks=0
 local function check(value,message) assert(value,message);checks+=1 end
 local function phase(rms)
  test.analyzer.RmsLevel=rms
  for _=1,20 do test:Step(.016) end
  test.phaseStarted=os.clock()-2.1;test:Step(.016)
 end
 local ok,err=xpcall(function()
  local quiet,voice={},{}
  for _=1,20 do table.insert(quiet,.002);table.insert(voice,.08) end
  assert(test.model:Calibrate(quiet,voice));test.ready=true;test.power=.8;test.captureStarted=os.clock()
  test:Calibrate()
  check(not test.model.calibrated and not test.ready and test.power==0,"Old ready state survived new attempt")
  check(test.captureStarted==nil and test.phase=="quiet","Old attack survived new attempt")
  phase(.002);check(test.phase=="voice","Quiet phase failed to advance")
  phase(.002);check(test.phase==nil and not test.ready,"Failed retry remained ready")
  test:Step(.016);test:Step(.016)
  check(not test.ready and not test.model.calibrated and not test:Begin(),"Old calibration silently restored readiness")
  test:Calibrate();phase(.002);phase(.08)
  check(test.ready and test.model.calibrated and test:Begin(),"Good retry did not restore readiness")
 end,debug.traceback)
 test:Destroy()
 workspace:SetAttribute("MicRecalibrationResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
 print("Mic recalibration",ok,checks,err)
end)
