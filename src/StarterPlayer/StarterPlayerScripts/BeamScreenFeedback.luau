-- Local presentation only; no camera, audio, input or gameplay ownership.
local Feedback={};Feedback.__index=Feedback
local function finite(n)return type(n)=="number" and n==n and math.abs(n)<math.huge end
local function frame(parent,name,size,position)
 local f=Instance.new("Frame");f.Name=name;f.AnchorPoint=Vector2.new(.5,.5)
 f.Size=size;f.Position=position;f.BorderSizePixel=0;f.BackgroundTransparency=1
 f.Active=false;f.Selectable=false;f.Interactable=false;f.ZIndex=0;f.Parent=parent
 return f
end
function Feedback.new(parent)
 local root=frame(parent,"BeamScreenFeedback",UDim2.fromScale(1,1),UDim2.fromScale(.5,.5));root.Visible=false
 local self=setmetatable({root=root,rays={},marks={},sequence=0,clock=0,launchEnds=0,hitEnds=0,nextHit=0,destroyed=false},Feedback)
 for i,p in ipairs({{.08,.3,0},{.08,.7,0},{.92,.3,0},{.92,.7,0},{.3,.08,90},{.7,.08,90},{.3,.92,90},{.7,.92,90}}) do
  local ray=frame(root,"Launch"..i,UDim2.fromOffset(26,2),UDim2.fromScale(p[1],p[2]));ray.Rotation=p[3];self.rays[i]=ray
 end
 for i,p in ipairs({{-30,0,0},{30,0,0},{0,-30,90},{0,30,90}}) do
  local mark=frame(root,"Hit"..i,UDim2.fromOffset(6,2),UDim2.new(.5,p[1],.5,p[2]));mark.Rotation=p[3]
  mark.BackgroundColor3=Color3.fromRGB(255,236,170);self.marks[i]=mark
 end
 return self
end
function Feedback:Time(now)
 if not finite(now) or now<self.clock then return false end
 self.clock=now;return true
end
function Feedback:Begin(sequence,now,color,allowed)
 if self.destroyed or not finite(sequence) or sequence%1~=0 or sequence<1 or sequence>9007199254740991 or sequence<=self.sequence then return false end
 -- Consume hidden starts too: they must never replay when a panel closes.
 self.sequence=sequence
 if not self:Time(now) or allowed~=true then return false end
 if typeof(color)~="Color3" or not finite(color.R) or not finite(color.G) or not finite(color.B) then color=Color3.fromRGB(255,220,90) end
 for _,ray in ipairs(self.rays)do ray.BackgroundColor3=color end
 self.launchEnds=now+.45;return true
end
function Feedback:Hit(now,allowed)
 if self.destroyed or not self:Time(now) or allowed~=true or now<self.nextHit then return false end
 -- No stacking or extending: sustained damage cannot maintain a bright marker.
 self.hitEnds=now+.25;self.nextHit=now+.35;return true
end
function Feedback:Clear()
 self.launchEnds=0;self.hitEnds=0
 if self.root then self.root.Visible=false end
 for _,ray in ipairs(self.rays)do ray.BackgroundTransparency=1 end
 for _,mark in ipairs(self.marks)do mark.BackgroundTransparency=1 end
end
function Feedback:Step(now,visible,reduced)
 if self.destroyed then return end
 if not self:Time(now) or visible~=true or reduced==true then self:Clear();return end
 local launch=math.clamp((self.launchEnds-now)/.45,0,1)
 local hit=math.clamp((self.hitEnds-now)/.25,0,1)
 self.root.Visible=launch>0 or hit>0
 for _,ray in ipairs(self.rays)do ray.BackgroundTransparency=1-.12*launch end
 for _,mark in ipairs(self.marks)do mark.BackgroundTransparency=1-.4*hit end
end
function Feedback:Destroy()
 if self.destroyed then return end
 self:Clear();self.destroyed=true;self.root:Destroy();self.root=nil
 self.rays={};self.marks={}
end
return Feedback
