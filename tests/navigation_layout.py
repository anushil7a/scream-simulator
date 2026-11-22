"""Actual guide layout sizing and wiring. Not native UI or text-raster evidence."""
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
a=s.index('function academy.trackerLayout(');b=s.index('local function menuKey()',a)
code='local academy={}\n'+s[a:b]+r'''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
for _,viewport in ipairs({{844,390},{667,375},{640,350},{1280,360}})do
 local x,y,w,h,compact=academy.guideLayout({X=viewport[1],Y=viewport[2]},true,160)
 check(compact and x and y and w and h,'short landscape hid navigation status')
 check(x>=264 and x+w<=viewport[1]-182,'landscape overlaps HUD or minimap reserve')
 check(y>=46 and y+h<=math.min(96,viewport[2]-249),'status overlaps top zone or touch TALK lane')
 check(w>=194 and h>=44,'status/clear tap area too small')
end
local x,y,w,h,compact=academy.guideLayout({X=390,Y=844},true,160)
check(x==16 and y==216 and w==290 and h==62 and compact==false,'portrait guide moved')
local a,b,c,d,e=academy.guideLayout({X=1280,Y=720},false,64)
check(a==16 and b==120 and c==290 and d==62 and e==false,'desktop guide moved')
check(not academy.guideLayout({X=320,Y=315},true,160),'cramped viewport should use clear in menu')
for _,view in ipairs({{529,242},{541,239},{567,241},{567,280},{600,314},{784,296},{567,315},{587,345}})do
 local width,height=view[1],view[2]
 local left,top,cardWidth,cardHeight,shared,center=academy.trackerLayout({X=width,Y=height},true,160)
 check(left>=math.ceil(width*.4)+8,'Tracker enters thumbstick lane')
 check(left+cardWidth<=width-103,'Tracker enters Jump lane')
 check(top>=height-91,'Tracker enters combat lane')
 check(top+cardHeight<=height-12,'Tracker crosses bottom safe margin')
 check(cardWidth>=196 and cardHeight==60,'Compact objective has no room for timer/Guide')
 check(shared,'Short touch route cannot use the idle objective lane')
 check(center,'Center tracker did not request its own meter layout')
end
for _,view in ipairs({{388,704,true,160},{567,346,true,160},{1024,768,false,64},{320,240,true,160}})do
 local left,top,w,h=academy.trackerLayout({X=view[1],Y=view[2]},view[3],view[4])
 check(left==16 and top==view[4] and w==290 and h==50,'Layout changed outside verified compact lane')
end
for _,width in ipairs({510,567,587,588})do
 local viewport={X=width,Y=241}
 local left,top,w,h,shared=academy.trackerLayout(viewport,false,160)
 check(shared and left==16 and top==160 and w==math.min(290,width-298) and h==60,'Short desktop tracker does not fit its rail')
 check(left+w<=width-274-8 and top+h<=viewport.Y-8,'Short desktop tracker crosses combat or screen bounds')
end
for _,viewport in ipairs({{X=750,Y=323},{X=588,Y=315}})do
 local left,top,w,h,shared=academy.trackerLayout(viewport,true,160)
 check(shared and left+w+8<=viewport.X-274 and top+h<=viewport.Y-102,'Landscape phone tracker cannot share its clear rail')
end
local _,_,_,_,_,tooNarrow=academy.trackerLayout({X=587,Y=315},true,160)
local _,_,_,_,_,tooLow=academy.trackerLayout({X=750,Y=323},true,178)
check(tooNarrow and tooLow,'Landscape phone sharing ignores the combat and touch lanes')
local _,_,_,_,talkOverlaps=academy.trackerLayout({X=588,Y=400},true,160)
check(not talkOverlaps,'Landscape guide clear button overlaps Talk on taller narrow screens')
local meter={RecentAmplitude={}}
local function meterLayout(w,h,touch)
 local viewport={X=w,Y=h}
 local trackerY=160
 local trackerX,_,_,_,_,centerTracker=academy.trackerLayout(viewport,touch,trackerY)
 local UDim2={fromOffset=function(x,y)return {x=x,y=y} end,new=function(_,x,_,y)return {x=x,y=y} end}
 academy.VoiceReactor={Layout=function()return 230,84 end}
 __METER_LAYOUT__
 return trackerX
end
local centerX=meterLayout(567,315,true)
check(meter.Position.x==14 and meter.Position.y==164 and meter.Position.x+meter.Size.x+8<=centerX
 and meter.Size.y==56 and not meter.RecentAmplitude.Visible,'Slim meter overlaps the center tracker or cannot fit its history')
meterLayout(750,323,true)
check(meter.Position.x==-115 and meter.Position.y==-96 and meter.Size.y==84 and meter.RecentAmplitude.Visible,
 'Full meter did not restore after resize')
local function visibility(active,selected,paused,touch,view,selection,routeStatus,preview,fighterReady,progress)
 local Config={ResonanceLayout=preview and {} or nil}
 local viewport=view or (touch and {X=750,Y=323} or {X=567,Y=241})
 local showQuest,gameplayVisible=true,not paused
 local data={activeQuest=active and 'sprint' or nil,combatChallenges={fighters=progress}}
 local devPanel={Visible=false}
 local function offset(x,y)return {X={Offset=x},Y={Offset=y}}end
 local UDim2={fromOffset=offset}
 local left,top,w,h,shared=academy.trackerLayout(viewport,touch,160)
 local tracked={Text='Boardwalk Dash\nRun east\n0/1 · 90s left',Position=offset(left,top),Size=offset(w,h)}
 academy.guideMayUseTracker=shared
 academy.guidePanel={}
 academy.guideText={}
 academy.guideTarget=selected and {label='Training courtyard'} or nil
 academy.guideSelection=selection
 academy.trainingGuideFighter=fighterReady~=nil and {Parent={},GetAttribute=function()return fighterReady end} or nil
 academy.guide={GetStatus=function()return routeStatus or 'Follow the markers',42,'N' end}
 academy.trainingGuideButton={}
 academy.canGuideTraining=function()return not active and not selected end
 local zone={}
 __SHARED_RAIL__
 return tracked.Visible,academy.guidePanel.Visible,academy.trainingGuideButton.Visible,academy.guideText.Text
end
local track,route,guide,text=visibility(false,true)
check(route and not track and not guide and text=='Training courtyard\nFollow the markers · 42 studs N','Selected route does not replace idle progress')
track,route,guide=visibility(true,true)
check(track and not route and not guide,'Selected route covered an active quest timer')
track,route,guide=visibility(false,false)
check(track and not route and guide,'Clearing a route did not restore the idle Guide button')
track,route,guide=visibility(false,true,true)
check(not track and not route and not guide,'Selected route remained over a modal')
track,route,guide,text=visibility(false,true,false,true)
check(route and not track and not guide and text=='Training courtyard\nFollow the markers · 42 studs N','Selected route hidden on landscape phone')
track,route,guide=visibility(true,true,false,true)
check(track and not route and not guide,'Landscape phone route covered active quest status')
track,route,guide,text=visibility(false,true,false,true,{X=529,Y=242})
check(route and not track and not guide and text=='Training courtyard\nFollow the markers · 42 studs N','Short touch route disappeared after Guide')
track,route,guide=visibility(true,true,false,true,{X=529,Y=242})
check(track and not route and not guide,'Short touch route covered an active quest timer')
local training={kind='place',id='training'}
local _,_,_,arrival=visibility(false,true,false,true,{X=529,Y=242},training,'Arrived',false,true)
check(arrival=='Hit the fighter to spar\nFighters 0/3','Training arrival does not teach the first action')
_,_,_,arrival=visibility(false,true,false,true,{X=667,Y=375},training,'Arrived',false,true)
check(arrival=='Hit the fighter to spar','Compact training arrival carries stale distance or heading')
_,_,_,arrival=visibility(false,true,false,true,{X=666,Y=316},training,'Arrived',false,false,1)
check(arrival=='Fighter recovering\nFighters 1/3','Recovery or progress is missing on the shared tracker')
_,_,_,arrival=visibility(false,true,false,true,{X=666,Y=316},training,'Arrived',false,nil,1)
check(arrival=='Sparring pad\nFighters 1/3','An unobserved fighter was reported alive or recovering')
_,_,_,arrival=visibility(false,true,false,true,{X=666,Y=316},training,'Arrived',false,true,1)
check(arrival=='Hit the fighter to spar\nFighters 1/3','A returned fighter did not restore the action')
_,_,_,arrival=visibility(false,true,false,true,{X=529,Y=242},training,'Follow the markers')
check(arrival=='Training courtyard\nFollow the markers · 42 studs N','Training arrival cue appears before reaching the pad')
_,_,_,arrival=visibility(false,true,false,true,{X=529,Y=242},{kind='place',id='gardens'},'Arrived')
check(arrival=='Training courtyard\nArrived · 42 studs N','Another destination showed fight instructions')
_,_,_,arrival=visibility(false,true,false,true,{X=529,Y=242},{kind='quest',id='training'},'Arrived')
check(arrival=='Training courtyard\nArrived · 42 studs N','Another guide type showed fight instructions')
track,route,guide=visibility(false,false,false,true,{X=666,Y=316},nil,nil,true)
check(not track and not guide,'Arena preview displayed the city training tracker')
print('PASS '..checks..' navigation layout checks; no native rendering claim')
'''
start=s.index(' local guideUsesTracker=false')
stop=s.index(' local now=workspace:GetServerTimeNow();local protected=',start)
code=code.replace('__SHARED_RAIL__',s[start:stop])
start=s.index(' local meterWidth,meterHeight=')
stop=s.index(' local testBottom=',start)
code=code.replace('__METER_LAYOUT__',s[start:stop])
start=s.index('academy.compactObjective=button(')
compact_ui=s[start:s.index('\nacademy.guideMenu=',start)]
start=s.index(' academy.compactObjective.Visible=academy.shortObjective and')
compact_render=s[start:s.index('\n local guideUsesTracker=false',start)]
code+=r'''
do
local top,shop,questsToggle={},{},{}
academy.passesToggle={}
local data={training='Rookie',quests={},combatChallenges={fighters=1}}
local quest={id='sprint',goal=3}
local Config={CompactCity=true,GetQuest=function(id)return id=='sprint' and quest or nil end}
local GuiService={MenuIsOpen=false};local modal,devPanel,conversationPanel={},{},{}
local gold={}
local showQuest=true
local tracked={Text='Only draw this once state arrives'}
local function toggleTab(tab,reset,focus)check(tab=='Quests' and reset and focus=='sprint','Compact quest opened the wrong task');modal.Visible=true end
local function button(_,_,_,size,pos,callback)return {Size=size,Position=pos,Activated=callback}end
local UDim2={fromOffset=function(x,y)return {x=x,y=y}end}
academy.surface=function()end
academy.canGuideTraining=function()return not data.activeQuest and not academy.guideSelection end
academy.selectGuide=function(kind,id)check(kind=='place' and id=='training','Compact Guide picked the wrong route');academy.guideSelection={kind=kind,id=id}end
academy.clearGuide=function()academy.guideSelection=nil end
local status='Follow the markers'
academy.guide={GetStatus=function()return status end}
''' + compact_ui + r'''
local function refresh(gameplayVisible)
''' + compact_render + r'''
 if academy.compactObjective.Visible then academy.compactObjective.Text=academy.compactObjectiveText() end
end
academy.layoutObjectiveNav({X=492,Y=150},true,true)
local b=academy.compactObjective
check(top.Position.y==0 and shop.Size.x>=45 and b.Size.x==104 and b.Size.y==44,'Compact navigation lacks a safe touch row')
local passes=academy.passesToggle
check(passes.Size.x>44 and passes.Size.y>44 and passes.Position.x==shop.Size.x+6,'Passes touch target or Menu clearance was lost')
check(b.Position.x>=passes.Position.x+passes.Size.x+6 and questsToggle.Position.x>=b.Position.x+52+6,'Compact objective overlaps a navigation sibling')
check(top.Position.x+questsToggle.Position.x+questsToggle.Size.x<492-246,'Compact navigation overlaps the action stack')
academy.layoutObjectiveNav({X=480,Y=150},true,true)
check(questsToggle.Size.x>=44 and questsToggle.Size.y>=44 and top.Position.x+questsToggle.Position.x+questsToggle.Size.x<480-246,
 'Narrow navigation overlaps the action stack or loses its touch target')

refresh(true);check(b.Visible and b.Text=='ROOKIE GUIDE\n1/3 fighters','Compact idle objective lost the first-spar goal')
b.Activated();refresh(true)
check(b.Text=='FOLLOW GUIDE\n1/3 · Clear','Compact training route missing progress or Clear')
academy.refreshCompactObjective(true);check(b.Text=='CLEAR\nEn route','Tight row concealed the active route clear action')
status='Arrived';academy.trainingGuideFighter={Parent={},GetAttribute=function()return true end};refresh(true)
check(b.Text=='HIT TO SPAR\n1/3 · Clear','Compact arrival lost its instruction')
academy.trainingGuideFighter.GetAttribute=function()return false end;refresh(true)
check(b.Text=='FIGHTER RESTING\n1/3 · Clear','Compact arrival masked recovery')
data.activeQuest='sprint';data.quests.sprint={progress=2};data.questTime=37
refresh(true);check(b.Text=='VIEW QUEST\n2/3 · 37s','Compact guide covered the active quest timer')
data.questTime=120;academy.refreshCompactObjective(true);check(b.Text=='2/3\n120s' and b.Size.x==52 and b.Size.y==46,'Tight row lost quest timing or its touch target')
b.Activated();check(modal.Visible and academy.guideSelection~=nil,'Quest click cleared the selected guide')
modal.Visible=false;data.activeQuest=nil
b.Activated();refresh(true);check(b.Text=='ROOKIE GUIDE\n1/3 fighters','Clearing the compact guide did not restore the goal')
refresh(false);b.Activated();check(not b.Visible and not academy.guideSelection,'A hidden compact objective accepted a click')
refresh(true);modal.Visible=true;b.Activated();check(not academy.guideSelection,'A stale compact click bypassed the menu')
modal.Visible=false;devPanel.Visible=true;refresh(true);check(not b.Visible,'Compact objective covered the tester panel');devPanel.Visible=false
academy.layoutObjectiveNav({X=509,Y=220},true,true);refresh(true)
check(b.Visible,'The compact objective disappeared inside the stacked band')
academy.layoutObjectiveNav({X=566,Y=244},true,false);refresh(true)
check(not b.Visible and top.Position.y==2 and shop.Size.x==74 and questsToggle.Size.x==78,'Standard navigation layout did not restore')
Config.ResonanceLayout={};academy.layoutObjectiveNav({X=509,Y=162},true,true);refresh(true)
check(not b.Visible,'PvP place exposed the Academy objective')
end
print('PASS '..checks..' total navigation and compact objective assertions')
'''
def run(payload):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='tmp_layout_',dir=root/'tests',delete=False) as f:
        f.write(payload)
        temp=Path(f.name)
    try:return subprocess.run(['luau',str(temp)],cwd=root,capture_output=True,text=True)
    finally:temp.unlink()
