"""Laketown: the farm. 0.5 m detail plan. Pass 3 of 3: review and finishing touches.

The Farmer's farmstead on the town's east side, at +5 m. A stone farmhouse under thatch along the north side
holds the kitchen and the bakehouse, with the Farmer's rooms in the roof; its kitchen door opens onto the foot
of the service stair up to the manor's east garden, so food goes straight up to the house. Beside it a tall
tarred barn turns its gable to the farmyard, which runs the width of the farm. South of the yard: the animals
(a byre along the west edge, pens for the yaks, goats and birds), the lane down to the east junction, the
fields, and a garden of seedbeds and beehives on flower soil leading to the herb bridge and the alchemist.

Coordinates are the layout's (doc `laketown`): this plan's corner is the layout's (106, 24).
Run: python laketown_farm.py  ->  writes laketown_farm.json
"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laketown_common import Area, WOOD, STONE, BED

RS, TAR = '#7d776a', '#5d5652'
OX, OY = 106, 24
A = Area('Laketown: the farm (detail)', OX, OY, 50, 54, {
    'F': {'name': 'Farm Soil', 'kind': 'floor', 'color': '#90450d'},                    # the fields
    'o': {'name': 'Flower Soil', 'kind': 'floor', 'color': '#a77e63'},                  # the apiary
    'e': {'name': 'Springlands Dirt', 'kind': 'floor', 'color': '#b39672'},             # the pens
    'd': {'name': 'Dirt Road Block', 'kind': 'floor', 'color': '#8c7455'},              # the lane
    'c': {'name': 'Field Stones', 'kind': 'floor', 'color': '#8a8170'},                 # the yard, the dooryard
    'g': {'name': 'Polished Granite Block', 'kind': 'floor', 'color': '#626c7a'},       # research hall, alchemist (theirs)
    'L': {'name': 'Limestone Road Block', 'kind': 'floor', 'color': '#a38b79'},         # the manor's east garden (its)
    'S': {'name': 'Rough Stone Block', 'kind': 'wall', 'color': RS},                    # the farmhouse
    'W': {'name': 'Plaited Block (wattle)', 'kind': 'wall', 'color': '#867561', 'height': 1},   # its kneewalls and gables
    'T': {'name': 'Tarred Wood Block', 'kind': 'wall', 'color': TAR, 'height': 5},      # the barn
    'K': {'name': 'Rough Stone Block (chimney)', 'kind': 'wall', 'color': RS, 'height': 11},
    'n': {'name': 'Rough Wood Block (byre post)', 'kind': 'block', 'color': '#7a6653', 'height': 2.5},
    'b': {'name': 'Plaited Block (byre back wall)', 'kind': 'wall', 'color': '#867561', 'height': 2.5},
    'D': {'name': 'Plaited Block (dormer)', 'kind': 'wall', 'color': '#867561', 'height': 2.5},
    'G': {'name': 'Plaited Block (gable, round the window)', 'kind': 'wall', 'color': '#867561', 'height': 3},
    'U': {'name': 'Refined Wood Block (lamp post)', 'kind': 'block', 'color': WOOD, 'height': 2},
})
P, R, zone, put = A.P, A.R, A.zone, A.put
stl = A.level('stilts', 'Stilts, standing on the lake bed (-4 m)', BED, 14)
lake = A.level('lake', 'Lake (water level, 0 m)', 0, 1)
walk = A.level('walk', 'East junction, its edge (+3 m)', 3, 4)
up5 = A.level('up5', 'The farm (+5 m)', 5, 4)
high = A.level('high', 'Research hall and alchemist, their edges (+6 m)', 6, 4)
mnr = A.level('manor', "Manor's east garden, its edge (+8 m)", 8, 4)
fh9 = A.level('fh9', 'Farmhouse: the rooms in the roof (+9 m)', 9, 4)
fhroof = A.level('fhroof', 'Farmhouse: the thatch (+10 m)', 10, 6)
loft9 = A.level('loft9', 'Barn: the hayloft (+9 m)', 9, 4)
broof = A.level('broof', 'Barn: the thatch (+10 m)', 10, 7)
byre = A.level('byre', 'Byre: its roof (+7.5 m)', 7.5, 3)
dorm = A.level('dorm', 'Farmhouse: the dormer roofs (+11.5 m)', 11.5, 2)
lamp7 = A.level('lamp7', 'Lamps on the posts (+7 m)', 7, 1)
sc7 = A.level('sc7', "Fields: the scarecrow's arms and head (+7 m)", 7, 1.5)
vane = A.level('vane', 'Barn: the weathervane (+16 m)', 16, 2.5)
wellr = A.level('wellr', 'Yard: the well, its windlass (+7 m)', 7, 1)
wellroof = A.level('wellroof', "Yard: the well's roof (+7.5 m)", 7.5, 2)
coop = A.level('coop', 'Pens: the henhouse roof (+7 m)', 7, 2)
cartload = A.level('cartload', 'Yard: the hay cart, its load (+5 m)', 5, 2.5)


def lamp(x, y, g=None):
    """A lamp post (2 m) with a lamp on top: over the floor (keeping it), or in a railing (g = its level)."""
    if g is None:
        A.overlay(up5, x, y, x + 0.5, y + 0.5, 'Refined Wood Block (lamp post)', WOOD, 2, 0)
    else:
        R(g, x, y, x + 0.5, y + 0.5, 'U')
    R(lamp7, x, y, x + 0.5, y + 0.5, P._alloc({'name': 'Yellow Luminescent Block (lamp)', 'kind': 'block', 'color': '#bd9a5f', 'height': 0.5}))

# ================================================================= the lake
# The layout's ground: out here it's all lake, the bed 4 m down.
def shoreline(x):
    return 140 + 2 * math.sin(x / 21) + 1.2 * math.sin(x / 8.3 + 1.3)


def ground(x, y):
    s = shoreline(x)
    if y < s:
        return -min(4, max(1, round((s - y) / 1.5)))
    return min(3, 1 + math.floor((y - s) / 3))


P.ground_fn(lambda mx, my: ground(mx + OX, my + OY))
for x, y in P.cells_rect(0, 0, 50, 54):
    if P.ground_at(x, y) < 0:
        lake[y][x] = '~'

# ================================================================= the farm deck (+5 m)
# The layout's 38 x 36 m of refined wood with a tarred edge, a wooden fence round its outer edges (open where
# the stairs and the herb bridge leave)
A.deck(up5, 114, 30, 152, 66, 'r', 't')
A.rail(up5, 114, 30, 152, 30.5, [(135, 139)])                       # north (the research hall's stair)
A.rail(up5, 114, 30.5, 114.5, 48, [(34, 40)])                       # west (the service stair to the manor)
A.rail(up5, 114, 65.5, 152, 66, [(124, 130), (143, 149)])           # south (the lane's stair, the herb bridge)
A.rail(up5, 151.5, 30.5, 152, 65.5)                                 # east
zone('up5', 'Farm (Farmer)', 114, 30, 152, 66, '#3f8a4f')

# ---- the stairs out: up to the manor, up to the research hall, down to the east junction, the herb bridge
# the service stair: up 3 m west from the farmhouse's kitchen door to the manor's east garden (the manor's
# hand-off: its top in the gap in the east balustrade, y 34..40), stepped stone flanks either side
R(up5, 110, 34, 114, 40, 'r')
A.stairs('up5', 'Service stair: farm to the manor', 110, 34, 116, 40, 3, 'W')
A.flanks(up5, 110, 34, 116, 40, 'W', steps=('1', '2', '3'))
R(up5, 114, 34, 119, 40, 'c')                                       # the kitchen's dooryard at its foot
zone('up5', "Kitchen dooryard (the manor's food goes up)", 116, 34, 119, 40, '#c46a2a')
# up 1 m north to the research hall (its blueprint), between stone cheeks
R(up5, 135, 28, 139, 30, 'r')
A.stairs('up5', 'Stairs up to the research hall', 135, 28, 139, 30, 1, 'N')
A.cheeks(up5, 135, 28, 139, 30, 'N')
R(up5, 135, 30, 139, 41, 'c')                                       # the alley up to it, between house and barn
# down 2 m south to the east junction (its blueprint): the lane's stair, between stone cheeks
R(walk, 124, 66, 130, 72, 'w')
A.stairs('walk', 'Stairs up to the farm', 124, 66, 130, 70, 2, 'N')
A.cheeks(walk, 124, 66, 130, 70, 'N')
# the herb bridge: from the garden's south edge over the water, up 1 m to the alchemist's garden (its blueprint)
R(up5, 143, 66, 149, 72, 'r')
A.rail(up5, 142.5, 66, 143, 72); A.rail(up5, 149, 66, 149.5, 72)
R(up5, 143, 72, 149, 74, 'r')
A.stairs('up5', 'Herb bridge: farm to the alchemist', 143, 72, 149, 74, 1, 'S')
A.cheeks(up5, 143, 72, 149, 74, 'S')
zone('up5', 'Herb bridge', 143, 66, 149, 72, '#3f8a4f')
lamp(142.5, 69, up5); lamp(149, 69, up5)

# ================================================================= the farmhouse (north-west)
# Rough stone, 16 x 10 m, its kitchen hall below (the Kitchen and the Cooking Station by the west door, the
# Oven in the east end, under its own chimney), the Farmer's rooms in the roof above wattle kneewalls, a
# thatched roof with its ridge along the farm; the kitchen door west onto the service stair's dooryard, the
# front door south onto the yard
A.walls(up5, 119, 31, 135, 41, 'S', 'r')
A.walls(fh9, 119, 31, 135, 41, 'W', 'r')
A.door('up5', 'Wooden Door', 119, 36, 119.5, 38)                   # the kitchen door, to the manor's stair
A.door('up5', 'Wooden Door', 126, 40.5, 128, 41)                   # the front door, to the yard
A.stairs('up5', 'Farmhouse stair', 128, 35, 132, 37, 4, 'E')       # up the middle to the rooms in the roof
R(fh9, 128, 35, 132, 37, ' ')
A.rail(fh9, 128, 34.5, 132, 35); A.rail(fh9, 128, 37, 132, 37.5); A.rail(fh9, 127.5, 34.5, 128, 37.5)
for x0, y0, x1, y1 in ((117.5, 32, 118.5, 33.5), (135.5, 32, 136.5, 33.5)):   # chimneys up both gables: the kitchen's
    R(up5, x0, y0, x1, y1, 'K')                                     # hearth and the oven
rf = A.roof(fhroof)
rf.gable(119, 31, 135, 41, 'x', 'straw', pitch=1.0, overhang=0.5)
# dormers for the rooms in the roof: a wattle face with a window rising out of the thatch at the eaves, cheeks
# back into the roof, a little thatched gable on top; two over the yard, one to the north
rd = A.roof(dorm)
for x0, side in ((121, 'S'), (130, 'S'), (122, 'N')):             # 3 m wide, the window on whole metres (clean at 1 m)
    fy0, fy1 = (40.5, 41) if side == 'S' else (31, 31.5)             # the face, on the wall line
    cy0, cy1 = (39.5, 40.5) if side == 'S' else (31.5, 32.5)         # the cheeks, into the roof
    R(fh9, x0, fy0, x0 + 3, fy1, 'D')
    R(fh9, x0, cy0, x0 + 0.5, cy1, 'D'); R(fh9, x0 + 2.5, cy0, x0 + 3, cy1, 'D')
    A.win('fh9', 'Wooden Window Frame', x0 + 1, fy0, x0 + 2, fy1, 0.5)
    rf.cut(x0 + 0.5, cy0 if side == 'S' else fy0 - 0.5, x0 + 2.5, fy1 + 0.5 if side == 'S' else cy1)
    rd.gable(x0, cy0 if side == 'S' else fy0 - 0.5, x0 + 3, fy1 + 0.5 if side == 'S' else cy1, 'y', 'straw', pitch=1.0, overhang=0)
rd.paint()
rf.paint()
# windows in both gables, in a stretch of taller wattle: the Farmer's room (west), the farmhands' (east)
for gx in (119, 134.5):
    R(fh9, gx, 35, gx + 0.5, 37, 'G')
    A.win('fh9', 'Wooden Window Frame', gx, 35.5, gx + 0.5, 36.5, 1)
# a wattle screen across the rooms in the roof, a gap to pass: the Farmer's room west, the farmhands' east
R(fh9, 125, 32.5, 125.5, 35, P._alloc({'name': 'Plaited Block (screen)', 'kind': 'block', 'color': '#867561', 'height': 1.5}))
R(fh9, 125, 37, 125.5, 39.5, P._alloc({'name': 'Plaited Block (screen)', 'kind': 'block', 'color': '#867561', 'height': 1.5}))
for x0 in (122.5, 124.5, 129, 131.5):                              # windows onto the yard, and over the fields' way
    A.win('up5', 'Wooden Window Frame', x0, 40.5, x0 + 1, 41, 1)
for x0 in (123, 126):
    A.win('up5', 'Wooden Window Frame', x0, 31, x0 + 1, 31.5, 1)
put('up5', 'kitchen', 119.5, 32); put('up5', 'cooking-station', 119.5, 38.5); put('up5', 'oven', 132.5, 32)
put('up5', 'npc-farmer', 129, 42.5)
# the kitchen hall: a long table with benches, a sink under the north window's neighbour, the pantry chest, a
# shelf of pots; in the bakehouse end flour sacks and the kneading table; lanterns
put('up5', 'Wooden Banquet Table', 122.5, 35.5); put('up5', 'Rustic Bench', 123, 34.5); put('up5', 'Rustic Bench', 123, 37)
put('up5', 'Wooden Sink', 121.5, 32); put('up5', 'chest-large', 119.5, 34.5, label='Large Chest (the pantry)')
put('up5', 'High Crude Wooden Shelf', 127.5, 31.5, label='High Crude Wooden Shelf (pots and crocks)')
put('up5', 'Supply Sacks I', 130, 32, label='Supply Sacks I (flour)'); put('up5', 'Supply Sacks I', 131, 32, label='Supply Sacks I (flour)')
put('up5', 'table', 132.5, 38, label='Table (for kneading)')
put('up5', 'Hanging Lantern', 124, 36); put('up5', 'Hanging Lantern', 131, 38.5)
# lived in: the farm dog's bed and bowl by the kitchen fire, the kettle on the stove, the morning's eggs on the
# table, milk from the goats by the pantry, bread dough rising on the kneading table
put('up5', 'Dog Pillow', 122, 39, label="Dog Pillow (the farm dog)"); put('up5', 'Dog Bowl', 123, 39.5)
put('up5', 'Kettle', 120, 39, z=1.5)
put('up5', 'Wooden Bowl', 123, 35.5, z=1, label='Wooden Bowl (eggs from the henhouse)')
put('up5', 'Scrap Bucket', 121.5, 34.5, label='Scrap Bucket (milk, from the goats)')
put('up5', 'Wooden Bowl', 133, 38, z=1, label='Wooden Bowl (bread dough, rising)')
# window boxes of flowers under the front windows
for x0 in (122.5, 124.5, 129, 131.5):
    A.overlay(up5, x0, 41, x0 + 1, 41.5, 'Flower Soil (window box)', '#a77e63', 0.5, 0.5)
# the rooms in the roof: the Farmer's bed against the west gable, his wardrobe and chest; the farmhands' two
# beds along the north side, a chest each
put('fh9', 'bed', 119.5, 35, label='Bed (the Farmer)'); put('fh9', 'Crude Wooden Closet', 122, 37.5)
put('fh9', 'chest-small', 121.5, 33)
put('fh9', 'bed', 125.5, 32, label='Bed (a farmhand)'); put('fh9', 'bed', 132.5, 32, label='Bed (a farmhand)')
put('fh9', 'chest-small', 126, 38); put('fh9', 'chest-small', 133.5, 38.5)
put('fh9', 'Hanging Lantern', 123, 36, z=2.5); put('fh9', 'Hanging Lantern', 130, 38, z=2.5)
# outside: lanterns at both doors; at the kitchen door a bench and a crate of vegetables waiting to go up to
# the manor; firewood stacked along the east wall in the alley, a chopping block
put('up5', 'Wall Lantern', 127, 41, 0, 3.0); put('up5', 'Wall Lantern', 118.5, 38.5, 90, 2.0)   # (the front door's over its lintel)
put('up5', 'Rustic Bench', 118, 38.5, 90, label='Rustic Bench (by the kitchen door)')
put('up5', 'Scrappy Crate', 117.5, 34.5, label='Scrappy Crate (vegetables for the manor)')
A.overlay(up5, 135.5, 34, 136.5, 37.5, 'Rough Wood Block (firewood, stacked)', '#7a6653', 1.5, 0)
A.overlay(up5, 137, 38, 137.5, 38.5, 'Rough Wood Block (chopping block)', '#7a6653', 0.5, 0)
zone('up5', 'Farmhouse kitchen and bakehouse', 120, 31.5, 134.5, 40.5, '#c46a2a')
zone('fh9', "The Farmer's rooms", 120, 32, 134, 40, '#9c6b8e')

# ================================================================= the barn (north-east)
# Tarred wood, 12 x 10 m and 5 m to the eaves, its gable to the yard with the big doors in it, a threshing
# floor of rough wood, a hayloft over its back half up a ladder, a steep thatch
A.walls(up5, 139, 31, 151, 41, 'T', 'w')
A.door('up5', 'Wooden Double Door', 143, 40.5, 147, 41)
R(loft9, 139.5, 31.5, 150.5, 36, 'w')
A.rail(loft9, 139.5, 36, 150.5, 36.5, [(140, 141)])
put('up5', 'ladder', 140, 36.5, label='Ladder up to the hayloft')
rb = A.roof(broof)
rb.gable(139, 31, 151, 41, 'y', 'straw', pitch=1.0, overhang=0.5)
rb.paint()
zone('up5', 'Barn (threshing floor)', 139.5, 36.5, 150.5, 40.5, '#9a7d55')
# (the gable fills down to the barn wall's own top, so the window sits in a stretch of that wall run up taller)
R(up5, 144, 40.5, 146, 41, P._alloc({'name': 'Tarred Wood Block (gable, round the window)', 'kind': 'wall', 'color': TAR, 'height': 7.5}))
A.win('up5', 'Round Wooden Window Frame', 144.5, 40.5, 145.5, 41, 6)
for x in (139, 150.5):
    A.win('up5', 'Wooden Window Frame', x, 37.5, x + 0.5, 38.5, 2)
for x in (142, 147.5):
    put('up5', 'Wall Lantern', x, 41, 0, 2.5)
R(vane, 144.5, 36, 145, 36.5, P._alloc({'name': 'Refined Wood Block (weathervane post)', 'kind': 'block', 'color': WOOD, 'height': 1.5}))
R(vane, 144.5, 35, 145, 36, P._alloc({'name': 'Iron Block (weathervane, the arrow)', 'kind': 'block', 'color': '#848483', 'height': 0.5, 'base': 1.5}))
R(vane, 144.5, 36.5, 145, 37.5, P._alloc({'name': 'Iron Block (weathervane, the cockerel)', 'kind': 'block', 'color': '#848483', 'height': 1, 'base': 1.5}))
# hay stacked in the loft (clear of the ladder's top), grain sacks and bundles under it, a shelf of tools
A.overlay(loft9, 141.5, 31.5, 150.5, 34.5, 'Straw Roof Block (hay, stacked)', '#a7753d', 1, 0)
A.overlay(loft9, 143, 34.5, 149, 35.5, 'Straw Roof Block (hay, stacked)', '#a7753d', 0.5, 0)
for x in (144, 145, 146):
    put('up5', 'Supply Sacks I', x, 32, label='Supply Sacks I (grain)')
put('up5', 'Resource Bundle I', 148, 32, label='Resource Bundle I (straw)'); put('up5', 'Resource Bundle II', 149, 32)
put('up5', 'Low Crude Wooden Shelf', 150, 34, 90, label='Low Crude Wooden Shelf (tools)')
put('up5', 'Hanging Lantern', 145, 38)
zone('loft9', 'Hayloft', 139.5, 31.5, 150.5, 36, '#9a7d55')

# ================================================================= the yard and the lane
# The farmyard runs the width of the farm between the buildings and the animals and fields, paved in field
# stones; the lane (dirt) goes south from it to the junction's stair
R(up5, 114.5, 41, 151.5, 48, 'c')
zone('up5', 'Farmyard', 114.5, 41, 151.5, 48, '#9a7d55')
# the well in the yard: a stone ring over a shaft down through the deck to the lake, posts and a windlass with
# its bucket, a little thatched roof
R(up5, 139.5, 43.5, 140.5, 44.5, ' ')
for x, y in P.cells_rect(139 - OX, 43 - OY, 141 - OX, 45 - OY):
    if up5[y][x] != ' ':
        up5[y][x] = P._alloc({'name': 'Rough Stone Block (well ring)', 'kind': 'block', 'color': RS, 'height': 1})
for x in (138.5, 141):
    A.overlay(up5, x, 43.5, x + 0.5, 44.5, 'Refined Wood Block (well post)', WOOD, 2.5, 0)
R(wellr, 139, 43.5, 141, 44, P._alloc({'name': 'Refined Wood Block (windlass)', 'kind': 'block', 'color': WOOD, 'height': 0.5}))
A.overlay(up5, 139.5, 44, 140, 44.5, 'Tarred Wood Block (the bucket, in the shaft)', TAR, 0.5, 1)
rw = A.roof(wellroof)
rw.gable(138.5, 42.5, 141.5, 45.5, 'x', 'straw', pitch=1.0, overhang=0)
rw.paint()
zone('up5', 'Well', 138.5, 42.5, 141.5, 45.5, '#9a7d55')
# the hay cart by the barn: two wheels, its bed, shafts down on the stones, a load of hay
for x in (147.5, 150):
    A.overlay(up5, x, 43.5, x + 0.5, 44.5, 'Tarred Wood Block (cart wheel)', TAR, 1, 0)
A.overlay(up5, 148, 42.5, 150, 45, 'Refined Wood Block (cart bed)', WOOD, 0.5, 0.5)
for x in (148, 149.5):
    A.overlay(up5, x, 45, x + 0.5, 46, 'Refined Wood Block (cart shafts)', WOOD, 0.5, 0)
R(cartload, 148, 42.5, 150, 44.5, P._alloc({'name': 'Straw Roof Block (hay on the cart)', 'kind': 'block', 'color': '#a7753d', 'height': 1, 'base': 1}))
zone('up5', 'Hay cart', 147.5, 42.5, 150.5, 46, '#9a7d55')
lamp(117, 40); lamp(118.5, 47.5); lamp(133.5, 47.5); lamp(150.5, 47.5)
R(up5, 124, 48, 130, 65.5, 'd')
R(up5, 124, 65.5, 130, 66, 'd')
zone('up5', 'Lane (down to the east junction)', 124, 48, 130, 66, '#8c7455')
lamp(130.5, 65)

# ================================================================= the animals (south-west)
# A byre along the west edge (posts at its front, a wattle back wall, a thatched lean-to sloping down to the
# west) sheltering the beds; in front of it three fenced pens on dirt, a gate from each onto the lane:
# the yaks (big beds, the yak feeder), the goats, the birds (redtails for eggs)
R(up5, 114.5, 48, 123.5, 65.5, 'e')
R(up5, 114, 48, 114.5, 65.5, 'b')
for y in (55, 60):                                                  # fences between the pens, under the byre too
    A.rail(up5, 114.5, y, 123.5, y + 0.5)
A.rail(up5, 123.5, 48, 124, 65.5, [(50, 52), (57, 59), (62, 64)])  # the fence along the lane, a gate to each pen
for y in (50, 57, 62):
    put('up5', 'Crude Wooden Gate I', 123.5, y, 90, label='Crude Wooden Gate I (shut)')
A.rail(up5, 114.5, 48, 123.5, 48.5)                                 # and along the yard
for y in (48, 52, 56, 60, 65):                                      # the byre's posts (after the fences)
    R(up5, 116.5, y, 117, y + 0.5, 'n')
rby = A.roof(byre)
rby.shed(114, 48, 117.5, 65.5, 'w', 'straw', pitch=0.5, overhang=0.5)
rby.paint()
PENS = (('Yaks', 48.5, 55), ('Goats', 55.5, 60), ('Birds (redtails)', 60.5, 65.5))
for name, y0, y1 in PENS:
    zone('up5', f'Pen: {name.lower()}', 117, y0, 123.5, y1, '#a0905a')
put('up5', 'Big Farm Animal Pillow', 114.5, 49); put('up5', 'Big Farm Animal Pillow', 114.5, 52)
put('up5', 'Yak Feeder', 121, 49, 270)
put('up5', 'Farm Animal Pillow', 115, 56.5); put('up5', 'Farm Animal Pillow', 115, 58)
put('up5', 'Goat Feeder', 121, 56, 270)
put('up5', 'Farm Animal Pillow', 115, 61); put('up5', 'Farm Animal Pillow', 115, 62.5)
put('up5', 'Bird Feeder', 121.5, 61)
put('up5', 'trough', 121, 52.5, 270, label='Water Trough (the yaks)')
zone('up5', 'Byre (the beds, under cover)', 114.5, 48.5, 117, 65.5, '#a0905a')
A.overlay(up5, 119, 63, 121, 65, 'Rough Wood Block (henhouse)', '#7a6653', 1.5, 0.5)    # on legs, a ramp up
A.overlay(up5, 121, 63.5, 121.5, 64.5, 'Rough Wood Block (henhouse ramp)', '#7a6653', 0.5, 0)
rc = A.roof(coop)
rc.gable(118.5, 62.5, 121.5, 65.5, 'x', 'straw', pitch=1.0, overhang=0)
rc.paint()
zone('up5', 'Henhouse', 119, 63, 121.5, 65, '#a0905a')
A.overlay(up5, 117.5, 49, 119.5, 49.5, 'Straw Roof Block (hay in the rack)', '#a7753d', 1, 0.5)
put('up5', 'Scrap Bucket', 122.5, 58.5, label='Scrap Bucket (water)'); put('up5', 'Scrap Bucket', 118, 61, label='Scrap Bucket (water)')

# ================================================================= the fields and the garden (south-east)
# Fields of farm soil in four plots, a path between them; the garden: seedbeds by the yard, then the apiary
# (beehives on flower soil) down to the herb bridge, a path down its middle
R(up5, 131, 48, 143, 65.5, 'F')
R(up5, 136.5, 48, 137.5, 65.5, 'd'); R(up5, 131, 56.5, 143, 57.5, 'd')
zone('up5', 'Fields', 131, 48, 143, 65.5, '#6f8a43')
# crops in rows, a row every metre (what grows where, for planting in game): wheat and flax by the yard,
# vegetables to the south, the fourth plot turned and lying fallow with the plough in it
CROPS = ((131, 48, 136.5, 56.5, 'Straw Roof Block (wheat)', '#a7753d', 1),
         (137.5, 48, 143, 56.5, 'Palm Leaf Roof Block (flax)', '#898870', 1),
         (131, 57.5, 136.5, 65.5, 'Foliage (cabbages and beans)', '#668f27', 0.5))
for x0, y0, x1, y1, name, color, h in CROPS:
    x = x0 + 0.5
    while x < x1 - 0.25:
        A.overlay(up5, x, y0 + 0.5, x + 0.5, y1 - 0.5, name, color, h, 0)
        x += 1
put('up5', 'Plough', 139, 61, label='Plough (the fallow plot)')
zone('up5', 'Wheat', 131, 48, 136.5, 56.5, '#a7753d'); zone('up5', 'Flax', 137.5, 48, 143, 56.5, '#898870')
zone('up5', 'Vegetables', 131, 57.5, 136.5, 65.5, '#668f27'); zone('up5', 'Fallow', 137.5, 57.5, 143, 65.5, '#90450d')
# a scarecrow in the wheat: a post, straw arms across it and a straw head
A.overlay(up5, 133, 52, 133.5, 52.5, 'Rough Wood Block (scarecrow post)', '#7a6653', 2.5, 0)
for x in (132, 132.5, 133.5, 134):
    R(sc7, x, 52, x + 0.5, 52.5, P._alloc({'name': "Straw Roof Block (the scarecrow's arms)", 'kind': 'block', 'color': '#a7753d', 'height': 0.5}))
R(sc7, 133, 52, 133.5, 52.5, P._alloc({'name': "Straw Roof Block (the scarecrow's head)", 'kind': 'block', 'color': '#a7753d', 'height': 0.5, 'base': 0.5}))
R(up5, 143, 48, 151.5, 65.5, 'o')
R(up5, 145, 48, 147, 66, 'd')
for (x, y) in ((143, 49), (143, 52), (147.5, 49), (147.5, 52), (149.5, 49), (149.5, 52)):
    put('up5', 'seedbed', x, y)
zone('up5', 'Nursery (seedbeds)', 143, 48, 151.5, 55, '#6f8a43')
for (x, y) in ((143, 57), (143, 61), (148.5, 57), (148.5, 61)):
    put('up5', 'Beehive', x, y, label='Beehive (honey and wax; a 2 x 2 m placeholder)')
zone('up5', 'Apiary (beehives on flower soil)', 143, 56, 151.5, 65.5, '#d4a017')
put('up5', 'table', 143, 54.5, label='Table (potting)'); put('up5', 'Scrap Pot I', 143.5, 54.5, z=1); put('up5', 'Scrap Pot II', 144.5, 55, z=1)
put('up5', 'Scrap Vat I', 150.5, 54.5, label='Scrap Vat I (a water butt)')
put('up5', 'Bench', 147, 59, 90, label='Bench (among the hives)')
lamp(147, 55.5)

# ================================================================= the neighbours' edges (their own blueprints)
R(mnr, 106, 30, 110, 42, 'L')                                       # the manor's east garden and its path
zone('manor', "Manor's east garden (manor blueprint)", 106, 30, 110, 42, '#8a5cc2')
R(high, 118, 24, 150, 28, 'g')                                      # the research hall's south edge
zone('high', 'Research hall (its blueprint)', 118, 24, 150, 28, '#56806c')
for x, y in P.cells_rect(136 - OX, 74 - OY, 156 - OX, 78 - OY):    # the alchemist's round platform
    if math.hypot(OX + x / 2 + 0.25 - 146, OY + y / 2 + 0.25 - 84) <= 10:
        high[y][x] = 'g'
zone('high', 'Alchemist (its blueprint)', 138, 74, 154, 78, '#56806c')
R(high, 143, 74, 149, 76, 'g')                                      # the landing the herb bridge needs (its blueprint)
R(walk, 116, 72, 130, 78, 'w')                                      # the east junction's north edge
zone('walk', 'East junction (its blueprint)', 116, 72, 130, 78, '#2f8f8a')

# ================================================================= stilts, rim beams and checks
print('stilts:', A.stilts(stl, [('walk', 3), ('up5', 5), ('high', 6), ('manor', 8)]))
own = lambda x, y: 110 <= x < 152 and 30 <= y < 74
print('rim beam squares:', A.rim_beams(stl, [('up5', 5)], own))
A.spawn('up5', 126.5, 46.5, 180)                                 # walk mode starts here: the top of the lane, facing the farmhouse
A.checks()

NOTES = """Laketown: the farm, as a 0.5 m detail blueprint. Pass 3 of 3 (review and finishing touches): done. Drafted by Claude.
This plan's corner is the layout's (106, 24), so it lines up with the Laketown layout and stamps back into the site plan there.

