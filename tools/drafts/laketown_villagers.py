"""Laketown: the villagers' quarter, 0.5 m detail plan. Pass 3 of 3: review and finishing touches (done).

The NW corner at +5 m, up a short stair from the smithy: eight homes for the ten villagers round a village
green with a well, the dining hall at the head of the green, allotments, and back steps from the south-east
corner down to the west landing (+4 m), so the quarter isn't a dead end.

Pass 1 laid out the bones. Pass 2 reshaped it so nothing is cramped (the deck grows to the build area's edge
on the west and north; every home has at least 6 x 6 m inside; the hall moved to the head of the green, on
the line of the way in) and added the detail: stone plinths under the timber and wattle walls, windows,
window boxes, door hoods on brackets, gable windows, chimney caps and pots, ridges, furniture and lights,
gardens, an entrance gateway with the quarter's sign, a notice board, a windlass over the well. Pass 3 reviewed
it: lanterns out of the hood brackets, a kitchen door for the hall, the back steps' bench turned to the view, a
signpost, lanterns and firewood in the passages, a weathervane on the bell-cote; the layout now matches.

The homes vary on purpose (a village grows a house at a time): wattle, timber, stone and tarred walls;
thatch, tile, stone shingle, tarred shingle and tarred straw roofs; ridges both ways; two two-storey family
houses (the Reeds' jettied over its yard).

Coordinates are the layout's (doc `laketown`): this plan's corner is the layout's (2, 2).
Run: python laketown_villagers.py  ->  writes laketown_villagers.json
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laketown_common import Area, WOOD, STONE
from mage_common import ROOF_MATS

ROOF_MATS.setdefault('fibre', ('Plant Fiber Roof Block', '#725e4f'))     # thatch ridges

RS, RCS, LIME, TAR, HT, BT = '#7d776a', '#62605d', '#a79a88', '#5d5652', '#71665e', '#947f75'
A = Area("Laketown: villagers' quarter (detail)", 2, 2, 54, 42, {
    'd': {'name': 'Dirt Road Block', 'kind': 'floor', 'color': '#8c7455'},             # lanes and paths
    'c': {'name': 'Field Stones', 'kind': 'floor', 'color': '#8a8170'},                # the forecourt, the way in
    'a': {'name': 'Farm Soil', 'kind': 'floor', 'color': '#90450d'},                   # the allotments
    'e': {'name': 'Flower Soil', 'kind': 'floor', 'color': '#a77e63'},                 # flower beds
    'b': {'name': 'Fired Bricks Block', 'kind': 'floor', 'color': '#aa7657'},          # the smithy (its blueprint)
    'k': {'name': 'Roughly Cut Stone Block', 'kind': 'floor', 'color': RCS},           # its edge
    'p': {'name': 'Roughly Cut Stone Block (parapet)', 'kind': 'block', 'color': RCS, 'height': 1},
    'o': {'name': 'Roughly Cut Stone Block (pier)', 'kind': 'block', 'color': RCS, 'height': 1.5},
    # walls: stone plinths (1 m) under the timber, wattle and tarred walls, which stand on them
    'Q': {'name': 'Rough Stone Block (plinth)', 'kind': 'wall', 'color': RS, 'height': 1},
    'A': {'name': 'Plaited Block', 'kind': 'wall', 'color': '#867561', 'height': 3, 'base': 1},
    'H': {'name': 'Half-Timbered Block', 'kind': 'wall', 'color': HT, 'height': 3, 'base': 1},
    'R': {'name': 'Rough Wood Block', 'kind': 'wall', 'color': '#7a6653', 'height': 3, 'base': 1},
    'X': {'name': 'Tarred Wood Block', 'kind': 'wall', 'color': TAR, 'height': 3, 'base': 1},
    'K': {'name': 'Brick-Timbered Block', 'kind': 'wall', 'color': BT, 'height': 5, 'base': 1},
    'j': {'name': 'Half-Timbered Block (party wall)', 'kind': 'wall', 'color': HT},
    'S': {'name': 'Rough Stone Block', 'kind': 'wall', 'color': RS},
    'L': {'name': 'Limestone Block', 'kind': 'wall', 'color': LIME},
    'B': {'name': 'Brick-Timbered Block (upper floor)', 'kind': 'wall', 'color': BT},
    'J': {'name': 'Half-Timbered Block (upper floor)', 'kind': 'wall', 'color': HT},
    # gable middles raised for a round window
    'g': {'name': 'Brick-Timbered Block (gable)', 'kind': 'wall', 'color': BT, 'height': 6.5, 'base': 1},
    'm': {'name': 'Plaited Block (gable)', 'kind': 'wall', 'color': '#867561', 'height': 5.5, 'base': 1},
    's': {'name': 'Rough Stone Block (gable)', 'kind': 'wall', 'color': RS, 'height': 6.5},
    # the well, the bell-cote, the gateway
    'W': {'name': 'Well Block (kerb)', 'kind': 'block', 'color': '#586256', 'height': 1},
    'V': {'name': 'Well Block (shaft lining)', 'kind': 'block', 'color': '#586256', 'height': 4.5, 'base': 4},
    'n': {'name': 'Refined Wood Block (well post)', 'kind': 'block', 'color': WOOD, 'height': 3},
    'v': {'name': 'Refined Wood Block (windlass)', 'kind': 'block', 'color': WOOD, 'height': 0.5, 'base': 2},
    'q': {'name': 'Limestone Block (bell-cote pier)', 'kind': 'block', 'color': LIME, 'height': 3},
    'Z': {'name': 'Bronze Block (bell)', 'kind': 'block', 'color': '#8b7852', 'height': 1, 'base': 1.5},
    'N': {'name': 'Refined Wood Block (gate post)', 'kind': 'block', 'color': WOOD, 'height': 3.5},
    'l': {'name': 'Yellow Luminescent Block (lamp)', 'kind': 'block', 'color': '#bd9a5f', 'height': 0.5},
    'x': {'name': 'Refined Wood Block (window box)', 'kind': 'block', 'color': WOOD, 'height': 0.5, 'base': 0.5},
    'F': {'name': 'Foliage (hedge)', 'kind': 'block', 'color': '#668f27', 'height': 1},
})
P, R, zone, put = A.P, A.R, A.zone, A.put
stl = A.level('stilts', 'Stilts, standing on the lake bed (-4 m)', -4, 12)
lake = A.level('lake', 'Lake (water level, 0 m)', 0, 1)
mid = A.level('mid', 'Smithy edge, stairs, west landing (+4 m)', 4, 4)
up5 = A.level('up5', "Villagers' quarter: deck, ground floors (+5 m)", 5, 4)
PL = A.level('plinth', 'Plinths and thresholds (+5 m)', 5, 1)
hood = A.level('hood', 'Door hoods (+7.5 m)', 7.5, 2)
well8 = A.level('well8', 'The well: its roof (+8 m)', 8, 2)
mnr = A.level('manor', 'Manor grounds, their edge (+8 m)', 8, 5)
gate = A.level('gate', 'The gateway: its lamps (+8.5 m)', 8.5, 1)
up9 = A.level('up9', 'Upper floors: the Godwins and the Reeds (+9 m)', 9, 3.5)
roof9 = A.level('roof9', 'Cottage roofs (+9 m)', 9, 6)
roof11 = A.level('roof11', 'Dining hall roof (+11 m)', 11, 7)
roof125 = A.level('roof125', 'The family houses: roofs (+12.5 m)', 12.5, 6)

# ================================================================= the lake (bed 4 m down)
P.ground_rect(0, 0, 54, 42, -4)
R(lake, 2, 2, 56, 44, '~')

# ================================================================= the deck (+5 m)
# 43 x 31 m of refined wood on a tarred edge, out to the build area's edge on the west and north (the layout
# had 36 x 28), with a wooden railing round it, open where the smithy's stair arrives and the back steps leave
A.deck(up5, 3, 3, 46, 34, 'r', 't')
A.rail(up5, 3, 3, 46, 3.5); A.rail(up5, 3, 3.5, 3.5, 33.5)
A.rail(up5, 3, 33.5, 44, 34, [(20, 26)]); A.rail(up5, 45.5, 3.5, 46, 30)
zone('up5', "Villagers' quarter", 3, 3, 46, 34, '#9c6b8e')

# lanes round the green: the forecourt in front of the hall, a lane down each side, the south lane along the
# south row on to the back steps, and the way in from the smithy's stair
R(up5, 3.5, 24, 45.5, 26, 'd')                          # south lane
R(up5, 42.5, 26, 45.5, 33.5, 'd')                       # on to the back steps
R(up5, 12, 13.5, 14, 24, 'd'); R(up5, 32, 13.5, 34, 24, 'd')
R(up5, 12, 13.5, 34, 16, 'c')                           # the forecourt
R(up5, 20, 26, 26, 33, 'c')                             # the way in
R(up5, 13, 4, 15.5, 13.5, 'd'); R(up5, 31, 4, 33.5, 13.5, 'd')     # paths up the passages to the lake
zone('up5', 'Forecourt', 12, 13.5, 34, 16, '#b8862b')

# ---- the green: grass on the line of the way in, a field stone path across it to the well and the hall's
# door, flower beds in the corners, lanterns, benches facing the well
R(up5, 14, 16, 32, 24, 'G')
R(up5, 22, 16, 24, 24, 'c')
A.circle(up5, 23, 20, 5, 'c')
for x0, y0 in ((14.5, 16.5), (29.5, 16.5), (14.5, 22), (29.5, 22)):
    R(up5, x0, y0, x0 + 2, y0 + 1.5, 'e')
for x, y in ((14, 16), (31.5, 16), (14, 23.5), (31.5, 23.5)):
    put('up5', 'Ground Lantern II', x, y)
put('up5', 'Bench', 19.5, 19, 270); put('up5', 'Bench', 26, 19, 90)
zone('up5', 'Village green', 14, 16, 32, 24, '#3f8a4f')
# the notice board, by the path up from the way in
A.overlay(up5, 25, 23, 25.5, 23.5, 'Refined Wood Block (notice board post)', WOOD, 2, 0)
A.overlay(up5, 26.5, 23, 27, 23.5, 'Refined Wood Block (notice board post)', WOOD, 2, 0)
A.overlay(up5, 25.5, 23, 26.5, 23.5, 'Tarred Wood Block (notice board)', TAR, 1.5, 0.5)

# ---- the well: a round kerb of well block over a shaft through the deck to the lake (lined down to the
# water), two posts carrying a windlass, a little thatched roof
A.circle(up5, 23, 20, 3, 'W')
A.circle(up5, 23, 20, 2, ' ')
R(up5, 21.5, 19.5, 22, 20.5, 'n'); R(up5, 24, 19.5, 24.5, 20.5, 'n')
R(up5, 22, 19.5, 24, 20, 'v')                           # the windlass, over the shaft
rw = A.roof(well8)
rw.gable(21.5, 19.5, 24.5, 20.5, 'x', 'straw', pitch=1.0, overhang=0.5)
rw.paint()
zone('up5', 'The well (down to the lake)', 21.5, 18.5, 24.5, 21.5, '#3f7f9e')

# ---- the way in: a timber gateway at the top of the smithy's stair, the quarter's sign hanging in the
# middle of its beam, lamps on the posts
R(up5, 19.5, 32.5, 20, 33, 'N'); R(up5, 26, 32.5, 26.5, 33, 'N')
A.overlay(up5, 20, 32.5, 22, 33, 'Refined Wood Block (gate beam)', WOOD, 0.5, 3)
A.overlay(up5, 24, 32.5, 26, 33, 'Refined Wood Block (gate beam)', WOOD, 0.5, 3)
A.overlay(up5, 22, 32.5, 24, 33, "Tarred Wood Block (the quarter's sign)", TAR, 1, 2.5)
R(gate, 19.5, 32.5, 20, 33, 'l'); R(gate, 26, 32.5, 26.5, 33, 'l')
put('up5', 'Ground Lantern II', 19.5, 26.5); put('up5', 'Ground Lantern II', 26, 26.5)
zone('up5', 'The way in (gateway)', 20, 26, 26, 33, '#b8862b')

# ---- the allotments, east of the stone cottage: farm soil with three seedbeds
R(up5, 43.5, 15.5, 45.5, 23.5, 'a')
for y in (16, 18.5, 21):
    put('up5', 'seedbed', 43.5, y, label="Seedbed (villagers' plot)")
zone('up5', 'Allotments (seedbeds)', 43.5, 15.5, 45.5, 23.5, '#6f8a43')

# lake-view benches at the north end of the passages either side of the hall
put('up5', 'Bench', 13, 3.5, 180); put('up5', 'Bench', 31.5, 3.5, 180)

# ================================================================= building helpers
ROOFS, CHIMNEYS = {}, []                                # building -> (roof elevation, roof helper, outline)


def shell(x0, y0, x1, y1, wall, plinth=True, g=None, floor='r'):
    """A building's outer walls (0.5 m) with a floor inside; on a 1 m stone plinth when the wall stands on one."""
    if plinth:
        A.walls(PL, x0, y0, x1, y1, 'Q')
    A.walls(g or up5, x0, y0, x1, y1, wall, floor)


