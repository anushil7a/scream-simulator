"""Bounded headless Blender 5.2 look-dev proxy from actual Fountain.luau and StreetArt.luau.
Proxy only, not native Roblox Studio parity.
"""
from pathlib import Path
import hashlib
import json
import math
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import zlib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/fountain-lookdev'
SOURCES = [
    'src/ServerScriptService/Fountain.luau',
    'src/ServerScriptService/StreetArt.luau',
]
BLENDER_EXE = Path(r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
DEFAULT_LUAU = Path(r'C:\Users\Sameer Pudasaini\AppData\Local\Programs\ScreamSimulatorTools\bin\luau.exe')

LUAU_HARNESS_PRE = r'''
local V3 = {}
V3.__index = V3
local Vector3 = {}
Vector3.new = function(x, y, z)
    return setmetatable({X = x or 0, Y = y or 0, Z = z or 0}, V3)
end
Vector3.zero = Vector3.new(0, 0, 0)
Vector3.yAxis = Vector3.new(0, 1, 0)
V3.__add = function(a, b)
    return Vector3.new(a.X + b.X, a.Y + b.Y, a.Z + b.Z)
end
V3.__sub = function(a, b)
    return Vector3.new(a.X - b.X, a.Y - b.Y, a.Z - b.Z)
end
V3.__unm = function(a)
    return Vector3.new(-a.X, -a.Y, -a.Z)
end
V3.__mul = function(a, b)
    if type(a) == 'number' then
        return Vector3.new(a * b.X, a * b.Y, a * b.Z)
    elseif type(b) == 'number' then
        return Vector3.new(a.X * b, a.Y * b, a.Z * b)
    end
    return Vector3.new(a.X * b.X, a.Y * b.Y, a.Z * b.Z)
end
function V3:Cross(b)
    return Vector3.new(
        self.Y * b.Z - self.Z * b.Y,
        self.Z * b.X - self.X * b.Z,
        self.X * b.Y - self.Y * b.X
    )
end
function V3:Dot(b)
    return self.X * b.X + self.Y * b.Y + self.Z * b.Z
end

local Vector2 = {
    new = function(x, y)
        return {X = x or 0, Y = y or 0}
    end
}

local UDim = {
    new = function(scale, offset)
        return {Scale = scale or 0, Offset = offset or 0}
    end
}

local UDim2 = {
    fromOffset = function(x, y)
        return {X = x or 0, Y = y or 0}
    end
}

local CF = {}
CF.__index = CF
local CFrame = {}

local function makeCF(pos, r00, r01, r02, r10, r11, r12, r20, r21, r22)
    return setmetatable({
        Position = pos,
        R = {r00, r01, r02, r10, r11, r12, r20, r21, r22},
        XVector = Vector3.new(r00, r10, r20),
        YVector = Vector3.new(r01, r11, r21),
        ZVector = Vector3.new(r02, r12, r22),
    }, CF)
end

CFrame.new = function(x, y, z)
    if type(x) == 'table' then
        return makeCF(Vector3.new(x.X, x.Y, x.Z), 1, 0, 0, 0, 1, 0, 0, 0, 1)
    end
    return makeCF(Vector3.new(x or 0, y or 0, z or 0), 1, 0, 0, 0, 1, 0, 0, 0, 1)
end

CFrame.Angles = function(rx, ry, rz)
    local cx, sx = math.cos(rx or 0), math.sin(rx or 0)
    local cy, sy = math.cos(ry or 0), math.sin(ry or 0)
    local cz, sz = math.cos(rz or 0), math.sin(rz or 0)
    -- Rx * Ry * Rz
    local r00 = cy * cz
    local r01 = -cy * sz
    local r02 = sy
    local r10 = cx * sz + sx * sy * cz
    local r11 = cx * cz - sx * sy * sz
    local r12 = -sx * cy
    local r20 = sx * sz - cx * sy * cz
    local r21 = sx * cz + cx * sy * sz
    local r22 = cx * cy
    return makeCF(Vector3.new(0, 0, 0), r00, r01, r02, r10, r11, r12, r20, r21, r22)
end

CFrame.fromMatrix = function(pos, vX, vY, vZ)
    local z = vZ or vX:Cross(vY)
    return makeCF(pos, vX.X, vY.X, z.X, vX.Y, vY.Y, z.Y, vX.Z, vY.Z, z.Z)
end

CF.__mul = function(a, b)
    local A = a.R
    if getmetatable(b) == V3 then
        local p = a.Position
        return Vector3.new(
            p.X + A[1] * b.X + A[2] * b.Y + A[3] * b.Z,
            p.Y + A[4] * b.X + A[5] * b.Y + A[6] * b.Z,
            p.Z + A[7] * b.X + A[8] * b.Y + A[9] * b.Z
        )
    end
    local B = b.R
    local pos = a * b.Position
    return makeCF(
        pos,
        A[1] * B[1] + A[2] * B[4] + A[3] * B[7],
        A[1] * B[2] + A[2] * B[5] + A[3] * B[8],
        A[1] * B[3] + A[2] * B[6] + A[3] * B[9],
        A[4] * B[1] + A[5] * B[4] + A[6] * B[7],
        A[4] * B[2] + A[5] * B[5] + A[6] * B[8],
        A[4] * B[3] + A[5] * B[6] + A[6] * B[9],
        A[7] * B[1] + A[8] * B[4] + A[9] * B[7],
        A[7] * B[2] + A[8] * B[5] + A[9] * B[8],
        A[7] * B[3] + A[8] * B[6] + A[9] * B[9]
    )
end

function CF:Inverse()
    local R = self.R
    local rt = makeCF(
        Vector3.zero,
        R[1], R[4], R[7],
        R[2], R[5], R[8],
        R[3], R[6], R[9]
    )
    local p = self.Position
    local invP = Vector3.new(
        -(R[1] * p.X + R[4] * p.Y + R[7] * p.Z),
        -(R[2] * p.X + R[5] * p.Y + R[8] * p.Z),
        -(R[3] * p.X + R[6] * p.Y + R[9] * p.Z)
    )
    return makeCF(invP, rt.R[1], rt.R[2], rt.R[3], rt.R[4], rt.R[5], rt.R[6], rt.R[7], rt.R[8], rt.R[9])
end

function CF:ToObjectSpace(other)
    return self:Inverse() * other
end

local Color3 = {
    new = function(r, g, b)
        return {R = r or 0, G = g or 0, B = b or 0}
    end,
    fromRGB = function(r, g, b)
        return {R = r / 255, G = g / 255, B = b / 255}
    end,
}

local ColorSequence = {
    new = function(c1, c2)
        return {colors = c2 and {c1, c2} or {c1}}
    end,
}

local NumberSequenceKeypoint = {
    new = function(t, v)
        return {Time = t, Value = v}
    end,
}

local NumberSequence = {
    new = function(arg)
        if type(arg) == 'table' then
            return {Keypoints = arg}
        end
        return {
            scalar = arg,
            Keypoints = {
                NumberSequenceKeypoint.new(0, arg),
                NumberSequenceKeypoint.new(1, arg),
            },
        }
    end,
}

local Enum = {
    ModelStreamingMode = {Atomic = 'Atomic'},
    PartType = {Block = 'Block', Cylinder = 'Cylinder', Ball = 'Ball'},
    Material = {
        Limestone = 'Limestone',
        CeramicTiles = 'CeramicTiles',
        Glass = 'Glass',
        SmoothPlastic = 'SmoothPlastic',
        Neon = 'Neon',
    },
    NormalId = {Front = 'Front'},
    SurfaceGuiSizingMode = {FixedSize = 'FixedSize'},
    ApplyStrokeMode = {Border = 'Border'},
    Font = {GothamBold = 'GothamBold'},
}

local task = {
    wait = function() end,
    spawn = function(fn, ...) fn(...) end,
    delay = function(_, fn, ...) fn(...) end,
}

local tags = {}
local CollectionService = {
    AddTag = function(_, obj, tag)
        tags[obj] = tags[obj] or {}
        tags[obj][tag] = true
    end,
}
local game = {
    GetService = function(_, name)
        if name == 'CollectionService' then
            return CollectionService
        end
        return {}
    end,
}

local InstMT = {}
local Instance = {}

local function attachMethods(obj)
    return setmetatable(obj, {
        __index = InstMT,
        __newindex = function(t, k, v)
            if k == 'Parent' then
                local old = rawget(t, '_parent')
                if old and old._children then
                    for i, c in ipairs(old._children) do
                        if c == t then
                            table.remove(old._children, i)
                            break
                        end
                    end
                end
                rawset(t, '_parent', v)
                if v and v._children then
                    table.insert(v._children, t)
                end
            else
                rawset(t, k, v)
            end
        end,
    })
end

function InstMT:IsA(kind)
    if self.ClassName == kind then return true end
    if kind == 'BasePart' and self.ClassName == 'Part' then return true end
    return false
end

function InstMT:FindFirstChild(name)
    for _, c in ipairs(self._children) do
        if c.Name == name then return c end
    end
    return nil
end

function InstMT:GetDescendants()
    local out = {}
    local function walk(node)
        for _, c in ipairs(node._children) do
            table.insert(out, c)
            walk(c)
        end
    end
    walk(self)
    return out
end

function InstMT:Clone()
    local copy = attachMethods({
        ClassName = self.ClassName,
        Name = self.Name,
        Shape = self.Shape,
        Size = self.Size,
        CFrame = self.CFrame,
        Color = self.Color,
        Material = self.Material,
        Transparency = self.Transparency,
        Reflectance = self.Reflectance,
        Anchored = self.Anchored,
        CanCollide = self.CanCollide,
        CanTouch = self.CanTouch,
        CanQuery = self.CanQuery,
        CastShadow = self.CastShadow,
        _pivot = self._pivot,
        _scale = self._scale,
        _children = {},
    })
    for _, c in ipairs(self._children) do
        local cc = c:Clone()
        cc.Parent = copy
    end
    return copy
end

function InstMT:Destroy()
    self._destroyed = true
    self.Parent = nil
end

function InstMT:ScaleTo(s)
    self._scale = s
end

function InstMT:GetBoundingBox()
    return CFrame.new(0, 0, 0), Vector3.new(1, 1, 1)
end

function InstMT:GetPivot()
    return self._pivot or CFrame.new(0, 0, 0)
end

function InstMT:PivotTo(cf)
    self._pivot = cf
end

Instance.new = function(className)
    return attachMethods({
        ClassName = className,
        Name = className,
        Shape = className == 'Part' and Enum.PartType.Block or nil,
        Size = className == 'Part' and Vector3.new(1, 1, 1) or nil,
        CFrame = CFrame.new(0, 0, 0),
        Color = Color3.new(1, 1, 1),
        Transparency = 0,
        _children = {},
    })
end

local RawFountain = (function()
'''

LUAU_HARNESS_MID = r'''
end)()

local RawStreetArt = (function()
'''

LUAU_HARNESS_POST = r'''
end)()

local Fountain = {}
function Fountain.create(parent, origin, template)
    if template == nil then
        template = Instance.new('Model')
        template.Name = 'FountainTemplate'
    end
    return RawFountain.create(template, parent, origin)
end

local StreetArt = {}
function StreetArt.create(parent, murals)
    local built = {}
    for _, spec in ipairs(murals) do
        local backing = Instance.new('Part')
        backing.Name = spec.name
        backing.Size = spec.size
        backing.CFrame = CFrame.new(spec.position)
        backing.Color = Color3.fromRGB(214, 200, 174)
        backing.Material = Enum.Material.Limestone
        backing.Anchored = true
        backing.Parent = parent

        local frontCf = CFrame.new(spec.position + Vector3.new(0, 0, spec.size.Z / 2 + 0.03))
        local wall = RawStreetArt.create(backing, frontCf, spec.size.X, spec.coastal)
        wall:SetAttribute('MuralName', spec.name)
        table.insert(built, wall)
    end
    return built
end

function InstMT:SetAttribute(k, v)
    self._attrs = self._attrs or {}
    self._attrs[k] = v
end

function InstMT:GetAttribute(k)
    return self._attrs and self._attrs[k] or nil
end

local workspace = Instance.new('Folder')
workspace.Name = 'Workspace'

local fountainModel = Fountain.create(workspace, Vector3.new(0, 0, 0), nil)
local muralWalls = StreetArt.create(workspace, {
    {name='WestMural', position=Vector3.new(-8.5, 6.2, -11.5), size=Vector3.new(12, 8.5, 0.5), coastal=false},
    {name='EastMural', position=Vector3.new(8.5, 6.2, -11.5), size=Vector3.new(12, 8.5, 0.5), coastal=true},
})

-- Structural assertions directly on live Luau module output.
assert(fountainModel and fountainModel.Name == 'MosaicFountain', 'Missing MosaicFountain')
assert(tags[fountainModel] and tags[fountainModel].OptionalLandmarkVisual, 'Missing OptionalLandmarkVisual tag')

local fallback = fountainModel:FindFirstChild('FallbackVisual')
assert(fallback ~= nil, 'Missing FallbackVisual')
local fallbackParts = {}
for _, c in ipairs(fallback._children) do
    if c.ClassName == 'Part' then
        table.insert(fallbackParts, c)
    end
end
assert(#fallbackParts == 28, 'Expected 28 FallbackVisual parts, got ' .. tostring(#fallbackParts))

local basinWater = fountainModel:FindFirstChild('BasinWater')
local bowlWater = fountainModel:FindFirstChild('BowlWater')
assert(basinWater and basinWater.ClassName == 'Part', 'Missing BasinWater')
assert(bowlWater and bowlWater.ClassName == 'Part', 'Missing BowlWater')

local collider = fountainModel:FindFirstChild('FountainCollision')
assert(collider ~= nil, 'Missing FountainCollision')

local streamCount, coreCount = 0, 0
for i = 0, 3 do
    local s = collider:FindFirstChild('WaterStream' .. i)
    local c = collider:FindFirstChild('WaterCore' .. i)
    assert(s and s.ClassName == 'Beam', 'Missing WaterStream' .. i)
    assert(c and c.ClassName == 'Beam', 'Missing WaterCore' .. i)
    streamCount += 1
    coreCount += 1
end
assert(streamCount == 4 and coreCount == 4, 'Wrong stream/core beam count')

assert(#muralWalls == 2, 'Expected 2 mural walls')
local surfaceGuiCount = 0
for _, wall in ipairs(muralWalls) do
    local gui = wall:FindFirstChild('OriginalStreetArt')
    assert(gui and gui.ClassName == 'SurfaceGui', 'Missing OriginalStreetArt')
    local paper = gui:FindFirstChild('Paper')
    assert(paper ~= nil, 'Missing Paper')
    local border = paper:FindFirstChild('MuralBorder')
    assert(border and border.ClassName == 'UIStroke', 'Missing MuralBorder')
    local accent = gui:FindFirstChild('MuralAccent')
    assert(accent ~= nil, 'Missing MuralAccent')
    surfaceGuiCount += 1
end
assert(surfaceGuiCount == 2, 'Expected 2 OriginalStreetArt murals')

local function emitPart(role, p)
    local pos = p.CFrame.Position
    local R = p.CFrame.R
    local s = p.Size
    local c = p.Color
    print(string.format(
        'PART|%s|%s|%s|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%s',
        role, p.Name, p.Shape,
        pos.X, pos.Y, pos.Z,
        s.X, s.Y, s.Z,
        c.R, c.G, c.B,
        p.Transparency or 0,
        R[1], R[2], R[3], R[4], R[5], R[6], R[7], R[8], R[9],
        tostring(p.Material or 'SmoothPlastic')
    ))
end

for _, p in ipairs(fallbackParts) do
    emitPart('FallbackVisual', p)
end
emitPart('Water', basinWater)
emitPart('Water', bowlWater)

for i = 0, 3 do
    local s = collider:FindFirstChild('WaterStream' .. i)
    local c = collider:FindFirstChild('WaterCore' .. i)
    local a0, a1 = s.Attachment0, s.Attachment1
    local p0, p1 = a0.WorldCFrame.Position, a1.WorldCFrame.Position
    local ax0, ax1 = a0.WorldCFrame.XVector, a1.WorldCFrame.XVector
    print(string.format(
        'BEAM|WaterStream|%d|StreamTop%d|StreamBottom%d|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%d',
        i, i, i,
        p0.X, p0.Y, p0.Z, p1.X, p1.Y, p1.Z,
        ax0.X, ax0.Y, ax0.Z, ax1.X, ax1.Y, ax1.Z,
        s.Width0, s.Width1, s.CurveSize0, s.CurveSize1, s.Segments
    ))
    print(string.format(
        'BEAM|WaterCore|%d|StreamTop%d|StreamBottom%d|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%d',
        i, i, i,
        p0.X, p0.Y, p0.Z, p1.X, p1.Y, p1.Z,
        ax0.X, ax0.Y, ax0.Z, ax1.X, ax1.Y, ax1.Z,
        c.Width0, c.Width1, c.CurveSize0, c.CurveSize1, c.Segments
    ))
end

for _, wall in ipairs(muralWalls) do
    local backing = wall._parent
    emitPart('MuralBacking', backing)
    emitPart('MuralWall', wall)
    local gui = wall:FindFirstChild('OriginalStreetArt')
    local mname = wall:GetAttribute('MuralName')
    local wp = wall.CFrame.Position
    local ws = wall.Size
    for _, child in ipairs(gui._children) do
        if child.ClassName == 'Frame' then
            local round = child:FindFirstChild('UICorner') ~= nil
            local bg = child.BackgroundColor3
            print(string.format(
                'GUI_FRAME|%s|%s|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%s',
                mname, child.Name,
                wp.X, wp.Y, wp.Z, ws.X, ws.Y, ws.Z,
                child.Position.X, child.Position.Y, child.Size.X, child.Size.Y,
                bg.R, bg.G, bg.B, child.Rotation or 0,
                round and '1' or '0'
            ))
            local stroke = child:FindFirstChild('MuralBorder')
            if stroke then
                local sc = stroke.Color
                print(string.format(
                    'GUI_STROKE|%s|%s|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g',
                    mname, stroke.Name,
                    wp.X, wp.Y, wp.Z, ws.X, ws.Y, ws.Z,
                    stroke.Thickness, stroke.Transparency,
                    sc.R, sc.G, sc.B,
                    child.Size.X, child.Size.Y
                ))
            end
        elseif child.ClassName == 'TextLabel' then
            local tc = child.TextColor3
            print(string.format(
                'GUI_TEXT|%s|%s|%s|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g|%.9g',
                mname, child.Name, child.Text,
                wp.X, wp.Y, wp.Z, ws.X, ws.Y, ws.Z,
                child.Position.X, child.Position.Y, child.Size.X, child.Size.Y,
                tc.R, tc.G, tc.B
            ))
        end
    end
end
print('LUAU_FOUNTAIN_EXPORT_OK')
'''


def _find_luau():
    found = shutil.which('luau')
    if found:
        return found
    if DEFAULT_LUAU.is_file():
        return str(DEFAULT_LUAU)
    raise FileNotFoundError('luau executable not found on PATH or at default tools path')


def export(out):
    source_bytes = {src: (ROOT / src).read_bytes() for src in SOURCES}
    source_hashes = {src: hashlib.sha256(b).hexdigest() for src, b in source_bytes.items()}
    fountain_src = source_bytes[SOURCES[0]].decode('utf-8-sig')
    art_src = source_bytes[SOURCES[1]].decode('utf-8-sig')
    code = LUAU_HARNESS_PRE + fountain_src + LUAU_HARNESS_MID + art_src + LUAU_HARNESS_POST

    (ROOT / 'build').mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.luau', prefix='.fountain_proxy_', dir=ROOT / 'build', encoding='utf-8', delete=False
    ) as f:
        f.write(code)
        temp = Path(f.name)
    try:
        result = subprocess.run(
            [_find_luau(), str(temp)],
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert result.returncode == 0, f'luau failed ({result.returncode}):\n{result.stdout}\n{result.stderr}'
    finally:
        temp.unlink(missing_ok=True)

    parts = []
    beams = []
    mural_elements = []

    for line in result.stdout.splitlines():
        if line.startswith('PART|'):
            _, role, name, shape, *rest = line.split('|')
            vals = list(map(float, rest[:-1]))
            material = rest[-1]
            parts.append({
                'role': role,
                'name': name,
                'shape': shape,
                'position': vals[0:3],
                'size': vals[3:6],
                'color': vals[6:9],
                'transparency': vals[9],
                'rotation': vals[10:19],
                'material': material,
            })
        elif line.startswith('BEAM|'):
            _, kind, idx, top_name, bot_name, *rest = line.split('|')
            vals = list(map(float, rest[:-1]))
            segments = int(rest[-1])
            color = [176 / 255, 232 / 255, 240 / 255] if kind == 'WaterStream' else [245 / 255, 253 / 255, 255 / 255]
            beams.append({
                'kind': kind,
                'name': f'{kind}{idx}',
                'index': int(idx),
                'streamTopName': top_name,
                'streamBottomName': bot_name,
                'streamTop': vals[0:3],
                'streamBottom': vals[3:6],
                'axis0': vals[6:9],
                'axis1': vals[9:12],
                'width0': vals[12],
                'width1': vals[13],
                'curveSize0': vals[14],
                'curveSize1': vals[15],
                'segments': segments,
                'color': color,
            })
        elif line.startswith('GUI_FRAME|'):
            _, mural, name, *rest = line.split('|')
            vals = list(map(float, rest[:-1]))
            is_round = rest[-1] == '1'
            mural_elements.append({
                'type': 'frame',
                'mural': mural,
                'name': name,
                'wallPos': vals[0:3],
                'wallSize': vals[3:6],
                'x': vals[6],
                'y': vals[7],
                'w': vals[8],
                'h': vals[9],
                'color': vals[10:13],
                'rotationDeg': vals[13],
                'round': is_round,
            })
        elif line.startswith('GUI_STROKE|'):
            _, mural, name, *rest = line.split('|')
            vals = list(map(float, rest))
            mural_elements.append({
                'type': 'stroke',
                'mural': mural,
                'name': name,
                'wallPos': vals[0:3],
                'wallSize': vals[3:6],
                'thickness': vals[6],
                'transparency': vals[7],
                'color': vals[8:11],
                'canvasW': vals[11],
                'canvasH': vals[12],
            })
        elif line.startswith('GUI_TEXT|'):
            _, mural, name, text, *rest = line.split('|')
            vals = list(map(float, rest))
            mural_elements.append({
                'type': 'text',
                'mural': mural,
                'name': name,
                'text': text,
                'wallPos': vals[0:3],
                'wallSize': vals[3:6],
                'x': vals[6],
                'y': vals[7],
                'w': vals[8],
                'h': vals[9],
                'color': vals[10:13],
            })

    fallback_parts = [p for p in parts if p['role'] == 'FallbackVisual']
    water_parts = [p for p in parts if p['role'] == 'Water']
    water_streams = [b for b in beams if b['kind'] == 'WaterStream']
    water_cores = [b for b in beams if b['kind'] == 'WaterCore']
    murals = sorted({e['mural'] for e in mural_elements})

    assert len(fallback_parts) == 28, f'Expected 28 FallbackVisual parts, got {len(fallback_parts)}'
    assert {p['name'] for p in water_parts} == {'BasinWater', 'BowlWater'}, f'Unexpected water parts: {water_parts}'
    assert [b['name'] for b in water_streams] == [f'WaterStream{i}' for i in range(4)]
    assert [b['name'] for b in water_cores] == [f'WaterCore{i}' for i in range(4)]
    assert murals == ['EastMural', 'WestMural'], f'Expected 2 murals, got {murals}'
    for m in murals:
        names = {e['name'] for e in mural_elements if e['mural'] == m}
        assert {'Paper', 'MuralBorder', 'MuralAccent'}.issubset(names), f'Missing required elements in {m}: {names}'

    for src in SOURCES:
        assert (ROOT / src).read_bytes() == source_bytes[src], f'{src} changed during export'

    data = {
        'counts': {
            'fallbackVisualParts': len(fallback_parts),
            'waterParts': len(water_parts),
            'waterStreams': len(water_streams),
            'waterCores': len(water_cores),
            'murals': len(murals),
            'muralElements': len(mural_elements),
        },
        'parts': parts,
        'beams': beams,
        'muralElements': mural_elements,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / 'geometry.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
    return source_bytes, source_hashes, data


def worker(out):
    import bpy
    from mathutils import Matrix, Vector

    geom = json.loads((out / 'geometry.json').read_text(encoding='utf-8'))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 8
    scene.cycles.use_denoising = False
    scene.cycles.max_bounces = 6
    scene.cycles.transparent_max_bounces = 12
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 4
    scene.render.resolution_x = 640
    scene.render.resolution_y = 480
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'

    scene.world = bpy.data.worlds.new('PlazaSky')
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes['Background']
    bg.inputs[0].default_value = (0.36, 0.56, 0.78, 1.0)
    bg.inputs[1].default_value = 0.75

    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'

    def xyz(v):
        return (v[0], -v[2], v[1])

    def srgb_to_linear(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    # M maps Roblox (x, y, z) -> Blender (x, -z, y)
    M = Matrix(((1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, 1.0, 0.0)))
    MT = M.transposed()

    def blender_rot(r_flat):
        Rr = Matrix((
            (r_flat[0], r_flat[1], r_flat[2]),
            (r_flat[3], r_flat[4], r_flat[5]),
            (r_flat[6], r_flat[7], r_flat[8]),
        ))
        return M @ Rr @ MT

    materials = {}

    def get_material(name_prefix, color, material_kind='SmoothPlastic', transparency=0.0, emission_strength=0.0):
        key = (
            tuple(round(c, 5) for c in color),
            material_kind,
            round(transparency, 4),
            round(emission_strength, 3),
        )
        if key in materials:
            return materials[key]
        mat = bpy.data.materials.new(f'Mat_{name_prefix}')
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        out_node = nodes.new('ShaderNodeOutputMaterial')
        lin = tuple(srgb_to_linear(c) for c in color)

        if emission_strength > 0.0 and transparency <= 0.001:
            shader = nodes.new('ShaderNodeEmission')
            shader.inputs['Color'].default_value = (*lin, 1.0)
            shader.inputs['Strength'].default_value = emission_strength
            links.new(shader.outputs[0], out_node.inputs[0])
        elif transparency > 0.001:
            mix = nodes.new('ShaderNodeMixShader')
            mix.inputs[0].default_value = 1.0 - transparency
            transp = nodes.new('ShaderNodeBsdfTransparent')
            if emission_strength > 0.0:
                shader = nodes.new('ShaderNodeEmission')
                shader.inputs['Color'].default_value = (*lin, 1.0)
                shader.inputs['Strength'].default_value = emission_strength
            else:
                shader = nodes.new('ShaderNodeBsdfPrincipled')
                shader.inputs['Base Color'].default_value = (*lin, 1.0)
                shader.inputs['Roughness'].default_value = 0.12 if material_kind == 'Glass' else 0.45
            links.new(transp.outputs[0], mix.inputs[1])
            links.new(shader.outputs[0], mix.inputs[2])
            links.new(mix.outputs[0], out_node.inputs[0])
        else:
            shader = nodes.new('ShaderNodeBsdfPrincipled')
            shader.inputs['Base Color'].default_value = (*lin, 1.0)
            if material_kind == 'Limestone':
                shader.inputs['Roughness'].default_value = 0.82
            elif material_kind == 'CeramicTiles':
                shader.inputs['Roughness'].default_value = 0.28
            else:
                shader.inputs['Roughness'].default_value = 0.55
            links.new(shader.outputs[0], out_node.inputs[0])

        materials[key] = mat
        return mat

    # Plaza ground plane beneath the fountain and murals.
    bpy.ops.mesh.primitive_plane_add(size=56.0, location=(0.0, 0.0, 0.0))
    plaza = bpy.context.object
    plaza.name = 'PlazaGround'
    plaza.data.materials.append(get_material('PlazaGround', (168 / 255, 160 / 255, 145 / 255), 'Limestone'))

    # 1. Fountain parts & mural walls from Luau export.
    for p in geom['parts']:
        loc = xyz(p['position'])
        sz = p['size']
        if p['shape'] == 'Cylinder':
            # Roblox Cylinder has circular axis along local X; Fountain.luau rotates it to world Y (Blender Z).
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=48,
                radius=sz[1] / 2.0,
                depth=sz[0],
                location=loc,
            )
            obj = bpy.context.object
        else:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
            obj = bpy.context.object
            obj.dimensions = (sz[0], sz[2], sz[1])
            obj.rotation_mode = 'QUATERNION'
            obj.rotation_quaternion = blender_rot(p['rotation']).to_quaternion()
        obj.name = f"{p['role']}_{p['name']}"
        obj.data.materials.append(get_material(p['name'], p['color'], p['material'], p['transparency']))

    # 2. Synthesize 3D cubic-Bezier arc cylinder segments for WaterStream0..3 and WaterCore0..3.
    def bezier_point(p0, p1, p2, p3, t):
        u = 1.0 - t
        return (u ** 3) * p0 + 3 * (u ** 2) * t * p1 + 3 * u * (t ** 2) * p2 + (t ** 3) * p3

    for beam in geom['beams']:
        p0 = Vector(beam['streamTop'])
        p3 = Vector(beam['streamBottom'])
        ax0 = Vector(beam['axis0'])
        ax1 = Vector(beam['axis1'])
        p1 = p0 + ax0 * beam['curveSize0']
        p2 = p3 - ax1 * beam['curveSize1']
        segs = beam['segments']
        is_core = beam['kind'] == 'WaterCore'
        mat = get_material(
            beam['kind'],
            beam['color'],
            'Neon',
            transparency=0.10 if is_core else 0.35,
            emission_strength=2.2 if is_core else 1.15,
        )
        for k in range(segs):
            t0 = k / segs
            t1 = (k + 1) / segs
            tm = 0.5 * (t0 + t1)
            a = Vector(xyz(bezier_point(p0, p1, p2, p3, t0)))
            b = Vector(xyz(bezier_point(p0, p1, p2, p3, t1)))
            delta = b - a
            width = (1.0 - tm) * beam['width0'] + tm * beam['width1']
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=12,
                radius=width * 0.5,
                depth=delta.length * 1.04,
                location=(a + b) * 0.5,
            )
            seg_obj = bpy.context.object
            seg_obj.name = f"{beam['name']}_seg{k}"
            seg_obj.rotation_mode = 'QUATERNION'
            seg_obj.rotation_quaternion = delta.to_track_quat('Z', 'Y')
            seg_obj.data.materials.append(mat)

    # 3. Synthesize 3D front-face relief planes on WestMural and EastMural.
    layer_z = {
        'Paper': 0.012,
        'Horizon': 0.024,
        'Garden': 0.024,
        'SeaLight': 0.036,
        'SeaShadow': 0.038,
        'Stem': 0.036,
        'Sail': 0.038,
        'Sun': 0.048,
        'Leaf': 0.048,
        'Petal': 0.052,
        'Sailcloth': 0.052,
        'MuralBorder': 0.056,
        'MuralAccent': 0.058,
        'FlowerCenter': 0.064,
    }
    canvas_w, canvas_h = 512.0, 160.0

    for idx, elem in enumerate(geom['muralElements']):
        wx, wy, wz = elem['wallPos']
        wall_w, wall_h, wall_d = elem['wallSize']
        front_roblox_z = wz + wall_d * 0.5
        etype = elem['type']

        if etype == 'frame':
            gx, gy, gw, gh = elem['x'], elem['y'], elem['w'], elem['h']
            cx_r = wx + ((gx + gw * 0.5) / canvas_w - 0.5) * wall_w
            cy_r = wy + (0.5 - (gy + gh * 0.5) / canvas_h) * wall_h
            pw = (gw / canvas_w) * wall_w
            ph = (gh / canvas_h) * wall_h
            offset = layer_z.get(elem['name'], 0.045) + (idx % 5) * 0.0005
            loc = xyz((cx_r, cy_r, front_roblox_z + offset))
            rot_rad = math.radians(-elem['rotationDeg'])

            if elem['round'] and abs(gw - gh) < 0.5:
                bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=pw * 0.5, depth=0.015, location=loc)
                obj = bpy.context.object
                obj.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
            else:
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
                obj = bpy.context.object
                obj.dimensions = (pw, 0.015, ph)
                if abs(rot_rad) > 1e-4:
                    obj.rotation_euler = (0.0, rot_rad, 0.0)
            obj.name = f"{elem['mural']}_{elem['name']}"
            obj.data.materials.append(get_material(elem['name'], elem['color'], 'SmoothPlastic'))

        elif etype == 'stroke':
            cw = (elem['canvasW'] / canvas_w) * wall_w
            ch = (elem['canvasH'] / canvas_h) * wall_h
            t_thick = max(0.08, (elem['thickness'] / canvas_h) * wall_h * 1.4)
            offset = layer_z['MuralBorder']
            strips = [
                ('Top', wx, wy + ch * 0.5 - t_thick * 0.5, cw, t_thick),
                ('Bottom', wx, wy - ch * 0.5 + t_thick * 0.5, cw, t_thick),
                ('Left', wx - cw * 0.5 + t_thick * 0.5, wy, t_thick, ch),
                ('Right', wx + cw * 0.5 - t_thick * 0.5, wy, t_thick, ch),
            ]
            mat = get_material('MuralBorder', elem['color'], 'SmoothPlastic', transparency=elem['transparency'])
            for side, sx, sy, sw, sh in strips:
                bpy.ops.mesh.primitive_cube_add(size=1.0, location=xyz((sx, sy, front_roblox_z + offset)))
                obj = bpy.context.object
                obj.name = f"{elem['mural']}_MuralBorder_{side}"
                obj.dimensions = (sw, 0.018, sh)
                obj.data.materials.append(mat)

        elif etype == 'text':
            gx, gy, gw, gh = elem['x'], elem['y'], elem['w'], elem['h']
            cx_r = wx + ((gx + gw * 0.5) / canvas_w - 0.5) * wall_w
            cy_r = wy + (0.5 - (gy + gh * 0.5) / canvas_h) * wall_h
            loc = xyz((cx_r, cy_r, front_roblox_z + 0.065))
            bpy.ops.object.text_add(location=loc)
            txt = bpy.context.object
            txt.name = f"{elem['mural']}_{elem['name']}"
            txt.data.body = elem['text']
            txt.data.align_x = 'CENTER'
            txt.data.align_y = 'CENTER'
            txt.data.size = 0.68
            txt.data.extrude = 0.015
            txt.rotation_euler = (math.pi / 2.0, 0.0, 0.0)
            txt.data.materials.append(get_material('MuralTitle', elem['color'], 'SmoothPlastic'))

    # 4. Three-point daylight rig.
    def aim_obj(obj, target):
        obj.rotation_euler = (target - obj.location).to_track_quat('-Z', 'Y').to_euler()

    bpy.ops.object.light_add(type='SUN', location=(16.0, -28.0, 32.0))
    key_sun = bpy.context.object
    key_sun.name = 'KeySun'
    key_sun.data.energy = 2.8
    aim_obj(key_sun, Vector((0.0, 0.0, 8.0)))

    bpy.ops.object.light_add(type='SUN', location=(-22.0, -18.0, 18.0))
    fill_sun = bpy.context.object
    fill_sun.name = 'FillSun'
    fill_sun.data.energy = 1.1
    aim_obj(fill_sun, Vector((0.0, 2.0, 7.0)))

    bpy.ops.object.light_add(type='SUN', location=(0.0, 24.0, 22.0))
    rim_sun = bpy.context.object
    rim_sun.name = 'RimSun'
    rim_sun.data.energy = 1.4
    aim_obj(rim_sun, Vector((0.0, 0.0, 8.0)))

    # 5. Camera + 3 look-dev views.
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.name = 'LookDevCamera'
    cam.data.type = 'PERSP'
    cam.data.clip_start = 0.1
    cam.data.clip_end = 250.0
    scene.camera = cam

    views = [
        ('overview', Vector((18.0, -35.0, 17.5)), Vector((0.0, 2.5, 8.2)), 28.0),
        ('stream_closeup', Vector((13.5, -17.5, 14.5)), Vector((6.2, 0.0, 10.8)), 30.0),
        ('mural_front', Vector((0.0, 2.35, 7.6)), Vector((0.0, 11.5, 6.2)), 11.2),
    ]

    # Save blend file framed at overview.
    cam.location = views[0][1]
    cam.data.lens = views[0][3]
    aim_obj(cam, views[0][2])
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'fountain_plaza.blend'))

    for name, pos, target, lens in views:
        cam.location = pos
        cam.data.lens = lens
        aim_obj(cam, target)
        scene.render.filepath = str(out / f'{name}.png')
        bpy.ops.render.render(write_still=True)

    print('FOUNTAIN_LOOKDEV_WORKER_COMPLETE views=3')


