"""Laketown: the causeway, the gatehouse and the shore landing. 0.5 m detail plan. Pass 3 of 3: review and finishing touches.

The town's front door, on its south side. From the shore road a paved path runs straight to the gate: into a
forecourt between two castle stone towers, through an open arch shallower than the towers and closed by a
pair of steel portcullises, and over a drawbridge that spans the moat between the towers' prows (its chains
up to the arch) onto the causeway, 6 m of rough wood at +3 m north to the square's stair, with a branch west
up to the arena's stands and a strip east for the main dock's stair on the way. A wall-walk on the arch joins
the towers.

The towers differ on purpose: the west tower is a battlemented fighting platform flying the town's banner;
the east tower is the watch tower, its top storey a watch room under a slate pyramid with a lantern. They
rise from the lake on stone foundations, not stilts.

Coordinates are the layout's (doc `laketown`): this plan's corner is the layout's (58, 98).
Run: python laketown_gatehouse.py  ->  writes laketown_gatehouse.json
"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laketown_common import Area, WOOD, STONE

CASTLE, RS, RCS, TAR = '#7c8084', '#7d776a', '#62605d', '#5d5652'
OX, OY = 58, 98
A = Area('Laketown: causeway, gatehouse and shore landing (detail)', OX, OY, 44, 62, {
    'C': {'name': 'Castle Block', 'kind': 'floor', 'color': CASTLE},                  # the gatehouse floors
    'c': {'name': 'Field Stones', 'kind': 'floor', 'color': '#8a8170'},                # the landing
    'q': {'name': 'Rocky Stone Road Block', 'kind': 'floor', 'color': '#84715f'},      # the path through the gate
    'd': {'name': 'Dirt Road Block', 'kind': 'floor', 'color': '#8c7455'},             # the shore road
    'k': {'name': 'Roughly Cut Stone Block', 'kind': 'floor', 'color': RCS},           # the arena (its blueprint)
    'D': {'name': 'Tarred Wood Block (drawbridge)', 'kind': 'floor', 'color': TAR},
    'K': {'name': 'Castle Block', 'kind': 'wall', 'color': CASTLE},                    # walls, a storey a level
    'M': {'name': 'Castle Block (gate pier)', 'kind': 'wall', 'color': CASTLE, 'height': 7.5},
    'j': {'name': 'Fancy Stone Block (arch jamb)', 'kind': 'wall', 'color': STONE, 'height': 7.5},
    'g': {'name': 'Castle Block (portcullis wall)', 'kind': 'wall', 'color': CASTLE, 'height': 6},
    'h': {'name': 'Castle Block (foundation)', 'kind': 'wall', 'color': CASTLE, 'height': 6.5},
    'b': {'name': 'Castle Block (battered base)', 'kind': 'block', 'color': CASTLE, 'height': 5},
    'p': {'name': 'Castle Block (parapet)', 'kind': 'block', 'color': CASTLE, 'height': 1},
    'o': {'name': 'Castle Block (merlon)', 'kind': 'block', 'color': CASTLE, 'height': 1.5},
    'n': {'name': 'Refined Wood Block (shelter post)', 'kind': 'block', 'color': WOOD, 'height': 3},
    'J': {'name': 'Iron Block (drawbridge band)', 'kind': 'floor', 'color': '#848483'},
    'Y': {'name': 'Arrow slit (a gap in the wall)', 'kind': 'window', 'color': CASTLE, 'opening': 1.5, 'sill': 1},
    'y': {'name': 'Arrow slit (its cross arms)', 'kind': 'window', 'color': CASTLE, 'opening': 0.5, 'sill': 1.5},
    'F': {'name': 'Fancy Stone Block (string course)', 'kind': 'block', 'color': STONE, 'height': 0.5},
    'T': {'name': 'Castle Block (corner turret)', 'kind': 'wall', 'color': CASTLE, 'height': 2.5},
    'U': {'name': 'Refined Wood Block (lamp post)', 'kind': 'block', 'color': WOOD, 'height': 2},
    'l': {'name': 'Yellow Luminescent Block (lamp)', 'kind': 'block', 'color': '#bd9a5f', 'height': 0.5},
    'N': {'name': 'Refined Wood Block (banner pole)', 'kind': 'block', 'color': WOOD, 'height': 4},
    'e': {'name': 'Flower Soil', 'kind': 'floor', 'color': '#a77e63'},
})
P, R, zone, put = A.P, A.R, A.zone, A.put
stl = A.level('stilts', 'Stilts and foundations, standing on the lake bed (-4 m)', -4, 12)
lake = A.level('lake', 'Lake (water level, 0 m)', 0, 1)
dock = A.level('dock', 'Main dock, its edge (+1 m)', 1, 3)
walk = A.level('walk', 'Causeway, gatehouse ground floor, landing (+3 m)', 3, 4)
gate = A.level('gate', 'Gatehouse: the portcullis wall in the arch (+3 m)', 3, 6)
mid = A.level('mid', 'Arena, its edge (+4 m)', 4, 4)
g7 = A.level('g7', 'Gatehouse first floor: the towers (+7 m)', 7, 4)
g11 = A.level('g11', 'Gatehouse second floor: towers, wall-walk (+11 m)', 11, 4)
arms = A.level('arms', "Wall-walk: the cap over the town's arms (+13.5 m)", 13.5, 2)
top15 = A.level('top15', 'West tower: the fighting platform (+15 m)', 15, 2)
roof15 = A.level('roof15', 'East tower: the watch room roof (+15 m)', 15, 6)
shelter6 = A.level('shelter6', 'Landing: the shelter roof (+6 m)', 6, 3)
lamp5 = A.level('lamp5', 'Lamps on the causeway posts (+5 m)', 5, 1)
galb = A.level('galb', 'East tower: the gallery brackets (+10.5 m)', 10.5, 1)
gal14 = A.level('gal14', 'East tower: the gallery roof (+14 m)', 14, 2)
caps175 = A.level('caps175', 'West tower: the turret caps (+17.5 m)', 17.5, 3)
lantern = A.level('lantern', 'East tower: the watch lantern (+18.5 m)', 18.5, 1.5)
lantcap = A.level('lantcap', 'East tower: the lantern cap (+20 m)', 20, 2)
flag19 = A.level('flag19', "West tower: the town's flag (+19 m)", 19, 2)
cartload = A.level('cartload', "Landing: the trader's cart, its load (+3 m)", 3, 2)
# spiral stairs, a storey a level: the west tower's to its platform, the east tower's to its watch room
SPIRALS = {'w': (3, 7, 11), 'e': (3, 7)}
spirals = {(t, s): A.level(f'{t}{s}', f"{'West' if t == 'w' else 'East'} tower: spiral stair (+{s} m)", s, 4)
           for t, ss in SPIRALS.items() for s in ss}

# ================================================================= the lake and the shore
# The layout's ground: the lake bed 4 m down, shelving up to a beach under the gatehouse, banks up to the
# meadow at +3 m. The meadow comes up to the towers' land side, and the forecourt between them is on it.
def shoreline(x):
    return 140 + 2 * math.sin(x / 21) + 1.2 * math.sin(x / 8.3 + 1.3)


def ground(x, y):
    s = shoreline(x)
    if y < s:
        return -min(4, max(1, round((s - y) / 1.5)))
    return min(3, 1 + math.floor((y - s) / 3))


P.ground_fn(lambda mx, my: ground(mx + OX, my + OY))
P.ground_rect(60 - OX, 142 - OY, 100 - OX, 160 - OY, 3, 'max')
P.ground_rect(74 - OX, 139 - OY, 86 - OX, 142 - OY, 3, 'max')
for x, y in P.cells_rect(0, 0, 44, 62):
    if P.ground_at(x, y) < 0:
        lake[y][x] = '~'

# ================================================================= the causeway (+3 m)
# 6 m of rough wood with a wooden railing just outside each edge (the walkway style), from the square's stair
# (its blueprint, to y 100) south to the drawbridge
R(walk, 77, 100, 83, 131, 'w')
A.rail(walk, 76.5, 100, 77, 131, [(110, 116)]); A.rail(walk, 83, 100, 83.5, 131, [(118, 124)])
zone('walk', 'Causeway', 77, 100, 83, 131, '#2f8f8a')
# lamp posts in the railings, lamps on top (+5 m); the last pair flanks the drawbridge
for x0, y0 in ((76.5, 104), (76.5, 120), (76.5, 130), (83, 104), (83, 112), (83, 130)):
    R(walk, x0, y0, x0 + 0.5, y0 + 0.5, 'U'); R(lamp5, x0, y0, x0 + 0.5, y0 + 0.5, 'l')
# the branch west to the arena: a strip and a stair up 1 m to its east landing (stone cheeks)
R(walk, 74, 110, 77, 116, 'w')
A.rail(walk, 74, 109.5, 76.5, 110); A.rail(walk, 74, 116, 76.5, 116.5)
A.stairs('walk', 'Stairs up to the arena', 72, 110, 74, 116, 1, 'W')
A.cheeks(walk, 72, 110, 74, 116, 'W')
# the strip east for the main dock's stair (the main dock's blueprint)
R(walk, 83, 118, 84, 124, 'w')
# the drawbridge over the moat between the towers' prows: tarred planks banded with iron, hinged at the arch,
# its chains from the far corners up to the arch's face, over the arch (the winch is on the wall-walk)
R(walk, 77, 131, 83, 135, 'D')
R(walk, 77, 132, 83, 132.5, 'J'); R(walk, 77, 133.5, 83, 134, 'J')               # iron bands across the planks
CHAIN = (0.5, 1.5, 2.5, 3, 4, 5, 6, 6.5, 7.5)            # the chain's course, from the far end up to the arch
for i in range(8):
    for x in (77, 82.5):
        A.overlay(walk, x, 131 + i * 0.5, x + 0.5, 131.5 + i * 0.5, 'Iron Block (drawbridge chain)', '#848483', CHAIN[i + 1] - CHAIN[i], CHAIN[i])
zone('walk', 'Drawbridge (lifts against the arch)', 77, 131, 83, 135, '#75726e')

# ================================================================= the gatehouse (castle stone, +3 m)
# Two towers either side of an open arch: the towers 8 x 9 m, the arch between them 4 m deep, so the towers
# stand 2 m proud of it over the moat and 3 m proud of it on the land side, round a forecourt
TOWERS = (('w', 66, 74, 68.5), ('e', 86, 94, 91.5))
CENTRE = (74, 135, 86, 139)                               # the arch block between the towers
# the forecourt between the towers' land ends, on the meadow; the path straight down the middle, from the
# drawbridge through the arch and the forecourt, over the landing to the shore road
R(walk, 74, 139, 86, 142, 'C')
R(walk, 77, 135, 83, 152, 'q')
zone('walk', 'Forecourt (both towers overlook it)', 74, 139, 86, 142, '#75726e')
# the arch: castle piers either side of an opening 6 m wide, fancy stone jambs, a stepped arch of fancy stone
# on both faces (castle between them) up to its crown at +10.5 m, with a keystone; the wall-walk on top
R(walk, 74, 135, 77, 139, 'M'); R(walk, 83, 135, 86, 139, 'M')
for x in (76.5, 83):
    for y in (135, 138.5):
        R(walk, x, y, x + 0.5, y + 0.5, 'j')
ARCH = ((77, 6, 1.5), (77.5, 6.5, 1), (78, 7, 0.5), (81.5, 7, 0.5), (82, 6.5, 1), (82.5, 6, 1.5))   # x, base, height
for x, b, h in ARCH:
    for y0, y1 in ((135, 135.5), (138.5, 139)):
        A.overlay(walk, x, y0, x + 0.5, y1, 'Fancy Stone Block (arch ring)', STONE, h, b)
    A.overlay(walk, x, 135.5, x + 0.5, 138.5, 'Castle Block (arch)', CASTLE, h, b)
for y0, y1 in ((135, 135.5), (138.5, 139)):
    A.overlay(walk, 79.5, y0, 80.5, y1, 'Fancy Stone Block (keystone)', STONE, 0.5, 7)
zone('walk', 'Gate arch', 77, 135, 83, 139, '#75726e')
# the gate: two steel portcullises side by side (each 6 m tall and 3 m wide) in a wall just inside the arch's
# land face, so the arch frames them
R(gate, 77, 138, 83, 138.5, 'g')
A.door('gate', 'Steel Portcullis', 77, 138, 80, 138.5)
A.door('gate', 'Steel Portcullis', 80, 138, 83, 138.5)
for it in P.items:                                      # steel grey, not the planner's wooden door colour
    if it['type'] == 'steel-portcullis':
        it['color'] = '#848483'
# the wall-walk on the arch between the towers: castle floor, merlons on both sides
R(g11, 74, 135, 86, 139, 'C')
for y in (135, 138.5):
    A.parapet(g11, 74, y, 86, y + 0.5, every=2, wall='p', pier='o')
zone('g11', 'Wall-walk', 74, 135, 86, 139, '#75726e')

# ---- the towers: three storeys of castle block, 8 x 9 m, a spiral stair in the back corner, a door onto the
# landing, a door onto the wall-walk
for t, x0, x1, sx in TOWERS:
    for g in (walk, g7, g11):
        A.walls(g, x0, 133, x1, 142, 'K', 'r' if g is not walk else 'C')
    for s in SPIRALS[t]:                                # the spiral, one storey a level, the floor above cut away
        A.spiral(spirals[(t, s)], sx, 135.5, 3, 4, f"{'West' if t == 'w' else 'East'} tower stair", STONE, start=180)
    for g in (g7, g11):
        A.circle(g, sx, 135.5, 3, ' ')
    A.door('walk', 'Wooden Door', (x0 + x1) / 2 - 1, 141.5, (x0 + x1) / 2 + 1, 142)
    wx = x1 - 0.5 if t == 'w' else x0                   # the wall shared with the wall-walk
    A.door('g11', 'Wooden Door', wx, 136, wx + 0.5, 138)         # (a metre clear of the merlons)
    zone('walk', f"{'West' if t == 'w' else 'East'} gate tower", x0, 133, x1, 142, '#5f6770')
# the east tower's top: the watch room's slate pyramid, cut flat for the watch lantern (the west tower's top,
# a fighting platform, is with the character below)
rw = A.roof(roof15)
rw.hip(86, 133, 94, 142, 'castle', pitch=1.0, overhang=0.5, ridge_h=3.5)
rw.paint()

# ================================================================= the gatehouse's character
def ring_trim(g, x0, y0, x1, y1, ch, every=1):
    """Paint ch on the 0.5 m ring just outside x0..x1, y0..y1 wherever the level is empty (every n-th square),
    leaving out the arch block between the towers."""
    k = 0
    for x, y in P.cells_rect(x0 - 0.5 - OX, y0 - 0.5 - OY, x1 + 0.5 - OX, y1 + 0.5 - OY):
        mx, my = OX + x / 2, OY + y / 2
        if x0 <= mx < x1 and y0 <= my < y1:
            continue
        k += 1
        if CENTRE[0] <= mx < CENTRE[2] and CENTRE[1] <= my < CENTRE[3]:
            continue
        if g[y][x] == ' ' and k % every == 0:
            g[y][x] = ch


def cross_slit(g, x, y, along):
    """A cross-shaped arrow slit: a gap 1.5 m tall in the wall square at x, y, a short one either side."""
    R(g, x, y, x + 0.5, y + 0.5, 'Y')
    for d in (-0.5, 0.5):
        ax, ay = (x + d, y) if along == 'x' else (x, y + d)
        R(g, ax, ay, ax + 0.5, ay + 0.5, 'y')


# arrow slits: in the ground floors' outer walls, and on both floors of the towers' inner walls, covering the
# forecourt in front of the portcullis
cross_slit(walk, 66, 137, 'y'); cross_slit(walk, 71.5, 133, 'x')               # west tower
cross_slit(walk, 93.5, 137, 'y'); cross_slit(walk, 88.5, 133, 'x')             # east tower
cross_slit(walk, 73.5, 140, 'y'); cross_slit(g7, 73.5, 140, 'y'); cross_slit(g7, 86, 140, 'y')
# windows upstairs; the porter's window onto the forecourt; stone hoods over the tower doors onto the landing
for g in ('g7', 'g11'):
    A.win(g, 'Wooden Window Frame', 66, 137, 66.5, 138, 1)                      # west tower, west face
    A.win(g, 'Wooden Window Frame', 67, 141.5, 68, 142, 1)                      # west tower, south face
A.win('g11', 'Wooden Window Frame', 71, 133, 72, 133.5, 1)
A.win('g7', 'Wooden Window Frame', 93.5, 137, 94, 138, 1)                       # east tower
for g in ('g7', 'g11'):
    A.win(g, 'Wooden Window Frame', 89.5, 141.5, 90.5, 142, 1)
A.win('g11', 'Wooden Window Frame', 88, 133, 89, 133.5, 1)                      # the watch room: windows all round
for y in (134.5, 140):
    A.win('g11', 'Wooden Window Frame', 93.5, y, 94, y + 1, 1)
A.win('walk', 'Wooden Window Frame', 86, 139.5, 86.5, 140.5, 1)                 # the porter's window
for x in (69, 89):
    A.overlay(walk, x, 142, x + 2, 142.5, 'Fancy Stone Block (door hood)', STONE, 0.5, 2.5)
# murder holes in the wall-walk's floor, over the arch's crown
for x in (79, 80.5):
    R(g11, x, 137, x + 0.5, 137.5, ' ')
# red banners on both faces of the arch block, one on each pier; the town's arms in the parapet over the gate
for x in (75, 84):
    for y in (134.5, 139):
        R(g7, x, y, x + 1, y + 0.5, P._alloc({'name': 'Red Carpet Block (banner)', 'kind': 'block', 'color': '#9e3742', 'height': 3, 'base': 0.5}))
frame = P._alloc({'name': "Fancy Stone Block (the town's arms, frame)", 'kind': 'block', 'color': STONE, 'height': 2.5})
R(g11, 78.5, 138.5, 79, 139, frame); R(g11, 81, 138.5, 81.5, 139, frame)
R(g11, 79, 138.5, 81, 139, P._alloc({'name': "Red Marble Block (the town's arms)", 'kind': 'block', 'color': '#643f43', 'height': 2.5}))
for x0, x1, h in ((78.5, 81.5, 0.5), (79, 81, 1), (79.5, 80.5, 1.5)):            # a stepped stone cap over them
    R(arms, x0, 138.5, x1, 139, P._alloc({'name': "Fancy Stone Block (cap over the arms)", 'kind': 'block', 'color': STONE, 'height': h}))
# stone string courses round the towers at each floor, to break up their height
for _, x0, x1, _ in TOWERS:
    for g in (g7, g11):
        ring_trim(g, x0, 133, x1, 142, 'F')
# the west tower's top: the parapet carried 0.5 m out on corbels (machicolations), merlons, a little round
# turret with a slate cone at each corner, the town's flag on a pole
R(top15, 66, 133, 74, 142, 'C'); A.circle(top15, 68.5, 135.5, 3, ' ')
ring_trim(top15, 66, 133, 74, 142, 'o', every=2)               # merlons, the parapet between them
ring_trim(top15, 66, 133, 74, 142, 'p')
corbel = P._alloc({'name': 'Castle Block (corbel)', 'kind': 'block', 'color': CASTLE, 'height': 0.5, 'base': 3.5})
ring_trim(g11, 66, 133, 74, 142, corbel, every=2)
rt = A.roof(caps175)
for (cx, cy) in ((66, 133), (74, 133), (66, 142), (74, 142)):
    A.circle(top15, cx, cy, 2, 'T')
    rt.cone(cx, cy, 1, 2, 'castle', overhang=0.5)
rt.paint()
R(top15, 71.5, 139.5, 72, 140, P._alloc({'name': 'Refined Wood Block (flagpole)', 'kind': 'block', 'color': WOOD, 'height': 6}))
R(flag19, 72, 139.5, 74, 140, P._alloc({'name': "Red Carpet Block (the town's flag)", 'kind': 'block', 'color': '#9e3742', 'height': 1.5}))
# the east tower: a timber lookout gallery on its harbour side off the watch room, on brackets, under a
# little roof; the watch lantern on its pyramid, lit for arrivals at night
R(g11, 94, 136, 95.5, 140, 'r')
A.rail(g11, 95, 136, 95.5, 140); A.rail(g11, 94, 136, 95, 136.5); A.rail(g11, 94, 139.5, 95, 140)
A.door('g11', 'Wooden Door', 93.5, 137, 94, 139)
for y in (136, 139.5):
    R(galb, 94, y, 94.5, y + 0.5, P._alloc({'name': 'Refined Wood Block (gallery bracket)', 'kind': 'block', 'color': WOOD, 'height': 0.5}))
rg = A.roof(gal14)
rg.shed(94, 136, 95.5, 140, 'w', 'lead', pitch=1.0, overhang=0.5)
rg.paint()
post = P._alloc({'name': 'Refined Wood Block (lantern post)', 'kind': 'block', 'color': WOOD, 'height': 1.5})
for (x, y) in ((89, 136.5), (90.5, 136.5), (89, 138.5), (90.5, 138.5)):
    R(lantern, x, y, x + 0.5, y + 0.5, post)
R(lantern, 89.5, 137, 90.5, 138.5, P._alloc({'name': 'Yellow Luminescent Block (the watch light)', 'kind': 'block', 'color': '#bd9a5f', 'height': 1}))
rl = A.roof(lantcap)
rl.hip(88.5, 136, 91.5, 139.5, 'castle', pitch=1.0, overhang=0)
rl.paint()
# the wall-walk: the drawbridge winch (a drum on a frame) over the bridge, the warning bell in a timber frame
# by the watch tower's door, braziers either side of the arms
for x in (77.5, 82):
    A.overlay(g11, x, 135.5, x + 0.5, 136.5, 'Refined Wood Block (winch frame)', WOOD, 2, 0)
A.overlay(g11, 78, 135.5, 82, 136.5, 'Refined Wood Block (drawbridge winch drum)', WOOD, 1, 0.5)
zone('g11', 'Drawbridge winch', 77.5, 135.5, 82.5, 136.5, '#75726e')
for x in (83, 84.5):
    A.overlay(g11, x, 135.5, x + 0.5, 136.5, 'Refined Wood Block (bell frame)', WOOD, 2.5, 0)
A.overlay(g11, 83.5, 135.5, 84.5, 136.5, 'Bronze Block (the warning bell)', '#8b7852', 1, 1)
put('g11', 'Brazier', 77.5, 137.5); put('g11', 'Brazier', 81.5, 137.5)

# ---- inside
# the west tower: the guardroom (a bunk for the night watch, a table, a rack, a chest), the armoury above, the
# arrow store at the top
put('walk', 'bed', 66.5, 138.5, label='Bed (the night watch)')
put('walk', 'table', 69.5, 138); put('walk', 'Rustic Chair', 69.5, 139, 180); put('walk', 'Rustic Chair', 70.5, 139, 180)
put('walk', 'Sword and Shield Rack', 73, 134, 90); put('walk', 'chest-large', 71, 134)
put('walk', 'Hanging Lantern', 72, 140)
put('g7', 'Two-Handed Melee Weapon Rack', 73, 134, 90); put('g7', 'Staff Weapon Rack', 66.5, 138, 270)
put('g7', 'Bow Weapon Rack', 70.5, 141, 180); put('g7', 'chest-large', 70.5, 134)
put('g7', 'Hanging Lantern', 71, 138, z=3)
put('g11', 'Supply Sacks I', 71, 134, label='Supply Sacks I (arrows)'); put('g11', 'Scrappy Crate', 72.5, 134)
put('g11', 'Supply Sacks II', 66.5, 139.5, label='Supply Sacks II (bolts)')
# the east tower: the porter's lodge (a counter at his window onto the forecourt, a chair, a chest), the
# gatekeeper's quarters above, the watch room at the top
put('walk', 'Wooden Tavern Counter', 86.5, 139, 90); put('walk', 'Rustic Chair', 87.5, 139.5, 90)
put('walk', 'chest-medium', 92, 139); put('walk', 'Hanging Lantern', 88.5, 137)
zone('walk', "Porter's lodge", 86.5, 133.5, 93.5, 141.5, '#5f6770')
put('g7', 'bed', 88, 138, label='Bed (the gatekeeper)'); put('g7', 'Crude Wooden Closet', 92.5, 139, 90)
put('g7', 'chest-small', 91, 140.5); put('g7', 'Hanging Lantern', 90, 139.5, z=3)
zone('g7', "Gatekeeper's quarters", 86.5, 133.5, 93.5, 141.5, '#5f6770')
put('g11', 'table', 88, 138); put('g11', 'Rustic Chair', 88, 139, 180); put('g11', 'Rustic Chair', 89, 139, 180)
put('g11', 'chest-small', 87, 134); put('g11', 'Hanging Lantern', 89, 140, z=3)
zone('g11', 'Watch room', 86.5, 133.5, 93.5, 141.5, '#5f6770')
zone('g7', 'Armoury', 66.5, 133.5, 73.5, 141.5, '#5f6770')
# lived in: the guards' jug and cups on the guardroom table and a brazier for the night watch; the gatekeeper's
# dog in the porter's lodge, his cup on the counter; a side table and a mat by the gatekeeper's bed; the
# watchmen's jug on the watch room table
put('walk', 'Crude Wooden Jug', 70, 138, z=1); put('walk', 'Wooden Cup', 70.5, 138, z=1); put('walk', 'Wooden Cup', 71, 138.5, z=1)
put('walk', 'Brazier', 72, 137)
put('walk', 'Dog Pillow', 87, 134, label="Dog Pillow (the gatekeeper's dog)"); put('walk', 'Dog Bowl', 88.5, 134.5)
put('walk', 'Wooden Cup', 87, 140.5, z=1)
put('g7', 'Wooden Side Table', 87, 138); put('g7', 'Wooden Cup', 87, 138, z=1); put('g7', 'Straw Mat', 90, 138)
put('g11', 'Crude Wooden Jug', 88.5, 138, z=1); put('g11', 'Wooden Cup', 89.5, 138.5, z=1)
# the forecourt: lanterns either side of the gate, a bench under the west tower for those waiting to be let in
put('walk', 'Wall Lantern', 76, 139, 0, 3.0); put('walk', 'Wall Lantern', 83.5, 139, 0, 3.0)
put('walk', 'Bench', 74, 140, 270)
# the wall-walk: a heap of stones by the murder holes, a bucket of water
A.overlay(g11, 79.5, 137, 80.5, 137.5, 'Rough Stone Block (stones for the murder holes)', RS, 0.5, 0)
put('g11', 'Scrap Bucket', 81.5, 136.5, label='Scrap Bucket (water)')
zone('walk', 'Guardroom', 66.5, 133.5, 73.5, 141.5, '#5f6770')

# ================================================================= the shore landing (+3 m, on the meadow)
# Grass up to the towers, a paved landing in front of them (the path down its middle), the shore road south
# to the build area's edge, a shelter for arrivals on posts under a thatched roof
R(walk, 60, 142, 100, 158, 'G')
R(walk, 66, 142, 94, 146, 'c'); R(walk, 70, 146, 90, 152, 'c')
R(walk, 77, 142, 83, 152, 'q')
R(walk, 77, 152, 83, 158, 'd')
for (x, y) in ((62, 147), (67.5, 147), (62, 150.5), (67.5, 150.5)):
    R(walk, x, y, x + 0.5, y + 0.5, 'n')
put('walk', 'Bench', 63, 147.5); put('walk', 'Bench', 65, 147.5)
rs = A.roof(shelter6)
rs.gable(62, 147, 68, 151, 'x', 'straw', pitch=1.0, overhang=0.5)
rs.paint()
put('walk', 'Scrap Vat I', 66.5, 149.5, label='Scrap Vat I (water)'); put('walk', 'Scrappy Crate', 63, 149.5)
put('walk', 'Hanging Lantern', 64.5, 149, z=2.5)
# a trader's handcart left on the verge by the trough, waiting to be let in: two wheels, the bed, its shafts
# down on the grass, crates and a bale of straw on it
for x in (91, 93):
    A.overlay(walk, x, 147.5, x + 0.5, 148.5, 'Tarred Wood Block (cart wheel)', TAR, 1, 0)
A.overlay(walk, 91.5, 147, 93, 149.5, 'Refined Wood Block (cart bed)', WOOD, 0.5, 0.5)
for x in (91.5, 92.5):
    A.overlay(walk, x, 149.5, x + 0.5, 150, 'Refined Wood Block (cart shafts)', WOOD, 0.5, 0.5)
    A.overlay(walk, x, 150, x + 0.5, 151, 'Refined Wood Block (cart shafts)', WOOD, 0.5, 0)
R(cartload, 91.5, 147, 92.5, 148, P._alloc({'name': 'Refined Wood Block (crates on the cart)', 'kind': 'block', 'color': '#8c6b4f', 'height': 1, 'base': 1}))
R(cartload, 92.5, 148, 93, 149, P._alloc({'name': 'Straw Roof Block (a bale of straw on the cart)', 'kind': 'block', 'color': '#a7753d', 'height': 0.5, 'base': 1}))
zone('walk', "Trader's cart", 91, 147, 93.5, 151, '#8c7455')
# banner poles either side of the road up to the gate, a red banner on each
for (x, bx) in ((76, 75.5), (83.5, 84)):
    for y in (152.5, 156):
        R(walk, x, y, x + 0.5, y + 0.5, 'N')
        A.overlay(walk, bx, y, bx + 0.5, y + 0.5, 'Red Carpet Block (banner)', '#9e3742', 1.5, 2)
put('walk', 'trough', 85.5, 147.5, label='Trough (water for arrivals)')
A.overlay(walk, 72, 146.5, 72.5, 147, 'Refined Wood Block (notice board post)', WOOD, 2, 0)
A.overlay(walk, 74, 146.5, 74.5, 147, 'Refined Wood Block (notice board post)', WOOD, 2, 0)
A.overlay(walk, 72.5, 146.5, 74, 147, 'Tarred Wood Block (notice board)', TAR, 1.5, 0.5)
A.overlay(walk, 84, 157, 84.5, 157.5, 'Rough Stone Block (milestone: Laketown)', RS, 1, 0)
R(walk, 70, 150, 72, 152, 'e'); R(walk, 88, 150, 90, 152, 'e')
put('walk', 'Ground Lantern II', 70.5, 151); put('walk', 'Ground Lantern II', 89, 151)
zone('walk', 'Shore landing (arrivals)', 60, 142, 100, 158, '#8c7455')
zone('walk', 'Waiting shelter', 62, 147, 68, 151, '#8c7455')

# ================================================================= the neighbours' edges (their own blueprints)
R(walk, 77, 98, 83, 100, 'w')                           # the square's end of the causeway
zone('walk', 'Causeway, its north end (square blueprint)', 77, 98, 83, 100, '#2f8f8a')
A.circle(mid, 59, 113, 26, 'k'); R(mid, 69.5, 110, 72, 116, 'k')               # the arena's stands and east landing
zone('mid', 'Arena (bathhouse and arena blueprint)', 58, 100, 72, 126, '#c2416e')
R(dock, 84, 114, 102, 132, 't')                         # the main dock and its stair up
A.stairs('dock', 'Stairs down to the main dock (main dock blueprint)', 84, 118, 88, 124, 2, 'W')
zone('dock', 'Main dock (main dock blueprint)', 84, 114, 102, 132, '#2f7fb3')

# ================================================================= stilts, foundations, rim beams and checks
print('stilts:', A.stilts(stl, [('dock', 1), ('walk', 3), ('mid', 4)]))
posts = {c for row in stl for c in row if c != ' '}


def in_gatehouse(mx, my):
    return (66 <= mx < 94 and 133 <= my < 142 and not (74 <= mx < 86 and not 135 <= my < 139))


# The gatehouse stands on stone, not stilts: a foundation wall round the towers and the arch block, from the
# lake bed to the floor, and a battered base 0.5 m out at the foot where it stands in the water (to +1 m).
# The drawbridge has no posts under it, so it can lift.
for x, y in P.cells_rect(0, 0, 44, 62):
    mx, my = OX + x / 2, OY + y / 2
    if in_gatehouse(mx, my) or (77 <= mx < 83 and 131 <= my < 135):
        stl[y][x] = ' '
n_found = n_batter = 0
for x, y in P.cells_rect(0, 0, 44, 62):
    mx, my = OX + x / 2, OY + y / 2
    near = [in_gatehouse(mx + dx, my + dy) for dx in (-0.5, 0, 0.5) for dy in (-0.5, 0, 0.5)]
    if in_gatehouse(mx, my) and not all(near):
        stl[y][x] = 'h'; n_found += 1
    elif not in_gatehouse(mx, my) and any(near) and P.ground_at(x, y) < 0.5:
        stl[y][x] = 'b'; n_batter += 1
print('foundation squares:', n_found, ' battered base squares:', n_batter)
buried = 0                                              # no posts where the deck sits on the ground
for y in range(P.H):
    for x in range(P.W):
        if stl[y][x] in posts and P.ground_at(x, y) >= 2.5:
            stl[y][x] = ' '; buried += 1
print('posts left out on the ground:', buried)
own = lambda x, y: ((76.5 <= x < 83.5 and 100 <= y < 135) or (72 <= x < 77 and 109.5 <= y < 116.5) or (83 <= x < 84 and 118 <= y < 124)
                    or (66 <= x < 94 and 133 <= y < 146))
print('rim beam squares:', A.rim_beams(stl, [('walk', 3)], lambda x, y: own(x, y) and P.ground_at(*A.sq(x, y)) < 2.5))
A.spawn('walk', 79.5, 151, 180)                                 # walk mode starts here: the shore landing, facing the gate
A.checks()

NOTES = """Laketown: the causeway, the gatehouse and the shore landing, as a 0.5 m detail blueprint. Pass 3 of 3 (review and finishing touches): done. Drafted by Claude.
This plan's corner is the layout's (58, 98), so it lines up with the Laketown layout and stamps back into the site plan there.

