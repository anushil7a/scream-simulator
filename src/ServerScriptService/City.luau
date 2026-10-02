-- Original Barcelona-inspired city geometry. All art is generated locally; no downloaded scripts/assets.
local City={}
local V=Vector3.new
local Collection=game:GetService("CollectionService")
local palette={Color3.fromRGB(219,192,151),Color3.fromRGB(227,206,171),Color3.fromRGB(195,151,117),Color3.fromRGB(234,214,180),Color3.fromRGB(191,169,135),Color3.fromRGB(220,174,143)}
local stone=Color3.fromRGB(207,191,159)
local dark=Color3.fromRGB(48,62,61)
local iron=Color3.fromRGB(39,53,53)
local glass=Color3.fromRGB(66,104,112)
local leaf=Color3.fromRGB(80,120,72)
local terra=Color3.fromRGB(168,89,60)
local cream=Color3.fromRGB(245,224,180)
local rng=Random.new(230926)
local function part(parent,name,size,cf,color,material,solid)
 local p=Instance.new("Part");p.Name=name;p.Size=size;p.CFrame=typeof(cf)=="CFrame" and cf or CFrame.new(cf);p.Color=color;p.Material=material or Enum.Material.SmoothPlastic
 p.CastShadow=solid~=false
 p.Anchored=true;p.CanCollide=solid~=false;p.CanQuery=solid~=false;p.CanTouch=false;p.Parent=parent;return p
end
local function model(parent,name) local m=Instance.new("Model");m.Name=name;m.Parent=parent;return m end
local function ellipsoid(parent,name,size,position,color,material)
 local p=part(parent,name,size,position,color,material,false);local mesh=Instance.new("SpecialMesh");mesh.MeshType=Enum.MeshType.Sphere;mesh.Parent=p;return p
end
local function cylinder(parent,name,radius,height,pos,color,material)
 local p=part(parent,name,V(height,radius*2,radius*2),CFrame.new(pos)*CFrame.Angles(0,0,math.pi/2),color,material);p.Shape=Enum.PartType.Cylinder;return p
end
local function sign(parent,text,cf,width)
 local p=part(parent,"FacadeSign",V(width,2,.25),cf,dark,nil,false)
 local g=Instance.new("SurfaceGui");g.Face=Enum.NormalId.Front;g.PixelsPerStud=28;g.SizingMode=Enum.SurfaceGuiSizingMode.PixelsPerStud;g.Parent=p
 local t=Instance.new("TextLabel");t.Size=UDim2.fromScale(1,1);t.BackgroundTransparency=1;t.Font=Enum.Font.GothamBold;t.TextColor3=cream;t.TextScaled=true;t.Text=text;t.Parent=g;return p
end
local function destructible(m,kind)
 m:SetAttribute("DestructibleType",kind);Collection:AddTag(m,"CityDestructible")
end
local function tree(parent,x,z,palm)
 local group=model(parent,palm and "Palm" or "SmallTree");parent=group
 if not palm and (V(x,0,z)-V(-600,0,210)).Magnitude>85 then destructible(group,"SmallTree") end
 local h=palm and rng:NextNumber(14,20) or rng:NextNumber(10,15)
 cylinder(parent,"TreeTrunk",.65,h,V(x,h/2+1,z),Color3.fromRGB(116,96,69),Enum.Material.Wood)
 if palm then
  for j=1,7 do
   local cf=CFrame.new(x,h+1,z)*CFrame.Angles(0,j*math.pi*2/7,0)
   for k=1,3 do part(parent,"PalmFrond",V(2.4,.22,3.5),cf*CFrame.new(0,-(k-1)^2*.35,k*2.2)*CFrame.Angles((k-2)*.23,0,0),leaf,Enum.Material.Grass,false) end
  end
 else
  -- Branches and separate crown clusters avoid the old stacked mushroom silhouette.
  for j=0,3 do
   local angle=j*math.pi/2+.45
   local direction=V(math.cos(angle),0,math.sin(angle))
   local start=V(x,h-2,z);local finish=V(x,h+1.5,z)+direction*3.2
   part(parent,"PlaneTreeBranch",V(.55,.55,(finish-start).Magnitude),CFrame.lookAt((start+finish)/2,finish),Color3.fromRGB(116,96,69),Enum.Material.Wood,false)
   ellipsoid(parent,"PlaneTreeCrown",V(7.4,5.8,7.4),finish+V(0,1,0),Color3.fromRGB(78+j*5,116+j*5,68+j*3),Enum.Material.Grass)
  end
  ellipsoid(parent,"PlaneTreeCrown",V(8.5,7,8.5),V(x,h+4,z),Color3.fromRGB(93,137,79),Enum.Material.Grass)
 end
 return group,h
end
local function lamp(parent,x,z)
 cylinder(parent,"StreetLamp",.22,12,V(x,7,z),iron,Enum.Material.Metal)
 local top=part(parent,"Lantern",V(1.4,2,1.4),V(x,13,z),cream,Enum.Material.Neon,false)
 part(parent,"LanternCap",V(2,.3,2),V(x,14.2,z),iron,Enum.Material.Metal,false)
 -- Limit dynamic lights: bright lantern geometry reads well without hundreds of shadow maps.
 if math.abs(x)<100 and math.abs(z)<100 then local l=Instance.new("PointLight");l.Range=16;l.Brightness=.3;l.Color=cream;l.Parent=top end
end
local function bench(parent,cf)
 local group=model(parent,"Bench");parent=group
 if (cf.Position-V(-600,0,210)).Magnitude>85 then destructible(group,"Bench") end
 local seat=part(parent,"BenchSeat",V(8,.5,2.5),cf*CFrame.new(0,2,0),Color3.fromRGB(139,100,66),Enum.Material.WoodPlanks)
 part(parent,"BenchBack",V(8,2.2,.35),cf*CFrame.new(0,3.2,1.1),Color3.fromRGB(139,100,66),Enum.Material.WoodPlanks)
 local usable=Instance.new("Seat");usable.Name="UsableSeat";usable.Size=V(3,.25,2);usable.CFrame=cf*CFrame.new(0,2.4,0);usable.Transparency=1;usable.Anchored=true;usable.CanCollide=false;usable.Parent=parent
 local sit=Instance.new("ProximityPrompt");sit.ActionText="Sit";sit.ObjectText="City bench";sit.KeyboardKeyCode=Enum.KeyCode.F;sit.MaxActivationDistance=7;sit.Parent=seat
 sit.Triggered:Connect(function(player) local h=player.Character and player.Character:FindFirstChildOfClass("Humanoid");local root=player.Character and player.Character:FindFirstChild("HumanoidRootPart");if h and root and (root.Position-seat.Position).Magnitude<9 and not group:GetAttribute("Destroyed") then usable:Sit(h) end end)
 for _,x in ipairs({-3,3}) do part(parent,"BenchLeg",V(.35,2,.9),cf*CFrame.new(x,1,0),iron,Enum.Material.Metal) end
end
local function cafe(parent,x,z,color)
 cylinder(parent,"CafeTable",2,.25,V(x,3,z),stone,Enum.Material.Marble)
 cylinder(parent,"TableLeg",.2,2,V(x,2,z),iron,Enum.Material.Metal)
 for _,dx in ipairs({-3.2,3.2}) do
  part(parent,"CafeChair",V(2,.4,2),V(x+dx,2,z),color,Enum.Material.Wood)
  part(parent,"CafeChairBack",V(.4,2.7,2),V(x+dx+(dx>0 and .9 or -.9),3,z),color,Enum.Material.Wood)
 end
 cylinder(parent,"Cup",.3,.55,V(x,3.45,z),cream,Enum.Material.CeramicTiles)
