"""Execute actual animation scripts with mocked events/rigs; no Animator/physics evidence."""
from pathlib import Path
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[1]
setup=r'''
local checks=0
local function check(ok,message)assert(ok,message);checks+=1 end
local events={}
local function event()
 local e={links={}}
 function e:Connect(fn)
  local c={Connected=true,fn=fn};function c:Disconnect()self.Connected=false end
  table.insert(self.links,c);return c
 end
 function e:Fire(...)
  for _,c in ipairs(table.clone(self.links)) do if c.Connected then c.fn(...) end end
 end
 function e:Count()local count=0;for _,c in ipairs(self.links)do if c.Connected then count+=1 end end;return count end
 table.insert(events,e);return e
end
local queue={}
local task={spawn=function(fn,...)table.insert(queue,{fn=fn,args=table.pack(...)})end}
local function drain()
 local pending=queue;queue={};for _,item in ipairs(pending)do item.fn(table.unpack(item.args,1,item.args.n))end
end
local function character()
 local c={Parent=true,DescendantAdded=event(),children={Humanoid={},HumanoidRootPart={}}}
 function c:WaitForChild(name)return self.children[name] end
 function c:GetDescendants()return {} end
 return c
end
local function player()
 return {CharacterAdded=event(),CharacterRemoving=event(),Character=character()}
end
local initial=player()
local players={PlayerAdded=event(),PlayerRemoving=event(),GetPlayers=function()return {initial}end}
local run={PreAnimation=event(),PreSimulation=event()}
local script={Destroying=event()}
local collection={added=event(),removed=event(),models={}}
function collection:GetInstanceAddedSignal()return self.added end
function collection:GetInstanceRemovedSignal()return self.removed end
function collection:GetTagged()return self.models end
local shared={WaitForChild=function()return 'config' end}
local services={Players=players,RunService=run,CollectionService=collection,ReplicatedStorage={WaitForChild=function()return shared end}}
local game={GetService=function(_,name)return services[name] end}
local require=function(name)assert(name=='config');return {} end
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local CFrame={identity='identity'}
local workspace={GetServerTimeNow=function()return 100 end}
local Enum={Material={Air='Air'}}
'''
player_checks=r'''
drain()
check(rigs[initial]~=nil and initial.Character.DescendantAdded:Count()==1,'Initial rig not watched')
local current=rigs[initial]
local attrs={}
function initial.Character:SetAttribute(name,value)attrs[name]=value end
local knocked=0
function initial:GetAttribute(name)return name=='KnockdownEnds' and knocked or 0 end
for _,condition in ipairs({'PlatformStand','Sit','seatPart','dead','knocked','missingRoot','missingHumanoid'}) do
 current.root.Parent=true;current.humanoid.Parent=true
 current.humanoid.Health=100;current.humanoid.Sit=false;current.humanoid.SeatPart=nil;current.humanoid.PlatformStand=false;knocked=0
 if condition=='missingRoot' then current.root.Parent=nil
 elseif condition=='missingHumanoid' then current.humanoid.Parent=nil
 elseif condition=='seatPart' then current.humanoid.SeatPart={}
 elseif condition=='dead' then current.humanoid.Health=0
 elseif condition=='knocked' then knocked=101
 else current.humanoid[condition]=true end
 current.charge=1;current.blend=1;current.airborne=true;current.landing=99
 run.PreAnimation:Fire();run.PreSimulation:Fire(.016)
 check(current.charge==0 and current.blend==0,'Combat/locomotion pose survived '..condition)
 check(attrs.RollAnimationProgress==-1 and attrs.SprintAnimationBlend==0,'Stale visual indicators survived '..condition)
 check(not current.airborne and current.landing==0,'Stale landing survived '..condition)
end

players.PlayerAdded:Fire(initial)
check(initial.CharacterAdded:Count()==1,'Duplicate player observer')
local joint={Parent=true,Transform=3}
rigs[initial].offsets[joint]={Inverse=function()return 2 end}
players.PlayerRemoving:Fire(initial)
check(rigs[initial]==nil and watchers[initial]==nil,'Removed player retained rig/watcher')
check(initial.CharacterAdded:Count()==0 and initial.CharacterRemoving:Count()==0,'Removed player retained character listeners')
check(initial.Character.DescendantAdded:Count()==0 and joint.Transform==6,'Rig cleanup failed to disconnect/undo additive offset')
local late=player();players.PlayerAdded:Fire(late);players.PlayerRemoving:Fire(late);drain()
check(rigs[late]==nil,'Pending initial registration recreated departed player')
local live=player();players.PlayerAdded:Fire(live);drain()
local old=live.Character;live.Character=character();live.CharacterRemoving:Fire(old);live.CharacterAdded:Fire(live.Character)
check(rigs[live].character==live.Character and old.DescendantAdded:Count()==0,'Respawn retained old rig')
local delayed=player();players.PlayerAdded:Fire(delayed)
script.Destroying:Fire();drain()
check(next(rigs)==nil and next(watchers)==nil,'Script teardown retained rigs/watchers')
check(run.PreAnimation:Count()==0 and run.PreSimulation:Count()==0,'Script teardown retained frame hooks')
check(players.PlayerAdded:Count()==0 and players.PlayerRemoving:Count()==0,'Script teardown retained player hooks')
check(live.CharacterAdded:Count()==0 and live.Character.DescendantAdded:Count()==0,'Script teardown retained character hooks')
'''
resident_checks=r'''
local function resident()
 return {IsDescendantOf=function()return true end,GetAttribute=function(self,name)if name=='ResidentActive' then return self.active end;return name=='DisplayName' and 'Resident' or nil end}
end
local m=resident();collection.added:Fire(m)
check(rigs[m]~=nil,'Resident not registered')
local limb={Parent=true,Transform='pose'};local neck={Parent=true,Transform='pose'}
local piece={Transparency=0}
local ball={GetChildren=function()return {piece} end,Destroy=function(self)self.destroyed=true end}
rigs[m].joints={limb};rigs[m].neck=neck;rigs[m].practiceBall=ball
workspace.CurrentCamera={};m.active=false;rigs[m].blend=1
run.PreSimulation:Fire(.1)
check(rigs[m].suspended and rigs[m].blend==0,'Recovering resident animation was not suspended')
check(limb.Transform=='identity' and neck.Transform=='identity' and piece.Transparency==1,'Recovery retained pose or practice prop')
run.PreSimulation:Fire(.1)
check(not ball.destroyed and rigs[m]~=nil,'Suspension destroyed reusable resident visuals')


-- Actual frame callback, with partial/out-of-workspace mocked streaming states.
m.active=true
function m:FindFirstChild()return nil end
function m:FindFirstChildOfClass()return nil end
for _,inWorld in ipairs({true,false}) do
 function m:IsDescendantOf()return inWorld end
 rigs[m].suspended=false;rigs[m].blend=1;piece.Transparency=0;limb.Transform='pose'
 run.PreSimulation:Fire(.1)
 check(rigs[m].suspended and piece.Transparency==1 and limb.Transform=='identity','Unavailable rig retained detached animation/prop')
 check(not ball.destroyed and rigs[m]~=nil,'Streaming suspension discarded reusable rig')
end

collection.removed:Fire(m)
check(rigs[m]==nil and ball.destroyed,'Streamed-out resident retained visual')
check(limb.Transform=='identity' and neck.Transform=='identity','Resident cleanup retained pose')
-- Run the actual frame loop on complete rigs before the subscription teardown checks.
local clockReads=0
function workspace:GetServerTimeNow()clockReads+=1;return 100 end
CFrame.Angles=function(x,y,z)return {x=x,y=y,z=z}end
local frameMT={__mul=function(_,b)return b end}
CFrame.new=function()return setmetatable({},frameMT)end
Vector3.new=function(x,y,z)return {X=x,Y=y,Z=z,Magnitude=math.sqrt(x*x+y*y+z*z)}end
local vectorMT={__sub=function(a,b)return Vector3.new(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end}
local function joint()
 local function pose()
  return {writes=0,Lerp=function(self,target)
   local nextPose=pose();nextPose.writes=self.writes+1;nextPose.x=target.x;nextPose.z=target.z
   return nextPose
  end}
 end
 return {Parent=true,Transform=pose()}
end
local function complete(distance,attributes)
 local m=resident();m.reads={}
 function m:GetAttribute(key)
  self.reads[key]=(self.reads[key] or 0)+1
  return attributes[key]
 end
 local position=setmetatable(Vector3.new(distance,0,0),vectorMT)
 local root={Position=position,AssemblyLinearVelocity=Vector3.new(0,0,0)}
 local torso={children={}}
 for _,name in ipairs({'RootJoint','Neck',table.unpack(jointNames)})do torso.children[name]=joint()end
 function torso:FindFirstChild(name)return self.children[name]end
 local human={Health=100,FloorMaterial='Solid'}
 function m:FindFirstChild(name)return name=='Torso' and torso or root end
 function m:FindFirstChildOfClass()return human end
 collection.added:Fire(m);m.reads={}
 return m,torso.children,human
end
workspace.CurrentCamera={CFrame={Position=Vector3.new(0,0,0)}}
local garden,gardenJoints=complete(10,{Role='Gardener',Working=true,WorkStarted=98})
local crowd,crowdJoints=complete(20,{Applauding=true})
local reader,readerJoints,readerHuman=complete(125,{Reading=true})
readerHuman.SeatPart={}
local distant,distantJoints=complete(190,{})
run.PreSimulation:Fire(.025)
check(gardenJoints['Right Shoulder'].Transform.x==.9-math.sin(160)*.12,'Gardener lost work pose')
check(crowdJoints['Left Shoulder'].Transform.x==1.15 and crowdJoints['Right Shoulder'].Transform.z<0,
 'Applause changed')
check(readerJoints.Neck.Transform.writes==0 and distantJoints.Neck.Transform.writes==0,'Distance update ran too early')
check(garden.reads.Working==1 and crowd.reads.Applauding==1 and crowd.reads.Gesturing==1,
 'Pose flags read more than once per resident update')
check(clockReads==1,'Multiple clock samples in one frame')
run.PreSimulation:Fire(.025)
check(readerJoints.Neck.Transform.x==-.22 and readerJoints['Left Shoulder'].Transform.x==1.15,
 'Reading did not update at the middle distance cadence')
check(reader.reads.Reading==1 and distantJoints.Neck.Transform.writes==0,'Reading or distant cadence changed')
collection.removed:Fire(garden);collection.removed:Fire(crowd);collection.removed:Fire(reader)
local previousReads=clockReads
run.PreSimulation:Fire(.02)
check(clockReads==previousReads,'Idle frame sampled the clock')
run.PreSimulation:Fire(.14)
check(distantJoints.Neck.Transform.writes==1 and clockReads==previousReads+1,'Distant update missed its cadence')
collection.removed:Fire(distant)

collection.added:Fire(m);local second=rigs[m]
collection.added:Fire(m);check(rigs[m]==second,'Duplicate tag replaced resident state')
script.Destroying:Fire()
check(next(rigs)==nil and collection.added:Count()==0 and collection.removed:Count()==0,'Resident teardown retained subscriptions')
check(run.PreSimulation:Count()==0,'Resident teardown retained frame hook')
register(resident());check(next(rigs)==nil,'Late registration revived destroyed animator')
'''
for name,checks in [('RunAnimation.client.luau',player_checks),('Residents.client.luau',resident_checks)]:
    source=(root/'src/StarterPlayer/StarterPlayerScripts'/name).read_text()
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.animation_',dir=root/'tests',delete=False) as file:
        path=Path(file.name)
        file.write(setup+source+checks+f'\nprint("PASS "..checks.." {name} mocked lifecycle checks")\n')
    try:
        subprocess.run(['luau',str(path)],cwd=root,check=True)
        if name=='Residents.client.luau' and '--negative-controls' in sys.argv:
            for before, after, message in (
                ('if workRequested then', 'if model:GetAttribute("Working") then',
                 'Pose flags read more than once per resident update'),
                ('now=now or workspace:GetServerTimeNow()', 'now=workspace:GetServerTimeNow()',
                 'Multiple clock samples in one frame'),
            ):
                assert source.count(before)==1, before
                path.write_text(setup+source.replace(before,after)+checks,encoding='utf-8')
                result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True)
                assert result.returncode and message in result.stderr, result.stderr
                print('PASS negative control:',message)

    finally:
        path.unlink()
