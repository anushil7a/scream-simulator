-- Account voice eligibility only; client speech/power is not authenticated.
-- Pure bounded retry state. Bootstrap owns a globally capped, paced scheduler.
local Eligibility={RequestTimeout=8,CacheLifetime=120,RefreshAfter=60,MaxAttempts=3,
 MaxConcurrent=8,StartInterval=.25,RecoveryBase=30,RecoveryMax=120,DeniedRetry=120}
local delays={2,5}
function Eligibility.New(fixture,now,userId)
 return {fixture=fixture==true,identity={},attempts=0,serial=0,nextCheck=now or 0,expires=0,
  bursts=0,jitter=(userId or 0)%11}
end
function Eligibility.Allowed(s,now)
 return s~=nil and (s.fixture==true or (s.expires or 0)>now)
end
function Eligibility.DueAt(s)
 if not s or s.fixture or s.pending then return nil end
 return s.nextCheck
end
function Eligibility.MarkWaiting(s,now)
 local due=Eligibility.DueAt(s)
 if due and due<=now then s.waitingSince=s.waitingSince or now end
end
function Eligibility.Status(s,now)
 if not s then return "checking" end
 if s.fixture then return "fixture" end
 if Eligibility.Allowed(s,now) then return "eligible" end
 if s.denied then return "denied" end
 if s.failed or (s.pending and now>=s.pending.deadline)
  or (s.waitingSince and now>=s.waitingSince+Eligibility.RequestTimeout) then return "unavailable" end
 return "checking"
end
function Eligibility.Poll(s,now)
 local due=Eligibility.DueAt(s)
 if not due or now<due then return nil end
 s.waitingSince=nil;s.attempts+=1;s.serial+=1
 s.pending={token=s.serial,deadline=now+Eligibility.RequestTimeout}
 return s.serial
end
function Eligibility.Complete(s,token,now,ok,result)
 local request=s and s.pending
 if not request or token~=request.token then return false end
 s.pending=nil
 -- Result deadlines do not cancel engine calls. The global scheduler keeps a
 -- slot occupied until actual return, even after departure or this deadline.
 if now<request.deadline and ok==true and type(result)=="boolean" then
  s.attempts=0;s.bursts=0;s.failed=nil
  if result then
   s.denied=nil;s.expires=now+Eligibility.CacheLifetime;s.nextCheck=now+Eligibility.RefreshAfter
  else
   s.expires=0;s.denied=true;s.nextCheck=now+Eligibility.DeniedRetry+s.jitter
  end
 else
  s.failed=true
  if s.attempts>=Eligibility.MaxAttempts then
   s.attempts=0;s.bursts=math.min(3,s.bursts+1)
   s.nextCheck=now+math.min(Eligibility.RecoveryMax,Eligibility.RecoveryBase*2^(s.bursts-1))+s.jitter
  else s.nextCheck=now+delays[s.attempts] end
 end
 return true
end
return Eligibility
