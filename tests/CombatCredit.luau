local C=require('../src/ReplicatedStorage/Shared/CombatCredit')
local P=require('../src/ReplicatedStorage/Shared/Progression')
local T=require('../src/ReplicatedStorage/Shared/TrainingRules')
local n=0;local function check(v,m) assert(v,m);n+=1 end
local ledger={}
C.Add(ledger,1,70,10,100);C.Add(ledger,2,25,12,100);C.Add(ledger,3,5,13,100)
local shares=C.Split(ledger,3,13,100)
check(shares[1]==.7 and shares[2]==.25 and shares[3]==.05,'Last hit stole shared pool')
check(next(ledger)==nil and next((C.Split(ledger,3,13,100)))==nil,'KO paid twice')
C.Add(ledger,3,1,13,100)
local tiny,meaningful=C.Split(ledger,3,13,100)
check(tiny[3]==.01 and not meaningful[3],'One damage finisher stole expired or missing credit')
C.Add(ledger,1,5,0,100);C.Add(ledger,2,90,0,100);C.Add(ledger,3,5,1,100)
shares=C.Split(ledger,3,1,100)
check(shares[1]==nil and shares[2]==.9 and shares[3]==.05,'Excluded damage was redistributed to other players')
C.Add(ledger,1,100,0,100);C.Add(ledger,2,10,26,100)
check(C.Split(ledger,2,26,100)[1]==nil,'Stale damage paid')
C.Add(ledger,1,100,0,100);C.Add(ledger,1,1,26,100)
check(ledger[1].damage==1,'Expired contributor revived old damage')
C.Add(ledger,1,1000,27,100);check(ledger[1].damage==100,'Healed damage inflated ledger unboundedly')
local h={pairs={}}
check(C.RepeatFactor(h,1,2,0)==1,'First victim suppressed')
check(C.RepeatFactor(h,1,2,59.9)==0,'Repeat cooldown bypassed')
check(C.RepeatFactor(h,1,2,60)==.5,'Second KO reduction missing')
check(C.RepeatFactor(h,1,2,120)==.25 and C.RepeatFactor(h,1,2,180)==0,'Repeated opponent farming')
check(C.RepeatFactor(h,1,3,181)==1 and C.RepeatFactor(h,2,1,181)==1,'Independent pair suppressed')
check(C.RepeatFactor(h,1,2,600)==1,'Ten minute reset failed')
check(P.RewardFactor(100,1)==.05 and P.RewardFactor(50,40)==1 and P.RewardFactor(10,50)==1.25,'Level difference incentive wrong')
for l=1,100 do
 local minimum=1.25
 for target=100,1,-1 do local f=P.RewardFactor(l,target);check(f<=minimum,'Weaker victim rewarded more');minimum=f end
end
local challenges={}
check(P.Advance(challenges,'fighters',1)==0,'Challenge paid early')
P.Advance(challenges,'fighters',1)
check(P.Advance(challenges,'fighters',1)==32 and challenges.fighters==0,'Challenge failed to pay/reset')
check(P.Advance(challenges,'unknown',1)==0,'Unknown objective paid')
check(T.Hits(4,false,false) and not T.Hits(4.01,false,false),'Telegraphed strike radius incorrect')
check(not T.Hits(0,true,false) and not T.Hits(0,false,true),'Protection or dodge failed')
print('PASS '..n..' combat credit, repeat farming, challenge and training rule checks')
