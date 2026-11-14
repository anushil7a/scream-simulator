"""Actual combat quest hooks/catalog/Profile persistence; mocked engine and atomic store only."""
from pathlib import Path
from config_fixture import inline_compact_layout
import subprocess,tempfile,sys
ROOT=Path(__file__).resolve().parents[1]
def read(path,baseline=False):
 return subprocess.check_output(['git','show','7a0b044:'+path],cwd=ROOT,text=True,encoding='utf-8') if baseline else (ROOT/path).read_text(encoding='utf-8')
def build(baseline=False,mutation=None):
 config=inline_compact_layout(read('src/ReplicatedStorage/Shared/Config.luau',baseline),ROOT)
 progression=read('src/ReplicatedStorage/Shared/Progression.luau',baseline)
 profiles=read('src/ServerScriptService/Profiles.luau',baseline)
 bootstrap=read('src/ServerScriptService/Bootstrap.server.luau',baseline)
 if mutation:config,profiles,bootstrap=mutation(config,profiles,bootstrap)
 hooks=bootstrap[bootstrap.index('local function questProgress('):bootstrap.index('local function stopQuest(')]
 accept=bootstrap.split(' elseif verb=="AcceptQuest" then',1)[1].split(' elseif verb=="AbandonQuest" then',1)[0]
 claim=bootstrap.split(' elseif verb=="ClaimQuest" then',1)[1].split(' elseif verb=="SetSettings"',1)[0]
 guarded=bootstrap[bootstrap.index('local function stepSustained('):bootstrap.index('  for _,viewer in ipairs(Players:GetPlayers())',bootstrap.index('local function stepSustained('))]+' end\nend\n'
 legacy=bootstrap[bootstrap.index(' local castMessage',bootstrap.index('local function cast(')):bootstrap.index(' if obstruction then',bootstrap.index(' local castMessage',bootstrap.index('local function cast(')))]
 return "local realQuestLifecycle=require('../src/ReplicatedStorage/Shared/QuestLifecycle')\nlocal realGuide=require('../src/ReplicatedStorage/Shared/QuestGuide')\nlocal realCredit=require('../src/ReplicatedStorage/Shared/CombatCredit')\nlocal realTraining=require('../src/ReplicatedStorage/Shared/TrainingRules')\n"+PRE+progression+AFTER_PROGRESSION+config+AFTER_CONFIG+profiles+'\nend\nlocal P=loadProfiles()\n'+SETUP+hooks+guarded+'\nlocal function accept(p,s,arg)\n'+accept+'\nend\nlocal function claim(p,s,arg)\n'+claim+'\nend\n'+CHECKS
