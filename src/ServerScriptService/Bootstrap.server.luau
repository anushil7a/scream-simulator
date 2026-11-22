local TestFlight=require(script.Parent.TestFlight)
local DodgeMotion=require(script.Parent.DodgeMotion)
local DamageSummary=require(script.Parent.DamageSummary)
local Credit=require(game:GetService("ReplicatedStorage").Shared.CombatCredit)
local TrainingRules=require(game:GetService("ReplicatedStorage").Shared.TrainingRules)
local Healing=require(game:GetService("ReplicatedStorage").Shared.Healing)
local SustainedRewards=require(game:GetService("ReplicatedStorage").Shared.SustainedRewards)
local InteractionRules=require(game:GetService("ReplicatedStorage").Shared.InteractionRules)
local Players=game:GetService("Players")
local ReplicatedStorage=game:GetService("ReplicatedStorage")
local RunService=game:GetService("RunService")
local VoiceChatService=game:GetService("VoiceChatService")
local VoiceEligibility=require(script.Parent.VoiceEligibility)
local Config=require(ReplicatedStorage.Shared.Config)
local World=require(script.Parent.World)
local Profiles=require(script.Parent.Profiles)
local Access=require(script.Parent.DeveloperAccess)
local Rules=require(script.Parent.CombatRules)
local VoiceCombat=require(ReplicatedStorage.Shared.VoiceCombat)
local TestBeamRules=require(script.Parent.TestBeam)
local testBeam=TestBeamRules.new(VoiceCombat,require(script.Parent.SustainedAim),require(ReplicatedStorage.Shared.SustainedAttack))
local Entitlements=require(script.Parent.Entitlements)
local Commerce=require(script.Parent.Commerce)
local ShopCatalog=require(ReplicatedStorage.Shared.ShopCatalog)
local Soccer=require(script.Parent.SoccerChallenge)
local BeachVolley=require(script.Parent.BeachVolley)
local QuestLifecycle=require(ReplicatedStorage.Shared.QuestLifecycle)
local QuestGuide=require(ReplicatedStorage.Shared.QuestGuide)
local NavigationCatalog=require(ReplicatedStorage.Shared.NavigationCatalog)
local Equipment=require(script.Parent.Equipment)
-- Only disposable local fixtures bypass persistent profiles. Attack mode is independent.
local localFixture=RunService:IsStudio() and game.PlaceId==0 and workspace:GetAttribute("LocalSustainedPrototype")==true
local function onlinePreviewTools()
 return Access.IsCityPreviewTools(game.CreatorType,game.CreatorId,RunService:IsStudio(),game.GameId,game.PlaceId)
end
local function toolAuthorized(p)
 return TestBeamRules.Available(Access.IsAuthorized(p,game.CreatorType,game.CreatorId,RunService:IsStudio(),game.GameId),localFixture)
end
local flightBounds={min=Vector3.new(Config.MapMin.X+8,-4,Config.MapMin.Z+8),max=Vector3.new(Config.MapMax.X-8,220,Config.MapMax.Z-8),localOnly=localFixture,
 previewAuthorized=function(p)return onlinePreviewTools() and toolAuthorized(p)end}
local sustainedEnabled=Config.AutomaticVoice==true or localFixture
local sustained
if sustainedEnabled then
 sustained=require(script.Parent.SustainedAttackAdapter).new(require(ReplicatedStorage.Shared.SustainedAttack),
  VoiceCombat,require(script.Parent.SustainedAim))
end
World.Build()
local questGivers=NavigationCatalog.IndexQuestGivers(World.Bots)
BeachVolley.Start(workspace.ScreamSimulatorWorld)
local Destruction=require(script.Parent.Destruction)
if Config.ObjectDestruction==true then Destruction.Start(workspace.ScreamSimulatorWorld) end
World.FindMaintenance=function(bot)
 if Config.ObjectDestruction~=true then return nil end
 if os.clock()<(bot.nextMaintenance or 0) then return nil end
 local station=Destruction.MaintenanceTarget(bot.root.Position,80)
 if station then bot.nextMaintenance=os.clock()+30 end
 return station
end
World.FinishMaintenance=function(bot,station)
 if Config.ObjectDestruction~=true then return false end
 if bot.alive and bot.working and (bot.reactionUntil or 0)<=os.clock() and (bot.socialUntil or 0)<=os.clock() then
  return Destruction.FinishMaintenance(station,bot.root.Position)
 end
 return false
end
local old=ReplicatedStorage:FindFirstChild("ScreamRemotes");if old then old:Destroy() end
local remotes=Instance.new("Folder");remotes.Name="ScreamRemotes"
remotes:SetAttribute("AutomaticVoice",sustainedEnabled)
remotes:SetAttribute("TestToolsAvailable",TestBeamRules.LocalFixture(localFixture) or onlinePreviewTools())
remotes.Parent=ReplicatedStorage
local function remote(name) local r=Instance.new("RemoteEvent");r.Name=name;r.Parent=remotes;return r end
local action=remote("Action");local stateRemote=remote("State");local effect=remote("Effect")
local damageSummary=remote("DamageSummary")
local function recordDamage(p,s,now,actual)
 local nextState,finished=DamageSummary.Record(s.damageSummary,now,actual)
 s.damageSummary=nextState
 if finished then damageSummary:FireClient(p,"recap",0,finished) end
end
local function stepDamageSummary(p,s,now)
 local nextState,phase,dps,total=DamageSummary.Step(s.damageSummary,now)
 s.damageSummary=nextState
 if phase then damageSummary:FireClient(p,phase,dps,total) end
end
local function clearDamageSummary(p,s)
 if not s.damageSummary then return end
 s.damageSummary=nil
 if p.Parent then damageSummary:FireClient(p,"clear",0,0) end
end
local sessions={}
local bosses
local closing=false
local shutdownSaveDeadline
local joinsInFlight=0
local rewardHistory={pairs={}} -- survives reconnects in this server
local testRewardHistory={pairs={}} -- temporary fights never consume normal-play anti-farm history
local function parts(p)
 local c=p.Character;local r=c and c:FindFirstChild("HumanoidRootPart");local h=c and c:FindFirstChildOfClass("Humanoid")
 if r and h and h.Health>0 then return c,r,h end
end
local function sustainedEnd(p,ended,now)
 if not ended then return end
 effect:FireAllClients("SustainedBeamEnd",nil,p.UserId)
 p:SetAttribute("SustainedActive",false)
 p:SetAttribute("SustainedEndsAt",0)
 p:SetAttribute("SustainedReadyAt",workspace:GetServerTimeNow()+math.max(0,ended.nextStart-now))
end
local function testBeamEnd(p,s,now,ended)
 if ended or testBeam.Stop(s,now) then
  -- Don't let alternating test and microphone attacks bypass either cooldown.
  local ready=s.testBeamReadyAt or now
  local protocol=s.sustained and s.sustained.protocol
  if protocol then
   protocol.nextStart=math.max(protocol.nextStart or 0,ready)
   p:SetAttribute("SustainedReadyAt",workspace:GetServerTimeNow()+math.max(0,protocol.nextStart-now))
  end
  s.voice.nextCast=math.max(s.voice.nextCast or 0,ready)
  s.nextCast=math.max(s.nextCast or 0,ready)
  effect:FireAllClients("TestBeamEnd",nil,p.UserId)
  return true
 end
 return false
end
local function cancelSustained(p,s,now)
 if s.sustained then sustainedEnd(p,sustained.Cancel(s.sustained,now),now) end
end
-- Do not rely on automatic Player destruction to release session closures.
-- Disconnect before any departure/shutdown save yields; running callbacks still
-- use their existing session/character guards and may finish independently.
local function disconnectSessionSignals(s)
 local added,removing=s.characterAddedConnection,s.characterRemovingConnection
 s.characterAddedConnection=nil;s.characterRemovingConnection=nil
 if added then added:Disconnect() end
 if removing then removing:Disconnect() end
end
local function beamColor(p,s)
 if s.data.useCustomColor and s.data.customColor and Entitlements.HasSpectrum(p) then return Color3.fromHex(s.data.customColor) end
 return s.data.aura
end
local function state(p,message,conversation,messageUrgent,messageKey)
 local s=sessions[p];if not s or not p.Parent then return end
 if p:GetAttribute("ScreamLevel")~=s.data.level then p:SetAttribute("ScreamLevel",s.data.level) end
 local _,r,h=parts(p)
 local soccer=Soccer.Status(p)
 local quest=Config.GetQuest(s.activeQuest);local progress=quest and s.data.quests[quest.id]
 local deliveryStop=Config.GetDeliveryStop(s.deliveryStop)
 local step=QuestGuide.Step(quest,progress and progress.progress or 0,s.carrying,s.raceStart~=nil,soccer and soccer.detail,deliveryStop and deliveryStop.name)
 Equipment.SyncGear(p,Config.Gear.Selected(s.data))
 stateRemote:FireClient(p,{coins=s.data.coins,level=s.data.level,xp=s.data.xp,xpNext=Config.XPToNext(s.data.level),sound=s.data.sound,aura=s.data.aura,
 shop=Commerce.Status(p),spectrumPass=Entitlements.HasSpectrum(p),customColor=s.data.customColor,useCustomColor=s.data.useCustomColor,
 combatChallenges=s.data.combatChallenges,training=TrainingRules.Recommended(s.data.level).name,milestone=s.milestone,
 gearOwned=s.data.gearOwned,gearEquipped=s.data.gearEquipped,gearMultiplier=Config.Gear.Multiplier(s.data),amplifierOwned=s.data.amplifierOwned,amplifierEquipped=s.data.amplifierEquipped,megaphoneOwned=s.data.megaphoneOwned,megaphoneEquipped=s.data.megaphoneEquipped,movementPass=Entitlements.HasMovement(p),achievements=s.data.achievements,
 questNavigation=NavigationCatalog.QuestTargets(s,questGivers),availableQuests=s.data.availableQuests,quests=s.data.quests,collected=s.collected,activeQuest=s.activeQuest,questStep=step,questTime=soccer and soccer.remaining or s.questDeadline and math.max(0,math.ceil(s.questDeadline-os.clock())) or 0,
 health=h and math.ceil(h.Health) or Config.HealthForLevel(s.data.level),maxHealth=Config.HealthForLevel(s.data.level),inWarZone=r and Config.InArena(r.Position) or false,
 voiceEligible=VoiceEligibility.Allowed(s.voiceEligibility,os.clock()),voiceStatus=VoiceEligibility.Status(s.voiceEligibility,os.clock()),
 castCooldown=math.max(0,(s.sustained and s.sustained.protocol.nextStart or s.voice.nextCast)-os.clock()),micReady=s.micReady,protection=math.max(0,s.protectedUntil-os.clock()),dodgeCooldown=math.max(0,s.nextDodge-os.clock()),
 conversation=conversation,settings=s.data.settings,devAccess=Access.IsAuthorized(p,game.CreatorType,game.CreatorId,RunService:IsStudio(),game.GameId),savingAvailable=s.canSave and not s.testBaseline,savingDelayed=s.saveDelayed==true,recoveryWarning=s.recoveryWarning==true,testSession=s.testBaseline~=nil,flying=s.flight~=nil,
 testBeamAvailable=s.testBeamAvailable==true,testBeamDamageAvailable=s.testBeamAvailable==true,
 testBeamActive=s.testBeam~=nil,testBeamPower=s.testBeam and s.testBeam.power or 0,testBeamCooldown=math.max(0,(s.testBeamReadyAt or 0)-os.clock()),message=message,messageUrgent=messageUrgent==true,messageKey=messageKey=="save" and "save" or nil})
