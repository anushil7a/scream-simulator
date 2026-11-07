-- Pure local onset gate. Input is calibrated power, never proof of human speech.
-- The caller supplies armed/allowed/ready and handles server acknowledgement.
local Gate={}
Gate.__index=Gate
Gate.OnPower=.35
Gate.OffPower=.18
Gate.OnSeconds=.25
Gate.QuietSeconds=.2
local function finite(n) return type(n)=="number" and n==n and math.abs(n)<math.huge end
function Gate.new()
 return setmetatable({active=false,quiet=0,onset=0,needsQuiet=true},Gate)
end
function Gate:Cancel()
 local wasActive=self.active
 self.active=false;self.quiet=0;self.onset=0;self.needsQuiet=true
 return wasActive and "stop" or nil
end
function Gate:Step(dt,power,armed,allowed,ready)
 if not finite(dt) or dt<=0 or not finite(power) or power<0 or power>1
  or armed~=true or allowed~=true or ready~=true then return self:Cancel() end
 -- A frame hitch cannot turn a one-frame sound into sustained voice/quiet.
 dt=math.min(dt,.1)
 if self.active then
  self.quiet=power<=Gate.OffPower and self.quiet+dt or 0
  if self.quiet+1e-7>=Gate.QuietSeconds then
   self.active=false;self.quiet=0;self.onset=0;self.needsQuiet=false
   return "stop"
  end
 elseif self.needsQuiet then
  self.quiet=power<=Gate.OffPower and self.quiet+dt or 0
  if self.quiet+1e-7>=Gate.QuietSeconds then self.needsQuiet=false;self.quiet=0 end
 else
  self.onset=power>=Gate.OnPower and self.onset+dt or 0
  if self.onset+1e-7>=Gate.OnSeconds then
   self.active=true;self.onset=0;self.quiet=0
   return "start"
  end
 end
 return nil
end
return Gate
