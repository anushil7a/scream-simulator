-- Disposable Academy course only. Held input is a test substitute, NOT microphone transport.
local RunService = game:GetService("RunService")
if not RunService:IsStudio() or game.GameId ~= 0 or game.PlaceId ~= 0 then return end
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local GuiService = game:GetService("GuiService")
local Workspace = game:GetService("Workspace")
local Debris = game:GetService("Debris")
local player = Players.LocalPlayer
local channel = ReplicatedStorage:WaitForChild("AcademyRoutePreview", 15)
if not channel or not channel:IsA("Folder") then warn("Academy preview channel unavailable"); return end
local inputRemote = channel:WaitForChild("BeamInput", 15)
local fxRemote = channel:WaitForChild("BeamFx", 15)
local toolsRemote = channel:WaitForChild("TestTools", 15)
if not toolsRemote or not toolsRemote:IsA("RemoteEvent") or not inputRemote or not inputRemote:IsA("RemoteEvent") or not fxRemote or not fxRemote:IsA("RemoteEvent") then
 warn("Academy preview remotes unavailable"); return
end
local gui = Instance.new("ScreenGui")
gui.Name = "AcademyRoutePreviewUI"
gui.ResetOnSpawn = false
gui.IgnoreGuiInset = true
gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
gui.Parent = player:WaitForChild("PlayerGui")
local connections = {}
local function connect(signal, callback)
 local connection = signal:Connect(callback)
 table.insert(connections, connection)
 return connection
end
local function corner(parent)
 local rounding = Instance.new("UICorner"); rounding.CornerRadius = UDim.new(0, 10); rounding.Parent = parent
end
local panel = Instance.new("Frame")
panel.Name = "AcademyCourse"
panel.AnchorPoint = Vector2.new(.5, 1)
panel.BackgroundColor3 = Color3.fromRGB(19, 31, 49)
panel.BackgroundTransparency = .08
panel.Parent = gui
corner(panel)
local function text(name, y, height, size)
 local label = Instance.new("TextLabel")
 label.Name = name; label.Position = UDim2.new(0, 12, 0, y); label.Size = UDim2.new(1, -24, 0, height)
 label.BackgroundTransparency = 1; label.TextColor3 = Color3.fromRGB(239, 246, 255)
 label.Font = Enum.Font.Gotham; label.TextSize = size; label.TextWrapped = true
 label.TextXAlignment = Enum.TextXAlignment.Left; label.Parent = panel
 return label
end
local heading = text("Course", 8, 22, 15)
local objective = text("Objective", 32, 38, 14)
objective.TextTruncate = Enum.TextTruncate.AtEnd
local routeText = text("SelectedGuide", 72, 32, 12)
routeText.TextTruncate = Enum.TextTruncate.AtEnd
local disclaimer = text("LocalOnly", 108, 30, 11)
disclaimer.TextColor3 = Color3.fromRGB(181, 199, 215)
disclaimer.Text = "LOCAL TEST • Progress resets when this Studio session ends. Held beams only, not your microphone."
local function button(name, x, width, caption)
 local b = Instance.new("TextButton")
 b.Name = name; b.Position = UDim2.new(x, 5, 1, -49); b.Size = UDim2.new(width, -10, 0, 42)
 b.BackgroundColor3 = Color3.fromRGB(39, 78, 103); b.TextColor3 = Color3.new(1, 1, 1)
 b.Font = Enum.Font.GothamBold; b.TextSize = 12; b.TextWrapped = true; b.Text = caption
 b.Parent = panel; corner(b); return b
end
local guideButton = button("ChooseGuide", 0, .4, "Choose guide")
local clearButton = button("ClearGuide", .4, .23, "Clear guide")
local holdButton = button("HoldBeam", .63, .37, "HOLD BEAM\nMouse / R2")
local reticle = Instance.new("TextLabel")
reticle.Name = "CenterAim"; reticle.AnchorPoint = Vector2.new(.5, .5)
reticle.Position = UDim2.fromScale(.5, .5); reticle.Size = UDim2.fromOffset(22, 22)
reticle.BackgroundTransparency = 1; reticle.Text = "+"; reticle.Font = Enum.Font.GothamBold
reticle.TextSize = 24; reticle.TextColor3 = Color3.fromRGB(157, 237, 255); reticle.Parent = gui
local navigation
local module = script.Parent:FindFirstChild("NavigationGuide")
if module and module:IsA("ModuleScript") then
 local ok, result = pcall(function() return require(module).new(gui) end)
 if ok then navigation = result else warn("Academy guide unavailable: " .. tostring(result)) end
