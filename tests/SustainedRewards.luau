local R=require('../src/ReplicatedStorage/Shared/SustainedRewards')
local checks=0
local function check(v,message)assert(v,message);checks+=1 end
local cooldowns={};local intent={}
local coins,xp=R.Hit(intent,cooldowns,1,1,true,false)
check(coins==2 and xp==1,'Initial hit reward changed')
for tick=1,18 do
 coins,xp=R.Hit(intent,cooldowns,1,1+tick*.15,false,false)
 check(coins==0 and xp==0,'Repeated damage tick paid again')
end
coins,xp=R.Hit(intent,cooldowns,1,4,false,true)
check(coins==3 and xp==2,'Later knockout did not top up to five coins/three XP')
coins,xp=R.Hit(intent,cooldowns,1,4.1,false,true)
check(coins==0 and xp==0,'Duplicate knockout reward')
coins,xp=R.Hit({},cooldowns,1,5,true,true)
check(coins==0 and xp==0,'Another attack bypassed victim cooldown')
coins,xp=R.Hit({},cooldowns,1,11,true,true)
check(coins==5 and xp==3,'First-hit knockout did not pay exactly one full reward')
local capped={};local gates={};local totalCoins,totalXP=0,0
for id=1,20 do
 local c,x=R.Hit(capped,gates,id,20,true,false);totalCoins+=c;totalXP+=x
end
for id=1,20 do
 local c,x=R.Hit(capped,gates,id,21,false,true);totalCoins+=c;totalXP+=x
end
check(capped.paid==5 and totalCoins==25 and totalXP==15,'Crowd exceeded five full knockout rewards')
check(gates[6]==nil,'Unpaid target had its cooldown consumed')
coins,xp=R.Hit({}, {}, 1,1,false,true)
check(coins==0 and xp==0,'Untracked later tick created a reward')
coins,xp=R.Hit({}, {}, 1,1,true,false)
check(coins==2 and xp==1,'Separate attacker/session inherited another reward budget')
print('PASS '..checks..' sustained NPC reward checks')
