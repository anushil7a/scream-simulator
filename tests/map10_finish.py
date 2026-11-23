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
assert_clear('Amphitheatre arrival', 108, 116, -233, -225)
assert_clear('academy training corridor', -475, -125, -413, -387)
assert_clear('Amphitheatre marquee centre', 107, 117, -243, -231)
assert all(part['id'] not in {'NorthMusicFacade6','NorthMusicFacadeInlay6'} for part in doc['parts']), \
    'A decorative wall masks the west entrance'
assert_clear('Amphitheatre west bridge', -70, 90, -346, -314)
assert_clear('coastal walkway centre', -480, 480, 410, 430)
assert_clear('coastal pitch', 254, 366, 257.5, 342.5)
assert_clear('dock centre', -227, -213, 430, 589)
def assert_planted(planter_parts):
    for index in range(4):
        soil = planter_parts[f'NorthCourtSoil{index}']
        soil_top = soil['position'][1] + soil['size'][1] / 2
        for suffix in 'AB':
            shrub = planter_parts[f'NorthCourtShrub{index}{suffix}']
            x, y, z = shrub['position']
            sx, sy, sz = shrub['size']
            assert shrub['shape'] == 'Ball' and not shrub['collidable']
            assert y - sy/2 <= soil_top - .3 < y, (shrub['id'], 'Foliage lacks soil contact depth')
            # Bound the ellipsoid's cut at soil height, inside the planter bed.
            section = math.sqrt(1 - ((y - soil_top) / (sy / 2)) ** 2)
            assert (abs(x-soil['position'][0]) + sx/2*section < soil['size'][0]/2
                    and abs(z-soil['position'][2]) + sz/2*section < soil['size'][2]/2), 'Foliage base leaves the soil bed'

planter_parts = {part['id']: part for part in doc['parts'] if part['id'].startswith('NorthCourt')}
assert_planted(planter_parts)
if '--negative-controls' in sys.argv:
    name = 'NorthCourtShrub2A'
    shrub = planter_parts[name]
    x, y, z = shrub['position']
    for position, error in (([x, y+1, z], 'Foliage lacks soil contact depth'),
                            ([x-4, y, z], 'Foliage base leaves the soil bed')):
        try:
            assert_planted({**planter_parts, name: {**shrub, 'position': position}})
        except AssertionError as exc:
            assert error in str(exc), exc
            print('PASS negative control:', error)
        else:
            raise AssertionError('Mutation accepted: '+error)

def assert_garden_structures(parts):
    beds = [name.removesuffix('Soil') for name in parts if name.endswith('Soil')]
    assert len(beds)==6
    for bed in beds:
        soil, trunk = parts[bed+'Soil'], parts[bed+'Trunk1']
        side, crown, shrub = (parts[bed+f'Cypress{i}'] for i in range(3))
        soil_top = soil['position'][1] + soil['size'][0]/2
        for foliage in (side, crown, shrub):
            assert foliage['shape']=='Ball' and not foliage['collidable']
        assert shrub['position'][1] - min(shrub['size'])/2 < soil_top-.25, 'Pocket shrub floats above soil'
        assert trunk['position'][1] - trunk['size'][1]/2 < soil_top, 'Pocket trunk floats above soil'
        assert crown['position'][::2]==trunk['position'][::2] and (
            crown['position'][1] - min(crown['size'])/2 < trunk['position'][1] + trunk['size'][1]/2
        ), 'Pocket crown is disconnected from its trunk'
        assert math.dist(side['position'], crown['position']) < (min(side['size']) + min(crown['size']))/2-.25, 'Pocket canopy lobe is detached'
        for part in (side, crown, shrub, trunk):
            assert math.dist(part['position'][::2], soil['position'][::2])+max(part['size'][::2])/2 < soil['size'][1]/2, 'Pocket foliage exceeds the bed footprint'

