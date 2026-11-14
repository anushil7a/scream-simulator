-- Run on the server in an unpublished Studio city. Move the player beside the
-- west tap and hold F through engine input after this observer is installed.
assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio())
local stations={}
for _,m in workspace.ScreamSimulatorWorld:GetDescendants() do
 if m.Name=="BeachRinseStation" then table.insert(stations,m) end
end
assert(#stations==2,"Expected two beach rinse stations")
table.sort(stations,function(a,b)return a.Tap.Position.X<b.Tap.Position.X end)
local checks=1
for _,m in stations do
 assert(m.ModelStreamingMode==Enum.ModelStreamingMode.Atomic);checks+=1
 local beams=0
 for _,v in m:GetDescendants() do
  if v:IsA("Beam") then assert(not v.Enabled);beams+=1 end
  if v:IsA("BasePart") then assert(v.Position.Z-v.Size.Z/2>430,"Station intrudes into promenade") end
 end
 assert(beams==6);checks+=1
 for _,goal in ipairs({Vector3.new(m.Tap.Position.X,4,446),Vector3.new(m.Tap.Position.X,4,460)}) do
  local path=game:GetService("PathfindingService"):CreatePath({AgentRadius=2,AgentHeight=5,AgentCanJump=false})
  path:ComputeAsync(Vector3.new(m.Tap.Position.X,4,403),goal)
  assert(path.Status==Enum.PathStatus.Success,"Rinse station blocks beach access");path:Destroy();checks+=1
 end
end
local station=stations[1];local prompt=station.Tap.ProximityPrompt
local function enabledBeams()
 local count=0
 for _,v in station:GetDescendants() do if v:IsA("Beam") and v.Enabled then count+=1 end end
 return count
end
local connection
connection=station:GetAttributeChangedSignal("RinseActive"):Connect(function()
 if not station:GetAttribute("RinseActive") then return end
 connection:Disconnect()
 task.defer(function()
  local ok,err=xpcall(function()
   assert(enabledBeams()==6 and not prompt.Enabled,"Tap did not activate water and debounce");checks+=1
   workspace:SetAttribute("BeachRinseFlowing",true)
   task.wait(5.3)
   assert(not station:GetAttribute("RinseActive") and enabledBeams()==0 and prompt.Enabled,"Tap did not stop and rearm");checks+=1
  end,debug.traceback)
  workspace:SetAttribute("BeachRinseResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
 end)
end)
return {geometryChecks=checks,waitingForTap=true}
