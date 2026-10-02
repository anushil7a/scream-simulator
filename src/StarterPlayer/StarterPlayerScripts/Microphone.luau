local Players=game:GetService('Players')
local Voice=game:GetService('VoiceChatService')
local Run=game:GetService('RunService')
local Power=require(game:GetService("ReplicatedStorage"):WaitForChild("Shared"):WaitForChild("MicPower"))
local Microphone={};Microphone.__index=Microphone
function Microphone.new()
 local self=setmetatable({model=Power.new(),power=0,eligible=false,ready=false,status='Checking Roblox voice access…',captureStarted=nil,phase=nil,quiet={},spoken={},generation=0},Microphone)
 self.connection=Run.Heartbeat:Connect(function(dt) self:Step(dt) end)
 self:Check()
 return self
end
function Microphone:Check()
 self.generation+=1;local generation=self.generation
 self.status='Checking Roblox voice access…';self.eligible=false;self.ready=false;self:Cancel()
 task.delay(10,function() if self.generation==generation and not self.eligible then self.status='Voice access check timed out. Check Roblox voice settings, then retry.' end end)
 task.spawn(function()
  local ok,enabled=pcall(function() return Voice:IsVoiceEnabledForUserIdAsync(Players.LocalPlayer.UserId) end)
  if self.generation~=generation then return end
  self.eligible=ok and enabled==true
  self.status=self.eligible and 'Unmute your Roblox microphone, then calibrate.' or 'Roblox voice access is required. Enable eligible voice access in your account and allow microphone permission.'
 end)
end
function Microphone:FindInput()
 if self.input and self.input.Parent then return self.input end
 self:Cancel();self.ready=false
 if self.analyzer then self.analyzer:Destroy();self.analyzer=nil end
 local input=Players.LocalPlayer:FindFirstChildWhichIsA('AudioDeviceInput',true)
 if not input then return nil end
 if self.input then self.model=Power.new() end
 self.input=input
 local analyzer=Instance.new('AudioAnalyzer');analyzer.Name='ScreamInputMeter';analyzer.SpectrumEnabled=false;analyzer.Parent=Players.LocalPlayer
 local wire=Instance.new('Wire');wire.SourceInstance=input;wire.TargetInstance=analyzer;wire.Parent=analyzer
 self.analyzer=analyzer
 return input
end
function Microphone:Calibrate()
 local input=self:FindInput()
 if not self.eligible or not input then self.status='Enable Roblox voice and reconnect your microphone first.';return end
 if input.Muted then self.status='Unmute using the Roblox microphone control, then calibrate.';return end
 self:Cancel();self.ready=false;self.phase='quiet';self.phaseStarted=os.clock();self.quiet={};self.spoken={}
 self.status='Calibration 1/2: stay quiet for two seconds.'
end
function Microphone:Cancel()
 self.captureStarted=nil;self.model:BeginCapture()
end
function Microphone:Begin()
 if not self.ready then return false end
 self.model:BeginCapture();self.captureStarted=os.clock();return true
end
function Microphone:Release()
 local started=self.captureStarted;self.captureStarted=nil
 if not started or not self.ready or os.clock()-started<.25 or os.clock()-started>8 then self.model:BeginCapture();return 0 end
 return self.model:Release()
end
function Microphone:Step(dt)
 if not self.eligible then self.power=0;return end
 local input=self:FindInput()
 if not input then self.status='Waiting for Roblox mic input. The experience needs Voice Chat and the Audio API enabled.';self.power=0;return end
 if input.Muted then
  self.ready=false;self.phase=nil;self:Cancel();self.model:Reset();self.power=0;self.status='Microphone muted. Unmute in Roblox to continue.';return
 end
 local rms=self.analyzer.RmsLevel
 self.power=self.model:Step(rms,dt)
 if self.phase then
  table.insert(self.phase=='quiet' and self.quiet or self.spoken,rms)
  if os.clock()-self.phaseStarted>=2 then
   if self.phase=='quiet' then self.phase='voice';self.phaseStarted=os.clock();self.status='Calibration 2/2: use a comfortable strong voice for two seconds.'
   else local ok,message=self.model:Calibrate(self.quiet,self.spoken);self.phase=nil;self.ready=ok;self.status=ok and 'Ready. Hold E, use your voice, then release to aim a scream.' or message end
  end
 elseif self.model.calibrated then self.ready=true;self.status='Microphone ready • live proximity voice' end
 if self.captureStarted and os.clock()-self.captureStarted<=1.25 then self.model:Capture(self.power) end
end
function Microphone:Destroy()
 self.generation+=1;self.connection:Disconnect();if self.analyzer then self.analyzer:Destroy() end
end
return Microphone
