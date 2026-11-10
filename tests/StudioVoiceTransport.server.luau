-- Appended only in VoiceTransportReview, never the production candidate.
assert(RunService:IsStudio() and game.PlaceId==0 and localFixture)
local transportProbe=Instance.new("RemoteFunction")
transportProbe.Name="VoiceTransportProbe";transportProbe.Parent=remotes
local transportOwner,transportSaved,transportTarget
local transportReceived={};local transportCounts={}
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
 transportSaved=nil
end
transportProbe.OnServerInvoke=function(player,verb,report)
 assert(localFixture and game.PlaceId==0 and RunService:IsStudio())
 local s=assert(sessions[player]);assert(not s.canSave)
 if verb=="prepare" then
  assert(not transportOwner,"One fixture run per session")
  transportOwner=player
  local c,r=parts(player);assert(c and r)
  for _,obj in ipairs(workspace:GetDescendants()) do
   if obj:IsA("BasePart") and obj:GetAttribute("MicPracticeTarget")==true then transportTarget=obj;break end
  end
  assert(transportTarget)
  transportSaved={data=s.data,micReady=s.micReady,protectedUntil=s.protectedUntil,dodgingUntil=s.dodgingUntil,knockedUntil=s.knockedUntil,frame=c:GetPivot(),anchored=r.Anchored,attributes={}}
  for _,name in ipairs({"ProtectionEnds","DodgeEnds","KnockdownEnds","SustainedActive","SustainedSequence","SustainedEndsAt","SustainedReadyAt"}) do
   transportSaved.attributes[name]={value=player:GetAttribute(name)}
   local initial=0;if name=="SustainedActive" then initial=false end
   player:SetAttribute(name,initial)
  end
  s.data=Profiles.Default();s.sustained=sustained.New();s.micReady=false
  s.protectedUntil=0;s.dodgingUntil=0;s.knockedUntil=0
  r.Anchored=true
  local line=assert(transportTarget.Parent:FindFirstChild("StandLine"))
  c:PivotTo(CFrame.lookAt(line.Position+Vector3.new(0,3,0),transportTarget.Position))
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
   practicePulse=transportTarget:GetAttribute("PracticePulse") or 0,firstBeam=s.data.achievements.FirstBeam==true,
   received=#transportReceived,counts=table.clone(transportCounts)}
 elseif verb=="finish" then
  assert(type(report)=="table")
  report.sourceSha256=workspace:GetAttribute("ReviewSourceSha256")
  report.serverCounts=transportCounts;report.savingDisabled=not s.canSave
  transportRestore();transportObserver:Disconnect()
  local encoded=game:GetService("HttpService"):JSONEncode(report)
  workspace:SetAttribute("VoiceTransportResult",encoded);print("VOICE_TRANSPORT_NATIVE",encoded)
  return true
 end
 error("Unknown fixture probe verb")
end