end
-- No remote can enqueue voice checks. Retry state belongs only to live sessions;
-- at most eight actual API calls exist, with one new start per quarter-second.
local voiceRequestBudget={inFlight=0,nextStart=0}
local function stepVoiceEligibility(p,s,now)
 if closing or sessions[p]~=s or not p.Parent then return end
 VoiceEligibility.MarkWaiting(s.voiceEligibility,now)
 local status=VoiceEligibility.Status(s.voiceEligibility,now)
 if not VoiceEligibility.Allowed(s.voiceEligibility,now) then
  if s.sustained and s.sustained.protocol.active then cancelSustained(p,s,now) end
  if s.voice.capture then VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0) end
 end
 if status~=s.voiceEligibilityStatus then s.voiceEligibilityStatus=status;state(p) end
end
local function voiceRequestCurrent(p,identity,token,now)
 local s=sessions[p];local eligibility=s and s.voiceEligibility
 return not closing and p.Parent~=nil and eligibility~=nil and eligibility.identity==identity
  and eligibility.pending~=nil and eligibility.pending.token==token and now<eligibility.pending.deadline
end
local function runVoiceRequest(p,identity,token)
 -- No session/profile local or closure is retained across the engine yield.
 local ok,result=false,nil
 if voiceRequestCurrent(p,identity,token,os.clock()) then
  ok,result=pcall(VoiceChatService.IsVoiceEnabledForUserIdAsync,VoiceChatService,p.UserId)
 end
 -- Deadline/departure never releases an in-flight call prematurely.
 voiceRequestBudget.inFlight-=1
 local s=sessions[p]
 if closing or not p.Parent or not s or s.voiceEligibility.identity~=identity then return end
 VoiceEligibility.Complete(s.voiceEligibility,token,os.clock(),ok,result)
 stepVoiceEligibility(p,s,os.clock())
end
local function dispatchVoiceEligibility(now)
 if closing or voiceRequestBudget.inFlight>=VoiceEligibility.MaxConcurrent or now<voiceRequestBudget.nextStart then return end
 -- Oldest due first; new joins use their arrival time, not zero. No persistent
 -- roster/queue retains departed sessions, and retrying users cannot jump ahead.
 local chosen,dueAt
 for p,s in pairs(sessions) do
  local due=VoiceEligibility.DueAt(s.voiceEligibility)
  if p.Parent and due and due<=now and (not dueAt or due<dueAt or (due==dueAt and p.UserId<chosen.UserId)) then chosen=p;dueAt=due end
 end
 if not chosen then return end
 local eligibility=sessions[chosen].voiceEligibility
 voiceRequestBudget.inFlight+=1;voiceRequestBudget.nextStart=now+VoiceEligibility.StartInterval
 local token=VoiceEligibility.Poll(eligibility,now)
 if not token then voiceRequestBudget.inFlight-=1;return end
 task.spawn(runVoiceRequest,chosen,eligibility.identity,token)
end
Commerce.Start(function(p)
 local s=sessions[p]
 return s~=nil and s.canSave and not s.testBaseline and not localFixture and not RunService:IsStudio()
end,state)
local function coins(p,amount)
 local s=sessions[p];if not s then return 0 end
 local reward=math.max(0,math.floor(amount*Commerce.Multiplier(p,"coins")))
 local before=s.data.coins
 s.data.coins=math.min(1000000000,s.data.coins+reward);return s.data.coins-before
end
local function syncHealth(p,full)
 local s=sessions[p];local _,_,h=parts(p);if not s or not h then return end
 local maximum=Config.HealthForLevel(s.data.level);local gain=maximum-h.MaxHealth
 h.MaxHealth=maximum;h.Health=full and maximum or math.clamp(h.Health+gain,1,maximum)
end
local function xp(p,amount)
 local s=sessions[p];if not s then return 0 end
 amount=amount*Commerce.Multiplier(p,"xp")
 local d=s.data;if d.level>=Config.MaxLevel then return 0 end
 local credited=math.max(0,math.floor(amount))
 d.xp+=credited;local before=d.level
 while d.level<Config.MaxLevel and d.xp>=Config.XPToNext(d.level) do d.xp-=Config.XPToNext(d.level);d.level+=1 end
 if d.level==Config.MaxLevel then credited-=d.xp;d.xp=0 end
 if d.level>before then
  syncHealth(p,false)
  local unlock="";for _,v in ipairs(Config.Sounds) do if v.level>before and v.level<=d.level then unlock=" · Unlocked "..v.name end end
  local stats=VoiceCombat.Stats(d.level,1,false)
  if math.floor(before/10)<math.floor(d.level/10) then
   s.milestone=string.format("LEVEL %d%s · %d HP · %.1f max DPS · Train: %s",d.level,unlock,stats.health,stats.maxDps,TrainingRules.Recommended(d.level).name)
  end
  state(p,string.format("Level %d%s · %d HP · %.1f max DPS",d.level,unlock,stats.health,stats.maxDps))
 end
 return credited
end
local function questProgress(p,event,amount)
 local s=sessions[p];if not s or not s.activeQuest then return end
 local q=Config.GetQuest(s.activeQuest);if not q or q.retired==true or q.event~=event then return end
 local v=s.data.quests[q.id];if not v or v.claimed or v.progress>=q.goal then return end
 v.progress=math.min(q.goal,v.progress+(amount or 1));state(p,v.progress==q.goal and "Quest complete! Claim your reward in Quests." or nil)
end
local function confirmBeamDodge(target,now)
 questProgress(target,"Evade")
 local s=sessions[target]
 if not s or now<(s.nextBeamDodgeCueAt or 0) then return end
 local _,_,humanoid=parts(target)
 if not humanoid then return end
 s.nextBeamDodgeCueAt=now+1
 effect:FireClient(target,"BeamDodged",humanoid)
end
local function combatChallenge(p,id,quiet)
 local s=sessions[p];if not s then return 0,0 end
 local reward,name=Config.Progression.Advance(s.data.combatChallenges,id,s.data.level)
 local credited=0
 if reward>0 then
  credited=xp(p,reward)
  if not quiet then state(p,name.." · +"..credited.." XP · challenge renewed") end
 end
 return reward,credited
end
local function sameCombatMode(a,b)
 return a~=nil and b~=nil and not a.flight and not b.flight and (a.testBaseline~=nil)==(b.testBaseline~=nil)
end
local function canDamageBots(s)
 -- Only the guarded local fixture makes every participant's profile temporary.
 return s~=nil and not s.flight and (s.testBaseline==nil or localFixture==true)
end
-- Ledger ownership uses an opaque session token, never a profile/session table.
local function recordCredit(ledger,p,damage,maximum,now)
 local s=sessions[p];if not s or type(s.rewardIdentity)~="table" or damage<=0 then return end
 local previous=ledger[p.UserId]
 Credit.Add(ledger,p.UserId,damage,now,maximum)
 local entry=ledger[p.UserId]
 if entry and entry~=previous then
  entry.rewardIdentity=s.rewardIdentity;entry.rewardTest=s.testBaseline~=nil
 elseif entry and (entry.rewardIdentity~=s.rewardIdentity or entry.rewardTest~=(s.testBaseline~=nil)) then
  -- Keep damage in the denominator, but never inherit another session/mode's credit.
  entry.rewardIdentity=false
 end
end
local function awardCombatKO(ledger,finisher,targetLevel,maximum,pool,now,victim,tier)
 local fs=sessions[finisher]
 if not fs or (victim and not sameCombatMode(fs,sessions[victim])) or (not victim and not canDamageBots(fs)) then table.clear(ledger);return end
 local attribution=table.clone(ledger)
 local shares,meaningful=Credit.Split(ledger,finisher.UserId,now,maximum)
 for id,share in pairs(shares) do
  local recipient=Players:GetPlayerByUserId(id);local rs=recipient and sessions[recipient]
  local entry=attribution[id]
  if not rs or type(rs.rewardIdentity)~="table" or not entry or entry.rewardIdentity~=rs.rewardIdentity or entry.rewardTest~=(rs.testBaseline~=nil) or not sameCombatMode(rs,fs) then continue end
  local factor=Config.Progression.RewardFactor(rs.data.level,tier and TrainingRules.RewardLevel(tier,rs.data.level) or targetLevel)
  local repeatFactor=victim and Credit.RepeatFactor(rs.testBaseline and testRewardHistory or rewardHistory,id,victim.UserId,now) or 1
  local reward=math.floor(pool*share*factor*repeatFactor)
  if reward>0 then
   local underdog=targetLevel>=rs.data.level
   local credited=xp(recipient,reward)
   local coinCredit=coins(recipient,math.floor((victim and 20 or 5)*share*factor*repeatFactor))
   if victim and recipient==finisher and underdog then questProgress(recipient,"Underdog") end
   if victim and recipient~=finisher and underdog and meaningful[id] then questProgress(recipient,"ArenaAssist") end
   local bonus,bonusXP=0,0
   if tier and factor>=.5 and meaningful[id] then
    bonus,bonusXP=combatChallenge(recipient,"fighters",true)
   end
   local summary=recipient==finisher and "KO" or "Assist"
   if tier then summary=tier.name..(recipient==finisher and " defeated" or " assist") end
   state(recipient,summary.." · +"..(credited+bonusXP).." XP"..((tier or coinCredit>0) and " · +"..coinCredit.." coins" or "")
    ..(bonus>0 and " · challenge completed & renewed" or "")..(factor<1 and " · weaker opponent" or ""))
  elseif recipient==finisher then state(recipient,"KO · no reward awarded") end
 end
end
local function stopQuest(p)
 local s=sessions[p];if not s then return end
 Soccer.Cancel(p);QuestLifecycle.Clear(s,Config.GetQuest)
end
local function protect(p,s)
 if s.damageSummary then clearDamageSummary(p,s) end
 if s.testBeam then testBeamEnd(p,s,os.clock()) end
 s.credit={}
 cancelSustained(p,s,os.clock())
 VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0)
 s.protectedUntil=os.clock()+Config.SpawnProtection
 p:SetAttribute("ProtectionEnds",workspace:GetServerTimeNow()+Config.SpawnProtection)
 local c=p.Character;if c then local oldField=c:FindFirstChild("SpawnProtection");if oldField then oldField:Destroy() end
  local f=Instance.new("ForceField");f.Name="SpawnProtection";f.Parent=c
  task.delay(Config.SpawnProtection,function() if f.Parent then f:Destroy() end end)
 end
end
local function resetMovement(p,s,h,root)
 -- Detach only this avatar before relocating; a seat weld can otherwise keep
 -- the rescued character attached to anchored furniture.
 local seat=h.SeatPart
 if seat and p.Character then
  for _,weld in ipairs(seat:GetChildren()) do
   if weld:IsA("Weld") and weld.Name=="SeatWeld" and weld.Part1 and weld.Part1:IsDescendantOf(p.Character) then weld:Destroy() end
  end
 end
 h.Sit=false
 s.dodgingUntil=0;s.knockedUntil=0;s.premiumRoll=false;s.sprintRequested=false
 p:SetAttribute("DodgeEnds",0);p:SetAttribute("DodgeStarted",0);p:SetAttribute("KnockdownEnds",0);p:SetAttribute("Sprinting",false)
 h.PlatformStand=false;h.AutoRotate=true
 if root then
  root.AssemblyLinearVelocity=Vector3.zero;root.AssemblyAngularVelocity=Vector3.zero
  if not root.Anchored then root:SetNetworkOwnershipAuto() end
 end
