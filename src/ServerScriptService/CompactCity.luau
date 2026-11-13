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
 -- Only the arena's meaningful PvP boundary label remains; no mic tutorial signs.
 anchor.Size=V(.2,3,39)
 local gui=Instance.new("SurfaceGui");gui.Face=Enum.NormalId.Left
 gui.SizingMode=Enum.SurfaceGuiSizingMode.FixedSize;gui.CanvasSize=Vector2.new(600,100)
 gui.LightInfluence=0;gui.MaxDistance=65;gui.AlwaysOnTop=false
 gui.Name="Wayfinding";gui.Parent=anchor
 local label=Instance.new("TextLabel");label.Name="Text";label.Size=UDim2.fromScale(1,1)
 label.BackgroundColor3=Color3.fromRGB(30,48,54);label.BackgroundTransparency=1;label.TextColor3=Color3.fromRGB(255,243,214)
 label.TextSize=36;label.TextWrapped=true;label.Font=Enum.Font.GothamBold;label.Text=text;label.Parent=gui
end
-- Original, static coastal-academy art. None of these pieces participate in hits,
-- navigation, touch events or quest state. Existing solid silhouettes remain opaque.
local function academyArt(parent,byId)
 local art=Instance.new("Folder");art.Name="CoastalAcademyArt";art.Parent=parent
 local ivory=Color3.fromRGB(239,224,190)
 local slate=Color3.fromRGB(42,65,72)
 local gold=Color3.fromRGB(244,188,75)
 local terracotta=Color3.fromRGB(166,91,69)
 local seam=Color3.fromRGB(197,187,159)
 local count=0
 local function detail(name,size,position,color,shape)
  count+=1
  local p=part(art,name,size,position,color,false)
  p.CanQuery=false
  p.CastShadow=false
  if shape then p.Shape=shape end
  return p
 end
 -- The original full solid tree crowns remain: rounded lobes dress, not replace,
 -- their collision silhouette. All canopy additions are above walking/head height.
 for i=0,7 do
  local crown=byId["TreeCrown"..i];local pos=crown.Position
  crown.Color=Color3.fromRGB(77,116,92)
  detail("CanopyCrown"..i,V(18,12,18),V(pos.X,pos.Y+1,pos.Z),Color3.fromRGB(91,133,101),Enum.PartType.Ball)
  detail("CanopyLight"..i,V(12,10,12),V(pos.X-4,pos.Y+4,pos.Z-2),Color3.fromRGB(120,151,109),Enum.PartType.Ball)
  detail("CanopyShade"..i,V(13,10,13),V(pos.X+4,pos.Y,pos.Z+3),Color3.fromRGB(66,104,85),Enum.PartType.Ball)
  local base=byId["Planter"..i].Position
  detail("PlanterRimN"..i,V(10.5,.45,.5),V(base.X,3.1,base.Z-5),ivory)
  detail("PlanterRimS"..i,V(10.5,.45,.5),V(base.X,3.1,base.Z+5),ivory)
  detail("PlanterRimW"..i,V(.5,.45,9.5),V(base.X-5,3.1,base.Z),ivory)
  detail("PlanterRimE"..i,V(.5,.45,9.5),V(base.X+5,3.1,base.Z),ivory)
 end
 -- Architecture is dressed within its existing footprint: deeper cornices,
 -- recessed-looking dark windows, warm sills and facade pilasters.
 for i=0,4 do
  local x=-90+i*60
  detail("MarketCornice"..i,V(44,.8,1),V(x,21,-250.8),ivory)
  detail("MarketBase"..i,V(44,2,.35),V(x,1,-250.7),ivory)
  for _,dx in ipairs({-20,20})do
   detail("MarketPilaster"..i.."_"..dx,V(1.4,20,.4),V(x+dx,11,-250.6),ivory)
  end
  for j=0,2 do
   local wx=x-12+j*12
   detail("MarketSill"..i.."_"..j,V(7,.6,.8),V(wx,10.8,-250.3),ivory)
   detail("MarketLintel"..i.."_"..j,V(7,.6,.55),V(wx,17.3,-250.4),ivory)
   detail("MarketMullion"..i.."_"..j,V(.3,6,.4),V(wx,14,-250.5),ivory)
  end
  -- Awning stripes sit on its top, leaving the existing underside/headroom alone.
  for j=0,5 do
   detail("AwningStripe"..i.."_"..j,V(3,.035,8),V(x-15+j*6,8.52,-247),ivory)
  end
  detail("MarketRoofLip"..i,V(47,.5,.45),V(x,23.15,-249.1),terracotta)
 end
 for i=0,3 do
  local z=-135+i*70
  detail("OldTownCornice"..i,V(.7,1,44),V(257.8,24.5,z),ivory)
  detail("OldTownBase"..i,V(.4,2,44),V(257.7,1,z),ivory)
  for _,dz in ipairs({-20,20})do
   detail("OldTownPilaster"..i.."_"..dz,V(.4,23,1.4),V(257.6,13,z+dz),ivory)
  end
  for j=0,2 do
   local wz=z-12+j*12
   detail("OldTownSill"..i.."_"..j,V(.8,.6,8),V(257.3,12.2,wz),ivory)
   detail("OldTownLintel"..i.."_"..j,V(.6,.6,8),V(257.4,19.8,wz),ivory)
   detail("OldTownMullion"..i.."_"..j,V(.4,7,.3),V(257.5,16,wz),ivory)
  end
 end
 -- A distinctive twin-spire skyline on the existing basilica mass, never in a lane.
 for _,x in ipairs({256,294})do
  detail("TowerBelt"..x,V(10.6,1.5,12.6),V(x,48,-262),ivory)
  detail("TowerCrown"..x,V(9,5,11),V(x,62.5,-262),ivory)
  detail("TowerCap"..x,V(6,5,8),V(x,67.5,-262),terracotta)
  detail("TowerLantern"..x,V(3,3,3),V(x,71.5,-262),gold,Enum.PartType.Ball)
 end
 detail("BasilicaFacadeBand",V(48,1,.4),V(275,27,-237.7),ivory)
 -- Portal dressing follows existing gate posts/beam, retaining the 36-stud opening.
 for _,z in ipairs({30,70})do
  detail("ArenaPostFace"..z,V(.35,11,3.5),V(-122.2,6,z),slate)
  detail("ArenaPostAccent"..z,V(.4,7,.6),V(-122.4,7,z),gold)
  detail("ArenaPostCrown"..z,V(4.8,2,4.8),V(-120,15,z),ivory)
 end
 detail("ArenaFascia",V(.35,3,39),V(-122.2,13.5,50),slate)
 detail("ArenaFasciaBand",V(.4,.5,39),V(-122.4,15.3,50),gold)
 -- Calm ground articulation: small cross-joints, never new borders resembling
 -- a damage or collision boundary. Route strips remain above.
 for z=-140,140,20 do
  detail("CourtyardJoint"..z,V(178,.012,.18),V(-260,.087,z),seam)
 end
 for x=-340,340,20 do
  detail("PromenadeJoint"..x,V(.18,.012,39),V(x,.097,200),seam)
 end
 -- Existing cover gets a clearly solid plinth/top and restrained paneling, wholly
 -- within 0.08 studs of its solid silhouette, without widening useful cover.
 for i=0,7 do
  local c=byId["CoverCore"..i];local pos=c.Position
  c.Color=slate
  detail("CoverTop"..i,V(11.8,.06,11.8),V(pos.X,6.04,pos.Z),ivory)
  detail("CoverFront"..i,V(10,.5,.08),V(pos.X,4.8,pos.Z-6.02),gold)
 end
 -- Clear value hierarchy without lighting/post-effect changes.
 byId.ArenaFloor.Color=Color3.fromRGB(126,147,145)
 byId.HubPaving.Color=Color3.fromRGB(224,214,188)
 byId.Promenade.Color=Color3.fromRGB(220,204,174)
 assert(count<=350,"Coastal art budget exceeded")
