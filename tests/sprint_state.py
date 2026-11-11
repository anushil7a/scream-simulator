"""Actual server sprint + Action handler with simulated time/velocity; no network/physics."""
from pathlib import Path
import argparse, subprocess, tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=source.index('local function stepSprint(');b=source.index('task.spawn(function()\n local tick=0',a)
step=source[a:b]
a=source.index('action.OnServerEvent:Connect(');b=source.index('local function joined(',a)
handler=source[a:b]
setup='''local Config={SprintDuration=10,SprintRecovery=5,SprintRegenDelay=1}
local now=0;local os={clock=function()return now end}
local handler;local action={OnServerEvent={Connect=function(_,fn)handler=fn end}}
local sessions={};local p={};local stranger={}
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local function near(a,b)return math.abs(a-b)<1e-6 end
local function session()return {sprintCharge=10,sprintLockedUntil=0,sprintRequested=false,micReady=true,dodgingUntil=0,knockedUntil=0}end
local r={AssemblyLinearVelocity={X=25,Y=0,Z=0}};local h={}
local function request(s,value) sessions[p]=s;handler(p,'Sprint',value) end
local function tick(s,t,dt)now=t;return stepSprint(s,r,h,t,dt)end
local s=session();request(s,true)
check(tick(s,0,0),'Moving start rejected')
request(s,false);check(not tick(s,.1,.1) and near(s.sprintCharge,9.9),'Release refunded granted interval')
check(not tick(s,1.1,1) and near(s.sprintCharge,9.9),'Refill began before quiet delay')
tick(s,1.2,.1);check(s.sprintCharge==10,'Refill did not resume/cap')
s=session();now=0;request(s,true);tick(s,0,0)
for i=1,100 do tick(s,i*.1,.1) end
check(s.sprintCharge==0 and near(s.sprintLockedUntil,15),'Hold failed to exhaust')
for i=101,149 do now=i*.1;request(s,i%2==0);check(not tick(s,now,.1) and s.sprintCharge==0,'Spam bypassed exhaustion') end
now=15;request(s,true);check(tick(s,15,.1) and s.sprintCharge==10,'Exhaustion recovery boundary failed')
s=session();local granted=0;local exhausted=false
for i=1,1200 do
 now=i*.1;request(s,i%2==1)
 if tick(s,now,.1) then granted+=.1 end
 if s.sprintLockedUntil>now then exhausted=true end
end
check(exhausted and granted<=51,'Alternating spam still grants unbounded sprint')
print('AFTER 120s alternating: granted',granted,'charge',s.sprintCharge)
-- Repeated starts carry no client duration/charge. Malformed and unknown sessions cannot alter it.
s=session();now=200;request(s,true);tick(s,now,0)
for _,value in ipairs({1,'false',{},0/0}) do request(s,value);check(s.sprintRequested==true and s.sprintCharge==10,'Malformed sprint mutated state') end
handler(stranger,'Sprint',true);check(sessions[stranger]==nil,'Unknown player gained session')
for i=1,50 do request(s,true) end
request(s,false) -- idempotent stop must survive the common flood cap
check(not tick(s,201,1) and s.sprintRequested==false and s.sprintCharge==9,'Flooded release did not stop and bill granted interval')
for i=1,100 do check(not tick(s,201+i*.1,.1),'Released sprint auto-restarted after recovery') end
-- A delayed server loop must bill real elapsed time, not give cheap sprint after stalls.
s=session();s.sprintRequested=true;tick(s,300,0);tick(s,303,3)
check(s.sprintCharge==7,'Delayed tick undercharged sprint')
-- Standing, airborne vertical-only, missing avatar and interruptions cannot grant speed.
for _,mode in ipairs({'still','vertical','anchored','seated','seat','ragdoll','mic','dodge','knock','missing'}) do
 s=session();s.sprintRequested=true;r.Anchored=mode=='anchored';h.Sit=mode=='seated';h.SeatPart=mode=='seat' and {} or nil;h.PlatformStand=mode=='ragdoll'
 s.micReady=mode~='mic';s.dodgingUntil=mode=='dodge' and 500 or 0;s.knockedUntil=mode=='knock' and 500 or 0
 r.AssemblyLinearVelocity.X=(mode=='still' or mode=='vertical') and 0 or 25;r.AssemblyLinearVelocity.Y=mode=='vertical' and 50 or 0
 check(not stepSprint(s,mode~='missing' and r or nil,mode~='missing' and h or nil,400,.1),'Blocked sprint allowed '..mode)
 check(s.sprintCharge==10,'Idle eligibility consumed fresh stamina '..mode)
end
-- Returning to a blocked state still pays for the last interval actually granted.
s=session();s.sprintRequested=true;r.Anchored=false;h.Sit=false;h.SeatPart=nil;h.PlatformStand=false;r.AssemblyLinearVelocity.X=25
tick(s,600,0);h.Sit=true;check(not tick(s,600.1,.1) and near(s.sprintCharge,9.9),'Interruption refunded granted interval');h.Sit=false
print('PASS '..checks..' server sprint/Action checks (synthetic time, players and velocity)')
'''
def run(label,text,expected=None):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.sprint_',dir=root/'tests',delete=False,encoding='utf-8') as f:
        path=Path(f.name);f.write(setup+text+handler+checks)
    try:
        result=subprocess.run(['luau',str(path)],cwd=root,text=True,capture_output=True)
        output=result.stdout+result.stderr
        if expected:
            assert result.returncode and expected in output, (label,output)
            print('PASS negative control:',label,'->',expected)
        else:
            print(output,end='');assert result.returncode==0,output
    finally:path.unlink()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--negative-controls',action='store_true');args=parser.parse_args()
    run('baseline',step)
    if args.negative_controls:
        original=handler;handler=handler.replace(' if verb=="Sprint" and arg==false then s.sprintRequested=false;return end\n','',1)
        run('drop flooded stop',step,'Flooded release did not stop and bill granted interval');handler=original
        run('bill current request',step.replace('if s.sprintRunning then','if s.sprintRequested then',1),'Release refunded granted interval')
        run('remove refill delay',step.replace('s.sprintRegenAt=now+Config.SprintRegenDelay','s.sprintRegenAt=now'),'Refill began before quiet delay')
        run('undercharge delayed ticks',step.replace('s.sprintCharge-dt','s.sprintCharge-math.min(dt,.25)'),'Flooded release did not stop and bill granted interval')
