"""Bounded recovery/global scheduler tests; synthetic coroutines, no service/network calls."""
from pathlib import Path
import subprocess,sys
from voice_eligibility import run
import voice_stop_rate_limit as stop_harness
ROOT=Path(__file__).resolve().parents[1]
def read(path,baseline=False):
 return subprocess.check_output(['git','show','dbb459c:'+path],cwd=ROOT,text=True,encoding='utf-8') if baseline else (ROOT/path).read_text(encoding='utf-8')
def baseline():
 module=read('src/ServerScriptService/VoiceEligibility.luau',True)
 pure='local E=(function()\n'+module+'\nend)()\n'+r"""
local s=E.New(false);local t=E.Poll(s,0);E.Complete(s,t,1,true,true)
t=E.Poll(s,61);E.Complete(s,t,62,false,'error')
t=E.Poll(s,64);E.Complete(s,t,65,false,'error')
t=E.Poll(s,70);E.Complete(s,t,71,false,'error')
assert(E.Allowed(s,120.999) and not E.Allowed(s,121),'Historical expiry changed')
for _,now in ipairs({121,180,1000,100000})do assert(E.Poll(s,now)==nil,'Historical exhausted check recovered')end
print('BASELINE: 3 refresh errors leave eligibility unavailable indefinitely despite later service recovery')
"""
 server=read('src/ServerScriptService/Bootstrap.server.luau',True)
 code=stop_harness.assemble(server).split('local checks=0',1)[0]
 code=code.replace('local VoiceCombat={Cancel=function(v)cancels+=1;v.capture=nil end}','local VoiceCombat=Combat')
 code=code.replace('local function sustainedContext(p,s,t)', 'local function canCapture()return true end\nlocal function sustainedContext(p,s,t)')
 code+=r"""
local p={UserId=1,SetAttribute=function()end};local s={voice=Combat.New(),micReady=true,nextAction=100};sessions[p]=s
 dispatch(p,'BeginCast',1)
for i=1,29 do dispatch(p,'Unknown')end
now=.1;dispatch(p,'CancelCast',nil)
assert(s.voice.capture~=nil,'Historical saturated cancellation now succeeds')
assert(Combat.Release(s.voice,.3,1,1,true),'Historical canceled capture cannot release')
print('BASELINE: legacy capture survives 30-request quota plus CancelCast; release remains accepted at .3s')
"""
 for source in [pure,code]:
  result=run(source);print(result.stdout+result.stderr,end='');assert result.returncode==0

def scheduler(mutation=None):
 b=read('src/ServerScriptService/Bootstrap.server.luau')
 if mutation:b=mutation(b)
 section=b[b.index('local voiceRequestBudget='):b.index('Commerce.Start(')]
 return SCHED_SETUP+section+SCHED_CHECKS
