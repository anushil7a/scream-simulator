-- Append to Bootstrap in a local disposable Studio build, then restore Source.
-- Uses actual natural worker loops; induces one scream reaction without a mic.
task.spawn(function()
 assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0,"Local Studio only")
 task.wait(4)
 local artist
 for _,bot in ipairs(World.Bots) do if bot.job and bot.role=="Artist" then artist=bot end end
 assert(artist,"Artist required")
 World.ReactToScream(artist,artist.root.Position-Vector3.new(8,0,0))
 task.wait(.3)
 local resumed=false;local maximum=0;local samples={};local displaced=0
 for i=1,100 do
  for _,bot in ipairs(World.Bots) do
   if bot.job and bot.jobStep>0 then
    local station=bot.job.stations[bot.jobStep]
    local delta=Vector3.new(bot.root.Position.X-station.position.X,0,bot.root.Position.Z-station.position.Z).Magnitude
    if bot==artist then displaced=math.max(displaced,delta) end
    if bot.working then
     maximum=math.max(maximum,delta);samples[bot.role]=(samples[bot.role] or 0)+1
     if bot==artist then resumed=true end
    end
   end
  end
  task.wait(.25)
 end
 local passed=resumed and displaced>2 and maximum<1
 local result={passed=passed,artistResumed=resumed,artistDisplacement=displaced,maxWorkOffset=maximum,samples=samples}
 workspace:SetAttribute("WorkArrivalResult",game:GetService("HttpService"):JSONEncode(result))
 print((passed and "PASS" or "FAIL").." natural work arrival: "..game:GetService("HttpService"):JSONEncode(result))
end)
