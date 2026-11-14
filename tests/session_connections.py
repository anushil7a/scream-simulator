"""Actual join/leave/shutdown signal ownership using retained mock Players.
Models callback reference edges only; not native Roblox memory/GC validation.
"""
from pathlib import Path
import subprocess,tempfile,sys
ROOT=Path(__file__).resolve().parents[1]
def read(baseline=False):
 path='src/ServerScriptService/Bootstrap.server.luau'
 return subprocess.check_output(['git','show','7ae5149:'+path],cwd=ROOT,text=True,encoding='utf-8') if baseline else (ROOT/path).read_text(encoding='utf-8')
def build(baseline=False,mutation=None):
 b=read(baseline)
 if mutation:b=mutation(b)
 joined=b[b.index('local function joined(p)'):b.index('local function joinTracked(p)')]
 leaving=b[b.index('local function leaving(p)'):b.index('Players.PlayerRemoving:Connect(',b.index('local function leaving(p)'))]
 shutdown=b[b.index('local function shutdown()'):b.index('game:BindToClose(shutdown)')]
 helper=''
 if 'local function disconnectSessionSignals(' in b:helper=b[b.index('local function disconnectSessionSignals('):b.index('local function beamColor(')]
 return SETUP+helper+joined+leaving+shutdown+(BASELINE if baseline else CHECKS)
SETUP=r"""
local now=0;local os={clock=function()return now end};local closing=false;local joinsInFlight=0;local departuresInFlight=0
local sessions={};local localFixture=false;local sustainedEnabled=false;local stateCalls=0;local cancels=0;local protects=0
local saveHook;local saves=0;local workers={};local disconnects=0
local task={spawn=function(f,...)
 local co=coroutine.create(f);local ok,err=coroutine.resume(co,...);assert(ok,err)
 if coroutine.status(co)~='dead' then table.insert(workers,co)end
end,wait=function(t)coroutine.yield(t)end}
local Profiles={Default=function()return {level=1}end,Load=function()return {level=1},true end,Save=function(...)
 saves+=1;if saveHook then saveHook(...)end;return true
end}
local Entitlements={Refresh=function()end};local Commerce={Load=function()end}
local VoiceCombat={New=function()return {}end,Cancel=function(v)v.capture=nil end}
local VoiceEligibility={New=function()return {}end}
local Config={HealQuietSeconds=12,SprintDuration=4,HealthForLevel=function()return 100 end}
local function state()stateCalls+=1 end
local function closeConversation()end
local function cancelSustained()cancels+=1 end
local function protect()protects+=1 end
local function stepVoiceEligibility()end;local function dispatchVoiceEligibility()end
local function warn()end
local function signal()
 local sig={callbacks={}}
 function sig:Connect(fn)
  local con={Connected=true}
  self.callbacks[con]=fn
  function con:Disconnect()
   if self.Connected then self.Connected=false;sig.callbacks[self]=nil;disconnects+=1 end
  end
  return con
 end
 function sig:Fire(...)
  local copy=table.clone(self.callbacks)
  for con,fn in pairs(copy)do if con.Connected then fn(...)end end
 end
 function sig:Count()local n=0;for _ in pairs(self.callbacks)do n+=1 end;return n end
 return sig
end
local function player(id)return {UserId=id,Parent=true,CharacterAdded=signal(),CharacterRemoving=signal(),SetAttribute=function()end}end
local function character(waitHook)
 local h={Health=100,MaxHealth=100,JumpPower=50,JumpHeight=7.2}
 return {humanoid=h,WaitForChild=function()if waitHook then waitHook()end;return h end}
end
local n=0;local function check(v,m)assert(v,m);n+=1 end
local function edges(p)return p.CharacterAdded:Count()+p.CharacterRemoving:Count()end
local function resume(co)local ok,value=coroutine.resume(co);assert(ok,value);return value end
"""
BASELINE=r"""
local retained=player(1);joined(retained);check(edges(retained)==2,'Join did not register both callbacks')
leaving(retained);check(sessions[retained]==nil and edges(retained)==2,'Historical leave no longer retains callbacks')
local second=player(2);joined(second);shutdown()
check(sessions[second]==nil and edges(second)==2,'Historical shutdown no longer retains callbacks')
print('BASELINE: retained mock Player keeps two session-closing signal callbacks after actual leave and shutdown; no native leak claim')
"""
CHECKS=r"""
local p=player(1);joined(p);local first=sessions[p]
check(edges(p)==2 and first.characterAddedConnection and first.characterRemovingConnection,'Join did not own exactly two connections')
local oldAdded=next(p.CharacterAdded.callbacks);local oldAddedFn=p.CharacterAdded.callbacks[oldAdded]
local oldRemoved=next(p.CharacterRemoving.callbacks);local oldRemovedFn=p.CharacterRemoving.callbacks[oldRemoved]
local c=character();p.Character=c;p.CharacterAdded:Fire(c)
check(first.character==c and protects==1 and c.humanoid.WalkSpeed==16,'Unready character spawn movement initialization changed')
first.micReady=true;p.CharacterRemoving:Fire(c)
check(first.character==nil and cancels==1,'Normal removal failed to cancel old character')
local c2=character();p.Character=c2;p.CharacterAdded:Fire(c2)
check(first.character==c2 and protects==2 and c2.humanoid.WalkSpeed==16,'Normal respawn readiness/initialization changed')
-- Callback already executing may yield before disconnection; original post-wait fence must protect replacement.
local delayedCharacter=character(function()coroutine.yield('humanoid')end);p.Character=delayedCharacter
local delayed=coroutine.create(function()oldAddedFn(delayedCharacter)end)
check(resume(delayed)=='humanoid','Spawn callback did not pause in actual WaitForChild')
local atSave;local leaveClean=false
saveHook=function()
 leaveClean=edges(p)==0 and first.characterAddedConnection==nil and first.characterRemovingConnection==nil
 check(sessions[p]==nil,'Leave saved before detaching gameplay')
 atSave=disconnects;coroutine.yield('save')
end
local departure=coroutine.create(function()leaving(p)end)
check(resume(departure)=='save','Actual leave save did not yield')
check(leaveClean and edges(p)==0 and disconnects==2,'Leave save yielded with retained signal callbacks')
disconnectSessionSignals(first);leaving(p)
check(disconnects==2,'Duplicate cleanup disconnected more than once')
-- Retained Player can acquire a new session while old save completion is pending.
p.Character=nil;saveHook=nil;joined(p);local replacement=sessions[p]
check(replacement~=first and edges(p)==2,'Replacement session registration failed')
local untouched=stateCalls;local protected=protects;local canceled=cancels
resume(delayed);oldAddedFn(c2);oldRemovedFn(c2)
check(replacement.character==nil and stateCalls==untouched and protects==protected and cancels==canceled,'Stale callback changed replacement session')
resume(departure)
check(sessions[p]==replacement and edges(p)==2 and disconnects==atSave,'Old save completion disconnected replacement handlers')
-- Cleanup tolerates partially registered/empty session state.
local partial={characterAddedConnection=p.CharacterAdded:Connect(function()end)}
check(edges(p)==3,'Partial registration fixture failed');disconnectSessionSignals(partial);disconnectSessionSignals(partial)
check(edges(p)==2 and partial.characterAddedConnection==nil,'Partial cleanup damaged live handlers')
disconnectSessionSignals({})
-- Every session is disconnected and detached before ANY shutdown save begins.
local q=player(2);joined(q);local r=player(3);joined(r);sessions[r].canSave=false
local tracked={p,q,r};local before=disconnects;local saveCount=0;local shutdownClean=true
saveHook=function()
 saveCount+=1
 for _,actor in ipairs(tracked)do shutdownClean=shutdownClean and edges(actor)==0 and sessions[actor]==nil end
 coroutine.yield('shutdown-save')
end
local stopping=coroutine.create(shutdown)
check(resume(stopping)==.1,'Shutdown did not wait for delayed saves')
check(shutdownClean,'Shutdown began a save before all signal cleanup')
check(disconnects==before+6 and saveCount==2,'Shutdown disconnect/save count wrong')
for _,co in ipairs(workers)do if coroutine.status(co)~='dead' then resume(co)end end
resume(stopping);check(coroutine.status(stopping)=='dead','Shutdown failed to complete after saves')
for _,actor in ipairs(tracked)do check(edges(actor)==0,'Retained Player still owns session signal edge')end
local done=disconnects;shutdown();check(disconnects==done,'Repeated shutdown cleanup not idempotent')
print('PASS',n,'actual session signal lifecycle assertions; mock reference graph, not native GC')
"""
def run(code):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False)as f:f.write(code);path=Path(f.name)
 try:return subprocess.run(['luau',str(path)],cwd=ROOT,text=True,capture_output=True,encoding='utf-8')
 finally:path.unlink()
