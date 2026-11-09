local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local VoiceGate = require(ReplicatedStorage.Shared.VoiceGate)
local Config = require(ReplicatedStorage.Shared.Config)

local Microphone = {}
Microphone.__index = Microphone

function Microphone.new(action)
    return setmetatable({action=action, gate=VoiceGate.new(Config.Scream), enabled=false,
        calibrated=false, power=0, status="Set up your microphone", smooth=0}, Microphone)
end

function Microphone:Cancel()
    local verb, arg = self.gate:Cancel(workspace:GetServerTimeNow())
    if verb then self.action:FireServer(verb,arg) end
end

function Microphone:Toggle()
    self:Cancel()
    self.error = nil
    if self.enabled then
        self.enabled = false
        self.phase = nil
        return
    end
    self.enabled = true
    self.calibrated = false
    self.phase = "quiet"
    self.phaseStarted = nil
    self.noise = 0
    self.sampleSum = 0
    self.sampleCount = 0
end

function Microphone:Update(dt, allowed, voiceEligible)
    local player = Players.LocalPlayer
    local input = player:FindFirstChildOfClass("AudioDeviceInput")
    if input ~= self.input then
        self:Cancel()
        if self.analyzer then self.analyzer:Destroy() end
        self.input = input
        self.analyzer = nil
        self.calibrated = false
        self.phaseStarted = nil
        if self.enabled then self.phase = "quiet"; self.noise = 0 end
        if input then
            local analyzer = Instance.new("AudioAnalyzer")
            analyzer.Name = "ScreamPowerAnalyzer"
            analyzer.SpectrumEnabled = false
            local wire = Instance.new("Wire")
            wire.SourceInstance = input
            wire.TargetInstance = analyzer
            wire.Parent = analyzer
            analyzer.Parent = player
            self.analyzer = analyzer
        end
    end
    if not self.enabled then
        self.status = self.error or "Tap SET UP MIC to calibrate"
        return
    end
    if not voiceEligible or not input or not input.Active or input.Muted then
        self:Cancel()
        self.phaseStarted = nil
        self.status = "Mic unavailable — check Roblox voice access and mute"
        return
    end
    local now = workspace:GetServerTimeNow()
    local rms = self.analyzer.RmsLevel
    if rms ~= rms or rms < 0 or rms == math.huge then
        self:Cancel()
        self.status = "Microphone signal unavailable"
        return
    end
    if self.phase then
        if not self.phaseStarted then
            self.phaseStarted = now
            self.sampleSum = 0
            self.sampleCount = 0
            if self.phase == "quiet" then self.noise = 0 end
        end
        local duration = now-self.phaseStarted
        if self.phase == "quiet" then
            self.status = "Calibration — stay quiet for 2 seconds"
            self.noise = math.max(self.noise,rms)
            if duration >= 2 then self.phase = "voice"; self.phaseStarted = nil end
        else
            self.status = "Calibration — use a comfortable voice for 2 seconds"
            self.sampleSum += rms
            self.sampleCount += 1
            if duration >= 2 then
                self.reference = self.sampleSum/math.max(1,self.sampleCount)
                self.phase = nil
                if self.reference <= self.noise*1.5+0.003 then
                    self.enabled = false
                    self.error = "Calibration failed — try a quieter room, then SET UP MIC"
                    self.status = self.error
                    return
                end
                self.calibrated = true
                self.smooth = 0
            end
        end
        return
    end
    if not self.calibrated then return end
    local normalized = math.clamp((rms-self.noise)/(self.reference-self.noise),0,1)
    self.smooth += (normalized-self.smooth)*(1-math.exp(-dt*18))
    self.power = self.smooth
    local cooldown = player:GetAttribute("ScreamCooldownEnds") or 0
    local verb,arg = self.gate:Update(now,self.power,allowed,cooldown)
    if verb then self.action:FireServer(verb,arg) end
    local remaining = math.max(cooldown,self.gate.cooldownUntil)-now
    if not allowed then
        self.status = "Mic paused during menus, protection or movement actions"
    elseif remaining > 0 then
        self.status = string.format("Recovering %.1fs",remaining)
    elseif self.gate.active then
        self.status = string.format("SCREAMING %.1fs · Power %d%%",math.max(0,Config.Scream.MaxDuration-(now-self.gate.started)),math.floor(self.power*100))
    elseif not self.gate.armed then
        self.status = "Briefly go quiet to ready your next scream"
    else
        self.status = string.format("Ready · Scream Power %d%% · use a comfortable voice",math.floor(self.power*100))
    end
end

return Microphone
