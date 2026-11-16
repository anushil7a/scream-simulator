"""Original five-boss silhouettes, Blender-authored and exported as upload-free runtime geometry.
Run blender --background --python tools/bosses/fidelity.py. Roblox units, Y up, facing -Z.
No external meshes/textures; source reference images stay in the user's vault.
"""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/boss-fidelity';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
C={'gold':(183,137,61),'edge':(233,191,102),'teal':(24,76,80),'cyan':(66,237,232),'dark':(26,32,39),'stone':(110,116,113),'lightstone':(157,159,141),'amber':(255,172,40),'iron':(65,70,79),'orange':(227,101,26),'silver':(147,179,184),'blue':(37,175,255),'purple':(89,40,137),'navy':(29,25,59),'ivory':(208,213,223),'coral':(193,96,126),'sea':(30,76,80),'skin':(91,102,156)}
C.update({'coat':(22,64,83),'white':(233,237,232),'beak':(244,185,31),'leather':(83,55,35)})
# Runtime and Blender share a material hierarchy; colors are authored in sRGB.
METAL={'gold','edge','silver','iron'}
STONE={'stone','lightstone'}
FABRIC={'purple','navy','coat'}
def style(c):
 return {'material':'Metal' if c in METAL else 'Slate' if c in STONE else 'Fabric' if c in FABRIC else 'SmoothPlastic','reflectance':.055 if c in METAL else 0}
M={}
for n,c in C.items():
 m=bpy.data.materials.new(n);m.diffuse_color=tuple((v/255)**2.2 for v in c)+(1,);m.use_nodes=True;q=m.node_tree.nodes.get('Principled BSDF');q.inputs['Base Color'].default_value=m.diffuse_color;q.inputs['Roughness'].default_value=.38 if n in ['gold','edge','silver'] else .65;q.inputs['Metallic'].default_value=.55 if n in ['gold','edge','silver','iron'] else .1
 if n in ['cyan','amber','blue']:q.inputs['Emission Color'].default_value=m.diffuse_color;q.inputs['Emission Strength'].default_value=.65
 if n in STONE or n in FABRIC:
  noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=32 if n in STONE else 65;noise.inputs['Detail'].default_value=2
  bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.035
  m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],q.inputs['Normal'])
 M[n]=m
A=Matrix(((1,0,0),(0,0,1),(0,1,0))) # reflect Z forward; winding corrected below
all_data={};groups={};entries=[];obs=[]
def finish(o,n,c):o.name=n;o.data.materials.append(M[c]);obs.append(o)
def primitive(n,p,s,c,kind='Block',axis=None):
 p=Vector(p);rot=Matrix.Identity(3)
 if axis:
  x=Vector(axis).normalized();z=x.cross(Vector((0,1,0)))
  if z.length<.01:z=x.cross(Vector((0,0,1)))
  z.normalize();y=z.cross(x);rot=Matrix((x,y,z)).transposed()
 entries.append({'name':n,'kind':kind,'position':list(p),'size':s,'rotation':[v for row in rot for v in row],'color':list(C[c]),'glow':c in ['cyan','amber','blue'],**style(c)})
 if kind=='Ball':bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.5)
 elif kind=='Cylinder':
  bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.5,depth=1);o=bpy.context.object;o.rotation_euler[1]=math.pi/2;bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
 else:bpy.ops.mesh.primitive_cube_add(size=1)
 o=bpy.context.object
 if kind=='Ball':
  for face in o.data.polygons:face.use_smooth=True
 elif kind=='Cylinder':
  for face in o.data.polygons:face.use_smooth=len(face.vertices)==4
 # local Roblox axes become Blender x,z,y; reflected geometry safe for primitives
 o.matrix_world=(A@rot@Matrix.Diagonal(Vector(s))).to_4x4();o.location=A@p
 finish(o,n,c)
def box(n,p,s,c):primitive(n,p,s,c)
def ball(n,p,s,c):primitive(n,p,s,c,'Ball')
def cylinder(n,p,r,l,c,axis=(0,0,1)):primitive(n,p,[l,2*r,2*r],c,'Cylinder',axis)
def rod(n,a,b,r,c):
 a,b=Vector(a),Vector(b);cylinder(n,(a+b)/2,r,(b-a).length,c,b-a)
