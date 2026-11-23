local travel=require(script.Parent.TravelGate)
local world=Instance.new("Folder")
world.Name="TravelOnlyCity"
world.Parent=workspace
local city=require(script.Parent.CompactCity).Build(world)
local ray=RaycastParams.new()
ray.FilterType=Enum.RaycastFilterType.Include
ray.FilterDescendantsInstances={world}
ray.RespectCanCollide=true
local point=city.spawn.Position+Vector3.new(8,0,0)
local ground=assert(workspace:Raycast(point+Vector3.new(0,8,0),Vector3.new(0,-26,0),ray),"Missing Academy portal ground")
local spawn=Instance.new("SpawnLocation")
spawn.Size=Vector3.new(5,.2,5)
spawn.CFrame=CFrame.lookAt(ground.Position+Vector3.new(-8,.15,0),ground.Position+Vector3.new(0,.15,0))
spawn.Anchored=true;spawn.Transparency=1;spawn.CanCollide=false;spawn.CanQuery=false;spawn.Duration=0;spawn.Parent=world
local portal=Instance.new("Part")
portal.Name="HallPortalAnchor";portal.Size=Vector3.new(1,6,8)
portal.Position=ground.Position+Vector3.new(0,3,0)
portal.Anchored=true;portal.CanCollide=false;portal.CanQuery=false;portal.CanTouch=false
portal.Material=Enum.Material.Neon;portal.Color=Color3.fromRGB(81,221,214);portal.Transparency=.65;portal.Parent=world
local prompt=Instance.new("ProximityPrompt")
prompt.ActionText="Enter arena";prompt.ObjectText="Resonance Hall";prompt.HoldDuration=.25
prompt.RequiresLineOfSight=false;prompt.MaxActivationDistance=10;prompt.Parent=portal
travel.Bind(prompt)
local arrival=spawn.Position+Vector3.new(0,3.65,0)
travel.BindArrival(CFrame.lookAt(arrival,arrival-Vector3.zAxis),
 "Academy arrival. Find the training courts to the north.")
