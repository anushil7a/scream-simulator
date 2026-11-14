-- One pending callback per object; clock/scheduler injected for deterministic tests.
local Timer={};Timer.__index=Timer
function Timer.new(clock,schedule,valid,repair,retry)
 return setmetatable({clock=clock,schedule=schedule,valid=valid,repair=repair,retry=retry,pending=false,due=0},Timer)
end
function Timer:Queue(delay)
 self.pending=true
 self.schedule(delay,function() self:Wake() end)
end
function Timer:Touch(duration)
 self.due=self.clock()+duration
 if not self.pending then self:Queue(duration) end
end
function Timer:Wake()
 if not self.valid() then self.pending=false;return end
 local remaining=self.due-self.clock()
 if remaining>1e-6 then self:Queue(remaining);return end
 if self.repair() then self.pending=false;return end
 self.due=self.clock()+5
 self.retry(5)
 self:Queue(5)
end
return Timer