result=run(code)
assert result.returncode==0,result.stderr
print(result.stdout.strip())
cases = [
    ('math.ceil(w*.4)+8','16','Tracker enters thumbstick lane'),
    ('w-103','w-80','Tracker enters Jump lane'),
    ('if width>=196 then','if width>=212 then','Tracker enters thumbstick lane'),
    ('math.max(defaultY,h-91),width,60,true,true','math.max(defaultY,h-91),width,60,false,true','Short touch route cannot use the idle objective lane'),
    ('h<346 and w>h and not canShare','h<315 and w>h and not canShare','Tracker enters thumbstick lane'),
    ('local slimMeter=centerTracker and viewport.Y>=315','local slimMeter=false','Slim meter overlaps the center tracker or cannot fit its history'),
    ('math.max(defaultY,h-91)','defaultY','Tracker enters combat lane'),
    ('math.min(290,w-274-8-16)','290','Short desktop tracker does not fit its rail'),
    ('and not data.activeQuest and showQuest','and showQuest','Selected route covered an active quest timer'),
    ('and not (guideUsesTracker and academy.guidePanel.Visible)','and true','Selected route does not replace idle progress'),
    ('w-274>=314 and defaultY+50<=h-102','true','Tracker enters thumbstick lane'),
    (' and h<346 and w-274>=314',' and w-274>=314','Landscape guide clear button overlaps Talk on taller narrow screens'),
    ('status=="Arrived" and selection.kind=="place" and selection.id=="training"', 'status=="Arrived" and selection.kind=="place"', 'Another destination showed fight instructions'),
    ('status=="Arrived" and selection.kind=="place" and selection.id=="training"', 'selection and selection.kind=="place" and selection.id=="training"', 'Training arrival cue appears before reaching the pad'),
    ('ready==false and "Fighter recovering"', 'false and "Fighter recovering"', 'Recovery or progress is missing on the shared tracker'),
    ('or "Sparring pad"', 'or "Fighter recovering"', 'An unobserved fighter was reported alive or recovering'),
    ('compact and 58 or 0', 'compact and 44 or 0', 'Compact objective overlaps a navigation sibling'),
    ('timer>0 and string.format(" · %ds",timer)', 'false and string.format(" · %ds",timer)', 'Compact guide covered the active quest timer'),
    ('compact and 45 or narrowNav and 54 or 78','compact and 56 or narrowNav and 54 or 78','Narrow navigation overlaps the action stack'),
    ('if not academy.shortObjective or not academy.compactObjective.Visible', 'if not academy.shortObjective', 'A hidden compact objective accepted a click'),
]
for old,new,reason in cases:
    assert code.count(old)==1,old
    result=run(code.replace(old,new))
    assert result.returncode and reason in result.stderr,(old,result.stderr)
print(f'PASS {len(cases)} tracker, guide, menu and timer negative controls')
assert 'or noticeView:Overlaps(passive,gui,talkButton)' in s and 'meter,academy.guidePanel}' in s
assert 'if academy.guideText.Text~=text' in s
