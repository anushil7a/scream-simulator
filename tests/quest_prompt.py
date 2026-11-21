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
local Config={GetQuest=function(id)return id=='garden' and {id=id,goal=3} or (id=='sprint' or id=='delivery') and {id=id,goal=1} or nil end}
Config.DeliveryStops={{id='Pier',name='pier'}}
Config.GetDeliveryStop=function()return Config.DeliveryStops[1] end
local messages=0;local function state()messages+=1 end
local awards=0;local function questProgress(p)awards+=1;sessions[p].data.quests[sessions[p].activeQuest].progress+=1 end
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local p={};local session={activeQuest='garden',collected={},data={quests={garden={progress=0}}}}
sessions[p]=session
local kind='Garden';local deliveryStop='Pier'
local marker={Name='Bed1',Position=position,IsA=function()return true end,GetAttribute=function(_,key)return key=="DeliveryStop" and deliveryStop or kind end}
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
session.activeQuest='delivery';session.data.quests.delivery={progress=0}
kind='Dropoff';before=awards;interactQuest(p,obj)
check(awards==before,'Delivery without pickup awarded progress')
kind='Pickup';now=100;interactQuest(p,obj)
check(session.carrying and session.deliveryStop=='Pier' and session.questDeadline==190,'Pickup did not set route/deadline')
now=110;interactQuest(p,obj)
check(session.deliveryStop=='Pier' and session.questDeadline==190,'Duplicate pickup replaced route/deadline')
kind='Dropoff';deliveryStop='Wrong';interactQuest(p,obj)
check(awards==before and session.carrying and session.deliveryStop=='Pier' and session.questDeadline==190,'Wrong destination consumed order or awarded progress')
deliveryStop='Pier';now=191;interactQuest(p,obj)
check(awards==before and session.carrying,'Expired delivery awarded progress')
-- Start a fresh attempt, simulating the existing timeout/reaccept flow.
session.carrying=false;session.deliveryStop=nil;session.questDeadline=nil
kind='Pickup';now=200;interactQuest(p,obj)
kind='Dropoff';now=290;interactQuest(p,obj)
check(awards==before+1 and not session.carrying and not session.deliveryStop and not session.questDeadline,'Delivery at exact deadline failed to complete/clear attempt')
interactQuest(p,obj);check(awards==before+1,'Duplicate dropoff awarded twice')
kind='Pickup';interactQuest(p,obj)
check(not session.carrying,'Completed delivery allowed another pickup before reward claim')
print('PASS '..checks..' actual quest prompt checks with mocked instances')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+s[a:b]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()

client=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text(encoding='utf-8')
refresh=client[client.index('local function refreshQuestObject('):client.index('local function saveStatus()')]
client_setup=r'''
local shown
local game={GetService=function(_,name)
 assert(name=="ProximityPromptService");return {PromptShown={}}
end}
local function connectClient(_,callback)shown=callback end
local data={}
local folder={children={}};function folder:GetChildren()return self.children end
local world={FindFirstChild=function(_,name)if name=="QuestObjects" then return folder end end}
local workspace={FindFirstChild=function(_,name)if name=="ScreamSimulatorWorld" then return world end end}
local function marker(name,action,parent)
 local part={Name=name,Parent=parent,LocalTransparencyModifier=.2}
 local prompt={Enabled=true,Parent=part}
 function part:IsA(class)return class=="BasePart" end
 function part:GetAttribute(attr)if attr=="QuestAction" then return action end end
 function part:FindFirstChildOfClass()return prompt end
 return part,prompt
end
'''
client_checks=r'''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local bed,bedPrompt=marker("Bed1","Garden",folder)
local otherBed,otherPrompt=marker("Bed2","Garden",folder)
local bottle,bottlePrompt=marker("Bottle1","Litter",folder)
local race,racePrompt=marker("RaceStart","RaceStart",folder)
folder.children={bed,otherBed,bottle,race}
refreshQuestObjects()
check(bedPrompt.Enabled and otherPrompt.Enabled and bottlePrompt.Enabled,"Initial prompts became unavailable")
data.collected={Bed1=true,Bottle1=true,RaceStart=true}
refreshQuestObjects()
check(not bedPrompt.Enabled and otherPrompt.Enabled,"Only the watered bed should retire its prompt")
check(bed.LocalTransparencyModifier==.2 and otherBed.LocalTransparencyModifier==.2,"Flowerbeds lost their world appearance")
check(not bottlePrompt.Enabled and bottle.LocalTransparencyModifier==1,"Collected bottle no longer hides")
check(racePrompt.Enabled and race.LocalTransparencyModifier==.2,"Unrelated quest prompt mutated")
data.collected={}
refreshQuestObjects()
check(bedPrompt.Enabled and otherPrompt.Enabled,"Restart left a bed disabled")
check(bottlePrompt.Enabled and bottle.LocalTransparencyModifier==0,"Restart left a bottle hidden")
data.collected={Bed1=true}
local streamed,streamedPrompt=marker("Bed1","Garden",folder)
shown(streamedPrompt)
check(not streamedPrompt.Enabled and streamed.LocalTransparencyModifier==.2,"Late-loaded watered bed showed a prompt")
local unrelated,unrelatedPrompt=marker("Bed1","Garden",{})
shown(unrelatedPrompt)
check(unrelatedPrompt.Enabled,"A similarly named prompt outside QuestObjects was mutated")
shown(otherPrompt)
check(otherPrompt.Enabled,"Unwatered nearby bed stopped being available")
print("PASS "..checks.." local quest prompt presentation checks")
'''

def run_client(source, failure=None):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False,encoding='utf-8') as f:
        path=Path(f.name)
        f.write(client_setup+source+client_checks)
    try:
        result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True,timeout=15)
        if failure:
            assert result.returncode and failure in result.stderr, result.stdout+result.stderr
            print('PASS negative control: '+failure)
        else:
            assert result.returncode==0,result.stderr
            print(result.stdout,end='')
    finally:
        path.unlink()

run_client(refresh)
for old,new,failure in [
    ('action~="Litter" and action~="Garden"','action~="Litter"','Only the watered bed should retire its prompt'),
    ('if objects and object.Parent==objects then refreshQuestObject(object) end','if false then refreshQuestObject(object) end','Late-loaded watered bed showed a prompt'),
]:
    assert refresh.count(old)==1,old
    run_client(refresh.replace(old,new),failure)
