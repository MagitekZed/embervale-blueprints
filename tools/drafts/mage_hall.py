"""Mage library: the survivors' hall, 0.5 m detail plan (every square is one single block).

Run: python mage_hall.py  ->  writes mage-hall.json
Local coordinates: the site plan's hall corner (104, 100) sits at (2, 2) here.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mage_common import Plan, PALETTE, FLOORS

# Extra real blocks for this plan (names/colours from the block catalogue)
PALETTE['m'] = {'name': 'Mycelium Overgrown Block', 'kind': 'wall', 'color': '#72664f'}
PALETTE['H'] = {'name': 'Half-Timbered Block', 'kind': 'wall', 'color': '#71665e'}
PALETTE['W'] = {'name': 'Refined Wood Block', 'kind': 'wall', 'color': '#75675f'}
PALETTE['C'] = {'name': 'Roughly Cut Stone Block (chimney)', 'kind': 'wall', 'color': '#62605d', 'height': 6}
PALETTE['K'] = {'name': 'Roughly Cut Stone Block', 'kind': 'floor', 'color': '#62605d'}        # hearth floor
PALETTE['T'] = {'name': 'Refined Wood Block (stage)', 'kind': 'block', 'color': '#75675f', 'height': 0.5}
PALETTE['X'] = {'name': 'Highly Polished Stone Block', 'kind': 'floor', 'color': '#b3b0a9'}     # bathhouse tiles
PALETTE['E'] = {'name': 'Weathered Stone Block', 'kind': 'block', 'color': '#6a6c67', 'height': 0.5}
PALETTE['Z'] = {'name': 'Rough Wood Block (pergola post)', 'kind': 'wall', 'color': '#7a6653', 'height': 2.5}
PALETTE['z'] = {'name': 'Rough Wood Block (pergola beam)', 'kind': 'block', 'color': '#7a6653', 'height': 0.5, 'base': 2.5, 'under': ';'}
FLOORS.update('KTX')

P = Plan("Mage library: survivors' hall", 0.5, 46, 30, 160)
P.project = 'Mage library'
g0 = P.level('g0', 'Ground: great hall & east wing', 0, 4)
g1 = P.level('g1', 'Dormitory & sitting room', 4, 4)
g2 = P.level('g2', 'Roof garden & hall attic', 8, 4)
KNEE = 2.5                            # the great hall's attic kneewall; its roof starts on top
hr = P.level('hr', f'Great hall roof ({8 + KNEE:g} m)', 8 + KNEE, 11)

X0, X1, Y0, Y1 = 2, 44, 2, 24
PART = 24                             # hall | east wing partition (x 24-25)

# ================================================================= ground
P.box_walls(g0, X0, Y0, X1, Y1, 'A', 1, floor=',')
P.scatter(g0, 0, 0, 46, 30, 'm', 0.1, 'A', 601)
P.rect(g0, PART, 3, PART + 1, 23, 'A'); P.rect(g0, PART, 11, PART + 1, 14, 'D')
# great hall: Refined Wood floor, central columns, fireplace, stage
P.rect(g0, 3, 3, PART, 23, '.')
for y in (7.5, 12.5, 17.5): P.rect(g0, 13, y, 14, y + 1, 'P')
P.rect(g0, 3, 14, 5, 14.5, 'S'); P.rect(g0, 3, 18.5, 5, 19, 'S'); P.rect(g0, 2, 14, 3, 19, 'S')   # fireplace surround
P.rect(g0, 3, 14.5, 5, 18.5, 'K')
P.rect(g0, 18, 3, PART, 7, 'T')                                                                    # bard's stage
# east wing: Limestone floor; bathhouse partition and tiles
P.rect(g0, 33.5, 15, 34, 23, 'W'); P.rect(g0, 34, 14.5, 43, 15, 'W'); P.rect(g0, 37, 14.5, 38.5, 15, 'D')
P.rect(g0, 34, 15, 43, 23, 'X')
P.rect(g0, 38, 18.5, 42.5, 22.5, 'w'); P.rect(g0, 38.5, 19, 42, 22, '~')                           # plunge pool
P.lining(g0, 'A', 'y', ',', P.sq(40), P.sq(6), P.sq(43), P.sq(13))                                 # collector's shelves
# doors and windows
P.rect(g0, 19, Y1 - 1, 24, Y1, 'G')                                                                # great south door
P.rect(g0, X0, 8, X0 + 1, 11, 'D'); P.rect(g0, 19, Y0, 22, Y0 + 1, 'D'); P.rect(g0, X1 - 1, 9, X1, 11, 'D')
for x in (6, 10, 15, 27, 31, 36, 40): P.rect(g0, x, Y0, x + 1, Y0 + 1, 'o', only='Am')
for x in (6, 10, 15, 28, 32, 36, 40): P.rect(g0, x, Y1 - 1, x + 1, Y1, 'o', only='Am')
# paths out
P.rect(g0, 19, Y1, 24, 30, ':'); P.rect(g0, 0, 8, X0, 11, ':'); P.rect(g0, 19, 0, 22, Y0, ':'); P.rect(g0, X1, 9, 46, 11, ':')

# ================================================================= upper floor (4-8 m): Half-Timbered storey
P.box_walls(g1, X0, Y0, X1, Y1, 'H', 1, floor='.')
P.rect(g1, PART, 3, PART + 1, 23, 'W'); P.rect(g1, PART, 11, PART + 1, 13, 'D')
P.rect(g1, 3.5, 3.5, 5.5, 7.5, ' ')                                                                # stairwell from the hall
for x in (6, 10, 15, 19, 27, 31, 36, 40):
    P.rect(g1, x, Y0, x + 1, Y0 + 1, 'o'); P.rect(g1, x, Y1 - 1, x + 1, Y1, 'o')
P.rect(g1, X0, 9, X0 + 1, 10, 'o'); P.rect(g1, X1 - 1, 17, X1, 18, 'o')
P.lining(g1, 'H', 'y', '.', P.sq(PART + 1), P.sq(15), P.sq(43), P.sq(23))                          # sitting-room shelves
P.rect(g1, 26, 15, 43, 23, '.', only='y'); P.rect(g1, 42.5, 15, 43, 23, 'y', only='.')

# ================================================================= 8 m: hall attic (west) and roof garden (east)
# great hall attic: a Half-Timbered kneewall under the roof, with a door out of the east gable onto the garden
knee = P._alloc({'name': 'Half-Timbered Block (kneewall)', 'kind': 'wall', 'color': '#71665e', 'height': KNEE})
P.box_walls(g2, X0, Y0, PART + 1, Y1, knee, 1, floor='.')
P.rect(g2, PART, 12, PART + 1, 14, 'D')                                                            # gable-end door
P.rect(g2, 15, 10, 19, 12, ' ')                                                                    # stairwell from the dormitory
# roof garden on the east half
P.rect(g2, PART + 1, Y0, X1, Y1, ';')
P.rect(g2, PART + 1, Y0, X1, Y0 + 0.5, 'w'); P.rect(g2, PART + 1, Y1 - 0.5, X1, Y1, 'w'); P.rect(g2, X1 - 0.5, Y0, X1, Y1, 'w')
for x0 in (26.5, 34.5):                                                                            # raised planters
    P.rect(g2, x0, 17.5, x0 + 6, 21.5, 'E'); P.rect(g2, x0 + 0.5, 18, x0 + 5.5, 21, 'f')
for px in (28, 33, 38):                                                                            # pergola posts
    for py in (5, 11):
        P.rect(g2, px, py, px + 0.5, py + 0.5, 'Z')
for py in (5, 11): P.rect(g2, 28.5, py, 38, py + 0.5, 'z')                                         # beams
for px in (28, 33, 38): P.rect(g2, px, 5.5, px + 0.5, 11, 'z')
for x in (30, 31.5, 35, 36.5): P.rect(g2, x, 5.5, x + 0.5, 11, 'z')                                # rafters
P.scatter(g2, PART + 1, Y0, X1, Y1, 'V', 0.008, ';', 602)

# chimney from the great-hall fireplace, up through every level and out through the roof
for g in (g1, g2):
    P.rect(g, 2, 15.5, 4, 17.5, 'C')

# ================================================================= great hall roof (10.5 m up)
# a tall Roof Tiles Block gable, ridge east-west, so its east gable end faces the roof garden
roof = P.roof(hr)
roof.gable(X0, Y0, PART + 1, Y1, 'x', 'tiles', pitch=0.8, overhang=1.0, end_overhang=0.5)
roof.caps('ridge')
roof.paint()
CH_H = 11.0
stack = P._alloc({'name': 'Roughly Cut Stone Block (chimney)', 'kind': 'wall', 'color': '#62605d', 'height': CH_H})
P.rect(hr, 2, 15.5, 4, 17.5, stack)
for x, y in P.cells_rect(1.5, 15, 4.5, 18):                                                       # cap course
    if not (P.sq(2) <= x < P.sq(4) and P.sq(15.5) <= y < P.sq(17.5)):
        P.overlay(hr, x, y, 'Roughly Cut Stone Block (chimney cap)', '#56544f', 0.5, CH_H - 0.5)

# ================================================================= items
I = P.item
# great hall
I('g0', 'stairs', 'Stairs up', 3.5, 3.5, 2, 4, 4, 0, '#a98a62', 'st1')
I('g0', 'campfire', 'Hearth fire', 3, 15.5, 2, 2, 1, color='#c46a2a', iid='hearth')
I('g0', 'npc-bard', 'Bard', 19.5, 3.5, 3, 3, 2, color='#b0596f', iid='bard')
for k, y in enumerate((9, 14)):
    I('g0', 'table', 'Long table', 6, y, 6, 1.5, 1, color='#9a7b52', iid=f'lt{k}')
    I('g0', 'custom', 'Bench', 6, y - 0.5, 6, 0.5, 0.5, color='#8a6a48', iid=f'bn{k}a')
    I('g0', 'custom', 'Bench', 6, y + 1.5, 6, 0.5, 0.5, color='#8a6a48', iid=f'bn{k}b')
I('g0', 'table', 'Long table', 16, 13, 1.5, 6, 1, color='#9a7b52', iid='lt2')
I('g0', 'mchest-small', 'Small Magic Chest', 22.5, 21.5, 1, 1, 1, color='#7b68b5', iid='mch')
for k, (x, y) in enumerate(((8, 3.5), (15, 21.5), (22.5, 9))):
    I('g0', 'light', 'Lantern', x, y, 0.5, 0.5, 1.5, color='#e3b341', iid=f'lan{k}')
# east wing
I('g0', 'npc-barber', 'Barber (Elio Ricci)', 26, 3.5, 3, 3, 2, color='#9c6b8e', iid='barber')
I('g0', 'custom', 'Barber chair', 30, 4.5, 1, 1, 1, color='#6b4a2e', iid='chair')
I('g0', 'custom', 'Mirror', 30, 3, 1, 0.5, 2, color='#a9d8e6', iid='mirror')
I('g0', 'npc-collector', 'Collector', 39.5, 3.5, 3, 3, 2, color='#8a6aa8', iid='coll')
I('g0', 'custom', 'Curio cabinet', 36.5, 3.5, 2, 1, 2, color='#6b4a2e', iid='curio')
I('g0', 'table', 'Lounge table', 28, 18, 2, 2, 1, color='#9a7b52', iid='lounge')
I('g0', 'custom', 'Settee', 27, 21.5, 4, 1, 1, color='#8c6b4f', iid='settee')
I('g0', 'custom', 'Settee', 31.5, 17.5, 1, 3, 1, color='#8c6b4f', iid='settee2')
I('g0', 'bathtub', 'Bathtub', 34.5, 15.5, 2, 3, 1, color='#6f8fa3', iid='tub1')
I('g0', 'bathtub', 'Bathtub', 34.5, 19.5, 2, 3, 1, color='#6f8fa3', iid='tub2')
I('g0', 'chest-small', 'Small Chest (towels)', 41.5, 15.5, 1, 1, 1, color='#8a5a2b', iid='towels')
# dormitory
for k, x in enumerate((7, 10, 13, 16, 19)):
    I('g1', 'bed', 'Survivor bed', x, 3.5, 2, 3, 1, 0, '#8c6b4f', f'bn{k}')
    I('g1', 'chest-small', 'Small Chest', x + 0.5, 7, 1, 1, 1, color='#8a5a2b', iid=f'cn{k}')
for k, x in enumerate((5, 8.5, 12, 15.5, 19)):
    I('g1', 'bed', 'Survivor bed', x, 19.5, 2, 3, 1, 180, '#8c6b4f', f'bs{k}')
    I('g1', 'chest-small', 'Small Chest', x + 0.5, 18, 1, 1, 1, color='#8a5a2b', iid=f'cs{k}')
# sitting room
I('g1', 'stairs', 'Stairs to the attic', 15, 10, 2, 4, 4, 90, '#a98a62', 'st2')
I('g1', 'table', 'Card table', 29, 6, 2, 2, 1, color='#9a7b52', iid='card')
I('g1', 'custom', 'Armchair', 27, 6.5, 1, 1, 1, color='#8c6b4f', iid='arm1')
I('g1', 'custom', 'Armchair', 31.5, 6.5, 1, 1, 1, color='#8c6b4f', iid='arm2')
I('g1', 'table', 'Writing desk', 33, 19, 2, 1, 1, color='#9a7b52', iid='desk')
I('g1', 'custom', 'Lectern', 29, 18.5, 1, 1, 1.5, color='#7a5236', iid='lect')
# roof garden
for k, x in enumerate((29, 34)):
    I('g2', 'custom', 'Bench', x, 7, 3, 0.5, 0.5, color='#8a6a48', iid=f'rb{k}')
I('g2', 'table', 'Garden table', 31, 8.5, 2, 1, 1, color='#9a7b52', iid='gtable')
I('g2', 'seedbed', 'Seedbed', 41, 18.5, 2, 2, 0.5, color='#6f8a43', iid='seed')
for k in range(2):
    I('g2', 'chest-small', 'Small Chest (attic store)', 4 + 3 * k, 3.5, 1, 1, 1, color='#8a5a2b', iid=f'att{k}')
for k, (x, y) in enumerate(((25.5, 3), (42.5, 22.5), (25.5, 22.5), (42.5, 3))):
    I('g2', 'light', 'Lantern', x, y, 0.5, 0.5, 1.5, color='#e3b341', iid=f'rlan{k}')

Z = P.zone
Z('g0', 'Great hall', 3, 3, 24, 23, '#b0596f')
Z('g0', "Barber's corner", 25, 3, 33, 9, '#9c6b8e')
Z('g0', "Collector's corner", 34, 3, 43, 9, '#8a6aa8')
Z('g0', 'Lounge', 25, 14, 33, 23, '#b8862b')
Z('g0', 'Bathhouse', 34, 15, 43, 23, '#2f7fb3')
Z('g1', 'Dormitory', 3, 3, 24, 23, '#8a5cc2')
Z('g1', 'Sitting room', 25, 3, 43, 23, '#3f8a4f')
Z('g2', 'Roof garden', 25, 3, 43, 23, '#5f7d3a')
Z('g2', 'Hall attic', 3, 3, 24, 23, '#8a6a48')

P.clear_under_items('V', lambda lid, x, y: ';' if lid == 'g2' else ',')
problems = P.check(outdoor_ok=('g0',), ignore_types=('stairs', 'tree', 'spire'))
print('item problems:', len(problems))
for p_ in problems[:40]: print('  ', p_)

NOTES = """Survivors' hall of the mage library, drafted by Claude. Uses 0.5 m squares, so every square is one single block. On the campus site plan it's the building south-east of the rotunda.

