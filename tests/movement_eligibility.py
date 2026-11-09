"""Server action guards extracted from production; mocked character/entitlement state."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=s.index('local function dodge(p)');a=s.index(' if not s or',a);b=s.index('\n',a)
dodge=s[a:b]
a=s.index(' elseif verb=="ExtraJump" then');a=s.index('  if root and',a);b=s.index(' then',a)
jump=s[a+5:b]
setup='''
local Enum={Material={Air='air'}};local p={}
local premium=true;local Entitlements={CanUseMovement=function()return premium end}
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local s={micReady=true,nextDodge=0,dodgingUntil=0,knockedUntil=0,jumpOriginY=0}
local root={Anchored=false,Position={Y=5}}
local h={Sit=false,PlatformStand=false,FloorMaterial='ground'}
check(canDodge(s,root,h,10),'Standing player cannot dodge')
h.FloorMaterial='air';check(not canDodge(s,root,h,10),'Airborne player can dodge')
check(canJump(s,root,h,10),'Eligible airborne player cannot extra-jump')
for _,mode in ipairs({'seated','seat attachment','ragdoll','anchored'})do
 h.Sit=mode=='seated';h.SeatPart=mode=='seat attachment' and {} or nil
 h.PlatformStand=mode=='ragdoll';root.Anchored=mode=='anchored'
 h.FloorMaterial='ground';check(not canDodge(s,root,h,10),'Blocked dodge allowed: '..mode)
 h.FloorMaterial='air';check(not canJump(s,root,h,10),'Blocked jump allowed: '..mode)
end
h.Sit=false;h.SeatPart=nil;h.PlatformStand=false;root.Anchored=false
s.nextDodge=11;h.FloorMaterial='ground';check(not canDodge(s,root,h,10),'Dodge cooldown bypassed')
s.nextDodge=0;s.micReady=false;check(not canDodge(s,root,h,10),'Missing mic allowed dodge')
h.FloorMaterial='air';check(not canJump(s,root,h,10),'Missing mic allowed jump')
s.micReady=true;premium=false;check(not canJump(s,root,h,10),'Missing movement entitlement allowed jump')
premium=true;root.Position.Y=24;check(not canJump(s,root,h,10),'Height cap bypassed')
print('PASS '..checks..' actual movement eligibility checks with mocked state')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.movement_',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+'local function canDodge(s,r,h,now)\n'+dodge+'\nreturn true\nend\nlocal function canJump(s,root,h,now)\nreturn '+jump+'\nend\n'+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
