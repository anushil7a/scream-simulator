"""Actual fixture finish/interrupt callbacks; mocked failures, not native cleanup proof."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'tests/StudioBeamPerformance.client.luau').read_text()
finish=s[s.index('local function finish('):s.index('-- Wait for a real, stable viewport')]
setup=r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
for _,failure in ipairs({'none','manager','visuals','cameraType','cameraFrame','cameraFov'})do
 for _,interrupt in ipairs({'success','failure','destroy','timeout'})do
 local buildIdentity='synthetic-build';local done=false;local checks=0;local rows={};local tracked={};local calls={};local result;local watchdog
 local function hit(k)calls[k]=(calls[k]or 0)+1;if failure==k then error('injected '..k)end end
 local manager={count=0,entries={},Destroy=function()hit('manager')end}
 local Visuals={Clear=function()hit('visuals')end,Budget=function()return 0,0 end}
 local original={type='oldtype',cf='oldframe',fov=77}
 local camera=setmetatable({},{__newindex=function(_,k,v)hit(k=='CameraType' and 'cameraType' or k=='CFrame' and 'cameraFrame' or 'cameraFov');assert(v==(k=='CameraType' and original.type or k=='CFrame' and original.cf or original.fov))end})
 local connection={Connected=true,Disconnect=function(self)self.Connected=false;hit('disconnect')end}
 local destruction;local destroyCallback;local timeoutCallback
 local startupConnection={Disconnect=function()end}
 local script={Destroying={Connect=function(_,f)destroyCallback=f;return {Disconnect=function()hit('destroyDisconnect')end}end}}
 local task={delay=function(_,f)timeoutCallback=coroutine.create(f);return timeoutCallback end,cancel=function(thread)assert(thread~=coroutine.running(),"Watchdog canceled itself");hit('cancel')end}
 local Http={JSONEncode=function(_,v)result=v;return ''end};local print=function()hit('print')end
'''
checks=r'''
 if interrupt=='destroy' then destroyCallback()elseif interrupt=='timeout' then local ok,err=coroutine.resume(timeoutCallback);assert(ok,err)else finish(interrupt=='success','synthetic')end
 check(done and not connection.Connected,'Terminal callback remained live')
 for _,k in ipairs({'manager','visuals','cameraType','cameraFrame','cameraFov'})do check(calls[k]==1,'Cleanup skipped '..k)end
 check(result.buildIdentity==buildIdentity,'Result missing build identity')
 check(result.ok==(failure=='none' and interrupt=='success'),'Incorrect terminal success')
 check(#result.cleanupErrors==(failure=='none' and 0 or 1),'Cleanup error not reported')
 finish(true);check(calls.print==1 and calls.manager==1,'Repeated completion repeated cleanup')
 end
end
print('PASS '..n..' actual fixture cleanup/interrupt assertions; mocked failures only')
'''
def run(code):
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(code);p=Path(f.name)
 try:return subprocess.run(['luau',str(p)],capture_output=True,text=True,timeout=20)
 finally:p.unlink()
r=run(setup+finish+checks);print(r.stdout,end='');assert r.returncode==0,r.stderr
mutant=finish.replace(' and coroutine.running()~=watchdog','');assert mutant!=finish
r=run(setup+mutant+checks);assert r.returncode and 'Watchdog canceled itself' in r.stderr,r.stdout+r.stderr
print('PASS self-cancel watchdog negative control')

# Execute only pure builder contracts, never its build side effects.
import ast
builder=ast.parse((R/'tests/build_beam_performance_review.py').read_text())
ns={}
exec(compile(ast.Module(body=[n for n in builder.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'builder-contracts','exec'),ns)
client=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
ns['validate_cadence'](client,s)
for c,f in [(client.replace('beamFrame>=1/30','beamFrame>=1/15'),s),(client,s.replace('beamFrame>=1/30','beamFrame>=1/15'))]:
 try:ns['validate_cadence'](c,f)
 except AssertionError:pass
 else:raise AssertionError('Cadence mutant survived')
token='__BEAM_PERFORMANCE_BUILD_ID__';identity='a'*64
assert ns['stamp'](s,identity).count('local buildIdentity="'+identity+'"')==1
for bad in [s.replace(token,''),s+token]:
 try:ns['stamp'](bad,identity)
 except AssertionError:pass
 else:raise AssertionError('Identity token mutant survived')
assert s.count('buildIdentity=buildIdentity')==3,'START/ROW/RESULT identity missing'
print('PASS builder cadence/identity contracts and 4 rejection controls')

# Actual readiness helper and actual callback preamble; no phase/performance simulation.
settle=s[s.index('local function settleCamera('):s.index('connection=Run.RenderStepped:Connect')]
preamble=s[s.index('connection=Run.RenderStepped:Connect'):s.index('  if phase==4 then')]
ready_setup=r"""
local n=0;local function check(v,m)assert(v,m);n+=1 end
for _,case in ipairs({'initial-small','initial-nil','resize','replace','timeout','destroy','drift'})do
 local now=0;local os={clock=function()return now end};local buildIdentity='ready-fixture'
 local done=false;local checks=0;local rows={};local tracked={};local starts,measures=0,0;local result
 local camera,original;local readinessStarted=0;local readinessCandidate,readinessViewport,readinessSince
 local fixedFrame,fixedFov,fixedViewport;local phaseStart;local watchdog;local connection;local destruction
 local function vec(x,y)return {X=x,Y=y}end
 local candidate={ViewportSize=vec(1,1),CameraType='original',CFrame='original-frame',FieldOfView=77}
 local workspace={CurrentCamera=case=='initial-nil' and nil or candidate}
 if case=='initial-nil'then workspace.CurrentCamera=nil end
 local manager={count=0,entries={},Destroy=function()end}
 local Visuals={Clear=function()end,Budget=function()return 0,0 end}
 local last;local Http={JSONEncode=function(_,v)last=v;return ''end}
 local print=function(message)if string.find(message,'START',1,true)then starts+=1 else result=last end end
 local Enum={CameraType={Scriptable='scriptable'}};local CFrame={lookAt=function()return 'fixed-frame'end};local Vector3={new=function()return {}end}
 local UserSettings=function()return {GetService=function()return {SavedQualityLevel='Automatic'}end}end
 local destroyCallback;local script={Destroying={Connect=function(_,fn)destroyCallback=fn;return {Disconnect=function()end}end}}
 local startupConnection={Disconnect=function()end}
 local task={delay=function(_,fn)return coroutine.create(fn)end,cancel=function()end}
 local step;local Run={RenderStepped={Connect=function(_,fn)step=fn;return {Connected=true,Disconnect=function(self)self.Connected=false end}end}}
