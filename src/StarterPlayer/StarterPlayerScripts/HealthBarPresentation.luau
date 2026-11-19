-- Local presentation only. Boss values are server attributes; player bars stay native.
local Presentation={}
local function finite(value)
 return type(value)=="number" and value==value and math.abs(value)<math.huge
end
function Presentation.Value(health,maximum,state)
 if not finite(health) or not finite(maximum) or maximum<=0 or health<=0 or state=="Defeated" then return nil end
 health=math.clamp(health,0,maximum)
 return health/maximum
end
local function disconnect(list)
 for _,connection in ipairs(list) do connection:Disconnect() end
 table.clear(list)
end
-- Native renderer owns actual remote health, distance, team and name occlusion.
-- Do not derive remote ratios from Humanoid.Health (API marks it Not Replicated).
function Presentation.NativePlayer(humanoid)
 local original=humanoid.HealthDisplayType
 local alive=true
 local function policy()
  return humanoid:GetState()==Enum.HumanoidStateType.Dead and Enum.HumanoidHealthDisplayType.AlwaysOff or Enum.HumanoidHealthDisplayType.AlwaysOn
 end
 local owned=policy();humanoid.HealthDisplayType=owned
 local function stateChanged()
  if not alive then return end
  local nextPolicy=policy()
  if nextPolicy~=owned then owned=nextPolicy;humanoid.HealthDisplayType=owned end
 end
 local died=humanoid.Died:Connect(stateChanged)
 local state=humanoid.StateChanged:Connect(stateChanged)
 return {Destroy=function()
  if not alive then return end;alive=false;died:Disconnect();state:Disconnect()
  -- Never restore over a later independent policy owner.
  pcall(function()if humanoid.HealthDisplayType==owned then humanoid.HealthDisplayType=original end end)
 end}
end
function Presentation.Boss(model,board,label)
 if board:FindFirstChild("LocalBossHealth") then return nil end
 local alive=true
 local originalSize,originalLabelSize=board.Size,label.Size
 local originalTop,originalDistance=board.AlwaysOnTop,board.MaxDistance
 local ownedSize=UDim2.fromOffset(296,46)
 local ownedLabelSize=UDim2.new(1,-16,0,32)
 board.Size=ownedSize;label.Size=ownedLabelSize
 board.AlwaysOnTop=false;board.MaxDistance=math.min(originalDistance>0 and originalDistance or 90,90)
 local ownedDistance=board.MaxDistance
 local row=Instance.new("Frame");row.Name="LocalBossHealth";row.BackgroundTransparency=1
 row.Size=UDim2.new(1,-16,0,12);row.Position=UDim2.fromOffset(8,32);row.Active=false;row.Selectable=false;row.Interactable=false;row.Parent=board
 local track=Instance.new("Frame");track.Name="Track";track.BorderSizePixel=0
 track.BackgroundColor3=Color3.fromRGB(6,10,18);track.BackgroundTransparency=.12
 track.Size=UDim2.fromOffset(130,5);track.Position=UDim2.new(.5,-65,.5,-2)
 track.Active=false;track.Selectable=false;track.Interactable=false;track.Parent=row
 local fill=Instance.new("Frame");fill.Name="Fill";fill.BorderSizePixel=0
 fill.BackgroundColor3=label.TextColor3;fill.BackgroundTransparency=0
 fill.Size=UDim2.fromScale(1,1);fill.Active=false;fill.Selectable=false;fill.Interactable=false;fill.Parent=track
 local lastRatio,lastVisible
 local function refresh()
  if not alive then return end
  local ratio=Presentation.Value(model:GetAttribute("BossHealth"),model:GetAttribute("BossMaxHealth"),model:GetAttribute("BossState"))
  local visible=ratio~=nil
  if visible~=lastVisible then row.Visible=visible;lastVisible=visible end
  if visible then
   if ratio~=lastRatio then fill.Size=UDim2.fromScale(ratio,1);lastRatio=ratio end
  end
 end
 local connections={}
 for _,name in ipairs({"BossHealth","BossMaxHealth","BossState"}) do
  table.insert(connections,model:GetAttributeChangedSignal(name):Connect(refresh))
 end
 refresh()
 return {Destroy=function()
  if not alive then return end;alive=false;disconnect(connections);row:Destroy()
  pcall(function()
   if board.Size==ownedSize then board.Size=originalSize end
   if board.AlwaysOnTop==false then board.AlwaysOnTop=originalTop end
   if board.MaxDistance==ownedDistance then board.MaxDistance=originalDistance end
  end)
  pcall(function()if label.Size==ownedLabelSize then label.Size=originalLabelSize end end)
 end}
end
-- Event-driven binding: no WaitForChild task may install a stale respawn observer.
function Presentation.Players(players,localPlayer,world)
 local records,connections={},{}
 local stopped=false
 local function remove(player)
  local record=records[player];if not record then return end
  if record.native then record.native:Destroy() end
  disconnect(record.characterConnections);disconnect(record.connections);records[player]=nil
 end
 local function add(player)
  if stopped or player==localPlayer or records[player] then return end
  local record={connections={},characterConnections={}};records[player]=record
  local function character(character)
   if record.native then record.native:Destroy();record.native=nil end
   disconnect(record.characterConnections);record.character=character;record.humanoid=nil
   if not character then return end
   local function reconcile()
    if stopped or record.character~=character then return end
    local humanoid=character:IsDescendantOf(world) and character:FindFirstChildOfClass("Humanoid") or nil
    if humanoid==record.humanoid then return end
    if record.native then record.native:Destroy();record.native=nil end
    record.humanoid=humanoid
    if humanoid then record.native=Presentation.NativePlayer(humanoid) end
   end
   for _,signal in ipairs({character.ChildAdded,character.ChildRemoved,character.AncestryChanged}) do
    table.insert(record.characterConnections,signal:Connect(reconcile))
   end
   reconcile()
  end
  table.insert(record.connections,player.CharacterAdded:Connect(character))
  table.insert(record.connections,player.CharacterRemoving:Connect(function(c)if record.character==c then character(nil) end end))
  character(player.Character)
 end
 table.insert(connections,players.PlayerAdded:Connect(add))
 table.insert(connections,players.PlayerRemoving:Connect(remove))
 for _,player in ipairs(players:GetPlayers()) do add(player) end
 return {Destroy=function()
  if stopped then return end;stopped=true;disconnect(connections)
  local pending={};for player in pairs(records) do table.insert(pending,player) end
  for _,player in ipairs(pending) do remove(player) end
 end}
end
return Presentation
