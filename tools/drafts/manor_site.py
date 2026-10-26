"""English manor: the estate, 1 m site plan for an altar level 3 (120 m) build area.

Terrain, water, formal gardens, the park and lake, and the tunnels. The house comes from manor-house.json
(run manor_house.py first), stamped in and simplified to 1 m squares.
Run: python manor_site.py  ->  writes manor-site.json
"""
import json, math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from manor_common import Plan, PALETTE

P = Plan('English manor: the estate', 1, 120, 120, 120)
P.project = 'English manor'
deep = P.level('deep', 'Deep tunnel & ice well (−7 m)', -7, 3)
tun = P.level('tun', 'Grotto tunnel (−4 m)', -4, 3)
cel = P.level('cel', 'Cellars & hill stair (−4 m)', -4, 4)
park = P.level('park', 'Park & lake (−3 m)', -3, 4)
casc = P.level('casc', 'Cascade step (−2 m)', -2, 1)
gar = P.level('garden', 'Parterre (−1 m)', -1, 4)
g0 = P.level('g0', 'Ground: house, forecourt, gardens', 0, 4)
grot = P.level('grot', 'Grotto & hill passage (0 m)', 0, 3)
f1 = P.level('f1', 'Boathouse & temple roofs (1 m)', 1, 3)
h2 = P.level('h2', 'Hill, lower terrace (+2 m)', 2, 4)
g1 = P.level('g1', 'First floor, hill (+4 m), roofs', 4, 4)
h6 = P.level('h6', 'Hilltop belvedere (+6 m)', 6, 3)
h9 = P.level('h9', 'Belvedere dome (9 m)', 9, 3)
R = P.rect
AX = 60.0
def M(g, x0, y0, x1, y1, ch, only=None):                 # a rectangle and its mirror across the main axis
    R(g, x0, y0, x1, y1, ch, only); R(g, 2 * AX - x1, y0, 2 * AX - x0, y1, ch, only)
wall_h = lambda name, color, h, base=0: P._alloc({'name': name, 'kind': 'wall', 'color': color, 'height': h, **({'base': base} if base else {})})
block_h = lambda name, color, h, base=0: P._alloc({'name': name, 'kind': 'block', 'color': color, 'height': h, **({'base': base} if base else {})})

# ================================================================= terrain
HILL = (108, 12)
def hill(mx, my):
    d = math.hypot(mx - HILL[0], my - HILL[1])
    return 6 if d <= 11 else 4 if d <= 15 else 2 if d <= 20 else None
P.ground_fn(hill)
P.ground_fn(lambda mx, my: 4, 99, 20, 105, 31, mode='max')  # a spur of the hill over the grotto passage
P.ground_rect(30, 65, 90, 91, -1)                          # parterre, a step below the terrace
P.ground_rect(0, 91, 120, 120, -3)                         # the park below the ha-ha
LAKE = lambda mx, my: ((mx - 60) / 38) ** 2 + ((my - 105.5) / 8) ** 2 <= 1 or ((mx - 34) / 10) ** 2 + ((my - 104) / 6) ** 2 <= 1
ISLE = (79, 105)
in_lake = lambda mx, my: LAKE(mx, my) and math.hypot(mx - ISLE[0], my - ISLE[1]) > 4.5
P.ground_fn(lambda mx, my: -4 if in_lake(mx, my) else None)
P.ground_disc(14, 100, 5.5, -2)                            # ice-house mound
P.ground_disc(14, 100, 3.5, -1)

# ================================================================= the house (from its own plan)
house = json.load(open(os.path.join(HERE, 'manor-house.json'), encoding='utf-8'))
HX, HY = 24, 25                                            # the house plan's corner on the site: its axis on x 60, the terrace meeting the parterre at y 65
# ================================================================= north: gate lodges, drive, forecourt
R(g0, 57, 0, 63, 18, ':')
LODGES = (44, 70)
for x0 in LODGES:                                          # lodges with pyramid roofs
    P.box_walls(g0, x0, 1, x0 + 6, 7, 'A', 1, floor='m')
    R(g0, x0 + 2, 6, x0 + 4, 7, 'D')
    R(g0, x0, 3, x0 + 1, 5, 'o'); R(g0, x0 + 5, 3, x0 + 6, 5, 'o')
