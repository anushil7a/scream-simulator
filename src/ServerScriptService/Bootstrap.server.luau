local Players=game:GetService("Players")
local ReplicatedStorage=game:GetService("ReplicatedStorage")
local RunService=game:GetService("RunService")
local Config=require(ReplicatedStorage.Shared.Config)
local World=require(script.Parent.World)
local Profiles=require(script.Parent.Profiles)
local Access=require(script.Parent.DeveloperAccess)
local Rules=require(script.Parent.CombatRules)
local VoiceCombat=require(ReplicatedStorage.Shared.VoiceCombat)
local Entitlements=require(script.Parent.Entitlements)
local Soccer=require(script.Parent.SoccerChallenge)
local QuestLifecycle=require(ReplicatedStorage.Shared.QuestLifecycle)
local Equipment=require(script.Parent.Equipment)
World.Build()
local Destruction=require(script.Parent.Destruction)
Destruction.Start(workspace.ScreamSimulatorWorld)
local old=ReplicatedStorage:FindFirstChild("ScreamRemotes");if old then old:Destroy() end
local remotes=Instance.new("Folder");remotes.Name="ScreamRemotes";remotes.Parent=ReplicatedStorage
local function remote(name) local r=Instance.new("RemoteEvent");r.Name=name;r.Parent=remotes;return r end
local action=remote("Action");local stateRemote=remote("State");local effect=remote("Effect")
local sessions={}
local function parts(p)
 local c=p.Character;local r=c and c:FindFirstChild("HumanoidRootPart");local h=c and c:FindFirstChildOfClass("Humanoid")
 if r and h and h.Health>0 then return c,r,h end
end
local function state(p,message,conversation)
 local s=sessions[p];if not s or not p.Parent then return end
 local _,r,h=parts(p)
 local soccer=Soccer.Status(p)
 Equipment.Sync(p,s.data.amplifierEquipped)
 stateRemote:FireClient(p,{coins=s.data.coins,level=s.data.level,xp=s.data.xp,xpNext=Config.XPToNext(s.data.level),sound=s.data.sound,aura=s.data.aura,
 amplifierOwned=s.data.amplifierOwned,amplifierEquipped=s.data.amplifierEquipped,movementPass=Entitlements.HasMovement(p),achievements=s.data.achievements,
 availableQuests=s.data.availableQuests,quests=s.data.quests,collected=s.collected,activeQuest=s.activeQuest,questStep=soccer and soccer.detail,questTime=soccer and soccer.remaining or s.questDeadline and math.max(0,math.ceil(s.questDeadline-os.clock())) or 0,
 health=h and math.ceil(h.Health) or Config.HealthForLevel(s.data.level),maxHealth=Config.HealthForLevel(s.data.level),inWarZone=r and Config.InArena(r.Position) or false,
 castCooldown=math.max(0,s.voice.nextCast-os.clock()),micReady=s.micReady,protection=math.max(0,s.protectedUntil-os.clock()),dodgeCooldown=math.max(0,s.nextDodge-os.clock()),
 conversation=conversation,settings=s.data.settings,devAccess=Access.IsAuthorized(p,game.CreatorType,game.CreatorId),savingAvailable=s.canSave and not s.testBaseline,testSession=s.testBaseline~=nil,message=message})
end
local function syncHealth(p,full)
 local s=sessions[p];local _,_,h=parts(p);if not s or not h then return end
 local maximum=Config.HealthForLevel(s.data.level);local gain=maximum-h.MaxHealth
 h.MaxHealth=maximum;h.Health=full and maximum or math.clamp(h.Health+gain,1,maximum)
end
local function xp(p,amount)
 local s=sessions[p];if not s then return end
 local d=s.data;if d.level>=Config.MaxLevel then return end
 d.xp+=math.max(0,math.floor(amount));local before=d.level
 while d.level<Config.MaxLevel and d.xp>=Config.XPToNext(d.level) do d.xp-=Config.XPToNext(d.level);d.level+=1 end
 if d.level==Config.MaxLevel then d.xp=0 end
 if d.level>before then
  syncHealth(p,false)
  local unlock="";for _,v in ipairs(Config.Sounds) do if v.level>before and v.level<=d.level then unlock=" · Unlocked "..v.name end end
  state(p,"Level "..d.level..unlock)
 end
