-- Automatic voice server adapter. Context (including origin and character identity)
-- must come from the server; only aim, power and sequence fields come from remotes.
local Adapter={}
function Adapter.new(Attack, Combat, directionFor)
 local api={}
 local function validPower(power)
  return Combat.IsFinite(power) and power>=0 and power<=1
 end
 local function sampleIndex(n)
  return Combat.IsFinite(n) and n%1==0 and n>=1 and n<=2^31
 end
 function api.New()
  return {protocol=Attack.New()}
 end
 local function clear(s)
  s.intent=nil
 end
 function api.Begin(s,now,request,context)
  if type(request)~="table" then return false,"request" end
  local direction=context and directionFor(context.origin,request.aim)
  local power=validPower(request.power) and request.power or nil
  local level=context and Combat.Level(context.level) or 1
  local amplifier=context~=nil and context.amplifier==true
  local stats=power and Combat.Stats(level,power,amplifier)
  local ok,reason,ended=Attack.Begin(s.protocol,now,request.sequence,
   Combat.Stats(level,1,false).maxDps,stats and stats.power,
   context~=nil and context.character~=nil and direction~=nil)
  if not s.protocol.active then clear(s) end
  if ok then
   s.intent={character=context.character,level=level,amplifier=amplifier,aim=request.aim,sample=0}
  end
  return ok,reason,ended
 end
 function api.Pulse(s,now,request,context)
  local intent=s.intent;local active=s.protocol.active
  if type(request)~="table" or not intent or not active or request.sequence~=active.sequence then return false,"sequence" end
  if not sampleIndex(request.sample) or request.sample<=intent.sample then return false,"sample" end
  -- Consume even rate-rejected samples so delayed/replayed packets cannot revive input.
  intent.sample=request.sample
  local allowed=context~=nil and context.character==intent.character
   and directionFor(context.origin,request.aim)~=nil
  local power=validPower(request.power) and Combat.Stats(intent.level,request.power,intent.amplifier).power or nil
  local ok,reason,ended=Attack.Pulse(s.protocol,now,request.sequence,power,allowed)
  if ok then intent.aim=request.aim end
  if not s.protocol.active then clear(s) end
  return ok,reason,ended
 end
 function api.Stop(s,now,sequence)
  local ended,reason=Attack.Stop(s.protocol,now,sequence)
  if not s.protocol.active then clear(s) end
  return ended,reason
 end
 function api.Cancel(s,now)
  local ended,reason=Attack.Cancel(s.protocol,now)
  if not s.protocol.active then clear(s) end
  return ended,reason
 end
 function api.Step(s,now,context,resolve)
  local a=s.protocol.active;local intent=s.intent
  if not a then return {} end
  local allowed=intent~=nil and context~=nil and context.character==intent.character
  local direction=allowed and directionFor(context.origin,intent.aim)
  local ids,details,beam
  if direction and Attack.NeedsTargets(s.protocol,now) then
   -- Power was already amplified when accepted; do not amplify a second time.
   local stats=Combat.Stats(intent.level,a.power,false)
   ids,details,beam=resolve(context,direction,stats,now)
  end
  local hits,ended,reason=Attack.Step(s.protocol,now,direction~=nil and direction~=false,ids)
  if not s.protocol.active then clear(s) end
  return hits,ended,details,beam,reason
 end
 return api
end
return Adapter
