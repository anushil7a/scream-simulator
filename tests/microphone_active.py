"""Actual microphone + power + controls with fake input/time; no hardware evidence."""
from pathlib import Path
import ast,argparse,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
def setup_source():
    tree=ast.parse((ROOT/'tests/microphone_lifecycle.py').read_text())
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='setup' for t in n.targets))
CHECKS=r"""
end
local Mic=loadMicrophone();local n=0
local function check(ok,message)assert(ok,message);n+=1 end
local m=Mic.new();player.input.Active=false;m:Step(.05)
check(not m.ready and m.power==0,'Inactive before calibration was ready')
m:Calibrate();check(m.phase==nil and not m.ready,'Inactive input began calibration')
player.input.Active=true;m:Calibrate();check(m.phase=='quiet','Active input could not calibrate')
now+=.1;m.analyzer.RmsLevel=.001;m:Step(.05)
player.input.Active=false;m:Step(.05)
check(m.phase==nil and #m.quiet==0 and #m.spoken==0,'Inactive input retained partial calibration')
player.input.Active=true;m:Step(.05);check(m.ready and not m.model.calibrated,'Interrupted calibration silently completed or finite input failed recovery')
m:Calibrate();m.phase='voice';m.quiet={.001,.001};m.spoken={.08};player.input.Active=false;m:Step(.05)
check(m.phase==nil and #m.quiet==0 and #m.spoken==0,'Inactive voice calibration retained samples')
player.input.Active=true;m:Step(.05);check(m.ready and not m.model.calibrated,'Interrupted voice calibration completed or finite input failed recovery')
local function calibrate()
 m:Calibrate()
 for _,phase in ipairs({'quiet','voice'}) do
  for i=1,42 do now+=.05;m.analyzer.RmsLevel=phase=='quiet' and .001 or .08;m:Step(.05) end
 end
 check(m.ready and m.model.calibrated,'Active calibration failed')
end
calibrate()
player.input.Active=false
check(not m:Begin() and not m.ready,'Direct Begin missed inactive input before heartbeat')
check(m.model.calibrated,'Inactive input discarded validated calibration')
player.input.Active=true;m:Step(.05);check(m:Begin(),'Direct Release fixture failed')
for i=1,10 do m.model:Capture(1) end;now+=.3;player.input.Active=false
check(m:Release()==0 and not m.ready and m.captureStarted==nil,'Direct Release leaked cached inactive energy')
player.input.Active=true;m:Step(.05)
check(m:Begin(),'Legacy capture failed')
player.input.Active=false;m:Step(.05)
check(not m.ready and m.power==0 and m.captureStarted==nil,'Inactive input retained capture/readiness')
check(m.model.calibrated,'Inactive input discarded validated calibration')
check(not m:Begin() and m:Release()==0,'Inactive input accepted legacy capture')
check(m.status:lower():find('inactive',1,true),'Inactive status missing')
for i=1,50 do m:Step(.05) end
check(not m.ready and m.power==0 and m.model.calibrated,'Repeated inactivity changed safe state')
player.input.Active=true;m.analyzer.RmsLevel=0;m:Step(.05);check(m.ready,'Reactivation lost valid calibration')
local packets={};local control=Controls.new(Gate.new(),function(v,a)table.insert(packets,{v,a})end,function()return 1 end)
local function frames(count,rms)
 for i=1,count do
  now+=.05;m.analyzer.RmsLevel=rms;m:Step(.05);control:ObserveAvailability(m.ready,true)
  local attack=control.attack;control:Step(.05,now,m.power,m.ready,true,attack~=nil,attack and attack.sequence)
 end
end
frames(15,0);frames(15,.08);check(control.attack~=nil,'Automatic attack fixture missing')
player.input.Active=false;frames(1,.08)
check(not control.armed and not control.attack and packets[#packets][1]=='SustainedStop','Inactive input did not disarm and stop')
local stopped=#packets;frames(30,.08);check(#packets==stopped,'Inactive repeats sent more packets')
player.input.Active=true;frames(15,.08);frames(15,0);frames(15,.08)
check(m.ready and not control.armed and #packets==stopped,'Reactivation auto-rearmed attack')
control:SetArmed(true);frames(15,.08);check(#packets==stopped,'Manual resume bypassed quiet gate')
frames(15,0);frames(15,.08);check(control.attack~=nil,'Manual quiet/voice resume failed')
player.input.Muted=true;frames(1,.08);check(not m.ready and not control.armed,'Muted path regressed')
player.input.Muted=false;player.input.Active=false;m:Calibrate()
check(not m.ready and m.phase==nil and m.power==0,'Calibrate bypassed inactive guard')
player.input.Active=true;frames(1,0);check(m.ready and not control.armed,'Unmute/reactivation failed deliberate rearm')
local old=m.input;old.Parent=nil;player.input={Parent=true,Muted=false,Active=false};frames(1,0)
check(m.input~=old and not m.model.calibrated and not m.ready,'Inactive replacement retained old calibration')
player.input.Active=true;frames(1,0);check(m.ready and not m.model.calibrated,'Finite replacement failed default readiness or retained calibration')
calibrate();check(not control.armed,'Replacement recalibration silently rearmed initialized control')
control:Destroy();m:Destroy();check(m.destroyed and not m.ready,'Cleanup failed')
print('PASS',n,'actual inactive-input/controller assertions; synthetic Active transitions, not device/voice transport')
"""
def run(source,expected=None):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False) as f:
        path=Path(f.name);f.write(setup_source()+source+CHECKS)
    try:result=subprocess.run(['luau',str(path)],cwd=ROOT,text=True,capture_output=True,timeout=10)
    finally:path.unlink()
    out=result.stdout+result.stderr
    if expected:assert result.returncode and expected in out,out;print('PASS expected failure:',expected)
    else:print(out,end='');assert result.returncode==0,out
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',action='store_true');parser.add_argument('--negative-controls',action='store_true');args=parser.parse_args()
    name='src/StarterPlayer/StarterPlayerScripts/Microphone.luau'
    source=subprocess.check_output(['git','show','15df683:'+name],cwd=ROOT,text=True) if args.baseline else (ROOT/name).read_text()
    if args.baseline:run(source,'Inactive input began calibration')
    else:
        run(source)
        if args.negative_controls:
            guard='if input.Active==false then self:HandleInactive();return end'
            assert source.count(guard)==2
            run(source.replace(guard,'-- omitted calibration guard',1),'Inactive input began calibration')
            at=source.rindex(guard)
            run(source[:at]+source[at:].replace(guard,'-- omitted heartbeat guard',1),'Inactive before calibration was ready')
            begin_guard='if input.Active==false then self:HandleInactive();return false end'
            assert source.count(begin_guard)==1
            run(source.replace(begin_guard,'-- omitted direct Begin guard'),'Direct Begin missed inactive input before heartbeat')
            release_guard='if input.Active==false then self:HandleInactive();return 0,self.status end'
            assert source.count(release_guard)==1
            run(source.replace(release_guard,'-- omitted direct Release guard'),'Direct Release leaked cached inactive energy')
            start=source.index('function Microphone:HandleInactive()');end=source.index('function Microphone:Step(dt)',start)
            body=source[start:end]
            # Interrupt now independently clears readiness/capture on the first loss.
            # Remove both reset sites for this invariant control, not just its redundant line.
            changed=body.replace('self.ready=false;','').replace('self:Interrupt()','')
            assert changed!=body
            run(source[:start]+changed+source[end:],'Direct Begin missed inactive input before heartbeat')
            changed=body.replace('self:Cancel();','').replace('self:Interrupt()','')
            assert changed!=body
            run(source[:start]+changed+source[end:],'Direct Release leaked cached inactive energy')
            changed=body.replace('self.model:Reset();','self.model:Reset();self.model.calibrated=false;')
            run(source[:start]+changed+source[end:],'Inactive input discarded validated calibration')
