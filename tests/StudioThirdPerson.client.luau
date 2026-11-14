-- Append to Client only in a disposable PlaceId=0 Studio copy.
-- No microphone, transport, touch hardware or camera-occlusion claim.
task.spawn(function()
 assert(game.PlaceId==0 and Run:IsStudio())
 task.wait(7)
 local checks=0
 local function check(v,msg)assert(v,msg);checks+=1 end
 local wasVisible,wasSelected=modal.Visible,selected
 local ok,err=xpcall(function()
  check(p.CameraMode==Enum.CameraMode.Classic and p.CameraMinZoomDistance>=6,"Third-person zoom policy missing")
  check(controls:FindFirstChild("CameraToggle")==nil,"View button remains")
  selected="Settings";modal.Visible=true;render();Run.RenderStepped:Wait()
  check(content:FindFirstChild("CameraMode",true)==nil,"Settings view toggle remains")
  applyThirdPerson()
  check(p.CameraMode==Enum.CameraMode.Classic and p.CameraMinZoomDistance>=6,"Reapplying camera policy failed")
 end,debug.traceback)
 selected=wasSelected;modal.Visible=wasVisible;if wasVisible then render() end
 print("THIRD_PERSON_RESULT",ok,checks,err or "properties/UI only")
end)