def door(name, x0, y0, x1, y1, plinth=True):
    if plinth:
        R(PL, x0, y0, x1, y1, 'r')                       # the plinth stops for the threshold
    A.door('up5', name, x0, y0, x1, y1)


def chimney(x0, y0, x1, y1, building, through=()):
    """A rough stone stack from the deck, rising a metre above its building's ridge; cut through the roof and
    any upper walls it passes."""
    CHIMNEYS.append((x0, y0, x1, y1, building))
    for g in through:
        R(g, x0, y0, x1, y1, ' ')


def wbox(g, x0, y0, x1, y1):
    """A window box under a window, outside (overlaid on the ground floor's floor; hanging upstairs)."""
    if g is up5:
        A.overlay(up5, x0, y0, x1, y1, 'Refined Wood Block (window box)', WOOD, 0.5, 0.5)
    else:
        R(g, x0, y0, x1, y1, 'x')


HOODS = []


def door_hood(x0, y0, x1, y1, out, mat='tiles'):
    """A little shed roof over a door (the door's wall squares x0..x1, y0..y1), 1 m out on side `out`, on two
    brackets."""
    HOODS.append((x0, y0, x1, y1, out, mat))


def home(label, x0, y0, x1, y1, color='#9c6b8e'):
    zone('up5', label, x0, y0, x1, y1, color)


