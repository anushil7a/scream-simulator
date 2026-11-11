"""Actual panel registrations/wrappers + server quest/style helpers, mocked UI/session.
No native queued-event, remote transport, persistence or full dispatcher claim.
"""
from pathlib import Path
import argparse,re,subprocess,tempfile
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');a=p.parse_args()
path='src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
assert re.search(r'MicroSpeakerPrice\s*=\s*1500', (R/'src/ReplicatedStorage/Shared/Config.luau').read_text()), 'Fixture price must follow Config'
c=(R/path).read_text();server=(R/'src/ServerScriptService/Bootstrap.server.luau').read_text()
setup=r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local function fixture()
local function copy(t)if type(t)~='table'then return t end;local out={};for k,v in pairs(t)do out[k]=copy(v)end;return out end
local function node()return {Parent=true,Visible=true,GetChildren=function()return {}end,Destroy=function(self)self.Parent=nil end}end
local Color3={fromRGB=function()return {}end};local Vector2={new=function(x,y)return {X=x,Y=y}end,zero={X=0,Y=0}}
local UDim2={new=function()return {}end,fromOffset=function()return {}end,fromScale=function()return {}end}
local Enum={Font={GothamMedium=1},AutomaticSize={Y=1}};local TextService={GetTextSize=function()return {Y=30}end}
local buttons={};local function button(parent,name,text,size,pos,callback,color)local b=node();b.Text=text;b.callback=callback;b.color=color;buttons[name]=b;return b end
local function card()return node()end;local function label(_,text)local n=node();n.Text=text;return n end;local function frame()return node()end;local function info()end
local Config={MaxLevel=100,MicroSpeakerPrice=1500,MovementPassId=0,Auras={Gold={}},Progression={Challenges={}},Quests={}}
for _,id in ipairs({'garden','practice_beams'})do table.insert(Config.Quests,{id=id,name=id,description='Task',goal=3,event='PracticeBeam',xp=60,coins=25,menuAvailable=id=='practice_beams'})end
function Config.GetQuest(id)for _,q in ipairs(Config.Quests)do if q.id==id then return q end end end
local p={};local s={activeQuest='garden',data={coins=2000,xp=0,aura='Blue',useCustomColor=false,amplifierOwned=false,amplifierEquipped=false,availableQuests={garden=true},quests={garden={progress=1,claimed=false},practice_beams={progress=2,claimed=false}},achievements={}}}
local sessions={[p]=s};local Soccer={Cancel=function()end};local Commerce={Multiplier=function()return 1 end}
local function state()end;local function coins(_,v)s.data.coins+=v end;local function xp(_,v)s.data.xp+=v end
local QuestLifecycle=require('../src/ReplicatedStorage/Shared/QuestLifecycle')
'''
ui=r'''
local sent={};local action={FireServer=function(_,verb,arg)table.insert(sent,{verb,arg});dispatch(verb,arg)end}
local clientDestroyed=false;local modal=node();modal.Visible=false;local gui={AbsoluteSize={X=720}}
local content=node();content.CanvasPosition={X=0,Y=40};content.AbsoluteCanvasSize={Y=600};content.AbsoluteWindowSize={Y=200}
local title,subtitle={},{};local selected='Quests';local render;local tabs={};local devPanel=node();local narrow=false
local conversationPanel=node();conversationPanel.Visible=false;local showConversation,closeConversation;local conversationName=node();local conversationList=node()
local muted,gold,panel,white={},{},{},{};local version=0;local data
local function snapshot()data=copy(s.data);data.activeQuest=s.activeQuest;data.level=1;data.settings={volume=.5,reducedShake=false};version+=1 end
snapshot()
local function menuKey()return selected..version end
local ShopUI={Clear=function()end,ColorMixer=function(_,ui)ui.button({},'Forward','Forward',{}, {},function(...)return ... end)end}
local task={spawn=function()end};local Run={Heartbeat={Wait=function()end}}
local effects={calibrate=0,cancel=0,disarm=0,sprint=0}
local function cancelCapture()effects.cancel+=1 end
local function setSprint()effects.sprint+=1 end
local mic={Calibrate=function()effects.calibrate+=1 end}
local sustainedControl={SetArmed=function()effects.disarm+=1 end};local sustainedRules={MaxDuration=4,Cooldown=5}
local UIS={TouchEnabled=false};Config.DodgeCooldown=3;Config.SprintDuration=4;Config.SprintRecovery=3;Config.SprintRegenDelay=1
local attackAudio={level='NORMAL'};local gameplayAudio={enabled=true};local gameplayAudioSettings={Ready=function()return false end}
'''
def assemble(client):
 close=client[client.index('local renderedMenuKey,renderedTab'):client.index('button(modal,"Close","X"')]
 toggle=client[client.index('local function toggleTab('):client.index('\nlocal shop=button(top,')]
 render=client[client.index('render=function()'):client.index('\nlocal conversationNPC,conversationUntil')]
 convdecl=client[client.index('local conversationNPC,conversationUntil'):].split('conversationPanel=frame',1)[0]
 closeconv=client[client.index('closeConversation=function()'):client.index('local function refreshConversation()')]
 show=client[client.index('showConversation=function(info)'):client.index('\nlocal function refreshQuestObjects()')]
 stop=server[server.index('local function stopQuest(p)'):server.index('local function protect(p,s)')]
 micro=server[server.index('local function microSpeaker(p,s,toggleOwned)'):server.index('local function vendorPurchase(p,s,arg)')]
 branches=server[server.index(' elseif verb=="SetAura" and'):server.index(' elseif verb=="SetSettings" and')]
 dispatch='local function dispatch(verb,arg) if verb=="MicroSpeaker" then microSpeaker(p,s,true)'+branches+' end end\n'
 return '\n'.join([setup,stop,micro,dispatch,ui,close,toggle,render,convdecl,closeconv,show])+r'''