PRE="\nlocal Healing=require('../src/ReplicatedStorage/Shared/Healing')\nlocal Combat=require('../src/ReplicatedStorage/Shared/VoiceCombat')\nlocal Lease=require('../src/ReplicatedStorage/Shared/ProfileLease')\nlocal Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}\nlocal Color3={fromRGB=function(r,g,b)return {r,g,b}end}\nlocal Progression=(function()\n"
AFTER_PROGRESSION="\nend)()\n-- MUTATION_INSERT\nlocal script={Parent={WaitForChild=function(_,name)return name end}}\nlocal config\nlocal require=function(name)\n if name=='Healing' then return Healing elseif name=='VoiceCombat' then return Combat elseif name=='Progression' then return Progression\n elseif name=='Config' then return config elseif name=='Lease' then return Lease end\n error('Unexpected dependency '..tostring(name))\nend\nlocal function loadConfig()\n"
AFTER_CONFIG="\nend\nconfig=loadConfig()\nlocal now,clock,guid=1000,100,0\nlocal os={time=function()return now end,clock=function()return clock end}\nlocal task={wait=function(t)now+=t;clock+=t end}\nlocal durable;local writes=0\nlocal store={UpdateAsync=function(_,key,transform)\n assert(key=='Player_7','Unexpected test key');writes+=1\n local result=transform(durable)\n if result~=nil then durable=result end\n return result\nend}\nlocal services={DataStoreService={GetDataStore=function(_,name)assert(name=='ScreamSimulator_v1','Wrong fake store');return store end},\n ReplicatedStorage={Shared={Config='Config',ProfileLease='Lease'}},RunService={IsStudio=function()return false end},\n HttpService={GenerateGUID=function()guid+=1;return 'retirement-'..guid end}}\nlocal game={JobId='retirement-fixture',GetService=function(_,name)return services[name]end}\nlocal warn=function()end\nlocal function loadProfiles()\n"
SETUP=r"""
local Config=config
local Credit=realCredit;local TrainingRules=realTraining
local sessions={};local players={};local rewardHistory={pairs={}}
local Players={GetPlayerByUserId=function(_,id)return players[id]end}
local Commerce={Multiplier=function()return 1 end}
local notices=0;local reenter;local earned=0
local function state()notices+=1 end
local function coins(p,amount)sessions[p].data.coins+=amount;return amount end
local function xp(p,amount)earned+=amount;if reenter then local f=reenter;reenter=nil;f()end;return amount end
local QuestLifecycle=realQuestLifecycle
local function stopQuest(p)QuestLifecycle.Clear(sessions[p],Config.GetQuest) end
local function parts()return nil,nil end
local task={delay=function()end}
local fixtureBeam,fixtureEnded
local sustained={Step=function()return {},fixtureEnded,{},fixtureBeam end}
local function sustainedContext()return {}end
local function sustainedEnd()end
local function resolveSustained()end
local Soccer={Hit=function()return false end};local BeachVolley=Soccer
local p={UserId=1};players[1]=p
local function session(player,id)
 local s={rewardIdentity={},data=P.Default(),activeQuest=id,voice={},collected={}}
 s.data.level=20;if id then s.data.quests[id]={progress=0,claimed=false}end
 sessions[player]=s;return s
end
"""
CHECKS=r"""
local n=0;local function check(v,m)assert(v,m);n+=1 end
check(Config.GetQuest('practice_beams')~=nil and Config.GetQuest('arena_assist')~=nil,'Additive combat quest IDs missing')
local legacy={nick={1,1800,1200,'Soccer'},garden={3,130,80,'Garden'},beach={6,100,50,'Litter'},delivery={1,120,60,'Delivery'},crowd={1,100,40,'Crowd'},sprint={1,120,50,'Race'},dodge={3,160,70,'Evade'},arena={1,180,80,'Underdog'}}
check(#Config.Quests==10,'Unexpected quest catalog size')
local crowd=Config.GetQuest('crowd').description
check(crowd:find('3 different NPCs',1,true) and crowd:find('residents or training fighters',1,true) and crowd:find('during one beam',1,true) and crowd:find('do not need to be hit at the same instant',1,true),'Crowd copy lost distinct-target/non-simultaneous clarification')
for _,row in ipairs({{'crowd','Hit 3 different NPCs during one beam'},{'arena_assist','Assist an equal/higher-level arena KO'}})do
 local q=Config.GetQuest(row[1]);check(realGuide.Step(q,0)==row[2],'Quest guide objective mismatch')
 check(realGuide.Step(q,q.goal):find('claim in Quests',1,true)~=nil,'Completed quest guide missing claim')
end
local seen={}
for _,q in ipairs(Config.Quests)do
 check(not seen[q.id],'Duplicate quest ID');seen[q.id]=true
 local old=legacy[q.id]
 if old then check(q.goal==old[1] and q.xp==old[2] and q.coins==old[3] and q.event==old[4] and q.menuAvailable~=true,'Legacy quest semantics changed')end
end
for _,row in ipairs({{'arena_assist',1,120,50,'ArenaAssist'}})do
 local q=Config.GetQuest(row[1]);check(q.goal==row[2] and q.xp==row[3] and q.coins==row[4] and q.event==row[5] and q.menuAvailable==true,'New quest contract mismatch')
 local s=session(p,nil);accept(p,s,q.id)
 check(s.activeQuest==q.id and s.data.quests[q.id].progress==0,'Menu quest requires nonexistent giver')
 questProgress(p,'wrong');check(s.data.quests[q.id].progress==0,'Wrong event advanced task')
 s.data.quests[q.id].progress=q.goal;local before=s.data.coins;local beforeXP=earned
 reenter=function()claim(p,s,q.id)end;claim(p,s,q.id);claim(p,s,q.id)
 check(s.data.quests[q.id].claimed and s.data.coins==before+q.coins and earned==beforeXP+q.xp,'Reentrant/repeated claim duplicated reward')
 questProgress(p,q.event);check(s.data.quests[q.id].progress==q.goal,'Claimed progress changed')
end
for id in pairs(legacy)do
 local s=session(p,nil);accept(p,s,id);check(s.activeQuest==nil and s.data.quests[id]==nil,'Legacy discovery bypassed')
end
local retired=Config.GetQuest('practice_beams')
check(retired.retired==true and retired.goal==3 and retired.xp==60 and retired.coins==25,'Retired quest identity or reward changed')
local s=session(p,nil);accept(p,s,'practice_beams');check(s.activeQuest==nil and s.data.quests.practice_beams==nil,'Retired acceptance allowed')
s=session(p,'practice_beams');questProgress(p,'PracticeBeam');check(s.data.quests.practice_beams.progress==0,'Retired objective progressed')
local finisher={UserId=2};local victim={UserId=3};players[2]=finisher;players[3]=victim
local function assist(damage,level,hasVictim,at,online)
 local ss=session(p,'arena_assist');session(finisher,'arena');session(victim,nil)
 rewardHistory={pairs={}};players[1]=p;if online==false then players[1]=nil end
 local ledger={};recordCredit(ledger,p,damage,100,at);recordCredit(ledger,finisher,100-damage,100,at)
 awardCombatKO(ledger,finisher,level,100,100,at,hasVictim and victim or nil)
 check(next(ledger)==nil,'KO ledger was not consumed')
 return ss,ledger
end
s=session(p,'arena_assist');local ledger
s,ledger=assist(70,20,true,100,true);check(s.data.quests.arena_assist.progress==1,'Eligible equal-level assist failed')
local before=s.data.coins;awardCombatKO(ledger,finisher,20,100,100,100,victim)
check(s.data.coins==before and s.data.quests.arena_assist.progress==1,'Consumed ledger rewarded again')
for _,row in ipairs({{9,20,true,true},{70,19,true,true},{70,20,false,true},{70,20,true,false}})do
 s=assist(row[1],row[2],row[3],200,row[4]);check(s.data.quests.arena_assist.progress==0,'Ineligible assist progressed')
end
players[1]=p;s=session(p,'arena_assist');session(finisher,nil)
ledger={};recordCredit(ledger,p,100,100,300);awardCombatKO(ledger,p,20,100,100,300,victim)
check(s.data.quests.arena_assist.progress==0,'Finisher counted as assist')
s,ledger=assist(70,30,true,400,true);s.data.quests.arena_assist.progress=0
recordCredit(ledger,p,70,100,401);recordCredit(ledger,finisher,30,100,401);awardCombatKO(ledger,finisher,30,100,100,401,victim)
check(s.data.quests.arena_assist.progress==0,'Repeat-suppressed reward counted as assist')
s,ledger=assist(10,20,true,500,true);check(s.data.quests.arena_assist.progress==1,'Exact meaningful threshold rejected')
-- Actual Credit.Window boundary and stale contribution rejection.
for _,age in ipairs({25,25.001})do
 s=session(p,'arena_assist');session(finisher,nil);rewardHistory={pairs={}};players[1]=p
 ledger={};recordCredit(ledger,p,70,100,600);recordCredit(ledger,finisher,30,100,600)
 awardCombatKO(ledger,finisher,20,100,100,600+age,victim)
 check(s.data.quests.arena_assist.progress==(age==25 and 1 or 0),'Assist credit expiry boundary incorrect')
 check(next(ledger)==nil,'Expired/boundary ledger not consumed')
end
-- Credit is inactivity-based, not a rolling-damage window: chained hits retain it.
s=session(p,'arena_assist');session(finisher,nil);session(victim,nil);rewardHistory={pairs={}}
ledger={};recordCredit(ledger,p,10,100,700);recordCredit(ledger,p,1,100,724);recordCredit(ledger,p,1,100,748)
recordCredit(ledger,finisher,88,100,749);awardCombatKO(ledger,finisher,20,100,100,749,victim)
check(s.data.quests.arena_assist.progress==1,'Chained inactive-window credit semantics changed')
check(Config.GetQuest('arena_assist').description:find('expires after 25 seconds without a hit',1,true)~=nil,'Assist copy falsely implies rolling damage window')
-- Actual sanitize/load/save/release/rejoin with an isolated atomic store.
local seed=P.Default();seed.level=20;seed.xp=7;seed.coins=123
for _,q in ipairs(Config.Quests)do seed.quests[q.id]={progress=math.max(0,q.goal-1),claimed=q.id=='arena'};seed.availableQuests[q.id]=true end
local function preserve(d)
 check(d.coins==123 and d.xp==7 and d.level==20,'Unrelated economy changed')
 for _,q in ipairs(Config.Quests)do local v=d.quests[q.id];check(v and v.progress==math.max(0,q.goal-1) and v.claimed==(q.id=='arena') and d.availableQuests[q.id],'Saved quest state lost or reinterpreted')end
end
local clean=P.Sanitize(seed);preserve(clean)
for i=1,3 do clean=P.Sanitize(clean);preserve(clean)end
local defaults=P.Sanitize({});check(defaults.quests.practice_beams==nil and defaults.availableQuests.practice_beams==nil,'New quest invented saved state')
durable=seed;local loaded,writable=P.Load(7);check(writable,'Fake acquisition failed');preserve(loaded)
check(P.Save(7,loaded,true),'Fake save/release failed');preserve(durable)
now+=10;clock+=10;local rejoined,save=P.Load(7);check(save,'Fake rejoin failed');preserve(rejoined)
check(P.Save(7,rejoined,true),'Fake final release failed')
-- Both new claimed flags must survive persistence and deny reentrant/repeated claims.
for _,id in ipairs({'practice_beams','arena_assist'})do
 local q=Config.GetQuest(id);rejoined.quests[id]={progress=q.goal,claimed=true}
end
now+=10;clock+=10
local acquired,allowed=P.Load(7);check(allowed,'Claimed-state reacquisition failed')
for _,id in ipairs({'practice_beams','arena_assist'})do acquired.quests[id]=rejoined.quests[id] end
check(P.Save(7,acquired,true),'Claimed-state save failed')
now+=10;clock+=10;local claimedLoaded,claimedWritable=P.Load(7)
check(claimedWritable,'Claimed-state rejoin failed')
s={data=claimedLoaded};sessions[p]=s;local oldCoins=s.data.coins;local oldXP=earned
for _,id in ipairs({'practice_beams','arena_assist'})do
 local q=Config.GetQuest(id)
 check(s.data.quests[id].claimed and s.data.quests[id].progress==q.goal,'New claimed quest lost on rejoin')
 reenter=function()claim(p,s,id)end;claim(p,s,id);claim(p,s,id);reenter=nil
 check(s.data.coins==oldCoins and earned==oldXP,'Reloaded claimed quest replayed reward')
end
check(P.Save(7,claimedLoaded,true),'Claimed-state final release failed')
-- Actual Profiles fake-store reload -> mock inactive session -> actual acceptance/claim/Clear.
-- This does not execute the joined handler or prove native persistence.
local restartSeed=P.Default();restartSeed.level=20
for _,id in ipairs({'practice_beams','garden','delivery'})do
 local q=Config.GetQuest(id);restartSeed.quests[id]={progress=q.goal-1,claimed=false};restartSeed.availableQuests[id]=true
end
durable=restartSeed;now+=10;clock+=10
local beforeRestart,canWrite=P.Load(7);check(canWrite,'Restart fixture load failed')
check(P.Save(7,beforeRestart,true),'Restart fixture save failed');now+=10;clock+=10
local restartData,restartWritable=P.Load(7);check(restartWritable,'Restart fixture rejoin failed')
s={data=restartData,collected={}};sessions[p]=s
for _,id in ipairs({'practice_beams','garden','delivery'})do
 local q=Config.GetQuest(id)
 check(s.data.quests[id].progress==q.goal-1,'Reload lost unfinished counter before restart')
 if q.retired then accept(p,s,id);check(s.activeQuest~=id and s.data.quests[id].progress==q.goal-1,'Retired restart altered dormant progress');continue end
 accept(p,s,id);check(s.activeQuest==id and s.data.quests[id].progress==0,'Inactive acceptance did not restart attempt')
 if q.goal>1 then
  s.data.quests[id].progress=1;accept(p,s,id)
  check(s.data.quests[id].progress==1,'Duplicate active acceptance reset progress')
 end
end
s.data.quests.practice_beams.progress=3;s.activeQuest='garden';s.data.quests.garden.progress=1
accept(p,s,'practice_beams')
check(s.activeQuest=='garden' and s.data.quests.practice_beams.progress==3,'Completed acceptance discarded reward or active task')
local beforeCoins=s.data.coins;local beforeEarned=earned
claim(p,s,'practice_beams');claim(p,s,'practice_beams')
check(s.data.coins==beforeCoins+25 and earned==beforeEarned+60,'Restart sequence completion reward not exactly once')
check(s.activeQuest=='garden' and s.data.quests.garden.progress==1,'Claiming prior reward discarded current attempt')
accept(p,s,'practice_beams');check(s.activeQuest=='garden','Claimed acceptance replaced current task')
check(P.Save(7,restartData,true),'Restart fixture final release failed')
-- Old catalogs necessarily discard unknown new IDs: rollback needs coordination.
local catalog=Config.Quests;local old={};for _,q in ipairs(catalog)do if legacy[q.id]then table.insert(old,q)end end
Config.Quests=old;local rollback=P.Sanitize(seed);Config.Quests=catalog
check(rollback.quests.practice_beams==nil and rollback.quests.arena_assist==nil,'Rollback sanitation assumption changed')
print('PASS',n,'actual combat quest assertions; fake persistence and engine inputs only')
"""
def run(code):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False) as f:f.write(code);path=Path(f.name)
 try:return subprocess.run(['luau',str(path)],cwd=ROOT,text=True,capture_output=True,encoding='utf-8')
 finally:path.unlink()