# ================================================================= the dining hall, at the head of the green
# Brick-timbered on a stone plinth, 6 m walls, a tiled roof; an entrance bay on the line of the way in, its
# gable carrying a round window and the bell-cote. Inside: the kitchen along the back wall (Cooking Station,
# Kitchen, a sink, the Oven under its own chimney, the pantry), a serving counter with a gap in the middle,
# two long tables with benches either side of the aisle, a big hearth, a dresser, lanterns.
shell(16, 4, 30, 13.5, 'K')
shell(19, 13, 27, 14.5, 'K')                            # the entrance bay
R(up5, 19.5, 13, 26.5, 13.5, 'r'); R(PL, 19.5, 13, 26.5, 13.5, ' ')    # open to the hall
R(up5, 22, 14, 24, 14.5, 'g')                           # the bay's gable middle, up for the round window
door('Wooden Double Door', 21, 14, 25, 14.5)
A.win('up5', 'Round Wooden Window Frame', 22.5, 14, 23.5, 14.5, 6)
for x in (17, 28):
    A.win('up5', 'Wooden Window Frame', x, 13, x + 1, 13.5, 1.5)          # south, either side of the bay
for y in (5.5, 11):
    A.win('up5', 'Wooden Window Frame', 16, y, 16.5, y + 1, 2)             # west
A.win('up5', 'Wooden Window Frame', 29.5, 11, 30, 12, 2)                 # east
# the kitchen door, into the east passage: deliveries from the back steps and the allotments
door('Wooden Door', 29.5, 5.5, 30, 7.5)
door_hood(29.5, 5.5, 30, 7.5, 'e', 'tiles')
put('up5', 'Wall Lantern', 30, 8, 90, 2.0)
put('up5', 'Ground Lantern II', 15, 7.5); put('up5', 'Ground Lantern II', 30.5, 10)     # up the passages
put('up5', 'Resource Bundle I', 15, 10, label='Resource Bundle I (firewood, by the hearth)')
for x in (21, 24):
    A.win('up5', 'Wooden Window Frame', x, 4, x + 1, 4.5, 2.5)             # north, high over the kitchen
chimney(15.5, 9, 16.5, 10, 'hall'); chimney(26, 3.5, 27, 4.5, 'hall')
put('up5', 'Stone Fireplace', 16.5, 8.5, 270)
put('up5', 'cooking-station', 17, 4.5); put('up5', 'kitchen', 19.5, 4.5)
put('up5', 'Wooden Sink', 22, 4.5); put('up5', 'oven', 25.5, 4.5)
put('up5', 'chest-large', 27.5, 4.5, label='Large Chest (the pantry)')
for x in (17, 19, 25, 27):
    put('up5', 'Wooden Tavern Counter', x, 7.5)
for tx in (19.5, 25.5):                                 # the tables, a bench either side
    put('up5', 'Wooden Banquet Table', tx, 9.5, 90)
    put('up5', 'Rustic Bench', tx - 0.5, 10, 90); put('up5', 'Rustic Bench', tx + 1, 10, 90)
    put('up5', 'Ceiling Lantern', tx, 11)
put('up5', 'Large Carved Wooden Cabinet', 28.5, 9, 90, label='Large Carved Wooden Cabinet (the dresser)')
put('up5', 'Ceiling Lantern', 23, 6)
put('up5', 'Wall Lantern', 19.5, 14.5, 0, 2.0); put('up5', 'Wall Lantern', 26, 14.5, 0, 2.0)    # at the bay's corners
put('up5', 'Bench', 17, 13.5); put('up5', 'Bench', 27, 13.5)              # against the front, facing the green
ROOFS['hall'] = (11, None, (16, 4, 30, 14.5))
zone('up5', 'Dining hall (food stations)', 16, 4, 30, 14.5, '#c46a2a')
zone('up5', 'Kitchen', 16.5, 4.5, 29.5, 7.5, '#c46a2a')

# ================================================================= the homes
# Eight homes for the ten villagers (enshrouded.tools/survivors). The two families share: Hannah and
# Marianne Reed, Oscar and Anton Godwin. The names on the beds are suggestions; assign them in game with the
# Summoning Staff.

# ---- the Godwins' house (NW): two storeys, limestone below, brick-timbered above, a tarred shingle hip;
# the door to its front garden on the south (a dog's bed by it), a stair up the back wall
shell(4, 4, 12, 12, 'L', plinth=False)
door('Wooden Door', 7, 11.5, 9, 12, plinth=False)
A.stairs('up5', "The Godwins' stair", 6, 5, 10, 6, 4, 'W')        # (0.5 m off the wall: whole metres for the site map)
chimney(3.5, 8, 4.5, 9, 'godwins', through=(up9,))
put('up5', 'Stone Fireplace', 4.5, 7.5, 270)
put('up5', 'table', 7, 7.5); put('up5', 'Rustic Chair', 7, 8.5, 180); put('up5', 'Rustic Chair', 8, 8.5, 180)
put('up5', 'Rustic Chair', 9, 7.5, 90)
put('up5', 'chest-medium', 10, 10)
put('up5', 'High Crude Wooden Shelf', 4.5, 5.5, 270)
put('up5', 'Hanging Lantern', 8, 10)
for x in (5, 10):
    A.win('up5', 'Wooden Window Frame', x, 11.5, x + 1, 12, 1)
    wbox(up5, x, 12, x + 1, 12.5)