PASSES
1. Design and bones: the causeway and its branches, the drawbridge, the gatehouse's shells with floors, doors, spiral stairs and tops, the landing and the shelter, stilts, labels.
2. Details: character for a big blocky building (string courses, arrow slits, corbelled parapet and turrets, the flag, the watch lantern and gallery, banners, the town's arms, murder holes, the winch, the bell), the rooms, lamps, the landing's furniture. Then a 3D review and a refining round. Then, at the user's ask, the plan reshaped so it isn't one big rectangle: the enclosed gate passage and the gate hall over it became an open arch between the towers, shallower than they are, closed by two steel portcullises, with a path straight through.
3. Review and finishing touches (done): lanterns either side of the gate, a bench in the forecourt, the guards' and watchmen's jugs and cups, a brazier in the guardroom, the gatekeeper's dog, his cup and side table, stones and a bucket on the wall-walk, a lantern in the shelter, a trader's handcart waiting by the trough; the layout's gatehouse redrawn as built; the hand-off for the main dock.

THE CAUSEWAY (+3 m): 6 m of rough wood with a wooden railing just outside each edge (the walkway style), lamp posts in the railings, from the square's stair (y 100) south to the drawbridge.
- West, a branch to the arena: a strip and a stair up 1 m (stone cheeks) to the arena's east landing (the bathhouse and arena blueprint's hand-off).
- East, a strip for the main dock's stair down (the main dock's blueprint).
- The drawbridge (y 131..135) spans the moat between the towers' prows: tarred planks with iron bands across them, hinged at the arch, with no posts under it so it can lift. Iron chains run from its far corners up to the arch's face, to the winch on the wall-walk.

