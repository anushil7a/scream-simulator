-- Append to Bootstrap in an unpublished Studio copy. Synthetic accepted casts;
-- verifies hit-resolution feedback, not actual microphone or multiplayer input.
task.spawn(function()
 assert(game.PlaceId==0 and RunService:IsStudio())
 local p=Players:GetPlayers()[1] or Players.PlayerAdded:Wait()
 while not sessions[p] do task.wait(.1) end
 local s=sessions[p];assert(not s.canSave,"Feedback fixture requires temporary test progress")
 local c,r,h=parts(p)
 local deadline=os.clock()+20
 while not r and os.clock()<deadline do task.wait(.1);c,r,h=parts(p) end
 assert(c and r and h,"Test character did not spawn")
 local oldState=state;local oldBots=World.Bots;local oldFrame=r.CFrame;local anchored=r.Anchored
 local checks=0;local message;local testPart
 local bot=assert(oldBots[10]);local botFrame=bot.model:GetPivot();local botHealth=bot.health;local botAlive=bot.alive;local botAnchor=bot.root.Anchored
 local ok,err=xpcall(function()
  World.Bots={};r.Anchored=true;r.CFrame=CFrame.new(0,504,0)
  s.micReady=true;s.protectedUntil=0;s.dodgingUntil=0;s.knockedUntil=0
  state=function(player,text,conversation) if player==p and text then message=text end end
  local function fire(sequence)
   s.voice=VoiceCombat.New()
   assert(VoiceCombat.Begin(s.voice,os.clock()-.5,sequence,true))
   message=nil;cast(p,{sequence=sequence,power=1,aim=Vector3.new(0,505,-100)})
  end
  fire(1);assert(message=="Scream missed",tostring(message));checks+=1
  testPart=Instance.new("Part");testPart.Anchored=true;testPart.Size=Vector3.new(20,20,1);testPart.CFrame=CFrame.new(0,505,-12);testPart.Parent=workspace
  fire(2);assert(message=="Scream stopped by cover",tostring(message));checks+=1
  testPart:SetAttribute("MicPracticeTarget",true);testPart:SetAttribute("RestColor",testPart.Color)
  fire(3);assert(string.find(message,"Practice hit",1,true),tostring(message));checks+=1
  testPart:Destroy();testPart=nil
  bot.health=Config.BotMaxHealth;bot.alive=true;bot.model:PivotTo(CFrame.new(0,504,-12));bot.root.Anchored=true;World.Bots={bot}
  fire(4)
  assert(message=="Hit 1 target · 18 damage each",tostring(message));checks+=1
  assert(bot.health==Config.BotMaxHealth-18,"Hit feedback did not match applied resident damage");checks+=1
 end,debug.traceback)
 state=oldState;World.Bots=oldBots
 bot.health=botHealth;bot.alive=botAlive;World.UpdateBot(bot);bot.model:PivotTo(botFrame);bot.root.Anchored=botAnchor
 if testPart then testPart:Destroy() end
 r.CFrame=oldFrame;r.Anchored=anchored;VoiceCombat.Cancel(s.voice)
 workspace:SetAttribute("CastFeedbackResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
end)
