import bpy,math,json
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[2]/'build'/'boss-models';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
def align_normals():
 if bpy.app.version >= (5,2,0):
  bpy.ops.mesh.set_normals_from_faces()
 else:
  bpy.ops.mesh.normals_make_consistent(inside=False)
def mat(n,c,metal=0,em=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.38
 if em:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=em
 return m
brass=mat('Brass',(.65,.39,.095),.7);teal=mat('Teal enamel',(.015,.23,.25),.5);cyan=mat('Cyan signal',(.03,.95,.9),.15,2);stone=mat('Stone',(.22,.24,.28));black=mat('Speaker charcoal',(.018,.024,.035));amber=mat('Amber bass',(.95,.38,.025),.2,1.5);purple=mat('Violet coat',(.19,.035,.36),.2);navy=mat('Midnight',(.035,.025,.09));ivory=mat('Ivory gloves',(.7,.73,.85));violet=mat('Bell runes',(.6,.16,.98),.2,1.3)
objects=[]
def finish(o,n,m):o.name=n;o.data.materials.append(m);objects.append(o);return o
def cube(n,p,s,m,b=.06):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:
  mod=o.modifiers.new('Soft bevel','BEVEL');mod.width=b;mod.segments=1;bpy.ops.object.modifier_apply(modifier=mod.name)
 return finish(o,n,m)
def cone(n,p,r1,r2,h,m,verts=12):
 bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r1,radius2=r2,depth=h,location=p);return finish(bpy.context.object,n,m)
def ring(n,p,r,m,minor=.1):
 bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=6,major_radius=r,minor_radius=minor,location=p,rotation=(math.pi/2,0,0));return finish(bpy.context.object,n,m)
def rod(n,a,b,r,m):
 a,b=Vector(a),Vector(b);o=cone(n,(a+b)/2,r,r,(b-a).length,m,8);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def plate(n,pts,depth,m):
 vs=[(x,y,z) for y in [-depth/2,depth/2] for x,z in pts];L=len(pts);fs=[tuple(reversed(range(L))),tuple(range(L,2*L))]+[(i,(i+1)%L,(i+1)%L+L,i+L) for i in range(L)];me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);return finish(o,n,m)
def bodylimbs(m):
 for x in [-1,1]:
  cube('Boot',(x,-.25,.4),(1.5,2,.8),black)
  cube('Greave',(x,0,1.8),(1.2,1.3,2.2),m)
  cube('Arm',(x*2.5,0,4.9),(1.3,1.4,2.6),m)
  cube('Gauntlet',(x*2.5,-.1,3.5),(1.5,1.6,1.2),brass)
# Ignis: opera armor, organ-pipe shoulders, cyan sculpted flame plume, tuning fork.
steel=mat('Gunmetal steel',(.055,.085,.12),.65);orange=mat('Molten copper',(.9,.15,.025),.6);blue=mat('Azure flame',(.02,.45,1),.1,2)
bodylimbs(steel)
cube('Breastplate',(0,0,5.2),(3,1.9,2.6),steel)
for side in [-1,1]:
 o=plate('Orange fauld',[(side*.15,4.3),(side*1.7,4.6),(side*1.5,2.6),(side*.8,2.8)],.12,orange);o.location.y=-1
 rod('Chest copper',(.2*side,-1.01,4.8),(1.3*side,-1.01,6.4),.13,orange)
 cube('Pauldron',(2.3*side,0,6.3),(1.6,2,.65),steel)
 for j in range(3):
  x=side*(1.85+j*.38);h=1+.25*j
  cone('Organ pipe',(x,.15,6.6+h/2),.15,.15,h,orange)
  cone('Pipe flame',(x,.15,6.6+h+.35),.17,0,.7,blue,5)
ring('Sonic heart',(0,-1.05,5.3),.63,cyan,.13)
cube('Helm',(0,0,7.2),(1.6,1.35,1.65),steel)
for side in [-1,1]:cube('Eye slit',(side*.4,-.71,7.4),(.55,.1,.17),cyan,.02)
rod('Face trim',(0,-.74,6.5),(0,-.74,7.8),.1,orange)
for x,h in [(-.45,1.1),(0,1.8),(.45,1.35)]:
 o=plate('Azure flame',[(x-.22,7.9),(x-.35,8.4),(x,8.2+h*.8),(x+.15,8.0+h),(x+.25,8.2)],.22,blue);o.location.y=.1
rod('Fork grip',(-2.5,-1.15,3.7),(-2.5,-1.15,2.7),.15,orange)
cube('Fork bridge',(-2.5,-1.15,2.6),(1.4,.3,.35),orange)
for x in [-3.05,-1.95]:
 o=plate('Molten tuning prong',[(x-.16,2.65),(x+.16,2.65),(x+.16,.5),(x,.2),(x-.16,.5)],.2,amber);o.location.y=-1.15
