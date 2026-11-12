"""Actual ambience script with deterministic services; no native playback or loading evidence."""
from pathlib import Path
import subprocess,tempfile,sys
R=Path(__file__).resolve().parents[1]
A='src/StarterPlayer/StarterPlayerScripts/Ambience.client.luau'
L='src/ReplicatedStorage/Shared/CompactLayout.luau'
SETUP=r'''
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local V={};V.__index=function(t,k)if k=='Magnitude' then return math.sqrt(t.X*t.X+t.Y*t.Y+t.Z*t.Z)end;return V[k]end
local Vector3={new=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},V)end};Vector3.one=Vector3.new(1,1,1)
V.__sub=function(a,b)return Vector3.new(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
local Color3={fromRGB=function(r,g,b)return {R=r,G=g,B=b}end}
local Layout=(function()
'''
HARNESS=r'''
end)()
local function scenario(compact,pauseAt,loadFailures)
 local nodes,jobs,connections={}, {}, {};local syncs=0;local loads=0;local delays={}
 local function signal()local s={};function s:Connect(f)local c={Connected=true,fn=f};function c:Disconnect()self.Connected=false end;table.insert(connections,c);self.c=c;return c end;return s end
 local destruction=signal();local heartbeat=signal();local state=signal()
 local workspace={};local script={Destroying=destruction}
 local Instance={new=function(class)local n={ClassName=class,IsLoaded=false,attributes={}};function n:SetAttribute(k,v)self.attributes[k]=v end;function n:Destroy()self.dead=true end;function n:Play()self.plays=(self.plays or 0)+1 end;table.insert(nodes,n);return n end}
 local Enum={RollOffMode={InverseTapered='tapered'}}
 local config={CompactCity=compact,CityLayout=Layout}
 local dependencyCalls=0
 local token={};local function require(t)dependencyCalls+=1;check(t==token,'Unexpected import');if pauseAt=='require' then coroutine.yield()end;return config end
 local shared={WaitForChild=function(_,name)dependencyCalls+=1;check(name=='Config','Unexpected shared child');if pauseAt=='Config' then coroutine.yield()end;return token end}
 local action={FireServer=function(_,verb)check(verb=='Sync','Unexpected action');syncs+=1 end}
 local remotes={WaitForChild=function(_,name)if pauseAt==name then coroutine.yield()end;return name=='State' and {OnClientEvent=state} or action end}
 local replicated={WaitForChild=function(_,name)if pauseAt==name then coroutine.yield()end;if name=='Shared' then return shared end;check(name=='ScreamRemotes','Unexpected replica child');return remotes end}
 local bot={position=Vector3.new(-300,3,125),active=true,working=true,health=100,inside=true}
 function bot:GetAttribute(k)if k=='Role' then return 'Busker' elseif k=='Working' then return self.working elseif k=='ResidentActive' then return self.active end end
 function bot:IsDescendantOf(w)return self.inside end
 function bot:FindFirstChild()return {Position=self.position}end
 function bot:FindFirstChildOfClass()return {Health=self.health}end
 local services={CollectionService={GetTagged=function()return {bot}end},RunService={Heartbeat=heartbeat},SoundService={},ReplicatedStorage=replicated,ContentProvider={PreloadAsync=function(_,items)loads+=1;if pauseAt=='Preload' then coroutine.yield()end;if loads>(loadFailures or 0)then items[1].IsLoaded=true end end}}
 local game={GetService=function(_,name)return assert(services[name],name)end}
 local task={spawn=function(f)table.insert(jobs,f)end,wait=function(n)table.insert(delays,n)end}
 local function start()
'''
TAIL=r'''
 end
 local co=coroutine.create(start);local ok,err=coroutine.resume(co);assert(ok,err)
 local function destroy()check(destruction.c~=nil,'Missing early startup teardown');destruction.c.fn()end
 return {nodes=nodes,jobs=jobs,heartbeat=heartbeat,state=state,bot=bot,co=co,destroy=destroy,counts=function()return syncs,loads,delays end,connections=connections,dependencies=function()return dependencyCalls end}
end
local function sounds(f)local surf={};local guitar;for _,n in ipairs(f.nodes)do if n.ClassName=='Sound' then if n.Name=='CoastalSurf' then table.insert(surf,n)else guitar=n end end end;return surf,guitar end
for _,compact in ipairs({true,false})do
 local f=scenario(compact);check(coroutine.status(f.co)=='dead','Startup hung')
 local surf,guitar=sounds(f);check(#surf==4 and guitar~=nil,'Emitter cardinality')
 for i,sound in ipairs(surf)do
  local expected=compact and Layout.Ambience.surfPositions[i] or Vector3.new((i-1)*360-540,1,590)
  check((sound.Parent.Position-expected).Magnitude==0,'Surf position wrong')
  check(sound.SoundId=='rbxassetid://9119677305' and sound.Volume==.16 and sound.RollOffMinDistance==45 and sound.RollOffMaxDistance==230 and sound.RollOffMode=='tapered' and sound.Looped,'Surf mix changed')
 end
 local expected=compact and Layout.Ambience.buskerPosition or Vector3.new(150,5,426)
 check((guitar.Parent.Position-expected).Magnitude==0,'Guitar position wrong')
 check(guitar.SoundId=='rbxassetid://15675051846' and guitar.Volume==0 and guitar.RollOffMinDistance==8 and guitar.RollOffMaxDistance==70,'Guitar mix changed')
 f.bot.position=expected;f.heartbeat.c.fn(.5);check(guitar.Volume==.2,'Working busker silent')
 for _,field in ipairs({'active','working','inside','health'})do local old=f.bot[field];f.bot[field]=field=='health' and 0 or false;f.heartbeat.c.fn(.5);check(guitar.Volume==0,'Inactive busker audible');f.bot[field]=old end
 f.bot.position=expected+Vector3.new(36,0,0);f.heartbeat.c.fn(.5);check(guitar.Volume==0,'Distant busker audible')
 for _,job in ipairs(f.jobs)do job()end
 local _,loads=f.counts();check(loads==2,'Shared assets loaded more than once')
 for _,sound in ipairs(surf)do check(sound.plays==1,'Surf not played once')end;check(guitar.plays==1,'Guitar not started')
 f.state.c.fn({settings={volume=.25}});check(guitar.SoundGroup.Volume==.25,'Settings ignored')
 f.destroy();local volume=guitar.SoundGroup.Volume;local gain=guitar.Volume;f.state.c.fn({settings={volume=.9}});f.bot.position=expected;f.heartbeat.c.fn(.5);check(guitar.SoundGroup.Volume==volume and guitar.Volume==gain,'Retained callbacks changed destroyed audio');check(guitar.SoundGroup.dead and guitar.Parent.Parent.dead and not f.heartbeat.c.Connected and not f.state.c.Connected,'Cleanup missing')
end
for _,at in ipairs({'Shared','Config','require','ScreamRemotes','State','Action'})do
 local f=scenario(true,at);check(coroutine.status(f.co)=='suspended','Missing simulated yield '..at)
 f.destroy();local before=#f.nodes;local dependencies=f.dependencies();local ok,err=coroutine.resume(f.co);assert(ok,err)
 check(#f.nodes==before,'Allocated after teardown '..at)
 check(f.dependencies()==dependencies,'Continued dependencies after teardown '..at)
 local syncs=f.counts();check(syncs==0,'Sync after teardown '..at)
 for _,job in ipairs(f.jobs)do job()end;local _,loads=f.counts();check(loads==0,'Load after teardown '..at)
end
local pending=scenario(true,'Preload');local job=coroutine.create(pending.jobs[1]);assert(coroutine.resume(job));pending.destroy();assert(coroutine.resume(job))
for _,node in ipairs(pending.nodes)do if node.ClassName=='Sound' then check(not node.plays,'Pending load played after destruction')end end
local f=scenario(true,nil,100);for _,job in ipairs(f.jobs)do job()end
local _,loads,delays=f.counts();check(loads==6 and #delays==4,'Retry bound changed')
local surf=sounds(f);check(not surf[1].plays,'Failed asset played')
for x=-350,350,10 do local nearest=math.huge;for _,pos in ipairs(Layout.Ambience.surfPositions)do nearest=math.min(nearest,(pos-Vector3.new(x,3,260)).Magnitude)end;check(nearest<230,'Compact beach outside surf range')end
print('PASS '..checks..' actual ambience construction/lifecycle and geometric assertions; mocked services only')
'''
# Arithmetic metamethod added separately to keep source mock explicit.
SETUP=SETUP.replace('local Color3=', 'V.__add=function(a,b)return Vector3.new(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end\nlocal Color3=')
def run(a,l,tail=TAIL):
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(SETUP+l+HARNESS+a+tail);p=Path(f.name)
 try:return subprocess.run(['luau',str(p)],capture_output=True,text=True,timeout=20)
 finally:p.unlink()
