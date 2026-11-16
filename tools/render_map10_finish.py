"""Blender renders from the shipped world/finishing layout; not Roblox screenshots."""
import bpy
import json
import math
import re
import sys
from pathlib import Path
from mathutils import Matrix, Vector
ROOT=Path(__file__).resolve().parents[1]
O=ROOT/'build/map10-finish'
O.mkdir(parents=True, exist_ok=True)
base=json.loads((ROOT/'prototypes/map10/geometry.json').read_text())['parts']
finish=json.loads((ROOT/'prototypes/map10/finish_geometry.json').read_text())['parts']
loader=(ROOT/'src/ServerScriptService/Map10Finish.luau').read_text()
grades=re.findall(r'\{"([^"]+)",\s*"([^"]+)",\s*(?:Color3.fromRGB\(([\d, ]+)\)|nil)\}',loader)
bpy.ops.wm.read_factory_settings(use_empty=True)
materials={}
def to_linear(v):
    s=v/255
    return s/12.92 if s<=.04045 else ((s+.055)/1.055)**2.4
def material(rgb, name):
    key=(tuple(rgb),name)
    if key not in materials:
        m=bpy.data.materials.new(f'{name} '+str(tuple(rgb)));m.use_nodes=True
        b=m.node_tree.nodes.get('Principled BSDF');rgb=tuple(to_linear(v) for v in rgb)+(1,)
        b.inputs['Base Color'].default_value=rgb
        b.inputs['Roughness'].default_value={'Neon':.23,'Metal':.36,'Glass':.18,'Sandstone':.82}.get(name,.65)
        if name=='Metal':b.inputs['Metallic'].default_value=.35
        if name=='Neon':
            b.inputs['Emission Color'].default_value=rgb;b.inputs['Emission Strength'].default_value=1.1
        materials[key]=m
    return materials[key]

axis=Matrix(((1,0,0),(0,0,-1),(0,1,0)))
mesh_shapes={}
for label,make in [
    ('Block',lambda: bpy.ops.mesh.primitive_cube_add(size=1)),
    ('Cylinder',lambda: bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=1,depth=1)),
    ('Ball',lambda: bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.5)),
]:
    make()
    obj=bpy.context.object;mesh_shapes[label]=obj.data
    bpy.data.objects.remove(obj,do_unlink=True)
mesh_shapes['Wedge']=bpy.data.meshes.new('Basalt crown wedge')
mesh_shapes['Wedge'].from_pydata(
    [(-.5,-.5,-.5),(.5,-.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(-.5,.5,.5),(.5,.5,.5)],
    [],[(0,2,3,1),(0,4,2),(1,3,5),(2,4,5,3),(0,1,5,4)])
mesh_shapes['Wedge'].update()
mesh_variants={}
for p in (base+finish):
    name=p['id']
    if name.startswith(('Crystal','LavaFissure','BranchLava')) and not p['collidable']: continue
    x,y,z=p['position'];sx,sy,sz=p['size'];rx,ry,rz=map(math.radians,p['rotation'])
    orientation=axis@Matrix.Rotation(ry,3,'Y')@Matrix.Rotation(rx,3,'X')@Matrix.Rotation(rz,3,'Z')
    shape=p.get('shape') or 'Block'
    if shape=='Cylinder':
        scale=(sy/2,sz/2,sx)
        orientation=orientation@Matrix.Rotation(math.pi/2,3,'Y')
    else:
        scale=(sx,sy,sz)
    colour,mat=p['color'],p['material']
    for prefix,as_mat,rgb in grades:
        if name.startswith(prefix):
            if rgb:colour=tuple(int(v) for v in rgb.split(','))
            if not p['collidable']:mat=as_mat
            break
    key=(shape,tuple(colour),mat)
    if key not in mesh_variants:
        mesh_variants[key]=mesh_shapes[shape].copy()
        mesh_variants[key].materials.append(material(colour,mat))
    o=bpy.data.objects.new(name,mesh_variants[key]);bpy.context.collection.objects.link(o)
    o.location=(x,-z,y);o.rotation_euler=orientation.to_euler();o.scale=scale
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=44;scene.cycles.use_denoising=False
scene.render.threads_mode='FIXED';scene.render.threads=4
scene.world=bpy.data.worlds.new('Coastal afternoon');scene.world.use_nodes=True
bg=scene.world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.58,.72,.90,1);bg.inputs[1].default_value=.6
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object
sun.rotation_euler=(.65,-.52,-.40);sun.data.energy=2.0;sun.data.angle=.12
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam
cam.data.clip_end=6000
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.15
scene.render.resolution_x=1500;scene.render.resolution_y=1060
quick='--quick' in sys.argv
if quick:scene.render.resolution_percentage=55;scene.cycles.samples=10
else:scene.render.resolution_percentage=100
views=[
('Island',(1100,-1540,1120),(-20,-50,-12),1730,36),
('Academy',(-337,208,48),(-291,340,41),None,31),
('Garden',(-153,-43,65),(-24,-87,19),None,33),
('Arena',(-155,-216,40),(-330,-115,4),None,29),
('East',(610,15,115),(349,100,46),None,27),
('Coast',(57,-645,57),(-131,-511,-10),None,30)]
if quick:views=[views[i] for i in (0,1,4,5)]
for label,position,target,ortho,lens in views:
    cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO' if ortho else 'PERSP';cam.data.ortho_scale=ortho or 1000;cam.data.lens=lens
    scene.render.filepath=str(O/(label+'.png'));bpy.ops.render.render(write_still=True)
if not quick:bpy.ops.wm.save_as_mainfile(filepath=str(O/'Map10-Polished.blend'))
print('MAP10_FINISH_RENDER_DONE')