if __name__=='__main__':
 r=run(build('--baseline' in sys.argv));print(r.stdout+r.stderr,end='')
 if r.returncode:sys.exit(r.returncode)
 if '--negative-controls' in sys.argv:
  for name,mutation,expected in [
   ('leave cleanup',lambda b:b.replace(' disconnectSessionSignals(s)\n cancelSustained',' -- removed cleanup\n cancelSustained',1),'Leave save yielded with retained'),
   ('CharacterAdded disconnect',lambda b:b.replace('added:Disconnect()','do end',1),'Leave save yielded with retained'),
   ('CharacterRemoving disconnect',lambda b:b.replace('removing:Disconnect()','do end',1),'Leave save yielded with retained'),
   ('post-yield spawn fence',lambda b:b.replace(' or sessions[p]~=s or p.Character~=c or s.character==c',' or s.character==c',1),'Stale callback changed replacement'),
   ('shutdown cleanup',lambda b:b[:b.index('local function shutdown()')]+b[b.index('local function shutdown()'):].replace('disconnectSessionSignals(s)','',1),'Shutdown began a save before all signal cleanup')]:
   original=read();mutant=mutation(original);assert mutant!=original,name
   r=run(build(mutation=mutation));out=r.stdout+r.stderr
   assert r.returncode and expected in out,out
   print('PASS negative control:',name)
