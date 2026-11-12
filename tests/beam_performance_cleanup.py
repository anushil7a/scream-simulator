"""Actual fixture finish/interrupt callbacks; mocked failures, not native cleanup proof."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'tests/StudioBeamPerformance.client.luau').read_text()
finish=s[s.index('local function finish('):s.index('camera.CameraType=Enum.CameraType.Scriptable;')]
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
