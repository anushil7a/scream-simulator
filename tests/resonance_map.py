"""Execute the guarded Hall map renderer with GUI doubles."""
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
arena=root/'prototypes/resonance-arena'
layout=(arena/'Layout.luau').read_text()
source=(arena/'Map.luau').read_text()
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
local game={GetService=function()return {Shared={Config="Config"}} end}
local script={Parent={CityMapBase="Base"}}
local layout=(function()
'''
bridge=r'''
end)()
local function require(name)
 if name=="Config" then return {ResonanceLayout=layout} end
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
check(hall.Position.x+hall.Size.x<practice.Position.x,"Map visually connects the two floors")
check(portal.Position.x>=apron.Position.x and portal.Position.x+portal.Size.x<=apron.Position.x+apron.Size.x
 and portal.Position.y>=apron.Position.y and portal.Position.y+portal.Size.y<=apron.Position.y+apron.Size.y,"Portal outside protected map area")
check(layout.IsSafeApron({Z=50,X=11}) and not layout.IsSafeApron({Z=49.99,X=11})
 and not layout.IsSafeApron({Z=50,X=11.01}),"Safe boundaries drifted")
local avatar={Parent=true,Position={X=0,Z=65},CFrame={LookVector={X=0,Z=-1}}}
map.update(view,avatar)
check(view.dot.Visible and equal(view.dot.Position.x,portal.Position.x+portal.Size.x/2) and
 equal(view.dot.Position.y,portal.Position.y+portal.Size.y/2),"Player did not project onto Hall portal")
avatar.Position.Z=265
map.update(view,avatar)
local back=projected.ReturnPortal
check(view.dot.Visible and equal(view.dot.Position.x,back.Position.x+back.Size.x/2) and
 equal(view.dot.Position.y,back.Position.y+back.Size.y/2),"Player did not project onto return portal")
avatar.Position.Z=175
map.update(view,avatar)
check(not view.dot.Visible,"A player in the gap was drawn inside a floor")
map.MiniUpdate(view,avatar,1,false)
check(not view.dot.Visible and not view.nextUpdate,"Hidden map retained a player marker")
print("PASS "..count.." Hall map geometry, portal and player projection assertions")
'''
with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',suffix='.luau',dir=root/'tests',prefix='tmp_hall_',delete=False) as file:
    file.write(setup+layout+bridge+source+checks)
    path=Path(file.name)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