local f={s=s,sent=sent,modal=modal,conversation=conversationPanel,effects=effects}
function f.open(tab)snapshot();toggleTab(tab)end
function f.tab(tab)tabs[tab].callback()end
function f.rerender()snapshot();render()end
function f.button(name)return buttons[name].callback end
function f.close()closeMenu()end
function f.destroy()clientDestroyed=true end
function f.dialogue(id,complete)
 snapshot();showConversation({npc={},name='NPC',line='Hello',hint='Hint',quests={{id=id,name=id,description='Task',complete=complete==true,claimed=false}}})
end
function f.npcAction()return buttons.Choice.callback end
function f.closeNpc()closeConversation()end
return f
end
'''
# Choice buttons share names, so capture by visible quest text in the raw mock.
# This observes actual registrations, not a recreated production callback.
setup=setup.replace('buttons[name]=b;return b','buttons[name]=b;if name=="Choice" and (text:find("Accept: ",1,true) or text:find("Restart: ",1,true) or text:find("Claim: ",1,true))then buttons.QuestChoice=b end;return b')
def tail(case):
 return r'''
local f=fixture();f.open('Quests');local old=f.button('ActiveQuestAction');f.close();f.s.activeQuest='practice_beams';old()
check(f.s.activeQuest=='practice_beams' and f.s.data.quests.practice_beams.progress==2,'Stale menu abandon erased newer attempt')
f=fixture();f.dialogue('garden');old=f.npcAction();f.closeNpc();f.s.activeQuest='practice_beams';old()
check(f.s.activeQuest=='practice_beams' and f.s.data.quests.practice_beams.progress==2,'Stale NPC accept erased newer attempt')
''' if case=='baseline' else checks
checks=r'''
for _,mode in ipairs({'hidden','close','reopen','replace','sameReplace','destroy'})do
 local f=fixture();f.open('Quests');local old=f.button('ActiveQuestAction');f.s.activeQuest='practice_beams'
 if mode=='hidden'then f.modal.Visible=false elseif mode=='close'then f.close()elseif mode=='reopen'then f.close();f.open('Quests')elseif mode=='replace' or mode=='sameReplace'then f.rerender()else f.destroy()end
 old();check(f.s.activeQuest=='practice_beams' and f.s.data.quests.practice_beams.progress==2,'Menu stale abandon: '..mode)
