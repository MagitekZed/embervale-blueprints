"""Laketown: the hunting lodge. 0.5 m detail plan. Pass 3 of 3: review and finishing touches.

The Hunter's lodge at +4 m on conifer timber, between the east junction (north, up its stair) and the fisher's
smokehouse (south, down a stair), the harbour's mouth on its west side. On the west, the lodge hall: log walls
under a steep roof of plant fibre shingles, a great hearth with its stone chimney on the harbour side, the
Hunter's room in a loft at its south end. On the east, the work yard: the tannery shed (open, the Tanning
Station), the weaving house (the Loom, the Spinning Machine, the Hand Spindle), drying racks in the open, and an
archery lane down the east edge with its butts.

Coordinates are the layout's (doc `laketown`): this plan's corner is the layout's (110, 92).
Run: python laketown_lodge.py  ->  writes laketown_lodge.json
"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laketown_common import Area, WOOD, STONE, BED

CON, RS = '#6e5a51', '#7d776a'
BONE, HIDE = '#816a55', '#958580'                                   # antlers, hides
OX, OY = 110, 92
A = Area('Laketown: the hunting lodge (detail)', OX, OY, 42, 32, {
    'c': {'name': 'Conifer Wood Block', 'kind': 'floor', 'color': CON},                 # the lodge's deck
    'g': {'name': 'Polished Granite Block', 'kind': 'floor', 'color': '#626c7a'},       # the alchemist (its)
    'k': {'name': 'Roughly Cut Stone Block', 'kind': 'floor', 'color': '#62605d'},      # its rim
    'C': {'name': 'Conifer Wood Block (logs)', 'kind': 'wall', 'color': CON},           # the hall, the weaving house
    'W': {'name': 'Conifer Wood Block (logs)', 'kind': 'wall', 'color': CON, 'height': 3},
    'K': {'name': 'Rough Stone Block (chimney)', 'kind': 'wall', 'color': RS, 'height': 11},
    'n': {'name': 'Conifer Wood Block (post)', 'kind': 'block', 'color': CON, 'height': 2.5},
    'G': {'name': 'Conifer Wood Block (logs, round the gable window)', 'kind': 'wall', 'color': CON, 'height': 7},
    'U': {'name': 'Refined Wood Block (lamp post)', 'kind': 'block', 'color': WOOD, 'height': 2},
})
P, R, zone, put = A.P, A.R, A.zone, A.put
stl = A.level('stilts', 'Stilts, standing on the lake bed (-4 m)', BED, 12)
lake = A.level('lake', 'Lake (water level, 0 m)', 0, 1)
dock = A.level('dock', 'Boardwalk and fishing pier, their edges (+1 m)', 1, 3)
low = A.level('low', 'Smokehouse, its edge (+2 m)', 2, 4)
walk = A.level('walk', "East junction's strip, its edge (+3 m)", 3, 4)
mid = A.level('mid', 'The hunting lodge (+4 m)', 4, 4)
high = A.level('high', 'Alchemist, its edge (+6 m)', 6, 4)
l8 = A.level('l8', "Lodge hall: the Hunter's loft (+8 m)", 8, 4)
hroof = A.level('hroof', 'Lodge hall: the roof (+8 m)', 8, 7)
troof = A.level('troof', 'Tannery shed: the roof (+6.5 m)', 6.5, 4)
wroof = A.level('wroof', 'Weaving house: the roof (+7 m)', 7, 4)
gab8 = A.level('gab8', 'Lodge hall: the stag antlers on the north gable (+8 m)', 8, 3)
chand = A.level('chand', 'Lodge hall: the antler chandelier (+9 m)', 9, 1)
lamp6 = A.level('lamp6', 'Lamps on the posts (+6 m)', 6, 1)


def block(name, color, h, base=0):
    e = {'name': name, 'kind': 'block', 'color': color, 'height': h}
    if base:
        e['base'] = base
    return P._alloc(e)


def lamp(x, y, g=None):
    """A yellow lamp on a post (the walkways' style): over the deck, or in a railing (g = its level)."""
    if g is None:
        A.overlay(mid, x, y, x + 0.5, y + 0.5, 'Refined Wood Block (lamp post)', WOOD, 2, 0)
    else:
        R(g, x, y, x + 0.5, y + 0.5, 'U')
    R(lamp6, x, y, x + 0.5, y + 0.5, block('Yellow Luminescent Block (lamp)', '#bd9a5f', 0.5))

# ================================================================= the lake
def shoreline(x):
    return 140 + 2 * math.sin(x / 21) + 1.2 * math.sin(x / 8.3 + 1.3)


def ground(x, y):
    s = shoreline(x)
    if y < s:
        return -min(4, max(1, round((s - y) / 1.5)))
    return min(3, 1 + math.floor((y - s) / 3))


P.ground_fn(lambda mx, my: ground(mx + OX, my + OY))
for x, y in P.cells_rect(0, 0, 42, 32):
    if P.ground_at(x, y) < 0:
        lake[y][x] = '~'

# ================================================================= the deck (+4 m)
# The layout's 32 x 20 m of conifer timber on a tarred edge, a wooden railing round it, open where the
# junction's stair arrives (north) and the smokehouse's stair leaves (south)
A.deck(mid, 114, 96, 146, 116, 'c', 't')
A.rail(mid, 114, 95.5, 146, 96, [(118, 124)])                      # north (the junction's stair)
A.rail(mid, 113.5, 95.5, 114, 116.5)                                # west (over the harbour's mouth)
A.rail(mid, 146, 95.5, 146.5, 116.5)                                # east
A.rail(mid, 114, 116, 146, 116.5, [(134, 140)])                    # south (the smokehouse's stair)
zone('mid', 'Hunting lodge (Hunter)', 114, 96, 146, 116, '#6d7a45')

# ================================================================= the lodge hall (west)
# Log walls, 12 x 15 m and 4 m to the eaves, a steep roof of plant fibre shingles (45 degrees, ridge north-
# south); the great hall below, its hearth on the west wall with a stone chimney outside on the harbour side;
# the Hunter's room in a loft over the south end, up a stair through the middle of the hall; a double door north to the
# junction's stair, a door east to the yard
A.walls(mid, 116, 99, 128, 114, 'C', 'c')
A.door('mid', 'Wooden Double Door', 120, 99, 124, 99.5)
A.door('mid', 'Wooden Door', 127.5, 109, 128, 111)
put('mid', 'Stone Fireplace', 116.5, 102, 270, label='Stone Fireplace (the great hearth)')
R(mid, 115, 102.5, 116, 103.5, 'K')
A.stairs('mid', 'Lodge stair', 121, 103, 123, 107, 4, 'S')         # up the middle under the ridge, on whole metres
R(l8, 116.5, 107, 127.5, 113.5, 'r')
A.rail(l8, 116.5, 106.5, 127.5, 107, [(121, 123)])
rh = A.roof(hroof)
rh.gable(116, 99, 128, 114, 'y', 'fiber', pitch=1.0, overhang=0.5)
rh.cut(115, 102.5, 116, 103.5)                                       # (the chimney passes the eave)
rh.caps('lead', min_lower=1)                                        # a dark shingle ridge
rh.paint()
put('mid', 'npc-hunter', 118, 108)
zone('mid', 'Lodge hall', 116.5, 99.5, 127.5, 106.5, '#6d7a45')
zone('l8', "The Hunter's loft", 116.5, 107, 127.5, 113.5, '#9c6b8e')
# a rough stone base course (1 m) round the hall's foot, open at the doors and the chimney
for x, y in P.cells_rect(115.5 - OX, 98.5 - OY, 128.5 - OX, 114.5 - OY):
    mx, my = OX + x / 2, OY + y / 2
    if 116 <= mx < 128 and 99 <= my < 114:
        continue
    if (119 <= mx < 125 and my < 99) or (mx >= 128 and 108 <= my < 111.5) or (mx < 116 and 102.5 <= my < 103.5):   # (doors, their lanterns)
        continue
    mid[y][x] = block('Rough Stone Block (base course)', RS, 1)
# windows: the great hall's west and east sides, the south end below the loft, the loft's high in the south
# gable (in a stretch of wall run up taller: the gable fills down to the wall's own top)
for y0 in (105.5, 109):
    A.win('mid', 'Wooden Window Frame', 116, y0, 116.5, y0 + 1, 1)
for y0 in (101, 106):
    A.win('mid', 'Wooden Window Frame', 127.5, y0, 128, y0 + 1, 1)
for x0 in (118.5, 124.5):
    A.win('mid', 'Wooden Window Frame', x0, 113.5, x0 + 1, 114, 1)
R(mid, 120.5, 113.5, 123.5, 114, 'G')
A.win('mid', 'Wooden Window Frame', 121.5, 113.5, 122.5, 114, 5)
# stag antlers mounted on the north gable over the double door: a skull, the antlers spreading either side
R(gab8, 121.5, 98.5, 122.5, 99, block('Bone Block (the stag\'s skull)', BONE, 1, 1))
for (x, b, h) in ((121, 1.5, 1), (122.5, 1.5, 1), (120.5, 2, 1), (123, 2, 1), (120, 2.5, 0.5), (123.5, 2.5, 0.5)):
    R(gab8, x, 98.5, x + 0.5, 99, block('Bone Block (the stag\'s antlers)', BONE, h, b))
# lanterns at both doors
put('mid', 'Wall Lantern', 119, 98.5, 180, 2.5); put('mid', 'Wall Lantern', 124.5, 98.5, 180, 2.5)
put('mid', 'Wall Lantern', 128, 108, 270, 2.0)
# the great hall: chairs and a rug at the hearth, a long table with benches, an antler chandelier hung high
# under the ridge, bow and spear racks, trophies on the walls, a chest of pelts
put('mid', 'Big Straw Mat', 117.5, 102, label='Big Straw Mat (the hearth rug)')
put('mid', 'Rustic Chair', 118, 100.5, 90); put('mid', 'Rustic Chair', 118, 104.5, 90)
put('mid', 'Wooden Banquet Table', 124, 102.5, 90); put('mid', 'Rustic Bench', 123.5, 103, 90); put('mid', 'Rustic Bench', 125, 103, 90)
put('mid', 'Bow Weapon Rack', 127, 103, 90); put('mid', 'Two-Handed Melee Weapon Rack', 127, 111.5, 90, label='Two-Handed Melee Weapon Rack (spears)')
put('mid', 'chest-large', 116.5, 112, label='Large Chest (pelts)')
for x, y in P.cells_rect(121 - OX, 100 - OY, 123 - OX, 102 - OY):
    mx, my = OX + x / 2, OY + y / 2
    if not (121.5 <= mx < 122.5 and 100.5 <= my < 101.5):
        chand[y][x] = block('Bone Block (the antler chandelier)', BONE, 0.5)
for (x, y) in ((121, 100), (122.5, 100), (121, 101.5), (122.5, 101.5)):
    A.overlay(chand, x, y, x + 0.5, y + 0.5, 'Yellow Luminescent Block (candles)', '#bd9a5f', 0.5, 0.5)
for (x0, y0, x1, y1) in ((116.5, 107.5, 117, 108), (116.5, 111, 117, 111.5), (117, 99.5, 118, 100), (126, 99.5, 127, 100)):
    A.overlay(mid, x0, y0, x1, y1, 'Bone Block (antlers, a trophy)', BONE, 1, 2.5)
put('mid', 'Hanging Lantern', 119, 110.5)
# the Hunter's loft: his bed, a wardrobe and chest under the ridge, a lantern
put('l8', 'bed', 117.5, 109.5, label='Bed (the Hunter)'); put('l8', 'Crude Wooden Closet', 121, 111)
put('l8', 'chest-small', 124, 112); put('l8', 'Hanging Lantern', 122, 109.5, z=2.5)
# firewood stacked by the chimney
A.overlay(mid, 114.5, 99.5, 116, 102, 'Conifer Wood Block (firewood, stacked)', CON, 1.5, 0)

# ================================================================= the work yard (east)
# the tannery shed: open on posts under a fibre-shingle gable, the Tanning Station
for (x, y) in ((130, 98), (137.5, 98), (130, 103.5), (137.5, 103.5)):
    R(mid, x, y, x + 0.5, y + 0.5, 'n')
rt = A.roof(troof)
rt.gable(130, 98, 138, 104, 'x', 'fiber', pitch=1.0, overhang=0.5)
rt.paint()
put('mid', 'tannery', 133, 99.5)
zone('mid', 'Tannery shed', 130, 98, 138, 104, '#9a7d55')
put('mid', 'Scrap Vat I', 131, 99.5, label='Scrap Vat I (a tanning vat)'); put('mid', 'Scrap Vat I', 131, 101, label='Scrap Vat I (a tanning vat)')
for x0 in (130.5, 135):                                             # hides stretched on frames along its south side
    A.overlay(mid, x0, 103, x0 + 2, 103.5, 'Palm Wood Block (a hide, stretched on a frame)', HIDE, 1.5, 0.5)
# the weaving house: log walls (3 m), a door south to the yard; the Loom, the Spinning Machine (it uses up a
# Spinning Wheel to make) and the Hand Spindle
A.walls(mid, 139, 97.5, 146, 104.5, 'W', 'c')
A.door('mid', 'Wooden Door', 141.5, 104, 143.5, 104.5)
rw = A.roof(wroof)
rw.gable(139, 97.5, 146, 104.5, 'x', 'fiber', pitch=1.0, overhang=0.5)
rw.paint()
put('mid', 'loom', 139.5, 98); put('mid', 'spinning-machine', 143.5, 98); put('mid', 'hand-spindle', 139.5, 101.5)
zone('mid', 'Weaving house', 139.5, 98, 145.5, 104, '#9a7d55')
for x0 in (139.5, 144):
    A.win('mid', 'Wooden Window Frame', x0, 104, x0 + 1, 104.5, 1)
A.win('mid', 'Wooden Window Frame', 145.5, 100.5, 146, 101.5, 1)
put('mid', 'Supply Sacks I', 143.5, 101.5, label='Supply Sacks I (raw wool)'); put('mid', 'Resource Bundle II', 144.5, 101.5, label='Resource Bundle II (cloth)')
put('mid', 'Hanging Lantern', 142.5, 101, z=2.5)
# drying racks in the open yard
for (x, y) in ((130.5, 106), (133.5, 106), (130.5, 110), (133.5, 110)):
    put('mid', 'drying-rack', x, y)
zone('mid', 'Drying racks', 130.5, 106, 135.5, 112, '#9a7d55')
# the archery lane down the east edge: straw butts at its north end, the shooting line 8 m south
for x in (140.5, 142.5, 144.5):
    A.overlay(mid, x, 106, x + 1, 107, 'Straw Roof Block (a target butt)', '#a7753d', 1.5, 0)
zone('mid', 'Archery lane', 140, 106, 146, 115.5, '#6d7a45')
put('mid', 'Bow Weapon Rack', 140.5, 114.5, label='Bow Weapon Rack (at the shooting line)')
lamp(129, 105); lamp(138.5, 105.5); lamp(117.5, 95.5, mid); lamp(124, 95.5, mid); lamp(133.5, 116, mid); lamp(140, 116, mid)

# ================================================================= lived in (pass 3)
# the Hunter's two hounds (their beds and a bowl) by the hearth; a jug, a cup and a bowl of stew on the long
# table; a mat and a nightstand in the loft; thread in the weaving house, tannin in the tannery; a sack of
# arrows at the shooting line; a bench by the hall's east door looking over the yard; a chopping block by the
# woodpile
put('mid', 'Dog Pillow', 119.5, 102, label='Dog Pillow (a hound)'); put('mid', 'Dog Pillow', 119.5, 103, label='Dog Pillow (a hound)')
put('mid', 'Dog Bowl', 120, 104.5)
put('mid', 'Crude Wooden Jug', 124, 103, z=1); put('mid', 'Wooden Cup', 124.5, 104, z=1)
put('mid', 'Wooden Bowl', 124, 105, z=1, label='Wooden Bowl (venison stew)')
put('l8', 'Straw Mat', 119.5, 110); put('l8', 'Crude Wooden Nightstand', 117.5, 108.5)
put('mid', 'Scrap Bucket', 142, 98.5, label='Scrap Bucket (thread)'); put('mid', 'Scrap Bucket', 132.5, 102, label='Scrap Bucket (tannin)')
put('mid', 'Supply Sacks I', 143, 114.5, label='Supply Sacks I (arrows)')
put('mid', 'Rustic Bench', 128.5, 105.5, 270, label='Rustic Bench (over the yard)')
A.overlay(mid, 114.5, 102.5, 115, 103, 'Conifer Wood Block (chopping block)', CON, 0.5, 0)

# ---- down 2 m to the smokehouse (its blueprint), between stone cheeks
R(low, 134, 116, 140, 120, 't')
A.stairs('low', 'Stairs down to the smokehouse', 134, 116, 140, 120, 2, 'N')
A.cheeks(low, 134, 116, 140, 120, 'N')

# ================================================================= the neighbours' edges (their own blueprints)
R(walk, 118, 92, 124, 96, 'w')                                      # the junction's strip and its stair up here
A.rail(walk, 117.5, 92, 118, 94); A.rail(walk, 124, 92, 124.5, 94)
A.stairs('walk', 'Stairs up to the hunting lodge (alchemist blueprint)', 118, 94, 124, 96, 1, 'S')
A.cheeks(walk, 118, 94, 124, 96, 'S')
zone('walk', 'East junction (alchemist blueprint)', 118, 92, 124, 96, '#2f8f8a')
for x, y in P.cells_rect(136 - OX, 92 - OY, 156 - OX, 94 - OY):     # the alchemist's platform, its south edge
    mx, my = OX + x / 2 + 0.25, OY + y / 2 + 0.25
    d = math.hypot(mx - 146, my - 84)
    if d <= 10:
        high[y][x] = 'k' if d > 9.5 else 'g'
zone('high', 'Alchemist (its blueprint)', 138, 92, 154, 94, '#56806c')
R(low, 128, 120, 150, 124, 't')                                     # the smokehouse's north edge
zone('low', 'Smokehouse (its blueprint)', 128, 120, 150, 124, '#3f7f9e')
R(dock, 110, 122, 126, 124, 't')                                    # the boardwalk (the main dock's)
zone('dock', 'Boardwalk (main dock blueprint)', 110, 122, 126, 124, '#2f8f8a')
R(dock, 150, 112, 152, 124, 't')                                    # the fishing pier (the smokehouse's)
zone('dock', 'Fishing pier (smokehouse blueprint)', 150, 112, 152, 124, '#2f7fb3')

# ================================================================= stilts, rim beams and checks
print('stilts:', A.stilts(stl, [('dock', 1), ('low', 2), ('walk', 3), ('mid', 4), ('high', 6)]))
own = lambda x, y: 113.5 <= x < 146.5 and 95.5 <= y < 116.5
print('rim beam squares:', A.rim_beams(stl, [('mid', 4)], own))
A.spawn('mid', 126, 97, 0)                                 # walk mode starts here: the north edge, looking between the hall and the work yard
A.checks()

NOTES = """Laketown: the hunting lodge, as a 0.5 m detail blueprint. Pass 3 of 3 (review and finishing touches): done. Drafted by Claude.
This plan's corner is the layout's (110, 92), so it lines up with the Laketown layout and stamps back into the site plan there.

PASSES
1. Design and bones: the deck and its railing, the lodge hall (hearth, chimney, loft, stair, doors, roof), the work yard (the tannery shed, the weaving house, the drying racks, the archery lane), the stations, the stair down to the smokehouse; the neighbours' edges, stilts, labels.
2. Details: contrast and a hunting lodge's character (a stone base course, a dark ridge, stag antlers on the gable, an antler chandelier, trophies), windows, the rooms, the tannery's vats and hides, the weaving house's wool and cloth, the lane's bow rack, lamps; then a 3D review and a refining round.
3. Review and finishing touches (done): the Hunter's hounds by the hearth, supper on the long table, a mat and a nightstand in the loft, thread, tannin and arrows at their work, a bench over the yard, a chopping block; the layout redrawn as built; the hand-off for the smokehouse.

THE IDEA: the Hunter's lodge at +4 m on conifer timber, between the east junction (north, up its stair) and the fisher's smokehouse (south, down a stair), the harbour's mouth to its west: the lodge hall on the west, the work yard on the east.

THE DECK (+4 m): the layout's 32 x 20 m of conifer timber on a tarred edge, a wooden railing round it, open where the junction's stair arrives (x 118..124) and the smokehouse's stair leaves (x 134..140), lamps in the railing either side of both.

THE LODGE HALL (west): log walls (conifer) on a rough stone base course, 12 x 15 m and 4 m to the eaves, under a steep roof of plant fibre shingles (45 degrees, ridge north-south) with a dark shingle ridge.
- On the north gable over the double door, a stag's skull and antlers; lanterns either side of the door. A door east to the yard with a lantern.
- The great hall: the hearth on the west wall (its stone chimney outside on the harbour side, firewood stacked by it) with a rug and two chairs; a long table with benches; an antler chandelier with candles hung high under the ridge; a bow rack, a spear rack, trophies on the walls, a chest of pelts; windows west and east; the Hunter.
- The Hunter's room in a loft over the south end (+8 m), up a stair through the middle of the hall under the ridge: his bed, a wardrobe, a chest, a lantern, a window high in the south gable.

THE WORK YARD (east):
- The tannery shed: open on posts under a fibre-shingle gable, the Tanning Station, two tanning vats, hides stretched on frames along its south side.
- The weaving house: log walls (3 m), a door south to the yard, windows; the Loom, the Spinning Machine and the Hand Spindle, raw wool and cloth, a lantern. (The Spinning Machine uses up a Spinning Wheel to make, so a late-game lodge has the machine.)
- Drying racks (four) in the open yard.
- The archery lane down the east edge: three straw butts at its north end, a bow rack at the shooting line 8 m south.
- Lamps between the hall and the yard and by the weaving house.

HAND-OFF FOR THE SMOKEHOUSE (area 13): the lodge's stair comes down 2 m (x 134..140, y 116..120, stone cheeks, lamps either side at its top) onto the smokehouse's deck (+2 m) at y 120. Keep 1 m clear at its foot (y 120..121).

CONNECTIONS
- North: the junction's strip and its stair up 1 m (x 118..124, y 94..96, the alchemist blueprint's), onto the lodge's north edge; 1 m clear in front of it.
- South: the stair down 2 m to the smokehouse (x 134..140, y 116..120, stone cheeks), onto its deck (+2 m) at y 120 (its blueprint keeps 1 m clear at the foot).
- West: the harbour's mouth, open water between the main dock's mole and the lodge (the main dock blueprint's hand-off).

SIZES: the stations (Tanning Station, Drying Rack, Loom, Spinning Machine, Hand Spindle) are the planner's 2 x 2 m placeholders until measured; the furniture is estimates. The antlers, the chandelier and the hides are drawn in blocks, to show where things go.

STILTS: 1 m posts on the layout's 4 m grid, from the lake bed 4 m down to each deck's underside; tarred rim beams under the edges.
"""
A.save('laketown_lodge.json', NOTES, 'r-claude-laketown-lodge-3')