end
local function eject(p,h)
 local s=sessions[p];local character=p.Character;local root=character and character:FindFirstChild("HumanoidRootPart")
 h.Health=Config.HealthForLevel(s.data.level)
 resetMovement(p,s,h,root)
 character:PivotTo(World.SafeSpawn);protect(p,s)
 s.nextHeal=os.clock()+Config.HealQuietSeconds;state(p,"Knocked out · back at the safe hub")
end
local function audible(c,origin,target,targetModel)
 local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Exclude;params.FilterDescendantsInstances={c,targetModel};params.RespectCanCollide=true
 return workspace:Raycast(origin,target-origin,params)==nil
end
-- Bigger visual silhouettes need a taller aim envelope, not a larger
-- engagement circle. Callers still require the same server CanHit gate.
local function bossInBeam(boss,c,origin,direction,length,width)
 local scale=boss.spec.scale or 1
 local center=boss.root.Position
 for i=-1,1 do
  local sample=center+Vector3.new(0,i*2.5*scale,0)
  if Rules.InBeam(origin,direction,sample,length,width,2*scale) and audible(c,origin,sample,boss.model) then return true end
 end
 return false
end
local function canCapture(p,s,now)
 if s.flight or s.testBeam then return false end
 local _,r,h=parts(p)
 local bot=s.conversationBot
 if r and bot and bot.alive and bot.root.Parent and bot.talkingTo==p and (bot.socialUntil or 0)>now
  and (bot.root.Position-r.Position).Magnitude<=14 then return false end
 return r~=nil and h~=nil and not h.PlatformStand and s.micReady and VoiceEligibility.Allowed(s.voiceEligibility,now) and now>=s.protectedUntil and now>=s.dodgingUntil and now>=(s.knockedUntil or 0)
end
local function attackOrigin(c,r)
 local head=c:FindFirstChild("Head")
 if head and head:IsA("BasePart") and (head.Position-r.Position).Magnitude<5 then return head.Position end
 return r.Position+Vector3.new(0,1,0)
end
local function beamObstruction(c,origin,direction,range,players)
 local exclude={c};for _,bot in ipairs(World.Bots) do table.insert(exclude,bot.model) end
 for _,other in ipairs(players) do if other.Character then table.insert(exclude,other.Character) end end
 local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Exclude
 params.FilterDescendantsInstances=exclude;params.RespectCanCollide=true
 return workspace:Raycast(origin,direction*range,params)
end
-- Dedicated sandbox targets. Normal combat keeps its own resolver, credit
-- ledger and rewards; do not call those from a Test Beam.
local function resolveTestBeam(p,s,ctx,direction,stats,now)
 if type(s.testBaseline)~="table" or s.flight or now<s.protectedUntil or not Config.InArena(ctx.root.Position) then return end
 local ids,details={},{}
 local players=Players:GetPlayers()
 local obstruction=beamObstruction(ctx.character,ctx.origin,direction,stats.range,players)
 local length=obstruction and obstruction.Distance or stats.range
 details.length=length
 for _,target in ipairs(players) do
  local ts=sessions[target]
  if target~=p and ts and type(ts.testBaseline)=="table" and not ts.flight and toolAuthorized(target) then
   local c,r,h=parts(target)
   if r and Rules.CanTarget(ctx.root.Position,r.Position,ts.protectedUntil,now,stats.range+2)
    and (now>=ts.dodgingUntil or ts.premiumRoll)
    and Rules.InBeam(ctx.origin,direction,r.Position,length,stats.width,1) and audible(ctx.character,ctx.origin,r.Position,c) then
    local id="player:"..target.UserId
    table.insert(ids,id);details[id]={player=target,session=ts,humanoid=h}
   end
  end
 end
 return ids,details
end
local function applyTestBeam(p,s,now,hits,details)
 if not hits or not details then return end
 local total=0
 for _,hit in ipairs(hits) do
  local target=details[hit.id]
  if not target then continue end
  local ts,h=target.session,target.humanoid
  local actual=math.min(hit.damage,h.Health)
  if actual<=0 then continue end
  total+=actual;ts.nextHeal=now+Config.HealQuietSeconds
  if h.Health<=actual then eject(target.player,h) else h.Health-=actual end
 end
 if total>0 then
  s.nextHeal=now+Config.HealQuietSeconds
  recordDamage(p,s,now,total)
 end
end
local function sustainedContext(p,s,now)
 if not canCapture(p,s,now) then return nil end
 local c,r=parts(p)
 local style=Config.GetSound(s.data.sound)
 if not style or style.level>s.data.level then return nil end
 return {player=p,character=c,origin=attackOrigin(c,r),position=r.Position,
  level=s.data.level,gearMultiplier=Config.Gear.Multiplier(s.data),amplifier=s.data.amplifierEquipped,megaphone=s.data.megaphoneEquipped}
end
local function resolveSustained(ctx,direction,stats,now)
 local ids,details,dodged={},{},{}
 local function add(id,detail)
  if not details[id] then table.insert(ids,id);details[id]=detail end
 end
 local players=Players:GetPlayers()
 local obstruction=beamObstruction(ctx.character,ctx.origin,direction,stats.range,players)
 local length=obstruction and obstruction.Distance or stats.range
 if Config.InArena(ctx.position) then
  for _,p in ipairs(players) do
   local ts=sessions[p];local c,r,h=parts(p)
   if p~=ctx.player and sameCombatMode(sessions[ctx.player],ts) and r and Rules.CanTarget(ctx.position,r.Position,ts.protectedUntil,now,stats.range+2)
    and Rules.InBeam(ctx.origin,direction,r.Position,length,stats.width,1) and audible(ctx.character,ctx.origin,r.Position,c) then
    if now<ts.dodgingUntil and not ts.premiumRoll then table.insert(dodged,p)
    else add("player:"..p.UserId,{player=p,session=ts,humanoid=h}) end
   end
  end
 end
 if Config.ObjectDestruction==true and obstruction then
  local model=obstruction.Instance
  while model and not Destruction.objects[model] do model=model.Parent end
  local id=model and model:GetAttribute("ObjectId")
  if type(id)=="string" and not model:GetAttribute("Destroyed") then add("object:"..id,{object=model}) end
 end
 for _,bot in ipairs(World.Bots) do
  if canDamageBots(sessions[ctx.player]) and bot.alive and bot.root.Parent and (not bot.training or (ctx.position-bot.start).Magnitude<=TrainingRules.Radius) and Rules.InBeam(ctx.origin,direction,bot.root.Position,length,stats.width,1)
   and audible(ctx.character,ctx.origin,bot.root.Position,bot.model) then
   add("bot:"..tostring(bot.id),{bot=bot})
  end
 end
 if bosses then
  for _,boss in ipairs(bosses.bosses) do
   if bosses:CanHit(boss,ctx.player,now) and bossInBeam(boss,ctx.character,ctx.origin,direction,length,stats.width) then
    add("boss:"..boss.spec.id,{boss=boss})
   end
  end
 end
 return ids,details,{origin=ctx.origin,direction=direction,length=length,width=stats.width,power=stats.power,obstruction=obstruction,dodged=dodged}
end
local function clearTrainingStrike(bot)
 local strike=bot.strike
 bot.strike=nil
 if strike and strike.warning then strike.warning:Destroy() end
 if strike and strike.cueUntil and strike.character:GetAttribute("TrainingStrikeAt")==strike.cueUntil then
  strike.character:SetAttribute("TrainingStrikeAt",nil)
  strike.character:SetAttribute("TrainingStrikeCenter",nil)
 end
 return strike
end
local function restoreBot(bot)
 if not bot.model.Parent then return end
 bot.recoveryVersion=(bot.recoveryVersion or 0)+1
 clearTrainingStrike(bot)
 bot.health=bot.maxHealth or Config.BotMaxHealth;bot.alive=true;bot.credit={};bot.trainingTarget=nil;World.UpdateBot(bot)
end
local function knockOutBot(bot)
 if not bot.alive then return end
 clearTrainingStrike(bot)
 bot.trainingTarget=nil;bot.alive=false;bot.recoveryVersion=(bot.recoveryVersion or 0)+1
 local version=bot.recoveryVersion
 task.delay(Config.BotRespawnSeconds,function()
  if bot.model.Parent and not bot.alive and bot.recoveryVersion==version then restoreBot(bot) end
 end)
end
local function destructionHint(intent,result)
 if not result then return nil end
 if result.reason=="level" and not intent.destructionHintShown then
  intent.destructionHintShown=true
  return "This object needs beam level "..tostring(result.required).." to damage"
 end
 if not result.reason and result.destroyed and not intent.destructionBreakShown then
  intent.destructionBreakShown=true
  local name=result.model:GetAttribute("ObjectName") or result.kind or "Object"
  return name.." destroyed · repairs automatically"
 end
 return nil
