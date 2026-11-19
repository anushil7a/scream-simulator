local Gate=require("../src/ReplicatedStorage/Shared/VoiceActivation")
local Attack=require("../src/ReplicatedStorage/Shared/SustainedAttack")
local Controls=require("../src/StarterPlayer/StarterPlayerScripts/SustainedControls")
assert(Gate.OnPower==.33 and Gate.OffPower==.18 and Gate.OnSeconds==.25 and Gate.QuietSeconds==.20)
assert(Attack.MinimumPower==.08)
local sent={}
local controls=Controls.new(Gate.new(),function(verb,data) table.insert(sent,{verb,data}) end,function() return 1 end)
local now=0
local function feed(n,power,ready,active)
 for _=1,n do
  now+=.05
  controls:Step(.05,now,power,true,ready,active,active and 1 or nil)
 end
end
feed(20,1,true,false)
assert(#sent==0,"paused input triggered")
controls:SetArmed(true)
feed(20,.4,true,false)
assert(#sent==0,"re-arm without silence")
feed(4,.10,true,false)
feed(30,.329,true,false)
assert(#sent==0,"sub-threshold trace triggered")
for _=1,4 do
 feed(3,.345,true,false)
 feed(2,.27,true,false)
end
assert(#sent==0,"short interrupted peaks triggered")
feed(4,.33,true,false)
assert(#sent==0,"onset fired early")
feed(1,.33,true,false)
assert(#sent==1 and sent[1][1]=="SustainedBegin" and sent[1][2].power==.33,"new boundary did not begin")
local session=Attack.New()
assert(Attack.Begin(session,now,1,30,sent[1][2].power,true),"server rejected the new boundary")
feed(4,.25,true,true)
assert(sent[#sent][1]=="SustainedPulse","hold below onset did not sustain")
feed(3,.18,true,true)
assert(sent[#sent][1]~="SustainedStop","release fired early")
feed(1,.18,true,true)
assert(sent[#sent][1]=="SustainedStop","release hysteresis did not stop")
Attack.Stop(session,now,1)
assert(not Attack.Begin(session,now+4.99,2,30,.33,true),"server cooldown shortened")
feed(20,.4,false,false)
local total=#sent
feed(20,.4,true,false)
assert(#sent==total,"cooldown armed held voice without quiet")
feed(4,0,true,false)
feed(5,.34,true,false)
assert(sent[#sent][1]=="SustainedBegin" and #sent==total+1,".34 did not start after quiet")
controls:SetArmed(false)
assert(sent[#sent][1]=="SustainedStop","off did not interrupt")
total=#sent
feed(40,1,true,false)
assert(#sent==total,"off toggle rearmed or sent attacks")
print("PASS normalized onset boundary, interrupted peaks, hold/release, cooldown and explicit off")
