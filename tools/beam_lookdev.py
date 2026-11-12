"""Bounded original Blender look-development proxy. Never imports/uploads Roblox assets.
Only translates the pinned cosmetic formulas; no combat range/width or native Neon claim.
"""
from pathlib import Path
import hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/beam-lookdev'
SOURCES=['src/ReplicatedStorage/Shared/BeamStyle.luau','src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau']
PINNED={'src/ReplicatedStorage/Shared/BeamStyle.luau':'7d04942802ed56fb09d18002e7a11dc02275783021fc06285433d61599ad58d2','src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau':'89ff773cebcb2d3a5876a6d70e3bc561d3a7573c12119232a5cce950a08eccda'}
def hashes():return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}

def geometry(level,reduced,age=.6,length=24,width=3):
 tier=math.floor(max(1,min(level,100))/10);rings=0 if reduced else 1+tier//3
 strands=0 if reduced or tier<4 else 2 if tier>=8 else 1
 sparks=0 if reduced or tier<2 else 8 if tier>=7 else 4
 launch=1 if reduced else .55+.45*(1-(1-min(1,max(0,age/.12)))**3)
 radius=width*(.24+tier*.012)*launch;pulse=1 if reduced else 1+.035*math.sin(age*9)
 gold=(1,220/255,90/255);white=(245/255,252/255,1);parts=[]
 def line(a,b,thickness,color,alpha):parts.append(dict(shape='cylinder',a=a,b=b,diameter=thickness,color=color,transparency=alpha))
 def ball(center,size,color,alpha):parts.append(dict(shape='sphere',center=center,diameter=size,color=color,transparency=alpha))
 def offset(x,angle,r):return (x,math.cos(angle)*r,math.sin(angle)*r)
 line((0,0,0),(length,0,0),radius*1.65*pulse,gold,.72 if reduced else .68)
 line((0,0,0),(length,0,0),radius*.85,gold,.32 if reduced else .12)
 line((0,0,0),(length,0,0),radius*.28,white,.45 if reduced else .08)
 ball((length,0,0),min(length,radius*1.5),gold,.3)
 if not reduced:
  ball((0,0,0),radius*1.15,white,.18)
  for ring in range(1,rings+1):
   travel=(age*(.6+tier*.025)+ring/rings)%1;r=radius*(.85+.2*math.sin(travel*math.pi));phase=age*.9+ring*.6
   for i in range(1,11):line(offset(travel*length,(i-1)*math.pi/5+phase,r),offset(travel*length,i*math.pi/5+phase,r),.055+tier*.008,gold,.22+travel*.28)
  for strand in range(1,strands+1):
   previous=(0,0,0)
   for i in range(1,13):
    t=i/12;phase=t*math.pi*(5 if tier>=9 else 3)-age*5+strand*math.pi
    point=offset(length*t,phase,radius*.95*math.sin(t*math.pi))
    line(previous,point,.065+tier*.006,tuple(a+(b-a)*.4 for a,b in zip(gold,white)),.25);previous=point
  for i in range(1,sparks+1):
   phase=i*math.pi*2/sparks+age*(.6 if i%2==0 else -.6)
   line(offset(length,phase,radius*.35),offset(length,phase,width*.47),.08+tier*.006,gold,.3)
 return parts

