-- Local preview map. The two panels are connected by portals in the place.
local Config=require(game:GetService("ReplicatedStorage").Shared.Config)
local Layout=assert(Config.ResonanceLayout)
local Base=require(script.Parent.CityMapBase)
local Map={
 aspectRatio=1.2,
 MiniLayout=Base.MiniLayout,
 mapHelp="Gold arrow: you. Cyan: protected portal areas.",
 legend="RESONANCE HALL · red shows the PvP floor.\nTRAINING LANDING · local practice preview.",
 legendHeight=66,
 activityHelp="Use the cyan Training City portal to leave the Hall. Use the return portal at the landing to come back.",
}
local background=Color3.fromRGB(20,28,38)
local red=Color3.fromRGB(104,57,65)
local slate=Color3.fromRGB(57,72,89)
local cyan=Color3.fromRGB(81,221,214)
local gold=Color3.fromRGB(255,203,99)
local function frame(parent,name,x,y,w,h,color)
 local item=Instance.new("Frame")
 item.Name=name;item.BorderSizePixel=0;item.BackgroundColor3=color
 item.Position=UDim2.fromScale(x,y);item.Size=UDim2.fromScale(w,h);item.Parent=parent
 return item
end
local function label(parent,name,x,y,w,h,words,color)
 local item=Instance.new("TextLabel")
 item.Name=name;item.Position=UDim2.fromScale(x,y);item.Size=UDim2.fromScale(w,h)
 item.BackgroundTransparency=1;item.Text=words;item.TextColor3=color
 item.Font=Enum.Font.GothamBold;item.TextSize=11;item.Parent=parent
 return item
end
local hall={x=.045,y=.16,w=.65,h=.72,bounds=Layout.Hall}
local practice={x=.76,y=.30,w=.195,h=.40,bounds=Layout.Practice}
local function project(panel,x,z)
 local bounds=panel.bounds
 local u=math.clamp((x-bounds.x)/bounds.width+.5,0,1)
 local v=math.clamp((z-bounds.z)/bounds.depth+.5,0,1)
 return panel.x+u*panel.w,panel.y+v*panel.h
end
local function footprint(map,panel,name,x,z,width,depth,color)
 local left,top=project(panel,x-width/2,z-depth/2)
 local right,bottom=project(panel,x+width/2,z+depth/2)
 return frame(map,name,left,top,right-left,bottom-top,color)
end
function Map.create(parent,compact)
 local map=frame(parent,"ResonanceMap",.5,.5,1,1,background)
 map.AnchorPoint=Vector2.new(.5,.5)
 local ratio=Instance.new("UIAspectRatioConstraint")
 ratio.AspectRatio=Map.aspectRatio;ratio.AspectType=Enum.AspectType.FitWithinMaxSize;ratio.Parent=map
 frame(map,"HallFloor",hall.x,hall.y,hall.w,hall.h,slate)
 frame(map,"TrainingLanding",practice.x,practice.y,practice.w,practice.h,slate)
 local bounds=Layout.Combat
 footprint(map,hall,"HallPvP",(bounds.minX+bounds.maxX)/2,(bounds.minZ+bounds.maxZ)/2,
  bounds.maxX-bounds.minX,bounds.maxZ-bounds.minZ,red)
 local hallEnd=Layout.Hall.z+Layout.Hall.depth/2
 local apron=Layout.Apron
 footprint(map,hall,"SafeApron",0,(apron.startZ+hallEnd)/2,apron.halfWidth*2,hallEnd-apron.startZ,slate)
 local desk=Layout.Desk
 footprint(map,hall,"MixingDesk",desk.x,desk.z,desk.width,desk.depth,background)
 for _,speaker in ipairs(Layout.Speakers) do
  for _,side in ipairs({-1,1}) do
   for _,endSide in ipairs({-1,1}) do
    footprint(map,hall,"SpeakerCover",speaker.x*side,speaker.z*endSide,speaker.width,speaker.depth,background)
   end
  end
 end
 footprint(map,hall,"TrainingPortal",Layout.HallPortal.x,Layout.HallPortal.z,14,4,cyan)
 footprint(map,practice,"ReturnPortal",Layout.PracticePortal.x,Layout.PracticePortal.z,14,4,cyan)
 if not compact then
  local hallLabel=label(map,"HallLabel",hall.x,.03,hall.w,.10,"HALL",gold)
  local trainingLabel=label(map,"TrainingLabel",.71,.16,.29,.10,"TRAINING",cyan)
  for _,title in ipairs({hallLabel,trainingLabel}) do
   title.TextScaled=true
   local size=Instance.new("UITextSizeConstraint")
   size.MinTextSize=7;size.MaxTextSize=11;size.Parent=title
  end
 end
 local dot=frame(map,"Player",0,0,0,0,gold)
 dot.AnchorPoint=Vector2.new(.5,.5);dot.Size=UDim2.fromOffset(compact and 8 or 16,compact and 8 or 16)
 dot.ZIndex=5;dot.Visible=false
 local rounded=Instance.new("UICorner");rounded.CornerRadius=UDim.new(1,0);rounded.Parent=dot
 local border=Instance.new("UIStroke");border.Color=background;border.Thickness=1;border.Parent=dot
 local arrow
 if not compact then arrow=label(dot,"Facing",0,0,1,1,"▲",background);arrow.ZIndex=6 end
 return {map=map,dot=dot,arrow=arrow}
end
function Map.update(view,root)
 if not view or not view.map.Parent then return end
 view.dot.Visible=root~=nil and root.Parent~=nil
 if not view.dot.Visible then return end
 local position=root.Position
 local panel=Layout.Contains(Layout.Practice,position) and practice or Layout.Contains(Layout.Hall,position) and hall
 if not panel then view.dot.Visible=false;return end
 local x,z=project(panel,position.X,position.Z)
 view.dot.Position=UDim2.fromScale(x,z)
 local look=root.CFrame.LookVector
 if view.arrow then view.arrow.Rotation=math.deg(math.atan2(look.X,-look.Z)) end
end
function Map.MiniUpdate(view,root,now,visible)
 if not view or not view.map.Parent then return end
 if not visible or not root or not root.Parent then
  view.dot.Visible=false;view.nextUpdate=nil;view.lastRoot=nil;return
 end
 if view.lastRoot==root and view.nextUpdate and now<view.nextUpdate then return end
 view.lastRoot=root;view.nextUpdate=now+.1
 Map.update(view,root)
end
return Map