A.win('up5', 'Wooden Window Frame', 11.5, 7, 12, 8, 1)
A.walls(up9, 4, 4, 12, 12, 'B', 'r')
R(up9, 4, 8, 4.5, 9, ' ')
R(up9, 6, 5, 10, 6, ' ')                                # the stairwell, railed
R(up9, 6, 6, 10, 6.5, 'i'); R(up9, 10, 5, 10.5, 6, 'i')
put('up9', 'bed', 4.5, 7, 270, label='Bed (Oscar Godwin)')
put('up9', 'bed', 8.5, 7, 90, label='Bed (Anton Godwin)')
put('up9', 'Crude Wooden Closet', 6.5, 10.5)
put('up9', 'chest-small', 10.5, 10.5)
put('up9', 'Hanging Lantern', 8, 9, z=3)
for x in (5, 9.5):
    A.win('up9', 'Wooden Window Frame', x, 11.5, x + 1, 12, 1)
    wbox(up9, x, 12, x + 1, 12.5)
A.win('up9', 'Wooden Window Frame', 4, 10, 4.5, 11, 1); A.win('up9', 'Wooden Window Frame', 11.5, 10, 12, 11, 1)
A.win('up9', 'Wooden Window Frame', 10, 4, 11, 4.5, 1)                   # north, over the lake
R(up5, 4.5, 12.5, 6.5, 13.5, 'e')                      # front garden, a hedge along Gabrielle's side
R(up5, 3.5, 14.5, 12, 15, 'F')
R(up5, 7, 12, 9, 14.5, 'c'); R(up5, 9, 13.5, 12, 14.5, 'c')            # the path out to the lane
put('up5', 'Dog Pillow', 10, 12.5); put('up5', 'Dog Bowl', 11, 12.5)
put('up5', 'Wall Lantern', 9.5, 12, 0, 2.5)            # beside the hood's bracket, above the window heads
put('up5', 'Scrap Vat I', 12, 4.5, label='Scrap Vat I (water butt)')
door_hood(7, 11.5, 9, 12, 's', 'lead')
ROOFS['godwins'] = (12.5, None, (4, 4, 12, 12))
home("The Godwins' house (Oscar and Anton)", 4, 4, 12, 12)

# ---- the Reeds' house (NE): two storeys, rough stone below, half-timbered above and jettied 0.5 m over the
# yard on brackets (the jetty shelters the door), a stone shingle gable; the kitchen corner, a stair up the
# back wall, two beds upstairs
shell(34.5, 4, 44.5, 12, 'S', plinth=False)
door('Wooden Door', 38.5, 11.5, 40.5, 12, plinth=False)
A.stairs('up5', "The Reeds' stair", 37, 5, 41, 6, 4, 'W')        # (0.5 m off the wall: whole metres for the site map)
chimney(44, 8, 45, 9, 'reeds', through=(up9,))
put('up5', 'Stone Fireplace', 43, 7.5, 90)
put('up5', 'Wooden Sink', 35, 7, 270)
put('up5', 'table', 38, 8); put('up5', 'Rustic Chair', 38, 9, 180); put('up5', 'Rustic Chair', 39, 9, 180)
put('up5', 'chest-medium', 42.5, 5.5)
put('up5', 'Low Crude Wooden Shelf', 35, 9.5, 270)
put('up5', 'Hanging Lantern', 40, 9.5)
A.win('up5', 'Wooden Window Frame', 36, 11.5, 37, 12, 1); A.win('up5', 'Wooden Window Frame', 42, 11.5, 43, 12, 1)
A.win('up5', 'Wooden Window Frame', 34.5, 5, 35, 6, 1); A.win('up5', 'Wooden Window Frame', 44, 10, 44.5, 11, 1)
A.walls(up9, 34.5, 4, 44.5, 12.5, 'J', 'r')
R(up9, 44, 8, 44.5, 9, ' ')
R(up9, 37, 5, 41, 6, ' ')
R(up9, 37, 6, 41, 6.5, 'i'); R(up9, 41, 5, 41.5, 6, 'i')
put('up9', 'bed', 35, 9, label='Bed (Hannah Reed)')
put('up9', 'bed', 41.5, 9, label='Bed (Marianne Reed)')
put('up9', 'Crude Wooden Closet', 38.5, 11)
put('up9', 'Hanging Lantern', 39.5, 8, z=3)
for x in (37.5, 40.5):
    A.win('up9', 'Wooden Window Frame', x, 12, x + 1, 12.5, 1)
    wbox(up9, x, 12.5, x + 1, 13)
A.win('up9', 'Wooden Window Frame', 42, 4, 43, 4.5, 1)                   # north, over the lake
A.win('up9', 'Wooden Window Frame', 34.5, 6, 35, 7, 1); A.win('up9', 'Wooden Window Frame', 44, 6, 44.5, 7, 1)
for x in (35, 37.5, 41, 44):                            # brackets under the jetty
    A.overlay(up5, x, 12, x + 0.5, 12.5, 'Refined Wood Block (jetty bracket)', WOOD, 0.5, 3.5)
R(up5, 35, 12.5, 38, 13.5, 'e'); R(up5, 41, 12.5, 44, 13.5, 'e')
ROOFS['reeds'] = (12.5, None, (34.5, 4, 44.5, 12.5))
home("The Reeds' house (Hannah and Marianne)", 34.5, 4, 44.5, 12)

# ---- the wattle cottage (W, Gabrielle Fairburn): plaited walls on a stone plinth, thatched, the door in the
# east gable end under a hood with a round window high above it; a cat's bed by the hearth
shell(4, 15.5, 11.5, 23.5, 'A')
R(up5, 11, 19, 11.5, 20, 'm')
door('Wooden Door', 11, 18.5, 11.5, 20.5)
A.win('up5', 'Round Wooden Window Frame', 11, 19, 11.5, 20, 5)
chimney(3.5, 19, 4.5, 20, 'gabrielle')
put('up5', 'Fireplace', 4.5, 18.5, 270)
put('up5', 'bed', 8.5, 16, label='Bed (Gabrielle Fairburn)')
put('up5', 'table', 6.5, 21.5); put('up5', 'Rustic Chair', 6.5, 20.5); put('up5', 'Rustic Chair', 8.5, 21.5, 90)
put('up5', 'chest-small', 10, 22)
put('up5', 'Low Crude Wooden Shelf', 5, 16, 180)
put('up5', 'Cat Pillow', 4.5, 21.5); put('up5', 'Cat Bowl', 5.5, 22.5)
put('up5', 'Hanging Lantern', 7.5, 19)
A.win('up5', 'Wooden Window Frame', 7, 15.5, 8, 16, 1)
for x in (5, 8.5):
    A.win('up5', 'Wooden Window Frame', x, 23, x + 1, 23.5, 1)
    wbox(up5, x, 23.5, x + 1, 24)
