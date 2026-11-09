-- Local prototype input. Roblox transports voice independently; only power and
-- aim are sent here. Server acceptance, damage and cooldown stay authoritative.
local Controls={}
Controls.__index=Controls
local PULSE_INTERVAL=.125
local ACK_TIMEOUT=.4
local MIN_PULSE_POWER=.08

function Controls.new(gate,send,getAim)
 return setmetatable({gate=gate,send=send,getAim=getAim,armed=false,sequence=0},Controls)
end
function Controls:Cancel()
 self.gate:Cancel()
 local attack=self.attack
 self.attack=nil
 if attack then self.send("SustainedStop",attack.sequence) end
end
function Controls:SetArmed(armed)
 if self.armed==armed then return end
 self.armed=armed
 self:Cancel()
end
-- Auto-arm only on the first valid calibration. A mute, death or explicit pause
-- requires a deliberate resume; returning focus must never silently re-arm.
function Controls:ObserveAvailability(available,autoArmAllowed)
 if not available then self:SetArmed(false);return end
 if not self.initialized then self.initialized=true;self:SetArmed(autoArmAllowed~=false) end
end
function Controls:Step(dt,now,power,allowed,ready,active,serverSequence)
 if not self.armed or not allowed or not ready then self:Cancel();return end
 local attack=self.attack
 if attack then
  if active and serverSequence==attack.sequence then
   attack.acknowledged=true
  elseif attack.acknowledged then
   self.attack=nil;self.gate:Cancel();return
  elseif now>=attack.ackDeadline then
   self:Cancel();return
  end
 elseif active then
  self.gate:Cancel();return
 end
 local transition=self.gate:Step(dt,power,self.armed,allowed,ready)
 if transition=="stop" then self:Cancel();return end
 if transition=="start" then
  local aim=self.getAim()
  if not aim then self:Cancel();return end
  self.sequence+=1
  self.attack={sequence=self.sequence,sample=0,nextPulse=now+PULSE_INTERVAL,ackDeadline=now+ACK_TIMEOUT}
  self.send("SustainedBegin",{sequence=self.sequence,power=power,aim=aim})
 elseif attack and attack.acknowledged and now>=attack.nextPulse and power>=MIN_PULSE_POWER then
  local aim=self.getAim()
  if not aim then self:Cancel();return end
  attack.sample+=1;attack.nextPulse=now+PULSE_INTERVAL
  self.send("SustainedPulse",{sequence=attack.sequence,sample=attack.sample,power=power,aim=aim})
 end
end
return Controls