end
for _,mode in ipairs({'hidden','close','reopen','replace','sameReplace','destroy'})do
 local f=fixture();f.dialogue('garden');local old=f.npcAction();f.s.activeQuest='practice_beams'
 if mode=='hidden'then f.conversation.Visible=false elseif mode=='close'then f.closeNpc()elseif mode=='reopen'then f.closeNpc();f.dialogue('practice_beams')elseif mode=='replace'then f.dialogue('practice_beams')elseif mode=='sameReplace'then f.dialogue('garden')else f.destroy()end
 old();check(f.s.activeQuest=='practice_beams' and f.s.data.quests.practice_beams.progress==2,'NPC stale accept: '..mode)
end
for _,name in ipairs({'MicroSpeaker','BaseColor'})do
 for _,mode in ipairs({'close','reopen','replace','destroy'})do
  local f=fixture();f.open('Quests');f.tab('Style');local old=f.button(name)
  if mode=='close'then f.close()elseif mode=='reopen'then f.close();f.open('Style')elseif mode=='replace' or mode=='sameReplace'then f.rerender()else f.destroy()end
  old();check(f.s.data.coins==2000 and not f.s.data.amplifierOwned and f.s.data.aura=='Blue','Stale Style changed economy/color: '..mode..name)
 end
end
local f=fixture();f.open('Quests');f.button('ActiveQuestAction')();check(f.s.activeQuest==nil and f.s.data.quests.garden.progress==0,'Current abandon blocked')
f.rerender();f.button('practice_beams')();check(f.s.activeQuest=='practice_beams' and f.s.data.quests.practice_beams.progress==0,'Current accept blocked')
f.s.data.quests.practice_beams.progress=3;f.rerender();local claim=f.button('practice_beams');claim();claim();check(f.s.data.coins==2025 and f.s.data.xp==60 and f.s.data.quests.practice_beams.claimed,'Claim duplicate/authority changed')
f.tab('Style');f.button('MicroSpeaker')();check(f.s.data.coins==525 and f.s.data.amplifierOwned,'Current Style purchase blocked')
f.button('BaseColor')();check(f.s.data.aura=='Gold','Current legacy-color action blocked')
f=fixture();f.dialogue('practice_beams');f.npcAction()();check(f.s.activeQuest=='practice_beams' and not f.conversation.Visible,'Current NPC accept blocked')
f.s.data.quests.practice_beams.progress=3;f.dialogue('practice_beams',true);local claim=f.npcAction();claim();claim();check(f.s.data.coins==2025 and f.s.data.xp==60,'NPC claim duplicate/authority changed')
f=fixture();f.s.data.availableQuests.garden=false;f.dialogue('garden');f.npcAction()();check(f.s.activeQuest=='garden' and f.s.data.quests.garden.progress==1,'Server discovery gate changed')
f=fixture();local a,b=f.forwardNpc(23,'npc');check(a==23 and b=='npc','NPC callback arguments/return not forwarded');f.open('Style');local one,two=f.button('Forward')(17,'sentinel');check(one==17 and two=='sentinel','Menu callback arguments/return not forwarded')
for _,panel in ipairs({'menu','npc'})do
 f=fixture();f.s.data.quests.practice_beams.progress=3
 local old
 if panel=='menu'then f.open('Quests');old=f.button('practice_beams');f.close()else f.dialogue('practice_beams',true);old=f.npcAction();f.closeNpc()end
 old();check(f.s.data.coins==2000 and not f.s.data.quests.practice_beams.claimed,'Stale claim paid reward: '..panel)
