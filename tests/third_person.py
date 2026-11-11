"""Third-person policy with mocked player/signals; no native camera occlusion claim."""
from pathlib import Path
import argparse,json,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
a=s.index('local originalCameraMode=');b=s.index('local Config=',a);policy=s[a:b]
a=s.index('script.Destroying:Connect(function()\n p.CameraMode=');b=s.index('local function blocked()',a);cleanup=s[a:b]
for removed in ('toggleCamera','firstPerson','viewButton','Enum.KeyCode.V','LockFirstPerson','CameraToggle'):
 assert removed not in s,removed
props=json.loads((root/'default.project.json').read_text())['tree']['StarterPlayer']['$properties']
assert props['CameraMode']=='Classic' and props['CameraMinZoomDistance']>=6
setup='''local Enum={CameraMode={Classic='classic'}}
local p={CameraMode='locked',CameraMinZoomDistance=.5,CameraMaxZoomDistance=4,CharacterAdded={}}
local added,cleanup
local function connectClient(signal,fn)assert(signal==p.CharacterAdded);added=fn end
local script={Destroying={Connect=function(_,fn)cleanup=fn end}}
'''
checks='''local n=0;local function check(v,msg)assert(v,msg);n+=1 end
check(p.CameraMode=='classic' and p.CameraMinZoomDistance==6 and p.CameraMaxZoomDistance==6,'First person remains reachable')
check(type(added)=='function','Respawn callback missing')
p.CameraMode='locked';p.CameraMinZoomDistance=.5;added()
check(p.CameraMode=='classic' and p.CameraMinZoomDistance==6,'Respawn lost third-person policy')
cleanup();check(p.CameraMode=='locked' and p.CameraMinZoomDistance==.5 and p.CameraMaxZoomDistance==4,'Teardown failed to restore prior properties')
print('PASS '..n..' third-person policy checks plus removed UI/input/project contracts')
'''
def run(code,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
  path=Path(f.name);f.write(setup+code+cleanup+checks)
 try:
  r=subprocess.run(['luau',str(path)],capture_output=True,text=True);out=r.stdout+r.stderr
  if expected:assert r.returncode and expected in out,out;print('PASS negative control:',expected)
  else:print(out,end='');assert r.returncode==0,out
 finally:path.unlink()
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--negative-controls',action='store_true');args=parser.parse_args()
 run(policy)
 if args.negative_controls:
  run(policy.replace('math.max(originalMinZoom,6)','originalMinZoom'),'First person remains reachable')
  run(policy.replace('connectClient(p.CharacterAdded,applyThirdPerson)',''),'Respawn callback missing')