end
local alive, held, heldInput, sentAt = true, false, nil, -math.huge
local testUntil, vertical = nil, 0
local toolsPanel
local windowFocused=true
local selected, selectedLabel
local function finiteVector(v)
 return typeof(v) == "Vector3" and v.X == v.X and v.Y == v.Y and v.Z == v.Z
  and math.abs(v.X) < 1e7 and math.abs(v.Y) < 1e7 and math.abs(v.Z) < 1e7
end
local effects
local aimParams = RaycastParams.new()
aimParams.FilterType = Enum.RaycastFilterType.Exclude
local targetCache, cacheAt
local function aimDirection()
 local camera = Workspace.CurrentCamera
 if not camera then return Vector3.new(0, 0, -1) end
 local size = camera.ViewportSize
 local ray = camera:ViewportPointToRay(size.X / 2, size.Y / 2)
 local character = player.Character
 local root = character and character:FindFirstChild("HumanoidRootPart")
 if not root then return ray.Direction.Unit end
 local origin = root.Position + Vector3.new(0, 1.5, 0)
 aimParams.FilterDescendantsInstances = {character, effects or character}
 local worldHit = Workspace:Raycast(ray.Origin, ray.Direction * 45, aimParams)
 local point = worldHit and worldHit.Position or ray.Origin + ray.Direction * 45
 -- Query-disabled targets require bounded reticle geometry, never an automatic lock-on.
 -- Converge from the actual server muzzle to the center under the crosshair.
 local stage = player:GetAttribute("AcademyStage")
 local target, radius
 if stage == "Train" then
  if not cacheAt or os.clock() - cacheAt > .5 then
   cacheAt = os.clock(); targetCache = Workspace:FindFirstChild("AcademyTrainingResonator", true)
  end
  target = targetCache; radius = 3.3
 elseif stage == "Fight" then
  local world = Workspace:FindFirstChild("ScreamSimulatorWorld")
  local bosses = world and world:FindFirstChild("BossEncounters")
  local boss = bosses and bosses:FindFirstChild("metronome")
  target = boss and boss:FindFirstChild("Core"); radius = 4
 end
 if target and target:IsA("BasePart") and target:IsDescendantOf(Workspace) then
  local offset = target.Position - ray.Origin
  local t = offset:Dot(ray.Direction)
  if t > 0 and t <= 80 and (offset - ray.Direction * t).Magnitude <= radius then
   local obstruction = Workspace:Raycast(ray.Origin, offset, aimParams)
   local muzzleOffset = target.Position - origin
   local muzzleBlock = Workspace:Raycast(origin, muzzleOffset, aimParams)
   if (not obstruction or obstruction.Distance >= offset.Magnitude - .15)
    and (not muzzleBlock or muzzleBlock.Distance >= muzzleOffset.Magnitude - .15) then point = target.Position end
  end
 end
 local delta = point - origin
 return delta.Magnitude > .01 and delta.Unit or ray.Direction.Unit
end
local function stopBeam()
 if held then inputRemote:FireServer(false, aimDirection()) end
 held = false; heldInput = nil; testUntil = nil
 holdButton.BackgroundColor3 = Color3.fromRGB(39, 78, 103)
end
local function startBeam(input,singleTest)
 local c=player.Character;local h=c and c:FindFirstChildOfClass("Humanoid")
 if not h or h.Health<=0 then return end
 if not alive or not windowFocused or held or player:GetAttribute("TestFlight") or (player:GetAttribute("AcademyBeamPercent") or 100)<=0 or GuiService.MenuIsOpen or UserInputService:GetFocusedTextBox() then return end
 held = true; heldInput = input; sentAt = os.clock()
 if toolsPanel then toolsPanel.Visible=false end
 holdButton.BackgroundColor3 = Color3.fromRGB(20, 128, 149)
 inputRemote:FireServer(true, aimDirection(),singleTest and "TestStart" or nil)
 return true
