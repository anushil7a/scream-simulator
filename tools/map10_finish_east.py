"""Original Map10 eastern finish; append-only cosmetic geometry, no gameplay edits.

Reference: actual MAP-10_Master_Overworld_Blueprint.jpg pixels, MAP10_REVIEW.md
vault make-map/style/level-flow guidance. Preserve the readable two bridges,
crater boss disk and east approach to the tethered shrine. The caller owns
noncollision for every emitted prop. No external meshes, scripts or textures.
"""
import math


def add(box, disk, line):
    basalt = [48, 43, 54]
    slate = [72, 61, 73]
    ash = [101, 81, 88]
    iron = [53, 58, 67]
    copper = [164, 106, 66]
    obsidian = [59, 46, 77]
    violet = [123, 84, 153]
    pale = [187, 151, 204]
    # Layered branching rivulets: dark scorched shoulders, rusty melt and only a
    # narrow incandescent center. Flat, nonphysical art never becomes damage.
    channels = [
        ((330, -210), (320, -165), 8),
        ((320, -165), (315, -115), 7),
        ((315, -115), (308, -74), 7),
        ((308, -74), (310, -40), 8),
        ((310, -40), (280, 5), 7),
        ((310, -40), (335, 0), 6),
        ((335, 0), (355, 75), 8),
        ((355, 75), (415, 90), 9),
        ((415, 90), (405, 5), 7),
        ((405, 5), (393, -75), 8),
        ((393, -75), (420, -135), 7),
        ((420, -135), (395, -185), 7),
        ((320, -165), (269, -125), 4),
        ((308, -74), (274, -60), 4),
        ((335, 0), (369, 18), 4),
        ((405, 5), (449, -12), 4),
        ((420, -135), (456, -158), 4),
        ((395, -185), (365, -215), 4),
    ]
    for i, (a, b, width) in enumerate(channels):
        # This source deliberately skirts the full existing radius32 boss pad.
        for layer, extra, y, color, mat in [
            ('Shoulder', 5, 32.48, [60, 40, 45], 'Slate'),
            ('Melt', 0, 32.58, [184, 62, 22], 'SmoothPlastic'),
            ('Heart', -width * .66, 32.68, [247, 141, 45], 'Neon'),
        ]:
            line(f'EastLava{i}{layer}', [a[0], y, a[1]],
                 [b[0], y, b[1]], width + extra, .10, color, material=mat)

    # Broken crater lip frames the reserved boss pad without entering its
    # radius32 floor. Dark matte plates, not a second neon combat boundary.
    for i in range(10):
        a = i * math.tau / 10
        x, z = 350 + math.cos(a) * 39, -80 + math.sin(a) * 39
        box(f'EastCraterLip{i}', [x, 32.8, z], [6, 1.3, 15],
            [83, 65, 69] if i % 3 else [106, 80, 72],
            rot=[0, -math.degrees(a), (i % 3 - 1) * 5], material='Slate')

    # Uneven slanted outer crags with mineral seams. Keep all footprint mass
    # outside boss/pedestrian corridors; asymmetry reads as a geological rim.
    crags = [(244, -223, 24, -17), (272, -245, 36, 12),
             (333, -249, 42, -11), (386, -244, 30, 16),
             (485, -196, 39, -13), (489, -122, 46, 18),
             (490, -36, 33, -16), (475, 60, 36, 12),
             (433, 116, 26, -20), (361, 117, 29, 11),
             (290, 114, 22, -15)]
    for i, (x, z, height, lean) in enumerate(crags):
        turn = (i * 37 + 21) % 180
        box(f'EastRimShard{i}', [x, 43 + height * .30, z],
            [15, height, 18], basalt, rot=[lean, turn, lean * .35], material='Slate')
        box(f'EastRimFacet{i}', [x + 6, 43 + height * .24, z + 5],
            [8, height * .8, 13], slate, rot=[-lean * .5, turn + 24, lean], material='Slate')
        box(f'EastMineralSeam{i}', [x - 5, 43 + height * .46, z - 5],
            [2, height * .43, 3], ash, rot=[lean, turn, lean * .35], material='Rock')

    # Bridge edge engineering, not obstacles: continuous iron side stringers,
    # warm cap rails, spaced riveted uprights and underslung diagonal braces.
    # Endpoints and clear widths exactly track the existing two walking ramps.
    bridges = [([90, 32, -190], [300, 32, -180], 28),
               ([170, 16, 40], [300, 32, 40], 30)]
    for bi, (a, b, width) in enumerate(bridges):
        dx, dz = b[0] - a[0], b[2] - a[2]
        distance = math.hypot(dx, dz)
        nx, nz = -dz / distance, dx / distance
        def at(t, side, dy):
            return [a[0] + dx * t + nx * side * (width / 2 + 2.8),
                    a[1] + (b[1] - a[1]) * t + dy,
                    a[2] + dz * t + nz * side * (width / 2 + 2.8)]
        for side in (-1, 1):
            prefix = f'EastBridge{bi}Side{side}'
            line(prefix + 'Stringer', at(0, side, -1.5), at(1, side, -1.5),
                 2.6, 4, iron, material='Metal')
            line(prefix + 'CapRail', at(0, side, 6.8), at(1, side, 6.8),
                 1.1, 1.2, copper, material='Metal')
            for j in range(5):
                t = j / 4
                box(prefix + f'Post{j}', at(t, side, 3.5), [1.8, 7, 1.8], iron, material='Metal')
                box(prefix + f'Rivet{j}', at(t, side, 6.2), [2.1, .7, 2.1], copper, material='Metal')
            for j in range(4):
                line(prefix + f'Truss{j}', at(j / 4, side, -3), at((j + 1) / 4, side, -8),
                     1.4, 1.7, iron, material='Metal')

    # Crafted shrine portal with an OPEN center, not a glowing block that hides
    # the destination. Layered piers and a crown frame north of the playable pad.
    for side in (-1, 1):
        x = 350 + side * 15
        box(f'EastPortalFoot{side}', [x, 76, -458], [12, 3, 12], obsidian)
        box(f'EastPortalPillar{side}', [x, 89, -458], [7, 24, 8], violet,
            rot=[0, 0, -side * 4], material='Slate')
        box(f'EastPortalFlute{side}', [x - side * 2.8, 89, -453.7], [1, 19, .7], pale)
        box(f'EastPortalCapital{side}', [x, 102, -458], [10, 3, 11], pale)
        line(f'EastPortalCrown{side}', [x, 103, -458], [350, 113, -458],
             5, 5, obsidian, material='Slate')
        line(f'EastPortalCrownTrim{side}', [x, 103.7, -454.8], [350, 113.7, -454.8],
             .8, .9, copper, material='Metal')
    # Small static etched thresholds, no particles or whole-panel neon bloom.
    for i in range(5):
        box(f'EastPortalRune{i}', [342 + i * 4, 75.55, -455], [1.2, .15, 3.5],
            [171, 133, 193], rot=[0, 30 if i % 2 else -30, 0])

    # Tapered mineral clusters: stacked faceted slabs, not cylindrical neon bars.
    # Heights vary and long-axis lean gives the mass a fractured, grown silhouette.
    crystals = [(350, -480, 30, 13, -9), (317, -458, 19, 8, 14),
                (389, -453, 24, 9, -15), (327, -478, 13, 6, -18)]
    for i, (x, z, height, width, lean) in enumerate(crystals):
        base = 70 if i == 0 else 73
        for k in range(5):
            t = k / 4
            taper = 1 - .83 * t
            cx = x + math.sin(math.radians(lean)) * height * t
            box(f'EastCrystal{i}Facet{k}', [cx, base + height * (k + .5) / 5, z],
                [width * taper, height / 5 + .25, width * taper],
                [[113, 76, 150], [143, 105, 175], [171, 133, 198]][(k + i) % 3],
                rot=[0, 45 + i * 17, -lean])
        # A narrow reflective edge suggests energy without a luminous solid mass.
        line(f'EastCrystal{i}Inclusion', [x, base + 2, z - width * .45],
             [x + math.sin(math.radians(lean)) * height * .7, base + height * .75, z - width * .15],
             .7, .6, [180, 150, 214], material='Neon')

    # Reinforced tether anchors visually explain the suspended island's weight.
    for i, (x, y, z) in enumerate([(302, 62, -420), (390, 62, -370),
                                  (205, 51, -400), (400, 58, -225)]):
        box(f'EastTetherAnchor{i}', [x, y, z], [9, 7, 11], iron, rot=[0, 22, 0], material='Metal')
        box(f'EastTetherClamp{i}', [x, y + 3.8, z], [11, 1.6, 13], copper, rot=[0, 22, 0], material='Metal')
    # Suspended undercroft teeth break the coarse square stepped base silhouette.
    for i in range(8):
        a = i * math.tau / 8
        box(f'EastShrineUndercroft{i}', [350 + math.cos(a) * 35, 43 - i % 3 * 3, -420 + math.sin(a) * 35],
            [10, 23 + i % 3 * 4, 13], obsidian if i % 2 else violet,
            rot=[12 * math.sin(a), math.degrees(a), 16 * math.cos(a)], material='Slate')
