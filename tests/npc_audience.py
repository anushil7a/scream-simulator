"""Actual audience behavior with mocked residents/time; no native animation evidence."""
from pathlib import Path
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
s = (root/'src/ServerScriptService/World.luau').read_text()
a = s.index('function World.WatchPerformance(bot)')
b = s.index('local function socialize(bot)', a)
setup = '''
local now=0;local os={clock=function()return now end}
local World={Bots={}};local removeDuringWait
local task={wait=function(dt)now+=dt;if removeDuringWait then removeDuringWait.model.Parent=nil;removeDuringWait=nil end end}
local rng={NextNumber=function()return 5 end}
local RaycastParams={new=function()return {}end};local Enum={RaycastFilterType={Exclude=1}}
local workspace={Raycast=function()return nil end}
local function stopWalking(bot)bot.pathVersion=(bot.pathVersion or 0)+1 end
local function faceToward()end
local position=setmetatable({},{__sub=function()return {Magnitude=10}end})
local function resident()
 local attrs={};return {alive=true,root={Parent=true,Position=position},model={Parent=true,SetAttribute=function(_,k,v)attrs[k]=v end},attrs=attrs}
end
'''
checks = '''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local function pair()
 now=0;local listener,performer=resident(),resident()
 performer.role='Busker';performer.job={};performer.working=true
 World.Bots={listener,performer};return listener,performer
end
local listener,performer=pair();performer.model.Parent=nil
check(not World.WatchPerformance(listener),'Removed performer accepted an audience')
listener,performer=pair();performer.root.Parent=nil
check(not World.WatchPerformance(listener),'Detached performer root accepted an audience')
listener,performer=pair();listener.model.Parent=nil
check(not World.WatchPerformance(listener),'Removed listener joined a performance')
listener,performer=pair();removeDuringWait=performer
check(World.WatchPerformance(listener) and now<.5,'Listener waited out a removed performance')
check(listener.watchingPerformer==nil and listener.watchingUntil==nil and listener.attrs.Applauding==false,'Removed performance retained audience state')
listener,performer=pair()
check(World.WatchPerformance(listener) and now>=5,'Healthy performance ended prematurely')
check(listener.attrs.Applauding==false and listener.attrs.Activity=='Exploring the neighborhood','Completed performance failed activity cleanup')
print('PASS '..checks..' audience lifecycle checks with mocked residents/time')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.audience_',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(setup+s[a:b]+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
