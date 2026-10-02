local Config = require(game:GetService("ReplicatedStorage").Shared.Config)
local RunService = game:GetService("RunService")
local PathfindingService = game:GetService("PathfindingService")
local Collection=game:GetService("CollectionService")

local World = {}
World.ZoneMin = Config.ZoneMin
World.ZoneMax = Config.ZoneMax
World.SafeSpawn = CFrame.new(-600, 4, 210)
World.Cars = {}
local PhysicsService=game:GetService("PhysicsService")
local City=require(script.Parent.City)
World.Bots = {}
World.WalkPoints = {}
World.ActivityPoints = {}
World.Seats = {}

local rng = Random.new(8044)
local C = {
    road = Color3.fromRGB(43, 48, 54), concrete = Color3.fromRGB(184, 183, 171),
    gold = Color3.fromRGB(247, 192, 59), glass = Color3.fromRGB(76, 139, 159),
    dark = Color3.fromRGB(30, 50, 52), green = Color3.fromRGB(60, 126, 79),
}

local function part(parent, name, size, cf, color, material, solid)
    local p = Instance.new("Part")
    p.Name, p.Size = name, size
    p.CFrame = typeof(cf) == "CFrame" and cf or CFrame.new(cf)
    p.Anchored = true
    p.Color = color
    p.Material = material or Enum.Material.SmoothPlastic
    p.CanCollide = solid ~= false
    p.CanQuery = solid ~= false
    p.Parent = parent
    return p
end

local function billboard(parent, words, offset, width)
    local gui = Instance.new("BillboardGui")
    gui.Name = "Label"
    gui.Size = UDim2.fromOffset(math.min(width or 150, 180), 30)
    gui.StudsOffsetWorldSpace = offset
    gui.AlwaysOnTop = false
    gui.MaxDistance = 24
    gui.Parent = parent
    local text = Instance.new("TextLabel")
    text.Size = UDim2.fromScale(1, 1)
    text.BackgroundColor3 = C.dark
    text.BackgroundTransparency = 0.12
    text.TextColor3 = Color3.fromRGB(255, 247, 218)
    text.Font = Enum.Font.GothamBold
    text.TextSize = 12
    text.TextWrapped = true
    text.Text = words
    text.Parent = gui
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 7)
    corner.Parent = text
    return text
end

local function vehicle(parent, kind, paint)
    local model = Instance.new("Model")
    model.Name = kind .. "Car"
    model.Parent = parent
    local body = part(model, "PaintedBody", Vector3.new(12, 1.8, 5.7), CFrame.new(), paint, Enum.Material.SmoothPlastic, false)
    model.PrimaryPart = body
    local hull=part(model,"CollisionHull",Vector3.new(12.6,4.2,6.2),CFrame.new(0,.55,0),paint,Enum.Material.SmoothPlastic,true)
    hull.Transparency=1;hull.CanTouch=true
    hull.CustomPhysicalProperties=PhysicalProperties.new(1,.35,0)
    model:SetAttribute("Vehicle",true)
    part(model, "LowerChassis", Vector3.new(12.5, 0.65, 5.9), CFrame.new(0, -0.85, 0),
        Color3.fromRGB(37, 43, 47), Enum.Material.Metal, false)
    part(model, "Hood", Vector3.new(3.1, 0.45, 5.35), CFrame.new(4.3, 1.03, 0), paint, Enum.Material.SmoothPlastic, false)
    part(model, "Trunk", Vector3.new(2.3, 0.35, 5.35), CFrame.new(-4.65, 1, 0), paint, Enum.Material.SmoothPlastic, false)
    part(model, "Cabin", Vector3.new(5.8, 1.8, 4.9), CFrame.new(-0.2, 1.8, 0),
        Color3.fromRGB(47, 72, 78), Enum.Material.Metal, false)
    part(model, "CabinRoof", Vector3.new(5.4, 0.25, 4.8), CFrame.new(-0.2, 2.78, 0), paint, Enum.Material.SmoothPlastic, false)
    for _, side in ipairs({-1, 1}) do
        local z = side * 2.52
        for _, x in ipairs({-1.45, 1.05}) do
            part(model, "SideGlass", Vector3.new(2, 1.25, 0.12), CFrame.new(x, 1.85, z),
                Color3.fromRGB(95, 150, 169), Enum.Material.Glass, false)
        end
        for _, x in ipairs({-4.2, 0.2}) do
            part(model, "DoorHandle", Vector3.new(0.85, 0.13, 0.15), CFrame.new(x, 0.38, side * 2.93),
                Color3.fromRGB(210, 218, 216), Enum.Material.Metal, false)
        end
        part(model, "SideMirror", Vector3.new(0.7, 0.35, 0.7), CFrame.new(2.65, 1.25, side * 3),
            Color3.fromRGB(42, 50, 54), Enum.Material.Metal, false)
        for _, x in ipairs({-3.85, 3.85}) do
            local tire = part(model, "RubberTire", Vector3.new(0.8, 2.1, 2.1),
                CFrame.new(x, -1.05, side * 2.83) * CFrame.Angles(0, math.pi / 2, 0),
                Color3.fromRGB(26, 29, 32), Enum.Material.Rubber, false)
            tire.Shape = Enum.PartType.Cylinder
            local hub = part(model, "WheelHub", Vector3.new(0.84, 1.05, 1.05),
                CFrame.new(x, -1.05, side * 3.27) * CFrame.Angles(0, math.pi / 2, 0),
                Color3.fromRGB(156, 165, 163), Enum.Material.Metal, false)
            hub.Shape = Enum.PartType.Cylinder
        end
        part(model, "Headlight", Vector3.new(0.2, 0.55, 1.1), CFrame.new(6.08, 0.3, side * 1.7),
            Color3.fromRGB(255, 239, 194), Enum.Material.Neon, false)
        part(model, "Taillight", Vector3.new(0.2, 0.58, 1.1), CFrame.new(-6.08, 0.3, side * 1.7),
            Color3.fromRGB(197, 58, 54), Enum.Material.Neon, false)
    end
    part(model, "Windshield", Vector3.new(0.18, 1.62, 4.55),
        CFrame.new(2.78, 1.8, 0) * CFrame.Angles(0, 0, math.rad(-23)),
        Color3.fromRGB(106, 162, 177), Enum.Material.Glass, false)
    part(model, "RearGlass", Vector3.new(0.18, 1.55, 4.55),
        CFrame.new(-3.15, 1.78, 0) * CFrame.Angles(0, 0, math.rad(22)),
        Color3.fromRGB(86, 139, 158), Enum.Material.Glass, false)
    part(model, "FrontGrille", Vector3.new(0.2, 0.65, 3), CFrame.new(6.12, -0.28, 0),
        Color3.fromRGB(45, 54, 59), Enum.Material.Metal, false)
    for _, x in ipairs({-6.2, 6.2}) do
        part(model, "Bumper", Vector3.new(0.35, 0.35, 5.75), CFrame.new(x, -0.75, 0),
            Color3.fromRGB(65, 73, 74), Enum.Material.Metal, false)
    end
    if kind == "Taxi" then
        part(model, "TaxiRoofSign", Vector3.new(2.8, 0.8, 1.35), CFrame.new(-0.2, 3.36, 0),
            Color3.fromRGB(252, 227, 161), Enum.Material.Neon, false)
        part(model, "TaxiChecker", Vector3.new(8, 0.25, 0.12), CFrame.new(0, -0.12, -2.94),
            Color3.fromRGB(44, 50, 52), Enum.Material.Metal, false)
    elseif kind == "Delivery" then
        part(model, "CargoRoof", Vector3.new(5.8, 0.7, 4.8), CFrame.new(-0.4, 3.17, 0),
            Color3.fromRGB(214, 212, 198), Enum.Material.Metal, false)
    end
    return model