end
local function questProgress(p,event,amount)
 local s=sessions[p];if not s or not s.activeQuest then return end
 local q=Config.GetQuest(s.activeQuest);if not q or q.event~=event then return end
 local v=s.data.quests[q.id];if not v or v.claimed or v.progress>=q.goal then return end
 v.progress=math.min(q.goal,v.progress+(amount or 1));state(p,v.progress==q.goal and "Quest complete! Claim your reward in Quests." or nil)
end
local function stopQuest(p)
 local s=sessions[p];if not s then return end
 Soccer.Cancel(p);QuestLifecycle.Clear(s,Config.GetQuest)
end
local function protect(p,s)
 VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0)
 s.protectedUntil=os.clock()+Config.SpawnProtection
 p:SetAttribute("ProtectionEnds",workspace:GetServerTimeNow()+Config.SpawnProtection)
 local c=p.Character;if c then local oldField=c:FindFirstChild("SpawnProtection");if oldField then oldField:Destroy() end
  local f=Instance.new("ForceField");f.Name="SpawnProtection";f.Parent=c
  task.delay(Config.SpawnProtection,function() if f.Parent then f:Destroy() end end)
 end
end
local function eject(p,h)
 local s=sessions[p];h.Health=Config.HealthForLevel(s.data.level);p.Character:PivotTo(World.SafeSpawn);s.dodgingUntil=0;protect(p,s)
 s.nextHeal=os.clock()+Config.HealQuietSeconds;state(p,"Knocked out · back at the safe hub")
end
local function audible(c,origin,target,targetModel)
 local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Exclude;params.FilterDescendantsInstances={c,targetModel};params.RespectCanCollide=true
 return workspace:Raycast(origin,target-origin,params)==nil
end
local function canCapture(p,s,now)
 local _,r=parts(p)
 return r~=nil and s.micReady and now>=s.protectedUntil and now>=s.dodgingUntil and now>=(s.knockedUntil or 0)
