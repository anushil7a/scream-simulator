-- Disposable Studio traversal only: no progression systems, live services or writes.
local Run=game:GetService("RunService")
if not Run:IsStudio() or game.GameId~=0 or game.PlaceId~=0 then return end
local Players=game:GetService("Players")
local Lighting=game:GetService("Lighting")
Players.CharacterAutoLoads=false
local make=require(script.Parent.OverworldSpecs)
local builder,groupNames,layout=make()
local scale=1
local academyScale=script.Parent:FindFirstChild("AcademyWorldScale")
if academyScale then
 local transform=require(academyScale)
 scale=transform.Factor
 layout=transform.Apply(builder,layout)
end
local world=Instance.new("Folder");world.Name="Map10V21_Overworld"
local groups=builder:Build(world,groupNames)

Lighting.ClockTime=14.5;Lighting.Brightness=2.5
Lighting.Ambient=Color3.fromRGB(126,126,133);Lighting.OutdoorAmbient=Color3.fromRGB(133,143,151)
Lighting.EnvironmentDiffuseScale=.4;Lighting.EnvironmentSpecularScale=.52
local atmosphere=Instance.new("Atmosphere")
atmosphere.Density=.18;atmosphere.Haze=.8;atmosphere.Color=Color3.fromRGB(188,218,230)
atmosphere.Decay=Color3.fromRGB(134,165,193);atmosphere.Parent=Lighting
local bloom=Instance.new("BloomEffect")
bloom.Name="LandmarkBloom";bloom.Intensity=.17;bloom.Threshold=2.7;bloom.Size=20;bloom.Parent=Lighting

local spawn=Instance.new("SpawnLocation")
spawn.Name="AcademyPreviewSpawn";spawn.Transparency=1;spawn.Size=Vector3.new(8,.4,8)
spawn.Anchored=true;spawn.CanCollide=false;spawn.CanQuery=false;spawn.CanTouch=false;spawn.Neutral=true;spawn.Duration=0
local spawnPosition=Vector3.new(table.unpack(layout.districts["01"].center))+Vector3.new(0,.2,0)
spawn.CFrame=CFrame.lookAt(spawnPosition,spawnPosition-Vector3.zAxis)
spawn.Parent=groups["01"]
local trail=Instance.new("Folder")
trail.Name="NativeReviewMarkers";trail.Parent=world
local function marker(id,p)
 local v=Instance.new("Vector3Value");v.Name=id;v.Value=Vector3.new(table.unpack(p));v.Parent=trail
end
for id,zone in pairs(layout.districts) do marker("District_"..id,zone.center) end
for id,link in pairs(layout.worldLinks) do
 for i,p in ipairs(link) do marker("Link_"..id.."_"..i,p) end
end
-- Gate labels are local wayfinding, not invisible physical panels.
local function label(parent,word,p,size,distance)
 local sign=Instance.new("Part");sign.Name="Wayfinder"
 sign.Size=Vector3.one;sign.Position=p;sign.Anchored=true;sign.Transparency=1
 sign.CanCollide=false;sign.CanQuery=false;sign.CanTouch=false;sign.CastShadow=false
 sign.Parent=parent
 local gui=Instance.new("BillboardGui");gui.Size=UDim2.fromOffset(size,38);gui.MaxDistance=distance
 gui.AlwaysOnTop=false;gui.Parent=sign
 local t=Instance.new("TextLabel");t.BackgroundColor3=Color3.fromRGB(20,30,39)
 t.BackgroundTransparency=.12;t.TextColor3=Color3.fromRGB(228,248,245)
 t.Size=UDim2.fromScale(1,1);t.Font=Enum.Font.GothamBold;t.TextSize=14;t.Text=word;t.Parent=gui
 local corner=Instance.new("UICorner");corner.CornerRadius=UDim.new(0,6);corner.Parent=t