def mesh(n,vs,faces,c):
 # Triangles exported from the authored continuous surface, not disconnected blobs.
 triangles=[]
 for f in faces:
  poly=[Vector(vs[i]) for i in f]
  for tri in tessellate_polygon([poly]):triangles.append([f[v] if isinstance(v,int) else f[poly.index(v)] for v in tri])
 entries.append({'name':n,'kind':'Surface','vertices':vs,'triangles':triangles,'color':list(C[c]),'glow':c in ['cyan','amber','blue'],**style(c)})
 me=bpy.data.meshes.new(n);me.from_pydata([A@Vector(v) for v in vs],[],[tuple(reversed(t)) for t in triangles]);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);finish(o,n,c)
def panel(n,points,z,depth,c):
 L=len(points);vs=[(x,y,z-depth/2) for x,y in points];mesh(n,vs,[list(range(L))],c)
def profile(n,rings,c):
 # One closed continuous four-sided box-modelled surface with changing silhouette.
 vs=[]
 for x,y,z,w,d in rings:vs += [(x-w,y,z-d),(x+w,y,z-d),(x+w,y,z+d),(x-w,y,z+d)]
 fs=[[3,2,1,0]]
 for k in range(len(rings)-1):
  for j in range(4):a=4*k+j;b=4*k+(j+1)%4;fs.append([a,b,b+4,a+4])
 fs.append([len(vs)-4+i for i in range(4)]);mesh(n,vs,fs,c)
def chamfer_head(n,x,y,z,w,h,d,c):
 # Six-sided carved head volume: beveled front cheeks without adding surface cost.
 vs=[]
 for yy,scale in [(y-h/2,1),(y+h/2,.88)]:
  for xx,zz in [(-.65,-1),(.65,-1),(1,-.3),(1,1),(-1,1),(-1,-.3)]:vs.append((x+xx*w*scale,yy,z+zz*d*scale))
 mesh(n,vs,[list(reversed(range(6))),list(range(6,12))]+[[i,(i+1)%6,(i+1)%6+6,i+6] for i in range(6)],c)
def ring(n,p,r,c,width=.09,N=12):
 x,y,z=p
 for k in range(N):
  a=k*math.tau/N;b=(k+1)*math.tau/N
  rod(n,(x+r*math.cos(a),y+r*math.sin(a),z),(x+r*math.cos(b),y+r*math.sin(b),z),width,c)
def wave(n,x,y,z,w,c='cyan',N=7):
 for k in range(N):box(n,(x+(k-(N-1)/2)*w/N,y,z),(.045,.12+.38*abs(math.sin(k*2.1)),.035),c)
def armor_legs(c,spread=1):
 for side in [-1,1]:
  x=side*spread
  box('Boot',(x,.45,-.3),(1.15,.8,1.6),'dark')
  profile('Greave',[(x,.75,0,.48,.55),(x,2.35,.05,.42,.48),(x,3.05,0,.6,.6)],c)
  ball('Knee',(x,2.8,-.51),(.9,.8,.4),'gold' if c=='teal' else 'iron')
def save_group(id):
 global entries,obs
 all_data[id]=entries;groups[id]=obs;entries=[];obs=[]
# METRONOME: broad rounded pauldrons, tapered continuous clock case and exposed gear mechanism.
armor_legs('teal')
profile('ClockCase',[(0,3.5,0,1.55,.8),(0,7.9,0,.66,.65),(0,8.35,0,.5,.45)],'gold')
panel('RecessedClockFace',[(-1.32,3.72),(1.32,3.72),(.48,7.9),(-.48,7.9)],-.83,.08,'teal')
for side in [-1,1]:
 rod('ClockFrame',(side*1.5,3.6,-.9),(side*.6,7.95,-.76),.09,'edge')
 ball('RoundPauldron',(side*2.12,6.35,.02),(1.95,1.85,1.8),'gold')
 ball('TealShoulderEnamel',(side*2.12,6.44,-.18),(1.65,1.55,1.55),'teal')
 rod('Arm',(side*2.2,5.8,0),(side*2.85,4,-.15),.56,'teal')
 for y,x in [(5.5,2.3),(4.7,2.58),(4.05,2.8)]:cylinder('ArmBrassBand',(side*x,y,-.09),.61,.15,'gold',(side*.3,1,0))
 wave('ShoulderWave',side*2.12,6.45,-.99,.95);wave('ArmWave',side*2.6,4.8,-.64,.7)
 ball('Gauntlet',(side*2.95,3.55,-.15),(.85,.85,.8),'gold')
 for j in range(3):rod('Finger',(side*2.65+j*.22*side,3.4,-.45),(side*2.65+j*.22*side,2.95,-.48),.1,'teal')
