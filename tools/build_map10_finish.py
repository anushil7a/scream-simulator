"""Build Map 10 finishing art and authored solid footprints. No imported dependencies or asset IDs."""
import argparse
import importlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'prototypes/map10/finish_geometry.json'
MODULE=ROOT/'src/ServerScriptService/Map10FinishGeometry.luau'
LIMITS={'North':325,'East':255,'Coast':290,'Stadium':155,'Landmark':135}
MATERIALS={'SmoothPlastic','Sandstone','Concrete','Wood','WoodPlanks','Metal','Neon','Slate',
           'Rock','Basalt','Granite','Grass','Brick','Cobblestone','Fabric','Marble','Glass',
           'Limestone','Ground','Pebble','Sand','Asphalt','DiamondPlate'}
SHAPES={None,'Block','Ball','Cylinder','Wedge'}

# Only visible structural pieces take part in movement and clearance queries.
# Gate supports remain separate so the entrance centre line stays open.
SOLID_PROP_IDS = {
    *(f'StadiumEntry{side}{part}' for side in (-1, 1) for part in ('Plinth', 'Stone')),
    *(f'StadiumButtress{side}_{i}{part}' for side in (0, 1, 3, 4, 5, 6, 7)
      for i in range(2) for part in ('Base', 'Stem')),
    *(f'NorthCourtPlanter{i}' for i in range(4)),
    'NorthAcademyMarqueePostL', 'NorthAcademyMarqueePostR',
    *(f'CoastBenchSlat{i}_{offset}' for i in range(4) for offset in (-1.3, 0, 1.3)),
    *(f'CoastBenchBack{i}' for i in range(4)),
    *(f'CoastBenchFoot{i}_{side}' for i in range(4) for side in (-1, 1)),
    *(f'CoastPlanter{i}' for i in range(6)),
    *(f'CoastBollard{i}' for i in range(2)),
    *(f'LandmarkCoastPalm{i}Trunk' for i in range(6)),
}


def collect(wip=False):
    all_props=[]
    def box(name,pos,size,color,rot=None,material='SmoothPlastic',shape=None):
        rot=rot or (0,0,0)
        props=tuple(map(tuple,(pos,size,color,rot)))
        assert all(len(row)==3 and all(math.isfinite(v) for v in row) for row in props),name
        assert all(.015<=v<=1500 for v in size), (name,size)
        assert all(type(v) is int and 0<=v<=255 for v in color), (name,color)
        assert material in MATERIALS,(name,material)
        assert shape in SHAPES,(name,shape)
        assert all(abs(v)<=1600 for v in pos), (name,pos)
        all_props.append(dict(id=name,position=pos,size=size,color=color,rotation=rot,material=material,shape=shape,
                              collidable=name in SOLID_PROP_IDS))
    def disk(name,x,y,z,r,h,color,material='SmoothPlastic'):
        box(name,(x,y,z),(h,2*r,2*r),color,(0,0,90),material,'Cylinder')
    def line(name,a,b,width,height,color,material='SmoothPlastic'):
        dx,dy,dz=(b[i]-a[i] for i in range(3))
        flat=math.hypot(dx,dz);length=math.hypot(flat,dy)
        rot=(-math.degrees(math.atan2(dy,flat)),math.degrees(math.atan2(dx,dz)),0)
        box(name,tuple((a[i]+b[i])/2 for i in range(3)),(width,height,length),color,rot,material)
    def signs(key):
        ink=(34,57,60);sand=(223,204,166);bronze=(154,119,73)
        if key=='North':
            box('NorthAcademyMarquee',(-286,42.7,-277),(12,1.75,.32),ink,(0,180,0),'Metal')
            box('NorthRookieDirection',(-286,40.92,-277),(10.6,1.42,.30),(35,91,94),(0,180,0),'Metal')
            box('NorthAcademyMarqueePostL',(-291.05,37,-277),(.8,10.4,.8),bronze,material='Metal')
            box('NorthAcademyMarqueePostR',(-280.95,37,-277),(.8,10.4,.8),bronze,material='Metal')
            box('NorthMusicMarquee',(112,38,-237),(18,2.1,.54),(52,43,67),(0,180,0),'Metal')
            box('NorthMusicMarqueePostL',(104,34.75,-237),(.95,5.7,.95),ink,material='Metal')
            box('NorthMusicMarqueePostR',(120,34.75,-237),(.95,5.7,.95),ink,material='Metal')
        elif key=='East':
            box('EastShrineMarquee',(350,99,-452.9),(18,2.05,.32),(57,42,73),(0,180,0),'Slate')
        elif key=='Coast':
            box('CoastDockMarquee',(-233,6.1,466),(8,1.3,.25),ink,material='Wood')
            box('CoastDockMarqueePostL',(-236,3.3,466),(.68,5.1,.68),sand,material='Wood')
            box('CoastDockMarqueePostR',(-230,3.3,466),(.68,5.1,.68),sand,material='Wood')
    groups={}
    for key,limit in LIMITS.items():
        package='map10_finish_'+key.lower()
        if wip and not (ROOT/'tools'/(package+'.py')).exists():
            continue
        first=len(all_props)
        importlib.import_module(package).add(box,disk,line)
        signs(key)
        group=all_props[first:]
        assert 0<len(group)<=limit,(key,len(group),limit)
        assert all(q['id'].startswith(key) for q in group),key
        groups[key]=len(group)
    if not wip:
        assert SOLID_PROP_IDS <= {q['id'] for q in all_props}, 'missing authored collision part'
    assert len({q['id'] for q in all_props})==len(all_props),'duplicate finishing ID'
    assert sum(q['material']=='Neon' for q in all_props)<=160,'emissive accents must remain sparse'
    return all_props,groups

def encode(parts):
    def vector(value):
        return ','.join(format(v,'.6f').rstrip('0').rstrip('.') for v in value)
    lines=['-- Generated with tools/build_map10_finish.py. Original environment art.','return {']
    for q in parts:
        # Append a true flag only for authored solid geometry.
        lines.append(' {'+','.join([json.dumps(q['id']),
             f'Vector3.new({vector(q["position"])})',f'Vector3.new({vector(q["size"])})',
             f'Color3.fromRGB({vector(q["color"])})',f'Vector3.new({vector(q["rotation"])})',
             json.dumps(q['material']),json.dumps(q['shape'] or 'Block')])+(',true' if q['collidable'] else '')+'},')
    return '\n'.join(lines+['}',''])

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--wip',action='store_true',help='Allow missing district art only for local iterations')
    parser.add_argument('--check',action='store_true',help='Validate without writing output')
    args=parser.parse_args()
    parts,groups=collect(args.wip)
    src=encode(parts)
    data=json.dumps({'groups':groups,'parts':parts},indent=1)+'\n'
    if args.check:
        assert MODULE.read_text()==src,'server art differs from reproducible source'
        # OS math libraries can differ in the last floating-point digits.
        precision = lambda value: round(float(value), 9)
        assert json.loads(OUT.read_text(),parse_float=precision)==json.loads(data,parse_float=precision),'preview art differs from reproducible source'
    else:
        OUT.write_text(data)
        MODULE.write_text(src)
    print('Map 10 finish:', groups, 'total',len(parts))
if __name__=='__main__': main()
