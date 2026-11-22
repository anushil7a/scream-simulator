"""Actual catalog/config/layout under synthetic vectors. No native pathfinding claim."""
from pathlib import Path
import ast, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
def read(p): return (ROOT/p).read_text()
def strings(p):
 tree=ast.parse(read(p));return {n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str)}
bootstrap=read('src/ServerScriptService/Bootstrap.server.luau')
assert 'questNavigation=NavigationCatalog.QuestTargets(s,questGivers)' in bootstrap
assert 'World.Build()\nlocal questGivers=NavigationCatalog.IndexQuestGivers(World.Bots)' in bootstrap
setup=strings('tests/compact_world.py')['setup'];setup=setup[:setup.index('local Layout=')]
s=strings('tests/compact_integration.py')
source=setup+s['pre']+read('src/ReplicatedStorage/Shared/CompactLayout.luau')+s['bridge']+read('src/ReplicatedStorage/Shared/Config.luau')+'\nend)()\n'
source+='script.Parent.CompactLayout="CompactLayout"\nlocal BossCatalog=(function()\n'+read('src/ReplicatedStorage/Shared/BossCatalog.luau')+'\nend)()\n'
source+='local TrainingRules=(function()\n'+read('src/ReplicatedStorage/Shared/TrainingRules.luau')+'\nend)()\n'
source+='local require=function(name) if name=="Config" then return Config elseif name=="BossCatalog" then return BossCatalog elseif name=="TrainingRules" then return TrainingRules else error(name) end end\nlocal Nav=(function()\n'+read('src/ReplicatedStorage/Shared/NavigationCatalog.luau')+'\nend)()\n'
# Frozen actual production source from 9507e84 provides a differential oracle.
source+='local scanCount=0\nlocal Before=(function()\nlocal table=setmetatable({find=function(t,v) scanCount+=1;return table.find(t,v) end},{__index=table})\n'+read('tests/fixtures/navigation_catalog_before_index.luau')+'\nend)()\n'
source+=r'''
local function eq(a,b) check(a.X==b.X and a.Y==b.Y and a.Z==b.Z,"wrong position") end
local data={quests={},availableQuests={}}
local session={data=data,collected={}}
local bots={}
for i,q in ipairs(Config.Quests) do table.insert(bots,{questIds={q.id},start=Vector3.new(i,3,i)}) end
local givers=Nav.IndexQuestGivers(bots)
check(Nav.Resolve('quest','nick',data)==nil,'hidden revealed')
check(Nav.Resolve('boss','invalid',data)==nil,'invalid boss')
check(Nav.Resolve('boss','leviathan',data).label=='Seagull Siren Captain · Lv 70','captain navigation name/level')
for _,b in ipairs(BossCatalog.Entries) do
 local guide=Nav.Resolve('boss',b.id,data)
 eq(guide.position,Vector3.new(b.x,(b.y or 0)+3,b.z))
 check(guide.minimumLevel==b.level,'Boss guide minimum differs from encounter catalog')
end
for _,place in ipairs(Nav.Places) do check(Nav.Resolve('place',place.id,data)~=nil,'place missing') end
local function checkTraining(level,index,label)
 local home=Layout.TrainingHomes[index]
 local guide=Nav.Resolve('place','training',{level=level})
 check(guide and guide.label==label,'wrong training guide label at level '..tostring(level))
 eq(guide.position,Vector3.new(home.x,home.y+3,home.z))
end
checkTraining(nil,1,'Rookie Training · Lv 1')
checkTraining(1,1,'Rookie Training · Lv 1')
checkTraining(24,1,'Rookie Training · Lv 1')
checkTraining(25,2,'Brawler Training · Lv 25')
checkTraining(59,2,'Brawler Training · Lv 25')
checkTraining(60,3,'Elite Training · Lv 60')
checkTraining(100,3,'Elite Training · Lv 60')
local amphitheatre=Nav.Resolve('place','amphitheatre',data)
check(amphitheatre and amphitheatre.label=='Amphitheatre entrance','Amphitheatre guide missing or misnamed')
eq(amphitheatre.position,Vector3.new(112,35,-229))
check(Layout.MapLandmarks[8].name=='8 Amphitheatre' and Layout.MapLandmarks[8].z==-330,'Map pin moved away from the venue')
check(Nav.Resolve('place','resonance',data)==nil,'Local PvP preview advertised from the City')
check(Nav.Resolve('place','nick',data)==nil,'hidden place exposed')
check(Nav.QuestTargets(session,givers).nick==nil,'hidden server target')
for _,q in ipairs(Config.Quests) do data.availableQuests[q.id]=true end
local function resolve(id)
 session.activeQuest=id;data.activeQuest=id;data.questNavigation=Nav.QuestTargets(session,givers)
 return Nav.Resolve('quest',id,data)
end
local first=resolve('garden');eq(first.position,Layout.QuestMarkers[1].position)
session.collected.Flowerbed228=true;eq(resolve('garden').position,Layout.QuestMarkers[2].position)
session.collected.Flowerbed250=true;session.collected.Flowerbed272=true;check(resolve('garden')==nil,'finished markers persist')
session.collected={};eq(resolve('beach').position,Layout.QuestMarkers[7].position)
eq(resolve('delivery').position,Layout.CafePickup)
session.carrying=true
for _,stop in ipairs(Layout.DeliveryStops) do session.deliveryStop=stop.id;eq(resolve('delivery').position,stop.position) end
session.deliveryStop='invalid';check(resolve('delivery')==nil,'invalid delivery persists')
session.carrying=false;eq(resolve('sprint').position,Layout.QuestMarkers[5].position)
session.raceStart=123;eq(resolve('sprint').position,Layout.QuestMarkers[6].position)
eq(resolve('nick').position,bots[1].start) -- giver only, never puzzle solution
check(resolve('practice_beams')==nil,'retired quest exposed')
data.quests.garden={progress=3};check(resolve('garden')==nil,'complete target persists')
data.quests.garden={progress=0,claimed=true};check(resolve('garden')==nil,'claimed target persists')
data.quests.garden=nil;session.activeQuest=nil;data.activeQuest=nil;data.availableQuests.garden=nil
data.questNavigation=Nav.QuestTargets(session,givers);check(Nav.Resolve('quest','garden',data)==nil,'unavailable persists')
check(session.activeQuest==nil,'auto-selected quest')

-- Compare indexed production with the unchanged pre-optimization production
-- module, across availability, completion, every active stage, and duplicates.
local botReads=0
local countedBots={}
for _,bot in ipairs(bots) do
 table.insert(countedBots,setmetatable({}, {__index=function(_,key) botReads+=1;return bot[key] end}))
end
local countedIndex=Nav.IndexQuestGivers(countedBots)
local buildReads=botReads
check(buildReads>0,'index did not inspect authoritative bots')
local duplicate={questIds={'garden'},start=Vector3.new(999,3,999)}
table.insert(countedBots,duplicate)
local duplicateIndex=Nav.IndexQuestGivers(countedBots)
eq(duplicateIndex.garden.position,countedIndex.garden.position)
local nilFirst=Nav.IndexQuestGivers({{questIds={'garden'}},duplicate})
check(nilFirst.garden~=nil and nilFirst.garden.position==nil,'nil first giver replaced')
local function compare()
 local before=Before.QuestTargets(session,countedBots)
 local after=Nav.QuestTargets(session,countedIndex)
 for _,q in ipairs(Config.Quests) do
  local a,b=before[q.id],after[q.id]
  check((a==nil)==(b==nil),'target availability changed '..q.id)
  if a then eq(a.position,b.position);check(a.label==b.label,'label changed '..q.id) end
 end
end
for _,q in ipairs(Config.Quests) do data.availableQuests[q.id]=true end
for _,q in ipairs(Config.Quests) do
 session.activeQuest=q.id
 for _,claimed in ipairs({false,true}) do
  for _,progress in ipairs({0,q.goal}) do
   data.quests[q.id]={claimed=claimed,progress=progress};compare()
  end
 end
 data.quests[q.id]=nil
end
for _,stop in ipairs(Layout.DeliveryStops) do
 session.activeQuest='delivery';session.carrying=true;session.deliveryStop=stop.id;compare()
end
session.carrying=false;compare()
session.activeQuest='sprint';session.raceStart=nil;compare();session.raceStart=10;compare()
session.activeQuest='garden';session.collected={};compare()
for _,marker in ipairs(Layout.QuestMarkers) do session.collected[marker.id]=true;compare() end
session.activeQuest=nil;data.availableQuests={};compare()
for _,q in ipairs(Config.Quests) do data.availableQuests[q.id]=true end
session.collected={};session.activeQuest=nil
scanCount=0
for _=1,1000 do Before.QuestTargets(session,countedBots) end
local oldScans=scanCount
botReads=0
for _=1,1000 do Nav.QuestTargets(session,countedIndex) end
check(botReads==0,'packet path still reads bots')
check(oldScans>0 and scanCount==oldScans,'indexed path still scans')
print('Quest giver bot reads per index build: '..buildReads..'; per 1000 indexed states: '..botReads..'; old membership scans per 1000 states: '..oldScans)

Config.CompactCity=false
check(next(Nav.QuestTargets(session,givers))==nil,'legacy targets')
check(Nav.Resolve('boss','golem',data)==nil and Nav.Resolve('place','spawn',data)==nil,'legacy resolve')
print('Navigation catalog assertions passed')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',delete=False) as f:
 f.write(source)
 path=Path(f.name)
try: subprocess.run(['luau',str(path)],cwd=ROOT,check=True)
finally: path.unlink()
