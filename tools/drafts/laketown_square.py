"""Laketown: the main square, 0.5 m detail plan. Pass 3 of 3: review and finishing touches.

The square at +4 m with the Flame Altar on a raised dais, the market stalls and trader's stall in its north
corners, the storage halls in its south corners either side of the south entrance, the north promenade and
the grand stair up to the manor, and up a step either side of the promenade the tavern and the lodging house.
Pass 1 laid out the bones (decks, shells, partitions, doors, stairs, roofs, stilts); pass 1.5 reshaped the
roofs at 45 degrees; pass 2 adds the detail: balustrades and lamp piers, paving, the stair flanks, windows,
trim (plinths, quoins, corbels, a jettied upper floor, gable windows, a porch, a door hood, a balcony, a sign,
window boxes), stall counters, planters, lights, and the furniture and stations that matter (chests, beds,
hearths, the bar, the kitchen); pass 3 reviewed it all and finished it: connections to the neighbouring
areas (a side stair from the tavern to the west landing, the bathhouse deck, stone cheeks on every stair,
walkway railings in the style the next blueprints should follow), a gateway arch over the main entrance from
the causeway, rim beams under the deck edges, newel posts, a sign for the lodging house, and small fixes.

Coordinates are the layout's (doc `laketown`): this plan's corner is the layout's (54, 40), so it can be
stamped back into a site plan at that offset.
Run: python laketown_square.py  ->  writes laketown_square.json
"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mage_common import Plan, PALETTE, ROOF_MATS, ALTAR_W, ALTAR_D, ALTAR_H

OX, OY = 54, 40                                         # this plan's corner, in layout metres
STONE, WOOD = '#92908c', '#75675f'
PALETTE.clear()
PALETTE.update({                                        # catalogue names and colours (blocks.js)
    '~': {'name': 'Water', 'kind': 'water', 'color': '#3f6f8f'},
    'w': {'name': 'Rough Wood Block', 'kind': 'floor', 'color': '#7a6653'},           # walkways
    'r': {'name': 'Refined Wood Block', 'kind': 'floor', 'color': WOOD},              # floors indoors
    't': {'name': 'Tarred Wood Block', 'kind': 'floor', 'color': '#5d5652'},          # deck edges
    'h': {'name': 'Brick-Timbered Block', 'kind': 'floor', 'color': '#947f75'},       # the tavern and lodging decks
    'L': {'name': 'Limestone Road Block', 'kind': 'floor', 'color': '#a38b79'},       # the square's paving
    'f': {'name': 'Fancy Stone Block', 'kind': 'floor', 'color': STONE},              # the square's stone edge
    'S': {'name': 'Smooth Stone Road Block', 'kind': 'floor', 'color': '#746553'},    # the band round the dais, the paths
    'P': {'name': 'Highly Polished Stone Block', 'kind': 'floor', 'color': '#b3b0a9'},  # the dais, the manor
    'B': {'name': 'Fired Bricks Block', 'kind': 'wall', 'color': '#aa7657'},          # tavern, ground floor
    'T': {'name': 'Half-Timbered Block', 'kind': 'wall', 'color': '#71665e'},         # tavern, upper floor
    'Q': {'name': 'Refined Stone Block', 'kind': 'wall', 'color': '#84837e'},         # storage halls, lodging ground floor
    'K': {'name': 'Brick-Timbered Block', 'kind': 'wall', 'color': '#947f75'},        # lodging, upper floor
    # trim
    'G': {'name': 'Half-Timbered Block (gable, 5 m)', 'kind': 'wall', 'color': '#71665e', 'height': 5},
    'H': {'name': 'Brick-Timbered Block (gable, 5 m)', 'kind': 'wall', 'color': '#947f75', 'height': 5},
    'R': {'name': 'Refined Stone Block (gable, 6 m)', 'kind': 'wall', 'color': '#84837e', 'height': 6},
    'C': {'name': 'Fired Bricks Block (chimney)', 'kind': 'wall', 'color': '#aa7657', 'height': 14.5},
    'D': {'name': 'Refined Stone Block (chimney)', 'kind': 'wall', 'color': '#84837e', 'height': 12},
    'c': {'name': 'Fired Bricks Block (chimney cap)', 'kind': 'block', 'color': '#aa7657', 'height': 0.5, 'base': 2.5},
    'd': {'name': 'Refined Stone Block (chimney cap)', 'kind': 'block', 'color': '#84837e', 'height': 0.5},
    'z': {'name': 'Roughly Cut Stone Block (plinth)', 'kind': 'block', 'color': '#62605d', 'height': 0.5},
    'Z': {'name': 'Roughly Cut Stone Block (quoin)', 'kind': 'wall', 'color': '#62605d', 'height': 4},
    'b': {'name': 'Fancy Stone Block (balustrade)', 'kind': 'block', 'color': STONE, 'height': 1},
    'o': {'name': 'Fancy Stone Block (pier)', 'kind': 'block', 'color': STONE, 'height': 1.5},
    'O': {'name': 'Fancy Stone Block (lamp pier)', 'kind': 'block', 'color': STONE, 'height': 2},
    'X': {'name': 'Fancy Stone Block (gate pillar)', 'kind': 'block', 'color': STONE, 'height': 5},
    'l': {'name': 'Yellow Luminescent Block (lamp)', 'kind': 'block', 'color': '#bd9a5f', 'height': 0.5},
    '1': {'name': 'Fancy Stone Block (stair flank)', 'kind': 'wall', 'color': STONE, 'height': 2},
    '2': {'name': 'Fancy Stone Block (stair flank)', 'kind': 'wall', 'color': STONE, 'height': 3},
    '3': {'name': 'Fancy Stone Block (stair flank)', 'kind': 'wall', 'color': STONE, 'height': 4},
    '4': {'name': 'Fancy Stone Block (stair flank)', 'kind': 'wall', 'color': STONE, 'height': 5},
    # woodwork
    'p': {'name': 'Refined Wood Block (stall post)', 'kind': 'block', 'color': WOOD, 'height': 2.5},
    'v': {'name': 'Refined Wood Block (stall post)', 'kind': 'block', 'color': WOOD, 'height': 3},
    'k': {'name': 'Rough Wood Block (stall back)', 'kind': 'wall', 'color': '#7a6653', 'height': 3},
    'i': {'name': 'Refined Wood Block (rail, counter)', 'kind': 'block', 'color': WOOD, 'height': 1},
    'u': {'name': 'Refined Wood Block (newel post)', 'kind': 'block', 'color': WOOD, 'height': 1.5},
    'n': {'name': 'Refined Wood Block (porch post)', 'kind': 'block', 'color': WOOD, 'height': 3},
    'e': {'name': 'Refined Wood Block (balcony post)', 'kind': 'block', 'color': WOOD, 'height': 3.5},
    'x': {'name': 'Refined Wood Block (window box)', 'kind': 'block', 'color': WOOD, 'height': 0.5, 'base': 0.5},
    'j': {'name': 'Refined Wood Block (sign bracket)', 'kind': 'block', 'color': WOOD, 'height': 0.5, 'base': 2},
    'J': {'name': 'Tarred Wood Block (sign board)', 'kind': 'block', 'color': '#5d5652', 'height': 1.5, 'base': 1},
    # planting
    'F': {'name': 'Flower Soil (bed)', 'kind': 'block', 'color': '#a77e63', 'height': 0.5},
    'Y': {'name': 'Foliage (shrubs)', 'kind': 'block', 'color': '#668f27', 'height': 1},
})
ROOF_MATS['straw'] = ('Straw Roof Block', '#a7753d')
ROOF_MATS['tarstraw'] = ('Tarred Straw Block', '#3b4457')

P = Plan('Laketown: main square (detail)', 0.5, 58, 60, 160)
P.project = 'Laketown'
stl = P.level('stilts', 'Stilts, standing on the lake bed (-4 m)', -4, 13)
lake = P.level('lake', 'Lake (water level, 0 m)', 0, 1)
low = P.level('low', 'Bathhouse deck, its edge (+2 m)', 2, 4)
walk = P.level('walk', 'Walkways to the neighbours (+3 m)', 3, 4)
mid = P.level('mid', 'Main square, promenade, storage halls (+4 m)', 4, 4)
dais = P.level('dais', 'Altar dais (+4.5 m)', 4.5, 3)
up5 = P.level('up5', 'Tavern and lodging house, ground floor (+5 m)', 5, 4)
stage = P.level('stage', "Tavern: the Bard's stage (+5.5 m)", 5.5, 3.5)
lamp6 = P.level('lamp6', 'Lamps on the piers (+6 m)', 6, 1)
stallroof = P.level('stallroof', 'Market stall awnings (+6.5 m)', 6.5, 2)
hood = P.level('hood', "Lodging house: the door hood (+7.5 m)", 7.5, 2)
hallroof = P.level('hallroof', 'Storage hall roofs (+8 m)', 8, 5)
mnr = P.level('manor', 'Manor grounds, its edge (+8 m)', 8, 4)
porch8 = P.level('porch8', 'Tavern porch roof (+8 m)', 8, 3)
up9 = P.level('up9', 'Tavern and lodging house, upper floor (+9 m)', 9, 3)
roof12 = P.level('roof12', 'Tavern and lodging roofs (+12 m)', 12, 7)
caps = P.level('caps', 'Chimney caps (+16.5 m)', 16.5, 3)
LEV = {'mid': mid, 'up5': up5, 'up9': up9}


# ---- everything below is in layout metres
def R(g, x0, y0, x1, y1, ch):
    P.rect(g, x0 - OX, y0 - OY, x1 - OX, y1 - OY, ch)


def zone(lid, name, x0, y0, x1, y1, c):
    P.zone(lid, name, x0 - OX, y0 - OY, x1 - OX, y1 - OY, c)


def deck(g, x0, y0, x1, y1, ch, edge=None, w=1):
    R(g, x0, y0, x1, y1, edge or ch)
    if edge:
        R(g, x0 + w, y0 + w, x1 - w, y1 - w, ch)


def walls(g, x0, y0, x1, y1, ch, floor=None):
    """A building's outer walls, one block (0.5 m) thick, with a floor inside if given."""
    P.box_walls(g, x0 - OX, y0 - OY, x1 - OX, y1 - OY, ch, 0.5, floor)


