-- North is -Z. Coordinates match City's 1440-by-1200 playable land.
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
local function position(x,z) return UDim2.fromScale(math.clamp((x+720)/1440,0,1),math.clamp((z+600)/1200,0,1)) end
local landmarks={
 {name='1 · Plaça del Sol / spawn',x=-600,z=240},
 {name='2 · Rambla gardens',x=-360,z=240},
 {name='3 · Basilica',x=120,z=-240},
 {name='4 · Market',x=120,z=0},
 {name='5 · Old town',x=600,z=0},
 {name='6 · Beach & promenade',x=0,z=515},
}
function CityMap.create(parent)
 local map=box(parent,'CityMap',.5,.5,1,1,Color3.fromRGB(50,93,82));map.AnchorPoint=Vector2.new(.5,.5)
 local ratio=Instance.new('UIAspectRatioConstraint');ratio.AspectRatio=1.2;ratio.AspectType=Enum.AspectType.FitWithinMaxSize;ratio.Parent=map
 box(map,'Arena',1/6,.2,2/3,.6,Color3.fromRGB(136,65,70))
 box(map,'Beach',0,1030/1200,1,170/1200,Color3.fromRGB(179,153,104))
 -- Street widths and extents are world-derived, not decorative subdivisions.
 for x=-720,720,240 do box(map,'Avenue',math.max(0,(x+720-14)/1440),0,(x==-720 or x==720) and 14/1440 or 28/1440,.8,Color3.fromRGB(34,47,54)) end
 for z=-600,360,240 do box(map,'Street',0,math.max(0,(z+600-14)/1200),1,z==-600 and 14/1200 or 28/1200,Color3.fromRGB(34,47,54)) end
 local boundary=box(map,'ArenaBoundary',1/6,.2,2/3,.6,cream);boundary.BackgroundTransparency=1
 local stroke=Instance.new('UIStroke');stroke.Color=Color3.fromRGB(247,139,120);stroke.Thickness=2;stroke.Parent=boundary
 local north=box(map,'North',.04,.025,.25,.075,cream);north.BackgroundTransparency=1;text(north,'N ↑',13)
 for i,v in ipairs(landmarks) do
  local pin=box(map,'Landmark'..i,0,0,0,0,Color3.fromRGB(22,39,46));pin.Size=UDim2.fromOffset(23,23);pin.AnchorPoint=Vector2.new(.5,.5);pin.Position=position(v.x,v.z)
  local corner=Instance.new('UICorner');corner.CornerRadius=UDim.new(1,0);corner.Parent=pin;text(pin,tostring(i),13)
 end
 local dot=box(map,'Player',0,0,0,0,gold);dot.Size=UDim2.fromOffset(18,18);dot.AnchorPoint=Vector2.new(.5,.5);dot.ZIndex=5
 local corner=Instance.new('UICorner');corner.CornerRadius=UDim.new(1,0);corner.Parent=dot
 local arrow=text(dot,'▲',14,Color3.fromRGB(19,32,40));arrow.ZIndex=6
 return {map=map,dot=dot,arrow=arrow}
end
function CityMap.update(view,root)
 if not view or not view.map.Parent then return end
 view.dot.Visible=root~=nil
 if not root then return end
 view.dot.Position=position(root.Position.X,root.Position.Z)
 local look=root.CFrame.LookVector
 view.arrow.Rotation=math.deg(math.atan2(look.X,-look.Z))
end
CityMap.legend='1  Plaça del Sol / spawn     2  Rambla gardens\n3  Basilica     4  Market     5  Old town\n6  Beach & promenade'
return CityMap