end
function City.Build(parent)
 local byId={}
 for _,spec in ipairs(Layout.PartSpecs) do
  local p=part(parent,spec.id,spec.size,spec.position,spec.color,spec.collidable);byId[spec.id]=p
  if spec.id=="Ground" then p:SetAttribute("GroundSurface",true) end
 end
 local guidance=Instance.new("Folder");guidance.Name="FirstMinuteGuidance";guidance.Parent=parent
 for _,spec in ipairs(Layout.GuidanceSpecs) do
  local p=part(guidance,spec.id,spec.size,spec.position,spec.color,false)
  p.CanQuery=false;p.CastShadow=false;p.Transparency=0
 end
 wayfinding(parent,"ArenaWayfinding",V(-122.6,13.5,50),"BEAM ARENA\nPVP INSIDE RED LINES")
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
 -- Decorative practice goal only; local resident animation never scores or collides.
 local practiceGoal=Layout.Soccer.practiceGoal
 for _,spec in ipairs({
  {name="NickPracticeGoalLeft",size=V(.35,7,.35),position=V(practiceGoal.X-8,3.5,practiceGoal.Z-1)},
  {name="NickPracticeGoalRight",size=V(.35,7,.35),position=V(practiceGoal.X+8,3.5,practiceGoal.Z-1)},
  {name="NickPracticeGoalCrossbar",size=V(16,.35,.35),position=V(practiceGoal.X,7,practiceGoal.Z-1)},
 }) do
  local goal=part(parent,spec.name,spec.size,spec.position,Color3.fromRGB(235,235,220),false)
  goal.CanQuery=false;goal.CanTouch=false;goal.CastShadow=false
 end
 academyArt(parent,byId)
 local walk,activities={},{}
 for _,point in ipairs(Layout.Walk) do table.insert(walk,point);table.insert(activities,{position=point,kind="Stroll"}) end
 local function station(x,z,lookX,lookZ,action)return {position=V(x,3,z),lookAt=V(lookX or x,3,lookZ or z-5),action=action} end
 local jobs={
  {role="Gardener",name="Mar Soler",quests={"garden","beach"},stations={station(-325,-250,-325,-270,"Watering flowers"),station(-295,-250,-295,-270,"Watering flowers"),station(-265,-250,-265,-270,"Watering flowers")}},
  {role="Vendor",name="Pau Vidal",quests={"delivery"},stations={station(30,-225,30,-247,"Arranging produce")}},
  {role="CafeWorker",name="Julia Ferrer",stations={station(42,-225,30,-225,"Preparing coffee")}},
  {role="Soccer",name="Nick Booty",quests={"nick"},stations={station(239,281,practiceGoal.X,practiceGoal.Z-1,"Practicing missed kicks")}},
  {role="Busker",name="Eric Sol",quests={"crowd"},stations={station(Layout.Ambience.buskerPosition.X,Layout.Ambience.buskerPosition.Z,-310,140,"Playing for the courtyard")}},
  {role="Commuter",name="Boardwalk runner",quests={"sprint"},stations={station(-220,190,-220,200,"Waiting by the promenade")}},
  {role="Fighter",name="Arena coach",quests={"dodge","arena"},stations={station(-137,40,-100,50,"Watching the arena")}},
 }
 return {walk=walk,activities=activities,spawn=CFrame.new(Layout.Spawn),jobs=jobs,
  seeds={{-310,130,role="Local"},{-310,140,role="Local"},{-310,150,role="Local"},{110,-225,role="Tourist"}},traffic=false,compact=true}
end
return City