end
local function cast(p,request)
 local s=sessions[p];local c,r=parts(p);if not s or not r or type(request)~="table" then return end
 p:SetAttribute("CaptureStarted",0)
 local now=os.clock();local style=Config.GetSound(s.data.sound)
 local aim=request.aim
 if typeof(aim)~="Vector3" or not VoiceCombat.IsFinite(aim.X) or not VoiceCombat.IsFinite(aim.Y) or not VoiceCombat.IsFinite(aim.Z) then VoiceCombat.Cancel(s.voice);return end
 local origin=r.Position+Vector3.new(0,1,0)
 local head=c:FindFirstChild("Head");if head and (head.Position-r.Position).Magnitude<5 then origin=head.Position end
 local delta=aim-origin
 if delta.Magnitude<.01 or delta.Magnitude>2048 then VoiceCombat.Cancel(s.voice);return end
 if not VoiceCombat.Release(s.voice,now,request.sequence,request.power,style~=nil and style.level<=s.data.level and canCapture(p,s,now)) then return end
 local sound=VoiceCombat.Stats(s.data.level,request.power,s.data.amplifierEquipped==true)
 local direction=delta.Unit
 s.nextCast=s.voice.nextCast;p:SetAttribute("ScreamReleased",workspace:GetServerTimeNow());p:SetAttribute("CaptureStarted",0)
 local exclude={c};for _,bot in ipairs(World.Bots) do table.insert(exclude,bot.model) end
 for _,other in ipairs(Players:GetPlayers()) do if other.Character then table.insert(exclude,other.Character) end end
 local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Exclude;params.FilterDescendantsInstances=exclude;params.RespectCanCollide=true
 local obstruction=workspace:Raycast(origin,direction*sound.range,params)
 local length=obstruction and obstruction.Distance or sound.range
 effect:FireAllClients("Scream",origin,style.id,s.data.aura,direction,length,sound.width)
 Soccer.Hit(p,origin,direction,length,sound.width,sound.power)
 if obstruction then
  local result=Destruction.Damage(obstruction.Instance,s.data.level,sound.damage)
  if result then
   if result.reason=="level" then state(p,"Requires level "..result.required)
   elseif result.destroyed then effect:FireAllClients("Break",result.position,s.data.aura);questProgress(p,"Demolition") end
  end
 end
 local hits=0;local paid=0
 for _,bot in ipairs(World.Bots) do
  if bot.alive and bot.root.Parent and Rules.InBeam(origin,direction,bot.root.Position,length,sound.width,1) and audible(c,origin,bot.root.Position,bot.model) then
   hits+=1;bot.health=math.max(0,bot.health-sound.damage);local ko=bot.health==0
   if ko then bot.alive=false;task.delay(Config.BotRespawnSeconds,function() if bot.model.Parent then bot.health=Config.BotMaxHealth;bot.alive=true;World.UpdateBot(bot) end end)
   else World.ReactToScream(bot,r.Position) end
   World.UpdateBot(bot)
   if now>=(s.botRewards[bot.id] or 0) and paid<5 then
    s.botRewards[bot.id]=now+VoiceCombat.Cooldown;paid+=1;s.data.coins+=ko and 5 or 2;xp(p,ko and 16 or 5)
   end
  end
 end
 if hits>=3 then questProgress(p,"Crowd") end
 if Config.InArena(r.Position) then
  for _,target in ipairs(Players:GetPlayers()) do
   local ts=sessions[target];local tc,tr,th=parts(target)
   if target~=p and ts and tr and Rules.CanTarget(r.Position,tr.Position,ts.protectedUntil,now,sound.range+2) and Rules.InBeam(origin,direction,tr.Position,length,sound.width,1) and audible(c,origin,tr.Position,tc) then
    if now<ts.dodgingUntil and not ts.premiumRoll then questProgress(target,"Evade")
    else
     ts.nextHeal=now+Config.HealQuietSeconds
     if th.Health<=sound.damage then
      local targetLevel=ts.data.level;local attackerLevel=s.data.level;eject(target,th)
      -- A repeated victim has a reward cooldown, independent from hit rewards.
      if now>=(s.koRewards[target.UserId] or 0) then
       s.koRewards[target.UserId]=now+30;local reward=Config.PlayerKOXP(targetLevel);xp(p,reward);s.data.coins+=20
       if targetLevel>=attackerLevel then questProgress(p,"Underdog") end
       state(p,"Player knockout · +"..reward.." XP")
      end
     else th.Health-=sound.damage;state(target) end
    end
   end
  end
 end
 state(p)