def stairs(lid, label, x0, y0, x1, y1, rise, up):
    """Stairs over x0..x1, y0..y1 on the lower level, rising `rise` m towards `up`, no steeper than 45 degrees."""
    rot = {'N': 0, 'S': 180, 'E': 90, 'W': 270}[up]
    w, d = (x1 - x0, y1 - y0) if up in 'NS' else (y1 - y0, x1 - x0)
    assert d >= rise, (label, d, rise)
    P.item(lid, 'stairs', label, x0 - OX, y0 - OY, w, d, rise, rot, '#a98a62')


TALL = {'Wooden Door': 2.5, 'Round Wooden Door': 3, 'Wooden Double Door': 3.5}   # measured in game (blocks x 0.5)
WIN = {'Wooden Window Frame': 1.5, 'Round Wooden Window Frame': 1, 'Large Round Wooden Window Frame': 3}


def door(lid, name, x0, y0, x1, y1):
    P.opening(lid, name, x0 - OX, y0 - OY, x1 - OX, y1 - OY, TALL[name], 0, '#6b4a2e')


def win(lid, name, x0, y0, x1, y1, z=1.0):
    """A window item in the wall squares x0..x1, y0..y1, its sill z metres above the level floor."""
    P.opening(lid, name, x0 - OX, y0 - OY, x1 - OX, y1 - OY, WIN[name], z)


# Furniture and lights: real item names (the planner's catalogue types are their slugs). Sizes in metres
# (w along the front, d deep, h tall) are estimates until measured in game; the library's own (chests,
# stations, beds) come from the planner.
ITEM = {
    'Brazier': (1, 1, 1), 'Bench': (2, 0.5, 0.5), 'Ground Lantern II': (0.5, 0.5, 2), 'Wall Lantern': (0.5, 0.5, 0.5),
    'Hanging Lantern': (0.5, 0.5, 0.5), 'Supply Sacks I': (1, 1, 1), 'Supply Sacks II': (1, 1, 1),
    'Resource Bundle I': (1, 1, 1), 'Scrappy Crate': (1, 1, 1), 'Stone Fireplace': (2, 1, 1.5), 'Fireplace': (2, 1, 1.5),
    'Wooden Tavern Counter': (2, 1, 1), 'Wooden Banquet Table': (3, 1, 1), 'Rustic Chair': (1, 1, 1),
    'Wooden Sink': (2, 1, 1),
}
LIB = {   # library types: (name, w, d, h) as in the planner's LIBRARY
    'mchest-large': ('Large Magic Chest', 2, 1, 1), 'quickstack': ('Quick Stack Station', 1, 1, 2),
    'chest-small': ('Small Chest', 1, 1, 1), 'bed': ('Bed', 2, 3, 1), 'npc-bard': ('Bard', 3, 3, 2),
    'cooking-station': ('Cooking Station', 2, 2, 1.5), 'oven': ('Oven', 2, 2, 2), 'kitchen': ('Kitchen', 2, 2, 1.5),
}
MOUNT = {'Wall Lantern': 'wall', 'Hanging Lantern': 'ceiling'}
COL = {'wall': '#b08a4a', 'ceiling': '#c9a23a'}


def put(lid, name, x, y, rot=0, z=None, label=None):
    """A catalogue item (by its game name) or a library item (by type) at x, y: the top-left of its footprint,
    which is turned for rot 90 and 270. rot 0 faces south, 90 west, 180 north, 270 east."""
    if name in LIB:
        nm, w, d, h = LIB[name]
        typ, color, mount = name, '#7b68b5' if 'chest' in name else '#8c6b4f', None
    else:
        (w, d, h), nm, typ = ITEM[name], name, name.lower().replace(' ', '-')
        mount = MOUNT.get(name)
        color = COL.get(mount, '#8a7a6a')
    if mount == 'ceiling' and z is None:
        z = LEVEL_H[lid] - h
    return P.item(lid, typ, label or nm, x - OX, y - OY, w, d, h, rot, color, z=z, mount=mount)


LEVEL_H = {L['id']: L['height'] for L in P.levels}


def roof(g):
    rf = P.roof(g)

    class W:                                            # the Roof helper, in layout metres
        def gable(self, x0, y0, x1, y1, *a, **k): rf.gable(x0 - OX, y0 - OY, x1 - OX, y1 - OY, *a, **k)
        def hip(self, x0, y0, x1, y1, *a, **k): rf.hip(x0 - OX, y0 - OY, x1 - OX, y1 - OY, *a, **k)
        def lean_to(self, x0, y0, x1, y1, *a, **k): rf.lean_to(x0 - OX, y0 - OY, x1 - OX, y1 - OY, *a, **k)
        def cut(self, x0, y0, x1, y1): rf.cut(x0 - OX, y0 - OY, x1 - OX, y1 - OY)
        def caps(self, *a, **k): return rf.caps(*a, **k)
        def paint(self): rf.paint()
    return W()


