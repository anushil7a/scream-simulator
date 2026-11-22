-- Server-owned finishing art. Only authored structural pieces take part in collision.
local Data=require(script.Parent.Map10FinishGeometry)
local Finish={}
local grades={
 {"ArenaTier", "Concrete",Color3.fromRGB(159,149,129)},
 {"ArenaCover","Sandstone",Color3.fromRGB(141,132,115)},
 {"IslandCore","Sandstone",Color3.fromRGB(204,171,122)},
 {"CliffFacet","Sandstone",nil},{"SideCliff","Sandstone",nil},
 {"AcademyPlateau","Sandstone",Color3.fromRGB(200,174,132)},
 {"CentralGardenTerrace","Grass",Color3.fromRGB(115,152,85)},
 {"ShoreSand","Sandstone",nil},
 {"VolcanoPlateau","Basalt",Color3.fromRGB(65,58,63)},
 {"VolcanicRidge","Rock",Color3.fromRGB(59,52,58)},
 {"DockMain","WoodPlanks",Color3.fromRGB(156,109,69)},
 {"DockCross","WoodPlanks",Color3.fromRGB(156,109,69)},
 {"FootballLawn","Grass",Color3.fromRGB(87,146,77)},
 {"ShrineUnderFacet","Slate",nil},
}
local names={
 StadiumMarquee="COASTAL ARENA",
 NorthAcademyMarquee="ACADEMY PLAZA",
 NorthRookieDirection="←  ROOKIE TRAINING",
 NorthMusicMarquee="AMPHITHEATRE",
 CoastDockMarquee="TIMBER PIER",
 EastShrineMarquee="ECLIPSE SHRINE",
}
local function starts(s,p) return string.sub(s,1,#p)==p end
local function mark(part,title)
 local gui=Instance.new("SurfaceGui");gui.Name="LandmarkSign"
 gui.Face=Enum.NormalId.Front;gui.SizingMode=Enum.SurfaceGuiSizingMode.PixelsPerStud
 gui.PixelsPerStud=30;gui.LightInfluence=.4;gui.AlwaysOnTop=false
 local text=Instance.new("TextLabel")
 text.Position=UDim2.fromScale(.065,.1);text.Size=UDim2.fromScale(.87,.8)
 text.Text=title;text.Font=Enum.Font.GothamBold;text.TextScaled=true
 text.TextColor3=Color3.fromRGB(246,222,177);text.BackgroundTransparency=1;text.Parent=gui
 gui.Parent=part
end
function Finish.Build(world)
 for _,p in ipairs(world:GetChildren()) do
  if not p:IsA("BasePart") then continue end
  for _,spec in ipairs(grades) do
   if starts(p.Name,spec[1]) then
    if not p.CanCollide then p.Material=Enum.Material[spec[2]] end
    if spec[3] then p.Color=spec[3] end
    break
   end
  end
 end
 local root=Instance.new("Folder");root.Name="Map10Finishing";root.Parent=world
 local groups={}
 for _,row in ipairs(Data) do
  local id,pos,size,color,rot,material,shape,solid=table.unpack(row)
  local key=id:match("^Stadium") or id:match("^North") or id:match("^East") or id:match("^Coast") or id:match("^Landmark")
  local district=groups[key]
  if not district then
   district=Instance.new("Folder");district.Name=key;district.Parent=root;groups[key]=district
  end
  local p=Instance.new(shape=="Wedge" and "WedgePart" or "Part");p.Name=id;p.Anchored=true
  p.CanCollide=solid==true;p.CanTouch=false;p.CanQuery=solid==true
  p.CastShadow=material~="Neon" and math.min(size.X,size.Y,size.Z)>=.6
  p.Size=size;p.Color=color;p.Material=Enum.Material[material]
  if shape~="Wedge" then p.Shape=Enum.PartType[shape] end
  p.TopSurface=Enum.SurfaceType.Smooth;p.BottomSurface=Enum.SurfaceType.Smooth
  p.CFrame=CFrame.new(pos)*CFrame.Angles(0,math.rad(rot.Y),0)*CFrame.Angles(math.rad(rot.X),0,math.rad(rot.Z))
  p.Parent=district
  if names[id] then mark(p,names[id]) end
 end
 return root
end
return Finish
