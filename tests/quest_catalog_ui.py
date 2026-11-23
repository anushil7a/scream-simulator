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
local routes,menuCloses={},0
local function closeMenu()menuCloses+=1 end
local hasGardens=Config.CompactCity==true
local academy={
 guideMenu=function()end,
 NavigationCatalog={Resolve=function(kind,id,value)
  if hasGardens and kind=="place" and id=="gardens" then return {} end
  if kind=="quest" then return value.questNavigation and value.questNavigation[id] end
 end},
 selectGuide=function(kind,id)table.insert(routes,{kind,id})end,
}
local data,narrow;local title,subtitle={},{};local gui={AbsoluteSize={X=390}};local gold,muted={},{}
MENU_CONTENT_WIDTH
local messages,buttons,calls,cards,order={},{},{},{},{}
local function info(text)table.insert(messages,text);table.insert(order,{kind="info",text=text})end
local function card()local c={labels={}};table.insert(cards,c);table.insert(order,{kind="card",card=c});return c end
local function label(c,text)table.insert(messages,text);table.insert(c.labels,text);return {}end
local function button(c,id,text,size,pos,fn)buttons[id]={text=text,call=fn,card=c,height=size.Y,pos=pos};c.button=id;return {}end
local action={FireServer=function(_,verb,id)table.insert(calls,{verb,id})end}
local function render(value,isNarrow)
 data=value;narrow=isNarrow;gui.AbsoluteSize.X=isNarrow and 390 or 1280;messages={};buttons={};calls={};cards={};order={}
