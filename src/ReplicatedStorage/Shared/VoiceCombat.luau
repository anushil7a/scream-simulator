-- Pure rules: no client-selected damage, range, victim, or reward is authoritative.
local VoiceCombat = {}
VoiceCombat.MaxLevel = 300
VoiceCombat.Cooldown = 4
VoiceCombat.MinCapture = 0.25
VoiceCombat.MaxCapture = 1.25
VoiceCombat.CaptureExpiry = 8
VoiceCombat.MinimumPower = 0.08

function VoiceCombat.IsFinite(value)
 return type(value) == "number" and value == value and math.abs(value) < math.huge
end
function VoiceCombat.Level(value)
 if not VoiceCombat.IsFinite(value) then return 1 end
 return math.clamp(math.floor(value), 1, VoiceCombat.MaxLevel)
end
function VoiceCombat.Stats(level, power, amplifier)
 local l = VoiceCombat.Level(level)
 local p = VoiceCombat.IsFinite(power) and math.clamp(power, 0, 1) or 0
 if amplifier then p = math.min(1, p * 1.12) end
 local maximum = 30 + 0.25 * (l - 1)
 return {
  maxRange = maximum,
  range = math.min(110, maximum * (0.4 + 0.6 * p)),
  damage = math.min(48, math.floor((18 + 0.1 * (l - 1)) * (0.45 + 0.55 * p) + 0.5)),
  width = 4 + 3 * (l - 1) / 299,
  health = math.floor(100 + 0.35 * (l - 1) + 0.5),
  power = p,
  cooldown = VoiceCombat.Cooldown,
 }
end
function VoiceCombat.New()
 return {lastSequence = 0, nextCast = 0, capture = nil}
end
function VoiceCombat.Cancel(state)
 state.capture = nil
end
function VoiceCombat.Begin(state, now, sequence, allowed)
 if not VoiceCombat.IsFinite(sequence) or sequence % 1 ~= 0 or sequence < 1 or sequence > 2^31 then return false, "sequence" end
 if sequence <= state.lastSequence then return false, "replay" end
 state.lastSequence = sequence
 -- Every begin invalidates an older capture, including a rejected one.
 state.capture = nil
 if not allowed then return false, "state" end
 if now < state.nextCast then return false, "cooldown" end
 state.capture = {started = now, sequence = sequence}
 return true
end
function VoiceCombat.Release(state, now, sequence, power, allowed)
 local capture = state.capture
 state.capture = nil -- consume even invalid releases; never queue a shot
 if not capture or sequence ~= capture.sequence then return false, "capture" end
 if not allowed then return false, "state" end
 if now < state.nextCast then return false, "cooldown" end
 local elapsed = now - capture.started
 if elapsed < VoiceCombat.MinCapture or elapsed > VoiceCombat.CaptureExpiry then return false, "duration" end
 if not VoiceCombat.IsFinite(power) or power < VoiceCombat.MinimumPower or power > 1 then return false, "power" end
 state.nextCast = now + VoiceCombat.Cooldown
 return true
end
return VoiceCombat
