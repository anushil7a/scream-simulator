"""Read-only full-world analytic audit. Not native avatar/streaming certification.
Run from any directory; accepts --geometry and --part-budget. No output files written.
"""
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SOLID_TAGS={'SolidObstacle','GateRail','CollisionSolid','Cover','ArenaPillar','Building','Wall','Rail','Trunk'}
DECOR_TAGS={'Decoration','Decorative','Cosmetic','Water','Foam','Light','Glow','Foliage','Canopy','Trim','Sign','VFX','Marker','Optical','NonPhysical'}

def rotation(degrees):
    x,y,z=np.radians(degrees);cx,cy,cz=np.cos([x,y,z]);sx,sy,sz=np.sin([x,y,z])
    return np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]) @ np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]) @ np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])

def hits(part, starts, directions, lengths):
    """Batch finite ray vs oriented block/elliptical cylinder; t in world studs."""
    rot=rotation(part.get('rotation',[0,0,0]));half=np.array(part['size'])/2
    o=(starts-np.array(part['position']))@rot;d=directions@rot
    lo=np.zeros(len(starts));hi=np.array(lengths,dtype=float);valid=np.ones(len(starts),bool)
    shape=part.get('shape','Block')
    for i in ([0] if shape=='Cylinder' else range(3)):
        parallel=abs(d[:,i])<1e-10
        valid &= ~parallel | (abs(o[:,i])<=half[i]+1e-7)
        denom=np.where(parallel,1,d[:,i]);a=(-half[i]-o[:,i])/denom;b=(half[i]-o[:,i])/denom
        lo=np.maximum(lo,np.where(parallel,-np.inf,np.minimum(a,b)))
        hi=np.minimum(hi,np.where(parallel,np.inf,np.maximum(a,b)))
    if shape=='Cylinder':
        u=o[:,1:]/half[1:];v=d[:,1:]/half[1:]
        a=np.sum(v*v,axis=1);b=2*np.sum(u*v,axis=1);c=np.sum(u*u,axis=1)-1
        parallel=a<1e-12;disc=b*b-4*a*c
        valid &= np.where(parallel,c<=1e-7,disc>=0)
        denom=np.where(parallel,1,2*a);q=np.sqrt(np.maximum(0,disc))
        lo=np.maximum(lo,np.where(parallel,-np.inf,(-b-q)/denom))
        hi=np.minimum(hi,np.where(parallel,np.inf,(-b+q)/denom))
    elif shape=='Ball':
        u=o/half;v=d/half
        a=np.sum(v*v,axis=1);b=2*np.sum(u*v,axis=1);c=np.sum(u*u,axis=1)-1
        parallel=a<1e-12;disc=b*b-4*a*c
        valid &= np.where(parallel,c<=1e-7,disc>=0)
        denom=np.where(parallel,1,2*a);q=np.sqrt(np.maximum(0,disc))
        lo=np.maximum(lo,np.where(parallel,-np.inf,(-b-q)/denom))
        hi=np.minimum(hi,np.where(parallel,np.inf,(-b+q)/denom))
    # The wedge OBB is conservative for headroom; no arterial uses a wedge for support.
    return valid & (lo<=hi+1e-7),lo

