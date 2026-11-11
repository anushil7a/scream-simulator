local Attack=require("../src/ReplicatedStorage/Shared/SustainedAttack")
local Combat=require("../src/ReplicatedStorage/Shared/VoiceCombat")
local Adapter=require("../src/ServerScriptService/SustainedAttackAdapter")
-- Scalar geometry stub; this checks adapter plumbing, not Roblox raycasts.
local api=Adapter.new(Attack,Combat,function(origin,aim)
 if not Combat.IsFinite(aim) or math.abs(aim-origin)<.01 or math.abs(aim-origin)>2048 then return nil end
 return aim>origin and 1 or -1
end)
local checks=0
local function check(v,msg) assert(v,msg);checks+=1 end
local character={}
local context={origin=0,character=character,level=1,amplifier=true}
local function request(sequence,sample,aim,power)
 return {sequence=sequence,sample=sample,aim=aim,power=power,level=100,damage=999,targets={"forged"}}
end
local s=api.New()
check(not api.Begin(s,0,request(1,0,50,.5),nil),"Missing server context accepted")
check(not api.Begin(s,0,request(2,0,0,.5),context),"Degenerate aim accepted")
check(api.Begin(s,0,request(3,0,50,.5),context),"Valid begin rejected")
check(s.protocol.active.maxDps==15 and s.intent.level==1,"Client overrode server level/budget")
check(not api.Pulse(s,.01,request(3,1,-50,.5),context),"Fast pulse accepted")
check(not api.Pulse(s,.1,request(3,1,-50,.5),context),"Rate-rejected sample replayed")
check(not api.Pulse(s,.1,request(2,2,-50,.5),context),"Old attack sample accepted")
check(api.Pulse(s,.1,request(3,2,50,.5),context),"Fresh pulse rejected")
check(not api.Pulse(s,.19,request(3,2,-50,.5),context),"Duplicate pulse accepted")
local calls=0
local moved={origin=60,character=character,level=100,amplifier=false}
local function resolve(current,direction,stats,now)
 calls+=1
 check(current==moved and direction==-1,"Tick did not recompute aim from current origin")
 check(math.abs(stats.power-.56)<1e-6,"Amplification applied twice or lost")
 check(stats.maxRange==30,"Attack level changed mid-flight")
 return {"server-target"},{["server-target"]="server-detail"},"beam"
