"""Starter house: a cozy farmstead for the first altar (level 1, 40 m), 0.5 m detail plan.

A thatched timber cottage (kitchen, hearth hall with the Flame Altar, store and stair, a sleeping loft with
beds for the first crafters and you), round a small courtyard: a stone smithy, a timber workshop for the
Carpenter and Hunter, a south range with the Alchemist's still room, a storehouse and a covered gateway,
and a kitchen garden behind the house for the Farmer.
Everything is built from blocks that unlock from day-one Springlands resources (see NOTES).
Run: python starter_house.py  ->  writes starter-house.json
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mage_common import Plan, PALETTE, ROOF_MATS, ALTAR_W, ALTAR_D, ALTAR_H

PALETTE.clear()
PALETTE.update({
    # walls and floors: catalogue names and colours (blocks.js)
    'W': {'name': 'Rough Wood Block', 'kind': 'wall', 'color': '#7a6653'},
    'S': {'name': 'Rough Stone Block', 'kind': 'wall', 'color': '#7d776a'},
    'w': {'name': 'Rough Wood Block', 'kind': 'floor', 'color': '#7a6653'},
    'p': {'name': 'Smooth Stone Road Block', 'kind': 'floor', 'color': '#746553'},
    'd': {'name': 'Dirt Road Block', 'kind': 'floor', 'color': '#8c7455'},
    'g': {'name': 'Farm Soil', 'kind': 'floor', 'color': '#90450d'},
})
ROOF_MATS['thatch'] = ('Plant Fiber Roof Block', '#725e4f')

P = Plan('Starter house (cozy farmstead)', 0.5, 40, 40, 40)
P.project = 'Starter house'
g0 = P.level('g0', 'Ground floor, workshops & yard', 0, 4)
lf = P.level('loft', 'Sleeping loft (4 m)', 4, 1)
wrf = P.level('wroof', 'Workshop & porch roofs (3 m)', 3, 5)
rf = P.level('roof', 'House roof (5 m)', 5, 6)
R = P.rect


def blk(name, h, base=0):
    e = {'name': name[:40], 'kind': 'block', 'color': PALETTE['S' if 'Stone' in name else 'W']['color'], 'height': h}
    if base: e['base'] = base
    return P._alloc(e)


def wal(name, h):
    return P._alloc({'name': name[:40], 'kind': 'wall', 'color': PALETTE['S' if 'Stone' in name else 'W']['color'], 'height': h})


I = P.item
Z = P.zone

# Doors and windows are placed items set in solid walls (each cuts its own opening), real ones made from
# Springlands materials at the sizes measured in game (blocks tall x wide): Wooden Door and Crude Wooden Door
# 5 x 4, Round Wooden Door 6 x 6, Wooden Window Frame 3 x 2, Round Wooden Window Frame 2 x 2, Large Round
# Wooden Window Frame 6 x 6. A window's top is level with the doors' (2.5 m up), a tall one starts 0.5 m up.
TALL = {'Wooden Door': 2.5, 'Crude Wooden Door': 2.5, 'Round Wooden Door': 3, 'Wooden Window Frame': 1.5,
        'Round Wooden Window Frame': 1, 'Large Round Wooden Window Frame': 3}


def O(lid, name, x0, y0, x1, y1):
    h = TALL[name]
    window = 'Window' in name
    P.opening(lid, name, x0, y0, x1, y1, h, max(0.5, 2.5 - h) if window else 0,
              ('#a3cfe6' if 'Round' in name else '#8fc3df') if window else '#6b4a2e')

# ================================================================= the house: 18 x 10 m, the altar at its heart
X0, Y0, X1, Y1 = 11, 15, 29, 25
R(g0, X0, Y0, X1, Y1, 'w')
P.box_walls(g0, X0, Y0, X1, Y1, 'W', 0.5)
foot = blk('Rough Stone Block (footing)', 0.5)               # a stone footing all round, a step at the doors
R(g0, X0 - 0.5, Y0 - 0.5, X1 + 0.5, Y0, foot); R(g0, X0 - 0.5, Y1, X1 + 0.5, Y1 + 0.5, foot)
R(g0, X0 - 0.5, Y0, X0, Y1, foot); R(g0, X1, Y0, X1 + 0.5, Y1, foot)
R(g0, 15.5, 15.5, 16, 24.5, 'W'); R(g0, 24, 15.5, 24.5, 24.5, 'W')   # kitchen | hall | store and stair
WD, WF, RW = 'Wooden Door', 'Wooden Window Frame', 'Round Wooden Window Frame'
O('g0', WD, 15.5, 21, 16, 23)                                         # kitchen | hall
O('g0', WD, 24, 19, 24.5, 21)                                         # hall | store and stair, in line with the altar
O('g0', WD, 19, 24.5, 21, 25)                                         # front door, under the porch
O('g0', WD, 13.5, 15, 15.5, 15.5)                                     # kitchen door to the garden
O('g0', WD, 28.5, 17.5, 29, 19.5)                                     # side door to the workshop
O('g0', WF, 13, 24.5, 14, 25); O('g0', WF, 26, 24.5, 27, 25)          # south: kitchen, store
for x0, x1 in ((16.5, 17.5), (22.5, 23.5)): O('g0', WF, x0, 24.5, x1, 25)   # south: over the armchairs
for x0, x1 in ((17.5, 18.5), (21.5, 22.5)): O('g0', WF, x0, 15, x1, 15.5)   # north: over the table
O('g0', WF, 25, 15, 26, 15.5)                                         # north: over the workbench
O('g0', RW, 11, 16.5, 11.5, 17.5); O('g0', RW, 11, 22.5, 11.5, 23.5)  # west: round, either side of the chimney (one over the Kitchen)
O('g0', RW, 28.5, 16, 29, 17)                                         # east: round, over the store chests
chimney = wal('Rough Stone Block (chimney)', 12)                       # outside the kitchen's west gable
R(g0, 10, 18.5, 11, 21.5, chimney)
post = wal('Rough Wood Block (post)', 3)                               # the porch
R(g0, 18.5, 25.5, 21.5, 27, 'p')                                      # centred on the front door
R(g0, 18.5, 26.5, 19, 27, post); R(g0, 21, 26.5, 21.5, 27, post)

# kitchen (the Farmer's cooking stations, by the chimney)
I('g0', 'cooking-station', 'Cooking Station', 11.5, 18.5, 2, 2, 1.5, color='#c46a2a', iid='cook')
I('g0', 'oven', 'Oven', 11.5, 20.5, 2, 2, 2, color='#b0643a', iid='oven')
I('g0', 'kitchen', 'Kitchen', 11.5, 22.5, 2, 2, 1.5, color='#9a6a48', iid='kitch')
for k, x in enumerate((11.5, 12.5)): I('g0', 'chest-small', 'Pantry chest', x, 15.5, 1, 1, 1, color='#8a5a2b', iid=f'pan{k}')
# hearth hall
# The altar (4 x 4 m) stands in the middle, at the centre of the build area. Round it: 2 m clear to the
# east and west, a long table under the north windows, armchairs in the south corners, and the ways in from
# the kitchen (west), the store (north-east) and the front door (south) left open.
I('g0', 'altar', 'Flame Altar', 20 - ALTAR_W / 2, 20 - ALTAR_D / 2, ALTAR_W, ALTAR_D, ALTAR_H, color='#d9541e', iid='altar')
for k, x in enumerate((17, 19)):
    I('g0', 'table', 'Table', x, 15.5, 2, 1, 1, color='#9a7b52', iid=f'tab{k}')
    I('g0', 'custom', 'Bench', x, 16.5, 2, 0.5, 0.5, color='#7a6653', iid=f'ben{k}')
for k, x in enumerate((16.5, 22.5)): I('g0', 'custom', 'Armchair by the fire', x, 23.5, 1, 1, 1, color='#8c6b4f', iid=f'arm{k}')
for k, x in enumerate((16, 23)): I('g0', 'light', 'Lantern', x, 15.5, 1, 1, 1.5, color='#e3b341', iid=f'hl{k}')
# store and stair
# The stair runs up the east wall and rises north, with a 1 m landing at its foot, so you walk on from
# the passage (2 m wide) that runs from the hall door down the west side of the store.
I('g0', 'workbench', 'Workbench', 24.5, 15.5, 2, 2, 1, color='#9a7b52', iid='wb')
I('g0', 'stairs', 'Stairs up to the loft', 26.5, 19.5, 2, 4, 4, 0, '#a98a62', 'st')
for k, (x, y) in enumerate(((26.5, 15.5), (27.5, 15.5), (26.5, 16.5), (27.5, 16.5))):
    I('g0', 'chest-small', 'Store chest', x, y, 1, 1, 1, color='#8a5a2b', iid=f'sc{k}')

# ---- sleeping loft: a 1 m kneewall under the thatch, beds along the north eave
R(lf, X0 + 0.5, Y0 + 0.5, X1 - 0.5, Y1 - 0.5, 'w')
P.box_walls(lf, X0, Y0, X1, Y1, 'W', 0.5)
R(lf, 26.5, 19.5, 28.5, 22.5, ' ')                                    # stairwell: open over the top 3 m
rail = blk('Rough Wood Block (railing)', 1)
R(lf, 26, 19.5, 26.5, 23, rail); R(lf, 26.5, 22.5, 28.5, 23, rail)    # you step off north, by your bed
for k, x in enumerate((12, 14.5, 17, 19.5, 22)): I('loft', 'bed', f'Bed: crafter {k + 1}', x, 15.5, 2, 3, 1, color='#8c6b4f', iid=f'bed{k}')
I('loft', 'bed2', 'Your bed', 25.5, 15.5, 3, 3, 1, color='#7d5d43', iid='mybed')
for k, x in enumerate((12, 13)): I('loft', 'chest-small', 'Clothes chest', x, 23.5, 1, 1, 1, color='#8a5a2b', iid=f'cc{k}')
I('loft', 'table', 'Table', 18.5, 21.5, 2, 1, 1, color='#9a7b52', iid='ltab')
I('loft', 'light', 'Lantern', 21, 21.5, 1, 1, 1.5, color='#e3b341', iid='ll')
# gable windows: the middle of each gable end rises as a 4 m wall from the loft floor (the thatch is above
# 8 m there), with small windows 1.5 to 2.5 m above the loft floor; the roof fills the gable on above them
gable = wal('Rough Wood Block', 4)
for gx in (X0, X1 - 0.5): R(lf, gx, 17.5, gx + 0.5, 22.5, gable)
O('loft', RW, X0, 17.5, X0 + 0.5, 18.5); O('loft', RW, X0, 21.5, X0 + 0.5, 22.5)    # west: a window each side of the chimney
O('loft', 'Large Round Wooden Window Frame', X1 - 0.5, 18.5, X1, 21.5)             # east: a big round one (6 x 6), over the stair

# ---- the thatch: steep (45 degree) gable, east-west ridge at 10.5 m, the chimney through the end
hr = P.roof(rf)
hr.gable(X0, Y0, X1, Y1, 'x', 'thatch', pitch=1.0, overhang=0.5, base=0.5)
hr.cut(10, 18.5, 11, 21.5)
hr.paint()

# ================================================================= workshops round the courtyard
# On the ground floor, in 3 m walls: their doors and windows sit in 3 m walls too, so nothing rises past
# the eaves of their roofs. Crude Wooden Doors (5 x 4), Wooden Window Frames (3 x 2), and on the workshop a
# Round Wooden Door (6 x 6), which fills its wall to the eaves.
wg = g0
S3, W3 = wal('Rough Stone Block', 3), wal('Rough Wood Block', 3)
CD = 'Crude Wooden Door'
# smithy (west): stone on three sides, open to the courtyard between timber posts
R(wg, 3.5, 26.5, 11, 37.5, 'd')
R(wg, 3, 26, 11, 26.5, S3); R(wg, 3, 37.5, 11, 38, S3); R(wg, 3, 26, 3.5, 38, S3)
for y in (29, 32, 35): R(wg, 10.5, y, 11, y + 0.5, W3)
O('g0', WF, 3, 34.5, 3.5, 35.5)
I('g0', 'forge', 'Forge', 3.5, 26.5, 2, 2, 2, color='#6f6a66', iid='forge')
I('g0', 'charcoal-kiln', 'Charcoal Kiln', 3.5, 29, 2, 2, 2.5, color='#5f5550', iid='ckiln')
I('g0', 'smithing-tools', 'Smithing Tools', 3.5, 31.5, 2, 2, 1, color='#5a6066', iid='stools')
I('g0', 'npc-blacksmith', 'Blacksmith (Oswald Anders)', 6.5, 28, 3, 3, 2, color='#5f6770', iid='smith')
I('g0', 'chest-small', 'Ore chest', 9.5, 26.5, 1, 1, 1, color='#8a5a2b', iid='ore')
# workshop (east): timber, a large square door onto the courtyard at the end of the cross path; the
# Carpenter north, the Hunter south
R(wg, 29, 26, 37, 38, 'w')
P.box_walls(wg, 29, 26, 37, 38, W3, 0.5)
O('g0', 'Round Wooden Door', 29, 29.5, 29.5, 32.5)
O('g0', WF, 36.5, 28.5, 37, 29.5); O('g0', WF, 36.5, 34.5, 37, 35.5); O('g0', WF, 32.5, 26, 33.5, 26.5)
O('g0', RW, 35, 37.5, 36, 38)                                         # round, over the Tanning Station
I('g0', 'npc-carpenter', 'Carpenter (Cade Hawthorn)', 29.5, 26.5, 3, 3, 2, color='#9a7344', iid='carp')
I('g0', 'masonry-tools', 'Masonry Tools', 32.5, 26.5, 2, 2, 1, color='#8a8f87', iid='mason')
I('g0', 'kiln', 'Kiln', 34.5, 26.5, 2, 2, 2, color='#a0613f', iid='kiln')
I('g0', 'npc-hunter', 'Hunter (Athalan Skree)', 29.5, 34.5, 3, 3, 2, color='#6d7a45', iid='hunt')
I('g0', 'drying-rack', 'Drying Rack', 32.5, 35.5, 2, 2, 2, color='#9a7d55', iid='rack')
I('g0', 'tannery', 'Tanning Station', 34.5, 35.5, 2, 2, 1.5, color='#8b6a4a', iid='tan')
for k, y in enumerate((31, 32)): I('g0', 'chest-small', 'Workshop chest', 35.5, y, 1, 1, 1, color='#8a5a2b', iid=f'wc{k}')
# south range: the Alchemist's still room, the gateway, a storehouse
R(wg, 11, 33, 29, 38, 'w')
P.box_walls(wg, 11, 33, 29, 38, S3, 0.5)
R(wg, 18, 33, 22, 38, 'p')                                            # covered gateway, open at both ends
R(wg, 17.5, 33.5, 18, 37.5, S3); R(wg, 22, 33.5, 22.5, 37.5, S3)
O('g0', CD, 14, 33, 16, 33.5); O('g0', WF, 13.5, 37.5, 14.5, 38)     # still room
O('g0', CD, 24.5, 33, 26.5, 33.5); O('g0', WF, 25.5, 37.5, 26.5, 38) # storehouse
I('g0', 'alchemy', 'Alchemy Station', 11.5, 33.5, 2, 2, 1.5, color='#5f7d6e', iid='alch')
I('g0', 'grinding-stones', 'Grinding Stones', 11.5, 35.5, 2, 2, 1, color='#7d8a80', iid='grind')
I('g0', 'npc-alchemist', 'Alchemist (Balthazar)', 14.5, 34.5, 3, 3, 2, color='#56806c', iid='alc')
I('g0', 'chest-small', 'Reagent chest', 16.5, 33.5, 1, 1, 1, color='#8a5a2b', iid='reag')
for k, x in enumerate((22.5, 23.5, 24.5, 25.5)): I('g0', 'chest-small', 'Storehouse chest', x, 36.5, 1, 1, 1, color='#8a5a2b', iid=f'sh{k}')
for k, y in enumerate((34, 35)): I('g0', 'chest-small', 'Storehouse chest', 27.5, y, 1, 1, 1, color='#8a5a2b', iid=f'sh{k + 4}')

# ---- thatch on the workshops (north-south ridges), the south range and the porch; they meet in valleys
wr = P.roof(wrf)
wr.gable(3, 26, 11, 38, 'y', 'thatch', pitch=1.0, overhang=0.5)
wr.gable(29, 26, 37, 38, 'y', 'thatch', pitch=1.0, overhang=0.5)
wr.gable(11, 33, 29, 38, 'x', 'thatch', pitch=1.0, overhang=0.5)
wr.gable(18.25, 25.25, 21.75, 27.25, 'y', 'thatch', pitch=1.0, overhang=0.25)
wr.paint()

# ================================================================= courtyard and garden
R(g0, 19, 27, 21, 33, 'p')                                            # path from the porch to the gateway
R(g0, 11, 30, 29, 32, 'p')                                            # cross path, smithy to workshop doors
R(g0, 29, 16.5, 31, 26, 'd'); R(g0, 29, 25, 29.5, 26, 'd')            # round the house's east end
I('g0', 'tree', 'Apple tree', 13, 27, 2, 2, 7, color='#4f6b34', iid='apple')
I('g0', 'campfire', 'Fire pit', 24.5, 27.5, 2, 2, 1, color='#c46a2a', iid='pit')
I('g0', 'custom', 'Bench', 24.5, 26.5, 2, 0.5, 0.5, color='#7a6653', iid='pb0')
I('g0', 'custom', 'Bench', 27, 27.5, 2, 0.5, 0.5, 90, color='#7a6653', iid='pb1')
for k, x in enumerate((17, 22.5)): I('g0', 'light', 'Lantern', x, 32, 1, 1, 1.5, color='#e3b341', iid=f'gl{k}')
# kitchen garden behind the house, fenced
fence = blk('Rough Wood Block (fence)', 1)
R(g0, 7, 2, 33, 2.5, fence); R(g0, 7, 13, 33, 13.5, fence); R(g0, 7, 2, 7.5, 13.5, fence); R(g0, 32.5, 2, 33, 13.5, fence)
R(g0, 13.5, 2.5, 15.5, 14.5, 'd')                                     # path from the kitchen door
R(g0, 7.5, 7, 32.5, 8.5, 'd'); R(g0, 7, 7, 7.5, 8.5, 'd'); R(g0, 32.5, 7, 33, 8.5, 'd')   # cross path, gates both ends
for (x0, y0, x1, y1) in ((8, 3, 13, 6.5), (8, 9, 13, 12.5), (16, 3, 24, 6.5), (25, 3, 32, 6.5), (25, 9, 32, 12.5)):
    R(g0, x0, y0, x1, y1, 'g')
I('g0', 'seedbed', 'Seedbed', 16.5, 9.5, 2, 2, 0.5, color='#6f8a43', iid='seed')
I('g0', 'npc-farmer', 'Farmer (Emily Fray)', 19, 9.5, 3, 3, 2, color='#7c9a3d', iid='farm')
I('g0', 'chest-small', 'Seed chest', 22.5, 10, 1, 1, 1, color='#8a5a2b', iid='seedc')
I('g0', 'custom', 'Woodpile', 22, 13.5, 3, 1, 1.5, color='#6b4a2e', iid='wood')

# ================================================================= areas
Z('g0', 'Kitchen', 11.5, 15.5, 15.5, 24.5, '#c4501a')
Z('g0', 'Hearth hall', 16, 15.5, 24, 24.5, '#b8862b')
Z('g0', 'Store & stair', 24.5, 15.5, 28.5, 24.5, '#8a5cc2')
Z('g0', 'Courtyard', 11, 25.5, 29, 33, '#2f8f8a')
Z('g0', 'Kitchen garden (Farmer)', 7.5, 2.5, 32.5, 13, '#3f8a4f')
Z('loft', 'Crafters\' beds', 11.5, 15.5, 24.5, 18.5, '#9a7344')
Z('loft', 'Your corner', 25, 15.5, 28.5, 19.5, '#c2416e')
Z('g0', 'Smithy (Blacksmith)', 3.5, 26.5, 11, 37.5, '#5f6770')
Z('g0', 'Room for the Smelter later', 3.5, 34, 8, 37.5, '#8a8f96')
Z('g0', 'Carpenter', 29.5, 26.5, 36.5, 30, '#9a7344')
Z('g0', 'Room for the Table Saw, Spinning Wheel, Loom', 32.5, 30, 35.5, 34.5, '#8a8f96')
Z('g0', 'Hunter', 29.5, 34.5, 36.5, 37.5, '#6d7a45')
Z('g0', 'Still room (Alchemist)', 11.5, 33.5, 17.5, 37.5, '#56806c')
Z('g0', 'Gateway', 18, 33, 22, 38, '#2f8f8a')
Z('g0', 'Storehouse', 22.5, 33.5, 28.5, 37.5, '#8a5cc2')

problems = P.check(outdoor_ok=('g0',), ignore_types=('stairs', 'tree'))
print('item problems:', len(problems))
for p_ in problems: print('  ', p_)

NOTES = """Starter house: a cozy farmstead for your first Flame Altar (level 1, a 40 m build area), drafted by Claude. Uses 0.5 m squares, so every square is one single block. The altar sits in the middle of the hearth hall, at the centre of the build area, and everything fits inside it with room to spare.

