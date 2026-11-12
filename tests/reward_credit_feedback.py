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
    return SETUP+helpers+'\nlocal function claim(p,s,arg)\n'+claim+'\nend\nlocal function nick(p) local s=sessions[p];local b={name="Nick Booty"};local message="hello"\n'+nick+'\nreturn message end\n'+CHECKS
SETUP=r'''
local Progression=require('../src/ReplicatedStorage/Shared/Progression')
local Credit=require('../src/ReplicatedStorage/Shared/CombatCredit')
local TrainingRules=require('../src/ReplicatedStorage/Shared/TrainingRules')
local p={UserId=1};local victim={UserId=2};local sessions={};local notices={};local calls={xp=0,coins=0};local multiplier=1;local once=false
local Commerce={Multiplier=function(_,kind)calls[kind]+=1;if once and calls[kind]>1 then return 1 end;return multiplier end}
local Config={MaxLevel=100,Sounds={},Progression=Progression,XPToNext=Progression.XPToNext,HealthForLevel=function()return 100 end}
local q={id='test',goal=1,xp=120,coins=50,event='Underdog'}
Config.GetQuest=function(id)if id==q.id then return q end end
local VoiceCombat={Stats=function()return {health=100,maxDps=1}end}
local function parts()return nil,nil,nil end
local function state(_,message)table.insert(notices,message or '')end
local function stopQuest(p)sessions[p].activeQuest=nil end
local localFixture=false;local rewardHistory={pairs={}}
local Players={GetPlayerByUserId=function(_,id)if id==1 then return p elseif id==2 then return victim end end}
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
print('PASS '..checks..' actual reward credit assertions')
'''
def run(source):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',delete=False,encoding='utf-8') as f:
        path=Path(f.name);f.write(build(source))
    try:return subprocess.run(['luau',str(path)],cwd=ROOT,text=True,capture_output=True,timeout=20)
    finally:path.unlink()
if __name__=='__main__':
    s=(ROOT/PATH).read_text(encoding='utf-8')
    if '--baseline' in sys.argv:
        old=subprocess.check_output(['git','show',BASE+':'+PATH],cwd=ROOT).decode()
        result=run(old);assert result.returncode and 'Claim feedback not actual credit' in result.stderr,result.stdout+result.stderr
        print('PASS historical baseline: actual claim credited10coins/0XP but displayed50coins/120XP')
    else:
        result=run(s);print(result.stdout,end='');assert result.returncode==0,result.stderr
        if '--negative-controls' in sys.argv:
            mutations=[('return s.data.coins-before','return reward','Claim feedback not actual credit'),('credited-=d.xp;d.xp=0','d.xp=0','Cap overflow credit'),('return reward,credited','return credited,credited','Zero credit erased completion'),('(credited+bonusXP)','(reward+bonus)','KO nominal base/bonus displayed'),('..xpCredit..','..(q.xp*Commerce.Multiplier(p,"xp"))..','Claim feedback not actual credit')]
            for old,new,expected in mutations:
                assert old in s,old
                r=run(s.replace(old,new,1));assert r.returncode and expected in r.stderr,r.stdout+r.stderr
            print('PASS '+str(len(mutations))+' negative controls')