garden_parts = {part['id']: part for part in doc['parts'] if part['id'].startswith('LandmarkPlazaGarden')}
assert_garden_structures(garden_parts)
if '--negative-controls' in sys.argv:
    for suffix, offset, error in (
        ('Cypress2', (0, 2, 0), 'Pocket shrub floats above soil'),
        ('Cypress0', (-6, 0, 0), 'Pocket canopy lobe is detached'),
    ):
        name = 'LandmarkPlazaGarden-388_-326'+suffix
        part = garden_parts[name]
        lifted = [value+shift for value, shift in zip(part['position'], offset)]
        try:
            assert_garden_structures({**garden_parts, name: {**part, 'position': lifted}})
        except AssertionError as exc:
            assert error in str(exc), exc
            print('PASS negative control:', error)
        else:
            raise AssertionError('Mutation accepted: '+error)
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
stones = [part for part in trail if 'Stone' in part['id']]
def garden_path_clearance(bed, stone):
    x, _, z = bed['position']
    cx, _, cz = stone['position']
    width, _, length = stone['size']
    yaw = math.radians(stone['rotation'][1])
    u = (x-cx)*math.cos(yaw) - (z-cz)*math.sin(yaw)
    v = (x-cx)*math.sin(yaw) + (z-cz)*math.cos(yaw)
    return math.hypot(max(0, abs(u)-width/2), max(0, abs(v)-length/2)) - bed['size'][1]/2

for bed_name, bed in garden_parts.items():
    if bed_name.endswith('Stone'):
        assert all(garden_path_clearance(bed, stone)>2 for stone in stones), (bed_name, 'Garden bed covers the training route')
if '--negative-controls' in sys.argv:
    old_bed = {**garden_parts['LandmarkPlazaGarden-388_-326Stone'], 'position': [-388, 32.68, -326]}
    assert any(garden_path_clearance(old_bed, stone)<0 for stone in stones), 'Baseline bed no longer reproduces the route overlap'
    print('PASS negative control: Garden bed covers the training route')
last = max(stones, key=lambda part: int(part['id'].removeprefix('NorthRookiePathStone')))
layout = (R/'src/ReplicatedStorage/Shared/CompactLayout.luau').read_text()
home_x, home_z = map(int, re.search(r'TrainingHomes=\{\{x=(-?\d+),y=-?\d+,z=(-?\d+)\}', layout).groups())
rules = (R/'src/ReplicatedStorage/Shared/TrainingRules.luau').read_text()
radius = int(re.search(r'local Training=\{Radius=(\d+)', rules).group(1))
x, _, z = last['position']
yaw = math.radians(last['rotation'][1])
half_length = last['size'][2] / 2
tip_x, tip_z = x + math.sin(yaw) * half_length, z + math.cos(yaw) * half_length
assert math.hypot(tip_x-home_x, tip_z-home_z) <= radius-10, 'Rookie trail ends before a usable position inside the sparring pad'
assert len(trail)==20 and all(not part['collidable'] and part['size'][1]<=.05 for part in trail)
tier_marks = [part for part in doc['parts'] if part['id'].startswith('NorthTrainingInlay')]
assert len(tier_marks)==9, 'Missing the three training pad inlay sets'
homes = [(int(x),int(z)) for x,z in re.findall(r'\{x=(-?\d+),y=32,z=(-?\d+)\}', layout.split('TrainingHomes=', 1)[1].splitlines()[0])]
assert len(homes)==3
for (x,z),tier in zip(homes,('Rookie','Brawler','Elite')):
    marks = [part for part in tier_marks if part['id'].startswith('NorthTrainingInlay'+tier)]
    assert len(marks)==3 and all(not part['collidable'] for part in marks)
    plate = next(part for part in marks if part['id']=='NorthTrainingInlay'+tier)
    assert plate['rotation']==[0,-90,0] and plate['size'][2]>plate['size'][0], 'Inlay text must read from the south'
    assert plate['position'][0]-x==10.5, 'Training name is back under the centerline avatar'
    for mark in marks:
        left,right,near,far=footprint(mark)
        assert max(math.hypot(px-x,pz-z) for px in (left,right) for pz in (near,far))<radius
        assert far < z-18 and mark['position'][1]-mark['size'][1]/2 >= 32.26-1e-6
        assert mark['position'][1]+mark['size'][1]/2 <= 32.32
