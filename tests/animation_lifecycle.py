"""Execute actual animation scripts with mocked events/rigs; no Animator/physics evidence."""
from pathlib import Path
import subprocess
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
for _,condition in ipairs({'PlatformStand','Sit','seatPart','dead','knocked'}) do
 current.humanoid.Health=100;current.humanoid.Sit=false;current.humanoid.SeatPart=nil;current.humanoid.PlatformStand=false;knocked=0
 if condition=='seatPart' then current.humanoid.SeatPart={}
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
    finally:
        path.unlink()
