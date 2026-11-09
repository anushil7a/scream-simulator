-- Shared by authoritative gameplay and deterministic balance scenarios.
local Healing={QuietSeconds=10,Fraction=.2}
function Healing.Step(health,maximum,nextHeal,now)
 -- One heal per observation: lag must not accumulate instant catch-up heals.
 if health<=0 or health>=maximum or now<nextHeal then return health,nextHeal end
 return math.min(maximum,health+maximum*Healing.Fraction),now+Healing.QuietSeconds
end
return Healing
