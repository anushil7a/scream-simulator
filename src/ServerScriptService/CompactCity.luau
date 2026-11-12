-- Compact runtime city; source draft and preserved original remain separate.
local Layout=require(game:GetService("ReplicatedStorage").Shared.CompactLayout)
local City={}
local V=Vector3.new
local function part(parent,name,size,position,color,collidable)
 local p=Instance.new("Part");p.Name=name;p.Size=size;p.Position=position;p.Color=color
 p.Material=Enum.Material.SmoothPlastic;p.Anchored=true;p.CanCollide=collidable;p.CanTouch=false;p.CanQuery=true;p.Parent=parent
 return p
end
local function prompt(p,kind,text,object)
 p:SetAttribute("QuestAction",kind)
 local pr=Instance.new("ProximityPrompt");pr.ActionText=text;pr.ObjectText=object or p.Name;pr.KeyboardKeyCode=Enum.KeyCode.F
 pr.MaxActivationDistance=10;pr.HoldDuration=kind=="Garden" and 1.5 or .25;pr.RequiresLineOfSight=false;pr.Parent=p
end
local function wayfinding(parent,name,position,text)
 local anchor=part(parent,name,V(.2,.2,.2),position,Color3.fromRGB(255,203,99),false)
 anchor.Transparency=1;anchor.CanQuery=false
 local gui=Instance.new("BillboardGui");gui.Name="Wayfinding";gui.Size=UDim2.fromOffset(260,60);gui.StudsOffset=V(0,3,0)
 gui.MaxDistance=65;gui.AlwaysOnTop=false;gui.Parent=anchor
 local label=Instance.new("TextLabel");label.Name="Text";label.Size=UDim2.fromScale(1,1)
 label.BackgroundColor3=Color3.fromRGB(30,48,54);label.BackgroundTransparency=.15;label.TextColor3=Color3.fromRGB(255,243,214)
 label.TextSize=16;label.TextWrapped=true;label.Font=Enum.Font.GothamBold;label.Text=text;label.Parent=gui
end
function City.Build(parent)
 local byId={}
 for _,spec in ipairs(Layout.PartSpecs) do
  local p=part(parent,spec.id,spec.size,spec.position,spec.color,spec.collidable);byId[spec.id]=p
  if spec.id=="Ground" then p:SetAttribute("GroundSurface",true) end
  if spec.id=="PracticeTarget" then p.CanCollide=true;p:SetAttribute("MicPracticeTarget",true);p:SetAttribute("RestColor",spec.color) end
 end
 local guidance=Instance.new("Folder");guidance.Name="FirstMinuteGuidance";guidance.Parent=parent
 for _,spec in ipairs(Layout.GuidanceSpecs) do
  local p=part(guidance,spec.id,spec.size,spec.position,spec.color,false)
  p.CanQuery=false;p.CastShadow=false;p.Transparency=0
 end
 -- Above the existing paving and cosmetic route; never a collision/raycast surface.
 local stand=part(parent,"StandLine",V(.35,.04,10),V(Layout.Practice.position.X,.14,Layout.Practice.position.Z),Color3.fromRGB(255,203,99),false);stand.CanQuery=false
 wayfinding(parent,"SpawnWayfinding",V(Layout.Spawn.X,4,Layout.Spawn.Z),"MIC PRACTICE: NORTH\nTraining pads are in the west courtyard")
 wayfinding(parent,"PracticeWayfinding",V(-270,4,65),"MIC PRACTICE / AIM WEST, SPEAK, GO QUIET")
 wayfinding(parent,"ArenaWayfinding",V(-137,4,50),"BEAM ARENA / PVP INSIDE RED LINES")
 local quests=Instance.new("Folder");quests.Name="QuestObjects";quests.Parent=parent
 for _,spec in ipairs(Layout.QuestMarkers) do
  local p=part(quests,spec.id,V(1,1.6,1),spec.position,Color3.fromRGB(226,181,83),false)
  prompt(p,spec.action,spec.text,spec.action=="Garden" and "Community garden" or nil)
 end
 for _,stop in ipairs(Layout.DeliveryStops) do
  local p=part(quests,stop.id,V(1,1.6,1),stop.position,Color3.fromRGB(226,181,83),false)
  p:SetAttribute("DeliveryStop",stop.id);prompt(p,"Dropoff","Deliver coffee",stop.name)
 end
 -- Net is cosmetic and non-colliding; authoritative ball rules live in BeachVolley.
 local net=part(parent,"VolleyNet",V(40,4,.2),V(-20,6,250),Color3.fromRGB(235,235,220),false);net.Transparency=.6
 for _,x in ipairs({-41,1}) do part(parent,"VolleyPost",V(.5,9,.5),V(x,4.5,250),Color3.fromRGB(235,235,220),true) end
 local walk,activities={},{}
 for _,point in ipairs(Layout.Walk) do table.insert(walk,point);table.insert(activities,{position=point,kind="Stroll"}) end
 local function station(x,z,lookX,lookZ,action)return {position=V(x,3,z),lookAt=V(lookX or x,3,lookZ or z-5),action=action} end
 local jobs={
  {role="Gardener",name="Mar Soler",quests={"garden","beach"},stations={station(-325,-250,-325,-270,"Watering flowers"),station(-295,-250,-295,-270,"Watering flowers"),station(-265,-250,-265,-270,"Watering flowers")}},
  {role="Vendor",name="Pau Vidal",quests={"delivery"},stations={station(30,-225,30,-247,"Arranging produce")}},
  {role="CafeWorker",name="Julia Ferrer",stations={station(42,-225,30,-225,"Preparing coffee")}},
  {role="Soccer",name="Nick Booty",quests={"nick"},stations={station(239,281,252,251,"Practicing missed kicks")}},
  {role="Busker",name="Eric Sol",quests={"crowd"},stations={station(-300,125,-310,140,"Playing for the courtyard")}},
  {role="Commuter",name="Boardwalk runner",quests={"sprint"},stations={station(-220,190,-220,200,"Waiting by the promenade")}},
  {role="Fighter",name="Arena coach",quests={"dodge","arena"},stations={station(-137,40,-100,50,"Watching the arena")}},
 }
 return {walk=walk,activities=activities,spawn=CFrame.new(Layout.Spawn),jobs=jobs,
  seeds={{-310,130,role="Local"},{-310,140,role="Local"},{-310,150,role="Local"},{110,-225,role="Tourist"}},traffic=false,compact=true}
end
return City