A.win('up5', 'Wooden Window Frame', 4, 16.5, 4.5, 17.5, 1); A.win('up5', 'Wooden Window Frame', 11, 16, 11.5, 17, 1)
put('up5', 'Wall Lantern', 11.5, 17.5, 270, 2.0)
door_hood(11, 18.5, 11.5, 20.5, 'e', 'straw')
ROOFS['gabrielle'] = (9, None, (4, 15.5, 11.5, 23.5))
home('Wattle cottage (Gabrielle Fairburn)', 4, 15.5, 11.5, 23.5)

# ---- the stone cottage (E, Hugo Vanderhall): rough stone, a tiled gable with a round window in the north
# gable, the door onto the east lane under a hood, its allotment beside it
shell(35, 15.5, 43, 23.5, 'S', plinth=False)
R(up5, 38.5, 15.5, 39.5, 16, 's')
door('Wooden Door', 35, 18.5, 35.5, 20.5, plinth=False)
A.win('up5', 'Round Wooden Window Frame', 38.5, 15.5, 39.5, 16, 5)
chimney(38.5, 23, 39.5, 24, 'hugo')
put('up5', 'Stone Fireplace', 38, 22, 180)
put('up5', 'bed', 40.5, 16, label='Bed (Hugo Vanderhall)')
put('up5', 'Crude Wooden Closet', 41.5, 20, 90)
put('up5', 'table', 37, 18.5); put('up5', 'Rustic Chair', 37, 19.5, 180); put('up5', 'Rustic Chair', 38, 19.5, 180)
put('up5', 'chest-medium', 35.5, 22)
put('up5', 'Hanging Lantern', 38.5, 18)
A.win('up5', 'Wooden Window Frame', 35, 16.5, 35.5, 17.5, 1); A.win('up5', 'Wooden Window Frame', 35, 21.5, 35.5, 22.5, 1)
A.win('up5', 'Wooden Window Frame', 36, 15.5, 37, 16, 1); A.win('up5', 'Wooden Window Frame', 41, 23, 42, 23.5, 1)
A.win('up5', 'Wooden Window Frame', 42.5, 22, 43, 23, 1)
put('up5', 'Wall Lantern', 34.5, 21, 90, 2.0)
door_hood(35, 18.5, 35.5, 20.5, 'w', 'tiles')
R(up5, 34, 16, 35, 18, 'e'); R(up5, 34, 21.5, 35, 23.5, 'e')           # beds either side of the door
ROOFS['hugo'] = (9, None, (35, 15.5, 43, 23.5))
home('Stone cottage (Hugo Vanderhall)', 35, 15.5, 43, 23.5)

# ---- the pair (SW, Ramone Jones and Robert Gibson): two half-timbered cottages on a stone plinth under one
# long thatched roof, sharing a chimney stack on the party wall; doors on the south lane under hoods
shell(4, 26, 19, 33, 'H')
R(up5, 11, 26.5, 11.5, 32.5, 'j')                       # the party wall
door('Wooden Door', 6.5, 26, 8.5, 26.5); door('Wooden Door', 14, 26, 16, 26.5)
chimney(10.5, 29, 12, 30, 'pair')
put('up5', 'Fireplace', 9.5, 28.5, 90); put('up5', 'Fireplace', 12, 28.5, 270)
put('up5', 'bed', 4.5, 29.5, label='Bed (Ramone Jones)')
put('up5', 'table', 7, 28); put('up5', 'Rustic Chair', 7.5, 29, 180)
put('up5', 'chest-small', 9.5, 31.5); put('up5', 'Hanging Lantern', 7.5, 30.5)
put('up5', 'bed', 16.5, 29.5, label='Bed (Robert Gibson)')
put('up5', 'table', 13.5, 31); put('up5', 'Rustic Chair', 14, 30)
put('up5', 'chest-small', 12, 31.5); put('up5', 'Hanging Lantern', 15, 28.5)
for x in (4.5, 17):
    A.win('up5', 'Wooden Window Frame', x, 26, x + 1, 26.5, 1)
    wbox(up5, x, 25.5, x + 1, 26)
for x in (7.5, 13.5):
    A.win('up5', 'Wooden Window Frame', x, 32.5, x + 1, 33, 1)          # south, over the lake
A.win('up5', 'Wooden Window Frame', 4, 27.5, 4.5, 28.5, 1); A.win('up5', 'Wooden Window Frame', 18.5, 27.5, 19, 28.5, 1)
put('up5', 'Wall Lantern', 9, 25.5, 0, 2.5); put('up5', 'Wall Lantern', 16.5, 25.5, 0, 2.5)
door_hood(6.5, 26, 8.5, 26.5, 'n', 'straw'); door_hood(14, 26, 16, 26.5, 'n', 'straw')
ROOFS['pair'] = (9, None, (4, 26, 19, 33))
home('The pair: west cottage (Ramone Jones)', 4, 26, 11.25, 33)
home('The pair: east cottage (Robert Gibson)', 11.25, 26, 19, 33)

# ---- Kaori's cottage (S, Kaori Conway): rough wood on a stone plinth, a thatched hip, its door facing
# whoever comes up the stair, under a hood
shell(27, 26, 34, 33, 'R')
door('Wooden Door', 27, 28.5, 27.5, 30.5)
chimney(33.5, 29, 34.5, 30, 'kaori')
put('up5', 'Fireplace', 32.5, 28.5, 90)
put('up5', 'bed', 30, 29.5, label='Bed (Kaori Conway)')
put('up5', 'table', 28.5, 27); put('up5', 'Rustic Chair', 28.5, 28, 180)
put('up5', 'chest-small', 28, 31.5); put('up5', 'Hanging Lantern', 30.5, 28)
A.win('up5', 'Wooden Window Frame', 31, 26, 32, 26.5, 1); wbox(up5, 31, 25.5, 32, 26)
A.win('up5', 'Wooden Window Frame', 29, 32.5, 30, 33, 1)
A.win('up5', 'Wooden Window Frame', 27, 31, 27.5, 32, 1)
put('up5', 'Wall Lantern', 26.5, 31, 270, 2.5)
door_hood(27, 28.5, 27.5, 30.5, 'w', 'straw')
ROOFS['kaori'] = (9, None, (27, 26, 34, 33))
home("Kaori's cottage (Kaori Conway)", 27, 26, 34, 33)