end
check(#api.Step(s,.19,moved,resolve)==0 and calls==0,"Geometry ran before damage tick")
local hits,ended,details,beam=api.Step(s,.2,moved,resolve)
check(#hits==1 and hits[1].id=="server-target" and hits[1].damage==2 and hits[1].firstHit,"Hit not server-derived")
check(not ended and details[hits[1].id]=="server-detail" and beam=="beam","Resolution metadata lost")
check(#api.Step(s,.2,moved,resolve)==0 and calls==1,"Duplicate tick re-ran geometry")
check(not api.Stop(s,.25,2) and s.intent~=nil,"Stale stop canceled fresh attack")
local noHits,stop=api.Step(s,.3,{origin=0,character={},level=100},resolve)
check(#noHits==0 and stop.reason=="state" and s.intent==nil,"Respawn retained attack")
check(not api.Begin(s,5.299,request(4,0,50,.5),context),"Respawn bypassed cooldown")
check(api.Begin(s,5.3,request(5,0,50,.5),context),"Restart after cooldown failed")
local _,timeout=api.Step(s,11,context,resolve)
check(timeout.reason=="timeout" and calls==1 and s.intent==nil,"Stale input resolved geometry")
check(api.Begin(s,21,request(6,0,50,.5),context),"Start after timeout failed")
local _,reason=api.Pulse(s,21.1,request(6,1,0,.5),context)
check(reason=="state" and s.intent==nil,"Bad updated aim kept damage active")
check(not api.Begin(s,32,request(7,0,50,1.01),context),"Over-range power was clamped into valid start")
check(api.Begin(s,32,request(8,0,50,.5),context),"Valid follow-up rejected")
local canceled=api.Cancel(s,32.05)
check(canceled and canceled.reason=="state" and s.intent==nil,"Server cancellation left intent")
local expired=api.New()
check(api.Begin(expired,0,request(1,0,50,.5),context),"Timeout precondition")
local accepted,why,expiry=api.Begin(expired,1,request(2,0,50,.5),context)
check(not accepted and why=="cooldown" and expiry.reason=="timeout" and expired.intent==nil,"Begin hid expiry from caller")
-- Adversarial payloads exercise the actual adapter/protocol. Geometry is still
-- scalar and transport synchronous: this does not establish network behavior.
for _,bad in ipairs({"loud",false,0/0,math.huge,-1,1.01}) do
 local test=api.New()
 check(not api.Begin(test,0,request(1,0,50,bad),context) and not test.protocol.active,"Malformed begin power started attack")
 check(api.Begin(test,0,request(2,0,50,.5),context),"Bad begin poisoned next valid sequence")
 local ok,_,ended=api.Pulse(test,.125,request(2,1,50,bad),context)
 check(not ok and ended~=nil and test.intent==nil and not test.protocol.active,"Malformed pulse power retained attack")
 check(not api.Pulse(test,.25,request(2,2,50,1),context),"Later pulse revived canceled attack")
 check(not api.Begin(test,1,request(3,0,50,1),context),"Malformed pulse bypassed cooldown")
 local called=false
 check(#api.Step(test,1,context,function()called=true;return {"victim"},{} end)==0 and not called,"Canceled attack still resolved targets")
end
local replay=api.New()
check(api.Begin(replay,0,request(1,0,50,.5),context),"Replay scenario setup failed")
local originalIntent=replay.intent
for _,packet in ipairs({false,"packet",42,{sequence=2,aim=50,power=.9}}) do
 check(not api.Begin(replay,.01,packet,context) and replay.intent==originalIntent,"Rejected begin replaced live intent")
end
for _,sample in ipairs({0,-1,.5,math.huge,0/0,"sample",2^31+1}) do
 check(not api.Pulse(replay,.1,request(1,sample,-50,.5),context) and replay.intent.sample==0,"Invalid sample consumed valid ordering")
end
check(api.Pulse(replay,.125,request(1,1,50,.5),context),"Valid sample rejected after malformed samples")
local geometryCalls=0
local _,staleEnd=api.Step(replay,.626,context,function()geometryCalls+=1;return {"victim"},{} end)
check(staleEnd and staleEnd.reason=="timeout" and geometryCalls==0,"Expired input ran target geometry")
check(not api.Pulse(replay,.7,request(1,2,50,1),context),"Delayed packet revived timed-out attack")
-- Full duration and cooldown through the adapter, with scalar mocked geometry.
local cycle=api.New()
local high={origin=0,character=character,level=100,amplifier=false}
check(api.Begin(cycle,0,request(1,0,50,1),high),"Full-cycle begin failed")
local total=0;local resolutions=0;local finalEnd
local function fullResolve()
 resolutions+=1;return {"victim"},{},"beam"
end
for tick=1,20 do
 local now=tick*.2
 if tick<20 then check(api.Pulse(cycle,now,request(1,tick,50,1),high),"Full-cycle pulse rejected") end
 local damage,ended=api.Step(cycle,now,high,fullResolve)
 for _,hit in ipairs(damage) do total+=hit.damage end
 if ended then finalEnd=ended end
end
check(total==math.floor(Combat.Stats(100,1,false).maxDps*Attack.MaxDuration+1e-7),"Full attack exceeded or missed its expected synthetic budget")
check(finalEnd and finalEnd.reason=="duration" and finalEnd.nextStart==9 and cycle.intent==nil,"Duration end/cooldown metadata incorrect")
local before=resolutions
check(#api.Step(cycle,4.2,high,fullResolve)==0 and resolutions==before,"Completed attack kept resolving geometry")
check(not api.Begin(cycle,8.999,request(2,0,50,1),high),"Restart before cooldown accepted")
check(api.Begin(cycle,9,request(3,0,50,1),high),"Exact cooldown boundary rejected")
print("PASS "..checks.." sustained adapter checks with mocked geometry")
