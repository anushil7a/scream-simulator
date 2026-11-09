local Window = require("../src/ReplicatedStorage/Shared/ScreamWindow")
local Gate = require("../src/ReplicatedStorage/Shared/VoiceGate")
local settings = {MaxDuration=5, Cooldown=10, TickInterval=0.2, PulseInterval=0.1, PulseTimeout=0.45}
local checks = 0
local function check(value, label)
    assert(value,label)
    checks += 1
end

local attack = Window.new(settings)
check(not attack:Start(0,1,0/0),"NaN loudness rejected")
check(not attack:Start(0,1,math.huge),"Infinite loudness rejected")
check(not attack:Start(0,1,2),"Excess loudness rejected")
check(attack:Start(0,1,1),"Start accepted")
check(not attack:Start(0,2,1),"Overlapping start rejected")
local damageTime = 0
for index=0,49 do
    local now=index/10
    if index>0 then attack:Pulse(now,1,index,1) end
    local _, duration=attack:Step(now,true)
    damageTime += duration or 0
end
check(damageTime>0 and damageTime<=5.00001,"Total damage bounded by five seconds")
check(attack:Step(5,true)==nil and attack.active==nil,"Five second maximum")
check(attack.cooldownUntil==15,"Cooldown starts at attack end")
check(not attack:Start(14.99,2,1),"Cooldown blocks early restart")
check(attack:Start(15,2,1),"Restart after cooldown")
check(not attack:Pulse(15.1,1,50,1),"Old attack pulse rejected")
check(attack:Pulse(15.1,2,1,0.5),"Matching pulse accepted")
check(not attack:Pulse(15.2,2,1,1),"Repeated pulse rejected")
check(attack:Step(15.56,true)==nil and attack.active==nil,"Missing heartbeat ends attack")
check(not attack:Start(16,3,1),"Disconnect cannot skip cooldown")
check(attack:Start(26,3,1),"Next attack starts normally")
check(attack:Step(26,false)==nil and not attack.active,"Dodge, death or protection cancels damage")
check(not attack:Stop(30) and attack.cooldownUntil==36,"Repeated stop does not extend cooldown")
check(not attack:Start(36,2,1),"Old start rejected")

local gate=Gate.new(settings)
check(gate:Update(0,1,true,0)==nil,"Already loud input cannot auto-start")
gate:Update(1,0,true,0)
gate:Update(1.31,0,true,0)
check(gate:Update(1.4,1,true,0)==nil,"Short spike cannot start")
gate:Update(1.45,0,true,0)
gate:Update(2,1,true,0)
check(gate:Update(2.19,1,true,0)=="VoiceStart","Sustained onset starts without a key")
check(gate:Update(2.3,1,true,0)=="VoicePulse","Loudness heartbeat sent")
check(gate:Update(2.4,1,false,0)=="VoiceStop","Dodge or menu cancels immediately")
check(gate:Update(13,1,true,0)==nil,"Post-dodge noise requires fresh silence")
gate:Update(14,0,true,0)
gate:Update(14.31,0,true,0)
gate:Update(14.4,1,true,0)
check(gate:Update(14.59,1,true,0)=="VoiceStart","Rearmed voice starts")
check(gate:Update(19.59,1,true,0)=="VoiceStop","Client stops after five seconds")
check(gate:Update(29.7,1,true,0)==nil,"Held scream cannot retrigger on cooldown expiry")

local quietGate=Gate.new(settings)
quietGate:Update(0,0,true,0)
quietGate:Update(0.31,0,true,0)
quietGate:Update(0.4,1,true,0)
quietGate:Update(0.59,1,true,0)
quietGate:Update(0.7,0,true,0)
check(quietGate:Update(0.91,0,true,0)=="VoiceStop","Quiet input stops before maximum duration")
print(string.format("Passed %d combat timing checks",checks))
