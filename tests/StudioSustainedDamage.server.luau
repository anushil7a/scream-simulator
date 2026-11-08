-- Append to Bootstrap only in a disposable local Studio copy.
-- Set Workspace.LocalSustainedPrototype=true in Edit mode before Play.
-- Drives the adapter/server ticks with synthetic power and a controlled target.
task.spawn(function()
 assert(sustainedEnabled and game.PlaceId==0)
 local p=Players:GetPlayers()[1] or Players.PlayerAdded:Wait()
 local deadline=os.clock()+20
 while (not sessions[p] or not parts(p)) and os.clock()<deadline do task.wait(.1) end
 local s=assert(sessions[p]);assert(not s.canSave)
 local c,r=parts(p);assert(c and r)
 local bot=assert(World.Bots[1])
 local oldBots=World.Bots
 local oldBotFrame,oldPlayerFrame=bot.model:GetPivot(),c:GetPivot()
 local oldBotHealth,oldBotAlive,oldBotAnchor,oldPlayerAnchor=bot.health,bot.alive,bot.root.Anchored,r.Anchored
 local oldReady,oldProtection=s.micReady,s.protectedUntil
 local wall=Instance.new("Part")
 local checks=0
 local function check(value,message) assert(value,message);checks+=1 end
 local ok,err=xpcall(function()
  World.Bots={bot}
  r.Anchored=true;c:PivotTo(CFrame.new(0,504,0))
  bot.root.Anchored=true;bot.model:PivotTo(CFrame.new(0,504,-12))
  bot.alive=true;bot.health=Config.BotMaxHealth
  s.micReady=true;s.protectedUntil=0;s.dodgingUntil=0;s.knockedUntil=0
  local origin=attackOrigin(c,r)
  local aim=bot.root.Position
  wall.Anchored=true;wall.Size=Vector3.new(20,20,1);wall.Position=(origin+aim)/2;wall.Parent=workspace
  local now=os.clock()
  check(sustained.Begin(s.sustained,now, {sequence=1,power=1,aim=aim},sustainedContext(p,s,now)),"Begin rejected")
  stepSustained(p,s,now+.2)
  check(bot.health==Config.BotMaxHealth,"Damage crossed cover")
  wall:Destroy()
  check(sustained.Pulse(s.sustained,now+.3,{sequence=1,sample=1,power=1,aim=aim},sustainedContext(p,s,now+.3)),"Pulse rejected")
  local coins=s.data.coins
  stepSustained(p,s,now+.4)
  check(bot.health==Config.BotMaxHealth-2 and s.data.coins==coins+2,"First hit damage or reward incorrect")
  stepSustained(p,s,now+.6)
  check(bot.health==Config.BotMaxHealth-5 and s.data.coins==coins+2,"Second tick did not apply bounded damage or repeated reward")
  stepSustained(p,s,now+.81)
  check(not s.sustained.protocol.active and bot.health==Config.BotMaxHealth-5,"Stale input still dealt damage")
 end,debug.traceback)
 wall:Destroy()
 World.Bots=oldBots
 bot.health=oldBotHealth;bot.alive=oldBotAlive;bot.model:PivotTo(oldBotFrame);bot.root.Anchored=oldBotAnchor;World.UpdateBot(bot)
 c:PivotTo(oldPlayerFrame);r.Anchored=oldPlayerAnchor
 s.sustained=sustained.New();s.micReady=oldReady;s.protectedUntil=oldProtection
 p:SetAttribute("SustainedActive",false);p:SetAttribute("SustainedReadyAt",0)
 workspace:SetAttribute("SustainedDamageResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
end)