PASSES
1. Design and bones: the farm deck and its fence, the four ways out (the service stair to the manor, the stairs to the research hall and the east junction, the herb bridge), the farmhouse and the barn with floors, doors, stairs and roofs, the yard and the lane, the byre and the pens, the fields, the nursery and the apiary, the stations; the neighbours' edges, stilts, labels.
2. Details: dormers and gable windows, the rooms, the barn's window, weathervane, hay and grain, the well, the hay cart, crops and a scarecrow, the henhouse, hay rack and water, the garden's potting table, lamps; then a 3D review and a refining round.
3. Review and finishing touches (done): gates in the pens' openings (they were bare gaps), the farm dog by the kitchen fire, the kettle on the stove, eggs, milk and rising dough, window boxes under the front windows; the layout redrawn as built; the hand-offs for the research hall, the east junction and the alchemist.

THE IDEA: the Farmer's farmstead at +5 m on the town's east side, round a farmyard that runs its width. Its kitchen feeds the manor: the kitchen door opens onto the foot of the service stair, so food goes straight up to the house.

THE FARMHOUSE (north-west): rough stone, 16 x 10 m, under a thatched roof (45 degrees) with its ridge along the farm, chimneys up both gables.
- Below, the kitchen hall: the Kitchen and the Cooking Station by the west door, a sink, the pantry chest, a long table with benches, a shelf of pots; the Oven in the east end (the bakehouse) under its own chimney, with flour sacks and a kneading table. Lanterns.
- Above, the rooms in the roof over wattle kneewalls, up a stair through the middle of the house, a wattle screen between them: the Farmer's (his bed against the west gable, a wardrobe, a chest) and the farmhands' (two beds, a chest each). Light from three thatched dormers (two over the yard, one to the north) and a window in each gable.
- The kitchen door west onto the dooryard at the service stair's foot (a lantern, a bench, a crate of vegetables waiting to go up to the manor); the front door south onto the yard (a lantern). Firewood stacked along the east wall in the alley, a chopping block.

