"""Actual reward branch with mocked XP/state callbacks; no save or network evidence."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=s.index(' elseif verb=="ClaimQuest" then')+len(' elseif verb=="ClaimQuest" then')
b=s.index(' elseif verb=="SetSettings"',a)
setup='''
local p={};local earned=0;local stops=0;local messages=0;local reenter
local definitions={garden={id='garden',goal=3,coins=40,xp=100},nick={id='nick',goal=1,coins=200,xp=500}}
local Config={GetQuest=function(id)return definitions[id]end}
local s={activeQuest='garden',data={coins=10,achievements={},quests={garden={progress=2,claimed=false}}}}
local function xp(_,amount)earned+=amount;if reenter then local fn=reenter;reenter=nil;fn() end end
local function state()messages+=1 end
local function stopQuest()stops+=1;s.activeQuest=nil end
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
for _,arg in ipairs({'missing',{},'nick','garden'})do claim(p,s,arg) end
check(s.data.coins==10 and earned==0 and stops==0 and messages==0,'Invalid/missing/incomplete quest granted reward')
s.data.quests.garden.progress=3
reenter=function()claim(p,s,'garden')end
claim(p,s,'garden')
check(s.data.coins==50 and earned==100 and s.data.quests.garden.claimed,'Completed quest failed or reentrant callback duplicated reward')
check(stops==1 and s.activeQuest==nil and messages==1,'Active completion did not clean up exactly once')
claim(p,s,'garden')
check(s.data.coins==50 and earned==100 and stops==1 and messages==1,'Repeated claim duplicated rewards or cleanup')
s.activeQuest='delivery';s.carrying=true;s.questDeadline=90
s.data.quests.nick={progress=1,claimed=false}
claim(p,s,'nick')
check(s.data.achievements.NickChampion==true and s.data.coins==250 and earned==600,'Nick reward/achievement missing')
check(s.activeQuest=='delivery' and s.carrying and s.questDeadline==90 and stops==1,'Claiming older earned reward erased current quest')
claim(p,s,'nick')
check(s.data.coins==250 and earned==600 and messages==2,'Nick reward was repeatable')
check(s.data.quests.garden.progress==3 and s.data.quests.nick.progress==1,'Claim erased earned progress')
print('PASS '..checks..' actual quest claim checks with mocked callbacks')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(setup+'\nlocal function claim(p,s,arg)\n'+s[a:b]+'\nend\n'+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
