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
        b(f'Pavilion{i}Entablature', [x, 59.6, z + width * .50 + 2], [width + 6, .7, 1], brass)
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

    # Asymmetric courtyard planting, deliberately outside paths, trainers and boss ring.
    for i, (x, z, scale) in enumerate([(-500,-235,1),(-135,-350,.85),(-365,-330,.8),(-235,-330,.8)]):
        b(f'CourtPlanter{i}', [x, 33, z], [13, 2, 13], limestone, material='Marble')
        b(f'CourtSoil{i}', [x, 34.05, z], [11.3, .2, 11.3], [98, 82, 60])
        b(f'CourtShrub{i}A', [x-2, 37, z], [9*scale, 6*scale, 9*scale], leaf, shape='Ball')
        b(f'CourtShrub{i}B', [x+2, 39, z+1], [7*scale, 8*scale, 7*scale], leaf_light, shape='Ball')
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
    for i in range(1,8):
        a = i * math.pi/4
        x,z=90+math.sin(a)*126,-330+math.cos(a)*126
        b(f'MusicFacade{i}',[x,38,z],[64,10,1.0],plum,rot=[0,math.degrees(a),0])
        b(f'MusicFacadeInlay{i}',[x,41,z+.02],[48,.75,1.2],violet,rot=[0,math.degrees(a),0])
    for i in range(12):
        a,c=i*math.tau/12,(i+1)*math.tau/12
        rail(f'StageMedallion{i}',[90+math.sin(a)*30,32.83,-330+math.cos(a)*30],
             [90+math.sin(c)*30,32.83,-330+math.cos(c)*30],1,.12,brass)