THE BARN (north-east): tarred wood, 12 x 10 m and 5 m to the eaves, its gable to the yard with a double door in it (lanterns either side) and a round window high above, a threshing floor of rough wood, side windows, a hayloft over its back half up a ladder, stacked with hay; grain sacks, straw bundles and a shelf of tools below; a steep thatch with a weathervane (an arrow and a cockerel) on the ridge.

THE YARD AND THE LANE: the farmyard (field stones) runs the width of the farm between the buildings and the animals and fields: the well (a stone ring over a shaft down through the deck to the lake, a windlass and its bucket, a little thatched roof), a hay cart by the barn, lamps. The lane (dirt) runs south from it to the stair down to the east junction. The alley between the house and the barn leads north to the research hall's stair.

THE ANIMALS (south-west): a byre along the west edge (posts at its front, a wattle back wall, a thatched lean-to) sheltering the beds, so they count as under cover; three fenced pens in front of it on dirt, each with a gate (shut) onto the lane: the yaks (two big beds, the yak feeder, a water trough, a hay rack), the goats (two beds, the goat feeder, a bucket of water), the birds (two beds, the bird feeder, a bucket of water, and a henhouse on legs with a ramp, under a little thatch).

THE FIELDS AND THE GARDEN (south-east): four plots of farm soil with paths between, the crops in rows a metre apart (what grows where, for planting in game): wheat and flax by the yard, cabbages and beans to the south, the fourth plot turned and lying fallow with the plough in it; a scarecrow in the wheat. The garden: six seedbeds (the nursery) with a potting table and its pots and a water butt, then the apiary, four beehives on flower soil with a bench among them, down to the herb bridge, a path and a lamp down its middle.

