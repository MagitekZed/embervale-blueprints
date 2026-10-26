"""Laketown: the smithy, 0.5 m detail plan. Pass 3 of 3: review and finishing touches.

The Blacksmith's platform at +4 m, west of the square: a forge hall with a vented monitor roof and a tall
chimney over the forge, a furnace shed for the charcoal kiln, smelter and blast furnace with a brick stack
behind each, a work yard between them, an open-fronted ore and fuel store in three bays, fuel bunkers, the
Blacksmith's cottage, and a cobbled lane from the walkway stair into the yard. The west landing beside it
carries the west stair up to the manor and takes the tavern's side stair; a short stair climbs north to the
villagers' quarter.
Pass 1 laid out the bones; pass 2 adds the detail: a stone parapet round the deck with lamp piers at the
lane, rim beams, windows (high ones in the forge hall), brick quoins, the forge's hood, a hanging sign,
beams along the open fronts, chimney caps, the store's bays and chests, the cottage's windows, window boxes,
gable window, door hood and furniture, braziers, lanterns, ridge caps. Pass 3 reviewed it all: a hood over
the forge hall's double door, a round window in the east gable over the archway (facing the landing and the
manor stair), the side stair's railing clear of the west stair's flank, and the connections set down for the
neighbouring blueprints.

Coordinates are the layout's (doc `laketown`): this plan's corner is the layout's (10, 32).
Run: python laketown_smithy.py  ->  writes laketown_smithy.json
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laketown_common import Area, WOOD, STONE

BRICK, RCS, TAR = '#aa7657', '#62605d', '#5d5652'
A = Area('Laketown: smithy (detail)', 10, 32, 48, 48, {
    'b': {'name': 'Fired Bricks Block', 'kind': 'floor', 'color': BRICK},              # the smithy's paving
    'k': {'name': 'Roughly Cut Stone Block', 'kind': 'floor', 'color': RCS},           # its edge
    'c': {'name': 'Field Stones', 'kind': 'floor', 'color': '#8a8170'},                # the cobbled lane
    'S': {'name': 'Roughly Cut Stone Block', 'kind': 'wall', 'color': RCS, 'height': 5},   # the forge hall
    'Q': {'name': 'Roughly Cut Stone Block', 'kind': 'wall', 'color': RCS},            # the cottage, ground floor
    'F': {'name': 'Fired Bricks Block', 'kind': 'wall', 'color': BRICK},               # the furnace shed
    'W': {'name': 'Tarred Wood Block', 'kind': 'wall', 'color': TAR},                  # the ore and fuel store
    'T': {'name': 'Half-Timbered Block', 'kind': 'wall', 'color': '#71665e'},          # the cottage, upper floor
    'G': {'name': 'Half-Timbered Block (gable, 5 m)', 'kind': 'wall', 'color': '#71665e', 'height': 5},
    'Z': {'name': 'Fired Bricks Block (quoin)', 'kind': 'wall', 'color': BRICK, 'height': 5},
    'C': {'name': 'Fired Bricks Block (chimney)', 'kind': 'wall', 'color': BRICK, 'height': 14},
    'E': {'name': 'Fired Bricks Block (chimney)', 'kind': 'wall', 'color': BRICK, 'height': 12},
    'H': {'name': 'Fired Bricks Block (furnace stack)', 'kind': 'wall', 'color': BRICK, 'height': 9},
    'n': {'name': 'Refined Wood Block (post)', 'kind': 'block', 'color': WOOD, 'height': 4},
    'K': {'name': 'Roughly Cut Stone Block (bunker wall)', 'kind': 'block', 'color': RCS, 'height': 1.5},
    'p': {'name': 'Roughly Cut Stone Block (parapet)', 'kind': 'block', 'color': RCS, 'height': 1},
    'o': {'name': 'Roughly Cut Stone Block (pier)', 'kind': 'block', 'color': RCS, 'height': 1.5},
    'O': {'name': 'Fancy Stone Block (lamp pier)', 'kind': 'block', 'color': STONE, 'height': 2},
    'l': {'name': 'Yellow Luminescent Block (lamp)', 'kind': 'block', 'color': '#bd9a5f', 'height': 0.5},
    'x': {'name': 'Refined Wood Block (window box)', 'kind': 'block', 'color': WOOD, 'height': 0.5, 'base': 0.5},
    '5': {'name': 'Fired Bricks Block (chimney cap)', 'kind': 'block', 'color': BRICK, 'height': 0.5},
    '6': {'name': 'Fired Bricks Block (chimney cap)', 'kind': 'block', 'color': BRICK, 'height': 0.5, 'base': 3},
    '7': {'name': 'Fired Bricks Block (chimney cap)', 'kind': 'block', 'color': BRICK, 'height': 0.5, 'base': 5},
})
P, R, zone, put = A.P, A.R, A.zone, A.put
stl = A.level('stilts', 'Stilts, standing on the lake bed (-4 m)', -4, 12)
lake = A.level('lake', 'Lake (water level, 0 m)', 0, 1)
walk = A.level('walk', 'West walkway and the stair up (+3 m)', 3, 4)
mid = A.level('mid', 'Smithy deck and west landing (+4 m)', 4, 4)
up5 = A.level('up5', "Villagers' quarter, its edge (+5 m)", 5, 4)
lamp6 = A.level('lamp6', 'Lamps on the piers and flanks (+6 m)', 6, 1)
hood = A.level('hood', "Cottage: the door hood (+6.5 m)", 6.5, 2)
hood75 = A.level('hood75', 'Forge hall: the door hood (+7.5 m)', 7.5, 2)
cot8 = A.level('cot8', "Blacksmith's cottage, upper floor (+8 m)", 8, 3)
roof8 = A.level('roof8', 'Furnace shed and store roofs (+8 m)', 8, 4)
mnr = A.level('manor', 'Manor grounds, their edge (+8 m)', 8, 5)
forge9 = A.level('forge9', 'Forge hall roof (+9 m)', 9, 6)
lamp9 = A.level('lamp9', 'Lamps on the west stair flanks (+9 m)', 9, 1)
cot11 = A.level('cot11', "Blacksmith's cottage roof (+11 m)", 11, 5)
caps = A.level('caps', 'Chimney caps (+12.5 m)', 12.5, 6)
monitor = A.level('monitor', 'Forge hall: the vented monitor roof (+14.5 m)', 14.5, 3)

# ================================================================= the lake (bed 4 m down)
P.ground_rect(0, 0, 48, 48, -4)
R(lake, 10, 32, 58, 80, '~')

# ================================================================= the smithy deck (+4 m)
# 32 x 30 m of fired brick paving on a rough-cut stone edge (the layout's footprint). The forge hall and the
# furnace shed along the north, the work yard across the middle, the store, the cottage and the fuel
# bunkers along the south, and a cobbled lane up the middle from the walkway stair.
A.deck(mid, 12, 40, 44, 70, 'b', 'k')
R(mid, 34, 59, 40, 70, 'c')                             # the lane, from the walkway stair into the work yard
zone('mid', 'Smithy and smelting', 12, 40, 44, 70, '#5f6770')
zone('mid', 'Work yard', 14, 55, 44, 59, '#8a8f96')
zone('mid', 'Smithy lane', 34, 59, 40, 70, '#8a8f96')
# a rough stone parapet round the edge (a 4 m drop to the water), open to the villagers' stair, the lane and
# the west landing; lamp piers either side of the lane's top
A.parapet(mid, 12, 40, 44, 40.5, [(20, 26)]); A.parapet(mid, 12, 40, 12.5, 70)
A.parapet(mid, 12, 69.5, 44, 70, [(34, 40)]); A.parapet(mid, 43.5, 40, 44, 70, [(42, 52), (58, 69)])
for x0 in (33, 40):
    R(mid, x0, 69, x0 + 1, 70, 'O'); R(lamp6, x0, 69, x0 + 1, 70, 'l')
# braziers and an outdoor quench trough along the line between the smelting yard and the work yard (gaps
# either side to walk through)
put('mid', 'Brazier', 32.5, 53.5); put('mid', 'Brazier', 42, 53.5)
put('mid', 'trough', 36.5, 53.5, label='Trough (quenching, outdoors)')
put('mid', 'Ground Lantern II', 25, 58.5)                # where the yard meets the store and the cottage

# ---- the forge hall (Blacksmith): heavy rough-cut stone, 5 m walls with brick quoins, a double door onto the
# work yard, an open archway east to the smelting yard, a back door north to the path from the villagers'
# quarter, high windows all round
A.walls(mid, 14, 44, 30, 55, 'S')
for qx, qy in ((13.5, 43.5), (29.5, 43.5), (13.5, 54.5), (29.5, 54.5)):
    R(mid, qx, qy, qx + 1, qy + 1, 'Z')
A.door('mid', 'Wooden Double Door', 20, 54.5, 24, 55)
A.door('mid', 'Wooden Door', 16, 44, 18, 44.5)
R(mid, 29.5, 48, 30, 52, 'b')                           # the archway: 4 m wide, 3.5 m high, under a lintel
A.overlay(mid, 29.5, 48, 30, 49, 'Roughly Cut Stone Block (lintel)', RCS, 1.5, 3.5, kind='wall')
A.overlay(mid, 29.5, 51, 30, 52, 'Roughly Cut Stone Block (lintel)', RCS, 1.5, 3.5, kind='wall')
A.overlay(mid, 29.5, 49, 30, 51, 'Roughly Cut Stone Block (lintel, gable)', RCS, 4.5, 3.5, kind='wall')   # up into the gable
A.win('mid', 'Round Wooden Window Frame', 29.5, 49.5, 30, 50.5, 5.5)      # high in the east gable, over the archway
for x in (20, 23):
    A.win('mid', 'Wooden Window Frame', x, 44, x + 1, 44.5, 2.5)          # north
for y in (47.5, 51.5):
    A.win('mid', 'Wooden Window Frame', 14, y, 14.5, y + 1, 2.5)          # west, over the chests
for x in (16, 27):
    A.win('mid', 'Wooden Window Frame', x, 54.5, x + 1, 55, 2.5)          # south, either side of the door
for y in (45, 53):
    A.win('mid', 'Wooden Window Frame', 29.5, y, 30, y + 1, 2.5)          # east, either side of the archway
R(mid, 26, 43, 28, 44.5, 'C')                           # the forge's chimney, through the north wall
R(mid, 25.5, 44.5, 28.5, 47.5, 'k')                     # a stone hearth apron round the forge
A.overlay(mid, 26, 44.5, 28, 45.5, 'Fired Bricks Block (forge hood)', BRICK, 2.5, 2.5, kind='wall')   # the hood over the forge, up to the chimney
put('mid', 'forge', 26, 44.5)                           # under its hood and chimney
put('mid', 'smithing-tools', 22, 48)
put('mid', 'npc-blacksmith', 17, 46, label='Blacksmith (Oswald Anders)')
put('mid', 'trough', 26, 49.5, label='Trough (quenching)')
for y in (47, 49.5, 52):
    put('mid', 'chest-large', 14.5, y, 270)             # bars, tools and finished work along the west wall
put('mid', 'Sword and Shield Rack', 15.5, 54, 180); put('mid', 'Two-Handed Melee Weapon Rack', 25, 54, 180)
put('mid', 'Hanging Lantern', 20.5, 50.5); put('mid', 'Hanging Lantern', 25.5, 51.5)
put('mid', 'Wall Lantern', 19, 55, 0, 2.0); put('mid', 'Wall Lantern', 24.5, 55, 0, 2.0)
fh = A.roof(hood75)                                     # a tarred shingle hood over the double door, on brackets
fh.shed(19.5, 55, 24.5, 56, 'n', 'lead', pitch=1.0, overhang=0)
fh.paint()
for x in (19.5, 24):
    A.overlay(mid, x, 55, x + 0.5, 55.5, 'Refined Wood Block (bracket)', WOOD, 0.5, 3.5)
put('mid', 'Wall Lantern', 15, 43.5, 180, 2.0)       # by the back door
# its sign, on a bracket from the east wall over the way in from the landing
A.overlay(mid, 30, 47, 30.5, 47.5, 'Refined Wood Block (sign bracket)', WOOD, 0.5, 4)
A.overlay(mid, 30.5, 47, 31.5, 47.5, 'Tarred Wood Block (sign board)', TAR, 2, 2.5)
zone('mid', 'Forge hall (Blacksmith)', 14, 44, 30, 55, '#5f6770')

# ---- the furnace shed: a brick back wall and ends, open to the yard on the south under a timber beam, the
# three furnaces in a row, each with a brick stack behind it rising through the roof
R(mid, 32.5, 42.5, 42.5, 47, 'k')                      # rough stone flooring under the furnaces
R(mid, 32, 42, 43, 42.5, 'F'); R(mid, 32, 42.5, 32.5, 47, 'F'); R(mid, 42.5, 42.5, 43, 47, 'F')
R(mid, 37.5, 46.5, 38, 47, 'n')                         # a post mid-front
A.overlay(mid, 32.5, 46.5, 37.5, 47, 'Refined Wood Block (beam)', WOOD, 0.5, 3.5)
A.overlay(mid, 38, 46.5, 42.5, 47, 'Refined Wood Block (beam)', WOOD, 0.5, 3.5)
STACKS = ((33.5, 34.5), (37, 38), (40.5, 41.5))
for x0, x1 in STACKS:
    R(mid, x0, 41.5, x1, 42.5, 'H')
put('mid', 'charcoal-kiln', 33, 43); put('mid', 'smelter', 36.5, 43); put('mid', 'blast-furnace', 40, 43)
put('mid', 'Hanging Lantern', 37.5, 45)
zone('mid', 'Furnace shed (charcoal kiln, smelter, blast furnace)', 32, 42, 43, 47, '#8a8f96')
zone('mid', 'Smelting yard', 32, 47, 44, 55, '#8a8f96')

# ---- the ore and fuel store: a tarred wood shed open to the work yard on the north under a beam, in three
# bays (ore, bars and metal, coal and charcoal), each with a large chest at the back
R(mid, 14, 59.5, 14.5, 68, 'W'); R(mid, 24.5, 59.5, 25, 68, 'W'); R(mid, 14.5, 67.5, 24.5, 68, 'W')
for x in (17.5, 21):
    R(mid, x, 59.5, x + 0.5, 60, 'n')                   # the front posts
    R(mid, x, 60, x + 0.5, 67.5, 'W')                   # and the partitions behind them
for (x0, x1) in ((14.5, 17.5), (18, 21), (21.5, 24.5)):
    A.overlay(mid, x0, 59.5, x1, 60, 'Refined Wood Block (beam)', WOOD, 0.5, 3.5)
BAYS = (('Ore bay', 14.5, 17.5, 'Resource Bundle II'), ('Bars and metal', 18, 21, 'Supply Sacks I'), ('Coal and charcoal', 21.5, 24.5, 'Supply Sacks II'))
for label, x0, x1, deco in BAYS:
    put('mid', 'chest-large', x0 + 0.5, 66.5, 180)
    put('mid', deco, x0 + 1, 64)
    zone('mid', label, x0, 60, x1, 67.5, '#8a8f96')
zone('mid', 'Ore and fuel store', 14, 59.5, 25, 68, '#8a8f96')

# ---- the fuel bunkers: rough stone bins open to the lane, for logs, coal and charcoal
R(mid, 43.5, 58, 44, 69, 'K')
for y in (58, 61.5, 65, 68.5):
    R(mid, 40.5, y, 44, y + 0.5, 'K')
for y, deco in ((59.5, 'Resource Bundle I'), (63, 'Supply Sacks II'), (66.5, 'Supply Sacks I')):
    put('mid', deco, 42, y)
zone('mid', 'Fuel bunkers (logs, coal, charcoal)', 40.5, 58, 44, 69, '#8a8f96')

# ---- the Blacksmith's cottage: rough stone below, half-timbered above, the door onto the lane under a hood,
# a stair up along the west wall, a hearth on the south wall under its chimney, a gable window to the north
A.walls(mid, 26, 59.5, 33, 68, 'Q', 'r')
A.door('mid', 'Wooden Door', 32.5, 62, 33, 64)
A.stairs('mid', 'Cottage stair up', 26.5, 62, 28, 66, 4, 'N')
R(mid, 29, 67.5, 30, 69, 'E')
A.win('mid', 'Wooden Window Frame', 30, 59.5, 31, 60)                      # north, onto the work yard
A.win('mid', 'Wooden Window Frame', 26, 60.5, 26.5, 61.5)                  # west
A.win('mid', 'Wooden Window Frame', 31, 67.5, 32, 68)                      # south
A.win('mid', 'Wooden Window Frame', 32.5, 65.5, 33, 66.5)                  # east, onto the lane
put('mid', 'Fireplace', 28.5, 66.5, 180)
put('mid', 'Wooden Side Table', 29, 63); put('mid', 'Rustic Chair', 29, 64, 180); put('mid', 'Rustic Chair', 30, 63, 90)
put('mid', 'chest-small', 31.5, 60, 180)
put('mid', 'Hanging Lantern', 29.5, 63.5)
put('mid', 'Wall Lantern', 33, 64.5, 270, 2.0)
dh = A.roof(hood)                                       # the door hood, on two brackets
dh.shed(33, 61.5, 34, 64.5, 'w', 'tiles', pitch=1.0, overhang=0)
dh.paint()
for y in (61.5, 64):
    A.overlay(mid, 33, y, 33.5, y + 0.5, 'Refined Wood Block (bracket)', WOOD, 0.5, 2.5)
A.walls(cot8, 26, 59.5, 33, 68, 'T', 'r')
R(cot8, 29, 67.5, 30, 68, ' ')                          # the chimney passes up through the wall
R(cot8, 26.5, 62, 28, 66, ' ')                          # the stairwell
R(cot8, 28, 62, 28.5, 66.5, 'i'); R(cot8, 26.5, 66, 28, 66.5, 'i')
R(cot8, 29, 59.5, 30, 60, 'G')                          # the north gable's middle rises for a round window
A.win('cot8', 'Round Wooden Window Frame', 29, 59.5, 30, 60, 3.5)
COT_WIN = [(29, 59.5, 'N'), (32.5, 60.5, 'E'), (32.5, 65.5, 'E'), (31, 67.5, 'S')]   # (none west: the store's roof is 0.5 m off that wall)
for (x, y, side) in COT_WIN:                            # upper windows, each with a window box outside
    if side in 'WE':
        A.win('cot8', 'Wooden Window Frame', x, y, x + 0.5, y + 1)
        bx = x - 0.5 if side == 'W' else x + 0.5
        R(cot8, bx, y, bx + 0.5, y + 1, 'x')
    else:
        A.win('cot8', 'Wooden Window Frame', x, y, x + 1, y + 0.5)
        by = y - 0.5 if side == 'N' else y + 0.5
        R(cot8, x, by, x + 1, by + 0.5, 'x')
put('cot8', 'bed', 30.5, 64); put('cot8', 'chest-small', 31.5, 60, 180)
put('cot8', 'Hanging Lantern', 30, 62.5, z=2.5)
zone('mid', "Blacksmith's cottage", 26, 59.5, 33, 68, '#9c6b8e')
zone('cot8', "Blacksmith's room", 26.5, 60, 32.5, 67.5, '#9c6b8e')
put('mid', 'Rustic Bench', 25, 55, 0)                   # in the work yard, against the forge hall

# ================================================================= the west landing and the west stair to the manor
# Rough wood at +4 m, joined to the smithy's east edge. The west stair climbs 4 m north to the manor's west
# garden between stepped stone flanks (as the grand stair does), lamps on their ends; the tavern's side
# stair comes down onto the landing by its foot.
R(mid, 44, 42, 56, 52, 'w')
A.stairs('mid', 'West stair to the manor', 50, 42, 56, 50, 4, 'N')
A.flanks(mid, 50, 42, 56, 50, 'N')
for x in (49.5, 56):
    R(lamp6, x, 49.5, x + 0.5, 50, 'l'); R(lamp9, x, 42, x + 0.5, 42.5, 'l')
A.rail(mid, 48, 41.5, 49.5, 42); A.rail(mid, 44, 52, 56, 52.5)    # (open at x 44..48 for the quarter's back steps)
put('mid', 'Bench', 46, 51.5, 180); put('mid', 'Ground Lantern II', 44.5, 51)
zone('mid', 'West landing', 44, 42, 56, 52, '#2f8f8a')
# the villagers' quarter's back steps, coming down onto the landing's north-west corner (its blueprint)
R(up5, 44, 32, 48, 39, 'w'); R(mid, 44, 39, 48, 42, 'w')
A.stairs('mid', "Back steps down to the west landing (villagers' quarter blueprint)", 45, 39, 47, 41, 1, 'N')
A.cheeks(mid, 45, 39, 47, 41, 'N')
# the tavern's side stair (the square blueprint has it)
R(mid, 56, 50, 58, 52, 'w')
A.stairs('mid', 'Side stair: tavern to the west landing (square blueprint)', 56, 50, 58, 52, 1, 'E')
A.rail(mid, 56.5, 49.5, 58, 50); A.rail(mid, 56, 52, 58, 52.5)    # (clear of the flank at x 56 to 56.5)

# ================================================================= north: up to the villagers' quarter (+5 m)
R(mid, 20, 34, 26, 40, 'w')
A.stairs('mid', "Stairs up to the villagers' quarter", 20, 34, 26, 36, 1, 'N')
A.cheeks(mid, 20, 34, 26, 36, 'N')
A.rail(mid, 19.5, 36, 20, 40); A.rail(mid, 26, 36, 26.5, 40)
put('mid', 'Ground Lantern II', 20, 38.5)
R(up5, 10, 32, 42, 34, 't'); R(up5, 10, 32, 41, 33, 'r')      # the villagers' quarter's south edge (its own blueprint)
zone('up5', "Villagers' quarter (its own blueprint)", 10, 32, 42, 34, '#9c6b8e')

# ================================================================= south: down to the west walkway (+3 m)
R(walk, 34, 70, 40, 77, 'w')
A.stairs('walk', 'Stairs up to the smithy', 34, 70, 40, 72, 1, 'N')
A.cheeks(walk, 34, 70, 40, 72, 'N')
R(walk, 34, 77, 58, 80, 'w')                            # the west walkway (its own blueprint)
A.rail(walk, 33.5, 72, 34, 80); A.rail(walk, 40, 72, 40.5, 77); A.rail(walk, 40, 76.5, 58, 77)
zone('walk', 'West walkway (walkway blueprint)', 34, 77, 58, 80, '#2f8f8a')

# ================================================================= the manor's west garden edge (+8 m, its own blueprint)
R(mnr, 50, 32, 58, 42, 'P'); R(mnr, 50, 32, 51, 42, 'f'); R(mnr, 50, 41, 58, 42, 'f'); R(mnr, 52, 32, 58, 40, 'G')
zone('manor', 'Manor grounds, west garden (manor blueprint)', 50, 32, 58, 42, '#8a5cc2')

# ================================================================= roofs, at 45 degrees (or 1 in 2) in even steps
# the forge hall: a dark tarred shingle gable (ridge east-west) cut off flat at 4 m, with a vented monitor
# roof along the flat on posts (1.5 m of open vent under it for the forge's heat and smoke)
rf = A.roof(forge9)
rf.gable(14, 44, 30, 55, 'x', 'lead', pitch=1.0, overhang=0.5, ridge_h=4.0)
rf.cut(26, 43, 28, 44.5)
rf.paint()
for x in (16, 22, 27.5):
    for y in (47.5, 51):
        A.overlay(forge9, x, y, x + 0.5, y + 0.5, 'Refined Wood Block (vent post)', WOOD, 1.5, 4.0)
rm = A.roof(monitor)
rm.gable(16, 47.5, 28, 51.5, 'x', 'lead', pitch=1.0, overhang=0.5)
rm.caps('shingle', min_lower=1)                         # a stone ridge
rm.paint()
# the furnace shed: a stone shingle shed roof rising to the back wall, 1 in 2; the store: a tarred shingle
# gable, 1 in 2
rs = A.roof(roof8)
rs.shed(32, 42, 43, 47, 'n', 'shingle', pitch=0.5, overhang=0.5)
for x0, x1 in STACKS:
    rs.cut(x0, 41.5, x1, 42.5)
rs.gable(14, 59.5, 25, 68, 'x', 'lead', pitch=0.5, overhang=0.5)
rs.paint()
# the cottage: a steep tiled gable, ridge north-south, a dark ridge
rc = A.roof(cot11)
rc.gable(26, 59.5, 33, 68, 'y', 'tiles', pitch=1.0, overhang=0.5)
rc.caps('lead', min_lower=1)
rc.cut(29, 67.5, 30, 69)
rc.paint()
# chimney caps: a course 0.5 m proud all round the top of each stack
for x0, x1 in STACKS:
    A.ring(caps, x0, 41.5, x1, 42.5, '5')               # the furnace stacks (tops at 13 m)
A.ring(caps, 29, 67.5, 30, 69, '6')                     # the cottage (16 m)
A.ring(caps, 26, 43, 28, 44.5, '7')                     # the forge (18 m)

# ================================================================= stilts, rim beams and checks
print('stilts:', A.stilts(stl, [('walk', 3), ('mid', 4), ('up5', 5), ('manor', 8)]))
own = lambda x, y: (12 <= x < 44 and 34 <= y < 77) or (44 <= x < 56.5 and 41.5 <= y < 52.5)
print('rim beam squares:', A.rim_beams(stl, [('walk', 3), ('mid', 4)], own))
A.spawn('mid', 36.5, 56.5, 90)                                 # walk mode starts here: the top of the lane at the work yard, facing the forge hall, the store and the cottage
A.checks()

NOTES = """Laketown: the smithy, as a 0.5 m detail blueprint (all three passes done). Drafted by Claude.
This plan's corner is the layout's (10, 32), so it lines up with the Laketown layout and stamps back into the site plan there.