end

local function taxi(parent, x, z, kind, paint)
    local car = vehicle(parent, kind or "Taxi", paint or Color3.fromRGB(244, 184, 42))
    car:PivotTo(CFrame.new(x, 2, z))
end

local names = {
    "Alex", "Jordan", "Sam", "Casey", "Taylor", "Riley", "Morgan", "Jamie", "Avery", "Cameron",
    "Drew", "Robin", "Parker", "Quinn", "Sky", "Hayden", "Blake", "Rowan", "Nico", "Ari",
    "Ellis", "Remy", "Sage", "Kit", "Milo", "Lena", "Zoe", "Noor", "Owen", "Jules",
    "Kai", "Maya", "Theo", "Ada", "Rafi", "Indie", "Marin", "Leo", "Nia", "Finn",
    "Uma", "Ezra", "Luca", "Iris", "Mira", "Dani", "June", "Sol", "Tess", "Jae", "Bea",
}
local lines = {"That was loud!", "Can you hear me?", "This city is wild!", "Nice scream!", "Watch out for the War Zone!", "I need some quiet.", "Whoa, my ears!", "You leveled up yet?"}
local roleLines = {
    CafeWorker = {"Two coffees for the terrace!", "The cups are hot. My jokes are lukewarm.", "Take a seat; the sea is the best view."},
    Sanitation = {"This promenade deserves a little care.", "If you find litter, Mar can use a hand.", "Keeping the city ready for tomorrow."},
    BeachWorker = {"Sunshade, water, and a little sea breeze.", "The loungers are ready. Please leave the sand clean.", "Someone keeps kicking footballs down the beach."},
    Soccer = {"I aimed for the goal. The goal moved. Probably.", "My best trick is missing from here.", "I celebrated before looking. It did not go in."},
    Gardener = {"These flowers need water, not another scream!", "I planted the blue ones for the sea.", "The garden is everyone’s front yard."},
    Artist = {"Hold still! You might end up in this painting.", "The sea changes color every hour.", "My last seagull looked like a potato."},
    Busker = {"One more song before the train!", "The market's got rhythm today.", "Toss me a request!"},
    Commuter = {"The next train is always late.", "I know a shortcut through the square.", "Coffee first, then the commute."},
    Tourist = {"That plaza is incredible!", "Where's the best snack cart?", "I keep finding new corners."},
    Local = {"I grew up on this block.", "The pier is my quiet spot.", "Meet me by the market later."},
    Fighter = {"The War Zone is getting loud.", "Time your dodge when you see a scream coming.", "I heard a knockout from the plaza."},
    Vendor = {"Fresh snacks on the corner!", "Busy day at the market.", "Try the stall across the street."},
}
local skinColors = {
    Color3.fromRGB(244, 204, 164), Color3.fromRGB(204, 149, 107), Color3.fromRGB(130, 88, 63),
    Color3.fromRGB(238, 184, 135), Color3.fromRGB(89, 59, 46), Color3.fromRGB(174, 118, 83),
    Color3.fromRGB(229, 172, 125), Color3.fromRGB(108, 72, 53),
}
local shirtColors = {
    Color3.fromRGB(63, 120, 173), Color3.fromRGB(192, 83, 79), Color3.fromRGB(77, 145, 105),
    Color3.fromRGB(169, 117, 65), Color3.fromRGB(117, 88, 150), Color3.fromRGB(56, 91, 114),
    Color3.fromRGB(203, 159, 96), Color3.fromRGB(65, 121, 124), Color3.fromRGB(170, 105, 141),
}
local pantsColors = {
    Color3.fromRGB(49, 58, 70), Color3.fromRGB(77, 64, 58), Color3.fromRGB(46, 68, 93),
    Color3.fromRGB(107, 102, 88), Color3.fromRGB(43, 49, 56), Color3.fromRGB(98, 76, 68),
}
local hairColors = {
    Color3.fromRGB(42, 33, 29), Color3.fromRGB(94, 58, 37), Color3.fromRGB(174, 128, 73),
    Color3.fromRGB(55, 61, 65), Color3.fromRGB(105, 74, 58), Color3.fromRGB(184, 164, 129),
}

local function rigPart(model, name, size, cf, color, collide)
    local p = Instance.new("Part")
    p.Name, p.Size, p.CFrame = name, size, cf
    p.Color = color
    p.CanCollide = collide == true
    p.CanQuery = false
    p.CanTouch = false
    p.CollisionGroup="Residents"
    p.Massless=name~="HumanoidRootPart"
    p.Parent = model
    return p
end

local function joint(parent, name, p0, p1, c0, c1)
    local m = Instance.new("Motor6D")
    m.Name, m.Part0, m.Part1, m.C0, m.C1 = name, p0, p1, c0, c1
    m.Parent = parent
    return m
end

