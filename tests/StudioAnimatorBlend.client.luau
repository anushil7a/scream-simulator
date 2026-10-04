-- Append to production RunAnimation in a disposable Studio copy.
-- Uses the current real avatar with its default Animate/Animator still active.
-- Attribute-driven poses are synthetic, not physical controls or mic input.
task.spawn(function()
 assert(Run:IsStudio() and game.PlaceId==0)
 local player=Players.LocalPlayer
 local character=player.Character or player.CharacterAdded:Wait()
 local checks=0;local samples={};local original={}
 local names={"CaptureStarted","DodgeStarted","DodgeEnds","ScreamReleased"}
 for _,name in names do original[name]=player:GetAttribute(name) end
 local function check(value,message) assert(value,message);checks+=1 end
 local ok,err=xpcall(function()
  local deadline=os.clock()+20
  repeat task.wait(.1) until rigs[player] or os.clock()>deadline
  local rig=assert(rigs[player],"Missing animation rig")
  local animate=character:FindFirstChild("Animate")
  check(animate and animate.Enabled,"Default Animate must remain enabled")
  local animator=assert(rig.humanoid:FindFirstChildOfClass("Animator"),"Missing Animator")
  task.wait(2)
  check(#animator:GetPlayingAnimationTracks()>0,"No base animation playing")
  for cycle=1,8 do
   player:SetAttribute("CaptureStarted",workspace:GetServerTimeNow())
   task.wait(.35)
   check(rig.charge>.9,"Charge did not blend in")
   player:SetAttribute("CaptureStarted",0)
   local now=workspace:GetServerTimeNow()
   player:SetAttribute("DodgeStarted",now);player:SetAttribute("DodgeEnds",now+Config.DodgeDuration)
   task.wait(Config.DodgeDuration*.5)
   check((character:GetAttribute("RollAnimationProgress") or -1)>0,"Roll did not animate")
   check(#animator:GetPlayingAnimationTracks()>0,"Roll stopped base Animator")
   task.wait(Config.DodgeDuration*.6)
   player:SetAttribute("DodgeEnds",0);player:SetAttribute("DodgeStarted",0)
   player:SetAttribute("ScreamReleased",workspace:GetServerTimeNow())
   task.wait(.8)
   local maxPosition,maxAngle=0,0
   for _,offset in rig.offsets do
    maxPosition=math.max(maxPosition,offset.Position.Magnitude)
    local _,angle=offset:ToAxisAngle();maxAngle=math.max(maxAngle,math.abs(angle))
   end
   check(rig.charge<.002 and maxPosition<.002 and maxAngle<.002,"Additive pose failed to settle")
   check(character:GetAttribute("RollAnimationProgress")==-1,"Roll state did not recover")
   table.insert(samples,{cycle=cycle,tracks=#animator:GetPlayingAnimationTracks(),residualAngle=maxAngle,residualPosition=maxPosition})
  end
  check(animate.Enabled and #animator:GetPlayingAnimationTracks()>0,"Base animation lost after repeated actions")
 end,debug.traceback)
 for _,name in names do player:SetAttribute(name,original[name]) end
 local result={passed=ok,checks=checks,rig=character:FindFirstChildOfClass("Humanoid").RigType.Name,samples=samples,error=not ok and tostring(err) or nil}
 workspace:SetAttribute("AnimatorBlendResult",game:GetService("HttpService"):JSONEncode(result))
 print("Animator blend regression",ok,checks,err)
end)
