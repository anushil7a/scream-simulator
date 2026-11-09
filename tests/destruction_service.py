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
local now=0;local queue={};local occupied=false;local occupantCollidable=true;local checks=0
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
local deferred={}
local task={delay=schedule,defer=function(fn)table.insert(deferred,fn)end}
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
local addedCallbacks={};local removedCallbacks={}
local function signal(list)return {Connect=function(_,fn)table.insert(list,fn);return {Disconnect=function()end}end}end
local collection={GetTagged=function()return {} end,HasTag=function(_,model)return model.tagged~=false end,
 GetInstanceAddedSignal=function()return signal(addedCallbacks)end,
 GetInstanceRemovedSignal=function()return signal(removedCallbacks)end}
local game={ReplicatedStorage={Shared={DestructionRules='rules'}},GetService=function(_,name)
 if name=='Players' then return players elseif name=='CollectionService' then return collection end
 error(name)
end}
local workspace={GetServerTimeNow=function()return now end,GetPartBoundsInBox=function(_,box,size,params)return occupied and (occupantCollidable or not params.RespectCanCollide) and {1} or {} end}
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
check(m:GetAttribute('RepairBlocked')==true,'Occupied retry did not explain repair delay')
occupied=false;advance(125)
check(m:GetAttribute('RepairBlocked')==false,'Successful repair retained blocked status')
check(not m:GetAttribute('Destroyed') and m:GetAttribute('ObjectHealth')==50,'Deferred repair failed')
check(seat.CanCollide and seat.CanQuery and not seat.CanTouch and not seat.Disabled and seat.Transparency==.3 and prompt.Enabled,'Original seat/properties not restored')
check(m:GetAttribute('RepairAt')==0 and #queue==0,'Repair timer leaked')
D.Damage(seat,1,1);check(m:GetAttribute('RepairBlocked')==false,'Fresh damage retained blocked status');advance(200);D.Damage(seat,1,1);advance(245)
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
occupied=true;occupantCollidable=false;advance(840)
check(m:GetAttribute('ObjectHealth')==48 and m:GetAttribute('RepairAt')==845,'Queryable noncolliding occupant did not defer repair')
check(m:GetAttribute('RepairBlocked')==true,'Noncolliding occupant missing blocked status')
occupied=false;advance(845)
check(m:GetAttribute('ObjectHealth')==50 and #queue==0,'Repair did not resume after noncolliding occupant left')
-- Rejected input must not mutate health, scheduling or repair generations.
local beforeVersion=D.objects[m].version
for _,request in ipairs({{level=0,damage=1},{level=0/0,damage=1},{level=math.huge,damage=1},{level=1,damage=0},{level=1,damage=-1},{level=1,damage=49},{level=1,damage=0/0},{level=1,damage=math.huge},{level=1,damage='loud'}})do
 local result=D.Damage(seat,request.level,request.damage)
 check(result.reason~=nil and m:GetAttribute('ObjectHealth')==50 and D.objects[m].version==beforeVersion and #queue==0 and m:GetAttribute('RepairAt')==0,'Rejected hit mutated object or timer')
end
D.Damage(seat,1,10)
station.maintenanceVersion=D.objects[m].version
beforeVersion=D.objects[m].version
local deadline=m:GetAttribute('RepairAt')
local function unchanged(message)
 check(m:GetAttribute('ObjectHealth')==40 and D.objects[m].version==beforeVersion and m:GetAttribute('RepairAt')==deadline and #queue==1,message)
end
check(not D.FinishMaintenance(station,station.position),'Maintenance ignored quiet interval')
unchanged('Early maintenance mutated repair state')
advance(890)
check(not D.FinishMaintenance(station,station.position+vector(3,0,0)),'Distant worker repaired object')
unchanged('Distant maintenance mutated repair state')
occupied=true;occupantCollidable=false
check(not D.FinishMaintenance(station,station.position),'Maintenance restored into a noncolliding occupant')
unchanged('Occupied maintenance mutated repair state')
occupied=false
local farStation={maintenanceModel=m,maintenanceVersion=beforeVersion,position=vector(30,2,0)}
check(not D.FinishMaintenance(farStation,farStation.position),'Fabricated distant station bypassed object distance')
unchanged('Distant station mutated repair state')
check(D.FinishMaintenance(station,station.position),'Cleared maintenance guards failed to recover')
check(m:GetAttribute('ObjectHealth')==50 and m:GetAttribute('RepairAt')==0,'Valid maintenance did not restore state')
advance(965)
check(#queue==0,'Completed maintenance left timer queued')
-- A destruction repeat cannot keep extending the automatic repair deadline.
D.Damage(seat,1,48);D.Damage(seat,1,2)
local brokenDeadline=m:GetAttribute('RepairAt');beforeVersion=D.objects[m].version
check(D.Damage(seat,1,1).reason=='health','Destroyed object accepted another hit')
check(m:GetAttribute('RepairAt')==brokenDeadline and D.objects[m].version==beforeVersion and #queue==1,'Hit on destroyed prop postponed repair')
advance(brokenDeadline)
check(m:GetAttribute('ObjectHealth')==50 and #queue==0,'Destroyed object failed to repair after rejected repeat')
local world={}
function m:IsDescendantOf(candidate)return candidate==world end
D.Start(world)
addedCallbacks[1](m)
check(#deferred==1,'Added tag did not defer registration')
D.Start(world)
deferred[1]()
check(D.objects[m]==nil,'Stale deferred registration survived service restart')
addedCallbacks[1](m)
check(#deferred==1,'Stale added callback queued work after restart')
addedCallbacks[2](m);deferred[2]()
check(D.objects[m]~=nil,'Current added callback failed registration')
local registered=D.objects[m]
removedCallbacks[1](m)
check(D.objects[m]==registered,'Stale removal deleted current registration')
removedCallbacks[2](m)
check(D.objects[m]==nil and D.ids[m:GetAttribute('ObjectId')]==nil,'Current removal failed cleanup')
m.tagged=true;addedCallbacks[2](m)
m.tagged=false;removedCallbacks[2](m)
deferred[3]()
check(D.objects[m]==nil and D.ids[m:GetAttribute('ObjectId')]==nil,'Removed tag was resurrected by pending registration')
check(D.Damage(seat,1,1)==nil,'Untagged object remained damageable after pending registration')
m.tagged=true;addedCallbacks[2](m);deferred[4]()
check(D.objects[m]~=nil,'Retagged object did not register after canceled pending registration')
print('PASS '..checks..' actual Destruction service checks with mocked engine/scheduler')
'''
with tempfile.NamedTemporaryFile(mode='w', suffix='.luau', prefix='.destruction_', dir=root/'tests', delete=False) as f:
    path=Path(f.name)
    f.write(preamble+source+checks)
try:
    subprocess.run(['/opt/homebrew/bin/luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
