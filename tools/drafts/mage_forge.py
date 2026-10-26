"""Mage library: the forge court, 0.5 m detail plan (every square is one single block).

Run: python mage_forge.py  ->  writes mage-forge.json
Local coordinates: the site plan's forge court corner (14, 62) sits at (2, 2) here.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mage_common import Plan, PALETTE, FLOORS
FLOORS.add('K')                       # hearth flooring is a floor

# Extra real blocks for this plan (names/colours from the block catalogue)
PALETTE['m'] = {'name': 'Mycelium Overgrown Block', 'kind': 'wall', 'color': '#72664f'}
PALETTE['N'] = {'name': 'Temple Stones (arch haunch)', 'kind': 'block', 'color': '#857f5d', 'height': 1.5, 'base': 2.5, 'under': ';'}
PALETTE['n'] = {'name': 'Temple Stones (arch crown)', 'kind': 'block', 'color': '#857f5d', 'height': 1, 'base': 3, 'under': ';'}
PALETTE['C'] = {'name': 'Roughly Cut Stone Block (chimney)', 'kind': 'wall', 'color': '#62605d', 'height': 6}
PALETTE['K'] = {'name': 'Roughly Cut Stone Block', 'kind': 'floor', 'color': '#62605d'}       # hearth floor

P = Plan('Mage library: forge court', 0.5, 44, 44, 160)
P.project = 'Mage library'
g0 = P.level('g0', 'Ground: workshops & yard', 0, 4)
g1 = P.level('g1', 'Lofts', 4, 4)
g2 = P.level('g2', 'Roofs & chimneys', 8, 4)

X0, X1, Y0, Y1 = 2, 40, 2, 40           # court outer faces
NW = (2, 2, 40, 12)                     # north wing: smithy
WW = (2, 11, 12, 31)                    # west wing: carpentry & leather
SW = (2, 30, 40, 40)                    # south wing: kitchen & stores
YARD = (12, 12, 39, 30)

# ================================================================= ground
for r in (NW, WW, SW):
    P.box_walls(g0, *r, 'A', 1, floor=',')
P.rect(g0, 3, 11, 11, 12, 'A'); P.rect(g0, 3, 30, 11, 31, 'A')              # wing junction walls
P.rect(g0, 3, 3, 39, 11, ';')                                                # smithy floor: Field Stones
P.rect(g0, 3.5, 3, 15, 6, 'K')                                               # hearth floor along the forge wall
P.rect(g0, 2, 2, 40, 3, 'S', only='A'); P.rect(g0, 2, 2, 3, 12, 'S', only='A'); P.rect(g0, 39, 2, 40, 12, 'S', only='A')
P.scatter(g0, 0, 0, 44, 44, 'm', 0.12, 'A', 501)
# smithy front: open arcade to the yard, columns every 3 m with arches
cols = [12 + 3 * k for k in range(9)]                                        # 12 .. 36
P.rect(g0, 12, 11, 39, 12, ';')
for k, x in enumerate(cols):
    P.rect(g0, x, 11, x + 1, 12, 'P')
    gap_end = cols[k + 1] if k + 1 < len(cols) else 39
    span = int((gap_end - (x + 1)) / 0.5)
    pattern = 'N' + 'n' * (span - 2) + 'N' if span >= 2 else 'n' * span
    for j, ch in enumerate(pattern):
        P.rect(g0, x + 1 + j * 0.5, 11, x + 1.5 + j * 0.5, 12, ch)
# doors
P.rect(g0, 25, 2, 27, 3, 'D')                                                # smithy north door (to the cloister path)
P.rect(g0, 5, 11, 7, 12, 'D')                                                # smithy <-> carpentry
P.rect(g0, 3, 20, 11, 21, 'A'); P.rect(g0, 6, 20, 8, 21, 'D')                # carpentry | leather partition
P.rect(g0, 11, 14, 12, 16, 'D'); P.rect(g0, 11, 25, 12, 27, 'D')             # west wing doors to the yard
P.rect(g0, 20, 31, 21, 39, 'A'); P.rect(g0, 20, 34, 21, 36, 'D')             # kitchen | stores partition
P.rect(g0, 14, 30, 16, 31, 'D'); P.rect(g0, 28, 30, 31, 31, 'G')             # south wing doors to the yard
P.rect(g0, 39, 31, 40, 39, 'A', only='A')
# windows
for x in (8, 18, 31): P.rect(g0, x, 2, x + 1, 3, 'o', only='SA')
for y in (13, 17, 23, 28): P.rect(g0, 2, y, 3, y + 1, 'o', only='Am')
for x in (13, 24, 33): P.rect(g0, x, 39, x + 1, 40, 'o', only='Am')
P.rect(g0, 39, 4, 40, 5, 'o', only='S'); P.rect(g0, 39, 34, 40, 35, 'o', only='Am')
# quench trough beside the forge
P.rect(g0, 8, 7, 11, 8.5, 'w'); P.rect(g0, 8.5, 7.5, 10.5, 8, '~')
# yard: Field Stones, Limestone walks, a low east wall with a gated opening
P.rect(g0, *YARD, ';')
P.rect(g0, 12, 19, 39, 22, ',')                                              # east-west walk to the gate
P.rect(g0, 24.5, 12, 26.5, 30, ',')                                          # north-south walk
P.rect(g0, 39, 12, 40, 30, 'w')
P.rect(g0, 39, 18.5, 40, 22.5, ',')
P.rect(g0, 39, 17.5, 40, 18.5, 'P'); P.rect(g0, 39, 22.5, 40, 23.5, 'P')     # gate posts
P.rect(g0, 40, 18.5, 44, 22.5, ':')                                          # path on to the rotunda
P.rect(g0, 25, 0, 27, 2, ':')                                                # path north to the cloister
P.disc(g0, 31, 26.5, 1.4, 'w'); P.disc(g0, 31, 26.5, 0.9, '~')               # well
P.scatter(g0, *YARD, 'V', 0.02, ';', 502)

# ================================================================= lofts (4-8 m)
P.box_walls(g1, *NW, 'A', 1)                                                 # smithy stays double height...
P.rect(g1, 34, 3, 39, 11, '.')                                               # ...except a loft at the east end
P.rect(g1, 34, 6.5, 36, 10.5, ' ')                                           # stairwell
P.rect(g1, 33.5, 3, 34, 11, 'w')                                             # loft railing
for x in (14, 20, 26, 32): P.rect(g1, x, 11, x + 1.5, 12, 'o')               # clerestory over the arcade
for x in (8, 18, 31): P.rect(g1, x, 2, x + 1, 3, 'o')
P.box_walls(g1, *WW, 'A', 1, floor='.')
P.rect(g1, 3, 11, 11, 12, 'A')
P.rect(g1, 11, 16, 12, 17.5, 'D')                                            # loft door to the outside stair landing
P.rect(g1, 12, 15.5, 14, 17.5, ',')                                          # landing
P.rect(g1, 14, 15.5, 14.5, 17.5, 'w'); P.rect(g1, 12, 15, 14.5, 15.5, 'w')
for y in (13, 23, 28): P.rect(g1, 2, y, 3, y + 1, 'o')
P.box_walls(g1, *SW, 'A', 1, floor='.')
P.rect(g1, 3, 30, 11, 31, 'A'); P.rect(g1, 20, 31, 21, 39, 'A'); P.rect(g1, 20, 34, 21, 36, 'D')
P.rect(g1, 37, 31.5, 39, 35.5, ' ')                                          # stores stairwell
for x in (13, 24, 33): P.rect(g1, x, 39, x + 1, 40, 'o')
for x in (16, 27, 35): P.rect(g1, x, 30, x + 1, 31, 'o', only='A')

# ================================================================= roofs (8 m up) and chimneys
# Stone Shingle Roof Block gables with 1 m eaves; where wings cross, the higher roof wins and valleys form.
roof = P.roof(g2)
roof.gable(2, 2, 12, 40, 'y', 'shingle', pitch=1.0, overhang=1.0, end_overhang=1.0)        # west wing
roof.gable(2, 30, 40, 40, 'x', 'shingle', pitch=1.0, overhang=1.0, end_overhang=0.5)       # south wing
# smithy: steeper and taller, with a monitor along the ridge (a raised roof over open vents, for the forge smoke)
SM_PITCH = 1.2
roof.gable(2, 2, 40, 12, 'x', 'shingle', pitch=SM_PITCH, overhang=1.0, end_overhang=0.5)
smithy_h = lambda y_m: 0.5 + (min(y_m - 1, 13 - y_m) - 0.25) * SM_PITCH   # smithy roof height at a square centre
MON = (14, 5.5, 37, 8.5)                                                   # monitor over the forge line
mon_base = round((smithy_h(MON[1] - 0.25) + 1.75) * 2) / 2                 # its eaves stand 1.75 m+ clear
roof.gable(*MON, 'x', 'shingle', pitch=1.0, overhang=0.5, base=mon_base)
roof.caps('ridge')                                                         # Temple Stones ridge caps
roof.paint()
# vent posts under the monitor's eaves, every 3 m, standing on the smithy roof
for xm in range(15, 37, 3):
    for ym in (MON[1] - 0.5, MON[3]):
        x, y = P.sq(xm), P.sq(ym)
        b = math.floor(smithy_h(ym + 0.25) * 2) / 2
        P.overlay(g2, x, y, 'Roughly Cut Stone Block (vent post)', '#62605d', mon_base - 0.5 - b, b)
CHIMNEYS = [(5.5, 2), (9.5, 2), (12.5, 2), (28, 2), (32, 2),                  # forge, smelters, charcoal kiln, blast furnace
            (2, 17.5),                                                       # carpentry kiln
            (4.5, 39), (7.5, 39)]                                            # oven, cooking station
CH_H = 8.0                                                                   # chimneys rise 8 m from the wall tops
for (cx, cy) in CHIMNEYS:
    P.rect(g1, cx, cy, cx + 1, cy + 1, 'C')
    P.rect(g2, cx, cy, cx + 1, cy + 1, ' ')
    for x, y in P.cells_rect(cx, cy, cx + 1, cy + 1):
        g2[y][x] = P._alloc({'name': 'Roughly Cut Stone Block (chimney)', 'kind': 'wall', 'color': '#62605d', 'height': CH_H})
    for x, y in P.cells_rect(cx - 0.5, cy - 0.5, cx + 1.5, cy + 1.5):     # a projecting cap course at the top
        if not (P.sq(cx) <= x < P.sq(cx + 1) and P.sq(cy) <= y < P.sq(cy + 1)):
            P.overlay(g2, x, y, 'Roughly Cut Stone Block (chimney cap)', '#56544f', 0.5, CH_H - 0.5)

# ================================================================= items
I = P.item
# smithy
I('g0', 'forge', 'Forge', 5, 3.5, 2, 2, 2, color='#6f6a66', iid='forge')
I('g0', 'smelter', 'Smelter', 9, 3.5, 2, 2, 3, color='#7b5a4a', iid='sm1')
I('g0', 'smelter', 'Smelter', 12, 3.5, 2, 2, 3, color='#7b5a4a', iid='sm2')
I('g0', 'npc-blacksmith', 'Blacksmith', 4, 7, 3, 3, 2, color='#5f6770', iid='smith')
I('g0', 'smithing-tools', 'Smithing Tools', 14, 7.5, 2, 2, 1, color='#5a6066', iid='stools')
I('g0', 'chest-large', 'Large Chest (ore)', 18, 3.5, 2, 1, 1, color='#7a4f27', iid='ore')
I('g0', 'chest-large', 'Large Chest (coal)', 21, 3.5, 2, 1, 1, color='#7a4f27', iid='coal')
I('g0', 'charcoal-kiln', 'Charcoal Kiln', 27.5, 3.5, 2, 2, 2.5, color='#5f5550', iid='ckiln')
I('g0', 'blast-furnace', 'Blast Furnace', 31.5, 3.5, 2, 2, 4, color='#6a4a3c', iid='blast')
for k in range(3):
    I('g0', 'mchest-small', 'Small Magic Chest', 36 + k, 3.5, 1, 1, 1, color='#7b68b5', iid=f'mcs{k}')
I('g0', 'stairs', 'Stairs to the loft', 34, 6.5, 2, 4, 4, 0, '#a98a62', 'st_smith')
I('g1', 'bed', 'Blacksmith’s bed', 36.5, 3.5, 2, 3, 1, 0, '#8c6b4f', 'bed_smith')
I('g1', 'chest-medium', 'Medium Chest', 37, 8.5, 1.5, 1, 1, color='#7a4f27', iid='loftchest')
# carpentry
I('g0', 'npc-carpenter', 'Carpenter', 3.5, 12.5, 3, 3, 2, color='#9a7344', iid='carp')
I('g0', 'table-saw', 'Table Saw', 7.5, 12.5, 2, 2, 1, color='#a5824f', iid='saw')
I('g0', 'masonry-tools', 'Masonry Tools', 7.5, 15, 2, 2, 1, color='#8a8f87', iid='mason')
I('g0', 'kiln', 'Kiln', 3.5, 16.5, 2, 2, 2, color='#a0613f', iid='kiln')
I('g0', 'chest-large', 'Large Chest (lumber)', 7.5, 18.5, 2, 1, 1, color='#7a4f27', iid='lumber')
# leatherworks
I('g0', 'npc-hunter', 'Hunter', 3.5, 21.5, 3, 3, 2, color='#6d7a45', iid='hunter')
I('g0', 'tannery', 'Tanning Station', 7, 21.5, 2, 2, 1.5, color='#8b6a4a', iid='tan')
I('g0', 'hand-spindle', 'Hand Spindle', 7, 23.5, 2, 2, 1, color='#a68a62', iid='spindle')
I('g0', 'loom', 'Loom', 3.5, 27, 2, 2, 2, color='#a7896a', iid='loom')
I('g0', 'spinning', 'Spinning Wheel', 6, 27, 2, 2, 1.5, color='#b49770', iid='spin')
I('g0', 'spinning-machine', 'Spinning Machine', 8.5, 27.5, 2, 2, 2, color='#9c8160', iid='spinm')
# west wing loft (outside stair from the yard)
I('g0', 'stairs', 'Outside stair to the loft', 12, 17.5, 2, 4, 4, 0, '#a98a62', 'st_west')
I('g1', 'bed', 'Carpenter’s bed', 3.5, 12.5, 2, 3, 1, 0, '#8c6b4f', 'bed_carp')
I('g1', 'bed', 'Hunter’s bed', 3.5, 26.5, 2, 3, 1, 180, '#8c6b4f', 'bed_hunt')
I('g1', 'chest-wooden', 'Wooden Chest', 8.5, 12.5, 1.5, 1, 1, color='#8a5a2b', iid='wch1')
I('g1', 'chest-wooden', 'Wooden Chest', 8.5, 28.5, 1.5, 1, 1, color='#8a5a2b', iid='wch2')
# kitchen
I('g0', 'oven', 'Oven', 3.5, 36.5, 2, 2, 2, color='#b0643a', iid='oven')
I('g0', 'cooking-station', 'Cooking Station', 6.5, 36.5, 2, 2, 1.5, color='#c46a2a', iid='cook')
I('g0', 'kitchen', 'Kitchen', 9.5, 36.5, 2, 2, 1.5, color='#9a6a48', iid='kitchen')
I('g0', 'table', 'Long table', 5, 32.5, 6, 1.5, 1, color='#9a7b52', iid='ltable')
I('g0', 'mchest-small', 'Small Magic Chest', 18.5, 37.5, 1, 1, 1, color='#7b68b5', iid='mck')
# stores
for k in range(7):
    I('g0', 'chest-large', 'Large Chest', 22 + k * 2.5, 37.5, 2, 1, 1, color='#7a4f27', iid=f'lcs{k}')
for k in range(5):
    I('g0', 'chest-large', 'Large Chest', 22 + k * 2.5, 33.5, 2, 1, 1, color='#7a4f27', iid=f'lcm{k}')
I('g0', 'quickstack', 'Quick Stack Station', 32, 31.5, 1, 1, 2, color='#4f7f8f', iid='qs')
I('g0', 'stairs', 'Stairs up', 37, 31.5, 2, 4, 4, 180, '#a98a62', 'st_south')
for k in range(3):
    I('g1', 'bed', 'Bunk', 4 + k * 3, 31.5, 2, 3, 1, 0, '#8c6b4f', f'bunk{k}')
for k in range(4):
    I('g1', 'chest-huge', 'Huge Chest', 23 + k * 3.5, 36.5, 2.5, 1.5, 1.5, color='#6b4422', iid=f'hc{k}')
# yard
I('g0', 'workbench', 'Workbench', 35, 13.5, 2, 2, 1, color='#9a7b52', iid='wb')
I('g0', 'drying-rack', 'Drying Rack', 14.5, 13.5, 2, 2, 2, color='#9a7d55', iid='dry')
I('g0', 'custom', 'Woodpile', 14.5, 27.5, 3, 1.5, 1.5, color='#7a5a3a', iid='wood')
I('g0', 'tree', 'Ancient tree', 35.5, 25.5, 3, 3, 12, color='#4f6b34', iid='tree')
I('g0', 'light', 'Lantern', 38.5, 17.5, 0.5, 0.5, 1.5, color='#e3b341', iid='lan1')
I('g0', 'light', 'Lantern', 38.5, 23, 0.5, 0.5, 1.5, color='#e3b341', iid='lan2')
I('g0', 'light', 'Lantern', 24, 12.5, 0.5, 0.5, 1.5, color='#e3b341', iid='lan3')

Z = P.zone
Z('g0', 'Smithy', 3, 3, 39, 11, '#c4501a')
Z('g0', 'Carpentry', 3, 12, 11, 20, '#9a7344')
Z('g0', 'Leatherworks', 3, 21, 11, 30, '#6d7a45')
Z('g0', 'Kitchen', 3, 31, 20, 39, '#b0643a')
Z('g0', 'Stores', 21, 31, 39, 39, '#8b8478')
Z('g0', 'Work yard', 12, 12, 39, 30, '#8a8a5a')
Z('g1', 'Blacksmith’s loft', 34, 3, 39, 11, '#c2416e')
Z('g1', 'Craftspeople’s loft', 3, 12, 11, 30, '#9a7344')
Z('g1', 'Bunk room', 3, 31, 20, 39, '#8a5cc2')
Z('g1', 'Stores loft', 21, 31, 39, 39, '#8b8478')

problems = P.check(outdoor_ok=('g0',), ignore_types=('stairs', 'tree'))
print('item problems:', len(problems))
for p_ in problems[:40]: print('  ', p_)

NOTES = """Forge court of the mage library, drafted by Claude. Uses 0.5 m squares, so every square is one single block. On the campus site plan it's the block west of the rotunda.

