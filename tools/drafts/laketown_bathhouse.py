"""Laketown: the bathhouse and the arena. 0.5 m detail plan. Pass 3 of 3: review and finishing touches (done).

South-west of the square, between the west walkway, the carpentry and the causeway.
- The bathhouse (+2 m), the Barber's (Elio Ricci): down a short stair from the west walkway's branch. A
  stone bath hall on the ground floor with a sunken plunge pool and a row of bathtubs, one of each of 1.0's
  four kinds, lockers and a steam stove; upstairs the Barber's salon and his rooms, and an open loggia on the
  south side looking over the arena (barbers ran the bathhouses). A cupola on the roof lets the steam out.
- The arena: a round stone amphitheatre 26 m across. A sand floor 14 m across at +2 m, walled; round it at
  +4 m a promenade behind a parapet, three tiers of seats rising outward, and an outer wall. Three ways in:
  from the carpentry's stair (west, with the landing it needs), from the causeway (east), and the fighters'
  way from the bathhouse's south door, up a short stair, across the stands and down onto the sand.

Coordinates are the layout's (doc `laketown`): this plan's corner is the layout's (40, 76).
Run: python laketown_bathhouse.py  ->  writes laketown_bathhouse.json
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math
from laketown_common import Area, WOOD, STONE

RS, RCS, LIME, BT = '#7d776a', '#62605d', '#a79a88', '#947f75'
A = Area('Laketown: bathhouse and arena (detail)', 40, 76, 44, 52, {
    'h': {'name': 'Brick-Timbered Block', 'kind': 'floor', 'color': BT},               # the bathhouse deck
    'k': {'name': 'Roughly Cut Stone Block', 'kind': 'floor', 'color': RCS},           # the arena's promenade
    's': {'name': 'Sand', 'kind': 'floor', 'color': '#f3dfc9'},                       # the arena floor
    'L': {'name': 'Limestone Road Block', 'kind': 'floor', 'color': '#a38b79'},        # the square (its blueprint)
    'c': {'name': 'Field Stones', 'kind': 'floor', 'color': '#8a8170'},
    'S': {'name': 'Limestone Block', 'kind': 'wall', 'color': LIME},                   # the bathhouse, ground floor
    'B': {'name': 'Brick-Timbered Block (upper floor)', 'kind': 'wall', 'color': BT},
    'C': {'name': 'Limestone Block (loggia column)', 'kind': 'wall', 'color': LIME},
    'q': {'name': 'Limestone Block (loggia parapet)', 'kind': 'block', 'color': LIME, 'height': 1},
    'O': {'name': 'Rough Stone Block (arena wall)', 'kind': 'wall', 'color': RS, 'height': 3},
    'W': {'name': 'Roughly Cut Stone Block (podium wall)', 'kind': 'wall', 'color': RCS, 'height': 2},
    'p': {'name': 'Fancy Stone Block (parapet)', 'kind': 'block', 'color': STONE, 'height': 1},
    'a': {'name': 'Roughly Cut Stone Block (seats, tier 1)', 'kind': 'block', 'color': RCS, 'height': 0.5},
    'b': {'name': 'Roughly Cut Stone Block (seats, tier 2)', 'kind': 'block', 'color': RCS, 'height': 1},
    'e': {'name': 'Roughly Cut Stone Block (seats, tier 3)', 'kind': 'block', 'color': RCS, 'height': 1.5},
    'x': {'name': 'Refined Wood Block (window box)', 'kind': 'block', 'color': WOOD, 'height': 0.5, 'base': 0.5},
    'F': {'name': 'Foliage (potted shrub)', 'kind': 'block', 'color': '#668f27', 'height': 1},
    'Y': {'name': 'Red Carpet Block', 'kind': 'floor', 'color': '#9e3742'},           # the champion's box
    'Z': {'name': 'Roughly Cut Stone Block (box base)', 'kind': 'block', 'color': RCS, 'height': 1},
    'V': {'name': 'Limestone Block (canopy post)', 'kind': 'wall', 'color': LIME, 'height': 2.5},
    'N': {'name': 'Refined Wood Block (banner pole)', 'kind': 'block', 'color': WOOD, 'height': 3},
    'G': {'name': 'Red Carpet Block (banner)', 'kind': 'block', 'color': '#9e3742', 'height': 1.5, 'base': 1},
    'l': {'name': 'Yellow Luminescent Block (lamp)', 'kind': 'block', 'color': '#bd9a5f', 'height': 0.5},
})
P, R, zone, put = A.P, A.R, A.zone, A.put
stl = A.level('stilts', 'Stilts, standing on the lake bed (-4 m)', -4, 12)
lake = A.level('lake', 'Lake (water level, 0 m)', 0, 1)
pool = A.level('pool', 'The plunge pool (+1.5 m)', 1.5, 1)
low = A.level('low', 'Bathhouse deck, arena floor (+2 m)', 2, 4)
walk = A.level('walk', 'West walkway, causeway (+3 m)', 3, 4)
mid = A.level('mid', 'Arena stands; the square (+4 m)', 4, 4)
box = A.level('box', "Arena: the champion's box (+5.5 m)", 5.5, 3)
hood55 = A.level('hood55', 'Bathhouse: the door hood (+5.5 m)', 5.5, 2)
up6 = A.level('up6', "Bathhouse upper floor: the Barber's (+6 m)", 6, 3.5)
banner = A.level('banner', 'Arena: banners on the wall (+7 m)', 7, 4)
canopy = A.level('canopy', "Arena: the box's canopy (+8 m)", 8, 2)
work = A.level('work', 'Arena: the training dummies, their heads (+2 m)', 2, 3)
roof95 = A.level('roof95', 'Bathhouse roof (+9.5 m)', 9.5, 5)

# ================================================================= the lake (bed 4 m down)
P.ground_rect(0, 0, 44, 52, -4)
R(lake, 40, 76, 84, 128, '~')

# ================================================================= the bathhouse (+2 m)
# The layout's deck, 16 x 12 m of brick-timbered on a tarred edge, down a stair from the walkway's branch.
A.deck(low, 46, 86, 62, 98, 'h', 't')
A.stairs('low', 'Stairs down to the bathhouse', 54, 86, 58, 88, 1, 'N')
A.cheeks(low, 54, 86, 58, 88, 'N')
A.rail(low, 46, 86, 54, 86.5); A.rail(low, 58, 86, 62, 86.5)
A.rail(low, 46, 86.5, 46.5, 97.5); A.rail(low, 61.5, 86.5, 62, 97.5)
A.rail(low, 46, 97.5, 57, 98); A.rail(low, 61, 97.5, 62, 98)
zone('low', 'Barber and bathhouse (Elio Ricci)', 46, 86, 62, 98, '#3f7f9e')
# the house: limestone below (the wet rooms), brick-timbered above, 14.5 x 8 m; the door from the walkway's
# stair on the north, a door south to the arena (its stair inside on whole metres, so it stays clean in the
# 1 m site plan)
A.walls(low, 47, 89, 61.5, 97, 'S', 'P')
A.door('low', 'Wooden Double Door', 54, 89, 58, 89.5)
A.door('low', 'Wooden Door', 57.5, 96.5, 59.5, 97)
# the bath hall: the sunken plunge pool (water 0.5 m below the floor), the four bathtubs of 1.0 (two along
# the west wall, two along the south), lockers either side of the door, benches, a steam stove under a
# chimney in the north-west corner, the stair up along the east wall
R(low, 50.5, 91.5, 56, 94.5, ' ')
R(pool, 50.5, 91.5, 56, 94.5, '~')
put('low', 'bathtub', 47.5, 91, 270, label='Bronze Bathtub'); put('low', 'bathtub', 47.5, 93.5, 270, label='Granite Stone Bathtub')
put('low', 'bathtub', 51, 94.5, 90, label='Wooden Bathtub'); put('low', 'bathtub', 54.5, 94.5, 90, label='Maritime Bathtub')
for x in (51, 52, 58, 59):
    put('low', 'chest-small', x, 89.5, 0, label='Small Chest (locker)')
put('low', 'Bench', 51, 90.5); put('low', 'Bench', 58.5, 92, 90)
R(low, 47.5, 88.5, 48.5, 89.5, P._alloc({'name': 'Rough Stone Block (chimney)', 'kind': 'wall', 'color': RS, 'height': 12.5}))
put('low', 'Stone Fireplace', 47.5, 89.5, 0, label='Stone Fireplace (the steam stove)')
A.stairs('low', 'Bathhouse stair up', 60, 91, 61, 95, 4, 'N')
zone('low', 'Bath hall and plunge pool', 47, 89, 61.5, 97, '#3f7f9e')
# a fancy stone border round the pool; high windows in the stone walls (2 m up, for privacy)
for (x0, y0, x1, y1) in ((50, 91, 56.5, 91.5), (56, 91.5, 56.5, 94.5)):
    R(low, x0, y0, x1, y1, 'f')
for x in (49.5, 60):
    A.win('low', 'Wooden Window Frame', x, 89, x + 1, 89.5, 2)
for y in (92, 94.5):
    A.win('low', 'Wooden Window Frame', 47, y, 47.5, y + 1, 2)
A.win('low', 'Wooden Window Frame', 61, 92, 61.5, 93, 2)
for x in (48.5, 52.5, 60):
    A.win('low', 'Wooden Window Frame', x, 96.5, x + 1, 97, 2)
# the warmth and the wet: a kettle of hot water on the stove, buckets by the tubs, towels by the lockers, a
# brazier by the pool, lanterns
put('low', 'Kettle', 48.5, 89.5, z=1.5, label='Kettle (hot water)')
put('low', 'Scrap Bucket', 56.5, 91.5); put('low', 'Scrap Bucket', 57.5, 94)
put('low', 'Supply Sacks I', 53, 90.5, label='Supply Sacks I (towels)')
put('low', 'Brazier', 57, 91.5)
put('low', 'Hanging Lantern', 57.5, 93); put('low', 'Hanging Lantern', 58, 95)
# outside: a tiled hood over the double door on brackets, lanterns, potted shrubs either side of the way in
hb = A.roof(hood55)
hb.shed(53.5, 88, 58.5, 89, 's', 'tiles', pitch=1.0, overhang=0)
hb.paint()
for x in (53.5, 58):
    A.overlay(low, x, 88.5, x + 0.5, 89, 'Refined Wood Block (bracket)', WOOD, 0.5, 3)
put('low', 'Wall Lantern', 53, 88.5, 0, 2.0); put('low', 'Wall Lantern', 58.5, 88.5, 0, 2.0)
for x in (52, 59.5):
    A.overlay(low, x, 87, x + 1, 88, 'Foliage (potted shrub)', '#668f27', 1, 0)
put('low', 'Bench', 47.5, 87, 0)
put('low', 'Wall Lantern', 58.5, 97, 0, 3.0)
# the bathhouse's sign, on a bracket from the wall beside the door, over the potted shrub
A.overlay(low, 52.5, 88.5, 53, 89, 'Refined Wood Block (sign bracket)', WOOD, 0.5, 3)
A.overlay(low, 51.5, 88.5, 52.5, 89, "Tarred Wood Block (the bathhouse's sign)", '#5d5652', 1, 2)
# lived in: the bathhouse cat's bed and bowl by the warm stove
put('low', 'Cat Pillow', 49.5, 89.5, label="Cat Pillow (the bathhouse cat's, by the stove)"); put('low', 'Cat Bowl', 50, 90.5)
# upstairs (+6 m): the Barber's salon and his room behind a partition, the loggia over the arena: the upper
# walls stand back to y 95, the loggia in front under the roof on limestone columns with a parapet
A.walls(up6, 47, 89, 61.5, 95, 'B', 'h')
R(up6, 47.5, 89, 48.5, 89.5, ' ')                       # the chimney passes up through the wall
R(up6, 60, 91, 61, 94.5, ' ')                           # the stairwell, railed
R(up6, 59.5, 91, 60, 94.5, 'i')
R(up6, 53, 89.5, 53.5, 94.5, 'B')                       # the partition
A.door('up6', 'Wooden Door', 53, 90, 53.5, 92)
R(up6, 47, 95, 61.5, 97, 'h')                           # the loggia
for x in (47, 50.5, 54, 57.5, 61):
    R(up6, x, 96.5, x + 0.5, 97, 'C')
for x0, x1 in ((47.5, 50.5), (51, 54), (54.5, 57.5), (58, 61)):
    R(up6, x0, 96.5, x1, 97, 'q')
R(up6, 47, 95, 47.5, 96.5, 'C'); R(up6, 61, 95, 61.5, 96.5, 'C')
A.door('up6', 'Wooden Door', 50, 94.5, 52, 95); A.door('up6', 'Wooden Door', 56, 94.5, 58, 95)
put('up6', 'npc-barber', 55, 90, label='Barber (Elio Ricci)')
put('up6', 'Rustic Chair', 58.5, 92, label="Rustic Chair (the barber's chair)")
put('up6', 'Wooden Sink', 54, 93.5)
put('up6', 'bed', 48, 89.5, label='Bed (Elio Ricci)')
put('up6', 'Crude Wooden Closet', 48, 93.5)
# the salon: a waiting bench, a side table with the shaving bowl, shelves; his room: a nightstand, a chest,
# a mat; windows (window boxes on the north), lanterns
put('up6', 'Rustic Bench', 54, 89.5)
put('up6', 'Wooden Side Table', 59, 90); put('up6', 'Wooden Bowl', 59, 90, z=1, label='Wooden Bowl (shaving)')
put('up6', 'Carved Wooden Shelf', 53.5, 92.5, 270)
put('up6', 'Carved Wooden Nightstand', 50, 89.5); put('up6', 'chest-small', 51.5, 92.5)
put('up6', 'Straw Mat', 50.5, 91)
put('up6', 'Hanging Lantern', 56.5, 93.5, z=3); put('up6', 'Hanging Lantern', 50.5, 92.5, z=3)
for x in (50, 57.5):
    A.win('up6', 'Wooden Window Frame', x, 89, x + 1, 89.5, 1)
    R(up6, x, 88.5, x + 1, 89, 'x')
A.win('up6', 'Wooden Window Frame', 47, 91, 47.5, 92, 1)
A.win('up6', 'Wooden Window Frame', 61, 92, 61.5, 93, 1)
A.win('up6', 'Wooden Window Frame', 54, 94.5, 55, 95, 2)
# the loggia: chairs and a little table at the parapet, cups on it (a good seat for a bout)
put('up6', 'Rustic Chair', 52.5, 95.5, 0); put('up6', 'Rustic Chair', 54.5, 95.5, 0)
put('up6', 'Wooden Side Table', 53.5, 95.5); put('up6', 'Wooden Cup', 53.5, 95.5, z=1); put('up6', 'Crude Wooden Jug', 54, 96, z=1)
put('up6', 'Rustic Chair', 59, 95.5, 0)
zone('up6', "Barber's salon", 53.5, 89.5, 61, 94.5, '#9c6b8e')
zone('up6', "Barber's room", 47.5, 89.5, 53, 94.5, '#9c6b8e')
zone('up6', 'Loggia (over the arena)', 47, 95, 61.5, 97, '#3f7f9e')

# ================================================================= the arena
# The layout's ring: stands at +4 m, 26 m across, round a sand floor at +2 m, 14 m across.
AX, AY = 59, 113
A.circle(low, AX, AY, 15, 'W')                          # the podium wall round the floor (+2 to +4 m)
A.circle(low, AX, AY, 14, 's')                          # the sand floor
A.circle(mid, AX, AY, 26, 'O')                          # the outer wall (+4 to +7 m)
A.circle(mid, AX, AY, 24, 'e')                          # three tiers of seats rising outward
A.circle(mid, AX, AY, 22, 'b')
A.circle(mid, AX, AY, 20, 'a')
A.circle(mid, AX, AY, 18, 'k')                          # the promenade
A.circle(mid, AX, AY, 15, 'p')                          # the parapet over the floor
A.circle(mid, AX, AY, 14, ' ')
zone('mid', 'Arena stands (three tiers)', 46, 100, 72, 126, '#c2416e')
zone('low', 'Arena floor (sand)', 52, 106, 66, 120, '#c2416e')
# the ways in: landings and aisles through the wall and the tiers, down to the promenade
R(mid, 46, 110, 48.5, 116, 'k'); R(mid, 48, 111, 50.5, 115, 'k')          # west, from the carpentry's stair
R(mid, 69.5, 110, 72, 116, 'k'); R(mid, 67.5, 111, 70, 115, 'k')          # east, from the causeway's stair
R(mid, 57, 100, 61, 104.5, 'k')                         # north, the fighters' way from the bathhouse,
R(mid, 57, 104.5, 61, 106, 'k')                         # across the promenade to the stair down to the sand
zone('mid', 'West entrance (from the carpentry)', 46, 110, 50, 116, '#8a8f96')
zone('mid', 'East entrance (from the causeway)', 68, 110, 72, 116, '#8a8f96')
zone('mid', "The fighters' way", 57, 100, 61, 106, '#8a8f96')
R(low, 57, 106, 61, 108, 's')
A.stairs('low', 'Stairs down to the arena floor', 57, 106, 61, 108, 2, 'N')
# a fighting ring marked in the sand in field stones; weapon racks round the edge, facing the middle
A.circle(low, AX, AY, 6.5, 'c'); A.circle(low, AX, AY, 5.5, 's')
put('low', 'Sword and Shield Rack', 52.5, 112, 270); put('low', 'Two-Handed Melee Weapon Rack', 65, 112, 90)
put('low', 'Bow Weapon Rack', 56, 119, 180); put('low', 'Staff Weapon Rack', 60, 119, 180)
put('low', 'Shield Rack', 53.5, 116.5, 270, label='Shield Rack (practice shields)')
# two training dummies on the sand (1.0 has none to place, so they're built): a post, arms across it, a
# straw head on top
for dy in (110, 115.5):
    R(low, 54, dy, 54.5, dy + 0.5, P._alloc({'name': 'Refined Wood Block (dummy post)', 'kind': 'block', 'color': WOOD, 'height': 1.5}))
    for ax in (53.5, 54.5):
        A.overlay(low, ax, dy, ax + 0.5, dy + 0.5, 'Refined Wood Block (dummy arms)', WOOD, 0.5, 1)
    R(work, 54, dy, 54.5, dy + 0.5, P._alloc({'name': 'Plaited Block (dummy head)', 'kind': 'block', 'color': '#867561', 'height': 0.5, 'base': 1.5}))
zone('low', 'Training dummies', 53.5, 110, 55, 116, '#c2416e')
# the fighters' bench and a water barrel at the foot of their stair
put('low', 'Rustic Bench', 55, 108, label="Rustic Bench (the fighters')")
put('low', 'Scrap Vat I', 61.5, 108, label='Scrap Vat I (water for the fighters)')
# braziers on the promenade, lanterns at the ways in
for ang in (45, 135, 225, 315):
    bx = round((AX + 8.25 * math.cos(math.radians(ang)) - 0.5) * 2) / 2
    by = round((AY + 8.25 * math.sin(math.radians(ang)) - 0.5) * 2) / 2
    put('mid', 'Brazier', bx, by)
put('mid', 'Ground Lantern II', 48, 110); put('mid', 'Ground Lantern II', 69.5, 110)
put('mid', 'Ground Lantern II', 57, 101)
# lintels over the ways in through the outer wall, so they read as gateways
for (x0, y0, x1, y1) in ((46, 110, 47.5, 116), (70.5, 110, 72, 116), (57, 100, 61, 101)):
    A.overlay(mid, x0, y0, x1, y1, 'Rough Stone Block (lintel)', RS, 0.5, 2.5)
# the champion's box on the south stands: a red carpet floor at the top tier's height (the tiers are its
# steps), a red canopy on four limestone posts, chairs facing the floor
R(mid, 56, 121.5, 62, 124.5, 'Z')
R(box, 56, 121.5, 62, 124.5, 'Y')
for (x, y) in ((56, 121.5), (61.5, 121.5), (56, 124), (61.5, 124)):
    R(box, x, y, x + 0.5, y + 0.5, 'V')
for x in (57.5, 58.5, 59.5):
    put('box', 'Rustic Chair', x, 122, 180)
zone('box', "The champion's box", 56, 121.5, 62, 124.5, '#9e3742')

# the fighters' way up from the bathhouse's south door onto the stands
R(low, 57, 98, 61, 100, 'h')
A.stairs('low', 'Stairs: bathhouse to the arena', 57, 98, 61, 100, 2, 'S')
A.cheeks(low, 57, 98, 61, 100, 'S')

# ================================================================= the neighbours' edges (their own blueprints)
# the west walkway (+3 m) and its bathhouse branch (the carpentry blueprint; the square's at x 56 on)
R(walk, 40, 77, 64, 83, 'w'); R(walk, 54, 83, 58, 86, 'w')
A.rail(walk, 40, 76.5, 62, 77); A.rail(walk, 40, 83, 54, 83.5); A.rail(walk, 58, 83, 62, 83.5)
A.rail(walk, 53.5, 83.5, 54, 86); A.rail(walk, 58, 83.5, 58.5, 86)
zone('walk', 'West walkway (carpentry and square blueprints)', 40, 77, 64, 83, '#2f8f8a')
# the carpentry (+2 m): its east edge and its stair up to the arena
R(low, 40, 92, 44, 126, 'r'); R(low, 43, 92, 44, 126, 't')
R(low, 42, 110, 46, 116, 'r')
A.stairs('low', 'Stairs: carpentry to the arena (carpentry blueprint)', 42, 110, 46, 116, 2, 'E')
A.cheeks(low, 42, 110, 46, 116, 'E')
zone('low', 'Carpentry (carpentry blueprint)', 40, 92, 44, 126, '#9a7344')
# the causeway (+3 m) and its stair up to the arena (the causeway blueprint)
R(walk, 77, 96, 83, 128, 'w'); R(walk, 72, 110, 77, 116, 'w')
A.stairs('walk', 'Stairs up to the arena (causeway blueprint)', 72, 110, 74, 116, 1, 'W')
zone('walk', 'Causeway (causeway blueprint)', 77, 96, 83, 128, '#2f8f8a')
# the square (+4 m): its south-west corner
R(mid, 64, 86, 84, 96, 'L'); R(mid, 64, 86, 65, 96, 'f'); R(mid, 64, 95, 84, 96, 'f')
zone('mid', 'Main square (square blueprint)', 64, 86, 84, 96, '#b8862b')

# ================================================================= roofs, at 45 degrees in even steps
# the bathhouse: a tiled hip over house and loggia, cut flat for a cupola that lets the steam out: a drum of
# limestone with openings, a little castle slate dome
rb = A.roof(roof95)
rb.hip(47, 89, 61.5, 97, 'tiles', pitch=1.0, overhang=0.5, ridge_h=3.5)
rb.cut(47.5, 88.5, 48.5, 89.5)
rb.paint()
cup_el = 9.5 + 3.5
drum = A.level('drum', 'Bathhouse: the cupola drum (+%g m)' % cup_el, cup_el, 1.5)
cupdome = A.level('cupdome', 'Bathhouse: the cupola dome (+%g m)' % (cup_el + 1.5), cup_el + 1.5, 2)
A.circle(drum, 54, 93, 4, P._alloc({'name': 'Limestone Block (cupola drum)', 'kind': 'wall', 'color': LIME, 'height': 1.5}))
A.circle(drum, 54, 93, 3, ' ')
R(drum, 53.5, 91, 54.5, 95, ' '); R(drum, 52, 92.5, 56, 93.5, ' ')     # its openings, the steam's way out
rd = A.roof(cupdome)
rd.dome(54, 93, 2, 1.5, 'castle')
rd.paint()
fin_el = cup_el + 1.5 + round(rd.top(53.5, 92.5) * 2) / 2
fin = A.level('finial', 'Bathhouse: the cupola finial (+%g m)' % fin_el, fin_el, 1)
R(fin, 53.5, 92.5, 54, 93, P._alloc({'name': 'Fancy Stone Block (finial)', 'kind': 'block', 'color': STONE, 'height': 1}))
caps = A.level('caps', 'Bathhouse: the chimney cap (+14 m)', 14, 1)
A.ring(caps, 47.5, 88.5, 48.5, 89.5, P._alloc({'name': 'Rough Stone Block (chimney cap)', 'kind': 'block', 'color': RS, 'height': 0.5}))
R(caps, 47.5, 88.5, 48, 89, P._alloc({'name': 'Fired Bricks Block (chimney pot)', 'kind': 'block', 'color': '#aa7657', 'height': 0.5, 'base': 0.5}))
# the box's canopy: a flat red cloth on the posts, matching the banners, its front edge scalloped
R(canopy, 55.5, 121, 62.5, 125, P._alloc({'name': 'Red Carpet Block (canopy)', 'kind': 'block', 'color': '#9e3742', 'height': 0.5}))
scallop = P._alloc({'name': 'Red Carpet Block (canopy valance)', 'kind': 'block', 'color': '#9e3742', 'height': 0.5, 'base': 2})
for i in range(7):
    R(box, 55.5 + i, 121, 56 + i, 121.5, scallop)
# red banners on poles round the arena's outer wall, between the ways in
mg = P.grids['mid']
for ang in (30, 60, 120, 150, 210, 240, 300, 330):
    c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    px, py = math.floor((AX + 12.5 * c) * 2) / 2, math.floor((AY + 12.5 * sn) * 2) / 2
    fx, fy = math.floor((AX + 13.25 * c) * 2) / 2, math.floor((AY + 13.25 * sn) * 2) / 2
    sx, sy = A.sq(px, py)
    assert mg[sy][sx] == 'O', (ang, px, py, mg[sy][sx])
    R(banner, px, py, px + 0.5, py + 0.5, 'N')
    R(banner, fx, fy, fx + 0.5, fy + 0.5, 'G')

# ================================================================= stilts, rim beams and checks
print('stilts:', A.stilts(stl, [('low', 2), ('walk', 3), ('mid', 4)]))
own = lambda x, y: ((46 <= x < 62 and 86 <= y < 98) or (57 <= x < 61 and 98 <= y < 100) or (46 <= x < 72 and 100 <= y < 126))
print('rim beam squares:', A.rim_beams(stl, [('low', 2), ('mid', 4)], own))
A.spawn('mid', 59, 101, 0)                                      # walk mode starts here: the fighters' way from the bathhouse, looking down into the arena
A.checks()

NOTES = """Laketown: the bathhouse and the arena, as a 0.5 m detail blueprint (all three passes done). Drafted by Claude.
This plan's corner is the layout's (40, 76), so it lines up with the Laketown layout and stamps back into the site plan there.