def overlay(g, x0, y0, x1, y1, name, color, height, base):
    """A raised piece over each square of x0..x1, y0..y1, keeping the floor under it."""
    for x, y in P.cells_rect(x0 - OX, y0 - OY, x1 - OX, y1 - OY):
        P.overlay(g, x, y, name, color, height, base)


def balustrade(g, x0, y0, x1, y1, gaps=(), every=4):
    """A stone balustrade along a straight edge (0.5 m thick), with piers at its ends and about every `every`
    metres, leaving `gaps` (spans along the run) open."""
    horiz = (x1 - x0) >= (y1 - y0)
    a0, a1 = (x0, x1) if horiz else (y0, y1)
    seg = lambda a, b, ch: R(g, a, y0, b, y1, ch) if horiz else R(g, x0, a, x1, b, ch)
    pieces, cur = [], a0
    for (g0, g1) in sorted(gaps):
        if g0 > cur:
            pieces.append((cur, g0))
        cur = max(cur, g1)
    if cur < a1:
        pieces.append((cur, a1))
    for s0, s1 in pieces:
        seg(s0, s1, 'b')
        seg(s0, min(s0 + 1, s1), 'o'); seg(max(s1 - 1, s0), s1, 'o')
        n = int((s1 - s0) // every)
        for i in range(1, n):
            c = round((s0 + (s1 - s0) * i / n) * 2) / 2
            seg(c - 0.5, c + 0.5, 'o')


def rail(g, x0, y0, x1, y1, gaps=()):
    """A wooden railing (1 m) along a straight edge, leaving `gaps` open, with a newel post (1.5 m) at the
    ends of each piece."""
    horiz = (x1 - x0) >= (y1 - y0)
    a0, a1 = (x0, x1) if horiz else (y0, y1)
    seg = lambda a, b, ch: R(g, a, y0, b, y1, ch) if horiz else R(g, x0, a, x1, b, ch)
    cur = a0
    for (g0, g1) in sorted(gaps) + [(a1, a1)]:
        if g0 > cur:
            seg(cur, g0, 'i'); seg(cur, cur + 0.5, 'u'); seg(g0 - 0.5, g0, 'u')
        cur = max(cur, g1)


def cheeks(g, x0, y0, x1, y1, up):
    """Stone cheek walls (2 m) either side of a short stair over x0..x1, y0..y1 rising towards `up`, just
    outside its sides."""
    if up in 'NS':
        R(g, x0 - 0.5, y0, x0, y1, '1'); R(g, x1, y0, x1 + 0.5, y1, '1')
    else:
        R(g, x0, y0 - 0.5, x1, y0, '1'); R(g, x0, y1, x1, y1 + 0.5, '1')


def planter(g, x0, y0, x1, y1):
    """A raised flower bed: a stone kerb round flower soil, with shrubs every other square."""
    R(g, x0, y0, x1, y1, 'z')
    R(g, x0 + 0.5, y0 + 0.5, x1 - 0.5, y1 - 0.5, 'F')
    for x, y in P.cells_rect(x0 + 0.5 - OX, y0 + 0.5 - OY, x1 - 0.5 - OX, y1 - 0.5 - OY):
        if (x + y) % 2 == 0:
            g[y][x] = 'Y'


def lamp(x0, y0, g=None):
    """A lamp head (a luminescent block) on the 1 x 1 m pier whose corner is x0, y0."""
    R(g or lamp6, x0, y0, x0 + 1, y0 + 1, 'l')


# ================================================================= the lake (bed 4 m down)
P.ground_rect(0, 0, 58, 60, -4)
R(lake, OX, OY, OX + 58, OY + 60, '~')

# ================================================================= the main square (+4 m)
# 32 x 32 m: limestone paving on a fancy stone edge; four entrances (north promenade, south causeway stair,
# west and east walkway stairs) and the altar dais in the middle; stalls in the north corners, storage
# halls in the south corners, the middle and the cross between the entrances left open.
deck(mid, 64, 64, 96, 96, 'L', 'f')
R(mid, 74, 74, 86, 86, 'S')                             # a smooth stone band round the dais
R(mid, 78, 50, 82, 74, 'S'); R(mid, 78, 86, 82, 96, 'S')       # paths from the band to each entrance (and up
R(mid, 64, 78, 74, 82, 'S'); R(mid, 86, 78, 96, 82, 'S')       # the promenade to the grand stair)
deck(dais, 76, 76, 84, 84, 'P', 'f', 0.5)               # the dais, with a fancy stone kerb
P.item('dais', 'altar', 'Flame Altar', 80 - ALTAR_W / 2 - OX, 80 - ALTAR_D / 2 - OY, ALTAR_W, ALTAR_D, ALTAR_H, color='#d9541e', iid='altar')
for x, y in ((76.5, 76.5), (82.5, 76.5), (76.5, 82.5), (82.5, 82.5)):
    put('dais', 'Brazier', x, y)                        # a brazier at each corner of the dais
zone('mid', 'Main square', 64, 64, 96, 96, '#b8862b')
zone('dais', 'Altar dais (one step up)', 76, 76, 84, 84, '#d9541e')
stairs('walk', 'Stairs: square to the causeway', 77, 96, 83, 98, 1, 'N')
stairs('walk', 'Stairs: square to the west walkway', 62, 77, 64, 83, 1, 'E')
stairs('walk', 'Stairs: square to the east walkway', 96, 77, 98, 83, 1, 'W')
# benches round the band facing the altar, lanterns at its north corners
for x in (74, 84):
    put('mid', 'Bench', x, 73, 0)
for y in (74, 84):
    put('mid', 'Bench', 73, y, 270); put('mid', 'Bench', 86.5, y, 90)
put('mid', 'Ground Lantern II', 73, 73); put('mid', 'Ground Lantern II', 86.5, 73)
# the balustrade round the square's edge (a 4 m drop to the water), open at the four entrances, with lamp
# piers either side of each entrance
balustrade(mid, 64, 64, 74, 64.5); balustrade(mid, 86, 64, 96, 64.5)
balustrade(mid, 64, 64, 64.5, 96, [(77, 83)]); balustrade(mid, 95.5, 64, 96, 96, [(77, 83)])
balustrade(mid, 64, 95.5, 96, 96, [(77, 83)])
for x0, y0 in ((73, 64), (86, 64), (64, 76), (64, 83), (95, 76), (95, 83)):
    R(mid, x0, y0, x0 + 1, y0 + 1, 'O'); lamp(x0, y0)
# the main entrance, from the causeway and the gatehouse: a stone gateway arch on two 5 m pillars, lamps on
# top, stepping down to a 1 m lintel (4 m clear over the path, 2.5 m at the sides)
for x0 in (76, 83):
    R(mid, x0, 95, x0 + 1, 96, 'X'); lamp(x0, 95, up9)
for (xa, xb, h, base) in ((77, 77.5, 2.5, 2.5), (82.5, 83, 2.5, 2.5), (77.5, 78, 1.5, 3.5), (82, 82.5, 1.5, 3.5), (78, 82, 1, 4)):
    overlay(mid, xa, 95, xb, 96, 'Fancy Stone Block (arch)', STONE, h, base)
cheeks(walk, 77, 96, 83, 98, 'N'); cheeks(walk, 62, 77, 64, 83, 'E'); cheeks(walk, 96, 77, 98, 83, 'W')

# market stalls: timber frames under straw awnings that slope down towards the square, a plank back wall,
# and a counter across the front of each bay
for (xb, xf, side) in ((66, 72.5, 'w'), (94, 87.5, 'e')):           # back (high side) and front post lines
    for y in (66, 70.5, 74.5):
        R(mid, xb, y, xb + 0.5, y + 1, 'v'); R(mid, xf, y, xf + 0.5, y + 1, 'p')
    for (y0, y1) in ((67, 70.5), (71.5, 74.5)):
        R(mid, xb, y0, xb + 0.5, y1, 'k'); R(mid, xf, y0, xf + 0.5, y1, 'i')
sr = roof(stallroof)
sr.lean_to(65.5, 65.5, 73.5, 76, 'w', 1.0, 0.5, 'straw')
sr.lean_to(86.5, 65.5, 94.5, 71, 'e', 1.0, 0.5, 'tarstraw')       # the trader's bay, in tarred straw
sr.lean_to(86.5, 71, 94.5, 76, 'e', 1.0, 0.5, 'straw')
sr.paint()
put('mid', 'Supply Sacks II', 66.5, 67.5); put('mid', 'Resource Bundle I', 66.5, 72)
put('mid', 'Scrappy Crate', 93, 67.5); put('mid', 'Supply Sacks I', 93, 72)
zone('mid', 'Market stalls (two)', 66, 66, 73, 75.5, '#c4501a')
zone('mid', "Trader's stall (Mei-Yin Chen)", 87.5, 66, 94.5, 70.5, '#c4501a')
zone('mid', 'Market stall', 87.5, 71, 94.5, 75.5, '#c4501a')

# storage halls (magic chests): stone on a rough stone plinth with quoins, a Wooden Double Door onto the
# square under a gabled bay with a round window, windows down the sides and over the water
for x0 in (65.5, 85.5):                                             # (the doors on whole metres)
    x1, dx = x0 + 9, x0 + 2.5
    walls(mid, x0, 87, x1, 95, 'Q', 'r')
    R(mid, x0 - 0.5, 87, x0, 95.5, 'z'); R(mid, x1, 87, x1 + 0.5, 95.5, 'z'); R(mid, x0 - 0.5, 95, x1 + 0.5, 95.5, 'z')
    for (qx, qy) in ((x0 - 0.5, 86.5), (x1 - 0.5, 86.5), (x0 - 0.5, 94.5), (x1 - 0.5, 94.5)):
        R(mid, qx, qy, qx + 1, qy + 1, 'Z')
    R(mid, dx - 0.5, 86.5, dx, 87.5, 'Z'); R(mid, dx + 4, 86.5, dx + 4.5, 87.5, 'Z')    # pilasters by the door
    R(mid, dx + 1, 87, dx + 3, 87.5, 'R')                           # the wall over the door rises into the bay's gable
    door('mid', 'Wooden Double Door', dx, 87, dx + 4, 87.5)
    win('mid', 'Round Wooden Window Frame', dx + 1.5, 87, dx + 2.5, 87.5, 4.5)
    for y in (89.5, 92):
        win('mid', 'Wooden Window Frame', x0, y, x0 + 0.5, y + 1, 1.5); win('mid', 'Wooden Window Frame', x1 - 0.5, y, x1, y + 1, 1.5)
    for x in (x0 + 2, x0 + 5.5):
        win('mid', 'Wooden Window Frame', x, 94.5, x + 1, 95, 1.5)
    # inside: large magic chests round the walls, a quick stack station by the door, a lantern
    for x in (x0 + 1, x0 + 3.5, x0 + 6):
        put('mid', 'mchest-large', x, 93.5, 180)
    for y in (88.5, 91):
        put('mid', 'mchest-large', x0 + 0.5, y, 270); put('mid', 'mchest-large', x1 - 1.5, y, 90)
    put('mid', 'quickstack', x0 + 0.5, 87.5)
    put('mid', 'Hanging Lantern', x0 + 4.5, 90.5)
    put('mid', 'Wall Lantern', dx - 1, 86.5, 180, 2.0); put('mid', 'Wall Lantern', dx + 4.5, 86.5, 180, 2.0)
# roofs: low stone shingle hips cut off flat at 2 m, so they stay squat beside the square, each with a
# gabled bay over its doors that puts a gable on the front
hr = roof(hallroof)
for (x0, x1, dx) in ((65.5, 74.5, 68), (85.5, 94.5, 88)):
    hr.hip(x0, 87, x1, 95, 'shingle', pitch=1.0, overhang=0.5, ridge_h=2.0)
    hr.gable(dx - 0.5, 87, dx + 4.5, 90, 'y', 'shingle', pitch=1.0, overhang=0.5)
hr.paint()
zone('mid', 'Storage hall, west wing (magic chests)', 65.5, 87, 74.5, 95, '#8a5cc2')
zone('mid', 'Storage hall, east wing (magic chests)', 85.5, 87, 94.5, 95, '#8a5cc2')
zone('mid', 'South entrance', 75, 87, 85, 96, '#b8862b')

# ================================================================= the north promenade and the grand stair
R(mid, 74, 42, 86, 64, 'L')
R(mid, 78, 50, 82, 64, 'S')                             # the runner up the middle
stairs('mid', 'Grand stair to the manor', 76, 42, 84, 50, 4, 'N')
# stone flanks either side of the stair, stepping up with it (a metre or more above the treads), lamps on
# their ends
for (xa, xb) in ((74, 76), (84, 86)):
    for (y0, ch) in ((48, '1'), (46, '2'), (44, '3'), (42, '4')):
        R(mid, xa, y0, xb, y0 + 2, ch)
    lamp(xa + 0.5, 49); lamp(xa + 0.5, 42, up9)
# the promenade's edges over the water, open where the stairs go up to the tavern and the lodging house
balustrade(mid, 74, 57, 74.5, 64); balustrade(mid, 85.5, 57, 86, 64)
R(mid, 74, 50, 74.5, 51, 'o'); R(mid, 85.5, 50, 86, 51, 'o')
for (x0, xb, rot) in ((74.5, 74.5, 270), (83.5, 85, 90)):
    planter(mid, x0, 61, x0 + 2, 63.5)
    put('mid', 'Bench', xb, 58.5, rot)
    put('mid', 'Ground Lantern II', xb, 57.5)
zone('mid', 'North promenade', 74, 50, 86, 64, '#b8862b')
R(mnr, 54, 40, 110, 42, 'P'); R(mnr, 54, 41.5, 110, 42, 'f')    # the manor's front edge (its own blueprint)
zone('manor', 'Manor grounds (manor blueprint)', 54, 40, 110, 42, '#8a5cc2')

# ================================================================= the tavern (Bard), up a step west of the promenade
deck(up5, 58, 46, 72, 62, 'h', 't')
R(mid, 72, 51, 74, 57, 'L')
stairs('mid', 'Stairs up to the tavern', 72, 51, 74, 57, 1, 'W')
cheeks(mid, 72, 51, 74, 57, 'W')
# ground floor (+5 m): a brick hall with the bar, a kitchen and pantry behind, the stair up along the north wall
walls(up5, 59, 47, 69, 61, 'B', 'r')
R(up5, 59.5, 55.5, 68.5, 56, 'B')                               # hall | kitchen
door('up5', 'Round Wooden Door', 68.5, 52, 69, 55)             # the front door, onto the terrace
door('up5', 'Wooden Door', 63, 55.5, 65, 56)                   # hall to kitchen
door('up5', 'Wooden Door', 68.5, 58, 69, 60)                   # the kitchen's back door, onto the terrace
R(up5, 60, 46, 62, 47.5, 'C')                                   # the hall's chimney, on the north gable end (clear of the stair)
R(up5, 63.5, 60.5, 64.5, 62, 'C')                               # the kitchen flue, up the middle of the south gable end
stairs('up5', 'Tavern stair up to the rooms', 63, 47.5, 67, 49, 4, 'W')     # (1.5 m wide: its well stays open at 1 m)
win('up5', 'Wooden Window Frame', 59, 48.5, 59.5, 49.5)      # west: the hall
door('up5', 'Wooden Door', 59, 50, 59.5, 52)                   # west: a side door, down to the west landing
R(mid, 56, 50, 58, 52, 'w')
stairs('mid', 'Side stair: tavern to the west landing', 56, 50, 58, 52, 1, 'E')
rail(mid, 56.5, 49.5, 58, 50); rail(mid, 56, 52, 58, 52.5)    # (the west stair's flank stands at x 56 to 56.5)
put('up5', 'Wall Lantern', 58.5, 52, 90, 2.0)
win('up5', 'Wooden Window Frame', 59, 58.5, 59.5, 59.5)        # west: the kitchen
win('up5', 'Wooden Window Frame', 68.5, 49, 69, 50)            # east: the hall, north of the door
for x in (60.5, 66.5):
    win('up5', 'Wooden Window Frame', x, 60.5, x + 1, 61)      # south: the kitchen
win('up5', 'Round Wooden Window Frame', 65, 47, 66, 47.5, 2.5) # north: over the stair
# a gabled porch over the front door, on two posts
for y in (52, 55.5):
    R(up5, 70.5, y, 71, y + 0.5, 'n')
pr = roof(porch8)
pr.gable(69.5, 52, 71.5, 56, 'x', 'tiles', pitch=1.0, overhang=0.5, end_overhang=0)
pr.paint()
# the terrace and deck: a railing round the edge (open at the stair), a bench, lanterns
rail(up5, 58, 46, 72, 46.5, [(60, 62)]); rail(up5, 58, 61.5, 72, 62, [(63.5, 64.5)])
rail(up5, 58, 46, 58.5, 62, [(50, 52)]); rail(up5, 71.5, 46, 72, 62, [(51, 57)])
put('up5', 'Bench', 71, 58, 90)
put('up5', 'Ground Lantern II', 71, 50)
put('up5', 'Hanging Lantern', 70, 53.5, z=3.0)
# inside: the hearth, the Bard's stage, the bar, a long table, the kitchen's stations, the pantry
put('up5', 'Stone Fireplace', 60, 47.5, 0)
put('up5', 'Rustic Chair', 60, 49, 180); put('up5', 'Rustic Chair', 61, 49, 180)
R(stage, 59.5, 52, 63, 55, 'r')                                # the stage, a step up in the hall's corner
put('stage', 'npc-bard', 59.5, 52, 270, label='Bard (on the stage)')
for x in (63, 65):
    put('up5', 'Wooden Tavern Counter', x, 53, 180)            # the bar, served from the kitchen side
put('up5', 'Wooden Banquet Table', 63.5, 50.5)
put('up5', 'Bench', 64, 50, 0); put('up5', 'Bench', 64, 51.5, 180)
put('up5', 'Hanging Lantern', 65, 51); put('up5', 'Hanging Lantern', 65.5, 54); put('up5', 'Hanging Lantern', 61, 50.5)
put('up5', 'cooking-station', 59.5, 56); put('up5', 'kitchen', 65.5, 56)
put('up5', 'oven', 63, 58.5, 180)                              # under the flue
put('up5', 'Wooden Sink', 65, 59, 180)
put('up5', 'chest-small', 59.5, 59.5, 180); put('up5', 'chest-small', 60.5, 59.5, 180)
put('up5', 'Hanging Lantern', 63.5, 57.5)
# upper floor (+9 m): half-timbered, jettied 0.5 m out over the ground floor on the east and west, on
# wooden corbels; a landing along the north and two rooms
walls(up9, 58.5, 47, 69.5, 61, 'T', 'r')
R(up9, 60, 47, 62, 47.5, ' '); R(up9, 63.5, 60.5, 64.5, 61, ' ')     # the chimneys pass up through the wall
R(up9, 63, 47.5, 67, 49, ' ')                                   # the stairwell
R(up9, 63, 49, 67.5, 49.5, 'i'); R(up9, 67, 47.5, 67.5, 49, 'i')     # railing round it
R(up9, 59, 51.5, 69, 52, 'T')                                   # landing | rooms
R(up9, 63.5, 52, 64, 60.5, 'T')                                 # room | room
door('up9', 'Wooden Door', 60.5, 51.5, 62.5, 52)
door('up9', 'Wooden Door', 65.5, 51.5, 67.5, 52)
for y in (47, 49, 51, 57, 59, 60.5):
    overlay(up5, 69, y, 69.5, y + 0.5, 'Refined Wood Block (corbel)', WOOD, 0.5, 3)
    overlay(up5, 58.5, y, 59, y + 0.5, 'Refined Wood Block (corbel)', WOOD, 0.5, 3)
# the cross gable's end rises as a wall with a round window in it
R(up9, 69, 52.5, 69.5, 55.5, 'G')
win('up9', 'Round Wooden Window Frame', 69, 53.5, 69.5, 54.5, 3.5)
UP9_WIN = [(58.5, 49, 'W'), (58.5, 54, 'W'), (58.5, 58, 'W'), (69, 49, 'E'), (69, 58, 'E'), (61, 60.5, 'S'), (66, 60.5, 'S'), (67.5, 47, 'N')]
# a sign on a bracket from the jetty, over the terrace
R(up9, 69.5, 50.5, 70, 51, 'j'); R(up9, 70, 50.5, 71, 51, 'J')
put('up9', 'bed', 59, 57); put('up9', 'chest-small', 62.5, 52.5)
put('up9', 'bed', 66.5, 57); put('up9', 'chest-small', 64, 52.5)
put('up9', 'Hanging Lantern', 68, 50, z=2.5)
put('up9', 'Hanging Lantern', 61, 55.5, z=2.5); put('up9', 'Hanging Lantern', 66.5, 55.5, z=2.5)
zone('up5', 'Tavern (Bard): food and rooms', 58, 46, 72, 62, '#b0596f')
zone('up5', 'Tavern hall and bar', 59.5, 47.5, 68.5, 55.5, '#b0596f')
zone('stage', "Bard's stage", 59.5, 52.5, 62.5, 55.5, '#b0596f')
zone('up5', 'Kitchen and pantry (food stations)', 59.5, 56, 68.5, 60.5, '#c46a2a')
zone('up5', 'Terrace', 69, 47, 72, 61, '#b8862b')
zone('up9', 'Landing', 59, 47.5, 69, 51.5, '#b0596f')
zone('up9', "Bard's room", 59, 52, 63.5, 60.5, '#b0596f')
zone('up9', 'Guest room', 64, 52, 69, 60.5, '#9c6b8e')

# ================================================================= the lodging house, up a step east of the promenade
deck(up5, 88, 46, 108, 62, 'h', 't')
R(mid, 86, 51, 88, 57, 'L')
stairs('mid', 'Stairs up to the lodging house', 86, 51, 88, 57, 1, 'E')
cheeks(mid, 86, 51, 88, 57, 'E')
# ground floor (+5 m): stone on a plinth with quoins, a common room with the stair up, two bedrooms with
# fireplaces on a shared chimney
walls(up5, 91, 47, 107, 59, 'Q', 'r')
R(up5, 90.5, 46.5, 107.5, 47, 'z'); R(up5, 107, 46.5, 107.5, 59.5, 'z'); R(up5, 90.5, 59, 107.5, 59.5, 'z')
for (qx, qy) in ((90.5, 46.5), (106.5, 46.5), (90.5, 58.5), (106.5, 58.5)):
    R(up5, qx, qy, qx + 1, qy + 1, 'Z')
door('up5', 'Wooden Door', 91, 53, 91.5, 55)                    # the front door, onto the forecourt
R(up5, 99, 47.5, 99.5, 58.5, 'Q')                               # common room | bedrooms
R(up5, 99.5, 53, 106.5, 53.5, 'Q')                              # bedroom | bedroom
R(up5, 98.5, 52.5, 99.5, 54.5, 'D')                             # the common room's chimney, in the partition
door('up5', 'Wooden Door', 99, 50, 99.5, 52)
door('up5', 'Wooden Door', 99, 55, 99.5, 57)
stairs('up5', 'Lodging stair up to the rooms', 93, 47.5, 97, 49, 4, 'E')    # (1.5 m wide: its well stays open at 1 m)
R(up5, 107, 52.5, 108, 54.5, 'D')                               # the chimney, outside the east wall
for y in (50, 57):
    win('up5', 'Wooden Window Frame', 91, y, 91.5, y + 1)      # west, either side of the door
for x in (97.5, 101, 104):
    win('up5', 'Wooden Window Frame', x, 47, x + 1, 47.5)      # north
win('up5', 'Wooden Window Frame', 106.5, 49.5, 107, 50.5); win('up5', 'Wooden Window Frame', 106.5, 56.5, 107, 57.5)   # east
for x in (93, 96, 101, 104):
    win('up5', 'Wooden Window Frame', x, 58.5, x + 1, 59)      # south, onto the garden
# a lean-to hood over the front door on two brackets, lanterns either side
dh = roof(hood)
dh.lean_to(89.5, 52, 91, 56, 'e', 1.0, 0.5, 'lead')
dh.paint()
overlay(up5, 90.5, 52, 91, 52.5, 'Refined Wood Block (bracket)', WOOD, 1, 2)
overlay(up5, 90.5, 55.5, 91, 56, 'Refined Wood Block (bracket)', WOOD, 1, 2)
put('up5', 'Wall Lantern', 90.5, 51, 90, 2.0); put('up5', 'Wall Lantern', 90.5, 56.5, 90, 2.0)
R(up9, 90.5, 51, 91, 51.5, 'j'); R(up9, 89.5, 51, 90.5, 51.5, 'J')   # its sign, on a bracket over the forecourt
# the deck: a railing round the edge (open at the stair and the chimney), a bench and a lantern in the
# forecourt, flower beds in the garden
rail(up5, 88, 46, 108, 46.5); rail(up5, 88, 61.5, 108, 62)
rail(up5, 88, 46, 88.5, 62, [(51, 57)]); rail(up5, 107.5, 46, 108, 62, [(52.5, 54.5)])
put('up5', 'Bench', 88.5, 47.5, 270); put('up5', 'Ground Lantern II', 88.5, 50)
planter(up5, 89, 47, 90.5, 48.5); planter(up5, 89, 57.5, 90.5, 59)
for (x0, x1) in ((92, 95.5), (96.5, 100.5), (101.5, 105.5)):     # flower beds along the garden's outer edge
    R(up5, x0, 61, x1, 61.5, 'F')
    for x in range(int(x0 * 2), int(x1 * 2), 3):
        R(up5, x / 2, 61, x / 2 + 0.5, 61.5, 'Y')
# inside
put('up5', 'Wooden Banquet Table', 93.5, 53); put('up5', 'Bench', 94, 52.5, 0); put('up5', 'Bench', 94, 54, 180)
put('up5', 'Stone Fireplace', 97.5, 52.5, 90)
put('up5', 'chest-small', 97.5, 47.5, 180); put('up5', 'chest-small', 97.5, 57.5, 180)
put('up5', 'Hanging Lantern', 95.5, 51.5); put('up5', 'Hanging Lantern', 95.5, 56)
put('up5', 'bed', 101, 47.5); put('up5', 'Fireplace', 105.5, 51, 90)
put('up5', 'bed', 101, 55.5); put('up5', 'Fireplace', 105.5, 53.5, 90)
put('up5', 'Hanging Lantern', 103, 50.5); put('up5', 'Hanging Lantern', 103, 56)
put('up5', 'chest-small', 103.5, 47.5, 180); put('up5', 'chest-small', 103.5, 57.5, 180)
# upper floor (+9 m): brick-timbered, a landing along the north and four bedrooms, each with a door onto
# a balcony over the garden
walls(up9, 91, 47, 107, 59, 'K', 'r')
R(up9, 93, 47.5, 97, 49, ' ')                                   # the stairwell
R(up9, 92.5, 49, 97, 49.5, 'i'); R(up9, 92.5, 47.5, 93, 49, 'i')     # railing round it
R(up9, 91.5, 51.5, 106.5, 52, 'K')                              # landing | rooms
for x in (95, 99, 103):
    R(up9, x, 52, x + 0.5, 58.5, 'K')                           # room | room
R(up9, 98.5, 52.5, 99.5, 54.5, ' ')                             # the chimney passes up through
R(up9, 91, 52.5, 91.5, 55.5, 'H')                               # the cross gable's end, with a round window
win('up9', 'Round Wooden Window Frame', 91, 53.5, 91.5, 54.5, 3.5)
BEDROOMS = ((91.5, 95, 92.5), (95.5, 99, 96.5), (99.5, 103, 100.5), (103.5, 106.5, 104.5))
# (the second room's landing door 0.5 m west, clear of the chimney; the fourth room's doors 0.5 m west, off the
# end wall, and its chest by the landing door instead: whole metres for the site map)
LANDING_DX = {96.5: 96, 104.5: 104}
for x0, x1, dx in BEDROOMS:
    door('up9', 'Wooden Door', LANDING_DX.get(dx, dx), 51.5, LANDING_DX.get(dx, dx) + 2, 52)    # from the landing
    bx = 104 if dx == 104.5 else dx
    door('up9', 'Wooden Door', bx, 58.5, bx + 2, 59)            # onto the balcony
    put('up9', 'bed', x0, 53.5, 0)
    put('up9', 'Hanging Lantern', x0 + 2.5, 55, z=2.5)
    put('up9', 'chest-small', *((104, 52.5) if dx == 104.5 else (x0, 57.5)), 0)
R(up9, 91, 59, 107, 60.5, 'r')                                  # the balcony, the length of the house
rail(up9, 91, 60, 107, 60.5); rail(up9, 91, 59, 91.5, 60); rail(up9, 106.5, 59, 107, 60)
for x in (91, 96, 101, 106.5):
    R(up5, x, 60, x + 0.5, 60.5, 'e')                           # its posts, down to the garden
UP9_WIN += [(91, 49, 'W'), (91, 56, 'W'), (98, 47, 'N'), (101, 47, 'N'), (104, 47, 'N'), (106.5, 55, 'E')]
put('up9', 'Hanging Lantern', 99, 49.5, z=2.5)
zone('up5', 'Lodging house (assistants and guests)', 88, 46, 108, 62, '#9c6b8e')
zone('up5', 'Common room', 91.5, 47.5, 99, 58.5, '#9c6b8e')
zone('up5', 'Bedroom 1', 99.5, 47.5, 106.5, 53, '#9c6b8e')
zone('up5', 'Bedroom 2', 99.5, 53.5, 106.5, 58.5, '#9c6b8e')
zone('up5', 'Forecourt', 88, 47, 91, 59, '#b8862b')
zone('up5', 'Garden', 91, 59, 107, 61, '#3f8a4f')
zone('up9', 'Landing', 91.5, 47.5, 106.5, 51.5, '#9c6b8e')
zone('up9', 'Balcony', 91, 59, 107, 60.5, '#b8862b')
for i, (x0, x1, _) in enumerate(BEDROOMS):
    zone('up9', f'Bedroom {i + 3}', x0, 52, x1, 58.5, '#9c6b8e')

# upper-floor windows, each with a window box under it outside
for (x, y, side) in UP9_WIN:
    if side in 'WE':
        win('up9', 'Wooden Window Frame', x, y, x + 0.5, y + 1)
        bx = x - 0.5 if side == 'W' else x + 0.5
        R(up9, bx, y, bx + 0.5, y + 1, 'x')
    else:
        win('up9', 'Wooden Window Frame', x, y, x + 1, y + 0.5)
        by = y - 0.5 if side == 'N' else y + 0.5
        R(up9, x, by, x + 1, by + 0.5, 'x')

# ---- roofs, at 45 degrees in even one-block steps
# the tavern: a steep tiled gable (ridge north-south) over the jettied upper floor, with a cross gable over
# the front door, a dark ridge, and the two chimneys rising through the gable ends
rt = roof(roof12)
rt.gable(58.5, 47, 69.5, 61, 'y', 'tiles', pitch=1.0, overhang=0.5)
rt.gable(64, 51, 69.5, 57, 'x', 'tiles', pitch=1.0, overhang=0.5)
rt.caps('lead', min_lower=1)
rt.cut(60, 46, 62, 47.5); rt.cut(63.5, 60.5, 64.5, 62)
rt.paint()
# the lodging house: a tarred shingle hip cut off flat at half height, and a cross gable over the entrance
rl = roof(roof12)
rl.hip(91, 47, 107, 59, 'lead', pitch=1.0, overhang=0.5, ridge_h=3.5)
rl.gable(91, 51, 97, 57, 'x', 'lead', pitch=1.0, overhang=0.5)
rl.cut(107, 52.5, 108, 54.5); rl.cut(98.5, 52.5, 99.5, 54.5)   # round the chimneys
rl.paint()
# chimney caps: a course 0.5 m proud all round the top of each stack
for (x0, y0, x1, y1, ch) in ((60, 46, 62, 47.5, 'c'), (63.5, 60.5, 64.5, 62, 'c'), (107, 52.5, 108, 54.5, 'd'), (98.5, 52.5, 99.5, 54.5, 'd')):
    R(caps, x0 - 0.5, y0 - 0.5, x1 + 0.5, y1 + 0.5, ch); R(caps, x0, y0, x1, y1, ' ')

# ================================================================= the walkways off the square (their own blueprints)
# Walkways are 6 m of rough wood at +3 m with a wooden railing just outside each edge (newel posts at the
# ends): the style for the walkway blueprints to carry on.
R(walk, 54, 77, 64, 83, 'w')
R(walk, 54, 83, 58, 86, 'w')                                    # the branch down to the bathhouse
R(walk, 96, 77, 112, 83, 'w')
R(walk, 77, 96, 83, 100, 'w')
rail(walk, 54, 76.5, 62, 77); rail(walk, 58, 83, 62, 83.5); rail(walk, 58, 83.5, 58.5, 86)
rail(walk, 98, 76.5, 112, 77); rail(walk, 98, 83, 112, 83.5)
rail(walk, 76.5, 98, 77, 100); rail(walk, 83, 98, 83.5, 100)
# the east end of the west landing and the west stair up to the manor (the smithy blueprint has the rest);
# the tavern's side stair comes down onto the landing
R(mid, 54, 42, 56, 52, 'w')
stairs('mid', 'West stair to the manor (its east end)', 54, 42, 56, 50, 4, 'N')
# the bathhouse deck (+2 m) and the end of its stair up to the bathhouse branch (the bathhouse blueprint)
R(low, 54, 86, 62, 98, 't'); R(low, 54, 87, 61, 97, 'h')
stairs('low', 'Stairs up to the west walkway (bathhouse)', 54, 86, 58, 88, 1, 'N')
zone('walk', 'West walkway (smithy, carpentry, bathhouse)', 54, 77, 62, 83, '#2f8f8a')
zone('walk', 'East walkway (to the east junction)', 98, 77, 112, 83, '#2f8f8a')
zone('walk', 'Causeway (to the gatehouse)', 77, 98, 83, 100, '#2f8f8a')
zone('mid', 'West stair and landing (smithy blueprint)', 54, 42, 56, 52, '#2f8f8a')
zone('low', 'Barber and bathhouse (bathhouse blueprint)', 54, 86, 62, 98, '#3f7f9e')

# ================================================================= stilts: 1 m posts on the layout's 4 m grid
# A post (2 x 2 blocks) wherever the layout has one: on the 4 m grid, plus wherever a narrow deck would
# otherwise be more than 2 m from a post of its own. Each stands on the bed and stops under its deck.
BED = -4
DECKS = [('low', 2), ('walk', 3), ('mid', 4), ('up5', 5), ('manor', 8)]
post_ch = {lid: P._alloc({'name': f'Tarred Wood Block (stilt to +{el} m)', 'kind': 'block', 'color': '#4e4844', 'height': el - 0.5 - BED})
           for lid, el in DECKS}
lowest = {}                                             # per layout metre: the lowest deck over it
for lid, el in DECKS:
    g = P.grids[lid]
    for y in range(P.H):
        for x in range(P.W):
            if g[y][x] != ' ':
                m = (OX + x // 2, OY + y // 2)
                lowest.setdefault(m, lid)
posts = {m: lid for m, lid in lowest.items() if m[0] % 4 == 1 and m[1] % 4 == 1}
for (mx, my), lid in sorted(lowest.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    if not any(posts.get((mx + dx, my + dy)) == lid for dx in range(-2, 3) for dy in range(-2, 3)):
        posts[(mx, my)] = lid
for (mx, my), lid in posts.items():
    R(stl, mx, my, mx + 1, my + 1, post_ch[lid])
print('stilts:', len(posts))
# rim beams: a course of tarred wood under each deck's floor course round its exposed edges (this blueprint's
# own decks; the neighbours' edges get theirs in their own blueprints)
nb = 0
for lid, el in (('walk', 3), ('mid', 4), ('up5', 5)):
    beam = P._alloc({'name': f'Tarred Wood Block (rim beam, +{el} m)', 'kind': 'block', 'color': '#4e4844', 'height': 0.5, 'base': el - 1 - BED})
    g = P.grids[lid]
    for y in range(P.H):
        for x in range(P.W):
            if g[y][x] == ' ' or stl[y][x] != ' ':
                continue
            if lid == 'mid' and OX + x / 2 < 56 and OY + y / 2 < 52:   # the west stair: the smithy blueprint's
                continue
            if any(0 <= x + dx < P.W and 0 <= y + dy < P.H and g[y + dy][x + dx] == ' ' for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                stl[y][x] = beam; nb += 1
print('rim beam squares:', nb)

P.item('mid', 'spawn', 'Spawn point', 79.5 - OX, 91 - OY, 1, 1, 0.5, 180, '#2fa36b')   # walk mode starts here: the south entrance, facing up the promenade
problems = P.check(outdoor_ok=('lake',), ignore_types=('stairs',))
print('item problems:', len(problems))
for p_ in problems:
    print('  ', p_)
access = P.check_access()
print('access problems:', len(access))
seen = {}
for p_ in access:
    k = p_.split(' at ')[0] + ' / ' + p_.split(': ', 1)[1].split(' at ')[0][:60]
    seen.setdefault(k, []).append(p_)
for k, v in seen.items():
    print(f'   [{len(v)}] {v[0]}')
outside = P.altar_problems()                            # (this plan holds the altar)
print("outside the altar's build volume:", len(outside))
for p_ in outside:
    print('  ', p_)

NOTES = """Laketown: the main square, as a 0.5 m detail blueprint (all three passes done). Drafted by Claude.
This plan's corner is the layout's (54, 40), so it lines up with the Laketown layout and can be stamped back into a site plan there.

PASSES
1. Design and bones: decks, the dais, building shells with walls, partitions, doors, stairs and roof shapes, the stairs to the neighbours, stilts, labels.
1.5. Roofs: every roof at 45 degrees in even one-block steps, so the game's roof brushes fit them, with a shape suited to each building.
2. Details: windows, trim, railings and balustrades, lamps, planters, stall counters, and the furniture and stations that matter.
3. Review and finishing touches (this one): a critical look at passes 1 and 2, the connections to the neighbouring areas, and the last details.

PASS 3: WHAT THE REVIEW FOUND AND CHANGED
- The tavern had no way west: the smithy and the villagers' quarter had to cross the square to reach it. It now has a side door in the hall's west wall and a short stair down to the west landing (the smithy's stair up to the manor). The 1 m layout has it too.
- The 1 m stairs (to the tavern, the lodging house and the three walkways) had open sides over a 3-4 m drop: they have stone cheek walls now.
- The main entrance (from the causeway and the gatehouse) looked like the others: it has a stone gateway arch on two 5 m pillars, lamps on top.
- The deck edges were a bare floor course: a tarred wood rim beam runs under every exposed edge.
- Railings ended abruptly: newel posts at the end of every piece.
- The lodging house had no sign (the tavern did): one on a bracket over the forecourt.
- The lodging garden path was squeezed between the balcony posts and the flower beds: the beds moved to the outer edge.
- Chests in every lodging bedroom.
- Checked, all clear (check_access): nothing in front of any door or window, no door onto a drop, every stair with 1 m clear at the foot and top and 2 m of headroom.

CONNECTIONS (for the neighbouring blueprints to match)
- West walkway (+3 m): 6 m wide, y 77..83, rough wood, a wooden railing just outside each edge with newel posts. The bathhouse branch leaves its south side at x 54..58 and the bathhouse stair climbs to it from +2 m at y 86..88.
- West landing (+4 m): the tavern's side stair (x 56..58, y 50..52) comes down onto it beside the foot of the west stair to the manor (x 50..56, y 42..50, 4 m up).
- East walkway (+3 m): 6 m wide, y 77..83, the same railing; on to the east junction.
- Causeway (+3 m): 6 m wide, x 77..83, the same railing; south to the drawbridge and the gatehouse. It arrives under the gateway arch.
- Manor (+8 m): its front edge runs along y 40..42. The grand stair (x 76..84) arrives at y 42 between stone flanks that stand 1 m above the manor deck, with lamps; the manor's front terrace should leave that gap open.
- Stair cheeks are 2 m Fancy Stone walls just outside each stair; walkway stairs meet the square between lamp piers.


THE SQUARE (+4 m, 32 x 32 m)
- Limestone paving on a fancy stone edge, with smooth stone paths from the band round the dais out to each entrance (and up the promenade).
- A fancy stone balustrade round the edge, with piers, open at the four entrances. Each entrance has a lamp pier either side (a luminescent block on top).
- The Flame Altar on an 8 x 8 m polished stone dais, one step (0.5 m) up, with a fancy stone kerb and a brazier at each corner. Benches round the band face it.
- Market stalls in the north corners (two NW; the trader's stall and one more NE): timber posts, a plank back wall, a counter across each bay, straw awnings sloping down towards the square. The trader's awning is tarred straw, so it stands out.
- Storage halls (magic chests) in the south corners: refined stone on a rough stone plinth with quoins, a Wooden Double Door (7 x 8 blocks) under a gabled bay with a round window, windows down the sides and over the water. Inside: seven Large Magic Chests each and a Quick Stack Station by the door. Low hipped roofs cut off flat at 2 m.

THE PROMENADE AND THE GRAND STAIR
- 12 m wide, with a smooth stone runner up the middle, benches, lanterns and planters, and a balustrade along its edges where they face the water.
- The grand stair (8 m wide, 4 m up) has stone flanks that step up with it, with lamps at both ends.
- The manor grounds are their own blueprint (only their front edge is drawn here).

THE TAVERN (Bard), up a step west of the promenade (+5 m deck)
- Ground floor (fired brick): the hall with a stone fireplace, the Bard's stage (a step up) in the corner, a bar served from the kitchen side, and a long table. The kitchen holds the Farmer's cooking station, kitchen and oven (under the flue), a sink and the pantry chests, with a back door onto the terrace.
- Upper floor (+9 m, half-timbered), jettied 0.5 m out over the ground floor east and west on wooden corbels: a railed landing, the Bard's room and a guest room. Window boxes under the upper windows.
- The front: a Round Wooden Door (6 x 6) under a gabled porch on two posts, a hanging sign on a bracket, the cross gable above with a round window in its end.
- Roof: a steep 45 degree tiled gable with a dark ridge; brick chimneys up both gable ends, with corbelled caps.
- A railing round the deck, open at the stair from the promenade; a bench and lanterns on the terrace.

THE LODGING HOUSE (assistants and guests), up a step east of the promenade (+5 m deck)
- Ground floor (refined stone on a plinth, with quoins): a common room with a long table, a hearth and the stair up, two bedrooms with fireplaces on a shared chimney outside the east wall. A lean-to hood over the front door on brackets, with lanterns.
- The common room's chimney rises in the partition, through the upper floor, to a stack on the flat roof.
- Upper floor (+9 m, brick-timbered): a railed landing and four bedrooms, each with a door onto a balcony over the garden (on posts). Window boxes under the upper windows; a round window in the cross gable.
- Roof: a tarred shingle hip cut off flat at half height, with a cross gable over the entrance.
- A railing round the deck, a bench, a lantern and two planters in the forecourt, flower beds in the garden.

BEDS: the Bard's room and the guest room in the tavern, and six bedrooms in the lodging house: eight beds.

ITEMS: doors and windows are placed items at their measured sizes: Wooden Door (5 x 4 blocks), Round Wooden Door (6 x 6), Wooden Double Door (7 x 8), Wooden Window Frame (3 tall x 2 wide), Round Wooden Window Frame (2 x 2). Furniture, lights and decorations use real item names; their sizes are estimates until measured. Stations and chests use the planner's library sizes (2 x 2 m placeholders for stations).

STILTS: 1 m posts (2 x 2 blocks) on the layout's 4 m grid, from the lake bed 4 m down to each deck's underside.

THE EDGES: the walkway stubs (west, east, causeway, the bathhouse branch), the east end of the west landing and the west stair, the bathhouse deck and the manor's front edge are drawn for where the stairs lead. They belong to their own blueprints.

TO CHECK IN GAME: furniture and light sizes (estimates); the stations are 2 x 2 m placeholders; which station feeds survivors; luminescent blocks glow but are a softer light than the lanterns.
"""
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'laketown_square.json')
print('bytes', P.save(out, NOTES, 'r-claude-laketown-square-3b'))
for a, b in P.merged:
    print('  folded:', a, '->', b)
print('palette', len(PALETTE))
