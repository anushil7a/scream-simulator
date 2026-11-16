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
# A clockwork knight with tapered metronome casing and cyan pendulum.
bodylimbs(teal)
plate('Metronome brass casing',[(-2,3),(2,3),(.9,8.8),(-.9,8.8)],1.8,brass)
o=plate('Recessed teal face',[(-1.7,3.25),(1.7,3.25),(.7,8.5),(-.7,8.5)],.15,teal);o.location.y=-.98
cube('Helmet',(0,-1.1,7.3),(1.3,.8,1.3),brass);cube('Cyan visor',(0,-1.53,7.5),(1.05,.08,.18),cyan)
for x in [-1,1]:
 cone('Shoulder brass',(x*2.4,0,6.2),.95,.75,.9,brass)
 for k in range(4):cube('Cyan arm bars',(x*2.5,-.72,4.3+k*.35),(.7,.05,.09),cyan,.01)
for x,z,r in [(0,4.2,.7),(.95,4,.36),(-.8,4.6,.4)]:
 ring('Clock gear',(x,-1.12,z),r,brass)
 for k in range(10):
  a=k*math.tau/10;o=cube('Gear tooth',(x+math.sin(a)*r,-1.12,z+math.cos(a)*r),(.18,.2,.25),brass,.01);o.rotation_euler.y=a
rod('Pendulum',(0,-1.3,4.2),(.55,-1.3,6.7),.065,cyan)
o=plate('Pendulum crescent blade',[(-3.6,1),(-2.9,.55),(.6,.45),(1.9,1.2),(-.5,.9),(-2.2,1.55)],.18,cyan);o.location.y=-1.4
rod('Blade grip',(-2.5,-1.4,1.2),(-2.5,-1.4,3.5),.12,brass)
groups={'WhisperingMetronome':objects};objects=[]
# Broad stone/speaker titan, four head stacks and concentric subwoofer chest.
bodylimbs(stone);cube('Cabinet torso',(0,0,5),(4.3,2.2,3.3),stone);cube('Grille',(0,-1.15,5),(3.9,.12,2.8),black)
for r,m in [(1.35,brass),(1.08,amber),(.8,black),(.5,amber)]:ring('Subwoofer',(0,-1.32,5),r,m,.13)
o=cone('Subwoofer cap',(0,-1.45,5),.42,.42,.3,black,20);o.rotation_euler.x=math.pi/2
cube('Stone head',(0,0,7.6),(1.8,1.6,1.6),stone)
for x in [-.45,.45]:cube('Eye',(x,-.83,7.8),(.42,.09,.22),amber,.03)
for side in [-1,1]:
 for z in [7.3,8.65]:
  cube('Head speaker cabinet',(side*2.1,0,z),(1.3,1.4,1.2),black)
  ring('Head speaker rim',(side*2.1,-.74,z),.42,brass,.07);ring('Head speaker driver',(side*2.1,-.78,z),.25,amber,.05)
 cube('Shoulder slab',(side*2.7,0,6.1),(1.5,1.9,1.6),stone)
 cube('Forearm speaker',(side*2.65,-.82,4.3),(1.35,.7,1.6),black)
 ring('Forearm cone',(side*2.65,-1.2,4.3),.46,brass,.09)
 for k in range(3):cube('Stone toe',(side+k*.38-.38,-1,.45),(.3,.55,.55),stone)
groups['DecibelGolem']=objects;objects=[]
# Slim celestial maestro: split coat, epaulettes, crown and exactly six bells.
for x in [-.65,.65]:
 cube('Boot',(x,-.3,.35),(.9,1.5,.7),navy);cube('Trouser',(x,0,2),(.72,.85,3.2),navy)
cone('Tailcoat',(0,.15,3.7),1.65,.95,3.4,purple,8)
cube('Waistcoat',(0,-.15,5.4),(1.9,1.2,2.6),purple)
for side in [-1,1]:
 o=plate('Gold lapel',[(side*.1,4.6),(side*1.1,6.9),(side*.6,6.4)],.12,brass);o.location.y=-.82
 rod('Sleeve',(side*1,0,6.3),(side*2.2,-.2,4.9),.38,purple)
 cone('Epaulette',(side*1.15,0,6.5),.55,.55,.2,brass)
 cube('Glove',(side*2.3,-.2,4.65),(.5,.6,.7),ivory)
 rod('Coat gold edge',(side*.8,-.66,5.1),(side*1.5,-.66,2.2),.045,brass)
for z in [4.6,5.1,5.6]:cone('Button',(0,-.79,z),.08,.08,.06,brass,8).rotation_euler.x=math.pi/2
cube('Face',(0,0,7.3),(1.05,.95,1.3),ivory,.15)
cube('Mask',(0,-.5,7.5),(.95,.12,.32),violet)
ring('Crown halo',(0,.3,8.1),.8,brass,.1)
for x in [-.65,0,.65]:cone('Crown prong',(x,0,8.4),.18,0,.9,brass,5)
for i,(x,z) in enumerate([(-2.8,8.3),(2.8,8.3),(-3.1,6.8),(3.1,6.8),(-3.1,5.2),(3.1,5.2)]):
 cone('Bell %d'%i,(x,.5,z),.58,.3,.9,purple,12);cone('Bell lip',(x,.5,z-.45),.62,.62,.12,brass,16)
 cone('Bell crown',(x,.5,z+.5),.32,.12,.22,brass,12)
 ring('Bell suspension',(x,.5,z+.72),.15,brass,.04)
 rod('Rune slash',(x-.16,-.02,z+.18),(x+.16,-.02,z-.15),.035,violet)
 cone('Bell clapper',(x,.5,z-.57),.11,.11,.2,brass)
groups['EclipseConductor']=objects
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
 for o in obs:o.location.x+=(index-1)*10
(O/'manifest.json').write_text(json.dumps(report,indent=2))
# Render actual geometry, not an image-generation mockup.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=3
floor=mat('Studio ground',(.035,.045,.065));cube('Studio floor',(0,0,-.2),(45,22,.3),floor)
scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.16,.22,1)
for pos,power,size in [((0,-12,16),2500,12),((-12,4,12),1800,10),((14,3,13),1800,10)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,4))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(14,-40,18));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,4.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=33;scene.camera=cam
scene.render.resolution_x=1500;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.filepath=str(O/'boss_montage.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'BossTrio.blend'));bpy.ops.render.render(write_still=True)
print('BOSS_ART_DONE',json.dumps(report))
