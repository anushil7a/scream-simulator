-- North is -Z. Use the selected world's bounds; retain the archived-city projection when disabled.
local Config=require(game:GetService("ReplicatedStorage"):WaitForChild("Shared"):WaitForChild("Config"))
local CityMap={}
local gold=Color3.fromRGB(255,205,111)
local cream=Color3.fromRGB(239,244,240)
local function box(parent,name,x,z,w,h,color)
 local f=Instance.new('Frame');f.Name=name;f.BorderSizePixel=0;f.BackgroundColor3=color
 f.Position=UDim2.fromScale(x,z);f.Size=UDim2.fromScale(w,h);f.Parent=parent;return f
end
local function text(parent,value,size,color)
 local t=Instance.new('TextLabel');t.BackgroundTransparency=1;t.Size=UDim2.fromScale(1,1)
 t.Font=Enum.Font.GothamBold;t.Text=value;t.TextSize=size;t.TextColor3=color or cream;t.Parent=parent;return t
end
local function position(x,z)
 local minimum=Config.CompactCity and Config.MapMin
 local maximum=Config.CompactCity and Config.MapMax
 local minX,minZ=minimum and minimum.X or -720,minimum and minimum.Z or -600
 local width,depth=maximum and maximum.X-minX or 1440,maximum and maximum.Z-minZ or 1200
 return UDim2.fromScale(math.clamp((x-minX)/width,0,1),math.clamp((z-minZ)/depth,0,1))
end
CityMap.Project=position
CityMap.aspectRatio=Config.CompactCity and (Config.MapMax.X-Config.MapMin.X)/(Config.MapMax.Z-Config.MapMin.Z) or 1.2
local arenaStart=position(Config.ZoneMin.X,Config.ZoneMin.Z)
local arenaEnd=position(Config.ZoneMax.X,Config.ZoneMax.Z)
local arenaX,arenaZ=arenaStart.X.Scale,arenaStart.Y.Scale
local arenaWidth,arenaHeight=arenaEnd.X.Scale-arenaX,arenaEnd.Y.Scale-arenaZ
CityMap.arenaPercent=math.floor(arenaWidth*arenaHeight*100+.5)
local CompactLayout=Config.CompactCity and require(game:GetService("ReplicatedStorage"):WaitForChild("Shared"):WaitForChild("CompactLayout"))
local landmarks=CompactLayout and CompactLayout.MapLandmarks or {
 {name='1 · Plaça del Sol / spawn',x=-600,z=240},
 {name='2 · Rambla gardens',x=-360,z=240},
 {name='3 · Basilica',x=120,z=-240},
 {name='4 · Market',x=120,z=0},
 {name='5 · Old town',x=600,z=0},
 {name='6 · Beach & promenade',x=0,z=515},
 {name='7 · Timber pier',x=525,z=537},
 {name='8 · Training fighters',x=-320,z=545},
}
function CityMap.create(parent,compact)
 local map=box(parent,'CityMap',.5,.5,1,1,Color3.fromRGB(50,93,82));map.AnchorPoint=Vector2.new(.5,.5)
 local ratio=Instance.new('UIAspectRatioConstraint');ratio.AspectRatio=CityMap.aspectRatio;ratio.AspectType=Enum.AspectType.FitWithinMaxSize;ratio.Parent=map
 box(map,'Arena',arenaX,arenaZ,arenaWidth,arenaHeight,Color3.fromRGB(136,65,70))
 if CompactLayout then
  local width=Config.MapMax.X-Config.MapMin.X;local depth=Config.MapMax.Z-Config.MapMin.Z
  -- Match the actual shared beach footprint instead of the legacy shoreline.
  for _,part in ipairs(CompactLayout.PartSpecs) do
   if part.id=="Beach" then
    local start=position(part.position.X-part.size.X/2,part.position.Z-part.size.Z/2)
    box(map,'Beach',start.X.Scale,start.Y.Scale,part.size.X/width,part.size.Z/depth,Color3.fromRGB(179,153,104))
   end
  end
  for _,road in ipairs(CompactLayout.MapRoads) do
   local start=position(road.x-road.width/2,road.z-road.depth/2)
   box(map,road.name,start.X.Scale,start.Y.Scale,road.width/width,road.depth/depth,Color3.fromRGB(197,176,141))
  end
 else
 box(map,'Beach',0,1030/1200,1,170/1200,Color3.fromRGB(179,153,104))
 -- PasseigMaritim and TimberPier dimensions mirror the generated waterfront.
 box(map,'Promenade',0,(401-26+600)/1200,1,52/1200,Color3.fromRGB(197,176,141))
 box(map,'TimberPier',(525-14+720)/1440,(537-62.5+600)/1200,28/1440,125/1200,Color3.fromRGB(111,82,56))
 -- Street widths and extents are world-derived, not decorative subdivisions.
 for x=-720,720,240 do box(map,'Avenue',math.max(0,(x+720-14)/1440),0,(x==-720 or x==720) and 14/1440 or 28/1440,.8,Color3.fromRGB(34,47,54)) end
 for z=-600,360,240 do box(map,'Street',0,math.max(0,(z+600-14)/1200),1,z==-600 and 14/1200 or 28/1200,Color3.fromRGB(34,47,54)) end
 end
 local boundary=box(map,'ArenaBoundary',arenaX,arenaZ,arenaWidth,arenaHeight,cream);boundary.BackgroundTransparency=1
 local stroke=Instance.new('UIStroke');stroke.Color=Color3.fromRGB(247,139,120);stroke.Thickness=2;stroke.Parent=boundary
 local north=box(map,'North',.04,.025,.25,.075,cream);north.BackgroundTransparency=1;text(north,'N ↑',13)
 for i,v in ipairs(compact and {} or landmarks) do
  local pin=box(map,'Landmark'..i,0,0,0,0,Color3.fromRGB(22,39,46));pin.Size=UDim2.fromOffset(23,23);pin.AnchorPoint=Vector2.new(.5,.5);pin.Position=position(v.x,v.z)
  local corner=Instance.new('UICorner');corner.CornerRadius=UDim.new(1,0);corner.Parent=pin;text(pin,tostring(i),13)
 end
 local dot=box(map,'Player',0,0,0,0,gold);dot.Size=UDim2.fromOffset(18,18);dot.AnchorPoint=Vector2.new(.5,.5);dot.ZIndex=5
 dot.Visible=false
 local corner=Instance.new('UICorner');corner.CornerRadius=UDim.new(1,0);corner.Parent=dot
 local arrow=text(dot,'▲',14,Color3.fromRGB(19,32,40));arrow.ZIndex=6
 return {map=map,dot=dot,arrow=arrow}