lodge_roof = P.roof(g1)
for x0 in LODGES: lodge_roof.hip(x0, 1, x0 + 6, 7, 'slate', pitch=0.9, overhang=0.5, base=0.5)
pier = wall_h('Highly Polished Stone Block (gate pier)', '#b3b0a9', 3)
for x in (56, 63): R(g0, x, 6, x + 1, 7, pier)
P.disc(g0, 60, 22, 13, ':')                                # gravel sweep before the portico
R(g0, 37, 27, 84, 43, ':')                                 # the court between the pavilions, embraced by the colonnades
P.disc(g0, 60, 22, 7, 'l')                                 # lawn round a fountain
P.disc(g0, 60, 22, 3.2, 'c'); P.disc(g0, 60, 22, 2.6, '~')
# ================================================================= stables (north-west): three brick ranges round a cobbled yard
R(g0, 6, 8, 23, 32, 'z')
for (x0, y0, x1, y1) in ((4, 6, 24, 12), (4, 6, 10, 34), (4, 28, 24, 34)):
    P.box_walls(g0, x0, y0, x1, y1, 'K', 1, floor=';')
R(g0, 10, 12, 24, 28, 'z')                                 # the yard opens east onto the kitchen yard
R(g0, 15, 6, 19, 12, 'z'); R(g0, 15, 6, 16, 12, 'K'); R(g0, 18, 6, 19, 12, 'K')      # carriage arch through the north range
for x in (11, 20): R(g0, x, 11, x + 2, 12, 'D')
for x in (12, 19): R(g0, x, 28, x + 2, 29, 'D')
for y in (16, 22): R(g0, 9, y, 10, y + 2, 'D')
sroof = P.roof(g1)
sroof.gable(4, 6, 24, 12, 'x', 'slate', pitch=0.8, overhang=0.5)
sroof.gable(4, 6, 10, 34, 'y', 'slate', pitch=0.8, overhang=0.5)
sroof.gable(4, 28, 24, 34, 'x', 'slate', pitch=0.8, overhang=0.5)
sroof.cut(15, 5, 19, 13)
sroof.caps('slatecap')
sroof.paint(only=' ')
clock = wall_h('Refined Sandstone Block (clock tower)', '#ada198', 6)
R(g1, 15, 7, 19, 11, clock, only=' ')
R(g0, 24, 13, 37, 27, ';')                                 # kitchen yard, between the stables and the kitchen pavilion
# ================================================================= walled kitchen garden (west)
gw = wall_h('Fired Bricks Block (garden wall, 3 m)', '#aa7657', 3)
P.box_walls(g0, 3, 38, 26, 90, gw, 1, floor=':')
for y0 in range(46, 86, 6):
    for (x0, x1) in ((5, 13), (16, 24)):
        R(g0, x0, y0, x1, y0 + 4, 'g')
R(g0, 14, 44, 15, 89, ':'); R(g0, 4, 64, 25, 66, ':')
P.disc(g0, 14.5, 65, 2.2, 'c'); P.disc(g0, 14.5, 65, 1.7, '~')                         # dipping pond
R(g0, 25, 64, 26, 66, 'D'); R(g0, 13, 89, 16, 90, 'D'); R(g0, 13, 38, 16, 39, 'D')
R(g0, 4, 39, 25, 43, ';')                                  # glasshouse along the warm north wall
R(g0, 4, 43, 25, 44, 'q'); R(g0, 14, 43, 15, 44, 'D')
gh = P.roof(g1); gh.lean_to(4, 39, 25, 44, 'n', 2.0, 0.5, 'glass'); gh.paint(only=' ')
# ================================================================= the parterre (−1 m): mirrored about the axis
R(gar, 30, 65, 90, 91, 'l')
step = block_h('Limestone Block (step)', '#a79a88', 0.5)
R(gar, 56, 65, 64, 66, step)                               # steps down from the terrace
ret = wall_h('Limestone Block (retaining wall)', '#a79a88', 1)
R(gar, 30, 65, 56, 65.5 + 0.5, ret); R(gar, 64, 65, 90, 66, ret)
R(gar, 30, 65, 30.5 + 0.5, 91, ret); R(gar, 89, 65, 90, 91, ret)
R(gar, 57, 66, 63, 91, ':'); R(gar, 31, 72, 89, 74, ':')
P.disc(gar, 60, 73, 4.2, 'c'); P.disc(gar, 60, 73, 3.6, '~'); P.disc(gar, 60, 73, 0.9, 'c')     # central fountain
R(gar, 57, 80, 63, 91, 'c'); R(gar, 58, 80, 62, 91, '~')   # the long canal down the axis
for side in (0, 1):                                        # long waters at the sides
    x0 = 31 if side == 0 else 86
    R(gar, x0, 66, x0 + 3, 90, 'c'); R(gar, x0 + 1, 67, x0 + 2, 89, '~')
