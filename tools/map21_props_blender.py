"""Original Tidal Foundry study; blender -b --python tools/map21_props_blender.py.
Inspected owner IMG_1527: dark bronze bells/gantries, cyan crystal cage.
Vault-derived constraints: docs/MAP10_REVIEW.md, MAP10_ART_FINISH.md.
No runtime/physics/import/publish. One source unit intended as one stud.
"""
import bpy, math, json, pathlib, hashlib
from mathutils import Vector
OUT=pathlib.Path(__file__).resolve().parents[1]/'assets/drafts/map21-props'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
M={}
for name,c,metal in [('Bronze',(.22,.13,.065,1),.7),('DarkIron',(.035,.065,.07,1),.65),('Cream',(.67,.61,.44,1),0),('Cyan',(.015,.78,.9,1),.1),('Timber',(.19,.12,.07,1),0)]:
 m=bpy.data.materials.new(name);m.diffuse_color=c;m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=c;p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.38
 if name=='Cyan':p.inputs['Emission Color'].default_value=c;p.inputs['Emission Strength'].default_value=2
 M[name]=m
parts=[]; catalog=[]
def finish(o,n,mat):
 o.name=n;o.data.materials.append(M[mat]);parts.append(o);return o
def box(n,p,s,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,mat)
def rod(n,a,b,r,mat='DarkIron',v=10):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,n,mat)
def lathe(n,prof,mat,count=24):
 vs=[(r*math.cos(j*math.tau/count),r*math.sin(j*math.tau/count),z) for r,z in prof for j in range(count)]
 fs=[(i*count+j,i*count+(j+1)%count,((i+1)%len(prof))*count+(j+1)%count,((i+1)%len(prof))*count+j) for i in range(len(prof)) for j in range(count)]
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);return finish(o,n,mat)
def ring(n,r,z,t=.12,mat='Bronze'):
 return lathe(n,[(r-t,z-t),(r,z-t),(r,z+t),(r-t,z+t)],mat)
def export(name,offset):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0]
 # Real geometry, not a render proxy. Keep individually editable mesh objects in source.
 bpy.context.view_layer.update()
 bottom=min((o.matrix_world@Vector(v)).z for o in parts for v in o.bound_box)
 for o in parts:o.location.z-=bottom
 bpy.context.view_layer.update();vs=[o.matrix_world@Vector(v) for o in parts for v in o.bound_box]
 lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
 tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in parts)
 assert tris<4000 and all(math.isfinite(c) for v in vs for c in v)
 path=OUT/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True)
 catalog.append(dict(name=name,triangles=tris,mesh_objects=len(parts),bounds_blender_xyz=[lo,hi],dimensions_studs=[round(hi[i]-lo[i],4) for i in range(3)],file=path.name,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 collection=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(collection)
 for o in parts:
  for old in list(o.users_collection):old.objects.unlink(o)
  collection.objects.link(o);o.location.x+=offset
 parts.clear()
# Lantern cage: open dark uprights protect a faceted crystal with no glass transparency sorting.
lathe('Stone octagonal socket',[(.01,0),(3,0),(3,.5),(2.6,.8),(.01,.8)],'Cream',8)
ring('Lower iron rim',2.35,1,.22,'DarkIron');ring('Upper iron rim',2.35,5.9,.18,'DarkIron')
for j in range(8):
 a=j*math.tau/8;rod('Cage upright %02d'%j,(2.15*math.cos(a),2.15*math.sin(a),.8),(2.15*math.cos(a),2.15*math.sin(a),5.9),.095)
lathe('Luminous faceted crystal',[(.01,1.1),(1.05,1.9),(1.3,4.1),(.01,7.4)],'Cyan',6)
ring('Crystal cradle',1.3,1.8,.12);export('LighthouseCrystalCage',-10)
# Hollow cast bell with thick mouth, neck, suspension eye and visible clapper.
lathe('Hollow bronze bell',[(2.45,.15),(2.5,.45),(2.08,.7),(1.55,1.65),(1.18,3.35),(.7,3.8),(.24,3.8),(.24,3.5),(.86,3.3),(1.25,1.55),(1.85,.55),(2.2,.18)],'Bronze')
ring('Bell skirt bead',2.5,.4,.1);ring('Bell shoulder bead',1.2,3.25,.07)
rod('Clapper stem',(0,0,.55),(0,0,3.4),.13,'DarkIron');lathe('Clapper weight',[(.01,.25),(.4,.45),(.32,.9),(.01,1)],'DarkIron',12)
box('Bell crown',(0,0,4.05),(.8,.5,.5),'Bronze');rod('Suspension pin',(-.7,0,4.2),(.7,0,4.2),.13)
export('FoundryBell',0)
# Standalone braced gantry bay, intended scalable dressing not climbable collision.
for x in [-3.8,3.8]:
 box('Timber upright',(x,0,3.6),(.55,.7,7.2),'Timber');box('Stone foot',(x,0,.3),(1.05,1.2,.6),'Cream')
 for z in [1,5.8]:box('Iron collar',(x,0,z),(.62,.77,.18),'DarkIron')
 rod('Diagonal knee',(x,0,4.8),(x*.53,0,7),.18,'Timber',4)
box('Gantry crossbeam',(0,0,7.15),(9,.85,.7),'Timber')
for x in [-2,0,2]:box('Crossbeam strap',(x,0,7.15),(.18,.92,.77),'DarkIron')
rod('Bell hanging shank',(0,0,5.9),(0,0,6.9),.16,'Bronze');export('GantryBay',10)
# Capstan wheel reads at distance, eight spokes and thick rim; center base mounted.
lathe('Capstan base',[(.01,0),(1.4,0),(1.4,.3),(1,.5),(.01,.5)],'DarkIron',16)
rod('Capstan hub',(0,0,.3),(0,0,1.9),.35,'Bronze',16);ring('Wheel rim',2.0,1.6,.14,'Timber')
for j in range(8):
 a=j*math.tau/8;rod('Wheel spoke %02d'%j,(.25*math.cos(a),.25*math.sin(a),1.6),(2.25*math.cos(a),2.25*math.sin(a),1.6),.1,'Bronze')
export('DockCapstan',18)
(OUT/'manifest.json').write_text(json.dumps({'version':1,'source_units':'1 Blender unit intended as 1 Roblox stud; verify importer scale','glb_up_axis':'Y','origin':'base centered, no baked display offset in exports','individual_triangle_cap':4000,'assets':catalog},indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'TidalFoundryProps.blend'))
# Studio-neutral display only; not runtime lighting.
bpy.ops.object.camera_add(location=(19,-29,23));cam=bpy.context.object;cam.rotation_euler=(Vector((3,0,3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=36;bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(1,-9,18));bpy.context.object.data.energy=2300;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=18
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=False;sc.world.color=(.18,.18,.18);sc.render.resolution_x=1400;sc.render.resolution_y=650;sc.render.resolution_percentage=100;sc.render.filepath=str(OUT/'preview.png');bpy.ops.render.render(write_still=True)
print('MAP21_PROPS_OK',json.dumps(catalog))