PASSES
1. Design and bones: the deck, building shells with walls, doors, stairs and roof shapes, the stations, the connections, stilts, labels.
2. Details: windows, trim, parapets, lights, furniture, storage, the store's bays.
3. Review and finishing touches (this one).

PASS 3: WHAT THE REVIEW FOUND AND CHANGED
- The tavern's side stair railing started on the same square as the foot of the west stair's east flank, cutting the flank short and leaving its lamp floating. The railing now starts past the flank (in the square blueprint too).
- The forge hall's south front, the one you walk up to from the lane, was plain: a tarred shingle hood on brackets over the double door.
- The forge hall's east gable faces everyone coming off the landing and down the manor stair, and was blank: the archway's lintel rises into the gable in the middle, with a round window in it.
- The layout's labels showed the old arrangement (the cottage in front of the walkway stair): updated to match.
- Checked, all clear (check_access): nothing in front of any door or window, no door onto a drop, every stair with 1 m clear at the foot and top and 2 m of headroom.

CONNECTIONS (for the neighbouring blueprints to match)
- The lane, the walkway stair and its strip (x 34..40) line up with the carpentry branch south of the west walkway (also x 34..40): one straight run from the smithy to the carpentry. The carpentry blueprint should keep its branch on that line.
- Villagers' quarter (+5 m): the stair arrives at x 20..26 on its south edge (y 33..34), at the quarter's gateway between the pair and Kaori's cottage. The quarter keeps that strip clear as its landing.
- Manor (+8 m): the west stair arrives at x 50..56 on the west garden's south edge (y 40..42), between flanks standing 1 m above the deck with lamps on top. Keep 50..56 x 40..42 clear and the lawn and beds back from it.
- West landing (+4 m): the tavern's side stair (x 56..58, y 50..52) lands beside the foot of the west stair.
- West landing (+4 m): the villagers' quarter's back steps (x 44..48) come down onto its north-west corner; the railing there is open for them, and the bench moved to the south rail.
- West walkway (+3 m): the smithy's strip joins it at x 34..40, y 77; the walkway's style (6 m of rough wood, rails just outside the edges) carries on.


