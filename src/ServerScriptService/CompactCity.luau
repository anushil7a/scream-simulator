-- Map10 original island builder. Compatibility module name; no compact-city geometry retained.
local Layout=require(game:GetService("ReplicatedStorage").Shared.CompactLayout)
local City={};local V=Vector3.new
local function part(parent,name,size,position,color,solid)
 local p=Instance.new("Part");p.Name=name;p.Size=size;p.Position=position;p.Color=color
 p.Anchored=true;p.Material=Enum.Material.SmoothPlastic;p.CanCollide=solid;p.CanTouch=false;p.CanQuery=solid;p.Parent=parent
 return p
end
local function prompt(p,action,text,object)
 p:SetAttribute("QuestAction",action)
 local pr=Instance.new("ProximityPrompt");pr.ActionText=text;pr.ObjectText=object or p.Name
 pr.KeyboardKeyCode=Enum.KeyCode.F;pr.MaxActivationDistance=10;pr.HoldDuration=action=="Garden" and 1.5 or .25;pr.RequiresLineOfSight=false;pr.Parent=p
end
function City.Build(parent,withMap10Finish)
 local ocean
 for _,spec in ipairs(Layout.PartSpecs) do
  -- The finishing pass supplies crystals, lava channels and layered speaker drivers.
  local id=spec.id
  if withMap10Finish and not spec.collidable
   and (id:match("^Crystal%d+$") or id:match("^LavaFissure%d+$") or id:match("^BranchLava%d+$") or id:match("^Speaker[0-2]%d%d$")) then continue end
  local oceanTile=id=="Sea" or id:match("^SeaHorizon")
  if oceanTile and not ocean then
   ocean=Instance.new("Model")
   ocean.Name="OceanBackdrop";ocean.ModelStreamingMode=Enum.ModelStreamingMode.Persistent;ocean.Parent=parent
  end
  local p=part(oceanTile and ocean or parent,spec.id,spec.size,spec.position,spec.color,spec.collidable)
  if oceanTile then p.CastShadow=false end
  local r=spec.rotation or Vector3.zero;p.CFrame=CFrame.new(spec.position)*CFrame.Angles(0,math.rad(r.Y),0)*CFrame.Angles(math.rad(r.X),0,math.rad(r.Z))
  if spec.shape then p.Shape=Enum.PartType[spec.shape] end
  if spec.material then p.Material=Enum.Material[spec.material] end
  if spec.collidable then p:SetAttribute("GroundSurface",true) end
 end
 -- Offset a narrow line just inside confirmed green, so even at a cut
 -- corner the decoration neither floats over a notch nor paints a ramp.
 if Layout.MapId=="Map10" and Layout.GardenPvpEdges then
  local boundaries=Instance.new("Folder");boundaries.Name="GardenPvPBoundary";boundaries.Parent=parent
  local width=.65
  for i,e in ipairs(Layout.GardenPvpEdges) do
   local xLen,zLen=math.abs(e.x2-e.x1),math.abs(e.z2-e.z1)
   local position=V((e.x1+e.x2)/2+e.inX*.48,Layout.GardenPvpMinY+.09,(e.z1+e.z2)/2+e.inZ*.48)
   local size=V(xLen>0 and xLen-.9 or width,.05,zLen>0 and zLen-.9 or width)
   local stripe=part(boundaries,"GardenPvP" .. i,size,position,Color3.fromRGB(195,88,73),false)
   stripe.Transparency=.18;stripe.CastShadow=false
  end
 end
 local quests=Instance.new("Folder");quests.Name="QuestObjects";quests.Parent=parent
 for _,spec in ipairs(Layout.QuestMarkers) do
  local p=part(quests,spec.id,V(1,1.6,1),spec.position,Color3.fromRGB(226,181,83),false)
  prompt(p,spec.action,spec.text,spec.action=="Garden" and "Community garden" or nil)
 end
 for _,stop in ipairs(Layout.DeliveryStops) do
  local p=part(quests,stop.id,V(1,1.6,1),stop.position,Color3.fromRGB(226,181,83),false)
  p:SetAttribute("DeliveryStop",stop.id);prompt(p,"Dropoff","Deliver coffee",stop.name)
 end
 local v=Layout.Volley
 local net=part(parent,"VolleyNet",V(v.netMaxX-v.netMinX,4,.2),V((v.netMinX+v.netMaxX)/2,6,v.netZ),Color3.fromRGB(235,235,220),false);net.Transparency=.6
 for _,x in ipairs({v.netMinX-1,v.netMaxX+1}) do part(parent,"VolleyPost",V(.5,9,.5),V(x,4.5,v.netZ),Color3.fromRGB(235,235,220),true) end
 local g=Layout.Soccer.practiceGoal
 for _,spec in ipairs({{name="NickPracticeGoalLeft",size=V(.35,7,.35),position=V(g.X-8,3.5,g.Z-1)},{name="NickPracticeGoalRight",size=V(.35,7,.35),position=V(g.X+8,3.5,g.Z-1)},{name="NickPracticeGoalCrossbar",size=V(16,.35,.35),position=V(g.X,7,g.Z-1)}}) do
  part(parent,spec.name,spec.size,spec.position,Color3.fromRGB(235,235,220),false).CastShadow=false
 end
 local walk,activities={},{}
 for _,point in ipairs(Layout.Walk) do table.insert(walk,point);table.insert(activities,{position=point,kind="Stroll"}) end
 local function station(x,y,z,lx,lz,action)return {position=V(x,y+3,z),lookAt=V(lx or x,y+3,lz or z-5),action=action} end
 local jobs={
  {role="Gardener",name="Mar Soler",quests={"garden","beach"},stations={station(-490,32,-160,-490,-140,"Watering flowers"),station(-460,32,-160,-460,-140,"Watering flowers"),station(-430,32,-160,-430,-140,"Watering flowers")}},
  {role="Vendor",name="Pau Vidal",quests={"delivery"},stations={station(-40,16,120,-40,150,"Arranging produce")}},
  {role="CafeWorker",name="Julia Ferrer",stations={station(-25,16,120,-40,150,"Preparing coffee")}},
  {role="Soccer",name="Nick Booty",quests={"nick"},stations={station(264,0,335.5,g.X,g.Z-1,"Practicing missed kicks")}},
  {role="Busker",name="Eric Sol",quests={"crowd"},stations={station(-350,32,-230,-300,-260,"Playing for the courtyard")}},
  {role="Commuter",name="Boardwalk runner",quests={"sprint"},stations={station(-220,0,405,-220,420,"Waiting by the promenade")}},
  {role="Fighter",name="Arena coach",quests={"dodge","arena"},stations={station(-225,0,140,-330,120,"Watching the arena")}},
 }
 return {walk=walk,activities=activities,spawn=CFrame.new(Layout.Spawn),jobs=jobs,
  seeds={{-345,-250,role="Local",y=32},{-355,-250,role="Local",y=32},{-365,-250,role="Local",y=32},{-60,110,role="Tourist",y=16}},traffic=false,compact=true}
end
return City
