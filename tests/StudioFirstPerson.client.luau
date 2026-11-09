-- Append to Client only in an unpublished Studio copy. Exercises real camera
-- properties/rendered reticle with synthetic mic readiness; no voice pass.
task.spawn(function()
 assert(game.PlaceId==0 and Run:IsStudio())
 task.wait(7)
 local original=mic;local checks=0;local cancels=0
 local fake={ready=true,power=0,status="Camera fixture"}
 function fake:Cancel() cancels+=1;self.captureStarted=nil end
 function fake:Begin() self.captureStarted=os.clock();return true end
 function fake:CapturePower() return 0 end
 local function check(value,message) assert(value,message);checks+=1 end
 local ok,err=xpcall(function()
  mic=fake;modal.Visible=false;devPanel.Visible=false;conversationPanel.Visible=false
  local camera=workspace.CurrentCamera
  check(not firstPerson,"Expected default third person")
  if sustainedControl then
   sustainedControl:SetArmed(true)
   sustainedControl.attack={sequence=1};sustainedControl.gate.active=true
  else captureSource="fixture";fake.captureStarted=os.clock() end
  toggleCamera();task.wait(.4)
  check(firstPerson and p.CameraMode==Enum.CameraMode.LockFirstPerson,"First person not applied")
  if sustainedControl then
   check(sustainedControl.attack==nil and sustainedControl.gate.needsQuiet,"View switch retained automatic attack")
  else check(captureSource==nil and fake.captureStarted==nil and cancels>0,"Switch retained pending attack") end
  check(reticle.Visible and viewButton.Text=="3RD [V]","First person HUD missing")
  local ray=aimRay()
  check(ray.Direction:Dot(camera.CFrame.LookVector)>.99999,"Attack ray does not match camera center")
  -- AbsolutePosition includes the ScreenGui's coordinate origin (-top inset
  -- for a fullscreen GUI). Compare in viewport coordinates.
  local center=reticle.AbsolutePosition+reticle.AbsoluteSize/2-aimGui.AbsolutePosition
  check((center-camera.ViewportSize/2).Magnitude<1,"Crosshair is offset by GUI inset")
  check(modal.Close.Modal and micPanel.Calibrate.Modal and conversationPanel.Close.Modal and testContent.XP.Modal,"Overlay cursor gates missing")
  selected="Settings";modal.Visible=true;render();task.wait(.1)
  check(not reticle.Visible and content:FindFirstChild("Card")~=nil,"Menu did not hide crosshair")
  toggleCamera();task.wait(.3)
  check(not firstPerson and p.CameraMode==Enum.CameraMode.Classic,"Third person not restored")
  check(p.CameraMinZoomDistance==originalMinZoom,"Temporary zoom limit leaked")
  local found=false;for _,v in content:GetDescendants() do if v:IsA("TextButton") and v.Name=="CameraMode" then found=v.Text=="VIEW: THIRD PERSON" end end
  check(found,"Settings camera toggle is stale")
  -- Rapid view switches must not let an older deferred restore overwrite state.
  toggleCamera();toggleCamera();toggleCamera();task.wait(.2)
  check(firstPerson and p.CameraMode==Enum.CameraMode.LockFirstPerson,"Rapid toggles lost first person")
  toggleCamera();task.wait(.2)
  check(p.CameraMinZoomDistance==originalMinZoom,"Rapid toggles leaked zoom minimum")
 end,debug.traceback)
 if firstPerson then toggleCamera() end
 modal.Visible=false;mic=original;original:Cancel()
 workspace:SetAttribute("FirstPersonResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
end)