end
for _,link in ipairs(layout.plannedZone09Links) do
 local points=layout.worldLinks[table.concat(link,"-")]
 for k,id in ipairs(link) do
  local a=k==1 and points[1] or points[#points]
  local b=k==1 and points[2] or points[#points-1]
  local along=Vector3.new(b[1]-a[1],0,b[3]-a[3]).Unit
  local anchor=Vector3.new(table.unpack(a))-along*7+Vector3.new(0,9,0)
  label(groups[id], "TO  "..layout.districts[link[3-k]].name,anchor,190,120*scale)
 end
end
world.Parent=workspace

local count=0
local headroomCount=0
local vector=Vector3.new
local pending={}
local params=RaycastParams.new()
params.FilterType=Enum.RaycastFilterType.Include
params.FilterDescendantsInstances={world}
local function probe(point,id,scope)
 count+=1
 local hit=workspace:Raycast(point+vector(0,6,0),vector(0,-12,0),params)
 if not hit or math.abs(hit.Position.Y-point.Y)>.25 then
  table.insert(pending,id..":"..tostring(point)..":"..(hit and hit.Instance.Name or "no floor"))
 end
 if scope then
  local authoredCeiling=(scope=="arterial" or scope=="main") and 16 or 6
  local ceiling=math.max(6,authoredCeiling*scale)
  local obstruction=workspace:Raycast(point+vector(0,.66,0),vector(0,ceiling-.66,0),params)
  headroomCount+=1
  if obstruction then table.insert(pending,id..":"..tostring(point)..":overhead "..obstruction.Instance.Name) end
 end
end
for id,zone in pairs(layout.districts) do probe(vector(table.unpack(zone.center)),id) end
for _,r in ipairs(builder.routes) do
 local a,c=vector(table.unpack(r.a)),vector(table.unpack(r.b))
 local d=c-a
 local side=vector(d.Z,0,-d.X).Unit
 local steps=math.ceil(d.Magnitude/(22*scale))
 for n=0,steps do
  for _,o in ipairs({-r.width*.5+2,0,r.width*.5-2}) do
   probe(a:Lerp(c,n/steps)+side*o,r.id,r.class)
  end
 end
end
if #pending>0 then
 warn("[OverworldReview] route probe failures "..#pending.." / "..count.." :: "..table.concat(pending," | ",1,math.min(#pending,16)))
end
workspace:SetAttribute("ReviewBuildName","Map10V21OverworldReview")
local colliders=0
for _,p in ipairs(world:GetDescendants()) do
 if p:IsA("BasePart") and p:GetAttribute("CollisionRole")=="Solid" then
  assert(p.CanCollide and p.CanQuery and p.Anchored and not p.CanTouch,"Invalid solid flags: "..p.Name)
  colliders+=1
 end
end
workspace:SetAttribute("ReviewSolidCount",colliders)
workspace:SetAttribute("ReviewNativeFailures",#pending)
workspace:SetAttribute("ReviewNativeRayProbes",count)
workspace:SetAttribute("ReviewNativeHeadroomProbes",headroomCount)
workspace:SetAttribute("ReviewPartCount",#builder.parts)
print("[OverworldReview] Native floor probes",count,"headroom",headroomCount,"failures",#pending,"parts",#builder.parts)
assert(#pending==0,"Overworld failed native floor check; see Studio output")

local function setup(player) player.RespawnLocation=spawn end
Players.PlayerAdded:Connect(setup)
Players.CharacterAutoLoads=true
for _,player in Players:GetPlayers() do
 setup(player)
 if not player.Character then task.spawn(function() player:LoadCharacterAsync() end) end
end

-- Backstop for slips off the intended routes. Rock below the walkable terrace
-- is physically solid (obeys the silhouette), so a fall there needs recovery
-- rather than stranding a player until they jump off again.
local Collection=game:GetService("CollectionService")
local stranded={}
Players.PlayerRemoving:Connect(function(player) stranded[player]=nil end)
task.spawn(function()
 while world.Parent==workspace do
  task.wait(.45)
  for _,player in ipairs(Players:GetPlayers()) do
   local character=player.Character
   local root=character and character:FindFirstChild("HumanoidRootPart")
   local humanoid=character and character:FindFirstChildOfClass("Humanoid")
   local probe=root and humanoid and humanoid.Health>0
     and math.abs(root.AssemblyLinearVelocity.Y)<8
     and workspace:Raycast(root.Position,vector(0,-5.5,0),params)
   local part=probe and probe.Instance
   if part and (Collection:HasTag(part,"CoastalCliff") or Collection:HasTag(part,"CliffReturn")
      or Collection:HasTag(part,"BridgeSupport")) then
    if stranded[player]==character then
     stranded[player]=nil
     character:PivotTo(spawn.CFrame+vector(0,4,0))
     root.AssemblyLinearVelocity=Vector3.zero
     root.AssemblyAngularVelocity=Vector3.zero
    else
     stranded[player]=character
    end
   else
    stranded[player]=nil
   end
  end
 end
end)