local function accessory(model, attachedTo, name, size, offset, color, material, shape)
    local p = rigPart(model, name, size, attachedTo.CFrame * offset, color, false)
    p.Material = material or Enum.Material.SmoothPlastic
    p.Massless = true
    if shape then p.Shape = shape end
    local weld = Instance.new("WeldConstraint")
    weld.Part0, weld.Part1, weld.Parent = attachedTo, p, p
    return p
end

local function faceToward(bot, position)
    if not bot.alive or not bot.model.Parent then return end
    local flat = Vector3.new(position.X, bot.root.Position.Y, position.Z)
    if (flat - bot.root.Position).Magnitude > 0.4 then
        bot.root.CFrame = CFrame.lookAt(bot.root.Position, flat)
    end
end

function World.Speak(bot, message)
    if not bot.model.Parent or not bot.alive then return end
    bot.speech.Text = message
    bot.speech.Visible = true
    bot.speechToken = (bot.speechToken or 0) + 1
    local token = bot.speechToken
    task.delay(3.5, function()
        if bot.speechToken == token and bot.speech.Parent then bot.speech.Visible = false end
    end)
end

local seatReservations={}
local function releaseSeat(bot)
    local seat=bot.restSeat
    if seat and seatReservations[seat]==bot then seatReservations[seat]=nil end
    bot.restSeat=nil
    if bot.readingBook then bot.readingBook:Destroy();bot.readingBook=nil end
    if bot.model.Parent then bot.model:SetAttribute("Resting",false);bot.model:SetAttribute("Reading",false) end
    if seat and bot.humanoid.SeatPart==seat then
        bot.humanoid.Sit=false
        bot.humanoid:ChangeState(Enum.HumanoidStateType.GettingUp)
    end
end
local function stopWalking(bot)
    releaseSeat(bot)
    bot.pathVersion=(bot.pathVersion or 0)+1
    bot.humanoid:MoveTo(bot.root.Position)
    bot.working=false
