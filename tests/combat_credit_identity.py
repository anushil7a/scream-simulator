"""Actual combat credit provenance; mock reference graph, not native GC/memory proof.
Default: behavioral/source assertions. --negative-controls explicitly runs mutations.
"""
from pathlib import Path
import subprocess,tempfile,sys
ROOT=Path(__file__).resolve().parents[1]
def read(baseline=False):
 path='src/ServerScriptService/Bootstrap.server.luau'
 return subprocess.check_output(['git','show','a503c5e:'+path],cwd=ROOT,text=True,encoding='utf-8') if baseline else (ROOT/path).read_text(encoding='utf-8')
def build(baseline=False,mutation=None):
 b=read(baseline)
 if mutation:b=mutation(b)
 helpers=b[b.index('local function combatChallenge('):b.index('local function stopQuest(')]
 constructor=b[b.index(' local s={data=data',b.index('local function joined(p)')):b.index(';sessions[p]=s',b.index(' local s={data=data',b.index('local function joined(p)')))]
 return SETUP+helpers+'\nlocal function joinedState(p,data) local save=true;local recoveryWarning=false\n'+constructor+'\nreturn s end\n'+(BASELINE if baseline else CHECKS)
SETUP=r"""
local Credit=require('../src/ReplicatedStorage/Shared/CombatCredit')
local Progression=require('../src/ReplicatedStorage/Shared/Progression')
local TrainingRules=require('../src/ReplicatedStorage/Shared/TrainingRules')
local Config={Progression=Progression,HealQuietSeconds=12,SprintDuration=4}
local VoiceCombat={New=function()return {}end};local VoiceEligibility={New=function()return {}end}
local sessions={};local players={};local localFixture=false;local rewardHistory={pairs={}}
local Players={GetPlayerByUserId=function(_,id)return players[id]end}
local Commerce={Multiplier=function()return 1 end}
local function xp(p,n)sessions[p].data.xp+=n;return n end
local function coins(p,n)sessions[p].data.coins+=n end
local events={};local function questProgress(p,event)events[event]=(events[event] or 0)+1 end
local function state()end
local n=0;local function check(v,m)assert(v,m);n+=1 end
local function newPlayer(id,level)
 local p={UserId=id};players[id]=p
 local s={rewardIdentity={},data={level=level or 20,xp=0,coins=0,combatChallenges={},quests={garden={progress=2}}}}
 sessions[p]=s;return p,s
end
"""
BASELINE=r"""
local p,s=newPlayer(1);local ledger={};recordCredit(ledger,p,20,100,0);sessions[p]=nil
check(ledger[1].rewardSession==s and ledger[1].rewardSession.data.quests.garden.progress==2,'Historical whole-session reference absent')
local now=100000;check(now-ledger[1].at>Credit.Window and ledger[1].rewardSession==s,'Idle expiry unexpectedly pruned reference')
print('BASELINE: expired idle credit retains whole departed session/profile at100000s; reference graph only')
"""
CHECKS=r"""
local p,s=newPlayer(1);local victim,vs=newPlayer(2);local finisher,fs=newPlayer(3)
local constructor1=joinedState(p,{level=1});local constructor2=joinedState(p,{level=1})
check(type(constructor1.rewardIdentity)=='table' and next(constructor1.rewardIdentity)==nil and getmetatable(constructor1.rewardIdentity)==nil,'Joined token is not opaque empty table')
check(constructor1.rewardIdentity~=constructor2.rewardIdentity,'Separate joins reused reward identity')
local function reachable(value,wanted,seen)
 if value==wanted then return true end
 if type(value)~='table'then return false end
 seen=seen or {};if seen[value]then return false end;seen[value]=true
 for k,v in pairs(value)do if reachable(k,wanted,seen)or reachable(v,wanted,seen)then return true end end
 return false
end
local ledger={};recordCredit(ledger,p,20,100,0)
check(ledger[1].rewardIdentity==s.rewardIdentity and ledger[1].rewardSession==nil,'Credit still retains session or wrong identity')
check(not reachable(ledger,s) and not reachable(ledger,s.data) and not reachable(ledger,p),'Credit graph retains session/profile/player')
check(next(ledger[1].rewardIdentity)==nil,'Reward token acquired back references')
sessions[p]=nil
check(100000-ledger[1].at>Credit.Window and not reachable(ledger,s),'Idle expired credit retained departed session')
Credit.Add(ledger,3,1,100000,100);check(ledger[1]==nil,'Existing expired ledger pruning changed')
sessions[p]=s
-- Missing token must neither be initialized nor earn/record contribution.
s.rewardIdentity=nil;ledger={};recordCredit(ledger,p,100,100,1)
check(next(ledger)==nil and s.rewardIdentity==nil,'Missing token was adopted or recorded')
s.rewardIdentity={};recordCredit(ledger,p,90,100,2);recordCredit(ledger,finisher,10,100,2)
s.rewardIdentity=nil
awardCombatKO(ledger,finisher,20,100,100,2,victim)
check(s.data.xp==0 and fs.data.xp==10,'Missing recipient token paid or redistributed share')
check(rewardHistory.pairs['1:2']==nil and next(ledger)==nil,'Missing-token attribution spent repeat history or retained ledger')
-- Malformed identity values cannot record or authorize attribution even if equal.
for _,bad in ipairs({false,true,0,1,'token'})do
 s.rewardIdentity=bad;ledger={};recordCredit(ledger,p,90,100,3)
 check(next(ledger)==nil,'Malformed identity recorded credit')
 s.rewardIdentity={};recordCredit(ledger,p,90,100,4);recordCredit(ledger,finisher,10,100,4)
 s.rewardIdentity=bad;ledger[1].rewardIdentity=bad;s.data.xp=0;fs.data.xp=0;rewardHistory={pairs={}}
 awardCombatKO(ledger,finisher,20,100,100,4,victim)
 check(s.data.xp==0 and fs.data.xp==10 and rewardHistory.pairs['1:2']==nil,'Matching malformed identity authorized payout')
end
s.rewardIdentity={}
-- Same UserId new session gets a new token, never inherits credit.
s.rewardIdentity={};ledger={};recordCredit(ledger,p,70,100,10)
local old=s;local replacement={rewardIdentity={},data={level=20,xp=0,coins=0,combatChallenges={}}};sessions[p]=replacement;s=replacement
recordCredit(ledger,p,1,100,11)
check(ledger[1].rewardIdentity==false,'Rejoin rehabilitated stale credit')
recordCredit(ledger,p,1,100,35)
check(ledger[1].rewardIdentity==false,'Continuous hits reset identity quarantine')
recordCredit(ledger,p,10,100,60.001)
check(ledger[1].rewardIdentity==s.rewardIdentity and ledger[1].damage==10,'Expired entry failed fresh identity acquisition')
-- Mode changes poison existing entry even when session identity itself is unchanged.
ledger={};recordCredit(ledger,p,50,100,70);s.testBaseline={};recordCredit(ledger,p,1,100,71)
check(ledger[1].rewardIdentity==false,'Mode change failed quarantine')
s.testBaseline=nil;recordCredit(ledger,p,1,100,72)
check(ledger[1].rewardIdentity==false,'Returning mode rehabilitated poisoned entry')
recordCredit(ledger,p,1,100,97);check(ledger[1].rewardIdentity==false,'Exact25s incorrectly replaced quarantine')
recordCredit(ledger,p,5,100,122.001);check(ledger[1].rewardIdentity==s.rewardIdentity,'Greater-than25s did not replace expired entry')
-- Payout rejects stale identity even without another hit, keeping denominator.
for _,kind in ipairs({'missing','stale','false','legacy','mode'})do
 s.data.xp=0;s.data.coins=0;s.testBaseline=nil;s.rewardIdentity={};fs.data.xp=0;fs.data.coins=0;rewardHistory={pairs={}}
 ledger={};recordCredit(ledger,p,90,100,200);recordCredit(ledger,finisher,10,100,200)
 if kind=='missing'then ledger[1].rewardIdentity=nil
 elseif kind=='stale'then s.rewardIdentity={}
 elseif kind=='false'then ledger[1].rewardIdentity=false
 elseif kind=='legacy'then ledger[1].rewardIdentity=nil;ledger[1].rewardSession=s
 else s.testBaseline={}end
 awardCombatKO(ledger,finisher,20,100,100,200,victim)
 check(s.data.xp==0 and s.data.coins==0,'Rejected '..kind..' token earned payout')
 check(fs.data.xp==10 and fs.data.coins==2,'Rejected '..kind..' damage redistributed')
 check(rewardHistory.pairs['1:2']==nil and next(ledger)==nil,'Rejected '..kind..' consumed history/retained ledger')
end
s.testBaseline=nil
-- Valid numeric payouts/quest events retain previous share and multiplier rules.
for _,level in ipairs({1,20,30,40,50,100})do
 for _,damage in ipairs({10,30,90})do
  s.rewardIdentity={};s.data.level=level;s.data.xp=0;s.data.coins=0;fs.data.level=20;fs.data.xp=0;fs.data.coins=0
  ledger={};rewardHistory={pairs={}};events={}
  recordCredit(ledger,p,damage,100,300);recordCredit(ledger,finisher,100-damage,100,300)
  awardCombatKO(ledger,finisher,20,100,100,300,victim)
  local factor=Progression.RewardFactor(level,20)
  check(s.data.xp==math.floor(100*(damage/100)*factor),'Valid XP share/balance changed')
  check(s.data.coins==math.floor(20*(damage/100)*factor),'Valid coin share/balance changed')
  check(fs.data.xp==100-damage and next(ledger)==nil,'Finisher share/consumption changed')
 end
end
print('PASS',n,'actual opaque credit identity assertions; reference graph and synthetic payouts only')
"""
def run(code):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False)as f:f.write(code);path=Path(f.name)
 try:return subprocess.run(['luau',str(path)],cwd=ROOT,text=True,capture_output=True,encoding='utf-8')
 finally:path.unlink()
