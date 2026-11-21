"""Original arena finishing: pale stone, teal enamel, aged bronze. Art-only."""
import math

def add(box, disk, line):
    limestone=(201,180,146); highlight=(237,221,191); dark=(53,68,71)
    tile=(37,102,104); bronze=(163,123,69)
    # Build contrasting continuous seat caps on the existing seven bowl faces.
    for seat in range(5):
        r=112+seat*7
        for side in (0,1,3,4,5,6,7):
            a=side*math.pi/4; rad=(math.sin(a),math.cos(a))
            x,z=-330+rad[0]*r,120+rad[1]*r
            width=2*r*math.tan(math.pi/8)-5
            name=f'StadiumTier{seat}_{side}'
            box(name+'Coping',(x,seat*3+3.16+side*.007,z),
                (width,.24,7.2),highlight if seat%2==0 else limestone,(0,side*45,0),'Concrete')
            sx,sz=x-rad[0]*4.04,z-rad[1]*4.04
            box(name+'Tile',(sx,seat*3+2.45,z-rad[1]*4.04),(width,.45,.11),
                tile if seat<4 else bronze,(0,side*45,0),'Metal')
    # Exterior pillars face their own octagon wall. Never place props in the
    # floor, entry, trainer area or the close gameplay silhouette.
    for side in (0,1,3,4,5,6,7):
        a=side*math.pi/4; rad=(math.sin(a),math.cos(a)); tangent=(rad[1],-rad[0])
        for i,k in enumerate((-32,32)):
            x=-330+rad[0]*146+tangent[0]*k
            z=120+rad[1]*146+tangent[1]*k
            name=f'StadiumButtress{side}_{i}'
            box(name+'Base',(x,.75,z),(10,1.5,13),dark,(0,side*45,0),'Concrete')
            box(name+'Stem',(x,7.4,z),(7,13,9),limestone,(0,side*45,0),'Sandstone')
            box(name+'Cornice',(x,14.55,z),(10,1.45,12),highlight,(0,side*45,0),'Concrete')
            box(name+'BronzeInlay',(x+rad[0]*4.56,9,z+rad[1]*4.56),(2.1,8,.12),bronze,(0,side*45,0),'Metal')
    # Entrance gateway straddles the wide east access without narrowing it.
    for side in (-1,1):
        x,z=-215,120+side*34
        name=f'StadiumEntry{side}'
        box(name+'Plinth',(x,.65,z),(12,1.3,12),dark,material='Slate')
        box(name+'Stone',(x,10,z),(9,19,8),limestone,material='Sandstone')
        box(name+'Seat',(x,19.9,z),(12,1.3,12),highlight,material='Concrete')
    box('StadiumEntryLintel',(-215,21.15,120),(10,3.4,78),dark,material='Concrete')
    box('StadiumEntryBronzeEdge',(-220.13,22.15,120),(.15,.45,76),bronze,material='Metal')
    box('StadiumEntryStoneEdge',(-215,23.1,120),(13,.6,80),highlight,material='Concrete')
    box('StadiumMarquee',(-209.84,21.42,120),(29,2.65,.28),dark,(0,-90,0),'Metal')
    for side in (-1,1):
        box(f'StadiumEntryRibbon{side}',(-220.15,20.6,120+side*25),(.15,.26,13),tile,material='Metal')
    # Painted registration marks outside the PvP square. Keep existing red
    # boundary and unobstructed view of player/boss strike or beam effects.
    for x in (-414,-246):
        for z in (36,204):
            name=f'StadiumCorner{x}_{z}'
            box(name+'X',(x,.207,z),(8,.03,.28),highlight)
            # The east Z ticks sit inside the raised garden terraces.
            if x == -414:
                box(name+'Z',(x,.206,z),(.28,.03,8),highlight)
