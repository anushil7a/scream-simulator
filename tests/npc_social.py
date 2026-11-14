"""Actual delayed resident reply with mocked activity generations/time."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/World.luau').read_text()
a=s.index('local function socialize(bot)');b=s.index('local function noticePlayers(',a)
setup='''
local now=0;local os={clock=function()return now end}
local pending;local task={delay=function(_,fn)pending=fn end}
local calls=0;local World={Bots={},Speak=function()calls+=1 end}
local InteractionRules={CanReachNpc=function()return true end}
local function stopWalking(bot)bot.pathVersion+=1 end
local function faceToward()end
local roleLines={Local={'hello'}};local rng={NextInteger=function()return 1 end}
'''
checks='''
local function schedule(bot,friend)
 World.Bots={bot,friend};assert(socialize(bot));calls=0
end
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local position=setmetatable({},{__sub=function()return {Magnitude=10} end})
local function resident()return {alive=true,model={Parent=true},root={Position=position},pathVersion=1,socialUntil=-1,role='Local'} end
local bot,friend=resident(),resident();schedule(bot,friend);now=1.8;pending()
check(calls==1,'Uninterrupted resident reply missing')
for _,scenario in ipairs({'speaker moved','listener moved','speaker talking','listener talking','speaker KO','listener KO','speaker removed','listener removed','expired'})do
 now=0;calls=0;bot=resident();friend=resident();schedule(bot,friend)
 if scenario=='speaker moved' then bot.pathVersion+=1
 elseif scenario=='listener moved' then friend.pathVersion+=1
 elseif scenario=='speaker talking' then bot.talkingTo={}
 elseif scenario=='listener talking' then friend.talkingTo={}
 elseif scenario=='speaker KO' then bot.alive=false
 elseif scenario=='listener KO' then friend.alive=false
 elseif scenario=='speaker removed' then bot.model.Parent=nil
 elseif scenario=='listener removed' then friend.model.Parent=nil end
 now=scenario=='expired' and 8 or 1.8;pending()
 check(calls==0,'Stale social reply survived '..scenario)
end
now=20;calls=0;bot=resident();friend=resident();bot.talkingTo={};friend.talkingTo={}
schedule(bot,friend)
check(bot.talkingTo==nil and friend.talkingTo==nil,'Expired player references survived ambient conversation')
now=21.8;pending();check(calls==1,'Expired dialogue suppressed new resident reply')
now=0;bot=resident();friend=resident();World.Bots={bot,friend}
local owner={};bot.talkingTo=owner;bot.socialUntil=20
check(not socialize(bot) and bot.talkingTo==owner,'Active player conversation was stolen')
bot.socialUntil=-1;friend.talkingTo=owner;friend.socialUntil=20
check(not socialize(bot) and friend.talkingTo==owner,'Active listener conversation was stolen')
print('PASS '..checks..' actual resident conversation checks with mocked activity/time')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.social_',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+s[a:b]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
