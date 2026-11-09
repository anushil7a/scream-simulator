-- Server-only callers supply actual damage and a monotonic clock. No remote claims.
local Credit={Window=25,RepeatWindow=600,RepeatCooldown=60,MaxPairs=4096}
function Credit.Add(ledger,id,damage,now,maximum)
 if damage<=0 then return end
 for key,entry in pairs(ledger) do if now-entry.at>Credit.Window then ledger[key]=nil end end
 local old=ledger[id]
 if not old or now-old.at>Credit.Window then old={damage=0};ledger[id]=old end
 old.damage=math.min(maximum,old.damage+damage);old.at=now
end
function Credit.Split(ledger,finisher,now,maximum)
 local total=0;local shares={};local meaningful={}
 for id,entry in pairs(ledger) do
  if now-entry.at<=Credit.Window and entry.damage>0 and (entry.damage>=maximum*.1 or id==finisher) then
   shares[id]=entry.damage;total+=entry.damage;meaningful[id]=entry.damage>=maximum*.1
  end
 end
 -- Expired, excluded or otherwise missing damage must not become a last-hit bonus.
 -- Healing can create more than one health bar of damage; still cap the whole pool.
 local denominator=math.max(total,maximum)
 for id,damage in pairs(shares) do shares[id]=damage/denominator end
 table.clear(ledger) -- a KO consumes this life even if its reward is suppressed
 return shares,meaningful
end
function Credit.RepeatFactor(history,attacker,victim,now)
 if now>=(history.nextCleanup or 0) then
  for key,entry in pairs(history.pairs) do if now-entry.started>=Credit.RepeatWindow then history.pairs[key]=nil end end
  history.nextCleanup=now+30
 end
 local key=tostring(attacker)..":"..tostring(victim);local entry=history.pairs[key]
 if entry and now-entry.started>=Credit.RepeatWindow then history.pairs[key]=nil;entry=nil end
 if not entry then
  local count=0;for _ in pairs(history.pairs) do count+=1 end
  if count>=Credit.MaxPairs then return 0 end
  entry={started=now,last=-math.huge,count=0};history.pairs[key]=entry
 end
 if now-entry.last<Credit.RepeatCooldown then return 0 end
 entry.last=now;entry.count+=1
 return ({1,.5,.25})[entry.count] or 0
end
return Credit
