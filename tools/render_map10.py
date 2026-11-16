import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'prototypes/map10';data=json.loads((O/'geometry.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);materials={}
def mat(c,neon=False):
 key=(tuple(c),neon)
 if key not in materials:
  m=bpy.data.materials.new(str(c));m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*[v/255 for v in c],1);bs.inputs['Roughness'].default_value=.65
  if neon:bs.inputs['Emission Color'].default_value=(*[v/255 for v in c],1);bs.inputs['Emission Strength'].default_value=.7
  materials[key]=m
 return materials[key]
T=Matrix(((1,0,0),(0,0,-1),(0,1,0)))
for q in data['parts']:
 x,y,z=q['position'];sx,sy,sz=q['size'];a,b,c=map(math.radians,q['rotation']);rot=Matrix.Rotation(b,3,'Y')@Matrix.Rotation(a,3,'X')@Matrix.Rotation(c,3,'Z')
 if q.get('shape')=='Cylinder':
  # Roblox cylinder longitudinal axis X; rotate Blender cylinder Z into X first.
  bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=1,depth=1);o=bpy.context.object;o.scale=(sy/2,sz/2,sx);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.rotation_euler=(T@rot@Matrix.Rotation(math.pi/2,3,'Y')).to_euler()
 else:
  bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.scale=q['size'];bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.rotation_euler=(T@rot).to_euler()
 o.name=q['id'];o.location=(x,-z,y);o.data.materials.append(mat(q['color'],q['material']=='Neon'))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=3
scene.world=bpy.data.worlds.new('Clear sky');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.63,.76,.9,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.45,-.45,-.6);bpy.context.object.data.energy=1.5
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.clip_end=6000
scene.view_settings.exposure=-.35;scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast'
scene.render.resolution_x=1500;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
for name,position,target,ortho in [('hero',(1100,-1500,1200),(0,0,0),1850),('top_down',(0,0,1900),(0,1,0),1550),('spawn',(-300,260,39),(-90,170,28),None)]:
 cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if ortho else 'PERSP';cam.data.ortho_scale=ortho or 1000;cam.data.lens=28
 scene.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Map10OriginalComposition.blend'));print('MAP10_RENDER_DONE')
