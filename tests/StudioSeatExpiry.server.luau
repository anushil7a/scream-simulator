-- Ordinary Bootstrap fixture in a disposable local place. Uses real SeatWelds.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio(),"Local Studio only")
 task.wait(3)
 local bot=World.Bots[2];local originals={};local checks=0;local moved={}
 for _,b in World.Bots do originals[b]=b.socialUntil;World.Talk(b);b.socialUntil=os.clock()+120 end
 local seats={}
 for _,seat in World.Seats do
  if seat.Name=="UsableSeat" and not seat.Occupant and (seat.Position-World.SafeSpawn.Position).Magnitude<90 then table.insert(seats,seat);break end
 end
 for _,seat in World.Seats do if seat.Name=="BeachSeat" and not seat.Occupant then table.insert(seats,seat);break end end
 local function check(v,msg) assert(v,msg);checks+=1 end
 local ok,err=xpcall(function()
  check(#seats==2,"Bench and beach seat exist")
  for cycle=1,4 do
   local seat=seats[(cycle-1)%2+1]
   bot.socialUntil=0;bot.reactionUntil=0
   bot.model:PivotTo(seat.CFrame*CFrame.new(0,1,-5));bot.root.AssemblyLinearVelocity=Vector3.zero
   check(World.UseSeat(bot,seat,1),"Timed seat activity completed")
   bot.socialUntil=os.clock()+10;task.wait(.3)
   check(bot.humanoid.SeatPart==nil and not bot.humanoid.Sit,"Expired break physically detached")
   check(bot.restSeat==nil and bot.readingBook==nil and not bot.model:GetAttribute("Resting"),"Expired break cleared activity")
   for _,w in seat:GetChildren() do check(not(w:IsA("Weld") and w.Name=="SeatWeld" and w.Part1 and w.Part1:IsDescendantOf(bot.model)),"NPC seat weld remains") end
   local before=bot.root.Position
   bot.humanoid:MoveTo(before+seat.CFrame.LookVector*10);task.wait(1.8)
   local distance=(bot.root.Position-before).Magnitude;table.insert(moved,distance)
   check(distance>3,"Resident cannot walk away after expiry")
  end
 end,debug.traceback)
 World.Talk(bot);for b,value in pairs(originals) do b.socialUntil=value end
 workspace:SetAttribute("SeatExpiryResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,moved=moved,error=not ok and tostring(err) or nil}))
 print("Seat expiry regression",ok,checks,err)
end)