end
connect(holdButton.InputBegan, function(input)
 if input.UserInputType == Enum.UserInputType.Touch or input.UserInputType == Enum.UserInputType.MouseButton1 then startBeam(input) end
end)
connect(UserInputService.InputBegan, function(input, processed)
 if processed then return end
 if input.UserInputType == Enum.UserInputType.MouseButton1 or input.KeyCode == Enum.KeyCode.ButtonR2 or input.KeyCode == Enum.KeyCode.B then startBeam(input) end
end)
local function ownsBeamInput(input)
 if not heldInput then return false end
 if input.UserInputType == Enum.UserInputType.Touch then return input == heldInput end
 return input.UserInputType == heldInput.UserInputType and input.KeyCode == heldInput.KeyCode
end
connect(UserInputService.InputEnded, function(input)
 if ownsBeamInput(input) then stopBeam() end
end)
connect(UserInputService.InputChanged, function(input)
 if input.KeyCode == Enum.KeyCode.ButtonR2 and ownsBeamInput(input) and input.Position.Z < .1 then stopBeam() end
end)
connect(UserInputService.WindowFocusReleased, stopBeam)
connect(UserInputService.TextBoxFocused, stopBeam)
connect(UserInputService.GamepadDisconnected, stopBeam)
connect(GuiService.MenuOpened, stopBeam)
connect(player.CharacterRemoving, stopBeam)
-- Explicitly opened local tools. Values are server-owned, temporary and silent.
local toolsToggle = Instance.new("TextButton")
toolsToggle.Name="TestToolsToggle";toolsToggle.AnchorPoint=Vector2.new(1,0)
toolsToggle.Position=UDim2.new(1,-12,0,48);toolsToggle.Size=UDim2.fromOffset(172,40)
toolsToggle.BackgroundColor3=Color3.fromRGB(39,78,103);toolsToggle.TextColor3=Color3.new(1,1,1)
toolsToggle.Text="Test Tools";toolsToggle.Font=Enum.Font.GothamBold;toolsToggle.TextSize=13;toolsToggle.Parent=gui;corner(toolsToggle)
toolsPanel=Instance.new("ScrollingFrame")
toolsPanel.CanvasSize=UDim2.fromOffset(0,284);toolsPanel.ScrollBarThickness=5
toolsPanel.ScrollingDirection=Enum.ScrollingDirection.Y
toolsPanel.Name="LocalTestTools";toolsPanel.AnchorPoint=Vector2.new(1,0)
toolsPanel.Position=UDim2.new(1,-12,0,92);toolsPanel.Size=UDim2.fromOffset(252,284)
toolsPanel.BackgroundColor3=Color3.fromRGB(19,31,49);toolsPanel.Visible=false;toolsPanel.Parent=gui;corner(toolsPanel)
local function toolButton(name,x,y,w,label)
 local b=Instance.new("TextButton");b.Name=name;b.Position=UDim2.fromOffset(x,y);b.Size=UDim2.fromOffset(w,40)
 b.Text=label;b.BackgroundColor3=Color3.fromRGB(39,78,103);b.TextColor3=Color3.new(1,1,1)
 b.Font=Enum.Font.GothamBold;b.TextSize=12;b.TextWrapped=true;b.Parent=toolsPanel;corner(b);return b
end
local toolLabel=Instance.new("TextLabel")
toolLabel.Position=UDim2.fromOffset(8,4);toolLabel.Size=UDim2.new(1,-16,0,38);toolLabel.BackgroundTransparency=1
 toolLabel.Text="LOCAL • silent Beam Test\nPower 0–100% • no microphone";toolLabel.TextColor3=Color3.new(1,1,1);toolLabel.TextSize=12;toolLabel.Parent=toolsPanel
