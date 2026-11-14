"""Actual compact quest labels and race-start snippet; not native wayfinding."""
from pathlib import Path
import ast,argparse,re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');args=p.parse_args()
def read(name):return (ROOT/name).read_text(encoding='utf-8')
tree=ast.parse(read('tests/compact_world.py'));setup=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='setup' for t in n.targets));setup=setup[:setup.index('local Layout=')]
layout=read('src/ReplicatedStorage/Shared/CompactLayout.luau');city=read('src/ServerScriptService/CompactCity.luau');config=read('src/ReplicatedStorage/Shared/Config.luau');server=read('src/ServerScriptService/Bootstrap.server.luau')
pre="""
local Healing=require('../src/ReplicatedStorage/Shared/Healing');local VoiceCombat=require('../src/ReplicatedStorage/Shared/VoiceCombat');local Progression=require('../src/ReplicatedStorage/Shared/Progression')
local Layout=(function()
"""
bridge="""
end)()
local script={Parent={WaitForChild=function(_,name)return name end}}
local game={GetService=function()return {Shared={CompactLayout='CompactLayout'}}end}
local require=function(name)return ({Healing=Healing,VoiceCombat=VoiceCombat,Progression=Progression,CompactLayout=Layout})[name]end
local function makeConfig(compact)
"""
citybridge="""
end
local Config=makeConfig(true)
local City=(function()
"""
checks="""
end)()
local built=City.Build({})
local expected={crowd='Eric Sol · west courtyard',sprint='Boardwalk runner · west promenade',dodge='Arena coach · west arena gate',arena='Arena coach · west arena gate'}
for id,text in pairs(expected)do
 check(Config.GetQuest(id).giver==text,'Compact giver label wrong:'..id)
 local found
 for _,job in ipairs(built.jobs)do for _,qid in ipairs(job.quests or {})do if qid==id then found=job end end end
 check(found and text:find(found.name,1,true)==1,'Guidance names absent quest giver:'..id)
 local pos=found.stations[1].position
 check((id=='crowd' and pos.X< -200 and pos.Z>=100 and pos.Z<=170) or (id=='sprint' and pos.Z>=180 and pos.Z<=210) or ((id=='dodge' or id=='arena') and pos.X>= -150 and pos.X<= -120 and pos.Z>=20 and pos.Z<=60),'Giver is outside described compact district:'..id)
end
local old=makeConfig(false)
local expectedLegacy={crowd='Busker · west gardens',sprint='Commuter · Plaça del Sol',dodge='Fighter · Rambla Gardens',arena='Fighter · Rambla Gardens'}
for id,text in pairs(expectedLegacy)do check(old.GetQuest(id).giver==text,'Legacy giver fallback changed:'..id)end
check(#Config.Quests==10 and #old.Quests==10,'Quest count changed')
for _,q in ipairs(Config.Quests)do local prior=old.GetQuest(q.id);for _,field in ipairs({'id','goal','event','xp','coins','description'})do check(q[field]==prior[field],'Quest identity/reward/objective changed')end end
local now=100;local os={clock=function()return now end};local s={};local p={};local messages={}
local function state(_,message)table.insert(messages,message)end
local function startRace()
__RACE__
end
startRace()
check(s.raceStart==100 and s.questDeadline==125,'Race timing changed')
check(messages[1]=='Go! Follow the promenade east to the finish · 25s','Race start has stale destination')
now=102;startRace()
check(s.raceStart==100 and s.questDeadline==125,'Repeat start extended race')
check(#messages==2 and messages[2]=='Your race is already running. Follow the boardwalk to the finish.','Repeat race response changed')
print('PASS '..checks..' compact navigation-copy assertions; mocked modules/snippet only')
"""
a=server.index('  elseif kind=="RaceStart" and s.activeQuest=="sprint" then');a=server.index('\n',a)+1;b=server.index('  elseif kind=="RaceFinish"',a);race=server[a:b]
config=config.replace('Config.CompactCity=true','Config.CompactCity=compact')
code=setup+pre+layout+bridge+config+citybridge+city+checks.replace('__RACE__',race)
def run(body,error=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False)as f:f.write(body);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],text=True,capture_output=True)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS negative control:',error)
 else:assert r.returncode==0,out;print(out.strip())
run(code)
if args.negative_controls:
 for before,after,error in [('questGivers.crowd="Eric Sol · west courtyard"','questGivers.crowd="Busker · west gardens"','Compact giver label wrong:crowd'),('questGivers.sprint="Boardwalk runner · west promenade"','questGivers.sprint="Commuter · Plaça del Sol"','Compact giver label wrong:sprint'),('questGivers.dodge="Arena coach · west arena gate"','questGivers.dodge="Fighter · Rambla Gardens"','Compact giver label wrong:'),('Follow the promenade east to the finish · 25s','Follow the boardwalk to the pier finish · 25s','Race start has stale destination')]:
  # Only mutate production fragment, not expectations.
  head,tail=code.split('local built=City.Build({})',1)
  if before.startswith('Follow '):
   head,tail=code.split('local function startRace()',1);racepart,rest=tail.split('\nend\nstartRace()',1);changed=head+'local function startRace()'+racepart.replace(before,after)+'\nend\nstartRace()'+rest
  else:changed=head.replace(before,after)+'local built=City.Build({})'+tail
  assert changed!=code,before;run(changed,error)
