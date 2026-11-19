-- Silent adjustable test input. Server authorizes scope, targets and applied damage.
local Tools={};Tools.__index=Tools
function Tools.new(env)
 return setmetatable({env=env,power=50,running=false,started=0,nextPulse=0,acknowledged=false},Tools)
end
function Tools:Stop()
 if not self.running then return end
 self.running=false;self.acknowledged=false
 self.env.send("TestBeamStop")
end
function Tools:SetPower(value)
 if type(value)~="number" or value~=value then return end
 self.power=math.clamp(math.floor(value+.5),0,100)
 if self.power==0 then self:Stop() end
end
function Tools:Toggle()
 if self.running then self:Stop();return end
 local state=self.env.state()
 if not self.env.allowed() or state.testBeamAvailable~=true or self.power==0
  or (state.testBeamCooldown or 0)>0 then return end
 local aim=self.env.aim(self.power/100);if not aim then return end
 self.running=true;self.started=self.env.now();self.nextPulse=self.started+.1;self.acknowledged=false
 self.env.send("TestBeamBegin",{power=self.power,aim=aim})
end
function Tools:Tick()
 if not self.running then return end
 local now=self.env.now();local state=self.env.state()
 if not self.env.allowed() or state.testBeamAvailable~=true or now-self.started>=4
  or (self.acknowledged and state.testBeamActive~=true)
  or (not self.acknowledged and state.testBeamActive~=true and now-self.started>=.5) then self:Stop();return end
 if state.testBeamActive==true then self.acknowledged=true end
 if now<self.nextPulse then return end
 self.nextPulse=now+.1
 local aim=self.env.aim(self.power/100);if not aim then self:Stop();return end
 self.env.send("TestBeamPulse",{power=self.power,aim=aim})
end
return Tools
