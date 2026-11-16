"""Original Blender look package from tested runtime accessory geometry, NOT uploaded or a rig replacement.
Run with Python; creates per-resident FBX/GLB and one .blend/contact preview in build/supporting-npcs.
No external assets. Bone/animation installation requires native Studio validation.
"""
from pathlib import Path
import json,sys,subprocess,importlib.util
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/supporting-npcs'
if '--blender-stage' not in sys.argv:
 spec=importlib.util.spec_from_file_location('npc_test',ROOT/'tests/supporting_npcs.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 roster=[]
 import trainer_preview_geometry
 for line in (mod.run()+trainer_preview_geometry.run()).splitlines():
  row=line.split('|')
  if row[0]=='NPC':roster.append(dict(name=row[1],home=[float(row[2]),float(row[3])],kind=row[4],parts=[]))
  elif row[0]=='PART':roster[-1]['parts'].append(dict(name=row[1],target=row[2],size=list(map(float,row[3:6])),offset=list(map(float,row[6:9])),color=list(map(float,row[9:12]))))
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/'manifest.json').write_text(json.dumps({'status':'Original static look package; no upload, rig or animation integration','stud_units':True,'residents':roster},indent=2))
 subprocess.run(['blender','-b','--python',str(Path(__file__).resolve()),'--','--blender-stage'],check=True)
 sys.exit()
import bpy,math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
roster=json.loads((OUT/'manifest.json').read_text())['residents']
materials={}
def material(rgb):
 k=tuple(rgb)
 if k not in materials:
  m=bpy.data.materials.new('RGB_'+'_'.join(map(str,rgb)));m.diffuse_color=tuple(v/255 for v in rgb)+(1,);m.use_nodes=True
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=.65;materials[k]=m
 return materials[k]
def xyz(v):return (v[0],-v[2],v[1])
def cube(name,size,position,color,parent):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(position));o=bpy.context.object;o.name=name;o.dimensions=xyz([size[0],size[1],-size[2]])
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material(color));o.parent=parent
 bevel=o.modifiers.new('Soft silhouette edges','BEVEL');bevel.width=.045;bevel.segments=2
 o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
for index,s in enumerate(roster):
 parent=bpy.data.objects.new(s['name'],None);bpy.context.collection.objects.link(parent)
 shirt={'dj':[32,91,105],'tinker':[81,104,62],'lifeguard':[232,101,75],'archivist':[30,112,117],'trainer':[31,48,67]}[s['kind']]
 positions={'Torso':[0,3,0],'Head':[0,4.5,0],'Left Arm':[-1.5,3,0],'Right Arm':[1.5,3,0],'Left Leg':[-.5,1,0],'Right Leg':[.5,1,0]}
 for name,pos in positions.items():
  size=[2,1,1] if name=='Head' else [2,2,1] if name=='Torso' else [1,2,1]
  color=[224,179,140] if name=='Head' else [44,53,65] if 'Leg' in name else shirt
  cube(name,size,pos,color,parent)
 for part in s['parts']:
  pos=[a+b for a,b in zip(positions[part['target']],part['offset'])]
  cube(part['name'],part['size'],pos,part['color'],parent)
 bpy.ops.object.select_all(action='DESELECT');parent.select_set(True)
 for o in parent.children:o.select_set(True)
 slug=s['name'].replace(' ','_')
 bpy.ops.export_scene.fbx(filepath=str(OUT/(slug+'.fbx')),use_selection=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',add_leaf_bones=False)
 bpy.ops.export_scene.gltf(filepath=str(OUT/(slug+'.glb')),use_selection=True,export_format='GLB')
 parent.location.x=(index%4)*5.5-8.25
 parent.location.y=-8*(index//4)
# Preview-only ground/camera/light are excluded from exports.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.03));bpy.context.object.data.materials.append(material([22,31,42]))
bpy.ops.object.light_add(type='AREA',location=(0,5,12));bpy.context.object.data.energy=2300;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=14
bpy.ops.object.camera_add(location=(10,29,20));camera=bpy.context.object;camera.rotation_euler=(Vector((0,-3,2.5))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=29
scene=bpy.context.scene;scene.camera=camera;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.color=(.22,.22,.22);scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'roster.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'SupportingResidents.blend'));bpy.ops.render.render(write_still=True)
camera.location=(-11,-32,17);camera.rotation_euler=(Vector((0,-3,2.5))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(OUT/'roster-back.png');bpy.ops.render.render(write_still=True)
print('PASS seven actual-runtime costume previews exported; NOT uploaded or runtime mesh-integrated')