ball('Helmet',(0,7.1,-.9),(1.05,1.2,.8),'gold');box('Face',(0,7,-1.31),(.8,.7,.06),'teal');box('EyeSlit',(0,7.2,-1.36),(.8,.1,.05),'cyan');wave('MouthWave',0,6.9,-1.36,.6)
for x,y,r in [(0,4.35,.62),(.8,4.05,.35),(-.7,4.7,.32)]:
 cylinder('GearDisk',(x,y,-.98),r,.12,'dark');ring('GearRim',(x,y,-1.07),r,'gold',.085,10)
 for k in range(8):
  a=k*math.tau/8;box('GearTooth',(x+(r+.08)*math.cos(a),y+(r+.08)*math.sin(a),-1.05),(.18,.18,.15),'edge')
 cylinder('GearHub',(x,y,-1.18),r*.28,.16,'edge')
rod('Pendulum',(0,4.35,-1.3),(.75,6.6,-1.3),.065,'gold');ball('PendulumTip',(.75,6.6,-1.3),(.3,.4,.12),'cyan')
rod('SickleHandle',(-2.85,3.5,-.6),(-2.85,2,-.6),.12,'gold')
panel('CrescentBlade',[(-3.55,2.4),(-3.05,1.4),(-1.2,.8),(.9,.95),(1.6,1.35),(-.6,1.2),(-2.25,1.8)],-.6,.12,'cyan')
# Restrained clock-face engraving and dimensional cheek guard; brightest areas remain visor/blade.
for side in [-1,1]:
 rod('VisorBrow',(side*.05,7.32,-1.38),(side*.42,7.42,-1.33),.055,'edge')
 rod('HelmetCheek',(side*.42,7.18,-1.32),(side*.32,6.7,-1.3),.06,'gold')
 for k in range(4):box('ClockTick',(side*(.65+k*.1),6.15-k*.3,-.94),(.2,.025,.04),'silver')
rod('DialHand',(0,5.15,-1.03),(.32,5.63,-1.03),.035,'edge')
save_group('metronome')
# GOLEM: separated squat stone legs, wide speaker shoulders and real skull-like face.
armor_legs('stone',1.05)
profile('StoneChest',[(0,3.45,0,1.05,.65),(0,5.2,0,1.65,.85),(0,6.4,0,1.55,.75)],'stone')
box('ChestGrille',(0,5.2,-.9),(3,.95,.1),'dark')
for r,c,z in [(1.35,'gold',-1.02),(1.17,'dark',-1.13),(.93,'amber',-1.22),(.65,'gold',-1.29),(.4,'dark',-1.36)]:cylinder('ChestSubwoofer',(0,4.95,z),r,.12,c)
profile('Skull',[(0,6.3,-.12,.55,.48),(0,6.8,-.2,.7,.56),(0,7.6,-.12,.8,.57),(0,7.95,0,.58,.42)],'lightstone')
for side in [-1,1]:
 box('EyeSocket',(side*.36,7.25,-.8),(.5,.38,.12),'dark');ball('Eye',(side*.36,7.25,-.89),(.23,.23,.1),'amber')
 rod('Brow',(side*.1,7.48,-.84),(side*.65,7.58,-.8),.13,'stone')