rod('Opera microphone',(2.5,-.3,3.6),(3.1,-.4,3.6),.12,orange)
cone('Microphone head',(3.15,-.4,3.6),.27,.27,.4,amber,12).rotation_euler.y=math.pi/2
groups={'PyroTenorIgnis_L50':objects};objects=[]
# Leviathan: coiled stone body (not humanoid), coral ridges and open sonar mouth.
sea=mat('Sea stone',(.18,.32,.31));coral=mat('Coral',(.65,.14,.26));shell=mat('Shell highlight',(.48,.57,.49));deep=mat('Deep throat',(.025,.09,.12))
def rock(n,p,scale,m):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=p);o=bpy.context.object;o.scale=scale;return finish(o,n,m)
# Lifted closed coil, radius2.3 fits8-stud footprint.
for i in range(16):
 a=i*math.tau/16;x=math.cos(a)*2.3;y=math.sin(a)*2.3
 rock('Coil stone',(x,y,1.15+math.sin(a)*.25),(1,.8,.95),sea if i%2 else shell)
 if i%3==0:
  for j in range(2):rod('Coral branch',(x,y,1.8),(x+.25*(j*2-1),y,2.6),.12,coral)
for x,y,z,r in [(1.8,1,2.5,1),(1.5,1.1,3.6,1.1),(.9,.7,4.8,1.15),(0,.2,5.8,1.15)]:
 rock('Raised neck',(x,y,z),(r,.9,r),sea)
 rock('Dorsal stone',(x,y+.7,z+.5),(.45,.6,.7),shell)
# Wide upper/lower jaws frame cyan throat rings, front=-Y.
rock('Skull',(0,-.55,7.35),(1.6,1,1),sea)
rock('Upper snout',(0,-1.4,7.1),(1.6,1,.55),shell)
rock('Lower jaw',(0,-1.2,5.3),(1.45,1,.45),sea)
for x in [-1.15,1.15]:
 rock('Jaw hinge',(x,-.55,6.1),(.55,.55,.95),shell)
 rock('Sonar eye',(x,-1.4,7.45),(.28,.2,.18),cyan)
 for k in range(3):
  cone('Upper fang',(x*(.4+.25*k),-1.8,6.65),0,.12,.55,shell,5)
  cone('Lower fang',(x*(.4+.25*k),-1.8,5.7),.12,0,.45,shell,5)
 rod('Coral horn',(x,-.2,7.8),(x*1.3,.1,8.75),.16,coral)
 rod('Horn fork',(x*1.15,0,8.3),(x*1.7,.1,8.65),.1,coral)
for y,r in [(-.65,.82),(-1.0,.7),(-1.3,.56)]:ring('Sonar throat',(0,y,6.25),r,cyan,.1)
# Two short fins reinforce sea-serpent silhouette.
for side in [-1,1]:
 o=plate('Flank fin',[(side*1.1,4.6),(side*2.2,3.6),(side*2.4,4.9),(side*1.8,5.1)],.18,teal);o.location.y=.2
for o in objects:o.location.z-=.02
# feet/base bottom-normalize the assembly.
bpy.context.view_layer.update();lo=min((o.matrix_world@Vector(v)).z for o in objects for v in o.bound_box)
for o in objects:o.location.z-=lo
groups['LeviathanSubBass_L70']=objects
# Prepare exports in local origin, then move only for source montage.
report={}
for index,(name,obs) in enumerate(groups.items()):
 for o in obs:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');align_normals();bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
  mod=o.modifiers.new('Triangulate','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.context.view_layer.update();pts=[o.matrix_world@Vector(v) for o in obs for v in o.bound_box];bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)];dims=[b-a for a,b in bounds];assert dims[0]<=8 and dims[1]<=8 and dims[2]<=10
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',add_leaf_bones=False)
 bpy.ops.export_scene.gltf(filepath=str(O/(name+'.glb')),use_selection=True,export_format='GLB')
 report[name]={'triangles':sum(len(o.data.polygons) for o in obs),'meshObjects':len(obs),'sourceXYZDimensions':dims,'bounds':bounds,'UV':all(len(o.data.uv_layers)>0 for o in obs),'nativeImported':False}
 for o in obs:o.location.x+=(index-.5)*11
(O/'manifest_50_70.json').write_text(json.dumps(report,indent=2))
# Render actual geometry, not an image-generation mockup.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=3
floor=mat('Studio ground',(.035,.045,.065));cube('Studio floor',(0,0,-.2),(45,22,.3),floor)
scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.16,.22,1)
for pos,power,size in [((0,-12,16),2500,12),((-12,4,12),1800,10),((14,3,13),1800,10)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,4))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(14,-40,18));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,4.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=25;scene.camera=cam
scene.render.resolution_x=1500;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.filepath=str(O/'boss_50_70_montage.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'Boss50_70.blend'));bpy.ops.render.render(write_still=True)
print('BOSS_ART_DONE',json.dumps(report))
