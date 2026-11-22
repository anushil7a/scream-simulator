"""Execute actual selection lifecycle; source-check explicit-only UI wiring. Not native UI proof."""
from pathlib import Path
import subprocess, tempfile
R=Path(__file__).resolve().parents[1]
s=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
f=s[s.index('academy.clearGuide=function()'):s.index('academy.guideMenu=function()')]
setup=r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local data={};local Config={CompactCity=true};local target=nil;local sets,clears=0,0
local throttled
local renderedMenuKey='old';local UDim2={fromOffset=function()end,new=function()end}
local click,guideTraining
local function button(_,name,_,_,_,callback)
 if name=='ClearGuide' then click=callback else guideTraining=callback end
 return {}
end
local academy={guidePanel={Visible=false},guide={
 Clear=function()clears+=1 end, SetTarget=function(_,v,keepThrottle)sets+=1;throttled=keepThrottle end},
 NavigationCatalog={Resolve=function(kind,id,state)check(state==data,'Wrong state');return target end}}
'''
checks=r'''
check(academy.guideSelection==nil and sets==0,'Auto-selected at startup')
academy.refreshGuide();check(sets==0 and clears==0,'Sync selected a destination')
academy.selectGuide('quest','garden');check(academy.guideSelection==nil,'Unavailable destination selected')
target={position=1,label='Garden'}
academy.selectGuide('quest','garden');check(sets==1 and academy.guideSelection.id=='garden','Explicit selection failed')
academy.refreshGuide();check(sets==1,'Same target reset route')
target={position=2,label='Next garden marker'}
academy.refreshGuide();check(sets==2 and academy.guideSelection.id=='garden','Selected stage not updated')
academy.selectGuide('boss','ignis');check(academy.guideSelection.kind=='boss','Switch failed')
click();check(academy.guideSelection==nil and academy.guideTarget==nil and not academy.guidePanel.Visible,'Clear failed')
academy.refreshGuide();check(sets==2,'Clear followed by Sync reselected')
academy.selectGuide('place','coast');target=nil;academy.refreshGuide()
check(academy.guideSelection==nil,'Invalid/complete target not cleared')
target={position=3,label='Rookie Training'}
guideTraining();check(academy.guideSelection==nil,'Hidden training button selected a route')
academy.trainingGuideButton.Visible=true
data.activeQuest='garden';guideTraining();check(academy.guideSelection==nil,'Training replaced an active quest')
data.activeQuest=nil;Config.CompactCity=false;guideTraining();check(academy.guideSelection==nil,'Training guide exposed in legacy city')
Config.CompactCity=true;guideTraining()
check(academy.guideSelection.kind=='place' and academy.guideSelection.id=='training','HUD did not select training')
local selected=academy.guideSelection;guideTraining()
check(academy.guideSelection==selected,'Training button replaced existing route')
click();check(academy.canGuideTraining(),'Clear did not restore training eligibility')
local function position(x)
 return setmetatable({X=x},{__sub=function(a,b)return {Magnitude=math.abs(a.X-b.X)} end})
end
local r={Position=position(-492)}
local h={Health=100}
local mar={Parent={},GetAttribute=function(_,key)if key=="DisplayName" then return "Mar Soler" end end,
 FindFirstChild=function()return r end,FindFirstChildOfClass=function()return h end}
local center={Position=position(-460)}
target={position=center.Position,label="Gardens"}
academy.selectGuide("mar","gardens")
check(academy.guideTarget.label=="Mar's work area" and not throttled,'Missing honest initial work-area destination')
academy.refreshMarGuide(center,{mar})
check(academy.guideTarget.label=="Mar Soler" and academy.guideTarget.position==r.Position and throttled,'Nearby Mar did not replace work-area waypoint')
local saved=academy.guideTarget;local before=sets
r.Position=position(-491);academy.refreshMarGuide(center,{mar})
check(academy.guideTarget==saved and sets==before,'Small resident movement rebuilt the route')
r.Position=position(-428);academy.refreshMarGuide(center,{mar})
check(academy.guideTarget.position==r.Position and sets==before+1,'Route stayed at the old flowerbed')
h.Health=0;academy.refreshMarGuide(center,{mar})
check(academy.guideTarget.label=="Mar's work area" and academy.guideTarget.position==center.Position,'Unavailable resident retained stale destination')
h.Health=100;academy.refreshMarGuide({Position=position(-200)},{mar})
check(academy.guideTarget.label=="Mar's work area",'Distant motion replaced stable work-area destination')
click();academy.refreshMarGuide(center,{mar})
check(not academy.guideSelection and not academy.guideTarget,'Refresh restarted a cleared guide')
print('PASS',n,'actual selection lifecycle checks')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=R/'tests',delete=False) as t:
 t.write(setup+f+checks);p=Path(t.name)
try:subprocess.run(['luau',str(p)],check=True)
finally:p.unlink()
assert s.count('academy.guideSelection={')==1
assert 'data.activeQuest==q.id and "ACTIVE"' in s and '"TRACKING"' not in s
for marker in ['"Guide_"..q.id','"GuideBoss_"..boss.id','"GuidePlace_"..place.id','choice("Guide me: "..q.name','choice("Choose a boss or place to guide me to"','academy.guide:GetStatus()','academy.guide:Destroy()']:
 assert marker in s,marker
state=s[s.index('connectClient(remotes.State.OnClientEvent'):s.index('local BeamVisuals=')]
assert 'selectGuide' not in state and 'academy.refreshGuide()' in state
assert 'academy.guide:Step' in s
print('PASS explicit-only wiring, stage refresh, ownership and HUD source contracts')

# Render the actual HUD block with a selected guide and staged routing/level state.
render=s[s.index(' local guideUsesTracker=false'):s.index(' tracked.Visible=gameplayVisible')]
arrival=r'''
local n=0
local UDim2={fromOffset=function(...)return {...} end}
local viewport,touch,tracked,devPanel={},true,{Position={Y={Offset=0}}},{Visible=false}
local showQuest,gameplayVisible=true,true
local data={level=9}
local mode,compact,distance='Arrived',true,8
local academy={
 guideLayout=function()return 0,0,245,44,compact end,
 guidePanel={},guideText={},
 guideTarget={label="Whispering Metronome · Lv 10",minimumLevel=10},
 guideSelection={kind="boss",id="metronome"},
 guide={GetStatus=function()return mode,distance,distance==8 and 'NW' or nil end},
}
local function render()
'''
expected=r'''
end
local function check(text)
 render()
 assert(academy.guideText.Text==text, 'Guide showed '..academy.guideText.Text..' instead of '..text)
 n+=1
end
check("Requires Lv 10")
data.level=10
check("Hit boss to join")
compact=false
check("Whispering Metronome · Lv 10\nHit boss to join")
mode,compact,distance="Follow the markers",true,42
check("Follow the markers · 42 studs")
mode,distance="Arrived",nil
academy.guideSelection={kind="place",id="coast"}
academy.guideTarget={label="Coast"}
check("Arrived")
print("PASS",n,"actual guide HUD state checks")
'''
with tempfile.TemporaryDirectory() as directory:
 p=Path(directory)/'guide-arrival.luau'
 p.write_text(arrival+render+expected,encoding='utf-8')
 subprocess.run(['luau',str(p)],check=True)
