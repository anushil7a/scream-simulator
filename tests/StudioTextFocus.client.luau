-- Append to Client in an unpublished Studio copy. Actual TextBox focus and
-- production input callbacks with synthetic mic readiness, not live audio.
task.spawn(function()
 assert(game.PlaceId==0 and Run:IsStudio())
 task.wait(7)
 local original=mic;local releases=0;local screams=0;local checks=0
 local fake={ready=true,power=.65,status="Synthetic focus regression"}
 function fake:Cancel() self.captureStarted=nil end
 function fake:Begin() self.captureStarted=os.clock();return true end
 function fake:CapturePower() return .65 end
 function fake:Release() releases+=1;return .65 end
 local box=Instance.new("TextBox");box.Size=UDim2.fromOffset(240,40);box.Position=UDim2.fromOffset(20,220);box.Text="";box.Parent=gui
 local connection=remotes.Effect.OnClientEvent:Connect(function(kind) if kind=="Scream" then screams+=1 end end)
 local function check(v,message) assert(v,message);checks+=1 end
 local ok,err=xpcall(function()
  mic=fake;modal.Visible=false;devPanel.Visible=false;conversationPanel.Visible=false;nextCast=0
  beginCapture("fixture");check(captureSource=="fixture","Initial capture did not start")
  task.wait(.35)
  box:CaptureFocus();check(UIS:GetFocusedTextBox()==box,"TextBox did not acquire engine focus")
  -- Test release immediately, before the render callback gets a cancellation turn.
  releaseCapture("fixture")
  check(captureSource==nil and releases==0,"Focused release sampled/fired the microphone")
  beginCapture("fixture");check(captureSource==nil,"Typing allowed a new capture")
  task.wait(.2);check(screams==0,"Typing produced a scream effect")
  box:ReleaseFocus(false)
  beginCapture("fixture");check(captureSource=="fixture","Capture did not recover after typing")
 end,debug.traceback)
 cancelCapture();box:ReleaseFocus(false);box:Destroy();connection:Disconnect();mic=original;original:Cancel()
 workspace:SetAttribute("TextFocusResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
end)
