-- Account voice eligibility only. This cannot authenticate speech or client power.
-- Poll/Complete never yield. Bootstrap owns the one asynchronous call per session.
local Eligibility={RequestTimeout=8,CacheLifetime=120,RefreshAfter=60,MaxAttempts=3}
local delays={2,5}
function Eligibility.New(fixture)
 return {fixture=fixture==true,attempts=0,serial=0,nextCheck=0,expires=0}
end
function Eligibility.Allowed(s,now)
 return s~=nil and (s.fixture==true or (s.expires or 0)>now)
end
function Eligibility.Status(s,now)
 if not s then return "checking" end
 if s.fixture then return "fixture" end
 if Eligibility.Allowed(s,now) then return "eligible" end
 if s.denied then return "denied" end
 if s.exhausted or (s.pending and now>=s.pending.deadline) then return "unavailable" end
 return "checking"
end
function Eligibility.Poll(s,now)
 if not s or s.fixture or s.denied or s.exhausted or s.pending or now<s.nextCheck then return nil end
 s.attempts+=1;s.serial+=1
 s.pending={token=s.serial,deadline=now+Eligibility.RequestTimeout}
 return s.serial
end
function Eligibility.Complete(s,token,now,ok,result)
 local request=s and s.pending
 if not request or token~=request.token then return false end
 s.pending=nil
 -- A timeout abandons the result, NOT the underlying yielding API call. Never
 -- overlap it with another call. Once it returns, a bounded retry may proceed.
 if now<request.deadline and ok==true and type(result)=="boolean" then
  if result then
   s.expires=now+Eligibility.CacheLifetime;s.nextCheck=now+Eligibility.RefreshAfter
   s.attempts=0
  else
   s.expires=0;s.denied=true
  end
 else
  if s.attempts>=Eligibility.MaxAttempts then s.exhausted=true
  else s.nextCheck=now+delays[s.attempts] end
 end
 return true
end
return Eligibility
