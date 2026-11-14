"""Actual Action dispatcher + protocol/adapter/controller; synchronous synthetic transport."""
from pathlib import Path
import subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
PATH='src/ServerScriptService/Bootstrap.server.luau'
def source(baseline=False):
 return subprocess.check_output(['git','show','909dceb:'+PATH],cwd=ROOT,text=True) if baseline else (ROOT/PATH).read_text()
def assemble(s,baseline=False):
 dispatcher=s[s.index('action.OnServerEvent:Connect(function'):s.index('\nlocal function joined(p)')]
 helpers=s[s.index('local function sustainedEnd('):s.index('local function beamColor(')]
 return r'''
local nativeRequire=require
local Attack=require('../src/ReplicatedStorage/Shared/SustainedAttack')
local Combat=require('../src/ReplicatedStorage/Shared/VoiceCombat')
local Adapter=require('../src/ServerScriptService/SustainedAttackAdapter')
local Controls=require('../src/StarterPlayer/StarterPlayerScripts/SustainedControls')
local Gate=require('../src/ReplicatedStorage/Shared/VoiceActivation')
local require=function(_)return Attack end
local ReplicatedStorage={Shared={SustainedAttack={}}}
local now=0;local os={clock=function()return now end}
local workspace={GetServerTimeNow=function()return now end}
local broadcasts,attributes,cancels=0,0,0
local effect={FireAllClients=function()broadcasts+=1 end}
local VoiceCombat={Cancel=function(v)cancels+=1;v.capture=nil end}
local sustained=Adapter.new(Attack,Combat,function()return 1 end)
local sessions={};local dispatch
local action={OnServerEvent={Connect=function(_,f)dispatch=f end}}
local context={origin=0,character={},level=1,amplifier=false}
local function sustainedContext(p,s,t)if s.micReady then return context end end
''' + helpers+dispatcher+r'''
local checks=0
local function check(v,m)assert(v,m);checks+=1 end
local function request(seq)return {sequence=seq,power=.8,aim=20}end
local function fresh()
 now=0;broadcasts=0;attributes=0;cancels=0
 local p={UserId=42,SetAttribute=function()attributes+=1 end}
 local s={sustained=sustained.New(),micReady=true,voice={},data={sound='Default'},nextAction=100}
 sessions[p]=s
 dispatch(p,'SustainedBegin',request(1));check(s.sustained.protocol.active~=nil,'Begin precondition')
 for i=1,29 do dispatch(p,'Unknown',nil)end
 check(s.requestCount==30,'Window not saturated exactly')
 return p,s
end
local baseline=BASELINE
for _,mode in ipairs({'OFF','focus','mic-loss','MicReady'})do
 local p,s=fresh();now=.01
 local sends=0
 local controls=Controls.new(Gate.new(),function(verb,arg)sends+=1;dispatch(p,verb,arg)end,function()return 20 end)
 controls.armed=true;controls.attack={sequence=1}
 if mode=='OFF' then controls:SetArmed(false)
 elseif mode=='focus' then controls:Step(.01,now,.8,false,true,true,1)
 elseif mode=='mic-loss' then controls:ObserveAvailability(false)
 else dispatch(p,'MicReady',false) end
 local calls,damage=0,0
 for _,t in ipairs({.2,.4,.501}) do
  now=t
  local hits,ended=sustained.Step(s.sustained,now,sustainedContext(p,s,now),function()calls+=1;return {'victim'},{} end)
  sustainedEnd(p,ended,now)
  for _,hit in ipairs(hits)do damage+=hit.damage end
 end
 print('SCENARIO',mode,'post-stop resolutions',calls,'damage',damage,'end broadcasts',broadcasts)
 if baseline then check(calls==2 and damage>0,'Historical dropped-stop reproduction changed')
 else check(calls==0 and damage==0,'Received stop permitted post-stop damage') end
 if mode~='MicReady' then check(sends==1 and controls.attack==nil,'Controller did not send exactly one stop') end
end

if not baseline then
 -- Invalid/mismatched sequence cannot stop even after admission is saturated.
 for _,bad in ipairs({false,true,'1',{},0,-1,1.5,2,math.huge,0/0}) do
  local p,s=fresh();now=.01;dispatch(p,'SustainedStop',bad)
  check(s.sustained.protocol.active~=nil and broadcasts==0,'Malformed/stale stop canceled current attack')
 end
 local p,s=fresh();now=.01
 dispatch({},'SustainedStop',1);dispatch({},'MicReady',false);dispatch(p,{},false)
 check(s.sustained.protocol.active~=nil and s.micReady,'Stranger/malformed verb affected player')
 dispatch(p,'SustainedStop',1)
 check(not s.sustained.protocol.active and broadcasts==1,'Valid stop lost after saturation')
 local ready=s.sustained.protocol.nextStart
 check(ready>=5,'Stop removed cooldown')
 local writes=attributes
 for i=1,1000 do dispatch(p,'SustainedStop',1) end
 check(broadcasts==1 and attributes==writes,'Repeated stop caused repeated output')
 dispatch(p,'SustainedBegin',request(2));check(not s.sustained.protocol.active,'Saturated begin admitted')
 now=1.01;dispatch(p,'SustainedBegin',request(3));check(not s.sustained.protocol.active,'Fresh window bypassed cooldown')
 now=ready;dispatch(p,'SustainedBegin',request(4));check(s.sustained.protocol.active~=nil,'Cooldown/window never recovered')
 dispatch(p,'SustainedStop',1);check(s.sustained.protocol.active.sequence==4,'Old stop ended newer attack')
 dispatch(p,'SustainedStop',4);check(not s.sustained.protocol.active,'New sequence stop failed')
 -- False readiness is idempotent, but true remains under ordinary admission.
 p,s=fresh();now=.01;dispatch(p,'MicReady',false)
 check(not s.micReady and not s.sustained.protocol.active and broadcasts==1,'Mic loss retained server attack/readiness')
 ready=s.sustained.protocol.nextStart;writes=attributes;local oldCancels=cancels
 for i=1,1000 do dispatch(p,'MicReady',false) end
 check(broadcasts==1 and attributes==writes and cancels==oldCancels,'Repeated mic loss caused repeated side effects')
 dispatch(p,'MicReady',true);check(not s.micReady,'Saturated readiness true admitted')
 now=1.01;dispatch(p,'MicReady',true);check(s.micReady,'Readiness did not recover with window')
 dispatch(p,'SustainedBegin',request(2));check(not s.sustained.protocol.active,'Mic reenable bypassed cooldown')
 check(s.sustained.protocol.nextStart==ready,'Readiness changed cooldown')
 -- Pulses, unlike cancellation, must not bypass admission or extend stale input.
 p,s=fresh();now=.125;dispatch(p,'SustainedPulse',{sequence=1,sample=1,power=.8,aim=20})
 check(s.sustained.protocol.active.lastPulse==0,'Saturated pulse refreshed attack')
 -- Legacy capture and inconsistent false-readiness active state also clean up once.
 p,s=fresh();s.micReady=false;now=.01;dispatch(p,'MicReady',false)
 check(not s.sustained.protocol.active and broadcasts==1,'False readiness left inconsistent live attack')
 p,s=fresh();s.sustained=nil;s.voice.capture={};s.micReady=false;now=.01
 dispatch(p,'MicReady',false);check(s.voice.capture==nil and cancels==1,'Legacy capture survived mic loss')
 writes=attributes;dispatch(p,'MicReady',false);check(cancels==1 and attributes==writes,'Idle legacy false repeated work')
 -- Wrong sequence after timeout must not bypass quota and trigger expiry side effects.
 p,s=fresh();now=.6;dispatch(p,'SustainedStop',2)
 check(broadcasts==0 and s.sustained.protocol.active~=nil,'Stale stop bypassed quota through expiry')
 -- Matching expired stop may finish only its owner, preserving timeout cooldown semantics.
 p,s=fresh();now=.6;dispatch(p,'SustainedStop',1)
 check(not s.sustained.protocol.active and broadcasts==1,'Matching expired stop was lost')
 check(math.abs(s.sustained.protocol.nextStart-5.5)<1e-6,'Expired stop changed authoritative timeout cooldown')
 local first,firstState=fresh()
 local second={UserId=43,SetAttribute=function()attributes+=1 end}
 local secondState={sustained=sustained.New(),micReady=true,voice={},data={sound='Default'},nextAction=100}
 sessions[second]=secondState
 dispatch(second,'SustainedBegin',request(1))
 for i=1,29 do dispatch(second,'Unknown',nil)end
 now=.01;dispatch(first,'SustainedStop',1)
 check(not firstState.sustained.protocol.active and secondState.sustained.protocol.active~=nil,'Player stop crossed session boundary')
 dispatch(first,'MicReady',false)
 check(secondState.micReady and secondState.sustained.protocol.active~=nil,'Player mic loss crossed session boundary')
 dispatch(second,'MicReady',false)
 check(not secondState.micReady and not secondState.sustained.protocol.active,'Second player stop failed independently')
 -- A valid stop must work below saturation too.
 p,s=fresh();s.requestCount=0;now=.01;dispatch(p,'SustainedStop',1)
 check(not s.sustained.protocol.active and broadcasts==1,'Unsaturated stop regressed')
end
print('PASS',checks,'dispatcher/adapter assertions')
'''.replace('BASELINE','true' if baseline else 'false')
def run(s,baseline=False):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',delete=False) as f:
  f.write(assemble(s,baseline));name=f.name
 try:return subprocess.run(['luau',name],cwd=ROOT,text=True,capture_output=True)
 finally:Path(name).unlink()