PASSES
1. Design and bones: the decks, the buildings' shells with walls, doors, stairs and roof shapes, the pool and bathtubs, the Barber, the arena's floor, stands and ways in, the connections, stilts, labels.
2. Details: windows, the door hood, lanterns, the pool's border, furnishing, the arena's banners, braziers, weapon racks, fighting ring, gateways and the champion's box. Then a 3D review and a refining round.
3. Review and finishing touches (this one).

PASS 3: WHAT THE REVIEW FOUND AND CHANGED
- The arena had seats and weapons but nothing that said people train there: two training dummies on the sand (1.0 has none to place, so they're built from blocks: a post, arms across it, a straw head), the fighters' bench and a water barrel at the foot of their stair.
- Nothing named the bathhouse from the walkway: its sign hangs on a bracket from the wall beside the door, over the potted shrub (first tried over the door, where it hung in front of the door's top).
- Lived in: the bathhouse cat's bed and bowl by the warm stove; a jug with the cup on the loggia's table.
- The carpentry's hand-off suggested a footbridge across the 2 m between its deck and the bathhouse's. Not built: the carpentry's kiln shed backs onto that edge, so there's nowhere for it to land; the bathhouse is a short walk round by the walkway.
- The 1 m layout (doc laketown): labels for the bath hall, the Barber's rooms and the loggia, the champion's box, and the fighters' way and its stair up from the bathhouse.
- Checked, all clear: nothing in front of any door or window, no door onto a drop, every stair with 1 m clear at the foot and top and 2 m of headroom, no item running into another or into a raised piece, nothing outside the altar's build volume. In the site plan (a dry run), nothing is blocked where the bathhouse and arena meet the walkway, the carpentry and the layout's causeway.

CONNECTIONS (for the neighbouring blueprints to match)
- West walkway (the carpentry and square blueprints): the bathhouse stair arrives at its branch, x 54..58, y 86.
- Carpentry: its stair (x 42..46, y 110..116) arrives at the arena's west landing (x 46..48.5), which keeps 1 m clear in front of it.
- Causeway (its own blueprint, next): its stair up to the arena (x 72..74, y 110..116, rising 1 m west from the causeway's strip at +3 m) arrives at the arena's east landing (x 69.5..72, +4 m). Keep that stair where the layout has it, and give it the walkway style: stone cheeks, railings on the strip.

THE BATHHOUSE (+2 m, the Barber's, Elio Ricci): the layout's deck, 16 x 12 m of brick-timbered on a tarred edge, a railing round it; down a short stair (with stone cheeks) from the west walkway's branch to a double door under a tiled hood on brackets, lanterns either side, potted shrubs flanking the way in, a bench by the wall. Limestone below, brick-timbered above, 14.5 x 8 m.
- The bath hall (ground floor, polished stone): a sunken plunge pool, the water 0.5 m below the floor, a fancy stone border round it; the four bathtubs of 1.0 (Wooden, Bronze, Granite Stone, Maritime); lockers either side of the door with towels by them; benches; buckets by the tubs; a stone stove for the steam under its own chimney, a kettle of hot water on it; a brazier by the pool; high windows (2 m up) all round for privacy; the stair up along the east wall; a door south to the arena, a lantern over it.
- Upstairs (+6 m): the Barber's salon (the Barber, his chair, a basin, a side table with the shaving bowl, a waiting bench, a carved shelf) and his room (the bed, a nightstand, a wardrobe, a chest, a mat) behind a partition; windows (window boxes on the north); doors out onto the loggia, open on the south side under the roof on limestone columns with a parapet, chairs and a little table with a cup at the parapet: a good seat for a bout. Barbers ran the bathhouses.
- The roof: a tiled hip over house and loggia, cut flat for a cupola that lets the steam out (a limestone drum with openings, a little castle slate dome, a fancy stone finial); the stove's chimney capped, with a pot.
- The Barber in 1.0 has no station: you talk to him to change your appearance (Destructoid's guide).

THE ARENA: the layout's ring, a round stone amphitheatre 26 m across on stilts.
- The floor: sand, 14 m across, at +2 m, walled round by a 2 m podium wall; a fighting ring marked in it in field stones; weapon racks round the edge facing the middle (sword and shield, two-handed, bow, staff, practice shields).
- The stands (+4 m): a promenade behind a fancy stone parapet over the floor with a brazier at each quarter, three tiers of seats rising outward (+4.5, +5, +5.5 m), an outer wall (to +7 m) with red banners on poles between the ways in.
- The champion's box on the south stands, facing the fighters' way: a red carpet floor at the top tier's height (the tiers are its steps), a flat red canopy on four limestone posts with a scalloped front edge, three chairs.
- The ways in, each a landing and an aisle through the wall and the tiers down to the promenade, a stone lintel over the gap in the wall and a lantern on the landing:
  - west, from the carpentry's stair (x 46..48, y 110..116: the landing the carpentry's blueprint asked for);
  - east, from the causeway's stair (x 72);
  - north, the fighters' way: from the bathhouse's south door up a short stair (2 m, stone cheeks) onto the stands, across the promenade and down a stair onto the sand.
- Refining round: the box's canopy was a tiled hip that read as a little house sitting on the stands; it's a flat red cloth now, matching the banners.

CONNECTIONS
- West walkway: the bathhouse stair arrives at its branch (x 54..58), as the square's and the carpentry's blueprints have it.
- Carpentry: its stair (x 42..46) arrives at the arena's west landing.
- Causeway (its own blueprint): its stair (x 72..74, the layout's) arrives at the arena's east landing.

SIZES: furniture, light and weapon rack sizes are estimates until measured; the Barber is the planner's 3 x 3 m NPC placeholder.

STILTS: 1 m posts on the layout's 4 m grid, from the lake bed 4 m down to each deck's underside, with tarred rim beams under the edges.
"""
A.save('laketown_bathhouse.json', NOTES, 'r-claude-laketown-bathhouse-3')
