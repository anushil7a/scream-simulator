"""Actual sustained PvP hit branch with fake players/health; no geometry/network evidence."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=s.index('  if target.player then',s.index('local dealt=0'))
b=s.index('  elseif target.object then',a)
setup='''
local Config={HealQuietSeconds=10,PlayerKOXP=function(level)return level*7 end}
local rewards,ejections,quests=0,0,0
local function xp(_,amount)rewards+=amount end
local function eject(_,h)ejections+=1;h.Health=h.MaxHealth end
local function questProgress(_,event)assert(event=='Underdog');quests+=1 end
local function hitPlayer(s,target,damage,now,level)
 local dealt=0;local hit={damage=damage};local intent={level=level};local p={}
'''
checks='''
 end
 return dealt
end
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local s={koRewards={},data={coins=0}}
local h={Health=10,MaxHealth=100}
local target={player={UserId=2},humanoid=h,session={data={level=20}}}
check(hitPlayer(s,target,4,100,10)==4 and h.Health==6,'Nonlethal applied damage incorrect')
check(target.session.nextHeal==110 and rewards==0 and s.data.coins==0,'Nonlethal reward/healing state incorrect')
check(hitPlayer(s,target,9,101,10)==6 and h.Health==100 and ejections==1,'KO feedback exceeded remaining health or recovery failed')
check(rewards==140 and s.data.coins==20 and quests==1 and s.koRewards[2]==131,'KO reward/cooldown/underdog incorrect')
h.Health=1;hitPlayer(s,target,2,130.9,10)
check(ejections==2 and rewards==140 and s.data.coins==20 and quests==1,'Repeated opponent paid before cooldown')
check(s.koRewards[2]==131,'Rejected repeat extended reward cooldown')
h.Health=1;hitPlayer(s,target,2,131,30)
check(rewards==280 and s.data.coins==40 and quests==1,'Cooldown boundary or higher-attacker underdog rule incorrect')
target.player={UserId=3};target.session.data.level=50;h.Health=1
hitPlayer(s,target,2,132,50)
check(rewards==630 and s.data.coins==60 and quests==2,'Different/equal-level opponent reward was suppressed')
check(s.koRewards[2]==161 and s.koRewards[3]==162,'Opponent cooldowns were not independent')
print('PASS '..checks..' actual PvP reward branch checks with mocked players/health')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+s[a:b]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