end
function CityMap.update(view,root)
 if not view or not view.map.Parent then return end
 view.dot.Visible=root~=nil and root.Parent~=nil
 if not view.dot.Visible then return end
 view.dot.Position=position(root.Position.X,root.Position.Z)
 local look=root.CFrame.LookVector
 view.arrow.Rotation=math.deg(math.atan2(look.X,-look.Z))
end
-- Reserve the compact HUD's left column and combat/talk controls below.
function CityMap.MiniLayout(viewport,touch)
 local available=viewport.X>=280 and viewport.Y>=(touch and 315 or 168)
 local width=math.min(160,viewport.X-278)
 -- The quest tracker is wider than the HUD. Stay above it or to its right.
 width=math.min(width,math.max(119,viewport.X-328))
 if touch then width=math.min(width,(viewport.Y-269)*CityMap.aspectRatio+16) end
 local expanded=width>=96 and viewport.Y>=360
 if not expanded then return {width=math.min(90,math.max(44,viewport.X-220)),height=44,expanded=false,available=available} end
 return {width=width,height=52+(width-16)/CityMap.aspectRatio,expanded=true,available=available}
end
function CityMap.MiniUpdate(view,root,now,visible)
 if not view or not view.map.Parent then return end
 if not visible or not root or not root.Parent then
  view.dot.Visible=false;view.nextUpdate=nil;view.lastRoot=nil;return
 end
 if view.lastRoot==root and view.nextUpdate and now<view.nextUpdate then return end
 view.lastRoot=root;view.nextUpdate=now+.1
 CityMap.update(view,root)
end
CityMap.legend='1  Plaça del Sol / spawn     2  Rambla gardens\n3  Basilica     4  Market     5  Old town\n6  Beach & promenade     7  Timber pier\n8  Training fighters (west beach)'
CityMap.legendHeight=94
CityMap.mapHelp="Gold arrow: you and your facing direction. Red: PvP. Green and sand: safe. Pale coast path: promenade. North is up."
CityMap.activityHelp="Coffee: collect at the west café, then check your objective for the assigned stop. Race: lifeguard start to east promenade finish. PvP ends at the marked district boundary."
if CompactLayout then
 CityMap.mapHelp="Gold arrow: you and your facing direction. Red: PvP arena. Pale paths connect the courtyard, market and coast. North is up."
 CityMap.activityHelp="Coffee: collect at the north market, then follow your assigned stop. Training is in the west courtyard. Race starts on the west promenade. PvP ends at the marked arena boundary."
 CityMap.legendHeight=#landmarks*20+24
 local lines={}
 for _,landmark in ipairs(landmarks) do table.insert(lines,landmark.name) end
 CityMap.legend=table.concat(lines,"\n")
end
return CityMap
