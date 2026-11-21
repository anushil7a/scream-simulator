"""Run the finish module with Instance/CFrame doubles, not Studio physics or visual evidence."""
import json
import math
import re
from pathlib import Path
import subprocess
import sys
import tempfile
R=Path(__file__).resolve().parents[1]; S=R/'src/ServerScriptService'
doc=json.loads((R/'prototypes/map10/finish_geometry.json').read_text())
assert set(doc['groups'])=={'Stadium','North','East','Coast','Landmark'}
assert not any(re.fullmatch(r'NorthPavilion[0-3]Entablature|StadiumEntry(?:-1|1)(?:Lantern|LanternLens|GlazedPanel)|StadiumCorner-246_(?:36|204)Z', part['id']) for part in doc['parts'])
solid_parts = [part for part in doc['parts'] if part['collidable']]
expected_groups = {
    r'StadiumEntry(?:-1|1)(?:Plinth|Stone)': 4,
    r'StadiumButtress[0134567]_[01](?:Base|Stem)': 28,
    r'NorthCourtPlanter[0-3]': 4,
    r'NorthAcademyMarqueePost[LR]': 2,
    r'NorthMusicMarqueePost[LR]': 2,
    r'CoastBench(?:Slat[0-3]_(?:-1[.]3|0|1[.]3)|Back[0-3]|Foot[0-3]_(?:-1|1))': 24,
    r'CoastPlanter[0-5]': 6,
    r'CoastBollard[01]': 2,
    r'LandmarkCoastPalm[0-5]Trunk': 6,
}
for pattern, count in expected_groups.items():
    assert sum(bool(re.fullmatch(pattern, part['id'])) for part in solid_parts) == count, pattern
assert len(solid_parts) == sum(expected_groups.values())

def footprint(part):
    x, _, z = part['position']
    sx, sy, sz = part['size']
    rx, ry, rz = map(math.radians, part['rotation'])
    # Conservative XZ bound for the authored cylinders, yawed blocks and tilted trunks.
    if part['shape'] == 'Cylinder':
        assert part['rotation'] == [0, 0, 90]
        return x - sy/2, x + sy/2, z - sz/2, z + sz/2
    assert rx == 0
    width = abs(math.cos(rz)) * sx + abs(math.sin(rz)) * sy
    hx = (abs(math.cos(ry)) * width + abs(math.sin(ry)) * sz) / 2
    hz = (abs(math.sin(ry)) * width + abs(math.cos(ry)) * sz) / 2
    return x - hx, x + hx, z - hz, z + hz

def assert_clear(name, x0, x1, z0, z1):
    for part in solid_parts:
        left, right, near, far = footprint(part)
        assert right < x0 or left > x1 or far < z0 or near > z1, (name, part['id'])

assert_clear('stadium east gate', -260, -170, 108, 132)
assert_clear('academy spawn approach', -340, -260, -274, -247)
assert_clear('academy directory passage', -290, -282, -278, -276)
assert_clear('academy training corridor', -475, -125, -413, -387)
assert_clear('Resonance Hall marquee centre', 107, 117, -243, -231)
assert_clear('coastal walkway centre', -480, 480, 410, 430)
assert_clear('coastal pitch', 254, 366, 257.5, 342.5)
assert_clear('dock centre', -227, -213, 430, 589)
directory = {part['id']: part for part in doc['parts'] if part['id'].startswith(('NorthAcademyMarquee', 'NorthRookieDirection'))}
rookie = directory['NorthRookieDirection']
plaza = directory['NorthAcademyMarquee']
assert rookie['position'][1] - rookie['size'][1] / 2 > plaza['position'][1] + plaza['size'][1] / 2
assert rookie['size'][0] > plaza['size'][0] and rookie['size'][1] > plaza['size'][1]
for suffix in 'LR':
    post = directory['NorthAcademyMarqueePost' + suffix]
    assert post['position'][1] - post['size'][1] / 2 == 31.8
    assert post['position'][1] + post['size'][1] / 2 > rookie['position'][1] - rookie['size'][1] / 2
trail=[part for part in doc['parts'] if part['id'].startswith('NorthRookiePath')]
assert len(trail)==15 and all(not part['collidable'] and part['size'][1]<=.05 for part in trail)
for part in (p for p in trail if 'Stone' in p['id']):
    x,_,z=part['position']
    width,_,length=part['size']
    yaw=math.radians(part['rotation'][1])
    # Cover the entire rotated ribbon with overlapping conservative bounds.
    margin=width/2+length/48
    for i in range(25):
        along=(i/24-.5)*length
        cx,cz=x+math.sin(yaw)*along,z+math.cos(yaw)*along
        assert_clear(part['id'],cx-margin,cx+margin,cz-margin,cz+margin)

