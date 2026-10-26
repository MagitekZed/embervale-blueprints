"""Laketown: the carpentry, storehouse and west dock, with the west walkway. 0.5 m detail plan. Pass 3 of 3:
review and finishing touches (done).

The Carpenter's platform at +2 m, south-west of the square, reached by the west walkway (+3 m): the walkway
runs west from the square past the bathhouse branch, and at its west end the smithy's lane carries straight
on south, one run from the smithy to the carpentry, down a short stair onto the deck.
- The north range: one long building under one big roof, the stone storehouse at its west end (over the
  dock) and the Carpenter's workshop in timber beside it, a door between them.
- The kiln shed across the lane, brick, open to it.
- The stone yard in front of the storehouse, the Masonry Tools under a lean-to.
- The timber yard: a long drying shed for seasoning planks, and a jib crane on the yard's edge swinging out
  over the west dock to lift timber off the boats.
- The work yard at the foot of the lane, with the stair up to the arena's stands.
- The Carpenter's cottage in the south-east corner: refined wood, carved doors.
- The west dock (+1 m) along the west side, a stair up into the timber yard.

The deck grows from the layout's 32 x 28 m to 34 x 34 m (east to x 44, south to y 126) so nothing is
cramped; the dock runs on south beside the yard.

Coordinates are the layout's (doc `laketown`): this plan's corner is the layout's (0, 68).
Run: python laketown_carpentry.py  ->  writes laketown_carpentry.json
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laketown_common import Area, WOOD, STONE
from mage_common import ROOF_MATS

ROOF_MATS.setdefault('fibre', ('Plant Fiber Roof Block', '#725e4f'))

RS, RCS, BRICK, TAR, HT = '#7d776a', '#62605d', '#aa7657', '#5d5652', '#71665e'
A = Area('Laketown: carpentry and west walkway (detail)', 0, 68, 66, 60, {
    'c': {'name': 'Field Stones', 'kind': 'floor', 'color': '#8a8170'},                # the lane and work yard
    'k': {'name': 'Roughly Cut Stone Block', 'kind': 'floor', 'color': RCS},           # the stone yard; the smithy's edge
    'b': {'name': 'Fired Bricks Block', 'kind': 'floor', 'color': BRICK},              # the kiln shed; the smithy
    'L': {'name': 'Limestone Road Block', 'kind': 'floor', 'color': '#a38b79'},        # the square (its blueprint)
    'h': {'name': 'Brick-Timbered Block', 'kind': 'floor', 'color': '#947f75'},        # the bathhouse (its blueprint)
    'p': {'name': 'Roughly Cut Stone Block (parapet)', 'kind': 'block', 'color': RCS, 'height': 1},
    'o': {'name': 'Roughly Cut Stone Block (pier)', 'kind': 'block', 'color': RCS, 'height': 1.5},
    'Q': {'name': 'Rough Stone Block (plinth)', 'kind': 'wall', 'color': RS, 'height': 1},
    'S': {'name': 'Rough Stone Block', 'kind': 'wall', 'color': RS, 'height': 6},       # the storehouse
    'H': {'name': 'Half-Timbered Block', 'kind': 'wall', 'color': HT, 'height': 5, 'base': 1},   # the workshop
    'B': {'name': 'Fired Bricks Block', 'kind': 'wall', 'color': BRICK},               # the kiln shed (4 m)
    'R': {'name': 'Refined Wood Block', 'kind': 'wall', 'color': WOOD, 'height': 3, 'base': 1},  # the cottage
    'Y': {'name': 'Conifer Wood Block (upper floor)', 'kind': 'wall', 'color': '#6e5a51'},
    'C': {'name': 'Conifer Wood Block (corner post)', 'kind': 'wall', 'color': '#6e5a51', 'height': 3, 'base': 1},
    'n': {'name': 'Refined Wood Block (post)', 'kind': 'block', 'color': WOOD, 'height': 3},
    'N': {'name': 'Refined Wood Block (drying shed post)', 'kind': 'block', 'color': WOOD, 'height': 3.5},
    'M': {'name': 'Refined Wood Block (crane mast)', 'kind': 'block', 'color': WOOD, 'height': 5.5},
    'J': {'name': 'Refined Wood Block (crane jib)', 'kind': 'block', 'color': WOOD, 'height': 0.5},
    'K': {'name': 'Iron Block (crane hook)', 'kind': 'block', 'color': '#848483', 'height': 0.5},
    'U': {'name': 'Refined Wood Block (lamp post)', 'kind': 'block', 'color': WOOD, 'height': 2},
    'l': {'name': 'Yellow Luminescent Block (lamp)', 'kind': 'block', 'color': '#bd9a5f', 'height': 0.5},
    'x': {'name': 'Refined Wood Block (window box)', 'kind': 'block', 'color': WOOD, 'height': 0.5, 'base': 0.5},
    's': {'name': 'Rough Stone Block (under the loft door)', 'kind': 'wall', 'color': RS, 'height': 4},
    'T': {'name': 'Rough Stone Block (loft door wall)', 'kind': 'wall', 'color': RS, 'height': 3},
    'G': {'name': 'Refined Wood Block (gable)', 'kind': 'wall', 'color': WOOD, 'height': 5.5},
    'v': {'name': 'Refined Wood Block (louvres)', 'kind': 'block', 'color': WOOD, 'height': 1.5},
    'F': {'name': 'Refined Wood Block (hoist beam)', 'kind': 'block', 'color': WOOD, 'height': 0.5},
    'z': {'name': 'Fine Sand (sawdust)', 'kind': 'floor', 'color': '#f3dfcc'},
    'e': {'name': 'Flower Soil', 'kind': 'floor', 'color': '#a77e63'},
    'g': {'name': 'Half-Timbered Block (gable)', 'kind': 'wall', 'color': HT, 'height': 8.5, 'base': 1},
})
P, R, zone, put = A.P, A.R, A.zone, A.put
stl = A.level('stilts', 'Stilts, standing on the lake bed (-4 m)', -4, 12)
lake = A.level('lake', 'Lake (water level, 0 m)', 0, 1)
dock = A.level('dock', 'West dock (+1 m)', 1, 3)
low = A.level('low', 'Carpentry deck, ground floors (+2 m)', 2, 4)
PL = A.level('plinth', 'Plinths and thresholds (+2 m)', 2, 1)
walk = A.level('walk', 'West walkway and its branches (+3 m)', 3, 4)
hook = A.level('hook', 'The crane hook (+3.5 m)', 3.5, 1)
brace = A.level('brace', 'The crane brace (+2 m)', 2, 6)
work = A.level('work', 'Timber yard: the boat and the log on the sawhorse (+2 m)', 2, 3)
mid = A.level('mid', 'Smithy, square, arena: their edges (+4 m)', 4, 4)
roof5 = A.level('roof5', 'Stone yard lean-to roof (+5 m)', 5, 3)
roof55 = A.level('roof55', 'Drying shed roof (+5.5 m)', 5.5, 3)
roof6 = A.level('roof6', 'Kiln shed roof (+6 m)', 6, 3)
lamp5 = A.level('lamp5', 'Lamps on the walkway posts (+5 m)', 5, 1)
hood45 = A.level('hood45', "Cottage: the door hood (+4.5 m)", 4.5, 2)
up6 = A.level('up6', "Cottage upper floor, storehouse loft (+6 m)", 6, 3.5)
crane = A.level('crane', 'The crane jib (+7.5 m)', 7.5, 1)
roof8 = A.level('roof8', 'The north range roof (+8 m)', 8, 8)
hoist = A.level('hoist', 'Storehouse: the hoist beam (+9.5 m)', 9.5, 1)
roof95 = A.level('roof95', "Carpenter's cottage roof (+9.5 m)", 9.5, 5)

# ================================================================= the lake (bed 4 m down)
P.ground_rect(0, 0, 66, 60, -4)
R(lake, 0, 68, 66, 128, '~')

# ================================================================= the west walkway (+3 m)
# 6 m of rough wood with a wooden railing just outside each edge (the square's style), from the square's stair
# west to the smithy's lane; there the run turns south, on the lane's line (x 34..40), down to the carpentry.
# The bathhouse branch leaves its south side at x 54..58.
R(walk, 34, 77, 56, 83, 'w')
R(walk, 34, 83, 40, 90, 'w')                            # the carpentry branch
R(walk, 54, 83, 58, 86, 'w')                            # the bathhouse branch (its stair: the bathhouse blueprint)
A.rail(walk, 40, 76.5, 56, 77)                          # north side, from the smithy's strip to the square's part
A.rail(walk, 33.5, 77, 34, 90)                          # west side of the run, down to the carpentry stair
A.rail(walk, 40, 83, 54, 83.5, [(45, 49)]); A.rail(walk, 40, 83.5, 40.5, 90)
# a bay off the south side between the branches, a bench in it looking out over the water to the carpentry
R(walk, 45, 83, 49, 84.5, 'w')
A.rail(walk, 44.5, 83.5, 45, 85); A.rail(walk, 49, 83.5, 49.5, 85); A.rail(walk, 45, 84.5, 49, 85)
put('walk', 'Bench', 46, 84)
# lamp posts in the railings (lamps on top, +5 m), and either side of the stair down to the carpentry
for x0, y0 in ((44, 76.5), (51.5, 76.5), (42, 83), (51.5, 83), (33.5, 89.5), (40, 89.5)):
    R(walk, x0, y0, x0 + 0.5, y0 + 0.5, 'U'); R(lamp5, x0, y0, x0 + 0.5, y0 + 0.5, 'l')
A.rail(walk, 53.5, 83.5, 54, 86)
zone('walk', 'West walkway', 34, 77, 56, 83, '#2f8f8a')
zone('walk', 'Branch down to the carpentry', 34, 83, 40, 90, '#2f8f8a')
R(low, 34, 90, 40, 92, 'w')
A.stairs('low', 'Stairs down to the carpentry', 34, 90, 40, 92, 1, 'N')
A.cheeks(low, 34, 90, 40, 92, 'N')

# ================================================================= the carpentry deck (+2 m)
# 34 x 34 m of refined wood on a tarred edge (the layout had 32 x 28), a wooden railing round it, open where
# the lane's stair, the dock stair and the arena stair arrive
A.deck(low, 10, 92, 44, 126, 'r', 't')
A.rail(low, 10, 92, 44, 92.5, [(34, 40)])
A.rail(low, 10, 92.5, 10.5, 126, [(110, 116)])
A.rail(low, 10, 125.5, 44, 126)
A.rail(low, 43.5, 92.5, 44, 125.5, [(93, 104), (109.5, 124.5)])
zone('low', 'Carpentry and storehouse (Carpenter)', 10, 92, 44, 126, '#9a7344')
# the lane: field stones on from the smithy's lane, down from the stair to the work yard at its foot
R(low, 34, 92, 40, 107, 'c')
R(low, 34, 107, 43.5, 117, 'c')
zone('low', "Carpenters' lane", 34, 92, 40, 107, '#8a8f96')
zone('low', 'Work yard', 34, 107, 44, 117, '#8a8f96')

# ---- the north range: one building under one roof. The storehouse at the west end, rough stone (6 m), over
# the dock; the workshop beside it, half-timbered on a stone plinth (6 m), its double door on the lane and
# another onto the timber yard; a door between them.
A.walls(PL, 18.5, 93, 33, 106, 'Q')
A.walls(low, 18.5, 93, 33, 106, 'H', 'r')
A.walls(low, 11, 93, 19, 106, 'S', 'r')                 # (its east wall is the party wall)
R(PL, 18.5, 93, 19, 106, ' ')
A.door('low', 'Wooden Door', 18.5, 99, 19, 101)
R(PL, 32.5, 97, 33, 101, 'r'); A.door('low', 'Wooden Double Door', 32.5, 97, 33, 101)
R(PL, 24, 105.5, 28, 106, 'r'); A.door('low', 'Wooden Double Door', 24, 105.5, 28, 106)
A.door('low', 'Metal Bound Wooden Double Door', 13, 105.5, 17, 106)
# the workshop: the Carpenter, the Table Saw, a workbench, the 1.0 Decoration and Sparkworks workbenches
put('low', 'npc-carpenter', 29, 94, label='Carpenter (Cade Hawthorn)')
put('low', 'table-saw', 21, 94); put('low', 'workbench', 24.5, 94)
put('low', 'chest-large', 26.5, 94)
put('low', 'Decoration Workbench', 20, 102.5); put('low', 'Sparkworks Workbench', 29.5, 102.5)
zone('low', 'Workshop (Carpenter)', 18.5, 93, 33, 106, '#9a7344')
# the storehouse: bulk wood and stone in huge chests
for y, what in ((94, 'logs'), (97, 'planks'), (100.5, 'stone')):
    put('low', 'chest-huge', 11.5, y, 270, label=f'Huge Chest ({what})')
put('low', 'chest-huge', 17, 94, 90, label='Huge Chest (nails, metal, glue)')
zone('low', 'Storehouse (bulk wood and stone)', 11, 93, 19, 106, '#8a5cc2')
# windows: high ones along the workshop's north wall (over the benches), more either side of its doors; small
# high ones in the storehouse
for x in (20, 23, 27, 30.5):
    A.win('low', 'Wooden Window Frame', x, 93, x + 1, 93.5, 2.5)
for y in (94, 103):                                                 # (the north one high, over the Carpenter's head)
    A.win('low', 'Wooden Window Frame', 32.5, y, 33, y + 1, 2.5 if y == 94 else 1.5)
for x in (20, 30):
    A.win('low', 'Wooden Window Frame', x, 105.5, x + 1, 106, 1.5)
A.win('low', 'Wooden Window Frame', 14, 93, 15, 93.5, 2.5)
for y in (95, 103):
    A.win('low', 'Wooden Window Frame', 11, y, 11.5, y + 1, 2.5)
put('low', 'High Crude Wooden Shelf', 19, 95, 270); put('low', 'High Crude Wooden Shelf', 19, 102.5, 270)
# lived in: sawdust round the saw, a hammer left on the bench, a chair half made by the decoration bench,
# offcuts, the workshop dog's bed by the Carpenter
R(low, 20.5, 96, 23.5, 97, 'z'); R(low, 23, 94, 23.5, 96, 'z')
put('low', 'Construction Hammer', 25, 94.5, z=1)
put('low', 'Rustic Chair', 22.5, 103, 90, label='Rustic Chair (half made)')
put('low', 'Resource Bundle I', 29.5, 99, label='Resource Bundle I (offcuts)')
put('low', 'Dog Pillow', 26.5, 96, label="Dog Pillow (the workshop dog's)"); put('low', 'Dog Bowl', 27.5, 96)
# the east gable, over the lane: its middle raised for a round window, as the forge hall's is
R(low, 32.5, 99, 33, 100, 'g')
A.win('low', 'Round Wooden Window Frame', 32.5, 99, 33, 100, 8)
put('low', 'Ceiling Lantern', 23, 99); put('low', 'Ceiling Lantern', 28, 100)
put('low', 'Hanging Lantern', 15, 99.5)
put('low', 'Wall Lantern', 33, 95.5, 270, 2.0); put('low', 'Wall Lantern', 23, 106, 0, 2.0)
# a tarred shingle hood over the workshop's double door onto the lane, on brackets
hd = A.roof(roof55)
hd.shed(33, 96.5, 34, 101.5, 'w', 'lead', pitch=1.0, overhang=0)
hd.paint()
for y in (96.5, 101):
    A.overlay(low, 33, y, 33.5, y + 0.5, 'Refined Wood Block (bracket)', WOOD, 0.5, 3)
# the carpentry's sign, on a bracket from the range's corner over the top of the lane
A.overlay(low, 33, 93.5, 33.5, 94, 'Refined Wood Block (sign bracket)', WOOD, 0.5, 3.5)
A.overlay(low, 33.5, 93.5, 34.5, 94, "Tarred Wood Block (the carpentry's sign)", TAR, 1, 2.5)
# the storehouse loft (+6 m): a floor under the roof, a ladder up through a hatch, and a loft door in the west
# gable onto a little platform over the dock, a hoist beam above it to lift goods off the boats
R(low, 11, 98, 11.5, 102, 's')                          # the gable wall stops at the loft floor for the door,
R(up6, 11, 98, 11.5, 102, 'T')                          # which sits in a stretch of wall of its own
R(up6, 11.5, 93.5, 18.5, 105.5, 'r')
R(up6, 17.5, 104, 18.5, 105, ' '); R(up6, 17, 104, 17.5, 105, 'i')
put('low', 'ladder', 17.5, 104, label='Ladder up to the storehouse loft')
A.door('up6', 'Wooden Door', 11, 99, 11.5, 101)
R(up6, 9.5, 98.5, 11, 101.5, 't')
A.rail(up6, 9, 98, 11, 98.5); A.rail(up6, 9, 98.5, 9.5, 101.5); A.rail(up6, 9, 101.5, 11, 102)
for y in (98.5, 101):
    A.overlay(low, 10.5, y, 11, y + 0.5, 'Refined Wood Block (bracket)', WOOD, 0.5, 3)
R(hoist, 8, 99.5, 11, 100, 'F')
A.overlay(dock, 8, 99.5, 8.5, 100, 'Plaited Block (hoist rope)', '#867561', 5.5, 3)
R(hook, 8, 99.5, 8.5, 100, 'K')
for (x, y, it) in ((12, 94, 'Supply Sacks II'), (12, 96, 'Resource Bundle II'), (14, 104, 'Scrappy Crate'), (12, 104, 'Supply Sacks I')):
    put('up6', it, x, y)
zone('up6', 'Storehouse loft (hoist door to the dock)', 11, 93, 19, 106, '#8a5cc2')

# ---- the kiln shed, across the lane: fired brick, open to the lane, the Kiln under its own stack
A.walls(low, 40.5, 93, 44, 104, 'B', 'b')
R(low, 40.5, 93.5, 41, 103.5, 'b')                      # open to the lane
R(low, 43, 96.5, 44, 97.5, P._alloc({'name': 'Fired Bricks Block (kiln stack)', 'kind': 'wall', 'color': BRICK, 'height': 8}))
put('low', 'kiln', 41, 96, 90)
bricks = P._alloc({'name': 'Fired Bricks Block (brick stack)', 'kind': 'block', 'color': BRICK, 'height': 1})
R(low, 41.5, 100, 43, 101.5, bricks); R(low, 41.5, 102, 43, 103.5, bricks)
put('low', 'Supply Sacks II', 41.5, 94, label='Supply Sacks II (clay and sand)')
put('low', 'Hanging Lantern', 42, 99)
put('low', 'Scrap Pot I', 41.5, 98.5, label='Scrap Pot I (fresh from the kiln)'); put('low', 'Scrap Pot II', 42.5, 98.5)
put('low', 'Resource Bundle I', 42.5, 104.5, label='Resource Bundle I (firewood for the kiln)')
zone('low', 'Kiln shed', 40.5, 93, 44, 104, '#a0613f')

# ---- the stone yard: rough-cut stone in front of the storehouse, the Masonry Tools under a lean-to on posts
R(low, 11, 106, 19, 110, 'k')
R(low, 11, 109.5, 11.5, 110, 'n'); R(low, 18.5, 109.5, 19, 110, 'n')
put('low', 'masonry-tools', 11.5, 107)
R(low, 16, 107, 18.5, 109, P._alloc({'name': 'Roughly Cut Stone Block (stone stack)', 'kind': 'block', 'color': RCS, 'height': 1}))
put('low', 'Wall Lantern', 12, 106, 0, 2.0)
zone('low', 'Stone yard (Masonry Tools)', 11, 106, 19, 110, '#8a8f96')

# ---- the timber yard: worn rough wood, the drying shed (a long roof on posts for seasoning planks), and the
# jib crane on the yard's west edge, swinging out over the dock
R(low, 19, 106, 34, 117, 'w'); R(low, 10.5, 110, 19, 125.5, 'w'); R(low, 19, 117, 34, 125.5, 'w')
for x in (14, 18.5, 23, 27.5, 31.5):
    for y in (117, 122.5):
        R(low, x, y, x + 0.5, y + 0.5, 'N')
zone('low', 'Timber yard', 10.5, 106, 34, 125.5, '#7a6653')
zone('low', 'Drying shed (seasoning planks)', 14, 117, 32, 123, '#7a6653')
R(low, 11, 119, 12, 120, 'M')                           # the crane: a mast on the yard's edge,
R(crane, 6.5, 119, 12, 120, 'J')                        # its jib out over the dock,
A.overlay(dock, 6.5, 119, 7, 119.5, 'Plaited Block (crane rope)', '#867561', 3.5, 3)
R(hook, 6.5, 119, 7, 119.5, 'K')                        # and the hook,
for i, x in enumerate((10.5, 10, 9.5, 9)):              # a brace stepping up from the mast under the jib
    R(brace, x, 119, x + 0.5, 120, P._alloc({'name': 'Refined Wood Block (crane brace)', 'kind': 'block', 'color': WOOD, 'height': 0.5, 'base': 3.5 + i * 0.5}))
zone('low', 'Jib crane (timber off the boats)', 6.5, 118.5, 12, 120.5, '#7a6653')
# logs by the crane and the dock stair; planks stacked to season under the drying shed, aisles between
R(low, 12, 112, 16, 114.5, P._alloc({'name': 'Rough Wood Block (log pile)', 'kind': 'block', 'color': '#7a6653', 'height': 1}))
planks = P._alloc({'name': 'Refined Wood Block (plank stack)', 'kind': 'block', 'color': WOOD, 'height': 1.5})
for x0, x1 in ((15, 17.5), (19.5, 22.5), (24, 27), (28.5, 31)):
    R(low, x0, 118, x1, 122, planks)
put('low', 'Ground Lantern II', 19.5, 107); put('low', 'Ground Lantern II', 11.5, 116.5)
put('low', 'Resource Bundle I', 17, 112, label='Resource Bundle I (logs)')
# a boat on trestles outside the workshop's yard door, half planked (ribs showing at the stern end): the
# village needs boats
trestle = P._alloc({'name': 'Refined Wood Block (trestle)', 'kind': 'block', 'color': WOOD, 'height': 1})
for x in (22, 25.5):
    R(low, x, 111, x + 0.5, 112.5, trestle)
hull = lambda h, b: P._alloc({'name': 'Refined Wood Block (boat hull)', 'kind': 'block', 'color': WOOD, 'height': h, 'base': b})
R(work, 21.5, 111.5, 26.5, 112, hull(0.5, 1))           # the keel and bottom planks
R(work, 21, 111.5, 21.5, 112, hull(1.5, 1))             # the stem, at the bow
R(work, 26.5, 111.5, 27, 112, hull(1, 1))               # the sternpost
for y in (111, 112):                                    # the sides: planked forward, ribs aft
    R(work, 22, y, 24.5, y + 0.5, hull(0.5, 1.5))
    for x in (24.5, 25.5):
        R(work, x, y, x + 0.5, y + 0.5, hull(1, 1.5))
put('low', 'Construction Hammer', 23, 113)
zone('low', 'Boat on trestles (half built)', 21, 111, 27, 112.5, '#7a6653')
# a sawhorse by the log pile with a log across it
R(low, 13, 115.5, 13.5, 116, trestle); R(low, 15, 115.5, 15.5, 116, trestle)
R(work, 12.5, 115.5, 16, 116, P._alloc({'name': 'Rough Wood Block (log, on the sawhorse)', 'kind': 'block', 'color': '#7a6653', 'height': 0.5, 'base': 1}))
# the workers' break table at the yard's south end: a jug and cups, two stools
put('low', 'Crude Wooden Side Table', 22, 123.5)
put('low', 'Crude Wooden Stool', 21, 124); put('low', 'Crude Wooden Stool', 23.5, 124)
put('low', 'Crude Wooden Jug', 22, 123.5, z=1); put('low', 'Wooden Cup', 22.5, 124, z=1)

# ---- the Carpenter's cottage (SE): refined wood on a stone plinth with conifer corner posts, conifer upstairs, a carved door onto the work
# yard (the Carpenter shows off the trade), a stair up the back wall, a fireplace under the west chimney
# (its stair on whole metres, so it stays clean in the 1 m site plan)
A.walls(PL, 35, 116.5, 44, 124.5, 'Q')
A.walls(low, 35, 116.5, 44, 124.5, 'R', 'r')
R(PL, 38, 116.5, 40, 117, 'r'); A.door('low', 'Carved Wooden Door', 38, 116.5, 40, 117)
A.stairs('low', "Cottage stair up", 37, 123, 41, 124, 4, 'E')
for cx, cy in ((35, 116.5), (43.5, 116.5), (35, 124), (43.5, 124)):
    R(low, cx, cy, cx + 0.5, cy + 0.5, 'C')
R(low, 34.5, 119.5, 35.5, 120.5, P._alloc({'name': 'Rough Stone Block (chimney)', 'kind': 'wall', 'color': RS, 'height': 13}))
put('low', 'Fireplace', 35.5, 119, 270)
put('low', 'table', 38.5, 120); put('low', 'Rustic Chair', 38.5, 121, 180)
A.walls(up6, 35, 116.5, 44, 124.5, 'Y', 'r')
R(up6, 35, 119.5, 35.5, 120.5, ' ')                     # the chimney passes up through the wall
R(up6, 37, 123, 41, 124, ' ')                           # the stairwell, railed
R(up6, 37, 122.5, 41, 123, 'i'); R(up6, 36.5, 123, 37, 124, 'i')
put('up6', 'bed', 41.5, 117.5, label='Bed (Cade Hawthorn)')
put('up6', 'chest-small', 36, 117.5)
# carved windows all round (the trade on show), window boxes upstairs, a round carved window high in the east
# gable, a tiled hood over the carved door, a bench by it, carved furniture
for x in (35.5, 40.5):
    A.win('low', 'Carved Wooden Window Frame I', x, 116.5, x + 1, 117, 1)
A.win('low', 'Carved Wooden Window Frame I', 43.5, 118, 44, 119, 1)
A.win('low', 'Carved Wooden Window Frame I', 35, 122, 35.5, 123, 1)
A.win('low', 'Carved Wooden Window Frame I', 42, 124, 43, 124.5, 1)
for x in (37, 41.5):
    A.win('up6', 'Carved Wooden Window Frame I', x, 116.5, x + 1, 117, 1)
    R(up6, x, 116, x + 1, 116.5, 'x')
A.win('up6', 'Carved Wooden Window Frame I', 38.5, 124, 39.5, 124.5, 1)
A.win('up6', 'Carved Wooden Window Frame I', 35, 123, 35.5, 124, 1)
R(up6, 43.5, 120, 44, 121, 'G')
A.win('up6', 'Round Carved Window Frame', 43.5, 120, 44, 121, 4)
put('low', 'Large Carved Wooden Cabinet', 42.5, 121, 90)
put('low', 'Hanging Lantern', 39.5, 119)
# lived in: a mat before the hearth, the kettle by it, supper things on the table, firewood by the chimney,
# a mat by the bed, a flower border along the south wall
put('low', 'Big Straw Mat', 36.5, 119); put('low', 'Kettle', 36.5, 121.5)
put('low', 'Wooden Bowl', 39, 120, z=1); put('low', 'Wooden Cup', 40, 120.5, z=1)
put('low', 'Resource Bundle I', 34, 121, label='Resource Bundle I (firewood)')
put('up6', 'Straw Mat', 40, 118.5)
R(low, 35.5, 124.5, 43.5, 125.5, 'e')
put('up6', 'Carved Wooden Nightstand', 40.5, 117.5)
put('up6', 'Large Carved Wooden Cabinet', 35.5, 121, 270)
put('up6', 'Hanging Lantern', 39, 119.5, z=3)
ch = A.roof(hood45)
ch.shed(37.5, 115.5, 40.5, 116.5, 's', 'tiles', pitch=1.0, overhang=0)
ch.paint()
for x in (37.5, 40):
    A.overlay(low, x, 116, x + 0.5, 116.5, 'Refined Wood Block (bracket)', WOOD, 0.5, 2)
put('low', 'Bench', 35.5, 115.5, 180)
zone('low', "Carpenter's cottage (Cade Hawthorn)", 35, 116.5, 44, 124.5, '#9c6b8e')

# lanterns at the top of the lane, by the arena stair's foot, crates by the kiln shed
put('low', 'Ground Lantern II', 33, 93); put('low', 'Ground Lantern II', 40, 93)
put('low', 'Ground Lantern II', 41.5, 109)
put('low', 'Scrappy Crate', 40.5, 104.5); put('low', 'Supply Sacks I', 41.5, 104.5)

# ---- the stair up to the arena's stands (+4 m), from the work yard's east edge
R(low, 42, 110, 46, 116, 'r')
A.stairs('low', 'Stairs: carpentry to the arena', 42, 110, 46, 116, 2, 'E')
A.cheeks(low, 42, 110, 46, 116, 'E')

# ================================================================= the west dock (+1 m)
# Tarred wood along the deck's west side, from the storehouse down past the crane; a stair up into the
# timber yard
R(dock, 2, 96, 10, 124, 't')
A.stairs('dock', 'Stairs down to the west dock', 8, 110, 10, 116, 1, 'E')
A.cheeks(dock, 8, 110, 10, 116, 'E')
zone('dock', 'West dock (timber and stone in)', 2, 96, 10, 124, '#2f7fb3')
for y in (97, 104, 108, 116.5, 122.5):                  # bollards along the water's edge
    A.overlay(dock, 2, y, 2.5, y + 0.5, 'Refined Wood Block (bollard)', WOOD, 1, 0)
put('dock', 'Scrappy Crate', 6, 107); put('dock', 'Supply Sacks II', 7, 107)
put('dock', 'Ground Lantern II', 3, 96.5); put('dock', 'Ground Lantern II', 3, 123)
# a rowing boat moored off the dock's south end (on the water, a thwart across the middle)
rb = lambda h, b=0: {'name': 'Refined Wood Block (rowing boat)', 'color': WOOD, 'height': h, 'base': b}
for (x0, y0, x1, y1, h, b) in ((3.5, 124.5, 4, 125, 1, 0), (3.5, 127.5, 4, 128, 1, 0), (3.5, 125, 4, 127.5, 0.5, 0),
                               (3, 125, 3.5, 127.5, 1, 0), (4, 125, 4.5, 127.5, 1, 0)):
    e = rb(h, b)
    A.overlay(lake, x0, y0, x1, y1, e['name'], e['color'], e['height'], e['base'])
A.overlay(lake, 3.5, 126, 4, 126.5, 'Refined Wood Block (rowing boat, thwart)', WOOD, 0.5, 0.5)
zone('lake', 'Rowing boat (moored)', 3, 124.5, 4.5, 128, '#2f7fb3')

# ================================================================= the neighbours' edges (their own blueprints)
# the smithy (+4 m): its south edge, its lane, the stair down to the walkway
R(mid, 12, 68, 44, 70, 'k'); R(mid, 13, 68, 43, 69, 'b'); R(mid, 34, 68, 40, 70, 'c')
A.parapet(mid, 12, 69.5, 44, 70, [(34, 40)])
R(walk, 34, 70, 40, 77, 'w')
A.stairs('walk', 'Stairs up to the smithy (smithy blueprint)', 34, 70, 40, 72, 1, 'N')
A.cheeks(walk, 34, 70, 40, 72, 'N')
A.rail(walk, 33.5, 72, 34, 77); A.rail(walk, 40, 72, 40.5, 76.5)
zone('mid', 'Smithy (smithy blueprint)', 12, 68, 44, 70, '#5f6770')
# the square (+4 m): its part of the walkway and its stair down to it
R(walk, 56, 77, 64, 83, 'w')
A.stairs('walk', 'Stairs: square to the west walkway (square blueprint)', 62, 77, 64, 83, 1, 'E')
A.rail(walk, 56, 76.5, 62, 77); A.rail(walk, 58, 83, 62, 83.5); A.rail(walk, 58, 83.5, 58.5, 86)
R(mid, 64, 70, 66, 90, 'f')
zone('walk', 'West walkway, its east end (square blueprint)', 56, 77, 64, 83, '#2f8f8a')
# the bathhouse (+2 m) and its stair up to the branch
R(low, 46, 86, 62, 98, 't'); R(low, 47, 87, 61, 97, 'h')
A.stairs('low', 'Stairs up to the west walkway (bathhouse blueprint)', 54, 86, 58, 88, 1, 'N')
zone('low', 'Barber and bathhouse (bathhouse blueprint)', 46, 86, 62, 98, '#3f7f9e')
# the arena's stands (+4 m), with a landing where the stair arrives
A.circle(mid, 59, 113, 26, 'k'); A.circle(mid, 59, 113, 14, ' ')
R(mid, 46, 110, 48, 116, 'k')
zone('mid', 'Arena stands (arena blueprint)', 46, 100, 66, 126, '#c2416e')

# ================================================================= roofs, at 45 degrees (or 1 in 2) in even steps
# the north range: one dark tarred shingle gable over storehouse and workshop together (ridge east-west)
rr = A.roof(roof8)
rr.gable(11, 93, 33, 106, 'x', 'lead', pitch=1.0, overhang=0.5)
rr.caps('shingle', min_lower=1)
rr.paint()
# a louvred ventilator on the ridge over the workshop (sawdust and heat out), under a little hipped roof
vent_el = 8 + rr.top(25, 99)
vent = A.level('vent', 'North range: the ventilator (+%g m)' % vent_el, vent_el, 1.5)
ventroof = A.level('ventroof', 'North range: the ventilator roof (+%g m)' % (vent_el + 1.5), vent_el + 1.5, 2)
R(vent, 24, 99, 28, 100, 'v')
rv = A.roof(ventroof)
rv.hip(24, 99, 28, 100, 'lead', pitch=1.0, overhang=0.5)
rv.paint()
# the kiln shed: a stone shingle shed rising to its back wall, 1 in 2, cut round the stack
rk = A.roof(roof6)
rk.shed(40.5, 93, 44, 104, 'e', 'shingle', pitch=0.5, overhang=0.5)
rk.cut(43, 96.5, 44, 97.5)
rk.paint()
# the stone yard's lean-to: stone shingle, 1 in 2, down from the range's wall
rl = A.roof(roof5)
rl.shed(11, 106, 19, 110, 'n', 'shingle', pitch=0.5, overhang=0)
rl.paint()
# the drying shed: a tarred straw gable on posts
rd = A.roof(roof55)
rd.gable(14, 117, 32, 123, 'x', 'tarstraw', pitch=1.0, overhang=0.5)
rd.caps('fibre', min_lower=1)
rd.paint()
# the cottage: a tiled gable, ridge east-west, cut round the chimney
rc = A.roof(roof95)
rc.gable(35, 116.5, 44, 124.5, 'x', 'tiles', pitch=1.0, overhang=0.5)
rc.cut(34.5, 119.5, 35.5, 120.5)
rc.caps('lead', min_lower=1)
rc.paint()
# chimney caps: a course 0.5 m proud round the top of the cottage chimney (+15 m) and the kiln stack (+10 m)
caps = A.level('caps', 'Chimney caps (+9.5 m)', 9.5, 6)
A.ring(caps, 34.5, 119.5, 35.5, 120.5, P._alloc({'name': 'Rough Stone Block (chimney cap)', 'kind': 'block', 'color': RS, 'height': 0.5, 'base': 5}))
R(caps, 34.5, 119.5, 35, 120, P._alloc({'name': 'Fired Bricks Block (chimney pot)', 'kind': 'block', 'color': BRICK, 'height': 0.5, 'base': 5.5}))
A.ring(caps, 43, 96.5, 44, 97.5, P._alloc({'name': 'Fired Bricks Block (stack cap)', 'kind': 'block', 'color': BRICK, 'height': 0.5}))

# ================================================================= stilts, rim beams and checks
print('stilts:', A.stilts(stl, [('dock', 1), ('low', 2), ('walk', 3), ('mid', 4)]))
own = lambda x, y: ((33.5 <= x < 56 and 76.5 <= y < 83.5) or (33.5 <= x < 40.5 and 83.5 <= y < 92) or (53.5 <= x < 56 and 83.5 <= y < 86)
                    or (10 <= x < 44 and 92 <= y < 126) or (2 <= x < 10 and 96 <= y < 124) or (42 <= x < 46 and 109.5 <= y < 116.5))
print('rim beam squares:', A.rim_beams(stl, [('dock', 1), ('low', 2), ('walk', 3)], own))
A.spawn('low', 36.5, 93.5, 0)                                 # walk mode starts here: the top of the carpenters' lane, looking down it
A.checks()

NOTES = """Laketown: the carpentry, storehouse and west dock, with the west walkway, as a 0.5 m detail blueprint (all three passes done). Drafted by Claude.
This plan's corner is the layout's (0, 68), so it lines up with the Laketown layout and stamps back into the site plan there.

