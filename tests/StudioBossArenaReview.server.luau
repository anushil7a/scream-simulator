-- Appended ONLY to an unpublished Studio QA build. No replication or player trigger.
do
 assert(RunService:IsStudio() and game.PlaceId==0 and game.GameId==0 and localFixture,"Boss arena evidence is local only")
 assert(bosses,"Boss service unavailable")
 local storage=game:GetService("ServerStorage")
 local invoke=Instance.new("BindableFunction");invoke.Name="BossArenaReview";invoke.Parent=storage
 local rules=require(ReplicatedStorage.Shared.BossRules)
 local patterns=require(ReplicatedStorage.Shared.BossPatterns)
 local motion=require(ReplicatedStorage.Shared.BossMotion)
 local busy=false
 invoke.OnInvoke=function(id,mode)
  assert(not busy,"A boss test is already active")
  local beamMode=mode=="beam" or mode=="beam-low"
  local gapMode=mode=="gap" and id=="leviathan"
  local ranged=mode=="ranged" or gapMode
  assert(mode=="melee" or ranged or mode=="dodge" or beamMode,"Unrecognized local diagnostic mode")
  local ps=Players:GetPlayers()
  assert(#ps==1 and sessions[ps[1]] and sessions[ps[1]].canSave~=true,"Single temporary local participant required")
  local p=ps[1];local s=sessions[p];local c,r,h=parts(p)
  assert(c and r and h and not s.flight,"Living grounded test player required")
  local chosen
  for _,b in ipairs(bosses.bosses) do
   if b.spec.id==id then chosen=b end
  end
  assert(chosen,"Unknown boss")
  for _,b in ipairs(bosses.bosses) do
   if b.warning then b.warning:Destroy();b.warning=nil end
   rules.Reset(b,b.spec,os.clock())
   b.readyAt=0
   b.motion=motion.New()
  end
  local distance=beamMode and 13 or ranged and (id=="conductor" and chosen.spec.radius-9 or math.min(23,chosen.spec.radius-3)) or 7
  local point=chosen.center+Vector3.new(0,0,distance)
  local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Exclude;params.FilterDescendantsInstances={c};params.RespectCanCollide=true
  local floor=workspace:Raycast(point+Vector3.new(0,3,0),Vector3.new(0,-6,0),params)
  -- Ignis's authored crater pad intentionally rises .30 studs above the home.
  assert(floor and math.abs(floor.Position.Y-point.Y)<.35,"No suitable floor at diagnostic start")
  print("BOSSQA_FLOOR",id,floor.Instance.Name,floor.Position.Y)
  local footHeight=h.HipHeight+r.Size.Y/2
  if h.RigType==Enum.HumanoidRigType.R6 then
   local leg=c:FindFirstChild("Left Leg");footHeight+=leg and leg.Size.Y or 2
  end
  local start=Vector3.new(point.X,floor.Position.Y+footHeight+.025,point.Z)
  assert(not Config.InArena(start),"Test point overlaps PvP")
  cancelSustained(p,s,os.clock())
  s.data=Profiles.Default();s.data.level=chosen.spec.level
  s.protectedUntil=0;s.dodgingUntil=0;s.knockedUntil=0
  h.MaxHealth=Config.HealthForLevel(s.data.level);h.Health=h.MaxHealth
  print("BOSSQA_BALANCE",id,"level",s.data.level,"playerHP",h.MaxHealth,"bossHP",chosen.spec.health,"ranged",chosen.spec.damage,"melee",chosen.spec.meleeDamage)
  c:PivotTo(CFrame.lookAt(start,Vector3.new(chosen.center.X,start.Y,chosen.center.Z)))
  r.AssemblyLinearVelocity=Vector3.zero
  chosen.turn=(ranged and 0 or 1);chosen.nextAttack=os.clock()+1.3;chosen.recoverUntil=0
  if beamMode then
   -- Solo budget endpoint: no retaliation, no human aim or audio claims.
   -- Actual server clock, adapter, beam/cover resolver, boss health and rewards.
   assert(s.voiceEligibility and s.voiceEligibility.fixture,"Fixture eligibility required")
   chosen.nextAttack=math.huge
   local priorReady=s.micReady
   s.sustained=sustained.New()
   busy=true
   task.spawn(function()
    local ok,why=xpcall(function()
     task.wait(.4)
     local power=mode=="beam-low" and .35 or 1
     local begun,cast,sample,nextPulse=0,0,0,0
     local deadline=os.clock()+110
     local oldHP=chosen.health;local required=oldHP
     while p.Parent and p.Character==c and h.Health>0 and chosen.health>0 and os.clock()<=deadline do
      local now=os.clock()
      s.micReady=true
      local protocol=s.sustained.protocol
      if not protocol.active and now>=protocol.nextStart then
       local sequence=protocol.lastSequence+1
       local started,err=sustained.Begin(s.sustained,now,{sequence=sequence,power=power,aim=chosen.root.Position},sustainedContext(p,s,now))
       assert(started,err)
       s.sustained.intent.audioStyleId=s.data.sound
       if cast==0 then begun=now end
       cast+=1;sample=0;nextPulse=now+.13
       print("BOSSQA_BEAM_CAST",id,power,cast,chosen.health)
      elseif protocol.active and now>=nextPulse then
       sample+=1;nextPulse=now+.13
       sustained.Pulse(s.sustained,now,{sequence=protocol.active.sequence,sample=sample,power=power,aim=chosen.root.Position},sustainedContext(p,s,now))
      end
      assert(chosen.health<=oldHP,"Unexpected reset during uninterrupted ranged budget check")
      oldHP=chosen.health
      task.wait(.035)
     end
     assert(chosen.health==0 and required==chosen.spec.health and cast>=3 and cast<=12,"Incomplete unlock-level boss budget check")
     print("BOSSQA_BEAM_PASS",id,power,cast,os.clock()-begun,required,"playerHP",h.MaxHealth)
    end,debug.traceback)
    cancelSustained(p,s,os.clock());s.micReady=priorReady;busy=false
    if not ok then warn("BOSSQA_BEAM_FAILED",id,mode,why) end
   end)
   return chosen.spec.name,chosen.spec.health,h.MaxHealth,start
  end
  local previous=chosen.attackSerial or 0
  assert(bosses:Hit(chosen,p,1,os.clock())==1,"Could not credit the real encounter")
  busy=true
  task.spawn(function()
   local ok,why=xpcall(function()
    local limit=os.clock()+9
    repeat task.wait(.035) until os.clock()>limit or chosen.attackSerial and chosen.attackSerial>previous
    assert(chosen.strike and chosen.attackSerial>previous,"Actual BossService cast failed")
    local strike=chosen.strike
    local expected=ranged and "Ranged" or "Melee"
    assert(strike.kind==expected,"Wrong attack branch for diagnostic case")
    local expectedLabel=chosen.spec.name.." · Lv "..chosen.spec.level
    assert(chosen.label.Text==expectedLabel and chosen.warning,"Missing identity or ground warning")
    print("BOSSQA_NAMEPLATE",chosen.label.Text)
    print("BOSSQA_WINDUP",id,mode,strike.style,strike.kind,#strike.shapes,strike.serial)
    local gapHealth
    if gapMode then
     gapHealth=h.Health
     local markers=chosen.warning:GetChildren()
     assert(strike.style=="TwinSirens" and #markers==2,"Expected two committed siren lanes")
     local initial=r.Position-chosen.center
     assert(patterns.Hits(strike,initial.X,initial.Z),"Gap scenario did not begin inside a damaging lane")
     local center=(markers[1].Position+markers[2].Position)/2
     local along=markers[1].CFrame.LookVector
     local target=center+along*(r.Position-center):Dot(along)
     r:SetNetworkOwner(nil)
     target=Vector3.new(target.X,r.Position.Y,target.Z)
     h:MoveTo(target)
     repeat task.wait(.025) until (r.Position-target).Magnitude<1.5 or os.clock()>strike.at-.18
     local safe=r.Position-chosen.center
     assert(s.dodgingUntil==0 and not patterns.Hits(strike,safe.X,safe.Z),"Ordinary movement failed to reach the safe gap before impact")
     print("BOSSQA_GAP",id,Vector3.new(safe.X-initial.X,0,safe.Z-initial.Z).Magnitude)
    elseif mode=="dodge" then s.dodgingUntil=strike.at+.18 end -- immunity negative control, not physical Q
    while os.clock()<strike.at-.075 do task.wait(.025) end
    local before=r.Position;local health=gapHealth or h.Health
    repeat task.wait(.025) until os.clock()>limit or chosen.model:GetAttribute("BossAttackImpactSerial")==strike.serial
    assert(chosen.model:GetAttribute("BossAttackImpactSerial")==strike.serial,"No confirmed attack resolution")
    task.wait(.12)
    local after=r.Position;local offset=Vector3.new(after.X-before.X,0,after.Z-before.Z).Magnitude
    local damage=health-h.Health
    print("BOSSQA_RESULT",id,mode,strike.style,strike.kind,"damage",damage,"shove",offset,"HP",h.Health,"ground",tostring(h.FloorMaterial))
    if gapMode then assert(damage==0 and s.dodgingUntil==0,"Safe gap inflicted damage")
    elseif mode=="dodge" then assert(damage==0 and offset<.25,"Dodge immunity regression")
    elseif mode=="melee" then assert(damage==chosen.spec.meleeDamage and offset>=strike.push-.3,"Expected balanced grounded melee displacement")
    else assert(damage==chosen.spec.damage and offset<.25,"Expected balanced ranged hit without shove") end
    print("BOSSQA_PASS",id,mode)
    chosen.credit={};chosen.nextAttack=os.clock()+30
    s.dodgingUntil=0
   end,debug.traceback)
   if gapMode and r.Parent then r:SetNetworkOwnershipAuto() end
   busy=false
   if not ok then warn("BOSSQA_FAILED",id,mode,why) end
  end)
  return chosen.spec.name,chosen.spec.scale,chosen.spec.radius,start
 end
 print("BOSSQA_READY; local single-player ServerStorage.BossArenaReview")
end