end
local function dodge(p)
 local s=sessions[p];local c,r,h=parts(p);local now=os.clock()
 if s then VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0) end
 if not s or not r or not s.micReady or now<s.nextDodge or now<(s.knockedUntil or 0) or h.FloorMaterial==Enum.Material.Air then return end
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
 effect:FireAllClients("Dodge",r.Position,s.data.aura)
 task.spawn(function()
  local previousDistance=0
  while c.Parent and p.Character==c and h.Health>0 and s.dodgingUntil>os.clock() and os.clock()-now<Config.DodgeDuration do
   local t=math.clamp((os.clock()-now)/Config.DodgeDuration,0,1)
   local desired=distance*(t*t*(3-2*t));local step=desired-previousDistance
   local blocked=step>0 and workspace:Blockcast(r.CFrame,Vector3.new(2,2.5,2),direction*step,params)
   if blocked then break end
   r.CFrame=CFrame.lookAt(r.Position+direction*step,r.Position+direction*(step+1));previousDistance=desired
   r.AssemblyLinearVelocity=Vector3.zero;RunService.Heartbeat:Wait()
  end
  if h.Parent then h.AutoRotate=true end
  if r.Parent and os.clock()>=(s.knockedUntil or 0) then r:SetNetworkOwnershipAuto() end
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
  if s.data.coins<Config.MicroSpeakerPrice then state(p,"Micro-speaker costs "..Config.MicroSpeakerPrice.." coins. You need "..(Config.MicroSpeakerPrice-s.data.coins).." more.");return end
  s.data.coins-=Config.MicroSpeakerPrice;s.data.amplifierOwned=true;s.data.amplifierEquipped=true
 end
 state(p,s.data.amplifierEquipped and "Micro-speaker equipped · +12% normalized power, capped at 100%" or "Micro-speaker unequipped")
end
local function vendorPurchase(p,s,arg)
 local bot=s.conversationBot;local _,root=parts(p)
 if type(arg)~="table" or arg.product~="MicroSpeaker" or not bot or arg.npc~=bot.id or bot.role~="Vendor" or not bot.alive or not bot.root.Parent or bot.talkingTo~=p or (bot.socialUntil or 0)<=os.clock() or not root or (root.Position-bot.root.Position).Magnitude>14 then
  state(p,"Speak with the market vendor nearby before buying.");return
 end
 -- No yielding between ownership check and debit: duplicate requests never charge twice.
 microSpeaker(p,s,false)
end
local function talk(p,id)
 local s=sessions[p];local _,r=parts(p);if not s or not r or type(id)~="string" or os.clock()<(s.nextTalk or 0) then return end
 for _,b in ipairs(World.Bots) do if b.id==id and b.alive and b.root.Parent and (b.root.Position-r.Position).Magnitude<=14 then
  if b.talkingTo and b.talkingTo~=p and (b.socialUntil or 0)>os.clock() then state(p,b.name.." is speaking with someone. Try again shortly.");return end
  closeConversation(p);s.conversationBot=b;b.talkingTo=p
  s.nextTalk=os.clock()+2
  local message=b.name..": "..World.Talk(b,p)
  if b.name=="Nick Booty" and not s.data.achievements.FoundNick then
   s.data.achievements.FoundNick=true;s.data.coins+=50;message="Hidden achievement: Found Nick Booty! +50 coins. "..message
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
  local hints={Gardener="The raised flowerbeds in Rambla Gardens need water. Hold F beside each bed after accepting my task.",Vendor="The café prepares orders for the music stage. Pick up a fresh order before starting your delivery.",Soccer="I call it an assist when I miss. Your microphone can steer a training ball; softer shots give you more control.",BeachWorker="Please keep the sand clear. You can follow the promenade to the pier and the hidden courts beyond it.",Busker="Come for the music, stay for the beach. The central arena is the only place where players can damage each other."}
  state(p,message,{npc=b.model,name=b.name,line=message,hint=hints[b.role] or "Explore the courtyards, shops and waterfront. Some residents offer tasks; player combat stays inside the central arena.",quests=choices,products=b.role=="Vendor" and {{id="MicroSpeaker",name="Micro-speaker",price=Config.MicroSpeakerPrice,owned=s.data.amplifierOwned,description="Handheld amplifier · +12% normalized power, capped at 100%. Buy once with earned coins."}} or nil});return
 end end
end
local function dev(p,command)
 local s=sessions[p];if not s or not Access.IsAuthorized(p,game.CreatorType,game.CreatorId) then return end
 local valid={Coins=true,XP=true,MaxLevel=true,LevelOne=true,Heal=true,Hub=true,Arena=true,Beach=true,ResetQuests=true,ResetBots=true}
 if type(command)~="string" or not valid[command] then return end
 -- Freeze legitimate progress before any test mutation. Keep renewing/releasing its lease.
 if not s.testBaseline then s.testBaseline=Profiles.Sanitize(s.data);s.data=Profiles.Sanitize(s.data) end
 local c,_,h=parts(p)
 local positions={Hub=World.SafeSpawn,Arena=CFrame.new(0,6,0),Beach=CFrame.new(0,4,403)}
 if command=="Coins" then s.data.coins+=1000
 elseif command=="XP" then xp(p,500)
 elseif command=="MaxLevel" then s.data.level=Config.MaxLevel;s.data.xp=0
 elseif command=="LevelOne" then s.data.level=1;s.data.xp=0;s.data.sound="TinyAah"
 elseif command=="Heal" and h then h.Health=h.MaxHealth
 elseif positions[command] and c then c:PivotTo(positions[command]);protect(p,s)
 elseif command=="ResetQuests" then stopQuest(p);s.data.quests={}
 elseif command=="ResetBots" then for _,b in ipairs(World.Bots) do b.health=Config.BotMaxHealth;b.alive=true;World.UpdateBot(b) end
 else return end
 syncHealth(p,command=="Heal");state(p,"Test applied · this session does not save")
end
World.OnVehicleSweep=function(car,previous,nextFrame)
 for player,s in pairs(sessions) do
  local character,root,humanoid=parts(player);local now=os.clock()
  if root and now>=s.protectedUntil and now>=(s.nextCarHit or 0) and Rules.VehicleSweep(previous*CFrame.new(0,.55,0),nextFrame*CFrame.new(0,.55,0),root.Position,Vector3.new(8,4,4.5)) then
   VoiceCombat.Cancel(s.voice);player:SetAttribute("CaptureStarted",0)
   s.nextCarHit=now+4;s.knockedUntil=now+1.3;s.dodgingUntil=0;s.sprintRequested=false;s.nextHeal=now+10
   player:SetAttribute("DodgeEnds",0);player:SetAttribute("KnockdownEnds",workspace:GetServerTimeNow()+1.3)
   local damage=math.clamp(math.floor(car.speed*1.1),15,35)
   if humanoid.Health<=damage then eject(player,humanoid);s.knockedUntil=0
   else
    humanoid.Health-=damage;humanoid.PlatformStand=true;humanoid.AutoRotate=false;root:SetNetworkOwner(nil)
    local direction=(nextFrame.Position-previous.Position).Unit
    local sideways=Vector3.new(0,0,car.lane%240<120 and -1 or 1)
    root.AssemblyLinearVelocity=direction*8+sideways*28+Vector3.new(0,12,0);root.AssemblyAngularVelocity=Vector3.new(0,0,4)*car.direction
    task.delay(1.3,function()
     if player.Character==character and humanoid.Parent and humanoid.Health>0 then
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
  elseif kind=="Pickup" and s.activeQuest=="delivery" then s.questDeadline=os.clock()+90;s.carrying=true;state(p,"Order collected · deliver to the boardwalk stage in 90s")
  elseif kind=="Dropoff" and s.activeQuest=="delivery" then
   if s.carrying and s.questDeadline and os.clock()<=s.questDeadline then s.carrying=false;s.questDeadline=nil;questProgress(p,"Delivery")
   else state(p,"Pick up a fresh order from the café first.") end
  elseif kind=="RaceStart" and s.activeQuest=="sprint" then s.questDeadline=os.clock()+25;s.raceStart=os.clock();state(p,"Go! Follow the boardwalk to the pier finish · 25s")
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
 local now=os.clock()
 s.requestWindow=s.requestWindow or now;s.requestCount=s.requestCount or 0
 if now-s.requestWindow>=1 then s.requestWindow=now;s.requestCount=0 end
 s.requestCount+=1;if s.requestCount>30 then return end
 if verb=="BeginCast" then
  p:SetAttribute("CaptureStarted",0)
  if VoiceCombat.Begin(s.voice,now,arg,canCapture(p,s,now)) then p:SetAttribute("CaptureStarted",workspace:GetServerTimeNow()) end;return
 elseif verb=="CancelCast" then VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0);return
 elseif verb=="EndConversation" then closeConversation(p);return
 elseif verb=="MicReady" then s.micReady=arg==true;if not s.micReady then VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0) end;return
 elseif verb=="Cast" then cast(p,arg);return elseif verb=="Dodge" then dodge(p);return
 elseif verb=="ExtraJump" then
  local _,root,h=parts(p)
  if root and s.micReady and Entitlements.CanUseMovement(p,root.Position) and now>=(s.nextExtraJump or 0) and now>=s.dodgingUntil and now>=(s.knockedUntil or 0) and h.FloorMaterial==Enum.Material.Air and s.jumpOriginY and root.Position.Y<s.jumpOriginY+24 then
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
 elseif verb=="SetAura" and type(arg)=="string" and Config.Auras[arg] then s.data.aura=arg;state(p)
 elseif verb=="AcceptQuest" then
  local q=type(arg)=="string" and Config.GetQuest(arg)
  if q and not s.data.availableQuests[q.id] then state(p,"Meet "..(q.giver or "the quest giver").." to unlock this task.");return end
  if q and q.id=="nick" then
   local _,root=parts(p)
   if not root or (root.Position-Vector3.new(647,4,547)).Magnitude>90 then state(p,"Return to Nick's coastal court to start.");return end
  end
  if q then local v=s.data.quests[q.id];if not v then v={progress=0,claimed=false};s.data.quests[q.id]=v end
   if not v.claimed and v.progress>=q.goal then state(p,"Task complete · claim your reward.");return end
   if not v.claimed then stopQuest(p);v.progress=0;s.activeQuest=q.id;state(p,q.name.." accepted")
    if q.id=="nick" then Soccer.Start(p,function(message) state(p,message) end,function()
     if sessions[p]==s and s.activeQuest=="nick" then s.questDeadline=nil;questProgress(p,"Soccer");state(p,"Nick: WE DID IT! Claim your reward in Quests.") end
    end,function() if sessions[p]==s and s.activeQuest=="nick" then stopQuest(p);state(p,"Nick: Attempt ended. Return to the court and accept my task to try again.") end end) end
   end end
 elseif verb=="AbandonQuest" then stopQuest(p);state(p,"Task abandoned. Unfinished progress was reset; earned rewards remain claimable.")
 elseif verb=="ClaimQuest" then
  local q=type(arg)=="string" and Config.GetQuest(arg);local v=q and s.data.quests[q.id]
  if v and not v.claimed and v.progress>=q.goal then v.claimed=true;if q.id=="nick" then s.data.achievements.NickChampion=true end;s.data.coins+=q.coins;xp(p,q.xp);if s.activeQuest==q.id then stopQuest(p) end;state(p,"Quest reward · +"..q.xp.." XP · +"..q.coins.." coins") end
 elseif verb=="SetSettings" and type(arg)=="table" then
  if type(arg.volume)=="number" and arg.volume==arg.volume then s.data.settings.volume=math.clamp(arg.volume,0,1) end
  if type(arg.reducedShake)=="boolean" then s.data.settings.reducedShake=arg.reducedShake end;state(p)
 end