def audit(data,layout,budget):
    errors=[];parts=data['parts'];routes=data['routes'];ids=[p['id'] for p in parts]
    if len(ids)!=len(set(ids)):errors.append('Duplicate part IDs')
    if len(parts)>budget:errors.append(f'Part budget exceeded: {len(parts)} > {budget}')
    solids=[];nonphysical=Counter()
    for p in parts:
        if any(not math.isfinite(v) for k in ['position','size','rotation'] for v in p.get(k,[0,0,0])) or min(p['size'])<=0:
            errors.append(f"Invalid geometry: {p['id']}");continue
        tags=set(p.get('tags',[]));role=p.get('collisionRole',p.get('CollisionRole',p.get('attributes',{}).get('CollisionRole')))
        if role=='Solid' or tags&SOLID_TAGS:
            if not p.get('collidable') or p.get('queryable',True) is False:errors.append(f"Pass-through solid obstacle: {p['id']}")
        if p.get('collidable'):
            if p.get('shape','Block') not in ('Block','Cylinder','Ball','Wedge'):errors.append(f"Unsupported collision shape: {p['id']}")
            solids.append(p)
        else:
            for tag in tags:nonphysical[tag]+=1
            if role not in ('Decorative','Decoration','Optical','NonPhysical') and not tags&DECOR_TAGS:
                errors.append(f"Nonphysical part needs explicit decorative exception: {p['id']} tags={sorted(tags)}")
    expected={tuple(sorted(x)) for x in layout['plannedZone09Links']};found=set();graph=defaultdict(set);edge_routes=defaultdict(list)
    samples=0
    for r in routes:
        a=np.array(r['a'],dtype=float);b=np.array(r['b'],dtype=float);delta=b-a
        horizontal=math.hypot(delta[0],delta[2]);length=float(np.linalg.norm(delta));width=r['width']
        link=r.get('link',r.get('districts'))
        if link:
            edge=tuple(sorted(str(x).zfill(2) for x in link));found.add(edge)
            if len(edge)==2:
                graph[edge[0]].add(edge[1]);graph[edge[1]].add(edge[0]);edge_routes[edge].append(r)
        minimum=32 if link or r.get('class')=='arterial' else 24 if r.get('class','main')=='main' else 8
        angle=math.degrees(math.atan2(abs(delta[1]),horizontal))
        if not math.isfinite(width) or width<minimum:errors.append(f"{r['id']}: width {width} < {minimum}")
        if horizontal<.001 or angle>layout['rampLimitDegrees']+1e-6:
            errors.append(f"{r['id']}: invalid route/slope {angle:.2f}");continue
        side=np.array([delta[2]/horizontal,0,-delta[0]/horizontal])
        ts=np.linspace(0,1,max(2,math.ceil(length/2)+1))
        offsets=np.linspace(-width/2+1.5,width/2-1.5,max(3,math.ceil((width-3)/4)+1))
        points=np.array([a+t*delta+side*off for t in ts for off in offsets]);samples+=len(points)
        starts=points+np.array([0,.25,0]);directions=np.tile([0,-1,0],(len(points),1));lengths=np.full(len(points),.5)
        support=np.zeros(len(points),bool);blocked=np.zeros(len(points),bool)
        ceiling=16 if r.get("class") in ("main","arterial") else 6
        # Conservative horizontal AABB filter only excludes solids impossible to intersect.
        low=points.min(axis=0);high=points.max(axis=0)
        for p in solids:
            extent=abs(rotation(p.get('rotation',[0,0,0])))@(np.array(p['size'])/2);pos=np.array(p['position'])
            if any(pos[i]+extent[i]<low[i]-1e-6 or pos[i]-extent[i]>high[i]+1e-6 for i in [0,2]):continue
            # Wedge OBB is conservative for obstruction only; never claim floor support from one.
            if p.get('shape','Block')!='Wedge':
                mask,_=hits(p,starts,directions,lengths);support |=mask
            mask,_=hits(p,points+np.array([0,.65,0]),np.tile([0,1,0],(len(points),1)),np.full(len(points),ceiling-.65));blocked |=mask
        if not support.all():errors.append(f"{r['id']}: {int((~support).sum())}/{len(points)} unsupported floor samples; first={points[~support][0].round(2).tolist()}")
        if blocked.any():errors.append(f"{r['id']}: {int(blocked.sum())}/{len(points)} blocked 0.65..{ceiling}stud clearance samples; first={points[blocked][0].round(2).tolist()}")
        print(f"ROUTE {r['id']} length={length:.1f} width={width} slope={angle:.2f} samples={len(points)}")
    for edge,segments in edge_routes.items():
        # Metadata connectivity alone is insufficient: require one endpoint-linked chain.
        nodes=defaultdict(set)
        key=lambda p:tuple(round(float(v),3) for v in p)
        for segment in segments:
            a,b=key(segment['a']),key(segment['b']);nodes[a].add(b);nodes[b].add(a)
        reached=set();todo=[next(iter(nodes))]
        while todo:
            n=todo.pop()
            if n in reached:continue
            reached.add(n);todo.extend(nodes[n]-reached)
        if len(reached)!=len(nodes):errors.append(f'{edge}: disconnected physical route segments')
        for district in edge:
            spec=layout['districts'].get(district,{})
            if 'center' not in spec:continue
            x,y,z=spec['center'];w,d=spec['size']
            if not any(abs(p[0]-x)<=w/2+.25 and abs(p[2]-z)<=d/2+.25 and abs(p[1]-y)<=.25 for p in nodes):
                errors.append(f'{edge}: no route endpoint joins district {district} floor envelope')
    if found!=expected:errors.append(f'Link coverage mismatch missing={sorted(expected-found)} extra={sorted(found-expected)}')
    seen=set();queue=['01']
    while queue:
        n=queue.pop()
        if n in seen:continue
        seen.add(n);queue.extend(graph[n]-seen)
    if seen!=set(layout['districts']):errors.append(f'Disconnected district graph: reached={sorted(seen)}')
    print(f'PARTS total={len(parts)} solid={len(solids)} budget={budget}; routes={len(routes)} samples={samples}; edges={len(found)}')
    print('NONPHYSICAL TAGS',dict(sorted(nonphysical.items())))
    return errors