local minus=toolButton("PowerDown",8,46,42,"−")
local powerBox=Instance.new("TextBox");powerBox.Name="BeamPowerPercent";powerBox.Position=UDim2.fromOffset(56,46)
powerBox.Size=UDim2.fromOffset(140,40);powerBox.Text="100";powerBox.ClearTextOnFocus=false
powerBox.BackgroundColor3=Color3.fromRGB(30,53,70);powerBox.TextColor3=Color3.new(1,1,1);powerBox.TextSize=16;powerBox.Parent=toolsPanel;corner(powerBox)
local plus=toolButton("PowerUp",202,46,42,"+")
local fireTest=toolButton("FireTest",8,92,236,"Fire test • once, up to 4s")
local flyButton=toolButton("FlyToggle",8,138,236,"Fly on")
local up=toolButton("FlyUp",8,184,115,"Fly up")
local down=toolButton("FlyDown",129,184,115,"Fly down")
local flightHint=Instance.new("TextLabel");flightHint.Position=UDim2.fromOffset(8,228);flightHint.Size=UDim2.new(1,-16,0,50)
flightHint.BackgroundTransparency=1;flightHint.TextColor3=Color3.fromRGB(181,199,215);flightHint.TextSize=11;flightHint.TextWrapped=true
flightHint.Text="Fly: WASD / joystick, Space / Ctrl. Home or Fly off returns to start. Beam: hold B / mouse / R2.";flightHint.Parent=toolsPanel
local function setPower(n)
 stopBeam()
 if type(n)~="number" or n~=n or math.abs(n)==math.huge then powerBox.Text=tostring(player:GetAttribute("AcademyBeamPercent") or 100);return end
 n=math.clamp(math.floor(n+.5),0,100);powerBox.Text=tostring(n)
 if n~=(player:GetAttribute("AcademyBeamPercent") or 100) then toolsRemote:FireServer("BeamPower",n) end
end
connect(powerBox.FocusLost,function() setPower(tonumber(powerBox.Text)) end)
connect(minus.Activated,function() setPower((tonumber(powerBox.Text) or 100)-10) end)
connect(plus.Activated,function() setPower((tonumber(powerBox.Text) or 100)+10) end)
connect(toolsToggle.Activated,function() stopBeam();toolsPanel.Visible=not toolsPanel.Visible end)
connect(fireTest.Activated,function()
 if testUntil then stopBeam();return end
 -- A test click is never queued behind cooldown or an unknown server status.
 if player:GetAttribute("AcademyCharge")~=0 then return end
 if startBeam(nil,true) then testUntil=os.clock()+4 end -- one cast only; no auto-repeat after cooldown
end)
connect(flyButton.Activated,function()
 stopBeam();vertical=0;toolsRemote:FireServer(player:GetAttribute("TestFlight") and "FlyOff" or "FlyOn")
end)
connect(up.Activated,function() vertical=vertical==1 and 0 or 1 end)
connect(down.Activated,function() vertical=vertical==-1 and 0 or -1 end)
local function hover()
 vertical=0
 if player:GetAttribute("TestFlight") then toolsRemote:FireServer("FlightInput",{x=0,y=0,z=0}) end
end
connect(UserInputService.WindowFocusReleased,function() windowFocused=false;hover() end)
connect(UserInputService.WindowFocused,function() windowFocused=true end)
connect(UserInputService.TextBoxFocused,hover)
connect(GuiService.MenuOpened,hover)
connect(player.CharacterRemoving,hover)
connect(player:GetAttributeChangedSignal("TestFlight"),function() stopBeam();vertical=0 end)
connect(UserInputService.InputBegan,function(input,processed)
 if not processed and input.KeyCode==Enum.KeyCode.Home then stopBeam();vertical=0;toolsRemote:FireServer("FlyOff") end
end)
local flightSent=-math.huge
local function flightInput(now)
 if not player:GetAttribute("TestFlight") or now-flightSent<.1 then return end
 flightSent=now
 local x,y,z=0,0,0
 if windowFocused and not GuiService.MenuIsOpen and not UserInputService:GetFocusedTextBox() then
  local function key(k) return UserInputService:IsKeyDown(k) and 1 or 0 end
  x=key(Enum.KeyCode.D)-key(Enum.KeyCode.A);z=key(Enum.KeyCode.W)-key(Enum.KeyCode.S)
  y=key(Enum.KeyCode.Space)-key(Enum.KeyCode.LeftControl)
  if UserInputService.TouchEnabled then
   y=vertical
   local c=player.Character;local h=c and c:FindFirstChildOfClass("Humanoid");local r=c and c:FindFirstChild("HumanoidRootPart")
   if h and r then
    local forward=Vector3.new(r.CFrame.LookVector.X,0,r.CFrame.LookVector.Z)
    if forward.Magnitude>.001 then
     forward=forward.Unit;local right=Vector3.new(-forward.Z,0,forward.X)
     local function axis(n) return n>.2 and 1 or n<-.2 and -1 or 0 end
     x=axis(h.MoveDirection:Dot(right));z=axis(h.MoveDirection:Dot(forward))
    end
   end
  end
 end
 toolsRemote:FireServer("FlightInput",{x=x,y=y,z=z})
