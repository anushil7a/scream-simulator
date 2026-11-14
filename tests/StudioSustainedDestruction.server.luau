-- Append to Bootstrap in a disposable unpublished local place only.
-- Synthetic voice/aim; actual raycast, destruction service and session rules.
task.spawn(function()
 assert(sustainedEnabled and game.PlaceId==0)
 task.wait(3) -- let the independent immediate damage fixture finish
 local p=Players:GetPlayers()[1] or Players.PlayerAdded:Wait()
 local limit=os.clock()+20
 repeat task.wait(.1) until (sessions[p] and parts(p)) or os.clock()>limit
 local s=assert(sessions[p]);assert(not s.canSave)
 local c,r=parts(p);assert(c and r)
 local old={frame=c:GetPivot(),anchor=r.Anchored,level=s.data.level,sound=s.data.sound,
  mic=s.micReady,protection=s.protectedUntil,dodge=s.dodgingUntil,knock=s.knockedUntil}
 local models={};local checks=0
 local function check(v,msg) assert(v,msg);checks+=1 end
 local function target(kind,x)
  local model=Instance.new("Model");model.Name="SustainedDestructionTest";model:SetAttribute("DestructibleType",kind)
  local body=Instance.new("Part");body.Anchored=true;body.Size=Vector3.new(6,8,2);body.Position=Vector3.new(x,1004,-12);body.Parent=model
  model.Parent=workspace;Destruction.Register(model);table.insert(models,model);return model,body
 end
 local ok,err=xpcall(function()
  r.Anchored=true;c:PivotTo(CFrame.new(0,1004,0))
  s.micReady=true;s.protectedUntil=0;s.dodgingUntil=0;s.knockedUntil=0
  local bench,body=target("Bench",0)
  local function start(level)
   s.sustained=sustained.New();s.data.level=level;s.data.sound=Config.SoundForLevel(level).id
   local now=os.clock()
   check(sustained.Begin(s.sustained,now,{sequence=1,power=1,aim=body.Position},sustainedContext(p,s,now)),"Start rejected")
   return now
  end
  local now=start(1);stepSustained(p,s,now+.2)
  check(bench:GetAttribute("ObjectHealth")==47,"Sustained beam missed destructible")
  Destruction.Damage(bench,1,46)
  check(sustained.Pulse(s.sustained,now+.3,{sequence=1,sample=1,power=1,aim=body.Position},sustainedContext(p,s,now+.3)),"Pulse rejected")
  stepSustained(p,s,now+.4)
  check(bench:GetAttribute("Destroyed") and not body.CanCollide and not body.CanQuery,"Sustained hit did not destroy weakened cover")
  bench:Destroy()
  local tree;tree,body=target("SmallTree",0)
  now=start(25);stepSustained(p,s,now+.2)
  check(tree:GetAttribute("ObjectHealth")==110,"Low level damaged gated tree")
  now=start(26);stepSustained(p,s,now+.2)
  check(tree:GetAttribute("ObjectHealth")<110,"Unlocked tree rejected sustained damage")
  s.sustained=sustained.New();s.protectedUntil=os.clock()+5
  check(not sustained.Begin(s.sustained,os.clock(),{sequence=1,power=1,aim=body.Position},sustainedContext(p,s,os.clock())),"Spawn protection allowed attack")
  s.protectedUntil=0;now=start(26);s.dodgingUntil=now+1
  local health=tree:GetAttribute("ObjectHealth");stepSustained(p,s,now+.2)
  check(not s.sustained.protocol.active and tree:GetAttribute("ObjectHealth")==health,"Roll did not cancel damage")
 end,debug.traceback)
 for _,model in ipairs(models) do
  local id=model:GetAttribute("ObjectId");Destruction.objects[model]=nil;if id then Destruction.ids[id]=nil end;model:Destroy()
 end
 c:PivotTo(old.frame);r.Anchored=old.anchor;s.data.level=old.level;s.data.sound=old.sound
 s.micReady=old.mic;s.protectedUntil=old.protection;s.dodgingUntil=old.dodge;s.knockedUntil=old.knock
 s.sustained=sustained.New();p:SetAttribute("SustainedActive",false);p:SetAttribute("SustainedReadyAt",0)
 print("SUSTAINED_DESTRUCTION_NATIVE",ok,checks,err or "synthetic voice; native geometry/destruction")
 workspace:SetAttribute("SustainedDestructionResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
end)