if __name__=='__main__':
 r=run(build('--baseline' in sys.argv));print(r.stdout+r.stderr,end='')
 if r.returncode:sys.exit(r.returncode)
 if '--negative-controls' in sys.argv:
  for name,old,new,expected in [
   ('session reference restored','entry.rewardIdentity=s.rewardIdentity','entry.rewardIdentity=s','Credit still retains session'),
   ('quarantine repaired','entry.rewardIdentity=false','entry.rewardIdentity=s.rewardIdentity;entry.rewardTest=s.testBaseline~=nil','Rejoin rehabilitated'),
   ('recipient comparison removed','entry.rewardIdentity~=rs.rewardIdentity','false','Rejected missing token earned'),
   ('missing recorder token allowed','or type(s.rewardIdentity)~="table" or damage<=0','or damage<=0','Missing token was adopted'),
   ('malformed payout identity','or type(rs.rewardIdentity)~="table" or not entry','or not entry','Matching malformed identity authorized payout'),
   ('joined token carries profile','rewardIdentity={},voice=','rewardIdentity={data=data},voice=','Joined token is not opaque')]:
   def mutate(b):
    assert old in b,name
    return b.replace(old,new,1)
   r=run(build(mutation=mutate));out=r.stdout+r.stderr
   assert r.returncode and expected in out,out
   print('PASS negative control:',name)