# ---- the tarred cottage (SE, Gunther Galeforth): tarred wood on a stone plinth, a tarred straw hip, by
# the back steps; crates and a water butt
shell(35.5, 26, 42.5, 33, 'X')
door('Wooden Door', 38, 26, 40, 26.5)
chimney(42, 29.5, 43, 30.5, 'gunther')
put('up5', 'Fireplace', 41, 29, 90)
put('up5', 'bed', 36, 29.5, label='Bed (Gunther Galeforth)')
put('up5', 'table', 38.5, 28); put('up5', 'Rustic Chair', 38.5, 29, 180)
put('up5', 'chest-medium', 39.5, 31.5); put('up5', 'Hanging Lantern', 38.5, 30.5)
A.win('up5', 'Wooden Window Frame', 36, 26, 37, 26.5, 1); wbox(up5, 36, 25.5, 37, 26)
A.win('up5', 'Wooden Window Frame', 38.5, 32.5, 39.5, 33, 1)
A.win('up5', 'Wooden Window Frame', 35.5, 27.5, 36, 28.5, 1); A.win('up5', 'Wooden Window Frame', 42, 27, 42.5, 28, 1)
put('up5', 'Wall Lantern', 40.5, 25.5, 0, 2.0)
door_hood(38, 26, 40, 26.5, 'n', 'lead')
put('up5', 'Scrap Vat I', 42.5, 32, label='Scrap Vat I (water butt)')
put('up5', 'Scrappy Crate', 43.5, 32); put('up5', 'Supply Sacks I', 44.5, 31)
ROOFS['gunther'] = (9, None, (35.5, 26, 42.5, 33))
home('Tarred cottage (Gunther Galeforth)', 35.5, 26, 42.5, 33)

# ================================================================= the back steps, down to the west landing (+4 m)
# The south lane runs on past the tarred cottage into a railed footbridge (4 m) off the deck's south-east
# corner, south past the smithy's corner and 1 m down onto the west landing, by the foot of the west stair to
# the manor and the tavern's side stair. (The stair and its cheeks sit on whole metres, so they stay clean in
# the 1 m site plan.)
R(up5, 44, 30, 48, 39, 'w')
A.rail(up5, 46, 30, 48, 30.5); A.rail(up5, 47.5, 30.5, 48, 39); A.rail(up5, 44, 34, 44.5, 39)
R(mid, 44, 39, 48, 42, 'w')
A.stairs('mid', 'Back steps down to the west landing', 45, 39, 47, 41, 1, 'N')
A.cheeks(mid, 45, 39, 47, 41, 'N')
A.rail(mid, 47.5, 41, 48, 42)
put('up5', 'Bench', 46.5, 31, 270)                      # looking out to the manor
put('up5', 'Ground Lantern II', 44.5, 30.5)
# a signpost where the south lane turns onto the footbridge, its board pointing the way down
A.overlay(up5, 43, 33, 43.5, 33.5, 'Refined Wood Block (signpost)', WOOD, 2.5, 0)
A.overlay(up5, 43.5, 33, 44.5, 33.5, 'Tarred Wood Block (sign: the west landing, the tavern, the manor)', TAR, 0.5, 2)
zone('up5', 'Back steps (to the west landing)', 44, 30, 48, 39, '#2f8f8a')

# ================================================================= the neighbours' edges (their own blueprints)
R(mid, 12, 40, 44, 44, 'k'); R(mid, 13, 41, 43, 44, 'b')
A.parapet(mid, 12, 40, 44, 40.5, [(20, 26)])
R(mid, 20, 34, 26, 40, 'w')
A.stairs('mid', "Stairs up to the villagers' quarter (smithy blueprint)", 20, 34, 26, 36, 1, 'N')
A.cheeks(mid, 20, 34, 26, 36, 'N')
A.rail(mid, 19.5, 36, 20, 40); A.rail(mid, 26, 36, 26.5, 40)
zone('mid', 'Smithy (smithy blueprint)', 12, 40, 44, 44, '#5f6770')
R(mid, 44, 42, 56, 44, 'w')
A.rail(mid, 48, 41.5, 49.5, 42)
zone('mid', 'West landing (smithy blueprint)', 44, 42, 56, 44, '#2f8f8a')
R(mnr, 50, 6, 56, 42, 'P'); R(mnr, 50, 6, 51, 42, 'f')
zone('manor', 'Manor grounds (manor blueprint)', 50, 6, 56, 42, '#8a5cc2')

# ================================================================= roofs, at 45 degrees in even steps
# thatch for the humbler cottages (plant fibre ridges on the gables), tiles for the hall and the stone cottage,
# stone shingle for the Reeds, tarred shingle for the Godwins, tarred straw for the tarred cottage. Ridge caps
# go on the gables only: on a 45 degree hip they zigzag down the hip lines.
r9s, r9h, r9t, r9x = A.roof(roof9), A.roof(roof9), A.roof(roof9), A.roof(roof9)
r10, r125a, r125b = A.roof(roof11), A.roof(roof125), A.roof(roof125)
r9s.gable(4, 15.5, 11.5, 23.5, 'x', 'straw', pitch=1.0, overhang=0.5)              # Gabrielle
r9s.gable(4, 26, 19, 33, 'x', 'straw', pitch=1.0, overhang=0.5)                    # the pair
r9h.hip(27, 26, 34, 33, 'straw', pitch=1.0, overhang=0.5)                          # Kaori
r9t.gable(35, 15.5, 43, 23.5, 'y', 'tiles', pitch=1.0, overhang=0.5)               # Hugo
r9x.hip(35.5, 26, 42.5, 33, 'tarstraw', pitch=1.0, overhang=0.5)                   # Gunther
r10.gable(16, 4, 30, 13.5, 'x', 'tiles', pitch=1.0, overhang=0.5)                  # the hall
r10.gable(19, 10, 27, 14.5, 'y', 'tiles', pitch=1.0, overhang=0.5)                 # its entrance bay
r125a.hip(4, 4, 12, 12, 'lead', pitch=1.0, overhang=0.5)                           # the Godwins
r125b.gable(34.5, 4, 44.5, 12.5, 'x', 'shingle', pitch=1.0, overhang=0.5)          # the Reeds
HELPER = {'gabrielle': r9s, 'pair': r9s, 'kaori': r9h, 'hugo': r9t, 'gunther': r9x, 'hall': r10,
          'godwins': r125a, 'reeds': r125b}


def ridge_top(b):
    """The highest roof square over a building's outline and eaves, in metres above the water."""
    el, _, (x0, y0, x1, y1) = ROOFS[b]
    rf = HELPER[b]
    hs = [rf.top(x0 + i / 2, y0 + j / 2) for i in range(-1, int((x1 - x0) * 2) + 1) for j in range(-1, int((y1 - y0) * 2) + 1)]
    return el + max(h for h in hs if h is not None)


