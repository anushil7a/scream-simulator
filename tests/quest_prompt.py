"""Actual quest prompt handler with mocked prompts/characters; no native input."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=s.index('local function interactQuest(p,obj)');b=s.index('for _,obj in ipairs(workspace.ScreamSimulatorWorld:GetDescendants())',a)
setup='''
local now=0;local os={clock=function()return now end}
local sessions={};local workspace={ScreamSimulatorWorld={}}
local distance=5;local position=setmetatable({},{__sub=function()return {Magnitude=distance}end})
local root={Position=position};local function parts()return {},root end
local Config={GetQuest=function(id)return id=='garden' and {id=id,goal=3} or id=='sprint' and {id=id,goal=1} or nil end}
local messages=0;local function state()messages+=1 end
local awards=0;local function questProgress(p)awards+=1;sessions[p].data.quests[sessions[p].activeQuest].progress+=1 end
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local p={};local session={activeQuest='garden',collected={},data={quests={garden={progress=0}}}}
sessions[p]=session
local kind='Garden'
local marker={Name='Bed1',Position=position,IsA=function()return true end,GetAttribute=function()return kind end}
local obj={Enabled=true,Parent=marker,inWorld=true}
function obj:IsDescendantOf(world)assert(world==workspace.ScreamSimulatorWorld);return self.inWorld end
obj.Enabled=false;interactQuest(p,obj)
check(awards==0 and next(session.collected)==nil,'Disabled prompt awarded progress')
obj.Enabled=true;obj.inWorld=false;interactQuest(p,obj)
check(awards==0,'Removed prompt awarded progress')
obj.inWorld=true;distance=13;interactQuest(p,obj)
check(awards==0,'Distant prompt awarded progress')
distance=5;obj.Parent=nil;interactQuest(p,obj)
check(awards==0,'Unparented prompt awarded progress')
obj.Parent=marker;local saved=root;root=nil;interactQuest(p,obj)
check(awards==0,'Missing living character awarded progress');root=saved
interactQuest(p,obj)
check(awards==1 and session.collected.Bed1,'Valid prompt failed')
interactQuest(p,obj);check(awards==1,'Repeated garden prompt awarded twice')
marker.Name='Bed2';session.data.quests.garden.progress=3;interactQuest(p,obj)
check(awards==1 and not session.collected.Bed2,'Completed task accepted more progress')
sessions[p]=nil;interactQuest(p,obj)
check(awards==1,'Departed player prompt awarded progress')
sessions[p]=session;session.activeQuest='sprint';session.data.quests.sprint={progress=0}
kind='RaceStart';now=50;interactQuest(p,obj)
check(session.raceStart==50 and session.questDeadline==75,'Race failed to start with one consistent deadline')
now=52;interactQuest(p,obj)
check(session.raceStart==50 and session.questDeadline==75,'Repeated start reset active race')
kind='RaceFinish';local before=awards;interactQuest(p,obj)
check(awards==before and session.raceStart==50,'Too-early finish awarded progress')
now=55;interactQuest(p,obj)
check(awards==before+1 and not session.raceStart and not session.questDeadline,'Valid race finish failed')
interactQuest(p,obj);check(awards==before+1,'Repeated finish awarded progress twice')
kind='RaceStart';interactQuest(p,obj)
check(not session.raceStart,'Completed race restarted before reward claim')
print('PASS '..checks..' actual quest prompt checks with mocked instances')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+s[a:b]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
