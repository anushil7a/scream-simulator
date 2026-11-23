"""Execute the guarded Hall map renderer with GUI doubles."""
from pathlib import Path
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[1]
arena=root/'prototypes/resonance-arena'
layout=(arena/'Layout.luau').read_text()
source=(arena/'Map.luau').read_text()
world_source=(arena/'CombatWorld.luau').read_text()
setup=r'''
local function equal(a,b)return math.abs(a-b)<.00001 end
local count=0
local function check(ok,reason)assert(ok,reason);count+=1 end
local Color3={fromRGB=function(r,g,b)return {r=r,g=g,b=b}end}
local UDim={new=function(...)return {...}end}
local Vector2={new=function(...)return {...}end}
local UDim2={fromScale=function(x,y)return {x=x,y=y}end,fromOffset=function(x,y)return {x=x,y=y}end}
local Enum={Font={GothamBold=true},AspectType={FitWithinMaxSize=true}}
local all={}
local Instance={new=function(kind)local node={kind=kind};table.insert(all,node);return node end}
-- Access through WaitForChild can discover modules that have not replicated yet.
local function delayed(children)
 return setmetatable({WaitForChild=function(_,name)return assert(children[name],name) end},
  {__index=function(_,name) error(name.." read before replication") end})
end
local game={GetService=function()return delayed({Shared=delayed({Config="Config"})}) end}
local script={Parent=delayed({CityMapBase="Base"})}
local layout=(function()
'''
bridge=r'''
end)()
local function require(name)
 if name=="Config" then return {ResonanceLayout=layout,ResonanceTravel=travelOnly} end
 assert(name=="Base")
 return {MiniLayout=function()end}
end
local map=(function()
'''
checks=r'''
end)()
local view=map.create({},false)
local projected={}
local speakers=0
for _,node in ipairs(all)do
 if node.Name then
  projected[node.Name]=node
  if node.Name=="SpeakerCover" then speakers+=1 end
 end
end
check(speakers==8 and projected.MixingDesk,"Missing speaker or desk footprint")
check(not projected.TimberPier and not projected.Beach and projected.HallLabel.Text=="HALL","Legacy city map leaked")
local hall,practice=projected.HallFloor,projected.TrainingLanding
local portal,apron=projected.TrainingPortal,projected.SafeApron
if travelOnly then
 check(not practice and not projected.ReturnPortal and not projected.TrainingLabel,
  "Travel Hall map still advertises the absent practice deck")
else
 check(hall.Position.x+hall.Size.x<practice.Position.x,"Map visually connects the two floors")
end
check(portal.Position.x>=apron.Position.x and portal.Position.x+portal.Size.x<=apron.Position.x+apron.Size.x
 and portal.Position.y>=apron.Position.y and portal.Position.y+portal.Size.y<=apron.Position.y+apron.Size.y,"Portal outside protected map area")
check(layout.IsSafeApron({Z=50,X=11}) and not layout.IsSafeApron({Z=49.99,X=11})
 and not layout.IsSafeApron({Z=50,X=11.01}),"Safe boundaries drifted")
local dimensions=layout.ApronFootprint()
check(dimensions.width==2*layout.Apron.halfWidth and dimensions.z-dimensions.depth/2==layout.Apron.startZ
 and dimensions.z+dimensions.depth/2==layout.Combat.maxZ,"Apron footprint drifted from the PvP boundary")
check(layout.IsSafeApron({X=layout.HallEntry.x,Z=layout.HallEntry.z}) and
 math.abs(layout.HallPortal.z-3-layout.HallEntry.z)<10,"Hall arrival cannot reach the local portal")
local avatar={Parent=true,Position={X=0,Z=65},CFrame={LookVector={X=0,Z=-1}}}
map.update(view,avatar)
check(view.dot.Visible and equal(view.dot.Position.x,portal.Position.x+portal.Size.x/2) and
 equal(view.dot.Position.y,portal.Position.y+portal.Size.y/2),"Player did not project onto Hall portal")
avatar.Position.Z=265
map.update(view,avatar)
local back=projected.ReturnPortal
if travelOnly then
 check(not view.dot.Visible,"Travel Hall map marked an absent training floor")
else
 check(view.dot.Visible and equal(view.dot.Position.x,back.Position.x+back.Size.x/2) and
  equal(view.dot.Position.y,back.Position.y+back.Size.y/2),"Player did not project onto return portal")
end
avatar.Position.Z=175
map.update(view,avatar)
check(not view.dot.Visible,"A player in the gap was drawn inside a floor")
map.MiniUpdate(view,avatar,1,false)
check(not view.dot.Visible and not view.nextUpdate,"Hidden map retained a player marker")
print("PASS "..count.." Hall map geometry, portal and player projection assertions")
'''
recovery_setup=r'''
local world=(function()
 local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z} end}
 local CFrame={lookAt=function(position,target)return {Position=position,Target=target} end}
 local studio={IsStudio=function()return true end}
 local script={Parent={FindFirstChild=function()return travelOnly end}}
 local storage={Shared={ResonanceLayout={}}}
 local game={PlaceId=0,GameId=0,GetService=function(_,name)
  if name=="RunService" then return studio end
  assert(name=="ReplicatedStorage");return storage
 end}
 local function require(module)assert(module==storage.Shared.ResonanceLayout);return layout end
'''
recovery_checks=r'''
end)()
check(layout.Practice.railHeight>=12,'Practice rail is lower than the native-validated height')
local fromHall=world.FallRescue({X=0,Z=layout.HallEntry.z})
check(fromHall==nil,'Hall fall redirected to practice')
local fromPractice,text=world.FallRescue({X=42,Z=layout.Practice.z})
if travelOnly then
 check(fromPractice==nil and layout.IsSafeApron(world.SafeSpawn.Position),
  "Travel Hall fall routed to the missing practice deck")
else
 check(fromPractice and fromPractice.Position.Z==layout.PracticeEntry.z
  and fromPractice.Target.Z==layout.PracticePortal.z and text:find('training landing',1,true),
  'Practice fall did not recover facing the practice portal')
 check(world.FallRescue({X=0,Z=149})==nil and world.FallRescue({X=0,Z=150})~=nil,'Fall midgap split drifted')
end
print('PASS Hall and practice fall routing and rail height checks')
'''
def run(metadata, expected=None, world=world_source, map_source=source, travel=False):
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',suffix='.luau',dir=root/'tests',prefix='tmp_hall_',delete=False) as file:
        file.write(f"local travelOnly={str(travel).lower()}\n"+setup+metadata+bridge+map_source+checks+recovery_setup+world+recovery_checks)
        path=Path(file.name)
    try:
        result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True)
    finally:
        path.unlink()
    if expected:
        assert result.returncode and expected in result.stderr, result.stderr
        print('PASS control:',expected)
    else:
        assert result.returncode==0,result.stderr
        print(result.stdout.strip())