tops = []
for x0, y0, x1, y1, b in CHIMNEYS:
    top = ridge_top(b) + 1
    tops.append((x0, y0, x1, y1, top))
    R(up5, x0, y0, x1, y1, P._alloc({'name': 'Rough Stone Block (chimney)', 'kind': 'wall', 'color': RS, 'height': top - 5}))
    HELPER[b].cut(x0, y0, x1, y1)
for rf, cap in ((r9s, 'fibre'), (r9h, None), (r9t, 'lead'), (r9x, None), (r10, 'lead'), (r125a, None), (r125b, 'lead')):
    if cap:
        rf.caps(cap, min_lower=1)
    rf.paint()

# chimney caps: a course 0.5 m proud round the top of each stack, and a terracotta pot or two on top
cap_el = min(t for *_, t in tops) - 0.5
caps = A.level('caps', 'Chimney caps and pots (+%g m)' % cap_el, cap_el, max(t for *_, t in tops) - cap_el + 1)
for i, (x0, y0, x1, y1, top) in enumerate(tops):
    ring = P._alloc({'name': 'Rough Stone Block (chimney cap)', 'kind': 'block', 'color': RS, 'height': 0.5, 'base': top - 0.5 - cap_el})
    A.ring(caps, x0, y0, x1, y1, ring)
    pot = P._alloc({'name': 'Fired Bricks Block (chimney pot)', 'kind': 'block', 'color': '#aa7657', 'height': 0.5, 'base': top - cap_el})
    R(caps, x0, y0, x0 + 0.5, y0 + 0.5, pot)
    if i % 2 == 0 and x1 - x0 > 0.5:
        R(caps, x1 - 0.5, y1 - 0.5, x1, y1, pot)

# door hoods: shed roofs 1 m out over the doors, rising to the wall, on brackets
for x0, y0, x1, y1, out, mat in HOODS:
    hr = A.roof(hood)
    if out in 'ns':
        oy0, oy1 = (y1, y1 + 1) if out == 's' else (y0 - 1, y0)
        hr.shed(x0 - 0.5, oy0, x1 + 0.5, oy1, 'n' if out == 's' else 's', mat, pitch=1.0, overhang=0)
        by0, by1 = (y1, y1 + 0.5) if out == 's' else (y0 - 0.5, y0)
        for bx in (x0 - 0.5, x1):
            A.overlay(up5, bx, by0, bx + 0.5, by1, 'Refined Wood Block (bracket)', WOOD, 0.5, 2)
    else:
        ox0, ox1 = (x1, x1 + 1) if out == 'e' else (x0 - 1, x0)
        hr.shed(ox0, y0 - 0.5, ox1, y1 + 0.5, 'w' if out == 'e' else 'e', mat, pitch=1.0, overhang=0)
        bx0, bx1 = (x1, x1 + 0.5) if out == 'e' else (x0 - 0.5, x0)
        for by in (y0 - 0.5, y1):
            A.overlay(up5, bx0, by, bx1, by + 0.5, 'Refined Wood Block (bracket)', WOOD, 0.5, 2)
    hr.paint()

# the bell-cote on the entrance bay's gable: two limestone piers on the roof, the bell between them over the
# ridge, a little tiled roof
bell_el = 11 + r10.top(22, 14)
bell = A.level('bell', 'Dining hall: the bell-cote (+%g m)' % bell_el, bell_el, 3)
belltop = A.level('belltop', 'Dining hall: the bell-cote roof (+%g m)' % (bell_el + 3), bell_el + 3, 2)
R(bell, 22, 14, 22.5, 14.5, 'q'); R(bell, 23.5, 14, 24, 14.5, 'q')
R(bell, 22.5, 14, 23.5, 14.5, 'Z')
rb = A.roof(belltop)
rb.gable(22, 14, 24, 14.5, 'x', 'tiles', pitch=1.0, overhang=0.5)
rb.paint()
vane = A.level('vane', 'Dining hall: the weathervane (+%g m)' % (bell_el + 3 + rb.top(23, 14)), bell_el + 3 + rb.top(23, 14), 1.5)
R(vane, 23, 14, 23.5, 14.5, P._alloc({'name': 'Iron Block (weathervane)', 'kind': 'block', 'color': '#848483', 'height': 1.5}))

# ================================================================= stilts, the well's lining, rim beams and checks
print('stilts:', A.stilts(stl, [('mid', 4), ('up5', 5), ('manor', 8)]))
for x, y in P.cells_rect(21.5 - 2, 18.5 - 2, 24.5 - 2, 21.5 - 2):
    mx, my = P.centre_m(x, y)
    if 1.0 <= ((mx + 2 - 23) ** 2 + (my + 2 - 20) ** 2) ** 0.5 <= 1.5 and stl[y][x] == ' ':
        stl[y][x] = 'V'                                 # the shaft lining, from the water up to the deck
own = lambda x, y: (3 <= x < 46 and 3 <= y < 34) or (44 <= x < 48 and 30 <= y < 41.5)
print('rim beam squares:', A.rim_beams(stl, [('mid', 4), ('up5', 5)], own))
print('chimney tops:', sorted(round(t, 1) for *_, t in tops), ' bell-cote top:', bell_el + 3 + max(rb.top(x, 14) or 0 for x in (21.5, 22, 22.5, 23, 23.5, 24)))
A.spawn('up5', 22.5, 24.5, 180)                                 # walk mode starts here: the green's edge inside the gateway, facing the well and the dining hall
A.checks()

