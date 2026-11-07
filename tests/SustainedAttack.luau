local Attack=require("../src/ReplicatedStorage/Shared/SustainedAttack")
local Gate=require("../src/ReplicatedStorage/Shared/VoiceActivation")
local Combat=require("../src/ReplicatedStorage/Shared/VoiceCombat")
local checks=0
local function check(v,msg) assert(v,msg);checks+=1 end
local function near(a,b) return math.abs(a-b)<1e-6 end
local function total(hits) local n=0;for _,hit in hits do n+=hit.damage end;return n end
local function begin(level)
 local s=Attack.New()
 check(Attack.Begin(s,0,1,Combat.Stats(level or 1,1,false).damage*.75,1,true),"Initial start")
 return s
end
-- Full sustained attack, moving target enters halfway, duplicate IDs cannot
-- duplicate damage; only first damage event is eligible for a hit reward.
for level=1,100 do
 local s=begin(level);local damage,lateDamage,rewards,ended=0,0,0,nil
 for i=1,40 do
  local now=i/10
  if i<40 then check(Attack.Pulse(s,now,1,1,true),"Legal pulse") end
  local hits,finish=Attack.Step(s,now,true,now<=2 and {"one","one"} or {"one","late"})
  for _,hit in hits do
   if hit.id=="one" then damage+=hit.damage;if hit.firstHit then rewards+=1 end
   else lateDamage+=hit.damage end
  end
  if finish then ended=finish end
  check(#Attack.Step(s,now,true,{"one"})==0,"Duplicate step deals damage")
 end
 local dps=Combat.Stats(level,1,false).damage*.75
 check(damage==math.floor(dps*4+1e-7),"Four-second damage budget")
 check(lateDamage==math.floor(dps*2+1e-7),"Late target inherited old damage")
 check(rewards==1,"Repeated first-hit reward")
 check(ended and ended.reason=="duration" and near(ended.endedAt,4) and near(s.nextStart,14),"Duration/cooldown deadline")
 check(s.active==nil,"Attack remains active after cap")
 check(not Attack.Begin(s,13.999,2,dps,1,true),"Cooldown shortened")
 check(Attack.Begin(s,14,3,dps,1,true),"Exact cooldown boundary")
 check(not Attack.Pulse(s,14.1,1,1,true),"Old attack pulse reached new attack")
 check(Attack.Stop(s,14.2,1)==nil and s.active~=nil,"Old stop canceled new attack")
 local stopped=Attack.Stop(s,14.2,3)
 check(stopped and near(stopped.nextStart,24.2),"Short attack cooldown starts at end")
end
do
 local s=begin();local a=s.active
 check(not Attack.Begin(s,.1,2,24,1,true) and s.active==a and a.started==0,"Begin refreshed active deadline")
 check(not Attack.Pulse(s,.01,1,1,true) and a.lastPulse==0,"Too-fast pulse refreshed timeout")
 local hits,ended=Attack.Step(s,2,true,{"one"})
 check(#hits==0 and ended.reason=="timeout" and near(ended.endedAt,.5),"Missing-input damage backfill")
 check(near(s.nextStart,10.5),"Timeout delayed cooldown origin")
end
for _,reason in ipairs({"stop","cancel","quiet","invalid","blocked"}) do
 local s=begin();local result
 check(Attack.Pulse(s,.2,1,.5,true),"Pulse before interruption")
 Attack.Step(s,.2,true,{"one"})
 if reason=="stop" then result=Attack.Stop(s,.3,1)
 elseif reason=="cancel" then result=Attack.Cancel(s,.3)
 elseif reason=="quiet" then local _,_,r=Attack.Pulse(s,.3,1,0,true);result=r
 elseif reason=="invalid" then local _,_,r=Attack.Pulse(s,.3,1,math.huge,true);result=r
 else local _,r=Attack.Step(s,.3,false,{"one"});result=r end
 check(result and s.active==nil and near(s.nextStart,10.3),"Interruption cooldown")
 check(#Attack.Step(s,.4,true,{"one"})==0,"Damage after interruption")
 check(not Attack.Begin(s,.5,2,10,1,true),"Interrupt bypassed cooldown")
end
do
 local s=begin()
 for i=1,38 do Attack.Pulse(s,i/10,1,1,true);Attack.Step(s,i/10,true,{"one"}) end
 local hits,ended=Attack.Step(s,5,true,{"one"})
 check(#hits==0 and ended.reason=="duration" and near(ended.endedAt,4),"Late observation lost earlier duration deadline")
 check(near(s.nextStart,14),"Late observation extended cooldown")
end
do
 local s=begin();local damage=0
 for i=1,400 do
  local now=i/100
  if i<400 then Attack.Pulse(s,now,1,1,true) end
  damage+=total(Attack.Step(s,now,true,{"one","one"}))
 end
 check(damage==54,"Pulse/step spam increased legal level-one damage")
end
do
 local s=begin();check(Attack.Pulse(s,.4,1,1,true),"Pulse before delayed tick")
 local hits=Attack.Step(s,.4,true,{"one"})
 check(total(hits)<=math.floor(s.active.maxDps*Attack.MaxStep),"Stall burst exceeded capped step")
 check(#Attack.Step(s,.3,true,{"one"})==0,"Clock rollback damage")
 check(s.time==.4,"Clock rollback changed observed time")
end
for _,bad in ipairs({0/0,math.huge,-1,0,2^31+1,"1"}) do
 local s=Attack.New();check(not Attack.Begin(s,0,bad,10,1,true),"Invalid sequence accepted")
end
for _,bad in ipairs({0/0,math.huge,-1,0,25,"10"}) do
 local s=Attack.New();check(not Attack.Begin(s,0,1,bad,1,true),"Invalid server budget accepted")
end
for _,bad in ipairs({0/0,math.huge,-1,0,1.01,"1"}) do
 local s=Attack.New();check(not Attack.Begin(s,0,1,10,bad,true),"Invalid start power accepted")
end
do
 local s=Attack.New();check(not Attack.Begin(s,0,1,10,1,false),"Disallowed state started")
 check(not Attack.Begin(s,0,1,10,1,true),"Rejected begin replayed")
 check(Attack.Begin(s,0,2,10,1,true),"New sequence after rejection")
 check(Attack.Pulse(s,.2,2,1,true),"Target-budget pulse")
 local targets={};for i=1,200 do targets[i]="target"..i end
 local hits=Attack.Step(s,.2,true,targets)
 check(#hits==Attack.MaxTargets and s.active.targetCount==Attack.MaxTargets,"Unbounded target tracking")
 check(Attack.Pulse(s,.4,2,1,true),"Second target-budget pulse")
 check(#Attack.Step(s,.4,true,{"new"})==0 and s.active.targetCount==Attack.MaxTargets,"Target budget grew")
end
-- Voice onset/cancellation, including noisy UI/cooldown boundaries.
local function frames(g,n,power,armed,allowed,ready)
 local events={};for _=1,n do local e=g:Step(.05,power,armed~=false,allowed~=false,ready~=false);if e then table.insert(events,e) end end
 return events
end
do
 local g=Gate.new()
 check(#frames(g,20,1)==0,"Hot mic on arming attacked without quiet")
 check(#frames(g,4,0)==0 and not g.needsQuiet,"Quiet did not rearm")
 check(#frames(g,4,1)==0,"Short voice triggered")
 check(g:Step(.05,1,true,true,true)=="start","Sustained voice did not start")
 check(#frames(g,20,.25)==0 and g.active,"Hysteresis dropped active voice")
 check(#frames(g,3,0)==0 and g.active,"Brief pause stopped attack")
 check(g:Step(.05,0,true,true,true)=="stop","Quiet did not stop")
 check(#frames(g,20,0)==0,"Quiet generated repeated stops")
end
for _,block in ipairs({"armed","allowed","ready","invalid"}) do
 local g=Gate.new();frames(g,4,0);frames(g,5,1);check(g.active,"Active precondition")
 local e=g:Step(.05,block=="invalid" and 0/0 or 1,block~="armed",block~="allowed",block~="ready")
 check(e=="stop" and not g.active,"Blocked input failed cancellation")
 check(#frames(g,20,1)==0,"Blocked/cooldown voice queued an attack")
 frames(g,4,0);check(#frames(g,5,1)==1,"Fresh voice failed recovery")
end
do
 local g=Gate.new();frames(g,4,0)
 check(g:Step(10,1,true,true,true)==nil and not g.active,"Frame hitch counted as onset")
 frames(g,1,0);check(#frames(g,4,1)==0,"Broken onset accumulated old sound")
 check(g:Step(.05,1,true,true,true)=="start","Fresh onset after hitch failed")
 check(g:Cancel()=="stop" and g.needsQuiet,"Explicit cancellation failed")
 check(g:Cancel()==nil,"Repeated cancellation emitted stop")
end
print("PASS "..checks.." pure sustained attack/onset checks; no remote, geometry or real-audio integration")