previous = next(part for part in stones if part['id']=='NorthRookiePathStone2')
previous_yaw = math.radians(previous['rotation'][1])
previous_north = previous['position'][2] - (
    abs(math.sin(previous_yaw)) * previous['size'][0] + abs(math.cos(previous_yaw)) * previous['size'][2]
) / 2
final_south = z + half_length
assert final_south < previous_north, 'Rookie trail stones overlap at the final seam'
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
local paving=Instance.new('Part');paving.Name='CoastalWalk';paving.CanCollide=false;paving.CanQuery=false;paving.Material='SmoothPlastic'
local world={GetChildren=function()return {fixed,unaffected,paving}end}
local folder=Finish.Build(world)
assert(folder.Parent==world and folder.Name=='Map10Finishing')
assert(fixed.CanCollide and fixed.CanQuery and fixed.Material=='SmoothPlastic' and fixed.Position.Y==4,'Base collision material or position changed')
assert(unaffected.Color==nil and unaffected.Material==nil,'Non-map part changed')
assert(paving.Material=='Concrete' and not paving.CanCollide and not paving.CanQuery
 and paving.Color.R==212 and paving.Color.G==207 and paving.Color.B==189,'Coast paving lost its finish or affects physics')
local expected={}
for _,row in ipairs(Data) do expected[row[1]]=row[8]==true end
local count,labels,solids=0,0,0
local deckFaces,pavingAccents=0,0
local expectedInlays={NorthTrainingInlayRookie='ROOKIE',NorthTrainingInlayBrawler='BRAWLER',NorthTrainingInlayElite='ELITE'}
local inlays=0
for _,p in ipairs(nodes)do
 if (p.ClassName=='Part' or p.ClassName=='WedgePart') and p.Parent and p.Parent.Parent==folder then
  assert(expected[p.Name]~=nil and p.CanCollide==expected[p.Name] and p.CanQuery==expected[p.Name],
    'Unexpected movement/query flags for '..p.Name)
  assert(not p.CanTouch and p.Anchored,'Finish must remain anchored without touch events')
  if p.CanCollide then solids+=1 end
  assert(p.Size.X>0 and p.Size.Y>0 and p.Size.Z>0 and p.Material~=nil and (p.ClassName=='WedgePart' or p.Shape~=nil),'Invalid decoration')
  if p.Material=='Neon' then assert(p.CastShadow==false,'Emissive accent casts shadow') end
  if p.Name:match('^CoastDeckSurface') then
   assert(p.Material=='WoodPlanks' and not p.CanCollide and not p.CanQuery and not p.CastShadow,
    'Pier finish must remain visual-only timber')
   local position=p.CFrame[1]
   assert(math.abs(position.Y-p.Size.Y/2-.1)<.00001,'Pier finish leaves the support surface')
   if p.Name=='CoastDeckSurfaceDockMain' then
    assert(position.Z-p.Size.Z/2==438 and position.Z+p.Size.Z/2==594,'Main deck overlaps paving or leaves a gap')
   end
   deckFaces+=1
  elseif p.Name:match('^CoastPaving') then
   assert(not p.CanCollide and not p.CanQuery and not p.CastShadow,'Paving accents must remain visual-only')
   pavingAccents+=1
  end
  count+=1
 elseif p.ClassName=='SurfaceGui' then
  assert(p.AlwaysOnTop==false and p.Parent,'Labels should not reveal through walls')
  if expectedInlays[p.Parent.Name] then
   assert(p.Face==Enum.NormalId.Top,'Training inlay label is not on the top face')
   inlays+=1
  end
  labels+=1
 elseif p.ClassName=='TextLabel' and expectedInlays[p.Parent.Parent.Name] then
  assert(p.Text==expectedInlays[p.Parent.Parent.Name],'Training inlay does not name its pad')
 end
