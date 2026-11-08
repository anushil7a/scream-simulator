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
check(s.protocol.active.maxDps==13.5 and s.intent.level==1,"Client overrode server level/budget")
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
check(not api.Begin(s,10.29,request(4,0,50,.5),context),"Respawn bypassed cooldown")
check(api.Begin(s,10.3,request(5,0,50,.5),context),"Restart after cooldown failed")
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
print("PASS "..checks.." sustained adapter checks with mocked geometry")
