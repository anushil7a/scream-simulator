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
local Entitlements=require(script.Parent.Entitlements)
local Commerce=require(script.Parent.Commerce)
local ShopCatalog=require(ReplicatedStorage.Shared.ShopCatalog)
local Soccer=require(script.Parent.SoccerChallenge)
local BeachVolley=require(script.Parent.BeachVolley)
local QuestLifecycle=require(ReplicatedStorage.Shared.QuestLifecycle)
local QuestGuide=require(ReplicatedStorage.Shared.QuestGuide)
local Equipment=require(script.Parent.Equipment)
-- Only disposable local fixtures bypass persistent profiles. Attack mode is independent.
local localFixture=RunService:IsStudio() and game.PlaceId==0 and workspace:GetAttribute("LocalSustainedPrototype")==true
local sustainedEnabled=Config.AutomaticVoice==true or localFixture
local sustained
if sustainedEnabled then
 sustained=require(script.Parent.SustainedAttackAdapter).new(require(ReplicatedStorage.Shared.SustainedAttack),
  VoiceCombat,require(script.Parent.SustainedAim))
end
World.Build()
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
remotes.Parent=ReplicatedStorage
local function remote(name) local r=Instance.new("RemoteEvent");r.Name=name;r.Parent=remotes;return r end
local action=remote("Action");local stateRemote=remote("State");local effect=remote("Effect")
local sessions={}
local closing=false
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
 Equipment.Sync(p,s.data.amplifierEquipped)
 stateRemote:FireClient(p,{coins=s.data.coins,level=s.data.level,xp=s.data.xp,xpNext=Config.XPToNext(s.data.level),sound=s.data.sound,aura=s.data.aura,
 shop=Commerce.Status(p),spectrumPass=Entitlements.HasSpectrum(p),customColor=s.data.customColor,useCustomColor=s.data.useCustomColor,
 combatChallenges=s.data.combatChallenges,training=TrainingRules.Recommended(s.data.level).name,milestone=s.milestone,
 amplifierOwned=s.data.amplifierOwned,amplifierEquipped=s.data.amplifierEquipped,movementPass=Entitlements.HasMovement(p),achievements=s.data.achievements,
 availableQuests=s.data.availableQuests,quests=s.data.quests,collected=s.collected,activeQuest=s.activeQuest,questStep=step,questTime=soccer and soccer.remaining or s.questDeadline and math.max(0,math.ceil(s.questDeadline-os.clock())) or 0,
 health=h and math.ceil(h.Health) or Config.HealthForLevel(s.data.level),maxHealth=Config.HealthForLevel(s.data.level),inWarZone=r and Config.InArena(r.Position) or false,
 voiceEligible=VoiceEligibility.Allowed(s.voiceEligibility,os.clock()),voiceStatus=VoiceEligibility.Status(s.voiceEligibility,os.clock()),
 castCooldown=math.max(0,(s.sustained and s.sustained.protocol.nextStart or s.voice.nextCast)-os.clock()),micReady=s.micReady,protection=math.max(0,s.protectedUntil-os.clock()),dodgeCooldown=math.max(0,s.nextDodge-os.clock()),
 conversation=conversation,settings=s.data.settings,devAccess=Access.IsAuthorized(p,game.CreatorType,game.CreatorId,RunService:IsStudio(),game.GameId),savingAvailable=s.canSave and not s.testBaseline,savingDelayed=s.saveDelayed==true,recoveryWarning=s.recoveryWarning==true,testSession=s.testBaseline~=nil,message=message,messageUrgent=messageUrgent==true,messageKey=messageKey=="save" and "save" or nil})
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
 return a~=nil and b~=nil and (a.testBaseline~=nil)==(b.testBaseline~=nil)
