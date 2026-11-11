"""Actual quest renderer/catalog with synthetic UI; not a native layout assertion."""
from pathlib import Path
import argparse,re,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
client=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text(encoding='utf-8')
config=(root/'src/ReplicatedStorage/Shared/Config.luau').read_text(encoding='utf-8')
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
local messages,buttons,calls={},{},{}
local function info(text)table.insert(messages,text)end
local function card()return {}end
local function label(_,text)table.insert(messages,text)end
local function button(_,id,text,_,_,fn)buttons[id]={text=text,call=fn}end
local action={FireServer=function(_,verb,id)table.insert(calls,{verb,id})end}
local function render(value,isNarrow)
 data=value;narrow=isNarrow;messages={};buttons={};calls={}
"""
checks="""
end
for _,isNarrow in ipairs({false,true})do
 local value={level=60,training='Elite',combatChallenges={fighters=2,cover=4,elite=1},quests={},availableQuests={}}
 render(value,isNarrow)
 local text=table.concat(messages,' | ')
 check(not text:find('Destroy 5',1,true) and not text:find('Help defeat 2',1,true),'Retired challenge displayed')
 local _,count=text:gsub('XP on completion','')
 check(count==1 and text:find('2/3',1,true),'Active training challenge missing or duplicated')
 check(text:find('Breaking objects is not a quest.',1,true)~=nil,'Quest help still implies destruction task')
 check(text:find('no more than 20 levels above',1,true)~=nil,'Training help invents lower-level exclusion')
 check(not buttons.nick,'Hidden city quest exposed before discovery')
 for _,q in ipairs(Config.Quests)do
  value.availableQuests[q.id]=true;value.quests[q.id]={progress=q.goal,claimed=q.id=='nick'}
 end
 value.activeQuest='garden';render(value,isNarrow)
 local count=0;for _,q in ipairs(Config.Quests)do
  count+=1;check(buttons[q.id]~=nil,'Existing city quest removed')
  check(buttons[q.id].text==(q.id=='nick' and 'CLAIMED' or 'CLAIM'),'Existing completion state lost')
 end
 check(count==8,'City quest definitions unexpectedly changed')
 buttons.nick.call();check(#calls==0,'Claimed city quest can replay reward')
 buttons.ActiveQuestAction.call();check(#calls==1 and calls[1][1]=='ClaimQuest' and calls[1][2]=='garden','Active completed quest no longer claimable')
 check(value.combatChallenges.cover==4 and value.combatChallenges.elite==1,'Renderer mutated dormant counters')
end
print('PASS '..checks..' actual quest renderer/catalog assertions; synthetic UI only')
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
 parser=argparse.ArgumentParser();parser.add_argument('--negative-controls',action='store_true');args=parser.parse_args()
 code=setup+config+between+fragment+checks
 run(code)
 if args.negative_controls:
  run(code.replace('local function render(value,isNarrow)','table.insert(Config.Progression.Challenges,{id="cover",name="Destroy 5 eligible cover objects",goal=5})\nlocal function render(value,isNarrow)'),'Retired challenge displayed')
  run(code.replace('if q.hidden and not available then continue end','if false then continue end'),'Hidden city quest exposed before discovery')
