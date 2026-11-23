"""Build the original GEAR-01 authoring model in a disposable Blender process."""
import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


OUT = Path(__file__).resolve().parents[1] / "build" / "academy-megaphone"
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name, rgb, metallic, roughness):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    shader = next(node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
    shader.inputs["Base Color"].default_value = mat.diffuse_color
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return mat


cream = material("Warm enamel", (.86, .77, .58), .1, .35)
brass = material("Brushed brass", (.72, .43, .12), .7, .29)
leather = material("Saddle leather", (.23, .084, .028), 0, .64)
stitch = material("Warm stitching", (.64, .38, .17), 0, .69)
dark = material("Inner driver", (.105, .065, .033), .25, .5)


def turned_shell(name, profile, mat):
    sides = 20
    vertices = [
        (radius * math.cos(i * math.tau / sides), y, .38 + radius * math.sin(i * math.tau / sides))
        for y, radius in profile for i in range(sides)
    ]
    faces = [
        (j * sides + i, j * sides + (i + 1) % sides,
         ((j + 1) % len(profile)) * sides + (i + 1) % sides,
         ((j + 1) % len(profile)) * sides + i)
        for j in range(len(profile)) for i in range(sides)
    ]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(mat)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return obj


def rounded_block(name, center, size, bevel, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    modifier = obj.modifiers.new("Rounded corners", "BEVEL")
    modifier.width = bevel
    modifier.segments = 2
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.data.materials.append(mat)
    return obj


# The handle is at the origin. The horn fires along -Y, and Z is up.
turned_shell("Enamel horn", [(-.19,.15),(-.28,.195),(-.48,.21),(-.61,.253),
    (-.77,.34),(-.95,.45),(-1.015,.474),(-1.015,.423),(-.95,.405),(-.77,.297),
    (-.61,.212),(-.48,.172),(-.27,.112),(-.19,.105)], cream)
turned_shell("Rolled bell rim", [(-.966,.46),(-.99,.486),(-1.021,.49),
    (-1.039,.47),(-1.039,.436),(-1.018,.426),(-.995,.431),(-.966,.445)], brass)
turned_shell("Rear collar", [(-.16,.137),(-.18,.178),(-.255,.184),
    (-.276,.172),(-.276,.127),(-.17,.095)], brass)
turned_shell("Driver sleeve", [(-.49,.105),(-.53,.093),(-.71,.068),(-.75,.06),
    (-.752,.032),(-.67,.032),(-.53,.051),(-.49,.072)], dark)
rounded_block("Leather handle", (0,0,-.01), (.22,.235,.57), .035, leather)
rounded_block("Handle bracket", (0,-.153,.243), (.17,.38,.18), .025, brass)
rounded_block("Handle cap", (0,0,-.302), (.239,.252,.08), .025, brass)
for i in range(5):
    rounded_block(f"Stitch {i + 1}", (.112,.059,-.18+i*.086), (.014,.052,.014), .005, stitch)

meshes = list(bpy.context.scene.objects)
stats = {}
for obj in meshes:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    assert all(edge.is_manifold for edge in bm.edges), obj.name
    bm.free()
    obj.data.calc_loop_triangles()
    stats[obj.name] = len(obj.data.loop_triangles)
total = sum(stats.values())
assert total <= 2400, total

scene = bpy.context.scene
target = Vector((0,-.5,.08))
bpy.ops.object.camera_add(location=(2.2,-3.3,1.54))
camera = bpy.context.object
camera.rotation_euler = (target - camera.location).to_track_quat("-Z","Y").to_euler()
camera.data.type = "ORTHO"
camera.data.ortho_scale = 1.86
scene.camera = camera
for name, location, energy, size in [
    ("Key",(1.1,-2.1,2.8),150,2.1), ("Rim",(-1.8,.2,1.9),125,1.5),
    ("Fill",(1.2,1.0,.3),45,1.7),
]:
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.name = name
    light.rotation_euler = (target - light.location).to_track_quat("-Z","Y").to_euler()
    light.data.energy = energy
    light.data.shape = "DISK"
    light.data.size = size

scene.world = bpy.data.worlds.new("Slate backdrop")
scene.world.use_nodes = True
background = next(node for node in scene.world.node_tree.nodes if node.type == "BACKGROUND")
background.inputs["Color"].default_value = (.057,.10,.11,1)
background.inputs["Strength"].default_value = .42
scene.render.engine = "CYCLES"
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
scene.render.filepath = "//preview.png"

bpy.ops.object.select_all(action="DESELECT")
for obj in meshes:
    obj.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "AcademyMegaphone.blend"))

# Keep the editable pieces in the master, but export one mesh per material.
bpy.ops.object.select_all(action="DESELECT")
export_objects = []
for mat in (cream, brass, leather, stitch, dark):
    copies = []
    for source in meshes:
        if source.data.materials[0] != mat:
            continue
        obj = source.copy()
        obj.data = source.data.copy()
        bpy.context.collection.objects.link(obj)
        obj.select_set(True)
        copies.append(obj)
    first = copies[0]
    bpy.context.view_layer.objects.active = first
    if len(copies) > 1:
        bpy.ops.object.join()
    first.name = mat.name
    first.select_set(False)
    export_objects.append(first)
for obj in export_objects:
    obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT / "AcademyMegaphone.glb"), use_selection=True)
bpy.ops.export_scene.fbx(filepath=str(OUT / "AcademyMegaphone.fbx"), use_selection=True,
                         object_types={"MESH"}, axis_forward="-Z", axis_up="Y")
for obj in export_objects:
    bpy.data.objects.remove(obj, do_unlink=True)
(OUT / "mesh-counts.json").write_text(json.dumps({
    "triangles": total, "exportMeshes": len(export_objects), "sourceObjects": stats,
}, indent=2)+"\n")
bpy.ops.render.render(write_still=True)
