"""Actual payout helpers and sustained PvP handler, mocked players/health."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
helpers=s[s.index('local function combatChallenge('):s.index('local function stopQuest(')]
a=s.index('  if target.player then',s.index('local dealt=0'))
b=s.index('  elseif target.object then',a)
setup="""
local Credit=require('../src/ReplicatedStorage/Shared/CombatCredit')
local Progression=require('../src/ReplicatedStorage/Shared/Progression')
local TrainingRules=require('../src/ReplicatedStorage/Shared/TrainingRules')
local Config={Progression=Progression,HealQuietSeconds=12,PlayerKOXP=function()return 100 end}
local rewardHistory={pairs={}};local coverRewards={}
local one={UserId=1};local two={UserId=2};local victim={UserId=3,DisplayName='Opponent'}
local players={[1]=one,[2]=two,[3]=victim}
local Players={GetPlayerByUserId=function(_,id)return players[id]end}
local sessions={}
for _,p in pairs(players) do sessions[p]={data={level=20,xp=0,coins=0,combatChallenges={}},credit={}} end
local notices={};local updates={};local quests=0;local ejections=0
local function state(p,message)notices[p]=message;updates[p]=(updates[p] or 0)+1 end
local Commerce={Multiplier=function()return 1 end}
local function coins(p,amount)sessions[p].data.coins+=amount end
local function xp(p,amount)sessions[p].data.xp+=amount end
local function questProgress()quests+=1 end
local function eject(_,h)ejections+=1;h.Health=h.MaxHealth end
"""
wrapper="""
local function hitPlayer(p,target,damage,now)
 local s=sessions[p];local dealt=0;local hit={damage=damage};local intent={level=s.data.level}
"""
checks="""
 end
 return dealt
end
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local h={Health=100,MaxHealth=100}
local target={player=victim,humanoid=h,session=sessions[victim]}
check(hitPlayer(one,target,70,100)==70 and h.Health==30,'Nonlethal damage wrong')
check(sessions[one].data.xp==0 and sessions[victim].nextHeal==112,'Per-hit XP or missing heal delay')
check(hitPlayer(two,target,50,101)==30 and h.Health==100 and ejections==1,'Overkill credit or ejection wrong')
check(sessions[one].data.xp==70 and sessions[two].data.xp==30,'Assist pool not damage-proportional')
check(sessions[one].data.coins==14 and sessions[two].data.coins==6 and quests==1,'Coins/underdog wrong')
check(notices[one]=='Assist · +70 XP' and notices[two]=='KO · +30 XP','Assist/KO feedback missing')
hitPlayer(two,target,100,102)
check(ejections==2 and sessions[two].data.xp==30,'Repeat victim paid')
hitPlayer(two,target,100,161)
check(sessions[two].data.xp==80,'Second eligible victim must pay half')
sessions[one].data.level=100;hitPlayer(one,target,100,162)
check(sessions[one].data.xp==72,'Weak victim and repeat factors not combined')
sessions[one].data.level=20;hitPlayer(one,target,80,800);players[1]=nil;hitPlayer(two,target,20,801)
check(sessions[two].data.xp==100,'Offline credit redistributed into last-hit bonus')
players[1]=one
local ledger={};local tier=TrainingRules.Tiers[3]
sessions[one].data.level=100;local before=sessions[one].data.xp
Credit.Add(ledger,1,378,900,420);Credit.Add(ledger,2,42,900,420)
awardCombatKO(ledger,two,60,420,420,900,nil,tier)
check(sessions[one].data.xp==before+378 and sessions[one].data.combatChallenges.elite==1,'Elite reward band or assist challenge broken')
sessions[one].data.level=60;sessions[one].data.combatChallenges={fighters=2,elite=1}
ledger={};Credit.Add(ledger,1,420,901,420);local sent=updates[one];before=sessions[one].data.xp
awardCombatKO(ledger,one,60,420,420,901,nil,tier)
check(sessions[one].data.xp==before+720,'KO plus two challenges lost XP')
check(updates[one]==sent+1 and notices[one]=='KO · +720 XP · challenge completed & renewed','Challenge feedback overwritten or emitted redundant state updates')
local model={};coverChallenge(one,{destroyed=true,model=model},1000);coverChallenge(one,{destroyed=true,model=model},1001)
check(sessions[one].data.combatChallenges.cover==1,'Duplicate cover credit')
coverChallenge(one,{destroyed=true,model=model,reason='level'},1120)
check(sessions[one].data.combatChallenges.cover==1,'Locked cover credit')
coverChallenge(one,{destroyed=true,model=model},1120)
check(sessions[one].data.combatChallenges.cover==2,'Repaired cover never eligible')
print('PASS '..checks..' actual combat payouts and PvP damage checks (mocked services)')
"""
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False,encoding='utf-8') as f:
 path=Path(f.name);f.write(setup+helpers+wrapper+s[a:b]+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
