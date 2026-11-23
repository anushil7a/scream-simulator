"""Server action guards extracted from production; mocked character/entitlement state."""
from pathlib import Path
import subprocess
import sys
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=s.index('local function dodge(p,sideIntent)');a=s.index('\n',a)+1;b=s.index(' local cooldown=',a)
dodge=s[a:b]
a=s.index(' elseif verb=="ExtraJump" then');a=s.index('  if root and',a);b=s.index(' then',a)
jump=s[a+5:b]
setup='''
local Enum={Material={Air='air'}}
local acceptedStops,legacyStops,captureClears=0,0,0
local p={SetAttribute=function(_,key,value)assert(key=='CaptureStarted' and value==0);captureClears+=1 end}
local function cancelSustained()acceptedStops+=1 end
local VoiceCombat={Cancel=function()legacyStops+=1 end}
local premium=true;local Entitlements={CanUseMovement=function()return premium end}
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local s={micReady=true,nextDodge=0,dodgingUntil=0,knockedUntil=0,jumpOriginY=0}
local root={Anchored=false,Position={Y=5}}
local h={Sit=false,PlatformStand=false,FloorMaterial='ground'}
check(canDodge(s,root,h,10),'Standing player cannot dodge')
check(acceptedStops==1 and legacyStops==1 and captureClears==1,'Accepted dodge did not interrupt combat')
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
check(acceptedStops==1 and legacyStops==1 and captureClears==1,'Rejected dodge interrupted combat')
s.knockedUntil=12;s.nextDodge=0;check(not canDodge(s,root,h,10),'Knockdown allowed dodge')
check(acceptedStops==1 and legacyStops==1 and captureClears==1,'Knocked-down rejection interrupted combat')
s.knockedUntil=0
s.nextDodge=0;s.micReady=false;check(canDodge(s,root,h,10),'Missing mic blocked dodge')
check(acceptedStops==2 and legacyStops==2 and captureClears==2,'Accepted dodge did not interrupt combat')
h.FloorMaterial='air';check(canJump(s,root,h,10),'Missing mic blocked jump')
s.micReady=true;premium=false;check(not canJump(s,root,h,10),'Missing movement entitlement allowed jump')
premium=true;root.Position.Y=24;check(not canJump(s,root,h,10),'Height cap bypassed')
print('PASS '..checks..' actual movement eligibility checks with mocked state')
'''
def run(fragment):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.movement_',dir=root/'tests',delete=False) as f:
        path=Path(f.name);f.write(setup+'local function canDodge(session,root,humanoid,time)\nlocal sessions={[p]=session};local parts=function()return {},root,humanoid end;local os={clock=function()return time end}\n'+fragment+'\nreturn true\nend\nlocal function canJump(s,root,h,now)\nreturn '+jump+'\nend\n'+checks)
    try:
        return subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True)
    finally:
        path.unlink()

result=run(dodge)
assert result.returncode==0,result.stderr
print(result.stdout.strip())
if '--negative-controls' in sys.argv:
    cancel=next(line for line in dodge.splitlines() if 'cancelSustained' in line)
    guard=next(line for line in dodge.splitlines() if 'if not s or' in line)
    mutations=[
        (dodge.replace(cancel+'\n','').replace(guard,' if s then'+cancel+' end\n'+guard),'Rejected dodge interrupted combat'),
        (dodge.replace(cancel+'\n',''),'Accepted dodge did not interrupt combat'),
    ]
    for mutation,expected in mutations:
        result=run(mutation)
        assert result.returncode and expected in result.stderr,result.stderr
    print(f'PASS {len(mutations)} interruption negative controls')