PASSES
1. Design and bones: the decks, the walkway and its branches, building shells with walls, doors, stairs and roof shapes, the stations, the crane, the connections, stilts, labels.
2. Details: windows, the storehouse loft and hoist, the ventilator, the sign, hoods, lamps, the yards' timber, stone and bricks, the dock's bollards, furniture and lights. Then a 3D review and a refining round.
3. Review and finishing touches (this one): making it feel lived in, the range's east gable, the layout, the site plan.

PASS 3: WHAT THE REVIEW FOUND AND CHANGED
- It looked built but not lived in: nothing in progress, nobody's things about. Now:
  - the workshop has sawdust round the Table Saw, a hammer left on the bench, a chair half made by the Decoration Workbench, a heap of offcuts, and the workshop dog's bed and bowl by the Carpenter;
  - a boat sits on trestles outside the workshop's yard door, its forward planks on and its ribs still bare aft, a hammer beside it: the village needs boats;
  - a log lies across a sawhorse by the log pile;
  - the workers' break table at the timber yard's south end, a jug and cups on it, two stools;
  - fresh pots by the Kiln, firewood stacked for it;
  - the storehouse's huge chests labelled (logs, planks, stone, nails and metal);
  - in the cottage, a mat before the hearth, the kettle by it, a bowl and cup on the table, firewood stacked by the chimney outside, a mat by the bed, a flower border along the south wall;
  - a rowing boat moored off the dock's south end.