CONNECTIONS
- West: the service stair (x 110..116, y 34..40), up 3 m to the manor's east garden, between stepped stone flanks; its top lands in the gap in the manor's east balustrade, on the manor's gravel service path (the manor blueprint's hand-off).
- North: up 1 m to the research hall (x 135..139, y 28..30), between stone cheeks (its blueprint matches it).
- South: the lane's stair down 2 m to the east junction (x 124..130, y 66..70), between stone cheeks; its foot lands on the junction at y 70..72 (the junction's blueprint matches it). The layout had it at x 118..124.
- South-east: the herb bridge (x 143..149, lamps in its railings) over the water, then up 1 m (y 72..74) to the alchemist's garden. Its round platform only touches y 74 at x 146, so its blueprint needs a landing across x 143..149, y 74..76 (drawn here as its edge).

HAND-OFF FOR THE RESEARCH HALL (area 10): the farm's stair rises 1 m north (x 135..139, y 28..30, stone cheeks) onto its deck (+6 m) at y 28. Keep 1 m clear at its top (y 27..28). The alley between the farmhouse and the barn leads to it.

HAND-OFF FOR THE EAST JUNCTION (area 11): the farm's stair now comes down 2 m at x 124..130 (y 66..70, stone cheeks), on the lane's line, not the layout's x 118..124. Its foot lands on a landing at y 70..72 (+3 m, drawn here); keep 1 m clear there. The old spot is open water now.

