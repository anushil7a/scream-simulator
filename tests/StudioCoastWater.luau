-- Disposable PlaceId-zero Play test. Moves one test character, then restores it.
-- Covers physical swimming and server rescue, not real microphone/input behavior.
assert(game.PlaceId==0,"Run only in a disposable local place")
local p=assert(game.Players:GetPlayers()[1],"Start Play with a client")
local c=assert(p.Character);local h=c:FindFirstChildOfClass("Humanoid");local root=c.HumanoidRootPart
local original=c:GetPivot();local health=h.Health
local results={}
local ok,message=pcall(function()
 c:PivotTo(CFrame.new(0,-1,650));root.AssemblyLinearVelocity=Vector3.zero;task.wait(2)
 assert(h:GetState()==Enum.HumanoidStateType.Swimming,"Did not enter swimming")
 assert(root.Position.Z>600 and root.Position.Y>-16,"Character fell through water")
 table.insert(results,"native swimming and buoyancy")
 for _,v in ipairs({Vector3.new(0,-1,790),Vector3.new(-710,-1,650),Vector3.new(710,-1,650)}) do
  c:PivotTo(CFrame.new(v));task.wait(.35)
  assert(root.Position.Z<600 and math.abs(root.Position.X)<=670.1,"Rescue did not return to shore")
  assert((p:GetAttribute("ProtectionEnds") or 0)>workspace:GetServerTimeNow(),"Rescue missing protection")
  assert(h.Health>=health,"Rescue unexpectedly damaged the character")
  table.insert(results,"rescue from "..tostring(v))
 end
end)
c:PivotTo(original);root.AssemblyLinearVelocity=Vector3.zero;root.AssemblyAngularVelocity=Vector3.zero
assert(ok,message)
return {passed=#results,checks=results}
