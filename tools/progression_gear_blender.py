"""Blender-authored progression props. Run: blender -b --python tools/progression_gear_blender.py.
References: vault approved GEAR-02/03/07/09, inspected 2026-11-16.
1 unit=1 stud; front -Y, Z up. No asset upload or Roblox runtime claim.
"""
import bpy, math, json, os, pathlib, zipfile
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1]/'build/progression-gear-assets'
ROOT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
M={}
for name,color,metal in [('Teal',(0.035,.23,.25,1),.5),('Brass',(.65,.39,.10,1),.75),('Dark',(.025,.035,.045,1),.3),('Cyan',(.03,.9,1,1),.1),('Purple',(.12,.035,.23,1),.45),('Violet',(.65,.08,1,1),.15)]:
 m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.32
 if name in ('Cyan','Violet'):p.inputs['Emission Color'].default_value=color;p.inputs['Emission Strength'].default_value=1.5
 M[name]=m
parts=[]
def align_normals():
 if bpy.app.version >= (5,2,0):
  bpy.ops.mesh.set_normals_from_faces()
 else:
  bpy.ops.mesh.normals_make_consistent(inside=False)
def finish(o,name,mat):
 o.name=name;o.data.materials.append(M[mat]);parts.append(o);return o
def box(name,pos,size,mat,bevel=.04):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Machined softened edge','BEVEL');mod.width=bevel;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
 return finish(o,name,mat)
def lathe(name,profile,mat,pos=(0,0,0),axis='Z',n=40):
 # Closed ring section profile, including inner wall for genuinely hollow geometry.
 verts=[]
 for r,z in profile:
  for j in range(n):
   a=j*math.tau/n;v=Vector((r*math.cos(a),r*math.sin(a),z))
   if axis=='Y':v=Vector((v.x,-v.z,v.y))
   verts.append(tuple(v+Vector(pos)))
 faces=[]
 for k in range(len(profile)):
  for j in range(n):faces.append((k*n+j,k*n+(j+1)%n,((k+1)%len(profile))*n+(j+1)%n,((k+1)%len(profile))*n+j))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
 for p in mesh.polygons:p.use_smooth=True
 return finish(o,name,mat)
def cylinder(name,pos,r,depth,mat,axis='Z'):
 return lathe(name,[(.001,-depth/2),(r,-depth/2),(r,depth/2),(.001,depth/2)],mat,pos,axis)
def ring(name,pos,r,thick,mat,axis='Z'):
 return lathe(name,[(r-thick,-thick/2),(r,-thick/2),(r,thick/2),(r-thick,thick/2)],mat,pos,axis)
def rod(name,a,b,r,mat):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,name,mat)
def mic():
 lathe('Tapered microphone grip',[(.04,-.7),(.17,-.7),(.21,.55),(.04,.55)],'Teal')
 for z,r in [(-.7,.2),(-.59,.19),(.47,.24),(.58,.27),(.91,.3),(1.26,.26)]:ring('Turned brass collar',(0,0,z),r,.045,'Brass')
 lathe('Rounded capsule head',[(.01,.54),(.24,.54),(.30,.72),(.3,1.08),(.25,1.28),(.01,1.28)],'Dark')
 for z in [.66+i*.065 for i in range(9)]:ring('Grille circumferential wire',(0,0,z),.302 if z<1.12 else .28,.013,'Brass')
 for j in range(24):
  a=j*math.tau/24;rod('Grille axial wire',(.294*math.cos(a),.294*math.sin(a),.68),(.294*math.cos(a),.294*math.sin(a),1.10),.009,'Brass')
 ring('Cyan status band',(0,0,.89),.314,.045,'Cyan')
 for z in [-.42,-.12,.18]:
  for s in [-1,1]:rod('Mosaic diamond inlay',(0,-.208,z-.13),(s*.13,-.208,z),.013,'Brass');rod('Mosaic diamond inlay',(s*.13,-.208,z),(0,-.208,z+.13),.013,'Brass')
 box('Mute switch',(0,-.218,.36),(.10,.045,.12),'Dark',.015)
