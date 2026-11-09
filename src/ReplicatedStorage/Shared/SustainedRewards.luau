-- Server-owned NPC reward budget for one sustained scream. A later KO tops up
-- the initial hit reward; repeated damage/KO observations never pay twice.
local Rewards={Limit=5,Cooldown=10,HitCoins=2,HitXP=1,KOCoins=5,KOXP=3}
function Rewards.Hit(intent,cooldowns,id,now,firstHit,knockedOut)
 intent.rewardedBots=intent.rewardedBots or {}
 local paid=intent.rewardedBots[id]
 local coins,xp=0,0
 if not paid and firstHit and (intent.paid or 0)<Rewards.Limit and now>=(cooldowns[id] or 0) then
  paid={knockedOut=false};intent.rewardedBots[id]=paid
  intent.paid=(intent.paid or 0)+1;cooldowns[id]=now+Rewards.Cooldown
  coins,xp=Rewards.HitCoins,Rewards.HitXP
 end
 if paid and knockedOut and not paid.knockedOut then
  paid.knockedOut=true
  coins+=Rewards.KOCoins-Rewards.HitCoins;xp+=Rewards.KOXP-Rewards.HitXP
 end
 return coins,xp
end
return Rewards
