"""Test-mode cross-session reward isolation; actual helper/dev/save slices, fake stores only."""
from pathlib import Path
from config_fixture import inline_compact_layout
import subprocess,tempfile,sys,re
ROOT=Path(__file__).resolve().parents[1]
def read(path,baseline=False):
 return subprocess.check_output(['git','show','1e14e91:'+path],cwd=ROOT,text=True,encoding='utf-8') if baseline else (ROOT/path).read_text(encoding='utf-8')
def build(baseline=False,mutation=None):
 config=inline_compact_layout(read('src/ReplicatedStorage/Shared/Config.luau',baseline),ROOT)
 profiles=read('src/ServerScriptService/Profiles.luau',baseline)
 access=read('src/ServerScriptService/DeveloperAccess.luau',baseline)
 b=read('src/ServerScriptService/Bootstrap.server.luau',baseline)
 if mutation:b=mutation(b)
 dev=b[b.index('local function dev(p,command)'):b.index('World.OnVehicleSweep=')]
 payout=b[b.index('local function xp('):b.index('local function stopQuest(')]
 save=b[b.index('local function autosave('):b.index('task.spawn(function() while true do task.wait(60)')]
 predicates=''
 if not baseline:
  sections={'sustained':b[b.index('local function resolveSustained('):b.index('local function destructionHint(')],'legacy':b[b.index('local function cast('):b.index('local function dodge(')]}
  for name,section,loop in [('sustainedPlayer','sustained','for _,p in ipairs(players) do'),('legacyPlayer','legacy','for _,target in ipairs(Players:GetPlayers()) do'),('sustainedBot','sustained','for _,bot in ipairs(World.Bots) do'),('legacyBot','legacy','for _,bot in ipairs(World.Bots) do')]:
   body=sections[section].split(loop,1)[1]
   match=re.search(r'\bif (.*?) then',body,re.S);assert match,name
   predicates+='local function '+name+'(actor,targetPlayer)\nlocal p,target,ctx,s,ts,r,tr,c,tc,h,th,bot,stats,sound,origin,direction,length,now=predicateVars(actor,targetPlayer)\n'+('p=actor\n' if name.startswith('legacy') else '')+'return '+match[1]+'\nend\n'
 return PRE+config+BETWEEN+profiles+HELPERS+access+SETUP+PREDICATE_SETUP+payout+dev+save+predicates+(CHECKS if baseline else FIXED)
