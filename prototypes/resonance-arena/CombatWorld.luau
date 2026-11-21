-- World adapter for the disposable combat build only.
assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0 and game.GameId==0)
local World={Bots={},SafeSpawn=CFrame.lookAt(Vector3.new(0,3.8,52),Vector3.new(0,3.8,0))}
function World.Build()
 local arena=assert(workspace:WaitForChild("ResonanceArena",10),"Resonance Hall geometry did not load")
 for _,object in ipairs(arena:GetDescendants()) do
  if object:IsA("ProximityPrompt") then object.KeyboardKeyCode=Enum.KeyCode.F end
 end
 arena.Name="ScreamSimulatorWorld"
end
return World
