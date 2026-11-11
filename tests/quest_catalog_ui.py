"""Actual quest renderer/catalog with synthetic UI; not a native layout assertion."""
from config_fixture import inline_compact_layout
from pathlib import Path
import argparse,re,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--negative-controls',action='store_true');parser.add_argument('--baseline',action='store_true');args=parser.parse_args()
def read(name):
 if args.baseline:return subprocess.check_output(['git','show','32cced3:'+name],cwd=root,text=True,encoding='utf-8')
 return (root/name).read_text(encoding='utf-8')
client=read('src/StarterPlayer/StarterPlayerScripts/Client.client.luau')
config=read('src/ReplicatedStorage/Shared/Config.luau')
config=inline_compact_layout(config,root)
config=re.sub(r'require\(script\.Parent:WaitForChild\("(\w+)"\)\)',lambda m:'require("../src/ReplicatedStorage/Shared/'+m[1]+'")',config)
a=client.index(' elseif selected=="Quests" then\n  title.Text=')
a=client.index('\n',a)+1
fragment=client[a:client.index(' elseif selected=="Style" then',a)]
setup="""
local checks=0;local function check(ok,msg)assert(ok,msg);checks+=1 end
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local Color3={fromRGB=function(r,g,b)return {r,g,b}end}
local Vector2={new=function(x,y)return {X=x,Y=y}end}
local UDim2={new=function(...)return {...}end,fromOffset=function(x,y)return {X=x,Y=y}end}
local Enum={Font={GothamMedium=1}}
local TextService={GetTextSize=function()return {Y=40}end}
local Config=(function()
"""
between="""
end)()
local data,narrow;local title,subtitle={},{};local gui={AbsoluteSize={X=390}};local gold,muted={},{}
local messages,buttons,calls,cards,order={},{},{},{},{}
local function info(text)table.insert(messages,text);table.insert(order,{kind="info",text=text})end
local function card()local c={labels={}};table.insert(cards,c);table.insert(order,{kind="card",card=c});return c end
local function label(c,text)table.insert(messages,text);table.insert(c.labels,text);return {}end
local function button(c,id,text,_,_,fn)buttons[id]={text=text,call=fn,card=c};c.button=id;return {}end
local action={FireServer=function(_,verb,id)table.insert(calls,{verb,id})end}
local function render(value,isNarrow)
 data=value;narrow=isNarrow;gui.AbsoluteSize.X=isNarrow and 390 or 1280;messages={};buttons={};calls={};cards={};order={}
"""
checks="""
end
local function copy(value)
 if type(value)~='table' then return value end
 local out={};for k,v in pairs(value)do out[k]=copy(v)end;return out
end
local function equal(a,b)
 if type(a)~=type(b) then return false end
 if type(a)~='table' then return a==b end
 for k,v in pairs(a)do if not equal(v,b[k])then return false end end
 for k in pairs(b)do if a[k]==nil then return false end end
 return true
end
local expected={nick={1,1800,1200},garden={3,130,80},beach={6,100,50},delivery={1,120,60},crowd={1,100,40},sprint={1,120,50},dodge={3,160,70},arena={1,180,80},practice_beams={3,60,25},arena_assist={1,120,50}}
check(#Config.Quests==10,'City quest definitions unexpectedly changed')
for _,q in ipairs(Config.Quests)do
 local e=expected[q.id];check(e and q.goal==e[1] and q.xp==e[2] and q.coins==e[3],'Quest identity/goal/rewards changed')
end
local catalog=copy(Config.Quests)
local combat={crowd=true,dodge=true,arena=true,practice_beams=true,arena_assist=true}
local function grouped(count)
 local group;local headings={};local seen={};local sequence={}
 for _,entry in ipairs(order)do
  if entry.kind=='info' and (entry.text=='BEAM COMBAT TASKS' or entry.text=='OPTIONAL CITY ACTIVITIES')then
   group=entry.text;table.insert(headings,group)
  elseif entry.kind=='card' and expected[entry.card.button]then
   local id=entry.card.button
   check(not seen[id],'Quest card duplicated');seen[id]=true;table.insert(sequence,id)
   check(group==(combat[id] and 'BEAM COMBAT TASKS' or 'OPTIONAL CITY ACTIVITIES'),'Quest in wrong group')
  end
 end
 check(#headings==2 and headings[1]=='BEAM COMBAT TASKS' and headings[2]=='OPTIONAL CITY ACTIVITIES','Combat quest group is not first')
 check(#sequence==count,'Visible quest count changed')
 check(sequence[1]=='crowd' and sequence[2]=='dodge' and sequence[3]=='arena','Combat quests not prioritized')
 return sequence
end
local function renderChecked(value,isNarrow)
 local before=copy(value);render(value,isNarrow)
 check(equal(value,before),'Rendering mutated player quest/save state')
 check(equal(Config.Quests,catalog),'Rendering reordered or mutated quest catalog')
end
for _,isNarrow in ipairs({false,true})do
 local value={level=60,training='Elite',combatChallenges={fighters=2,cover=4,elite=1},quests={},availableQuests={}}
 renderChecked(value,isNarrow)
 local text=table.concat(messages,' | ')
 check(not text:find('Destroy 5',1,true) and not text:find('Help defeat 2',1,true),'Retired challenge displayed')
 local _,count=text:gsub('XP on completion','')
 check(count==1 and text:find('2/3',1,true),'Active training challenge missing or duplicated')
 check(text:find(Config.CompactCity and 'Environment cover is static.' or 'Breaking objects is not a quest.',1,true)~=nil,'Quest help still implies destruction task')
 check(text:find('no more than 20 levels above',1,true)~=nil,'Training help invents lower-level exclusion')
 check(not buttons.nick,'Hidden city quest exposed before discovery')
 local garden=table.concat(buttons.garden.card.labels,' | ')
 local beach=table.concat(buttons.beach.card.labels,' | ')
 check(garden:find(Config.GetQuest('garden').description,1,true) and beach:find(Config.GetQuest('beach').description,1,true),'Distinct undiscovered objectives missing')
 check(buttons.garden.card.labels[2]~=buttons.beach.card.labels[2],'Distinct tasks look like duplicate generic quests')
 check(Config.GetQuest('garden').giver==Config.GetQuest('beach').giver and garden:find(Config.GetQuest('garden').giver,1,true) and beach:find(Config.GetQuest('beach').giver,1,true),'Shared correct giver missing')
 grouped(9)
 for _,q in ipairs(Config.Quests)do if not q.hidden and q.menuAvailable~=true then
  local b=buttons[q.id];local cardText=table.concat(b.card.labels,' | ')
  check(cardText:find(q.description,1,true) and cardText:find('To unlock:',1,true) and cardText:find(q.giver,1,true),'Locked card lacks objective or discovery instructions')
  check(b.text=='MEET NPC','Undiscovered button bypasses meet requirement');b.call()
  check(#calls==0,'Undiscovered quest action bypassed guard')
 end end
 for _,id in ipairs({'practice_beams','arena_assist'})do
  local b=buttons[id];check(b and b.text=='ACCEPT','Direct-available combat quest locked')
  check(not table.concat(b.card.labels,' | '):find('To unlock:',1,true),'Direct quest shows nonexistent giver lock')
  local before=#calls;b.call();check(#calls==before+1 and calls[#calls][1]=='AcceptQuest' and calls[#calls][2]==id,'Direct quest acceptance missing')
 end
 calls={}
 -- Even a stale completed progress packet must not bypass discovery.
 for _,q in ipairs(Config.Quests)do value.quests[q.id]={progress=q.goal}end
 renderChecked(value,isNarrow);check(not buttons.nick,'Hidden quest exposed by progress alone')
 for _,q in ipairs(Config.Quests)do if not q.hidden and q.menuAvailable~=true then buttons[q.id].call();check(#calls==0,'Locked completed quest bypassed discovery')end end
 -- Discovery reveals every original quest, preserving acceptance and hiding unlock instructions.
 for _,q in ipairs(Config.Quests)do value.availableQuests[q.id]=true;value.quests[q.id]={progress=0}end
 renderChecked(value,isNarrow);grouped(10)
 for _,q in ipairs(Config.Quests)do
  local b=buttons[q.id];check(b and b.text=='ACCEPT','Discovered quest cannot be accepted')
  check(b.card.labels[2]==q.description,'Discovered objective still has lock text or changed description')
  local old=#calls;b.call();check(#calls==old+1 and calls[#calls][1]=='AcceptQuest' and calls[#calls][2]==q.id,'Accept command changed')
 end
 value.activeQuest='garden';value.quests.garden.progress=1
 renderChecked(value,isNarrow);grouped(10)
 check(buttons.ActiveQuestAction and buttons.ActiveQuestAction.text=='ABANDON','Current active quest card missing')
 check(cards[1]==buttons.ActiveQuestAction.card,'Current active quest card no longer first')
 check(buttons.garden.text=='TRACKING','Active quest tracking state lost')
 buttons.garden.call();check(#calls==0,'Tracking quest can be reaccepted')
 buttons.ActiveQuestAction.call();check(#calls==1 and calls[1][1]=='AbandonQuest','Active quest abandon changed')
 for _,q in ipairs(Config.Quests)do value.quests[q.id]={progress=q.goal,claimed=q.id=='nick'}end
 renderChecked(value,isNarrow);grouped(10)
 for _,q in ipairs(Config.Quests)do
  local b=buttons[q.id];check(b~=nil,'Existing city quest removed')
  check(b.text==(q.id=='nick' and 'CLAIMED' or 'CLAIM'),'Existing completion state lost')
  local old=#calls;b.call()
  if q.id=='nick' then check(#calls==old,'Claimed city quest can replay reward')
  else check(#calls==old+1 and calls[#calls][1]=='ClaimQuest' and calls[#calls][2]==q.id,'Completed quest claim changed')end
 end
 -- Rejoined partial counters are visible but no active attempt is restored.
 local restartValue={level=20,quests={},availableQuests={}}
 for _,id in ipairs({'practice_beams','garden'})do
  local q=Config.GetQuest(id);restartValue.availableQuests[id]=true;restartValue.quests[id]={progress=q.goal-1,claimed=false}
 end
 restartValue.availableQuests.delivery=true;restartValue.quests.delivery={progress=0,claimed=false}
 renderChecked(restartValue,isNarrow)
 for _,id in ipairs({'practice_beams','garden'})do
  local b=buttons[id];check(b.text=='RESTART','Inactive partial quest misleading ACCEPT label')
  check(table.concat(b.card.labels,' | '):lower():find('reset',1,true),'Restart does not disclose progress reset')
  local old=#calls;b.call();check(#calls==old+1 and calls[#calls][1]=='AcceptQuest' and calls[#calls][2]==id,'Restart changed server command')
 end
 check(buttons.delivery.text=='ACCEPT','Zero progress falsely called restart')
 restartValue.availableQuests.garden=nil;renderChecked(restartValue,isNarrow)
 check(buttons.garden.text=='MEET NPC','Partial counter bypassed discovery');buttons.garden.call();check(#calls==0,'Locked partial sends action')
 restartValue.availableQuests.garden=true;restartValue.activeQuest='garden';renderChecked(restartValue,isNarrow)
 check(buttons.garden.text=='TRACKING','Active partial falsely called restart')
 restartValue.quests.garden.progress=3;renderChecked(restartValue,isNarrow);check(buttons.garden.text=='CLAIM','Completed partial falsely called restart')
 restartValue.quests.garden.claimed=true;renderChecked(restartValue,isNarrow);check(buttons.garden.text=='CLAIMED','Claimed partial falsely called restart')
 renderChecked(value,isNarrow)
 local old=#calls;buttons.ActiveQuestAction.call()
 check(#calls==old+1 and calls[#calls][1]=='ClaimQuest' and calls[#calls][2]=='garden','Active completed quest no longer claimable')
 check(value.combatChallenges.cover==4 and value.combatChallenges.elite==1,'Renderer mutated dormant counters')
end
print('PASS '..checks..' actual quest renderer/catalog assertions; synthetic UI only, no native text-fit claim')
"""

