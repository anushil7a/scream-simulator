"""Validate actual compact-city boss locations; conservative 2-D geometry, not Studio physics."""
from collections import deque
from math import hypot
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
shared=root/'src/ReplicatedStorage/Shared'
pre='''
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local Color3={fromRGB=function()return {}end}
'''
for name,file in [('Layout','CompactLayout.luau'),('Bosses','BossCatalog.luau')]:
    pre+=f'local {name}=(function()\n'+(shared/file).read_text()+'\nend)()\n'
pre+='''
local function point(kind,p)
 print(string.format('%s\t%f\t%f',kind,p.X,p.Z))
end
point('SPAWN',Layout.Spawn)
point('MIN',Layout.BoundsMin);point('MAX',Layout.BoundsMax)
point('ZMIN',Layout.ZoneMin);point('ZMAX',Layout.ZoneMax)
for _,p in ipairs(Layout.PartSpecs)do
 local low,high=p.position.Y-p.size.Y/2,p.position.Y+p.size.Y/2
 if p.collidable and high>.25 and low<5 then
  print(string.format('SOLID\t%f\t%f\t%f\t%f',p.position.X-p.size.X/2,p.position.Z-p.size.Z/2,p.position.X+p.size.X/2,p.position.Z+p.size.Z/2))
 end
 if p.kind=='pad' then point('PAD',p.position) end
end
for _,p in ipairs(Layout.DeliveryStops) do point('WAYPOINT',p.position) end
point('WAYPOINT',Layout.CafePickup)
for _,p in ipairs(Layout.Soccer.lost) do point('WAYPOINT',p) end
local function court(t)
 print(string.format('COURT\t%f\t%f\t%f\t%f',t.min.X,t.min.Z,t.max.X,t.max.Z))
end
court(Layout.Soccer);court(Layout.Volley)
for _,b in ipairs(Bosses.Entries)do
 print(string.format('BOSS\t%s\t%d\t%f\t%f\t%f',b.id,b.level,b.x,b.z,b.radius))
end
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=root/'tests',delete=False,encoding='utf-8') as f:
    f.write(pre); tmp=Path(f.name)
try: rows=subprocess.check_output(['luau',str(tmp)],cwd=root,text=True).splitlines()
finally: tmp.unlink()
key={}; solids=[]; courts=[]; pads=[]; points=[]; bosses=[]
for line in rows:
    k,*a=line.split('\t')
    if k=='BOSS':bosses.append((a[0],int(a[1]),*map(float,a[2:])))
    elif k in ('SOLID','COURT','PAD','WAYPOINT'):
        {'SOLID':solids,'COURT':courts,'PAD':pads,'WAYPOINT':points}[k].append(tuple(map(float,a)))
    else:key[k]=tuple(map(float,a))
assert [b[1] for b in bosses]==[10,30,50,70,95],bosses
assert len({b[0] for b in bosses})==5
arena=(*key['ZMIN'],*key['ZMAX'])
def distance(x,z,r):
    x0,z0,x1,z1=r
    return hypot(max(x0-x,0,x-x1),max(z0-z,0,z-z1))
lo=key['MIN'];hi=key['MAX'];step=5; avatar=2
points_to_walk={(x,z) for x in range(int(lo[0])+step,int(hi[0]),step) for z in range(int(lo[1])+step,int(hi[1]),step)
                if min(distance(x,z,r) for r in [*solids,arena])>=avatar}
spawn=tuple(round(x/step)*step for x in key['SPAWN'])
assert spawn in points_to_walk,spawn
queue=deque([spawn]); reachable={spawn:0}
while queue:
    x,z=queue.popleft()
    for p in ((x+step,z),(x-step,z),(x,z+step),(x,z-step)):
        if p in points_to_walk and p not in reachable:
            reachable[p]=reachable[x,z]+step;queue.append(p)
for i,(name,level,x,z,radius) in enumerate(bosses):
    center=(round(x/step)*step,round(z/step)*step)
    assert center in reachable,(name,'no walkable route outside PvP')
    assert radius<=18,(name,'arena envelope exceeds review')
    clearance=min(distance(x,z,r) for r in solids)
    assert clearance>=radius+avatar,(name,'solid intersects encounter',clearance)
    assert distance(x,z,arena)>=radius+avatar,(name,'PvP overlap')
    assert min(distance(x,z,r) for r in courts)>=radius+avatar,(name,'sports overlap')
    assert min(hypot(x-a,z-b) for a,b in points)>=radius+avatar,(name,'quest marker too close')
    assert min(hypot(x-a,z-b) for a,b in pads)>=radius+54,(name,'trainer engagement too close')
    for other,_,a,b,r in bosses[:i]:assert hypot(x-a,z-b)>=radius+r+avatar,(name,other,'overlapping rings')
    print(f'{name} L{level}: {clearance:.1f}-stud solid clearance; {reachable[center]}-stud static path outside PvP')
print('PASS 5 boss sites from actual catalog/layout; no Studio traversal or rendered visibility claim')
