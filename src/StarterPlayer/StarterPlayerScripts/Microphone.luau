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
 if self.destroyed or self.checkPending then return end
 if os.clock()<(self.nextCheckAt or 0) then
  if not self.eligible then self.status='Please wait two seconds after a check finishes before checking again.' end
  return
 end
 self.generation+=1;local generation=self.generation
 self.status='Checking Roblox voice access…';self.eligible=false;self.ready=false;self.checkPending=true;self.checkStarted=os.clock();self:CancelCalibration();self:Cancel()
 -- One actual call owns the slot until return, including after the notice timeout.
 task.spawn(function()
  if self.destroyed or self.generation~=generation then return end
  local ok,enabled=pcall(function() return Voice:IsVoiceEnabledForUserIdAsync(Players.LocalPlayer.UserId) end)
  if self.destroyed or self.generation~=generation then return end
  self.checkPending=false;self.nextCheckAt=os.clock()+2
  self.eligible=ok and enabled==true
  self.status=self.eligible and 'Unmute your Roblox microphone, then calibrate.' or not ok and 'Voice access check failed. Wait two seconds, then check again.' or 'Roblox voice access is required. Enable eligible voice access in your account and allow microphone permission.'
 end)
end
function Microphone:CancelCalibration()
 self.phase=nil;self.phaseStarted=nil;self.quiet={};self.spoken={}
end
function Microphone:FindInput()
 if self.destroyed then return nil end
 if self.input and self.input.Parent and self.analyzer and self.analyzer.Parent
  and self.wire and self.wire.Parent==self.analyzer
  and self.wire.SourceInstance==self.input and self.wire.TargetInstance==self.analyzer then return self.input end
 self:Cancel();self:CancelCalibration();self.ready=false
 if self.wire then self.wire:Destroy();self.wire=nil end
 if self.analyzer then self.analyzer:Destroy();self.analyzer=nil end
 local input=Players.LocalPlayer:FindFirstChildWhichIsA('AudioDeviceInput',true)
 if not input then return nil end
 if self.input then self.model=Power.new() end
 self.input=input
 local analyzer=Instance.new('AudioAnalyzer');analyzer.Name='ScreamInputMeter';analyzer.SpectrumEnabled=false;analyzer.Parent=Players.LocalPlayer
 local wire=Instance.new('Wire');wire.SourceInstance=input;wire.TargetInstance=analyzer;wire.Parent=analyzer
 self.analyzer=analyzer;self.wire=wire
 self.status='Microphone input found. Calibrate before attacking.'
 return input
end
function Microphone:Calibrate()
 if self.destroyed or self.checkPending then return end
 local input=self:FindInput()
 if not self.eligible or not input then self.status='Enable Roblox voice and reconnect your microphone first.';return end
 if input.Muted then self:HandleMute();self.status='Unmute using the Roblox microphone control, then calibrate.';return end
 if input.Active==false then self:HandleInactive();return end
 -- A new attempt supersedes the previous calibration, including failed retries.
 self:Cancel();self.model=Power.new();self.power=0;self.ready=false;self.phase='quiet';self.phaseStarted=os.clock();self.quiet={};self.spoken={}
 self.status='Calibration 1/2: stay quiet for two seconds.'
end
function Microphone:Cancel()
 self.captureStarted=nil;self.model:BeginCapture()
end
function Microphone:Begin()
 if self.destroyed then return false end
 local input=self:FindInput();if not input then return false end
 if input.Muted then self:HandleMute();return false end
 if input.Active==false then self:HandleInactive();return false end
 if not self.ready then return false end
 self.model:BeginCapture();self.captureStarted=os.clock();return true
end
function Microphone:CapturePower()
 return self.captureStarted and self.ready and self.model:CapturePower() or 0
