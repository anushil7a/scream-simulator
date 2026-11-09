"""Actual fixture snapshot counts with mock instances; no performance measurement."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'tests/StudioPerformance.server.luau').read_text();a=s.index(' local function worldCounts()');b=s.index(' local runner=',a)
setup='''
local function model(attrs,inside)return {GetAttribute=function(_,name)return attrs[name]end,IsDescendantOf=function()return inside~=false end}end
local residents={model({Working=true}),model({Working=true,ResidentActive=false}),model({}),model({Working=true},false)}
local props={model({ObjectHealth=50,ObjectMaxHealth=50}),model({ObjectHealth=10,ObjectMaxHealth=50,RepairBlocked=true}),model({ObjectHealth=0,ObjectMaxHealth=50,Destroyed=true}),model({}),model({Destroyed=true},false)}
local tags={CityResident=residents,CityDestructible=props}
local game={GetService=function()return {GetTagged=function(_,tag)return tags[tag]end}end}
local workspace={GetDescendants=function()return {{IsA=function()return true end},{IsA=function()return false end}}end}
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
print('PASS '..checks..' fixture workload count checks with mocked instances; no measured performance')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(setup+s[a:b]+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