WHAT'S WHERE
- The house (18 x 10 m): a thatched timber cottage on a stone footing, with a stone chimney and a little porch.
  - Kitchen (west): the Farmer's Cooking Station, Oven and Kitchen by the chimney, a pantry, and a door to the garden.
  - Hearth hall: the Flame Altar (4 x 4 m) in the middle with 2 m clear all round it, a long table and benches under the north windows, armchairs in the south corners.
  - Store & stair (east): your Workbench and store chests, a side door to the workshop, and the stairs to the loft up the east wall, with a 1 m landing at the foot so you can walk straight on.
  - Sleeping loft: five beds for the first crafters along the north eave, your double bed in the corner, gable windows at both ends.
  - Doors and windows are placed items set in solid walls (each cuts its own opening), real ones made from Springlands materials at the sizes you measured (blocks tall x wide): Wooden Doors (5 x 4), Wooden Window Frames (3 x 2), Round Wooden Window Frames (2 x 2) by the chimney, over the store chests and in the west gable, and a Large Round Wooden Window Frame (6 x 6) high in the east gable over the stair. The windows' tops are level with the doors'.
- Smithy (west of the courtyard): stone, open to the yard. Forge, Charcoal Kiln, Smithing Tools, the Blacksmith, room for the Smelter.
- Workshop (east): timber, with a Round Wooden Door (6 x 6) onto the courtyard. The other outbuildings have Crude Wooden Doors. The Carpenter (Kiln, Masonry Tools) and the Hunter (Drying Rack, Tanning Station), with room for the Table Saw, Spinning Wheel and Loom.
- South range: the Alchemist's still room (Alchemy Station, Grinding Stones), a covered gateway, and a storehouse for bulk stone and wood.
- Courtyard: paths, an apple tree and a fire pit with benches. Kitchen garden behind the house: Farm Soil beds, the Seedbed and the Farmer.