end
local shops={"FORN DEL SOL","CAFÈ MARINA","FLORS I FULLES","LLIBRERIA","GELATS","MERCAT LOCAL","TAPES DEL BARRI","ESTUDI D'ART","PANADERIA","MÚSICA","FRUITA FRESCA","CASA DE TE"}
local function building(parent,cf,w,d,floors,index,style)
 local m=model(parent,"Casa_"..index)
 local h=floors*8+7;local color=palette[Random.new(index*7919):NextInteger(1,#palette)]
 local refined=parent:GetAttribute("RefinedFrontages")==true
 local frontage=index%4
 local accents={Color3.fromRGB(57,112,105),Color3.fromRGB(130,72,65),Color3.fromRGB(69,94,121),Color3.fromRGB(136,116,64)}
 local accent=accents[frontage+1]
 if refined then
  local paints={Color3.fromRGB(230,207,165),Color3.fromRGB(204,146,117),Color3.fromRGB(183,199,177),Color3.fromRGB(237,220,185)}
  color=paints[frontage+1];m:SetAttribute("FrontageStyle",({"Gallery","Terracotta","TileHouse","Atelier"})[frontage+1])
 end
 local function b(name,size,pos,c,mat,solid) return part(m,name,size,cf*CFrame.new(pos),c,mat,solid) end
 local shopIndex=index==501 and 2 or index==266 and 3 or (index-1)%#shops+1
 local shopKind=({"Bakery","Cafe","Florist","Books","Gelato","Market","Cafe","Art","Bakery","Music","Market","Cafe"})[shopIndex]
 m:SetAttribute("ShopName",shops[shopIndex]);m:SetAttribute("ShopKind",shopKind)
 local doorWidth=8
 local interior=(index%7==0 or index==501) and w>=24 and d>=20
 if interior then
  m:SetAttribute("WalkableInterior",true);m:SetAttribute("Entrance",cf*CFrame.new(0,3.8,-d/2))
  b("UpperMasonry",V(w,h-8,d),V(0,9+(h-8)/2,0),color,Enum.Material.Plaster)
  b("InteriorFloor",V(w,.3,d),V(0,1.1,0),cream,Enum.Material.WoodPlanks)
  b("RearWall",V(w,8,1),V(0,5,d/2-.5),stone,Enum.Material.Limestone)
  for _,side in ipairs({-1,1}) do
   b("SideWall",V(1,8,d),V(side*(w/2-.5),5,0),color,Enum.Material.Plaster)
   b("ShopfrontWall",V((w-doorWidth)/2,8,1),V(side*(w+doorWidth)/4,5,-d/2+.5),stone,Enum.Material.Limestone)
   b("DoorJamb",V(.4,7,.6),V(side*(doorWidth/2+.2),4.5,-d/2-.1),cream,Enum.Material.Limestone)
  end
  b("DoorLintel",V(doorWidth+.8,1,.7),V(0,8.5,-d/2-.1),cream,Enum.Material.Limestone)
  if math.abs(cf.LookVector.X)>.1 and math.abs(cf.LookVector.Z)>.1 then
   -- Chamfered corner paving ends at the threshold. Bridge its 1.35-stud drop
   -- with a shallow apron so non-jumping pedestrians can enter from the street.
   local ramp=b("EntranceRamp",V(doorWidth+2,.3,12),V(0,.55,-d/2-6),stone,Enum.Material.Pavement)
   ramp.CFrame*=CFrame.Angles(-math.atan(1.3/12),0,0)
  end
  -- Furniture stays outside the central four-stud aisle, including in narrow shops.
  m:SetAttribute("InteriorAisle",cf*CFrame.new(0,4,0));m:SetAttribute("InteriorAisleSize",V(4,4.5,d-3))
  b("ServiceCounter",V(6,3,2),V(w/2-4,2.6,0),terra,Enum.Material.Wood)
  local left=-w/2+2
  if shopKind=="Books" then
   for shelf=1,3 do
    b("BookShelf",V(1.5,.25,d*.55),V(left,1.5+shelf*1.5,1),terra,Enum.Material.Wood)
    for book=1,6 do
     b("Book",V(.7,.7+(book%3)*.15,.6),V(left,2.1+shelf*1.5,-d*.2+book*d*.07),palette[(book+index)%#palette+1],Enum.Material.Fabric,false)
    end
   end
  elseif shopKind=="Cafe" then
   b("EspressoMachine",V(2.6,1.7,1.5),V(w/2-4,4.95,0),iron,Enum.Material.Metal,false)
   b("EspressoTrim",V(2.7,.15,1.6),V(w/2-4,5.55,0),cream,Enum.Material.Metal,false)
   for dx=-.7,.7,.7 do b("CoffeeCup",V(.4,.55,.4),V(w/2-4+dx,5.9,0),cream,Enum.Material.CeramicTiles,false) end
   local tx=-w/2+4
   b("CafeInteriorTable",V(3.4,.3,3.4),V(tx,3.4,2),stone,Enum.Material.Marble)
   b("CafeInteriorTableLeg",V(.35,2.1,.35),V(tx,2.2,2),iron,Enum.Material.Metal)
   for _,side in ipairs({-1,1}) do
    local seat=Instance.new("Seat");seat.Name="CafeSeat";seat.Size=V(2,.4,2)
    seat.CFrame=cf*CFrame.new(tx,2.5,2+side*3)*CFrame.Angles(0,side==1 and 0 or math.pi,0)
    seat.Color=accent;seat.Material=Enum.Material.Wood;seat.Anchored=true;seat.Parent=m
    for _,dx in ipairs({-.7,.7}) do for _,dz in ipairs({-.7,.7}) do b("CafeSeatLeg",V(.15,1.1,.15),V(tx+dx,1.75,2+side*3+dz),iron,Enum.Material.Metal,false) end end
    b("CafeSeatBack",V(2,2,.25),V(tx,3.3,2+side*3.85),accent,Enum.Material.Wood)
    local prompt=Instance.new("ProximityPrompt");prompt.ActionText="Sit";prompt.ObjectText=shops[shopIndex];prompt.KeyboardKeyCode=Enum.KeyCode.F;prompt.MaxActivationDistance=6;prompt.Parent=seat
    prompt.Triggered:Connect(function(player)
     local c=player.Character;local root=c and c:FindFirstChild("HumanoidRootPart");local h=c and c:FindFirstChildOfClass("Humanoid")
     if root and h and h.Health>0 and not seat.Occupant and (root.Position-seat.Position).Magnitude<=8 then seat:Sit(h) end
    end)
   end
  elseif shopKind=="Florist" then
   for i=1,4 do
    local z=-d*.25+i*d*.12
    b("FlowerStand",V(2.4,1.4,2.4),V(left,1.95,z),terra,Enum.Material.CeramicTiles)
    for j=-1,1 do
     b("CutFlowerStem",V(.08,2,.08),V(left+j*.45,3.5,z),leaf,Enum.Material.Grass,false)
     local flower=b("CutFlower",V(.8,.5,.8),V(left+j*.45,4.5,z),j==0 and cream or Color3.fromRGB(212,109,133),Enum.Material.SmoothPlastic,false);flower.Shape=Enum.PartType.Ball
    end
   end
  elseif shopKind=="Art" then
   for i=1,3 do
    local z=-d*.3+i*d*.18
    b("GalleryFrame",V(.3,3.8,3),V(left-1,4.8,z),terra,Enum.Material.Wood,false)
    b("GalleryCanvas",V(.1,3.3,2.5),V(left-.78,4.8,z),Color3.fromRGB(106,165,178),Enum.Material.Fabric,false)
    b("PaintedHorizon",V(.12,1.3,2.5),V(left-.7,3.85,z),i%2==0 and leaf or stone,nil,false)
   end
   b("GalleryBench",V(1.8,1.4,d*.45),V(left+1.3,1.95,0),terra,Enum.Material.Wood)
  elseif shopKind=="Music" then
   b("InstrumentRack",V(1.8,.4,d*.6),V(left,2.1,0),terra,Enum.Material.Wood)
   for i=1,3 do
    local z=-d*.3+i*d*.15
    local body=b("DisplayGuitar",V(.6,1.7,1.2),V(left,3.2,z),i%2==0 and terra or cream,Enum.Material.Wood,false);body.Shape=Enum.PartType.Ball
    b("GuitarNeck",V(.3,2,.3),V(left,4.7,z),dark,Enum.Material.Wood,false)
   end
  else
   for shelf=1,2 do
    b("FoodDisplayShelf",V(2.4,.25,d*.6),V(left,1.9+shelf*1.5,0),stone,Enum.Material.Marble)
    for item=1,5 do
     local z=-d*.3+item*d*.1
     local foodColor=shopKind=="Bakery" and Color3.fromRGB(211,159,91) or shopKind=="Gelato" and palette[(item%#palette)+1] or item%2==0 and Color3.fromRGB(177,74,65) or Color3.fromRGB(113,155,83)
     local food=b(shopKind=="Bakery" and "BreadLoaf" or shopKind=="Gelato" and "GelatoTub" or "ProduceBasket",V(1.6,.65,1),V(left,2.35+shelf*1.5,z),foodColor,Enum.Material.SmoothPlastic,false)
     if shopKind=="Bakery" then food.Shape=Enum.PartType.Ball end
    end
   end
  end
  b("PendantStem",V(.1,1.2,.1),V(0,7.7,0),iron,Enum.Material.Metal,false)
  b("WarmPendant",V(2,.6,2),V(0,7,0),cream,Enum.Material.Neon,false)
 else
  b("Masonry",V(w,h,d),V(0,h/2+1,0),color,Enum.Material.Plaster)
  b("StonePlinth",V(w+.3,5,d+.3),V(0,3.5,0),stone,Enum.Material.Limestone)
 end
 b("Cornice",V(w+1.7,.8,d+1.7),V(0,h+1,0),cream,Enum.Material.Limestone)
 b("TerracottaRoof",V(w+1.1,.5,d+1.1),V(0,h+1.7,0),terra,Enum.Material.RoofShingles)
 b("RoofParapet",V(w,.9,.5),V(0,h+2,-d/2),stone,Enum.Material.Limestone)
 b("Chimney",V(2,4,2),V(w*.25,h+3,0),stone,Enum.Material.Brick)
 if not interior then
  b("EntranceDoor",V(3.5,5.8,.3),V(0,4,-d/2-.35),Color3.fromRGB(84,66,49),Enum.Material.Wood,false)
  b("DoorTransom",V(3.4,1.1,.4),V(0,7,-d/2-.35),glass,Enum.Material.Glass,false)
 end
 for _,dx in ipairs({-w/2+.6,w/2-.6}) do b("CornerPilaster",V(1.2,h,.6),V(dx,h/2+1,-d/2-.4),stone,Enum.Material.Limestone,false) end
 if index%3==0 then
  local facade=model(m,"BreakableFrontage")
  part(facade,"DecorativeStonePanel",V(w*.35,3.2,.5),cf*CFrame.new(0,10.5,-d/2-.5),color,Enum.Material.Limestone)
  part(facade,"PanelCornice",V(w*.38,.4,.8),cf*CFrame.new(0,12.2,-d/2-.6),cream,Enum.Material.Limestone)
  destructible(facade,floors<=2 and "HouseFacade" or floors<=4 and "ApartmentFacade" or "TowerFacade")
 end
 local cols=math.max(2,math.floor(w/9));local spacing=(w-7)/cols
 for floor=1,floors do
  local y=4+floor*8
  for col=1,cols do
   local x=(col-(cols+1)/2)*spacing
   b("WindowRecess",V(3.1,4.6,.2),V(x,y,-d/2-.16),iron,nil,false)
   local paneColor=refined and (floor+col+index)%7==0 and Color3.fromRGB(193,168,109) or glass
   b("WindowGlass",V(2.6,4.1,.22),V(x,y,-d/2-.3),paneColor,Enum.Material.Glass,false)
   if refined and floor<=2 then
    b("WindowMullion",V(.12,4.1,.08),V(x,y,-d/2-.45),cream,nil,false)
    b("WindowTransom",V(2.6,.12,.08),V(x,y+.55,-d/2-.45),cream,nil,false)
   end
   b("WindowLintel",V(3.8,.4,.6),V(x,y+2.5,-d/2-.35),cream,Enum.Material.Limestone,false)
   if style=="Born" or (refined and frontage==1) or col%2==0 then
    b("Shutter",V(.8,4.4,.35),V(x-2,y,-d/2-.35),(refined and accent or Color3.fromRGB(73,101,83)),Enum.Material.Wood,false)
    b("Shutter",V(.8,4.4,.35),V(x+2,y,-d/2-.35),(refined and accent or Color3.fromRGB(73,101,83)),Enum.Material.Wood,false)
   end
   if (floor+col+index)%2==0 and not (refined and frontage==0 and floor==1) then
    b("BalconySlab",V(4.7,.3,2.1),V(x,y-2.2,-d/2-1),stone,Enum.Material.Limestone,false)
    b("IronBalconyRail",V(4.7,1,.15),V(x,y-1.25,-d/2-2),iron,Enum.Material.Metal,false)
    -- Broad upper rails read at distance; fine ironwork is reserved for street-level floors.
    if not refined or floor<=2 then for _,dx in ipairs({-1.7,0,1.7}) do b("Baluster",V(.12,1.6,.15),V(x+dx,y-1.4,-d/2-2),iron,Enum.Material.Metal,false) end end
    if col==1 then b("WindowFlowers",V(3,.55,.55),V(x,y-.9,-d/2-2),Color3.fromRGB(174,79,100),Enum.Material.Grass,false) end
   end
  end
  for col=1,cols do
   local x=(col-(cols+1)/2)*spacing
   b("CourtyardWindow",V(2.8,4,.15),V(x,y,d/2+.1),glass,Enum.Material.Glass,false)
  end
  for _,side in ipairs({-1,1}) do for k=-1,1 do
   b("SideWindow",V(.15,4,2.7),V(side*(w/2+.1),y,k*d/4),glass,Enum.Material.Glass,false)
  end end
 end
 if refined then
  -- Four frontage compositions share a collision shell and a clear central entrance.
  if frontage==0 then
   b("GalleryBalcony",V(w-5,.35,2.8),V(0,9.8,-d/2-1.3),stone,Enum.Material.Limestone,false)
   b("GalleryRail",V(w-5,1.1,.18),V(0,10.7,-d/2-2.6),iron,Enum.Material.Metal,false)
   for x=-w/2+4,w/2-4,4 do b("GallerySpindle",V(.14,1.8,.14),V(x,10.6,-d/2-2.6),iron,Enum.Material.Metal,false) end
   b("UpperTerrace",V(w*.64,1.8,d*.5),V(0,h+2.5,d*.12),stone,Enum.Material.Limestone,false)
  elseif frontage==1 then
   for _,side in ipairs({-1,1}) do
    b("SteppedGable",V(w*.22,2.6,.9),V(side*w*.23,h+2.7,-d/2),cream,Enum.Material.Limestone,false)
   end
   b("GableCrown",V(w*.22,4.1,.9),V(0,h+3.45,-d/2),cream,Enum.Material.Limestone,false)
  elseif frontage==2 then
   for floor=1,floors do
    b("CeramicBelt",V(w-.8,.65,.35),V(0,7.5+floor*8,-d/2-.4),accent,Enum.Material.CeramicTiles,false)
   end
   for _,side in ipairs({-1,1}) do b("CeramicPier",V(.55,h-8,.4),V(side*(w/2-2),h/2+5,-d/2-.45),accent,Enum.Material.CeramicTiles,false) end
  else
   for _,side in ipairs({-1,1}) do
    b("AtelierBay",V(4.8,h-12,1),V(side*w*.27,(h+12)/2,-d/2-.55),stone,Enum.Material.Limestone,false)
    for floor=2,floors do b("BayGlazing",V(3.5,5,.16),V(side*w*.27,4+floor*8,-d/2-1.1),glass,Enum.Material.Glass,false) end
   end
   b("AtelierRoofLight",V(w*.38,2,d*.34),V(0,h+2.8,0),accent,Enum.Material.Metal,false)
  end
  b("ShopFascia",V(w-.8,1.4,.55),V(0,8.3,-d/2-.4),accent,Enum.Material.Wood,false)
 end
 local shopOffset=(w+doorWidth)/4;local windowWidth=(w-doorWidth)/2-1.6
 for _,x in ipairs({-shopOffset,shopOffset}) do
  b("ShopGlazing",V(windowWidth,5.3,.25),V(x,4,-d/2-.25),glass,Enum.Material.Glass,false)
  local awningColor=refined and accent or index%2==0 and Color3.fromRGB(118,67,57) or Color3.fromRGB(61,111,99)
  local canopy=b("ShopAwning",V(windowWidth+.7,.35,3),V(x,7,-d/2-1),awningColor,Enum.Material.Fabric,false)
  if refined then
   canopy.CFrame*=CFrame.Angles(-.14,0,0)
   b("AwningValance",V(windowWidth+.7,.55,.12),V(x,6.5,-d/2-2.5),awningColor,Enum.Material.Fabric,false)
   b("ShopWindowFrame",V(windowWidth+.5,5.8,.13),V(x,4,-d/2-.39),accent,Enum.Material.Wood,false)
   b("ShopWindowInset",V(windowWidth-.4,4.9,.1),V(x,4,-d/2-.48),glass,Enum.Material.Glass,false)
   b("ShopTransom",V(windowWidth-.4,.14,.1),V(x,5.55,-d/2-.55),cream,nil,false)
   for _,side in ipairs({-1,1}) do b("DisplayMullion",V(.13,4.9,.12),V(x+side*windowWidth*.22,4,-d/2-.57),cream,nil,false) end
   b("DisplayShelf",V(windowWidth*.9,.18,.15),V(x,2.6,-d/2-.57),cream,nil,false)
  end
 end
 sign(m,shops[shopIndex],cf*CFrame.new(0,8.7,-d/2-(refined and .85 or .5)),math.min(w-3,26))
 if style=="Modernista" then
  for i=-2,2 do
   local ornament=b("CeramicCrown",V(3,2.8+math.abs(i),2),V(i*w/6,h+2.5,-d/2),i%2==0 and Color3.fromRGB(78,146,145) or cream,Enum.Material.CeramicTiles,false)
   ornament.Shape=Enum.PartType.Ball
  end
 end
 return m
end
local function octagon(parent,x,z)
 part(parent,"ChamferedPaving",V(208,1,152),V(x,.3,z),stone,Enum.Material.Pavement)
 part(parent,"ChamferedPaving",V(152,1,208),V(x,.3,z),stone,Enum.Material.Pavement)
 -- Four diamond infills turn the square cutouts into 45-degree corners.
 for _,sx in ipairs({-1,1}) do for _,sz in ipairs({-1,1}) do
  part(parent,"Chamfer",V(39.6,1,39.6),CFrame.new(x+sx*76,.3,z+sz*76)*CFrame.Angles(0,math.pi/4,0),stone,Enum.Material.Pavement)
 end end
end
local function garden(parent,x,z,index,activities)
 -- Every court keeps two unobstructed twelve-stud public passages. Details stay
 -- inside quadrants so the entrances never terminate at a fence or a tree.
 local theme=({"ReadingGarden","OrangeCourt","SculptureCourt","PergolaCourt"})[(index-1)%4+1]
 local m=model(parent,theme);m:SetAttribute("CourtyardTheme",theme)
 m:SetAttribute("CourtCenter",V(x,1.3,z))
 part(m,"CourtyardGarden",V(110,.3,110),V(x,1,z),Color3.fromRGB(112,138,79),Enum.Material.Grass)
 for _,size in ipairs({V(12,.12,110),V(110,.12,12)}) do part(m,"GardenPath",size,V(x,1.2,z),Color3.fromRGB(209,192,153),Enum.Material.Pavement) end
 local function pad(dx,dz)
  part(m,"CourtTerrace",V(36,.12,36),V(x+dx,1.22,z+dz),Color3.fromRGB(222,206,175),Enum.Material.Cobblestone)
 end
 local function planter(dx,dz)
  part(m,"LimestonePlanter",V(15,1.1,7),V(x+dx,1.7,z+dz),stone,Enum.Material.Limestone)
  part(m,"PlanterSoil",V(14.4,.12,6.4),V(x+dx,2.3,z+dz),Color3.fromRGB(90,73,54),Enum.Material.Ground,false)
  for k=-2,2 do
   ellipsoid(m,"Lavender",V(2.3,1.5,3.5),V(x+dx+k*2.6,2.8,z+dz),Color3.fromRGB(116+k*3,116,150),Enum.Material.Grass)
  end
 end
 local function seat(dx,dz,yaw)
  bench(m,CFrame.new(x+dx,0,z+dz)*CFrame.Angles(0,yaw or 0,0))
 end
 if theme=="ReadingGarden" then
  for _,side in ipairs({-1,1}) do
   pad(side*29,-29);tree(m,x+side*39,z-39,false)
   seat(side*27,-17,math.pi);planter(side*28,-47)
  end
  -- A pair of sheltered reading rooms, open toward the crossing paths.
  for _,side in ipairs({-1,1}) do
   pad(side*29,29)
   for _,dx in ipairs({-11,11}) do for _,dz in ipairs({-10,10}) do
    local top=11.3+math.sin(side*.06)*dx
    part(m,"ReadingCanopyPost",V(.65,top-1.3,.65),V(x+side*29+dx,(top+1.3)/2,z+29+dz),iron,Enum.Material.Metal)
   end end
   part(m,"ReadingCanopy",V(26,.4,24),CFrame.new(x+side*29,11.5,z+29)*CFrame.Angles(0,0,side*.06),Color3.fromRGB(132,86,65),Enum.Material.WoodPlanks,false)
   seat(side*29,33);seat(side*29,23,math.pi)
  end
 elseif theme=="OrangeCourt" then
  for _,dx in ipairs({-29,29}) do for _,dz in ipairs({-29,29}) do
   pad(dx,dz);local orangeTree,height=tree(m,x+dx,z+dz,false)
   for k=0,7 do
    local angle=math.floor(k/2)*math.pi/2+.45+(k%2-.5)*.35
    ellipsoid(orangeTree,"OrangeFruit",V(.9,.9,.9),V(x+dx+math.cos(angle)*5.3,height+.05,z+dz+math.sin(angle)*5.3),Color3.fromRGB(230,143,49))
   end
   seat(dx,dz+(dz<0 and 12 or -12),dz<0 and math.pi or 0)
  end end
 elseif theme=="SculptureCourt" then
  pad(-29,-29);pad(29,29)
  for _,side in ipairs({-1,1}) do
   local center=V(x+side*29,2,z+side*29)
   part(m,"SculpturePlinth",V(8,1.5,8),center,stone,Enum.Material.Limestone)
   -- Interlocking tilted blades give each end a recognizable silhouette.
   for blade=0,2 do
    part(m,"SculptureBlade",V(1.4,9,3.3),CFrame.new(center+V((blade-1)*2,5.5,0))*CFrame.Angles(.15,blade*.5,(blade-1)*.32),({Color3.fromRGB(63,132,138),Color3.fromRGB(203,123,79),Color3.fromRGB(222,185,99)})[blade+1],Enum.Material.Metal)
   end
   seat(side*29,side*29-side*12,side<0 and math.pi or 0)
   planter(side*29,-side*31);tree(m,x+side*40,z-side*43,false)
  end
 else
  for _,side in ipairs({-1,1}) do
   pad(side*29,-29);pad(side*29,29)
   for _,dx in ipairs({-12,12}) do for _,dz in ipairs({-12,12}) do
    part(m,"PergolaColumn",V(1.2,10,1.2),V(x+side*29+dx,6.3,z-29+dz),cream,Enum.Material.Limestone)
   end end
   for dx=-14,14,4 do
    part(m,"PergolaRafter",V(.65,.7,29),V(x+side*29+dx,11.5,z-29),Color3.fromRGB(136,101,71),Enum.Material.Wood,false)
   end
   for _,dz in ipairs({-11,11}) do part(m,"PergolaBeam",V(30,.8,.8),V(x+side*29,10.8,z-29+dz),Color3.fromRGB(136,101,71),Enum.Material.Wood,false) end
   for k=-2,2 do
    ellipsoid(m,"PergolaVine",V(7,2.5,7),V(x+side*29+k*4,12,z-35+(k%2)*2),leaf,Enum.Material.Grass)
   end
   for k=0,3 do
    ellipsoid(m,"ClimbingVine",V(2.3,3,2.3),V(x+side*29-12,3+k*2.3,z-41),leaf,Enum.Material.Grass)
   end
   seat(side*29,-24);cafe(m,x+side*29,z+29,Color3.fromRGB(89,126,111));planter(side*29,47)
  end
 end
 for _,side in ipairs({-1,1}) do
  table.insert(activities,{position=V(x+side*29,4,z-9),kind=theme=="SculptureCourt" and "Watch" or "Rest"})
 end
end
local function block(parent,x,z,index,style,walk,activities)
 local m=model(parent,style.."Block_"..index);m:SetAttribute("RefinedFrontages",true);octagon(m,x,z);garden(m,x,z,index,activities)
 for _,side in ipairs({-1,1}) do
  for j,offset in ipairs({-40,40}) do
   building(m,CFrame.lookAt(V(x+offset,0,z+side*82),V(x+offset,0,z+side*150)),52,28,3+(index+j)%3,index*20+j+(side+1)*2,style)
   building(m,CFrame.lookAt(V(x+side*82,0,z+offset),V(x+side*150,0,z+offset)),52,28,3+(index+j+1)%3,index*20+7+j+(side+1)*2,style)
  end
 end
 for _,sx in ipairs({-1,1}) do for _,sz in ipairs({-1,1}) do
  building(m,CFrame.lookAt(V(x+sx*82.5,0,z+sz*82.5),V(x+sx*150,0,z+sz*150)),24,20,4+index%2,index*20+14+(sx+1)+(sz+1)*2,style)
 end end
 -- Perimeter paths never cross the buildings; courtyard entrances are between facades.
 for _,side in ipairs({-1,1}) do for _,n in ipairs({-70,0,70}) do
  table.insert(walk,V(x+n,4,z+side*101));table.insert(walk,V(x+side*101,4,z+n))
 end end
 table.insert(activities,{position=V(x,4,z),kind="Rest"})
 for _,dx in ipairs({-102,102}) do lamp(m,x+dx,z-60);tree(m,x+dx,z+42,false) end
 if index%2==0 then cafe(m,x+18,z+40,Color3.fromRGB(103,129,108)) end
end
local function oldTown(parent,x,z,index,walk,activities)
 local m=model(parent,"BornLanes_"..index);m:SetAttribute("RefinedFrontages",true);octagon(m,x,z)
 part(m,"OldTownPaving",V(185,.12,185),V(x,.88,z),Color3.fromRGB(179,163,139),Enum.Material.Cobblestone)
 -- Staggered, narrow houses create small lanes and a sheltered café court.
 for row=-1,1 do for col=-2,2 do
  if row==0 and math.abs(col)<2 then continue end
  local px=x+col*37+(row%2)*5;local pz=z+row*65
  local yaw=(row==1 and math.pi or 0)+(col%2==0 and .035 or -.035)
  building(m,CFrame.new(px,0,pz)*CFrame.Angles(0,yaw,0),29,32,2+(index+col+row)%3,index*100+row*10+col,"Born")
 end end
 for n=-2,2 do table.insert(walk,V(x+n*28,4,z+29));table.insert(walk,V(x+n*28,4,z-29)) end
 for _,dx in ipairs({-22,22}) do cafe(m,x+dx,z,Color3.fromRGB(132,77,61));tree(m,x+dx,z+12,false) end
 table.insert(activities,{position=V(x,4,z),kind="Browse"})
 for j=-2,2 do
  local cf=CFrame.new(x+j*25,17,z+27)
  part(m,"FestivalPennant",V(5,3,.12),cf,({cream,terra,Color3.fromRGB(81,144,147)})[(j+2)%3+1],Enum.Material.Fabric,false)
 end
 part(m,"FestivalString",V(120,.08,.08),V(x,18.5,z+27),iron,nil,false)
 sign(m,"CARRER DEL SOL",CFrame.new(x-60,6,z-48),19)
end
local function waterfrontHomes(parent,x,z,index,walk,activities)
 local m=model(parent,"MaritimeQuarter_"..index);m:SetAttribute("RefinedFrontages",true);octagon(m,x,z)
 for row=-1,1,2 do for j=-2,2 do
  building(m,CFrame.new(x+j*37,0,z+row*59)*CFrame.Angles(0,row==1 and math.pi or 0,0),31,32,2+(j+index)%2,index*100+j+row*10,"Born")
 end end
 for i=-3,3 do
  tree(m,x+i*26,z,true);table.insert(walk,V(x+i*26,4,z+14))
 end
 for _,dx in ipairs({-45,45}) do cafe(m,x+dx,z+26,Color3.fromRGB(74,132,154));table.insert(activities,{position=V(x+dx,4,z+20),kind="Rest"}) end
end
local function landmarkQuarter(parent,x,z,walk,activities)
 local m=model(parent,"TorreLlumQuarter");octagon(m,x,z)
 part(m,"InnovationGarden",V(185,.15,185),V(x,.9,z),Color3.fromRGB(106,135,83),Enum.Material.Grass)
 for _,dx in ipairs({-52,52}) do part(m,"PedestrianWalk",V(15,.1,185),V(x+dx,1,z),stone,Enum.Material.Pavement);table.insert(walk,V(x+dx,4,z)) end
 -- Original tapered glass landmark, a visible orientation point for the east district.
 for level=0,17 do
  local taper=level>12 and (level-12)*2.4 or 0
  cylinder(m,"TowerGlass",23-taper,7.7,V(x,5+level*8,z),Color3.fromRGB(64+level*2,112+level,130+level),Enum.Material.Glass)
  cylinder(m,"TowerSunshade",23.5-taper,.35,V(x,8.6+level*8,z),Color3.fromRGB(159,185,182),Enum.Material.Metal)
 end
 ellipsoid(m,"TowerCrown",V(23,17,23),V(x,146,z),Color3.fromRGB(100,154,170),Enum.Material.Glass)
 for _,dx in ipairs({-75,75}) do for _,dz in ipairs({-70,0,70}) do tree(m,x+dx,z+dz,false) end end
 for _,dz in ipairs({-65,65}) do building(m,CFrame.new(x,0,z+dz)*CFrame.Angles(0,dz>0 and math.pi or 0,0),70,24,2,700+dz,"Modernista") end
 for _,dx in ipairs({-50,50}) do bench(m,CFrame.new(x+dx,0,z+34));table.insert(activities,{position=V(x+dx,4,z+26),kind="Watch"}) end
end
local function fountain(parent,x,z)
 local avoid=part(parent,"FountainNavigation",V(32,9,32),V(x,4,z),stone,nil,false);avoid.Transparency=1;avoid.CanQuery=true
 local modifier=Instance.new("PathfindingModifier");modifier.Label="Fountain";modifier.Parent=avoid
 cylinder(parent,"FountainBasin",15,1,V(x,1.5,z),stone,Enum.Material.Marble)
 cylinder(parent,"FountainWater",13,.2,V(x,2.1,z),Color3.fromRGB(75,166,177),Enum.Material.Glass)
 cylinder(parent,"FountainPedestal",2,5,V(x,4,z),cream,Enum.Material.Marble)
 cylinder(parent,"FountainBowl",6,.7,V(x,6.4,z),stone,Enum.Material.Marble)
 for i=1,8 do local a=i*math.pi/4;local f=part(parent,"WaterJet",V(.15,3,.15),V(x+math.cos(a)*4,4.5,z+math.sin(a)*4),Color3.fromRGB(153,216,218),Enum.Material.Glass,false);f.Transparency=.35 end
end
local function square(parent,x,z,name,walk,activities)
 local m=model(parent,name);octagon(m,x,z)
 part(m,"SquareInlay",V(130,.08,130),CFrame.new(x,.86,z)*CFrame.Angles(0,math.pi/4,0),Color3.fromRGB(162,137,113),Enum.Material.Cobblestone)
 fountain(m,x,z)
 for i=1,8 do local a=i*math.pi/4;local px,pz=x+math.cos(a)*58,z+math.sin(a)*58
  tree(m,px,pz,false);bench(m,CFrame.lookAt(V(x+math.cos(a)*43,0,z+math.sin(a)*43),V(x,0,z)))
  table.insert(walk,V(x+math.cos(a)*32,4,z+math.sin(a)*32));table.insert(activities,{position=V(x+math.cos(a)*32,4,z+math.sin(a)*32),kind="Watch"})
 end
 for i=1,4 do cafe(m,x-75+i*30,z+81,Color3.fromRGB(116,93,70)) end
 sign(m,name:upper(),CFrame.new(x,7,z+98),34)
 return m
end
local function basilica(parent,x,z)
 local m=model(parent,"BasilicaDelSol")
 part(m,"BasilicaNave",V(70,50,112),V(x,26,z),Color3.fromRGB(191,165,123),Enum.Material.Limestone)
 for _,dx in ipairs({-30,-10,10,30}) do
  
  for tier=0,4 do cylinder(m,"CarvedSpire",6-tier*.9,18,V(x+dx,57+tier*18,z+49),stone,Enum.Material.Limestone) end
  ellipsoid(m,"MosaicFinial",V(5,12,5),V(x+dx,145,z+49),Color3.fromRGB(222,175,74),Enum.Material.CeramicTiles)
 end
 for _,side in ipairs({-1,1}) do for j=-3,3 do
  part(m,"FlyingButtress",V(3,43,5),CFrame.new(x+side*39,25,z+j*14)*CFrame.Angles(0,0,side*.12),stone,Enum.Material.Limestone)
  part(m,"StainedGlass",V(.3,25,5),V(x+side*35.2,26,z+j*14),j%2==0 and Color3.fromRGB(70,139,171) or Color3.fromRGB(204,125,77),Enum.Material.Glass,false)
 end end
 for _,dx in ipairs({-20,0,20}) do part(m,"ArchDoor",V(12,18,.4),V(x+dx,10,z+56.4),dark,Enum.Material.Wood) end
 sign(m,"BASÍLICA DEL SOL",CFrame.new(x,6,z+85)*CFrame.Angles(0,math.pi,0),30)
end
local function market(parent,x,z,walk,activities)
 local m=model(parent,"MercatDelMar");octagon(m,x,z)
 for _,sx in ipairs({-1,1}) do for j=-3,3 do part(m,"MarketColumn",V(1,23,1),V(x+sx*60,12,z+j*23),Color3.fromRGB(57,94,84),Enum.Material.Metal) end end
 for _,side in ipairs({-1,1}) do part(m,"MarketRoof",V(66,1,165),CFrame.new(x+side*30,27,z)*CFrame.Angles(0,0,side*-.16),Color3.fromRGB(109,137,118),Enum.Material.Metal) end
 for i=1,8 do
  local px=x+((i-1)%2==0 and -35 or 35);local pz=z-60+math.floor((i-1)/2)*39
  part(m,"ProduceStall",V(20,3,8),V(px,2.3,pz),Color3.fromRGB(141,97,65),Enum.Material.WoodPlanks)
  for j=-3,3 do ellipsoid(m,"Produce",V(1.8,1.5,1.8),V(px+j*2,4.4,pz),i%2==0 and Color3.fromRGB(213,117,64) or Color3.fromRGB(114,152,67),Enum.Material.SmoothPlastic) end
  sign(m,({"FRUITA","FLORS","PA FRESC","GELATS"})[(i-1)%4+1],CFrame.new(px,7,pz-4),18)
  table.insert(activities,{position=V(px,4,pz-11),kind="Browse"});table.insert(walk,V(px,4,pz-11))
 end
 sign(m,"MERCAT DEL MAR",CFrame.new(x,23,z-84),75)
end
local function streetBin(parent,x,z)
 local m=model(parent,"StreetBin")
 cylinder(m,"BinBody",1.1,3,V(x,2.3,z),Color3.fromRGB(66,100,98),Enum.Material.Metal)
 cylinder(m,"BinLid",1.2,.3,V(x,3.95,z),iron,Enum.Material.Metal)
 destructible(m,"Bin")
end
local function bicycle(parent,x,z)
 local m=model(parent,"Bicycle")
 for _,dx in ipairs({-2.5,2.5}) do
  local wheel=part(m,"BikeWheel",V(.4,3,3),CFrame.new(x+dx,2,z)*CFrame.Angles(0,math.pi/2,0),iron,Enum.Material.Rubber);wheel.Shape=Enum.PartType.Cylinder
 end
 part(m,"BikeFrame",V(5,.4,.5),CFrame.new(x,3,z)*CFrame.Angles(0,0,.15),Color3.fromRGB(185,106,75),Enum.Material.Metal)
 part(m,"BikeSeat",V(1.3,.3,1),V(x-1,4.1,z),iron)
 part(m,"Handlebar",V(.3,.3,2),V(x+2.5,4.4,z),iron,Enum.Material.Metal)
 part(m,"Fork",V(.35,3,.35),V(x+2.5,3,z),iron,Enum.Material.Metal)
 destructible(m,"Bike")
end
local function coastalLookout(parent,walk,activities)
 local m=model(parent,"LifeguardLookout")
 local blue=Color3.fromRGB(112,173,181)
 -- A small open station, with a clear stair approach from the promenade.
 part(m,"LookoutDeck",V(22,.6,20),V(-240,3,458),Color3.fromRGB(160,126,87),Enum.Material.WoodPlanks)
 for _,x in ipairs({-249,-231}) do for _,z in ipairs({451,465}) do
  part(m,"LookoutSupport",V(.8,2.7,.8),V(x,1.65,z),dark,Enum.Material.Wood)
 end end
 for i=1,5 do
  local top=1+i*.46
  part(m,"LookoutStair",V(8,top-1,3.6),V(-240,(top+1)/2,430+i*3.6),Color3.fromRGB(160,126,87),Enum.Material.WoodPlanks)
 end
 for _,x in ipairs({-250.5,-229.5}) do
  part(m,"DeckRail",V(.3,.3,19),V(x,6,458),cream,Enum.Material.Wood)
  for _,z in ipairs({449,458,467}) do part(m,"DeckRailPost",V(.3,2.8,.3),V(x,4.7,z),cream,Enum.Material.Wood) end
 end
 -- Solid wall below windows, open doorway and shaded public balcony.
 part(m,"CabinBack",V(14,9,.4),V(-240,7.8,466),blue,Enum.Material.WoodPlanks)
 for _,x in ipairs({-247,-233}) do
  part(m,"CabinSideBase",V(.4,3,10),V(x,4.8,461),blue,Enum.Material.WoodPlanks)
  part(m,"CabinSideLintel",V(.4,.8,10),V(x,11.9,461),cream,Enum.Material.Wood)
  for _,z in ipairs({456,461,466}) do part(m,"WindowMullion",V(.35,5.2,.35),V(x,8.9,z),cream,Enum.Material.Wood) end
 end
 for _,x in ipairs({-245.5,-234.5}) do part(m,"DoorSide",V(3,9,.4),V(x,7.8,456),blue,Enum.Material.WoodPlanks) end
 part(m,"DoorLintel",V(8,1,.4),V(-240,11.8,456),cream,Enum.Material.Wood)
 part(m,"LifeguardRoof",V(19,.6,15),CFrame.new(-240,12.9,461)*CFrame.Angles(.08,0,0),terra,Enum.Material.RoofShingles)
 part(m,"FirstAidBox",V(2.4,2,.4),V(-243,6.7,465.6),cream,Enum.Material.Metal,false)
 part(m,"AidCross",V(1.4,.35,.1),V(-243,6.7,465.33),terra,nil,false)
 part(m,"AidCross",V(.35,1.4,.1),V(-243,6.7,465.32),terra,nil,false)
 sign(m,"SOCORRISME",CFrame.new(-240,11.6,455.7),12)
 cylinder(m,"Flagpole",.12,15,V(-251,8.5,465),iron,Enum.Material.Metal)
 part(m,"BeachFlag",V(4,2.5,.08),V(-249,14.3,465),Color3.fromRGB(242,201,97),Enum.Material.Fabric,false)
 table.insert(walk,V(-240,4,430));table.insert(walk,V(-240,6.3,452))
 table.insert(activities,{position=V(-240,6.3,452),kind="Watch"})
end
-- Two thin right-triangle wedges form one original fabric triangle.
local function fabricTriangle(parent,a,b,c,color)
 local ab,ac,bc=b-a,c-a,c-b
 if ab:Dot(ab)>ac:Dot(ac) and ab:Dot(ab)>bc:Dot(bc) then a,c=c,a
 elseif ac:Dot(ac)>bc:Dot(bc) then a,b=b,a end
 ab,ac,bc=b-a,c-a,c-b
 local right=ac:Cross(ab).Unit;local back=bc.Unit;local up=back:Cross(right).Unit
 local height=math.abs(ab:Dot(up))
 for _,spec in ipairs({{(a+b)/2,right,back,math.abs(ab:Dot(back))},{(a+c)/2,-right,-back,math.abs(ac:Dot(back))}}) do
  local w=Instance.new("WedgePart");w.Name="ParasolFabric";w.Size=V(.06,height,spec[4]);w.CFrame=CFrame.fromMatrix(spec[1],spec[2],up,spec[3]);w.Color=color;w.Material=Enum.Material.Fabric;w.Anchored=true;w.CanCollide=false;w.CanQuery=false;w.CanTouch=false;w.Parent=parent
 end
end
local function parasol(parent,x,z,color)
 local m=model(parent,"StripedBeachParasol")
 cylinder(m,"ParasolPole",.12,7.6,V(x,4.8,z),cream,Enum.Material.Wood)
 cylinder(m,"ParasolFoot",.6,.2,V(x,1.1,z),stone,Enum.Material.Concrete)
 local crown=V(x,8.65,z)
 for j=0,7 do
  local a=j*math.pi/4;local b=(j+1)*math.pi/4
  local edgeA=V(x+math.cos(a)*6,6.9,z+math.sin(a)*6)
  local edgeB=V(x+math.cos(b)*6,6.9,z+math.sin(b)*6)
  local stripe=j%2==0 and color or cream
  fabricTriangle(m,crown,edgeA,edgeB,stripe)
  local middle=(edgeA+edgeB)/2
  part(m,"CanopyValance",V((edgeA-edgeB).Magnitude,.45,.06),CFrame.lookAt(middle-V(0,.2,0),V(x,middle.Y-.2,z)),stripe,Enum.Material.Fabric,false)
  if j%2==0 then
   local tip=edgeA-V(0,.06,0);local start=crown-V(0,.08,0)
   part(m,"CanopyRib",V(.07,.07,(tip-start).Magnitude),CFrame.lookAt((tip+start)/2,tip),stone,Enum.Material.Wood,false)
  end
 end
 ellipsoid(m,"ParasolFinial",V(.35,.5,.35),crown+V(0,.2,0),cream,Enum.Material.Wood)
end
local function coast(parent,walk,activities)
 local m=model(parent,"BarcelonetaCoast")
 part(m,"Beach",V(1440,3,170),V(0,-.5,515),Color3.fromRGB(227,208,156),Enum.Material.Sand)
 -- Bounded tiles avoid oversized-Part clamping and keep the distant horizon loaded.
 local sea=model(m,"MediterraneanBackdrop");sea.ModelStreamingMode=Enum.ModelStreamingMode.Persistent
 for x=-2000,2000,2000 do for z=1600,5600,2000 do
  part(sea,"Mediterranean",V(2000,1,2000),V(x,-1,z),Color3.fromRGB(48,143,169),Enum.Material.Glass,false).Transparency=.16
 end end
 part(m,"PasseigMaritim",V(1440,1,52),V(0,.25,401),Color3.fromRGB(197,176,141),Enum.Material.Pavement)
 for x=-680,680,40 do
  part(m,"PromenadeTileBand",V(1,.05,52),V(x,.79,401),Color3.fromRGB(152,138,117),Enum.Material.Cobblestone,false)
  if x%80==0 then tree(m,x,421,true);lamp(m,x,380);bench(m,CFrame.new(x+14,0,412));streetBin(m,x+22,412);if x%160==0 then bicycle(m,x-12,414) end end
  table.insert(walk,V(x,3.8,403));table.insert(activities,{position=V(x,3.8,407),kind="Stroll"})
 end
 for i=1,18 do
  local x=-660+(i-1)*77;local z=470+(i%3)*25;local color=i%2==0 and Color3.fromRGB(215,116,85) or Color3.fromRGB(78,153,157)
  parasol(m,x,z,color)
  part(m,"BeachLounger",V(3,.5,7),V(x+4,1.6,z+5),cream,Enum.Material.Fabric)
  part(m,"LoungerBack",V(3,3,.4),CFrame.new(x+4,2.8,z+8)*CFrame.Angles(.4,0,0),color,Enum.Material.Fabric)
  for _,dx in ipairs({-1.65,1.65}) do
   part(m,"LoungerSideRail",V(.2,.3,7.6),V(x+4+dx,1.55,z+5),stone,Enum.Material.Wood)
   for _,dz in ipairs({-2.5,2.5}) do part(m,"LoungerLeg",V(.2,.55,.3),V(x+4+dx,1.25,z+5+dz),stone,Enum.Material.Wood) end
  end
  if i%2==0 then
   part(m,"BeachTowel",V(2.4,.04,3.3),V(x+4,1.88,z+3.5),color,Enum.Material.Fabric,false)
   cylinder(m,"BeachSideTable",1.1,.2,V(x+7,2.2,z+6),stone,Enum.Material.Wood)
   cylinder(m,"BeachTableLeg",.15,1.1,V(x+7,1.65,z+6),cream,Enum.Material.Wood)
   cylinder(m,"WaterCup",.22,.5,V(x+7,2.55,z+6),color,Enum.Material.SmoothPlastic)
  end
  local seat=Instance.new("Seat");seat.Name="BeachSeat";seat:SetAttribute("RestSetting","Beach");seat.Size=V(2.5,.2,2);seat.CFrame=CFrame.new(x+4,2,z+5);seat.Anchored=true;seat.Transparency=1;seat.CanCollide=false;seat.Parent=m
  local prompt=Instance.new("ProximityPrompt");prompt.ActionText="Sit";prompt.ObjectText="Beach lounger";prompt.KeyboardKeyCode=Enum.KeyCode.F;prompt.MaxActivationDistance=7;prompt.Parent=seat
  prompt.Triggered:Connect(function(player)
   local character=player.Character;local humanoid=character and character:FindFirstChildOfClass("Humanoid");local root=character and character:FindFirstChild("HumanoidRootPart")
   if humanoid and humanoid.Health>0 and root and not seat.Occupant and (root.Position-seat.Position).Magnitude<9 then seat:Sit(humanoid) end
  end)
  if i%3==1 then table.insert(walk,V(x+4,4,z-2));table.insert(activities,{position=V(x+4,4,z-2),kind="Rest"}) end
  if i%3==0 and x<590 then ellipsoid(m,"SandDune",V(27,4,18),V(x,.7,565),Color3.fromRGB(219,200,148),Enum.Material.Sand) end
 end
 for x=-700,700,60 do local p=part(m,"SurfLine",V(40,.05,1.2),V(x,.08,600),Color3.fromRGB(214,235,225),nil,false);p.Transparency=.35 end
 part(m,"TimberPier",V(28,1.5,125),V(525,1.5,537),Color3.fromRGB(144,113,78),Enum.Material.WoodPlanks)
 for i=1,3 do
  local top=1+i*(1.25/3)
  part(m,"PierApproachStep",V(20,top-1,3),V(525,(top+1)/2,466+i*3),Color3.fromRGB(144,113,78),Enum.Material.WoodPlanks)
 end
 for z=480,590,22 do for _,x in ipairs({511,539}) do cylinder(m,"PierPost",.4,6,V(x,2,z),dark,Enum.Material.Wood) end end
 for _,x in ipairs({511,539}) do part(m,"PierRail",V(.5,.5,110),V(x,4,535),stone,Enum.Material.Wood) end
 table.insert(walk,V(525,5,481));table.insert(walk,V(525,5,580))
 table.insert(activities,{position=V(525,5,580),kind="Watch"})
 -- Café and performance terrace are entirely pedestrian.
 building(m,CFrame.new(-480,0,399)*CFrame.Angles(0,math.pi,0),48,23,1,501,"Marina")
 for i=1,4 do cafe(m,-522+i*17,439,Color3.fromRGB(59,115,106)) end
 part(m,"EncoreStage",V(32,1.5,20),V(150,1.7,428),dark,Enum.Material.WoodPlanks)
 for _,x in ipairs({136,164}) do part(m,"StageSpeaker",V(3,6,3),V(x,5,433),iron,Enum.Material.Metal) end
 sign(m,"MÚSICA A LA MAR",CFrame.new(150,8,437)*CFrame.Angles(0,math.pi,0),30)
 coastalLookout(m,walk,activities)
 for _,x in ipairs({-70,-30}) do cylinder(m,"VolleyballPost",.3,9,V(x,5.5,505),iron,Enum.Material.Metal) end
 for y=5,9 do part(m,"VolleyballNet",V(40,.1,.1),V(-50,y,505),cream,nil,false) end
 for x=-70,-30,2 do part(m,"VolleyballNet",V(.1,4,.1),V(x,7,505),cream,nil,false) end
 return m
end
-- Hand-placed work sites: positions are pedestrian interiors, not traffic lanes.
local function workplaces(parent)
 local m=model(parent,"NeighborhoodWorkplaces")
 local beds={}
 for _,z in ipairs({228,250,272}) do
  local bed=part(m,"RaisedPlanter",V(10,1.5,7),V(-423,1.75,z),terra,Enum.Material.Brick)
  bed.Name="Flowerbed"..z;bed:SetAttribute("QuestAction","Garden")
  local prompt=Instance.new("ProximityPrompt");prompt.ActionText="Water flowers";prompt.ObjectText="Community garden";prompt.KeyboardKeyCode=Enum.KeyCode.F;prompt.HoldDuration=1.5;prompt.MaxActivationDistance=10;prompt.Parent=bed
  part(m,"PottingSoil",V(9,.15,6),V(-423,2.58,z),Color3.fromRGB(83,66,48),Enum.Material.Ground)
  for dx=-3,3,3 do for dz=-1.5,1.5,3 do
   cylinder(m,"FlowerStem",.09,1.1,V(-423+dx,3.1,z+dz),leaf,Enum.Material.Grass)
   ellipsoid(m,"Flowers",V(.9,.4,.9),V(-423+dx,3.7,z+dz),Color3.fromRGB(224,123+dx*8,148),Enum.Material.Grass)
  end end
  table.insert(beds,{position=V(-414,4,z),lookAt=V(-423,3,z)})
 end
 part(m,"GardenSupplyCrate",V(5,2,4),V(-422,2,289),stone,Enum.Material.WoodPlanks)
 -- A side court tucked behind the east promenade, reached from the pier path.
 part(m,"CoastalCourt",V(116,.2,90),V(648,1.1,545),Color3.fromRGB(188,157,109),Enum.Material.Sand)
 for _,z in ipairs({502,587}) do part(m,"CourtTouchline",V(112,.04,.3),V(648,1.25,z),cream,nil,false) end
 for _,x in ipairs({592,704}) do part(m,"CourtTouchline",V(.3,.04,85),V(x,1.25,544.5),cream,nil,false) end
 for _,x in ipairs({620,636}) do cylinder(m,"GoalPost",.18,7,V(x,4.5,585),cream,Enum.Material.Metal) end
 part(m,"GoalCrossbar",V(16,.35,.35),V(628,8,585),cream,Enum.Material.Metal)
 sign(m,"NO BALL GAMES? NICK DID NOT READ THIS.",CFrame.new(701,4,590)*CFrame.Angles(0,math.pi,0),17)
 local artist=V(-647,4,173.5)
 for _,dx in ipairs({-1.4,1.4}) do part(m,"EaselLeg",V(.2,5,.3),CFrame.new(-647+dx,3.5,171)*CFrame.Angles(0,0,dx*.08),terra,Enum.Material.Wood) end
 part(m,"EaselCanvas",V(4,3,.25),V(-647,5,171),cream,Enum.Material.Fabric)
 -- Original little coastal painting, visible from the pedestrian side.
 part(m,"PaintedSky",V(3.6,1.4,.04),V(-647,5.6,171.15),Color3.fromRGB(128,202,220),nil,false)
 part(m,"PaintedSea",V(3.6,1,.04),V(-647,4.45,171.15),Color3.fromRGB(62,143,166),nil,false)
 part(m,"PaintedSun",V(.55,.55,.05),V(-648,5.9,171.19),Color3.fromRGB(247,197,95),nil,false).Shape=Enum.PartType.Ball
 for i=1,4 do part(m,"PaintedHomes",V(.55,.6+i*.08,.05),V(-648.4+i*.65,4.95,171.2),palette[i],nil,false) end
 return {
  {role="CafeWorker",name="Júlia Ferrer",stations={{position=V(-480,4,399),lookAt=V(-460,3,399),action="Preparing coffee"},{position=V(-491,4,435),lookAt=V(-488,3,439),action="Serving the terrace"}}},
  {role="Sanitation",name="Biel Roca",stations={{position=V(262,4,406),lookAt=V(262,3,412),action="Sweeping the promenade"},{position=V(182,4,406),lookAt=V(182,3,412),action="Restocking the bins"},{position=V(22,4,406),lookAt=V(22,3,412),action="Checking the street furniture"}}},
  {role="BeachWorker",name="Nora Marín",stations={{position=V(-577,4,521),lookAt=V(-579,2,525),action="Checking beach loungers"},{position=V(-500,4,471),lookAt=V(-502,2,475),action="Tidying the beach"}}},
  {role="Busker",name="Èric Sol",stations={{position=V(150,5.5,426),lookAt=V(150,4,409),action="Playing for the promenade"}}},
  {role="Soccer",name="Nick Booty",quests={"nick"},stations={{position=V(602,4,580),lookAt=V(628,3,585)}}},
  {role="Gardener",name="Mar Soler",quests={"garden","beach"},stations=beds},
  {role="Artist",name="Laia Costa",stations={{position=artist,lookAt=V(-647,5,171)}}},
  {role="Vendor",name="Pau Vidal",quests={"delivery"},stations={{position=V(85,4,-52),lookAt=V(85,4,-60)},{position=V(91,4,-52),lookAt=V(91,4,-60)}}},
 }
end
function City.Build(parent)
 rng=Random.new(230926)
 local walk,activities={},{}
 local ground=part(parent,"CityLand",V(1440,3,1200),V(0,-1.6,0),Color3.fromRGB(126,139,108),Enum.Material.Ground)
 ground:SetAttribute("GroundSurface",true)
 local backdrop=model(parent,"CoastalBackdrop")
 part(backdrop,"Mainland",V(5200,10,2500),V(0,-7,-1850),Color3.fromRGB(105,127,91),Enum.Material.Grass)
 for i=-5,5 do
  ellipsoid(backdrop,"CollserolaRidge",V(1300,480+(i%3)*80,1400),V(i*490,-175,-2350-math.abs(i)*70),Color3.fromRGB(105,129,106),Enum.Material.Grass)
 end
 local roads=model(parent,"Boulevards")
 for x=-720,720,240 do part(roads,"TrafficAvenue",V(28,.2,960),V(x,0,-120),Color3.fromRGB(64,65,61),Enum.Material.Asphalt) end
 for z=-600,360,240 do part(roads,"TrafficStreet",V(1440,.2,28),V(0,.01,z),Color3.fromRGB(64,65,61),Enum.Material.Asphalt) end
 for x=-700,700,24 do for _,z in ipairs({-360,120,360}) do part(roads,"LaneMark",V(10,.03,.16),V(x,.14,z),cream,nil,false) end end
 for x=-480,480,240 do for z=-360,360,240 do
  for d=-8,8,4 do part(roads,"Crosswalk",V(2,.03,7),V(x+d,.15,z+21),cream,nil,false);part(roads,"Crosswalk",V(7,.03,2),V(x+21,.15,z+d),cream,nil,false) end
 end end
 local index=0
 for z=-480,240,240 do for x=-600,600,240 do
  index+=1
  if x==-600 and z==240 then square(parent,x,z,"Plaça del Sol",walk,activities)
  elseif x==-120 and z==0 then square(parent,x,z,"Plaça Central",walk,activities)
  elseif x==120 and z==0 then market(parent,x,z,walk,activities)
  elseif x==120 and z==-240 then
   local m=model(parent,"BasilicaSquare");octagon(m,x,z);basilica(m,x,z)
   for _,dx in ipairs({-93,93}) do table.insert(walk,V(x+dx,4,z));tree(m,x+dx,z+60,false) end
  elseif x==-360 and z==240 then
   local m=model(parent,"RamblaGardens");octagon(m,x,z)
   part(m,"RamblaWalk",V(50,.15,200),V(x,1,z),Color3.fromRGB(221,202,164),Enum.Material.Cobblestone)
   for n=-80,80,32 do tree(m,x-35,z+n,false);tree(m,x+35,z+n,false);bench(m,CFrame.new(x+22,0,z+n));table.insert(walk,V(x,4,z+n));table.insert(activities,{position=V(x,4,z+n),kind="Watch"}) end
  elseif x==600 and z==-240 then landmarkQuarter(parent,x,z,walk,activities)
  elseif x>=360 and z==0 then oldTown(parent,x,z,index,walk,activities)
  elseif x>=120 and z==240 then waterfrontHomes(parent,x,z,index,walk,activities)
  else block(parent,x,z,index,(x<0 and z<0) and "Modernista" or (x>300 and z>0) and "Born" or "Eixample",walk,activities) end
 end end
 coast(parent,walk,activities)
 -- Continuous border markings stay flat; warning plaques are on pedestrian corners.
 local red=Color3.fromRGB(209,107,83)
 for _,x in ipairs({-480,480}) do part(parent,"PvPPavingBoundary",V(.45,.04,720),V(x,.19,0),red,nil,false) end
 for _,z in ipairs({-360,360}) do part(parent,"PvPPavingBoundary",V(960,.04,.45),V(0,.19,z),red,nil,false) end
 for _,x in ipairs({-448,448}) do for _,z in ipairs({-332,332}) do sign(parent,"ARENA DISTRICT • PvP",CFrame.new(x,5,z),24) end end
 local quests=Instance.new("Folder");quests.Name="QuestObjects";quests.Parent=parent
 local function marker(name,kind,pos,text)
  local p=part(quests,name,V(1,1.6,1),pos,kind=="Litter" and Color3.fromRGB(65,145,143) or Color3.fromRGB(226,181,83),Enum.Material.Glass,false);p:SetAttribute("QuestAction",kind)
  local prompt=Instance.new("ProximityPrompt");prompt.ActionText=text;prompt.ObjectText=name;prompt.KeyboardKeyCode=Enum.KeyCode.F;prompt.MaxActivationDistance=10;prompt.HoldDuration=.25;prompt.RequiresLineOfSight=false;prompt.Parent=p
 end
 for i=1,6 do marker("Bottle"..i,"Litter",V(-380+i*115,1.9,535+(i%2)*25),"Collect bottle") end
 marker("CoffeeOrder","Pickup",V(-480,2,414),"Pick up coffee")
 marker("StageDelivery","Dropoff",V(150,2,403),"Deliver coffee")
 marker("BoardwalkStart","RaceStart",V(-240,2,403),"Start 25s dash")
 marker("PierFinish","RaceFinish",V(240,2,403),"Finish dash")
 -- Boundaries sit outside street edges, never across an interior road.
 for _,x in ipairs({-725,725}) do part(parent,"MapEdge",V(2,140,1210),V(x,68,0),dark).Transparency=1 end
 for _,z in ipairs({-605,605}) do part(parent,"MapEdge",V(1450,140,2),V(0,68,z),dark).Transparency=1 end
 return {jobs=workplaces(parent),walk=walk,activities=activities,spawn=CFrame.new(-600,4,210)}
end
-- Small review scene; never called by gameplay world generation.
function City.BuildFrontageSample(parent)
 parent:SetAttribute("RefinedFrontages",true)
 part(parent,"ReviewSidewalk",V(170,1,65),V(0,0,0),stone,Enum.Material.Pavement)
 for i=0,3 do building(parent,CFrame.new(-60+i*40,0,8),34,25,3+i%2,800+i,"Eixample") end
 for _,x in ipairs({-78,78}) do tree(parent,x,-15,false);lamp(parent,x,-22) end
end
return City