THE GATEHOUSE (castle stone, +3 m): two towers either side of an open arch, straddling the waterline. The arch block is 4 m deep against the towers' 9 m, so the towers stand 2 m proud of it over the moat and 3 m proud of it on the land side, round a forecourt. The towers and the arch stand on a stone foundation from the lake bed, battered out 0.5 m at the foot where it's in the water.
- The arch: 6 m wide, its crown at +10.5 m, between castle piers with fancy stone jambs. A stepped arch of fancy stone on both faces, castle between them, and a keystone.
- The gate: two Steel Portcullises side by side (6 m tall and 3 m wide each, the user's measurement), in a wall just inside the arch's land face so the arch frames them.
- The path: rocky stone road straight down the middle, from the drawbridge through the arch and the forecourt, over the landing to the shore road.
- The forecourt (castle paving either side of the path): covered by cross-shaped arrow slits in both towers' inner walls, and the porter's window.
- Red banners hang on both faces of the arch block, one on each pier.
- The wall-walk on the arch (+11 m): merlons along both sides, doors into both towers, the drawbridge winch (a drum on a frame) over the bridge, the warning bell in a timber frame by the watch tower's door, braziers, murder holes over the arch's crown. The town's arms (red marble in a fancy stone frame, a stepped stone cap) rise from the parapet over the gate.
- The towers, 8 x 9 m, three storeys (+3, +7, +11 m), a stone spiral stair in each back corner, a door onto the landing under a stone hood, a door onto the wall-walk, fancy stone string courses round them at each floor, cross-shaped arrow slits on the ground floor, windows above.
  - The west tower, the fighting tower: the guardroom (a bunk for the night watch, a table and chairs, a rack, a chest), the armoury above (racks for two-handed weapons, staves and bows), the arrow store at the top. Its top (+15 m) is the fighting platform: the parapet carried 0.5 m out on corbels, merlons, a little round turret at each corner under a slate cone, and the town's red flag on a pole.
  - The east tower, the watch tower: the porter's lodge (his counter at the window onto the forecourt, a chair, a chest), the gatekeeper's quarters above (bed, wardrobe, chest), the watch room at the top with windows all round and a timber lookout gallery on its harbour side, on brackets under a little roof. Its slate pyramid is cut flat for the watch lantern, a light on four posts under a little slate cap, for arrivals at night.

THE SHORE LANDING (+3 m, on the meadow): grass up to the towers, a paved landing (field stones) in front of them with the path down its middle, the shore road (dirt) south to the build area's edge between banner poles (red banners), flower beds and lanterns at the landing's corners, a trough for arrivals, a notice board, a milestone; the waiting shelter on posts under a thatched roof, with benches, a water barrel and a crate.

CONNECTIONS
- North: the square's stair down to the causeway (its blueprint) at y 96..98; the causeway carries on from y 100.
- West: the arena's east landing (x 69.5..72, +4 m), up the branch's stair.
- East: the main dock's stair (x 84..88, y 118..124), down from the strip.
- South: the shore road, the way in from the land.

HAND-OFF FOR THE MAIN DOCK (area 8):
- Its stair up to the causeway: x 84..88, y 118..124, rising 2 m west from the dock (+1 m) to the causeway's strip (x 83..84, +3 m), where the east railing has its gap. The causeway's lamp posts are in that railing at y 104, 112 and 130.
- The dock's south edge (y 132) runs 1 m from the east tower's prow (y 133). The tower stands on a stone foundation with a battered base 0.5 m out to +1 m, so keep the dock's edge at y 132 or short of it, and keep its south-west corner (x 84..86) out of the moat (x 74..86, y 132..135, open water under the drawbridge).
- The east tower's ground floor (the porter's lodge) is 2 m above the dock and has no door that way. A watergate stair down from the lodge would need a door in its north wall, where the arrow slit is (x 88..89.5).
- The watch tower's gallery (+11 m, x 94..95.5) looks out over the dock and the harbour.

ARROW SLITS are gaps left in the wall (painted openings, no item: in game, leave the blocks out), cross-shaped: a slit 1.5 m tall with a short one either side.

SIZES: the Steel Portcullis is measured (6 m tall, 3 m wide); furniture, light, weapon rack and tableware sizes are estimates until measured. The trader's cart is built from blocks (there's no cart to place).

STILTS: 1 m posts on the layout's 4 m grid, from the lake bed 4 m down to each deck's underside, left out where the deck sits on the ground and under the gatehouse and the drawbridge; tarred rim beams under the edges over the water.
"""
A.save('laketown_gatehouse.json', NOTES, 'r-claude-laketown-gatehouse-4')