end
local function canDamageBots(s)
 -- Only the guarded local fixture makes every participant's profile temporary.
 return s~=nil and (s.testBaseline==nil or localFixture==true)
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
   local credited=xp(recipient,reward);coins(recipient,math.floor((victim and 20 or 5)*share*factor*repeatFactor))
   if victim and recipient==finisher and underdog then questProgress(recipient,"Underdog") end
   if victim and recipient~=finisher and underdog and meaningful[id] then questProgress(recipient,"ArenaAssist") end
   local bonus,bonusXP=0,0
   if tier and factor>=.5 and meaningful[id] then
    bonus,bonusXP=combatChallenge(recipient,"fighters",true)
   end
   state(recipient,(recipient==finisher and "KO" or "Assist").." · +"..(credited+bonusXP).." XP"..(bonus>0 and " · challenge completed & renewed" or "")..(factor<1 and " · weaker opponent" or ""))
  elseif recipient==finisher then state(recipient,"KO · no reward awarded") end
 end
end
local function stopQuest(p)
 local s=sessions[p];if not s then return end
 Soccer.Cancel(p);QuestLifecycle.Clear(s,Config.GetQuest)
end
local function protect(p,s)
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
local function canCapture(p,s,now)
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
local function sustainedContext(p,s,now)
 if not canCapture(p,s,now) then return nil end
 local c,r=parts(p)
 local style=Config.GetSound(s.data.sound)
 if not style or style.level>s.data.level then return nil end
 return {player=p,character=c,origin=attackOrigin(c,r),position=r.Position,
  level=s.data.level,amplifier=s.data.amplifierEquipped}
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
 return ids,details,{origin=ctx.origin,direction=direction,length=length,width=stats.width,power=stats.power,obstruction=obstruction,dodged=dodged}
end
local function restoreBot(bot)
 if not bot.model.Parent then return end
 bot.recoveryVersion=(bot.recoveryVersion or 0)+1
 bot.health=bot.maxHealth or Config.BotMaxHealth;bot.alive=true;bot.credit={};bot.trainingTarget=nil;bot.strike=nil;World.UpdateBot(bot)
