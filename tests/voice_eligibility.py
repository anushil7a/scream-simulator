"""Server account-voice eligibility, not microphone or client-power authenticity.
Actual source slices, synthetic transport/clock/API; no native service requests.
"""
from pathlib import Path
import subprocess,tempfile,sys
import voice_stop_rate_limit as stop_harness
ROOT=Path(__file__).resolve().parents[1]
def read(path,baseline=False):
 return subprocess.check_output(['git','show','e977040:'+path],cwd=ROOT,text=True,encoding='utf-8') if baseline else (ROOT/path).read_text(encoding='utf-8')
def integration(baseline=False,mutation=None):
 b=read('src/ServerScriptService/Bootstrap.server.luau',baseline)
 if mutation:b=mutation(b)
 code=stop_harness.assemble(b).split('local checks=0',1)[0]
 capture=b[b.index('local function canCapture('):b.index('local function attackOrigin(')]
 code=code.replace('local VoiceCombat={Cancel=function(v)cancels+=1;v.capture=nil end}','local VoiceCombat=Combat')
 code=code.replace('local function sustainedContext(p,s,t)if s.micReady then return context end end',
  'local function parts(p)return context.character,{Position=0},{Health=100,PlatformStand=false}end\n'+capture+'local function sustainedContext(p,s,t)if canCapture(p,s,t)then return context end end')
 if baseline:return code+BASELINE
 asyncHelper=b[b.index('local voiceRequestBudget='):b.index('Commerce.Start(')]
 return "local VoiceEligibility=require('../src/ServerScriptService/VoiceEligibility')\n"+code+ASYNC+asyncHelper+'\nlocal observeOnly=stepVoiceEligibility\nstepVoiceEligibility=function(p,s,t)observeOnly(p,s,t);dispatchVoiceEligibility(t)end\n'+FIXED