PRE="local Credit=require('../src/ReplicatedStorage/Shared/CombatCredit')\nlocal TrainingRules=require('../src/ReplicatedStorage/Shared/TrainingRules')\n\nlocal Healing=require('../src/ReplicatedStorage/Shared/Healing')\nlocal Combat=require('../src/ReplicatedStorage/Shared/VoiceCombat')\nlocal Progression=require('../src/ReplicatedStorage/Shared/Progression')\nlocal Lease=require('../src/ReplicatedStorage/Shared/ProfileLease')\nlocal Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}\nlocal Color3={fromRGB=function(r,g,b)return {r,g,b}end}\nlocal CFrame={new=function(...)return {...}end}\nlocal Enum={CreatorType={User='User',Group='Group'}}\nlocal script={Parent={WaitForChild=function(_,name)return name end}}\nlocal config\nlocal require=function(name)\n if name=='Healing' then return Healing elseif name=='VoiceCombat' then return Combat elseif name=='Progression' then return Progression\n elseif name=='Config' then return config elseif name=='Lease' then return Lease end\n error('Unexpected dependency '..tostring(name))\nend\nlocal function loadConfig()\n"
BETWEEN="\nend\nconfig=loadConfig();local Config=config\nlocal studio=false\nlocal localFixture=false\nlocal durable={};local writes=0;local guid=0\nlocal store={UpdateAsync=function(_,key,transform)writes+=1;local d=transform(durable[key]);if d~=nil then durable[key]=d end;return d end}\nlocal RunService={IsStudio=function()return studio end}\nlocal services={DataStoreService={GetDataStore=function()return store end},\n ReplicatedStorage={Shared={Config='Config',ProfileLease='Lease'}},RunService=RunService,HttpService={GenerateGUID=function()guid+=1;return 'fixture-'..guid end}}\nlocal game={JobId='dev-fixture',GetService=function(_,name)return services[name]end,CreatorType=Enum.CreatorType.User,CreatorId=11499795799}\nlocal warn=function()end\nlocal function loadProfiles()\n"
HELPERS='\nend\nlocal Profiles=loadProfiles()\nlocal Access=(function()\n'
SETUP="\nend)()\nlocal owner={UserId=11499795799,Parent=true,SetAttribute=function()end};local ordinary={UserId=1234,Parent=true,SetAttribute=function()end};local third={UserId=5678,Parent=true,SetAttribute=function()end}\nlocal sessions={};local busy=false;local notices=0;local healthSync=0;local entitlementWrites=0;local movement=false\nlocal Commerce={Busy=function()return busy end,Multiplier=function()return 1 end}\nlocal function state()notices+=1 end\nlocal function parts()return nil,nil,{Health=100,MaxHealth=100}end\nlocal World={SafeSpawn={},Bots={}}\nlocal canceled=0;local function cancelSustained(p,s,now)canceled+=1;s.sustained=nil end\nlocal function syncHealth()healthSync+=1 end\nlocal function protect()error('Unexpected teleport')end\nlocal function stopQuest()error('Unexpected quest reset')end\nlocal function restoreBot()error('Unexpected bot reset')end\nlocal VoiceCombat=Combat\nlocal players={[owner.UserId]=owner,[ordinary.UserId]=ordinary,[third.UserId]=third}\nlocal Players={GetPlayerByUserId=function(_,id)return players[id]end}\nlocal rewardHistory={pairs={}}\nlocal function coins(p,n)sessions[p].data.coins+=n end\nlocal Entitlements={SetStudioMovement=function(_,enabled)movement=enabled;entitlementWrites+=1 end,HasStudioMovement=function()return movement end}\nlocal function fresh(p,level,xpValue)\n sessions[p]={data=Profiles.Sanitize({schemaVersion=4,level=level,xp=xpValue or 17,sound='TinyAah',aura='Gold',coins=123,\n amplifierOwned=true,amplifierEquipped=true,customColor='FA4FFF',useCustomColor=true,settings={volume=.4,reducedShake=true},\n achievements={FirstBeam=true},availableQuests={garden=true},quests={garden={progress=1,claimed=false}}})}\n return sessions[p]\nend\nlocal n=0;local function check(ok,msg)assert(ok,msg);n+=1 end\n"
CHECKS=r"""
local function acquire(p)
 local data,writable=Profiles.Load(p.UserId);check(writable,'Fake profile acquisition failed')
 sessions[p]={data=data,canSave=true,credit={},protectedUntil=0,dodgingUntil=0};return sessions[p]
end
local victim=acquire(owner);local attacker=acquire(ordinary)
check(victim.data.level==1 and attacker.data.level==1,'Fresh level precondition')
dev(owner,'MaxLevel')
check(victim.data.level==100 and victim.testBaseline.level==1,'Actual owner test command did not freeze baseline')
local maximum=Config.HealthForLevel(victim.data.level)
recordCredit(victim.credit,ordinary,maximum,maximum,100)
awardCombatKO(victim.credit,ordinary,victim.data.level,maximum,Config.PlayerKOXP(victim.data.level),100,owner)
local total=attacker.data.xp;for level=1,attacker.data.level-1 do total+=Config.XPToNext(level)end
print('TEST VICTIM PAYOUT',total,'XP',attacker.data.coins,'coins','recipient level',attacker.data.level)
check(total==862 and attacker.data.coins==25,'Historical test-victim payout changed')
autosave(owner,victim);autosave(ordinary,attacker)
check(durable['Player_'..owner.UserId].level==1,'Owner baseline did not remain isolated')
check(durable['Player_'..ordinary.UserId].level==attacker.data.level and durable['Player_'..ordinary.UserId].xp==attacker.data.xp and durable['Player_'..ordinary.UserId].coins==25,'Recipient contamination was not saved')
-- Test attacker contribution can help a normal recipient finish shared trainer life.
local helper=acquire(third);local tier=TrainingRules.Tiers[1]
local ledger={};recordCredit(ledger,owner,72,80,200);recordCredit(ledger,third,8,80,200)
awardCombatKO(ledger,third,tier.level,80,tier.xp,200,nil,tier)
print('MIXED TRAINER PAYOUT',helper.data.xp,'XP',helper.data.coins,'coins','challenge',helper.data.combatChallenges.fighters)
check(helper.data.xp>0 and helper.data.combatChallenges.fighters==1,'Historical mixed trainer help did not reward ordinary recipient')
print('PASS',n,'baseline contamination reproduction assertions; fake atomic store only')
"""
PREDICATE_SETUP=r"""
local Rules={CanTarget=function()return true end,InBeam=function()return true end}
local function audible()return true end
local function predicateVars(actor,targetPlayer)
 local root={Position=0};local bot={alive=true,root={Parent=true,Position=0},model={}}
 -- sustained p is target, legacy p is actor: wrapper substitutes identifiers below.
 return targetPlayer,targetPlayer,{player=actor,position=0,origin=0,character={}},sessions[actor],sessions[targetPlayer],root,root,{},{},{},{},bot,{range=30,width=4},{range=30,width=4},0,1,30,100
end
"""
FIXED=r"""
local function acquire(p)
 local data,writable=Profiles.Load(p.UserId);check(writable,'Fake profile acquisition failed')
 sessions[p]={data=data,canSave=true,credit={},voice={},protectedUntil=0,dodgingUntil=0};return sessions[p]
end
local victim=acquire(owner);local attacker=acquire(ordinary);local helper=acquire(third)
victim.voice.capture={};victim.sustained={};victim.credit[ordinary.UserId]={damage=20,at=1}
dev(owner,'MaxLevel')
check(victim.data.level==100 and victim.testBaseline.level==1,'Test baseline not frozen before mutation')
check(canceled==1 and victim.voice.capture==nil and next(victim.credit)==nil,'Test transition retained attack or incoming credit')
local baseline=victim.testBaseline;dev(owner,'AddLevels');check(victim.testBaseline==baseline and canceled==1,'Repeated test command recaptured baseline or transition')
attacker.activeQuest='arena';attacker.data.quests.arena={progress=0,claimed=false};attacker.data.availableQuests.arena=true;attacker.data.combatChallenges.fighters=2
local function equal(a,b)
 if type(a)~=type(b)then return false end
 if type(a)~='table'then return a==b end
 for k,v in pairs(a)do if not equal(v,b[k])then return false end end
 for k in pairs(b)do if a[k]==nil then return false end end
 return true
end
local rewardSnapshot=Profiles.Sanitize(attacker.data)

local maximum=Config.HealthForLevel(victim.data.level)
recordCredit(victim.credit,ordinary,maximum,maximum,100)
awardCombatKO(victim.credit,ordinary,100,maximum,Config.PlayerKOXP(100),100,owner)
check(attacker.data.level==1 and attacker.data.xp==0 and attacker.data.coins==0,'Test victim paid ordinary player')
check(next(victim.credit)==nil and next(rewardHistory.pairs)==nil,'Rejected mixed KO retained credit or spent repeat history')
check(equal(attacker.data,rewardSnapshot),'Rejected mixed victim changed XP/coins/quests/challenges snapshot')
autosave(owner,victim);autosave(ordinary,attacker)
check(durable['Player_'..owner.UserId].level==1 and durable['Player_'..ordinary.UserId].level==1 and durable['Player_'..ordinary.UserId].coins==0,'Test progress reached saved ordinary/baseline data')
check(Profiles.Save(owner.UserId,victim.testBaseline,true) and Profiles.Save(ordinary.UserId,attacker.data,true),'Fake baseline release failed')
local ownerRejoin,ownerWritable=Profiles.Load(owner.UserId);local normalRejoin,normalWritable=Profiles.Load(ordinary.UserId)
check(ownerWritable and normalWritable,'Fake baseline rejoin failed')
check(equal(ownerRejoin,victim.testBaseline) and equal(normalRejoin,rewardSnapshot),'Fake rejoin lost baseline or retained mixed reward')
attacker.data=normalRejoin
check(not sameCombatMode(victim,attacker) and not sameCombatMode(attacker,victim),'Mixed PvP allowed')
check(sameCombatMode(attacker,helper) and sameCombatMode(victim,victim),'Same mode incorrectly blocked')
check(not sameCombatMode(nil,attacker) and not sameCombatMode(attacker,nil),'Missing session accepted')
check(not canDamageBots(victim) and canDamageBots(attacker),'Shared NPC mode gate incorrect')
localFixture=true;check(canDamageBots(victim),'Guarded local fixture blocked');localFixture=false
for _,fn in ipairs({sustainedPlayer,legacyPlayer})do
 check(not fn(owner,ordinary) and not fn(ordinary,owner),'Actual target predicate allows mixed PvP')
 check(fn(ordinary,third),'Actual target predicate rejects legitimate PvP')
end
for _,fn in ipairs({sustainedBot,legacyBot})do
 check(not fn(owner,ordinary) and fn(ordinary,third),'Actual NPC predicate allows test damage')
 localFixture=true;check(fn(owner,ordinary),'Actual NPC predicate rejects guarded local fixture');localFixture=false
end
studio=true;check(not canDamageBots(victim),'Ordinary Studio bypassed NPC isolation');studio=false
local old=helper.data.level;dev(third,'MaxLevel');check(helper.data.level==old and helper.testBaseline==nil,'Ordinary player granted test tools')
local resets=0
-- ResetBots must reject before entering test mode in a live-like environment.
local previous=sessions[owner];sessions[owner]={data=Profiles.Default(),voice={},credit={}}
dev(owner,'ResetBots');check(sessions[owner].testBaseline==nil,'Rejected ResetBots froze real save')
studio=true;dev(owner,'ResetBots');check(sessions[owner].testBaseline==nil,'Ordinary Studio ResetBots froze save');studio=false;sessions[owner]=previous
local tier=TrainingRules.Tiers[1]
local function reward(ledger,finisher,now,target)
 awardCombatKO(ledger,finisher,target and sessions[target].data.level or tier.level,100,100,now,target,target and nil or tier)
end
attacker.data.combatChallenges={}
-- Mixed contribution cannot transfer test damage into legitimate share or challenge.
local ledger={};recordCredit(ledger,owner,90,100,200);recordCredit(ledger,third,10,100,200)
local before=helper.data.xp;reward(ledger,third,200,nil)
check(helper.data.xp-before==10,'Rejected test contribution redistributed to normal finisher')
check(next(ledger)==nil,'Mixed ledger not consumed')
check(victim.data.xp==0,'Test NPC contribution paid outside fixture')
-- Immutable acquisition identity: departure/rejoin never adopts earlier credit.
ledger={};recordCredit(ledger,third,90,100,300);local oldSession=helper
helper={data=Profiles.Default(),voice={},credit={}};sessions[third]=helper
recordCredit(ledger,third,1,100,301)
check(ledger[third.UserId].rewardSession==false,'Session replacement rehabilitated old credit')
recordCredit(ledger,third,1,100,325)
check(ledger[third.UserId].rewardSession==false,'Continuous hits cleared quarantine')
recordCredit(ledger,ordinary,10,100,325);before=attacker.data.xp
reward(ledger,ordinary,325,nil)
check(helper.data.xp==0 and attacker.data.xp-before==math.floor(100*10/102),'Quarantined share paid or redistributed')
-- Mode transition of existing outgoing contribution also poisons its whole entry.
ledger={};recordCredit(ledger,third,70,100,400);helper.testBaseline=Profiles.Default();recordCredit(ledger,third,1,100,401)
check(ledger[third.UserId].rewardSession==false,'Mode transition adopted prior contribution')
helper.testBaseline=nil;recordCredit(ledger,third,1,100,402)
check(ledger[third.UserId].rewardSession==false,'Returning mode rehabilitated quarantined credit')
recordCredit(ledger,third,10,100,427.001)
check(ledger[third.UserId].rewardSession==helper and ledger[third.UserId].damage==10,'Genuinely expired entry did not reset provenance')
-- Payout-time validation without a new hit rejects old session and mode too.
for _,mode in ipairs({'departed','rejoined','test','untagged'})do
 attacker.data.level=1;attacker.data.xp=0;attacker.data.combatChallenges={}
 ledger={};sessions[third]=helper;helper.testBaseline=nil;recordCredit(ledger,third,90,100,500)
 recordCredit(ledger,ordinary,10,100,500)
 if mode=='departed' then sessions[third]=nil
 elseif mode=='rejoined' then sessions[third]={data=Profiles.Default(),voice={}}
 elseif mode=='test' then helper.testBaseline=Profiles.Default()
 else ledger[third.UserId].rewardSession=nil end
 before=attacker.data.xp;reward(ledger,ordinary,500,nil)
 check(attacker.data.xp-before==10,'Rejected '..mode..' credit inflated normal share')
 check(next(ledger)==nil,'Rejected provenance retained ledger')
end
sessions[third]=helper;helper.testBaseline=nil
-- Finisher absent/mismatched and test NPC mode all fail closed.
for _,kind in ipairs({'missing','mixed','testnpc'})do
 ledger={};recordCredit(ledger,ordinary,100,100,600)
 local coinsBefore=attacker.data.coins
 if kind=='missing' then sessions[ordinary]=nil;reward(ledger,ordinary,600,nil);sessions[ordinary]=attacker
 elseif kind=='mixed' then reward(ledger,ordinary,600,owner)
 else recordCredit(ledger,owner,100,100,600);reward(ledger,owner,600,nil)end
 check(attacker.data.coins==coinsBefore and next(ledger)==nil,'Invalid finisher/mode leaked reward')
end
-- Rejected assist attribution must not spend repeat-pair history.
rewardHistory={pairs={}};ledger={};attacker.data.level=1;attacker.data.xp=0;helper.data.level=1
recordCredit(ledger,owner,90,100,700);recordCredit(ledger,ordinary,10,100,700)
reward(ledger,ordinary,700,third)
check(rewardHistory.pairs[tostring(owner.UserId)..':'..tostring(third.UserId)]==nil,'Rejected test assist spent repeat history')
check(rewardHistory.pairs[tostring(ordinary.UserId)..':'..tostring(third.UserId)]~=nil,'Legitimate finisher repeat history missing')
-- Actual first dev transition also invalidates outgoing pre-entry credit at payout.
local testOwner=sessions[owner];local transition={data=Profiles.Default(),voice={},credit={}};sessions[owner]=transition
ledger={};recordCredit(ledger,owner,90,100,800);dev(owner,'MaxLevel')
recordCredit(ledger,ordinary,10,100,800);before=attacker.data.coins
reward(ledger,ordinary,800,third)
check(transition.data.xp==0 and attacker.data.coins-before<=2,'Pre-test outgoing credit paid or redistributed')
check(transition.testBaseline.level==1,'Outgoing-credit transition damaged baseline');sessions[owner]=testOwner
-- Both test participants may interact, but save selection remains baseline-only.
helper.testBaseline=Profiles.Sanitize(helper.data)
check(sameCombatMode(victim,helper),'Test-to-test interaction unexpectedly blocked')
localFixture=true;ledger={};recordCredit(ledger,owner,100,100,900)
reward(ledger,owner,900,nil);check(next(ledger)==nil,'Local fixture payout failed to consume credit');localFixture=false
print('PASS',n,'test-session reward isolation assertions; helper-level synthetic inputs and fake stores only')
"""
def run(code):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False)as f:f.write(code);path=Path(f.name)
 try:return subprocess.run(['luau',str(path)],cwd=ROOT,text=True,capture_output=True,encoding='utf-8')
 finally:path.unlink()