SCHED_SETUP=r"""
local VoiceEligibility=require('../src/ServerScriptService/VoiceEligibility')
local now=0;local os={clock=function()return now end};local closing=false;local sessions={}
local calls,starts,workers={}, {}, {};local live=0;local maximumLive=0;local states=0
local function state()states+=1 end
local function cancelSustained(_,s)s.sustained.protocol.active=nil end
local VoiceCombat={Cancel=function(v)v.capture=nil end}
local VoiceChatService={IsVoiceEnabledForUserIdAsync=function(_,id)
 live+=1;maximumLive=math.max(maximumLive,live)
 table.insert(starts,{id=id,at=now});calls[id]=coroutine.running()
 local answer=coroutine.yield()
 live-=1;calls[id]=nil
 if answer=='error' then error('simulated API failure')end
 return answer
end}
local task={spawn=function(f,...)
 local co=coroutine.create(f);table.insert(workers,co)
 local ok,err=coroutine.resume(co,...);assert(ok,err)
end}
local function complete(id,answer)
 local co=calls[id];assert(co,'No suspended call')
 local ok,err=coroutine.resume(co,answer);assert(ok,err)
end
local function join(id,at)
 local p={UserId=id,Parent=true,SetAttribute=function()end}
 local s={voice={},voiceEligibility=VoiceEligibility.New(false,at or now,id)};sessions[p]=s
 return p,s
end
"""
SCHED_CHECKS=r"""
local n=0;local function check(v,m)assert(v,m);n+=1 end
local roster={}
for id=12,1,-1 do roster[id]=join(id,0)end
for i=0,7 do
 now=i*.25;dispatchVoiceEligibility(now)
 check(#starts==i+1 and starts[#starts].id==i+1,'Oldest due/UserId order incorrect')
 dispatchVoiceEligibility(now);dispatchVoiceEligibility(now+.249)
 check(#starts==i+1,'Global start interval exceeded')
end
check(live==8 and maximumLive==8 and #workers==8,'Eight actual-call bound failed')
for i=1,100 do now=2+i;dispatchVoiceEligibility(now)end
check(live==8 and #starts==8 and #workers==8,'Hung calls released slots or queued workers')
-- Departed users still occupy engine-call slots until actual return.
local departed=roster[1];departed.Parent=nil;sessions[departed]=nil
now=103;dispatchVoiceEligibility(now);check(#starts==8,'Departure released hung slot prematurely')
local replacement,newSession=join(1,now)
complete(1,true);check(live==7 and voiceRequestBudget.inFlight==7,'Actual return failed to release one slot')
check(not VoiceEligibility.Allowed(newSession.voiceEligibility,now),'Old departed result authorized rejoin')
dispatchVoiceEligibility(now);check(starts[#starts].id==9,'New join jumped older waiting users')
now=103.25;complete(2,'error');dispatchVoiceEligibility(now);check(starts[#starts].id==10,'Error completion broke oldest-due fairness')
now=103.5;complete(3,false);dispatchVoiceEligibility(now);check(starts[#starts].id==11,'Denied completion broke fairness')
now=103.75;complete(4,true);dispatchVoiceEligibility(now);check(starts[#starts].id==12,'Late positive retried ahead of queued players')
check(not VoiceEligibility.Allowed(sessions[roster[4]].voiceEligibility,now),'Late positive bypassed deadline')
-- Same Player object changes session during API yield; old identity must not adopt it.
local old=sessions[roster[5]];local replacement5={voice={},voiceEligibility=VoiceEligibility.New(false,104,5)}
sessions[roster[5]]=replacement5;VoiceEligibility.Poll(replacement5.voiceEligibility,104)
now=104;complete(5,true)
check(not VoiceEligibility.Allowed(replacement5.voiceEligibility,now),'Old request authorized replacement session')
check(old.voiceEligibility.pending~=nil,'Old session retained reference was completed after replacement')
-- Deadline expiry cancels attacks but does not release physical API slots.
local p=roster[9];local s=sessions[p];s.voice.capture={};s.sustained={protocol={active={}}}
now=112;stepVoiceEligibility(p,s,now)
check(s.voice.capture==nil and not s.sustained.protocol.active,'Timed out account check retained attack')
check(voiceRequestBudget.inFlight==live,'Deadline cancellation released engine slot')
-- After engine calls finish, the cap/interval remain stable under recovery traffic.
for _,id in ipairs({6,7,8,9,10,11,12})do if calls[id]then complete(id,'error')end end
check(live==0 and voiceRequestBudget.inFlight==0,'Completed calls leaked global slots')
for step=1,800 do
 now=112+step*.05;dispatchVoiceEligibility(now)
 if step%10==0 then
  local ids={};for id in pairs(calls)do table.insert(ids,id)end
  for _,id in ipairs(ids)do complete(id,'error')end
 end
 check(live<=8 and voiceRequestBudget.inFlight==live,'Recovery storm exceeded live-call bound')
end
for i=2,#starts do check(starts[i].at-starts[i-1].at>=.25-1e-8,'Recovery storm violated global pacing')end
check(maximumLive<=8,'Global concurrency exceeded eight')
-- Closed server does not schedule another worker.
closing=true;local count=#workers;now+=1000;dispatchVoiceEligibility(now);check(#workers==count,'Shutdown scheduled API worker')
-- Scheduler task delayed before entering engine must skip an already-expired request.
closing=false;sessions={};voiceRequestBudget.nextStart=0
local deferred
local normalSpawn=task.spawn;task.spawn=function(f,...)deferred={fn=f,args=table.pack(...)}end
now+=1;local waitingPlayer,waitingSession=join(99,now);local beforeStarts=#starts
dispatchVoiceEligibility(now);check(deferred~=nil and voiceRequestBudget.inFlight==1,'Delayed worker did not reserve exactly one slot')
now+=8
local co=coroutine.create(deferred.fn);local ok,err=coroutine.resume(co,table.unpack(deferred.args,1,deferred.args.n));check(ok,tostring(err))
check(#starts==beforeStarts and live==0 and voiceRequestBudget.inFlight==0,'Expired scheduled worker called API or leaked slot')
check(not VoiceEligibility.Allowed(waitingSession.voiceEligibility,now),'Expired scheduled worker authorized account')
task.spawn=normalSpawn
print('PASS',n,'actual coroutine API scheduler assertions; no live Roblox calls')
"""
RECOVERY=r"""
local E=require('../src/ServerScriptService/VoiceEligibility')
local n=0;local function check(v,m)assert(v,m);n+=1 end
local s=E.New(false,10,14);local now=10
check(E.DueAt(s)==10 and E.New(false,10,14).identity~=s.identity,'Arrival time or unique session identity wrong')
local function fail()
 local token=E.Poll(s,now);check(token~=nil,'Due recovery did not issue token')
 now+=.1;E.Complete(s,token,now,false,'error')
end
for burst=1,5 do
 fail();check(math.abs(E.DueAt(s)-(now+2))<1e-8,'First short backoff changed');now=E.DueAt(s)
 fail();check(math.abs(E.DueAt(s)-(now+5))<1e-8,'Second short backoff changed');now=E.DueAt(s)
 fail();local delay=math.min(120,30*2^(burst-1))+3
 check(math.abs(E.DueAt(s)-(now+delay))<1e-8,'Capped exponential recovery+jitter incorrect')
 check(not E.Allowed(s,now) and E.Poll(s,E.DueAt(s)-.001)==nil,'Backoff admitted or retried early')
 now=E.DueAt(s)
end
local token=E.Poll(s,now);E.Complete(s,token,now+.1,true,true);now+=.1
check(E.Allowed(s,now) and E.DueAt(s)==now+60,'Recovery success did not restore eligibility')
now=E.DueAt(s);fail();now=E.DueAt(s);fail();now=E.DueAt(s);fail()
check(math.abs(E.DueAt(s)-(now+33))<1e-8,'Success failed to reset error bursts')
local expires=now -- explicit separate cache expiry case follows
s=E.New(false,0,14);token=E.Poll(s,0);E.Complete(s,token,1,true,false)
check(E.DueAt(s)==124 and not E.Allowed(s,123.999),'Denied recheck delay/jitter wrong')
token=E.Poll(s,124);E.Complete(s,token,124.1,true,true)
check(E.Allowed(s,124.1),'Periodic denied recheck failed recovery')
s=E.New(false,0,0);token=E.Poll(s,0);E.Complete(s,token,1,true,true)
now=61;fail();now=E.DueAt(s);fail();now=E.DueAt(s);fail()
check(E.Allowed(s,120.999) and not E.Allowed(s,121),'Error retries extended old positive cache')
local waiting=E.New(false,0,0);E.MarkWaiting(waiting,0)
check(E.Status(waiting,7.999)=='checking' and E.Status(waiting,8)=='unavailable','Global budget wait has no bounded status')
check(not E.Allowed(waiting,100),'Waiting status granted access')
print('PASS',n,'bounded recovery/backoff/jitter assertions')
"""
def cancel_cases(mutation=None):
 b=read('src/ServerScriptService/Bootstrap.server.luau')
 if mutation:b=mutation(b)
 code=stop_harness.assemble(b).split('local checks=0',1)[0]
 code=code.replace('local VoiceCombat={Cancel=function(v)cancels+=1;v.capture=nil end}','local VoiceCombat={Begin=Combat.Begin,Cancel=function(v)cancels+=1;Combat.Cancel(v)end}')
 code=code.replace('local function sustainedContext(p,s,t)', 'local function canCapture()return true end\nlocal function sustainedContext(p,s,t)')
 return code+r"""
local n=0;local function check(v,m)assert(v,m);n+=1 end
local function fresh(automatic)
 now=0;cancels=0;attributes=0
 local p={UserId=1,SetAttribute=function()attributes+=1 end};local s={voice=Combat.New(),micReady=true,nextAction=100,sustained=automatic and sustained.New() or nil};sessions[p]=s
 if not automatic then dispatch(p,'BeginCast',1)else s.requestCount=1 end
 for i=1,29 do dispatch(p,'Unknown')end
 return p,s
end
local p,s=fresh(false);now=.1;dispatch(p,'CancelCast',nil)
check(s.voice.capture==nil and not Combat.Release(s.voice,.3,1,1,true),'Saturated CancelCast left usable legacy capture')
local old=cancels;local writes=attributes
for i=1,1000 do dispatch(p,'CancelCast',nil)end
check(cancels==old and attributes==writes,'Idle legacy cancels amplified output')
for _,arg in ipairs({false,true,0,'cancel',{}})do p,s=fresh(false);dispatch(p,'CancelCast',arg);check(s.voice.capture~=nil,'Malformed cancellation bypassed quota')end
p,s=fresh(true);s.voice.capture={};dispatch(p,'CancelCast',nil)
check(s.voice.capture~=nil and cancels==0,'Automatic mode legacy cancellation bypassed quota')
p,s=fresh(false);s.requestCount=0;dispatch(p,'CancelCast',nil);check(s.voice.capture==nil,'Ordinary legacy cancellation regressed')
print('PASS',n,'actual Action legacy cancellation assertions')
"""
if __name__=='__main__':
 if '--baseline' in sys.argv:baseline();sys.exit(0)
 for code in [RECOVERY,scheduler(),cancel_cases()]:
  r=run(code);print(r.stdout+r.stderr,end='');assert r.returncode==0

 if '--negative-controls' in sys.argv:
  for name,old,new,expected in [
   ('pre-call deadline',' and now<eligibility.pending.deadline','','Expired scheduled worker called API'),
   ('global cap','voiceRequestBudget.inFlight>=VoiceEligibility.MaxConcurrent','false','Hung calls released slots'),
   ('global pacing','voiceRequestBudget.nextStart=now+VoiceEligibility.StartInterval','voiceRequestBudget.nextStart=now','Global start interval exceeded'),
   ('oldest due fairness','due<dueAt','due>dueAt','New join jumped older waiting users'),
   ('tie fairness','p.UserId<chosen.UserId','p.UserId>chosen.UserId','Oldest due/UserId order incorrect'),
   ('session identity fence','if closing or not p.Parent or not s or s.voiceEligibility.identity~=identity then return end','if not s then return end','Old request authorized replacement session')]:
   def mutate(b):
    assert old in b,name
    return b.replace(old,new,1)
   r=run(scheduler(mutate));out=r.stdout+r.stderr
   assert r.returncode and expected in out,out
   print('PASS negative control:',name)
  for name,old,new,expected in [
   ('legacy cancel safety bypass','elseif verb=="CancelCast" and not s.sustained and arg==nil then','elseif false then','Saturated CancelCast left usable'),
   ('legacy cancel shape','and not s.sustained and arg==nil then','and not s.sustained then','Malformed cancellation bypassed'),
   ('legacy cancel idempotency','if s.voice.capture then VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0) end','VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0)','Idle legacy cancels amplified')]:
   def mutate(b):
    assert old in b,name
    return b.replace(old,new,1)
   def mutate(b):
    start=b.index('action.OnServerEvent:Connect(function')
    assert old in b[start:],name
    return b[:start]+b[start:].replace(old,new,1)
   r=run(cancel_cases(mutate));out=r.stdout+r.stderr
   assert r.returncode and expected in out,out
   print('PASS negative control:',name)
  module=read('src/ServerScriptService/VoiceEligibility.luau')
  for name,old,new,expected in [
   ('recovery cap','math.min(Eligibility.RecoveryMax,Eligibility.RecoveryBase*2^(s.bursts-1))','Eligibility.RecoveryBase*2^s.bursts','Capped exponential recovery+jitter incorrect'),
   ('successful recovery reset','s.attempts=0;s.bursts=0;s.failed=nil','s.attempts=0;s.failed=nil','Success failed to reset error bursts'),
   ('denied periodic recheck','now+Eligibility.DeniedRetry+s.jitter','math.huge','Denied recheck delay/jitter wrong')]:
   assert old in module,name
   code=RECOVERY.replace("require('../src/ServerScriptService/VoiceEligibility')",'(function()\n'+module.replace(old,new,1)+'\nend)()',1)
   r=run(code);out=r.stdout+r.stderr
   assert r.returncode and expected in out,out
   print('PASS negative control:',name)
 b=read('src/ServerScriptService/Bootstrap.server.luau')
 request=b[b.index('local function runVoiceRequest('):b.index('local function dispatchVoiceEligibility(')]
 assert 'task.spawn(runVoiceRequest,chosen,eligibility.identity,token)' in b
 assert request.index('local s=sessions[p]')>request.index('pcall(VoiceChatService.IsVoiceEnabledForUserIdAsync')
 assert 'function runVoiceRequest(p,identity,token)' in request
 print('PASS 3 source contracts: worker arguments and no session/profile local retained over API yield')