def self_test():
    # Actual cylinder, not an OBB: corner ray must miss circular face.
    p={'position':[0,-1,0],'size':[2,10,10],'rotation':[0,0,90],'shape':'Cylinder'}
    starts=np.array([[0,2,0],[4.9,2,4.9]],dtype=float)
    mask,_=hits(p,starts,np.array([[0,-1,0],[0,-1,0]]),[5,5])
    assert mask.tolist()==[True,False]
    layout={'plannedZone09Links':[['01','02']],'districts':{'01':{},'02':{}},'rampLimitDegrees':32}
    floor={'id':'floor','position':[0,-1,10],'size':[40,2,24],'rotation':[0,0,0],'shape':'Block','collidable':True,'queryable':True}
    route={'id':'test','a':[0,0,0],'b':[0,0,20],'width':32,'link':['01','02']}
    data={'parts':[floor],'routes':[route]}
    assert not audit(data,layout,2)
    gap=dict(floor,size=[10,2,24]);assert any('unsupported' in e for e in audit({'parts':[gap],'routes':[route]},layout,2))
    blocker=dict(floor,id='wall',position=[0,3,10],size=[3,6,2],tags=['SolidObstacle'])
    assert any('blocked' in e for e in audit({'parts':[floor,blocker],'routes':[route]},layout,2))
    blocker['collidable']=False
    assert any('Pass-through' in e for e in audit({'parts':[floor,blocker],'routes':[route]},layout,2))
    assert any('budget' in e for e in audit(data,layout,0))
    print('PASS analytic cylinder, supported corridor, gap, head obstruction, pass-through solid and budget controls')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry',type=Path,default=ROOT/'build/map21/overworld-geometry.json')
    parser.add_argument('--part-budget',type=int,default=3200)
    parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    if args.self_test:
        self_test();return 0
    data=json.loads(args.geometry.read_text());layout=json.loads((Path(__file__).parent/'layout.json').read_text())
    errors=audit(data,layout,args.part_budget)
    for message in errors:print('FAIL',message)
    print('STATIC_OVERWORLD_PASS' if not errors else f'STATIC_OVERWORLD_FAIL {len(errors)}')
    print('LIMIT: sampled analytic geometry only; no native avatar, streaming, FPS or multiplayer claim.')
    return bool(errors)

if __name__=='__main__':sys.exit(main())