end
assert(count==#Data and count>600 and count<=1100,'Total finishing props outside budget')
assert(deckFaces==5 and pavingAccents==25,'Missing promenade or pier finish')
assert(labels==9 and inlays==3,'Expected three training inlays alongside six world signs')
local amphitheatreSign
for _,n in ipairs(nodes) do
 if n.ClassName=='TextLabel' and n.Parent.Parent.Name=='NorthMusicMarquee' then amphitheatreSign=n.Text end
end
assert(amphitheatreSign=='AMPHITHEATRE','City marquee disagrees with the Amphitheatre map pin')
assert(solids==78,'Expected the authored collision parts')
print('PASS '..count..' actual finishing props, original collision material retained, nine occluded world signs')
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
local firstMapNode=#nodes+1
City.Build(baseParent)
City.Build(finishedParent,true)
function finishedParent:GetChildren()
 local children={}
 for _,node in ipairs(nodes) do if node.Parent==self then table.insert(children,node) end end
 return children
end
Finish.Build(finishedParent)
local standalone,finished={},{}
local pavilionCounts={}
for index=firstMapNode,#nodes do
 local node=nodes[index]
 local parent=node.Parent
 if parent and parent.Name=='OceanBackdrop' then
  assert(parent.ClassName=='Model' and parent.ModelStreamingMode==Enum.ModelStreamingMode.Persistent,'Water must persist across streaming')
  assert(node.Anchored and not node.CanCollide and not node.CanQuery and not node.CanTouch and not node.CastShadow,'Unexpected ocean part flags')
  parent=parent.Parent
 end
 local pavilion=node.Name and (node.Name:match("^Academy(Pavilion[0-3]).+") or node.Name:match("^North(Pavilion[0-3])"))
 if pavilion and parent~=baseParent then
  assert(parent.Name=="Academy"..pavilion and parent.ClassName=='Model', 'Pavilion streamed separately: '..node.Name)
  assert(parent.ModelStreamingMode==Enum.ModelStreamingMode.Atomic,'Pavilion must be Atomic')
  pavilionCounts[parent]=(pavilionCounts[parent] or 0)+1
  parent=parent.Parent
 end
 if parent==baseParent then standalone[node.Name]=node
 elseif parent==finishedParent then finished[node.Name]=node end
end
local pavilionModels=0
for _,count in pairs(pavilionCounts) do assert(count==27,'Pavilion must include eight structural and 19 trim parts');pavilionModels+=1 end
assert(pavilionModels==4,'Expected four independent pavilion models')
print('PASS four complete Atomic pavilions, including all 76 trim parts')
local omitted=0
for _,spec in ipairs(Layout.PartSpecs) do
 local id=spec.id
 local speaker=id:match("^Speaker([0-2])(%d%d)$")
 local replaced=id:match("^Crystal%d+$") or id:match("^LavaFissure%d+$") or id:match("^BranchLava%d+$") or speaker
 assert(standalone[id]~=nil,"Base preview lost "..id)
 if replaced then
  assert(not spec.collidable and finished[id]==nil,"Finished Map10 allocated replaced scenery "..id)
  omitted+=1
 else
  local p=assert(finished[id],"Finished Map10 lost "..id)
  assert(p.Position==standalone[id].Position and p.Size==standalone[id].Size and p.CanCollide==standalone[id].CanCollide and p.CanQuery==standalone[id].CanQuery)
 end
end
assert(omitted==26,"Unexpected Map10 replacement count")
local bedCount,flowers,markers=0,0,0
for i=0,2 do
 local soil=assert(finished["Flowers"..i])
 local bed=assert(finished["GardenBed"..i])
 assert(bed.CanCollide and bed.Material==standalone[bed.Name].Material,"Garden collider or surface changed")
 assert(soil.Material=="Ground" and standalone[soil.Name].Material=="SmoothPlastic","Garden still has flat pink slabs")
 for _,node in ipairs(nodes) do
  if node.Parent==soil then
   assert(node.Name=="GardenPlantings" and node.ModelStreamingMode==Enum.ModelStreamingMode.Atomic)
   bedCount+=1
   local parts={}
   for _,plant in ipairs(nodes) do
    if plant.Parent==node then
     assert(not plant.CanCollide and not plant.CanQuery and not plant.CanTouch and plant.Anchored,"Garden decor added physical or query surfaces")
     assert(math.abs(plant.Position.X-soil.Position.X)+plant.Size.X/2<=soil.Size.X/2
      and math.abs(plant.Position.Z-soil.Position.Z)+plant.Size.Z/2<=soil.Size.Z/2,"Garden planting hangs outside the bed")
     parts[plant.Name]=plant;flowers+=1
    end
   end
   for j=1,5 do
    local leaves,center=parts["Leaves"..j],parts["Center"..j]
    assert(leaves.Position.Y-leaves.Size.Y/2<=soil.Position.Y+soil.Size.Y/2,"Garden foliage floats above soil")
    for i=1,4 do
     local petal=parts["Petal"..i.."_"..j]
     assert(petal.Position.Y-petal.Size.Y/2<leaves.Position.Y+leaves.Size.Y/2
      and center.Position.Y-center.Size.Y/2<petal.Position.Y+petal.Size.Y/2,"Garden flowers are disconnected")
     assert(math.abs(petal.Position.X-center.Position.X)+math.abs(petal.Position.Z-center.Position.Z)>.45,
      "Garden petal collapsed into center")
    end
   end
  end
 end
end
for _,node in ipairs(nodes) do
 local folder=node.Parent
 if node.QuestAction=="Garden" and folder and folder.Parent==finishedParent then
  assert(node.Transparency==1 and not node.CastShadow,"Garden still shows a gold quest block")
  local original
  for _,other in ipairs(nodes) do
   if other.Name==node.Name and other.Parent and other.Parent.Parent==baseParent then original=other;break end
  end
  assert(original and original.Position==node.Position and not original.Transparency,"Garden prompt moved or altered in base preview")
  for _,prompt in ipairs(nodes) do
   if prompt.Parent==node then
    assert(prompt.ClassName=="ProximityPrompt" and prompt.MaxActivationDistance==10 and prompt.HoldDuration==1.5
     and prompt.ActionText=="Water flowers" and prompt.ObjectText=="Community garden","Garden prompt changed")
    markers+=1
   end
  end
 end
end
assert(bedCount==3 and flowers==90 and markers==3,"Community garden missing foliage or prompt")
print("PASS three existing quest beds dressed with 90 nonphysical pieces and three unchanged prompts")
local bottles=0
for _,node in ipairs(nodes) do
 local folder=node.Parent
 if node.QuestAction=="Litter" and folder and folder.Parent==finishedParent then
  local original,visual,prompt
  for _,child in ipairs(nodes) do
   if child.Name==node.Name and child.Parent and child.Parent.Parent==baseParent then original=child end
   if child.Parent==node then
    if child.ClassName=="Model" then visual=child elseif child.ClassName=="ProximityPrompt" then prompt=child end
   end
  end
  assert(original and original.Position==node.Position and not original.Transparency,"Bottle activation moved or base preview changed")
  assert(visual and visual.Name=="BottleVisual" and visual.ModelStreamingMode==Enum.ModelStreamingMode.Atomic
   and node.Transparency==1,"Bottle still has the placeholder block")
  local sections={}
  for _,piece in ipairs(nodes) do
   if piece.Parent==visual then
    assert(piece.Anchored and not piece.CanCollide and not piece.CanQuery and not piece.CanTouch
     and piece.Shape==Enum.PartType.Cylinder,"Bottle art interferes with gameplay")
    sections[piece.Name]=true
   end
  end
  assert(sections.Body and sections.Label and sections.Neck and sections.Cap,"Bottle silhouette is incomplete")
  assert(prompt and prompt.HoldDuration==.25 and prompt.MaxActivationDistance==10
   and prompt.ActionText=="Collect bottle" and not prompt.RequiresLineOfSight,"Bottle prompt behavior changed")
  bottles+=1
 end
end
assert(bottles==6,"Missing beach-cleanup bottles")
print("PASS six bottle props use existing nonphysical markers and collection prompts")
local finishedDrivers=0
for index=firstMapNode,#nodes do
 local node=nodes[index]
 if node.Name and node.Name:match("^NorthAudio[0-2]Driver[0-2]_[0-2]$") then
  assert(node.Parent.Parent.Parent==finishedParent and not node.CanCollide and not node.CanQuery,'Missing decorative finished driver')
  finishedDrivers+=1
 end
end
assert(finishedDrivers==27,"Expected all 27 finished speaker driver layers")
print('PASS 26 replaced props omitted and all 27 finished driver layers retained')
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',prefix='tmp_map_finish_',dir=R/'tests',delete=False,encoding='utf-8') as f:
    f.write(script)
    path=Path(f.name)
try:
    subprocess.run(['luau', str(path)], cwd=R, check=True)
    if '--negative-controls' in sys.argv:
        for before, after, expected_error in (
            ('{"CoastalWalk","Concrete",Color3.fromRGB(212,207,189)},', '', 'Coast paving lost its finish'),
            ('"CoastDeckSurfaceDockMain",Vector3.new(-220,0.12,516),Vector3.new(32,0.04,156)',
             '"CoastDeckSurfaceDockMain",Vector3.new(-220,0.12,507),Vector3.new(32,0.04,174)',
             'Main deck overlaps paving or leaves a gap'),
            ('mark(p,trainingNames[id],Enum.NormalId.Top)', 'mark(p,trainingNames[id],Enum.NormalId.Front)',
             'Training inlay label is not on the top face'),
            ('NorthTrainingInlayRookie="ROOKIE"', 'NorthTrainingInlayRookie="BRAWLER"',
             'Training inlay does not name its pad'),
            ('model.Name=pavilion;model.ModelStreamingMode=Enum.ModelStreamingMode.Atomic',
             'model.Name=pavilion;model.ModelStreamingMode=Enum.ModelStreamingMode.Default', 'Pavilion must be Atomic'),
            ('p.Parent=(pavilion and pavilions["Academy"..pavilion]) or district',
             'p.Parent=district', 'Pavilion streamed separately: NorthPavilion'),
            (' or id:match("^Speaker[0-2]%d%d$")', '', 'Finished Map10 allocated replaced scenery Speaker046'),
            ('if bottle then dressBottle(p,index) end', 'if false then dressBottle(p,index) end', 'Bottle still has the placeholder block'),
            ('layer("Leaves",.29', 'layer("Leaves",1.5', 'Garden foliage floats above soil'),
            ('size,V(x+(dx or 0),top+y,z+(dz or 0)),color,false)', 'size,V(x+(dx or 0),top+y,z+(dz or 0)),color,true)', 'Garden decor added physical or query surfaces'),
            ('local petalOffsets={{-.67,0}', 'local petalOffsets={{0,0}', 'Garden petal collapsed into center'),
            ('then p.Transparency=1;p.CastShadow=false end', 'then p.Transparency=0;p.CastShadow=false end', 'Garden still shows a gold quest block'),
        ):
            assert script.count(before) == 1, before
            path.write_text(script.replace(before, after), encoding='utf-8')
            mutant = subprocess.run(['luau', str(path)], cwd=R, text=True, capture_output=True)
            assert mutant.returncode and expected_error in mutant.stderr, mutant.stderr
            print('PASS negative control:', expected_error)
finally: path.unlink()
