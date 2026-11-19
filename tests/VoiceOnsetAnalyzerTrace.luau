-- Synthetic analyzer samples, not voice recordings or a device measurement.
local MicPower = require("../src/ReplicatedStorage/Shared/MicPower")
local Gate = require("../src/ReplicatedStorage/Shared/VoiceActivation")
local actualThreshold = Gate.OnPower
local dt = 1/60
local function checkTrace(threshold, armed, sample, frames, calibrate)
 Gate.OnPower = threshold
 local meter = MicPower.new()
 if calibrate then
  assert(meter:Calibrate(table.create(15,.006), table.create(15,.09)))
 end
 local gate = Gate.new()
 local starts, first, peak = 0, nil, 0
 for i = 1, 30 + frames do
  local raw = i <= 30 and .001 or sample(i-30)
  local power = meter:Step(raw,dt)
  local event = gate:Step(dt,power,armed,true,true)
  peak = math.max(peak,power)
  if event == "start" then
   starts += 1
   first = (i-30)*dt
  end
 end
 Gate.OnPower = actualThreshold
 return starts, first, peak
end
assert(actualThreshold == .33)
local steady = function() return .0224 end
local n, onset, peak = checkTrace(.33,true,steady,120,false)
assert(n == 1 and onset > .25 and onset < .67 and peak > .33 and peak < .35)
assert(checkTrace(.35,true,steady,120,false) == 0)
assert(checkTrace(.33,false,steady,120,false) == 0)
assert(checkTrace(.33,true,steady,120,true) == 0)
assert(checkTrace(.33,true,function(i) return i <= 6 and .06 or .001 end,120,false) == 0)
assert(checkTrace(.33,true,function() return .04 end,120,false) == 1)
assert(checkTrace(.35,true,function() return .04 end,120,false) == 1)
assert(checkTrace(.33,false,function() return .06 end,120,false) == 0)
print(string.format("PASS simulated raw analyzer through smoothing and gate: .0224 first start %.3fs, peak %.4f",onset,peak))
