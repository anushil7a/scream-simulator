"""Actual server step differential: only advisory contact position may differ; no native/hitbox claim."""
from pathlib import Path
import subprocess,tempfile,sys
R=Path(__file__).resolve().parents[1];P='src/ServerScriptService/Bootstrap.server.luau'
source=(R/P).read_text(encoding='utf8')
try:baseline=subprocess.check_output(['git','show','5622daa54424e639e7d3f671b2e453ff377b2cb6:'+P],cwd=R,text=True,encoding='utf8',stderr=subprocess.PIPE)
except subprocess.CalledProcessError as exc:raise SystemExit('Required local 5622daa54424e639e7d3f671b2e453ff377b2cb6 baseline unavailable; no fetch attempted.') from exc
def step(s):return s[s.index('local function stepSustained('):s.index('local function cast(')]

PRE=r'''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local function vector(x,y,z)return {_type='Vector3',X=x,Y=y,Z=z}end
local function typeof(o)return type(o)=='table' and o._type or type(o)end
local function serial(v)
 if type(v)~='table'then return tostring(v)end
 local keys={};for k in pairs(v)do table.insert(keys,k)end;table.sort(keys,function(a,b)return tostring(a)<tostring(b)end)
 local out={};for _,k in ipairs(keys)do table.insert(out,tostring(k)..'='..serial(v[k]))end;return '{'..table.concat(out,';')..'}'
end
'''
ENV=r'''
local calls,contacts={},{}
local VoiceCombat=require('../src/ReplicatedStorage/Shared/VoiceCombat')
local Config={HealQuietSeconds=12,PlayerKOXP=function(level)return level*2 end}
local function log(...)table.insert(calls,{...})end
local function root(position,class)
 local r={_type='Instance',Parent=true,Position=position or vector(1,3,10)}
 function r:IsA(name)return name==(class or 'BasePart')end;return r
end
local playerRoot=root(vector(1,3,10));local botRoot=root(vector(5,3,12))
local character={_type='Instance'}
function character:IsA(name)return name=='Model'end
function character:FindFirstChild()return playerRoot end
local victim={UserId=2,Character=character};local h={Health=100,MaxHealth=100}
local defender={data={level=20},nextHeal=2}
local bot={id=3,root=botRoot,health=100,maxHealth=100,alive=true,training={level=10,xp=5},credit={}}
local object={health=50,GetAttribute=function(self)return self.health end}
local queuedDetails={player={player=victim,session=defender,humanoid=h},bot={bot=bot},object={object=object}}
local queuedHits={{id='player',damage=3,firstHit=true}}
local p={UserId=1,GetAttribute=function(_,key)log('attribute',key);return 7 end}
local s={sustained={intent={level=10,damageTotal=7,audioStyleId='TinyAah'}},data={level=10},botRewards={},nextHeal=1}
local ended=nil
local function sustainedContext()log('context');return {position=vector(0,0,0)}end
local function resolveSustained()end
local sustained={Step=function()log('step');return queuedHits,ended,queuedDetails,nil end}
local function sustainedEnd(_,value,now)log('end',value or false,now)end
local function recordCredit(credit,_,actual,maximum,now)credit.amount=(credit.amount or 0)+actual;log('credit',actual,maximum,now)end
local function awardCombatKO(credit,_,level,maximum,xp,now,player,training)log('award',credit.amount or 0,level,maximum,xp,now,player and player.UserId or 0,training and training.level or 0)end
local function eject(_,humanoid)log('eject');humanoid.Health=100;playerRoot.Position=vector(999,4,999)end
local function knockOutBot(b)log('bot-ko');b.alive=false;b.root.Position=vector(-999,4,-999)end
local function questProgress(_,kind)log('quest',kind)end
local function coins(_,amount)log('coins',amount)end;local function xp(_,amount)log('xp',amount)end
local function state(_,hint)log('state',hint)end
local function destructionHint(_,result)return result and result.reason end
local function beamColor()return 'Gold'end
local World={ReactToScream=function(b)log('react',b.id)end,UpdateBot=function(b)log('bot-update',b.health,b.alive)end}
local SustainedRewards={Hit=function(intent,rewards,id,now,first,ko)log('reward',id,now,first,ko);rewards.hit=(rewards.hit or 0)+1;return 2,3 end}
local Destruction={Damage=function(o,level,damage)
 log('object-damage',level,damage)
 if o.locked then return {reason='level'}end
 o.health=math.max(0,o.health-damage);return {health=o.health}
end}
local effect={FireClient=function(_,who,kind,position,...)
 if kind=='SustainedHit'then table.insert(contacts,position or false);position='advisory omitted'end
 log('effect',who.UserId,kind,position,table.pack(...))
end,FireAllClients=function(_,...)log('all-effect',...)end}
if case=='fatal-player'then h.Health=2
elseif case=='bot'then queuedHits={{id='bot',damage=4,firstHit=true}}
elseif case=='fatal-bot'then bot.health=2;queuedHits={{id='bot',damage=4,firstHit=true}}
elseif case=='resident'then bot.training=nil;s.sustained.intent.crowdHits=2;queuedHits={{id='bot',damage=4,firstHit=true}}
elseif case=='multi'then queuedHits={{id='player',damage=3,firstHit=true},{id='bot',damage=4,firstHit=true}}
elseif case=='reversed'then queuedHits={{id='bot',damage=4,firstHit=true},{id='player',damage=3,firstHit=true}}
elseif case=='zero-first'then h.Health=0;queuedHits={{id='player',damage=0,firstHit=true},{id='bot',damage=4,firstHit=true}}
elseif case=='no-hurt'then h.Health=0;queuedHits={{id='player',damage=0,firstHit=true}}
elseif case=='miss'then queuedHits={}
elseif case=='missing-root'then playerRoot=nil
elseif case=='bad-root'then playerRoot='not-an-instance'
elseif case=='wrong-class'then playerRoot=root(nil,'Folder')
elseif case=='detached-root'then playerRoot.Parent=nil
elseif case=='bad-character'then victim.Character='not-an-instance'
elseif case=='bad-position'then playerRoot.Position={X=1,Y=3,Z=10}
elseif case=='nan-position'then playerRoot.Position=vector(0/0,3,10)
elseif case=='infinite-position'then playerRoot.Position=vector(1,math.huge,10)
elseif case=='invalid-first'then playerRoot.Position=vector(1,3,-math.huge);queuedHits={{id='player',damage=3,firstHit=true},{id='bot',damage=4,firstHit=true}}
elseif case=='object'then queuedHits={{id='object',damage=4,firstHit=true}}
elseif case=='object-rejected'then object.locked=true;queuedHits={{id='object',damage=4,firstHit=true}}
elseif case=='fractional'then s.sustained.intent.damageTotal=.2;queuedHits={{id='player',damage=.25,firstHit=true}}
elseif case=='ended'then ended={reason='duration'}end
'''
FINISH=r'''
stepSustained(p,s,10)
if case=='repeat'then stepSustained(p,s,10.2)end
return {calls=calls,intent=s.sustained.intent,nextHeal=s.nextHeal,health=h.Health,defender=defender,botHealth=bot.health,botAlive=bot.alive,botCredit=bot.credit,trainingTarget=bot.trainingTarget and bot.trainingTarget.UserId,lastTrainingHit=bot.lastTrainingHit,objectHealth=object.health,rewards=s.botRewards,playerRoot=type(playerRoot)=='table' and playerRoot.Position or playerRoot,botRoot=botRoot.Position},contacts
end
'''
CASES=r'''
local nilCue={['missing-root']=true,['bad-root']=true,['wrong-class']=true,['detached-root']=true,['bad-character']=true,['bad-position']=true,['nan-position']=true,['infinite-position']=true,['invalid-first']=true,object=true}
local absent={miss=true,['no-hurt']=true,['object-rejected']=true}
for _,case in ipairs({'player','fatal-player','bot','fatal-bot','resident','multi','reversed','zero-first','no-hurt','miss','missing-root','bad-root','wrong-class','detached-root','bad-character','bad-position','nan-position','infinite-position','invalid-first','object','object-rejected','fractional','ended','repeat'})do
 local a,old=oldStep(case);local b,new=newStep(case)
 check(serial(a)==serial(b),'Damage/state/call order differs: '..case)
 check(#old==#new,'Effect count differs: '..case)
 for _,v in ipairs(old)do check(v==false,'Baseline had a world anchor')end
 if absent[case]then check(#new==0,'No-hurt/miss produced feedback: '..case)
 elseif nilCue[case]then check(new[1]==false,'Malformed/object first contact was not quiet: '..case)
 else
  local expected=(case=='bot' or case=='fatal-bot' or case=='resident' or case=='reversed' or case=='zero-first') and vector(5,3,12) or vector(1,3,10)
  check(serial(new[1])==serial(expected),'Wrong/pre-eject contact snapshot: '..case)
 end
end
print('PASS '..checks..' actual server anchor/damage differential assertions;24cases, no native collision proof')
'''