THE SMITHY (+4 m, 32 x 30 m): fired brick paving on a rough-cut stone edge, a rough stone parapet with piers round it (open to the villagers' stair, the lane and the west landing), lamp piers either side of the lane's top, rim beams under the edges.
- Forge hall (Blacksmith, Oswald Anders), NW: rough-cut stone, 5 m walls with fired brick quoins. A Wooden Double Door onto the work yard under a tarred shingle hood on brackets (wall lanterns either side), an open archway (4 m wide, 3.5 m high) east to the smelting yard with the smithy's sign hanging beside it and a round window above it in the gable, a back door north. High windows all round (sills 2.5 m up, clear of the racks and chests).
  - Inside: the Forge under a brick hood and chimney on the north wall, the Smithing Tools, the Blacksmith's work area, a quenching trough, three large chests along the west wall, weapon racks by the door, lanterns.
  - Roof: a dark tarred shingle gable at 45 degrees, cut off flat at 4 m, with a vented monitor roof along the top on posts (1.5 m open under it) with a stone ridge, and the forge chimney rising past it.
- Furnace shed, NE: a fired brick back wall and ends, open to the yard under a timber beam. The Charcoal Kiln, Smelter and Blast Furnace in a row, each with a brick stack behind it through a stone shingle shed roof (1 in 2). Capped stacks; a lantern.
- Work and smelting yards: a line of braziers and an outdoor quench trough between them (gaps to walk through), a bench against the forge hall, a lantern where the yard meets the store and cottage.
- Rough stone underfoot where the fire is: under the furnace shed and a hearth apron round the forge.
- Ore and fuel store, SW: a tarred wood shed open to the yard under a beam, in three bays (ore; bars and metal; coal and charcoal), each with a large chest at the back. Tarred shingle gable, 1 in 2.
- Blacksmith's cottage: rough stone below, half-timbered above, a steep tiled gable with a dark ridge.
  - Ground floor: the door onto the lane under a tiled hood on brackets (a lantern by it), a fireplace under the chimney, a table and chairs, a chest, the stair up.
  - Upper floor: the bed, a chest, windows with window boxes, and a round window high in the north gable.
- Fuel bunkers: rough stone bins (1.5 m) open to the lane, stocked with logs, coal and charcoal.
- The smithy lane (field stones) runs from the walkway stair straight into the work yard.
  - Change from the layout: the layout had the cottage right in front of the walkway stair. It moved west, between the store and the lane.

CONNECTIONS
- South: the stair up from the west walkway (6 m wide, cheek walls), its strip and the walkway itself in the walkway's style; lamp piers at the top.
- East: the west landing (rough wood, a bench and a lantern), with the west stair up to the manor's west garden (8 m run, 4 m up, stepped stone flanks with lamps at both ends) and the tavern's side stair coming down by its foot.
- North: a short stair up to the villagers' quarter (+5 m), with cheek walls, railings and a lantern.

STATIONS (1.0, Blacksmith; 2 x 2 m placeholders until measured): Forge, Smithing Tools, Charcoal Kiln, Smelter, Blast Furnace. Furniture and light sizes are estimates until measured.

STILTS: 1 m posts on the layout's 4 m grid, from the lake bed 4 m down to each deck's underside.
"""
A.save('laketown_smithy.json', NOTES, 'r-claude-laketown-smithy-3d')
