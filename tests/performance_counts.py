"""Actual fixture snapshot counts with mock instances; no performance measurement."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'tests/StudioPerformance.server.luau').read_text();a=s.index(' local function worldCounts()');b=s.index(' local runner=',a)
setup='''
local summarizeHeartbeat=require('./support/HeartbeatSummary')
local function model(attrs,inside)return {GetAttribute=function(_,name)return attrs[name]end,IsDescendantOf=function()return inside~=false end}end
local residents={model({Working=true}),model({Working=true,ResidentActive=false}),model({}),model({Working=true},false)}
local props={model({ObjectHealth=50,ObjectMaxHealth=50}),model({ObjectHealth=10,ObjectMaxHealth=50,RepairBlocked=true}),model({ObjectHealth=0,ObjectMaxHealth=50,Destroyed=true}),model({}),model({Destroyed=true},false)}
local tags={CityResident=residents,CityDestructible=props}
local game={GetService=function(_,name)
 if name=='HttpService' then return {JSONEncode=function()return 'synthetic test output'end} end
 return {GetTagged=function(_,tag)return tags[tag]end}
end}
local workspace={GetAttribute=function(_,name)return name=='ReviewBuildName' and 'PerformanceReview' or 'test-source-hash' end,GetDescendants=function()return {{IsA=function()return true end},{IsA=function()return false end}}end}
local Players={GetPlayers=function()return {1,2}end}
local sessions={{sustained={protocol={active={}}}},{sustained={protocol={}}},{}}
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local c=worldCounts()
check(c.workspaceInstances==2 and c.baseParts==1 and c.players==2,'Basic snapshot incorrect')
check(c.residents==3 and c.workingResidents==1 and c.recoveringResidents==1,'Resident activity count included stale/working recovery rig')
check(c.destructibles==4 and c.damagedObjects==2 and c.destroyedObjects==1 and c.blockedRepairs==1,'Object state counts incorrect')
check(c.activeScreams==1,'Inactive/missing attack counted')
sessions={};tags.CityResident={};tags.CityDestructible={};c=worldCounts()
check(c.activeScreams==0 and c.residents==0 and c.destructibles==0,'Empty snapshot retained old counts')
local clock=0;local step=.5;local fail=false;local nestedRequest=false;local nestedResult;local runner
local os={clock=function()return clock end}
local warn=function()end
local Instance={new=function()runner={};return runner end}
local RunService={Heartbeat={Wait=function()
 if fail then error('synthetic heartbeat failure') end
 if nestedRequest then nestedRequest=false;nestedResult=runner.OnInvoke(10,'nested') end
 clock+=step;return step
end}}
'''
runner_source = 'do\n local sampleRunning=false\n' + s[b:]
runner_checks = '''
local result=runner.OnInvoke(-1,'idle')
check(result.requestedSeconds==10 and result.durationSeconds==10 and result.heartbeat.samples==20,'Minimum-duration sample incorrect')
check(result.build=='PerformanceReview' and result.sourceSha256=='test-source-hash','Sample omitted fixture identity')
check(result.before.players==2 and result.after.players==2,'Sample omitted workload snapshots')
result=runner.OnInvoke(math.huge,{})
check(result.requestedSeconds==30 and result.scenario=='unspecified','Invalid sample arguments not normalized')
result=runner.OnInvoke(999,string.rep('x',100))
check(result.requestedSeconds==120 and #result.scenario==80,'Sample duration or label not bounded')
nestedRequest=true;result=runner.OnInvoke(10,'outer')
check(nestedResult.error=='A sample is already running' and not result.error,'Overlapping sample was accepted or broke outer sample')
fail=true;result=runner.OnInvoke(10,'failure')
check(type(result.error)=='string' and string.find(result.error,'synthetic heartbeat failure',1,true),'Sampling error was not returned')
fail=false;result=runner.OnInvoke(10,'retry')
check(not result.error and result.heartbeat.samples==20,'Failed sample left runner permanently locked')
step=.0001;result=runner.OnInvoke(10,'cap')
check(result.sampleCapReached and result.heartbeat.samples==20000 and result.durationSeconds<10,'Fast synthetic samples exceeded collection cap')
print('PASS '..checks..' fixture count/runner checks with mocked instances/time; no measured performance')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(setup+s[a:b]+checks+runner_source+runner_checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