def run(s):
 code=PRE+'\nlocal function oldStep(case)\n'+ENV+step(baseline)+FINISH+'\nlocal function newStep(case)\n'+ENV+step(s)+FINISH+CASES
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(code);p=Path(f.name)
 try:r=subprocess.run(['luau',str(p)],cwd=R,text=True,capture_output=True,timeout=20)
 finally:p.unlink()
 return r

if __name__=='__main__':
 # The only edits surrounding the unchanged damage branches are presentation reads and payload position.
 old=step(baseline);new=step(source)
 a='  if target.player then';b='\n  end\n end\n if dealt>0 then'
 assert old[old.index(a):old.index(b)+len('\n  end')]==new[new.index(a,new.index('local position=')):new.index('\n  if dealt>dealtBefore')],'Damage/reward branch text changed'
 print('PASS unchanged damage/reward branch source contract')
 result=run(source);print(result.stdout,end='');assert result.returncode==0,result.stderr
 if '--negative-controls' in sys.argv:
  mutations=[('"SustainedHit",contactPosition,','"SustainedHit",nil,','Wrong/pre-eject contact'),('dealt>dealtBefore and not contactChosen','true','Wrong/pre-eject contact'),('not contactChosen','true','Wrong/pre-eject contact'),('contactPosition=position','contactPosition=targetRoot and targetRoot.Position','Wrong/pre-eject contact'),(' or not VoiceCombat.IsFinite(position.Y)','', 'Malformed/object first contact'),('math.floor(intent.damageTotal+.5)','math.floor(intent.damageTotal+1.5)','Damage/state/call order differs')]
  for old,new,reason in mutations:
   assert source.count(old)==1,old
   result=run(source.replace(old,new,1));assert result.returncode and reason in result.stderr,(old,result.stdout,result.stderr)
  print(f'PASS {len(mutations)} server contact negative controls')