box('Nose',(0,6.98,-.82),(.2,.34,.1),'dark');box('Mouth',(0,6.65,-.73),(1.05,.25,.11),'dark')
for x in [-.4,-.2,0,.2,.4]:box('SkullTooth',(x,6.65,-.8),(.13,.28,.1),'lightstone')
for side in [-1,1]:
 profile('ShoulderCabinet',[(side*2.1,5.4,0,.58,.62),(side*2.1,6.7,0,.78,.72)],'stone');box('ShoulderGrille',(side*2.1,6.15,-.79),(1.2,1.3,.08),'dark')
 rod('ArmPiston',(side*2.1,5.5,0),(side*2.65,3.8,0),.32,'iron')
 box('ForearmSpeaker',(side*2.7,4.05,0),(1.35,1.85,1.4),'stone');cylinder('ArmDriver',(side*2.7,4.1,-.77),.54,.15,'dark');cylinder('ArmCone',(side*2.7,4.1,-.87),.35,.12,'sea')
 box('Fist',(side*2.7,2.9,-.2),(1.2,.9,1.15),'stone')
 for j in range(3):box('Knuckle',(side*2.7+(j-1)*.32,2.9,-.8),(.26,.7,.25),'lightstone')
 for y in [7.1,8.15]:
  box('EarSpeaker',(side*1.75,y,.1),(1.05,1,1),'iron');cylinder('EarDriver',(side*1.75,y,-.45),.35,.1,'gold');cylinder('EarCone',(side*1.75,y,-.52),.21,.06,'dark')
for side in [-1,1]:
 rod('ChestCopperConduit',(side*1.2,6.3,-.84),(side*.85,5.65,-.98),.09,'gold')
 rod('KnuckleEtch',(side*2.4,3.1,-.94),(side*3,3.1,-.94),.035,'amber')
 for k in range(4):box('ShoulderGrilleSlat',(side*2.1,5.7+k*.25,-.86),(1.05,.035,.03),'iron')
 rod('SkullCheek',(side*.65,6.9,-.78),(side*.5,6.55,-.76),.1,'stone')
save_group('golem')
# IGNIS: narrow armoured opera knight, flared skirt, pipe shoulders, tuning fork and blue flame crest.
armor_legs('iron',.73)
profile('ArmoredTorso',[(0,3.1,0,.85,.55),(0,4.5,0,.85,.6),(0,6.1,0,1.2,.65)],'iron')
for side in [-1,1]:
 panel('SkirtArmor',[(side*.15,4),(side*1.05,4.3),(side*1.55,2.1),(side*.4,1.55)],-.45,.3,'orange')
 rod('SkirtTrim',(side*.3,3.8,-.65),(side*.6,1.8,-.65),.09,'silver')
 ball('ShoulderArmor',(side*1.55,5.9,0),(1.6,1.3,1.3),'silver');ball('ShoulderInset',(side*1.55,5.9,-.1),(1.3,1.1,1.2),'iron')
 for k in range(3):
  x=side*(1.2+k*.3);top=6.9+(1-k*.35)
  rod('OrganPipe',(x,6.1,0),(x,top,0),.14,'orange');cylinder('PipeMouth',(x,top+.02,0),.1,.03,'dark',(0,1,0))
 rod('UpperArm',(side*1.6,5.6,0),(side*1.95,4.5,-.1),.4,'iron');rod('Gauntlet',(side*1.95,4.5,-.1),(side*2.1,3.7,-.3),.44,'orange')
 box('ShoulderMusicStaff',(side*1.55,6.1,-.7),(1.4,.5,.07),'dark')
 for k in [-1,0,1]:box('StaffLine',(side*1.55,6.1+k*.12,-.76),(1.35,.025,.03),'silver')
 cylinder('ShoulderNote',(side*1.2,5.9,-.85),.3,.08,'silver')
profile('VisoredHelm',[(0,6.25,0,.4,.4),(0,7.3,0,.66,.5),(0,7.7,0,.25,.32)],'orange')
panel('FaceMask',[(-.5,7.2),(0,6.45),(.5,7.2),(0,7.45)],-.55,.09,'dark')
for side in [-1,1]:rod('FlameEye',(side*.08,7.1,-.65),(side*.37,7.2,-.64),.06,'cyan')
cylinder('VoiceCore',(0,5.25,-.74),.58,.16,'silver');cylinder('VoiceCoreInset',(0,5.25,-.85),.46,.12,'teal');wave('VoiceWave',0,5.25,-.94,.73)
for x,y in [(0,8.3),(-1.9,7.7),(1.9,7.7)]:
 panel('AzureFlame',[(x-.3,y-.4),(x-.52,y+.1),(x-.12,y+.8),(x+.04,y+.3),(x+.32,y+.6),(x+.4,y-.1),(x+.2,y-.4)],0,.13,'blue')
