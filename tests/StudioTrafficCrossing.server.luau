-- Append to Bootstrap in an unpublished Studio copy. Actual Humanoid walking
-- and server Heartbeat traffic; temporarily isolate one car and one resident.
task.spawn(function()
 task.wait(4)
 local cars=World.Cars
 local bot=World.Bots[1]
 local originalPose=bot.model:GetPivot()
 local originalSpeed=bot.humanoid.WalkSpeed
 local model=cars[3].model:Clone();model.Name="TrafficCrossingFixture";model.Parent=workspace
 local records={};local checks=0
 local function check(value,message) assert(value,message);checks+=1 end
 local ok,err=xpcall(function()
  World.Cars={}
  World.Talk(bot);bot.socialUntil=os.clock()+40
  task.wait(.5)
  for _,direction in ipairs({1,-1}) do
   local startX=direction>0 and -650 or 650
   local crossingX=startX+30*direction
   local car={model=model,hull=model.CollisionHull,direction=direction,lane=112,speed=24,cruiseSpeed=24,distance=40}
   model:PivotTo(CFrame.new(startX,2.05,112)*CFrame.Angles(0,direction>0 and 0 or math.pi,0))
   bot.model:PivotTo(CFrame.new(crossingX,3.2,104));bot.lastGrounded=bot.root.Position;bot.airSince=nil
   bot.root.AssemblyLinearVelocity=Vector3.zero;bot.root.AssemblyAngularVelocity=Vector3.zero
   bot.humanoid.WalkSpeed=7
   task.wait(.2)
   World.Cars={car};bot.humanoid:MoveTo(Vector3.new(crossingX,3.2,128))
   local started=os.clock();local minimumSpeed=24;local maximumHeight=0;local maximumHorizontalDrift=0;local sawYield=false
   while os.clock()-started<6 do
    game:GetService("RunService").Heartbeat:Wait()
    minimumSpeed=math.min(minimumSpeed,car.speed)
    maximumHeight=math.max(maximumHeight,bot.root.Position.Y)
    maximumHorizontalDrift=math.max(maximumHorizontalDrift,math.abs(bot.root.Position.X-crossingX))
    sawYield=sawYield or model:GetAttribute("Yielding")==true
   end
   table.insert(records,{direction=direction,minimumSpeed=minimumSpeed,maximumHeight=maximumHeight,horizontalDrift=maximumHorizontalDrift,finalZ=bot.root.Position.Z,finalSpeed=car.speed,sawYield=sawYield})
   check(sawYield and minimumSpeed<23,"Car never yielded to crossing NPC")
   check(bot.root.Position.Z>124,"NPC failed to cross")
   check(maximumHeight<6,"Crossing lifted NPC")
   check(maximumHorizontalDrift<2,"Car pushed NPC sideways")
   check(car.speed>23,"Car failed to resume")
   World.Cars={}
  end
 end,debug.traceback)
 World.Cars=cars;model:Destroy()
 bot.humanoid.WalkSpeed=originalSpeed;bot.model:PivotTo(originalPose);bot.lastGrounded=bot.root.Position;bot.airSince=nil
 bot.root.AssemblyLinearVelocity=Vector3.zero;bot.root.AssemblyAngularVelocity=Vector3.zero;bot.humanoid:MoveTo(bot.root.Position);bot.socialUntil=os.clock()+1
 local result={passed=ok,checks=checks,records=records,error=not ok and tostring(err) or nil}
 workspace:SetAttribute("TrafficCrossingResult",game:GetService("HttpService"):JSONEncode(result))
 print("Traffic crossing",game:GetService("HttpService"):JSONEncode(result))
end)
