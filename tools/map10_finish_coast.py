"""Map10 coastal finish, original visual-only props; caller owns collision flags.
Reference: actual MAP-10 blueprint + prior hero; vault make-map and level-flow notes.
Keep playable court, goal approaches, coastal race and dock deck unobstructed.
"""
import math


def add(box, disk, line):
    sand=(226,199,145); wet=(192,182,128); foam=(181,233,216)
    lagoon=(64,185,185); timber=(117,80,51); endgrain=(164,119,73)
    brass=(158,119,65); iron=(49,77,76); amber=(255,209,132)
    leaf=(73,123,74); sage=(119,156,87); cream=(231,218,174)

    def beam(name,a,b,width,color):
        dx,dy,dz=(b[i]-a[i] for i in range(3)); horizontal=math.hypot(dx,dz)
        box('Coast'+name,[(a[i]+b[i])/2 for i in range(3)],
            [width,width,math.sqrt(horizontal*horizontal+dy*dy)],color,
            [-math.degrees(math.atan2(dy,horizontal)),math.degrees(math.atan2(dx,dz)),0],material='Wood')

    # A scalloped sand apron AT THE WATERLINE, not a false extension of the
    # walkable plateau. Top stays far beneath all existing gameplay surfaces.
    edges=[(-490,442),(-430,490),(-370,495),(-310,526),(-250,527),
           (-190,527),(-130,540),(-70,541),(-10,541),(50,541),
           (110,526),(170,526),(230,526),(290,526),(350,496),(410,496),(470,454)]
    for i,(x,z) in enumerate(edges):
        width=74; reach=72+math.sin(i*1.7)*6
        box(f'CoastSandSlope{i}',[x,-88,z+reach*.35],[width,5,reach],sand,
            [19,0,0],material='Sand')
        disk(f'CoastWetSand{i}',x,-100.15,z+reach*.55,38,.7,wet,material='Sand')
        disk(f'CoastShallow{i}',x,-101.05,z+reach*.55,45,.3,lagoon)
        # Broken, unequal wave strokes read water rather than a perimeter fence.
        line(f'CoastFoam{i}',[x-23,-100.76,z+reach*.55+38],[x+21,-100.76,z+reach*.55+40],1.1,.12,foam)

    # Piles continue down to the sea rather than appearing to float; two
    # diagonals per bay support the existing cross-dock without changing it.
    for i,x in enumerate(range(-220,201,35)):
        box(f'CoastPileExtension{i}',[x,-65,610],[4.5,74,4.5],timber,material='Wood')
        box(f'CoastPileCap{i}',[x,.35,624],[4,1.1,4],endgrain,material='Wood')
        if i<12:
            beam(f'BraceA{i}',[x,-9,611],[x+35,-31,611],1.8,timber)
            beam(f'BraceB{i}',[x,-31,611],[x+35,-9,611],1.8,timber)
    # Fine board joints enhance timber reading without lots of full planks.
    for i,x in enumerate(range(-215,191,20)):
        box(f'CoastDeckJoint{i}',[x,.14,610],[.28,.08,30],timber)
    for i,z in enumerate([459,489,519,549,579]):
        box(f'CoastSpineJoint{i}',[-220,.14,z],[30,.08,.28],timber)

    # Low-profile nautical lanterns at the deck EDGE, 2.8 studs tall.
    # Warm emissive panes only, no global/PointLight changes or glare.
    for i,x in enumerate([-210,-145,-80,-15,50,115,180]):
        z=623
        box(f'CoastLanternBase{i}',[x,.42,z],[2.8,.6,2.8],brass)
        box(f'CoastLanternGlass{i}',[x,1.55,z],[1.65,1.75,1.65],amber,material='Neon')
        for side in [-1,1]:
            box(f'CoastLanternFrame{i}_{side}',[x+side*.95,1.55,z],[.22,1.9,2],iron)
        box(f'CoastLanternCap{i}',[x,2.64,z],[2.6,.45,2.6],iron)

    # Four spectator benches well south of goal/court envelopes and north of
    # the race corridor z402..438. Small planted pairs frame, not block, access.
    for i,x in enumerate([245,275,345,375]):
        z=382
        for dz in [-1.3,0,1.3]:
            box(f'CoastBenchSlat{i}_{dz}',[x,2,z+dz],[15,.55,1.05],endgrain,material='Wood')
        box(f'CoastBenchBack{i}',[x,4,z+2.1],[15,2,.6],timber,material='Wood')
        for side in [-1,1]:box(f'CoastBenchFoot{i}_{side}',[x+side*5.5,.9,z],[1.3,1.8,4],iron)
    for i,(x,z) in enumerate([(218,380),(402,380),(214,245),(412,245),(173,462),(344,462)]):
        disk(f'CoastPlanter{i}',x,1.2,z,4.5,2.4,cream)
        disk(f'CoastPlanterSoil{i}',x,2.44,z,3.8,.15,timber)
        for j in range(3):
            a=j*120+i*31
            box(f'CoastAgave{i}_{j}',[x,4,z],[1,4,5],leaf if j%2 else sage,[0,a,25])

    # A paired timber mooring bollard, intimate focal point at dock end.
    for i,x in enumerate([180,188]):
        disk(f'CoastBollard{i}',x,1,599,1.2,2,timber,material='Wood')
        disk(f'CoastBollardCap{i}',x,2.1,599,1.6,.35,brass)
