-- Appended only in VoiceTransportReview, never the production candidate.
assert(RunService:IsStudio() and game.PlaceId==0 and localFixture)
local transportProbe=Instance.new("RemoteFunction")
transportProbe.Name="VoiceTransportProbe";transportProbe.Parent=remotes
local transportOwner,transportSaved,transportTarget
local transportReceived={};local transportCounts={}
local transportBeamSteps=0;local transportBeamSequence
local transportResolve=resolveSustained
resolveSustained=function(ctx,direction,stats,now)
 local ids,details,beam=transportResolve(ctx,direction,stats,now)
 if ctx.player==transportOwner and transportTarget and beam.obstruction and beam.obstruction.Instance==transportTarget then
  transportBeamSteps+=1
  local active=sessions[transportOwner].sustained.protocol.active
  transportBeamSequence=active and active.sequence
 end
 return ids,details,beam
end
local transportAudit={};local transportOriginals={}
local function transportScalar(value)
 if type(value)=="number" and (value~=value or math.abs(value)==math.huge) then return "nonfinite" end
 return type(value)=="number" and value or nil
end
local function transportStateSnapshot(s)
 local a=s.protocol.active;local intent=s.intent;local aim=intent and intent.aim
 return {active=a~=nil,sequence=a and a.sequence,power=a and a.power,
  aimX=aim and aim.X,aimY=aim and aim.Y,aimZ=aim and aim.Z,sample=intent and intent.sample,
  lastPulse=a and a.lastPulse,started=a and a.started,nextStart=s.protocol.nextStart,lastSequence=s.protocol.lastSequence}
end
-- Observe inside each actual handler adapter call, without yielding. Copies survive
-- later valid pulses. The wrapper forwards all arguments and return values unchanged.
for _,operation in ipairs({"Begin","Pulse","Stop"}) do
 local original=sustained[operation];transportOriginals[operation]=original
 sustained[operation]=function(s,now,request,...)
  local watched=transportOwner and sessions[transportOwner] and sessions[transportOwner].sustained==s
  local before=watched and transportStateSnapshot(s)
  local result=table.pack(original(s,now,request,...))
  if watched and #transportAudit<256 then
   local ended;if operation=="Stop" then ended=result[1] else ended=result[3] end
   table.insert(transportAudit,{id=#transportAudit+1,operation=operation,now=now,
    requestKind=type(request),sequence=transportScalar(type(request)=="table" and request.sequence or request),
    sample=type(request)=="table" and transportScalar(request.sample) or nil,
    accepted=operation=="Stop" and ended~=nil or result[1]==true,reason=result[2],
    ended=ended and table.clone(ended),before=before,after=transportStateSnapshot(s)})
  end
  return table.unpack(result,1,result.n)
 end
end
local transportObserver=action.OnServerEvent:Connect(function(player,verb,arg)
 if player~=transportOwner then return end
 local name=type(verb)=="string" and verb or "nonstring"
 transportCounts[name]=(transportCounts[name] or 0)+1
 if #transportReceived<256 then
  table.insert(transportReceived,{verb=name,sequence=type(arg)=="table" and arg.sequence or nil,sample=type(arg)=="table" and arg.sample or nil})
 end
end)
local function transportRestore()
 if not transportSaved then return end
 local player=transportOwner;local s=sessions[player];local c,r=parts(player)
 if s then
  cancelSustained(player,s,os.clock());s.sustained=sustained.New()
  s.data=transportSaved.data;s.micReady=transportSaved.micReady
  s.protectedUntil=transportSaved.protectedUntil;s.dodgingUntil=transportSaved.dodgingUntil;s.knockedUntil=transportSaved.knockedUntil
  for name,saved in pairs(transportSaved.attributes) do player:SetAttribute(name,saved.value) end
  state(player)
 end
 if c and r then c:PivotTo(transportSaved.frame);r.Anchored=transportSaved.anchored end
 if transportTarget then transportTarget:Destroy();transportTarget=nil end
 resolveSustained=transportResolve
 transportSaved=nil