LAYOUT
- 38 x 38 m: three wings round a work yard. The yard opens east through a gate towards the rotunda, and the smithy has a door north to the cloister path.

SMITHY (north wing)
- Double height, open to the yard through an arcade of Highly Polished Stone columns and raised Temple Stones arches.
- Roughly Cut Stone back wall, with a hearth of Roughly Cut Stone Block flooring along the forge line.
- Stations: Forge, two Smelters, Charcoal Kiln and Blast Furnace along the back wall, each with its own chimney through the roof. Also Smithing Tools, and a quench trough beside the forge.
- Large Chests for ore and coal, and magic chests.
- The Blacksmith works at the forge and sleeps in the loft at the east end (stairs up).

CARPENTRY & LEATHERWORKS (west wing)
- Carpentry: Carpenter, Table Saw, Masonry Tools, Kiln (with chimney), lumber chest.
- Leatherworks: Hunter, Tanning Station, Hand Spindle, Loom, Spinning Wheel, Spinning Machine.
- An outside stair from the yard climbs to a landing and the craftspeople's loft (Carpenter's and Hunter's beds).

KITCHEN & STORES (south wing)
- Kitchen: Oven and Cooking Station (both chimneyed), Kitchen, long table.
- Stores: two rows of Large Chests, a Quick Stack Station, a great door to the yard, stairs up.
- Upstairs: a bunk room and a stores loft with Huge Chests.

YARD
- Field Stones with Limestone walks, a well, the Workbench, a Drying Rack, a woodpile and an ancient tree.
- A low Limestone wall closes the east side, with column gate posts and lanterns.

ROOFS
- Stone Shingle Roof Block gables on all three wings, with 1 m eaves and Temple Stones ridge caps.
  - Where the wings cross, the higher roof wins, so the corners form proper valleys and cross-gables.
  - The gable ends are the walls carried up.
- The smithy roof is steeper and taller, with a monitor along the ridge over the forge line.
  - The monitor is a raised strip of roof standing about 1.75 m clear on Roughly Cut Stone posts every 3 m.
  - The open sides let the forge smoke out.
- Roughly Cut Stone chimneys rise 8 m from the wall tops, each with a projecting cap course at the top.

NOTES
- Crafting stations are 2 x 2 m placeholders until measured. Chest sizes are estimates from the wiki-sourced library.
"""
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mage-forge.json')
print('bytes', P.save(out, NOTES, 'r-claude-mage-forge-1'))
print(P.preview('g0', 2))