end
function World.Talk(bot, player)
    stopWalking(bot)
    if player and player.Character then
        local root = player.Character:FindFirstChild("HumanoidRootPart")
        if root then faceToward(bot, root.Position) end
        bot.gestureUntil = os.clock() + 2.2
        bot.socialUntil = os.clock() + 5
    end
    local options = roleLines[bot.role] or lines
    local message = options[rng:NextInteger(1, #options)]
    World.Speak(bot, message)
    return message
end

local function chooseDestination(bot)
    local candidates = {}
    local useActivity = rng:NextNumber() < 0.47
    local source = useActivity and World.ActivityPoints or World.WalkPoints
    for _, entry in ipairs(source) do
        local point = useActivity and entry.position or entry
        local homeDistance = (point - bot.start).Magnitude
        local currentDistance = (point - bot.root.Position).Magnitude
        if homeDistance < bot.roamRadius and currentDistance > 14 and currentDistance < 145
            and (not bot.lastDestination or (point - bot.lastDestination).Magnitude > 18) then
            table.insert(candidates, {position = point, kind = useActivity and entry.kind or "Stroll"})
        end
    end
    if #candidates == 0 then return bot.start, "Stroll" end
    local chosen = candidates[rng:NextInteger(1, #candidates)]
    bot.lastDestination = chosen.position
    return chosen.position, chosen.kind
end

local function roamTo(bot, destination, precise)
    bot.pathVersion=(bot.pathVersion or 0)+1;local version=bot.pathVersion
    local path = PathfindingService:CreatePath({AgentRadius=2, AgentHeight=5, AgentCanJump=false, AgentCanClimb=false, WaypointSpacing=5, Costs={Fountain=math.huge,Asphalt=8}})
    local ok = pcall(function() path:ComputeAsync(bot.root.Position, destination) end)
    if not ok or path.Status ~= Enum.PathStatus.Success or bot.pathVersion~=version then path:Destroy();task.wait(0.3); return end
    local blocked = false
    local connection = path.Blocked:Connect(function() blocked = true end)
    for _, waypoint in ipairs(path:GetWaypoints()) do
        if bot.pathVersion~=version or blocked or not bot.alive or not bot.model.Parent or (bot.reactionUntil or 0) > os.clock() then break end
        if waypoint.Action == Enum.PathWaypointAction.Jump then break end
        bot.humanoid:MoveTo(waypoint.Position)
        local started, lastProgress, previous = os.clock(), os.clock(), bot.root.Position
        while (Vector3.new(waypoint.Position.X,bot.root.Position.Y,waypoint.Position.Z)-bot.root.Position).Magnitude > 2.8 do
            if bot.pathVersion~=version or not bot.alive or blocked or (bot.reactionUntil or 0) > os.clock() or os.clock()-started > 4 then break end
            if (bot.root.Position-previous).Magnitude > 0.7 then previous = bot.root.Position; lastProgress = os.clock() end
            if os.clock()-lastProgress > 0.8 then bot.humanoid:MoveTo(bot.root.Position); blocked=true; break end
            task.wait(0.06)
        end
    end
    connection:Disconnect();path:Destroy()
    -- MoveTo's broad arrival tolerance is fine for strolling, but leaves tools
    -- out of reach of work surfaces after an interrupted route. Finish the last
    -- short, path-checked segment using physical movement, never a position snap.
    if precise and not blocked and bot.pathVersion==version and (bot.root.Position-destination).Magnitude<4 then
        local speed=bot.humanoid.WalkSpeed;bot.humanoid.WalkSpeed=math.min(speed,4)
        local deadline=os.clock()+2
        while bot.alive and bot.model.Parent and bot.pathVersion==version and os.clock()<deadline and (bot.reactionUntil or 0)<=os.clock() do
            local delta=Vector3.new(destination.X-bot.root.Position.X,0,destination.Z-bot.root.Position.Z)
            if delta.Magnitude<.45 then break end
            bot.humanoid:Move(delta.Unit,false);task.wait(.05)
        end
        if bot.pathVersion==version then bot.humanoid:Move(Vector3.zero,false) end
        bot.humanoid.WalkSpeed=speed
    end
end

local function usableSeat(seat)
    local group=seat and seat.Parent
    return seat and seat.Parent and seat:IsA("Seat") and not seat.Disabled and group and not group:GetAttribute("Destroyed")
end
function World.UseSeat(bot,seat,duration)
    if not bot.alive or (bot.socialUntil or 0)>os.clock() or (bot.reactionUntil or 0)>os.clock() or not usableSeat(seat) or seat.Occupant or seatReservations[seat] then return false end
    stopWalking(bot);seatReservations[seat]=bot;bot.restSeat=seat
    bot.model:SetAttribute("Activity","Finding a seat")
    local approach=seat.Position+seat.CFrame.LookVector*4+Vector3.new(0,1,0)
    roamTo(bot,approach)
    if bot.restSeat~=seat then return false end
    if not bot.alive or not usableSeat(seat) or seat.Occupant or (bot.root.Position-seat.Position).Magnitude>8 then releaseSeat(bot);return false end
    bot.humanoid:MoveTo(bot.root.Position);seat:Sit(bot.humanoid)
    task.wait(.2)
    if bot.restSeat~=seat then return false end
    if bot.humanoid.SeatPart~=seat then releaseSeat(bot);return false end
    local reading=(bot.model:GetAttribute("AnimationSeed") or 0)%2==0
    bot.model:SetAttribute("Resting",true);bot.model:SetAttribute("Reading",reading)
    bot.model:SetAttribute("Activity",reading and (seat:GetAttribute("RestSetting")=="Beach" and "Reading by the sea" or "Reading in the courtyard") or "Taking a quiet break")
    if reading then
        local arm=bot.model:FindFirstChild("Left Arm")
        if arm then bot.readingBook=accessory(bot.model,arm,"CourtyardBook",Vector3.new(1.3,.15,1.1),CFrame.new(.3,-1,-.4),Color3.fromRGB(57,112,105),Enum.Material.Fabric) end
    end
    local ends=os.clock()+math.clamp(duration or rng:NextNumber(9,16),1,20)
    while bot.restSeat==seat and bot.alive and bot.model.Parent and usableSeat(seat) and seat.Occupant==bot.humanoid and os.clock()<ends do task.wait(.15) end
    if bot.restSeat==seat then releaseSeat(bot) end
    return true
end
local function restNearby(bot,destination)
    local choices={}
    for _,seat in ipairs(World.Seats) do
        if seat:IsA("Seat") and usableSeat(seat) and not seat.Occupant and not seatReservations[seat] and (seat.Position-destination).Magnitude<25 then table.insert(choices,seat) end
    end
    table.sort(choices,function(a,b) return (a.Position-bot.root.Position).Magnitude<(b.Position-bot.root.Position).Magnitude end)
    return choices[1] and World.UseSeat(bot,choices[1]) or false
end

local function socialize(bot)
    if (bot.socialUntil or 0) > os.clock() then return false end
    local friends = {}
    for _, other in ipairs(World.Bots) do
        if other ~= bot and other.alive and (other.socialUntil or 0) < os.clock()
            and (other.root.Position - bot.root.Position).Magnitude < 22 then
            table.insert(friends, other)
        end
    end
    if #friends == 0 then return false end
    local friend = friends[rng:NextInteger(1, #friends)]
    stopWalking(bot);stopWalking(friend)
    bot.socialUntil, friend.socialUntil = os.clock() + 8, os.clock() + 8
    bot.gestureUntil, friend.gestureUntil = os.clock() + 3, os.clock() + 3
    faceToward(bot, friend.root.Position)
    faceToward(friend, bot.root.Position)
    World.Speak(bot, roleLines[bot.role][rng:NextInteger(1, #roleLines[bot.role])])
    task.delay(1.8, function()
        if friend.alive and friend.model.Parent then
            World.Speak(friend, roleLines[friend.role][rng:NextInteger(1, #roleLines[friend.role])])
        end
    end)
    return true
end

local function noticePlayers(bot)
    if bot.restSeat or (bot.socialUntil or 0)>os.clock() then return end
    if (bot.lastGreeting or 0) + 14 > os.clock() then return end
    for _, player in ipairs(game:GetService("Players"):GetPlayers()) do
        local character = player.Character
        local root = character and character:FindFirstChild("HumanoidRootPart")
        if root and (root.Position - bot.root.Position).Magnitude < 16 then
            bot.lastGreeting = os.clock()
            bot.gestureUntil = os.clock() + 1.5
            faceToward(bot, root.Position)
            World.Speak(bot, ({"Hey there!", "Nice to see you around!", "What a day in the city!"})[rng:NextInteger(1, 3)])
            return
        end
    end
end

function World.ReactToScream(bot, origin)
    stopWalking(bot)
    bot.reactionUntil = os.clock() + 2.3
    bot.gestureUntil = bot.reactionUntil
    local delta = bot.root.Position - origin
    local away = Vector3.new(delta.X,0,delta.Z)
    if away.Magnitude > 0.5 then
        bot.humanoid:MoveTo(bot.root.Position + away.Unit * 8)
    end
    World.Speak(bot, ({"Whoa, my ears!", "That echoed down the block!", "Careful with that scream!"})[rng:NextInteger(1, 3)])
end

local function makeBot(parent, index, x, z, role, job)
    local displayName = names[(index - 1) % #names + 1] .. (index > #names and " " .. ({"Park", "Reed", "Chen", "Rivera", "Brooks", "Shah"})[(index-1)%6+1] or "")
    if job then displayName=job.name end
    local model = Instance.new("Model")
    model.Name = displayName .. "_TrainingNPC"
    model.ModelStreamingMode = Enum.ModelStreamingMode.Atomic
    model.Parent = parent
    model:SetAttribute("NpcId", "Bot" .. index)
    model:SetAttribute("DisplayName", displayName)
    model:SetAttribute("Role", role)
    local avatarRng = Random.new(8044 + index * 479)
    local home=Vector3.new(x,job and job.stations[1].position.Y or 3.9,z)
    local cf = CFrame.new(home)
    local skin = skinColors[avatarRng:NextInteger(1, #skinColors)]
    local shirt = shirtColors[avatarRng:NextInteger(1, #shirtColors)]
    local pants = pantsColors[avatarRng:NextInteger(1, #pantsColors)]
    local hairColor = hairColors[avatarRng:NextInteger(1, #hairColors)]
    local outfit = avatarRng:NextInteger(1, 5)
    if role=="Soccer" and job then shirt=Color3.fromRGB(43,105,168);pants=Color3.fromRGB(32,47,70);outfit=3 end
    model:SetAttribute("OutfitVariant", outfit)
    local root = rigPart(model, "HumanoidRootPart", Vector3.new(2, 2, 1), cf, Color3.new(1, 1, 1), false)
    root.Transparency = 1
    root.CanCollide = false
    local torso = rigPart(model, "Torso", Vector3.new(2, 2, 1), cf, shirt, true)
    local head = rigPart(model, "Head", Vector3.new(2, 1, 1), cf * CFrame.new(0, 1.5, 0), skin, false)
    local headMesh = Instance.new("SpecialMesh")
    headMesh.MeshType = Enum.MeshType.Head
    headMesh.Scale = Vector3.new(1.08, 1.08, 1.08)
    headMesh.Parent = head
    local la = rigPart(model, "Left Arm", Vector3.new(1, 2, 1), cf * CFrame.new(-1.5, 0, 0), skin, false)
    local ra = rigPart(model, "Right Arm", Vector3.new(1, 2, 1), cf * CFrame.new(1.5, 0, 0), skin, false)
    local ll = rigPart(model, "Left Leg", Vector3.new(1, 2, 1), cf * CFrame.new(-0.5, -2, 0), pants, false)
    local rl = rigPart(model, "Right Leg", Vector3.new(1, 2, 1), cf * CFrame.new(0.5, -2, 0), pants, false)
    joint(torso, "RootJoint", root, torso, CFrame.new(), CFrame.new())
    joint(torso, "Neck", torso, head, CFrame.new(0, 1, 0), CFrame.new(0, -0.5, 0))
    local ls = joint(torso, "Left Shoulder", torso, la, CFrame.new(-1, 0.5, 0), CFrame.new(0.5, 0.5, 0))
    local rs = joint(torso, "Right Shoulder", torso, ra, CFrame.new(1, 0.5, 0), CFrame.new(-0.5, 0.5, 0))
    local lh = joint(torso, "Left Hip", torso, ll, CFrame.new(-0.5, -1, 0), CFrame.new(0, 1, 0))
    local rh = joint(torso, "Right Hip", torso, rl, CFrame.new(0.5, -1, 0), CFrame.new(0, 1, 0))
    local face = Instance.new("Decal")
    face.Name, face.Texture, face.Face = "face", "rbxasset://textures/face.png", Enum.NormalId.Front
    face.Parent = head
    accessory(model, la, "LeftSleeve", Vector3.new(1.03, 0.9, 1.03), CFrame.new(0, 0.58, 0), shirt)
    accessory(model, ra, "RightSleeve", Vector3.new(1.03, 0.9, 1.03), CFrame.new(0, 0.58, 0), shirt)
    local shoeColor = avatarRng:NextNumber() < 0.5 and Color3.fromRGB(38, 42, 47) or Color3.fromRGB(230, 224, 209)
    accessory(model, ll, "LeftShoe", Vector3.new(1.05, 0.43, 1.22), CFrame.new(0, -0.78, -0.1), shoeColor)
    accessory(model, rl, "RightShoe", Vector3.new(1.05, 0.43, 1.22), CFrame.new(0, -0.78, -0.1), shoeColor)
    if outfit == 1 then
        accessory(model, head, "Beanie", Vector3.new(2.2, 0.6, 1.25), CFrame.new(0, 0.66, 0), hairColor, Enum.Material.Fabric)
        accessory(model, head, "BeanieBand", Vector3.new(2.24, 0.22, 1.3), CFrame.new(0, 0.34, 0), shirt, Enum.Material.Fabric)
    elseif outfit == 2 then
        accessory(model, head, "Cap", Vector3.new(2.15, 0.48, 1.2), CFrame.new(0, 0.66, 0), shirt, Enum.Material.Fabric)
        accessory(model, head, "CapBrim", Vector3.new(1.7, 0.13, 1.0), CFrame.new(0, 0.49, -0.85), shirt, Enum.Material.Fabric)
    elseif outfit == 3 then
        accessory(model, head, "Hair", Vector3.new(2.14, 0.5, 1.18), CFrame.new(0, 0.62, 0), hairColor)
        for _, dx in ipairs({-0.65, 0, 0.65}) do
            accessory(model, head, "CurlyHair", Vector3.new(0.78, 0.65, 0.8), CFrame.new(dx, 0.82, -0.21), hairColor, nil, Enum.PartType.Ball)
        end
    elseif outfit == 4 then
        accessory(model, head, "Hair", Vector3.new(2.17, 0.62, 1.27), CFrame.new(0, 0.66, 0), hairColor)
        for _, dx in ipairs({-1.07, 1.07}) do
            accessory(model, head, "HeadphoneEar", Vector3.new(0.35, 0.8, 0.7), CFrame.new(dx, 0.05, 0), C.dark)
        end
        accessory(model, head, "HeadphoneBand", Vector3.new(2.3, 0.18, 0.5), CFrame.new(0, 1.0, 0), C.dark)
    else
        accessory(model, head, "Hair", Vector3.new(2.16, 0.42, 1.2), CFrame.new(0, 0.61, 0), hairColor)
        accessory(model, torso, "Jacket", Vector3.new(2.12, 1.65, 0.18), CFrame.new(0, 0.05, -0.58),
            Color3.fromRGB(52, 67, 70), Enum.Material.Fabric)
    end
    if avatarRng:NextNumber() < 0.42 then
        for _, dx in ipairs({-0.47, 0.47}) do
            accessory(model, head, "GlassesLens", Vector3.new(0.68, 0.32, 0.1),
                CFrame.new(dx, 0.08, -0.58), Color3.fromRGB(58, 87, 93), Enum.Material.Glass)
        end
        accessory(model, head, "GlassesBridge", Vector3.new(0.28, 0.08, 0.14),
            CFrame.new(0, 0.09, -0.62), C.dark, Enum.Material.Metal)
    end
    local jobTool,water;local carryParts={}
    if role=="Soccer" and job then
        for _,leg in ipairs({ll,rl}) do accessory(model,leg,"FootballSock",Vector3.new(1.03,.9,1.03),CFrame.new(0,-.25,0),Color3.fromRGB(240,231,212),Enum.Material.Fabric) end
        local badge=accessory(model,torso,"NumberZero",Vector3.new(.62,.74,.12),CFrame.new(0,.15,-.58),Color3.fromRGB(240,231,212),Enum.Material.Fabric)
        local face=Instance.new("SurfaceGui");face.Face=Enum.NormalId.Front;face.CanvasSize=Vector2.new(80,100);face.Parent=badge
        local number=Instance.new("TextLabel");number.Size=UDim2.fromScale(1,1);number.BackgroundTransparency=1;number.Text="0";number.Font=Enum.Font.GothamBold;number.TextSize=76;number.TextColor3=Color3.fromRGB(32,47,70);number.Parent=face
    elseif role=="CafeWorker" then
        local trayGrip=CFrame.new(0,-1,-.6)*CFrame.Angles(-.8,0,0)
        table.insert(carryParts,accessory(model,la,"ServingTray",Vector3.new(1.5,.12,1),trayGrip,Color3.fromRGB(104,139,124),Enum.Material.Metal))
        for _,dx in ipairs({-.35,.35}) do table.insert(carryParts,accessory(model,la,"CoffeeCup",Vector3.new(.3,.4,.3),trayGrip*CFrame.new(dx,.26,0),Color3.fromRGB(243,225,191),Enum.Material.CeramicTiles)) end
        accessory(model,torso,"CafeApron",Vector3.new(1.7,1.5,.1),CFrame.new(0,-.2,-.57),Color3.fromRGB(71,139,125),Enum.Material.Fabric)
    elseif role=="Sanitation" then
        accessory(model,ra,"BroomHandle",Vector3.new(.14,2.7,.14),CFrame.new(0,-1.25,-.45),Color3.fromRGB(155,113,77),Enum.Material.Wood)
        accessory(model,ra,"BroomHead",Vector3.new(1.6,.35,.65),CFrame.new(0,-2.6,-.45),Color3.fromRGB(196,163,97),Enum.Material.Fabric)
        accessory(model,torso,"SafetyVest",Vector3.new(1.85,1.5,.12),CFrame.new(0,0,-.58),Color3.fromRGB(224,176,69),Enum.Material.Fabric)
    elseif role=="BeachWorker" then
        accessory(model,ra,"CleaningCloth",Vector3.new(.7,.15,.65),CFrame.new(0,-1,-.25),Color3.fromRGB(235,220,181),Enum.Material.Fabric)
        accessory(model,torso,"BeachCrewBadge",Vector3.new(.6,.4,.12),CFrame.new(.45,.4,-.59),Color3.fromRGB(199,83,74))
    elseif role=="Busker" and job then
        accessory(model,torso,"GuitarBody",Vector3.new(1.5,1.7,.5),CFrame.new(.2,-.35,-.9),Color3.fromRGB(183,121,65),Enum.Material.Wood,Enum.PartType.Ball)
        accessory(model,torso,"GuitarSoundhole",Vector3.new(.45,.45,.04),CFrame.new(.2,-.1,-1.17),Color3.fromRGB(55,41,32),nil,Enum.PartType.Ball)
        accessory(model,torso,"GuitarNeck",Vector3.new(.35,2.3,.17),CFrame.new(-.3,.9,-.92)*CFrame.Angles(0,0,-.35),Color3.fromRGB(112,74,47),Enum.Material.Wood)
    elseif role=="Gardener" then
        local canGrip=CFrame.new(0,-1.15,-.35)*CFrame.Angles(-1.15,0,0)
        jobTool=accessory(model,ra,"WateringCan",Vector3.new(.9,.85,.7),canGrip,Color3.fromRGB(77,133,123),Enum.Material.Metal)
        accessory(model,ra,"CanSpout",Vector3.new(.2,.2,.9),canGrip*CFrame.new(0,.1,-.65),Color3.fromRGB(77,133,123),Enum.Material.Metal)
        local outlet=Instance.new("Attachment");outlet.Position=Vector3.new(0,.1,-1.1);outlet.Parent=jobTool
        water=Instance.new("ParticleEmitter");water.Name="WaterDrops";water.EmissionDirection=Enum.NormalId.Front;water.Rate=12;water.Lifetime=NumberRange.new(.35,.6);water.Speed=NumberRange.new(1,2);water.Acceleration=Vector3.new(0,-12,0);water.Size=NumberSequence.new(.08);water.Color=ColorSequence.new(Color3.fromRGB(134,213,235));water.Enabled=false;water.Parent=outlet
    elseif role=="Artist" then
        jobTool=accessory(model,ra,"PaintBrush",Vector3.new(.14,1.3,.14),CFrame.new(0,-1.1,-.35),Color3.fromRGB(131,88,61),Enum.Material.Wood)
        accessory(model,ra,"BrushTip",Vector3.new(.19,.3,.19),CFrame.new(0,-1.8,-.35),Color3.fromRGB(64,143,165),Enum.Material.Fabric)
        accessory(model,la,"PaintPalette",Vector3.new(.9,.12,.7),CFrame.new(0,-1,-.3)*CFrame.Angles(-.7,0,0),Color3.fromRGB(190,144,92),Enum.Material.Wood)
    end
    if role == "Vendor" then
        accessory(model, torso, "VendorApron", Vector3.new(1.65, 1.4, 0.14),
            CFrame.new(0, -0.32, -0.61), Color3.fromRGB(222, 215, 188), Enum.Material.Fabric)
    elseif role == "Tourist" then
        accessory(model, torso, "Backpack", Vector3.new(1.4, 1.5, 0.55),
            CFrame.new(0, 0.05, 0.75), Color3.fromRGB(102, 74, 89), Enum.Material.Fabric)
    elseif role == "Fighter" then
        accessory(model, ra, "FighterArmband", Vector3.new(1.08, 0.3, 1.08),
            CFrame.new(0, 0.38, 0), C.gold, Enum.Material.Fabric)
    elseif role == "Commuter" then
        accessory(model, torso, "CrossbodyBag", Vector3.new(1.25, 0.9, 0.35),
            CFrame.new(0.4, -0.5, -0.72), Color3.fromRGB(86, 61, 47), Enum.Material.Fabric)
    end
    local humanoid = Instance.new("Humanoid")
    humanoid.RigType = Enum.HumanoidRigType.R6
    humanoid.HipHeight=0;humanoid.AutoJumpEnabled=false;humanoid.JumpPower=0;humanoid.JumpHeight=0
    humanoid:SetStateEnabled(Enum.HumanoidStateType.Jumping,false)
    humanoid:SetStateEnabled(Enum.HumanoidStateType.Climbing,false)
    humanoid:SetStateEnabled(Enum.HumanoidStateType.FallingDown,false)
    humanoid.MaxHealth, humanoid.Health = Config.BotMaxHealth, Config.BotMaxHealth
    humanoid.WalkSpeed = avatarRng:NextInteger(7, 11)
    humanoid.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
    humanoid.Parent = model
    model.PrimaryPart = root
    if RunService:IsRunning() then root:SetNetworkOwner(nil) end
    local nameLabel = billboard(head, displayName .. "  " .. Config.BotMaxHealth .. "/" .. Config.BotMaxHealth, Vector3.new(0, 2.5, 0))
    local speech = billboard(head, "", Vector3.new(0, 4.4, 0), 185)
    nameLabel.Parent.MaxDistance = 18
    speech.Parent.MaxDistance = 24
    speech.Visible = false
    speech.BackgroundColor3 = Color3.fromRGB(244, 237, 211)
    speech.TextColor3 = C.dark
    local bot = {id = "Bot" .. index, name = displayName, role = role, model = model, root = root, humanoid = humanoid,
        health = Config.BotMaxHealth, alive = true, label = nameLabel, speech = speech, questIds=job and job.quests or index==4 and {"sprint"} or index==5 and {"crowd"} or index==6 and {"dodge","arena"} or nil, job=job, jobTool=jobTool, water=water, carryParts=carryParts, jobStep=0,
        start = home, lastGrounded=home, roamRadius = role == "Commuter" and 200 or 125,
        joints = {ls, rs, lh, rh}, lastGreeting = -1000}
    for _, limb in ipairs(bot.joints) do limb:SetAttribute("RestPose", limb.C0) end
    table.insert(World.Bots, bot)
    model:SetAttribute("AnimationSeed",index);Collection:AddTag(model,"CityResident")
    if RunService:IsRunning() then
        task.spawn(function()
            task.wait(index * 0.08)
            while model.Parent do
                if bot.alive then
                    if bot.restSeat then
                        task.wait(.2)
                    elseif (bot.reactionUntil or 0) > os.clock() then
                        task.wait(0.5)
                    elseif (bot.socialUntil or 0)>os.clock() then
                        task.wait(.2)
                    elseif job then
                        bot.jobStep=bot.jobStep%#job.stations+1
                        local station=job.stations[bot.jobStep]
                        model:SetAttribute("WorkStep",bot.jobStep)
                        for _,item in ipairs(bot.carryParts) do item.Transparency=bot.jobStep==2 and 0 or 1 end
                        bot.working=false;model:SetAttribute("Activity","Walking to work")
                        roamTo(bot,station.position,true)
                        if bot.alive and (Vector3.new(bot.root.Position.X,station.position.Y,bot.root.Position.Z)-station.position).Magnitude<.8 and (bot.reactionUntil or 0)<=os.clock() and (bot.socialUntil or 0)<=os.clock() then
                            bot.humanoid:MoveTo(bot.root.Position);faceToward(bot,station.lookAt)
                            if role=="Soccer" then
                                bot.practiceCycle=(bot.practiceCycle or 0)+1
                                model:SetAttribute("PracticeRoutine",({"Miss","Trip","OwnGoal"})[(bot.practiceCycle-1)%3+1])
                            end
                            bot.working=true;model:SetAttribute("WorkStarted",workspace:GetServerTimeNow());model:SetAttribute("Activity",station.action or role=="Soccer" and "Practicing missed kicks" or role=="Gardener" and "Watering flowers" or role=="Artist" and "Painting the coast" or "Arranging produce")
                            local untilTime=os.clock()+(role=="Soccer" and 6.5 or rng:NextNumber(5,9))
                            while model.Parent and bot.alive and os.clock()<untilTime and (bot.socialUntil or 0)<=os.clock() and (bot.reactionUntil or 0)<=os.clock() do task.wait(.2) end
                            bot.working=false
                        end
                        task.wait(.3)
                    else
                        local choice = rng:NextNumber()
                        if choice < 0.23 then
                            bot.gestureUntil = os.clock() + rng:NextNumber(1.5, 3.5)
                            if role == "Busker" or role == "Vendor" or rng:NextNumber() < 0.45 then
                                World.Talk(bot)
                            end
                            task.wait(rng:NextNumber(2.5, 5.5))
                        elseif choice < 0.45 and socialize(bot) then
                            task.wait(rng:NextNumber(2.5, 4.5))
                        else
                            local destination, kind = chooseDestination(bot)
                            roamTo(bot, destination)
                            if bot.alive and (destination - bot.root.Position).Magnitude < 13 then
                                if kind=="Rest" and restNearby(bot,destination) then
                                    bot.model:SetAttribute("Activity","Exploring the neighborhood")
                                elseif kind == "Browse" or kind == "Watch" or kind == "Rest" then
                                    bot.gestureUntil = os.clock() + 2.5
                                    task.wait(rng:NextNumber(2, 4))
                                elseif rng:NextNumber() < 0.3 then
                                    task.wait(rng:NextNumber(0.7, 2))
                                end
                            end
                        end
                    end
                else task.wait(0.5) end
            end
        end)
        task.spawn(function()
            task.wait(3 + index % 9)
            while model.Parent do
                if bot.alive then noticePlayers(bot) end
                task.wait(2.5 + index % 4)
            end
        end)
    end
end

local function atmosphere()
    local lighting = game:GetService("Lighting")
    lighting.ClockTime = 16.5
    lighting.Brightness = 3
    lighting.EnvironmentDiffuseScale = 0.65
    lighting.EnvironmentSpecularScale = 0.65
    lighting.GlobalShadows = true
    lighting.ShadowSoftness = 0.35
    local grade = lighting:FindFirstChild("CityGrade") or Instance.new("ColorCorrectionEffect")
    grade.Name = "CityGrade"
    grade.Contrast = 0.08
    grade.Saturation = 0.08
    grade.TintColor = Color3.fromRGB(255, 248, 237)
    grade.Parent = lighting
    local haze = lighting:FindFirstChild("CityHaze")
    if not haze then
        haze = Instance.new("Atmosphere")
        haze.Name = "CityHaze"
        haze.Parent = lighting
    end
    haze.Density = 0.17
    haze.Haze = 0.3
    haze.Color = Color3.fromRGB(235, 210, 181)
end


function World.IsInWarZone(position) return Config.InArena(position) end

local function carAt(car,distance)
    local x=-690+distance*car.direction
    if car.direction<0 then x=690-distance end
    return CFrame.new(x,2.05,car.lane)*CFrame.Angles(0,car.direction>0 and 0 or math.pi,0)
end
function World.Build()
    local old=workspace:FindFirstChild("ScreamSimulatorWorld");if old then old:Destroy() end
    table.clear(World.Bots);table.clear(World.Cars);table.clear(seatReservations)
    pcall(function() PhysicsService:RegisterCollisionGroup("Residents") end)
    PhysicsService:CollisionGroupSetCollidable("Residents","Residents",false)
    atmosphere()
    local parent=Instance.new("Model");parent.Name="ScreamSimulatorWorld";parent.Parent=workspace
    local layout=City.Build(parent);World.WalkPoints=layout.walk;World.ActivityPoints=layout.activities;World.SafeSpawn=layout.spawn
    table.clear(World.Seats);for _,item in ipairs(parent:GetDescendants()) do if item:IsA("Seat") then table.insert(World.Seats,item) end end
    local spawn=Instance.new("SpawnLocation");spawn.Name="SafeSpawn";spawn.Size=Vector3.new(7,.2,7);spawn.CFrame=World.SafeSpawn-Vector3.new(0,3,0);spawn.Anchored=true;spawn.Neutral=true;spawn.Duration=0;spawn.Transparency=1;spawn.CanCollide=false;spawn.Parent=parent
    local roles={"Local","Tourist","Vendor","Commuter","Busker","Fighter"}
    -- Cluster residents at destinations; leave roads and building interiors clear.
    local seeds={{-625,205},{-575,205},{-600,185},{-610,265},{-360,180},{-360,260},{-120,-32},{-145,15},{-92,15},{85,-71},{155,-71},{85,7},{155,7},{-240,403},{0,403},{200,403},{420,403},{-540,403}}
    for i=1,20 do local point=layout.walk[((i-1)*29+5)%#layout.walk+1];table.insert(seeds,{point.X,point.Z}) end
    for i,spot in ipairs(seeds) do makeBot(parent,i,spot[1],spot[2],roles[(i-1)%#roles+1]) end
    for i,job in ipairs(layout.jobs or {}) do local point=job.stations[1].position;makeBot(parent,#seeds+i,point.X,point.Z,job.role,job) end
    for i,spec in ipairs({{-368,1,23},{-352,-1,21},{112,1,20},{128,-1,24},{352,1,18},{368,-1,22}}) do
        local m=vehicle(parent,i%2==0 and "Sedan" or "Taxi",i%2==0 and Color3.fromRGB(65+i*15,104,115) or Color3.fromRGB(226,177,64));m.Name="TrafficCar"..i
        local car={model=m,hull=m.CollisionHull,lane=spec[1],direction=spec[2],speed=spec[3],distance=(i-1)*210};m:PivotTo(carAt(car,car.distance));table.insert(World.Cars,car)
    end
    for i,pos in ipairs({{-490,-110},{490,105},{-490,130},{690,120}}) do taxi(parent,pos[1],pos[2],"Sedan",Color3.fromRGB(91+i*22,93,99)) end
    if RunService:IsRunning() then
        task.spawn(function()
            local grounding=0
            while parent.Parent do
                local dt=RunService.Heartbeat:Wait();local now=os.clock();grounding+=dt
                for _,car in ipairs(World.Cars) do
                    local previous=car.model:GetPivot();local travel=math.min(dt,.1)*car.speed;car.distance+=travel
                    local wrapped=car.distance>1380;if wrapped then car.distance-=1380 end
                    local nextFrame=carAt(car,car.distance)
                    if not wrapped and World.OnVehicleSweep then World.OnVehicleSweep(car,previous,nextFrame) end
                    car.model:PivotTo(nextFrame)
                    car.model:SetAttribute("Speed",car.speed)
                end
                local groundParams
                if grounding>=.25 then
                    groundParams=RaycastParams.new();groundParams.FilterType=Enum.RaycastFilterType.Exclude
                    local exclude={}
                    for _,bot in ipairs(World.Bots) do table.insert(exclude,bot.model) end
                    for _,player in ipairs(game.Players:GetPlayers()) do if player.Character then table.insert(exclude,player.Character) end end
                    groundParams.FilterDescendantsInstances=exclude;groundParams.RespectCanCollide=true
                end
                for _,bot in ipairs(World.Bots) do
                    if bot.water then bot.water.Enabled=bot.alive and bot.working==true end
                    if not bot.alive or not bot.root.Parent then continue end
                    local gesture=(bot.gestureUntil or 0)>now
                    if bot.model:GetAttribute("Gesturing")~=gesture then bot.model:SetAttribute("Gesturing",gesture) end
                    if bot.model:GetAttribute("Working")~=(bot.working==true) then bot.model:SetAttribute("Working",bot.working==true) end
                    if grounding>=.25 and not bot.humanoid.SeatPart then
                        local hit=workspace:Raycast(bot.root.Position+Vector3.new(0,2,0),Vector3.new(0,-20,0),groundParams)
                        local gap=hit and bot.root.Position.Y-hit.Position.Y or 99
                        if gap>5 or gap<1.5 or bot.root.Position.Y>8 or bot.root.Position.Y< -3 then
                            bot.airSince=bot.airSince or now
                            if now-bot.airSince>.45 then
                                bot.model:PivotTo(CFrame.new(bot.lastGrounded or bot.start));bot.root.AssemblyLinearVelocity=Vector3.zero;bot.root.AssemblyAngularVelocity=Vector3.zero;bot.humanoid:MoveTo(bot.root.Position);bot.airSince=nil
                            end
                        else bot.airSince=nil;bot.lastGrounded=bot.root.Position end
                    end
                end
                if grounding>=.25 then grounding=0 end
            end
        end)
    end
    return parent
end
function World.UpdateBot(bot)
    stopWalking(bot);bot.model:SetAttribute("Working",false)
    bot.label.Text=bot.alive and (bot.name.."  "..bot.health.."/"..Config.BotMaxHealth) or "RECOVERING"
    if bot.alive then
        bot.humanoid.Health=bot.health
        if bot.health==Config.BotMaxHealth then
            bot.root.Anchored=false;bot.model:PivotTo(CFrame.new(bot.start));bot.root.AssemblyLinearVelocity=Vector3.zero;bot.root:SetNetworkOwner(nil)
        end
    else
        bot.humanoid:MoveTo(bot.root.Position);bot.root.Anchored=true;bot.model:PivotTo(CFrame.new(bot.start-Vector3.new(0,100,0)));bot.speech.Visible=false
    end
end
return World