end
local function stepSustained(p,s,now)
 local intent=s.sustained.intent
 local context=sustainedContext(p,s,now)
 local hits,ended,details,beam=sustained.Step(s.sustained,now,context,resolveSustained)
 sustainedEnd(p,ended,now)
 if beam and not ended then
  intent.evaded=intent.evaded or {}
  for _,target in ipairs(beam.dodged) do
   if not intent.evaded[target.UserId] then
    intent.evaded[target.UserId]=true
    confirmBeamDodge(target,now)
   end
  end
  -- One successful impulse per activity per scream, not five impulses per second.
  if not intent.soccerHit then intent.soccerHit=Soccer.Hit(p,beam.origin,beam.direction,beam.length,beam.width,beam.power)==true end
  if not intent.volleyHit then intent.volleyHit=BeachVolley.Hit(p,beam.origin,beam.direction,beam.length,beam.width,beam.power)==true end
  local noHit=#hits==0 and not intent.damageTotal and not intent.soccerHit and not intent.volleyHit
  if noHit and #beam.dodged>0 and not intent.evadeReported then
   intent.evadeReported=true
   effect:FireClient(p,"SustainedEvaded",nil,p:GetAttribute("SustainedSequence"))
  elseif not intent.coverReported and not intent.evadeReported then
   local blocked=beam.obstruction and noHit and #beam.dodged==0
   intent.coverTicks=blocked and (intent.coverTicks or 0)+1 or nil
   if intent.coverTicks==2 then
    intent.coverReported=true
    effect:FireClient(p,"SustainedCover",nil,p:GetAttribute("SustainedSequence"))
   end
  end
  if not intent.openMissReported then
   local open=noHit and not beam.obstruction and #beam.dodged==0 and not intent.coverReported and not intent.evadeReported
   intent.openTicks=open and (intent.openTicks or 0)+1 or nil
   if intent.openTicks==4 then
    intent.openMissReported=true
    effect:FireClient(p,"SustainedNoHit",nil,p:GetAttribute("SustainedSequence"))
   end
  end
  for _,viewer in ipairs(Players:GetPlayers()) do
   local _,root=parts(viewer)
   if root and (root.Position-beam.origin).Magnitude<=180 then
    effect:FireClient(viewer,"SustainedBeam",beam.origin,p.UserId,beamColor(p,s),beam.direction,beam.length,beam.width,intent.audioStyleId,intent.level)
   end
  end
 end
 local dealt=0;local summaryDamage=0
 local contactPosition,contactChosen
 for _,hit in ipairs(hits) do
  local target=details[hit.id]
  local dealtBefore=dealt
  local targetRoot=(target.bot and target.bot.root) or (target.boss and target.boss.root)
  if target.player then
   local character=target.player.Character
   targetRoot=typeof(character)=="Instance" and character:IsA("Model") and character:FindFirstChild("HumanoidRootPart") or nil
  end
  local position=typeof(targetRoot)=="Instance" and targetRoot:IsA("BasePart") and targetRoot.Parent and targetRoot.Position
  if typeof(position)~="Vector3" or not VoiceCombat.IsFinite(position.X) or not VoiceCombat.IsFinite(position.Y) or not VoiceCombat.IsFinite(position.Z) then position=nil end
  if target.player then
   local ts,h=target.session,target.humanoid
   local actual=math.min(hit.damage,h.Health);dealt+=actual
   ts.credit=ts.credit or {};recordCredit(ts.credit,p,actual,h.MaxHealth,now)
   ts.nextHeal=now+Config.HealQuietSeconds
   if h.Health<=hit.damage then
    awardCombatKO(ts.credit,p,ts.data.level,h.MaxHealth,Config.PlayerKOXP(ts.data.level),now,target.player)
    eject(target.player,h)
   else
    local previous=h.Health
    h.Health-=hit.damage
    if h.Health<previous and now>=(ts.nextBeamCueAt or 0) then
     -- Refresh the 1.4-second defender cue at most once per second across all beams.
     ts.nextBeamCueAt=now+1
     effect:FireClient(target.player,"SustainedDamageTaken",h)
    end
   end
  elseif target.boss then
   dealt+=bosses:Hit(target.boss,p,hit.damage,now)
  elseif target.object then
   local previous=target.object:GetAttribute("ObjectHealth") or 0
   local result=Destruction.Damage(target.object,intent.level,hit.damage)
   local hint=destructionHint(intent,result);if hint then state(p,hint) end
   if result and not result.reason then dealt+=math.max(0,previous-result.health) end
   if result and result.destroyed then
    effect:FireAllClients("Break",result.position,beamColor(p,s))
   end
  else
   local bot=target.bot
   dealt+=math.min(hit.damage,bot.health)
   if hit.firstHit then
    intent.crowdHits=(intent.crowdHits or 0)+1
    if intent.crowdHits==3 then questProgress(p,"Crowd") end
   end
   if bot.training then
    recordCredit(bot.credit,p,math.min(hit.damage,bot.health),bot.maxHealth,now)
    bot.trainingTarget=p;bot.lastTrainingHit=now
   end
   bot.health=math.max(0,bot.health-hit.damage)
   local ko=bot.health==0
   if ko then
    if bot.training then awardCombatKO(bot.credit,p,bot.training.level,bot.maxHealth,bot.training.xp,now,nil,bot.training) end
    knockOutBot(bot)
   elseif hit.firstHit then World.ReactToScream(bot,context.position) end
   World.UpdateBot(bot)
   if not bot.training then
    local rewardCoins,rewardXP=SustainedRewards.Hit(intent,s.botRewards,bot.id,now,hit.firstHit,ko)
    if rewardCoins>0 or rewardXP>0 then coins(p,rewardCoins);xp(p,rewardXP) end
   end
  end
  if not target.object then summaryDamage+=dealt-dealtBefore end
  if dealt>dealtBefore and not contactChosen then contactChosen=true;contactPosition=position end
 end
 if summaryDamage>0 then recordDamage(p,s,now,summaryDamage) end
 if dealt>0 then
  s.nextHeal=now+Config.HealQuietSeconds
  intent.damageTotal=(intent.damageTotal or 0)+dealt
  effect:FireClient(p,"SustainedHit",contactPosition,p:GetAttribute("SustainedSequence"),math.floor(intent.damageTotal+.5))
 end
end
local function cast(p,request)
 local s=sessions[p];local c,r=parts(p);if not s or not r or type(request)~="table" then return end
 p:SetAttribute("CaptureStarted",0)
 local now=os.clock();local style=Config.GetSound(s.data.sound)
 local aim=request.aim
 if typeof(aim)~="Vector3" or not VoiceCombat.IsFinite(aim.X) or not VoiceCombat.IsFinite(aim.Y) or not VoiceCombat.IsFinite(aim.Z) then VoiceCombat.Cancel(s.voice);return end
 local origin=attackOrigin(c,r)
 local delta=aim-origin
 if delta.Magnitude<.01 or delta.Magnitude>2048 then VoiceCombat.Cancel(s.voice);return end
 if not VoiceCombat.Release(s.voice,now,request.sequence,request.power,style~=nil and style.level<=s.data.level and canCapture(p,s,now)) then return end
 local sound=VoiceCombat.Stats(s.data.level,request.power,s.data.amplifierEquipped==true,s.data.megaphoneEquipped==true,Config.Gear.Multiplier(s.data))
 local direction=delta.Unit
 s.nextCast=s.voice.nextCast;p:SetAttribute("ScreamReleased",workspace:GetServerTimeNow());p:SetAttribute("CaptureStarted",0)
 local obstruction=beamObstruction(c,origin,direction,sound.range,Players:GetPlayers())
 local length=obstruction and obstruction.Distance or sound.range
 effect:FireAllClients("Scream",origin,style.id,beamColor(p,s),direction,length,sound.width)
 Soccer.Hit(p,origin,direction,length,sound.width,sound.power)
 BeachVolley.Hit(p,origin,direction,length,sound.width,sound.power)
 local castMessage
 if obstruction then
  local result=Config.ObjectDestruction==true and Destruction.Damage(obstruction.Instance,s.data.level,sound.damage) or nil
  if result then
   if result.reason=="level" then castMessage="Requires level "..result.required
   elseif not result.reason then
    s.nextHeal=now+Config.HealQuietSeconds
    local name=result.model:GetAttribute("ObjectName") or result.kind
    castMessage=result.destroyed and name.." destroyed" or string.format("%s hit · %d durability left",name,result.health)
    if result.destroyed then effect:FireAllClients("Break",result.position,beamColor(p,s)) end
   end
  end
 end
 local hits=0;local paid=0;local playerHits=0;local evades=0;local knockoutMessage;local summaryDamage=0
 for _,bot in ipairs(World.Bots) do
  if canDamageBots(s) and bot.alive and bot.root.Parent and (not bot.training or (r.Position-bot.start).Magnitude<=TrainingRules.Radius) and Rules.InBeam(origin,direction,bot.root.Position,length,sound.width,1) and audible(c,origin,bot.root.Position,bot.model) then
   hits+=1;summaryDamage+=math.min(sound.damage,bot.health)
   if bot.training then recordCredit(bot.credit,p,math.min(sound.damage,bot.health),bot.maxHealth,now);bot.trainingTarget=p;bot.lastTrainingHit=now end
   bot.health=math.max(0,bot.health-sound.damage);local ko=bot.health==0
   if ko then
    if bot.training then awardCombatKO(bot.credit,p,bot.training.level,bot.maxHealth,bot.training.xp,now,nil,bot.training) end
    knockOutBot(bot)
   else World.ReactToScream(bot,r.Position) end
   World.UpdateBot(bot)
   if not bot.training and now>=(s.botRewards[bot.id] or 0) and paid<5 then
    s.botRewards[bot.id]=now+VoiceCombat.Cooldown;paid+=1;coins(p,ko and 5 or 2);xp(p,ko and SustainedRewards.KOXP or SustainedRewards.HitXP)
   end
  end
 end
 if bosses then
  for _,boss in ipairs(bosses.bosses) do
   if bosses:CanHit(boss,p,now) and bossInBeam(boss,c,origin,direction,length,sound.width) then
    local actual=bosses:Hit(boss,p,sound.damage,now)
    if actual>0 then summaryDamage+=actual;s.nextHeal=now+Config.HealQuietSeconds end
   end
  end
 end
 if hits>=3 then questProgress(p,"Crowd") end
 if Config.InArena(r.Position) then
  for _,target in ipairs(Players:GetPlayers()) do
   local ts=sessions[target];local tc,tr,th=parts(target)
   if target~=p and sameCombatMode(s,ts) and tr and Rules.CanTarget(r.Position,tr.Position,ts.protectedUntil,now,sound.range+2) and Rules.InBeam(origin,direction,tr.Position,length,sound.width,1) and audible(c,origin,tr.Position,tc) then
    if now<ts.dodgingUntil and not ts.premiumRoll then evades+=1;confirmBeamDodge(target,now)
    else
     playerHits+=1;summaryDamage+=math.min(sound.damage,th.Health)
     ts.nextHeal=now+Config.HealQuietSeconds
     ts.credit=ts.credit or {};recordCredit(ts.credit,p,math.min(sound.damage,th.Health),th.MaxHealth,now)
     if th.Health<=sound.damage then
      awardCombatKO(ts.credit,p,ts.data.level,th.MaxHealth,Config.PlayerKOXP(ts.data.level),now,target)
      eject(target,th);knockoutMessage="Player knockout"
     else th.Health-=sound.damage;state(target) end
    end
   end
  end
 end
 if summaryDamage>0 then recordDamage(p,s,now,summaryDamage) end
 local totalHits=hits+playerHits
 if totalHits>0 then s.nextHeal=now+Config.HealQuietSeconds end
 if knockoutMessage then castMessage=knockoutMessage
 elseif totalHits>0 then castMessage=string.format("Hit %d %s · %d damage each",totalHits,totalHits==1 and "target" or "targets",sound.damage)
 elseif not castMessage then castMessage=evades>0 and "Beam dodged" or obstruction and "Beam stopped by cover" or "Beam missed" end
 state(p,castMessage)
end
local function finishDodge(p,s,c,r,h,started,now)
 if sessions[p]~=s or p.Character~=c or s.lastDodge~=started or not h.Parent or h.Health<=0
  or now<(s.knockedUntil or 0) or h.PlatformStand then return end
 h.AutoRotate=true
 if r.Parent and not r.Anchored then r:SetNetworkOwnershipAuto() end
end
local function dodge(p,sideIntent)
 local s=sessions[p];local c,r,h=parts(p);local now=os.clock()
 if s then cancelSustained(p,s,now);VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0) end
 if not s or not r or r.Anchored or h.Sit or h.SeatPart or h.PlatformStand or now<s.nextDodge or now<(s.knockedUntil or 0) or h.FloorMaterial==Enum.Material.Air then return end
 local cooldown=Entitlements.CanUseMovement(p,r.Position) and Config.DodgeDuration or Config.DodgeCooldown
 s.nextDodge=now+cooldown;s.dodgingUntil=now+Config.DodgeDuration
 s.lastDodge=now;s.premiumRoll=cooldown<Config.DodgeCooldown
 p:SetAttribute("DodgeEnds",workspace:GetServerTimeNow()+Config.DodgeDuration)
 p:SetAttribute("DodgeReady",workspace:GetServerTimeNow()+cooldown)
 local direction,side,front=DodgeMotion.Direction(r.CFrame,h.MoveDirection,sideIntent)
 local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Exclude;params.FilterDescendantsInstances={c};params.RespectCanCollide=true
 local hit=workspace:Blockcast(r.CFrame,Vector3.new(2,3,2),direction*Config.DodgeDistance,params)
 local distance=hit and math.max(0,hit.Distance-1) or Config.DodgeDistance
 local start=r.CFrame;local facing=start.Rotation;r:SetNetworkOwner(nil);h.AutoRotate=false
 p:SetAttribute("DodgeSide",side);p:SetAttribute("DodgeForward",front)
 p:SetAttribute("DodgeStarted",workspace:GetServerTimeNow());p:SetAttribute("DodgeDirection",direction)
 effect:FireAllClients("Dodge",r.Position,p.UserId)
 task.spawn(function()
  local previousDistance=0
  while sessions[p]==s and s.lastDodge==now and c.Parent and p.Character==c and h.Health>0 and s.dodgingUntil>os.clock() and os.clock()-now<Config.DodgeDuration do
   local t=math.clamp((os.clock()-now)/Config.DodgeDuration,0,1)
   local desired=distance*(t*t*(3-2*t));local step=desired-previousDistance
   local target=DodgeMotion.Step(workspace,r.CFrame,direction,step,params,h)
   if not target then break end
   r.CFrame=CFrame.new(target)*facing;previousDistance=desired
   r.AssemblyLinearVelocity=Vector3.zero;RunService.Heartbeat:Wait()
  end
  if sessions[p]==s and s.lastDodge==now then
   s.dodgingUntil=math.min(s.dodgingUntil,os.clock());p:SetAttribute("DodgeEnds",workspace:GetServerTimeNow())
  end
  finishDodge(p,s,c,r,h,now,os.clock())
 end)
 state(p)
