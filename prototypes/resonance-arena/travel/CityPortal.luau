-- Place the Hall entrance beside the existing Academy spawn.
local travel=require(script.Parent.TravelGate)
local function bind(world,spawnPosition)
 local ray=RaycastParams.new()
 ray.FilterType=Enum.RaycastFilterType.Include
 ray.FilterDescendantsInstances={world}
 ray.RespectCanCollide=true
 local point=spawnPosition+Vector3.new(8,0,0)
 local ground=assert(workspace:Raycast(point+Vector3.new(0,8,0),Vector3.new(0,-26,0),ray),"Missing Academy portal ground")
 local portal=Instance.new("Part")
 portal.Name="HallPortalAnchor";portal.Size=Vector3.new(1,6,8)
 portal.Position=ground.Position+Vector3.new(0,3,0)
 portal.Anchored=true;portal.CanCollide=false;portal.CanQuery=false;portal.CanTouch=false
 portal.Material=Enum.Material.Neon;portal.Color=Color3.fromRGB(81,221,214);portal.Transparency=.65;portal.Parent=world
 local prompt=Instance.new("ProximityPrompt")
 prompt.ActionText="Enter arena";prompt.ObjectText="Resonance Hall";prompt.HoldDuration=.25
 prompt.RequiresLineOfSight=false;prompt.MaxActivationDistance=10;prompt.Parent=portal
 travel.Bind(prompt)
 local arrival=ground.Position+Vector3.new(-8,3.8,0)
 travel.BindArrival(CFrame.lookAt(arrival,arrival-Vector3.zAxis),
  "Academy arrival. Find the training courts to the north.")
 return ground.Position
end
return bind
