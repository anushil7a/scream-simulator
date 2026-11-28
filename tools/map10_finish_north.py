"""Original Map10 north/mid finishing overlays.

Reference: personally reviewed approved MAP-10_Master_Overworld_Blueprint.jpg.
Vault guidance: simulator palette/readability, open paths, sightlines/landmarks and
non-obstructing dressing. All callbacks MUST create noncolliding, nonqueryable
cosmetics. No live state, geometry edits, external files, textures or dependencies.
"""
import math


def add(box, disk, line):
    ivory = [240, 225, 191]
    limestone = [205, 190, 154]
    brass = [187, 137, 62]
    deep_teal = [35, 91, 94]
    slate = [44, 67, 72]
    leaf = [67, 115, 76]
    leaf_light = [103, 150, 85]
    violet = [113, 62, 154]
    plum = [47, 31, 67]
    cyan = [74, 188, 194]

    def b(name, pos, size, color, rot=None, material='SmoothPlastic', shape=None):
        box('North' + name, pos, size, color, rot=rot, material=material, shape=shape)

    def d(name, x, y, z, r, h, color, material='SmoothPlastic'):
        disk('North' + name, x, y, z, r, h, color, material=material)

    def rail(name, a, c, width, height, color, material='SmoothPlastic'):
        line('North' + name, a, c, width, height, color, material=material)

    # Architecture: each existing pavilion gets actual joinery, not a new box shell.
    # Capitals sit directly on existing columns; friezes remain above head height.
    for i, (x, z, width) in enumerate([
        (-450, -460, 44), (-300, -460, 58), (-140, -460, 44), (-490, -180, 36)
    ]):
        for j, (dx, dz) in enumerate([(a, c) for a in (-.36, .36) for c in (-.36, .36)]):
            cx, cz = x + dx * width, z + dz * width
            b(f'Pavilion{i}Base{j}', [cx, 33.1, cz], [5.2, 1.4, 5.2], limestone, material='Marble')
            b(f'Pavilion{i}Capital{j}', [cx, 57.15, cz], [5.8, 1.7, 5.8], ivory, material='Marble')
            b(f'Pavilion{i}Flute{j}', [cx, 46, cz - 1.54], [.5, 17, .10], limestone)
        for side in (-1, 1):
            b(f'Pavilion{i}FriezeZ{side}', [x, 57, z + side * width * .40], [width * .88, 2, 1.4], ivory)
            b(f'Pavilion{i}FriezeX{side}', [x + side * width * .40, 57, z], [1.4, 2, width * .88], ivory)
        ridge_y = 66 + math.sin(math.radians(22)) * width * .295
        b(f'Pavilion{i}Ridge', [x, ridge_y + .45, z], [2.0, 1.1, width + 12], deep_teal)
        # An acoustic crest suspended on the existing front frieze.
        b(f'Pavilion{i}Crest', [x, 56.9, z + width * .40 + .85], [5, 3.2, .22], deep_teal)
        b(f'Pavilion{i}CrestInlay', [x, 56.9, z + width * .40 + 1], [.7, 2.5, .10], brass)

    # Fountain: a crafted, low silhouette centrepiece, framed by a radial mosaic.
    # Outer radius22 remains comfortably clear of spawn at(-300,-260).
    for i in range(12):
        a, c = i * math.tau / 12, (i + 1) * math.tau / 12
        rail(f'FountainRim{i}', [-300 + math.sin(a)*20, 34.5, -300 + math.cos(a)*20],
             [-300 + math.sin(c)*20, 34.5, -300 + math.cos(c)*20], 2.8, 1.1, ivory, 'Marble')
        t = (a + c) / 2
        b(f'MosaicDiamond{i}', [-300 + math.sin(t)*28, 32.17, -300 + math.cos(t)*28],
          [3.2, .12, 3.2], deep_teal if i % 2 else brass, rot=[0, math.degrees(t)+45, 0])
    d('FountainUpperWater', -300, 41.08, -300, 7.7, .12, [65, 166, 178])
    d('FountainPedestalCollar', -300, 38.8, -300, 4.1, .6, brass, 'Metal')
    b('FountainCrown', [-300, 43, -300], [3.8, 4.1, 3.8], [111, 204, 212], shape='Ball')
    for i in range(4):
        a = i * math.pi / 2
        rail(f'FountainPavingSpoke{i}', [-300 + math.sin(a)*32, 32.19, -300 + math.cos(a)*32],
             [-300 + math.sin(a)*37, 32.19, -300 + math.cos(a)*37], .7, .10, brass)

    # The first route passes inside the west court, clear of the planter and boss.
    route = [(-320, -268), (-360, -294), (-399, -332), (-420, -368), (-420, -384)]
    for index, ((ax, az), (bx, bz)) in enumerate(zip(route, route[1:])):
        length = math.hypot(bx - ax, bz - az)
        dx, dz = (bx - ax) / length, (bz - az) / length
        lx, lz = -dz, dx

        def point(along, across, y):
            return [ax + along * dx + across * lx, y, az + along * dz + across * lz]

        # Clear the angled stone and edge at the turn into the pad.
        start = 2 if index == len(route) - 2 else 1
        end = length - 1
        rail(f'RookiePathStone{index}', point(start, 0, 32.26),
             point(end, 0, 32.26), 9, .05, [211, 200, 171])
        for side in (-1, 1):
            rail(f'RookiePathEdge{index}_{side}', point(start, side * 4, 32.30),
                 point(end, side * 4, 32.30), .50, .03, deep_teal)
            rail(f'RookiePathArrow{index}_{side}', point(length / 2 - 1.3, side * 1.8, 32.32),
                 point(length / 2 + 1.3, 0, 32.32), .48, .035, brass)

    # Slate inlays on the far edge stay visible when the approach billboard is behind the camera.
    # Offset them from the approach centerline so the avatar does not hide the names.
    for tier, x, accent in (
        ('Rookie', -420, (111, 196, 180)),
        ('Brawler', -300, (219, 120, 94)),
        ('Elite', -180, (240, 192, 89)),
    ):
        name = f'TrainingInlay{tier}'
        label_x = x + 10.5
        # Top SurfaceGui reads along local Z. South approach needs -90° yaw.
        b(name, [label_x, 32.28, -420.8], [5.4, .04, 18], slate, rot=[0, -90, 0], material='Slate')
        for side in (-1, 1):
            b(f'{name}Trim{side}', [label_x + side * 9.23, 32.28, -420.8],
              [.38, .04, 5.4], accent, material='SmoothPlastic')

    # Asymmetric courtyard planting, deliberately outside paths, trainers and boss ring.
    for i, (x, z, scale) in enumerate([(-500,-235,1),(-135,-350,.85),(-365,-330,.8),(-235,-330,.8)]):
        soil_y, soil_depth = 34.05, .2
        soil_top = soil_y + soil_depth/2
        b(f'CourtPlanter{i}', [x, 33, z], [13, 2, 13], limestone, material='Marble')
        b(f'CourtSoil{i}', [x, soil_y, z], [11.3, soil_depth, 11.3], [98, 82, 60])
        for lobe, dx, dz, dimensions, color in (
            ('A', -1.55, -.55, (8.8, 7.6, 8.3), leaf),
            ('B', 1.9, 1.35, (7.2, 6.6, 6.8), leaf_light),
        ):
            size = [dimension*scale for dimension in dimensions]
            center_y = soil_top + size[1]/2 - .48
            b(f'CourtShrub{i}{lobe}', [x+dx, center_y, z+dz], size, color, shape='Ball')
        b(f'CourtPlanterInlay{i}', [x, 33.4, z+6.55], [9, .35, .10], brass)

    # Market: canopies retain their original silhouette, now with canvas stripes,
    # stone counters and grouped provisions visible from the approach.
    for i, (x, z) in enumerate([(-100,150),(-40,150),(20,150),(-150,-20)]):
        for j in range(5):
            b(f'Cafe{i}CanvasStripe{j}', [x-10+j*5, 34.65, z], [2.5, .20, 18.1], ivory)
        b(f'Cafe{i}Counter', [x, 24.20, z], [23, .40, 11], limestone, material='Marble')
        for j, dx in enumerate((-5.5, 3)):
            b(f'Cafe{i}Tray{j}', [x+dx, 24.65, z], [5.5, .5, 5.5], [136, 89, 54], material='Wood')
        for j, (dx, dz) in enumerate([(-6,-1),(-4,1),(3,0)]):
            b(f'Cafe{i}Produce{j}', [x+dx, 25.8, z+dz], [2.1, 1.9, 2.1],
              [224, 145, 60] if j<2 else [163, 76, 68], shape='Ball')
        b(f'Cafe{i}MenuFrame', [x+9.3, 26.3, z-4], [3.6, 4.0, .5], deep_teal)

    # Garden islands: partial stone edging and distinct shrub/flower masses.
    # They occupy existing circular planted beds, not the walking ribbons.
    for i, (x, z) in enumerate([(-25,-20),(35,30),(-10,70),(140,-30)]):
        for j in range(4):
            a, c = (j+.08)*math.pi/2, (j+.8)*math.pi/2
            rail(f'Garden{i}Edging{j}', [x+math.sin(a)*21,16.8,z+math.cos(a)*21],
                 [x+math.sin(c)*21,16.8,z+math.cos(c)*21],1.2,1.2,ivory)
        for j, (dx,dz) in enumerate([(-13,-8),(12,8),(-9,13)]):
            b(f'Garden{i}Shrub{j}', [x+dx,19,z+dz], [10,4.8,8], leaf if j%2 else leaf_light,shape='Ball')
        for j, (dx,dz) in enumerate([(-12,-9),(13,9)]):
            b(f'Garden{i}Flowers{j}', [x+dx,21.4,z+dz], [4.5,.7,3.2], [211,141,168] if i%2 else [233,191,102],shape='Ball')

    # Amphitheatre: front-facing speaker drivers, chassis hardware, façade panels.
    # Cylinder longitudinal axis is X; Y90 makes fronts point along Z.
    for i, (x,z) in enumerate([(-30,-410),(90,-470),(210,-410)]):
        b(f'Audio{i}Face', [x,64,z+9.12], [25.3,60,.16], plum)
        for j,h in enumerate((46,70,86)):
            for k,(radius,depth,color) in enumerate([(8.5,.3,brass),(7.2,.4,[29,26,39]),(3.1,.5,violet)]):
                b(f'Audio{i}Driver{j}_{k}',[x,h,z+9.4+k*.25],[depth,radius*2,radius*2],color,
                  rot=[0,90,0],material='Metal' if k==0 else 'SmoothPlastic',shape='Cylinder')
        for side in (-1,1):
            b(f'Audio{i}Corner{side}',[x+side*12.7,64,z+9.4],[.8,60,.5],violet)
    for i in (1, 2, 3, 4, 5, 7):
        a = i * math.pi/4
        x,z=90+math.sin(a)*126,-330+math.cos(a)*126
        b(f'MusicFacade{i}',[x,38,z],[64,10,1.0],plum,rot=[0,math.degrees(a),0])
        b(f'MusicFacadeInlay{i}',[x,41,z+.02],[48,.75,1.2],violet,rot=[0,math.degrees(a),0])
    for i in range(12):
        a,c=i*math.tau/12,(i+1)*math.tau/12
        rail(f'StageMedallion{i}',[90+math.sin(a)*30,32.83,-330+math.cos(a)*30],
             [90+math.sin(c)*30,32.83,-330+math.cos(c)*30],1,.12,brass)

    # First-upgrade slice architectural landmarks (matched to Blender 5.2 blueprints).
    # Pylon frames the Spawn -> Rookie Courtyard approach; Totem marks Rookie Pad.
    px, pz = -320, -276
    b('PylonPlinth', [px, 32.45, pz], [3.2, .7, 3.2], [200, 168, 122], material='Sandstone')
    b('PylonStep', [px, 33.05, pz], [2.4, .5, 2.4], ivory, material='Limestone')
    d('PylonShaft', px, 35.1, pz, .75, 3.8, ivory, material='Limestone')
    b('PylonRibA', [px, 35.1, pz], [1.72, 3.3, .24], [61, 48, 36], material='Metal')
    b('PylonRibB', [px, 35.1, pz], [.24, 3.3, 1.72], [61, 48, 36], material='Metal')
    d('PylonCollar', px, 37.2, pz, .95, .48, deep_teal, material='SmoothPlastic')
    b('PylonFin', [px - .9, 37.9, pz - .3], [.32, 1.25, 1.1], brass, rot=[0, 35, 0], material='Metal', shape='Wedge')
    d('PylonCore', px, 38.45, pz, .48, 1.4, [255, 198, 92], material='Neon')
    d('PylonCap', px, 39.45, pz, .86, .48, [61, 48, 36], material='Metal')

    tx, tz = -454, -378
    b('TotemBase', [tx, 32.53, tz], [2.4, .55, 2.4], slate, material='Slate')
    b('TotemPedestal', [tx, 33.7, tz], [1.75, 1.8, 1.75], slate, material='Slate')
    b('TotemButtressX', [tx, 33.25, tz], [2.25, 1.1, .48], [194, 166, 122], material='Sandstone')
    b('TotemButtressZ', [tx, 33.25, tz], [.48, 1.1, 2.25], [194, 166, 122], material='Sandstone')
    d('TotemCollar', tx, 34.75, tz, .68, .3, brass, material='Metal')
    for side in (-1, 1):
        b(f'TotemStrut{side}', [tx + side * .62, 36.1, tz], [.2, 2.4, .2], [148, 158, 166], material='Metal')
    b('TotemCrystal', [tx, 36.1, tz], [.68, 1.5, .26], [255, 199, 98], material='Neon')
    b('TotemDish', [tx, 37.65, tz - .2], [.55, 2.5, 2.5], [122, 92, 56], rot=[0, 125, 25], material='Metal', shape='Cylinder')
