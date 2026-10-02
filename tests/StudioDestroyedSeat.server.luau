-- Append to Bootstrap in disposable Studio Play. Actual cloned resident and Seat mechanics.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio(),"Local Studio only")
 local fixture=Instance.new("Folder");fixture.Name="DestroyedSeatFixture";fixture.Parent=workspace.ScreamSimulatorWorld
 local checks=0;local details={}
 local function check(v,message) assert(v,message);checks+=1 end
 local ok,err=xpcall(function()
  local floor=Instance.new("Part");floor.Size=Vector3.new(60,1,40);floor.Position=Vector3.new(0,997,0);floor.Anchored=true;floor.Parent=fixture
  local actor=assert(World.Bots[1]).model:Clone();actor.Name="SeatTestResident";actor.Parent=fixture
  local h=actor:FindFirstChildOfClass("Humanoid");local root=actor.HumanoidRootPart
  actor:PivotTo(CFrame.new(0,1001,0));root:SetNetworkOwner(nil)
  for cycle=1,3 do
   local x=(cycle-2)*16
   local bench=Instance.new("Model");bench.Name="Bench"..cycle;bench:SetAttribute("DestructibleType","Bench");bench.Parent=fixture
   local seat=Instance.new("Seat");seat.Size=Vector3.new(4,1,2);seat.CFrame=CFrame.new(x,999,0);seat.Anchored=true;seat.Parent=bench
   game:GetService("CollectionService"):AddTag(bench,"CityDestructible");Destruction.Register(bench)
   actor:PivotTo(CFrame.new(x,1002,0));root.AssemblyLinearVelocity=Vector3.zero;task.wait(.15);seat:Sit(h);task.wait(.3)
   check(seat.Occupant==h and h.SeatPart==seat,"Real seating failed")
   Destruction.Damage(seat,1,24);task.wait(.1)
   check(seat.Occupant==h and not seat.Disabled,"Partial damage incorrectly ejects occupant")
   Destruction.Damage(seat,1,26);task.wait(.35)
   local retained=false
   for _,w in seat:GetChildren() do if w:IsA("Weld") and w.Name=="SeatWeld" and w.Part1 and w.Part1:IsDescendantOf(actor) then retained=true end end
   table.insert(details,{cycle=cycle,retainedWeld=retained,seated=h.SeatPart~=nil,state=h:GetState().Name})
   check(not retained and h.SeatPart==nil and not h.Sit,"Destroyed bench retained occupant")
   check(seat.Disabled and not seat.CanCollide and bench:GetAttribute("Destroyed"),"Destroyed seat remains usable")
   local start=root.Position;h:MoveTo(start+Vector3.new(10,0,0));task.wait(2)
   local moved=(Vector3.new(root.Position.X,0,root.Position.Z)-Vector3.new(start.X,0,start.Z)).Magnitude
   details[#details].moved=moved;check(moved>6,"Released resident cannot walk")
   bench:Destroy()
  end
 end,debug.traceback)
 fixture:Destroy()
 workspace:SetAttribute("DestroyedSeatResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,details=details,error=not ok and tostring(err) or nil}))
 print("Destroyed seat regression",ok,checks,err)
end)