end
function Microphone:Release()
 local input=not self.destroyed and self:FindInput()
 if not input then self:Cancel();return 0,'Microphone capture canceled. Try again.' end
 if input.Muted then self:HandleMute();return 0,'Microphone muted. Unmute in Roblox to continue.' end
 if input.Active==false then self:HandleInactive();return 0,self.status end
 local started=self.captureStarted;self.captureStarted=nil
 if not started or not self.ready then self.model:BeginCapture();return 0,'Microphone capture canceled. Try again.' end
 local elapsed=os.clock()-started
 if elapsed<.25 then self.model:BeginCapture();return 0,'Hold attack while speaking for at least 0.25 seconds.' end
 if elapsed>8 then self.model:BeginCapture();return 0,'Capture expired. Start a new live beam.' end
 local power=self.model:Release()
 return power,power<.08 and 'Hold attack FIRST, speak immediately, then release within 1.25 seconds.' or nil
end
function Microphone:HandleMute()
 self.wasMuted=true;self.ready=false;self:CancelCalibration();self:Cancel();self.model:Reset();self.power=0
 self.status='Microphone muted. Unmute in Roblox to continue.'
end
-- Active is publicly readable; only Roblox controls it. Do not use restricted IsReady.
function Microphone:HandleInactive()
 self.wasInactive=true;self.ready=false;self:CancelCalibration();self:Cancel();self.model:Reset();self.power=0
 self.status='Microphone input inactive. Check Roblox microphone controls and your input.'
end
function Microphone:Step(dt)
 if self.destroyed then return end
 if self.checkPending and os.clock()-self.checkStarted>=10 then
  self.status='Voice access check is still pending. Wait for it to finish; if it stays stuck, leave and rejoin.'
 end
 if not self.eligible then self.power=0;return end
 local input=self:FindInput()
 if not input then self.status='Waiting for Roblox mic input. The experience needs Voice Chat and the Audio API enabled.';self.power=0;return end
 if input.Muted then
  self:HandleMute();return
 end
 if input.Active==false then self:HandleInactive();return end
 if self.wasInactive then
  self.wasInactive=false
  if not self.model.calibrated and not self.phase then self.status='Microphone input active. Calibrate before attacking.' end
 end
 if self.wasMuted then
  self.wasMuted=false
  if not self.model.calibrated and not self.phase then self.status='Microphone unmuted. Calibrate before attacking.' end
 end
 local rms=self.analyzer.RmsLevel
 if type(rms)~="number" or rms~=rms or math.abs(rms)==math.huge or rms<0 then
  self.signalUnavailable=true;self.ready=false;self.power=0;self:CancelCalibration();self:Cancel()
  self.status='Microphone signal unavailable. Check your input.';return
 end
 if self.signalUnavailable then
  self.signalUnavailable=false
  if not self.model.calibrated and not self.phase then self.status='Microphone signal restored. Calibrate before attacking.' end
 end
 self.power=self.model:Step(rms,dt)
 if self.phase then
  table.insert(self.phase=='quiet' and self.quiet or self.spoken,rms)
  if os.clock()-self.phaseStarted>=2 then
   if self.phase=='quiet' then self.phase='voice';self.phaseStarted=os.clock();self.status='Calibration 2/2: use a comfortable strong voice for two seconds.'
   else local ok,message=self.model:Calibrate(self.quiet,self.spoken);self.phase=nil;self.ready=ok;self.status=ok and 'Calibration complete. Follow the voice meter to attack.' or message end
  end
 elseif self.model.calibrated then self.ready=true;self.status='Microphone ready • live input detected' end
 if self.captureStarted and os.clock()-self.captureStarted<=1.25 then self.model:Capture(self.power) end
end
function Microphone:Destroy()
 if self.destroyed then return end
 self.destroyed=true;self.generation+=1;self.checkPending=false
 self.ready=false;self.eligible=false;self.power=0
 self:CancelCalibration();self:Cancel();self.model.calibrated=false
 self.connection:Disconnect()
 if self.wire then self.wire:Destroy();self.wire=nil end
 if self.analyzer then self.analyzer:Destroy();self.analyzer=nil end
 self.input=nil
end
return Microphone
