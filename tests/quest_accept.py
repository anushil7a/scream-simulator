"""Actual acceptance branch with mocked quest/session callbacks; no native UI."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=source.index(' elseif verb=="AcceptQuest" then')+len(' elseif verb=="AcceptQuest" then')
b=source.index(' elseif verb=="AbandonQuest" then',a)
setup='''
local p={};local stops=0;local notices={}
local definitions={garden={id='garden',name='Garden',goal=3},delivery={id='delivery',name='Delivery',goal=1},sprint={id='sprint',name='Race',goal=1}}
local Config={GetQuest=function(id)return definitions[id] end}
local s={activeQuest='garden',data={availableQuests={garden=true,delivery=true,sprint=true},quests={garden={progress=1,claimed=false}}},collected={bed=true}}
local function state(_,message)table.insert(notices,message)end
local function stopQuest()stops+=1;s.activeQuest=nil;s.questDeadline=nil;s.raceStart=nil;s.carrying=false;s.deliveryStop=nil;s.collected={} end
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
accept(p,s,'garden')
check(stops==0 and s.data.quests.garden.progress==1 and s.collected.bed,'Duplicate acceptance erased garden progress')
for _,id in ipairs({'delivery','sprint'})do
 s.activeQuest=id;s.data.quests[id]={progress=0,claimed=false};s.questDeadline=90;s.raceStart=65;s.carrying=true;s.deliveryStop='Pier'
 accept(p,s,id)
 check(stops==0 and s.questDeadline==90 and s.raceStart==65 and s.carrying and s.deliveryStop=='Pier','Duplicate acceptance reset timed attempt '..id)
end
s.data.quests.sprint.progress=1;accept(p,s,'sprint')
check(stops==0 and s.data.quests.sprint.progress==1 and notices[#notices]=='Task complete · claim your reward.','Completed reward was reset')
accept(p,s,'garden')
check(stops==1 and s.activeQuest=='garden' and s.data.quests.garden.progress==0,'Switching quests stopped working')
stopQuest();accept(p,s,'garden')
check(stops==3 and s.activeQuest=='garden','Abandoned quest could not restart')
s.data.quests.delivery.claimed=true;accept(p,s,'delivery')
check(stops==3 and s.activeQuest=='garden','Claimed quest replaced active attempt')
s.data.availableQuests.sprint=false;accept(p,s,'sprint')
check(stops==3 and s.activeQuest=='garden','Locked quest replaced active attempt')
print('PASS '..checks..' actual quest acceptance checks with mocked session state')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(setup+'\nlocal function accept(p,s,arg)\n'+source[a:b]+'\nend\n'+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