def boombox():
 box('Outer brass chassis',(0,0,.7),(2.7,.65,1.5),'Brass',.13);box('Teal face',(0,-.36,.7),(2.56,.12,1.34),'Teal',.11)
 for x in [-.83,.83]:
  cylinder('Dark speaker recess',(x,-.46,.7),.52,.08,'Dark','Y');ring('Speaker bezel',(x,-.53,.7),.49,.055,'Brass','Y')
  lathe('Sculpted cone',[(.05,0),(.40,0),(.4,.03),(.14,.14),(.05,.14)],'Brass',(x,-.53,.7),'Y')
  cylinder('Driver dust cap',(x,-.70,.7),.14,.08,'Dark','Y')
  for j in range(7):rod('Speaker grille',(x-.29,-.73,.43+j*.085),(x+.29,-.73,.43+j*.085),.008,'Dark')
 box('EQ display',(0,-.45,1.08),(.53,.08,.34),'Dark',.03)
 for i in range(6):box('EQ phosphor',( -.21+i*.083,-.50,1.04),(.04,.025,.10+.12*(i%3)/2),'Cyan',.005)
 for x in [-.16,.16]:cylinder('Control dial',(x,-.48,.62),.075,.09,'Brass','Y')
 for x in [-.94,.94]:box('Handle mount',(x,0,1.58),(.16,.22,.4),'Brass')
 box('Carry handle',(0,0,1.80),(2.02,.22,.16),'Brass');box('Handle grip',(0,-.01,1.80),(1.32,.25,.19),'Dark')
 for x in [-1,1]:box('Rubber foot',(x,0,-.10),(.4,.5,.15),'Dark')
def cannon():
 cylinder('Reactor body',(0,.2,.5),.47,1.4,'Teal','Y')
 for y in [-.42,.05,.65]:ring('Brass reactor band',(0,y,.5),.50,.10,'Brass','Y')
 for a in [0,math.pi/2,math.pi,3*math.pi/2]:
  x,z=.45*math.cos(a),.5+.45*math.sin(a);rod('Cyan reactor rail',(x,-.3,z),(x,.58,z),.07,'Cyan')
 lathe('Parabolic dish',[(.20,.0),(.35,.12),(.60,.32),(.88,.60),(.92,.66),(.86,.68),(.55,.37),(.29,.17),(.16,.08)],'Teal',(0,-.46,.5),'Y')
 ring('Rolled dish rim',(0,-1.13,.5),.93,.065,'Brass','Y')
 cylinder('Emitter nose',(0,-1.02,.5),.14,.36,'Dark','Y');ring('Emitter glow',(0,-1.22,.5),.17,.04,'Cyan','Y')
 for a in [0,math.tau/3,2*math.tau/3]:rod('Dish radial brass brace',(.2*math.cos(a),-1.13,.5+.2*math.sin(a)),(.86*math.cos(a),-1.13,.5+.86*math.sin(a)),.035,'Brass')
 cylinder('Rear damper',(0,1,.5),.51,.38,'Dark','Y');ring('Rear damper edging',(0,1.2,.5),.5,.05,'Brass','Y')
 box('Pistol grip',(0,.65,-.18),(.24,.28,.65),'Dark');rod('Forward grip',(-.48,-.3,.2),(-.70,-.3,-.18),.09,'Dark')
def organ():
 box('Backpack core',(0,0,.8),(1.7,.6,1.9),'Purple',.15)
 box('Brass lower frame',(0,-.03,-.17),(1.8,.7,.17),'Brass')
 for x in [-.78,.78]:box('Brass side frame',(x,-.35,.65),(.12,.15,1.65),'Brass')
 for i,x in enumerate([-.66,-.44,-.22,0,.22,.44,.66]):
  h=1.6+(.66-abs(x))*1.7
  lathe('Hollow organ pipe',[(.065,0),(.09,0),(.09,h),(.065,h)],'Brass',(x,.05,.7),n=24)
  box('Pipe acoustic slit',(x,-.049,1.05),(.10,.022,.18),'Dark',.01)
 for i,x in enumerate([-.45,-.225,0,.225,.45]):
  h=.6+(.45-abs(x))*1.0
  lathe('Front organ pipe',[(.05,0),(.075,0),(.075,h),(.05,h)],'Brass',(x,-.49,.35),n=24)
 for s in [-1,1]:
  pts=[(s*.66,-.45,.1),(s*.66,-.45,1.3),(s*.4,-.45,1.7),(0,-.45,2.03)]
  for a,b in zip(pts,pts[1:]):rod('Gothic frame',a,b,.055,'Brass')
  pts=[(s*.55,-.49,.1),(s*.55,-.49,1.25),(s*.30,-.49,1.62),(0,-.49,1.86)]
  for a,b in zip(pts,pts[1:]):rod('Violet tracing',a,b,.025,'Violet')
  box('Back strap',(s*.48,.4,.65),(.13,.16,1.9),'Dark')
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.24,location=(0,-.60,.22));o=bpy.context.object;o.scale=(.7,.6,1.6);finish(o,'Faceted central crystal','Violet')

