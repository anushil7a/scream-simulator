"""Large-form dressing pass: focal paving, windy coastal trees, fractured basalt caps."""
import json
import math
from pathlib import Path

def add(box,disk,line):
    limestone=(210,192,158); ochre=(171,131,75); cream=(231,213,174)
    turquoise=(56,112,109); grout=(164,149,119)
    # Fountain plaza becomes a readable civic landmark instead of a bare slab.
    disk('LandmarkMosaicBedding',-300,32.113,-300,35,.16,grout)
    disk('LandmarkMosaicField',-300,32.22,-300,33.8,.12,limestone,'Marble')
    for i in range(16):
        a=2*math.pi*i/16
        b=a+2*math.pi/16
        def at(angle,r,y): return (-300+r*math.cos(angle),y,-300+r*math.sin(angle))
        line('LandmarkMosaicBorder'+str(i),at(a,33.4,32.31),at(b,33.4,32.31),.64,.075,turquoise,'Marble')
        if i%2==0:
            line('LandmarkMosaicRay'+str(i),at(a,23,32.31),at(a,32,32.31),
                 1.1 if i%4==0 else .58,.07,ochre,'Marble')
    # Garden-like edges in quiet plaza pockets. Ground-level layers guide the eye
    # without making furniture look like an obstacle in the trainer or access lanes.
    for index,(x,z) in enumerate([(-388,-326),(-216,-326),(-400,-369),(-205,-369),(-469,-218),(-128,-217)]):
        n=f'LandmarkPlazaGarden{x}_{z}'
        if index==0:
            x,z=-379,-352  # Leave the painted Rookie route clear while retaining the part IDs.
        disk(n+'Stone',x,32.68,z,10.3,1.1,cream,'Sandstone')
        disk(n+'Soil',x,33.27,z,9.55,.18,(126,144,88),'Grass')
        # Two interlocking crown lobes share one planted trunk; the third lobe is groundcover.
        side = -1 if index%2 else 1
        soil_top = 33.27+.18/2
        trunk_x, trunk_z = x+2*side, z+2
        trunk_base, trunk_height = soil_top-.06, 5.3
        crown_y = trunk_base+trunk_height+.55
        box(n+'Cypress0',(x-.15*side,crown_y-.55,z+.4),(4.8,4.4,4.6),(91,126,83),material='Grass',shape='Ball')
        box(n+'Trunk1',(trunk_x,trunk_base+trunk_height/2,trunk_z),(.85,trunk_height,.85),
            (111,79,54),material='Wood')
        box(n+'Cypress1',(trunk_x,crown_y,trunk_z),(6.4,6,6.2),(62,108,79),material='Grass',shape='Ball')
        box(n+'Cypress2',(x-2.9*side,soil_top+3.8/2-.42,z-2.9),(4.4,3.8,4),(118,147,89),material='Grass',shape='Ball')
    # Polygonal crowns interlock with the old tall ridge silhouette. Keep all
    # original solid surfaces and their material so gameplay physics stays put.
    geometry = Path(__file__).resolve().parents[1] / 'prototypes/map10/geometry.json'
    base_ids = {part['id'] for part in json.loads(geometry.read_text(encoding='utf-8'))['parts']}
    for i in range(12):
        if f'VolcanicRidge{i}' not in base_ids:
            continue
        a=i*math.tau/12
        x,z=355+math.cos(a)*125,-70+math.sin(a)*164
        y=62+(i%3)*14
        rot=(6+(i%4)*3, math.degrees(a)+11, -10+(i%4)*6)
        palette=[(72,64,70),(82,72,75),(66,63,72),(94,77,76)]
        box(f'LandmarkBasalt{i}Long',(x+math.cos(a)*2,y+2.8,z+math.sin(a)*3),(31,13+(i%3)*3,32),
            palette[i%4],rot,'Basalt','Wedge')
        box(f'LandmarkBasalt{i}Cut',(x-math.sin(a)*9,y-1.7,z+math.cos(a)*5),(19,10,25),
            palette[(i+2)%4],(-9,math.degrees(a)+122,7),'Slate','Wedge')
    # Breezy coastal garden clusters away from the playable centerline.
    for i,(x,z,k) in enumerate([(-167,326,1),(-143,323,.82),(-128,344,1.14),
                                (121,454,1.04),(149,463,.86),(160,439,.93)]):
        n=f'LandmarkCoastPalm{i}'
        disk(n+'Base',x,.46,z,5.3,.82,cream,'Sandstone')
        box(n+'Trunk',(x,6*k,z),(1.24*k,12*k,1.3*k),(115,81,49),(0,0,-5),'Wood')
        for j in range(6):
            a=(j/6)*math.tau+(i%3)*.22
            box(n+f'Canopy{j}',(x+math.cos(a)*3.1*k,12.15*k,z+math.sin(a)*3.1*k),
                (10.8*k,.52*k,2.7*k),[(72,129,87),(88,146,85),(112,154,87)][j%3],
                (0,-math.degrees(a),-9 if j%2==0 else 12),'Grass','Ball')
