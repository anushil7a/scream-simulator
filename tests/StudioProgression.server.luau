-- Appended only to the guarded disposable native fixture. Synthetic input,
-- real city fighters, geometry, health, server KO rewards and challenge counters.
task.spawn(function()
 local deadline=os.clock()+45
 repeat task.wait(.1) until workspace:GetAttribute("SustainedDestructionResult") or os.clock()>deadline
 local p=Players:GetPlayers()[1];local s=p and sessions[p];assert(s and not s.canSave)
 local c,r,h=parts(p);assert(c and r and h)
 local old={data=s.data,frame=c:GetPivot(),anchor=r.Anchored,mic=s.micReady,protection=s.protectedUntil,
  dodge=s.dodgingUntil,knock=s.knockedUntil,health=h.Health,maximum=h.MaxHealth,heal=s.nextHeal,milestone=s.milestone}
 local n=0;local function check(v,m)assert(v,m);n+=1 end
 local fighters={};for _,bot in ipairs(World.Bots) do if bot.training then table.insert(fighters,bot) end end
 local ok,err=xpcall(function()
  check(#fighters==3,"Expected exactly three training tiers")
  s.data=Profiles.Default();s.micReady=true;s.protectedUntil=0;s.dodgingUntil=0;s.knockedUntil=0;r.Anchored=true
  syncHealth(p,true)
  for _,bot in ipairs(fighters) do
   check(not Config.InArena(bot.start) and bot.maxHealth==bot.training.health and bot.humanoid.MaxHealth==bot.maxHealth,"Wrong tier health or unsafe training area")
  end
  local bot=fighters[1];restoreBot(bot)
  c:PivotTo(CFrame.new(bot.start+Vector3.new(0,0,15)))
  local function strike(now)
   bot.trainingTarget=p;bot.lastTrainingHit=now;bot.nextStrike=0;bot.strike=nil
   stepTraining(now);check(bot.strike~=nil,"No training telegraph")
  end
  local now=os.clock();strike(now);local hp=h.Health
  stepTraining(now+TrainingRules.Windup+.01)
  check(h.Health==hp-bot.training.damage,"Stationary player avoided counterattack")
  now+=5;strike(now);hp=h.Health;s.dodgingUntil=now+2
  stepTraining(now+TrainingRules.Windup+.01);check(h.Health==hp,"Dodge did not avoid counterattack");s.dodgingUntil=0
  now+=5;strike(now);c:PivotTo(c:GetPivot()+Vector3.new(6,0,0));hp=h.Health
  stepTraining(now+TrainingRules.Windup+.01);check(h.Health==hp,"Moving out of fixed strike still damaged player")
  c:PivotTo(CFrame.new(bot.start+Vector3.new(0,0,15)))
  now+=5;strike(now);s.protectedUntil=now+2;stepTraining(now+TrainingRules.Windup+.01)
  check(h.Health==hp and bot.strike==nil,"Protected player was attacked");s.protectedUntil=0
  -- Actual sustained target resolver: no credit when attacking from outside the pad.
  s.data.level=100;s.data.sound=Config.SoundForLevel(100).id;syncHealth(p,true)
  c:PivotTo(CFrame.new(bot.start+Vector3.new(0,0,40)))
  local ctx=sustainedContext(p,s,os.clock());local stats=VoiceCombat.Stats(100,1,false)
  local _,details=resolveSustained(ctx,(bot.root.Position-ctx.origin).Unit,stats,os.clock())
  check(details["bot:"..bot.id]==nil,"Training target hit from outside pad")
  s.data=Profiles.Default();syncHealth(p,true);c:PivotTo(CFrame.new(bot.start+Vector3.new(0,0,15)))
  -- Almost-complete legitimate damage ledger; final real beam tick must pay once.
  bot.health=3;bot.credit={};recordCredit(bot.credit,p,77,80,os.clock());World.UpdateBot(bot)
  s.data.combatChallenges.fighters=2
  s.sustained=sustained.New();now=os.clock()
  check(sustained.Begin(s.sustained,now,{sequence=1,power=1,aim=bot.root.Position},sustainedContext(p,s,now)),"Training beam rejected")
  stepSustained(p,s,now+.2)
  check(not bot.alive and s.data.level==2 and s.data.xp==9,"Training KO plus third-fighter challenge payout incorrect")
  check(s.data.combatChallenges.fighters==0 and next(bot.credit)==nil,"Challenge or consumed credit not reset")
  restoreBot(bot);check(bot.alive and bot.health==80 and not bot.root.Anchored and bot.humanoid.WalkSpeed==TrainingRules.RoamSpeed,"Training recovery lost tier HP or roaming")
  s.data.level=9;s.data.xp=Config.XPToNext(9)-1;xp(p,1)
  check(s.data.level==10 and s.milestone and string.find(s.milestone,"Unlocked",1,true),"Ten-level milestone missing")
 end,debug.traceback)
 for _,bot in ipairs(fighters) do restoreBot(bot);bot.lastTrainingHit=nil;bot.nextStrike=nil end
 s.data=old.data;s.micReady=old.mic;s.protectedUntil=old.protection;s.dodgingUntil=old.dodge;s.knockedUntil=old.knock;s.nextHeal=old.heal;s.milestone=old.milestone
 s.sustained=sustained.New();c:PivotTo(old.frame);r.Anchored=old.anchor;h.MaxHealth=old.maximum;h.Health=old.health
 p:SetAttribute("SustainedActive",false);p:SetAttribute("SustainedReadyAt",0);state(p)
 local result=game:GetService("HttpService"):JSONEncode({passed=ok,checks=n,error=not ok and tostring(err) or nil})
 workspace:SetAttribute("ProgressionResult",result);print("NATIVE_PROGRESSION_RESULT",result)
end)