BASELINE=r"""
local p={UserId=7,SetAttribute=function()end}
local s={data={sound='TinyAah'},voice=Combat.New(),micReady=false,protectedUntil=0,dodgingUntil=0,nextAction=100,sustained=sustained.New()};sessions[p]=s
-- No account eligibility evidence exists in this historical fixture.
dispatch(p,'MicReady',true);dispatch(p,'SustainedBegin',{sequence=1,power=1,aim=20})
assert(s.sustained.protocol.active,'Historical synthetic begin no longer accepted')
local hits=sustained.Step(s.sustained,.2,context,function()return {'victim'},{}end)
assert(#hits==1 and hits[1].damage>0,'Historical synthetic power produced no hit')
print('BASELINE automatic spoof accepted; first synthetic hit damage',hits[1].damage)
s.sustained=nil;s.voice=Combat.New();now=10
 dispatch(p,'BeginCast',1)
assert(s.voice.capture~=nil,'Historical synthetic legacy begin rejected')
assert(Combat.Release(s.voice,10.3,1,1,canCapture(p,s,10.3)),'Historical synthetic legacy release rejected')
print('BASELINE legacy spoof accepted; no account/microphone authentication')
"""
ASYNC=r"""
local closing=false;local queued={};local serviceCalls=0;local serviceAnswer=true;local serviceHook;local stateCalls=0
local task={spawn=function(f,...)local args=table.pack(...);table.insert(queued,function()f(table.unpack(args,1,args.n))end)end}
local function state()stateCalls+=1 end
local VoiceChatService={IsVoiceEnabledForUserIdAsync=function(_,id)
 serviceCalls+=1;if serviceHook then serviceHook()end
 if serviceAnswer=='error' then error('simulated error')end
 return serviceAnswer
end}
local function flush()
 local f=table.remove(queued,1);assert(f,'Missing queued API request');f()
end
"""
FIXED=r"""
local n=0;local function check(v,m)assert(v,m);n+=1 end
local function fresh(fixture)
 now=0;sessions={};voiceRequestBudget.inFlight=0;voiceRequestBudget.nextStart=0;queued={};serviceCalls=0;serviceHook=nil;serviceAnswer=true;closing=false
 local p={UserId=7,Parent=true,SetAttribute=function()end}
 local s={data={sound='TinyAah'},voice=Combat.New(),micReady=false,protectedUntil=0,dodgingUntil=0,nextAction=100,sustained=sustained.New(),voiceEligibility=VoiceEligibility.New(fixture)};sessions[p]=s
 return p,s
end
local function spoof(p,s)
 dispatch(p,'MicReady',true);dispatch(p,'SustainedBegin',{sequence=1,power=1,aim=20})
 check(s.micReady and not s.sustained.protocol.active,'Client ready/power bypassed account gate')
 check(sustained.Step(s.sustained,.2,nil,function()error('Blocked attack resolved targets')end)[1]==nil,'Blocked account damaged target')
 s.sustained=nil;s.voice=Combat.New();now=.3;dispatch(p,'BeginCast',1)
 check(s.voice.capture==nil and not Combat.Release(s.voice,.6,1,1,canCapture(p,s,.6)),'Legacy client spoof bypassed account gate')
end
local p,s=fresh(false);spoof(p,s)
check(s.micReady,'Eligibility gating changed calibration/movement readiness')
check(serviceCalls==0 and #queued==0,'Client packet triggered API calls')
p,s=fresh(false);s.testBaseline={};spoof(p,s)
p,s=fresh(false);local t=VoiceEligibility.Poll(s.voiceEligibility,0);VoiceEligibility.Complete(s.voiceEligibility,t,.1,true,false);spoof(p,s)
p,s=fresh(false);stepVoiceEligibility(p,s,0);check(#queued==1,'Join-like poll did not schedule API')
for i=1,100 do now=i*.1;stepVoiceEligibility(p,s,now)end
check(#queued==1 and serviceCalls==0,'Pending async request duplicated')
-- Queued work starts after its deadline: late success cannot authorize.
flush();check(not VoiceEligibility.Allowed(s.voiceEligibility,now),'Delayed async completion admitted account')
-- Session replaced before queued work starts: never call API or mutate replacement.
p,s=fresh(false);stepVoiceEligibility(p,s,0);local replacement={voiceEligibility=VoiceEligibility.New(false),voice={}};sessions[p]=replacement;flush()
check(serviceCalls==0 and not VoiceEligibility.Allowed(replacement.voiceEligibility,0),'Stale queued session reached API')
-- Session replaced during yielding API: completion must not affect either admission.
p,s=fresh(false);stepVoiceEligibility(p,s,0);replacement={voiceEligibility=VoiceEligibility.New(false),voice={}}
VoiceEligibility.Poll(replacement.voiceEligibility,0);serviceHook=function()sessions[p]=replacement end;now=.1;flush()
check(serviceCalls==1 and not VoiceEligibility.Allowed(s.voiceEligibility,.1) and not VoiceEligibility.Allowed(replacement.voiceEligibility,.1),'Stale API response authorized session')
-- Departures and server close also invalidate queued work.
for _,mode in ipairs({'departed','closing'})do
 p,s=fresh(false);stepVoiceEligibility(p,s,0)
 if mode=='departed' then p.Parent=nil else closing=true end
 flush();check(serviceCalls==0,'Departed/closing task called API')
end
-- Fresh session may independently acquire eligibility; no negative cache crosses rejoin.
p,s=fresh(false);stepVoiceEligibility(p,s,0);now=.1;flush()
check(VoiceEligibility.Allowed(s.voiceEligibility,now),'Fresh exact true service result denied')
dispatch(p,'MicReady',true);dispatch(p,'SustainedBegin',{sequence=1,power=1,aim=20})
check(s.sustained.protocol.active~=nil,'Eligible account could not start')
for i=1,30 do dispatch(p,'Unknown')end
dispatch(p,'SustainedStop',1);check(not s.sustained.protocol.active,'Eligibility broke saturated safety stop')
local ready=s.sustained.protocol.nextStart;check(ready>now,'Stop bypassed cooldown')
-- Cache expiry while refresh remains pending cancels both active attack modes.
p,s=fresh(false);stepVoiceEligibility(p,s,0);now=.1;flush();now=60.1;stepVoiceEligibility(p,s,now)
check(#queued==1,'Expiry fixture did not retain pending refresh')
now=120;dispatch(p,'MicReady',true);dispatch(p,'SustainedBegin',{sequence=1,power=1,aim=20});s.voice.capture={started=120,sequence=1}
check(s.sustained.protocol.active~=nil,'Expiry fixture failed live attack precondition')
now=120.1;stepVoiceEligibility(p,s,now)
check(not s.sustained.protocol.active and s.voice.capture==nil and s.micReady,'Cache expiry did not cancel both captures independently of readiness')
check(not canCapture(p,s,now),'Expired cached eligibility still allowed capture')
-- Restore eligible active setup for explicit denial scenario below.
p,s=fresh(false);stepVoiceEligibility(p,s,0);now=.1;flush();dispatch(p,'MicReady',true)
-- Revocation cancels automatic and legacy captures without wiping client micReady.
now=6;s.requestWindow=now;s.requestCount=0;dispatch(p,'SustainedBegin',{sequence=2,power=1,aim=20})
s.voice.capture={started=6,sequence=1};now=60.1;serviceAnswer=false;stepVoiceEligibility(p,s,now);now=60.2;flush()
check(not s.sustained.protocol.active and s.voice.capture==nil and s.micReady,'Revocation failed to cancel attacks or changed readiness')
check(not canCapture(p,s,now),'Revoked account can capture')
-- Legacy receives same account protection, successful eligible path unchanged.
p,s=fresh(false);stepVoiceEligibility(p,s,0);now=.1;flush();s.sustained=nil
 dispatch(p,'MicReady',true);dispatch(p,'BeginCast',1)
check(s.voice.capture~=nil and Combat.Release(s.voice,.4,1,1,canCapture(p,s,.4)),'Eligible legacy path regressed')
p,s=fresh(true);stepVoiceEligibility(p,s,0);dispatch(p,'MicReady',true);dispatch(p,'SustainedBegin',{sequence=1,power=1,aim=20})
check(s.sustained.protocol.active and #queued==0 and serviceCalls==0,'Strict fixture bypass called live service or failed')
print('PASS',n,'actual dispatcher/capture/async-helper eligibility assertions; synthetic API only')
"""
PURE=r"""
local n=0;local function check(v,m)assert(v,m);n+=1 end
local function begin(s,t)local token=E.Poll(s,t);check(type(token)=='number' and token%1==0,'No integer request token');return token end
for _,fixture in ipairs({false,0,1,'true',{}})do
 local s=E.New(fixture);check(not E.Allowed(s,0),'Truthy nonboolean fixture bypassed eligibility')
end
local f=E.New(true);check(E.Allowed(f,0) and E.Poll(f,0)==nil,'Exact fixture bypass failed')
local s=E.New(false);check(not E.Allowed(s,0),'Pending account allowed');local t=begin(s,0)
for _,now in ipairs({0,1,7.999,8,100,10000})do check(E.Poll(s,now)==nil,'Hung API call overlapped');check(not E.Allowed(s,now),'Hung API call allowed attack')end
E.Complete(s,t,10000,true,true);check(not E.Allowed(s,10000),'Late positive admitted')
check(E.Poll(s,10001.999)==nil,'Retry backoff shortened');local retry=begin(s,10002)
check(retry~=t,'Retry reused token');E.Complete(s,t,10002.1,true,true);check(not E.Allowed(s,10002.1),'Stale token granted access')
E.Complete(s,retry,10002.2,true,true);check(E.Allowed(s,10002.2),'Fresh exact true result rejected')
for _,row in ipairs({{7.999,true},{8,false},{8.001,false}})do
 local v=E.New(false);local k=begin(v,0);E.Complete(v,k,row[1],true,true)
 check(E.Allowed(v,row[1])==row[2],'Eight-second request deadline incorrect')
end
for _,answer in ipairs({false,'true',1,{},0})do
 local v=E.New(false);local k=begin(v,0);E.Complete(v,k,1,true,answer)
 check(not E.Allowed(v,1),'Nonboolean true service result accepted')
end
s=E.New(false);t=begin(s,0);E.Complete(s,t,1,true,false)
check(not E.Allowed(s,1) and E.Poll(s,120.999)==nil and E.Poll(s,121)~=nil,'Denied account bounded recheck failed')
s=E.New(false);t=begin(s,0);E.Complete(s,t,1,false,'error')
check(E.Poll(s,2.999)==nil,'First error backoff missing');t=begin(s,3);E.Complete(s,t,4,false,'error')
check(E.Poll(s,8.999)==nil,'Second error backoff missing');t=begin(s,9);E.Complete(s,t,10,false,'error')
check(E.Poll(s,39.999)==nil and E.Poll(s,40)~=nil and not E.Allowed(s,40),'Error recovery backoff failed')
s=E.New(false);t=begin(s,0);E.Complete(s,t,1,true,true)
check(E.Allowed(s,1) and E.Poll(s,60.999)==nil,'Positive refresh too early');t=begin(s,61)
E.Complete(s,t,62,false,'error');check(E.Allowed(s,62),'Refresh error prematurely discarded valid cache')
t=begin(s,64);E.Complete(s,t,65,false,'error');t=begin(s,70);E.Complete(s,t,71,false,'error')
check(E.Allowed(s,120.999) and not E.Allowed(s,121),'Refresh errors extended positive cache')
check(E.Poll(s,121)~=nil,'Error recovery failed to resume after cache expiry')
s=E.New(false);t=begin(s,0);E.Complete(s,t,1,true,true);t=begin(s,61);E.Complete(s,t,62,true,false)
check(not E.Allowed(s,62),'Fresh denial failed to revoke positive cache')
s=E.New(false);t=begin(s,0);E.Complete(s,t,1,true,true);t=begin(s,61);E.Complete(s,t,62,true,true)
check(E.Allowed(s,181.999) and not E.Allowed(s,182),'Successful refresh cache deadline incorrect')
check(E.Status(E.New(false),0)=='checking' and E.Status(E.New(true),0)=='fixture','Initial status mismatch')
local denied=E.New(false);local k=begin(denied,0);E.Complete(denied,k,1,true,false);check(E.Status(denied,1)=='denied','Denial status missing')
local hung=E.New(false);begin(hung,0);check(E.Status(hung,8)=='unavailable','Timed out pending status missing')
local live=E.New(false);k=begin(live,0);E.Complete(live,k,1,true,true);check(E.Status(live,1)=='eligible','Eligible status missing')
print('PASS',n,'pure eligibility timing/admission assertions')
"""
def client_cases(mutation=None):
 c=read('src/StarterPlayer/StarterPlayerScripts/Client.client.luau')
 if mutation:c=mutation(c)
 helpers=c[c.index('local function voiceEligibilityHint('):c.index('local function toggleVoice(')]
 blocked=c[c.index('local function beamBlocked('):c.index('local function beginCapture(')]
 observe=next(line.strip() for line in c.splitlines() if 'sustainedControl:ObserveAvailability(alive' in line)
 callback=c.split('connectClient(remotes.State.OnClientEvent,function(nextData)',1)[1].split(' local unclaimed=0',1)[0]
 return CLIENT_SETUP+blocked+helpers+'\nlocal function receive(nextData)\n'+callback+'\nend\nlocal function frame() '+observe+' end\n'+CLIENT_CHECKS