_FONT_5X7 = {
    'A': ('01110', '10001', '10001', '11111', '10001', '10001', '10001'),
    'B': ('11110', '10001', '10001', '11110', '10001', '10001', '11110'),
    'C': ('01110', '10001', '10000', '10000', '10000', '10001', '01110'),
    'D': ('11110', '10001', '10001', '10001', '10001', '10001', '11110'),
    'E': ('11111', '10000', '10000', '11110', '10000', '10000', '11111'),
    'F': ('11111', '10000', '10000', '11110', '10000', '10000', '10000'),
    'G': ('01110', '10001', '10000', '10111', '10001', '10001', '01110'),
    'H': ('10001', '10001', '10001', '11111', '10001', '10001', '10001'),
    'I': ('01110', '00100', '00100', '00100', '00100', '00100', '01110'),
    'J': ('00111', '00010', '00010', '00010', '10010', '10010', '01100'),
    'K': ('10001', '10010', '10100', '11000', '10100', '10010', '10001'),
    'L': ('10000', '10000', '10000', '10000', '10000', '10000', '11111'),
    'M': ('10001', '11011', '10101', '10101', '10001', '10001', '10001'),
    'N': ('10001', '11001', '10101', '10011', '10001', '10001', '10001'),
    'O': ('01110', '10001', '10001', '10001', '10001', '10001', '01110'),
    'P': ('11110', '10001', '10001', '11110', '10000', '10000', '10000'),
    'Q': ('01110', '10001', '10001', '10001', '10101', '10010', '01101'),
    'R': ('11110', '10001', '10001', '11110', '10100', '10010', '10001'),
    'S': ('01111', '10000', '10000', '01110', '00001', '00001', '11110'),
    'T': ('11111', '00100', '00100', '00100', '00100', '00100', '00100'),
    'U': ('10001', '10001', '10001', '10001', '10001', '10001', '01110'),
    'V': ('10001', '10001', '10001', '10001', '10001', '01010', '00100'),
    'W': ('10001', '10001', '10001', '10101', '10101', '11011', '10001'),
    'X': ('10001', '10001', '01010', '00100', '01010', '10001', '10001'),
    'Y': ('10001', '10001', '01010', '00100', '00100', '00100', '00100'),
    'Z': ('11111', '00001', '00010', '00100', '01000', '10000', '11111'),
    '0': ('01110', '10011', '10101', '10101', '11001', '10001', '01110'),
    '1': ('00100', '01100', '00100', '00100', '00100', '00100', '01110'),
    '2': ('01110', '10001', '00001', '00110', '01000', '10000', '11111'),
    '3': ('11110', '00001', '00001', '01110', '00001', '00001', '11110'),
    '4': ('00010', '00110', '01010', '10010', '11111', '00010', '00010'),
    '5': ('11111', '10000', '11110', '00001', '00001', '10001', '01110'),
    '6': ('01110', '10000', '11110', '10001', '10001', '10001', '01110'),
    '7': ('11111', '00001', '00010', '00100', '01000', '01000', '01000'),
    '8': ('01110', '10001', '10001', '01110', '10001', '10001', '01110'),
    '9': ('01110', '10001', '10001', '01111', '00001', '00001', '01110'),
    '-': ('00000', '00000', '00000', '11111', '00000', '00000', '00000'),
    '_': ('00000', '00000', '00000', '00000', '00000', '00000', '11111'),
    ' ': ('00000', '00000', '00000', '00000', '00000', '00000', '00000'),
}


