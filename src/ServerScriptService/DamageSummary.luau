-- Private presentation accounting. Only an authoritative health mutation may call Record.
local Summary={Window=3,Quiet=12,SendInterval=.25,MaxSamples=64}
local function finite(n)
 return type(n)=="number" and n==n and math.abs(n)<math.huge
end

local function discardExpired(s,now)
 local samples=s.samples
 while #samples>0 and now>=samples[1].at+Summary.Window do
  s.recent-=table.remove(samples,1).damage
 end
 if #samples==0 then s.recent=0 end
end

-- A state exists only for a session that has actually applied damage.
function Summary.Record(s,now,damage)
 if not finite(now) or not finite(damage) or damage<=0 or (s and now<s.lastHit) then return s end
 local finished
 if s and now>=s.lastHit+Summary.Quiet then
  finished=s.total;s=nil
 end
 s=s or {samples={},total=0,recent=0,nextSend=now}
 discardExpired(s,now)
 local samples=s.samples
 local last=samples[#samples]
 if last and last.at==now then last.damage+=damage
 elseif #samples>=Summary.MaxSamples then
  -- Current accepted damage cadence cannot saturate this window. If a
  -- future higher-rate caller does, collapse adjacent oldest samples.
  local oldest=table.remove(samples,1)
  samples[1].damage+=oldest.damage
  table.insert(samples,{at=now,damage=damage})
 else table.insert(samples,{at=now,damage=damage}) end
 s.lastHit=now;s.total+=damage;s.recent+=damage
 return s,finished
end

function Summary.Step(s,now)
 if not s or not finite(now) or now<s.lastHit then return s end
 if now>=s.lastHit+Summary.Quiet then return nil,"recap",0,s.total end
 if now<s.nextSend then return s end
 s.nextSend=now+Summary.SendInterval
 discardExpired(s,now)
 local dps=s.recent/Summary.Window
 if dps==s.sentDps and s.total==s.sentTotal then return s end
 s.sentDps=dps;s.sentTotal=s.total
 return s,"active",dps,s.total
end
return Summary