rod('ForkGrip',(-2.1,3.8,-.3),(-2.8,2.6,-.7),.14,'gold')
for d in [-.28,.28]:rod('TuningForkTine',(-2.7+d,2.8,-.75),(-3.3+d,.75,-.9),.12,'orange')
rod('ForkBridge',(-2.95,2.7,-.75),(-2.4,2.7,-.75),.14,'edge')
rod('MicHandle',(2.1,3.7,-.3),(2.6,3.9,-.6),.13,'gold');ball('MicHead',(2.7,4,-.7),(.5,.5,.5),'amber')
for side in [-1,1]:
 rod('MaskSilverBrow',(side*.04,7.24,-.66),(side*.42,7.38,-.6),.06,'silver')
 rod('BreastplateRib',(side*.28,4.35,-.7),(side*.7,4.85,-.78),.075,'orange')
 rod('BreastplateRib',(side*.48,4.3,-.64),(side*.95,4.95,-.7),.06,'gold')
 cylinder('CuffBand',(side*2.1,3.8,-.28),.45,.13,'silver',(side*.3,1,.2))
 panel('FlameCore',[(side*1.9-.12,7.3),(side*1.9,8),(side*1.9+.18,7.3)],-.12,.03,'cyan')
panel('HelmFlameCore',[(-.14,7.95),(.05,8.85),(.23,7.95)],-.13,.03,'cyan')
save_group('ignis')
# SEAGULL SIREN CAPTAIN: stable leviathan save/encounter key; original concept-derived art.
# Broad coat mass, readable hooked bill, tricorn and paired open brass horns first.
profile('CaptainCoat',[(0,2.3,.12,1.5,.65),(0,4.1,0,1.05,.72),(0,6.2,0,1.55,.7)],'coat')
for s in [-1,1]:
 panel('CoatTail',[(s*.45,3.8),(s*1.55,4),(s*1.95,1.7),(s*.85,2.1)],.55,.1,'coat')
 rod('CoatPiping',(s*1.5,2.3,-.55),(s*1.05,4.1,-.73),.055,'gold')
 panel('CaptainLapel',[(s*.3,4.35),(s*1.42,6.3),(s*.95,6.45)],-.76,.1,'gold')
 panel('LapelInset',[(s*.49,4.85),(s*1.24,6.18),(s*.99,6.25)],-.79,.1,'coat')
 cylinder('CaptainEpaulette',(s*1.8,6.15,0),.67,.17,'gold',(0,1,0))
 rod('CaptainArm',(s*1.8,5.9,0),(s*2.1,3.65,-.2),.55,'coat')
 cylinder('CaptainCuff',(s*2.1,3.65,-.2),.61,.42,'gold',(0,1,0))
 for j in range(3):rod('CaptainFringe',(s*1.8+(j-1)*.3,6.1,-.48),(s*1.8+(j-1)*.3,5.68,-.48),.075,'edge')
 # Hollow 8-sided flare: bright lip, dark throat, cyan driver (not a filled cone).
 x=s*2.65;y=6.95
 cylinder('SirenBarrel',(x,y,.15),.44,.8,'gold')
 vs=[]
 for z,r in [(-.15,.43),(-1.35,.98)]:
  for k in range(8):a=k*math.tau/8;vs.append((x+r*math.cos(a),y+r*math.sin(a),z))
 mesh('SirenHorn',vs,[[k,(k+1)%8,(k+1)%8+8,k+8] for k in range(8)],'gold')
 ring('SirenLip',(x,y,-1.35),.98,'edge',.065,8)
 cylinder('SirenThroat',(x,y,-.3),.36,.035,'dark')
 cylinder('SirenDriver',(x,y,-.34),.2,.045,'cyan')
 rod('SirenSupport',(s*1.8,6.25,.05),(x,6.85,.2),.16,'gold')
 box('SirenSignal',(x,y+.47,.02),(.36,.055,.4),'cyan')