# broderie beds: box hedge scrolls round flowers, mirrored
def broderie(x0, y0, x1, y1):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for x, y in P.cells_rect(x0, y0, x1, y1):
        mx, my = P.centre_m(x, y)
        u, v = abs(mx - cx) / ((x1 - x0) / 2), abs(my - cy) / ((y1 - y0) / 2)
        r = math.hypot(u, v * 0.9)
        edge = u > 0.93 or v > 0.9
        ring = abs(r - 0.62) < 0.08 or abs(r - 0.3) < 0.09
        diag = abs(u - v) < 0.06 and r > 0.38
        gar[y][x] = 'h' if (edge or ring or diag) else ('f' if 0.3 < r < 0.62 else 'l')
for (x0, y0, x1, y1) in ((35, 66, 55, 71.5), (35, 74.5, 55, 79.5), (35, 81, 55, 89.5)):
    broderie(x0, y0, x1, y1); broderie(2 * AX - x1, y0, 2 * AX - x0, y1)
# ha-ha (a sunken wall so the park can't be seen fenced) and the cascade on the axis
haha = wall_h('Limestone Block (ha-ha wall)', '#a79a88', 2)
R(park, 0, 91, 120, 92, haha); R(park, 57, 91, 63, 92, ' ')
R(casc, 57, 91, 63, 92, '~'); R(casc, 56, 91, 57, 92, 'c'); R(casc, 63, 91, 64, 92, 'c')
P.ground_rect(57, 91, 63, 92, -3)
for (x0, x1) in ((22, 26), (94, 98)):                      # steps down from the garden walks into the park
    R(g0, x0, 86, x1, 91, ':', only=' ')
    R(park, x0, 92, x1, 96, ':')
# ================================================================= park (−3 m), lake, island temple, boathouse, ice house
R(park, 0, 92, 120, 115, 'l')                              # (the altar's 120 m area ends at 115.5 m)
for x, y in P.cells_rect(0, 92, 120, 120):
    mx, my = P.centre_m(x, y)
    if in_lake(mx, my): park[y][x] = '~'
R(park, 57, 92, 63, 98, '~'); R(park, 56, 92, 57, 97, 'c'); R(park, 63, 92, 64, 97, 'c')      # canal from the cascade to the lake
P.ground_rect(57, 92, 63, 98, -4)
P.disc(park, ISLE[0], ISLE[1], 4.4, 'l'); P.disc(park, ISLE[0], ISLE[1], 3.2, ',')
P.ring_wall(park, ISLE[0], ISLE[1], 3.2, ' ', 0.5)
for k in range(8):                                         # temple folly: eight columns and a stone dome
    a = math.radians(k * 45 + 22.5)
    x, y = ISLE[0] + 2.6 * math.sin(a), ISLE[1] - 2.6 * math.cos(a)
    R(park, round(x - 0.5), round(y - 0.5), round(x - 0.5) + 1, round(y - 0.5) + 1, 'P')