CLIENT_SETUP=r"""
local Controls=require('../src/StarterPlayer/StarterPlayerScripts/SustainedControls')
local Gate=require('../src/ReplicatedStorage/Shared/VoiceActivation')
local data={voiceEligible=false,voiceStatus='checking'};local voiceAccessInterrupted=false
local unavailable=false;local function blocked()return unavailable end
local alive=true;local mic={ready=true};local windowFocused=true;local GuiService={MenuIsOpen=false}
local sends=0;local captureSource;local canceled=0
local function cancelCapture()captureSource=nil;canceled+=1 end
local function cueContext()end
local gameplayAudio={ObserveLevel=function()end}
local function controller()return Controls.new(Gate.new(),function()sends+=1 end,function()return 20 end)end
local sustainedControl=controller()
"""
CLIENT_CHECKS=r"""
local n=0;local function check(v,m)assert(v,m);n+=1 end
check(not blocked() and beamBlocked(),'Voice eligibility gated ordinary movement or failed beam gate')
observeVoiceEligibility(data);frame();check(not sustainedControl.armed,'Pending autoarmed')
local ready={voiceEligible=true,voiceStatus='eligible'};observeVoiceEligibility(ready);data=ready;frame()
check(sustainedControl.armed,'First normal success lost calibration autoarm')
sustainedControl.attack={sequence=1};local lost={voiceEligible=false,voiceStatus='denied'}
receive(lost);receive(ready);frame()
check(not sustainedControl.armed and sustainedControl.attack==nil and sends==1,'False-true same-frame transition retained attack/arm')
check(voiceAccessInterrupted,'Denial did not latch deliberate-resume requirement')
sustainedControl=controller();voiceAccessInterrupted=false
observeVoiceEligibility({voiceEligible=false,voiceStatus='unavailable'});data=ready;frame()
check(not sustainedControl.armed and voiceAccessInterrupted,'First success after error silently autoarmed')
sustainedControl:SetArmed(true);check(sustainedControl.armed,'Explicit resume after verification blocked')
observeVoiceEligibility({voiceEligible='true',voiceStatus='checking'});check(not sustainedControl.armed,'Truthy client state retained arm')
sustainedControl=nil;captureSource='mouse';observeVoiceEligibility(lost)
check(captureSource==nil and canceled==1,'Legacy capture survived state revocation')
for _,status in ipairs({'checking','denied','unavailable'})do
 data={voiceEligible=false,voiceStatus=status};local compact=voiceEligibilityHint(true);local full=voiceEligibilityHint(false)
 local _,lines=compact:gsub('\n','');check(lines<=1,'Compact voice status exceeds two logical lines')
 check(full:find('Voice chat is unchanged',1,true),'Eligibility hint implies microphone mute')
end
data=ready;check(voiceEligibilityHint()==nil and not beamBlocked(),'Eligible status retained beam lock')
print('PASS',n,'actual client eligibility transition assertions; no native text-fit claim')
"""
def run(code):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False)as f:f.write(code);path=Path(f.name)
 try:return subprocess.run(['luau',str(path)],cwd=ROOT,text=True,capture_output=True,encoding='utf-8')
 finally:path.unlink()