if __name__=='__main__':
 result=run(build('--baseline' in sys.argv));print(result.stdout+result.stderr,end='')
 if result.returncode:sys.exit(result.returncode)
 raw=read('src/ServerScriptService/Bootstrap.server.luau')
 cast=raw[raw.index('local function cast('):raw.index('local function dodge(')]
 assert 'MicPracticeTarget' not in raw and 'questProgress(p,"PracticeBeam")' not in raw,'Retired production practice hook remains'
 print('PASS source contract: no production mic-practice target/progress hooks')
 if '--negative-controls' in sys.argv:
  def change(which,old,new):
   def mutate(c,p,b):
    values=[c,p,b];assert old in values[which],'Mutation did not match'
    values[which]=values[which].replace(old,new,1);return tuple(values)
   return mutate
  controls=[
   ('retired acceptance gate',change(2,'if q and q.retired==true then return end',''),'Retired restart altered dormant progress'),
   ('retired progress gate',change(2,' or q.retired==true',''),'Retired objective progressed'),
   ('assist finisher gate',change(2,'victim and recipient~=finisher and underdog and meaningful[id]','victim and underdog and meaningful[id]'),'Finisher counted as assist'),
   ('assist level gate',change(2,'victim and recipient~=finisher and underdog and meaningful[id]','victim and recipient~=finisher and meaningful[id]'),'Ineligible assist progressed'),
   ('menu acceptance gate',change(2,'q.menuAvailable~=true and not s.data.availableQuests[q.id]','not s.data.availableQuests[q.id]'),'Menu quest requires'),
   ('claim flag before reward',change(2,'v.claimed=true;if q.id=="nick"','if q.id=="nick"'),'Reentrant/repeated claim'),
   ('new saved quest preservation',change(1,'local old=raw.quests[q.id]','local old=q.id~="practice_beams" and raw.quests[q.id]'),'Saved quest state lost')]
  for name,mutation,expected in controls:
   failed=run(build(mutation=mutation));output=failed.stdout+failed.stderr
   assert failed.returncode and expected in output,output
   print('PASS negative control:',name)