def worker():
 import bpy
 from mathutils import Vector
 OUT.mkdir(parents=True,exist_ok=True)
 records=[]
 for level in (1,50,100):
  for reduced in (False,True):
   bpy.ops.wm.read_factory_settings(use_empty=True)
   bpy.context.preferences.filepaths.save_version=0
   scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8
   scene.cycles.use_denoising=False;scene.cycles.max_bounces=6;scene.cycles.transparent_max_bounces=16
   scene.render.resolution_x=640;scene.render.resolution_y=280;scene.render.resolution_percentage=100
   scene.render.threads_mode='FIXED';scene.render.threads=4
   scene.world=bpy.data.worlds.new('Dark comparison background');scene.world.use_nodes=True
   scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.008,.015,.028,1)
   scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
   materials={};parts=geometry(level,reduced)
   for part in parts:
    if part['shape']=='cylinder':
     a,b=Vector(part['a']),Vector(part['b']);delta=b-a
     bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=part['diameter']/2,depth=delta.length,location=(a+b)/2)
     obj=bpy.context.object;obj.rotation_mode='QUATERNION';obj.rotation_quaternion=delta.to_track_quat('Z','Y')
     assert (obj.rotation_quaternion @ Vector((0,0,1))).dot(delta.normalized())>.999999,'Cylinder orientation mismatch'
    else:
     bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=part['diameter']/2,location=part['center']);obj=bpy.context.object
    obj.name='Original_formula_proxy';key=(tuple(part['color']),part['transparency'])
    if key not in materials:
     mat=bpy.data.materials.new('Emission transparency approximation');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear()
     output=nodes.new('ShaderNodeOutputMaterial');mix=nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=1-part['transparency']
     transparent=nodes.new('ShaderNodeBsdfTransparent');emission=nodes.new('ShaderNodeEmission');emission.inputs[0].default_value=(*part['color'],1);emission.inputs[1].default_value=1
     links=mat.node_tree.links;links.new(transparent.outputs[0],mix.inputs[1]);links.new(emission.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],output.inputs[0]);materials[key]=mat
    obj.data.materials.append(materials[key])
   bpy.ops.object.camera_add(location=(12,-32,18));cam=bpy.context.object;cam.rotation_euler=(Vector((12,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=29;scene.camera=cam
   name=f'level-{level}-'+('reduced' if reduced else 'regular')
   assert len(parts)<=77 and len(scene.objects)==len(parts)+1
   scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/(name+'.png'))
   bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')))
   bpy.ops.render.render(write_still=True)
   records.append({'case':name,'parts':len(parts),'objectsIncludingCamera':len(scene.objects),'polygons':sum(len(o.data.polygons) for o in scene.objects if o.type=='MESH'),'geometry':parts})
 (OUT/'geometry.json').write_text(json.dumps(records,indent=2))
 print('BEAM_LOOKDEV_WORKER_COMPLETE cases=6 maxObjects=78')

def main():
 import subprocess,time
 from PIL import Image,ImageDraw
 # Fail if the source expressions supporting this small translation disappear.
 style=(ROOT/SOURCES[0]).read_text();visual=(ROOT/SOURCES[1]).read_text()
 for fragment in ('1+math.floor(tier/3)','tier>=4 and (tier>=8 and 2 or 1)','tier>=2 and (tier>=7 and 8 or 4)'):
  assert fragment in style,fragment
 for fragment in ('width*(.24+tier*.012)','radius*1.65*pulse','radius*.85','radius*.28','age*(.6+tier*.025)','width*.47'):
  assert fragment in visual,fragment
 assert [len(geometry(l,r))for l in (1,50,100)for r in (False,True)]==[15,4,41,4,77,4]
 before=hashes();assert before==PINNED,'Source changed: review translation before repinning';OUT.mkdir(parents=True,exist_ok=True)
 completed=OUT/'provenance.json'
 if completed.exists():completed.unlink()
 exe=Path(r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe');start=time.monotonic()
 with (OUT/'blender.log').open('w',encoding='utf-8')as log:
  result=subprocess.run([str(exe),'--background','--factory-startup','--disable-autoexec','--python',str(Path(__file__).resolve()),'--','--blender-worker'],stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW)
 assert result.returncode==0,'Blender failed; inspect build/beam-lookdev/blender.log'
 assert before==hashes(),'Production source changed during render'
 sheet=Image.new('RGB',(1280,930),(10,16,28));draw=ImageDraw.Draw(sheet);artifacts={}
 for row,l in enumerate((1,50,100)):
  for col,r in enumerate((False,True)):
   name=f'level-{l}-'+('reduced' if r else 'regular');image=OUT/(name+'.png');blend=OUT/(name+'.blend')
   with Image.open(image)as im:
    assert im.size==(640,280) and len(im.convert('RGB').getcolors(640*280) or [])>10
    sheet.paste(im.convert('RGB'),(col*640,row*310+30))
   draw.text((col*640+12,row*310+8),name+' | fixed length24 width3 age0.6s',fill='white')
   assert blend.stat().st_size>1000
   for path in (image,blend):artifacts[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
 sheet.save(OUT/'comparison.png')
 for path in (OUT/'comparison.png',OUT/'geometry.json'):artifacts[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
 completed.write_text(json.dumps({'sourceHashes':before,'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'blender':'5.2 installed signed executable','elapsedSeconds':round(time.monotonic()-start,2),'inputs':{'levels':[1,50,100],'length':24,'width':3,'age':.6,'distanceBand':'near <=110; single beam, no pool pressure'},'expectedParts':[15,4,41,4,77,4],'render':{'engine':'Cycles CPU','samples':8,'resolution':[640,280],'threads':4,'timeoutSeconds':240},'artifacts':artifacts,'limits':'Original mathematical proxy; no native Neon, actual combat stats, temporal animation, pooling pressure, player aim or Roblox performance validation.'},indent=2))
 print('PASS six Blender look-development previews and contact sheet; no production/native changes')
 print(completed.read_text())
if __name__=='__main__':
 if '--blender-worker' in sys.argv:worker()
 else:main()
