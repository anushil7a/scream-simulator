"""Run actual Destruction/RepairTimer with mocked engine objects and simulated time.
No Roblox instance, physics, networking or scheduler performance evidence.
"""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'src/ServerScriptService/Destruction.luau').read_text()
preamble = r'''
local Rules=require('../src/ReplicatedStorage/Shared/DestructionRules')
local Timer=require('../src/ServerScriptService/RepairTimer')
local now=0;local queue={};local occupied=false;local checks=0
local function check(v,msg) assert(v,msg);checks+=1 end
local function schedule(seconds,fn) table.insert(queue,{at=now+seconds,fn=fn}) end
local function advance(t)
 while true do
  table.sort(queue,function(a,b)return a.at<b.at end)
  if not queue[1] or queue[1].at>t then break end
  local entry=table.remove(queue,1);now=entry.at;entry.fn()
 end
 now=t
end
local os={clock=function()return now end}
local task={delay=schedule}
local V={};V.__index=function(v,k) if k=='Magnitude' then return math.sqrt(v.X*v.X+v.Y*v.Y+v.Z*v.Z) end;return V[k] end
local function vector(x,y,z)return setmetatable({X=x,Y=y,Z=z},V) end
V.__add=function(a,b)return vector(a.X+b.X,a.Y+b.Y,a.Z+b.Z) end
V.__sub=function(a,b)return vector(a.X-b.X,a.Y-b.Y,a.Z-b.Z) end
local Vector3={new=vector}
local color={Lerp=function(self)return self end}
local Color3={fromRGB=function()return color end}
local Enum={RaycastFilterType={Include=1}}
local OverlapParams={new=function()return {} end}
local players={GetPlayers=function()return {{Character={}}} end}
local collection={GetTagged=function()return {} end}
local game={ReplicatedStorage={Shared={DestructionRules='rules'}},GetService=function(_,name)
 if name=='Players' then return players elseif name=='CollectionService' then return collection end
 error(name)
end}
local workspace={GetServerTimeNow=function()return now end,GetPartBoundsInBox=function()return occupied and {1} or {} end}
local script={Parent={RepairTimer='timer'}}
local require=function(key) if key=='rules' then return Rules elseif key=='timer' then return Timer end;error(key) end
local function loadService()
'''
checks = r'''
end
local D=loadService()
local function model(kind,x)
 local attrs={DestructibleType=kind};local m={Parent={},attrs=attrs}
 function m:GetAttribute(key)return attrs[key] end
 function m:SetAttribute(key,value)attrs[key]=value end
 function m:GetBoundingBox()return {Position=vector(x,2,0)},vector(4,4,4) end
 local seat={Parent=m,Color=color,Transparency=.3,CanCollide=true,CanQuery=true,CanTouch=false,Disabled=false,Occupant={Sit=true}}
 function seat:IsA(class)return class=='BasePart' or class=='Seat' end
 local prompt={Parent=seat,Enabled=true}
 function prompt:IsA(class)return class=='ProximityPrompt' end
 function m:GetDescendants()return {seat,prompt} end
 D.Register(m)
 return m,seat,prompt
end
local m,seat,prompt=model('Bench',0)
check(D.Damage(seat,1,48).health==2,'Actual damage missing')
check(D.Damage(seat,1,2).destroyed,'Actual destruction missing')
check(#queue==1,'One object scheduled multiple callbacks')
check(not seat.CanCollide and not seat.CanQuery and seat.Disabled and not seat.Occupant.Sit and not prompt.Enabled,'Broken bench retained seat/collision/prompt')
occupied=true;advance(120)
check(m:GetAttribute('Destroyed') and m:GetAttribute('RepairAt')==125,'Occupied repair was not deferred')
occupied=false;advance(125)
check(not m:GetAttribute('Destroyed') and m:GetAttribute('ObjectHealth')==50,'Deferred repair failed')
check(seat.CanCollide and seat.CanQuery and not seat.CanTouch and not seat.Disabled and seat.Transparency==.3 and prompt.Enabled,'Original seat/properties not restored')
check(m:GetAttribute('RepairAt')==0 and #queue==0,'Repair timer leaked')
D.Damage(seat,1,1);advance(200);D.Damage(seat,1,1);advance(245)
check(m:GetAttribute('ObjectHealth')==48 and #queue==1,'Stale first deadline restored newer damage')
advance(320);check(m:GetAttribute('ObjectHealth')==50,'Latest deadline not used')
local tree,body=model('SmallTree',20)
check(D.Damage(body,25,10).reason=='level' and #queue==0,'Locked prop scheduled repair')
D.Damage(body,26,10);tree.Parent=nil;advance(500)
check(#queue==0 and tree:GetAttribute('ObjectHealth')==100,'Removed object was restored')
D.Damage(seat,1,10);advance(550)
local station={maintenanceModel=m,maintenanceVersion=D.objects[m].version,position=vector(0,2,0)}
check(D.FinishMaintenance(station,station.position),'Valid maintenance rejected')
D.Damage(seat,1,3);advance(620)
check(m:GetAttribute('ObjectHealth')==47,'Old pre-maintenance timer restored new damage')
advance(670);check(m:GetAttribute('ObjectHealth')==50 and #queue==0,'Post-maintenance timer leaked')
D.Damage(seat,1,1);advance(720)
station.maintenanceVersion=D.objects[m].version
D.Damage(seat,1,1)
check(not D.FinishMaintenance(station,station.position),'Stale maintenance repaired newer damage')
print('PASS '..checks..' actual Destruction service checks with mocked engine/scheduler')
'''
with tempfile.NamedTemporaryFile(mode='w', suffix='.luau', prefix='.destruction_', dir=root/'tests', delete=False) as f:
    path=Path(f.name)
    f.write(preamble+source+checks)
try:
    subprocess.run(['/opt/homebrew/bin/luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
