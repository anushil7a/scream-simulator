-- Voice Reactor presentation only. The editable design is maintained separately.
-- Input is the existing normalized mic envelope, NOT decibels or frequency bands.
-- Never starts capture, changes voice eligibility, or sends a remote.
local Reactor={}
Reactor.Theme={Panel=Color3.fromRGB(23,42,51),Well=Color3.fromRGB(12,25,35),Edge=Color3.fromRGB(213,186,122),Text=Color3.fromRGB(239,247,247),Quiet=Color3.fromRGB(83,107,120),Cyan=Color3.fromRGB(101,230,234),Violet=Color3.fromRGB(183,149,255)}
function Reactor.Power(value)
 if type(value)~="number" or value~=value then return 0 end
 return math.clamp(value,0,1)
end
function Reactor.Layout(width,touch)
 local wide=width>=1100 and not touch
 return wide and 300 or math.min(230,math.max(140,width-28)),wide and 96 or 84
end
function Reactor.new(parent)
 local theme=Reactor.Theme
 local function frame(name,size,position,color,container)
  local f=Instance.new("Frame");f.Name=name;f.Size=size;f.Position=position;f.BackgroundColor3=color;f.BorderSizePixel=0;f.Active=false;f.Selectable=false;f.Interactable=false;f.Parent=container
  return f
 end
 local root=frame("MicPower",UDim2.fromOffset(230,84),UDim2.new(.5,-115,1,-96),theme.Panel,parent)
 root.Active=false
 local corner=Instance.new("UICorner");corner.CornerRadius=UDim.new(0,8);corner.Parent=root
 local stroke=Instance.new("UIStroke");stroke.Color=theme.Edge;stroke.Thickness=1;stroke.Parent=root
 local text=Instance.new("TextLabel");text.Name="Status";text.BackgroundTransparency=1;text.Position=UDim2.fromOffset(10,4);text.Size=UDim2.new(1,-20,0,40);text.Font=Enum.Font.GothamMedium;text.TextSize=12;text.TextColor3=theme.Text;text.TextWrapped=true;text.TextXAlignment=Enum.TextXAlignment.Left;text.Text="LIVE MIC 0%\nListening";text.Parent=root
 local well=frame("RecentAmplitude",UDim2.new(1,-20,0,24),UDim2.new(0,10,1,-32),theme.Well,root)
 well.ClipsDescendants=true
 local bars={};local history={}
 for i=1,28 do
  history[i]=0
  local bar=frame("Sample"..i,UDim2.new(1/28,-3,0,2),UDim2.fromScale((i-1)/28,.5),theme.Quiet,well)
  bar.AnchorPoint=Vector2.new(0,.5);bars[i]=bar
 end
 -- Retain the existing threshold/progress track as a truthful instantaneous input cue.
 local track=frame("Track",UDim2.new(1,-20,0,3),UDim2.new(0,10,1,-5),theme.Well,root)
 local fill=frame("Fill",UDim2.fromScale(0,1),UDim2.new(),theme.Edge,track)
 local self={root=root,text=text,fill=fill,track=track,bars=bars,history=history,elapsed=0}
 function self:Step(power,dt,reduced,enabled)
  power=Reactor.Power(power);self.fill.Size=UDim2.fromScale(power,1)
  self.elapsed+=math.clamp(type(dt)=="number" and dt==dt and dt or 0,0,.2)
  if self.elapsed>=.04 then
   self.elapsed=0;table.remove(self.history,1);table.insert(self.history,power)
  end
  for i,bar in ipairs(self.bars) do
   -- Reduced motion shows a static bank whose heights only follow current input.
   local amplitude=reduced and power or self.history[i]
   bar.Size=UDim2.new(1/28,-3,0,2+amplitude*20)
   bar.BackgroundColor3=not enabled and Reactor.Theme.Quiet or (i<=18 and Reactor.Theme.Cyan or Reactor.Theme.Violet)
  end
 end
 return self
end
return Reactor
