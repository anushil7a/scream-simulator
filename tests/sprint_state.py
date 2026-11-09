"""Actual server stamina transition with synthetic velocity/time; no movement/physics evidence."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
start=source.index('local function stepSprint(')
end=source.index('task.spawn(function()\n local tick=0',start)
setup='local Config={SprintDuration=10,SprintRecovery=5}\n'
checks='''
local checks=0
local function check(v,msg)assert(v,msg);checks+=1 end
local function session()return {sprintCharge=10,sprintLockedUntil=0,sprintRequested=true,micReady=true,dodgingUntil=0,knockedUntil=0}end
local s=session();local h={};local root={AssemblyLinearVelocity={X=0,Y=0,Z=0}}
check(not stepSprint(s,root,h,0,.1) and s.sprintCharge==10,'Standing still drained stamina')
root.AssemblyLinearVelocity.Y=50
check(not stepSprint(s,root,h,.1,.1) and s.sprintCharge==10,'Vertical motion alone drained stamina')
root.AssemblyLinearVelocity.X=16
check(stepSprint(s,root,h,.2,.1) and s.sprintCharge==9.9,'Moving sprint did not drain')
for _,field in ipairs({'dodgingUntil','knockedUntil'})do
 s[field]=20;local before=s.sprintCharge
 check(not stepSprint(s,root,h,1,.1) and s.sprintCharge>=before,'Blocked movement drained sprint: '..field);s[field]=0
end
s.micReady=false;check(not stepSprint(s,root,h,1,.1),'Unavailable microphone allowed sprint');s.micReady=true
check(not stepSprint(s,nil,nil,1,.1),'Missing character allowed sprint')
h.Sit=true;check(not stepSprint(s,root,h,1,.1),'Seated passenger drained sprint');h.Sit=false
h.PlatformStand=true;check(not stepSprint(s,root,h,1,.1),'Ragdoll drained sprint');h.PlatformStand=false
s=session()
for i=1,40 do stepSprint(s,root,h,i*.25,.25) end
check(s.sprintCharge==0 and s.sprintLockedUntil==15,'Ten seconds of movement did not exhaust stamina')
check(not stepSprint(s,root,h,14.9,.1) and s.sprintCharge==0,'Five-second break was bypassed')
check(stepSprint(s,root,h,15,.1) and math.abs(s.sprintCharge-9.9)<1e-6,'Sprint did not resume at cooldown deadline')
s.sprintRequested=false;s.sprintCharge=5
check(not stepSprint(s,root,h,16,.25) and s.sprintCharge==5.5,'Released sprint failed to recharge')
s.sprintCharge=9.9;stepSprint(s,root,h,17,.25)
check(s.sprintCharge==10,'Recharge exceeded capacity')
print('PASS '..checks..' actual server sprint checks with synthetic velocity/time')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.sprint_',dir=root/'tests',delete=False) as file:
    path=Path(file.name);file.write(setup+source[start:end]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
