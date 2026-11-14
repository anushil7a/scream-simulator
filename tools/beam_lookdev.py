"""Bounded original Blender look-development proxy. Never imports/uploads Roblox assets.
Only translates the pinned cosmetic formulas; no combat range/width or native Neon claim.
"""
from pathlib import Path
import hashlib,json,math,struct,sys,zlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/beam-lookdev'
SOURCES=['src/ReplicatedStorage/Shared/BeamStyle.luau','src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau']
PINNED={'src/ReplicatedStorage/Shared/BeamStyle.luau':'59bccd0163fb94883be138ab22fa62890004fb220799dbe915941ecb32757bc6','src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau':'d0afeb914318a16dc210647d8a4d49c6153a47735b5c58fbb86ffd48b57bf3e0'}
def hashes():return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}

def geometry(level,reduced,age=.6,length=24,width=3):
 tier=math.floor(max(1,min(level,100))/10);rings=0 if reduced else 1+tier//3
 strands=0 if reduced or tier<4 else 2 if tier>=8 else 1
 sparks=0 if reduced or tier<2 else 8 if tier>=7 else 4
 collar='diamond' if tier in (1,2) else 'star' if tier>=9 else 'round'
 ribbon='zigzag' if tier==5 else 'braid' if tier==10 else 'helix'
 turns=2.5 if tier==9 else 3.5 if tier==10 else 1.5
 launch=1 if reduced else .55+.45*(1-(1-min(1,max(0,age/.12)))**3)
 radius=width*(.24+tier*.012)*launch;pulse=1 if reduced else 1+.035*math.sin(age*9)
 detailed=not reduced;high=tier>=8
 gold=(1,220/255,90/255);white=(245/255,252/255,1);black=(0,0,0);parts=[]
 lerp=lambda c1,c2,t:tuple(a+(b-a)*t for a,b in zip(c1,c2))
 def line(a,b,thickness,color,alpha,material='neon'):parts.append(dict(shape='cylinder',a=a,b=b,diameter=thickness,color=color,transparency=alpha,material=material))
 def ball(center,size,color,alpha,material='neon'):parts.append(dict(shape='sphere',center=center,diameter=size,color=color,transparency=alpha,material=material))
 def offset(x,angle,r):return (x,math.cos(angle)*r,math.sin(angle)*r)
 def collarOffset(x,angle,r):
  if collar=='diamond':r/=abs(math.cos(angle))+abs(math.sin(angle))
  elif collar=='star':r*=.72+.28*(.5+.5*math.cos(angle*5))
  return offset(x+(math.cos(angle)*r*.75 if collar=='diamond' else 0),angle,r)
 line((0,0,0),(length,0,0),radius*(1.35 if detailed else 1.65)*pulse,lerp(gold,black,.35) if detailed else gold,.72 if reduced else (.78 if high else .55),'smooth' if detailed else 'neon')
 line((0,0,0),(length,0,0),radius*.85,gold,.32 if reduced else (.7 if high else .18),'smooth' if detailed else 'neon')
 line((0,0,0),(length,0,0),radius*(.10 if detailed else .28),lerp(gold,white,.72) if detailed else white,.45 if reduced else .08,'neon')
 if reduced:ball((length,0,0),min(length,radius*1.5),gold,.3,'neon')
 else:
  depth=min(length,radius*.22);line((length-depth,0,0),(length,0,0),radius*1.25,gold,.18,'smooth')
  ball((0,0,0),radius*.72,gold,.18,'smooth')
  for ring in range(1,rings+1):
   travel=(age*(.6+tier*.025)+ring/rings)%1;r=radius*(.85+.2*math.sin(travel*math.pi))*(1.25 if tier>=1 else 1);phase=age*.9+ring*.6;support=high and ring>1
   for i in range(1,11):line(collarOffset(travel*length,(i-1)*math.pi/5+phase,r),collarOffset(travel*length,(i-.28)*math.pi/5+phase,r),.1 if support else .16+tier*.012,lerp(gold,black,.2) if support else gold,.6+travel*.25 if support else .26+travel*.32,'smooth' if support else 'neon')
  for strand in range(1,strands+1):
   previous=(0,0,0);winding=(-1 if strand==2 else 1) if ribbon=='braid' else 1
   for i in range(1,13):
    t=i/12;phase=t*math.pi*2*turns*winding-age*5+strand*math.pi;radial=radius*.95*math.sin(t*math.pi)
    if ribbon=='zigzag':phase=age*.35+strand*math.pi;radial*=1 if i%2==0 else -1
    point=offset(length*t,phase,radial)
    line(previous,point,.065+tier*.006,lerp(gold,white,.12 if high else .4),.42 if high else .25,'smooth' if high else 'neon');previous=point
  back=min(length*.15,radius*.8)
  for i in range(1,sparks+1):
   phase=i*math.pi*2/sparks+age*(.6 if i%2==0 else -.6)
   line(offset(length,phase,radius*.25),offset(length-back,phase,width*.42),.08+tier*.006,gold,.55 if high else .3,'smooth' if high else 'neon')
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
    obj.name='Original_formula_proxy';key=(tuple(part['color']),part['transparency'],part['material'])
    if key not in materials:
     mat=bpy.data.materials.new('ProxyMaterial');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear()
     output=nodes.new('ShaderNodeOutputMaterial');mix=nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=1-part['transparency']
     transparent=nodes.new('ShaderNodeBsdfTransparent')
     if part['material']=='smooth':
      shader=nodes.new('ShaderNodeBsdfPrincipled');shader.inputs['Base Color'].default_value=(*part['color'],1);shader.inputs['Roughness'].default_value=.65
     else:
      shader=nodes.new('ShaderNodeEmission');shader.inputs[0].default_value=(*part['color'],1);shader.inputs[1].default_value=1
     links=mat.node_tree.links;links.new(transparent.outputs[0],mix.inputs[1]);links.new(shader.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],output.inputs[0]);materials[key]=mat
    obj.data.materials.append(materials[key])
   bpy.ops.object.light_add(type='SUN',location=(12,-20,25));sun=bpy.context.object;sun.rotation_euler=(.6,.2,.3);sun.data.energy=2.5
   bpy.ops.object.camera_add(location=(12,-32,18));cam=bpy.context.object;cam.rotation_euler=(Vector((12,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=29;scene.camera=cam
   name=f'level-{level}-'+('reduced' if reduced else 'regular')
   assert len(parts)<=77 and len(scene.objects)==len(parts)+2
   scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/(name+'.png'))
   bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')))
   bpy.ops.render.render(write_still=True)
   records.append({'case':name,'parts':len(parts),'objectsIncludingCamera':len(scene.objects),'polygons':sum(len(o.data.polygons) for o in scene.objects if o.type=='MESH'),'geometry':parts})
 (OUT/'geometry.json').write_text(json.dumps(records,indent=2))
 print('BEAM_LOOKDEV_WORKER_COMPLETE cases=6 maxObjects=78')

_FONT_5X7={
 'A':('01110','10001','10001','11111','10001','10001','10001'),
 'B':('11110','10001','10001','11110','10001','10001','11110'),
 'C':('01110','10001','10000','10000','10000','10001','01110'),
 'D':('11110','10001','10001','10001','10001','10001','11110'),
 'E':('11111','10000','10000','11110','10000','10000','11111'),
 'F':('11111','10000','10000','11110','10000','10000','10000'),
 'G':('01110','10001','10000','10111','10001','10001','01110'),
 'H':('10001','10001','10001','11111','10001','10001','10001'),
 'I':('01110','00100','00100','00100','00100','00100','01110'),
 'J':('00111','00010','00010','00010','10010','10010','01100'),
 'K':('10001','10010','10100','11000','10100','10010','10001'),
 'L':('10000','10000','10000','10000','10000','10000','11111'),
 'M':('10001','11011','10101','10101','10001','10001','10001'),
 'N':('10001','11001','10101','10011','10001','10001','10001'),
 'O':('01110','10001','10001','10001','10001','10001','01110'),
 'P':('11110','10001','10001','11110','10000','10000','10000'),
 'Q':('01110','10001','10001','10001','10101','10010','01101'),
 'R':('11110','10001','10001','11110','10100','10010','10001'),
 'S':('01111','10000','10000','01110','00001','00001','11110'),
 'T':('11111','00100','00100','00100','00100','00100','00100'),
 'U':('10001','10001','10001','10001','10001','10001','01110'),
 'V':('10001','10001','10001','10001','10001','01010','00100'),
 'W':('10001','10001','10001','10101','10101','11011','10001'),
 'X':('10001','10001','01010','00100','01010','10001','10001'),
 'Y':('10001','10001','01010','00100','00100','00100','00100'),
 'Z':('11111','00001','00010','00100','01000','10000','11111'),
 '0':('01110','10011','10101','10101','11001','10001','01110'),
 '1':('00100','01100','00100','00100','00100','00100','01110'),
 '2':('01110','10001','00001','00110','01000','10000','11111'),
 '3':('11110','00001','00001','01110','00001','00001','11110'),
 '4':('00010','00110','01010','10010','11111','00010','00010'),
 '5':('11111','10000','11110','00001','00001','10001','01110'),
 '6':('01110','10000','11110','10001','10001','10001','01110'),
 '7':('11111','00001','00010','00100','01000','01000','01000'),
 '8':('01110','10001','10001','01110','10001','10001','01110'),
 '9':('01110','10001','10001','01111','00001','00001','01110'),
 '-':('00000','00000','00000','11111','00000','00000','00000'),
 '|':('00100','00100','00100','00100','00100','00100','00100'),
 '.':('00000','00000','00000','00000','00000','01100','01100'),
 ':':('00000','01100','01100','00000','01100','01100','00000'),
 '_':('00000','00000','00000','00000','00000','00000','11111'),
 '/':('00001','00010','00010','00100','01000','01000','10000'),
 ' ':('00000','00000','00000','00000','00000','00000','00000'),
}

def _read_png_rgb(path):
 data=path.read_bytes()
 assert data[:8]==b'\x89PNG\r\n\x1a\n',f'Invalid PNG signature: {path}'
 pos=8;width=height=color_type=None;idat=bytearray()
 while pos<len(data):
  length=struct.unpack('>I',data[pos:pos+4])[0];ctype=data[pos+4:pos+8];cdata=data[pos+8:pos+8+length];pos+=12+length
  if ctype==b'IHDR':
   width,height,bit_depth,color_type,compression,filt,interlace=struct.unpack('>IIBBBBB',cdata)
   assert bit_depth==8 and compression==0 and filt==0 and interlace==0,(bit_depth,color_type,interlace)
  elif ctype==b'IDAT':idat.extend(cdata)
  elif ctype==b'IEND':break
 assert width and height and color_type in (0,2,4,6),f'Unsupported PNG format: {path}'
 bpp={0:1,2:3,4:2,6:4}[color_type];stride=width*bpp;raw=zlib.decompress(bytes(idat))
 assert len(raw)==height*(stride+1),f'Corrupt PNG scanlines: {path}'
 prev=bytearray(stride);rgb=bytearray(width*height*3);out_idx=0
 for row in range(height):
  row_start=row*(stride+1);ftype=raw[row_start];cur=bytearray(raw[row_start+1:row_start+1+stride])
  if ftype==1:
   for i in range(bpp,stride):cur[i]=(cur[i]+cur[i-bpp])&0xFF
  elif ftype==2:
   for i in range(stride):cur[i]=(cur[i]+prev[i])&0xFF
  elif ftype==3:
   for i in range(stride):cur[i]=(cur[i]+(((cur[i-bpp] if i>=bpp else 0)+prev[i])>>1))&0xFF
  elif ftype==4:
   for i in range(stride):
    a=cur[i-bpp] if i>=bpp else 0;b=prev[i];c=prev[i-bpp] if i>=bpp else 0
    p=a+b-c;pa,pb,pc=abs(p-a),abs(p-b),abs(p-c)
    cur[i]=(cur[i]+(a if pa<=pb and pa<=pc else (b if pb<=pc else c)))&0xFF
  elif ftype!=0:raise AssertionError(f'Unsupported PNG filter {ftype}: {path}')
  prev=cur
  if color_type==2:
   rgb[out_idx:out_idx+stride]=cur;out_idx+=stride
  elif color_type==6:
   for x in range(0,stride,4):rgb[out_idx:out_idx+3]=cur[x:x+3];out_idx+=3
  else:
   for x in range(0,stride,bpp):g=cur[x];rgb[out_idx:out_idx+3]=bytes((g,g,g));out_idx+=3
 return width,height,bytes(rgb)

def _has_min_colors(rgb,minimum=10):
 seen=set()
 for i in range(0,len(rgb),3):
  seen.add(rgb[i:i+3])
  if len(seen)>minimum:return True
 return False

def _paste_rgb(canvas,cw,ch,src,sw,sh,dst_x,dst_y):
 row_bytes=sw*3
 for y in range(sh):
  dy=dst_y+y
  if 0<=dy<ch:
   off=(dy*cw+dst_x)*3;canvas[off:off+row_bytes]=src[y*row_bytes:(y+1)*row_bytes]

def _draw_text(canvas,cw,ch,x,y,text,color=(255,255,255),scale=2):
 r,g,b=color;cx=x
 for ch_in in text.upper():
  glyph=_FONT_5X7.get(ch_in,_FONT_5X7[' '])
  for gy,row_bits in enumerate(glyph):
   for gx,bit in enumerate(row_bits):
    if bit=='1':
     for sy in range(scale):
      py=y+gy*scale+sy
      if 0<=py<ch:
       for sx in range(scale):
        px=cx+gx*scale+sx
        if 0<=px<cw:off=(py*cw+px)*3;canvas[off]=r;canvas[off+1]=g;canvas[off+2]=b
  cx+=6*scale

def _png_chunk(tag,data):
 return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xFFFFFFFF)

def _write_png_rgb(path,width,height,rgb):
 stride=width*3;raw=b''.join(b'\x00'+bytes(rgb[y*stride:(y+1)*stride]) for y in range(height))
 ihdr=struct.pack('>IIBBBBB',width,height,8,2,0,0,0)
 path.write_bytes(b'\x89PNG\r\n\x1a\n'+_png_chunk(b'IHDR',ihdr)+_png_chunk(b'IDAT',zlib.compress(raw,6))+_png_chunk(b'IEND',b''))

def main():
 import subprocess,time
 try:
  from PIL import Image,ImageDraw
 except ImportError:
  Image=None;ImageDraw=None
 # Fail if the source expressions supporting this small translation disappear.
 style=(ROOT/SOURCES[0]).read_text();visual=(ROOT/SOURCES[1]).read_text()
 for fragment in ('1+math.floor(tier/3)','tier>=4 and (tier>=8 and 2 or 1)','tier>=2 and (tier>=7 and 8 or 4)','[5]={collar="round",ribbon="zigzag",turns=1.5}','[10]={collar="star",ribbon="braid",turns=3.5}'):
  assert fragment in style,fragment
 for fragment in ('width*(.24+tier*.012)','radius*(detailed and 1.35 or 1.65)*pulse','radius*.85','radius*(detailed and .10 or .28)','age*(.6+tier*.025)','width*.42','collarOffset'):
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
 artifacts={}
 if Image is not None:
  sheet=Image.new('RGB',(1280,930),(10,16,28));draw=ImageDraw.Draw(sheet)
 else:
  sheet_w,sheet_h=1280,930;canvas=bytearray(bytes((10,16,28))*(sheet_w*sheet_h))
 for row,l in enumerate((1,50,100)):
  for col,r in enumerate((False,True)):
   name=f'level-{l}-'+('reduced' if r else 'regular');image=OUT/(name+'.png');blend=OUT/(name+'.blend')
   label=name+' | fixed length24 width3 age0.6s'
   if Image is not None:
    with Image.open(image)as im:
     assert im.size==(640,280) and len(im.convert('RGB').getcolors(640*280) or [])>10
     sheet.paste(im.convert('RGB'),(col*640,row*310+30))
    draw.text((col*640+12,row*310+8),label,fill='white')
   else:
    w,h,rgb=_read_png_rgb(image)
    assert (w,h)==(640,280) and _has_min_colors(rgb,10),f'Invalid or flat PNG: {image}'
    _paste_rgb(canvas,sheet_w,sheet_h,rgb,w,h,col*640,row*310+30)
    _draw_text(canvas,sheet_w,sheet_h,col*640+12,row*310+8,label,(255,255,255),2)
   assert blend.stat().st_size>1000
   for path in (image,blend):artifacts[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
 if Image is not None:
  sheet.save(OUT/'comparison.png')
 else:
  _write_png_rgb(OUT/'comparison.png',sheet_w,sheet_h,canvas)
 for path in (OUT/'comparison.png',OUT/'geometry.json'):artifacts[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
 completed.write_text(json.dumps({'sourceHashes':before,'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'blender':'5.2 installed signed executable','elapsedSeconds':round(time.monotonic()-start,2),'inputs':{'levels':[1,50,100],'length':24,'width':3,'age':.6,'distanceBand':'near <=110; single beam, no pool pressure'},'expectedParts':[15,4,41,4,77,4],'render':{'engine':'Cycles CPU','samples':8,'resolution':[640,280],'threads':4,'timeoutSeconds':240},'artifacts':artifacts,'limits':'Original mathematical proxy; no native Neon, actual combat stats, temporal animation, pooling pressure, player aim or Roblox performance validation.'},indent=2))
 print('PASS six Blender look-development previews and contact sheet; no production/native changes')
 print(completed.read_text())
if __name__=='__main__':
 if '--blender-worker' in sys.argv:worker()
 else:main()
