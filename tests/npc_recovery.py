"""Actual NPC recovery/reset helpers with fake delayed callbacks; no engine timing."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text();a=s.index('local function restoreBot(');b=s.index('local function destructionHint(',a)
setup='''
local queue={};local task={delay=function(seconds,fn)assert(seconds==8);table.insert(queue,fn)end}
local Config={BotMaxHealth=60,BotRespawnSeconds=8}
local updates=0;local World={UpdateBot=function()updates+=1 end}
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local bot={model={Parent=true},health=0,alive=true}
knockOutBot(bot);check(not bot.alive and #queue==1,'KO failed to schedule recovery')
knockOutBot(bot);check(#queue==1,'Duplicate KO scheduled a second recovery')
queue[1]();check(bot.alive and bot.health==60 and updates==1,'Current recovery failed')
queue[1]();check(updates==1,'Callback replay restored twice')
bot.health=0;knockOutBot(bot);local old=queue[2]
restoreBot(bot);bot.health=25;old()
check(bot.health==25 and bot.alive and updates==2,'Old recovery healed reset bot')
bot.health=0;knockOutBot(bot);local current=queue[3]
old();check(not bot.alive and bot.health==0,'Old recovery revived later KO early')
current();check(bot.alive and bot.health==60 and updates==3,'Later KO lost its own recovery')
bot.health=0;knockOutBot(bot);bot.model.Parent=nil;queue[4]()
check(not bot.alive and updates==3,'Removed bot revived')
restoreBot(bot);check(updates==3,'Reset touched removed bot')
print('PASS '..checks..' actual NPC recovery checks with mocked callbacks')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.npc_recovery_',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+s[a:b]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