run(layout)
run(layout,travel=True)
if '--negative-controls' in sys.argv:
    run(layout,'Travel Hall fall routed to the missing practice deck',
        world_source.replace('if hasPractice and position.Z>=gapMiddle','if position.Z>=gapMiddle'),travel=True)
    old='if not travel then frame(map,"TrainingLanding",practice.x,practice.y,practice.w,practice.h,slate) end'
    assert source.count(old)==1
    run(layout,'Travel Hall map still advertises the absent practice deck',
        map_source=source.replace(old,old.removeprefix('if not travel then ').removesuffix(' end')),travel=True)
    for old,new,expected in [
        ('local startZ,endZ=Layout.Apron.startZ,','local startZ,endZ=Layout.Apron.startZ+1,','Apron footprint drifted from the PvP boundary'),
        ('HallEntry={x=0,z=54}','HallEntry={x=0,z=52}','Hall arrival cannot reach the local portal'),
        ('railHeight=12','railHeight=9','Practice rail is lower than the native-validated height'),
    ]:
        assert layout.count(old)==1
        run(layout.replace(old,new),expected)
    run(layout,'Practice fall did not recover facing the practice portal',world_source.replace('position.Z>=gapMiddle','position.Z>Layout.Practice.z'))
    for name in ('Shared', 'Config', 'CityMapBase'):
        wait=':WaitForChild("'+name+'")'
        assert source.count(wait)==1
        run(layout,name+' read before replication',map_source=source.replace(wait,'.'+name))
