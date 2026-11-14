"""Actual client cadence slice plus real beam mix; synthetic frame timing, not native audio."""
from pathlib import Path
import argparse,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');args=p.parse_args()
name='src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
client=subprocess.check_output(['git','show','327e1dd:'+name],cwd=root,text=True,encoding='utf-8') if args.baseline else (root/name).read_text(encoding='utf-8')
a=client.index(' cueContext();gameplayAudio:Step(os.clock(),dt)',client.index('connectClient(Run.RenderStepped'))
fragment=client[a:client.index(' aimInfo.Text=',a)]
context=client[client.index('local function cueContext()'):client.index('local function playGameplayCue(')]
setup=r'''
local Mix=require('../src/StarterPlayer/StarterPlayerScripts/BeamAudioMix')
local settings=require('../src/ReplicatedStorage/Shared/AttackAudioConfig')
local checks=0;local function check(ok,msg)assert(ok,msg);checks+=1 end
local function near(a,b)return math.abs(a-b)<.0000001 end
local function make()
 local now=0;local os={clock=function()return now end};local elapsed=0
 local mic={ready=true,power=0,phase=nil};local handles={};local updates,destroyed=0,0
 local attackAudio=Mix.new(settings,function()local h={volume=0};table.insert(handles,h);return h end,
 function(h,position,volume,pitch)h.volume=volume;h.pitch=pitch;updates+=1 end,function(h)h.dead=true;destroyed+=1 end)
 local calls,contextCalls,cueCalls=0,0,0;local passed={}
 local step=attackAudio.Step
 function attackAudio:Step(clock,dt,voice,calibrating)
  calls+=1;table.insert(passed,{clock,dt,voice,calibrating});step(self,clock,dt,voice,calibrating)
 end
 local gameplayAudio={SetContext=function()contextCalls+=1 end,Step=function()cueCalls+=1 end}
'''
after_context='\n local function frame(dt)\n now+=dt\n'
after_fragment=r'''
 end
 return {frame=frame,mic=mic,mix=attackAudio,handles=handles,passed=passed,
  time=function()return now end,counts=function()return calls,contextCalls,cueCalls,updates,destroyed end,
  seed=function()attackAudio:Pulse(1,-.2,{},false,10);step(attackAudio,0,.2,false,false)end}
end
local scenarios={}
for _,hz in ipairs({30,60,144})do local seq={};for i=1,hz do table.insert(seq,1/hz)end;table.insert(scenarios,{name=tostring(hz)..'Hz',seq=seq})end
local jitter={};for i=1,60 do table.insert(jitter,({.005,.027,.011,.023})[(i-1)%4+1])end
table.insert(scenarios,{name='jitter',seq=jitter});table.insert(scenarios,{name='stall',seq={.016,.016,.5,.016,.2,.016}})
for _,case in ipairs(scenarios)do
 local f=make();f.mic.power=.5;local elapsed,integrated=0,0
 for i,dt in ipairs(case.seq)do
  f.mix:Pulse(1,f.time(),{},false,10);f.frame(dt);elapsed+=dt;integrated+=math.min(dt,.25)
 end
 local calls,contexts,cues=f.counts();local sum=0;for _,p in ipairs(f.passed)do sum+=p[2]end
 print(string.format('METRIC %s frames=%d beamSteps=%d frameSeconds=%.6f passedSeconds=%.6f duck=%.6f',case.name,#case.seq,calls,elapsed,sum,f.mix.duck))
 check(calls==#case.seq,'Beam Step not exactly once per render frame')
 check(contexts==#case.seq and cues==#case.seq,'Gameplay cue cadence changed')
 check(near(sum,elapsed),'Beam elapsed time lost or duplicated')
 check(near(f.mix.duck,.4+.6*math.exp(-30*integrated)),'Real mixer duck does not match integrated frames')
 for i,p in ipairs(f.passed)do check(p[2]==case.seq[i] and p[3]==true and p[4]==false,'Wrong frame delta or mic state')end
end
for _,dt in ipairs({1/30,1/60,1/144,.007})do
 local f=make();f.seed();check(near(f.handles[1].volume,.4),'Fixture did not start audible')
 f.mic.phase='calibrating';f.frame(dt)
 check(f.handles[1].volume==0,'Calibration silence delayed by HUD throttle')
 f.mic.phase=nil;f.mic.power=.5;f.frame(dt)
 check(f.handles[1].volume<=.24*f.mix.duck+.000001,'Voice ceiling delayed by HUD throttle')
 check(f.mix.duck<1,'Voice duck delayed by HUD throttle')
 f.mic.power=0;local previous=f.mix.duck;f.frame(dt);check(f.mix.duck>previous,'Voice recovery did not use next frame')
end
local f=make();f.seed();f.mix:Stop(1,0);f.frame(.01);check(f.handles[1].volume<.4,'Fade start delayed by HUD throttle')
for i=1,16 do f.frame(.01)end
check(f.handles[1].dead==true and f.mix.count==0,'Fade cleanup missed first eligible frame')
f=make();f.seed();f.frame(.65);check(f.handles[1].dead==true,'Stall timeout cleanup failed')
f=make();f.seed();f.mix:SetLevel('OFF');local n=f.counts();f.frame(.01);check(f.mix.count==0 and f.handles[1].dead,'OFF changed under cadence correction')
print('PASS '..checks..' actual cadence and mixer assertions; synthetic frames only')
'''
def run(code,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',encoding='utf-8',delete=False)as f:f.write(code);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],text=True,capture_output=True)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if expected:
  assert r.returncode and expected in out,out
  print(r.stdout.strip());print('PASS negative control:',expected)
 else:assert r.returncode==0,out;print(out.strip())
def assemble(part):return setup+context+after_context+part+after_fragment
if args.baseline:run(assemble(fragment),'Beam Step not exactly once per render frame')
else:
 run(assemble(fragment))
 if args.negative_controls:
  line=next(x for x in fragment.splitlines() if 'attackAudio:Step(' in x)
  gate=next(x for x in fragment.splitlines() if 'elapsed+=dt;' in x)
  old=fragment.replace(line+'\n','').replace(gate,gate+'\n'+line)
  run(assemble(old),'Beam Step not exactly once per render frame')
  run(assemble(fragment.replace(line,line+'\n'+line)),'Beam Step not exactly once per render frame')
  run(assemble(fragment.replace('attackAudio:Step(os.clock(),dt,','attackAudio:Step(os.clock(),.15,')),'Beam elapsed time lost or duplicated')
