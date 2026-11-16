-- Pure lifecycle; contribution belongs to one session identity, never a last-hit bonus.
local Rules={}
function Rules.New(spec) return {health=spec.health,credit={},lastHit=0,readyAt=0,nextAttack=0} end
function Rules.CanHit(b,spec,level,distance,now)
 return b.health>0 and now>=b.readyAt and level>=spec.level and distance<=spec.radius
end
function Rules.Reset(b,spec,now)
 b.health=spec.health;b.credit={};b.lastHit=now;b.strike=nil;b.nextAttack=now+2
end
function Rules.Hit(b,spec,id,identity,damage,now)
 if b.health<=0 or type(damage)~="number" or damage~=damage or damage<=0 or damage==math.huge then return 0 end
 local actual=math.min(damage,b.health)
 local entry=b.credit[id]
 if not entry or entry.identity~=identity or now-entry.at>20 then entry={identity=identity,damage=0};b.credit[id]=entry end
 entry.damage+=actual;entry.at=now;b.lastHit=now;b.health-=actual
 return actual
end
function Rules.Eligible(entry,identity,spec,now)
 return entry and entry.identity==identity and now-entry.at<=20 and entry.damage>=spec.health*.05
end
return Rules
