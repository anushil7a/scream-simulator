"""Actual production Catalog/Layout arena geometry; analytically test floor and headroom, not native physics."""
from math import sin, cos, radians, hypot, ceil
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
shared=root/'src/ReplicatedStorage/Shared'
pre='''
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local Color3={fromRGB=function()return {}end}
'''
pre+='local Layout=(function()\n'+(shared/'CompactLayout.luau').read_text()+'\nend)()\n'
pre+='local script={Parent={CompactLayout="Layout"}}\nlocal function require(name) assert(name=="Layout");return Layout end\n'
pre+='local Catalog=(function()\n'+(shared/'BossCatalog.luau').read_text()+'\nend)()\n'
pre+='''
for _,p in ipairs(Layout.PartSpecs) do
 if p.collidable then
  local o,s,r=p.position,p.size,p.rotation
  print("P",p.id,p.shape or "Block",o.X,o.Y,o.Z,s.X,s.Y,s.Z,r.X,r.Y,r.Z)
 end
end
for _,b in ipairs(Catalog.Entries) do print("B",b.id,b.x,b.y,b.z,b.radius,b.engageHeight) end
local a,z=Layout.ZoneMin,Layout.ZoneMax; print("ZONE",a.X,a.Z,z.X,z.Z)
local a,z=Layout.BoundsMin,Layout.BoundsMax; print("BOUNDS",a.X,a.Z,z.X,z.Z)
for _,sports in ipairs({Layout.Soccer,Layout.Volley}) do local a,z=sports.min,sports.max;print("SPORT",a.X,a.Z,z.X,z.Z) end
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=root/'tests',delete=False,encoding='utf-8') as f:
    f.write(pre); tmp=Path(f.name)
try: rows=subprocess.check_output(['luau',str(tmp)],cwd=root,text=True).splitlines()
finally: tmp.unlink()
parts=[]; bosses=[]; sports=[]; zone=bounds=None
def matrix(rotation):
    a,b,c=map(radians,rotation);ca,sa,cb,sb,cc,sc=cos(a),sin(a),cos(b),sin(b),cos(c),sin(c)
    return ((cb*cc+sb*sa*sc,-cb*sc+sb*sa*cc,sb*ca),(ca*sc,ca*cc,-sa),(-sb*cc+cb*sa*sc,sb*sc+cb*sa*cc,cb*ca))
for row in rows:
    k,*a=row.split()
    if k=='P':
        name,shape=a[:2]; x,y,z,sx,sy,sz,rx,ry,rz=map(float,a[2:]);m=matrix((rx,ry,rz)); hs=(sx/2,sy/2,sz/2)
        span=tuple(sum(abs(m[i][j])*hs[j] for j in range(3)) for i in range(3))
        parts.append((name,shape,(x,y,z),m,hs,span))
    elif k=='B': bosses.append((a[0],*map(float,a[1:])))
    elif k=='ZONE': zone=tuple(map(float,a))
    elif k=='BOUNDS': bounds=tuple(map(float,a))
    elif k=='SPORT': sports.append(tuple(map(float,a)))
def intersects(x,z,start,part):
    name,shape,pos,m,hs,span=part
    if abs(x-pos[0])>span[0]+.0001 or abs(z-pos[2])>span[2]+.0001:return None
    o=[sum((v-pos[j])*m[j][i] for j,v in enumerate((x,start,z))) for i in range(3)];dv=[-m[1][i] for i in range(3)]
    lo,hi=-1e9,1e9
    for i in range(3):
        if abs(dv[i])<1e-8:
            if abs(o[i])>hs[i]+1e-7:return None
        else:
            a,b=sorted(((-hs[i]-o[i])/dv[i],(hs[i]-o[i])/dv[i]))
            lo=max(lo,a);hi=min(hi,b)
    if lo>hi+1e-7:return None
    if shape=='Cylinder':
        # Authored horizontal-plane cylinders use a vertical local X-axis.
        assert abs(dv[0])>.99,(name,'unsupported tilted cylinder')
        hit=[o[i]+lo*dv[i] for i in range(3)]
        if (hit[1]/hs[1])**2+(hit[2]/hs[2])**2>1+1e-7:return None
    return start-lo,start-hi,name

def clearance(x,z,r):
    a,b,c,d=r
    return hypot(max(0,a-x,x-c),max(0,b-z,z-d))

assert sorted(b[0] for b in bosses)==['conductor','golem','ignis','leviathan','metronome']
for name,x,y,z,r,h in bosses:
    assert r>22 and h==12,(name,'arena radius grew, vertical envelope unchanged')
    margin=r+2
    a,b,c,d=bounds
    assert a+margin<=x<=c-margin and b+margin<=z<=d-margin,(name,'world edge')
    assert min(clearance(x,z,bounds) for bounds in [zone,*sports])>=margin,(name,'dedicated gameplay overlap')
    assert all(name==other or hypot(x-ox,z-oz)>=r+ro+2 for other,ox,_,oz,ro,_ in bosses)
    near=[p for p in parts if abs(p[2][0]-x)<=p[5][0]+margin and abs(p[2][2]-z)<=p[5][2]+margin and p[2][1]+p[5][1]>=y-.5]
    samples=0
    # 1-stud radial and no more than 1-stud angular spacing, including avatar margin.
    for distance in range(ceil(margin)+1):
        if distance>margin:distance=margin
        segments=max(1,ceil(2*3.141593*distance))
        for i in range(segments):
            angle=2*3.141592653589793*i/segments
            xx=x+cos(angle)*distance;zz=z+sin(angle)*distance
            hits=[result for p in near if (result:=intersects(xx,zz,y+25,p))]
            supports=[hi for hi,lo,_ in hits if hi<=y+.5]
            assert supports and max(supports)>=y-.5,(name,'floor',(xx,zz),hits)
            blocking=[n for hi,lo,n in hits if hi>y+.5 and lo<y+7]
            assert not blocking,(name,'walkable headroom',(xx,zz),blocking)
            samples+=1
    print(f'{name}: {r:g}-stud arena, {samples} floor/headroom samples incl. 2-stud clearance')
print('PASS: all five actual production homes, boss ring geometry, map and dedicated gameplay separation')