end
local function closeConversation(p)
 local s=sessions[p];local bot=s and s.conversationBot
 if bot and bot.talkingTo==p then bot.talkingTo=nil;bot.socialUntil=0 end
 if s then s.conversationBot=nil end
end
local function gearAction(p,s,id,intent)
 local ok,message=Config.Gear.Act(s.data,id,intent)
 state(p,message,nil,not ok)
end
local function megaphone(p,s,toggle) gearAction(p,s,"Megaphone",toggle) end
local function microSpeaker(p,s,toggle) gearAction(p,s,"MicroSpeaker",toggle) end
local function vendorPurchase(p,s,arg)
 local bot=s.conversationBot;local _,root=parts(p)
 if type(arg)~="table" or not Config.Gear.Get(arg.product) or not bot or arg.npc~=bot.id or bot.role~="Vendor" or not bot.alive or not bot.root.Parent or bot.talkingTo~=p or (bot.socialUntil or 0)<=os.clock() or not root or not InteractionRules.CanReachNpc(p.Character,bot.model,14) then
  state(p,"Speak with the market vendor nearby before buying.",nil,true);return
 end
 -- No yielding between ownership check and debit: duplicate requests never charge twice.
 gearAction(p,s,arg.product,false)
end
local function talk(p,id)
 local s=sessions[p];local _,r=parts(p);if not s or not r or type(id)~="string" or os.clock()<(s.nextTalk or 0) then return end
 for _,b in ipairs(World.Bots) do if b.id==id and b.alive and b.root.Parent and InteractionRules.CanReachNpc(p.Character,b.model,14) then
  if b.training then state(p,"Stand on the pad and hit to spar. Move out of red strikes or dodge.");return end
  if b.talkingTo and b.talkingTo~=p and (b.socialUntil or 0)>os.clock() then state(p,b.name.." is speaking with someone. Try again shortly.");return end
  -- Dialogue cancellation is authoritative, even if the client stop packet
  -- is delayed or omitted. The availability gate keeps subsequent pulses out.
  cancelSustained(p,s,os.clock());VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0)
  closeConversation(p);s.conversationBot=b;b.talkingTo=p
  s.nextTalk=os.clock()+2
  local contextLine
  for _,questId in ipairs(b.questIds or {}) do
   local q=Config.GetQuest(questId);local progress=s.data.quests[questId]
   if q and progress and not progress.claimed then
    if progress.progress>=q.goal then contextLine="You finished my task! Your reward is waiting in Quests.";break
    elseif s.activeQuest==questId then
     local soccer=Soccer.Status(p)
     local deliveryStop=Config.GetDeliveryStop(s.deliveryStop)
     contextLine="For our task: "..QuestGuide.Step(q,progress.progress,s.carrying,s.raceStart~=nil,soccer and soccer.detail,deliveryStop and deliveryStop.name)
    end
   end
  end
  if not contextLine and b.name=="Nick Booty" and s.data.achievements.NickChampion then contextLine="My champion is back! I have practiced. The goal is still winning." end
  local message=b.name..": "..World.Talk(b,p,contextLine)
  if b.name=="Nick Booty" and not s.data.achievements.FoundNick then
   s.data.achievements.FoundNick=true;local foundCoins=coins(p,50);message="Hidden achievement: Found Nick Booty! +"..foundCoins.." coins. "..message
  end
  if b.questIds then
   for _,questId in ipairs(b.questIds) do s.data.availableQuests[questId]=true end
   message..=" · Tasks available in Quests"
  end
  b.socialUntil=os.clock()+20
  local choices={}
  for _,id in ipairs(b.questIds or {}) do
   local q=Config.GetQuest(id);local progress=s.data.quests[id]
   if q then table.insert(choices,{id=id,name=q.name,description=q.description,claimed=progress and progress.claimed==true,complete=progress and progress.progress>=q.goal}) end
  end
  local gardenPvp=Config.HasGardenPvp()
  local pvpHint=gardenPvp and "PvP is active in the stadium arena and on marked lower Garden terraces. Check the map for red areas." or "Player combat stays inside the central arena."
  local gardenHint=gardenPvp and "Water each flowerbed with its prompt. On the way to the beach, check the PvP status on the lower Garden terraces." or "The raised flowerbeds in Rambla Gardens need water. Use the interaction prompt beside each bed after accepting my task."
  local hints={Gardener=gardenHint,Vendor="The café sends orders along the waterfront. Collect one, then check your objective for its destination.",Soccer="I call it an assist when I miss. Your microphone can steer a training ball; softer shots give you more control.",BeachWorker="Please keep the sand clear. You can follow the promenade to the pier and the hidden courts beyond it.",Busker=gardenPvp and pvpHint or "Come for the music, stay for the beach. The central arena is the only place where players can damage each other."}
  state(p,message,{npc=b.model,name=b.name,line=message,hint=hints[b.role] or (gardenPvp and pvpHint or "Explore the courtyards, shops and waterfront. Some residents offer tasks; player combat stays inside the central arena."),quests=choices,products=b.role=="Vendor" and Config.Gear.Products(s.data) or nil});return
 end end
end
local function dev(p,command)
 if Commerce.Busy(p) then state(p,"Wait for your purchase to finish saving.");return end
 local s=sessions[p];if not s or not Access.IsAuthorized(p,game.CreatorType,game.CreatorId,RunService:IsStudio(),game.GameId) then return end
 local valid={Coins=true,XP=true,AddLevels=true,MaxLevel=true,LevelOne=true,Heal=true,Hub=true,Arena=true,Beach=true,ResetQuests=true,ResetBots=true,StudioMovement=true,Fly=true}
 if type(command)~="string" or not valid[command] then return end
 if command=="Fly" and not toolAuthorized(p) then return end
 if command=="StudioMovement" and not game:GetService("RunService"):IsStudio() then return end
 if command=="ResetBots" and not localFixture then state(p,"Reset bots requires the isolated local Studio fixture; shared fights are unchanged.");return end
 if s.testBeam then testBeamEnd(p,s,os.clock()) end
 -- Freeze legitimate progress before any test mutation. Keep renewing/releasing its lease.
 if not s.testBaseline then
  cancelSustained(p,s,os.clock());VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0);s.credit={}
  s.testBaseline=Profiles.Sanitize(s.data);s.data=Profiles.Sanitize(s.data)
 end
 local c,_,h=parts(p)
 local positions={Hub=World.SafeSpawn,Arena=Config.CompactCity and CFrame.new(Config.CityLayout.Teleports.Arena) or CFrame.new(0,6,0),Beach=Config.CompactCity and CFrame.new(Config.CityLayout.Teleports.Beach) or CFrame.new(0,4,403)}
 if command=="Fly" then
  if s.flight then TestFlight.Stop(p,s)
  else
   cancelSustained(p,s,os.clock());VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0)
   local ok,reason=TestFlight.Start(p,s,toolAuthorized(p),flightBounds,os.clock())
   if not ok then state(p,reason or "Flight unavailable");return end
   if s.damageSummary then clearDamageSummary(p,s) end
   closeConversation(p);Soccer.Cancel(p);s.sprintRequested=false
  end
 elseif command=="Coins" then s.data.coins+=1000
 elseif command=="XP" then xp(p,500)
 elseif command=="AddLevels" then
  s.data.level=math.min(Config.MaxLevel,s.data.level+10)
  if s.data.level==Config.MaxLevel then s.data.xp=0 end
 elseif command=="MaxLevel" then s.data.level=Config.MaxLevel;s.data.xp=0
 elseif command=="LevelOne" then s.data.level=1;s.data.xp=0;s.data.sound="TinyAah"
 elseif command=="Heal" and h then h.Health=h.MaxHealth
 elseif positions[command] and c then c:PivotTo(positions[command]);protect(p,s)
 elseif command=="ResetQuests" then stopQuest(p);s.data.quests={}
 elseif command=="StudioMovement" then Entitlements.SetStudioMovement(p,not Entitlements.HasStudioMovement(p))
 elseif command=="ResetBots" then for _,b in ipairs(World.Bots) do restoreBot(b) end
 else return end
 syncHealth(p,command=="Heal");state(p,command=="Fly" and (s.flight and "Test flight ON · WASD, Space up, Ctrl down · combat disabled" or "Test flight OFF · returned to your starting position") or command=="StudioMovement" and ("Studio movement test "..(Entitlements.HasStudioMovement(p) and "ON" or "OFF").." · safe areas only · not saved") or "Test applied · progress is temporary. PvP is test-to-test only; NPC damage/reset requires the isolated local Studio fixture.")
end
World.OnVehicleSweep=function(car,previous,nextFrame)
 for player,s in pairs(sessions) do
  local character,root,humanoid=parts(player);local now=os.clock()
  if root and not s.flight and now>=s.protectedUntil and now>=(s.nextCarHit or 0) and Rules.VehicleSweep(previous*CFrame.new(0,.55,0),nextFrame*CFrame.new(0,.55,0),root.Position,Vector3.new(8,4,4.5)) then
   cancelSustained(player,s,now);VoiceCombat.Cancel(s.voice);player:SetAttribute("CaptureStarted",0)
   s.nextCarHit=now+4;s.knockedUntil=now+1.3;s.dodgingUntil=0;s.sprintRequested=false;s.nextHeal=now+Config.HealQuietSeconds
   player:SetAttribute("DodgeEnds",0);player:SetAttribute("KnockdownEnds",workspace:GetServerTimeNow()+1.3)
   local damage=math.clamp(math.floor(car.speed*1.1),15,35)
   if humanoid.Health<=damage then eject(player,humanoid);s.knockedUntil=0
   else
    humanoid.Health-=damage;humanoid.PlatformStand=true;humanoid.AutoRotate=false;root:SetNetworkOwner(nil)
    local direction=(nextFrame.Position-previous.Position).Unit
    local sideways=Vector3.new(0,0,car.lane%240<120 and -1 or 1)
    root.AssemblyLinearVelocity=direction*8+sideways*28+Vector3.new(0,12,0);root.AssemblyAngularVelocity=Vector3.new(0,0,4)*car.direction
    local recoveryEnds=s.knockedUntil
    task.delay(1.3,function()
     if sessions[player]==s and s.knockedUntil==recoveryEnds and player.Character==character and humanoid.Parent and humanoid.Health>0 then
      s.knockedUntil=0;player:SetAttribute("KnockdownEnds",0)
      humanoid.PlatformStand=false;humanoid.AutoRotate=true;root.AssemblyAngularVelocity=Vector3.zero
      local look=root.CFrame.LookVector;look=Vector3.new(look.X,0,look.Z);if look.Magnitude<.01 then look=Vector3.new(0,0,-1) end
      local recovered=root.Position+Vector3.new(0,2,0)
      root.AssemblyLinearVelocity=Vector3.zero
      root.CFrame=CFrame.lookAt(recovered,recovered+look)
      humanoid:ChangeState(Enum.HumanoidStateType.GettingUp);root:SetNetworkOwnershipAuto()
     end
    end)
   end
   state(player,"Traffic hit · -"..damage.." HP")
  end
 end
