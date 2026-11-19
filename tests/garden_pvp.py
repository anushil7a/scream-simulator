"""Exact active Map10 PvP source, outline, ground markings and combat authority (Luau/doubles)."""
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
shared=ROOT/'src/ReplicatedStorage/Shared'
server=ROOT/'src/ServerScriptService'
layout=(shared/'CompactLayout.luau').read_text()
config=(shared/'Config.luau').read_text()
city=(server/'CompactCity.luau').read_text()
combat=(server/'CombatRules.luau').read_text().split('\n',1)[1]
catalog=(shared/'BossCatalog.luau').read_text()
authority='\n'.join(line for line in config.splitlines() if line.startswith(('function Config.InGardenPvp(', 'function Config.InArena(')))
assert len(authority.splitlines())==2
setup=r'''
local checks=0
local function check(value,msg) assert(value,msg);checks+=1 end
local mt={__sub=function(a,b)
 local x,y,z=a.X-b.X,a.Y-b.Y,a.Z-b.Z
 return {Magnitude=math.sqrt(x*x+y*y+z*z)}
end}
local V=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},mt)end
local Vector3={new=V,zero=V(0,0,0)}
local Color3={fromRGB=function(...) return {...} end}
local cfmt={__mul=function(a,b)return a end}
local CFrame={new=function(...)return setmetatable({},cfmt) end,Angles=function(...)return setmetatable({},cfmt) end}
local Enum={Material=setmetatable({},{__index=function(_,k)return k end}),PartType={Cylinder="Cylinder",Ball="Ball"},KeyCode={F="F"}}
local parts={}
local Instance={new=function(class)
 local attributes={}
 local object={ClassName=class,Attributes=attributes,SetAttribute=function(_,k,v)attributes[k]=v end}
 table.insert(parts,object)
 return object
end}
'''
links=r'''
local CompactLayout=Layout
local Config={CompactCity=true,ZoneMin=Layout.ZoneMin,ZoneMax=Layout.ZoneMax}
local script={Parent={CompactLayout="CompactLayout"}}
local game={GetService=function() return {Shared={CompactLayout="CompactLayout"}} end}
local require=function(key) assert(key=="CompactLayout");return Layout end
'''
checks=r'''
local function inside(r,x,z)return x>=r.minX and x<=r.maxX and z>=r.minZ and z<=r.maxZ end
local raw={}
local spine
local byName={}
for _,p in ipairs(Layout.PartSpecs) do
 byName[p.id]=p
 if p.id:match("^CentralGardenTerrace%d+$") or p.id=="GardenSpine" then
  local o,d=p.position,p.size
  local foot={minX=o.X-d.X/2,maxX=o.X+d.X/2,minZ=o.Z-d.Z/2,maxZ=o.Z+d.Z/2}
  if p.id=="GardenSpine" then spine=foot
  else
   check(p.collidable and o.Y+d.Y/2==16,p.id.." differs from flat green ground")
   table.insert(raw,foot)
  end
 end
end
check(#raw==5 and #Layout.GardenPvpRects>=5 and #Layout.GardenPvpEdges>0,"missing authored bounds")
local function rampFoot(p)
 local a,b,c=math.rad(p.rotation.X),math.rad(p.rotation.Y),math.rad(p.rotation.Z)
 local x1,x2,z1,z2=math.huge,-math.huge,math.huge,-math.huge
 for _,xx in ipairs({-1,1}) do for _,zz in ipairs({-1,1}) do
  local x,y,z=xx*p.size.X/2,p.size.Y/2,zz*p.size.Z/2
  x,y=x*math.cos(c)-y*math.sin(c),x*math.sin(c)+y*math.cos(c)
  y,z=y*math.cos(a)-z*math.sin(a),y*math.sin(a)+z*math.cos(a)
  x,z=x*math.cos(b)+z*math.sin(b)+p.position.X,-x*math.sin(b)+z*math.cos(b)+p.position.Z
  x1,x2,z1,z2=math.min(x1,x),math.max(x2,x),math.min(z1,z),math.max(z2,z)
 end end
 -- Route top-face endpoints are authored at integral world coordinates.
 return {minX=math.round(x1),maxX=math.round(x2),minZ=math.round(z1),maxZ=math.round(z2)}
end
local ramp1,ramp2=rampFoot(byName.AcademyGarden),rampFoot(byName.VolcanoBridgeSouth)
local function oracle(x,z)
 if inside(spine,x,z) or inside(ramp1,x,z) or inside(ramp2,x,z) then return false end
 for _,r in ipairs(raw) do if inside(r,x,z) then return true end end
 return false
end
for x=-255,195 do for z=-185,215 do
 for _,d in ipairs({0,.5}) do
  local a,b=x+d,z+d
  check(Config.InGardenPvp(V(a,19,b))==oracle(a,b),"exact authored PvP union mismatch")
 end
end end
for i,a in ipairs(Layout.GardenPvpRects) do
 check(a.minX<a.maxX and a.minZ<a.maxZ,"degenerate zone")
 for j=1,i-1 do local b=Layout.GardenPvpRects[j]
  check(math.min(a.maxX,b.maxX)<=math.max(a.minX,b.minX) or math.min(a.maxZ,b.maxZ)<=math.max(a.minZ,b.minZ),"overlapping rectangle interiors")
 end
end
check(Layout.GardenPvpMinY==16 and Layout.GardenPvpMaxY==30,"wrong arena height ceiling")
check(Config.InGardenPvp(V(0,16,0)) and Config.InGardenPvp(V(0,30,0)),"inclusive height")
check(not Config.InGardenPvp(V(0,15.99,0)) and not Config.InGardenPvp(V(0,30.01,0)) and not Config.InGardenPvp(V(0,35,0)),"wrong platform vertical eligibility")
check(not Config.InArena(Layout.Spawn) and not Config.InArena(Layout.CafePickup),"spawn or cafe unexpectedly PvP")
check(not Config.InArena(V(-25,19,120)) and not Config.InArena(V(-40,19,118)),"NPC destinations must stay safe")
check(not Config.InArena(V(-226,15,110)) and not Config.InArena(V(80,19,170)),"west/seaside ramp gap")
check(Config.InGardenPvp(V(175,19,110)) and not Config.InGardenPvp(V(169,19,110)),"safe lane extends past actual paving")
check(not Config.InGardenPvp(V(-90,22,-98)) and not Config.InGardenPvp(V(180,22,40)),"overlapping elevated ramp unsafe")
for _,q in ipairs(Layout.QuestMarkers) do check(not Config.InArena(q.position),q.id.." unexpectedly in active arena") end
for _,q in ipairs(Layout.DeliveryStops) do check(not Config.InArena(q.position),q.id.." unexpectedly in active arena") end
for _,q in ipairs(Layout.MapLandmarks) do
 if q.name~="3 Stadium" then check(not Config.InArena(V(q.x,q.y+3,q.z)),q.name.." unexpectedly in arena") end
end
for _,q in ipairs({Layout.Soccer.center,Layout.Volley.center}) do check(not Config.InArena(q),"sports unexpectedly in PvP") end
for _,t in ipairs(Layout.TrainingHomes) do check(not Config.InArena(V(t.x,t.y+3,t.z)),"training home is not PvP") end
for _,b in ipairs(Bosses.Entries) do
 for _,r in ipairs(Layout.GardenPvpRects) do
  local dx=math.max(r.minX-b.x,0,b.x-r.maxX)
  local dz=math.max(r.minZ-b.z,0,b.z-r.maxZ)
  check(dx*dx+dz*dz>(b.radius+2)^2,b.id.." arena overlaps garden")
 end
end

-- All unit-length boundary edges exactly once, complete and exterior-only.
local outline={}
local function key(x,z,vertical) return x..","..z..","..tostring(vertical) end
for _,edge in ipairs(Layout.GardenPvpEdges) do
 local vert=edge.x1==edge.x2
 local length=vert and edge.z2-edge.z1 or edge.x2-edge.x1
 check((vert or edge.z1==edge.z2) and length>=1,"bad boundary direction")
 for n=0,length-1 do
  local x=edge.x1+(vert and 0 or n)
  local z=edge.z1+(vert and n or 0)
  local k=key(x,z,vert)
  check(outline[k]==nil,"duplicate boundary seam")
  outline[k]=true
  local cx,cz=x+(vert and 0 or .5),z+(vert and .5 or 0)
  check(oracle(cx+.25*edge.inX,cz+.25*edge.inZ) and not oracle(cx-.25*edge.inX,cz-.25*edge.inZ),"outline is an interior seam or wrong normal")
 end
end
for x=-251,191 do for z=-181,211 do
 check((outline[key(x,z,true)]==true)==(oracle(x-.25,z+.5)~=oracle(x+.25,z+.5)),"missing vertical edge")
 check((outline[key(x,z,false)]==true)==(oracle(x+.5,z-.25)~=oracle(x+.5,z+.25)),"missing horizontal edge")
end end

local world={}
City.Build(world)
local count=0
for _,stripe in ipairs(parts) do
 if stripe.Parent and stripe.Parent.Name=="GardenPvPBoundary" then
  count+=1
  check(stripe.Anchored and not stripe.CanCollide and not stripe.CanTouch and not stripe.CanQuery and not stripe.CastShadow,"stripe affects physics/rays")
  check(next(stripe.Attributes)==nil and stripe.Position.Y>16 and stripe.Position.Y<16.15,"stripe isn't cosmetic ground line")
  for _,i in ipairs({-1,1}) do for _,j in ipairs({-1,1}) do
   check(oracle(stripe.Position.X+i*stripe.Size.X/2,stripe.Position.Z+j*stripe.Size.Z/2),"stripe overlaps paved ramp or floats outside floor")
  end end
 end
end
check(count==#Layout.GardenPvpEdges and count<32,"marker count budget")

check(Config.InArena(V(-420,-20,30)) and Config.InArena(V(-240,14,210)) and not Config.InArena(V(-330,14.01,100)),"stadium bounds changed")
local north,south,safe,lower=V(0,19,94),V(0,19,126),V(0,19,96),V(0,3,94)
check(Rules.CanTarget(north,south,4,4,40),"existing targeted PvP permission can't enter new garden")
check(not Rules.CanTarget(north,south,5,4,40) and not Rules.CanTarget(north,south,4,4,3),"protection or distance rules changed")
check(not Rules.CanTarget(north,safe,0,1,40) and not Rules.CanTarget(lower,north,0,1,40),"safe route or another level allows targeting")
Config.CompactCity=false
check(not Config.InGardenPvp(north) and not Config.InArena(north),"garden leaked into noncompact variant")
Config.CompactCity=true
Layout.MapId="HistoricalFixture"
check(not Config.InGardenPvp(north) and not Config.InArena(north),"garden leaked into unrelated layout")
print("PASS "..checks.." actual-source geometry, cosmetic marking and PvP authority assertions; "..#Layout.GardenPvpRects.." rectangles, "..count.." exterior segments; no native claims")
'''
def module(name,content):
    return f'\nlocal {name}=(function()\n{content}\nend)()\n'
src=setup+module('Layout',layout)+links+authority+module('Bosses',catalog)+module('City',city)+module('Rules',combat)+checks
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=ROOT/'tests',delete=False) as f:
    f.write(src);path=Path(f.name)
try:
    subprocess.run(['luau',str(path)],cwd=ROOT,check=True)
finally:
    path.unlink()
