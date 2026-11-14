"""Bounded headless Blender 5.2 look-dev proxy from actual Equipment.luau; proxy only, not native Roblox Studio parity."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/equipment-lookdev'
SOURCE = 'src/ServerScriptService/Equipment.luau'
BLENDER_EXE = Path(r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
DEFAULT_LUAU = Path(r'C:\Users\Sameer Pudasaini\AppData\Local\Programs\ScreamSimulatorTools\bin\luau.exe')
EXPECTED_PARTS = [
    'Grip',
    'Enclosure',
    'GoldTrim',
    'SpeakerGrille',
    'GrilleSlot',
    'GrilleSlot',
    'GrilleSlot',
    'GrilleSlot',
    'GrilleSlot',
    'StatusLight',
    'PommelCap',
    'GuardCollar',
    'AcousticCone',
    'TelemetrySpine',
]

LUAU_HARNESS_PRE = r'''
local V = {}
V.__index = V
local Vector3 = {
    new = function(x, y, z)
        return setmetatable({X = x, Y = y, Z = z}, V)
    end
}
V.__add = function(a, b)
    return Vector3.new(a.X + b.X, a.Y + b.Y, a.Z + b.Z)
end

local CF = {}
CF.__index = CF
local CFrame = {
    new = function(x, y, z)
        return setmetatable({Position = Vector3.new(x or 0, y or 0, z or 0)}, CF)
    end
}
CF.__mul = function(a, b)
    return CFrame.new(
        a.Position.X + b.Position.X,
        a.Position.Y + b.Position.Y,
        a.Position.Z + b.Position.Z
    )
end

local Color3 = {
    fromRGB = function(r, g, b)
        return {R = r / 255, G = g / 255, B = b / 255}
    end
}

local Enum = {
    Material = {SmoothPlastic = 'SmoothPlastic', Neon = 'Neon'},
    PartType = {Ball = 'Ball', Block = 'Block'},
}

local nodes = {}
local Instance = {
    new = function(className)
        local n = {
            ClassName = className,
            Shape = className == 'Part' and 'Block' or nil,
            Destroy = function() end,
        }
        table.insert(nodes, n)
        return n
    end
}

local Equipment = (function()
'''

LUAU_HARNESS_POST = r'''
end)()

local hand = {
    Name = 'RightHand',
    Size = Vector3.new(1, 1, 1),
    CFrame = CFrame.new(0, 0, 0),
}
local character = {
    FindFirstChild = function(_, name)
        if name == 'RightHand' then
            return hand
        end
        return nil
    end
}
local player = {Character = character}

Equipment.Sync(player, true)

for _, n in ipairs(nodes) do
    if n.ClassName == 'Part' then
        local p = n.CFrame.Position
        local s = n.Size
        local c = n.Color
        print(string.format(
            'GEOM|%s|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%s|%s',
            n.Name, p.X, p.Y, p.Z, s.X, s.Y, s.Z, c.R, c.G, c.B, n.Material, n.Shape
        ))
    end
end
'''


def _find_luau():
    found = shutil.which('luau')
    if found:
        return found
    if DEFAULT_LUAU.is_file():
        return str(DEFAULT_LUAU)
    raise FileNotFoundError('luau executable not found on PATH or at default tools path')


def export(out):
    source_path = ROOT / SOURCE
    source_bytes = source_path.read_bytes()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    source_text = source_bytes.decode('utf-8-sig')
    code = LUAU_HARNESS_PRE + source_text + LUAU_HARNESS_POST

    (ROOT / 'build').mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.luau', prefix='.equip_proxy_', dir=ROOT / 'build', encoding='utf-8', delete=False
    ) as f:
        f.write(code)
        temp = Path(f.name)
    try:
        result = subprocess.run(
            [_find_luau(), str(temp)],
            capture_output=True,
            text=True,
            timeout=20,
            check=True,
        )
    finally:
        temp.unlink(missing_ok=True)

    parts = []
    for line in result.stdout.splitlines():
        if line.startswith('GEOM|'):
            _, name, *rest = line.split('|')
            vals = list(map(float, rest[:9]))
            material, shape = rest[9], rest[10]
            parts.append({
                'name': name,
                'position': vals[:3],
                'size': vals[3:6],
                'color': vals[6:9],
                'material': material,
                'shape': shape,
            })

    assert len(parts) == 14, f'Expected 14 BaseParts, got {len(parts)}'
    assert [p['name'] for p in parts] == EXPECTED_PARTS, f'Unexpected part names: {[p["name"] for p in parts]}'
    assert all(p['shape'] in ('Block', 'Ball') for p in parts)
    assert all(0.0 <= c <= 1.0 for p in parts for c in p['color'])
    assert source_path.read_bytes() == source_bytes, 'Equipment.luau changed during export'

    out.mkdir(parents=True, exist_ok=True)
    (out / 'geometry.json').write_text(json.dumps(parts, indent=2), encoding='utf-8')
    return source_bytes, source_sha256, parts


def worker(out):
    import bpy
    import numpy as np
    from mathutils import Vector

    parts = json.loads((out / 'geometry.json').read_text(encoding='utf-8'))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 8
    scene.cycles.use_denoising = False
    scene.cycles.max_bounces = 4
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 4
    scene.render.resolution_x = 640
    scene.render.resolution_y = 480
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

    scene.world = bpy.data.worlds.new('LookDevWorld')
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes['Background']
    bg.inputs[0].default_value = (0.025, 0.032, 0.045, 1.0)
    bg.inputs[1].default_value = 0.85

    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'

    def xyz(v):
        return (v[0], -v[2], v[1])

    def dim(sz):
        return (sz[0], sz[2], sz[1])

    def srgb_to_linear(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    materials = {}
    gold_parts = {'GoldTrim', 'PommelCap', 'AcousticCone'}
    mins = [float('inf')] * 3
    maxs = [float('-inf')] * 3

    for p in parts:
        loc = xyz(p['position'])
        dims = dim(p['size'])
        for i in range(3):
            mins[i] = min(mins[i], loc[i] - dims[i] / 2)
            maxs[i] = max(maxs[i], loc[i] + dims[i] / 2)

        if p['shape'] == 'Ball':
            bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.5, location=loc)
        else:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        obj = bpy.context.object
        obj.name = p['name']
        obj.dimensions = dims

        is_gold = p['name'] in gold_parts
        key = (tuple(round(c, 6) for c in p['color']), p['material'], is_gold)
        if key not in materials:
            mat = bpy.data.materials.new(f'Mat_{p["name"]}')
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            nodes.clear()
            out_node = nodes.new('ShaderNodeOutputMaterial')
            lin = tuple(srgb_to_linear(c) for c in p['color'])
            if p['material'] == 'Neon':
                shader = nodes.new('ShaderNodeEmission')
                shader.inputs['Color'].default_value = (*lin, 1.0)
                shader.inputs['Strength'].default_value = 2.5
            else:
                shader = nodes.new('ShaderNodeBsdfPrincipled')
                shader.inputs['Base Color'].default_value = (*lin, 1.0)
                if is_gold:
                    shader.inputs['Metallic'].default_value = 0.78
                    shader.inputs['Roughness'].default_value = 0.32
                else:
                    shader.inputs['Metallic'].default_value = 0.0
                    shader.inputs['Roughness'].default_value = 0.55
            links.new(shader.outputs[0], out_node.inputs[0])
            materials[key] = mat
        obj.data.materials.append(materials[key])

    center = Vector(((mins[0] + maxs[0]) / 2, (mins[1] + maxs[1]) / 2, (mins[2] + maxs[2]) / 2))

    def aim_obj(obj, target):
        obj.rotation_euler = (target - obj.location).to_track_quat('-Z', 'Y').to_euler()

    bpy.ops.object.light_add(type='SUN', location=(center.x + 3.0, center.y + 4.0, center.z + 4.0))
    key_light = bpy.context.object
    key_light.name = 'KeySun'
    key_light.data.energy = 2.6
    aim_obj(key_light, center)

    bpy.ops.object.light_add(type='SUN', location=(center.x - 3.0, center.y + 3.0, center.z - 1.0))
    fill_light = bpy.context.object
    fill_light.name = 'FillSun'
    fill_light.data.energy = 1.0
    aim_obj(fill_light, center)

    bpy.ops.object.light_add(type='SUN', location=(center.x + 2.5, center.y - 3.5, center.z + 1.5))
    rim_light = bpy.context.object
    rim_light.name = 'RimSun'
    rim_light.data.energy = 1.8
    aim_obj(rim_light, center)

    bpy.ops.object.light_add(type='SUN', location=(center.x + 3.0, center.y - 1.5, center.z - 1.0))
    side_fill = bpy.context.object
    side_fill.name = 'SideFillSun'
    side_fill.data.energy = 1.2
    aim_obj(side_fill, center)

    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.name = 'LookDevCamera'
    cam.data.type = 'PERSP'
    cam.data.lens = 38.0
    cam.data.clip_start = 0.05
    cam.data.clip_end = 100.0
    scene.camera = cam

    views = [
        ('front', Vector((center.x, center.y + 2.35, center.z + 0.04))),
        ('three_quarter', Vector((center.x + 1.55, center.y + 1.75, center.z + 0.65))),
        ('profile', Vector((center.x + 2.35, center.y, center.z + 0.04))),
    ]

    cam.location = views[1][1]
    aim_obj(cam, center)
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'micro_speaker.blend'))

    for name, pos in views:
        cam.location = pos
        aim_obj(cam, center)
        scene.render.filepath = str(out / f'{name}.png')
        bpy.ops.render.render(write_still=True)

    strips = []
    for name, _ in views:
        img = bpy.data.images.load(str(out / f'{name}.png'))
        img.colorspace_settings.name = 'Non-Color'
        assert tuple(img.size) == (640, 480), f'Unexpected size for {name}: {tuple(img.size)}'
        arr = np.array(img.pixels[:], dtype=np.float32).reshape(480, 640, 4)
        strips.append(arr)

    combined = np.concatenate(strips, axis=1)
    sheet = bpy.data.images.new('Comparison', width=1920, height=480, alpha=True, is_data=True)
    sheet.pixels.foreach_set(combined.ravel())
    sheet.filepath_raw = str(out / 'comparison.png')
    sheet.file_format = 'PNG'
    sheet.save()
    print('EQUIPMENT_LOOKDEV_WORKER_COMPLETE parts=14 views=3')


def _validate_png(path, expected_dims, min_mtime_ns):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', f'Invalid PNG magic bytes: {path}'
    assert data[12:16] == b'IHDR', f'Missing IHDR chunk: {path}'
    dims = struct.unpack('>II', data[16:24])
    assert dims == expected_dims, f'{path.name} dimensions {dims} != {expected_dims}'
    assert path.stat().st_mtime_ns >= min_mtime_ns, f'Stale PNG output: {path}'
    return hashlib.sha256(data).hexdigest()


def main():
    out = OUT
    source_bytes, source_sha256, parts = export(out)
    assert BLENDER_EXE.is_file(), f'Blender executable not found: {BLENDER_EXE}'

    tool_path = Path(__file__).resolve()
    tool_bytes = tool_path.read_bytes()
    geom_path = out / 'geometry.json'
    geom_bytes = geom_path.read_bytes()

    started = time.time_ns()
    start_mono = time.monotonic()
    result = subprocess.run(
        [
            str(BLENDER_EXE),
            '--background',
            '--factory-startup',
            '--disable-autoexec',
            '--python',
            str(tool_path),
            '--' ,
            '--worker',
            str(out),
        ],
        capture_output=True,
        text=True,
        timeout=240,
        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
    )
    (out / 'render.log').write_text(result.stdout + result.stderr, encoding='utf-8')
    assert result.returncode == 0, f'Blender worker failed:\n{(result.stdout + result.stderr)[-2000:]}'

    assert (ROOT / SOURCE).read_bytes() == source_bytes, 'Equipment.luau changed during render'
    assert tool_path.read_bytes() == tool_bytes, 'equipment_lookdev.py changed during render'
    assert geom_path.read_bytes() == geom_bytes, 'geometry.json changed during render'

    min_mtime = started - 2_000_000_000
    blend_path = out / 'micro_speaker.blend'
    assert blend_path.is_file() and blend_path.stat().st_size > 1000, 'Missing or empty micro_speaker.blend'
    assert blend_path.stat().st_mtime_ns >= min_mtime, 'Stale micro_speaker.blend'

    expected_pngs = {
        'front.png': (640, 480),
        'three_quarter.png': (640, 480),
        'profile.png': (640, 480),
        'comparison.png': (1920, 480),
    }
    artifacts = {
        'geometry.json': hashlib.sha256(geom_bytes).hexdigest(),
        'micro_speaker.blend': hashlib.sha256(blend_path.read_bytes()).hexdigest(),
    }
    for name, dims in expected_pngs.items():
        artifacts[name] = _validate_png(out / name, dims, min_mtime)

    provenance = {
        'sources': {SOURCE: source_sha256},
        'toolSha256': hashlib.sha256(tool_bytes).hexdigest(),
        'sourceSnapshotVerifiedUnchanged': True,
        'parts': len(parts),
        'partNames': [p['name'] for p in parts],
        'export': 'Actual Equipment.Sync(player, true) on mocked RightHand (Size 1,1,1; CFrame 0,0,0) via luau',
        'blender': '5.2 installed signed executable',
        'elapsedSeconds': round(time.monotonic() - start_mono, 2),
        'render': {
            'engine': 'Cycles CPU',
            'samples': 8,
            'threads': 4,
            'resolution': [640, 480],
            'comparisonResolution': [1920, 480],
            'viewTransform': 'Standard',
            'timeoutSeconds': 240,
        },
        'artifacts': artifacts,
        'limits': 'proxy only, not native Roblox Studio parity; mocked RightHand transform without character rig, studio lighting, or gameplay runtime.',
        'nativeExecuted': False,
    }
    (out / 'provenance.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
    print(f'PASS equipment look-dev ({len(parts)} parts, 4 PNGs verified); proxy only, not native Roblox Studio parity')
    print((out / 'provenance.json').read_text(encoding='utf-8'))


if __name__ == '__main__':
    if '--worker' in sys.argv:
        worker(Path(sys.argv[sys.argv.index('--worker') + 1]))
    else:
        main()
