-- Pure timing rules shared by server tests. Client loudness is always untrusted.
local ScreamWindow = {}
ScreamWindow.__index = ScreamWindow

local function finite(value)
    return type(value) == "number" and value == value and math.abs(value) < math.huge
end

function ScreamWindow.new(settings)
    return setmetatable({settings = settings, lastId = 0, cooldownUntil = 0}, ScreamWindow)
end

function ScreamWindow:Stop(now)
    if self.active then
        self.active = nil
        self.cooldownUntil = now + self.settings.Cooldown
        return true
    end
    return false
end

function ScreamWindow:Start(now, id, power)
    if self.active or now < self.cooldownUntil or not finite(id) or id % 1 ~= 0
        or id <= self.lastId or id > 1e9 or not finite(power) or power < 0.2 or power > 1 then
        return false
    end
    self.lastId = id
    self.active = {id = id, power = power, sequence = 0, started = now,
        lastPulse = now, nextTick = now, ticks = 0, evaded = {}}
    return true
end

function ScreamWindow:Pulse(now, id, sequence, power)
    local active = self.active
    if not active or id ~= active.id or not finite(sequence) or sequence % 1 ~= 0
        or sequence <= active.sequence or sequence > 1e9 or not finite(power)
        or power < 0.2 or power > 1 then
        return false
    end
    if now - active.started >= self.settings.MaxDuration
        or now - active.lastPulse > self.settings.PulseTimeout then
        return false
    end
    if now - active.lastPulse < self.settings.PulseInterval * 0.5 then
        return false
    end
    active.sequence = sequence
    active.power = power
    active.lastPulse = now
    return true
end

function ScreamWindow:Step(now, allowed)
    local active = self.active
    if not active then return nil end
    if not allowed or now - active.started >= self.settings.MaxDuration
        or now - active.lastPulse > self.settings.PulseTimeout then
        self:Stop(now)
        return nil
    end
    local maxTicks = math.floor(self.settings.MaxDuration / self.settings.TickInterval + 0.00001)
    if now < active.nextTick or active.ticks >= maxTicks then return nil end
    active.nextTick = now + self.settings.TickInterval
    active.ticks += 1
    return active.power, self.settings.TickInterval
end

return ScreamWindow