"""
if not args.baseline:
    start=client.index('function academy.menuContentWidth(')
    between=between.replace('MENU_CONTENT_WIDTH',client[start:client.index('\nlocal function info(',start)])
else:
    between=between.replace('MENU_CONTENT_WIDTH','')
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
if Config.HasGardenPvp() then
 check(Config.GetQuest('beach').description:find('lower Garden terraces',1,true)~=nil,'Beach quest hid the Garden route warning')
 for _,id in ipairs({'dodge','arena','arena_assist'})do
  check(Config.GetQuest(id).description:find('a PvP zone',1,true)~=nil,'PvP task still says arena only')
 end
end
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
 grouped(8)
 for _,q in ipairs(Config.Quests)do if not q.retired and not q.hidden and q.menuAvailable~=true then
  local b=buttons[q.id];local cardText=table.concat(b.card.labels,' | ')
  check(cardText:find(q.description,1,true) and cardText:find('To unlock:',1,true) and cardText:find(q.giver,1,true),'Locked card lacks objective or discovery instructions')
  local starter=hasGardens and (q.id=='garden' or q.id=='beach')
  local before,closed=#routes,menuCloses
  check(b.text==(starter and 'GUIDE TO MAR' or 'MEET NPC'),'Wrong undiscovered quest action')
  b.call()
  check(#calls==0,'Undiscovered quest action bypassed guard')
  if starter then
   check(b.height==44,'Mar guide is undersized for touch')
   check(#routes==before+1 and routes[#routes][1]=='mar' and routes[#routes][2]=='gardens' and menuCloses==closed+1,'Mar guide failed to select Mar and close menu')
  else
   check(#routes==before and menuCloses==closed,'Other locked quest routed to Mar')
  end
 end end
 for _,id in ipairs({'arena_assist'})do
  local b=buttons[id];check(b and b.text=='ACCEPT','Direct-available combat quest locked')
  check(not table.concat(b.card.labels,' | '):find('To unlock:',1,true),'Direct quest shows nonexistent giver lock')
  local before=#calls;b.call();check(#calls==before+1 and calls[#calls][1]=='AcceptQuest' and calls[#calls][2]==id,'Direct quest acceptance missing')
 end
 calls={}
 -- Even a stale completed progress packet must not bypass discovery.
 for _,q in ipairs(Config.Quests)do value.quests[q.id]={progress=q.goal}end
 renderChecked(value,isNarrow);check(not buttons.nick,'Hidden quest exposed by progress alone')
 if buttons.ReadyQuestAction then
  buttons.ReadyQuestAction.call()
  local promoted=Config.GetQuest(calls[1][2])
  check(promoted.retired or promoted.menuAvailable,'Stale progress promoted an undiscovered reward')
  calls={}
 end
 for _,q in ipairs(Config.Quests)do if not q.retired and not q.hidden and q.menuAvailable~=true then buttons[q.id].call();check(#calls==0,'Locked completed quest bypassed discovery')end end
 -- Discovery reveals every original quest, preserving acceptance and hiding unlock instructions.
 for _,q in ipairs(Config.Quests)do value.availableQuests[q.id]=true;value.quests[q.id]={progress=0}end
 renderChecked(value,isNarrow);grouped(9)
 for _,q in ipairs(Config.Quests)do if not q.retired then
  local b=buttons[q.id];check(b and b.text=='ACCEPT','Discovered quest cannot be accepted')
  check(b.card.labels[2]==q.description,'Discovered objective still has lock text or changed description')
  local old=#calls;b.call();check(#calls==old+1 and calls[#calls][1]=='AcceptQuest' and calls[#calls][2]==q.id,'Accept command changed')
 end end
 value.questNavigation={beach={label='Talk to Mar Soler'}}
 academy.menuQuestFocus='beach'
 renderChecked(value,isNarrow)
 check(buttons.beach.card.LayoutOrder==-1,'Focused quest stayed below unrelated cards')
 check(buttons.garden.card.LayoutOrder~=-1,'Unexpected quest also promoted')
 check(buttons.Guide_beach==nil,'Gear-focused inactive Beach offered a return trip to Mar')
 check(buttons.beach.text=='ACCEPT' and buttons.beach.height==44,'Gear-focused acceptance lost its 44-pixel target')
 if isNarrow then check(buttons.beach.pos[4]<=10,'Gear-focused acceptance starts below the compact card header') end
 buttons.beach.call()
 check(#calls==1 and calls[1][1]=='AcceptQuest' and calls[1][2]=='beach','Gear-focused acceptance sent the wrong action')
 value.activeQuest='beach';value.questNavigation.beach.label='Hold to pick up bottle'
 renderChecked(value,isNarrow)
 check(buttons.Guide_beach~=nil,'Focused Beach did not show its guide after acceptance')
 if isNarrow then
  check(buttons.Guide_beach.pos[4]<=10 and buttons.Guide_beach.height==44,'Focused active guide fell below the compact card header')
  check(not buttons.beach,'Compact guide kept a redundant Active control')
 end
 local routesBefore=#routes;buttons.Guide_beach.call()
 check(#routes==routesBefore+1 and routes[#routes][1]=='quest' and routes[#routes][2]=='beach','Active focused Beach guide selected the wrong route')
 academy.menuQuestFocus=nil;value.activeQuest=nil;value.questNavigation.beach.label='Talk to Mar Soler'
 renderChecked(value,isNarrow)
 check(buttons.beach.card.LayoutOrder~=-1,'Ordinary menu retained quest focus')
 check(buttons.Guide_beach~=nil,'Ordinary quest menu lost its separate giver guide')
 value.questNavigation=nil
 value.activeQuest='garden';value.quests.garden.progress=1
 renderChecked(value,isNarrow);grouped(9)
 check(buttons.ActiveQuestAction and buttons.ActiveQuestAction.text=='ABANDON','Current active quest card missing')
 check(cards[1]==buttons.ActiveQuestAction.card,'Current active quest card no longer first')
 check(buttons.garden.text=='ACTIVE','Active quest tracking state lost')
 local beach=buttons.beach
 check(beach.text=='SWITCH','Unfinished active task offered silent acceptance')
 check(table.concat(beach.card.labels,' '):find(Config.GetQuest('garden').name,1,true),'Switch warning omitted the active task name')
 check(table.concat(beach.card.labels,' '):find('Unfinished progress resets.',1,true),'Switch warning omitted progress loss')
 beach.call()
 check(#calls==1 and calls[1][1]=='AcceptQuest' and calls[1][2]=='beach','Switch sent the wrong server action')
 local alternate=copy(value);alternate.quests.beach={progress=1}
 renderChecked(alternate,isNarrow)
 local both=table.concat(buttons.beach.card.labels,' ')
 check(buttons.beach.text=='SWITCH' and both:find('Restarting resets this unfinished progress.',1,true) and both:find('Unfinished progress resets.',1,true),'Switch hid destination restart or current task reset')
 alternate.quests.beach={progress=Config.GetQuest('beach').goal}
 renderChecked(alternate,isNarrow)
 check(buttons.beach.text=='CLAIM' and not table.concat(buttons.beach.card.labels,' '):find('Unfinished progress resets.',1,true),'Claim was presented as a destructive task switch')
 alternate.quests.garden={progress=Config.GetQuest('garden').goal}
 alternate.quests.beach={progress=0}
 renderChecked(alternate,isNarrow)
 check(buttons.beach.text=='ACCEPT' and not table.concat(buttons.beach.card.labels,' '):find('Unfinished progress resets.',1,true),'Claimable active reward was presented as progress at risk')
 renderChecked(value,isNarrow)
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
 check(not buttons.practice_beams,'Retired partial quest offers restart')
 for _,id in ipairs({'garden'})do
  local b=buttons[id];check(b.text=='RESTART','Inactive partial quest misleading ACCEPT label')
  check(table.concat(b.card.labels,' | '):lower():find('reset',1,true),'Restart does not disclose progress reset')
  local old=#calls;b.call();check(#calls==old+1 and calls[#calls][1]=='AcceptQuest' and calls[#calls][2]==id,'Restart changed server command')
 end
 check(buttons.delivery.text=='ACCEPT','Zero progress falsely called restart')
 restartValue.availableQuests.garden=nil;renderChecked(restartValue,isNarrow)
 check(buttons.garden.text==(hasGardens and 'GUIDE TO MAR' or 'MEET NPC'),'Partial counter bypassed discovery');buttons.garden.call();check(#calls==0,'Locked partial sends action')
 local supported=hasGardens;hasGardens=false;renderChecked(restartValue,isNarrow)
 local routeCount=#routes
 check(buttons.garden.text=='MEET NPC','Missing route still offered guide')
 buttons.garden.call();check(#routes==routeCount and #calls==0,'Missing route unexpectedly activated')
 hasGardens=supported
 restartValue.availableQuests.garden=true;restartValue.activeQuest='garden';renderChecked(restartValue,isNarrow)
 check(buttons.garden.text=='ACTIVE','Active partial falsely called restart')
 restartValue.quests.garden.progress=3;renderChecked(restartValue,isNarrow);check(buttons.garden.text=='CLAIM','Completed partial falsely called restart')
 restartValue.quests.garden.claimed=true;renderChecked(restartValue,isNarrow);check(buttons.garden.text=='CLAIMED','Claimed partial falsely called restart')
 renderChecked(value,isNarrow)
 check(order[1].card==buttons.ActiveQuestAction.card,'Ready reward does not render first')
 check(buttons.ActiveQuestAction.height==44,'Ready reward tap target is shorter than 44 pixels')
 if academy.menuContentWidth then
  academy.sidebarMenu=true
  academy.menuQuestFocus=value.activeQuest
  renderChecked(value,isNarrow)
  check(buttons[value.activeQuest].card.LayoutOrder~=-1,'Compact quest focus pushed the matching reward below the fold')
  academy.sidebarMenu=false
  academy.menuQuestFocus=nil
  renderChecked(value,isNarrow)
 end
 local claimPos=buttons.ActiveQuestAction.pos
 check(claimPos[3]==0 and claimPos[4]+buttons.ActiveQuestAction.height<=45,'Claim target clips in the shortest tested reward window')
 local readyQuest=Config.GetQuest('garden')
 local baseReward=string.format("%d coins · %d XP (base)",readyQuest.coins,readyQuest.xp)
 check(table.find(buttons.ActiveQuestAction.card.labels,baseReward),'Quick claim hides the available base reward')
 local old=#calls;buttons.ActiveQuestAction.call()
 check(#calls==old+1 and calls[#calls][1]=='ClaimQuest' and calls[#calls][2]=='garden','Active completed quest no longer claimable')
 local inactive=copy(value);inactive.activeQuest=nil;inactive.quests={garden=copy(value.quests.garden)}
 renderChecked(inactive,isNarrow)
 check(order[1].card==buttons.ReadyQuestAction.card,'Inactive ready reward does not render first')
 check(table.find(buttons.ReadyQuestAction.card.labels,baseReward),'Inactive quick claim hides the available base reward')
 local capped=copy(inactive);capped.level=Config.MaxLevel
 renderChecked(capped,isNarrow)
 check(table.find(buttons.ReadyQuestAction.card.labels,readyQuest.coins.." coins (base)"),'Max-level quick claim advertises XP')
 renderChecked(inactive,isNarrow)
 buttons.ReadyQuestAction.call()
 check(#calls==1 and calls[1][1]=='ClaimQuest' and calls[1][2]=='garden','Inactive ready shortcut sends wrong claim')
 inactive.quests.garden.claimed=true;renderChecked(inactive,isNarrow)
 check(not buttons.ReadyQuestAction,'Already claimed reward was promoted')
 check(value.combatChallenges.cover==4 and value.combatChallenges.elite==1,'Renderer mutated dormant counters')
 -- Retired data remains durable but only an earned, unclaimed reward is actionable.
 for _,state in ipairs({{}, {progress=0}, {progress=1}, {progress=2}, {progress=3}, {progress=3,claimed=true}})do
  for _,discovered in ipairs({false,true})do
   for _,active in ipairs({false,true})do
    local retiredValue={level=20,quests={practice_beams=state.progress and copy(state) or nil},availableQuests={practice_beams=discovered},activeQuest=active and 'practice_beams' or nil}
    renderChecked(retiredValue,isNarrow)
    check(not buttons.ActiveQuestAction,'Retired active objective exposed')
    local earned=state.progress==3 and not state.claimed
    local b=buttons.practice_beams
    check((b~=nil)==earned,'Retired card visibility violates earned-only rule')
    if earned then
     check(b.text=='CLAIM','Retired earned card is not claim-only')
     check(b.card.labels[2]=='Earned reward available.','Retired objective instructions resurfaced')
     b.call();check(#calls==1 and calls[1][1]=='ClaimQuest' and calls[1][2]=='practice_beams','Retired earned reward action changed')
    else check(#calls==0,'Hidden retired state emitted action') end
    local sequence=grouped(earned and 9 or 8)
    local wanted=earned and {'crowd','dodge','arena','practice_beams','arena_assist','garden','beach','delivery','sprint'} or {'crowd','dodge','arena','arena_assist','garden','beach','delivery','sprint'}
    check(equal(sequence,wanted),'Remaining catalog order changed')
   end
  end
 end

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
   unwarned=code.replace('lower Garden terraces on the way.','path on the way.')
   assert unwarned!=code
   run(unwarned,'Beach quest hid the Garden route warning')
   focus=code.replace('if q.id==academy.menuQuestFocus and not (academy.sidebarMenu and q==reward) then c.LayoutOrder=-1 end','')
   assert focus!=code
   run(focus,'Focused quest stayed below unrelated cards')
   run(code.replace('canGuide=not focusedStart and academy', 'canGuide=academy'),
       'Gear-focused inactive Beach offered a return trip to Mar')
   run(code.replace('(switching or focusedStart) and 44','switching and 44'),
       'Gear-focused acceptance lost its 44-pixel target')
   run(code.replace('local actionY=headerAction and 6 or narrow and rewardY+34 or 32',
                    'local actionY=narrow and rewardY+34 or 32'),
       'Gear-focused acceptance starts below the compact card header')
   run(code.replace('headerGuide and actionY or actionY+46','actionY+46'),
       'Focused active guide fell below the compact card header')
   run(code.replace(' and not (academy.sidebarMenu and q==reward)', ''),'Compact quest focus pushed the matching reward below the fold')
   run(code.replace('local function render(value,isNarrow)','table.insert(Config.Progression.Challenges,{id="cover",name="Destroy 5 eligible cover objects",goal=5})\nlocal function render(value,isNarrow)'),'Retired challenge displayed')
   run(code.replace('if q.hidden and not available then continue end','if false then continue end'),'Hidden city quest exposed before discovery')
   generic=code.replace('local description=q.retired==true and "Earned reward available." or q.description','local description=available and q.description or "Meet "..(q.giver or "a resident")')
   assert generic!=code
   run(generic,'Distinct undiscovered objectives missing')
   reversed_groups=code.replace('for _,group in ipairs(questGroups) do','for _,group in ipairs({questGroups[2],questGroups[1]}) do')
   assert reversed_groups!=code
   run(reversed_groups,'Combat quest group is not first')
   bypassed=code.replace('if available and not v.claimed and','if not v.claimed and')
   assert bypassed!=code
   run(bypassed,'Undiscovered quest action bypassed guard')
   run(code.replace('academy.selectGuide("mar","gardens");closeMenu();return','academy.selectGuide("place","gardens");closeMenu();return'),'Mar guide failed to select Mar and close menu')
   run(code.replace('guideToMar and 44 or 38','38'),'Mar guide is undersized for touch')
   menu=code.replace('q.menuAvailable==true or (data.availableQuests and data.availableQuests[q.id])','(data.availableQuests and data.availableQuests[q.id])')
   assert menu!=code
   run(menu,'Direct-available combat quest locked')
   claimed=code.replace('if available and not v.claimed and','if available and')
   assert claimed!=code
   run(claimed,'Claimed city quest can replay reward')
   switch_label=code.replace('or switching and "SWITCH"', '')
   assert switch_label!=code
   run(switch_label,'Unfinished active task offered silent acceptance')
   switch_warning=code.replace('Unfinished progress resets."', 'New task begins."')
   assert switch_warning!=code
   run(switch_warning,'Switch warning omitted progress loss')
   restart_label=code.replace('or restarting and "RESTART" or "ACCEPT"','or "ACCEPT"')
   assert restart_label!=code
   run(restart_label,'Inactive partial quest misleading ACCEPT label')
   restart_warning=code.replace('Restarting resets this unfinished progress.','Restarting this task.')
   assert restart_warning!=code
   run(restart_warning,'Restart does not disclose progress reset')

   hidden=code.replace('if q.retired==true and (v.claimed or v.progress<q.goal) then continue end','if false then continue end')
   assert hidden!=code
   run(hidden,'Visible quest count changed')
   earned=code.replace('local available=q.retired==true or','local available=')
   assert earned!=code
   run(earned,'Retired earned card is not claim-only')
   active=code.replace('if data.activeQuest and not (current and current.retired==true) and (not reward or current~=reward) then','if data.activeQuest and (not reward or current~=reward) then')
   assert active!=code
   run(active,'Retired active objective exposed')
   below=code.replace('  if reward then\n','  info("Before claim")\n  if reward then\n',1)
   assert below!=code
   run(below,'Ready reward does not render first')
   undiscovered=code.replace('local progress=available and data.quests[quest.id]','local progress=data.quests[quest.id]',1)
   assert undiscovered!=code
   run(undiscovered,'Stale progress promoted an undiscovered reward')
   missing=code.replace('label(c,payout,','label(c,"",',1)
   assert missing!=code
   run(missing,'Quick claim hides the available base reward')
   capped=code.replace('local payout=data.level>=Config.MaxLevel','local payout=false',1)
   assert capped!=code
   run(capped,'Max-level quick claim advertises XP')
   clipped=code.replace('UDim2.new(1,-130,0,1),function()','UDim2.new(1,-130,.5,-22),function()',1)
   assert clipped!=code
   run(clipped,'Claim target clips in the shortest tested reward window')
