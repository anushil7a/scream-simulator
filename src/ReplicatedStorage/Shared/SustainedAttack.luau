-- Pure server-side protocol prototype; NOT connected to remotes/gameplay yet.
-- now is the server clock, maxDps is server-derived, targets are server-resolved
-- IDs after geometry/PvP checks. None may come directly from client payloads.
local Attack={MaxDuration=4,Cooldown=10,TickInterval=.2,InputTimeout=.5,
 MinPulseInterval=.1,MinimumPower=.08,MaxDps=24,MaxTargets=128,MaxStep=.25}
local EPS=1e-7
local function finite(n) return type(n)=="number" and n==n and math.abs(n)<math.huge end
local function observe(s,now)
 if not finite(now) or now<0 or now<s.time then return false end
 s.time=now;return true
end
local function deadline(a) return math.min(a.started+Attack.MaxDuration,a.lastPulse+Attack.InputTimeout) end
local function finish(s,now,reason)
 local a=s.active;if not a then return nil end
 local ended=math.min(now,deadline(a))
 s.active=nil;s.nextStart=ended+Attack.Cooldown
 return {sequence=a.sequence,endedAt=ended,nextStart=s.nextStart,reason=reason}
end
local function expire(s,now)
 local a=s.active
 if a and now+EPS>=deadline(a) then
  return finish(s,now,a.started+Attack.MaxDuration<=a.lastPulse+Attack.InputTimeout and "duration" or "timeout")
 end
end
function Attack.New() return {time=0,lastSequence=0,nextStart=0,active=nil} end
function Attack.Begin(s,now,sequence,maxDps,power,allowed)
 if not observe(s,now) then return false,"clock" end
 local ended=expire(s,now)
 if not finite(sequence) or sequence%1~=0 or sequence<1 or sequence>2^31 then return false,"sequence",ended end
 if sequence<=s.lastSequence then return false,"replay",ended end
 s.lastSequence=sequence
 -- A duplicate/new begin cannot cancel or refresh a running attack.
 if s.active then return false,"active",ended end
 if allowed~=true then return false,"state",ended end
 if now+EPS<s.nextStart then return false,"cooldown",ended end
 if not finite(maxDps) or maxDps<=0 or maxDps>Attack.MaxDps then return false,"budget",ended end
 if not finite(power) or power<Attack.MinimumPower or power>1 then return false,"power",ended end
 s.active={sequence=sequence,started=now,lastPulse=now,lastTick=now,power=power,
  maxDps=maxDps,targets={},targetCount=0}
 return true,nil,ended
end
function Attack.Pulse(s,now,sequence,power,allowed)
 if not observe(s,now) then return false,"clock" end
 local ended=expire(s,now);if ended then return false,ended.reason,ended end
 local a=s.active;if not a or sequence~=a.sequence then return false,"sequence" end
 if allowed~=true then return false,"state",finish(s,now,"state") end
 if not finite(power) or power<0 or power>1 then return false,"power",finish(s,now,"power") end
 if power<Attack.MinimumPower then return false,"quiet",finish(s,now,"quiet") end
 if now-a.lastPulse+EPS<Attack.MinPulseInterval then return false,"rate" end
 a.lastPulse=now;a.power=power
 return true
end
function Attack.Stop(s,now,sequence)
 if not observe(s,now) then return nil,"clock" end
 local ended=expire(s,now);if ended then return ended end
 if not s.active or sequence~=s.active.sequence then return nil,"sequence" end
 return finish(s,now,"stop")
end
function Attack.Cancel(s,now)
 if not observe(s,now) then return nil,"clock" end
 return finish(s,now,"state")
end
local function validId(id)
 return (type(id)=="string" and #id>0 and #id<=128)
  or (finite(id) and id%1==0 and id>=0)
end
function Attack.NeedsTargets(s,now)
 local a=s.active
 return a~=nil and finite(now) and now>=s.time and now+EPS<a.lastPulse+Attack.InputTimeout
  and math.min(now,a.started+Attack.MaxDuration)-a.lastTick+EPS>=Attack.TickInterval
end
function Attack.Step(s,now,allowed,targets)
 if not observe(s,now) then return {},nil,"clock" end
 local a=s.active;if not a then return {} end
 if allowed~=true then return {},finish(s,now,"state") end
 -- Missing input ends damage immediately when observed; never backfill hits
 -- against geometry we did not check. A regular final duration tick is allowed.
 if now+EPS>=a.lastPulse+Attack.InputTimeout then
  local reason=a.started+Attack.MaxDuration<=a.lastPulse+Attack.InputTimeout and "duration" or "timeout"
  return {},finish(s,now,reason)
 end
 local untilTime=math.min(now,a.started+Attack.MaxDuration)
 local elapsed=untilTime-a.lastTick
 local hits={}
 if elapsed+EPS>=Attack.TickInterval then
  local dt=math.min(elapsed,Attack.MaxStep)
  a.lastTick=untilTime
  local seen={};local visited=0
  for _,id in ipairs(type(targets)=="table" and targets or {}) do
   visited+=1;if visited>Attack.MaxTargets then break end
   if not validId(id) or seen[id] then continue end
   seen[id]=true
   local target=a.targets[id]
   if not target then
    if a.targetCount>=Attack.MaxTargets then continue end
    target={accumulated=0,applied=0};a.targets[id]=target;a.targetCount+=1
   end
   target.accumulated=math.min(a.maxDps*Attack.MaxDuration,
    target.accumulated+a.maxDps*(.45+.55*a.power)*dt)
   local whole=math.floor(target.accumulated+EPS)
   local damage=whole-target.applied
   if damage>0 then
    table.insert(hits,{id=id,damage=damage,firstHit=target.applied==0})
    target.applied=whole
   end
  end
 end
 local ended=now+EPS>=a.started+Attack.MaxDuration and finish(s,now,"duration") or nil
 return hits,ended
end
return Attack
