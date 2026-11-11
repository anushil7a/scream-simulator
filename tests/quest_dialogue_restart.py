"""Actual NPC dialogue renderer/callback with mock GUI; no native text metrics."""
from pathlib import Path
import argparse,subprocess,tempfile
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');a=p.parse_args()
path='src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
s=subprocess.check_output(['git','show','af8c277:'+path],cwd=R,text=True,encoding='utf-8') if a.baseline else (R/path).read_text(encoding='utf-8')
f=s[s.index('showConversation=function(info)'):s.index('\nlocal function refreshQuestObjects()')]
setup=r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local UDim2={new=function(...)return {...}end};local Vector2={zero={}};local Enum={AutomaticSize={Y='Y'}}
local modal={};local devPanel={};local conversationName={};local conversationPanel={};local conversationList={GetChildren=function()return {}end}
local texts,buttons,sent={},{},{};local closed=0
local function label(_,text)local l={Text=text};table.insert(texts,l);return l end
local function button(_,name,text,size,pos,callback)local b={Text=text,callback=callback};table.insert(buttons,b);return b end
local function cancelCapture()end;local function closeConversation()closed+=1 end
local function closeMenu()modal.Visible=false end -- Lifecycle exercised separately by shop_modal_lifecycle.py
local action={FireServer=function(_,verb,id)table.insert(sent,{verb,id})end}
local goals={garden=3,practice_beams=3,beach=6,delivery=1};local Config={GetQuest=function(id)return goals[id] and {goal=goals[id]}end}
local data={quests={}}
'''
checks=r'''
for _,id in ipairs({'garden','practice_beams','beach','delivery'})do
 for _,kind in ipairs({'zero','partial','active','complete','claimed','missing'})do
  texts={};buttons={};sent={};closed=0;data.quests={};data.activeQuest=nil
  local goal=goals[id];local progress=kind=='zero' and 0 or kind=='complete' and goal or kind=='claimed' and goal or math.max(0,goal-1)
  if kind~='missing'then data.quests[id]={progress=progress}end
  if kind=='active'then data.activeQuest=id end
  local q={id=id,name='Task',description='Objective',claimed=kind=='claimed',complete=kind=='complete' or kind=='claimed'}
  showConversation({name='NPC',line='Hello',hint='Hint',quests={q}})
  local b=buttons[2];local restart=kind=='partial' and goal>1
  local all='';for _,l in ipairs(texts)do all..=l.Text end
  check((all:find('Restarting resets this unfinished progress.',1,true)~=nil)==restart,'Restart disclosure mismatch '..id..' '..kind)
  check((b.Text:find('Restart: ',1,true)==1)==restart,'Restart label mismatch '..id..' '..kind)
  check(b.Active==(kind~='claimed') and b.AutoButtonColor==b.Active,'Claimed interaction changed')
  b.callback()
  if kind=='claimed'then check(#sent==0 and closed==0,'Claimed task sent action')
  else check(#sent==1 and sent[1][1]==(kind=='complete' and 'ClaimQuest' or 'AcceptQuest') and sent[1][2]==id and closed==1,'Action contract changed')end
 end
end
-- The server supplies unlocked dialogue choices; absent/locked choices stay absent.
texts={};buttons={};sent={};showConversation({name='NPC',line='Hello',hint='Hint',quests={}})
check(#buttons==2 and #sent==0,'Renderer invented locked quest choice')
print('PASS',n,'actual dialogue assertions; mocked GUI/catalog goals, no native fit')
'''
def run(fragment,error=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=R/'tests',encoding='utf-8',delete=False)as t:t.write(setup+fragment+checks);q=Path(t.name)
 try:r=subprocess.run(['luau',str(q)],capture_output=True,text=True)
 finally:q.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS expected failure:',error)
 else:print(out,end='');assert r.returncode==0
if a.baseline:run(f,'Restart disclosure mismatch garden partial')
else:
 run(f)
 if a.negative_controls:
  for old,new,error in [
   ('restarting and "\\n\\nRestarting resets this unfinished progress."','false and "\\n\\nRestarting resets this unfinished progress."','Restart disclosure mismatch garden partial'),
   ('restarting and "Restart: "','false and "Restart: "','Restart label mismatch garden partial'),
   (' and data.activeQuest~=q.id','','Restart disclosure mismatch garden active'),
   ('q.complete and "ClaimQuest" or "AcceptQuest"','"AcceptQuest"','Action contract changed')]:
   assert f.count(old)==1,old;run(f.replace(old,new),error)
