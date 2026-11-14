-- Append to Bootstrap in disposable Studio. Synthetic mic readiness, actual
-- dev handler / dodge state and server heartbeat; no purchase or live audio.
task.spawn(function()
 task.wait(4)
 local p=game.Players:GetPlayers()[1];local s=sessions[p];assert(s and not s.canSave and Config.MovementPassId==0)
 local checks=0
 local function check(value,message) assert(value,message);checks+=1 end
 local ok,err=xpcall(function()
  check(not Entitlements.HasMovement(p),"Unexpected initial entitlement")
  dev(p,"StudioMovement")
  check(s.testBaseline~=nil,"Entitlement test did not freeze legitimate save baseline")
  check(Entitlements.HasStudioMovement(p) and Entitlements.HasMovement(p),"Test entitlement missing")
  check(Entitlements.CanUseMovement(p,Vector3.new(-600,4,210)),"Safe movement unavailable")
  check(not Entitlements.CanUseMovement(p,Vector3.new(0,4,0)),"Premium movement enabled in arena")
  dev(p,"Hub");s.nextDodge=0
  task.wait(.4)
  -- Same-tick injection: the real client correctly reports its unavailable mic.
  s.micReady=true;dodge(p)
  check(s.premiumRoll and math.abs(s.nextDodge-s.lastDodge-Config.DodgeDuration)<.001,"Safe roll did not use premium recovery: premium="..tostring(s.premiumRoll).." mic="..tostring(s.micReady).." floor="..p.Character.Humanoid.FloorMaterial.Name)
  task.wait(.15)
  p.Character:PivotTo(CFrame.new(0,4,0))
  task.wait(.2)
  check(s.nextDodge>=s.lastDodge+Config.DodgeCooldown,"Arena entry retained premium cooldown")
  check(s.dodgingUntil<=os.clock(),"Arena entry retained premium roll immunity")
  dev(p,"StudioMovement")
  check(not Entitlements.HasMovement(p),"Test entitlement did not clear")
 end,debug.traceback)
 Entitlements.SetStudioMovement(p,false);dev(p,"Hub");s.micReady=false
 workspace:SetAttribute("StudioMovementResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
 print("Studio movement entitlement",ok,checks,err)
end)
