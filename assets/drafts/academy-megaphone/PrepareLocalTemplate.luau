-- Run in the Studio command bar after importing AcademyMegaphone.fbx with
-- Upload to Roblox off and Set Pivot to Scene Origin on.
local run = game:GetService("RunService")
assert(run:IsStudio() and not run:IsRunning() and game.PlaceId == 0 and game.GameId == 0,
    "Open an unpublished local place in Edit mode")

local model = workspace:FindFirstChild("AcademyMegaphone")
assert(model and model:IsA("Model"), "Import AcademyMegaphone as a Model into Workspace")

local storage = game:GetService("ServerStorage")
local templates = storage:FindFirstChild("GearTemplates")
local templateName = "AcademyMegaphoneAccessory"
assert(not templates or templates:IsA("Folder") and not templates:FindFirstChild(templateName),
    "GearTemplates already contains an Academy Megaphone or is not a Folder")

local palette = {
    ["Brushed brass"] = Color3.fromRGB(224, 180, 86),
    ["Inner driver"] = Color3.fromRGB(82, 62, 42),
    ["Saddle leather"] = Color3.fromRGB(122, 74, 42),
    ["Warm enamel"] = Color3.fromRGB(242, 232, 206),
    ["Warm stitching"] = Color3.fromRGB(214, 186, 140),
}
local parts = {}
assert(#model:GetDescendants() == 5, "Expected five MeshParts directly under AcademyMegaphone")
for name in pairs(palette) do
    local part = model:FindFirstChild(name)
    assert(part and part:IsA("MeshPart") and part.Size.X > 0, "Missing expected MeshPart: " .. name)
    parts[name] = part
end
local enamel, handle = parts["Warm enamel"], parts["Saddle leather"]
local axes = model:GetPivot().Rotation
local hornDirection = axes:VectorToObjectSpace(enamel.Position - handle.Position) / enamel.Size.X
assert(math.abs(hornDirection.X) < .05 and hornDirection.Y > .3 and hornDirection.Z < -.45,
    "Expected the upright FBX with its bell pointing along local -Z")

-- Use the enamel's local width so the result is independent of the import unit.
model:ScaleTo(model:GetScale() * (.948 / enamel.Size.X))
model.PrimaryPart = nil
-- The handle center is .01 studs below the authored grip origin.
model.WorldPivot = axes + handle.Position + axes.UpVector * .01
model:PivotTo(CFrame.identity)
for name, part in pairs(parts) do
    part.Color = palette[name]
    part.Material = name == "Brushed brass" and Enum.Material.Metal or Enum.Material.SmoothPlastic
    part.Anchored = true
    part.CanCollide = false
    part.CanTouch = false
    part.CanQuery = false
end
if not templates then
    templates = Instance.new("Folder")
    templates.Name = "GearTemplates"
    templates.Parent = storage
end
model.Name = templateName
model:SetAttribute("PalmSurfaceGrip", true)
model.Parent = templates
