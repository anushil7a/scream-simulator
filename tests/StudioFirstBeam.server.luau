-- Synthetic power through the real server adapter and authored practice geometry.
-- Appended only to a guarded, unsaved local Studio fixture.
task.spawn(function()
 local deadline=os.clock()+60
 repeat task.wait(.1) until workspace:GetAttribute("ProgressionResult") or os.clock()>deadline
 assert(game.PlaceId==0 and localFixture)
 local player=Players:GetPlayers()[1]
 local session=assert(sessions[player]);assert(not session.canSave)
 local character,root=parts(player);assert(character and root)
 local target
 for _,item in ipairs(workspace:GetDescendants()) do
  if item:IsA("BasePart") and item:GetAttribute("MicPracticeTarget")==true then target=item;break end
 end
 assert(target,"Practice target missing")
 local line=assert(target.Parent:FindFirstChild("StandLine"))
 local oldData,oldFrame,oldAnchor=session.data,character:GetPivot(),root.Anchored
 local oldReady,oldProtection,oldDodge,oldKnock=session.micReady,session.protectedUntil,session.dodgingUntil,session.knockedUntil
 local checks=0
 local function check(ok,message) assert(ok,message);checks+=1 end
 local ok,err=xpcall(function()
  session.data=Profiles.Default();session.data.level=1
  session.micReady=true;session.protectedUntil=0;session.dodgingUntil=0;session.knockedUntil=0
  root.Anchored=true
  character:PivotTo(CFrame.lookAt(line.Position+Vector3.new(0,3,0),target.Position))
  session.sustained=sustained.New()
  local now=os.clock()
  local power=require(ReplicatedStorage.Shared.VoiceActivation).OnPower
  check(sustained.Begin(session.sustained,now,{sequence=1,power=power,aim=target.Position},sustainedContext(player,session,now)),"Onset attack rejected")
  stepSustained(player,session,now+.2)
  check(session.data.achievements.FirstBeam==true,"Stand line is outside onset beam reach; first practice hit not confirmed")
  check(require(ReplicatedStorage.Shared.FirstBeamGuide).Text(session.data,true,0,true,false)==nil,"Completion guidance did not clear")
  check(Profiles.Sanitize(session.data).achievements.FirstBeam==true,"Completion lost during sanitization")
  local pulse=target:GetAttribute("PracticePulse")
  check(sustained.Pulse(session.sustained,now+.25,{sequence=1,sample=1,power=power,aim=target.Position},sustainedContext(player,session,now+.25)),"Follow-up pulse rejected")
  stepSustained(player,session,now+.4)
  check(target:GetAttribute("PracticePulse")==pulse,"Repeated completion within one attack")
  session.micReady=false;cancelSustained(player,session,now+.41)
  stepSustained(player,session,now+.6)
  check(not session.sustained.protocol.active and target:GetAttribute("PracticePulse")==pulse,"Interrupted input retained attack")
 end,debug.traceback)
 cancelSustained(player,session,os.clock())
 session.data=oldData;session.sustained=sustained.New()
 session.micReady=oldReady;session.protectedUntil=oldProtection;session.dodgingUntil=oldDodge;session.knockedUntil=oldKnock
 character:PivotTo(oldFrame);root.Anchored=oldAnchor
 local result=game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil,sourceSha256=workspace:GetAttribute("ReviewSourceSha256")})
 workspace:SetAttribute("FirstBeamResult",result);print("FIRST_BEAM_NATIVE",result)
end)
