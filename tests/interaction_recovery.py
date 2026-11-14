"""Actual shared interaction rule with mocked geometry; no physics/raycast evidence."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ReplicatedStorage/Shared/InteractionRules.luau').read_text()
setup='''
local raycasts=0
local workspace={Raycast=function()raycasts+=1;return nil end}
local RaycastParams={new=function()return {}end}
local Enum={RaycastFilterType={Exclude=1}}
local position=setmetatable({},{__sub=function()return {Magnitude=5}end})
local function character()
 local c={root={Position=position},humanoid={Health=100,PlatformStand=false}}
 function c:FindFirstChild()return self.root end
 function c:FindFirstChildOfClass()return self.humanoid end
 return c
end
local function loadRules()
'''
checks='''
end
local Rules=loadRules();local a,b=character(),character();local checks=0
local function check(v,msg)assert(v,msg);checks+=1 end
check(Rules.CanReachNpc(a,b,14),'Standing interaction failed')
local before=raycasts
a.humanoid.PlatformStand=true
check(not Rules.CanReachNpc(a,b,14),'Knocked player could interact')
check(raycasts==before,'Knocked player performed unnecessary cover query')
a.humanoid.PlatformStand=false;b.humanoid.PlatformStand=true
check(not Rules.CanReachNpc(a,b,14),'Knocked resident could interact')
check(raycasts==before,'Knocked resident performed unnecessary cover query')
b.humanoid.PlatformStand=false
check(Rules.CanReachNpc(a,b,14),'Recovered interaction failed')
print('PASS '..checks..' shared interaction recovery checks with mocked geometry')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(setup+s+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
