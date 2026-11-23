local bindPortal=require(script.Parent.CityPortal)
local world=Instance.new("Folder")
world.Name="TravelOnlyCity"
world.Parent=workspace
local city=require(script.Parent.CompactCity).Build(world)
local ground=bindPortal(world,city.spawn.Position)
local spawn=Instance.new("SpawnLocation")
spawn.Size=Vector3.new(5,.2,5)
spawn.CFrame=CFrame.lookAt(ground+Vector3.new(-8,.15,0),ground+Vector3.new(0,.15,0))
spawn.Anchored=true;spawn.Transparency=1;spawn.CanCollide=false;spawn.CanQuery=false;spawn.Duration=0;spawn.Parent=world
