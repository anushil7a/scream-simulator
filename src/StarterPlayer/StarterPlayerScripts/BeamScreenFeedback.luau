-- Local presentation only; no camera, audio, input or gameplay ownership.
local Feedback={};Feedback.__index=Feedback
local LAUNCH_LAYOUT={{.08,.3,0},{.08,.7,0},{.92,.3,0},{.92,.7,0},{.3,.08,90},{.7,.08,90},{.3,.92,90},{.7,.92,90}}
local HIT_LAYOUT={{-1,-1,45},{1,-1,-45},{-1,1,-45},{1,1,45}}
local HIT_OFFSET=27
local HIT_TRAVEL=6
local HIT_MIN_LEN=8
local HIT_PULSE_LEN=4
local HIT_THICK=3
local RAY_MIN_LEN=18
local RAY_PULSE_LEN=8
local RAY_THICK=2
local HIT_ONSET_COLOR=Color3.fromRGB(255,250,224)
local function finite(n)return type(n)=="number" and n==n and math.abs(n)<math.huge end
local function frame(parent,name,size,position)
 local f=Instance.new("Frame");f.Name=name;f.AnchorPoint=Vector2.new(.5,.5)
 f.Size=size;f.Position=position;f.BorderSizePixel=0;f.BackgroundTransparency=1
 f.Active=false;f.Selectable=false;f.Interactable=false;f.ZIndex=0;f.Parent=parent
 return f
end
local function hitColor(hit)
 local glow=math.clamp((hit-.35)/.65,0,1)
 return Color3.fromRGB(255,math.floor(214+36*glow+.5),math.floor(96+128*glow+.5))
end
local function applyMarks(self,offset,length,color,alpha)
 local size=UDim2.fromOffset(length,HIT_THICK)
 for i,mark in ipairs(self.marks)do
  local p=HIT_LAYOUT[i]
  mark.Position=UDim2.new(.5,p[1]*offset,.5,p[2]*offset)
  mark.Size=size
  mark.BackgroundColor3=color
  mark.BackgroundTransparency=alpha
 end
end
local function applyRays(self,length,alpha)
 local size=UDim2.fromOffset(length,RAY_THICK)
 for _,ray in ipairs(self.rays)do
  ray.Size=size
  ray.BackgroundTransparency=alpha
 end
end
function Feedback.new(parent)
 local root=frame(parent,"BeamScreenFeedback",UDim2.fromScale(1,1),UDim2.fromScale(.5,.5));root.Visible=false
 local self=setmetatable({root=root,rays={},marks={},sequence=0,clock=0,launchEnds=0,hitEnds=0,nextHit=0,destroyed=false},Feedback)
 local raySize=UDim2.fromOffset(RAY_MIN_LEN+RAY_PULSE_LEN,RAY_THICK)
 for i,p in ipairs(LAUNCH_LAYOUT)do
  local ray=frame(root,"Launch"..i,raySize,UDim2.fromScale(p[1],p[2]));ray.Rotation=p[3];self.rays[i]=ray
 end
 local markSize=UDim2.fromOffset(HIT_MIN_LEN+HIT_PULSE_LEN,HIT_THICK)
 for i,p in ipairs(HIT_LAYOUT)do
  local mark=frame(root,"Hit"..i,markSize,UDim2.new(.5,p[1]*HIT_OFFSET,.5,p[2]*HIT_OFFSET));mark.Rotation=p[3]
  mark.BackgroundColor3=HIT_ONSET_COLOR;self.marks[i]=mark
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
 applyRays(self,RAY_MIN_LEN+RAY_PULSE_LEN,1)
 applyMarks(self,HIT_OFFSET,HIT_MIN_LEN+HIT_PULSE_LEN,HIT_ONSET_COLOR,1)
end
function Feedback:Step(now,visible,reduced)
 if self.destroyed then return end
 if not self:Time(now) or visible~=true or reduced==true then self:Clear();return end
 local launch=math.clamp((self.launchEnds-now)/.45,0,1)
 local hit=math.clamp((self.hitEnds-now)/.25,0,1)
 self.root.Visible=launch>0 or hit>0
 if launch>0 then
  applyRays(self,RAY_MIN_LEN+RAY_PULSE_LEN*launch,1-.12*launch)
 else
  applyRays(self,RAY_MIN_LEN+RAY_PULSE_LEN,1)
 end
 if hit>0 then
  applyMarks(self,HIT_OFFSET+HIT_TRAVEL*(1-hit),HIT_MIN_LEN+HIT_PULSE_LEN*hit,hitColor(hit),1-.4*hit)
 else
  applyMarks(self,HIT_OFFSET,HIT_MIN_LEN+HIT_PULSE_LEN,HIT_ONSET_COLOR,1)
 end
end
function Feedback:Destroy()
 if self.destroyed then return end
 self:Clear();self.destroyed=true;self.root:Destroy();self.root=nil
 self.rays={};self.marks={}
end
return Feedback
