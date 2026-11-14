-- Append to Bootstrap in an unpublished Studio copy. Deterministic traffic steps,
-- native CFrames/models; does not replace a real multiplayer collision playtest.
task.spawn(function()
 task.wait(3)
 local originalBots,originalSweep=World.Bots,World.OnVehicleSweep
 local root=Instance.new("Part");root.Anchored=true;root.Parent=workspace
 local model=World.Cars[1].model:Clone();model.Parent=workspace
 local checks=0;local callbacks=0
 local function check(ok,message) assert(ok,message);checks+=1 end
 local ok,err=xpcall(function()
  World.Bots={{alive=true,root=root}}
  World.OnVehicleSweep=function(_,before,after)
   check((after.Position-before.Position).Magnitude>0,"Stationary impact callback")
   callbacks+=1
  end
  for _,direction in ipairs({1,-1}) do
   local car={model=model,speed=24,cruiseSpeed=24,direction=direction,distance=600,lane=1000}
   local x=direction>0 and -90 or 90
   model:PivotTo(CFrame.new(x,2.05,1000)*CFrame.Angles(0,direction>0 and 0 or math.pi,0))
   root.Position=Vector3.new(x+direction*24,4,1000)
   local previousSpeed=24
   for i=1,180 do
    World.StepTraffic(car,1/60)
    check(car.speed<=previousSpeed+.001,"Car accelerated toward resident")
    check((root.Position.X-model:GetPivot().Position.X)*direction>=8.99,"Car entered resident clearance")
    previousSpeed=car.speed
   end
   check(car.speed<.001,"Car did not stop")
   local count=callbacks;World.StepTraffic(car,.1)
   check(callbacks==count,"Stopped car caused impact")
   root.Position+=Vector3.new(0,0,10)
   World.StepTraffic(car,.1)
   check(car.speed>0 and car.speed<=.801,"Car did not accelerate gradually")
   for i=1,240 do World.StepTraffic(car,1/60) end
   check(math.abs(car.speed-24)<.001,"Car never resumed cruise")
   -- A resident steps directly in front of a moving car: clamp this frame's travel.
   root.Position=model:GetPivot():PointToWorldSpace(Vector3.new(9.05,2,0))
   local before=model:GetPivot().Position
   World.StepTraffic(car,.1)
   check((model:GetPivot().Position-before).Magnitude<=.051,"Sudden crossing overrun")
   root.Position=model:GetPivot():PointToWorldSpace(Vector3.new(-20,2,0))
   local speed=car.speed;World.StepTraffic(car,.1)
   check(car.speed>speed,"Resident behind car blocked recovery")
  end
 end,debug.traceback)
 World.Bots=originalBots;World.OnVehicleSweep=originalSweep
 root:Destroy();model:Destroy()
 workspace:SetAttribute("TrafficResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
 print("Traffic checks",ok,checks,err)
end)
