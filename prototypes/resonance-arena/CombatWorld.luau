-- World adapter for the disposable combat build only.
assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0 and game.GameId==0)
local Layout=require(game:GetService("ReplicatedStorage").Shared.ResonanceLayout)
local hasPractice=not script.Parent:FindFirstChild("TravelGate")
local entry=Layout.HallEntry
local practice=Layout.PracticeEntry
local practiceSpawn=CFrame.lookAt(Vector3.new(practice.x,3.8,practice.z),Vector3.new(Layout.PracticePortal.x,3.8,Layout.PracticePortal.z))
local gapMiddle=(Layout.Hall.z+Layout.Hall.depth/2+Layout.Practice.z-Layout.Practice.depth/2)/2
local World={Bots={},SafeSpawn=CFrame.lookAt(Vector3.new(entry.x,3.8,entry.z),Vector3.new(entry.x,3.8,0))}
function World.FallRescue(position)
 if hasPractice and position.Z>=gapMiddle then return practiceSpawn,"Rescued · back on the training landing" end
end
function World.Build()
 local arena=assert(workspace:WaitForChild("ResonanceArena",10),"Resonance Hall geometry did not load")
 for _,object in ipairs(arena:GetDescendants()) do
  if object:IsA("ProximityPrompt") then object.KeyboardKeyCode=Enum.KeyCode.F end
 end
 arena.Name="ScreamSimulatorWorld"
end
return World