HAND-OFF FOR THE ALCHEMIST (area 11): the herb bridge (x 143..149) rises 1 m south (y 72..74) onto the alchemist's garden. Its round platform only touches y 74 at x 146, so it needs a landing across x 143..149, y 74..76 (+6 m, polished granite, drawn here as its edge), and 1 m clear there.

1.0's FARM (enshrouded.tools, the wiki): the Farmer makes the Seedbed, Cooking Station, Oven and Kitchen, the Beehive (honey and wax), and the animals' beds and feeders. Farm animals need a bed within 50 m that counts as sheltered (20% cover) and their own feeder (both goats share the Goat Feeder, both birds the Bird Feeder; yaks need the Big Farm Animal Pillow). There is no pen item: a pen is fences and a gate round them.

CROPS, the scarecrow, the hay and the well's windlass are drawn in blocks, to show where things go; plant and furnish in game.

SIZES: the stations (Kitchen, Cooking Station, Oven, Seedbed, Beehive) are 2 x 2 m placeholders until measured; the beds, feeders, trough and furniture are estimates.

STILTS: 1 m posts on the layout's 4 m grid, from the lake bed 4 m down to each deck's underside; tarred rim beams under the edges.
"""
A.save('laketown_farm.json', NOTES, 'r-claude-laketown-farm-3')
