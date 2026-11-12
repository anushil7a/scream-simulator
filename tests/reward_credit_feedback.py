"""Actual reward helpers/call-site fragments; fake players/state, real progression/credit.
No dispatcher, persistence, live economy or native execution claim.
"""
from pathlib import Path
import subprocess, tempfile, sys
ROOT=Path(__file__).resolve().parents[1]
PATH='src/ServerScriptService/Bootstrap.server.luau'
BASE='b0099a0'
def build(s):
    helpers=s[s.index('local function coins('):s.index('local function stopQuest(')]
    a=s.index(' elseif verb=="ClaimQuest" then')+len(' elseif verb=="ClaimQuest" then')
    claim=s[a:s.index(' elseif verb=="SetSettings"',a)]
    a=s.index('  if b.name=="Nick Booty" and not s.data.achievements.FoundNick then')
    nick=s[a:s.index('  if b.questIds then',a)]
    a=s.index('  if target.player then',s.index('local dealt=0'));b=s.index('  elseif target.object then',a)
    pvp='local function hitPlayer(p,target,damage,now) local s=sessions[p];local dealt=0;local hit={damage=damage};local intent={level=s.data.level}\n'+s[a:b]+'\n end\nend\n'
    a=s.index('   local bot=target.bot',s.index('local function stepSustained'));b=s.index('   if not bot.training then',a)
    bot='local function hitBot(p,bot,damage,now) local target={bot=bot};local hit={damage=damage,firstHit=false};local dealt=0;local context={};local World={UpdateBot=function()end,ReactToScream=function()end};local function knockOutBot()end\n'+s[a:b]+'\nend\n'
    return SETUP+helpers+pvp+bot+'\nlocal function claim(p,s,arg)\n'+claim+'\nend\nlocal function nick(p) local s=sessions[p];local b={name="Nick Booty"};local message="hello"\n'+nick+'\nreturn message end\n'+CHECKS