end
transportProbe.OnServerInvoke=function(player,verb,report)
 assert(localFixture and game.PlaceId==0 and RunService:IsStudio())
 local s=assert(sessions[player]);assert(not s.canSave)
 if verb=="prepare" then
  assert(not transportOwner,"One fixture run per session")
  transportOwner=player
  local c,r=parts(player);assert(c and r)
  transportTarget=Instance.new("Part");transportTarget.Name="VoiceTransportFixtureCover"
  transportTarget.Anchored=true;transportTarget.Size=Vector3.new(10,10,1)
  transportTarget.CFrame=CFrame.new(0,505,-5);transportTarget.Parent=workspace
  transportSaved={data=s.data,micReady=s.micReady,protectedUntil=s.protectedUntil,dodgingUntil=s.dodgingUntil,knockedUntil=s.knockedUntil,frame=c:GetPivot(),anchored=r.Anchored,attributes={}}
  for _,name in ipairs({"ProtectionEnds","DodgeEnds","KnockdownEnds","SustainedActive","SustainedSequence","SustainedEndsAt","SustainedReadyAt"}) do
   transportSaved.attributes[name]={value=player:GetAttribute(name)}
   local initial=0;if name=="SustainedActive" then initial=false end
   player:SetAttribute(name,initial)
  end
  s.data=Profiles.Default();s.sustained=sustained.New();s.micReady=false
  s.protectedUntil=0;s.dodgingUntil=0;s.knockedUntil=0
  r.Anchored=true
  c:PivotTo(CFrame.lookAt(Vector3.new(0,503,0),transportTarget.Position))
  state(player)
  task.delay(120,function() if transportSaved then transportRestore();warn("VOICE_TRANSPORT_TIMEOUT") end end)
  return {aim=transportTarget.Position,sourceSha256=workspace:GetAttribute("ReviewSourceSha256")}
 end
 assert(player==transportOwner and transportSaved,"Fixture is not active")
 if verb=="snapshot" then
  local a=s.sustained.protocol.active
  return {active=a~=nil,sequence=a and a.sequence,power=a and a.power,sample=s.sustained.intent and s.sustained.intent.sample,
   aim=s.sustained.intent and s.sustained.intent.aim,lastSequence=s.sustained.protocol.lastSequence,
   cooldown=math.max(0,s.sustained.protocol.nextStart-os.clock()),micReady=s.micReady,eligible=sustainedContext(player,s,os.clock())~=nil,
   beamSteps=transportBeamSteps,beamSequence=transportBeamSequence,retiredAchievement=s.data.achievements.FirstBeam==true,
   received=#transportReceived,counts=table.clone(transportCounts),auditCount=#transportAudit}
 elseif verb=="audit" then
  local cursor=tonumber(report) or 0
  local result={};for _,entry in ipairs(transportAudit) do if entry.id>cursor then table.insert(result,entry) end end
  return result
 elseif verb=="finish" then
  assert(type(report)=="table")
  report.sourceSha256=workspace:GetAttribute("ReviewSourceSha256")
  report.serverCounts=transportCounts;report.savingDisabled=not s.canSave
  transportRestore();transportObserver:Disconnect()
  for operation,original in pairs(transportOriginals) do sustained[operation]=original end
  local encoded=game:GetService("HttpService"):JSONEncode(report)
  workspace:SetAttribute("VoiceTransportResult",encoded);print("VOICE_TRANSPORT_NATIVE",encoded)
  -- Studio truncates long log lines; retain the complete report in bounded chunks.
  local chunks=math.ceil(#encoded/700)
  for index=1,chunks do print("VOICE_TRANSPORT_EVIDENCE",index,chunks,string.sub(encoded,(index-1)*700+1,index*700)) end
  return true
 end
 error("Unknown fixture probe verb")
end