tdome = P.roof(f1); tdome.dome(ISLE[0], ISLE[1], 3.6, 2.5, 'stone', base=0.5, rim=0.85)
P.box_walls(park, 38, 92, 49, 99, 'K', 1, floor=';')       # boathouse, open to the lake on the south
R(park, 39, 98, 48, 99, ' '); R(park, 40, 94, 47, 99, '~'); R(park, 39, 92, 49, 93, 'K')
R(park, 43, 93, 44, 94, ' ')                               # ladder hole: the deep tunnel comes up here
R(park, 49, 94, 50, 96, ' '); R(park, 48, 94, 49, 96, 'D')
tdome.gable(38, 92, 49, 99, 'y', 'slate', pitch=0.8, overhang=0.5)
tdome.caps('slatecap')
tdome.paint()
# ice house: a brick chamber inside a grassy mound, a well below it for the ice
R(park, 11, 96, 18, 105, ' ')
P.ring_wall(park, 14, 100, 2.6, 'K', 1); P.disc(park, 14, 100, 1.7, ';')
R(park, 13, 94, 15, 97.5, ';'); R(park, 13, 97, 15, 98, 'D')
P.disc(deep, 14, 100, 1.7, '_')
# ================================================================= the maze (east): yew hedges from a random-walk maze
MX0, MY0, NX, NY = 97, 42, 10, 23
hedge = [[True] * (2 * NX + 1) for _ in range(2 * NY + 1)]
rnd = random.Random(1717)
stack, seen = [(0, 0)], {(0, 0)}
hedge[1][1] = False
while stack:
    cx, cy = stack[-1]
    nbrs = [(cx + dx, cy + dy, dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= cx + dx < NX and 0 <= cy + dy < NY and (cx + dx, cy + dy) not in seen]
    if not nbrs: stack.pop(); continue
    nx, ny, dx, dy = rnd.choice(nbrs)
    hedge[2 * cy + 1 + dy][2 * cx + 1 + dx] = False; hedge[2 * ny + 1][2 * nx + 1] = False
    seen.add((nx, ny)); stack.append((nx, ny))
for j in range(2 * NY + 1):
    for i in range(2 * NX + 1):
        g0[MY0 + j][MX0 + i] = 'H' if hedge[j][i] else ':'
R(g0, MX0 + 8, MY0 + 20, MX0 + 13, MY0 + 27, ':')         # the clearing in the middle
R(g0, MX0, MY0 + 23, MX0 + 1, MY0 + 25, ':')               # entrance from the west walk
R(g0, 90, 66, 97, 68, ':')
# walks round the gardens, and the two side gardens south of the pavilions
R(g0, 26, 43, 30, 91, ':', only=' '); R(g0, 90, 43, 97, 91, ':', only=' ')
R(g0, 30, 43, 44, 65, ':', only=' ')                       # bowling green beside the kitchen pavilion
R(g0, 31, 45, 41, 63, 'l')
R(g0, 76, 43, 90, 65, ':', only=' ')                       # flower garden under the orangery's glass front
for y0 in range(45, 63, 4):
    R(g0, 79, y0, 89, y0 + 3, 'h'); R(g0, 80, y0 + 1, 88, y0 + 2, 'f')
R(g0, 94, 31, 99, 43, ':', only=' ')                       # path up the orangery's east side to the hill door
# ================================================================= the hill: grotto, tunnel, belvedere
GROT = (105, 16)
# The grotto and its passage are on their own 3 m level, so the hill closes over them (the 6 m core over the
# grotto, a 4 m spur over the passage).
stal = block_h('White Luminescent Block (stalactite)', '#d1cac6', 0.5, base=2.5)
P.disc(grot, GROT[0], GROT[1], 5.2, 'L'); P.disc(grot, GROT[0], GROT[1], 4.4, ';')        # shell-lined cave
P.disc(grot, GROT[0] + 1.5, GROT[1] - 1, 2, '~')                                          # the spring
P.radial(grot, GROT[0], GROT[1], [0, 60, 120, 180, 240, 300], 0.4, 3.6, 4.4, stal)     # glowing stalactites
R(grot, 97, 17, 101, 20, ';', only=' L')                   # landing at the top of the hill stair
R(grot, 98, 20, 100, 24, '_')                              # headroom over the top of the stair
R(grot, 101, 18, 103, 31, ';', only=' L')                  # passage south through the spur
R(grot, 100, 20, 101, 30, 'L'); R(grot, 103, 20, 104, 30, 'L', only=' ')   # the lining stops short, so only bare earth shows round the door
R(grot, 101, 30, 103, 31, 'Z')                             # the door, in the spur's face
R(g0, 99, 31, 104, 35, ':')                                # a gravel landing outside
# tunnel: from the wine-cellar door (east of the house) at −4 m, north under the maze corner, up a stair in the hill
R(tun, 80, 42, 100, 44, ';'); R(tun, 98, 28, 100, 44, ';')   # joins the house's cellar passage at x 80
P.lining(tun, ';', 'K', ' ', 80, 28, 101, 45)
R(cel, 98, 20, 100, 28, ';')
I = P.item
I('cel', 'stairs', 'Hill stair up to the grotto', 98, 20, 2, 8, 4, 0, '#a98a62', 'gst')
# belvedere on the hilltop
P.disc(h6, HILL[0], HILL[1], 3.4, ',')
for k in range(6):
    a = math.radians(k * 60)
    x, y = HILL[0] + 2.6 * math.sin(a), HILL[1] - 2.6 * math.cos(a)
    R(h6, round(x - 0.5), round(y - 0.5), round(x - 0.5) + 1, round(y - 0.5) + 1, 'P')
bd = P.roof(h9); bd.dome(HILL[0], HILL[1], 3.8, 2.5, 'stone', base=0.5, rim=0.85); bd.paint()
# ================================================================= the deep tunnel: crypt passage to the boathouse (−7 m)
# South under the terrace and the parterre's canal, west under the broderie beds (well clear of the cascade and
# the lake canal, whose bed is at −4 m), then south to a ladder into the boathouse.
R(deep, 59, 63, 61, 90, ';'); R(deep, 43, 88, 61, 90, ';'); R(deep, 43, 88, 45, 95, ';')
P.lining(deep, ';', 'R', ' ', 42, 62, 62, 96)
I('deep', 'ladder', 'Ladder up to the crypt passage', 59, 64, 1, 1, 3, color='#7a5236', iid='dld')
R(tun, 43, 93, 44, 94, '_')                                # the ladder shaft up into the boathouse
I('deep', 'ladder', 'Ladder up into the boathouse', 43, 93, 1, 1, 4, color='#7a5236', iid='bld')

# ================================================================= stamp the house in
P.stamp(house, HX, HY, 'hs', 'House')
R(cel, 59, 64, 61, 65, '_')                                # a shaft at the end of the crypt passage, down to the deep tunnel

# ================================================================= planting, statues, lanterns
for k, y in enumerate((1, 6, 11)):                         # avenue along the drive
    I('g0', 'tree', 'Lime tree (avenue)', 53, y, 2, 2, 10, color='#4f6b34', iid=f'av{k}w')
    I('g0', 'tree', 'Lime tree (avenue)', 65, y, 2, 2, 10, color='#4f6b34', iid=f'av{k}e')
for k, y in enumerate(range(68, 90, 5)):                   # topiary down the central walk
    if 70 <= y <= 76: continue
    I('garden', 'custom', 'Topiary yew', 56, y, 1, 1, 2.5, color='#4f7a26', iid=f'tw{k}')
    I('garden', 'custom', 'Topiary yew', 63, y, 1, 1, 2.5, color='#4f7a26', iid=f'te{k}')
for k, (x, y) in enumerate(((34, 72), (85, 72), (57.5, 67), (62, 67))):
    I('garden', 'custom', 'Statue', x, y, 1, 1, 3, color='#b3b0a9', iid=f'gst{k}')
I('park', 'custom', 'Statue of the founder', ISLE[0] - 0.5, ISLE[1] - 0.5, 1, 1, 3, color='#b3b0a9', iid='tstat')
I('park', 'boat', 'Rowing boat', 41, 95, 3, 2, 1, color='#7a5236', iid='boat')
for k, (x, y) in enumerate(((8, 108), (24, 109), (100, 108), (110, 96), (30, 95), (88, 95), (104, 102), (6, 94))):
    I('park', 'tree', 'Cedar (park)', x, y, 3, 3, 14, color='#3f5f30', iid=f'pt{k}')
ON_GROUND = {-3: 'park', -1: 'garden', 0: 'g0', 2: 'h2', 4: 'g1', 6: 'h6'}
def hill_tree(k, ang, r):                                  # an oak on whatever terrace is under it
    x = round(HILL[0] + r * math.sin(math.radians(ang)) - 1); y = round(HILL[1] - r * math.cos(math.radians(ang)) - 1)
    hs = {P.ground_at(x + i, y + j) for i in (0, 1) for j in (0, 1)}
    if len(hs) == 1 and hs.pop() in ON_GROUND and 0 <= x and 0 <= y and x + 2 <= 120:
        I(ON_GROUND[P.ground_at(x, y)], 'tree', 'Oak (hill)', x, y, 2, 2, 12, color='#4f6b34', iid=f'ht{k}')
for k, (ang, r) in enumerate(((290, 17.5), (330, 17.5), (20, 17.5), (70, 17.5), (110, 17.5), (250, 13), (350, 13), (60, 13), (150, 13))):
    hill_tree(k, ang, r)
I('h6', 'custom', 'Telescope', HILL[0] - 0.5, HILL[1] - 0.5, 1, 1, 2, color='#c9a227', iid='scope')
I('grot', 'custom', 'Grotto statue (river god)', GROT[0] - 2, GROT[1] + 1, 1, 1, 2, color='#8c7958', iid='gstat')
I('g0', 'lever', 'Hidden lever (opens the rock door)', 103, 34, 1, 1, 1, color='#c9a227', iid='rlever')
I('g0', 'custom', 'Maze statue', MX0 + 10, MY0 + 23, 1, 1, 3, color='#b3b0a9', iid='mstat')
I('g0', 'custom', 'Bench', MX0 + 9, MY0 + 21, 2, 1, 0.5, color='#a79a88', iid='mbench')
for k, (x, y) in enumerate(((6, 47), (6, 59), (18, 47))):
    I('g0', 'seedbed', 'Seedbed', x, y + 4, 2, 2, 0.5, color='#6f8a43', iid=f'ks{k}')
I('g0', 'npc-farmer', 'Farmer (kitchen garden)', 17, 70, 2, 2, 2, color='#7c9a3d', iid='kfarm')
for k, (x, y) in enumerate(((11, 18), (11, 23))):
    I('g0', 'pen', 'Stable stalls', x, y, 5, 4, 1.5, color='#a0905a', iid=f'pen{k}')
I('g0', 'trough', 'Water trough', 19, 21, 2, 1, 1, color='#6f8fa3', iid='trough')
I('g0', 'npc-hunter', 'Hunter (gamekeeper)', 19, 14, 2, 2, 2, color='#6d7a45', iid='keeper')
for k, (x, y) in enumerate(((50, 18), (69, 18), (47, 33), (72, 33))):
    I('g0', 'light', 'Lantern', x, y, 1, 1, 1.5, color='#e3b341', iid=f'fl{k}')
I('park', 'npc-fisher', 'Fisher (lake)', 51, 93, 2, 2, 2, color='#3f7f9e', iid='fisher')
I('park', 'fishing', 'Fishing spot', 53, 95, 2, 2, 1, color='#3f8fc1', iid='fish')

Z = P.zone
Z('g0', 'Forecourt', 37, 9, 84, 43, '#b8862b')
Z('g0', 'Stables', 4, 6, 24, 34, '#9a7344')
Z('g0', 'Kitchen yard', 24, 13, 37, 27, '#8b8478')
Z('g0', 'Bowling green', 30, 43, 44, 65, '#3f8a4f')
Z('g0', 'Orangery flower garden', 76, 43, 90, 65, '#c2416e')
Z('g0', 'Walled kitchen garden', 4, 39, 25, 89, '#3f8a4f')
Z('g0', 'Hedge maze', MX0, MY0, MX0 + 21, MY0 + 47, '#4f7a26')
Z('grot', 'Grotto (secret)', 99, 10, 111, 22, '#2f7fb3')
Z('grot', 'Passage to the rock door', 100, 20, 104, 31, '#8a5cc2')
Z('garden', 'Parterre', 30, 65, 90, 91, '#5f7d3a')
Z('park', 'Lake', 22, 98, 98, 118, '#2f7fb3')
Z('park', 'Temple island', 74, 103, 84, 113, '#b8862b')
Z('park', 'Boathouse', 38, 92, 49, 99, '#9a7344')
Z('park', 'Ice house', 9, 95, 19, 106, '#6f8fa3')
Z('tun', 'Tunnel to the grotto', 80, 42, 100, 44, '#8a5cc2')
Z('deep', 'Tunnel to the boathouse', 59, 63, 61, 90, '#8a5cc2')
Z('deep', 'Tunnel to the boathouse (west)', 43, 88, 59, 90, '#8a5cc2')
Z('h6', 'Belvedere', 104, 8, 112, 16, '#b8862b')

problems = P.check(outdoor_ok=('g0', 'grot', 'garden', 'park', 'h2', 'g1', 'h6'), ignore_types=('stairs', 'spire', 'ladder', 'boat'))
print('item problems:', len(problems))
for p_ in problems[:50]: print('  ', p_)

NOTES = """English manor estate, drafted by Claude. Uses 1 m squares (1M cubes) and altar level 3 (120 m), with the Flame Altar in the saloon at the heart of the house. The house comes from "English manor: the house" (0.5 m detail), simplified to 1 m. The ground is shaped with terrain, and every height below is a level you can step through.

GROUND HEIGHTS
- 0 m: the house, its terrace, the forecourt, the stables, the side gardens, the walled kitchen garden and the maze.
- −1 m: the parterre, one step down from the terrace.
- −3 m: the park below the ha-ha, a sunken wall so nothing fences the view. The lake fills a basin 1 m deeper.
- +2, +4 and +6 m: a wooded hill in the north-east with a belvedere on top. A 4 m spur runs south over the grotto passage.

THE HOUSE
- A Palladian villa: a giant portico on the north, a domed round saloon bowing out over the south terrace.
- Curved quadrant colonnades reach forward to two pavilions: the brick kitchen (west) and the glass orangery (east). Between them they embrace the forecourt.
- See "English manor: the house" for the rooms, the levels above the eaves, and the nine secrets inside.

APPROACH
- Gate lodges with pyramid roofs and stone piers.
- A lime avenue leads to a gravel sweep round a lawn and fountain, then into the court between the colonnades.

GARDENS
- Parterre (60 x 26 m):
  - Six broderie beds of box hedge scrolls round flowers, mirrored about the axis, with topiary yews and statues.
  - A round fountain at the crossing, and long waters down both sides.
  - A central canal runs south and spills over a cascade in the ha-ha into the lake.
- Walled kitchen garden (west): brick walls, beds of Farm Soil, a dipping pond, Seedbeds and the Farmer.
- Hedge maze (east): 2.5 m yew hedges round a clearing with a statue.
- Stables (north-west): three brick ranges round a cobbled yard, a carriage arch under a clock tower, stalls, a trough and the gamekeeper (Hunter). The yard opens onto the kitchen yard by the kitchen's back door.
- Side gardens, either side of the house: a bowling green (west) and a flower garden of hedged beds under the orangery's glass front (east).

PARK & LAKE
- The lake, with a temple folly on an island (eight columns and a stone dome, round a statue). It's reached by boat.
- A brick boathouse with a water slip, a rowing boat, and the Fisher on the shore.
- An ice house: a brick chamber inside a grassy mound, with a deep ice well under it.

SECRETS & UNDERGROUND
- House: nine secrets, from the library bookcase to the astronomer's room (see the house plan). Two of them lead out into the grounds.
- Grotto tunnel (−4 m): from the wine-rack door in the cellars, brick-lined, east under the orangery and north under the maze corner.
  - A stair climbs inside the hill to a shell-lined grotto (its own 3 m level, under 6 m of hill) with a spring and glowing stalactites.
  - A passage runs south inside a spur of the hill to a rock-face door beside the orangery, opened by a hidden lever.
- Deep tunnel (−7 m): from the hidden door in the crypt, a short passage to a ladder shaft, then south under the terrace and the parterre's canal, west under the broderie beds, and south under the ha-ha.
  - It keeps clear of the cascade and the lake canal, whose beds are 3–4 m down.
  - A ladder comes up through a trapdoor in the boathouse floor.

NOTES
- Hedges are Foliage blocks. Building hedges from terrain material is an assumption, so check it in game.
- The park sits 3 m below the house, so you'd dig the gardens down or build the house up. Either works inside the altar's area.
"""
out = os.path.join(HERE, 'manor-site.json')
print('bytes', P.save(out, NOTES, 'r-claude-manor-site-2'))
for a, b in P.merged: print('  folded:', a, '->', b)
print('levels', [(L['id'], L['elev'], L['height']) for L in P.levels])
print('palette', len(set(c for g in P.grids.values() for r in g for c in r) - {' '}))
