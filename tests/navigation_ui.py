"""Execute actual selection lifecycle; source-check explicit-only UI wiring. Not native UI proof."""
from pathlib import Path
import subprocess, tempfile
R=Path(__file__).resolve().parents[1]
s=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
f=s[s.index('academy.clearGuide=function()'):s.index('academy.guideMenu=function()')]
setup=r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local data={};local Config={CompactCity=true};local target=nil;local sets,clears=0,0
local renderedMenuKey='old';local UDim2={fromOffset=function()end,new=function()end}
local click,guideTraining
local function button(_,name,_,_,_,callback)
 if name=='ClearGuide' then click=callback else guideTraining=callback end
 return {}
end
local academy={guidePanel={Visible=false},guide={
 Clear=function()clears+=1 end, SetTarget=function(_,v)sets+=1 end},
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