end
local function interactQuest(p,obj)
  if not obj.Enabled or not obj:IsDescendantOf(workspace.ScreamSimulatorWorld) then return end
  local s=sessions[p];local _,r=parts(p);local marker=obj.Parent
  if not s or s.flight or not r or not marker or not marker:IsA("BasePart") or (r.Position-marker.Position).Magnitude>12 then return end
  local active=Config.GetQuest(s.activeQuest)
  local progress=active and s.data.quests[active.id]
  if progress and (progress.claimed or progress.progress>=active.goal) then state(p,"Task complete · claim your reward in Quests.");return end
  local kind=marker:GetAttribute("QuestAction")
  if kind=="Garden" and s.activeQuest=="garden" then
   if s.collected[marker.Name] then state(p,"This bed is already watered.");return end
   s.collected[marker.Name]=true;questProgress(p,"Garden");state(p,"Flowers watered · thanks for helping the neighborhood!")
  elseif kind=="Litter" and s.activeQuest=="beach" then
   if s.collected[marker.Name] then state(p,"Already collected this bottle.");return end
   s.collected[marker.Name]=true;questProgress(p,"Litter")
  elseif kind=="Pickup" and s.activeQuest=="delivery" then
   if s.carrying then state(p,"You already have an order. Check your objective for its destination.");return end
   local stop=Config.DeliveryStops[math.random(1,#Config.DeliveryStops)]
   s.deliveryStop=stop.id;s.questDeadline=os.clock()+90;s.carrying=true;state(p,"Order collected · "..stop.name.." · 90s")
  elseif kind=="Dropoff" and s.activeQuest=="delivery" then
   if s.carrying and s.questDeadline and os.clock()<=s.questDeadline then
    if marker:GetAttribute("DeliveryStop")~=s.deliveryStop then local stop=Config.GetDeliveryStop(s.deliveryStop);state(p,"This order is for the "..(stop and stop.name or "assigned stop")..".");return end
    s.carrying=false;s.questDeadline=nil;s.deliveryStop=nil;questProgress(p,"Delivery")
   else state(p,"Pick up a fresh order from the café first.") end
  elseif kind=="RaceStart" and s.activeQuest=="sprint" then
   if s.raceStart then state(p,"Your race is already running. Follow the boardwalk to the finish.");return end
   s.raceStart=os.clock();s.questDeadline=s.raceStart+25;state(p,"Go! Follow the promenade east to the finish · 25s")
  elseif kind=="RaceFinish" and s.activeQuest=="sprint" then
   if s.raceStart and os.clock()-s.raceStart>=3 and s.questDeadline and os.clock()<=s.questDeadline then s.questDeadline=nil;s.raceStart=nil;questProgress(p,"Race")
   else state(p,"Start at the lifeguard tower and beat 25 seconds.") end
  else state(p,"Accept the matching quest from the Quests menu first.") end
end
for _,obj in ipairs(workspace.ScreamSimulatorWorld:GetDescendants()) do
 if obj:IsA("ProximityPrompt") and obj.Parent:GetAttribute("QuestAction") then obj.Triggered:Connect(function(p) interactQuest(p,obj) end) end
end
action.OnServerEvent:Connect(function(p,verb,arg)
 local s=sessions[p];if not s or type(verb)~="string" then return end
 if verb=="TestBeamStop" and arg==nil then
  if testBeamEnd(p,s,os.clock()) then state(p) end
  return
 end
 if verb=="FlightStop" then if s.flight then TestFlight.Stop(p,s) end;return end
 if verb=="FlightInput" then
  if s.flight then
   if toolAuthorized(p) then TestFlight.Input(p,s,arg,os.clock()) else TestFlight.Stop(p,s) end
  end
  return
 end
 if s.flight and not (verb=="DevCommand" and arg=="Fly") and verb~="SetSettings" and verb~="Sync" then return end
 -- Validated idempotent stops must survive saturation; they grant no new action.
 if verb=="Sprint" and arg==false then s.sprintRequested=false;return end
 if verb=="EndConversation" and arg==nil then
  if s.conversationBot then closeConversation(p) end
  return
 end
 local now=os.clock()
 if verb=="SustainedStop" and s.sustained then
  local active=s.sustained.protocol.active
  -- Stop can expire state before validating; only the current sequence bypasses quota.
  if active and arg==active.sequence then sustainedEnd(p,sustained.Stop(s.sustained,now,arg),now);return end
 elseif verb=="CancelCast" and not s.sustained and arg==nil then
  if s.voice.capture then VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0) end
  return
 elseif verb=="MicReady" and arg==false then
  -- Clean leftover attacks too, but do not amplify repeated idle false packets.
  if s.micReady~=false or (s.sustained and s.sustained.protocol.active) or s.voice.capture then
   s.micReady=false;cancelSustained(p,s,now);VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0)
  end
  return
 end
 if s.testBeam and verb~="TestBeamPulse" and verb~="TestBeamBegin" and verb~="DevCommand" and verb~="SetSettings" and verb~="Sync" then return end
 s.requestWindow=s.requestWindow or now;s.requestCount=s.requestCount or 0
 if now-s.requestWindow>=1 then s.requestWindow=now;s.requestCount=0 end
 s.requestCount+=1;if s.requestCount>30 then return end
 if verb=="TestBeamBegin" or verb=="TestBeamPulse" then
  local authorized=Access.IsAuthorized(p,game.CreatorType,game.CreatorId,RunService:IsStudio(),game.GameId)
  if verb=="TestBeamPulse" then
   local _,ended=testBeam.Pulse(p,s,authorized,localFixture,now,arg)
   if ended then testBeamEnd(p,s,now,true);state(p) end
  else
   if Commerce.Busy(p) then state(p,"Wait for your purchase to finish saving.");return end
   local ok,reason=testBeam.ValidateStart(p,s,authorized,localFixture,now,arg)
   if not ok then
    -- Do not return detailed test information to callers outside the guard.
    if TestBeamRules.Available(authorized,localFixture) then state(p,reason) end
    return
   end
   local protocol=s.sustained and s.sustained.protocol
   if (protocol and (protocol.active or now<protocol.nextStart)) or now<(s.voice.nextCast or 0) then
    state(p,"Finish the microphone attack and cooldown before Test Beam.")
    return
   end
   if not s.testBaseline then s.testBaseline=Profiles.Sanitize(s.data);s.data=Profiles.Sanitize(s.data);s.credit={} end
   cancelSustained(p,s,now);VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0)
   ok,reason=testBeam.Start(p,s,authorized,localFixture,now,arg,Config.Gear.Multiplier(s.data))
   state(p,ok and "Silent beam test · isolated test damage · no saved rewards" or reason)
  end
  return
 end
 if s.sustained then
  if verb=="BeginCast" or verb=="Cast" or verb=="CancelCast" then return end
  if verb=="SustainedBegin" then
   local ok,_,ended=sustained.Begin(s.sustained,now,arg,sustainedContext(p,s,now))
   sustainedEnd(p,ended,now)
   if ok then
    s.sustained.intent.audioStyleId=s.data.sound
    p:SetAttribute("SustainedSequence",arg.sequence)
    p:SetAttribute("SustainedEndsAt",workspace:GetServerTimeNow()+require(ReplicatedStorage.Shared.SustainedAttack).MaxDuration)
    p:SetAttribute("SustainedActive",true)
   end
   return
  elseif verb=="SustainedPulse" then
   local _,_,ended=sustained.Pulse(s.sustained,now,arg,sustainedContext(p,s,now))
   sustainedEnd(p,ended,now);return
  elseif verb=="SustainedStop" then sustainedEnd(p,sustained.Stop(s.sustained,now,arg),now);return end
 end
 if verb=="BeginCast" then
  p:SetAttribute("CaptureStarted",0)
  if VoiceCombat.Begin(s.voice,now,arg,canCapture(p,s,now)) then p:SetAttribute("CaptureStarted",workspace:GetServerTimeNow()) end;return
 elseif verb=="CancelCast" then VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0);return
 elseif verb=="MicReady" then s.micReady=arg==true;if not s.micReady then cancelSustained(p,s,now);VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0) end;return
 elseif verb=="Cast" then cast(p,arg);return elseif verb=="Dodge" then dodge(p,arg);return
 elseif verb=="ExtraJump" then
  local _,root,h=parts(p)
  if root and not root.Anchored and not h.Sit and not h.SeatPart and not h.PlatformStand and Entitlements.CanUseMovement(p,root.Position) and now>=(s.nextExtraJump or 0) and now>=s.dodgingUntil and now>=(s.knockedUntil or 0) and h.FloorMaterial==Enum.Material.Air and s.jumpOriginY and root.Position.Y<s.jumpOriginY+24 then
   s.nextExtraJump=now+.25
   local v=root.AssemblyLinearVelocity
   local remaining=math.max(0,s.jumpOriginY+24-root.Position.Y)
   local impulse=math.min(45,math.sqrt(2*workspace.Gravity*remaining))
   root.AssemblyLinearVelocity=Vector3.new(v.X,impulse,v.Z)
  end
  return
 elseif verb=="Sprint" then if type(arg)=="boolean" then s.sprintRequested=arg end;return end
 local now=os.clock();if now<s.nextAction then return end;s.nextAction=now+0.15
 if verb=="Sync" then state(p)
 elseif verb=="Talk" then talk(p,arg)
 elseif verb=="DevCommand" then dev(p,arg)
 elseif verb=="EquipSound" then local sound=type(arg)=="string" and Config.GetSound(arg);if sound and sound.level<=s.data.level then s.data.sound=sound.id;state(p,sound.name.." equipped") end
 elseif verb=="Gear" then
  if type(arg)=="string" then gearAction(p,s,arg,true)
  elseif type(arg)=="table" and type(arg.id)=="string" and (arg.intent=="buy" or arg.intent=="equip" or arg.intent=="unequip") then
   gearAction(p,s,arg.id,arg.intent)
  end
 elseif verb=="MicroSpeaker" then microSpeaker(p,s,true)
 elseif verb=="Megaphone" then megaphone(p,s,true)
 elseif verb=="VendorPurchase" then vendorPurchase(p,s,arg)
 elseif verb=="ShopPurchase" then Commerce.Prompt(p,arg)
 elseif verb=="ActivateBoost" then Commerce.Activate(p,arg)
 elseif verb=="ShopRefresh" then task.spawn(Commerce.Load,p)
 elseif verb=="SetCustomColor" then
  local hex=ShopCatalog.Hex(arg)
  if hex and Entitlements.HasSpectrum(p) then s.data.customColor=hex;s.data.useCustomColor=true;state(p,"Signature color equipped") end
 elseif verb=="SetAura" and arg=="Gold" then s.data.aura=arg;s.data.useCustomColor=false;state(p)
 elseif verb=="AcceptQuest" then
  local q=type(arg)=="string" and Config.GetQuest(arg)
  if q and q.retired==true then return end
  if q and q.menuAvailable~=true and not s.data.availableQuests[q.id] then state(p,"Meet "..(q.giver or "the quest giver").." to unlock this task.");return end
  if q and q.id=="nick" then
   local _,root=parts(p)
   if not root or (root.Position-(Config.CompactCity and Config.CityLayout.Soccer.center or Vector3.new(647,4,547))).Magnitude>90 then state(p,"Return to Nick's coastal court to start.");return end
  end
  if q then local v=s.data.quests[q.id];if not v then v={progress=0,claimed=false};s.data.quests[q.id]=v end
   if not v.claimed and v.progress>=q.goal then state(p,"Task complete · claim your reward.");return end
   if s.activeQuest==q.id then state(p,"Task already active · continue your current attempt.");return end
   if not v.claimed then stopQuest(p);v.progress=0;s.activeQuest=q.id;state(p,q.name.." accepted")
    if q.id=="nick" then Soccer.Start(p,function(message) state(p,message) end,function()
     if sessions[p]==s and s.activeQuest=="nick" then s.questDeadline=nil;questProgress(p,"Soccer");state(p,"Nick: WE DID IT! Claim your reward in Quests.") end
    end,function() if sessions[p]==s and s.activeQuest=="nick" then stopQuest(p);state(p,"Nick: Attempt ended. Return to the court and accept my task to try again.") end end) end
   end end
 elseif verb=="AbandonQuest" then stopQuest(p);state(p,"Task abandoned. Unfinished progress was reset; earned rewards remain claimable.")
 elseif verb=="ClaimQuest" then
  local q=type(arg)=="string" and Config.GetQuest(arg);local v=q and s.data.quests[q.id]
  if v and not v.claimed and v.progress>=q.goal then v.claimed=true;if q.id=="nick" then s.data.achievements.NickChampion=true end;local coinCredit=coins(p,q.coins);local xpCredit=xp(p,q.xp);if s.activeQuest==q.id then stopQuest(p) end;state(p,"Quest reward · +"..xpCredit.." XP · +"..coinCredit.." coins") end
 elseif verb=="SetSettings" and type(arg)=="table" then
  if type(arg.volume)=="number" and arg.volume==arg.volume then s.data.settings.volume=math.clamp(arg.volume,0,1) end
  if type(arg.reducedShake)=="boolean" then s.data.settings.reducedShake=arg.reducedShake end;state(p)
 end