SETUP=r'''
local Progression=require('../src/ReplicatedStorage/Shared/Progression')
local Credit=require('../src/ReplicatedStorage/Shared/CombatCredit')
local TrainingRules=require('../src/ReplicatedStorage/Shared/TrainingRules')
local p={UserId=1};local victim={UserId=2,DisplayName='Opponent'};local helper={UserId=3};local sessions={};local notices={};local calls={xp=0,coins=0};local multiplier=1;local once=false
local Commerce={Multiplier=function(_,kind)calls[kind]+=1;if once and calls[kind]>1 then return 1 end;return multiplier end}
local Config={HealQuietSeconds=12,PlayerKOXP=Progression.PlayerKOXP,MaxLevel=100,Sounds={},Progression=Progression,XPToNext=Progression.XPToNext,HealthForLevel=function()return 100 end}
local q={id='test',goal=1,xp=120,coins=50,event='Underdog'}
Config.GetQuest=function(id)if id==q.id then return q end end
local VoiceCombat={Stats=function()return {health=100,maxDps=1}end}
local function parts()return nil,nil,nil end
local function eject(_,h)h.Health=h.MaxHealth end
local function state(player,message)if player==p then table.insert(notices,message or '')end end
local function stopQuest(p)sessions[p].activeQuest=nil end
local localFixture=false;local rewardHistory={pairs={}}
local Players={GetPlayerByUserId=function(_,id)if id==1 then return p elseif id==2 then return victim elseif id==3 then return helper end end}
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local function reset(level,experience,balance)
 notices={};calls={xp=0,coins=0};multiplier=1;once=false
 sessions[p]={rewardIdentity={},canSave=false,data={level=level,xp=experience,coins=balance,achievements={},quests={test={progress=1,claimed=false}},combatChallenges={}}}
 sessions[victim]={rewardIdentity={},data={level=100}};return sessions[p]
end
'''
CHECKS=r'''
local s=reset(100,0,999999990);claim(p,s,'test')
check(s.data.coins==1000000000 and s.data.xp==0,'Claim cap mutation changed')
check(notices[#notices]=='Quest reward · +0 XP · +10 coins','Claim feedback not actual credit')
check(s.data.quests.test.claimed,'Cap claim not consumed')
local n=#notices;claim(p,s,'test');check(#notices==n,'Claim replay paid/notified')
s=reset(100,0,999999999);multiplier=2
check(nick(p):find('+1 coins',1,true)~=nil,'FoundNick capped notice')
check(s.data.achievements.FoundNick and calls.coins==1,'FoundNick grant missing')
nick(p);check(calls.coins==1,'FoundNick replay')
s=reset(1,0,0);multiplier=2;once=true;claim(p,s,'test')
check(notices[#notices]=='Quest reward · +240 XP · +100 coins','Multiplier reread changed feedback')
check(calls.xp==1 and calls.coins==1,'Feedback-only multiplier call')
s=reset(99,Progression.XPToNext(99)-7,0);multiplier=2
check(xp(p,50.9)==7 and s.data.level==100 and s.data.xp==0,'Cap overflow credit')
s=reset(98,3,0);local required=Progression.XPToNext(98)-3+Progression.XPToNext(99)
multiplier=2;check(xp(p,required+.75)==required and s.data.level==100,'Multi-level accepted cost wrong')
s=reset(1,0,0);multiplier=1.5;check(xp(p,3)==4 and s.data.xp==4,'Floor once')
check(coins(p,3)==4 and s.data.coins==4,'Coin floor once')
check(xp({},20)==0 and coins({},20)==0,'Missing session not numeric zero')
s=reset(100,0,1000000000);check(xp(p,5)==0 and coins(p,5)==0,'Full cap returns')
s=reset(99,Progression.XPToNext(99)-7,0)
s.data.combatChallenges.fighters=2
local ledger={};recordCredit(ledger,p,100,100,100)
awardCombatKO(ledger,p,100,100,100,100,nil,TrainingRules.Tiers[3])
check(s.data.level==100 and s.data.xp==0,'KO did not reach cap')
check(notices[#notices]:find('+7 XP',1,true)~=nil,'KO nominal base/bonus displayed')
check(notices[#notices]:find('challenge completed & renewed',1,true)~=nil,'Zero credit erased completion')
check(s.data.combatChallenges.fighters==0,'Challenge not renewed')
check(next(ledger)==nil,'Ledger not consumed')
s=reset(10,0,0);multiplier=2;once=true;s.data.combatChallenges.fighters=2
ledger={};recordCredit(ledger,p,100,100,150)
awardCombatKO(ledger,p,10,100,100,150,nil,TrainingRules.Tiers[1])
local actual=s.data.xp;for level=10,s.data.level-1 do actual+=Progression.XPToNext(level) end
check(notices[#notices]=='KO · +'..actual..' XP · challenge completed & renewed','Expiring boost KO notice differs from cumulative awarded progression')
check(calls.xp==2 and calls.coins==1,'Expiring boost feedback reread multiplier or skipped grant')
check(s.data.combatChallenges.fighters==0 and actual>200 and s.data.level<100,'Expiring boost challenge renewal or uncapped setup invalid')
s=reset(100,0,0);s.activeQuest='test';s.data.quests.test.progress=0
ledger={};recordCredit(ledger,p,100,100,200);awardCombatKO(ledger,p,100,100,100,200,victim,nil)
check(s.data.quests.test.progress==1,'Cap suppressed nominal eligible quest event')
check(notices[#notices]=='KO · +0 XP','Cap KO mislabeled limited')
s=reset(100,0,0);s.data.combatChallenges.fighters=2
local nominal,credited=combatChallenge(p,'fighters',false)
check(nominal>0 and credited==0 and notices[#notices]:find('+0 XP',1,true)~=nil,'Challenge return/notice contract')
s=reset(1,0,0);check(xp(p,5)==5 and coins(p,5)==5 and s.canSave==false and s.testBaseline==nil,'Ordinary unsavable grants changed')
s=reset(1,0,0);s.testBaseline={level=1,xp=0,coins=0};local base=s.testBaseline
check(xp(p,5)==5 and coins(p,5)==5 and s.canSave==false,'Unsavable grants changed')
check(base.xp==0 and base.coins==0 and s.testBaseline==base,'Baseline changed')

-- Actual sustained target branches, not dispatcher/geometry/network simulation.
local observed={};local originalRepeat=Credit.RepeatFactor
Credit.RepeatFactor=function(history,a,b,now)local factor=originalRepeat(history,a,b,now);observed[a]=factor;return factor end
local function fresh()
 local s=reset(1,0,0);rewardHistory={pairs={}};observed={}
 s.credit={};sessions[victim].data.level=1;sessions[victim].credit={}
 sessions[helper]={rewardIdentity={},data={level=1,xp=0,coins=0,combatChallenges={}}};return s
end
s=fresh();local rookie=TrainingRules.Tiers[1];local bot={health=1,maxHealth=80,training=rookie,credit={}}
recordCredit(bot.credit,helper,79,80,500);hitBot(p,bot,10,500)
check(bot.health==0 and s.data.xp==0 and s.data.coins==0,'Tiny NPC payout changed')
check(notices[#notices]=='KO · no reward awarded','Tiny first NPC falsely labeled repeat-limited')
check(next(rewardHistory.pairs)==nil and next(observed)==nil,'NPC started repeat history')
check(s.data.combatChallenges.fighters==nil and next(bot.credit)==nil,'Zero NPC reward gates/consumed credit changed')
s=fresh();local h={Health=1,MaxHealth=100};local target={player=victim,humanoid=h,session=sessions[victim]}
recordCredit(sessions[victim].credit,helper,99,100,600);hitPlayer(p,target,10,600)
check(s.data.xp==0 and s.data.coins==0 and observed[1]==1,'Tiny first PvP payout/factor changed')
check(notices[#notices]=='KO · no reward awarded','Tiny first PvP falsely labeled repeat-limited')
check(rewardHistory.pairs['1:2'].count==1 and rewardHistory.pairs['1:2'].last==600,'First zero payout changed existing repeat accounting')
s=fresh();h={Health=100,MaxHealth=100};target={player=victim,humanoid=h,session=sessions[victim]}
hitPlayer(p,target,100,700)
check(notices[#notices]=='KO · +96 XP' and s.data.coins==20 and observed[1]==1,'Positive first PvP changed')
local beforeXP,beforeLevel,beforeCoins=s.data.xp,s.data.level,s.data.coins
hitPlayer(p,target,100,701)
check(observed[1]==0 and s.data.xp==beforeXP and s.data.level==beforeLevel and s.data.coins==beforeCoins,'Actual repeat suppression changed')
check(notices[#notices]=='KO · no reward awarded','Repeat-zero notice not neutral')
check(rewardHistory.pairs['1:2'].count==1 and rewardHistory.pairs['1:2'].last==700,'Cooldown history changed')
s=fresh();for i=1,Credit.MaxPairs do rewardHistory.pairs['occupied:'..i]={started=800,last=800,count=1}end
h={Health=100,MaxHealth=100};target={player=victim,humanoid=h,session=sessions[victim]};hitPlayer(p,target,100,800)
check(observed[1]==0 and s.data.xp==0 and s.data.coins==0,'Full history payout changed')
check(rewardHistory.pairs['1:2']==nil,'Full history created extra pair')
check(notices[#notices]=='KO · no reward awarded','Full history new pair falsely labeled repeat-limited')
s=fresh();bot={health=80,maxHealth=80,training=rookie,credit={}};hitBot(p,bot,80,900)
check(s.data.xp==48 and s.data.coins==5 and notices[#notices]=='KO · +48 XP','Positive first NPC changed')
check(s.canSave==false and s.testBaseline==nil,'Keep Playing ordinary session changed')
print('PASS '..checks..' actual reward credit assertions')
'''
def run(source):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',delete=False,encoding='utf-8') as f:
        path=Path(f.name);f.write(build(source))
    try:return subprocess.run(['luau',str(path)],cwd=ROOT,text=True,capture_output=True,timeout=20)
    finally:path.unlink()
