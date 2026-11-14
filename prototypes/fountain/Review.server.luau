local template=game.ServerStorage:WaitForChild("MosaicFountainTemplate")
require(script.Parent.Install).create(template,workspace,Vector3.new(0,1,0))
local floor=Instance.new("Part")
floor.Name="ReviewPlaza";floor.Size=Vector3.new(100,1,100);floor.Position=Vector3.new(0,.5,0)
floor.Anchored=true;floor.Material=Enum.Material.Limestone;floor.Color=Color3.fromRGB(219,204,177);floor.Parent=workspace
local spawn=Instance.new("SpawnLocation")
spawn.Name="ReviewSpawn";spawn.Size=Vector3.new(6,1,6);spawn.Position=Vector3.new(0,1.5,-30)
spawn.Anchored=true;spawn.Neutral=true;spawn.Duration=0;spawn.Transparency=1;spawn.Parent=workspace
