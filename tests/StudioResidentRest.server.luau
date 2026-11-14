-- Append to Bootstrap in a disposable local place; restore Source after testing.
-- Actual server Humanoid/Seat integration, not real player input or multiplayer proof.
task.spawn(function()
 assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0,"Local Studio only")
 task.wait(4)
 local checks=0
 local function check(value,message) assert(value,message);checks+=1 end
 local originals={}
 for _,b in ipairs(World.Bots) do originals[b]={socialUntil=b.socialUntil};b.socialUntil=os.clock()+120 end
 local bot,other=World.Bots[2],World.Bots[3]
 local seat
 for _,candidate in ipairs(World.Seats) do
  if candidate.Name=="UsableSeat" and not candidate.Occupant and (candidate.Position-World.SafeSpawn.Position).Magnitude<90 then seat=candidate;break end
 end
 local ok,err=xpcall(function()
  check(seat~=nil,"Nearby bench exists")
  bot.socialUntil=0;other.socialUntil=0
  bot.model:PivotTo(seat.CFrame*CFrame.new(0,1,-5));bot.root.AssemblyLinearVelocity=Vector3.zero
  task.spawn(function() World.UseSeat(bot,seat,20) end)
  task.wait(2)
  check(bot.humanoid.SeatPart==seat and seat.Occupant==bot.humanoid,"NPC physically seated")
  check(bot.model:GetAttribute("Resting")==true and bot.readingBook~=nil,"Reading state and prop active")
  check(World.UseSeat(other,seat,1)==false,"Second NPC cannot claim occupied bench")
  World.Talk(bot)
  task.wait(.3)
  check(bot.restSeat==nil and bot.humanoid.SeatPart~=seat,"Talking releases reservation and physical seat")
  check(bot.readingBook==nil and not bot.model:GetAttribute("Resting"),"Talk clears reading prop and pose")
  bot.socialUntil=os.clock()+10;task.wait(3.2);bot.socialUntil=0
  bot.model:PivotTo(seat.CFrame*CFrame.new(0,1,-5));bot.root.AssemblyLinearVelocity=Vector3.zero
  task.spawn(function() World.UseSeat(bot,seat,20) end);task.wait(2)
  check(bot.humanoid.SeatPart==seat,"Bench reusable after interruption")
  World.ReactToScream(bot,bot.root.Position+Vector3.new(8,0,0));task.wait(.3)
  check(bot.restSeat==nil and bot.readingBook==nil and bot.humanoid.SeatPart~=seat,"Scream interrupts seating and reading")
  bot.socialUntil=os.clock()+10;task.wait(3.3);bot.socialUntil=0;bot.reactionUntil=0
  bot.model:PivotTo(seat.CFrame*CFrame.new(0,1,-5));bot.root.AssemblyLinearVelocity=Vector3.zero
  task.spawn(function() World.UseSeat(bot,seat,20) end);task.wait(2)
  check(bot.humanoid.SeatPart==seat,"Bench reusable after scream")
  seat.Disabled=true;task.wait(.3)
  check(bot.restSeat==nil and bot.readingBook==nil,"Disabled bench releases reservation and prop")
  check(World.UseSeat(other,seat,1)==false,"Disabled bench rejects new activity")
  seat.Disabled=false
 end,debug.traceback)
 if seat then seat.Disabled=false end
 World.Talk(bot)
 for b,previous in pairs(originals) do b.socialUntil=previous.socialUntil end
 workspace:SetAttribute("ResidentRestPassed",ok);workspace:SetAttribute("ResidentRestChecks",checks);workspace:SetAttribute("ResidentRestError",ok and "" or tostring(err))
 print(ok and ("PASS "..checks.." resident seating checks") or ("FAIL resident seating: "..tostring(err)))
end)