end
f=fixture();f.dialogue('practice_beams',true);f.npcAction()();check(f.s.data.coins==2000 and not f.s.data.quests.practice_beams.claimed,'Incomplete server claim gate changed')
f=fixture();f.open('Quests');local accept=f.button('practice_beams');f.close();f.open('Quests');accept();check(f.s.activeQuest=='garden' and f.s.data.quests.garden.progress==1,'Old menu accept reset current attempt')
for _,mode in ipairs({'close','replace','destroy'})do
 f=fixture();f.open('Settings');local old=f.button('Recalibrate')
 if mode=='close'then f.close()elseif mode=='replace'then f.rerender()else f.destroy()end
 old();check(f.effects.calibrate==0 and f.effects.cancel==0 and f.effects.disarm==0 and f.effects.sprint==0,'Stale recalibration changed microphone intent: '..mode)
end
f=fixture();f.open('Settings');f.button('Recalibrate')();check(f.effects.calibrate==1 and f.effects.cancel==1 and f.effects.disarm==1 and f.effects.sprint==1 and not f.modal.Visible,'Current recalibration blocked')
print('PASS',n,'registered panel callbacks with actual quest/style server helpers; mocked GUI/session')
'''
def run(client,error=None,case=None):
 code=assemble(client).replace('return buttons.Choice.callback','return buttons.QuestChoice.callback')
 if not a.baseline:
  choice=client[client.index(' local function choice(text,callback)'):client.index(' choice("Tell me about this neighborhood"')]
  probe='function f.forwardNpc(...) local order=0;local revision=conversationRevision;conversationPanel.Visible=true;'+choice+' local b=choice("probe",function(...)return ... end);return b.callback(...) end\n'
  code=code.replace('return f\nend',probe+'return f\nend')
 code+=tail(case)
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.panel_',dir=R/'tests',encoding='utf-8',delete=False)as t:t.write(code);q=Path(t.name)
 try:r=subprocess.run(['luau',str(q)],capture_output=True,text=True,timeout=20)
 finally:q.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS expected failure:',error)
 else:print(out,end='');assert r.returncode==0
if a.baseline:
 old=subprocess.check_output(['git','show','edc9442:'+path],cwd=R,text=True,encoding='utf-8');run(old,'Stale menu abandon erased newer attempt','baseline')
 run(old,'Menu stale abandon: hidden')
 # Isolate NPC/Style baseline cases so the first known failure cannot mask them.
 saved=checks
 checks=checks[checks.index("for _,mode in ipairs",checks.index("for _,mode in ipairs")+1):];run(old,'NPC stale accept: hidden')
 checks=saved[saved.index("for _,name in ipairs({'MicroSpeaker','BaseColor'})"):];run(old,'Stale Style changed economy/color: closeMicroSpeaker')
 checks=checks.replace("{'MicroSpeaker','BaseColor'}","{'BaseColor','MicroSpeaker'}");run(old,'Stale Style changed economy/color: closeBaseColor')
else:
 run(c)
 if a.negative_controls:
  for scope,word,error in [('modal','clientDestroyed or ','Menu stale abandon: destroy'),('modal','not modal.Visible or ','Menu stale abandon: hidden'),('modal',' or revision~=renderRevision','Menu stale abandon: reopen'),('conversation','clientDestroyed or ','NPC stale accept: destroy'),('conversation','not conversationPanel.Visible or ','NPC stale accept: hidden'),('conversation',' or revision~=conversationRevision','NPC stale accept: reopen')]:
   guard='if clientDestroyed or not '+('modal.Visible or revision~=renderRevision' if scope=='modal' else 'conversationPanel.Visible or revision~=conversationRevision')+' then return end'
   assert c.count(guard)==1;run(c.replace(guard,guard.replace(word,'')),error)