end
local function destinationForStage()
 local stage = player:GetAttribute("AcademyStage")
 if stage == "Guide" or stage == "Fight" then return "AcademyMetronomeEntry", "Whispering Metronome • Academy course" end
 if stage == "Gear" or stage == "Complete" then return "AcademyGear", "Academy starter gear" end
 return nil, nil
end
connect(guideButton.Activated, function()
 stopBeam()
 local name, label = destinationForStage()
 local value = name and channel:FindFirstChild(name)
 if not value or not value:IsA("Vector3Value") or not finiteVector(value.Value) then
  routeText.Text = "Guide unavailable. Wait for the course destination."; return
 end
 selected = value.Value; selectedLabel = label
 if navigation then navigation:SetTarget({position = selected, label = selectedLabel}) end
end)
connect(clearButton.Activated, function()
 stopBeam(); selected = nil; selectedLabel = nil
 if navigation then navigation:Clear() end
 routeText.Text = "No guide selected. Choosing a guide never moves your character."
end)
local stageCopy = {
 Train = "Train: aim at the Academy practice target. Hold mouse / R2 / HOLD BEAM.",
 Meet = "Meet: approach the Academy mentor and use the nearby prompt.",
 Guide = "Guide: choose a guide to Whispering Metronome, then walk to the course entry.",
 Fight = "Fight: hold your beam on Whispering Metronome. Move clear of its warnings.",
 Gear = "Gear: approach Academy starter gear and use its prompt to equip.",
 Complete = "Course complete! Explore the Academy. This local progress is temporary.",
}
effects = Instance.new("Folder"); effects.Name = "LocalAcademyBeamFlashes"; effects.Parent = Workspace
local effectCount = 0
connect(fxRemote.OnClientEvent, function(origin, endpoint, power)
 if type(power)~="number" or power~=power or power<=0 or power>1 or player:GetAttribute("TestFlight") then return end
 if not alive or effectCount >= 12 or not finiteVector(origin) or not finiteVector(endpoint) then return end
 local length = (endpoint - origin).Magnitude
 if length < .05 or length > 250 then return end
 effectCount += 1
 local flash = Instance.new("Part")
 flash.Name = "BeamFlash"; flash.Anchored = true; flash.CanCollide = false; flash.CanTouch = false; flash.CanQuery = false
 flash.CastShadow = false; flash.Material = Enum.Material.Neon; flash.Color = Color3.fromRGB(108, 224, 255)
 flash.Transparency = .25; flash.Size = Vector3.new(.08+.22*power, .08+.22*power, length)
 flash.CFrame = CFrame.lookAt((origin + endpoint) / 2, endpoint); flash.Parent = effects
 Debris:AddItem(flash, .12)
 task.delay(.14, function() effectCount = math.max(0, effectCount - 1) end)
end)
local rayParams = RaycastParams.new(); rayParams.FilterType = Enum.RaycastFilterType.Exclude
rayParams.RespectCanCollide = true
local updateAt = -math.huge
connect(RunService.Heartbeat, function()
 if not alive then return end
 local now = os.clock()
 flightInput(now)
 if testUntil and (now>=testUntil or (player:GetAttribute("AcademyCharge") or -1)<0) then stopBeam() end
 if held then
  local c=player.Character;local h=c and c:FindFirstChildOfClass("Humanoid")
  if not h or h.Health<=0 or not windowFocused or GuiService.MenuIsOpen or UserInputService:GetFocusedTextBox() or not player.Character or player:GetAttribute("TestFlight") or (player:GetAttribute("AcademyBeamPercent") or 100)<=0 then stopBeam()
  elseif now - sentAt >= .12 then sentAt = now; inputRemote:FireServer(true, aimDirection(),testUntil and "TestPulse" or nil) end
 end
 if now - updateAt < .15 then return end
 updateAt = now
 local camera = Workspace.CurrentCamera
 local viewport = camera and camera.ViewportSize or Vector2.new(800, 600)
 local touch = UserInputService.TouchEnabled
 -- Right-side tools remain clear of the left course/joystick in landscape.
 toolsPanel.Size=UDim2.fromOffset(math.min(252,viewport.X-24),math.min(284,math.max(100,viewport.Y-104)))
 if viewport.X<600 and viewport.Y>viewport.X then
  -- Keep the entire open tools panel above the center reticle in portrait.
  toolsPanel.Size=UDim2.fromOffset(math.min(252,viewport.X-24),math.max(80,math.min(284,viewport.Y/2-116)))
 end
 toolsPanel.Position=UDim2.new(1,-12,0,92)
 flyButton.Text=player:GetAttribute("TestFlight") and "Fly off • return to start (Home)" or "Fly on"
 fireTest.Text=testUntil and "Stop test" or "Fire test • once, up to 4s"
 up.Text=vertical==1 and "Up • STOP" or "Fly up";down.Text=vertical==-1 and "Down • STOP" or "Fly down"
 up.Visible=player:GetAttribute("TestFlight")==true;down.Visible=up.Visible
 panel.Size = UDim2.fromOffset(math.max(230, math.min(620, viewport.X - (touch and 36 or 32))), 193)
 if touch and viewport.Y < 500 then
  -- Short landscape: upper-left compact column leaves center reticle and bottom sticks free.
  panel.Size = UDim2.fromOffset(math.max(180, math.min(290, viewport.X * .38, viewport.X / 2 - 36)), 193)
  panel.AnchorPoint = Vector2.new(0, 0); panel.Position = UDim2.fromOffset(12, 44)
 else
  panel.AnchorPoint = Vector2.new(.5, 1)
  panel.Position = UDim2.new(.5, 0, 1, -(touch and 180 or 24))
 end
 if not UserInputService:GetFocusedTextBox() then powerBox.Text=tostring(player:GetAttribute("AcademyBeamPercent") or 100) end
 local narrow = panel.AbsoluteSize.X < 450
 heading.TextSize = narrow and 11 or 15
 objective.TextSize = narrow and 11 or 14
 routeText.TextSize = narrow and 10 or 12
 disclaimer.TextSize = narrow and 10 or 11
 holdButton.Text = touch and "HOLD BEAM\nAim center +" or "HOLD BEAM\nMouse / R2"
 local stage = player:GetAttribute("AcademyStage") or "Train"
 local coins = player:GetAttribute("AcademyCoins") or 0
 local level = player:GetAttribute("AcademyLevel") or 1
 local charge = player:GetAttribute("AcademyCharge")
 heading.Text = string.format("ACADEMY COURSE • Lv %s • %s coins%s", tostring(level), tostring(coins), type(charge) == "number" and (charge < 0 and string.format(" • Cooldown %.1fs", -charge) or charge > 0 and string.format(" • Beam %.1fs", charge) or " • Ready") or "")
 local notice = player:GetAttribute("AcademyNotice")
 objective.Text = (type(notice) == "string" and notice ~= "") and notice or stageCopy[stage] or "Waiting for Academy course…"
 local nextName = destinationForStage()
 guideButton.Visible = nextName ~= nil
 guideButton.Text = (stage == "Gear" or stage == "Complete") and "Guide: gear" or "Guide: Metronome"
 clearButton.Visible = selected ~= nil
 if not selected then
  routeText.Text = "No guide selected. Choose one when ready; walk there yourself."
 else
  local character = player.Character
  local root = character and character:FindFirstChild("HumanoidRootPart")
  rayParams.FilterDescendantsInstances = {effects, character or effects}
  local streamed = Workspace:Raycast(selected + Vector3.new(0, 12, 0), Vector3.new(0, -32, 0), rayParams) ~= nil
  if navigation then navigation:Step(root, now, streamed and not GuiService.MenuIsOpen) end
  local status, distance, bearing
  if navigation then status, distance, bearing = navigation:GetStatus() end
  if root then distance = (selected - root.Position).Magnitude end
  status = not streamed and "Destination not streamed; approach to load route" or status or "Markers unavailable; distance only"
  routeText.Text = string.format("%s • %s%s%s", selectedLabel, status, distance and string.format(" • %.0f studs", distance) or "", bearing and (" " .. bearing) or "")
 end
end)
connect(gui.Destroying, function()
 stopBeam(); hover();toolsRemote:FireServer("FlyOff"); alive = false
 for _, connection in connections do connection:Disconnect() end
 if navigation then navigation:Destroy() end
 effects:Destroy()
end)
connect(script.Destroying, function() if gui.Parent then gui:Destroy() end end)
