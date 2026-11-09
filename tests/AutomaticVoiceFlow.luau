-- End-to-end RULES test: synthesized RMS, synchronous fake transport and scalar
-- geometry. Does not exercise AudioDeviceInput, Roblox networking or raycasts.
local Power=require("../src/ReplicatedStorage/Shared/MicPower")
local Gate=require("../src/ReplicatedStorage/Shared/VoiceActivation")
local Controls=require("../src/StarterPlayer/StarterPlayerScripts/SustainedControls")
local Attack=require("../src/ReplicatedStorage/Shared/SustainedAttack")
local Combat=require("../src/ReplicatedStorage/Shared/VoiceCombat")
local Adapter=require("../src/ServerScriptService/SustainedAttackAdapter")
local api=Adapter.new(Attack,Combat,function(_,aim) return aim==20 and 1 or nil end)
local mic=Power.new()
assert(mic:Calibrate(table.create(40,.001),table.create(40,.08)))
local server=api.New()
local context={origin=0,character={},level=1,amplifier=false}
local now,damage,begins,checks=0,0,0,0
local losePulses=false
local loseStops=false
local hideAcknowledgement=false
local control=Controls.new(Gate.new(),function(verb,arg)
 if verb=="SustainedBegin" then
  if api.Begin(server,now,arg,context) then begins+=1 end
 elseif verb=="SustainedPulse" and not losePulses then api.Pulse(server,now,arg,context)
 elseif verb=="SustainedStop" and not loseStops then api.Stop(server,now,arg) end
end,function() return 20 end)
local function check(v,message) assert(v,message);checks+=1 end
local function advance(seconds,rms,allowed)
 for _=1,math.floor(seconds/.05+.5) do
  now+=.05
  local active=server.protocol.active
  control:Step(.05,now,mic:Step(rms,.05),allowed~=false,now>=server.protocol.nextStart,
   not hideAcknowledgement and active~=nil,not hideAcknowledgement and active and active.sequence)
  local hits=api.Step(server,now,context,function() return {"target"},{target={}} end)
  for _,hit in ipairs(hits) do damage+=hit.damage end
 end
end
control:ObserveAvailability(true)
advance(1,.001);advance(1,.015)
check(begins==0,"Quiet/background input attacked")
advance(5,.08)
check(begins==1 and not server.protocol.active,"Four-second scream did not stop")
check(damage>0 and damage<=60,"Damage exceeded level-one sustained budget")
advance(12,.08)
check(begins==1,"Held voice restarted after cooldown without fresh quiet")
advance(.8,.001);advance(1,.08)
check(begins==2 and server.protocol.active~=nil,"Fresh post-cooldown scream failed")
advance(.1,.08,false)
check(not server.protocol.active and not control.attack,"UI interruption did not stop server attack")
advance(11,.001);advance(1,.08)
check(begins==3,"Fresh attack after interruption failed")
losePulses=true;advance(1,.08)
local stoppedDamage=damage
advance(2,.08)
check(not server.protocol.active and damage==stoppedDamage,"Lost pulses left damage running")
control:ObserveAvailability(false);control:ObserveAvailability(true)
advance(12,.001);advance(1,.08)
check(not control.armed and begins==3,"Mic reconnect silently armed")
-- Escape menu/focus uses SetArmed(false), not only the transient UI gate.
losePulses=false;control:SetArmed(true);advance(.8,.001);advance(1,.08)
check(begins==4 and server.protocol.active~=nil,"Resume before suspension failed")
control:SetArmed(false)
check(not server.protocol.active,"Suspension did not immediately stop server")
advance(12,.001);advance(1,.08)
check(begins==4 and not control.armed,"Closing menu/focus silently resumed")
control:SetArmed(true);advance(1,.08)
check(begins==4,"Resume while speaking bypassed quiet gate")
losePulses=false;advance(.8,.001);advance(1,.08)
check(begins==5,"Fresh quiet and voice after manual resume failed")
-- Fault injection is synthetic: no claims about Roblox packet delivery/order.
local oldSequence=server.protocol.active.sequence
loseStops=true;control:SetArmed(false)
check(server.protocol.active~=nil and not control.attack,"Lost stop scenario did not retain server state")
advance(.6,.08)
check(not server.protocol.active,"Missing stop failed server input expiry")
local afterLostStop=damage
advance(2,.08)
check(damage==afterLostStop,"Damage continued after lost-stop timeout")
local readyAt=server.protocol.nextStart
check(readyAt>now,"Lost stop bypassed cooldown")
local replayOK=api.Pulse(server,now,{sequence=oldSequence,sample=999,power=1,aim=20},context)
check(not replayOK and server.protocol.nextStart==readyAt,"Late pulse revived expired scream or altered cooldown")
loseStops=false;advance(11,.001)
-- Server accepts the begin, but the client never sees its acknowledgement.
hideAcknowledgement=true;control:SetArmed(true)
advance(.8,.001);advance(1,.08)
check(begins==6 and not control.attack and not server.protocol.active,"Missing acknowledgement left attack running")
local afterAckLoss=damage
advance(12,.08)
check(begins==6 and damage==afterAckLoss,"Missing acknowledgement retried held voice")
hideAcknowledgement=false
advance(.8,.001);advance(1,.08)
check(begins==7 and control.attack and server.protocol.active,"Fresh scream failed after acknowledgement loss")
local newSequence=server.protocol.active.sequence
api.Stop(server,now,oldSequence)
check(server.protocol.active and server.protocol.active.sequence==newSequence,"Delayed old stop canceled a newer scream")
local sample=server.intent.sample
replayOK=api.Pulse(server,now,{sequence=oldSequence,sample=9999,power=1,aim=20},context)
check(not replayOK and server.intent.sample==sample,"Delayed old pulse mutated new attack input")
control:SetArmed(false)
check(not server.protocol.active,"Final test cancellation failed")
print("PASS "..checks.." simulated calibrated-mic-to-server flow checks; no real audio/network/geometry")