NOTES = """Laketown: the villagers' quarter, as a 0.5 m detail blueprint (all three passes done). Drafted by Claude.
This plan's corner is the layout's (2, 2), so it lines up with the Laketown layout and stamps back into the site plan there.

PASSES
1. Design and bones: the deck and lanes, the green and the well, building shells, doors, stairs and roof shapes, beds, the hall's stations, the connections, stilts, labels.
2. Details: reshaped so nothing is cramped, then windows, plinths, hoods, gable windows, chimney caps and pots, ridges, furniture and lights, gardens, the gateway, the notice board, the windlass. Then a 3D review and a refining round.
3. Review and finishing touches (this one).

PASS 3: WHAT THE REVIEW FOUND AND CHANGED
- Five door lanterns hung in the same square as their door hood's bracket, at the same height. The item check missed it (it didn't compare items with raised pieces over a floor); it does now, and the lanterns moved beside the brackets. The other Laketown blueprints were already clear.
- The dining hall had only its front door, so supplies from the back steps and the allotments came round through the green: a kitchen door in the east wall, into the passage, under a tiled hood with a lantern (it replaces a window).
- The back steps' bench faced back into the quarter: it now looks out to the manor.
- The passages either side of the hall were dark: a lantern up each. Firewood stacked by the hall's hearth chimney.
- Where the south lane turns onto the footbridge, nothing said where it went: a signpost, its board pointing down to the west landing, the tavern and the manor.
- A weathervane on the bell-cote's roof.
- The 1 m layout (doc laketown) now matches: the bigger deck, the back steps, and labels for the homes, the hall, the green and the allotments.
- Checked, all clear: nothing in front of any door or window, no door onto a drop, every stair with 1 m clear at the foot and top and 2 m of headroom, no item running into another or into a raised piece, nothing outside the altar's build volume. In the site plan, nothing is blocked where the quarter meets the smithy and the west landing.

CONNECTIONS (for the neighbouring blueprints to match)
- Smithy (+4 m): its stair (x 20..26) arrives at the quarter's gateway, between the pair and Kaori's cottage. Keep the strip in front of the stair clear.
- West landing (+4 m, the smithy blueprint): the back steps come down at x 44..48 onto its north-west corner. Its railing is open there, and its bench sits on the south rail.
- Manor (+8 m): the quarter's north-east corner is 4 m across the water from the manor's west garden. The Reeds' stone shingle gable (ridge +17.5 m) and the hall's bell-cote (+19 m) are what the west garden and the clock tower look across at; nothing needs to change there.

PASS 2: RESHAPED
- The deck grows to the build area's edge on the west and north: 43 x 31 m (the layout had 36 x 28). The layout follows in pass 3.
- Every home has at least 6 x 6 m inside, and the two family houses have two storeys (8 x 8 and 10 x 8 m). Ground floors are 4 m, upper floors 3.5 m.
- The dining hall moved to the head of the green, on the line of the way in: up the stair, through the gateway, past the well to the hall's door. It's 14 x 9.5 m with 6 m walls and an entrance bay, and its bell-cote is the quarter's high point (+19 m).
- Refining round: the hall raised so its bell-cote tops the family houses' ridges and chimneys; ridge caps kept to the gables (on a 45 degree hip they zigzag down the hip lines); plant fibre ridges on the thatch instead of dark tarred straw.

THE QUARTER (+5 m): refined wood on a tarred edge with a wooden railing. A paved forecourt in front of the hall, dirt lanes down both sides of the green and along the south row, on to the back steps, and paths up the passages either side of the hall to benches looking out over the lake.
- The way in: a timber gateway at the top of the smithy's stair, the quarter's sign hanging from its beam, lamps on its posts, lanterns either side.
- The green: grass, a field stone path across it to the well and the hall, flower beds in the corners, lanterns, benches facing the well, and a notice board by the path.
- The well: a round kerb of well block over a shaft through the deck, lined down to the lake. Two posts carry a windlass and a little thatched roof.
- Allotments: farm soil with three seedbeds beside the stone cottage.

THE DINING HALL (food stations): brick-timbered on a 1 m stone plinth, 6 m walls, a tiled roof. The entrance bay faces the green with a double door, a round window high in its gable, and the bell-cote on top (two limestone piers, a bronze bell over the ridge, a little tiled roof). Benches against the front, lanterns by the door.
- Inside: the kitchen along the back wall (Cooking Station, Kitchen, a sink, the Oven under its own chimney, a large chest for the pantry), a serving counter with a gap in the middle, two long tables with benches (12 seats) either side of the aisle, a big stone hearth, a dresser and lanterns. High windows over the kitchen, more along the sides and front.
- Which station counts as a survivor's food station isn't published: check in game.

THE HOMES: eight, for the ten villagers. The two families share (Hannah and Marianne Reed, Oscar and Anton Godwin). The names on the beds are suggestions: assign them in game with the Summoning Staff. Every home has a fireplace under a rough stone chimney that rises a metre above its ridge, capped, with terracotta pots; windows all round; a lantern inside and one by the door.
- The Godwins' house (NW, 8 x 8 m): limestone below, brick-timbered above, a tarred shingle hip. A living room with the hearth, a table and shelves; a stair up the back wall; two beds, a wardrobe and a chest upstairs. A front garden with a hedge, a path to the lane, a dog's bed and bowl by the door, a water butt.
- The Reeds' house (NE, 10 x 8 m): rough stone below, half-timbered above, jettied 0.5 m over the yard on brackets (the jetty shelters the door), a stone shingle gable. A kitchen corner with a sink, the hearth, a table; a stair up the back wall; two beds and a wardrobe upstairs. Flower beds along the front.
- Wattle cottage (W, Gabrielle Fairburn, 7.5 x 8 m): plaited walls on a stone plinth, thatched, the door in the east gable end under a thatched hood, a round window high above it. A cat's bed and bowl by the hearth.
- Stone cottage (E, Hugo Vanderhall, 8 x 8 m): rough stone, a tiled gable with a round window in the north gable, the door onto the east lane under a tiled hood between flower beds.
- The pair (SW, Ramone Jones and Robert Gibson, 15 x 7 m): two half-timbered cottages on a stone plinth under one long thatched roof, sharing a chimney stack on the party wall. Doors under thatched hoods, window boxes, windows over the lake at the back.
- Kaori's cottage (S, Kaori Conway, 7 x 7 m): rough wood on a stone plinth, a thatched hip, its door under a hood facing whoever comes up the stair.
- Tarred cottage (SE, Gunther Galeforth, 7 x 7 m): tarred wood on a stone plinth, a tarred straw hip, by the back steps; crates, sacks and a water butt outside.
Roofs: thatch for the humbler cottages (plant fibre ridges on the gables), tiles for the hall and the stone cottage, stone shingle for the Reeds, tarred shingle for the Godwins, tarred straw for the tarred cottage.

CONNECTIONS
- South: the smithy's stair (x 20..26) arrives at the gateway, between the pair and Kaori's cottage.
- The back steps: the south lane runs on past the tarred cottage into a railed footbridge (4 m) off the deck's south-east corner (a bench and a lantern there, looking out to the manor), then south past the smithy's corner and 1 m down onto the west landing's north-west corner, by the foot of the west stair to the manor and the tavern's side stair. The smithy blueprint's landing railing opens for it, and its bench moved to the landing's south rail.

STILTS: 1 m posts on the layout's 4 m grid, from the lake bed 4 m down to each deck's underside, with tarred rim beams under the edges.

SIZES: furniture and light sizes are estimates until measured; stations are the planner's 2 x 2 m placeholders.
"""
A.save('laketown_villagers.json', NOTES, 'r-claude-laketown-villagers-3')
