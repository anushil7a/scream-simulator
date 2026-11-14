-- Append to Bootstrap in disposable Studio. Real helper, cloned city rigs;
-- controlled performer state isolates capacity and interruption behavior.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio())
 task.wait(3)
 local clones={};local checks=0
 local function check(value,message) assert(value,message);checks+=1 end
 local ok,err=xpcall(function()
  local original
  for _,bot in ipairs(World.Bots) do if bot.role=="Busker" and bot.job then original=bot;break end end
  assert(original)
  original.socialUntil=os.clock()+30;original.working=false
  original.pathVersion=(original.pathVersion or 0)+1
  original.model:PivotTo(CFrame.new(195,4,413));original.humanoid:MoveTo(original.root.Position)
  local function clone(source,position)
   local m=source.model:Clone();m.Name="AudienceFixture";m.Parent=workspace
   m:PivotTo(CFrame.new(position))
   local b={model=m,root=m.HumanoidRootPart,humanoid=m.Humanoid,alive=true,health=60,role="Local",name="Audience test",label=source.label,speech=source.speech}
   b.root:SetNetworkOwner(nil)
   table.insert(clones,b);table.insert(World.Bots,b);return b
  end
  local performer=clone(original,Vector3.new(150,5.5,426));performer.role="Busker";performer.job={};performer.working=true
  local listeners={}
  for i=1,4 do listeners[i]=clone(World.Bots[1],Vector3.new(138+i*5,4,413)) end
  task.wait(.3)
  for i=1,3 do task.spawn(function() World.WatchPerformance(listeners[i]) end) end
  task.wait(.3)
  for i=1,3 do check(listeners[i].watchingPerformer==performer,"Listener failed to join") end
  check(not World.WatchPerformance(listeners[4]),"Audience exceeded three")
  -- Force only the remaining watch time; use actual client animation attributes.
  for i=1,3 do listeners[i].watchingUntil=os.clock()+2.2 end
  task.wait(.3)
  for i=1,3 do check(listeners[i].model:GetAttribute("Applauding"),"Applause did not start") end
  World.ReactToScream(listeners[1],Vector3.new(150,4,420))
  check(not listeners[1].watchingPerformer and not listeners[1].model:GetAttribute("Applauding"),"Attack did not cancel audience")
  performer.working=false;task.wait(.3)
  check(not listeners[2].watchingPerformer and not listeners[3].watchingPerformer,"Audience stayed after performance stopped")
  check(not listeners[2].model:GetAttribute("Applauding"),"Stale applause after performance")
  performer.working=true
  check(not World.WatchPerformance(listeners[2]),"Audience cooldown bypassed")
  listeners[4].nextPerformance=0;listeners[4].model:PivotTo(CFrame.new(150,4,470))
  check(not World.WatchPerformance(listeners[4]),"Distant resident joined")
 end,debug.traceback)
 for _,bot in ipairs(clones) do
  bot.alive=false;bot.model:Destroy()
  local index=table.find(World.Bots,bot);if index then table.remove(World.Bots,index) end
 end
 workspace:SetAttribute("AudienceResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
 print("Audience regression",ok,checks,err)
end)
