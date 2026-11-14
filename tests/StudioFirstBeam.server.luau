-- Synthetic power through the real server adapter and a fixture-owned cover target.
-- No production mic-practice area, quest, or achievement is recreated.
-- Appended only to a guarded, unsaved local Studio fixture.
task.spawn(function()
 local deadline=os.clock()+60
 repeat task.wait(.1) until workspace:GetAttribute("ProgressionResult") or os.clock()>deadline
 assert(game.PlaceId==0 and localFixture)
 local player=Players:GetPlayers()[1]
 local session=assert(sessions[player]);assert(not session.canSave)
 local character,root=parts(player);assert(character and root)
 local target=Instance.new("Part");target.Name="FixtureBeamCover";target.Anchored=true
 target.Size=Vector3.new(10,10,1);target.CFrame=CFrame.new(0,505,-5);target.Parent=workspace
 local originalResolve=resolveSustained;local contactSteps=0
 resolveSustained=function(ctx,direction,stats,now)
  local ids,details,beam=originalResolve(ctx,direction,stats,now)
  if ctx.player==player and beam.obstruction and beam.obstruction.Instance==target then contactSteps+=1 end
  return ids,details,beam
 end
 local oldData,oldFrame,oldAnchor=session.data,character:GetPivot(),root.Anchored
 local oldReady,oldProtection,oldDodge,oldKnock=session.micReady,session.protectedUntil,session.dodgingUntil,session.knockedUntil
 local oldActive,oldReadyAt=player:GetAttribute("SustainedActive"),player:GetAttribute("SustainedReadyAt")
 local Gate=require(ReplicatedStorage.Shared.VoiceActivation)
 local checks=0
 local function check(ok,message) assert(ok,message);checks+=1 end
 local ok,err=xpcall(function()
  session.data=Profiles.Default();session.data.level=1
  session.micReady=true;session.protectedUntil=0;session.dodgingUntil=0;session.knockedUntil=0
  root.Anchored=true
  character:PivotTo(CFrame.lookAt(Vector3.new(0,503,0),target.Position))
  session.sustained=sustained.New()
  local now=os.clock()
  local power=Gate.OnPower
  check(sustained.Begin(session.sustained,now,{sequence=1,power=power,aim=target.Position},sustainedContext(player,session,now)),"Onset attack rejected")
  stepSustained(player,session,now+.2)
  check(contactSteps==1,"Onset beam did not resolve fixture cover")
  check(session.data.achievements.FirstBeam~=true,"Retired practice achievement was granted")
  check(Profiles.Sanitize(session.data).achievements.FirstBeam~=true,"Sanitization created retired achievement")
  local pulse=contactSteps
  check(sustained.Pulse(session.sustained,now+.25,{sequence=1,sample=1,power=power,aim=target.Position},sustainedContext(player,session,now+.25)),"Follow-up pulse rejected")
  stepSustained(player,session,now+.4)
  check(contactSteps>pulse,"Follow-up step did not resolve fixture cover");pulse=contactSteps
  session.micReady=false;cancelSustained(player,session,now+.41)
  stepSustained(player,session,now+.6)
  check(not session.sustained.protocol.active and contactSteps==pulse,"Interrupted input retained attack")

  -- A distinct second attack keeps the existing protocol/cooldown/sequence state.
  -- At OffPower the client has a short quiet grace period, not indefinite sustain.
  -- No native time or mic sample is implied by these injected gate/server times.
  session.micReady=true;session.data.achievements.FirstBeam=nil
  now=session.sustained.protocol.nextStart+.01
  local gate=Gate.new()
  for _=1,2 do gate:Step(.1,0,true,true,true) end
  local onset
  for _=1,3 do onset=gate:Step(.1,Gate.OnPower,true,true,true) end
  check(onset=="start","Fresh quiet/onset did not arm the second attack")
  check(sustained.Begin(session.sustained,now,{sequence=2,power=Gate.OnPower,aim=target.Position},sustainedContext(player,session,now)),"Second attack rejected after cooldown")
  check(gate:Step(.1,Gate.OffPower,true,true,true)==nil and gate.active,"Boundary power ended before quiet grace")
  check(sustained.Pulse(session.sustained,now+.1,{sequence=2,sample=1,power=Gate.OffPower,aim=target.Position},sustainedContext(player,session,now+.1)),"Boundary pulse rejected")
  check(session.sustained.protocol.active.power==Gate.OffPower,"Boundary test retained onset power")
  stepSustained(player,session,now+.2)
  check(session.data.achievements.FirstBeam~=true and contactSteps==pulse+1,"Second attack did not hit at exact boundary power")
  pulse=contactSteps
  local lowSustain=Gate.OffPower+.001
  check(gate:Step(.1,lowSustain,true,true,true)==nil and gate.active,"Power above cutoff did not clear quiet accumulation")
  check(sustained.Pulse(session.sustained,now+.3,{sequence=2,sample=2,power=lowSustain,aim=target.Position},sustainedContext(player,session,now+.3)),"Low sustained pulse rejected")
  stepSustained(player,session,now+.4)
  check(session.sustained.protocol.active~=nil and contactSteps>pulse,"Low sustain failed to resolve fixture cover");pulse=contactSteps
  local firstQuiet=gate:Step(.1,Gate.OffPower,true,true,true)
  local secondQuiet=gate:Step(.1,Gate.OffPower,true,true,true)
  check(firstQuiet==nil and secondQuiet=="stop","Exact cutoff did not stop after fresh quiet interval")
  local ended=sustained.Stop(session.sustained,now+.5,2)
  check(ended~=nil and ended.reason=="stop","Quiet stop did not end the second server attack")
  sustainedEnd(player,ended,now+.5)
  stepSustained(player,session,now+.7)
  check(not session.sustained.protocol.active and contactSteps==pulse,"Quiet stop retained attack or added practice feedback")
 end,debug.traceback)
 resolveSustained=originalResolve;target:Destroy()
 cancelSustained(player,session,math.max(os.clock(),session.sustained.protocol.time))
 session.data=oldData;session.sustained=sustained.New()
 session.micReady=oldReady;session.protectedUntil=oldProtection;session.dodgingUntil=oldDodge;session.knockedUntil=oldKnock
 character:PivotTo(oldFrame);root.Anchored=oldAnchor
 player:SetAttribute("SustainedActive",oldActive);player:SetAttribute("SustainedReadyAt",oldReadyAt);state(player)
 local result=game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,scope="synthetic adapter/geometry and interruption; no microphone or practice quest",boundaryPower=Gate.OffPower,lowSustainPower=Gate.OffPower+.001,error=not ok and tostring(err) or nil,sourceSha256=workspace:GetAttribute("ReviewSourceSha256")})
 workspace:SetAttribute("FirstBeamResult",result);print("FIRST_BEAM_NATIVE",result)
end)