if __name__=='__main__':
 baseline='--baseline' in sys.argv
 current=source(baseline)
 result=run(current,baseline);print(result.stdout,end='');print(result.stderr,end='')
 if result.returncode:sys.exit(result.returncode)
 if '--negative-controls' in sys.argv:
  start=current.index(' if verb=="SustainedStop" and s.sustained then',current.index('action.OnServerEvent'))
  end=current.index(' s.requestWindow=',start)
  mutants=[('safety bypass removed',current[:start]+current[end:]),
   ('sequence validation bypassed',current.replace('if active and arg==active.sequence then','if active then',1)),
   ('false readiness idempotency removed',current.replace('if s.micReady~=false or (s.sustained and s.sustained.protocol.active) or s.voice.capture then','if true then',1)),
   ('ordinary quota removed',current.replace('s.requestCount+=1;if s.requestCount>30 then return end','s.requestCount+=1;if false then return end',1))]
  for label,mutant in mutants:
   assert mutant!=current,'Mutation did not match: '+label
   failed=run(mutant)
   assert failed.returncode!=0,'Mutation escaped: '+label
   assert 'assertion failed' in failed.stderr or any(x in failed.stderr for x in ['post-stop damage','bypassed quota','repeated side effects','refreshed attack','readiness true admitted']),failed.stderr
   print('PASS negative control:',label)