end)
local function joined(p)
 task.spawn(Entitlements.Refresh,p)
 local data,save,loadMessage=Profiles.Load(p.UserId);if not p.Parent then if save then Profiles.Save(p.UserId,data,true) end;return end
 local s={data=data,canSave=save,voice=VoiceCombat.New(),micReady=false,protectedUntil=0,nextCast=0,nextDodge=0,dodgingUntil=0,nextAction=0,nextHeal=os.clock()+10,
 botRewards={},koRewards={},collected={},sprintRequested=false,sprintCharge=10,sprintLockedUntil=0,lastStep=os.clock()};sessions[p]=s
 local function spawn(c)
  local h=c:WaitForChild("Humanoid",10);if not h or p.Character~=c then return end
  s.jumpPower=h.JumpPower;s.jumpHeight=h.JumpHeight
  h.MaxHealth=Config.HealthForLevel(s.data.level);h.Health=h.MaxHealth;h.WalkSpeed=s.micReady and 16 or 0;s.sprintCharge=10;s.sprintRequested=false;s.sprintLockedUntil=0;s.dodgingUntil=0
  protect(p,s);state(p)
 end
 p.CharacterAdded:Connect(spawn);if p.Character then task.spawn(spawn,p.Character) end
 state(p,loadMessage or "Welcome · train for XP, unlock screams, and explore the coast")