if __name__=='__main__':
 result=run(build('--baseline' in sys.argv));print(result.stdout+result.stderr,end='')
 if result.returncode:sys.exit(result.returncode)
 if '--negative-controls' in sys.argv:
  controls=[('victim mode gate','(victim and not sameCombatMode(fs,sessions[victim]))','false','Test victim paid'),
   ('immutable entry quarantine','entry.rewardSession=false','entry.rewardSession=s;entry.rewardTest=s.testBaseline~=nil','Session replacement rehabilitated'),
   ('payout provenance','entry.rewardSession~=rs','false','Quarantined share paid'),
   ('NPC damage gate','(s.testBaseline==nil or localFixture==true)','true','Shared NPC mode gate'),
   ('baseline freeze','s.testBaseline=Profiles.Sanitize(s.data)','s.testBaseline={level=100}','Test baseline not frozen')]
  controls.extend([
   ('sustained player wiring','p~=ctx.player and sameCombatMode(sessions[ctx.player],ts) and r','p~=ctx.player and r','Actual target predicate allows mixed PvP'),
   ('legacy player wiring','target~=p and sameCombatMode(s,ts) and tr','target~=p and tr','Actual target predicate allows mixed PvP'),
   ('sustained bot wiring','canDamageBots(sessions[ctx.player]) and bot.alive','bot.alive','Actual NPC predicate allows test damage'),
   ('legacy bot wiring','canDamageBots(s) and bot.alive','bot.alive','Actual NPC predicate allows test damage'),
   ('ResetBots guard','if command=="ResetBots" and not localFixture then','if false then','Rejected ResetBots froze real save'),
   ('first entry cancellation','cancelSustained(p,s,os.clock());VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0);s.credit={}','','Test transition retained attack')])
  for name,old,new,expected in controls:
   def mutate(b):
    assert old in b,name
    return b.replace(old,new,1)
   failed=run(build(mutation=mutate));out=failed.stdout+failed.stderr
   assert failed.returncode and expected in out,out
   print('PASS negative control:',name)
