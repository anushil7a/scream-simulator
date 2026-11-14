local Gate=require("../src/ReplicatedStorage/Shared/VoiceActivation")
local Controls=require("../src/StarterPlayer/StarterPlayerScripts/SustainedControls")
local sent={}
local aim=10
local c=Controls.new(Gate.new(),function(verb,arg) table.insert(sent,{verb,arg}) end,function() return aim end)
local now=0
local checks=0
local function check(v,message) assert(v,message);checks+=1 end
local function run(n,power,allowed,ready,active,seq)
 for _=1,n do
  now+=.05;c:Step(.05,now,power,allowed,ready,active,seq)
 end
end
local function count(verb)
 local n=0;for _,m in ipairs(sent) do if m[1]==verb then n+=1 end end;return n
end
run(20,1,true,true,false)
check(#sent==0,"Started while paused")
c:SetArmed(true)
run(10,1,true,true,false)
check(#sent==0,"No quiet before onset")
run(4,0,true,true,false);run(5,1,true,true,false)
check(#sent==1 and sent[1][1]=="SustainedBegin" and sent[1][2].sequence==1 and sent[1][2].aim==10,"Missing onset")
run(3,1,true,true,true,999)
check(#sent==1,"Wrong server sequence sent pulses")
aim=20
run(4,1,true,true,true,1)
check(count("SustainedPulse")==2 and sent[#sent][2].aim==20 and sent[#sent][2].sample==2,"Pulse pacing or refreshed aim failed")
run(4,0,true,true,true,1)
check(count("SustainedStop")==1 and sent[#sent][2]==1,"Quiet did not stop")
run(20,1,true,false,false)
check(count("SustainedBegin")==1,"Started during cooldown")
run(20,1,true,true,false)
check(count("SustainedBegin")==1,"Cooldown carried stale speech")
run(4,0,true,true,false);run(5,1,true,true,false)
run(12,1,true,true,false)
check(count("SustainedBegin")==2 and count("SustainedStop")==2 and not c.attack,"Unacknowledged attack hung or restarted")
check(c.unconfirmedUntil>now and c.gate.needsQuiet,"Missing acknowledgement omitted recovery notice or quiet gate")
run(4,0,true,true,false);run(5,1,true,true,false)
check(c.unconfirmedUntil==0,"Fresh attack retained old confirmation notice")
run(1,1,false,true,true,3)
check(count("SustainedStop")==3 and not c.attack,"Blocked UI did not stop")
run(4,0,true,true,false);run(5,1,true,true,false)
run(1,1,true,true,true,4);run(1,1,true,true,false,4)
check(not c.attack and count("SustainedStop")==3,"Server end did not clear local attack")
run(4,0,true,true,false);aim=nil;run(5,1,true,true,false)
check(count("SustainedBegin")==4 and not c.attack,"Missing camera sent attack")
aim=30;run(4,0,true,true,false);run(5,1,true,true,false)
c:SetArmed(false);c:SetArmed(false)
check(count("SustainedStop")==4 and not c.attack and not c.armed,"Pause failed or duplicated stop")
local fresh=Controls.new(Gate.new(),function() end,function() return 1 end)
fresh:ObserveAvailability(false)
check(not fresh.armed,"Unavailable mic auto-armed")
fresh:ObserveAvailability(true)
check(fresh.armed and fresh.gate.needsQuiet,"First calibration must arm behind quiet gate")
fresh:SetArmed(false);fresh:ObserveAvailability(true)
check(not fresh.armed,"Explicit pause was silently reversed")
fresh:SetArmed(true);fresh:ObserveAvailability(false);fresh:ObserveAvailability(true)
check(not fresh.armed,"Mic reconnect/death silently re-armed")
local background=Controls.new(Gate.new(),function() end,function() return 1 end)
background:ObserveAvailability(true,false)
check(background.initialized and not background.armed,"Background calibration armed microphone")
background:ObserveAvailability(true,true)
check(not background.armed,"Returning from background silently armed microphone")
background:SetArmed(true)
check(background.armed and background.gate.needsQuiet,"Explicit resume did not require quiet after background calibration")
local teardownMessages={}
local teardown=Controls.new(Gate.new(),function(verb,arg)table.insert(teardownMessages,{verb,arg}) end,function()return 1 end)
teardown:SetArmed(true)
for i=1,4 do teardown:Step(.05,i*.05,0,true,true,false) end
for i=5,9 do teardown:Step(.05,i*.05,1,true,true,false) end
check(teardown.attack~=nil and #teardownMessages==1,"Teardown fixture failed to start")
teardown:Destroy()
check(not teardown.armed and not teardown.attack and #teardownMessages==2 and teardownMessages[2][1]=="SustainedStop" and teardownMessages[2][2]==1,"Teardown did not stop pending attack")
teardown:Destroy();teardown:Cancel();teardown:SetArmed(true);teardown:ObserveAvailability(true)
for i=1,30 do teardown:Step(.05,1+i*.05,i<10 and 0 or 1,true,true,false) end
check(not teardown.armed and not teardown.attack and #teardownMessages==2,"Late callbacks revived controller or sent duplicate stop")
local idle=Controls.new(Gate.new(),function()error("Idle teardown sent packet")end,function()return 1 end)
idle:Destroy();idle:ObserveAvailability(true);idle:SetArmed(true)
check(not idle.armed,"Never-initialized destroyed controller auto-armed")
local packets={};local availableAim=true
local recovery=Controls.new(Gate.new(),function(verb,arg)table.insert(packets,{verb,arg})end,function()return availableAim and 1 or nil end)
recovery:SetArmed(true)
for i=1,4 do recovery:Step(.05,i*.05,0,true,true,false) end
for i=5,9 do recovery:Step(.05,i*.05,1,true,true,false) end
recovery:Step(.05,.5,1,true,true,true,1)
local before=#packets
recovery:Step(2,2.5,1,true,true,true,1)
check(#packets==before+1 and packets[#packets][1]=="SustainedPulse","Frame hitch burst multiple catch-up pulses")
availableAim=false;recovery:Step(.2,2.7,1,true,true,true,1)
check(not recovery.attack and packets[#packets][1]=="SustainedStop" and packets[#packets][2]==1,"Lost camera during active attack did not stop")
before=#packets;availableAim=true
for i=1,20 do recovery:Step(.05,2.7+i*.05,1,true,true,false) end
check(#packets==before and recovery.gate.needsQuiet,"Restored camera retriggered held voice without quiet")
for i=1,4 do recovery:Step(.05,3.7+i*.05,0,true,true,false) end
for i=1,5 do recovery:Step(.05,3.9+i*.05,1,true,true,false) end
check(recovery.attack and recovery.attack.sequence==2,"Fresh onset after camera recovery failed")
recovery:Step(.05,4.2,1,true,true,true,2)
recovery:Step(.05,4.25,0/0,true,true,true,2)
check(not recovery.attack and packets[#packets][1]=="SustainedStop","Invalid live power retained an active attack")
before=#packets
for i=1,20 do recovery:Step(.05,4.25+i*.05,i<6 and 0 or 1,true,true,true,2) end
check(#packets==before,"Server-active state without local ownership started another attack")
local delayedPackets={}
local delayed=Controls.new(Gate.new(),function(verb,arg)table.insert(delayedPackets,{verb,arg})end,function()return 1 end)
local delayedNow=0
local function delayedRun(n,power,active,sequence)
 for _=1,n do
  delayedNow+=.05;delayed:Step(.05,delayedNow,power,true,true,active,sequence)
 end
end
delayed:SetArmed(true)
delayedRun(4,0,false);delayedRun(5,1,false)
check(delayed.attack and delayed.attack.sequence==1,"Delayed acknowledgement fixture did not start")
delayedRun(9,1,false)
check(not delayed.attack and #delayedPackets==2 and delayedPackets[2][1]=="SustainedStop","Timeout did not send exactly one stop")
delayedRun(10,0,true,1);delayedRun(10,1,true,1)
check(#delayedPackets==2 and delayed.gate.needsQuiet,"Late server acknowledgement revived timed-out attack or accumulated quiet")
delayedRun(10,1,false,1)
check(#delayedPackets==2,"Server end restarted held voice after late acknowledgement")
delayedRun(4,0,false,1);delayedRun(5,1,false,1)
check(delayed.attack and delayed.attack.sequence==2 and #delayedPackets==3,"Fresh onset did not recover with a new sequence")
delayedRun(3,1,true,1)
check(#delayedPackets==3 and not delayed.attack.acknowledged,"Old sequence acknowledged a newer attempt")
delayedRun(1,1,true,2)
check(delayed.attack.acknowledged and #delayedPackets==4 and delayedPackets[4][1]=="SustainedPulse" and delayedPackets[4][2].sequence==2,"Current acknowledgement did not resume correctly sequenced pulses")
print("PASS "..checks.." synthetic sustained control checks")