# Asymmetric grounded footwear: one boot, one peg with brass seabird toes.
box('CaptainBoot',(-.72,.32,-.23),(1.0,.64,1.35),'dark')
rod('CaptainLeg',(-.72,.67,0),(-.72,2.5,0),.36,'coat')
rod('CaptainPeg',(.72,.23,0),(.72,2.5,0),.19,'gold')
for dx in [-.23,0,.23]:rod('CaptainToe',(.72,.15,0),(.72+dx,.15,-.65),.12,'edge')
box('CaptainBelt',(0,3.7,-.79),(2.3,.43,.18),'leather')
box('CaptainBuckle',(0,3.7,-.93),(.6,.55,.12),'gold');box('BuckleInset',(0,3.7,-1.01),(.35,.3,.04),'leather')
# Continuous angular white head, pointed neck bib and yellow hooked bill.
chamfer_head('GullHead',0,7.15,-.02,.86,1.55,.64,'white')
panel('GullRuff',[(-.73,6.7),(-.75,6.14),(-.4,6.28),(-.25,5.88),(0,6.04),(.25,5.88),(.4,6.28),(.75,6.14),(.73,6.7)],-.77,.1,'white')
mesh('HookedBeak',[(-.55,7.18,-.7),(.55,7.18,-.7),(0,7.42,-.96),(0,7.05,-1.5),(0,6.73,-1.28),(-.45,6.95,-.7),(.45,6.95,-.7)],[[0,1,2],[0,2,3],[0,3,4],[0,4,5],[1,6,4],[1,4,3],[1,3,2],[5,4,6],[0,5,6,1]],'beak')
for s in [-1,1]:
 ball('GullEyeSocket',(s*.47,7.52,-.61),(.47,.3,.12),'dark')
 ball('GullEye',(s*.47,7.52,-.69),(.27,.17,.07),'cyan')
 rod('GullBrow',(s*.21,7.65,-.68),(s*.74,7.79,-.59),.1,'white')
# Broad sculpted tricorn with peaked front; distinct from crown/helmet bosses.
cylinder('HatBand',(0,7.97,0),.88,.22,'leather',(0,1,0))
profile('TricornCrown',[(0,7.97,.05,1.08,.68),(0,8.7,.1,.72,.55)],'coat')
hat=[(-1.64,7.95),(-1.4,8.34),(-.72,8.6),(0,9.23),(.72,8.6),(1.4,8.34),(1.64,7.95)]
panel('TricornFront',hat,-.67,.1,'coat')
for a,b in zip(hat,hat[1:]):rod('TricornGold',(a[0],a[1],-.7),(b[0],b[1],-.7),.055,'edge')
for x in [-.42,.42]:
 cylinder('GoggleRim',(x,8.19,-.77),.28,.12,'gold')
 cylinder('GoggleLens',(x,8.19,-.85),.2,.04,'cyan')
# Anchor chest and asymmetric tools, attached to complete arm groups.
rod('AnchorStem',(0,5.74,-.87),(0,4.95,-.87),.075,'silver')
rod('AnchorBar',(-.35,5.53,-.87),(.35,5.53,-.87),.07,'silver')
for s in [-1,1]:rod('AnchorFluke',(0,4.95,-.87),(s*.4,5.2,-.87),.075,'silver')
ball('CaptainHand',(-2.1,3.2,-.2),(.65,.6,.6),'white')
rod('CutlassGrip',(-2.1,3.15,-.35),(-1.83,2.84,-.68),.12,'leather')
rod('CutlassGuard',(-2.35,2.93,-.67),(-1.59,3.15,-.67),.09,'gold')
panel('CutlassBlade',[(-1.86,2.98),(-1.55,2.75),(-.4,1.35),(-.69,1.18),(-1.15,1.42),(-2.05,2.79)],-.76,.1,'silver')
rod('CutlassEdge',(-1.93,2.77,-.78),(-.69,1.26,-.78),.045,'cyan')
# Open hook curve, no replacement hand blob.
for i in range(7):
 a=math.radians(85+i*38);b=math.radians(85+(i+1)*38)
 rod('CaptainHook',(2.1+.42*math.cos(a),2.85+.42*math.sin(a),-.2),(2.1+.42*math.cos(b),2.85+.42*math.sin(b),-.2),.09,'silver')
