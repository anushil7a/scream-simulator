"""Actual ambience remote hookup with synthetic yielding waits; no audio/device test."""
from pathlib import Path
import subprocess
import sys
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/Ambience.client.luau').read_text()
startup=s[:s.index('local assets={}')]
heartbeat=s[s.index('local performing=false'):s.index('local connection\n')]
s=s[s.index('local remotes=game:GetService("ReplicatedStorage")'):]
setup='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local destroyed=false;local connection;local group={Volume=.55};local sends=0;local connects=0;local pauseAt
local event={Connect=function(_,fn)connects+=1;local c={fn=fn,connected=true};function c:Disconnect()self.connected=false end;return c end}
local action={FireServer=function(_,verb)assert(verb=='Sync');sends+=1 end}
local remotes={WaitForChild=function(_,name)if pauseAt==name then coroutine.yield()end;return name=='State' and {OnClientEvent=event} or action end}
local replicated={WaitForChild=function(_,name)if pauseAt==name then coroutine.yield()end;return remotes end}
local game={GetService=function()return replicated end}
'''
checks='''
for _,stage in ipairs({'ScreamRemotes','State','Action'})do
 destroyed=false;connection=nil;pauseAt=stage;local before=sends
 local thread=coroutine.create(start);assert(coroutine.resume(thread))
 destroyed=true;if connection then connection:Disconnect()end
 assert(coroutine.resume(thread))
 check(sends==before,'Late startup sent sync after teardown at '..stage)
 check(not connection or not connection.connected,'Late startup retained subscription at '..stage)
end
destroyed=false;connection=nil;pauseAt=nil;start()
check(sends==1 and connection.connected,'Normal startup did not subscribe/sync')
connection.fn({settings={volume=.25}});check(group.Volume==.25,'Valid city volume ignored')
connection.fn({settings={volume=0/0}});check(group.Volume==.25,'Invalid volume changed group')
destroyed=true;connection.fn({settings={volume=.9}})
check(group.Volume==.25,'Queued state callback changed destroyed sound group')
print('PASS '..checks..' actual ambience startup checks with mocked waits')
'''
activity_setup="""
destroyed=false
local step
local Run={Heartbeat={Connect=function(_,fn)step=fn;return {}end}}
local stage={};local workspace={}
local position=setmetatable({},{__sub=function()return {Magnitude=5}end})
local bot={active=true,inside=true,working=true,health=100}
function bot:GetAttribute(key)if key=='Role' then return 'Busker' elseif key=='Working' then return self.working elseif key=='ResidentActive' then return self.active end end
function bot:IsDescendantOf()return self.inside end
function bot:FindFirstChild()return {Position=position}end
function bot:FindFirstChildOfClass()return {Health=self.health}end
local Collection={GetTagged=function()return {bot}end}
local guitar={Volume=0}
"""
activity_checks="""
step(.5);check(guitar.Volume==.2,'Active busker did not perform')
bot.active=false;step(.5);check(guitar.Volume==0,'Inactive busker kept performing')
bot.active=true;bot.inside=false;step(.5);check(guitar.Volume==0,'Removed busker kept performing')
bot.inside=true;step(.5);check(guitar.Volume==.2,'Returned active busker failed to resume')
destroyed=true;bot.working=false;step(.5);check(guitar.Volume==.2,'Queued heartbeat changed destroyed audio')
print('PASS '..checks..' total mocked ambience startup/activity checks; no audio playback evidence')
"""
world_setup="""
local config, reached
local script={Destroying={Connect=function()end}}
local dependency={WaitForChild=function(self)return self end}
local game={GetService=function()return dependency end}
local function require()return config end
local function start()
"""
world_checks="""
 reached=true
end
config={}
start()
assert(reached,'City ambience never reached emitter setup')
reached=false
config={ResonanceLayout={}}
start()
assert(not reached,'Hall reached City ambience emitter setup')
print('PASS City-only ambience startup')
"""

def run(fragment, error=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
  path=Path(f.name)
  f.write(fragment)
 try:
  result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True)
 finally:
  path.unlink()
 if error:
  assert result.returncode and error in result.stderr,result.stderr
  print('PASS negative control:',error)
 else:
  assert result.returncode==0,result.stderr
  print(result.stdout,end='')

run(setup+'local function start()\n'+s+'\nend\n'+checks+activity_setup+heartbeat+activity_checks)
run(world_setup+startup+world_checks)
if '--negative-controls' in sys.argv:
 guard=' or Config.ResonanceLayout'
 assert guard in startup
 run(world_setup+startup.replace(guard,'',1)+world_checks,'Hall reached City ambience emitter setup')