SIZE
- 42 x 22 m, two storeys plus a roof garden.
- Temple Stones ground floor patched with Mycelium Overgrown Block, with a Half-Timbered Block upper storey.

GREAT HALL (west half)
- Refined Wood floor and a row of three Highly Polished Stone columns.
- Long tables with benches.
- A Roughly Cut Stone fireplace on the west wall, with its chimney rising through the roof.
- A raised stage for the Bard in the north-east corner.
- Doors: a great door south (towards the entrance plaza), doors north (towards the tower) and west.

EAST WING
- The Barber's corner (chair and mirror) and the Collector's corner (curio cabinet, shelving).
- A lounge with settees.
- A bathhouse behind Refined Wood partitions: Highly Polished Stone tiles, two bathtubs and a plunge pool. Comfort items help with the Rested buff.

UPSTAIRS
- A dormitory of 10 beds, each with a chest.
- A sitting room with a card table, armchairs, a writing desk, a lectern and shelving.
- Stairs up from the dormitory to the hall attic.

GREAT HALL ROOF
- A tall Roof Tiles Block gable with a Temple Stones ridge cap, about 10 m high.
  - It sits on a 2.5 m Half-Timbered kneewall, so the attic under it is usable: a store with chests.
  - The eaves overhang 1 m.
  - The ridge runs east-west, so the east gable end faces the roof garden. A door in that gable is the way out onto the garden.
- The fireplace chimney rises through the west gable, capped, above the ridge.

ROOF GARDEN (8 m, east half)
- Field Stones terrace inside a Limestone parapet, entered through the door in the great hall's east gable.
- A Rough Wood pergola (posts, beams and rafters lifted with "Raise by") over benches and a table.
- Two raised planters and a Seedbed.

NOTES
- Crafting stations and furniture sizes are estimates. Benches, settees and armchairs are custom placeholders.
"""
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mage-hall.json')
print('bytes', P.save(out, NOTES, 'r-claude-mage-hall-1'))
print(P.preview('g2', 2))
