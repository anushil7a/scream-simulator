"""Actual ambience remote hookup with synthetic yielding waits; no audio/device test."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/Ambience.client.luau').read_text()
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
print('PASS '..checks..' actual ambience startup checks with mocked waits')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(setup+'local function start()\n'+s+'\nend\n'+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