- The range's east gable faces everyone coming down the lane and was blank above the doors: its middle rises for a round window, as the forge hall's does.
- The 1 m layout (doc laketown) now matches: the bigger deck, the dock running on south, the dock stair moved to the timber yard, labels for the range, the yards, the kiln shed and the cottage. The layout's bathhouse branch and its stair moved to x 54..58, where the square's blueprint and the walkway have them.
- Checked, all clear: nothing in front of any door or window, no door onto a drop, every stair with 1 m clear at the foot and top and 2 m of headroom, no item running into another or into a raised piece, nothing outside the altar's build volume. In the site plan, nothing is blocked where the carpentry meets the smithy, the square, the bathhouse branch and the arena.

CONNECTIONS (for the neighbouring blueprints to match)
- Smithy (+4 m): the walkway's carpentry branch carries the smithy lane's line (x 34..40) straight on to the carpentry, as its hand-off asked.
- Square (+4 m): its stair down to the walkway (x 62..64) and its part of the walkway (x 56..64) carry on unchanged; the walkway's railings and lamp posts match its style.
- Bathhouse (+2 m, the bathhouse and arena blueprint): the branch leaves the walkway at x 54..58 and the bathhouse stair climbs to it at y 86..88. The carpentry deck's north-east corner (x 44, y 92..98) is 2 m from the bathhouse deck's west edge (x 46), both at +2 m: a short footbridge could join them, if the bathhouse wants a back way to the carpentry.
- Arena (+4 m, the same blueprint): the stair from the carpentry's work yard arrives at x 46, y 110..116. The stands' outer edge doesn't reach x 46 at the stair's ends: it needs a landing at x 46..48 there (this blueprint draws one as a placeholder).