# Sparse layered feather contours and hardware, subordinate to the main silhouette.
for side in [-1,1]:
 for j in range(2):
  x=side*(.5+j*.22)
  panel('CheekFeather',[(x-side*.17,6.95-j*.17),(x+side*.15,7.04-j*.17),(x+side*.1,6.57-j*.17)],-.67,.06,'white')
 for y in [4.4,4.8,5.2]:cylinder('CoatButton',(side*.32,y,-.78),.07,.07,'edge')
 panel('HatFeather',[(side*.83,8.47),(side*1.26,8.95),(side*1.92,9.12),(side*1.55,8.68),(side*1.17,8.39)],.32,.06,'teal' if side<0 else 'white')
save_group('leviathan')
# CONDUCTOR: slim long split coat silhouette, gold lapels/crown, six flared floating bells.
for side in [-1,1]:
 profile('Trouser',[(side*.43,.55,0,.28,.3),(side*.43,3.5,0,.31,.35)],'navy');box('Shoe',(side*.43,.25,-.2),(.65,.45,1),'navy')
profile('Waistcoat',[(0,3.3,0,.58,.4),(0,5.7,0,.8,.45),(0,6.25,0,.65,.4)],'purple')
for side in [-1,1]:
 panel('LongSplitCoat',[(side*.18,4.7),(side*.85,5.8),(side*1.3,2.4),(side*.65,1.4)],.2,.22,'purple')
 rod('CoatGoldEdge',(side*.65,1.4,.04),(side*1.3,2.4,.04),.05,'edge');rod('CoatGoldEdge',(side*1.3,2.4,.04),(side*.85,5.8,.04),.05,'edge')
 panel('Lapel',[(side*.1,4.8),(side*.9,6.25),(side*.4,5.9)],-.52,.07,'gold')
 rod('Sleeve',(side*.85,5.85,0),(side*1.7,4.5,-.1),.3,'purple');cylinder('Epaulette',(side*.9,5.95,0),.43,.14,'gold',(0,1,0));ball('Glove',(side*1.8,4.3,-.12),(.35,.65,.35),'ivory')
 for j in range(4):rod('EpauletteFringe',(side*.9+(j-1.5)*.15,5.95,-.37),(side*.9+(j-1.5)*.15,5.6,-.37),.04,'edge')
chamfer_head('CarvedFace',0,6.83,0,.41,1.03,.35,'skin')
rod('Mouth',(-.09,6.53,-.36),(.09,6.53,-.36),.018,'navy')
for side in [-1,1]:rod('Eye',(side*.07,6.94,-.37),(side*.27,7,-.37),.035,'blue')
panel('WhiteCravat',[(-.23,6.25),(.23,6.25),(0,5.4)],-.55,.08,'ivory')
for y in [4.35,4.75,5.1]:ball('Button',(0,y,-.48),(.1,.1,.07),'edge')
for side in [-1,1]:panel('CrownHorn',[(side*.1,7.25),(side*.45,7.3),(side*.7,7.8),(side*.48,8.3),(side*.4,7.8)],-.05,.18,'gold')
ball('CrownGem',(0,7.45,-.43),(.32,.45,.12),'blue')
for idx,(x,y) in enumerate([(-2.05,7.8),(2.05,7.8),(-2.65,6.35),(2.65,6.35),(-2.8,4.9),(2.8,4.9)]):
 # Rounded octagonal flare; open underside stays shadow-dark, no invisible back caps.
 vs=[]
 for yy,r in [(y-.43,.5),(y+.4,.23)]:
  for k in range(8):a=k*math.tau/8;vs.append((x+r*math.cos(a),yy,.3+r*math.sin(a)))
 fs=[[k,(k+1)%8,(k+1)%8+8,k+8] for k in range(8)]
 mesh('OrbitBell'+str(idx),vs,fs,'purple');cylinder('BellGoldLip',(x,y-.45,.3),.53,.09,'gold',(0,1,0));cylinder('BellDarkInterior',(x,y-.51,.3),.4,.04,'navy',(0,1,0));ball('Clapper',(x,y-.62,.3),(.18,.23,.18),'gold');ball('BellCrown',(x,y+.45,.3),(.4,.2,.35),'gold')
 rod('BellRune',(x-.13,y+.1,-.05),(x+.12,y-.15,-.05),.04,'edge')
