-- Appended to the ACTUAL Client only in a guarded disposable fixture.
-- Replaces microphone source and aim only. RenderStepped, Controls, Action,
-- OnServerEvent, server loop, State and acknowledgement attributes stay native.
assert(Run:IsStudio() and game.PlaceId==0)
task.spawn(function()
 local probe=remotes:WaitForChild("VoiceTransportProbe",20);assert(probe)
 local checks=0;local sent={};local stages={};local started=os.clock()
 local function check(value,message) assert(value,message);checks+=1 end
 local function waitFor(predicate,seconds,message)
  local limit=os.clock()+seconds
  repeat if predicate() then return end;task.wait(.05) until os.clock()>limit
  error(message)
 end
 local function snapshot() return probe:InvokeServer("snapshot") end
 local function stage(name) table.insert(stages,{name=name,elapsed=os.clock()-started}) end
 local source;local replayEvidence={};local quietStopEvidence;local toggleStopEvidence
 local function unchangedRejection(entry,reason)
  if entry then table.insert(replayEvidence,entry) end
  check(entry~=nil and not entry.accepted and entry.reason==reason and entry.ended==nil,"Replay was not explicitly rejected: "..reason)
  check(entry.before.active and entry.before.sequence==2,"Replay did not exercise the active attack")
  for _,key in ipairs({"active","sequence","power","aimX","aimY","aimZ","sample","lastPulse","started","nextStart","lastSequence"}) do
   assert(entry.before[key]==entry.after[key],"Replay mutated immediate server state: "..key)
  end
  checks+=1
 end
 local ok,err=xpcall(function()
  waitFor(function() return p.Character and p.Character:FindFirstChild("HumanoidRootPart") end,20,"Character unavailable")
  mic:Destroy();mic.status="SYNTHETIC TRANSPORT TEST - no real microphone";mic.power=0;mic.ready=false
  local setup=probe:InvokeServer("prepare");source=setup.sourceSha256
  check(sustainedControl~=nil,"Actual client automatic control missing")
  sustainedControl.getAim=function() return setup.aim end
  local nativeSend=sustainedControl.send
  sustainedControl.send=function(verb,arg)
   table.insert(sent,{verb=verb,time=os.clock(),sequence=type(arg)=="table" and arg.sequence or arg,sample=type(arg)=="table" and arg.sample or nil,ack=p:GetAttribute("SustainedActive")==true and p:GetAttribute("SustainedSequence")==sustainedControl.sequence})
   nativeSend(verb,arg)
  end
  windowFocused=true -- fixture focus, not a physical keyboard/focus test
  mic.ready=true;mic.power=0
  waitFor(function() return data.micReady and sustainedControl.armed end,6,"Readiness did not round trip")
  check(snapshot().eligible,"Malformed-input tests require an eligible server context")
  stage("malformed")
  local baseline=snapshot().received
  action:FireServer({},nil)
  action:FireServer("SustainedBegin","bad request")
  action:FireServer("SustainedBegin",{sequence=0,power=.5,aim=setup.aim})
  action:FireServer("SustainedBegin",{sequence=0/0,power=.5,aim=setup.aim})
  action:FireServer("SustainedBegin",{sequence=1,power=0/0,aim=setup.aim})
  task.wait(.2)
  local invalid=snapshot()
  check(invalid.received>=baseline+5,"Malformed messages did not reach native Action")
  check(not invalid.active and not invalid.firstBeam and invalid.cooldown==0,"Malformed begin mutated combat")
  check(invalid.lastSequence==1,"Invalid consumed sequence not recorded")
  -- The real client next sends sequence 1; replay rejection must time out safely.
  task.wait(.35);mic.power=.5
  waitFor(function() return (sustainedControl.unconfirmedUntil or 0)>os.clock() end,4,"Replayed client begin did not expose acknowledgement timeout")
  check(not snapshot().active and not snapshot().firstBeam,"Rejected begin produced a practice hit")
  check(#sent==2 and sent[1].verb=="SustainedBegin" and sent[2].verb=="SustainedStop","Unacknowledged begin sent pulses or repeated stop")
  stage("scheduled attack")
  mic.power=0;task.wait(.4);mic.power=.5
  waitFor(function() return p:GetAttribute("SustainedActive")==true and p:GetAttribute("SustainedSequence")==2 end,4,"Fresh quiet retry was not acknowledged")
  waitFor(function() local v=snapshot();return v.firstBeam and (v.sample or 0)>=3 end,3,"Actual scheduler/server loop did not confirm practice hit")
  local active=snapshot();check(active.sequence==2 and active.power==.5,"Accepted attack state incorrect")
  local pulses={}
  for _,entry in ipairs(sent) do if entry.verb=="SustainedPulse" then table.insert(pulses,entry);check(entry.ack,"Client pulsed before replicated acknowledgement") end end
  check(#pulses>=3,"Too few scheduled pulses observed")
  for i=2,#pulses do check(pulses[i].sample==pulses[i-1].sample+1 and pulses[i].time-pulses[i-1].time>=.12,"Pulse cadence/sample ordering regressed") end
  -- Immutable in-call server snapshots prevent later valid pulses masking a mutation.
  local replayCursor=snapshot().auditCount
  -- Replays and malformed sample/aim fields traverse the real remote handler.
  action:FireServer("SustainedBegin",{sequence=2,power=1,aim=setup.aim})
  action:FireServer("SustainedPulse",{sequence=2,sample=1,power=1,aim=Vector3.new(0,0,0)})
  action:FireServer("SustainedPulse","bad request")
  action:FireServer("SustainedPulse",{sequence=2,sample=0/0,power=1,aim=setup.aim})
  action:FireServer("SustainedStop",1)
  local replayRecords
  waitFor(function()
   replayRecords=probe:InvokeServer("audit",replayCursor)
   for _,entry in ipairs(replayRecords) do if entry.operation=="Stop" and entry.sequence==1 then return true end end
   return false
  end,2,"Replay batch did not reach the server adapter")
  local beginReplay,pulseReplay,badRequest,badSample,staleStop
  for _,entry in ipairs(replayRecords) do
   if entry.operation=="Begin" and entry.sequence==2 then beginReplay=entry
   elseif entry.operation=="Pulse" and entry.sample==1 then pulseReplay=entry
   elseif entry.operation=="Pulse" and entry.requestKind=="string" then badRequest=entry
   elseif entry.operation=="Pulse" and entry.sample=="nonfinite" then badSample=entry
   elseif entry.operation=="Stop" and entry.sequence==1 then staleStop=entry end
  end
  unchangedRejection(beginReplay,"replay")
  unchangedRejection(pulseReplay,"sample")
  unchangedRejection(badRequest,"sequence")
  unchangedRejection(badSample,"sample")
  unchangedRejection(staleStop,"sequence")
  check(snapshot().practicePulse==active.practicePulse,"Repeated practice feedback within one attack")
  -- Fresh but invalid aim must cancel, rather than extending the active beam.
  action:FireServer("SustainedPulse",{sequence=2,sample=1000,power=.5,aim=Vector3.new(0/0,0,0)})
  waitFor(function() return not snapshot().active end,2,"Invalid aim did not cancel active attack")
  local ended=snapshot();check(ended.cooldown>3 and ended.cooldown<=5,"Cancellation failed to establish cooldown")
  waitFor(function() return not sustainedControl.attack end,2,"Client retained server-cancelled attack")
  stage("cooldown rejection")
  -- This consumes sequence 3. The real client later collides with it and retries.
  action:FireServer("SustainedBegin",{sequence=3,power=.5,aim=setup.aim})
  task.wait(.2)
  local cooling=snapshot()
  check(not cooling.active and cooling.lastSequence==3 and cooling.cooldown>2,"New sequence bypassed cooldown")
  local beginCount=0;for _,v in ipairs(sent) do if v.verb=="SustainedBegin" then beginCount+=1 end end
  waitFor(function() return (p:GetAttribute("SustainedReadyAt") or 0)<=workspace:GetServerTimeNow() end,7,"Real cooldown did not expire")
  task.wait(.4)
  local afterCount=0;for _,v in ipairs(sent) do if v.verb=="SustainedBegin" then afterCount+=1 end end
  check(afterCount==beginCount,"Held voice restarted at cooldown expiry")
  mic.power=0;task.wait(.4);mic.power=.5
  waitFor(function() return sustainedControl.sequence==3 and (sustainedControl.unconfirmedUntil or 0)>os.clock() end,4,"Consumed cooldown sequence did not reject safely")
  mic.power=0;task.wait(.4);mic.power=.5
  waitFor(function() return p:GetAttribute("SustainedActive")==true and p:GetAttribute("SustainedSequence")==4 end,4,"Cooldown recovery retry not acknowledged")
  waitFor(function() return snapshot().practicePulse>active.practicePulse end,2,"Recovered attack did not reach target")
  stage("availability interruption")
  mic.ready=false;mic.power=0
  waitFor(function() local v=snapshot();return not v.micReady and not v.active and not sustainedControl.armed end,3,"Availability loss did not traverse MicReady/Stop and disarm")
  local interrupted=snapshot();local sentAtInterrupt=#sent
  mic.ready=true;mic.power=.5
  waitFor(function() return data.micReady end,3,"Restored readiness did not round trip")
  waitFor(function() return (p:GetAttribute("SustainedReadyAt") or 0)<=workspace:GetServerTimeNow() end,12,"Interruption cooldown did not expire")
  task.wait(.3)
  check(not sustainedControl.armed and #sent==sentAtInterrupt and not snapshot().active,"Restored availability silently resumed")
  toggleVoice();task.wait(.4)
  check(sustainedControl.armed and not snapshot().active,"Manual resume bypassed fresh quiet")
  mic.power=0;task.wait(.4);mic.power=.5
  waitFor(function() return p:GetAttribute("SustainedActive")==true and p:GetAttribute("SustainedSequence")==5 end,4,"Manual resume/fresh quiet recovery failed")
  waitFor(function() return snapshot().practicePulse>interrupted.practicePulse end,2,"Final recovered attack missed practice target")
  local stopCursor=snapshot().auditCount
  mic.power=0
  waitFor(function()
   for _,entry in ipairs(probe:InvokeServer("audit",stopCursor)) do
    if entry.operation=="Stop" and entry.sequence==5 then quietStopEvidence=entry;return true end
   end
   return false
  end,1.5,"No explicit quiet SustainedStop reached the server")
  local stop=quietStopEvidence
  check(stop.accepted and stop.ended and stop.ended.reason=="stop" and stop.ended.sequence==5 and stop.before.active and stop.before.sequence==5 and not stop.after.active,"Quiet stop was not an explicit accepted stop")
  check(stop.now<stop.before.lastPulse+sustainedRules.InputTimeout and stop.now<stop.before.started+sustainedRules.MaxDuration,"Quiet stop arrived after an expiry deadline")
  local stopSends=0;for _,entry in ipairs(sent) do if entry.verb=="SustainedStop" and entry.sequence==5 then stopSends+=1 end end
  check(stopSends==1,"Quiet transition did not send exactly one matching stop")
  check(not sustainedControl.attack and snapshot().cooldown>7,"Quiet-stop acknowledgement or cooldown missing")
  local finalPulse=snapshot().practicePulse;task.wait(.4)
  check(snapshot().practicePulse==finalPulse,"Practice hit continued after quiet stop")
  stage("screams toggle")
  waitFor(function() return (p:GetAttribute("SustainedReadyAt") or 0)<=workspace:GetServerTimeNow() end,12,"Toggle setup cooldown did not expire")
  mic.power=0;task.wait(.4);mic.power=.5
  waitFor(function() local v=snapshot();return v.active and v.sequence==6 and (v.sample or 0)>=1 end,4,"Toggle setup attack did not start")
  local toggleCursor=snapshot().auditCount
  toggleVoice()
  check(not sustainedControl.armed and not sustainedControl.attack and mic.ready and mic.power==.5,"OFF altered mic readiness/input or retained local attack")
  waitFor(function()
   for _,entry in ipairs(probe:InvokeServer("audit",toggleCursor)) do
    if entry.operation=="Stop" and entry.sequence==6 then toggleStopEvidence=entry;return true end
   end
   return false
  end,1.5,"Toggle OFF did not deliver an explicit SustainedStop")
  local toggleStop=toggleStopEvidence
  check(toggleStop.accepted and toggleStop.ended and toggleStop.ended.reason=="stop" and toggleStop.before.active and not toggleStop.after.active,"Toggle OFF did not explicitly stop server combat")
  check(toggleStop.now<toggleStop.before.lastPulse+sustainedRules.InputTimeout and toggleStop.now<toggleStop.before.started+sustainedRules.MaxDuration,"Toggle stop was masked by server expiry")
  local toggleSends=0;for _,entry in ipairs(sent) do if entry.verb=="SustainedStop" and entry.sequence==6 then toggleSends+=1 end end
  check(toggleSends==1 and snapshot().micReady,"Toggle duplicated stop or disabled server mic readiness")
  local toggleCount=#sent;local readyAt=p:GetAttribute("SustainedReadyAt")
  check(snapshot().cooldown>8,"Toggle OFF lost cooldown")
  toggleVoice();mic.power=0;task.wait(.4);mic.power=.5;task.wait(.4)
  check(sustainedControl.armed and #sent==toggleCount and not snapshot().active and p:GetAttribute("SustainedReadyAt")==readyAt,"Toggle ON bypassed or reset cooldown")
  toggleVoice()
  waitFor(function() return (p:GetAttribute("SustainedReadyAt") or 0)<=workspace:GetServerTimeNow() end,12,"Toggle cooldown did not expire")
  mic.power=0;task.wait(.4);mic.power=.5;task.wait(.4)
  check(not sustainedControl.armed and #sent==toggleCount and not snapshot().active and snapshot().micReady,"OFF restarted on speech/cooldown expiry or changed readiness")
  stage("complete")
 end,debug.traceback)
 mic.ready=false;mic.power=0;sustainedControl:SetArmed(false)
 local report={passed=ok,checks=checks,error=not ok and tostring(err) or nil,elapsed=os.clock()-started,stages=stages,sourceSha256=source,scheduledMessages=#sent,replayEvidence=replayEvidence,quietStopEvidence=quietStopEvidence,toggleStopEvidence=toggleStopEvidence}
 local saved,saveError=pcall(function() return probe:InvokeServer("finish",report) end)
 if not saved then warn("VOICE_TRANSPORT_REPORT_FAILED",saveError) end
 print("VOICE_TRANSPORT_CLIENT",game:GetService("HttpService"):JSONEncode(report))
end)