report={}
for name,fn in [('MosaicMic',mic),('StreetBoombox',boombox),('SonicCannon',cannon),('CelestialOrgan',organ)]:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);parts=[];fn()
 # Collapse by material for modest draw-call count while preserving designed geometry.
 joined=[]
 for mat in M:
  subset=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials[0].name==mat]
  if not subset:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in subset:o.select_set(True)
  bpy.context.view_layer.objects.active=subset[0];bpy.ops.object.join();o=bpy.context.object;o.name=name+'_'+mat
  bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');align_normals();bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT');joined.append(o)
 directory=ROOT/name;directory.mkdir(exist_ok=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in joined:o.select_set(True)
 bpy.context.view_layer.objects.active=joined[0]
 meshes=[]
 for o in joined:
  o.data.calc_loop_triangles();tri=len(o.data.loop_triangles)
  assert tri<20000 and len(o.data.uv_layers)==1 and len(o.data.materials)==1
  assert all(math.isfinite(v) for vert in o.data.vertices for v in vert.co)
  meshes.append({'name':o.name,'triangles':tri,'uvMaps':1,'materials':1})
 report[name]={'meshes':meshes,'triangles':sum(m['triangles'] for m in meshes),'nativeStudioVerified':False}
 bpy.context.scene.unit_settings.system='NONE'
 bpy.ops.export_scene.fbx(filepath=str(directory/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_scale_options='FBX_SCALE_UNITS',axis_forward='Z',axis_up='Y',add_leaf_bones=False,bake_anim=False)
 bpy.ops.export_scene.gltf(filepath=str(directory/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
 # Camera and lighting are kept in editable source, never selected for exports.
 coords=[o.matrix_world@Vector(c) for o in joined for c in o.bound_box];center=sum(coords,Vector())/len(coords)
 extent=max(max(p[i] for p in coords)-min(p[i] for p in coords) for i in range(3))
 bpy.ops.object.camera_add(location=center+Vector((extent*1.2,-extent*1.8,extent*.9)));cam=bpy.context.object;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=extent*1.45;bpy.context.scene.camera=cam
 for loc,power,size in [((4,-6,8),1100,5),((-4,-2,4),700,4),((1,5,6),1300,3)]:
  bpy.ops.object.light_add(type='AREA',location=center+Vector(loc));o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=False;scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.world.color=(.16,.16,.16);scene.render.image_settings.file_format='PNG';scene.render.filepath=str(directory/'preview.png')
 bpy.ops.wm.save_as_mainfile(filepath=str(directory/(name+'.blend')));bpy.ops.render.render(write_still=True)
 # Actual exporter roundtrip, not merely a file existence assertion.
 for ext in ['fbx','glb']:
  bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
  if ext=='fbx':bpy.ops.import_scene.fbx(filepath=str(directory/(name+'.fbx')))
  else:bpy.ops.import_scene.gltf(filepath=str(directory/(name+'.glb')))
  obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(obs)==len(meshes)
  for o in obs:assert len(o.data.vertices)>0 and all(math.isfinite(v) for p in o.data.vertices for v in p.co)
  report[name][ext+'Roundtrip']=True
(ROOT/'validation.json').write_text(json.dumps(report,indent=2))
(ROOT/'README.txt').write_text('Four Blender-authored gear props from inspected approved vault GEAR-02/03/07/09 references. Native .blend sources, FBX and GLB exports, rendered previews. One unit = one stud, Blender front -Y and Z up. FBX Z Forward/Y Up with FBX Unit Scale; GLB Y Up. Import Scale Unit Studs; verify axes and hand/back fit in disposable local Studio before runtime activation. Upload to Roblox OFF while iterating. No uploads performed. One UV map and material per joined mesh. Flat materials, no texture dependency. Meshes are multipart props, NOT Marketplace avatar submissions. Overlapping manufactured components retained. Each export roundtripped in Blender; Studio, character clipping, material parity and mobile performance remain unverified. Cyan/violet emission is Blender preview appearance and requires explicit Roblox material setup. Preserve previous runtime visuals until validated replacements. See validation.json for measured triangles. Rebuild with blender -b --python tools/progression_gear_blender.py.\n')
with zipfile.ZipFile(ROOT.parent/'Progression-Gear-Blender.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in ROOT.rglob('*'):
  if p.is_file() and p.suffix!='.blend1':z.write(p,p.relative_to(ROOT))
 z.write(__file__,'progression_gear_blender.py')
print(json.dumps(report,indent=2))
