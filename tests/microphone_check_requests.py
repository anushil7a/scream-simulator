"""Actual Microphone and actual Settings retry callback and scoped render guard; fake clock/API/audio only."""
from pathlib import Path
import argparse,ast,re,subprocess,tempfile
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');a=p.parse_args()
path='src/StarterPlayer/StarterPlayerScripts/Microphone.luau';s=(R/path).read_text()
client=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
callback=re.search(r'button\(accessCard,"RetryVoiceAccess".*?function\(\)\s*(.*?)\s*end\)',client,re.S).group(1)
wrapper_start=client.index(' local function button(parent,name,text,size,pos,callback,color)')
wrapper=client[wrapper_start:client.index(' clearShop()',wrapper_start)]
tree=ast.parse((R/'tests/microphone_lifecycle.py').read_text())
setup=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='setup' for t in n.targets))
setup=setup.replace('local pending={};local timeouts={};local deferCheck=false',"local pending={};local timeouts={};local deferCheck=false;local calls=0;local response='yield';local queued=false")
start=setup.index('local task=');end=setup.index('\nlocal disconnected=',start)
setup=setup[:start]+'local task={delay=function(_,fn)table.insert(timeouts,fn)end,spawn=function(fn)local co=coroutine.create(fn);table.insert(pending,co);if not queued then assert(coroutine.resume(co))end end}'+setup[end:]
setup=setup.replace('IsVoiceEnabledForUserIdAsync=function()return true end',"IsVoiceEnabledForUserIdAsync=function()calls+=1;local v=response;if v=='yield'then v=coroutine.yield()end;if v=='error'then error('offline')end;return v end")
endsetup=r'''
end
local Mic=loadMicrophone();local mic
local modal={Visible=true};local clientDestroyed=false;local revision=1;local renderRevision=1
local registered
local function makeButton(_,_,_,_,_,fn)registered=fn end
WRAPPER
button(nil,nil,nil,nil,nil,function() CALLBACK end)
local f={}
function f.start(v,q)response=v;if v==nil then response='yield'end;queued=q==true;mic=Mic.new();f.mic=mic end
function f.retry() mic:Check() end
function f.settings() registered() end
function f.panel(visible,destroyed)modal.Visible=visible;clientDestroyed=destroyed==true end
function f.at(t)now=t;mic:Step(.05)end
function f.finish(i,value)local ok,e=coroutine.resume(pending[i],value);assert(ok,e)end
function f.stats()return calls,#pending,#timeouts end
return f
end
'''.replace('CALLBACK',callback).replace('WRAPPER',wrapper)
checks=r'''
local f=fixture();f.start();local m=f.mic;local generation=m.generation
for i=1,120 do f.retry()end
local calls,jobs,delays=f.stats();check(calls==1 and jobs==1 and delays==0,'Retry storm allocated calls/jobs/timers')
check(m.generation==generation and m.checkPending,'Pending retry reset generation or released slot')
f.at(9.999);check(not string.find(m.status,'still pending',1,true),'Timeout fired early')
f.at(10);check(string.find(m.status,'still pending',1,true) and string.find(m.status,'rejoin',1,true),'Timeout omitted honest pending/rejoin guidance')
local status=m.status;for i=1,120 do f.retry()end
check(m.status==status and f.stats()==1 and m.checkPending,'Timeout retries abandoned call or hid guidance')
f.at(100);f.finish(1,true);check(m.eligible and not m.checkPending,'Late authoritative true did not recover')
m.model.calibrated=true;m:Step(.05);check(m.ready,'Validated calibration was not reusable')
local readyStatus=m.status;f.retry();check(m.eligible and m.ready and m.status==readyStatus,'Cooldown retry discarded legitimate access')
f.at(101.999);f.retry();check(f.stats()==1,'Retry before completion cooldown allowed')
f.at(102);f.retry();check(f.stats()==2 and not m.ready and not m.eligible and m.model.calibrated,'Boundary retry did not start or erased calibration')
f.finish(2,false);check(not m.eligible and not m.checkPending,'Explicit false granted access')
for _,outcome in ipairs({true,false,'error',1,'true'})do
 f=fixture();f.start(outcome);m=f.mic
 check(m.eligible==(outcome==true) and not m.checkPending,'Synchronous outcome interpreted incorrectly')
 for i=1,120 do f.retry()end
 check(f.stats()==1,'Synchronous completion storm bypassed cooldown')
 if outcome~=true then check(string.find(m.status,'wait',1,true)~=nil,'Failed cooldown missing wait guidance')end
 f.at(1.999);f.retry();check(f.stats()==1,'Synchronous cooldown fired early')
 f.at(2);f.retry();check(f.stats()==2,'Synchronous boundary retry blocked')
end
for _,outcome in ipairs({false,'error',true})do
 f=fixture();f.start();m=f.mic;f.at(20);f.finish(1,outcome)
 check(m.eligible==(outcome==true) and not m.checkPending,'Late response misinterpreted')
 f.retry();check(f.stats()==1,'Late completion bypassed cooldown')
 m:Destroy();local oldStatus=m.status;for i=1,120 do f.retry()end;f.at(1000)
 check(f.stats()==1 and m.status==oldStatus and not m.ready and not m.eligible,'Destroyed controller restarted')
end
for _,at in ipairs({9.999,10,10.001})do
 f=fixture();f.start();m=f.mic;f.at(at);f.finish(1,true);check(m.eligible and not m.checkPending,'Notice boundary rejected real completion')
end
f=fixture();f.start();m=f.mic;m:Destroy();local oldStatus=m.status;f.finish(1,true)
check(not m.eligible and not m.ready and m.status==oldStatus,'Late completion resurrected destroyed controller')
f=fixture();f.start(nil,true);m=f.mic;m:Destroy();f.finish(1,true)
check(f.stats()==0 and not m.eligible,'Queued worker called API after destroy')
for _,state in ipairs({{false,false},{true,true}})do
 f=fixture();f.start(false);m=f.mic;f.at(2)
 local oldStatus=m.status;local oldGeneration=m.generation
 f.panel(state[1],state[2]);f.settings()
 check(f.stats()==1 and m.status==oldStatus and m.generation==oldGeneration,'Hidden/destroyed Settings retry reached controller')
 f.panel(true,false);f.settings();check(f.stats()==2,'Visible failed-access retry blocked after reopening')
end
f=fixture();f.start(true);f.at(2);f.settings();check(f.stats()==1 and f.mic.ready,'Settings retried already eligible access')
f=fixture();f.start();local g=f.mic.generation;f.settings();check(f.stats()==1 and f.mic.generation==g,'Settings retried pending access')
print('PASS',n,'actual Microphone/Retry assertions; coroutine API and clock mocks only')
'''
def run(source,error=None,baseline=False,callback_override=None):
 tail="local f=fixture();f.start();for i=1,120 do f.retry()end;local c,j,d=f.stats();assert(c==121 and j==121 and d==121);print('REPRO121 simulated concurrent calls/jobs and121 timeout closures')" if baseline else checks
 text='local n=0;local function check(v,m)assert(v,m);n+=1 end\nlocal function fixture()\n'+setup+source+(endsetup if callback_override is None else endsetup.replace(callback,callback_override))+tail
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.mic_check_',dir=R/'tests',encoding='utf-8',delete=False)as t:t.write(text);q=Path(t.name)
 try:r=subprocess.run(['luau',str(q)],capture_output=True,text=True,timeout=15)
 finally:q.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS negative control:',error)
 else:print(out,end='');assert r.returncode==0
