-- Append to Bootstrap in disposable Studio. Actual NPC locomotion with scripted damage.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio())
 local bot=assert(World.Bots[10]);local checks=0;local moved=0
 local ok,err=xpcall(function()
  bot.health=Config.BotMaxHealth;bot.alive=true;World.UpdateBot(bot)
  bot.socialUntil=os.clock()+5
  bot.model:PivotTo(CFrame.new(0,4,580));bot.root.AssemblyLinearVelocity=Vector3.zero;task.wait(.3)
  bot.health=Config.BotMaxHealth-10
  local start=bot.root.Position
  World.ReactToScream(bot,start-Vector3.new(10,0,0))
  local intended=bot.humanoid.WalkToPoint
  World.UpdateBot(bot)
  assert((bot.humanoid.WalkToPoint-intended).Magnitude<.01,"Health update cancelled flee target");checks+=1
  task.wait(2.1)
  moved=(Vector3.new(bot.root.Position.X,0,bot.root.Position.Z)-Vector3.new(start.X,0,start.Z)).Magnitude
  assert(moved>4,"Resident did not move away");checks+=1
  bot.alive=false;bot.health=0;bot.talkingTo=game.Players:GetPlayers()[1];bot.socialUntil=os.clock()+20
  World.UpdateBot(bot)
  assert(bot.root.Anchored and bot.talkingTo==nil and bot.socialUntil==0 and not bot.speech.Visible,"Knockout left stale activity");checks+=1
  bot.alive=true;bot.health=Config.BotMaxHealth;World.UpdateBot(bot)
  assert(not bot.root.Anchored and bot.humanoid.Health==Config.BotMaxHealth and (bot.root.Position-bot.start).Magnitude<.1,"Recovery did not restore resident");checks+=1
 end,debug.traceback)
 bot.alive=true;bot.health=Config.BotMaxHealth;World.UpdateBot(bot)
 workspace:SetAttribute("ResidentHitResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,moved=moved,error=not ok and tostring(err) or nil}))
 print("Resident hit regression",ok,checks,moved,err)
end)
