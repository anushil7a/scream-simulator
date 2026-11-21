"""Guard free aim and keep the aim readout backed by the camera ray."""
import re
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

client = Path(__file__).resolve().parents[1] / 'src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
source = client.read_text(encoding='utf-8')
assert not re.search(r'\b(?:LockOn|LockTarget|LockedTarget|lockContext|lockController|toggleLock|resolveLock|ButtonR3|KeyCode\.R)\b', source), 'Target lock returned'
assert 'reticle.Visible=usesCenterAim() and gameplayVisible' in source
assert re.search(r'if aimInfo.Visible then\s+local _,hit=aimRay\(\)', source)
assert re.search(r'local function releaseCapture\(source\).*?local ray,hit=aimRay\(\)', source, re.S)
assert 'return hit and hit.Position or ray.Origin+ray.Direction*1000' in source
aim = source[source.index("local function usesCenterAim()"):source.index('if remotes:GetAttribute("AutomaticVoice")')]
setup = """
local cast, projected, hit, ray
local p={Character={}}
local mouse={X=125,Y=61}
local UIS={PreferredInput='mouse',GetMouseLocation=function()return mouse end}
local half={X=320,Y=180}
local viewport=setmetatable({X=640,Y=360},{__div=function(_,divisor)
 assert(divisor==2)
 return half
end})
local camera={ViewportSize=viewport,ViewportPointToRay=function(_,x,y)
 projected={x,y}
 ray={Origin={},Direction=setmetatable({},{__mul=function(_,distance)return distance end})}
 return ray
end}
local workspace={Raycast=function(_,origin,distance,params)
 cast={origin=origin,distance=distance,params=params}
 return hit
end}
local RaycastParams={new=function()return {}end}
local Enum={RaycastFilterType={Exclude='exclude'},PreferredInput={Touch='touch',Gamepad='gamepad',KeyboardAndMouse='mouse'}}
"""
checks = """
assert(aimRay()==nil and cast==nil,'Missing camera cast a ray')
workspace.CurrentCamera=camera
camera.ViewportSize={X=1,Y=360}
assert(aimRay()==nil and cast==nil,'Unusable viewport cast a ray')
camera.ViewportSize=viewport
hit={Instance={Name='Wall'},Position={}}
local sampled, result=aimRay()
assert(sampled==ray and result==hit,'Free aim did not preserve first hit')
assert(projected[1]==125 and projected[2]==61,'Mouse aim moved off the cursor')
assert(cast.origin==ray.Origin and cast.distance==1000,'Camera ray range changed')
assert(cast.params.FilterType=='exclude' and cast.params.FilterDescendantsInstances[1]==p.Character
 and cast.params.RespectCanCollide==true,'Free aim stopped respecting avatar exclusion or cover')
local first=sampled
mouse.X=430
hit=nil
sampled, result=aimRay()
assert(projected[1]==430 and sampled==ray and sampled~=first and result==nil,'Off-target sample kept old aim')
UIS.PreferredInput=Enum.PreferredInput.Gamepad
aimRay()
assert(usesCenterAim() and projected[1]==320 and projected[2]==180,'Gamepad aim reused a parked mouse')
UIS.PreferredInput=Enum.PreferredInput.Touch
aimRay()
assert(usesCenterAim() and projected[1]==320 and projected[2]==180,'Touch aim moved off the crosshair')
UIS.PreferredInput=Enum.PreferredInput.KeyboardAndMouse
aimRay()
assert(not usesCenterAim() and projected[1]==430 and projected[2]==61,'Hybrid device did not return to mouse aim')
print('PASS free aim across mouse, touch and gamepad with camera guards, cover, hit and miss')
"""
def run(implementation, expected=None):
    with TemporaryDirectory() as folder:
        fixture = Path(folder) / 'FreeAim.luau'
        fixture.write_text(setup + implementation + checks, encoding='utf-8')
        result = subprocess.run(['luau', str(fixture)], capture_output=True, text=True)
    if expected:
        assert result.returncode and expected in result.stderr, result.stdout + result.stderr
        print('PASS control: ' + expected)
    else:
        assert result.returncode == 0, result.stderr
        print(result.stdout, end='')


run(aim)
if '--negative-controls' in sys.argv:
    run(aim.replace(' or input==Enum.PreferredInput.Gamepad', ''), 'Gamepad aim reused a parked mouse')
    run(aim.replace('usesCenterAim() and camera.ViewportSize/2 or UIS:GetMouseLocation()', 'camera.ViewportSize/2'),
        'Mouse aim moved off the cursor')
