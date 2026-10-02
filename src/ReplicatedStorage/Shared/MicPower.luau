-- Local normalized input energy; not physical dB and not proof of human speech.
local MicPower = {}
MicPower.__index = MicPower
local function finite(v) return type(v)=="number" and v==v and math.abs(v)<math.huge end
local function percentile(values, fraction)
 local copy=table.clone(values);table.sort(copy)
 return copy[math.clamp(math.ceil(#copy*fraction),1,#copy)] or 0
end
function MicPower.new()
 return setmetatable({floor=0.003,ceiling=0.06,smoothed=0,active=false,calibrated=false,samples={}},MicPower)
end
function MicPower:Calibrate(quiet,voice)
 if #quiet<15 or #voice<15 then return false,"Not enough microphone samples" end
 for _,list in ipairs({quiet,voice}) do for _,v in ipairs(list) do if not finite(v) or v<0 then return false,"Invalid microphone samples" end end end
 local noise=percentile(quiet,.9)
 local loud=percentile(voice,.8)
 if loud < math.max(noise*2,noise+.006) then return false,"Voice too close to background noise; try again" end
 self.floor=math.max(.0001,noise*1.15)
 self.ceiling=math.max(self.floor+.006,loud)
 self.calibrated=true;self.smoothed=0;self.active=false
 return true
end
function MicPower:Step(rms,dt)
 if not finite(rms) or rms<0 or not finite(dt) or dt<=0 then self:Reset();return 0 end
 dt=math.min(dt,.1)
 local normalized=math.clamp((rms-self.floor)/(self.ceiling-self.floor),0,1)
 self.smoothed += (normalized-self.smoothed)*(1-math.exp(-dt/0.09))
 if self.active then self.active=self.smoothed>.05 else self.active=self.smoothed>.12 end
 return self.active and self.smoothed or 0
end
function MicPower:Reset()
 self.smoothed=0;self.active=false;self.samples={}
end
function MicPower:BeginCapture()
 self.samples={}
end
function MicPower:Capture(power)
 if finite(power) then table.insert(self.samples,math.clamp(power,0,1)) end
end
function MicPower:Release()
 local samples=self.samples;self.samples={}
 if #samples<5 then return 0 end
 local voiced=0;for _,v in ipairs(samples) do if v>=.08 then voiced+=1 end end
 if voiced<5 or voiced/#samples<.35 then return 0 end
 -- A short pop cannot determine attack strength; use sustained energy.
 return percentile(samples,.65)
end
return MicPower