end
Players.PlayerAdded:Connect(joined);for _,p in ipairs(Players:GetPlayers()) do task.spawn(joined,p) end
Players.PlayerRemoving:Connect(function(p) closeConversation(p);local s=sessions[p];if s and s.canSave then Profiles.Save(p.UserId,s.testBaseline or s.data,true) end;sessions[p]=nil end)
task.spawn(function()
 local tick=0
 while true do task.wait(0.1);tick+=1;local now=os.clock()
  for p,s in pairs(sessions) do
   local dt=math.clamp(now-s.lastStep,0,.25);s.lastStep=now;local _,r,h=parts(p)
   -- Crossing into PvP immediately restores the full dodge cooldown.
   if r and Config.InArena(r.Position) and s.lastDodge then
    if s.premiumRoll then s.premiumRoll=false;s.dodgingUntil=0;p:SetAttribute("DodgeEnds",0) end
    s.nextDodge=math.max(s.nextDodge,s.lastDodge+Config.DodgeCooldown);p:SetAttribute("DodgeReady",workspace:GetServerTimeNow()+math.max(0,s.nextDodge-now)) end
   if s.voice.capture and now-s.voice.capture.started>VoiceCombat.CaptureExpiry then VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0) end
   if s.sprintLockedUntil>0 and now>=s.sprintLockedUntil then s.sprintLockedUntil=0;s.sprintCharge=10 end
   local running=h and s.sprintRequested and s.sprintCharge>0 and now>=s.sprintLockedUntil
   if running then s.sprintCharge=math.max(0,s.sprintCharge-dt);if s.sprintCharge==0 then running=false;s.sprintLockedUntil=now+5 end
   elseif now>=s.sprintLockedUntil then s.sprintCharge=math.min(10,s.sprintCharge+dt*2) end
   if h then
    if h.FloorMaterial~=Enum.Material.Air then s.jumpOriginY=r.Position.Y end
    h.WalkSpeed=not s.micReady and 0 or now<(s.knockedUntil or 0) and 0 or now<s.dodgingUntil and 0 or running and 25 or 16
    h.JumpPower=s.micReady and (s.jumpPower or 50) or 0;h.JumpHeight=s.micReady and (s.jumpHeight or 7.2) or 0
    if not s.micReady then h.Jump=false end
    if h.Health<h.MaxHealth and now>=s.nextHeal then h.Health=math.min(h.MaxHealth,h.Health+h.MaxHealth*.2);s.nextHeal=now+10 end
    if r.Position.Z>600 and (r.Position.Z>780 or math.abs(r.Position.X)>700) then
     p.Character:PivotTo(CFrame.new(math.clamp(r.Position.X,-670,670),5,594))
     r.AssemblyLinearVelocity=Vector3.zero;r.AssemblyAngularVelocity=Vector3.zero
     s.sprintRequested=false;s.dodgingUntil=0;s.knockedUntil=0;h.PlatformStand=false;h.AutoRotate=true
     p:SetAttribute("DodgeEnds",0);p:SetAttribute("KnockdownEnds",0);protect(p,s)
     state(p,"Lifeguard rescue · stay inside the gold buoys.")
    elseif r.Position.Y< -20 then p.Character:PivotTo(World.SafeSpawn);protect(p,s) end
   end
   if s.questDeadline and now>s.questDeadline then stopQuest(p);state(p,"Time's up · accept the task again to restart.") end
   p:SetAttribute("SprintCharge",s.sprintCharge);p:SetAttribute("SprintCooldown",math.max(0,s.sprintLockedUntil-now));p:SetAttribute("Sprinting",running==true)
   if tick%5==0 then state(p) end
  end
 end
end)
task.spawn(function() while true do task.wait(60);for p,s in pairs(sessions) do if s.canSave then task.spawn(Profiles.Save,p.UserId,s.testBaseline or s.data) end end end end)
game:BindToClose(function() local pending=0;for p,s in pairs(sessions) do if s.canSave then pending+=1;task.spawn(function() Profiles.Save(p.UserId,s.testBaseline or s.data,true);pending-=1 end) end end;local deadline=os.clock()+25;while pending>0 and os.clock()<deadline do task.wait(.1) end end)