end
local function knockOutBot(bot)
 if not bot.alive then return end
 bot.trainingTarget=nil;bot.strike=nil;bot.alive=false;bot.recoveryVersion=(bot.recoveryVersion or 0)+1
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
   if not intent.evaded[target.UserId] then intent.evaded[target.UserId]=true;questProgress(target,"Evade") end
  end
  -- One successful impulse per activity per scream, not five impulses per second.
  if not intent.soccerHit then intent.soccerHit=Soccer.Hit(p,beam.origin,beam.direction,beam.length,beam.width,beam.power)==true end
  if not intent.volleyHit then intent.volleyHit=BeachVolley.Hit(p,beam.origin,beam.direction,beam.length,beam.width,beam.power)==true end
  for _,viewer in ipairs(Players:GetPlayers()) do
   local _,root=parts(viewer)
   if root and (root.Position-beam.origin).Magnitude<=180 then
    effect:FireClient(viewer,"SustainedBeam",beam.origin,p.UserId,beamColor(p,s),beam.direction,beam.length,beam.width,intent.audioStyleId,intent.level)
   end
  end
 end
 local dealt=0
 for _,hit in ipairs(hits) do
  local target=details[hit.id]
  if target.player then
   local ts,h=target.session,target.humanoid
   local actual=math.min(hit.damage,h.Health);dealt+=actual
   ts.credit=ts.credit or {};recordCredit(ts.credit,p,actual,h.MaxHealth,now)
   ts.nextHeal=now+Config.HealQuietSeconds
   if h.Health<=hit.damage then
    awardCombatKO(ts.credit,p,ts.data.level,h.MaxHealth,Config.PlayerKOXP(ts.data.level),now,target.player)
    eject(target.player,h)
   else h.Health-=hit.damage end
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
 end
 if dealt>0 then
  s.nextHeal=now+Config.HealQuietSeconds
  intent.damageTotal=(intent.damageTotal or 0)+dealt
  effect:FireClient(p,"SustainedHit",nil,p:GetAttribute("SustainedSequence"),math.floor(intent.damageTotal+.5))
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
 local sound=VoiceCombat.Stats(s.data.level,request.power,s.data.amplifierEquipped==true)
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
 local hits=0;local paid=0;local playerHits=0;local evades=0;local knockoutMessage
 for _,bot in ipairs(World.Bots) do
  if canDamageBots(s) and bot.alive and bot.root.Parent and (not bot.training or (r.Position-bot.start).Magnitude<=TrainingRules.Radius) and Rules.InBeam(origin,direction,bot.root.Position,length,sound.width,1) and audible(c,origin,bot.root.Position,bot.model) then
   hits+=1
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
 if hits>=3 then questProgress(p,"Crowd") end
 if Config.InArena(r.Position) then
  for _,target in ipairs(Players:GetPlayers()) do
   local ts=sessions[target];local tc,tr,th=parts(target)
   if target~=p and sameCombatMode(s,ts) and tr and Rules.CanTarget(r.Position,tr.Position,ts.protectedUntil,now,sound.range+2) and Rules.InBeam(origin,direction,tr.Position,length,sound.width,1) and audible(c,origin,tr.Position,tc) then
    if now<ts.dodgingUntil and not ts.premiumRoll then evades+=1;questProgress(target,"Evade")
    else
     playerHits+=1
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
local function dodge(p)
 local s=sessions[p];local c,r,h=parts(p);local now=os.clock()
 if s then cancelSustained(p,s,now);VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0) end
 if not s or not r or r.Anchored or h.Sit or h.SeatPart or h.PlatformStand or now<s.nextDodge or now<(s.knockedUntil or 0) or h.FloorMaterial==Enum.Material.Air then return end
 local cooldown=Entitlements.CanUseMovement(p,r.Position) and Config.DodgeDuration or Config.DodgeCooldown
 s.nextDodge=now+cooldown;s.dodgingUntil=now+Config.DodgeDuration
 s.lastDodge=now;s.premiumRoll=cooldown<Config.DodgeCooldown
 p:SetAttribute("DodgeEnds",workspace:GetServerTimeNow()+Config.DodgeDuration)
 p:SetAttribute("DodgeReady",workspace:GetServerTimeNow()+cooldown)
 local direction=h.MoveDirection;if direction.Magnitude<0.1 then direction=r.CFrame.LookVector end
 direction=Vector3.new(direction.X,0,direction.Z).Unit
 local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Exclude;params.FilterDescendantsInstances={c}
 local hit=workspace:Blockcast(r.CFrame,Vector3.new(2,3,2),direction*Config.DodgeDistance,params)
 local distance=hit and math.max(0,hit.Distance-1) or Config.DodgeDistance
 local start=r.CFrame;r:SetNetworkOwner(nil);h.AutoRotate=false
 r.CFrame=CFrame.lookAt(r.Position,r.Position+direction)
 p:SetAttribute("DodgeStarted",workspace:GetServerTimeNow());p:SetAttribute("DodgeDirection",direction)
 effect:FireAllClients("Dodge",r.Position,beamColor(p,s))
 task.spawn(function()
  local previousDistance=0
  while sessions[p]==s and s.lastDodge==now and c.Parent and p.Character==c and h.Health>0 and s.dodgingUntil>os.clock() and os.clock()-now<Config.DodgeDuration do
   local t=math.clamp((os.clock()-now)/Config.DodgeDuration,0,1)
   local desired=distance*(t*t*(3-2*t));local step=desired-previousDistance
   local blocked=step>0 and workspace:Blockcast(r.CFrame,Vector3.new(2,2.5,2),direction*step,params)
   if blocked then break end
   r.CFrame=CFrame.lookAt(r.Position+direction*step,r.Position+direction*(step+1));previousDistance=desired
   r.AssemblyLinearVelocity=Vector3.zero;RunService.Heartbeat:Wait()
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
local function microSpeaker(p,s,toggleOwned)
 if s.data.amplifierOwned then
  if toggleOwned then s.data.amplifierEquipped=not s.data.amplifierEquipped
  else state(p,"You already own a micro-speaker. Equip it from Style.");return end
 else
  if s.data.coins<Config.MicroSpeakerPrice then state(p,"Micro-speaker costs "..Config.MicroSpeakerPrice.." coins. You need "..(Config.MicroSpeakerPrice-s.data.coins).." more.",nil,true);return end
  s.data.coins-=Config.MicroSpeakerPrice;s.data.amplifierOwned=true;s.data.amplifierEquipped=true
 end
 state(p,s.data.amplifierEquipped and "Micro-speaker equipped · +12% normalized power, capped at 100%" or "Micro-speaker unequipped")
end
local function vendorPurchase(p,s,arg)
 local bot=s.conversationBot;local _,root=parts(p)
 if type(arg)~="table" or arg.product~="MicroSpeaker" or not bot or arg.npc~=bot.id or bot.role~="Vendor" or not bot.alive or not bot.root.Parent or bot.talkingTo~=p or (bot.socialUntil or 0)<=os.clock() or not root or not InteractionRules.CanReachNpc(p.Character,bot.model,14) then
  state(p,"Speak with the market vendor nearby before buying.",nil,true);return
 end
 -- No yielding between ownership check and debit: duplicate requests never charge twice.
 microSpeaker(p,s,false)
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
  local hints={Gardener="The raised flowerbeds in Rambla Gardens need water. Use the interaction prompt beside each bed after accepting my task.",Vendor="The café sends orders along the waterfront. Collect one, then check your objective for its destination.",Soccer="I call it an assist when I miss. Your microphone can steer a training ball; softer shots give you more control.",BeachWorker="Please keep the sand clear. You can follow the promenade to the pier and the hidden courts beyond it.",Busker="Come for the music, stay for the beach. The central arena is the only place where players can damage each other."}
  state(p,message,{npc=b.model,name=b.name,line=message,hint=hints[b.role] or "Explore the courtyards, shops and waterfront. Some residents offer tasks; player combat stays inside the central arena.",quests=choices,products=b.role=="Vendor" and {{id="MicroSpeaker",name="Micro-speaker",price=Config.MicroSpeakerPrice,owned=s.data.amplifierOwned,description="Handheld amplifier · +12% normalized power, capped at 100%. Buy once with earned coins."}} or nil});return
 end end
end
local function dev(p,command)
 if Commerce.Busy(p) then state(p,"Wait for your purchase to finish saving.");return end
 local s=sessions[p];if not s or not Access.IsAuthorized(p,game.CreatorType,game.CreatorId,RunService:IsStudio(),game.GameId) then return end
 local valid={Coins=true,XP=true,AddLevels=true,MaxLevel=true,LevelOne=true,Heal=true,Hub=true,Arena=true,Beach=true,ResetQuests=true,ResetBots=true,StudioMovement=true}
 if type(command)~="string" or not valid[command] then return end
 if command=="StudioMovement" and not game:GetService("RunService"):IsStudio() then return end
 if command=="ResetBots" and not localFixture then state(p,"Reset bots requires the isolated local Studio fixture; shared fights are unchanged.");return end
 -- Freeze legitimate progress before any test mutation. Keep renewing/releasing its lease.
 if not s.testBaseline then
  cancelSustained(p,s,os.clock());VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0);s.credit={}
  s.testBaseline=Profiles.Sanitize(s.data);s.data=Profiles.Sanitize(s.data)
 end
 local c,_,h=parts(p)
 local positions={Hub=World.SafeSpawn,Arena=Config.CompactCity and CFrame.new(Config.CityLayout.Teleports.Arena) or CFrame.new(0,6,0),Beach=Config.CompactCity and CFrame.new(Config.CityLayout.Teleports.Beach) or CFrame.new(0,4,403)}
 if command=="Coins" then s.data.coins+=1000
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
 syncHealth(p,command=="Heal");state(p,command=="StudioMovement" and ("Studio movement test "..(Entitlements.HasStudioMovement(p) and "ON" or "OFF").." · safe areas only · not saved") or "Test applied · progress is temporary. PvP is test-to-test only; NPC damage/reset requires the isolated local Studio fixture.")
