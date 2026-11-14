"""Actual NPC greeting logic with mocked activity and visibility; no raycast evidence."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/World.luau').read_text();a=s.index('local function noticePlayers(');b=s.index('function World.ReactToScream',a)
setup='''
local os={clock=function()return 20 end}
local distance=10;local position=setmetatable({}, {__sub=function()return {Magnitude=distance}end})
local root={Position=position};local character={FindFirstChild=function()return root end}
local game={GetService=function()return {GetPlayers=function()return {{Character=character}}end}end}
local reachable=true;local rays=0
local InteractionRules={CanReachNpc=function()rays+=1;return reachable end}
local calls=0;local World={Speak=function()calls+=1 end}
local faceToward=function()end;local rng={NextInteger=function()return 1 end}
'''
checks='''
local count=0;local function check(v,msg)assert(v,msg);count+=1 end
local function bot()return {alive=true,model={},root={Position=position}}end
local b=bot();noticePlayers(b)
check(calls==1 and b.lastGreeting==20,'Visible idle resident failed to greet')
noticePlayers(b);check(calls==1,'Greeting cooldown bypassed')
for _,field in ipairs({'working','restSeat','watchingPerformer','socialUntil','reactionUntil'})do
 b=bot();b[field]=(field=='socialUntil' or field=='reactionUntil') and 21 or true
 local before=calls;local beforeRays=rays;noticePlayers(b)
 check(calls==before and rays==beforeRays,'Busy resident greeted: '..field)
end
b=bot();b.alive=false;local before=calls;noticePlayers(b);check(calls==before,'Inactive resident greeted')
b=bot();reachable=false;noticePlayers(b);check(calls==before and b.lastGreeting==nil,'Wall blocked visibility but not greeting')
reachable=true;distance=17;local beforeRays=rays;noticePlayers(bot());check(calls==before and rays==beforeRays,'Far greeting performed visibility work')
print('PASS '..count..' actual NPC greeting checks with mocked activity/visibility')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.greeting_',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+s[a:b]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
