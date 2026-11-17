-- Standalone geometry/route review; deliberately contains no game server, remotes, or stores.
local RunService = game:GetService("RunService")
if not RunService:IsStudio() or game.GameId ~= 0 or game.PlaceId ~= 0 then return end

local Players = game:GetService("Players")
local Lighting = game:GetService("Lighting")
Players.CharacterAutoLoads = false

local map = Instance.new("Folder")
map.Name = "Map10_Overworld"
local staging = require(script.Parent.Zone05Geometry)
local zone = staging.Build(map)

local ocean = Instance.new("Part")
ocean.Name = "OceanPlane"
ocean.Size = Vector3.new(4200, 4, 4200)
ocean.Position = Vector3.new(0, -2.05, 0)
ocean.Material = Enum.Material.SmoothPlastic
ocean.Color = Color3.fromRGB(30, 139, 160)
ocean.Anchored = true
ocean.CanCollide = false
ocean.CanTouch = false
ocean.CanQuery = false
ocean.CastShadow = false
ocean.Parent = map

-- Fixed coastal look for like-for-like review; no streaming-dependent lighting triggers.
Lighting.ClockTime = 14.4
Lighting.Brightness = 2.5
Lighting.Ambient = Color3.fromRGB(124, 121, 121)
Lighting.OutdoorAmbient = Color3.fromRGB(141, 150, 156)
Lighting.EnvironmentDiffuseScale = 0.45
Lighting.EnvironmentSpecularScale = 0.55
Lighting.GlobalShadows = true
local atmosphere = Instance.new("Atmosphere")
atmosphere.Density = 0.19
atmosphere.Haze = 0.9
atmosphere.Glare = 0.06
atmosphere.Color = Color3.fromRGB(193, 225, 233)
atmosphere.Decay = Color3.fromRGB(121, 161, 178)
atmosphere.Parent = Lighting

-- Probe before anyone spawns; a missing floor fails closed instead of starting in the ocean.
local spawn = Instance.new("SpawnLocation")
spawn.Name = "FoundryReviewSpawn"
spawn.Transparency = 1
spawn.Size = Vector3.new(8, 0.4, 8)
spawn.Anchored = true
spawn.Neutral = true
spawn.Duration = 0
spawn.CanCollide = false
spawn.CanQuery = false
spawn.CanTouch = false
spawn.CFrame = CFrame.lookAt(Vector3.new(420, 48.2, -545), Vector3.new(420, 48.2, -680))
spawn.Parent = zone

local function anchor(name, cue, position)
    local part = Instance.new("Part")
    part.Name = name
    part.Size = Vector3.one
    part.Position = position
    part.Transparency = 1
    part.Anchored = true
    part.CanCollide = false
    part.CanQuery = false
    part.CanTouch = false
    part.CastShadow = false
    part:SetAttribute("Cue", cue)
    part:AddTag("FoundryAmbienceAnchor")
    part.Parent = zone
end
anchor("DockAmbienceAnchor", "Dock", Vector3.new(420, 27, -318))
anchor("LighthouseAmbienceAnchor", "Lighthouse", Vector3.new(814, 53, -650))

map.Parent = workspace
local probes = 0
local function testFloor(point)
    local hit = workspace:Raycast(point + Vector3.new(0, 6, 0), Vector3.new(0, -12, 0))
    assert(hit and hit.Instance:IsDescendantOf(zone) and math.abs(hit.Position.Y - point.Y) < 0.19,
        "Missing Foundry route floor at " .. tostring(point))
    probes += 1
end
testFloor(Vector3.new(420, 48, -545))
testFloor(Vector3.new(420, 48, -680))
for _, route in ipairs(staging.Routes) do
    local a, b = Vector3.new(table.unpack(route.a)), Vector3.new(table.unpack(route.b))
    local delta = b - a
    local side = Vector3.new(delta.Z, 0, -delta.X).Unit
    local count = math.ceil(delta.Magnitude / 4)
    for i = 0, count do
        local p = a:Lerp(b, i / count)
        for _, offset in ipairs({-route.width / 2 + 2, 0, route.width / 2 - 2}) do
            testFloor(p + side * offset)
        end
    end
end
local cover = game:GetService("CollectionService"):GetTagged("ArenaPillar")
assert(#cover == 8, "Foundry cover group is incomplete")
for _, pillar in ipairs(cover) do
    local center = Vector3.new(420, 55, -680)
    local radial = Vector3.new(pillar.Position.X - center.X, 0, pillar.Position.Z - center.Z).Unit
    for _, dy in ipairs({-6, 0, 12}) do
        local hit = workspace:Raycast(center + Vector3.new(0, dy, 0), radial * 83)
        assert(hit and hit.Instance == pillar, "Foundry cover does not stop rays: " .. pillar.Name)
        probes += 1
    end
end
workspace:SetAttribute("ReviewNativeRayProbes", probes)
print("[FoundryReview] Native Workspace ray probes passed:", probes)

workspace:SetAttribute("ReviewBuildName", "Map10V21FoundryReview")
Players.CharacterAutoLoads = true
local function setSpawn(player)
    player.RespawnLocation = spawn
end
Players.PlayerAdded:Connect(setSpawn)
for _, player in Players:GetPlayers() do
    setSpawn(player)
    if not player.Character then task.spawn(function() player:LoadCharacterAsync() end) end
end