def run(code,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',encoding='utf-8',delete=False)as f:
  path=Path(f.name);f.write(code)
 try:
  r=subprocess.run(['luau',str(path)],capture_output=True,text=True,encoding='utf-8');out=r.stdout+r.stderr
  if expected:
   assert r.returncode and expected in out,out;print('PASS negative control:',expected)
  else:
   print(out,end='');assert r.returncode==0,out
 finally:path.unlink()
if __name__=='__main__':
 code=setup+config+between+fragment+checks
 if args.baseline:
  baseline="""end
local value={level=60,quests={},availableQuests={}}
render(value,false)
local garden=table.concat(buttons.garden.card.labels,' | ')
local beach=table.concat(buttons.beach.card.labels,' | ')
check(buttons.garden.card.labels[2]==buttons.beach.card.labels[2],'Baseline does not reproduce shared generic description')
check(garden:find(Config.GetQuest('garden').description,1,true) and beach:find(Config.GetQuest('beach').description,1,true),'Distinct undiscovered objectives missing')
"""
  run(setup+config+between+fragment+baseline,'Distinct undiscovered objectives missing')
 else:
  run(code)
  if args.negative_controls:
   run(code.replace('local function render(value,isNarrow)','table.insert(Config.Progression.Challenges,{id="cover",name="Destroy 5 eligible cover objects",goal=5})\nlocal function render(value,isNarrow)'),'Retired challenge displayed')
   run(code.replace('if q.hidden and not available then continue end','if false then continue end'),'Hidden city quest exposed before discovery')
   generic=code.replace('local description=q.description','local description=available and q.description or "Meet "..(q.giver or "a resident")')
   assert generic!=code
   run(generic,'Distinct undiscovered objectives missing')
   reversed_groups=code.replace('for _,group in ipairs(questGroups) do','for _,group in ipairs({questGroups[2],questGroups[1]}) do')
   assert reversed_groups!=code
   run(reversed_groups,'Combat quest group is not first')
   bypassed=code.replace('if available and not v.claimed and','if not v.claimed and')
   assert bypassed!=code
   run(bypassed,'Undiscovered quest action bypassed guard')
   menu=code.replace('q.menuAvailable==true or (data.availableQuests and data.availableQuests[q.id])','(data.availableQuests and data.availableQuests[q.id])')
   assert menu!=code
   run(menu,'Direct-available combat quest locked')
   claimed=code.replace('if available and not v.claimed and','if available and')
   assert claimed!=code
   run(claimed,'Claimed city quest can replay reward')
   restart_label=code.replace('or restarting and "RESTART" or "ACCEPT"','or "ACCEPT"')
   assert restart_label!=code
   run(restart_label,'Inactive partial quest misleading ACCEPT label')
   restart_warning=code.replace('Restarting resets this unfinished progress.','Restarting this task.')
   assert restart_warning!=code
   run(restart_warning,'Restart does not disclose progress reset')
