"""Bounded local composition proxy from actual CompactCity construction, not native Roblox."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys,tempfile,struct,time
R=Path(__file__).resolve().parents[1]
FILES=['src/ReplicatedStorage/Shared/CompactLayout.luau','src/ServerScriptService/CompactCity.luau','src/ServerScriptService/World.luau','src/ReplicatedStorage/Shared/TrainingRules.luau']
def export(out):
 snapshots={f:(R/f).read_bytes() for f in FILES+['tests/compact_world.py']}
 source_hashes={f:hashlib.sha256(b).hexdigest() for f,b in snapshots.items()}
 tree=ast.parse(snapshots['tests/compact_world.py'].decode('utf-8-sig'))
 literals={t.id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) for t in n.targets if isinstance(t,ast.Name)}
 layout,city,world,training=[snapshots[f].decode('utf-8-sig') for f in FILES]
 loop=world[world.index('    for index,originalTier in ipairs(TrainingRules.Tiers)'):world.index('    if layout.traffic~=false then')]
 pre=literals['setup']
 code=pre+layout+literals['between']+city+"\nend)()\nlocal result=City.Build({})\nlocal TrainingRules=(function()\n"+training+"\nend)()\n"+r'''local Config={CompactCity=true,CityLayout=Layout};local C={green=Color3.fromRGB(0,255,0),gold=Color3.fromRGB(255,203,99)}
Vector3.zero=Vector3.new(0,0,0);local World={Bots={}};local parent={}
local function part(_,name,size,position,color,material,collidable)local p=Instance.new('Part');p.Name=name;p.Size=size;p.Position=position;p.Color=color;p.CanCollide=collidable~=false;return p end
local function billboard()return {Parent={}}end;local function makeBot()end
'''+loop+r'''
for _,p in ipairs(nodes)do if p.ClassName=='Part' then
 print(string.format('GEOM|%s|%g|%g|%g|%g|%g|%g|%g|%g|%g|%g',p.Name,p.Position.X,p.Position.Y,p.Position.Z,p.Size.X,p.Size.Y,p.Size.Z,p.Color.R,p.Color.G,p.Color.B,p.Transparency or 0))
end end
'''
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.city_proxy_',dir=R/'build',delete=False)as f:f.write(code);temp=Path(f.name)
 try:result=subprocess.run(['luau',str(temp)],capture_output=True,text=True,timeout=20,check=True)
 finally:temp.unlink()
 parts=[]
 for line in result.stdout.splitlines():
  if line.startswith('GEOM|'):
   _,name,*values=line.split('|');v=list(map(float,values));parts.append({'name':name,'position':v[:3],'size':v[3:6],'color':[x/255 for x in v[6:9]],'transparency':v[9]})
 assert 0<len(parts)<400
 assert all((R/f).read_bytes()==b for f,b in snapshots.items()),'Source changed during export; recapture required'
 out.mkdir(parents=True,exist_ok=True);(out/'geometry.json').write_text(json.dumps(parts,indent=2))
 manifest={'sources':{f:source_hashes[f] for f in FILES},'mockHarnessSha256':source_hashes['tests/compact_world.py'],'sourceSnapshotVerifiedUnchanged':True,'parts':len(parts),'export':'Actual CompactCity.Build and actual World trainer construction fragment with mocked Instances; no copied geometry coordinates','limits':['No NPCs, HUD, text labels, prompts or native lighting','Other World-added runtime geometry omitted','Axis-aligned cube geometry and proxy materials; not Roblox parity, physics, FPS or gameplay verification'],'nativeExecuted':False}
 (out/'provenance.json').write_text(json.dumps(manifest,indent=2));print('EXPORTED',len(parts),out)
def worker(out):
 import bpy
 from mathutils import Vector
 parts=json.loads((out/'geometry.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True)
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=False;scene.cycles.max_bounces=3
 scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.resolution_x=800;scene.render.resolution_y=450;scene.render.resolution_percentage=100
 scene.world=bpy.data.worlds.new('Proxy daylight');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.66,.8,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
 scene.view_settings.view_transform='Standard';materials={}
 def xyz(v):return (v[0],-v[2],v[1])
 for p in parts:
  if p['transparency']>=1:continue
  bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p['position']));obj=bpy.context.object;obj.name=p['name'];sz=p['size'];obj.dimensions=(sz[0],sz[2],sz[1])
  key=(*p['color'],p['transparency'])
  if key not in materials:
   m=bpy.data.materials.new('SourceColor');m.use_nodes=True;shader=m.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(*p['color'],1);shader.inputs['Alpha'].default_value=1-p['transparency'];shader.inputs['Roughness'].default_value=.85;materials[key]=m
  obj.data.materials.append(materials[key])
 bpy.ops.object.light_add(type='SUN',location=(0,0,300));sun=bpy.context.object;sun.rotation_euler=(.4,-.5,-.3);sun.data.energy=2
 bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam
 views=[('overview',(650,650,700),(0,0,0),True),('spawn',(-270,10,145),(-270,5,65),False),('practice',(-250,8,65),(-281,6,65),False),('arena',(-175,10,50),(-100,7,50),False)]
 for name,pos,target,ortho in views:
  cam.location=xyz(pos);cam.rotation_euler=(Vector(xyz(target))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if ortho else 'PERSP';cam.data.ortho_scale=1400;cam.data.lens=28;cam.data.clip_end=5000
  scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 print('CITY_PROXY_RENDERED four views; no native claims')
def main():
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--phase',choices=['before','after'],default='before');a.add_argument('--export-only',action='store_true');a.add_argument('--render-only',action='store_true');args=a.parse_args()
 out=R/'build/compact-city-lookdev'/args.phase
 if not args.render_only:export(out)
 if args.export_only:return
 exe=Path('C:/Program Files/Blender Foundation/Blender 5.2/blender.exe');assert exe.is_file()
 tool_bytes=Path(__file__).read_bytes();geometry_bytes=(out/'geometry.json').read_bytes();started=time.time_ns()
 result=subprocess.run([str(exe),'--background','--factory-startup','--disable-autoexec','--python',str(Path(__file__).resolve()),'--','--worker',str(out)],capture_output=True,text=True,timeout=240,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 (out/'render.log').write_text(result.stdout+result.stderr);assert result.returncode==0,(result.stdout+result.stderr)[-2000:]
 assert Path(__file__).read_bytes()==tool_bytes and (out/'geometry.json').read_bytes()==geometry_bytes,'Render inputs changed during run'
 expected={'overview.png','spawn.png','practice.png','arena.png'}
 assert {f.name for f in out.glob('*.png')}==expected,'Unexpected or missing PNG outputs'
 outputs={}
 for name in sorted(expected):
  f=out/name;b=f.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n' and b[12:16]==b'IHDR' and struct.unpack('>II',b[16:24])==(800,450),name
  assert f.stat().st_mtime_ns>=started-2_000_000_000,'Stale render: '+name
  outputs[name]=hashlib.sha256(b).hexdigest()
 p=out/'provenance.json';m=json.loads(p.read_text());m['outputs']=outputs;m['toolSha256']=hashlib.sha256(tool_bytes).hexdigest();m['geometrySha256']=hashlib.sha256((out/'geometry.json').read_bytes()).hexdigest();m['render']={'samples':8,'threads':4,'resolution':[800,450],'timeoutSeconds':240,'blender':str(exe)};p.write_text(json.dumps(m,indent=2));print('RENDER COMPLETE',out)
if __name__=='__main__':
 if '--worker' in sys.argv:worker(Path(sys.argv[sys.argv.index('--worker')+1]))
 else:main()
