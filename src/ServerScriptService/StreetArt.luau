-- Original, asset-free courtyard murals. Decorative only: no navigation or combat geometry.
local Art={}
local colors={sand=Color3.fromRGB(243,213,162),sun=Color3.fromRGB(242,166,75),
 teal=Color3.fromRGB(55,133,137),coral=Color3.fromRGB(209,107,90),ink=Color3.fromRGB(39,71,78),
 leaf=Color3.fromRGB(98,144,103),cream=Color3.fromRGB(250,235,205)}
function Art.create(parent,cf,width,coastal)
 local wall=Instance.new("Part");wall.Name="CourtyardMural";wall.Size=Vector3.new(width,5.5,.06);wall.CFrame=cf
 wall.Anchored=true;wall.CanCollide=false;wall.CanTouch=false;wall.CanQuery=false;wall.CastShadow=false;wall.Color=colors.sand;wall.Parent=parent
 local canvas=Instance.new("SurfaceGui");canvas.Name="OriginalStreetArt";canvas.Face=Enum.NormalId.Front
 canvas.SizingMode=Enum.SurfaceGuiSizingMode.FixedSize;canvas.CanvasSize=Vector2.new(512,160)
 canvas.AlwaysOnTop=false;canvas.LightInfluence=1;canvas.MaxDistance=100;canvas.Parent=wall
 local function shape(name,x,y,w,h,color,round)
  local f=Instance.new("Frame");f.Name=name;f.BorderSizePixel=0;f.BackgroundColor3=color
  f.Position=UDim2.fromOffset(x,y);f.Size=UDim2.fromOffset(w,h);f.Parent=canvas
  if round then local corner=Instance.new("UICorner");corner.CornerRadius=UDim.new(.5,0);corner.Parent=f end
  return f
 end
 local paper=shape("Paper",0,0,512,160,colors.sand)
 local border=Instance.new("UIStroke");border.Name="MuralBorder";border.ApplyStrokeMode=Enum.ApplyStrokeMode.Border;border.Color=colors.ink;border.Thickness=3;border.Transparency=.25;border.Parent=paper
 shape("Sun",34,22,94,94,colors.sun,true)
 if coastal then
  shape("Horizon",0,94,512,66,colors.teal)
  for i=0,4 do
   local x=math.max(0,i*112-28)
   shape("SeaLight",x,110+(i%2)*17,math.min(84,512-x),8,colors.cream,true)
   shape("SeaShadow",i*112+10,139,math.min(60,502-i*112),7,colors.ink,true)
  end
  shape("Sail",151,32,8,62,colors.ink)
  local sail=shape("Sailcloth",163,40,42,42,colors.coral);sail.Rotation=12
 else
  for i=0,2 do
   local x=154+i*58;local y=39+(i%2)*20
   shape("Stem",x+13,y+23,5,97-y,colors.ink)
   local leaf=shape("Leaf",x-9,y+58,30,13,colors.leaf,true);leaf.Rotation=-25
   shape("Petal",x,y,32,32,i%2==0 and colors.coral or colors.teal,true)
   shape("FlowerCenter",x+10,y+10,12,12,colors.sun,true)
  end
  shape("Garden",0,143,512,17,colors.leaf)
 end
 local title=Instance.new("TextLabel");title.Name="MuralTitle";title.BackgroundTransparency=1
 title.Position=UDim2.fromOffset(335,24);title.Size=UDim2.fromOffset(157,64)
 title.Font=Enum.Font.GothamBold;title.TextColor3=colors.ink;title.TextSize=26;title.TextWrapped=true
 title.Text=coastal and "SOL I MAR" or "VIU EL BARRI";title.Parent=canvas
 shape("MuralAccent",335,92,132,4,colors.sun,true)
 return wall
end
return Art