BUILD ORDER (it grows with you)
1. First night: the house shell, the altar, the Workbench and a bed. Rough Wood and Rough Stone are 2 logs or 2 stone per 100 blocks, and thatch is plant fibre.
2. When the Blacksmith joins: the smithy.
3. Carpenter and Hunter: the workshop. Alchemist: the still room. Farmer: the garden (Farm Soil comes from her).
4. Then the gateway, storehouse and courtyard. Upgrade the altar and grow outward.

MATERIALS (all unlock from basic Springlands resources)
- Rough Wood Block: walls, floors, posts, railings, fence.
- Rough Stone Block: footing, chimney, smithy and south range.
- Plant Fiber Roof Block (thatch): every roof.
- Smooth Stone Road Block and Dirt Road Block: paths. Farm Soil: garden beds.
- Upgrades for later: Half-Timbered Block (found in Diadwyn, Revelwood) for the house walls, Stone Shingle Roof Block once you have Flintstone.

CHECK IN GAME
- Recipes and unlocks are from the wiki as of v0.9 (pre-1.0). 1.0 may have changed them, and which survivors you meet first.
- Station footprints are 2 x 2 m placeholders until measured. Beds go to the nearest free survivor (wiki), so set the five in the loft before they arrive.
- Comfort: beds, tables, chairs, lights and the fire all add to it. Add more furniture as you unlock it.
"""
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'starter-house.json')
print('bytes', P.save(out, NOTES, 'r-claude-starter-house-roof45'))
for a, b in P.merged: print('  folded:', a, '->', b)
print('palette', len(set(c for g in P.grids.values() for r in g for c in r) - {' '}))