BASE='435aeba7eed36924708df3bc2c2584fc85f10763'
if __name__=='__main__':
 a=(R/A).read_text();l=(R/L).read_text()
 if '--baseline' in sys.argv:
  a=subprocess.check_output(['git','show',BASE+':'+A],cwd=R).decode()
  probe=TAIL[:TAIL.index('for _,compact in ipairs')]+r"""
local f=scenario(true);local surf,guitar=sounds(f)
local minimum=math.huge;for _,sound in ipairs(surf)do minimum=math.min(minimum,sound.Parent.Position.Z-Layout.BoundsMax.Z)end
check(minimum==290 and minimum>surf[1].RollOffMaxDistance,'Historical surf mismatch not reproduced')
f.heartbeat.c.fn(.5);check(guitar.Volume==0 and (f.bot.position-guitar.Parent.Position).Magnitude>35,'Historical working busker mismatch not reproduced')
print('PASS historical actual constructor/heartbeat: all compact bounds beyond surf range; working busker silent')
"""
  r=run(a,l,probe);assert r.returncode==0,r.stderr;print(r.stdout,end='')
 else:
  r=run(a,l);print(r.stdout,end='');assert r.returncode==0,r.stderr
  if '--negative-controls' in sys.argv:
   controls=[('Config.CompactCity and Config.CityLayout.Ambience.surfPositions','false and Config.CityLayout.Ambience.surfPositions','Surf position wrong'),('Config.CompactCity and Config.CityLayout.Ambience.buskerPosition','false and Config.CityLayout.Ambience.buskerPosition','Guitar position wrong'),('local shared=replicated:WaitForChild("Shared");if destroyed then return end','local shared=replicated:WaitForChild("Shared")','Continued dependencies after teardown Shared'),('local configModule=shared:WaitForChild("Config");if destroyed then return end','local configModule=shared:WaitForChild("Config")','Continued dependencies after teardown Config'),('local Config=require(configModule);if destroyed then return end','local Config=require(configModule)','Allocated after teardown require'),('   if destroyed then return end\n   if representative.IsLoaded then','   if representative.IsLoaded then','Pending load played after destruction'),('for attempt=1,3 do','for attempt=1,4 do','Retry bound changed'),('model:GetAttribute("Working") and root','true and root','Inactive busker audible')]
   for old,new,error in controls:
    assert a.count(old)==1,old
    r=run(a.replace(old,new),l);assert r.returncode and error in r.stderr,r.stdout+r.stderr
   print('PASS '+str(len(controls))+' negative controls')
