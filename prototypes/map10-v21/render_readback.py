"""Blender lookback of exact Zone05 spec boxes/cylinders. Not a Studio screenshot."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Matrix, Vector

out = Path(sys.argv[sys.argv.index("--")+1]).resolve()
world = "--overworld" in sys.argv[sys.argv.index("--")+2:]
parts = json.loads((out/("overworld-geometry.json" if world else "geometry.json")).read_text())["parts"]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
zone = bpy.data.collections.new("Overworld from Lua" if world else "Zone 05 from Lua"); scene.collection.children.link(zone)
T=Matrix(((1,0,0),(0,0,-1),(0,1,0)))
mesh_library={}
def material(rgb, finish):
    m=bpy.data.materials.new(f"{finish} {rgb}");m.use_nodes=True
    m.diffuse_color=(*(v/255 for v in rgb),1)
    bs=m.node_tree.nodes.get("Principled BSDF")
    linear=lambda v: ((v/255+.055)/1.055)**2.4 if v>10 else v/3294.6
    bs.inputs["Base Color"].default_value=(*(linear(v) for v in rgb),1)
    bs.inputs["Roughness"].default_value=.37 if finish=="Metal" else .68
    if finish=="Metal": bs.inputs["Metallic"].default_value=.42
    if finish=="Neon":
        bs.inputs["Emission Color"].default_value=(*(linear(v) for v in rgb),1)
        bs.inputs["Emission Strength"].default_value=2.7
    return m
def add(p):
    key=tuple(p["color"]),p["shape"],p["material"]
    if key not in mesh_library:
        if p["shape"]=="Cylinder": bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.5,depth=1)
        elif p["shape"]=="Ball": bpy.ops.mesh.primitive_uv_sphere_add(radius=.5,segments=16,ring_count=8)
        elif p["shape"]=="Wedge":
            mesh=bpy.data.meshes.new("Wedge")
            mesh.from_pydata([(-.5,-.5,-.5),(.5,-.5,-.5),(.5,-.5,.5),(-.5,-.5,.5),(-.5,.5,-.5),(.5,.5,-.5)],
                             [],[(0,3,2,1),(0,1,5,4),(0,4,3),(1,2,5),(3,4,5,2)])
            mesh.materials.append(material(key[0],key[2]))
            mesh_library[key]=mesh
        else: bpy.ops.mesh.primitive_cube_add(size=1)
        if p["shape"]!="Wedge":
            temp=bpy.context.object; mesh=temp.data
            mesh.materials.append(material(key[0],key[2]))
            mesh_library[key]=mesh;bpy.data.objects.remove(temp,do_unlink=True)
    object=bpy.data.objects.new(p["id"],mesh_library[key]);zone.objects.link(object)
    if "GameplayMarker" in p.get("tags",[]): object.hide_render=True
    x,y,z=p["position"];object.location=(x,-z,y)
    a,b,c=map(math.radians,p["rotation"])
    rot=T@Matrix.Rotation(b,3,'Y')@Matrix.Rotation(a,3,'X')@Matrix.Rotation(c,3,'Z')
    u,v,w=p["size"]
    if p["shape"]=="Cylinder":
        rot=rot@Matrix.Rotation(math.pi/2,3,'Y');object.scale=(w,v,u)
    else: object.scale=(u,v,w)
    object.rotation_euler=rot.to_euler()
for p in parts: add(p)
if not world: add(dict(id="Ocean",position=[420,-2,-650],size=[4200,4,4200],rotation=[0,0,0],shape="Block",color=[42,172,185],material="Water"))
scene.world=bpy.data.worlds.new("Sea sky");scene.world.use_nodes=True
bg=scene.world.node_tree.nodes["Background"];bg.inputs[0].default_value=(.57,.76,.91,1);bg.inputs[1].default_value=.47
bpy.ops.object.light_add(type="SUN");sun=bpy.context.object
sun.rotation_euler=(.37,-.52,-.65);sun.data.energy=3.0;sun.data.angle=.15
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.clip_end=6000
scene.render.engine="CYCLES";scene.cycles.samples=20;scene.cycles.use_denoising=False
scene.render.threads_mode="FIXED";scene.render.threads=6
scene.render.resolution_x=1360;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.view_settings.view_transform="AgX"
renders = [
    ("Foundry-Aerial.png",(1080,230,670),(441,654,42),1130),
    ("Foundry-Causeway.png",(644,485,60),(783,645,106),None)
]
if world:
    renders=[
        ("Overworld-Aerial.png",(-2590,2930,2870),(15,-15,160),3600),
        ("Overworld-Academy.png",(-758,-690,69),(-934,-478,114),None),
        ("Overworld-Foundry.png",(980,410,330),(500,700,66),800),
    ]
    scene.render.resolution_x=1580;scene.render.resolution_y=1100
if "--academy-only" in sys.argv[sys.argv.index("--")+2:]:
    renders=[p for p in renders if p[0]=="Overworld-Academy.png"]
if "--aerial-only" in sys.argv[sys.argv.index("--")+2:]:
    renders=[p for p in renders if p[0]=="Overworld-Aerial.png"]
for file,loc,target,scale in renders:
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.data.type="ORTHO" if scale else "PERSP";cam.data.ortho_scale=scale or 1000;cam.data.lens=24
    scene.render.filepath=str(out/file);bpy.ops.render.render(write_still=True)