if __name__=='__main__':
 if '--baseline' in sys.argv:
  r=run(integration(True));print(r.stdout+r.stderr,end='');sys.exit(r.returncode)
 for code in ["local E=require('../src/ServerScriptService/VoiceEligibility')\n"+PURE,integration(),client_cases()]:
  r=run(code);print(r.stdout+r.stderr,end='')
  if r.returncode:sys.exit(r.returncode)


 if '--negative-controls' in sys.argv:
  module=read('src/ServerScriptService/VoiceEligibility.luau')
  controls=[('overlap prevention',' or s.pending then',' then','Hung API call overlapped'),
   ('deadline acceptance','now<request.deadline','now<=request.deadline','Eight-second request deadline'),
   ('expiry strictness','(s.expires or 0)>now','(s.expires or 0)>=now','Truthy nonboolean fixture bypassed eligibility'),
   ('exact result validation','type(result)=="boolean"','true','Nonboolean true service result accepted'),
   ('recovery pacing','Eligibility.RecoveryBase*2^(s.bursts-1)','0','Error recovery backoff failed'),
   ('positive cache extension','s.failed=true','s.expires=now+120;s.failed=true','Late positive admitted')]
  for name,old,new,expected in controls:
   assert old in module,name
   mutant=module.replace(old,new,1)
   failed=run('local E=(function()\n'+mutant+'\nend)()\n'+PURE);out=failed.stdout+failed.stderr
   assert failed.returncode and expected in out,out
   print('PASS negative control:',name)
  for name,old,new,expected in [
   ('capture eligibility','and VoiceEligibility.Allowed(s.voiceEligibility,now)','', 'Client ready/power bypassed')]:
   def mutate(b):
    assert old in b,name
    return b.replace(old,new)
   failed=run(integration(mutation=mutate));out=failed.stdout+failed.stderr
   assert failed.returncode and expected in out,out
   print('PASS negative control:',name)
  b=read('src/ServerScriptService/Bootstrap.server.luau')
  assert 'local localFixture=RunService:IsStudio() and game.PlaceId==0 and workspace:GetAttribute("LocalSustainedPrototype")==true' in b
  assert 'VoiceEligibility.New(localFixture,os.clock(),p.UserId)' in b
  assert 's.micReady=arg==true' in b
  print('PASS 3 source contracts: strict fixture creation and independent client readiness')

  for name,old,new,expected in [
   ('client revocation cancellation','sustainedControl:SetArmed(false)\n elseif captureSource','sustainedControl:SetArmed(true)\n elseif captureSource','False-true same-frame transition'),
   ('client interrupted autoarm',' and not voiceAccessInterrupted)',' )','First success after error silently autoarmed')]:
   def mutate(c):
    assert old in c,name
    return c.replace(old,new,1)
   failed=run(client_cases(mutate));out=failed.stdout+failed.stderr
   assert failed.returncode and expected in out,out
   print('PASS negative control:',name)
  c=read('src/StarterPlayer/StarterPlayerScripts/Client.client.luau')
  callback=c.split('connectClient(remotes.State.OnClientEvent,function(nextData)',1)[1].split(' local unclaimed=0',1)[0]
  assert callback.index('observeVoiceEligibility(nextData)')<callback.index('data=nextData')
  print('PASS source contract: eligibility transition observed before client state assignment')

  def remove_callback_call(c):
   anchor='connectClient(remotes.State.OnClientEvent,function(nextData)'
   before,after=c.split(anchor,1)
   assert '\n observeVoiceEligibility(nextData)' in after
   return before+anchor+after.replace('\n observeVoiceEligibility(nextData)','',1)
  failed=run(client_cases(remove_callback_call));out=failed.stdout+failed.stderr
  assert failed.returncode and 'False-true same-frame transition' in out,out
  print('PASS negative control: actual State callback invocation removed')
  def remove_expiry_cancel(b):
   start=b.index('local function stepVoiceEligibility(');end=b.index('Commerce.Start(',start)
   helper=b[start:end]
   helper=helper.replace('if not VoiceEligibility.Allowed(s.voiceEligibility,now) then','if false then',1)
   return b[:start]+helper+b[end:]
  failed=run(integration(mutation=remove_expiry_cancel));out=failed.stdout+failed.stderr
  assert failed.returncode and 'Cache expiry did not cancel both captures' in out,out
  print('PASS negative control: cache-expiry helper cancellation removed')
  def remove_after_yield_fence(b):
   old='if closing or not p.Parent or not s or s.voiceEligibility.identity~=identity then return end'
   assert old in b
   return b.replace(old,'if false then return end',1)
  failed=run(integration(mutation=remove_after_yield_fence));out=failed.stdout+failed.stderr
  assert failed.returncode and 'Stale API response authorized session' in out,out
  print('PASS negative control: independent post-yield session fence removed')