"""
ready_checks=r"""
 local function tick(t)now=t;step(.1)end
 tick(0);tick(.2);tick(.6);check(starts==0 and measures==0 and phaseStart==nil,'Measured before usable viewport')
 if case=='timeout' then
  tick(5);check(done and result.ok==false and string.find(result.error,'not ready',1,true)~=nil,'Readiness timeout failed')
  check(starts==0 and measures==0 and not connection.Connected,'Timeout started measurement')
 elseif case=='destroy' then
  destroyCallback();candidate.ViewportSize=vec(640,360);workspace.CurrentCamera=candidate;tick(1)
  check(done and result.ok==false and starts==0 and measures==0 and not connection.Connected,'Destroyed readiness resurrected')
 else
  workspace.CurrentCamera=candidate;candidate.ViewportSize=vec(640,360);tick(.7);tick(1.0)
  check(starts==0 and measures==0,'Viewport not settled')
  if case=='resize'then candidate.ViewportSize=vec(800,450);tick(1.1)
  elseif case=='replace'then candidate={ViewportSize=candidate.ViewportSize,CameraType='original',CFrame='original-frame',FieldOfView=77};workspace.CurrentCamera=candidate;tick(1.1)end
  if case=='resize' or case=='replace'then tick(1.3);check(starts==0 and measures==0,'Changed camera/viewport did not restart settling')end
  local at=(case=='resize' or case=='replace')and 1.7 or 1.3
  tick(at);check(starts==1 and measures==1 and phaseStart==at,'Stable real viewport did not start exactly once')
  check(fixedViewport==candidate.ViewportSize and camera==candidate,'Wrong camera/viewport snapshotted')
  if case=='drift'then
   candidate.ViewportSize=vec(641,360);tick(at+.1)
   check(done and result.ok==false and string.find(result.error,'Viewport changed',1,true)~=nil,'Post-start drift accepted')
  else finish(true);check(result.ok,'Ready cleanup failed')end
  check(candidate.CameraType=='original' and candidate.CFrame=='original-frame' and candidate.FieldOfView==77,'Readiness camera not restored')
 end
end
print('PASS '..n..' actual readiness helper/preamble assertions; synthetic viewport/frame delivery')
"""
def readiness_code(helper):
 return ready_setup+finish+helper+preamble+'  measures+=1\n end,debug.traceback)\n if not ok then finish(false,tostring(err))end\nend)\n'+ready_checks
r=run(readiness_code(settle));print(r.stdout,end='');assert r.returncode==0,r.stderr
for old,new,expected in [('viewport.X<64 or viewport.Y<64','viewport.X<0 or viewport.Y<0','Measured before usable viewport'),('now-readinessSince<.5','false','Viewport not settled'),('now-readinessStarted>=5','false','Readiness timeout failed'),('readinessSince=now','readinessSince=readinessSince or now','Changed camera/viewport did not restart settling'),('candidate~=readinessCandidate or ','','Changed camera/viewport did not restart settling')]:
 assert old in settle
 r=run(readiness_code(settle.replace(old,new)));assert r.returncode and expected in r.stderr,r.stdout+r.stderr
print('PASS 5 readiness negative controls (small viewport, settling, timeout, changed timestamp, camera identity)')