THE WEST WALKWAY (+3 m): 6 m of rough wood with a wooden railing just outside each edge (the square's style), from the square's stair west to the smithy's lane. There the run turns south on the lane's line (x 34..40), so the smithy, the walkway and the carpentry are one straight run, and steps down 1 m onto the carpentry deck between stone cheeks. The bathhouse branch leaves the walkway's south side at x 54..58.
- Lamp posts in the railings with lamps on top, and either side of the stair down to the carpentry.
- A bay off the south side between the branches, with a bench looking out over the water to the carpentry.

THE CARPENTRY (+2 m, 34 x 34 m; the layout had 32 x 28): refined wood on a tarred edge, a wooden railing round it.
- The carpenters' lane: field stones on from the smithy's lane, lanterns at its top, the carpentry's sign hanging over it from the range's corner; down to the work yard at its foot.
- The north range: one long building under one big tarred shingle roof (ridge east-west) with a stone shingle ridge and a louvred ventilator on the ridge over the workshop (sawdust and heat out).
  - The storehouse, at the west end over the dock: rough stone, 6 m walls, small high windows, a metal-bound double door onto the stone yard, huge chests for bulk wood and stone. A loft under the roof (+6 m), up a ladder through a hatch, with sacks, crates and bundles; its loft door in the west gable opens onto a railed platform over the dock, a hoist beam and hook above it to lift goods off the boats.
  - The workshop (Carpenter, Cade Hawthorn): half-timbered on a stone plinth, 6 m walls. A double door onto the lane under a tarred shingle hood on brackets, another onto the timber yard, a door through to the storehouse. High windows along the north wall over the benches, more either side of the doors. Inside: the Table Saw, a workbench, a large chest, 1.0's Decoration Workbench and Sparkworks Workbench, shelves, lanterns.
- The kiln shed, across the lane: fired brick, open to the lane, the Kiln under its own capped stack, stacks of bricks, sacks of clay and sand, a lantern; a stone shingle roof.
- The stone yard, in front of the storehouse: rough-cut stone, the Masonry Tools under a lean-to on posts, a stack of cut stone, a lantern by the door.
- The timber yard: worn rough wood. A log pile by the dock stair; a long drying shed (a tarred straw roof on posts, a plant fibre ridge) with planks stacked to season under it and aisles between; a jib crane on the yard's west edge, a brace under its jib, the jib swinging out over the dock with a rope and hook to lift timber off the boats; lanterns.
- The work yard at the foot of the lane: crates and sacks by the kiln shed, a lantern by the stair up to the arena's stands (2 m).
- The Carpenter's cottage (SE): two storeys, refined wood on a stone plinth with conifer corner posts and conifer upstairs (two woods: the trade on show), a tiled gable with a dark ridge, a capped chimney with a pot. A carved door under a tiled hood, carved windows all round (window boxes upstairs), a round carved window high in the east gable, a bench by the door. Inside: a fireplace, a table, a carved cabinet, the stair up; upstairs the bed, a carved nightstand and cabinet, a chest.

THE WEST DOCK (+1 m): tarred wood along the deck's west side, from under the storehouse's hoist down past the crane; bollards along the water's edge, crates and sacks, lanterns at its ends; a stair up into the timber yard.

CONNECTIONS
- North: the west walkway's carpentry branch, on the smithy lane's line (the smithy's hand-off).
- West walkway: the square's stair at its east end (the square blueprint), the smithy's stair at its west end (the smithy blueprint), the bathhouse branch at x 54..58 (its stair: the bathhouse blueprint).
- East: the stair up to the arena's stands (x 42..46, y 110..116). The arena blueprint needs a landing at x 46..48 there: the stands' outer edge doesn't reach x 46 at the stair's ends.

STATIONS (1.0, Carpenter; 2 x 2 m placeholders until measured): Kiln, Table Saw, Workbench, Decoration Workbench, Sparkworks Workbench; Masonry Tools (made at the Forge, used for stonework). Carved door and window sizes are estimates (the plain ones' sizes) until measured; furniture and light sizes are estimates.

STILTS: 1 m posts on the layout's 4 m grid, from the lake bed 4 m down to each deck's underside, with tarred rim beams under the edges.
"""
A.save('laketown_carpentry.json', NOTES, 'r-claude-laketown-carpentry-3')
