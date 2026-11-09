-- Microphone onset/release detection, independent of Roblox audio objects.
local VoiceGate = {}
VoiceGate.__index = VoiceGate

function VoiceGate.new(settings)
    return setmetatable({settings=settings, id=0, cooldownUntil=0, armed=false}, VoiceGate)
end

function VoiceGate:Cancel(now)
    self.armed = false
    self.quietSince = nil
    self.loudSince = nil
    self.silentSince = nil
    if self.active then
        self.active = false
        self.cooldownUntil = now + self.settings.Cooldown
        return "VoiceStop", self.id
    end
end

function VoiceGate:Update(now, power, allowed, serverCooldown)
    if not allowed or power ~= power or power < 0 or power > 1 then
        return self:Cancel(now)
    end
    if self.active then
        if power < 0.2 then
            self.silentSince = self.silentSince or now
        else
            self.silentSince = nil
        end
        if now - self.started >= self.settings.MaxDuration
            or (self.silentSince and now-self.silentSince >= 0.2)
            or now < serverCooldown then
            return self:Cancel(now)
        end
        if power >= 0.2 and now >= self.nextPulse then
            self.nextPulse = now + self.settings.PulseInterval
            self.sequence += 1
            return "VoicePulse", {id=self.id, sequence=self.sequence, power=power}
        end
        return nil
    end
    if now < math.max(self.cooldownUntil, serverCooldown) then
        self.armed = false
        self.quietSince = nil
        self.loudSince = nil
        return nil
    end
    if not self.armed then
        if power < 0.2 then
            self.quietSince = self.quietSince or now
            if now-self.quietSince >= 0.3 then self.armed = true end
        else
            self.quietSince = nil
        end
        return nil
    end
    if power < 0.55 then self.loudSince = nil; return nil end
    self.loudSince = self.loudSince or now
    if now-self.loudSince < 0.18 then return nil end
    self.id += 1
    self.sequence = 0
    self.active = true
    self.started = now
    self.nextPulse = now + self.settings.PulseInterval
    return "VoiceStart", {id=self.id, power=power}
end

return VoiceGate