roles=set(re.findall(r'\{role="([^"]+)",name=',(S/'CompactCity.luau').read_text()))
workers=(S/'World.luau').read_text().split('local function workerFinish',1)[1].split('local function trainerOutfit',1)[0]
assert len(roles)==7 and all(role+'={{' in workers for role in roles),'Missing Map 10 authored worker role'
assert 'not job.supporting' in (S/'World.luau').read_text()
subprocess.run([sys.executable,str(R/'tools/build_map10_finish.py'),'--check'],check=True)
city_dispatch=(S/'City.luau').read_text().split('function City.Build(',1)[1].split(' rng=',1)[0]
script='''
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
Vector3.zero=Vector3.new(0,0,0)
local Color3={fromRGB=function(r,g,b)return {R=r,G=g,B=b}end}
local Data=(function()
'''+(S/'Map10FinishGeometry.luau').read_text()+'''
end)()
local script={Parent={Map10FinishGeometry='data'}}
local function require(k)assert(k=='data');return Data end
local mt={__mul=function(a)return a end}
local function frame(...)return setmetatable({...},mt)end
local CFrame={new=frame,Angles=frame}
local UDim2={fromScale=function(...)return {...}end}
local enum=setmetatable({},{__index=function(_,key)return key end})
local Enum=setmetatable({},{__index=function()return enum end})
local nodes={}
local Instance={new=function(class)
 local o={ClassName=class}
 function o:IsA(k)return k==self.ClassName or k=='BasePart' and self.ClassName=='Part'end
 function o:SetAttribute(k,v)self[k]=v end
 table.insert(nodes,o)
 return o
end}
local Finish=(function()
'''+(S/'Map10Finish.luau').read_text()+'''
end)()
local fixed=Instance.new('Part');fixed.Name='IslandCore0';fixed.CanCollide=true
fixed.CanQuery=true;fixed.Material='SmoothPlastic';fixed.Position=Vector3.new(2,4,8)
local unaffected=Instance.new('Part');unaffected.Name='Other'
local world={GetChildren=function()return {fixed,unaffected}end}
local folder=Finish.Build(world)
assert(folder.Parent==world and folder.Name=='Map10Finishing')
assert(fixed.CanCollide and fixed.CanQuery and fixed.Material=='SmoothPlastic' and fixed.Position.Y==4,'Base collision material or position changed')
assert(unaffected.Color==nil and unaffected.Material==nil,'Non-map part changed')
local expected={}
for _,row in ipairs(Data) do expected[row[1]]=row[8]==true end
local count,labels,solids=0,0,0
for _,p in ipairs(nodes)do
 if (p.ClassName=='Part' or p.ClassName=='WedgePart') and p.Parent and p.Parent.Parent==folder then
  assert(expected[p.Name]~=nil and p.CanCollide==expected[p.Name] and p.CanQuery==expected[p.Name],
    'Unexpected movement/query flags for '..p.Name)
  assert(not p.CanTouch and p.Anchored,'Finish must remain anchored without touch events')
  if p.CanCollide then solids+=1 end
  assert(p.Size.X>0 and p.Size.Y>0 and p.Size.Z>0 and p.Material~=nil and (p.ClassName=='WedgePart' or p.Shape~=nil),'Invalid decoration')
  if p.Material=='Neon' then assert(p.CastShadow==false,'Emissive accent casts shadow') end
  count+=1
 elseif p.ClassName=='SurfaceGui' then
  assert(p.AlwaysOnTop==false and p.Parent,'Labels should not reveal through walls')
  labels+=1
 end
end
assert(count==#Data and count>600 and count<=1100,'Total finishing props outside budget')
assert(labels==6,'Expected six world signs including training direction')
assert(solids==78,'Expected the authored collision parts')
print('PASS '..count..' actual finishing props, original collision material retained, six occluded world signs')
local Layout=(function()
'''+(R/'src/ReplicatedStorage/Shared/CompactLayout.luau').read_text()+'''
end)()
local CompactCity=(function()
local game={GetService=function()return {Shared={CompactLayout='layout'}}end}
local function require(k)assert(k=='layout');return Layout end
'''+(S/'CompactCity.luau').read_text()+'''
end)()
local Config={CompactCity=true}
local City={}
function City.Build('''+city_dispatch+'''end
local baseParent,finishedParent={},{}
City.Build(baseParent)
City.Build(finishedParent,true)
local standalone,finished={},{}
for _,node in ipairs(nodes) do
 if node.Parent==baseParent then standalone[node.Name]=node
 elseif node.Parent==finishedParent then finished[node.Name]=node end
end
local omitted=0
for _,spec in ipairs(Layout.PartSpecs) do
 local id=spec.id
 local replaced=id:match("^Crystal%d+$") or id:match("^LavaFissure%d+$") or id:match("^BranchLava%d+$")
 assert(standalone[id]~=nil,"Base preview lost "..id)
 if replaced then
  assert(not spec.collidable and finished[id]==nil,"Finished Map10 allocated replaced scenery "..id)
  omitted+=1
 else
  local p=assert(finished[id],"Finished Map10 lost "..id)
  assert(p.Position==standalone[id].Position and p.Size==standalone[id].Size and p.CanCollide==standalone[id].CanCollide and p.CanQuery==standalone[id].CanQuery)
 end
end
assert(omitted==17,"Unexpected Map10 replacement count")
print('PASS 17 replaced props omitted only when finishing is enabled')
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',prefix='tmp_map_finish_',dir=R/'tests',delete=False,encoding='utf-8') as f:
    f.write(script)
    path=Path(f.name)
try: subprocess.run(['luau',str(path)],cwd=R,check=True)
finally: path.unlink()