end)
local function arrivedFromAnotherPlace(p)
 if game.GameId==0 then return false end
 local join=p:GetJoinData()
 local source=join.SourcePlaceId
 return join.SourceGameId==game.GameId and type(source)=="number" and source>0 and source~=game.PlaceId
end
local function joined(p)
 if closing then return end
 task.spawn(Entitlements.Refresh,p)
 local data,save,loadMessage,recoveryWarning
 if localFixture then data,save,loadMessage=Profiles.Default(),false,"Local sustained prototype · saving disabled"
 else data,save,loadMessage,recoveryWarning=Profiles.Load(p.UserId,arrivedFromAnotherPlace(p)) end
 if closing or not p.Parent then
  if save then
   local completed,ok,reason=pcall(Profiles.Save,p.UserId,data,true,shutdownSaveDeadline)
   if not completed or not ok then
    warn("ScreamSimulator late profile release failed",p.UserId,completed and reason or ok)
   end
  end
  return
 end
 local s={data=data,canSave=save,recoveryWarning=recoveryWarning,rewardIdentity={},voice=VoiceCombat.New(),voiceEligibility=VoiceEligibility.New(localFixture,os.clock(),p.UserId),micReady=false,protectedUntil=0,nextCast=0,nextDodge=0,dodgingUntil=0,nextAction=0,nextHeal=os.clock()+Config.HealQuietSeconds,
 botRewards={},credit={},collected={},sprintRequested=false,sprintRunning=false,sprintRegenAt=0,sprintCharge=Config.SprintDuration,sprintLockedUntil=0,lastStep=os.clock(),nextAutosaveAt=save and os.clock()+30 or nil};sessions[p]=s
 -- Visibility cache only. Every activation, pulse and tick rechecks the dynamic server guard.
 s.testBeamAvailable=toolAuthorized(p)
 task.spawn(Commerce.Load,p)
 if sustainedEnabled then
  s.sustained=sustained.New()
  p:SetAttribute("SustainedActive",false);p:SetAttribute("SustainedReadyAt",0);p:SetAttribute("SustainedEndsAt",0)
 end
 local function spawn(c)
  local h=c:WaitForChild("Humanoid",10)
  if not h or not p.Parent or sessions[p]~=s or p.Character~=c or s.character==c then return end
  if s.testBeam then testBeamEnd(p,s,os.clock()) end
  if s.flight then TestFlight.Stop(p,s) end;s.character=c;closeConversation(p)
  s.jumpPower=h.JumpPower;s.jumpHeight=h.JumpHeight
  h.MaxHealth=Config.HealthForLevel(s.data.level);h.Health=h.MaxHealth;h.WalkSpeed=16
  s.sprintCharge=Config.SprintDuration;s.sprintRequested=false;s.sprintRunning=false;s.sprintRegenAt=0;s.lastStep=os.clock();s.sprintLockedUntil=0;s.dodgingUntil=0;s.knockedUntil=0;s.premiumRoll=false
  s.nextHeal=os.clock()+Config.HealQuietSeconds;s.nextBeamCueAt=nil
  p:SetAttribute("DodgeEnds",0);p:SetAttribute("DodgeStarted",0);p:SetAttribute("KnockdownEnds",0)
  p:SetAttribute("Sprinting",false);p:SetAttribute("SprintCooldown",0);p:SetAttribute("SprintCharge",Config.SprintDuration)
  protect(p,s);state(p)
 end
 s.characterRemovingConnection=p.CharacterRemoving:Connect(function(c)
  if sessions[p]~=s or s.character~=c then return end
  if s.damageSummary then clearDamageSummary(p,s) end
  if s.testBeam then testBeamEnd(p,s,os.clock()) end
  if s.flight then TestFlight.Stop(p,s) end;closeConversation(p);cancelSustained(p,s,os.clock());VoiceCombat.Cancel(s.voice)
  p:SetAttribute("CaptureStarted",0);s.sprintRequested=false;s.character=nil
 end)
 s.characterAddedConnection=p.CharacterAdded:Connect(spawn);if p.Character then task.spawn(spawn,p.Character) end
 stepVoiceEligibility(p,s,os.clock());dispatchVoiceEligibility(os.clock())
 state(p,loadMessage or "Welcome · train for XP, unlock beam styles, and explore the coast")
end
local function joinTracked(p)
 if closing then return end
 joinsInFlight+=1
 local ok,err=pcall(joined,p)
 joinsInFlight-=1
 if not ok then warn("ScreamSimulator profile join failed",err) end
end
Players.PlayerAdded:Connect(joinTracked);for _,p in ipairs(Players:GetPlayers()) do task.spawn(joinTracked,p) end
local departuresInFlight=0
local function leaving(p)
 closeConversation(p)
 local s=sessions[p]
 if not s then return end
 if s.testBeam then testBeamEnd(p,s,os.clock()) end
 if s.flight then TestFlight.Stop(p,s) end;disconnectSessionSignals(s)
 cancelSustained(p,s,os.clock());VoiceCombat.Cancel(s.voice)
 s.damageSummary=nil
 -- Release gameplay ownership before Save yields. Delayed gameplay callbacks
 -- must not mutate a departing profile or clear a replacement session later.
 sessions[p]=nil
 if s.canSave then
  departuresInFlight+=1
  local completed,ok,reason=pcall(Profiles.Save,p.UserId,s.testBaseline or s.data,true,shutdownSaveDeadline)
  departuresInFlight-=1
  if not completed or not ok then warn("ScreamSimulator departure save failed",p.UserId,completed and reason or ok) end
 end
end
Players.PlayerRemoving:Connect(leaving)
-- Bosses are separate from residents/trainers: no crowd quests, NPC hit coins or KO credit.
if Config.CompactCity then
 local knockback=require(script.Parent.BossKnockback)
 bosses=require(script.Parent.BossService).new(workspace.ScreamSimulatorWorld,{
  player=function(id) return Players:GetPlayerByUserId(id) end,
  context=function(p,now)
   local s=sessions[p];local _,r,h=parts(p)
   if not canDamageBots(s) or not r or h.PlatformStand or Config.InArena(r.Position)
    or now<s.protectedUntil or now<(s.knockedUntil or 0) then return nil end
   return {position=r.Position,level=s.data.level,identity=s.rewardIdentity}
  end,
  reward=function(p,spec,share)
   local coinCredit=coins(p,math.floor(spec.coins*share))
   local xpCredit=xp(p,math.floor(spec.xp*share))
   local reward=if xpCredit==0 and coinCredit==0 then "no XP or coins credited" else "+"..xpCredit.." XP · +"..coinCredit.." coins"
   state(p,spec.name.." defeated · "..reward)
  end,
  damage=function(p,amount,now,boss,strike)
   local s=sessions[p];local c,r,h=parts(p)
   if not s or not r or not h or now<s.dodgingUntil or now<s.protectedUntil then return end
   if not audible(c,boss.root.Position,r.Position,boss.model) then return end
   s.nextHeal=now+Config.HealQuietSeconds
   if h.Health<=amount then eject(p,h);return end
   h.Health-=amount
   if strike.push and not r.Anchored and not h.Sit and not h.SeatPart and h.FloorMaterial~=Enum.Material.Air then
    local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Exclude;params.FilterDescendantsInstances={c};params.RespectCanCollide=true
    local target=knockback.Target(workspace,r.CFrame,boss,strike,params,h,function(pos)
     return pos.X>=Config.MapMin.X+2 and pos.X<=Config.MapMax.X-2 and pos.Z>=Config.MapMin.Z+2 and pos.Z<=Config.MapMax.Z-2
      and not Config.InArena(pos)
    end)
    if target then
     r.CFrame=CFrame.new(target)*r.CFrame.Rotation
     r.AssemblyLinearVelocity=Vector3.zero
    end
   end
   state(p)
  end,
 })
