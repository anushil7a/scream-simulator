"""Build upload-free Coastal Academy slice landmarks in headless Blender 5.2.

Matches the 3 auto-generated architectural blueprints:
1. Academy Resonance Wayfinder Pylon (~8 studs tall)
2. Courtyard Sparring Acoustic Totem (~6.5 studs tall)
3. Coastal Promenade Acoustic Beacon (~9 studs tall)

Run via:
"C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" --background --factory-startup --disable-autoexec --python tools/slice_landmarks_blender.py
"""
import json
import math
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "build" / "blender_slice_landmarks"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def get_mat(name, rgba, metallic=0.0, roughness=0.65, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgba, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def add_box(collection, name, center, size, mat, rot_deg=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    obj.rotation_euler = tuple(math.radians(a) for a in rot_deg)
    obj.data.materials.append(mat)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def add_cyl(collection, name, center, radius, height, verts, mat, rot_deg=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=height, location=center)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = tuple(math.radians(a) for a in rot_deg)
    obj.data.materials.append(mat)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def add_cone(collection, name, center, r1, r2, height, verts, mat, rot_deg=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=height, location=center)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = tuple(math.radians(a) for a in rot_deg)
    obj.data.materials.append(mat)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def scene_stats(collection):
    tris = 0
    mins = [math.inf, math.inf, math.inf]
    maxs = [-math.inf, -math.inf, -math.inf]
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in collection.objects:
        if obj.type != "MESH":
            continue
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        mesh.calc_loop_triangles()
        tris += len(mesh.loop_triangles)
        for v in mesh.vertices:
            w = obj.matrix_world @ Vector(v.co)
            for i in range(3):
                mins[i] = min(mins[i], w[i])
                maxs[i] = max(maxs[i], w[i])
        eval_obj.to_mesh_clear()
    return {
        "objects": len(collection.objects),
        "triangles": tris,
        "min": [round(v, 4) for v in mins],
        "max": [round(v, 4) for v in maxs],
        "height": round(maxs[2] - mins[2], 4),
    }


def setup_preview_studio(target_z):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 675
    scene.render.image_settings.file_format = "PNG"
    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.12, 0.16, 0.20, 1.0)
        bg.inputs[1].default_value = 1.1

    bpy.ops.object.light_add(type="SUN", location=(10, -10, 16))
    sun = bpy.context.active_object
    sun.data.energy = 3.2
    sun.rotation_euler = (math.radians(48), math.radians(15), math.radians(38))

    bpy.ops.object.light_add(type="AREA", location=(-8, -6, 9))
    fill = bpy.context.active_object
    fill.data.energy = 120.0
    fill.data.size = 6.0

    bpy.ops.object.camera_add(location=(11.5, -11.5, target_z + 2.5))
    cam = bpy.context.active_object
    direction = Vector((0.0, 0.0, target_z)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    return cam


def build_pylon():
    reset_scene()
    col = bpy.data.collections.new("AcademyResonancePylon")
    bpy.context.scene.collection.children.link(col)
    sandstone = get_mat("Sandstone", (0.78, 0.65, 0.48), roughness=0.78)
    limestone = get_mat("Limestone", (0.87, 0.82, 0.71), roughness=0.68)
    bronze = get_mat("DarkBronze", (0.24, 0.19, 0.14), metallic=0.85, roughness=0.38)
    teal = get_mat("TealCeramic", (0.14, 0.44, 0.45), metallic=0.15, roughness=0.28)
    brass = get_mat("PolishedBrass", (0.78, 0.58, 0.24), metallic=0.92, roughness=0.25)
    amber = get_mat("AmberCore", (1.0, 0.74, 0.30), emission=(1.0, 0.72, 0.26), emission_strength=3.6)

    # Blueprint Z heights (Blender Z = up, 0 to 8.0 studs)
    add_cyl(col, "PlinthBase", (0, 0, 0.25), 1.45, 0.50, 8, sandstone)
    add_cyl(col, "PlinthMid", (0, 0, 0.70), 1.18, 0.40, 8, limestone)
    add_cyl(col, "PlinthTop", (0, 0, 1.075), 0.94, 0.35, 8, limestone)
    add_cyl(col, "ShaftCore", (0, 0, 2.75), 0.64, 3.00, 8, limestone)
    for i in range(4):
        ang = i * math.pi / 2 + math.pi / 4
        add_box(col, f"BronzeRib_{i}", (math.cos(ang) * 0.63, math.sin(ang) * 0.63, 2.75), (0.18, 0.18, 2.95), bronze, (0, 0, math.degrees(ang)))
    add_cyl(col, "TealCollar", (0, 0, 4.45), 0.80, 0.42, 8, teal)
    add_cyl(col, "UpperHead", (0, 0, 5.28), 0.70, 1.24, 8, limestone)
    add_cone(col, "BrassFin", (0, -0.78, 5.20), 0.22, 0.02, 1.10, 4, brass, (15, 0, 0))
    add_cyl(col, "LanternCore", (0, 0, 6.72), 0.38, 1.28, 12, amber)
    add_cyl(col, "CageBaseRing", (0, 0, 5.98), 0.66, 0.16, 8, bronze)
    add_cyl(col, "CageTopRing", (0, 0, 7.60), 0.50, 0.14, 8, bronze)
    add_cyl(col, "CageCap", (0, 0, 7.82), 0.32, 0.30, 8, bronze)
    for i in range(8):
        ang = i * math.pi / 4
        add_box(col, f"CageStrut_{i}", (math.cos(ang) * 0.56, math.sin(ang) * 0.56, 6.79), (0.10, 0.10, 1.62), bronze, (0, 0, math.degrees(ang)))

    stats = scene_stats(col)
    assert stats["triangles"] <= 2500 and stats["min"][2] >= -0.001
    glb = OUT_DIR / "academy_resonance_pylon.glb"
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB")
    setup_preview_studio(4.0)
    png = OUT_DIR / "academy_resonance_pylon_preview.png"
    bpy.context.scene.render.filepath = str(png)
    bpy.ops.render.render(write_still=True)
    return {"id": "AcademyResonancePylon", "glb": str(glb), "preview": str(png), **stats}


def build_totem():
    reset_scene()
    col = bpy.data.collections.new("CourtyardSparringTotem")
    bpy.context.scene.collection.children.link(col)
    slate = get_mat("SlateBase", (0.20, 0.25, 0.28), roughness=0.58)
    sand = get_mat("SandButtress", (0.76, 0.65, 0.48), roughness=0.72)
    steel = get_mat("StrutSteel", (0.58, 0.62, 0.65), metallic=0.65, roughness=0.35)
    bronze = get_mat("DishBronze", (0.48, 0.36, 0.22), metallic=0.82, roughness=0.35)
    amber = get_mat("TuningAmber", (1.0, 0.78, 0.34), emission=(1.0, 0.75, 0.30), emission_strength=3.2)
    teal = get_mat("TuningTeal", (0.20, 0.76, 0.72), emission=(0.18, 0.74, 0.70), emission_strength=2.2)

    # Pedestal (0 to 2.5 studs)
    add_box(col, "BaseSlab", (0, 0, 0.22), (2.20, 2.20, 0.44), slate)
    add_cone(col, "PedestalBody", (0, 0, 1.32), 1.25, 0.92, 1.80, 4, slate, (0, 0, 45))
    add_box(col, "PedestalCap", (0, 0, 2.34), (1.42, 1.42, 0.26), slate)
    for i in range(4):
        ang = i * math.pi / 2
        add_box(col, f"Buttress_{i}", (math.cos(ang) * 0.95, math.sin(ang) * 0.95, 0.75), (0.42, 0.46, 1.48), sand, (0, 0, math.degrees(ang)))
    add_cyl(col, "CollarRing", (0, 0, 2.60), 0.56, 0.24, 12, bronze)
    # Strut frame + tuning fork crystal (2.7 to 5.4 studs)
    for side in (-1, 1):
        add_box(col, f"StrutLow_{side}", (side * 0.55, 0, 3.20), (0.14, 0.16, 1.25), steel, (0, side * 32, 0))
        add_box(col, f"StrutMid_{side}", (side * 0.86, 0, 4.10), (0.14, 0.16, 1.15), steel)
        add_box(col, f"StrutTop_{side}", (side * 0.62, 0, 4.95), (0.14, 0.16, 0.95), steel, (0, -side * 28, 0))
    add_cyl(col, "CrystalStem", (0, 0, 3.30), 0.12, 0.85, 6, teal)
    add_box(col, "CrystalBridge", (0, 0, 3.76), (0.64, 0.18, 0.22), amber)
    for side in (-1, 1):
        add_box(col, f"TuningTine_{side}", (side * 0.24, 0, 4.42), (0.16, 0.18, 1.15), amber)
    # Angled acoustic dish (~5.5 to 6.5 studs)
    add_cone(col, "AcousticDish", (0, 0.08, 5.75), 0.35, 1.38, 0.78, 16, bronze, (28, 0, 0))
    add_cone(col, "ReceiverSpike", (0, -0.05, 5.95), 0.14, 0.03, 0.72, 8, steel, (28, 0, 0))

    stats = scene_stats(col)
    assert stats["triangles"] <= 2500 and stats["min"][2] >= -0.001
    glb = OUT_DIR / "courtyard_sparring_totem.glb"
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB")
    setup_preview_studio(3.3)
    png = OUT_DIR / "courtyard_sparring_totem_preview.png"
    bpy.context.scene.render.filepath = str(png)
    bpy.ops.render.render(write_still=True)
    return {"id": "CourtyardSparringTotem", "glb": str(glb), "preview": str(png), **stats}


def build_beacon():
    reset_scene()
    col = bpy.data.collections.new("CoastalHarborBeacon")
    bpy.context.scene.collection.children.link(col)
    sandstone = get_mat("CoastSandstone", (0.80, 0.69, 0.52), roughness=0.75)
    timber = get_mat("CoastTimber", (0.45, 0.30, 0.18), roughness=0.72)
    iron = get_mat("DarkIron", (0.18, 0.21, 0.24), metallic=0.80, roughness=0.40)
    copper = get_mat("TealCopper", (0.18, 0.56, 0.53), metallic=0.65, roughness=0.38)
    amber = get_mat("BeaconAmber", (1.0, 0.76, 0.32), emission=(1.0, 0.74, 0.28), emission_strength=4.0)

    add_cyl(col, "BaseStep", (0, 0, 0.25), 1.65, 0.50, 14, sandstone)
    add_cone(col, "FlaredColumn", (0, 0, 2.65), 1.48, 1.12, 4.30, 12, sandstone)
    for i in range(8):
        ang = i * math.tau / 8
        add_box(col, f"TimberFlute_{i}", (math.cos(ang) * 1.24, math.sin(ang) * 1.24, 2.65), (0.28, 0.24, 3.85), timber, (0, 0, math.degrees(ang)))
    add_cyl(col, "GalleryDeck", (0, 0, 4.96), 1.42, 0.34, 14, sandstone)
    add_cyl(col, "IronGalleryRing", (0, 0, 5.54), 1.44, 0.26, 16, iron)
    for i in range(12):
        ang = i * math.tau / 12
        add_box(col, f"GalleryPost_{i}", (math.cos(ang) * 1.38, math.sin(ang) * 1.38, 5.32), (0.10, 0.10, 0.58), iron)
    add_cyl(col, "BeaconLens", (0, 0, 6.45), 0.76, 1.68, 12, amber)
    for i in range(6):
        ang = i * math.tau / 6
        add_box(col, f"BafflePillar_{i}", (math.cos(ang) * 0.96, math.sin(ang) * 0.96, 6.45), (0.16, 0.18, 1.85), timber, (0, 0, math.degrees(ang)))
    add_cyl(col, "RoofEave", (0, 0, 7.45), 1.35, 0.22, 14, copper)
    add_cone(col, "CopperCap", (0, 0, 8.28), 1.38, 0.04, 1.44, 14, copper)

    stats = scene_stats(col)
    assert stats["triangles"] <= 2500 and stats["min"][2] >= -0.001
    glb = OUT_DIR / "coastal_harbor_beacon.glb"
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB")
    setup_preview_studio(4.5)
    png = OUT_DIR / "coastal_harbor_beacon_preview.png"
    bpy.context.scene.render.filepath = str(png)
    bpy.ops.render.render(write_still=True)
    return {"id": "CoastalHarborBeacon", "glb": str(glb), "preview": str(png), **stats}


def main():
    results = [build_pylon(), build_totem(), build_beacon()]
    manifest = OUT_DIR / "manifest.json"
    manifest.write_text(json.dumps({"landmarks": results}, indent=2), encoding="utf-8")
    print("Blender slice landmarks built:", json.dumps(results))


if __name__ == "__main__":
    main()
