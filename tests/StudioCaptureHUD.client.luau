-- Append to Client only in an unpublished Studio copy. Synthetic UI state;
-- does not establish microphone capture, real input or server attack acceptance.
task.spawn(function()
 assert(Run:IsStudio() and game.PlaceId==0)
 task.wait(7)
 local original=mic;local checks=0
 local function check(ok,message) assert(ok,message);checks+=1 end
 local fake={ready=true,power=.8,status="Synthetic HUD check"}
 function fake:Cancel() self.captureStarted=nil end
 local ok,err=xpcall(function()
  mic=fake;modal.Visible=false;devPanel.Visible=false;conversationPanel.Visible=false
  captureSource=nil;nextCast=0
  task.wait(.1)
  check(string.find(meterText.Text,"Hold attack before speaking",1,true)~=nil,"Missing idle instructions")
  check(string.find(meterText.Text,"LIVE MIC 80%",1,true)~=nil,"Meter is not identified as live")
  captureSource="fixture";fake.captureStarted=os.clock()-.4
  task.wait(.1)
  check(string.find(meterText.Text,"Speak now",1,true)~=nil,"Missing sampling countdown")
  check(castButton.Text=="SPEAK • RELEASE","Attack control missing speak prompt")
  fake.captureStarted=os.clock()-1.5;task.wait(.1)
  check(string.find(meterText.Text,"Window ended",1,true)~=nil,"Frozen window appears live")
  check(castButton.Text=="RELEASE TO FIRE","Missing release action")
  fake.captureStarted=os.clock()-9;task.wait(.1)
  check(captureSource==nil and fake.captureStarted==nil,"Expired capture not canceled")
  check(string.find(toast.Text,"Capture expired",1,true)~=nil,"Expiry feedback missing")
 end,debug.traceback)
 captureSource=nil;mic=original;original:Cancel()
 workspace:SetAttribute("CaptureHUDResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
end)
