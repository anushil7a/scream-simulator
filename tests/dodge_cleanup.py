"""Actual roll cleanup with mocked lifecycle state; no Roblox physics evidence."""
from pathlib import Path
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
source = (root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
start = source.index('local function finishDodge(')
end = source.index('local function dodge(', start)
checks = '''
local count=0
local function check(v,message)assert(v,message);count+=1 end
local function fixture()
 local c={};local p={Character=c};local s={lastDodge=10,knockedUntil=0}
 local r={Parent=true,Anchored=false,auto=false}
 function r:SetNetworkOwnershipAuto()self.auto=true end
 local h={Parent=true,Health=100,AutoRotate=false,PlatformStand=false}
 sessions[p]=s
 return p,s,c,r,h
end
local p,s,c,r,h=fixture()
finishDodge(p,s,c,r,h,10,11)
check(h.AutoRotate and r.auto,'Completed roll did not restore controls')
for _,kind in ipairs({'knockdown','ragdoll','new roll','new character','new session','dead','removed'})do
 p,s,c,r,h=fixture()
 if kind=='knockdown' then s.knockedUntil=12
 elseif kind=='ragdoll' then h.PlatformStand=true
 elseif kind=='new roll' then s.lastDodge=11
 elseif kind=='new character' then p.Character={}
 elseif kind=='new session' then sessions[p]={}
 elseif kind=='dead' then h.Health=0
 elseif kind=='removed' then h.Parent=nil end
 finishDodge(p,s,c,r,h,10,11)
 check(not h.AutoRotate and not r.auto,'Old roll reclaimed controls during '..kind)
end
p,s,c,r,h=fixture();r.Anchored=true
finishDodge(p,s,c,r,h,10,11)
check(h.AutoRotate and not r.auto,'Anchored root attempted ownership mutation')
p,s,c,r,h=fixture();r.Parent=nil
finishDodge(p,s,c,r,h,10,11)
check(not r.auto,'Removed root attempted ownership mutation')
print('PASS '..count..' actual roll cleanup checks with mocked lifecycle state')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.dodge_',dir=root/'tests',delete=False) as f:
    path=Path(f.name)
    f.write('local sessions={}\n'+source[start:end]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