if __name__=='__main__':
    s=(ROOT/PATH).read_text(encoding='utf-8')
    if '--zero-baseline' in sys.argv:
        old=subprocess.check_output(['git','show','befa611:'+PATH],cwd=ROOT).decode()
        result=run(old);assert result.returncode and 'Tiny first NPC falsely labeled repeat-limited' in result.stderr,result.stdout+result.stderr
        print('PASS befa611 baseline: actual tiny first NPC KO mislabeled repeat-limited')
    elif '--baseline' in sys.argv:
        old=subprocess.check_output(['git','show',BASE+':'+PATH],cwd=ROOT).decode()
        result=run(old);assert result.returncode and 'Claim feedback not actual credit' in result.stderr,result.stdout+result.stderr
        print('PASS historical baseline: actual claim credited10coins/0XP but displayed50coins/120XP')
    else:
        result=run(s);print(result.stdout,end='');assert result.returncode==0,result.stderr
        if '--negative-controls' in sys.argv:
            mutations=[('return s.data.coins-before','return reward','Claim feedback not actual credit'),('credited-=d.xp;d.xp=0','d.xp=0','Cap overflow credit'),('return reward,credited','return credited,credited','Zero credit erased completion'),('(credited+bonusXP)','(reward+bonus)','KO nominal base/bonus displayed'),('..xpCredit..','..(q.xp*Commerce.Multiplier(p,"xp"))..','Claim feedback not actual credit')]
            mutations.append(('KO · no reward awarded','KO · repeat-opponent reward limited','Tiny first NPC falsely labeled repeat-limited'))
            for old,new,expected in mutations:
                assert old in s,old
                r=run(s.replace(old,new,1));assert r.returncode and expected in r.stderr,r.stdout+r.stderr
            print('PASS '+str(len(mutations))+' negative controls')
