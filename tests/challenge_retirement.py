"""Actual progression/profile retirement through an isolated in-memory atomic store.
No network, native Studio, or live DataStores. --baseline reproduces pre-retirement behavior.
"""
from pathlib import Path
import argparse, subprocess, tempfile
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--baseline',action='store_true');parser.add_argument('--negative-controls',action='store_true');args=parser.parse_args()
def read(name):
 if args.baseline:return subprocess.check_output(['git','show','36cfb69:'+name],cwd=root,text=True,encoding='utf-8')
 return (root/name).read_text(encoding='utf-8')
progression=read('src/ReplicatedStorage/Shared/Progression.luau')
config=read('src/ReplicatedStorage/Shared/Config.luau')
profiles=read('src/ServerScriptService/Profiles.luau')
preamble=r"""
local Healing=require('../src/ReplicatedStorage/Shared/Healing')
local Combat=require('../src/ReplicatedStorage/Shared/VoiceCombat')
local Lease=require('../src/ReplicatedStorage/Shared/ProfileLease')
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local Color3={fromRGB=function(r,g,b)return {r,g,b}end}
local Progression=(function()
"""
after_progression=r"""
end)()
-- MUTATION_INSERT
local script={Parent={WaitForChild=function(_,name)return name end}}
local config
local require=function(name)
 if name=='Healing' then return Healing elseif name=='VoiceCombat' then return Combat elseif name=='Progression' then return Progression
 elseif name=='Config' then return config elseif name=='Lease' then return Lease end
 error('Unexpected dependency '..tostring(name))
end
local function loadConfig()
"""
after_config=r"""
end
config=loadConfig()
local now,clock,guid=1000,100,0
local os={time=function()return now end,clock=function()return clock end}
local task={wait=function(t)now+=t;clock+=t end}
local durable;local writes=0
local store={UpdateAsync=function(_,key,transform)
 assert(key=='Player_7','Unexpected test key');writes+=1
 local result=transform(durable)
 if result~=nil then durable=result end
 return result
end}
local services={DataStoreService={GetDataStore=function(_,name)assert(name=='ScreamSimulator_v1','Wrong fake store');return store end},
 ReplicatedStorage={Shared={Config='Config',ProfileLease='Lease'}},RunService={IsStudio=function()return false end},
 HttpService={GenerateGUID=function()guid+=1;return 'retirement-'..guid end}}
local game={JobId='retirement-fixture',GetService=function(_,name)return services[name]end}
local warn=function()end
local function loadProfiles()
"""
checks=r"""
end
local P=loadProfiles();local n=0
local function check(ok,msg)assert(ok,msg);n+=1 end
check(#Progression.Challenges==1 and Progression.Challenges[1].id=='fighters','Retired challenges remain active')
check(Progression.Challenges[1].name=='Help defeat 3 eligible training fighters' and Progression.Challenges[1].goal==3,'Active challenge label/goal mismatch')
local retired={}
for _,spec in ipairs(Progression.RetiredChallenges or {})do retired[spec.id]=spec.goal end
check(retired.cover==5 and retired.elite==2,'Dormant challenge bounds absent')
local seed={schemaVersion=4,level=50,xp=12,coins=321,sound='TinyAah',aura='Gold',customColor='FA4FFF',useCustomColor=true,
 amplifierOwned=true,amplifierEquipped=true,achievements={FirstBeam=true},settings={volume=.4,reducedShake=true},
 combatChallenges={fighters=1,cover=4,elite=1},availableQuests={garden=true},quests={garden={progress=1,claimed=false}}}
local clean=P.Sanitize(seed)
local function preserved(data)
 check(data.combatChallenges.cover==4 and data.combatChallenges.elite==1,'Dormant partial progress lost')
 check(data.coins==321 and data.level==50 and data.xp==12,'Unrelated economy changed')
 check(data.sound=='TinyAah' and data.aura=='Gold' and data.customColor=='FA4FFF' and data.useCustomColor,'Unrelated style changed')
 check(data.amplifierOwned and data.amplifierEquipped and data.achievements.FirstBeam,'Ownership/achievement changed')
 check(data.availableQuests.garden and data.quests.garden.progress==1 and not data.quests.garden.claimed,'City quest progress changed')
 check(data.settings.volume==.4 and data.settings.reducedShake,'Unrelated settings changed')
end
preserved(clean)
for i=1,5 do clean=P.Sanitize(clean);preserved(clean)end
check(seed.combatChallenges.cover==4 and clean.combatChallenges~=seed.combatChallenges,'Sanitize mutated/aliased original counters')
for _,id in ipairs({'cover','elite','unknown'}) do
 local counters={fighters=1,cover=4,elite=1,unknown=7}
 local reward,name=Progression.Advance(counters,id,50)
 check(reward==0 and name==nil,'Retired challenge awarded reward')
 check(counters.cover==4 and counters.elite==1 and counters.fighters==1 and counters.unknown==7,'Retired challenge mutated progress')
end
local counters={fighters=2,cover=4,elite=1}
local reward=Progression.Advance(counters,'fighters',50)
check(reward==Progression.ChallengeXP(50) and counters.fighters==0,'Active fighter reward changed')
check(counters.cover==4 and counters.elite==1,'Active reward consumed dormant progress')
local values={{-5,0},{0,0},{1,1},{99,4},{1.9,1},{math.huge,0},{-math.huge,0},{0/0,0},{'4',0},{true,0},{ {},0}}
for _,row in ipairs(values)do
 local data=P.Sanitize({schemaVersion=4,combatChallenges={cover=row[1],elite=row[1],fighters=row[1],unknown=99}})
 check(data.combatChallenges.cover==row[2],'Dormant cover bound/type mismatch')
 check(data.combatChallenges.elite==math.min(1,row[2]),'Dormant elite bound/type mismatch')
 check(data.combatChallenges.fighters==math.min(2,row[2]),'Active counter bound/type mismatch')
 check(data.combatChallenges.unknown==nil,'Unknown counter retained')
end
for _,raw in ipairs({false,7,'invalid'})do
 local data=P.Sanitize({schemaVersion=4,combatChallenges=raw})
 check(next(data.combatChallenges)==nil,'Malformed challenge container accepted')
end
local defaults=P.Sanitize({schemaVersion=4,combatChallenges={}})
check((defaults.combatChallenges.cover or 0)==0 and (defaults.combatChallenges.elite or 0)==0,'Missing dormant keys invented progress')
-- Actual Profiles load, autosave, release and same-server/new-module rejoin, fake atomic store only.
durable=seed
local loaded,writable=P.Load(7)
check(writable,'Fake initial acquisition failed');preserved(loaded)
check(loaded.combatChallenges.fighters==1,'Load reinterpreted active counter')
check(P.Save(7,loaded)==true,'Fake autosave failed');preserved(durable)
check(P.Save(7,loaded,true)==true and durable._lease==nil,'Fake release failed');preserved(durable)
now+=10;clock+=10
local rejoined,canSave=P.Load(7)
check(canSave,'Fake same-server rejoin failed');preserved(rejoined)
check(P.Save(7,rejoined,true)==true,'Fake second release failed')
local restarted=loadProfiles();now+=10;clock+=10
local fresh,canWrite=restarted.Load(7)
check(canWrite,'Fake new-module rejoin failed');preserved(fresh)
check(restarted.Save(7,fresh,true)==true,'Fake restarted release failed')
check(writes>=7,'Persistence path was not exercised')
print('PASS '..n..' actual progression/profile retirement assertions with fake atomic persistence; no native/live validation')
"""
def assemble(ps=progression,profile_source=profiles):return preamble+ps+after_progression+config+after_config+profile_source+checks
def run(code,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',encoding='utf-8',delete=False) as f:path=Path(f.name);f.write(code)
 try:
  r=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True,encoding='utf-8');out=r.stdout+r.stderr
  if expected:
   assert r.returncode and expected in out,out
   print('PASS expected failure:',expected)
  else:print(out,end='');assert r.returncode==0,out
 finally:path.unlink()
if args.baseline:run(assemble(),'Retired challenges remain active')
else:
 run(assemble())
 if args.negative_controls:
  for id,goal in [('cover',5),('elite',2)]:
   code=assemble().replace('-- MUTATION_INSERT',f'table.insert(Progression.Challenges,{{id="{id}",name="reactivated",goal={goal}}})')
   run(code,'Retired challenges remain active')
  # Remove only the sanitizer retirement loop, preserving the published retired metadata.
  stripped=profiles.replace('Config.Progression.RetiredChallenges or {}','{}',1)
  assert stripped!=profiles,'Dormant preservation mutation did not match source'
  run(assemble(profile_source=stripped),'Dormant partial progress lost')