end
World.OnVehicleSweep=function(car,previous,nextFrame)
 for player,s in pairs(sessions) do
  local character,root,humanoid=parts(player);local now=os.clock()
  if root and now>=s.protectedUntil and now>=(s.nextCarHit or 0) and Rules.VehicleSweep(previous*CFrame.new(0,.55,0),nextFrame*CFrame.new(0,.55,0),root.Position,Vector3.new(8,4,4.5)) then
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
  if not s or not r or not marker or not marker:IsA("BasePart") or (r.Position-marker.Position).Magnitude>12 then return end
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
 s.requestWindow=s.requestWindow or now;s.requestCount=s.requestCount or 0
 if now-s.requestWindow>=1 then s.requestWindow=now;s.requestCount=0 end
 s.requestCount+=1;if s.requestCount>30 then return end
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
 elseif verb=="Cast" then cast(p,arg);return elseif verb=="Dodge" then dodge(p);return
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
 elseif verb=="MicroSpeaker" then microSpeaker(p,s,true)
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
local function joined(p)
 if closing then return end
 task.spawn(Entitlements.Refresh,p)
 local data,save,loadMessage,recoveryWarning
 if localFixture then data,save,loadMessage=Profiles.Default(),false,"Local sustained prototype · saving disabled"
 else data,save,loadMessage,recoveryWarning=Profiles.Load(p.UserId) end
 if closing or not p.Parent then
  if save then
   local completed,ok,reason=pcall(Profiles.Save,p.UserId,data,true)
   if not completed or not ok then
    warn("ScreamSimulator late profile release failed",p.UserId,completed and reason or ok)
   end
  end
  return
 end
 local s={data=data,canSave=save,recoveryWarning=recoveryWarning,rewardIdentity={},voice=VoiceCombat.New(),voiceEligibility=VoiceEligibility.New(localFixture,os.clock(),p.UserId),micReady=false,protectedUntil=0,nextCast=0,nextDodge=0,dodgingUntil=0,nextAction=0,nextHeal=os.clock()+Config.HealQuietSeconds,
 botRewards={},credit={},collected={},sprintRequested=false,sprintRunning=false,sprintRegenAt=0,sprintCharge=Config.SprintDuration,sprintLockedUntil=0,lastStep=os.clock()};sessions[p]=s
 task.spawn(Commerce.Load,p)
 if sustainedEnabled then
  s.sustained=sustained.New()
  p:SetAttribute("SustainedActive",false);p:SetAttribute("SustainedReadyAt",0);p:SetAttribute("SustainedEndsAt",0)
 end
 local function spawn(c)
  local h=c:WaitForChild("Humanoid",10)
  if not h or not p.Parent or sessions[p]~=s or p.Character~=c or s.character==c then return end
  s.character=c;closeConversation(p)
  s.jumpPower=h.JumpPower;s.jumpHeight=h.JumpHeight
  h.MaxHealth=Config.HealthForLevel(s.data.level);h.Health=h.MaxHealth;h.WalkSpeed=16
  s.sprintCharge=Config.SprintDuration;s.sprintRequested=false;s.sprintRunning=false;s.sprintRegenAt=0;s.lastStep=os.clock();s.sprintLockedUntil=0;s.dodgingUntil=0;s.knockedUntil=0;s.premiumRoll=false
  s.nextHeal=os.clock()+Config.HealQuietSeconds
  p:SetAttribute("DodgeEnds",0);p:SetAttribute("DodgeStarted",0);p:SetAttribute("KnockdownEnds",0)
  p:SetAttribute("Sprinting",false);p:SetAttribute("SprintCooldown",0);p:SetAttribute("SprintCharge",Config.SprintDuration)
  protect(p,s);state(p)
 end
 s.characterRemovingConnection=p.CharacterRemoving:Connect(function(c)
  if sessions[p]~=s or s.character~=c then return end
  closeConversation(p);cancelSustained(p,s,os.clock());VoiceCombat.Cancel(s.voice)
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
 disconnectSessionSignals(s)
 cancelSustained(p,s,os.clock());VoiceCombat.Cancel(s.voice)
 -- Release gameplay ownership before Save yields. Delayed gameplay callbacks
 -- must not mutate a departing profile or clear a replacement session later.
 sessions[p]=nil
 if s.canSave then
  departuresInFlight+=1
  local completed,ok,reason=pcall(Profiles.Save,p.UserId,s.testBaseline or s.data,true)
  departuresInFlight-=1
  if not completed or not ok then warn("ScreamSimulator departure save failed",p.UserId,completed and reason or ok) end
 end
end
Players.PlayerRemoving:Connect(leaving)
local function stepTraining(now)
 for _,bot in ipairs(World.Bots) do
  if not bot.training or not bot.alive then continue end
  if now-(bot.lastTrainingHit or now)>TrainingRules.ResetAfter and bot.health<bot.maxHealth then restoreBot(bot) end
  local p=bot.trainingTarget;local s=p and sessions[p];local c,r,h
  if p then c,r,h=parts(p) end
  local valid=s and r and s.micReady and not Config.InArena(r.Position) and (r.Position-bot.start).Magnitude<=TrainingRules.Radius
   and now>=s.protectedUntil and now>=(s.knockedUntil or 0) and audible(bot.model,bot.root.Position,r.Position,c)
  if not valid then bot.strike=nil;bot.trainingTarget=nil;continue end
  if bot.strike then
   if now>=bot.strike.at then
    local strike=bot.strike;bot.strike=nil
    local delta=r.Position-strike.position
    if TrainingRules.Hits(Vector3.new(delta.X,0,delta.Z).Magnitude,now<s.protectedUntil,now<s.dodgingUntil) then
     s.nextHeal=now+Config.HealQuietSeconds
     if h.Health<=bot.training.damage then eject(p,h) else h.Health-=bot.training.damage;state(p) end
    end
   end
  elseif now>=(bot.nextStrike or 0) then
   bot.nextStrike=now+TrainingRules.AttackInterval
   bot.strike={at=now+TrainingRules.Windup,position=r.Position}
   -- Replicated, bounded warning disc; never collides or blocks the player's beam.
   local disc=Instance.new("Part");disc.Name="TrainingStrikeWarning";disc.Anchored=true
   disc.CanCollide=false;disc.CanTouch=false;disc.CanQuery=false;disc.Shape=Enum.PartType.Cylinder
   disc.Size=Vector3.new(.1,8,8);disc.CFrame=CFrame.new(r.Position.X,1.4,r.Position.Z)*CFrame.Angles(0,0,math.pi/2)
   disc.Color=Color3.fromRGB(255,90,70);disc.Material=Enum.Material.Neon;disc.Transparency=.45;disc.Parent=workspace
   game:GetService("Debris"):AddItem(disc,TrainingRules.Windup)
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
  for p,s in pairs(sessions) do
   stepVoiceEligibility(p,s,now)
   local dt=math.max(0,now-s.lastStep);s.lastStep=now;local _,r,h=parts(p)
   -- Crossing into PvP immediately restores the full dodge cooldown.
   if r and Config.InArena(r.Position) and s.lastDodge then
    if s.premiumRoll then s.premiumRoll=false;s.dodgingUntil=0;p:SetAttribute("DodgeEnds",0) end
    s.nextDodge=math.max(s.nextDodge,s.lastDodge+Config.DodgeCooldown);p:SetAttribute("DodgeReady",workspace:GetServerTimeNow()+math.max(0,s.nextDodge-now)) end
   if s.sustained and s.sustained.protocol.active then stepSustained(p,s,os.clock()) end
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
     resetMovement(p,s,h,r);running=false;p.Character:PivotTo(World.SafeSpawn);protect(p,s)
     state(p,"Rescued · back at the safe hub")
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
task.spawn(function() while true do task.wait(60);for p,s in pairs(sessions) do if s.canSave then task.spawn(autosave,p,s) end end end end)
local function shutdown()
 closing=true
 local pending=0
 local deadline=os.clock()+25
 local finalSaves={}
 -- Freeze gameplay before any final save can yield or release its lease.
 -- In-flight joins see closing and release their acquired profile instead.
 for p,s in pairs(sessions) do
  disconnectSessionSignals(s)
  closeConversation(p);cancelSustained(p,s,os.clock());VoiceCombat.Cancel(s.voice)
  sessions[p]=nil
  if s.canSave then table.insert(finalSaves,{player=p,session=s}) end
 end
 for _,entry in ipairs(finalSaves) do
  local p,s=entry.player,entry.session
  if s.canSave then
   pending+=1
   task.spawn(function()
    local completed,ok,reason=pcall(Profiles.Save,p.UserId,s.testBaseline or s.data,true)
    pending-=1
    if not completed or not ok then warn("ScreamSimulator shutdown save failed",completed and reason or ok) end
   end)
  end
 end
 while (pending>0 or departuresInFlight>0 or joinsInFlight>0) and os.clock()<deadline do task.wait(.1) end
end
game:BindToClose(shutdown)