if a.baseline:
 old=subprocess.check_output(['git','show','0619103:'+path],cwd=R,text=True,encoding='utf-8');run(old,baseline=True)
else:
 run(s)
 if a.negative_controls:
  mutations=[('if self.destroyed or self.checkPending then return end','if self.destroyed then return end','Retry storm allocated calls/jobs/timers'),('os.clock()<(self.nextCheckAt or 0)','false','Cooldown retry discarded legitimate access'),('os.clock()+2','os.clock()','Cooldown retry discarded legitimate access'),('os.clock()-self.checkStarted>=10','os.clock()-self.checkStarted>=9','Timeout fired early'),('self.checkPending=false;self.nextCheckAt','self.checkPending=true;self.nextCheckAt','Late authoritative true did not recover'),('if self.destroyed or self.generation~=generation then return end','if false then return end','Late completion resurrected destroyed controller')]
  for old,new,error in mutations:
   assert old in s;run(s.replace(old,new,1) if old.startswith('if self.destroyed or self.checkPending') else s.replace(old,new),error)
  fence='if self.destroyed or self.generation~=generation then return end'
  assert s.count(fence)==2
  run(s.replace(fence,'if false then return end',1),'Queued worker called API after destroy')
  for guard in ('clientDestroyed or ', 'not modal.Visible or '):
   assert guard in wrapper
   old=endsetup;endsetup=endsetup.replace(guard,'')
   try:run(s,'Hidden/destroyed Settings retry reached controller')
   finally:endsetup=old
  assert not re.search(r'\.Active\s*=(?!=)|\.Muted\s*=(?!=)|\.IsReady\b',s)
  print('PASS source contract: no device Active/Muted writes or IsReady access')
