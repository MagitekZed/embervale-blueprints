"""Laketown: the alchemist, the east junction and the east walkway's end. 0.5 m detail plan. Pass 3 of 3: review and finishing touches.

The east walkway comes from the square (+3 m) onto the east junction, the crossroads of the town's east side:
the farm's stair up (north), the alchemist's stair up (east), the hunting lodge's stair up (south), a
timber pavilion in its quiet corner. Up 3 m east between stepped stone flanks is the alchemist's round
platform (+6 m, polished granite), its herb garden in arcs round the south side, and in the middle the
Alchemist's tower: weathered stone, three storeys (his laboratory, his quarters, a drying loft for the herbs),
a mossy witch's hat of a roof and the lab's chimney. The herb bridge from the farm comes in at its back door.

Coordinates are the layout's (doc `laketown`): this plan's corner is the layout's (110, 64).
Run: python laketown_alchemist.py  ->  writes laketown_alchemist.json
"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laketown_common import Area, WOOD, STONE, BED

RCS, WEA = '#62605d', '#6a6c67'
GREEN, COPPER, RS = '#3f975e', '#8d694b', '#7d776a'                # the alchemist's green glow, his copper
OX, OY = 110, 64
A = Area('Laketown: the alchemist and the east junction (detail)', OX, OY, 48, 34, {
    'g': {'name': 'Polished Granite Block', 'kind': 'floor', 'color': '#626c7a'},       # the alchemist's platform
    'k': {'name': 'Roughly Cut Stone Block', 'kind': 'floor', 'color': RCS},            # its rim, the lab floor
    'o': {'name': 'Flower Soil', 'kind': 'floor', 'color': '#a77e63'},                  # the herb beds
    'c': {'name': 'Conifer Wood Block', 'kind': 'floor', 'color': '#6e5a51'},           # the hunting lodge (its)
    'X': {'name': 'Weathered Stone Block', 'kind': 'wall', 'color': WEA},               # the tower, a storey a level
    'K': {'name': 'Rough Stone Block (chimney)', 'kind': 'wall', 'color': '#7d776a', 'height': 17},
    'U': {'name': 'Refined Wood Block (lamp post)', 'kind': 'block', 'color': WOOD, 'height': 2},
    'p': {'name': 'Roughly Cut Stone Block (parapet)', 'kind': 'block', 'color': RCS, 'height': 1},
    'n': {'name': 'Refined Wood Block (pavilion post)', 'kind': 'block', 'color': WOOD, 'height': 3},
})
P, R, zone, put = A.P, A.R, A.zone, A.put
stl = A.level('stilts', 'Stilts, standing on the lake bed (-4 m)', BED, 12)
lake = A.level('lake', 'Lake (water level, 0 m)', 0, 1)
walk = A.level('walk', 'East walkway, east junction (+3 m)', 3, 4)
mid = A.level('mid', 'Hunting lodge, its edge (+4 m)', 4, 4)
up5 = A.level('up5', 'Farm and herb bridge, their edges (+5 m)', 5, 4)
high = A.level('high', "The alchemist's platform and tower (+6 m)", 6, 4)
a10 = A.level('a10', "Tower: the Alchemist's quarters (+10 m)", 10, 4)
a14 = A.level('a14', 'Tower: the drying loft (+14 m)', 14, 4)
aroof = A.level('aroof', 'Tower: the roof (+18 m)', 18, 8)
as6 = A.level('as6', 'Tower: spiral stair (+6 m)', 6, 4)
as10 = A.level('as10', 'Tower: spiral stair (+10 m)', 10, 4)
pav = A.level('pav', 'Junction: the pavilion roof (+6 m)', 6, 3)
lamp5 = A.level('lamp5', 'Lamps on the posts (+5 m)', 5, 1)
sign = A.level('sign', "Junction: the signpost's arms (+5 m)", 5, 2.5)
glow8 = A.level('glow8', 'Platform: the green caps on the posts (+8 m)', 8, 1)
sc10 = A.level('sc10', 'Tower: the string course (+10 m)', 10, 1)
sc14 = A.level('sc14', 'Tower: the string course (+14 m)', 14, 1)
chim = A.level('chim', 'Tower: the chimney pot (+23 m)', 23, 1)
still = A.level('still', 'Platform: the copper still (+6.5 m)', 6.5, 2)
hang14 = A.level('hang14', 'Tower: herbs hung along the balcony (+14 m)', 14, 4)


def block(name, color, h, base=0):
    e = {'name': name, 'kind': 'block', 'color': color, 'height': h}
    if base:
        e['base'] = base
    return P._alloc(e)


def lamp(x, y, g=None):
    """A yellow lamp on a post (the walkways' style): over the deck, or in a railing (g = its level)."""
    if g is None:
        A.overlay(walk, x, y, x + 0.5, y + 0.5, 'Refined Wood Block (lamp post)', WOOD, 2, 0)
    else:
        R(g, x, y, x + 0.5, y + 0.5, 'U')
    R(lamp5, x, y, x + 0.5, y + 0.5, block('Yellow Luminescent Block (lamp)', '#bd9a5f', 0.5))


def green_lamp(x, y):
    """The alchemist's lamps: a stone post with a green glowing cap."""
    A.overlay(high, x, y, x + 0.5, y + 0.5, 'Weathered Stone Block (lamp post)', WEA, 2, 0)
    R(glow8, x, y, x + 0.5, y + 0.5, block('Green Luminescent Block (a glowing cap)', GREEN, 0.5))

# ================================================================= the lake
def shoreline(x):
    return 140 + 2 * math.sin(x / 21) + 1.2 * math.sin(x / 8.3 + 1.3)


def ground(x, y):
    s = shoreline(x)
    if y < s:
        return -min(4, max(1, round((s - y) / 1.5)))
    return min(3, 1 + math.floor((y - s) / 3))


P.ground_fn(lambda mx, my: ground(mx + OX, my + OY))
for x, y in P.cells_rect(0, 0, 48, 34):
    if P.ground_at(x, y) < 0:
        lake[y][x] = '~'

# ================================================================= the east walkway's end and the junction (+3 m)
# The walkway (6 m of rough wood, a railing just outside each edge: the square's style) comes in from the
# square; the junction, 14 x 18 m of rough wood on a tarred edge, railings round it, open at the four ways
R(walk, 112, 77, 116, 83, 'w')
A.rail(walk, 112, 76.5, 116, 77); A.rail(walk, 112, 83, 116, 83.5)
zone('walk', 'East walkway', 112, 77, 116, 83, '#2f8f8a')
A.deck(walk, 116, 72, 130, 90, 'w', 't')
A.rail(walk, 116, 71.5, 130, 72, [(124, 130)])                     # north: the farm's stair
A.rail(walk, 115.5, 71.5, 116, 90.5, [(77, 83)])                   # west: the walkway
A.rail(walk, 130, 71.5, 130.5, 90.5, [(81, 87)])                   # east: the alchemist's stair
A.rail(walk, 116, 90, 130, 90.5, [(118, 124)])                     # south: the lodge's stair
zone('walk', 'East junction', 116, 72, 130, 90, '#2f8f8a')
# a timber pavilion in the junction's quiet north-west corner, off every way across it
for (x, y) in ((117, 73), (121.5, 73), (117, 76), (121.5, 76)):
    R(walk, x, y, x + 0.5, y + 0.5, 'n')
rp = A.roof(pav)
rp.hip(117, 73, 122, 76.5, 'lead', pitch=1.0, overhang=0.5)
rp.paint()
zone('walk', 'Pavilion', 117, 73, 122, 76.5, '#2f8f8a')
put('walk', 'Bench', 118, 75.5, label='Bench (in the pavilion)'); put('walk', 'Bench', 119.5, 73.5, label='Bench (in the pavilion)')
# a signpost in the middle of the junction, its arms pointing the four ways (square, farm, alchemist, lodge)
A.overlay(walk, 123, 80.5, 123.5, 81, 'Refined Wood Block (signpost)', WOOD, 4, 0)
for (x0, y0, x1, y1, b, to) in ((122, 80.5, 123, 81, 0, 'the square'), (123.5, 80.5, 124.5, 81, 0.5, 'the alchemist'),
                                (123, 79.5, 123.5, 80.5, 1, 'the farm'), (123, 81, 123.5, 82, 1.5, 'the hunting lodge')):
    R(sign, x0, y0, x1, y1, block(f'Tarred Wood Block (signpost arm: {to})', '#5d5652', 0.5, b))
# lamps in the railings; a planter with a shrub in the south-east corner
lamp(120, 71.5, walk); lamp(115.5, 75, walk); lamp(115.5, 87, walk); lamp(130, 76, walk); lamp(130, 89, walk)
lamp(127, 90, walk); lamp(114, 76.5, walk); lamp(114, 83, walk)
A.overlay(walk, 127, 87, 129, 89, 'Flower Soil (planter)', '#a77e63', 0.5, 0)
A.overlay(walk, 127.5, 87.5, 128.5, 88.5, 'Foliage (a shrub)', '#668f27', 1.5, 0)
# south: a strip and a stair up 1 m to the hunting lodge (its blueprint), stone cheeks
R(walk, 118, 90, 124, 96, 'w')
A.rail(walk, 117.5, 90.5, 118, 94); A.rail(walk, 124, 90.5, 124.5, 94)
A.stairs('walk', 'Stairs up to the hunting lodge', 118, 94, 124, 96, 1, 'S')
A.cheeks(walk, 118, 94, 124, 96, 'S')
lamp(117.5, 92, walk); lamp(124, 92, walk)

# ================================================================= the alchemist's platform (+6 m)
# The layout's round platform, 20 m across: polished granite on a roughly cut stone rim with a low parapet,
# open where the stair from the junction (west) and the herb bridge from the farm (north) arrive, a landing
# at each
CX, CY = 146, 84
A.circle(high, CX, CY, 20, 'k')
A.circle(high, CX, CY, 19, 'g')
R(high, 136, 81, 138, 87, 'g')                                      # the junction stair's landing
R(high, 143, 74, 149, 76.5, 'g')                                    # the herb bridge's landing
for x, y in P.cells_rect(CX - 10 - OX, CY - 10 - OY, CX + 10 - OX, CY + 10 - OY):
    mx, my = OX + x / 2 + 0.25, OY + y / 2 + 0.25
    d = math.hypot(mx - CX, my - CY)
    if 9.5 <= d <= 10 and high[y][x] == 'k':
        if (mx < 140 and 80.5 <= my < 87.5) or (142.5 <= mx < 149.5 and my < 78):
            continue
        high[y][x] = 'p'
zone('high', "Alchemist's platform", 136, 74, 156, 94, '#56806c')
# up 3 m east from the junction, between stepped stone flanks
A.stairs('walk', 'Stairs up to the alchemist', 130, 81, 136, 87, 3, 'E')
A.flanks(walk, 130, 81, 136, 87, 'E', steps=('1', '2', '3'))
# the herb garden: beds of flower soil in arcs round the south side, a path through them to the platform's
# southern edge
for x, y in P.cells_rect(CX - 9 - OX, CY + 2 - OY, CX + 9 - OX, CY + 9 - OY):
    mx, my = OX + x / 2 + 0.25, OY + y / 2 + 0.25
    if 6.5 <= math.hypot(mx - CX, my - CY) <= 8.5 and not (145.5 <= mx < 146.5):
        high[y][x] = 'o'
zone('high', 'Herb garden', 138, 86, 154, 93, '#3f8a4f')
for (x, y) in ((137, 80.5), (137, 87), (143, 76), (148.5, 76)):
    green_lamp(x, y)
# the copper still on the platform's north-east side: a stone hearth, the copper pot on it, its pipe stepping
# down to a jar
R(high, 152, 78, 153, 79, block('Rough Stone Block (the still\'s hearth)', RS, 0.5))
R(still, 152, 78, 153, 79, block('Copper Block (the still\'s pot)', COPPER, 1))
R(still, 153, 78.5, 153.5, 79, block('Copper Block (the still\'s pipe)', COPPER, 0.5, 0.5))
R(still, 153.5, 78.5, 154, 79, block('Copper Block (the still\'s pipe)', COPPER, 0.5, 0))
put('high', 'Scrap Pot II', 153.5, 79.5, label='Scrap Pot II (the still\'s jar)')
zone('high', 'Copper still', 152, 78, 154.5, 79.5, '#8d694b')
put('high', 'Bench', 148, 88, label='Bench (facing the herb beds)'); put('high', 'Bench', 142, 88, label='Bench (facing the herb beds)')

# ================================================================= the Alchemist's tower
# Round, 10 m across, three storeys of weathered stone (+6, +10, +14 m): his laboratory (a stone floor, the
# Alchemy Station, the Laboratory, the Mortar and the Grinding Stones), his quarters, a loft for drying the
# herbs; a stone spiral stair up the east side; the front door west (to the junction's stair), a back door
# north (to the herb bridge); the lab's chimney up the south-west side; a witch's hat of a roof in mossy
# shingles, its brim flared
TX, TY = 146, 82
for g, fl in ((high, 'k'), (a10, 'r'), (a14, 'r')):
    A.circle(g, TX, TY, 10, 'X')
    A.circle(g, TX, TY, 9, fl)
for g in (a10, a14):
    A.circle(g, 148.5, 82, 3, ' ')
A.spiral(as6, 148.5, 82, 3, 4, 'Tower stair', STONE, start=180)
A.spiral(as10, 148.5, 82, 3, 4, 'Tower stair', STONE, start=180)
A.door('high', 'Wooden Door', 141, 81, 141.5, 83)                  # the front door, west
A.door('high', 'Wooden Door', 145, 77, 147, 77.5)                  # the back door, north (the herb bridge)
R(high, 142.5, 84.5, 143.5, 85.5, 'K')                              # the lab's chimney, up through the floors
for g in (a10, a14):
    R(g, 142.5, 84.5, 143.5, 85.5, ' ')
rt = A.roof(aroof)
rt.cone(TX, TY, 5, 7, 'moss', overhang=1, flare=(1.5, 0.5))
rt.cut(142.5, 84.5, 143.5, 85.5)
rt.paint()
put('high', 'alchemy', 143, 79); put('high', 'laboratory', 147, 78.5)
put('high', 'mortar', 145.5, 84); put('high', 'grinding-stones', 142.5, 82.5)
put('high', 'npc-alchemist', 138, 85.5)
zone('high', "The Alchemist's laboratory", 141.5, 77.5, 150.5, 86.5, '#56806c')
zone('a10', "The Alchemist's quarters", 141.5, 77.5, 147, 86.5, '#9c6b8e')
zone('a14', 'Drying loft (herbs)', 141.5, 77.5, 147, 86.5, '#3f8a4f')
for g in (sc10, sc14):                                              # rough stone bands round it at each floor
    A.circle(g, TX, TY, 11, block('Rough Stone Block (string course)', RS, 0.5))
    A.circle(g, TX, TY, 10, ' ')
R(sc14, TX - 6, TY + 1, TX + 6, TY + 6, ' ')                        # (the upper one stops at the balcony)
R(chim, 142.5, 84.5, 143, 85, block('Fired Bricks Block (chimney pot)', '#aa7657', 0.5))
R(chim, 143, 85, 143.5, 85.5, block('Green Luminescent Block (the furnace\'s fumes)', GREEN, 0.5, 0.5))
# windows: the lab's to the south and east; his quarters' all round; the loft's west, north and east
A.win('high', 'Wooden Window Frame', 145.5, 86.5, 146.5, 87, 1); A.win('high', 'Wooden Window Frame', 150.5, 81.5, 151, 82.5, 1)
for g in ('a10', 'a14'):
    A.win(g, 'Wooden Window Frame', 141, 81.5, 141.5, 82.5, 1); A.win(g, 'Wooden Window Frame', 145.5, 77, 146.5, 77.5, 1)
    A.win(g, 'Wooden Window Frame', 150.5, 81.5, 151, 82.5, 1)
A.win('a10', 'Wooden Window Frame', 145.5, 86.5, 146.5, 87, 1)
# the drying balcony: a timber gallery round the loft's south side on brackets, its door from the loft, herbs
# hung to dry along its rail under the roof's brim
for x, y in P.cells_rect(TX - 7 - OX, TY - OY, TX + 7 - OX, TY + 7 - OY):
    mx, my = OX + x / 2 + 0.25, OY + y / 2 + 0.25
    d = math.hypot(mx - TX, my - TY)
    if 5 <= d <= 7 and my >= TY + 1:                                # 1.5 m of floor, a railing round its edge
        a14[y][x] = 'i' if d > 6.5 else 'r'
        if 6 < d <= 6.5 and int(mx * 2) % 3 == 0:                   # herbs hung under the roof's brim, fresh and dried
            fresh = int(mx * 2) % 6 == 0
            R(hang14, mx - 0.25, my - 0.25, mx + 0.25, my + 0.25,
              block('Foliage (herbs, hung to dry)' if fresh else 'Straw Roof Block (herbs, dried)', '#668f27' if fresh else '#a7753d', 1, 2.5))
        if 5.5 < d <= 6 and int(mx * 2) % 6 == 0:
            R(a10, mx - 0.25, my - 0.25, mx + 0.25, my + 0.25, block('Refined Wood Block (balcony bracket)', WOOD, 0.5, 3))
A.door('a14', 'Wooden Door', 145, 86.5, 147, 87)
zone('a14', 'Drying balcony', 140, 84, 152, 89, '#3f8a4f')
# the laboratory: a worktable in the middle, a chest of reagents, potions glowing green on a ledge by the
# north-west wall, a lantern
put('high', 'table', 145, 81.5, label='Table (the worktable)'); put('high', 'chest-medium', 143.5, 81, label='Medium Chest (reagents)')
for (x, y) in ((142, 79.5), (142.5, 79), (143, 78.5)):
    A.overlay(high, x, y, x + 0.5, y + 0.5, 'Green Luminescent Block (potions on a ledge)', GREEN, 0.5, 1.5)
put('high', 'Hanging Lantern', 146, 83, z=3)
# his quarters: bed, wardrobe, a fire against the chimney, a table and chair, a chest, a lantern
put('a10', 'bed', 143, 79, label='Bed (the Alchemist)'); put('a10', 'Crude Wooden Closet', 147, 78.5)
put('a10', 'Stone Fireplace', 143.5, 84.5, 180); put('a10', 'table', 146, 85); put('a10', 'Rustic Chair', 146.5, 84)
put('a10', 'chest-small', 142, 82.5); put('a10', 'Hanging Lantern', 145.5, 82, z=3)
# the drying loft: herbs hung from the rafters in rows, bundles of them, a table to sort them on
for x in (142.5, 144, 145.5):
    A.overlay(a14, x, 79, x + 0.5, 84, 'Foliage (herbs, hung from the rafters)', '#668f27', 0.5, 3)
put('a14', 'Resource Bundle I', 147, 78.5, label='Resource Bundle I (dried herbs)'); put('a14', 'table', 146, 84, label='Table (sorting the herbs)')

# ================================================================= lived in (pass 3)
# the garden: a water butt and a bucket for the beds, a bowl of fresh-picked herbs left on a bench; the lab:
# pots of ingredients by the grinding stones; his quarters: a straw mat, a cup on his table; the junction: a
# traveller's crate and sacks set down by the pavilion
put('high', 'Scrap Vat I', 139, 89, label='Scrap Vat I (a water butt)'); put('high', 'Scrap Bucket', 140, 89.5, label='Scrap Bucket (for watering the beds)')
put('high', 'Wooden Bowl', 142.5, 88, z=0.5, label='Wooden Bowl (fresh-picked herbs)')
put('high', 'Scrap Pot I', 144.5, 83, label='Scrap Pot I (ingredients)'); put('high', 'Scrap Pot II', 145, 83, label='Scrap Pot II (ingredients)')
put('a10', 'Straw Mat', 145, 79.5, 90); put('a10', 'Wooden Cup', 146.5, 85, z=1)
put('walk', 'Scrappy Crate', 122.5, 74, label="Scrappy Crate (a traveller's)"); put('walk', 'Supply Sacks II', 122.5, 75, label="Supply Sacks II (a traveller's)")

# ================================================================= the neighbours' edges (their own blueprints)
R(walk, 110, 77, 112, 83, 'w')                                      # the square's walkway
zone('walk', 'East walkway (square blueprint)', 110, 77, 112, 83, '#2f8f8a')
R(up5, 114, 64, 152, 66, 'r')                                       # the farm's south edge
zone('up5', 'Farm (its blueprint)', 114, 64, 152, 66, '#3f8a4f')
R(walk, 124, 66, 130, 72, 'w')                                      # the farm's stair down to the junction
A.stairs('walk', 'Stairs up to the farm (farm blueprint)', 124, 66, 130, 70, 2, 'N')
A.cheeks(walk, 124, 66, 130, 70, 'N')
R(up5, 143, 66, 149, 74, 'r')                                       # the herb bridge
A.rail(up5, 142.5, 66, 143, 72); A.rail(up5, 149, 66, 149.5, 72)
A.stairs('up5', 'Herb bridge: farm to the alchemist (farm blueprint)', 143, 72, 149, 74, 1, 'S')
A.cheeks(up5, 143, 72, 149, 74, 'S')
R(mid, 114, 96, 146, 98, 'c')                                       # the hunting lodge's north edge
zone('mid', 'Hunting lodge (its blueprint)', 114, 96, 146, 98, '#6d7a45')

# ================================================================= stilts, rim beams and checks
print('stilts:', A.stilts(stl, [('walk', 3), ('mid', 4), ('up5', 5), ('high', 6)]))
own = lambda x, y: (112 <= x < 136 and 71.5 <= y < 96) or math.hypot(x - CX, y - CY) <= 10.5 or (136 <= x < 138 and 81 <= y < 87)
print('rim beam squares:', A.rim_beams(stl, [('walk', 3), ('high', 6)], own))
A.spawn('walk', 125, 83.5, 270)                                 # walk mode starts here: the east junction, facing the stair up to the tower
A.checks()

NOTES = """Laketown: the alchemist, the east junction and the east walkway's end, as a 0.5 m detail blueprint. Pass 3 of 3 (review and finishing touches): done. Drafted by Claude.
This plan's corner is the layout's (110, 64), so it lines up with the Laketown layout and stamps back into the site plan there.

PASSES
1. Design and bones: the walkway's end, the junction and its pavilion, the four stairs off it, the alchemist's round platform with its parapet and landings, the herb garden's beds, the tower with its floors, doors, spiral stair, chimney and roof, the stations; the neighbours' edges, stilts, labels.
2. Details: the alchemist's look (a green glow: potions, the lamps, the chimney's fumes; the copper still), the tower's windows, bands and drying balcony, the rooms, benches, the junction's signpost, pavilion benches, lamps and planter; then a 3D review and a refining round.
3. Review and finishing touches (done): a water butt and a bucket for the herb beds, a bowl of fresh-picked herbs on a bench, pots of ingredients in the lab, a straw mat and a cup in his quarters, a traveller's crate and sacks by the pavilion; the layout redrawn as built; the hand-off for the hunting lodge.

THE EAST WALKWAY AND THE JUNCTION (+3 m): the walkway (6 m of rough wood, a railing just outside each edge, as the square has it) comes in from the square onto the junction, 14 x 18 m of rough wood on a tarred edge with railings round it, open at its four ways: the farm's stair up (north, the farm blueprint's), the alchemist's stair up (east), a strip and a stair up 1 m to the hunting lodge (south), and the walkway (west).
- A timber pavilion in its quiet north-west corner, off every way across it, with two benches under it.
- A signpost in the middle, its four arms pointing to the square, the farm, the alchemist and the hunting lodge.
- Lamps in the railings (the walkways' yellow), a planter with a shrub in the south-east corner.

THE ALCHEMIST'S PLATFORM (+6 m): the layout's round platform, 20 m across, polished granite on a roughly cut stone rim with a low parapet, open where the junction's stair (west, up 3 m between stepped stone flanks) and the herb bridge (north) arrive, a landing at each with stone lamp posts capped in a green glow.
- The herb garden: beds of flower soil in arcs round the south side, a path through them, benches facing them.
- A copper still on the north-east side: a stone hearth, the copper pot on it, its pipe stepping down to a jar.

THE ALCHEMIST'S TOWER: round, 10 m across, three storeys of weathered stone (+6, +10, +14 m) with rough stone bands at the upper floors, set north of the platform's middle so the garden has the south.
- His laboratory (a stone floor): the Alchemy Station, the Laboratory, the Mortar and the Grinding Stones, a worktable in the middle, a chest of reagents, potions glowing green on a ledge by the north-west wall, a lantern; windows south and east.
- His quarters: bed, wardrobe, a fire against the chimney, a table and chair, a chest, a lantern, windows all round.
- The drying loft at the top: herbs hung from the rafters in rows, bundles of them, a table to sort them on; a door out onto the drying balcony, a timber gallery round the south side on brackets with herbs, fresh and dried, hung along it under the roof's brim.
- Up a stone spiral stair on the east side. The front door west, to the junction's stair; a back door north, to the herb bridge from the farm.
- The lab's chimney rises up the south-west side through the roof to a pot, a green glow of fumes at its top.
- A witch's hat of a roof in mossy shingles (Drak Temple Roof Block), its brim flared.
- The Alchemist stands out on the platform by the front door.

HAND-OFF FOR THE HUNTING LODGE (area 12): the junction's strip (x 118..124, y 90..94, +3 m, railings with lamps in them) and its stair up 1 m (y 94..96, stone cheeks) arrive at the lodge's north edge at y 96 (+4 m). Keep 1 m clear in front of the stair's top (y 96..97), and keep the railings' style there.

CONNECTIONS
- West: the east walkway, on from the square's (x 96..112, its blueprint).
- North: the farm's stair down to the junction (x 124..130, y 66..70, the farm blueprint's); the herb bridge from the farm onto the platform's north landing (x 143..149, y 74..76).
- South: the stair up 1 m to the hunting lodge (x 118..124, y 94..96), onto its north edge at y 96 (its blueprint).
- The Mill is at the research hall, by its water wheel (its blueprint's hand-off).

GLOW: the green is Green Luminescent Block (it needs Luminous Growth from caves); the still and the herbs are drawn in blocks, to show where things go.

SIZES: the stations (Alchemy Station, Laboratory, Mortar, Grinding Stones) are the planner's 2 x 2 m placeholders until measured; the furniture is estimates.

STILTS: 1 m posts on the layout's 4 m grid, from the lake bed 4 m down to each deck's underside; tarred rim beams under the edges.
"""
A.save('laketown_alchemist.json', NOTES, 'r-claude-laketown-alchemist-3')