def _read_png_rgb(path):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', f'Invalid PNG signature: {path}'
    pos = 8
    width = height = color_type = None
    idat = bytearray()
    while pos < len(data):
        length = struct.unpack('>I', data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        cdata = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if ctype == b'IHDR':
            width, height, bit_depth, color_type, compression, filt, interlace = struct.unpack('>IIBBBBB', cdata)
            assert bit_depth == 8 and compression == 0 and filt == 0 and interlace == 0
        elif ctype == b'IDAT':
            idat.extend(cdata)
        elif ctype == b'IEND':
            break
    assert width and height and color_type in (0, 2, 4, 6), f'Unsupported PNG format: {path}'
    bpp = {0: 1, 2: 3, 4: 2, 6: 4}[color_type]
    stride = width * bpp
    raw = zlib.decompress(bytes(idat))
    assert len(raw) == height * (stride + 1), f'Corrupt PNG scanlines: {path}'
    prev = bytearray(stride)
    rgb = bytearray(width * height * 3)
    out_idx = 0
    for row in range(height):
        row_start = row * (stride + 1)
        ftype = raw[row_start]
        cur = bytearray(raw[row_start + 1:row_start + 1 + stride])
        if ftype == 1:
            for i in range(bpp, stride):
                cur[i] = (cur[i] + cur[i - bpp]) & 0xFF
        elif ftype == 2:
            for i in range(stride):
                cur[i] = (cur[i] + prev[i]) & 0xFF
        elif ftype == 3:
            for i in range(stride):
                cur[i] = (cur[i] + (((cur[i - bpp] if i >= bpp else 0) + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:
            for i in range(stride):
                a = cur[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                cur[i] = (cur[i] + (a if pa <= pb and pa <= pc else (b if pb <= pc else c))) & 0xFF
        elif ftype != 0:
            raise AssertionError(f'Unsupported PNG filter {ftype}: {path}')
        prev = cur
        if color_type == 2:
            rgb[out_idx:out_idx + stride] = cur
            out_idx += stride
        elif color_type == 6:
            for x in range(0, stride, 4):
                rgb[out_idx:out_idx + 3] = cur[x:x + 3]
                out_idx += 3
        else:
            for x in range(0, stride, bpp):
                g = cur[x]
                rgb[out_idx:out_idx + 3] = bytes((g, g, g))
                out_idx += 3
    return width, height, bytes(rgb)


def _has_min_colors(rgb, minimum=10):
    seen = set()
    for i in range(0, len(rgb), 3):
        seen.add(rgb[i:i + 3])
        if len(seen) > minimum:
            return True
    return False


def _paste_rgb(canvas, cw, ch, src, sw, sh, dst_x, dst_y):
    row_bytes = sw * 3
    for y in range(sh):
        dy = dst_y + y
        if 0 <= dy < ch:
            off = (dy * cw + dst_x) * 3
            canvas[off:off + row_bytes] = src[y * row_bytes:(y + 1) * row_bytes]


def _draw_rect(canvas, cw, ch, x, y, w, h, color):
    r, g, b = color
    for py in range(max(0, y), min(ch, y + h)):
        for px in range(max(0, x), min(cw, x + w)):
            off = (py * cw + px) * 3
            canvas[off] = r
            canvas[off + 1] = g
            canvas[off + 2] = b


def _draw_text(canvas, cw, ch, x, y, text, color=(255, 255, 255), scale=2):
    r, g, b = color
    cx = x
    for ch_in in text.upper():
        glyph = _FONT_5X7.get(ch_in, _FONT_5X7[' '])
        for gy, row_bits in enumerate(glyph):
            for gx, bit in enumerate(row_bits):
                if bit == '1':
                    for sy in range(scale):
                        py = y + gy * scale + sy
                        if 0 <= py < ch:
                            for sx in range(scale):
                                px = cx + gx * scale + sx
                                if 0 <= px < cw:
                                    off = (py * cw + px) * 3
                                    canvas[off] = r
                                    canvas[off + 1] = g
                                    canvas[off + 2] = b
        cx += 6 * scale


def _png_chunk(tag, data):
    return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)


def _write_png_rgb(path, width, height, rgb):
    stride = width * 3
    raw = b''.join(b'\x00' + bytes(rgb[y * stride:(y + 1) * stride]) for y in range(height))
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    path.write_bytes(
        b'\x89PNG\r\n\x1a\n'
        + _png_chunk(b'IHDR', ihdr)
        + _png_chunk(b'IDAT', zlib.compress(raw, 6))
        + _png_chunk(b'IEND', b'')
    )


def _validate_png_header(path, expected_dims, min_mtime_ns):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', f'Invalid PNG magic bytes: {path}'
    assert data[12:16] == b'IHDR', f'Missing IHDR chunk: {path}'
    dims = struct.unpack('>II', data[16:24])
    assert dims == expected_dims, f'{path.name} dimensions {dims} != {expected_dims}'
    assert path.stat().st_mtime_ns >= min_mtime_ns, f'Stale PNG output: {path}'
    return hashlib.sha256(data).hexdigest()


def main():
    out = OUT
    source_bytes, source_hashes, geom = export(out)
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
            '--',
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

    for src in SOURCES:
        assert (ROOT / src).read_bytes() == source_bytes[src], f'{src} changed during render'
    assert tool_path.read_bytes() == tool_bytes, 'fountain_lookdev.py changed during render'
    assert geom_path.read_bytes() == geom_bytes, 'geometry.json changed during render'

    min_mtime = started - 2_000_000_000
    blend_path = out / 'fountain_plaza.blend'
    assert blend_path.is_file() and blend_path.stat().st_size > 1000, 'Missing or empty fountain_plaza.blend'
    assert blend_path.stat().st_mtime_ns >= min_mtime, 'Stale fountain_plaza.blend'

    view_names = ['overview', 'stream_closeup', 'mural_front']
    sheet_w, sheet_h = 1920, 480
    canvas = bytearray(bytes((10, 16, 28)) * (sheet_w * sheet_h))
    artifacts = {
        'geometry.json': hashlib.sha256(geom_bytes).hexdigest(),
        'fountain_plaza.blend': hashlib.sha256(blend_path.read_bytes()).hexdigest(),
    }

    for col, name in enumerate(view_names):
        img_path = out / f'{name}.png'
        artifacts[img_path.name] = _validate_png_header(img_path, (640, 480), min_mtime)
        w, h, rgb = _read_png_rgb(img_path)
        assert (w, h) == (640, 480) and _has_min_colors(rgb, 10), f'Blank or invalid render: {img_path}'
        _paste_rgb(canvas, sheet_w, sheet_h, rgb, w, h, col * 640, 0)
        badge_w = len(name) * 12 + 16
        _draw_rect(canvas, sheet_w, sheet_h, col * 640 + 8, 8, badge_w, 22, (10, 16, 28))
        _draw_text(canvas, sheet_w, sheet_h, col * 640 + 16, 12, name, (255, 255, 255), 2)

    comparison_path = out / 'comparison.png'
    _write_png_rgb(comparison_path, sheet_w, sheet_h, canvas)
    artifacts['comparison.png'] = _validate_png_header(comparison_path, (1920, 480), min_mtime)

    provenance = {
        'sources': source_hashes,
        'toolSha256': hashlib.sha256(tool_bytes).hexdigest(),
        'sourceSnapshotVerifiedUnchanged': True,
        'counts': geom['counts'],
        'export': 'Actual Fountain.create and StreetArt.create via mocked Luau harness',
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
        'limits': 'proxy only, not native Roblox Studio parity; mocked Luau instances, synthesized parabolic beam cylinders and 3D mural reliefs.',
        'nativeExecuted': False,
    }
    (out / 'provenance.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
    print(f"PASS fountain look-dev ({geom['counts']['fallbackVisualParts']} FallbackVisual parts, 4 streams, 2 murals, 4 PNGs verified)")
    print((out / 'provenance.json').read_text(encoding='utf-8'))


if __name__ == '__main__':
    if '--worker' in sys.argv:
        worker(Path(sys.argv[sys.argv.index('--worker') + 1]))
    else:
        main()