end
local function stepTraining(now)
 for _,bot in ipairs(World.Bots) do
  if not bot.training or not bot.alive then continue end
  if now-(bot.lastTrainingHit or now)>TrainingRules.ResetAfter and bot.health<bot.maxHealth then restoreBot(bot) end
  -- Hits during a windup select the next target, not the strike already on the ground.
  local p=if bot.strike then bot.strike.target else bot.trainingTarget
  local s=p and sessions[p];local c,r,h
  if p then c,r,h=parts(p) end
  local valid=s and not s.flight and r and s.micReady and not Config.InArena(r.Position) and (r.Position-bot.start).Magnitude<=TrainingRules.Radius
   and now>=s.protectedUntil and now>=(s.knockedUntil or 0) and audible(bot.model,bot.root.Position,r.Position,c)
  if not valid then
   clearTrainingStrike(bot)
   if bot.trainingTarget==p then bot.trainingTarget=nil end
   continue
  end
  if bot.strike then
   if now>=bot.strike.at then
    local strike=clearTrainingStrike(bot)
    if TrainingRules.Hits(strike.position,r.Position,now<s.protectedUntil,now<s.dodgingUntil) then
     s.nextHeal=now+Config.HealQuietSeconds
     if h.Health<=bot.training.damage then eject(p,h) else h.Health-=bot.training.damage;state(p) end
    end
   else
    local remaining=math.clamp((bot.strike.at-now)/TrainingRules.Windup,0,1)
    bot.strike.warning.Transparency=.24+.41*remaining
   end
  elseif now>=(bot.nextStrike or 0) then
   bot.nextStrike=now+TrainingRules.AttackInterval
   -- Replicated, bounded warning disc; never collides or blocks the player's beam.
   local disc=Instance.new("Part");disc.Name="TrainingStrikeWarning";disc.Anchored=true
   disc.CanCollide=false;disc.CanTouch=false;disc.CanQuery=false;disc.Shape=Enum.PartType.Cylinder
   local center=Vector3.new(r.Position.X,bot.trainingSurfaceY,r.Position.Z)
   local diameter=TrainingRules.StrikeRadius*2
   disc.Size=Vector3.new(.1,diameter,diameter);disc.CFrame=CFrame.new(center.X,center.Y+.07,center.Z)*CFrame.Angles(0,0,math.pi/2)
   disc.Color=Color3.fromRGB(255,90,70);disc.Material=Enum.Material.Neon;disc.Transparency=.65;disc.CastShadow=false;disc.Parent=workspace
   local cueUntil=workspace:GetServerTimeNow()+TrainingRules.Windup
   bot.strike={at=now+TrainingRules.Windup,position=center,warning=disc,target=p,character=c,cueUntil=cueUntil}
   c:SetAttribute("TrainingStrikeCenter",bot.strike.position)
   c:SetAttribute("TrainingStrikeAt",cueUntil)
   game:GetService("Debris"):AddItem(disc,TrainingRules.Windup+.5)
  end
 end
end
local function stepSprint(s,root,humanoid,now,dt)
 -- Charge the interval for which the server granted sprint speed. A release
 -- received just before this tick must not turn that interval into regeneration.
 if s.sprintRunning then
  s.sprintCharge=math.max(0,s.sprintCharge-dt)
  s.sprintRegenAt=now+Config.SprintRegenDelay
  if s.sprintCharge<=1e-6 then s.sprintCharge=0;s.sprintLockedUntil=now+Config.SprintRecovery end
 end
 if s.sprintLockedUntil>0 and now>=s.sprintLockedUntil then
  s.sprintLockedUntil=0;s.sprintCharge=Config.SprintDuration
 elseif not s.sprintRunning and now>=s.sprintLockedUntil then
  local recoveryDt=math.clamp(now-(s.sprintRegenAt or 0),0,dt)
  s.sprintCharge=math.min(Config.SprintDuration,s.sprintCharge+recoveryDt*2)
 end
 local velocity=root and root.AssemblyLinearVelocity
 local moving=velocity and velocity.X*velocity.X+velocity.Z*velocity.Z>2.25
 local running=root~=nil and not root.Anchored and humanoid~=nil and not humanoid.Sit and not humanoid.SeatPart and not humanoid.PlatformStand and s.sprintRequested and moving==true
  and now>=s.dodgingUntil and now>=(s.knockedUntil or 0) and s.sprintCharge>0 and now>=s.sprintLockedUntil
 s.sprintRunning=running==true
 return running
end
task.spawn(function()
 local tick=0
 while true do task.wait(0.1);tick+=1;local now=os.clock()
  dispatchVoiceEligibility(now)
  stepTraining(now)
  if bosses then bosses:Step(now) end
  local toolsAvailable=TestBeamRules.LocalFixture(localFixture) or onlinePreviewTools()
  if remotes:GetAttribute("TestToolsAvailable")~=toolsAvailable then remotes:SetAttribute("TestToolsAvailable",toolsAvailable) end
  for p,s in pairs(sessions) do
   s.testBeamAvailable=toolsAvailable and toolAuthorized(p)
   if s.flight then
    -- Pause timed quest counters while traversal/interactions are disabled.
    local pause=math.clamp(now-(s.lastStep or now),0,1)
    if s.questDeadline then s.questDeadline+=pause end
    if s.raceStart then s.raceStart+=pause end
    TestFlight.Step(p,s,toolAuthorized(p),flightBounds,now,.1)
   end
   if s.testBeam then
    local preview,ended,hits,details=testBeam.Step(p,s,Access.IsAuthorized(p,game.CreatorType,game.CreatorId,RunService:IsStudio(),game.GameId),localFixture,now,function(ctx,direction,stats,at)
     return resolveTestBeam(p,s,ctx,direction,stats,at)
    end)
    applyTestBeam(p,s,now,hits,details)
    if ended then testBeamEnd(p,s,now,true);state(p) end
    if preview then
     local length=details and details.length
     if not length then
      local obstruction=beamObstruction(s.testBeam.character,preview.origin,preview.direction,preview.length,Players:GetPlayers())
      length=obstruction and obstruction.Distance or preview.length
     end
     for _,viewer in ipairs(Players:GetPlayers()) do
      local _,root=parts(viewer)
      if root and (root.Position-preview.origin).Magnitude<=180 then
       effect:FireClient(viewer,"TestBeam",preview.origin,p.UserId,beamColor(p,s),preview.direction,length,preview.width,nil,preview.level)
      end
     end
    end
   end
   stepVoiceEligibility(p,s,now)
   local dt=math.max(0,now-s.lastStep);s.lastStep=now;local _,r,h=parts(p)
   -- Crossing into PvP immediately restores the full dodge cooldown.
   if r and Config.InArena(r.Position) and s.lastDodge then
    if s.premiumRoll then s.premiumRoll=false;s.dodgingUntil=0;p:SetAttribute("DodgeEnds",0) end
    s.nextDodge=math.max(s.nextDodge,s.lastDodge+Config.DodgeCooldown);p:SetAttribute("DodgeReady",workspace:GetServerTimeNow()+math.max(0,s.nextDodge-now)) end
   if s.sustained and s.sustained.protocol.active then stepSustained(p,s,os.clock()) end
   if s.damageSummary then
    if h and not s.flight then stepDamageSummary(p,s,os.clock()) else clearDamageSummary(p,s) end
   end
   if s.voice.capture and now-s.voice.capture.started>VoiceCombat.CaptureExpiry then VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0) end
   local running=stepSprint(s,r,h,now,dt)
   if h then
    if h.FloorMaterial~=Enum.Material.Air then s.jumpOriginY=r.Position.Y end
    h.WalkSpeed=now<(s.knockedUntil or 0) and 0 or now<s.dodgingUntil and 0 or running and 25 or 16
    h.JumpPower=s.jumpPower or 50;h.JumpHeight=s.jumpHeight or 7.2
    local healed,nextHeal=Healing.Step(h.Health,h.MaxHealth,s.nextHeal,now)
    if healed~=h.Health then h.Health=healed end;s.nextHeal=nextHeal
    if Config.CompactCity and (r.Position.X<Config.MapMin.X-10 or r.Position.X>Config.MapMax.X+10 or r.Position.Z<Config.MapMin.Z-10 or r.Position.Z>Config.MapMax.Z+10 or r.Position.Y< -15) then
     resetMovement(p,s,h,r);running=false
     p.Character:PivotTo(World.SafeSpawn);protect(p,s)
     r.AssemblyLinearVelocity=Vector3.zero;r.AssemblyAngularVelocity=Vector3.zero
     state(p,"Returned to the safe courtyard")
    elseif not Config.CompactCity and r.Position.Z>600 and (r.Position.Z>780 or math.abs(r.Position.X)>700) then
     resetMovement(p,s,h,r);running=false
     p.Character:PivotTo(CFrame.new(math.clamp(r.Position.X,-670,670),5,594));protect(p,s)
     state(p,"Lifeguard rescue · stay inside the gold buoys.")
    elseif r.Position.Y< -20 then
     local rescue,notice
     if World.FallRescue then rescue,notice=World.FallRescue(r.Position) end
     resetMovement(p,s,h,r);running=false;p.Character:PivotTo(rescue or World.SafeSpawn);protect(p,s)
     state(p,notice or "Rescued · back at the safe hub")
    end
   end
   if s.questDeadline and now>s.questDeadline then stopQuest(p);state(p,"Time's up · accept the task again to restart.") end
   p:SetAttribute("SprintCharge",s.sprintCharge);p:SetAttribute("SprintCooldown",math.max(0,s.sprintLockedUntil-now));p:SetAttribute("Sprinting",running==true)
   if tick%5==0 then state(p) end
  end
 end
end)
local function autosave(p,s)
 local completed,ok,reason=pcall(Profiles.Save,p.UserId,s.testBaseline or s.data)
 if not completed then ok=false;reason="exception" end
 -- A leave/rejoin can finish while UpdateAsync is yielding.
 if sessions[p]~=s or not p.Parent then return end
 if ok then s.saveDelayed=false
 elseif reason=="ownership" or reason=="unavailable" then
  s.canSave=false;s.saveDelayed=false;state(p,"Saving is unavailable. Progress from here is temporary; rejoin before continuing progression.",nil,true,"save")
 else
  local first=not s.saveDelayed;s.saveDelayed=true
  if first then state(p,"Save delayed. Your progress is still in this server; saving will retry automatically.",nil,true,"save") end
 end
end
local function stepAutosaves(now)
 if closing then return end
 local player,session
 for p,s in pairs(sessions) do
  if s.canSave and p.Parent and not s.autosaveInFlight and now>=s.nextAutosaveAt
   and (not session or s.nextAutosaveAt<session.nextAutosaveAt) then
   player,session=p,s
  end
 end
 if not session then return end
 -- Pace starts, including after a slow frame, without stacking a player's saves.
 session.nextAutosaveAt=now+60
 session.autosaveInFlight=true
 task.defer(function()
  if not closing and sessions[player]==session and player.Parent and session.canSave then
   autosave(player,session)
  end
  session.autosaveInFlight=false
 end)
end
task.spawn(function()
 while not closing do
  task.wait(.25)
  stepAutosaves(os.clock())
 end
end)
local function shutdown()
 local deadline=os.clock()+25
 shutdownSaveDeadline=deadline
 closing=true
 local pending=0
 local finalSaves={}
 -- Freeze gameplay before any final save can yield or release its lease.
 -- In-flight joins see closing and release their acquired profile instead.
 for p,s in pairs(sessions) do
  if s.testBeam then testBeamEnd(p,s,os.clock()) end
  if s.flight then TestFlight.Stop(p,s) end;disconnectSessionSignals(s)
  closeConversation(p);cancelSustained(p,s,os.clock());VoiceCombat.Cancel(s.voice)
  sessions[p]=nil
  if s.canSave then table.insert(finalSaves,{player=p,session=s}) end
 end
 for _,entry in ipairs(finalSaves) do
  local p,s=entry.player,entry.session
  if s.canSave then
   pending+=1
   task.spawn(function()
    local completed,ok,reason=pcall(Profiles.Save,p.UserId,s.testBaseline or s.data,true,deadline)
    pending-=1
    if not completed or not ok then warn("ScreamSimulator shutdown save failed",completed and reason or ok) end
   end)
  end
 end
 while pending>0 or departuresInFlight>0 or joinsInFlight>0 do
  local remaining=deadline-os.clock()
  if remaining<=0 then break end
  task.wait(math.min(.1,remaining))
 end
end
game:BindToClose(shutdown)