for side in [-1,1]:
 rod('LapelPiping',(side*.1,4.8,-.58),(side*.9,6.25,-.58),.035,'edge')
 rod('FaceBrow',(side*.05,7.06,-.38),(side*.3,7.15,-.37),.045,'navy')
 cylinder('GloveCuff',(side*1.73,4.45,-.12),.22,.15,'edge',(side*.5,1,0))
 for k in range(3):rod('GloveFinger',(side*1.82+(k-1)*.075,4.18,-.15),(side*1.85+(k-1)*.075,3.96,-.18),.035,'ivory')
 rod('CoatEmbroideredSeam',(side*.4,3.7,.04),(side*.65,2.2,.04),.03,'gold')
save_group('conductor')
# Export immutable authored primitive + surface data. Exact same geometry goes to Roblox.
def lua(v):
 if isinstance(v,str):return json.dumps(v)
 if isinstance(v,bool):return str(v).lower()
 if isinstance(v,(int,float)):return str(round(v,5))
 if isinstance(v,dict):return '{'+','.join('['+lua(k)+']='+lua(x) for k,x in v.items())+'}'
 return '{'+','.join(lua(x) for x in v)+'}'
(ROOT/'src/ReplicatedStorage/Shared/BossVisualData.luau').write_text('-- Generated by Blender tools/bosses/fidelity.py. Original geometry, no asset IDs.\nreturn '+lua(all_data)+'\n')
report={}
for id,data in all_data.items():
 cost=sum(2*len(e['triangles']) if e['kind']=='Surface' else 1 for e in data)
 assert cost<=(435 if id=='leviathan' else 450),(id,cost)
 report[id]={'objects':len(data),'maximumNativeParts':cost,'continuousSurfaces':sum(e['kind']=='Surface' for e in data)}
(OUT/'manifest.json').write_text(json.dumps(report,indent=2))
# Render actual Blender authored geometry, front three-quarter and black silhouettes.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=False;scene.render.threads_mode='FIXED';scene.render.threads=3
scene.view_settings.look='AgX - Medium High Contrast'
scene.world=bpy.data.worlds.new('World');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.2,.25,1)
for p,power,size in [((0,-11,13),2000,9),((8,5,12),1800,8),((-8,0,8),1000,8)]:
 bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,4))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(11,-24,12));camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,4.3))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=11;scene.camera=camera
scene.render.resolution_x=700;scene.render.resolution_y=760;scene.render.resolution_percentage=100
import os
only=os.environ.get('BOSS_RENDER_ONLY')
for id,objects in groups.items():
 if only and id!=only:continue
 for group,oo in groups.items():
  for o in oo:o.hide_render=group!=id;o.hide_set(group!=id)
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(id+'.blend')))
 scene.render.filepath=str(OUT/(id+'.png'));bpy.ops.render.render(write_still=True)
 # Front silhouette: verify continuous mass and recognizable weapon/coil/coat outline.
 saved=camera.matrix_world.copy();camera.location=(0,-30,4.4);camera.rotation_euler=(Vector((0,0,4.4))-camera.location).to_track_quat('-Z','Y').to_euler()
 black=bpy.data.materials.get('Silhouette') or bpy.data.materials.new('Silhouette');black.diffuse_color=(0,0,0,1);black.use_nodes=True;black.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(0,0,0,1)
 scene.view_layers[0].material_override=black;scene.render.filepath=str(OUT/(id+'_silhouette.png'));bpy.ops.render.render(write_still=True);scene.view_layers[0].material_override=None;camera.matrix_world=saved
for oo in groups.values():
 for o in oo:o.hide_render=False;o.hide_set(False)
for i,(id,oo) in enumerate(groups.items()):
 for o in oo:o.location.x+=(i-2)*9
camera.location=(12,-45,15);camera.rotation_euler=(Vector((0,0,4))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=47
scene.render.resolution_x=1900;scene.render.resolution_y=600;scene.render.filepath=str(OUT/'lineup.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'BossFidelity.blend'));bpy.ops.render.render(write_still=True)
print('BOSS_FIDELITY',json.dumps(report))
