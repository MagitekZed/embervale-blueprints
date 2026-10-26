"""Laketown: the manor, 0.5 m detail plan. Pass 3 of 3: review and finishing touches.

The manor grounds at +8 m, north of the square, on the village's main axis (gatehouse, causeway, altar, grand
stair). The house is limestone with castle slate roofs, eaves at +17 m, dressed in Fancy Stone:
- the centre block (two storeys): a double-height front hall with twin stairs up to a balcony landing, a
  great room behind it joining the wings, two guest rooms upstairs; a giant-order portico with an oculus in
  its pediment; a pyramid roof with a cupola (a lantern glowing in it) on top, the highest point;
- the west wing: the Collector's gallery, one tall hall (9 m) with clerestory windows and a great round
  window in its front gable;
- the east wing (two storeys): the dining room and parlour below, the master bedroom and study above, a great
  round window in its front gable;
- two towers flanking the wings, three storeys with belvederes on top and stone spiral stairs inside.
Pass 1 laid out the bones (and the portico); pass 2 reshaped the wings (front gables) and added the towers,
then the detail: tall windows, a base course with sills, window and door hoods, a string course, quoins,
stone cornices and ridges, four capped chimneys, finials, the gardens (beds, paths, topiary), a fountain on
the terrace, lights, and the furniture: the Collector's showcases and mannequins, fireplaces, the dining
table, beds. Pass 3 reviewed it all: a master bath in the east tower off the master bedroom, the farm's
service route marked in gravel the whole way, red banners on the towers and a flag on the cupola.

Coordinates are the layout's (doc `laketown`): this plan's corner is the layout's (48, 4).
Run: python laketown_manor.py  ->  writes laketown_manor.json
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laketown_common import Area, STONE, WOOD, TALL

LIME = '#a79a88'
A = Area('Laketown: manor (detail)', 48, 4, 70, 46, {
    'L': {'name': 'Limestone Road Block', 'kind': 'floor', 'color': '#a38b79'},       # paths, the promenade (square)
    'M': {'name': 'Limestone Block', 'kind': 'wall', 'color': LIME},                    # the house
    'N': {'name': 'Limestone Block', 'kind': 'wall', 'color': LIME, 'height': 9},       # the gallery, full height
    'g': {'name': 'Limestone Block (gable)', 'kind': 'wall', 'color': LIME, 'height': 13.5},   # the gallery's front gable
    'j': {'name': 'Limestone Block (gable)', 'kind': 'wall', 'color': LIME, 'height': 8.5},    # the east wing's, upstairs
    'J': {'name': 'Limestone Block (chimney)', 'kind': 'wall', 'color': LIME, 'height': 18},
    'b': {'name': 'Fancy Stone Block (balustrade)', 'kind': 'block', 'color': STONE, 'height': 1},
    'o': {'name': 'Fancy Stone Block (pier)', 'kind': 'block', 'color': STONE, 'height': 1.5},
    'X': {'name': 'Fancy Stone Block (column)', 'kind': 'block', 'color': STONE, 'height': 9},
    'q': {'name': 'Fancy Stone Block (quoin)', 'kind': 'wall', 'color': STONE, 'height': 9},
    'Q': {'name': 'Fancy Stone Block (quoin)', 'kind': 'wall', 'color': STONE, 'height': 13},
    'p': {'name': 'Fancy Stone Block (base course)', 'kind': 'block', 'color': STONE, 'height': 0.5},
    's': {'name': 'Fancy Stone Block (sill)', 'kind': 'block', 'color': STONE, 'height': 1},
    'c': {'name': 'Fancy Stone Block (string course)', 'kind': 'block', 'color': STONE, 'height': 0.5},
    '6': {'name': 'Fancy Stone Block (chimney cap)', 'kind': 'block', 'color': STONE, 'height': 0.5, 'base': 1.5},
    'k': {'name': 'Fancy Stone Block (kerb)', 'kind': 'block', 'color': STONE, 'height': 0.5},
    'R': {'name': 'Fancy Stone Block (basin rim)', 'kind': 'block', 'color': STONE, 'height': 0.5},
    'U': {'name': 'Fancy Stone Block (fountain)', 'kind': 'block', 'color': STONE, 'height': 1.5},
    'F': {'name': 'Flower Soil (bed)', 'kind': 'block', 'color': '#a77e63', 'height': 0.5},
    'Y': {'name': 'Foliage (shrubs)', 'kind': 'block', 'color': '#668f27', 'height': 1},
    'T': {'name': 'Foliage (topiary)', 'kind': 'block', 'color': '#668f27', 'height': 1.5},
    'l': {'name': 'Yellow Luminescent Block (lamp)', 'kind': 'block', 'color': '#bd9a5f', 'height': 0.5},
    'V': {'name': 'Red Carpet Block (banner)', 'kind': 'block', 'color': '#9e3742', 'height': 3},
    'W': {'name': 'Red Carpet Block (flag)', 'kind': 'block', 'color': '#9e3742', 'height': 1.5, 'base': 2.5},
    'Z': {'name': 'Refined Wood Block (flagpole)', 'kind': 'block', 'color': WOOD, 'height': 4},
    'E': {'name': 'Fancy Stone Block (quoin)', 'kind': 'wall', 'color': STONE, 'height': 17},       # the clock tower's
    'D': {'name': 'Fancy Stone Block (pavilion column)', 'kind': 'block', 'color': STONE, 'height': 3},
    'h': {'name': 'Fired Bricks Block (chimney pot)', 'kind': 'block', 'color': '#aa7657', 'height': 1, 'base': 2},
})
P, R, zone, put = A.P, A.R, A.zone, A.put
stl = A.level('stilts', 'Stilts, standing on the lake bed (-4 m)', -4, 12)
lake = A.level('lake', 'Lake (water level, 0 m)', 0, 1)
mid = A.level('mid', 'The square and smithy stairs, their tops (+4 m)', 4, 4)
up5 = A.level('up5', "The farm's service stair (+5 m)", 5, 4)
lamp6 = A.level('lamp6', 'Lamps on the stair flanks (+6 m)', 6, 1)
mnr = A.level('manor', 'Manor grounds and ground floor (+8 m)', 8, 5)
mtrim = A.level('mtrim', 'Manor: base course and sills (+8 m)', 8, 1)
ts8 = A.level('ts8', 'Towers: spiral stairs, ground floor (+8 m)', 8, 5.5)
lamp9 = A.level('lamp9', 'Lamps on the stair flanks (+9 m)', 9, 1)
lamp95 = A.level('lamp95', 'The fountain lamp (+9.5 m)', 9.5, 1)
banner = A.level('banner', 'Towers: their banners (+13.5 m)', 13.5, 3.5)
mup = A.level('mup', 'Manor house, upper floor (+13 m)', 13, 4)
ts13 = A.level('ts13', 'Towers: spiral stairs, first floor (+13 m)', 13, 4.5)
pav = A.level('pav', 'West garden: the pavilion roof (+11 m)', 11, 4)
mtop = A.level('mtop', 'Towers: the belvederes (+17 m)', 17, 4)
ctop = A.level('ctop', 'West tower: the clock stage (+21 m)', 21, 4)
mroof = A.level('mroof', 'Manor house roofs (+17 m)', 17, 8)
troof = A.level('troof', 'East tower roof (+21 m)', 21, 6)
troof2 = A.level('troof2', 'West tower roof, over the clock (+25 m)', 25, 6)
caps = A.level('caps', 'Chimney caps (+24 m)', 24, 3)
cupola = A.level('cupola', 'The cupola (+26 m)', 26, 4)
flag = A.level('flag', 'The flag on the cupola (+29 m)', 29, 5)


# ---- facade helpers (layout metres): the wall squares of a 0.5 m wall whose outer face is `line`, and the
# squares just outside it, for a stretch a0..a1 along it
def wall_sq(side, line, a0, a1):
    return {'S': (a0, line - 0.5, a1, line), 'N': (a0, line, a1, line + 0.5),
            'E': (line - 0.5, a0, line, a1), 'W': (line, a0, line + 0.5, a1)}[side]


def out_sq(side, line, a0, a1):
    return {'S': (a0, line, a1, line + 0.5), 'N': (a0, line - 0.5, a1, line),
            'E': (line, a0, line + 0.5, a1), 'W': (line - 0.5, a0, line, a1)}[side]


def window(kind, side, line, a, w=1):
    """A tall window of two stacked Wooden Window Frames: g = ground floor (9 to 12 m) with a stone sill on the
    base course and a hood over it; u = upper floor (13.5 to 16.5 m) on the string course; c = the gallery's
    clerestory (13.5 to 16.5 m, in its 9 m wall); t = a tower's belvedere (17.5 to 20.5 m)."""
    lid, zs = {'g': ('manor', (1.0, 2.5)), 'u': ('mup', (0.5, 2.0)), 'c': ('manor', (5.5, 7.0)), 't': ('mtop', (0.5, 2.0)),
               'b': ('mup', (1.0,))}[kind]                  # b: a bathroom's small high window
    for z in zs:
        A.win(lid, 'Wooden Window Frame', *wall_sq(side, line, a, a + w), z)
    if kind == 'g':
        R(mtrim, *out_sq(side, line, a, a + w), 's')
        A.overlay(mnr, *out_sq(side, line, a - 0.5, a + w + 0.5), 'Fancy Stone Block (window hood)', STONE, 0.5, 4.0)


def entrance(name, side, line, a0, a1, hood=True):
    """A door in an outside wall: no base course across its threshold, a stone hood over it."""
    A.door('manor', name, *wall_sq(side, line, a0, a1))
    R(mtrim, *out_sq(side, line, a0, a1), ' ')
    if hood:
        A.overlay(mnr, *out_sq(side, line, a0 - 0.5, a1 + 0.5), 'Fancy Stone Block (door hood)', STONE, 0.5, TALL[name])


def quoin(cx, cy, ch):
    """Stone quoins up an outside corner (cx, cy): a 1 m column taking in the wall's corner block."""
    for g in (mtrim, mup, mtop):
        R(g, cx - 0.5, cy - 0.5, cx + 0.5, cy + 0.5, ' ')
    R(mnr, cx - 0.5, cy - 0.5, cx + 0.5, cy + 0.5, ch)


def planter(g, x0, y0, x1, y1, centre='T'):
    """A raised bed: a stone kerb round flower soil, shrubs every other square, a topiary in the middle."""
    R(g, x0, y0, x1, y1, 'k'); R(g, x0 + 0.5, y0 + 0.5, x1 - 0.5, y1 - 0.5, 'F')
    for x, y in P.cells_rect(x0 + 0.5 - A.OX, y0 + 0.5 - A.OY, x1 - 0.5 - A.OX, y1 - 0.5 - A.OY):
        if (x + y) % 2 == 0:
            g[y][x] = 'Y'
    if centre:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        R(g, cx - 0.5, cy - 0.5, cx + 0.5, cy + 0.5, centre)


# ================================================================= the lake (bed 4 m down)
P.ground_rect(0, 0, 70, 46, -4)
R(lake, 48, 4, 118, 50, '~')

# ================================================================= the manor grounds (+8 m)
# The layout's deck: polished stone on a fancy stone edge, 60 x 36 m, with a balustrade round the whole
# edge, open at the three stairs.
A.deck(mnr, 50, 6, 110, 42, 'P', 'f')
R(mnr, 52, 8, 61, 38, 'G'); R(mnr, 99, 8, 108, 38, 'G')      # the west and east gardens' lawns
A.parapet(mnr, 50, 6, 110, 6.5, wall='b', pier='o')          # north
A.parapet(mnr, 50, 6, 50.5, 41, wall='b', pier='o')          # west (clear of the west stair's top)
A.parapet(mnr, 109.5, 6, 110, 42, [(34, 40)], wall='b', pier='o')    # east, open to the service stair
A.parapet(mnr, 56, 41.5, 110, 42, [(76, 84)], wall='b', pier='o')    # south, open to the grand stair
zone('manor', 'Manor grounds', 50, 6, 110, 42, '#8a5cc2')
zone('manor', 'Forecourt', 62, 28, 98, 30, '#b7a3dc')
zone('manor', 'Rear court', 72, 7, 88, 12, '#b7a3dc')

# ---- the front terrace: a fancy stone way along the axis from the grand stair to the portico, a fountain
# on it (a stone basin, a lamp glowing on its pedestal), planters with topiary, benches and lanterns
R(mnr, 78, 31, 82, 41.5, 'f')
A.circle(mnr, 80, 36, 6, 'f')                            # a paved ring round it
A.circle(mnr, 80, 36, 4, 'R'); A.circle(mnr, 80, 36, 3, '~')
R(mnr, 79.5, 35.5, 80.5, 36.5, 'U'); R(lamp95, 79.5, 35.5, 80.5, 36.5, 'l')
for x0 in (64, 70, 88, 94):
    planter(mnr, x0, 33, x0 + 2, 35)
for x in (66, 92):
    put('manor', 'Bench', x, 39.5, 0)
for x in (63, 70.5, 89, 96.5):
    put('manor', 'Ground Lantern II', x, 40)
zone('manor', 'Front terrace (over the square)', 62, 30, 98, 41, '#b7a3dc')

# ---- the gardens: formal beds and gravel paths. West: a path from the gallery's garden door, a path down
# the middle between two long beds, a path from the west tower's door to the terrace, topiary. East, the
# same mirrored, with the service path from the farm's stair to the dining room's door.
R(mnr, 51, 19, 62, 21, 'L'); R(mnr, 56, 13, 57, 19, 'L'); R(mnr, 58, 29, 60, 38, 'L')
planter(mnr, 52.5, 14, 55.5, 18, None); planter(mnr, 57.5, 14, 60.5, 18, None)
# the pavilion: a garden folly at the end of the path, four stone columns on a fancy stone floor under a slate
# pyramid with a finial, a bench and a lantern inside (the west garden's alone: the east one has the service path)
R(mnr, 54, 8, 59, 13, 'f')
for cx, cy in ((54, 8), (58, 8), (54, 12), (58, 12)):
    R(mnr, cx, cy, cx + 1, cy + 1, 'D')
put('manor', 'Rustic Bench', 55.5, 9, 0); put('manor', 'Hanging Lantern', 56, 10.5, z=3.5)
zone('manor', 'Garden pavilion', 54, 8, 59, 13, '#3f8a4f')
for y in (31.5, 35.5):
    R(mnr, 53.5, y, 54.5, y + 1, 'T')
R(mnr, 98, 12, 109, 14, 'L'); R(mnr, 103, 14, 104, 21, 'L'); R(mnr, 100, 29, 102, 38, 'L')
R(mnr, 108, 14, 109, 40, 'L')                          # the service path, up the east edge from the farm's stair
planter(mnr, 99.5, 15, 102.5, 21, None); planter(mnr, 104.5, 15, 107.5, 21, None)
for y in (31.5, 35.5):
    R(mnr, 105.5, y, 106.5, y + 1, 'T')
put('manor', 'Ground Lantern II', 57.5, 21.5); put('manor', 'Ground Lantern II', 102, 14.5)
put('manor', 'Bench', 52.5, 26, 270); put('manor', 'Bench', 107, 26, 90)
zone('manor', 'West garden', 51, 7, 61, 41, '#3f8a4f')
zone('manor', 'East garden', 98, 7, 109, 41, '#3f8a4f')

# ================================================================= the house
# ground floor walls 5 m (+8 to +13), upper floor 4 m (+13 to +17); the gallery is one 9 m hall; the towers
# rise to +21 m
A.walls(mnr, 62, 9, 72.5, 28, 'N')                      # the west wing: the Collector's gallery
A.walls(mnr, 72, 12, 88, 28, 'M')                       # the centre block
A.walls(mnr, 87.5, 9, 98, 28, 'M')                      # the east wing
for (x0, x1) in ((55.5, 62.5), (97.5, 104.5)):          # the towers, flanking the wings (1 m proud of the front)
    A.walls(mnr, x0, 22, x1, 29, 'M')
    A.walls(mup, x0, 22, x1, 29, 'M')
    A.walls(mtop, x0, 22, x1, 29, 'M')
R(mnr, 66, 27.5, 69, 28, 'g')                           # the gallery's front gable rises over its door
# ---- the centre block, ground floor: the front hall (double height, twin stairs) and the great room behind
R(mnr, 75.5, 28, 84.5, 31.5, 'f')                       # the portico's floor
A.door('manor', 'Wooden Double Door', 78, 27.5, 82, 28)              # the front door, on the axis
R(mnr, 72.5, 18.5, 87.5, 19, 'M')                                    # front hall | great room
A.door('manor', 'Wooden Double Door', 78, 18.5, 82, 19)
A.stairs('manor', 'Front hall stair (west)', 73, 21, 75, 26, 5, 'N')    # (their feet a metre off the front wall, at 1 m too)
A.stairs('manor', 'Front hall stair (east)', 85, 21, 87, 26, 5, 'N')
A.door('manor', 'Round Wooden Door', 72, 14, 72.5, 17)               # great room to the gallery
A.door('manor', 'Round Wooden Door', 87.5, 14, 88, 17)               # great room to the dining room
# the portico: paired 9 m stone columns either side of the axis, an entablature between them at the eaves,
# rising in the middle into the pediment round an oculus; the pediment roof carried forward over it all
for x0 in (76, 77.5, 81.5, 83):
    R(mnr, x0, 30, x0 + 1, 31, 'X')
for (x0, x1) in ((77, 77.5), (78.5, 79), (81, 81.5), (82.5, 83)):
    A.overlay(mnr, x0, 30.5, x1, 31, 'Fancy Stone Block (entablature)', STONE, 1, 8, kind='wall')
A.overlay(mnr, 79, 30.5, 81, 31, 'Fancy Stone Block (tympanum)', STONE, 3.5, 8, kind='wall')
A.win('manor', 'Round Wooden Window Frame', 79.5, 30.5, 80.5, 31, 9.5)       # the oculus
put('manor', 'Hanging Lantern', 79.5, 29.5, z=6.0)
zone('manor', 'Portico', 76, 28, 84, 31, '#b7a3dc')
# ---- inside the centre block
put('manor', 'Hanging Lantern', 78, 24, z=6.5); put('manor', 'Hanging Lantern', 81.5, 24, z=6.5)   # over the front hall
put('manor', 'Ground Lantern II', 76.5, 19); put('manor', 'Ground Lantern II', 83, 19)
put('manor', 'Stone Fireplace', 75, 12.5); put('manor', 'Stone Fireplace', 83, 12.5)       # the great room's hearths
put('manor', 'Bench', 75, 14.5, 180); put('manor', 'Bench', 83, 14.5, 180)
put('manor', 'Wooden Side Table', 79.5, 15); put('manor', 'Rustic Chair', 78.5, 15, 270); put('manor', 'Rustic Chair', 80.5, 15, 90)
put('manor', 'Carved Wooden Shelf', 73, 18, 180); put('manor', 'Carved Wooden Shelf', 85, 18, 180)
put('manor', 'Hanging Lantern', 77, 16, z=4.0); put('manor', 'Hanging Lantern', 83, 16, z=4.0)
zone('manor', 'Front hall (double height)', 72.5, 19, 87.5, 27.5, '#6b4fa3')
zone('manor', 'Great room', 72.5, 12.5, 87.5, 18.5, '#6b4fa3')
# ---- the gallery: one tall hall: showcases along the walls, mannequins down the middle, a hearth
put('manor', 'npc-collector', 68.5, 11, 0, label='Collector (showcases)')
for y in (10, 12.5, 15):
    put('manor', 'Embervale Miniature Showcase', 62.5, y, 270)
for y in (18, 20.5):
    put('manor', 'Embervale Miniature Showcase', 71, y, 90)
for (x, y), m in zip(((66.5, 17), (68.5, 17), (66.5, 21), (68.5, 21)),
                     ('Mannequin "Strike A Pose"', 'Mannequin "Victory"', 'Mannequin "Look At Me"', 'Mannequin "Here I Come"')):
    put('manor', m, x, y, 180)
put('manor', 'Stone Fireplace', 66.5, 9.5)
for y in (13, 19, 25):
    put('manor', 'Hanging Lantern', 67.5, y, z=7.0)
zone('manor', "Gallery (the Collector's showcases)", 62.5, 9.5, 72, 27.5, '#8a6aa8')
# ---- the east wing, ground floor: the dining room (behind) and the parlour (in front)
R(mnr, 88, 18.5, 97.5, 19, 'M')
A.door('manor', 'Wooden Door', 91.5, 18.5, 93.5, 19)
put('manor', 'Stone Fireplace', 92, 9.5)
for x in (89.5, 92.5):
    put('manor', 'Wooden Banquet Table', x, 13.5)
for x in (90, 91.5, 93, 94.5):
    put('manor', 'Rustic Chair', x, 12.5, 0); put('manor', 'Rustic Chair', x, 14.5, 180)
put('manor', 'Large Carved Wooden Cabinet', 88, 10, 270)
put('manor', 'Hanging Lantern', 91, 14, z=4.0); put('manor', 'Hanging Lantern', 94, 14, z=4.0)
put('manor', 'Wooden Side Table', 89.5, 22.5); put('manor', 'Rustic Chair', 88.5, 22.5, 270)
put('manor', 'Rustic Chair', 90.5, 22.5, 90); put('manor', 'Rustic Chair', 89.5, 21.5, 180)
put('manor', 'Rustic Bench', 94.5, 20, 0)
put('manor', 'Hanging Lantern', 93, 23, z=4.0)
zone('manor', 'Dining room', 88, 9.5, 97.5, 18.5, '#6b4fa3')
zone('manor', 'Parlour', 88, 19, 97.5, 27.5, '#6b4fa3')
# ---- the upper floor (+13 m): over the great room and a landing that looks down into the front hall
A.walls(mup, 72, 12, 88, 28, 'M')
R(mup, 72.5, 12.5, 87.5, 21.5, 'r')                     # the floor, stopping at the front hall's balcony
R(mup, 73, 21, 75, 21.5, ' '); R(mup, 85, 21, 87, 21.5, ' ')   # (open over the stairs' tops)
R(mup, 75, 21.5, 85, 22, 'i')                           # the balcony railing between the two stair tops
R(mup, 72.5, 18.5, 87.5, 19, 'M')                       # landing | rooms
R(mup, 79.5, 12.5, 80, 18.5, 'M')                       # room | room
A.door('mup', 'Wooden Door', 75, 18.5, 77, 19)
A.door('mup', 'Wooden Door', 83, 18.5, 85, 19)
A.walls(mup, 87.5, 9, 98, 28, 'M', 'r')                 # the east wing, upper floor
for (x0, x1) in ((97.5, 104.5),):                       # (re-close the tower's wall where the wing's ring ran)
    A.walls(mup, x0, 22, x1, 29, 'M')
R(mup, 88, 18.5, 97.5, 19, 'M')
A.door('mup', 'Wooden Door', 87.5, 19, 88, 21)                       # landing to the master bedroom
A.door('mup', 'Wooden Door', 91.5, 18.5, 93.5, 19)                   # master bedroom to the study
R(mup, 91, 27.5, 94, 28, 'j')                           # the east wing's front gable rises over the bedroom
# the master bedroom's balcony, over the parlour's door: a stone floor on two brackets, a balustrade, a door
# from the bedroom under the gable's round window
A.door('mup', 'Wooden Door', 91.5, 27.5, 93.5, 28)
for x in (91, 93.5):
    A.overlay(mnr, x, 28.5, x + 0.5, 29, 'Fancy Stone Block (balcony bracket)', STONE, 0.5, 4.0)
zone('mup', 'Balcony', 90.5, 28, 94.5, 29.5, '#b7a3dc')
put('mup', 'bed', 72.5, 13); put('mup', 'chest-small', 78, 13.5); put('mup', 'Hanging Lantern', 76, 15.5, z=3.0)
put('mup', 'bed', 85.5, 13); put('mup', 'chest-small', 81, 13.5); put('mup', 'Hanging Lantern', 84, 15.5, z=3.0)
put('mup', 'bed2', 93, 22, label='Double bed (the master bedroom)')
put('mup', 'Carved Wooden Nightstand', 93, 21); put('mup', 'Carved Wooden Nightstand', 95, 21)
put('mup', 'Large Carved Wooden Cabinet', 88, 23, 270); put('mup', 'chest-small', 89.5, 26.5)
put('mup', 'Hanging Lantern', 92, 23, z=3.0)
put('mup', 'Wooden Side Table', 92, 14); put('mup', 'Rustic Chair', 92, 15, 180)
put('mup', 'Carved Wooden Shelf', 88, 11, 270); put('mup', 'Carved Wooden Shelf', 88, 13.5, 270)
put('mup', 'Hanging Lantern', 93, 13, z=3.0)
zone('mup', 'Landing and balcony', 72.5, 19, 87.5, 22, '#6b4fa3')
zone('mup', 'Guest room', 72.5, 12.5, 79.5, 18.5, '#9c6b8e')
zone('mup', 'Guest room', 80, 12.5, 87.5, 18.5, '#9c6b8e')
zone('mup', 'Master bedroom', 88, 19, 97.5, 27.5, '#9c6b8e')
zone('mup', 'Study', 88, 9.5, 97.5, 18.5, '#9c6b8e')

# ---- the towers: a stone spiral stair in the back corner from the ground to the belvedere; the west tower
# opens to the gallery and the west garden, the east one to the parlour, the master bedroom and the east
# garden
TOWERS = (('west', 55.5, 62.5, 58, 90), ('east', 97.5, 104.5, 102, 270))   # walls x0..x1, the stair's centre x and start bearing
for name, x0, x1, scx, start in TOWERS:
    A.spiral(ts8, scx, 24.5, 4, 5, 'Fancy Stone Block (spiral)', STONE, start)
    A.spiral(ts13, scx, 24.5, 4, 4, 'Fancy Stone Block (spiral)', STONE, start)
    R(mup, x0 + 0.5, 22.5, x1 - 0.5, 28.5, 'r'); A.circle(mup, scx, 24.5, 4, ' ')
    R(mtop, x0 + 0.5, 22.5, x1 - 0.5, 28.5, 'r'); A.circle(mtop, scx, 24.5, 4, ' ')
    zone('manor', f'{name.title()} tower', x0, 22, x1, 29, '#6b4fa3')
    zone('mtop', f'{name.title()} tower: the belvedere', x0 + 0.5, 22.5, x1 - 0.5, 28.5, '#6b4fa3')
A.door('manor', 'Round Wooden Door', 62, 24, 62.5, 27)               # gallery to the west tower
A.door('manor', 'Wooden Door', 97.5, 24, 98, 26)                     # parlour to the east tower
A.door('mup', 'Wooden Door', 97.5, 24, 98, 26)                       # master bedroom to the east tower
put('manor', 'Ground Lantern II', 60.5, 27.5)
put('mup', 'Wooden Side Table', 57, 27); put('mup', 'Rustic Chair', 58, 27, 90); put('mup', 'chest-small', 61, 27.5)
put('mup', 'bathtub', 100, 26.5, 90, label='Bathtub (the master bath)')   # under the small high windows
put('mup', 'Wooden Sink', 103, 26.5, 270); put('mup', 'Wooden Lavatory', 98, 27.5)
for bx in (59.5, 100.5):
    put('mtop', 'Rustic Bench', bx, 28, 0)
put('mtop', 'Hanging Lantern', 58, 27.5, z=3.0); put('mtop', 'Hanging Lantern', 99, 23.5, z=3.0)
zone('mup', "West tower: the Collector's study", 56, 22.5, 62, 28.5, '#8a6aa8')
# the clock stage on the west tower (the Collector's tower): another 4 m, clock faces (great round frames) on
# three sides, a ladder up from the belvedere; the east tower stays a storey lower
A.walls(ctop, 55.5, 22, 62.5, 29, 'M', 'r')
R(ctop, 61, 23, 62, 24, ' ')                            # the hatch over the ladder
put('mtop', 'ladder', 61, 23, label='Ladder up to the clock')
A.win('ctop', 'Large Round Wooden Window Frame', 57.5, 28.5, 60.5, 29, 0.5)      # clock faces: south,
A.win('ctop', 'Large Round Wooden Window Frame', 55.5, 24, 56, 27, 0.5)          # west,
A.win('ctop', 'Large Round Wooden Window Frame', 62, 24, 62.5, 27, 0.5)          # and east over the gallery roof
zone('ctop', 'West tower: the clock stage', 56, 22.5, 62, 28.5, '#8a6aa8')
zone('mup', 'East tower: the master bath', 98, 22.5, 104, 28.5, '#9c6b8e')

# ================================================================= the facades
# A Fancy Stone base course (with sills under the ground floor windows), a string course at the upper
# floor line (+13 m, the upper windows' sills), and the towers' course at +17 m under the belvederes
FACADES = [('S', 28, 62.5, 72), ('S', 28, 72, 88), ('S', 28, 88, 97.5), ('S', 29, 55.5, 62.5), ('S', 29, 97.5, 104.5),
           ('W', 62, 9, 22), ('W', 55.5, 22, 29), ('E', 98, 9, 22), ('E', 104.5, 22, 29),
           ('N', 9, 62, 72.5), ('N', 12, 72.5, 87.5), ('N', 9, 87.5, 98), ('N', 22, 55.5, 62), ('N', 22, 98, 104.5),
           ('E', 72.5, 9, 12), ('W', 87.5, 9, 12), ('E', 62.5, 28, 29), ('W', 97.5, 28, 29)]
for side, line, a0, a1 in FACADES:
    R(mtrim, *out_sq(side, line, a0, a1), 'p')
    R(mup, *out_sq(side, line, a0, a1), 'c')
for side, line, a0, a1 in (('S', 29, 55.5, 62.5), ('S', 29, 97.5, 104.5), ('W', 55.5, 22, 29), ('E', 104.5, 22, 29),
                           ('N', 22, 55.5, 61.5), ('N', 22, 98.5, 104.5)):   # (clear of the wings' eaves)
    R(mtop, *out_sq(side, line, a0, a1), 'c')
for side, line, a0, a1 in (('S', 29, 55.5, 62.5), ('W', 55.5, 22, 29), ('N', 22, 55.5, 62.5), ('E', 62.5, 22, 29)):
    R(ctop, *out_sq(side, line, a0, a1), 'c')           # the course under the clock stage, all round
# the master bedroom's balcony floor and balustrade (over the string course there)
R(mup, 90.5, 28, 94.5, 29.5, 'f')
R(mup, 90.5, 29, 94.5, 29.5, 'b'); R(mup, 90.5, 28, 91, 29, 'b'); R(mup, 94, 28, 94.5, 29, 'b')
# ---- doors and windows: tall windows in pairs round each door; symmetric about the axis (x 80)
# south
for a in (63.5, 70.5):
    window('g', 'S', 28, a); window('c', 'S', 28, a)                      # the gallery
entrance('Round Wooden Door', 'S', 28, 66, 69)
for a in (74, 76.5, 82.5, 85):
    window('g', 'S', 28, a); window('u', 'S', 28, a)                      # the centre block (two under the portico)
R(mtrim, 78, 28, 82, 28.5, ' ')                         # no base course across the front door
for a in (88.5, 95.5):
    window('g', 'S', 28, a); window('u', 'S', 28, a)                      # the east wing
entrance('Round Wooden Door', 'S', 28, 91, 94)
for x0, door, first in ((55.5, 58, 'u'), (97.5, 100, 'b')):            # the towers' fronts (the east one's first floor is the bath)
    entrance('Wooden Door', 'S', 29, door, door + 2)
    window(first, 'S', 29, door + 0.5)
    window('t', 'S', 29, x0 + 1); window('t', 'S', 29, x0 + 5)
# the great round windows in the wings' front gables, and the oculus over them all in the portico
A.win('manor', 'Large Round Wooden Window Frame', 66, 27.5, 69, 28, 9.5)
A.win('mup', 'Large Round Wooden Window Frame', 91, 27.5, 94, 28, 4.5)
# west and east
for a in (11, 14.5):
    window('c', 'W', 62, a)                             # the gallery: clerestory only (showcases along the wall)
entrance('Wooden Door', 'W', 62, 19, 21)                # the gallery's garden door
window('g', 'W', 55.5, 27); window('u', 'W', 55.5, 27); window('t', 'W', 55.5, 23); window('t', 'W', 55.5, 26.5)
entrance('Wooden Door', 'E', 98, 12, 14)                # the dining room's service door, from the farm's stair
for a in (16, 19.5):
    window('g', 'E', 98, a); window('u', 'E', 98, a)
window('g', 'E', 104.5, 27); window('b', 'E', 104.5, 27); window('t', 'E', 104.5, 23); window('t', 'E', 104.5, 26.5)
# north
for a in (64, 70):
    window('g', 'N', 9, a); window('c', 'N', 9, a)
entrance('Wooden Door', 'N', 12, 79, 81)                # the great room to the rear court
window('g', 'N', 12, 73); window('g', 'N', 12, 86); window('u', 'N', 12, 77.5); window('u', 'N', 12, 81.5)
for a in (89.5, 95):
    window('g', 'N', 9, a); window('u', 'N', 9, a)
window('g', 'N', 22, 60.5); window('u', 'N', 22, 60.5); window('t', 'N', 22, 56.5); window('t', 'N', 22, 59.5)
window('g', 'N', 22, 98.5); window('u', 'N', 22, 98.5); window('t', 'N', 22, 99.5); window('t', 'N', 22, 102.5)   # (belvederes clear of the wings' eaves)
# red banners on the towers' fronts, hanging below the belvedere windows either side of the first floor window
for x0 in (55.5, 97.5):
    for dx in (1, 5):
        R(banner, x0 + dx, 29, x0 + dx + 1, 29.5, 'V')
# lanterns by the outside doors
for x in (65, 69.5, 90, 94.5):
    put('manor', 'Wall Lantern', x, 28, 0, 2.0)
for x in (57, 60.5, 99, 102.5):
    put('manor', 'Wall Lantern', x, 29, 0, 2.0)
put('manor', 'Ground Lantern II', 80, 8)
for x in (74, 85):                                      # the rear court: topiary in stone planters, a bench
    planter(mnr, x, 8, x + 2, 10)
put('manor', 'Bench', 79, 9.5, 180)
# ---- quoins up every outside corner (Fancy Stone), 9 m on the wings, 13 m on the towers
for cx, cy in ((62, 9), (72.5, 9), (87.5, 9), (98, 9)):
    quoin(cx, cy, 'q')
for cx, cy in ((104.5, 29), (104.5, 22), (97.5, 29)):
    quoin(cx, cy, 'Q')
for cx, cy in ((55.5, 29), (55.5, 22), (62.5, 29)):     # the clock tower's run up to its clock stage
    quoin(cx, cy, 'E')
    R(ctop, cx - 0.5, cy - 0.5, cx + 0.5, cy + 0.5, ' ')
# ---- chimneys: up the wings' rear gables and either side of the great room, capped in stone
CHIMNEYS = (((66.5, 8, 68, 9.5), 'J'), ((92, 8, 93.5, 9.5), 'J'), ((75.5, 11, 77, 12.5), 'J'), ((83, 11, 84.5, 12.5), 'J'))   # all to +26 m
for (x0, y0, x1, y1), ch in CHIMNEYS:
    R(mnr, x0, y0, x1, y1, ch)
    for g in (mtrim, mup):
        R(g, x0, y0, x1, y1, ' ')                       # through the courses and the upper floor's wall
    A.ring(caps, x0, y0, x1, y1, '6')
for (px, py) in ((67, 8.5), (92.5, 8.5), (75.5, 11.5), (76.5, 11.5), (83, 11.5), (84, 11.5)):
    R(caps, px, py, px + 0.5, py + 0.5, 'h')           # terracotta chimney pots

# ================================================================= roofs: castle slate at 45 degrees in even steps,
# with Fancy Stone eaves (a cornice) and ridges
rr = A.roof(mroof)
rr.gable(62, 9, 72.5, 28, 'y', 'castle', pitch=1.0, overhang=0.5)     # the wings: front gables
rr.gable(87.5, 9, 98, 28, 'y', 'castle', pitch=1.0, overhang=0.5)
rr.hip(72, 12, 88, 28, 'castle', pitch=1.0, overhang=0.5, ridge_h=7.0)   # the centre: a pyramid cut flat near the top
rr.gable(76, 24, 84, 31, 'y', 'castle', pitch=1.0, overhang=0.5)     # the pediment, carried forward over the portico
rr.cut(55.5, 22, 62.5, 29); rr.cut(97.5, 22, 104.5, 29)              # (the towers rise through)
for (x0, y0, x1, y1), ch in CHIMNEYS:
    rr.cut(x0, y0, x1, y1)
rr.eaves('cornice'); rr.caps('cornice', min_lower=1)
rr.paint()
for x0 in (67, 92.5):                                   # stone finials on the wings' front gable apexes
    A.overlay(mroof, x0, 28, x0 + 0.5, 28.5, 'Fancy Stone Block (finial)', STONE, 1.0, 6.0)
for x in (78.5, 81):                                    # the cupola: four stone posts on the flat, a lantern among them
    for y in (18.5, 21):
        A.overlay(mroof, x, y, x + 0.5, y + 0.5, 'Fancy Stone Block (cupola post)', STONE, 2.0, 7.0)
A.overlay(mroof, 79.5, 19.5, 80.5, 20.5, 'Yellow Luminescent Block (cupola lantern)', '#bd9a5f', 1.0, 7.0)
rc = A.roof(cupola)
rc.hip(78.5, 18.5, 81.5, 21.5, 'castle', pitch=1.0, overhang=0.5)
rc.eaves('cornice'); rc.caps('cornice', min_lower=1)
rc.paint()
A.overlay(cupola, 79.5, 19.5, 80.5, 20.5, 'Fancy Stone Block (finial)', STONE, 1.0, 2.0)
R(flag, 79.5, 19.5, 80, 20, 'Z'); R(flag, 80, 19.5, 81.5, 20, 'W')   # a flagpole on the finial, its flag flying east
for g, x0, x1, fx in ((troof, 97.5, 104.5, 100.5), (troof2, 55.5, 62.5, 58.5)):   # the towers: pyramids with stone finials
    rt = A.roof(g)
    rt.hip(x0, 22, x1, 29, 'castle', pitch=1.0, overhang=0.5)
    rt.eaves('cornice'); rt.caps('cornice', min_lower=1)
    rt.paint()
    A.overlay(g, fx, 25, fx + 1, 26, 'Fancy Stone Block (finial)', STONE, 1.0, 4.0)
rv = A.roof(pav)                                        # the garden pavilion
rv.hip(54, 8, 59, 13, 'castle', pitch=1.0, overhang=0.5)
rv.eaves('cornice'); rv.caps('cornice', min_lower=1)
rv.paint()
A.overlay(pav, 56, 10, 57, 11, 'Fancy Stone Block (finial)', STONE, 1.0, 3.0)
zone('manor', 'Manor house', 62, 9, 98, 28, '#6b4fa3')

# ================================================================= the stairs that arrive (their own blueprints)
# the grand stair from the square, between its stepped flanks (lamps at both ends)
R(mid, 74, 42, 86, 50, 'L')
A.stairs('mid', 'Grand stair from the square (square blueprint)', 76, 42, 84, 50, 4, 'N')
A.flanks(mid, 76, 42, 84, 50, 'N', thick=2)
for x in (74.5, 84.5):
    R(lamp6, x, 49, x + 1, 50, 'l'); R(lamp9, x, 42, x + 1, 43, 'l')
# the west stair from the smithy's landing
R(mid, 48, 42, 56, 50, 'w')
A.stairs('mid', 'West stair from the smithy (smithy blueprint)', 50, 42, 56, 50, 4, 'N')
A.flanks(mid, 50, 42, 56, 50, 'N')
for x in (49.5, 56):
    R(lamp6, x, 49.5, x + 0.5, 50, 'l'); R(lamp9, x, 42, x + 0.5, 42.5, 'l')
# the farm's service stair, up 3 m from the farm's west edge to the east garden
R(up5, 110, 34, 114, 40, 'r')
A.stairs('up5', 'Service stair from the farm (farm blueprint)', 110, 34, 116, 40, 3, 'W')
R(up5, 114, 30, 118, 50, 'r'); R(up5, 114, 30, 115, 50, 't'); R(up5, 114, 30, 118, 31, 't')   # the farm's west edge
zone('mid', 'Grand stair (square blueprint)', 74, 42, 86, 50, '#b8862b')
zone('mid', 'West stair (smithy blueprint)', 49.5, 42, 56.5, 50, '#2f8f8a')
zone('up5', 'Farm and its service stair (farm blueprint)', 110, 30, 118, 50, '#3f8a4f')

# ================================================================= stilts, rim beams and checks
print('stilts:', A.stilts(stl, [('mid', 4), ('up5', 5), ('manor', 8)]))
print('rim beam squares:', A.rim_beams(stl, [('manor', 8)], lambda x, y: 50 <= x < 110 and 6 <= y < 42))
A.spawn('manor', 79.5, 39, 180)                                 # walk mode starts here: the front terrace at the top of the grand stair, facing the fountain and the portico
A.checks()

NOTES = """Laketown: the manor, as a 0.5 m detail blueprint (all three passes done). Drafted by Claude.
This plan's corner is the layout's (48, 4), so it lines up with the Laketown layout and stamps back into the site plan there.

PASSES
1. Design and bones: the grounds, the house's walls, rooms, doors, stairs and roof shapes, the portico, the Collector, the connections, stilts, labels.
2. Details: the towers and the wings' front gables, windows, stonework, chimneys, roof trim, the gardens and terrace, lights, furniture.
3. Review and finishing touches (this one).

PASS 3: WHAT THE REVIEW FOUND AND CHANGED
- The master suite had no bath. The east tower's first floor, off the master bedroom, is the master bath now: a bathtub, a sink and a lavatory, under two small high windows (one frame each, sills 1 m up) where the tall ones were.
- The farm's service route was only plain paving up the east edge: it's gravel the whole way now, from the farm's stair to the dining room's service door.
- From across the lake the towers were plain stone: red banners (Red Carpet Block, 3 m) hang on their fronts below the belvedere windows, and a red flag flies from a pole on the cupola's finial (+33 m), the highest point in Laketown.
- Checked, all clear (check_access): nothing in front of any door or window, no door onto a drop, every stair with 1 m clear at the foot and top and 2 m of headroom. The three stairs that arrive (the grand stair, the west stair, the farm's service stair) land cleanly in the site plan.

CHARACTER (after pass 3): a little asymmetry, each piece with a reason:
- The west tower is the Collector's clock tower: a fourth stage (+21 to +25 m) with clock faces (Large Round Wooden Window Frames, 3 m) south, west and east, a ladder up from the belvedere, its pyramid a stage higher (+29 m, finial to +30 m). The east tower stays a storey lower, so the skyline leans west.
- The master bedroom has a balcony over the parlour's door (the east wing only, the private side): a stone floor on two brackets, a balustrade, a door from the bedroom under the gable's round window.
- A garden pavilion at the north end of the west garden's path: four stone columns, a fancy stone floor, a slate pyramid with a finial, a bench and a lantern. The east garden keeps the service path.
- Terracotta chimney pots: two on each great room stack, one on each wing's.

CONNECTIONS (for the neighbouring blueprints to match)
- Farm: the service stair (x 110..116, y 34..40, rising 3 m west) lands in the gap in the east balustrade; the gravel service path leads from it up the east edge and along y 12..14 to the dining room's service door. Keep the stair's top on that line and give it cheek walls or railings in the town's style.
- Square: the grand stair arrives at x 76..84 between its flanks; the terrace's way leads straight on to the fountain and the portico.
- Smithy: the west stair arrives at x 50..56 by the west garden.
- The tavern's roof stands about 10 m above the deck, south of the west end of the terrace: the west tower's belvedere looks over it; nothing at that end of the terrace faces it.

THE GROUNDS (+8 m, 60 x 36 m): polished stone on a fancy stone edge, a balustrade with piers round the whole edge, open where the grand stair (x 76..84), the west stair (x 50..56) and the farm's service stair (east edge, y 34..40) arrive. Rim beams under the edges.
- Front terrace over the square: a fancy stone way on the axis from the grand stair to the portico, a round fountain on it (a stone basin with a lamp glowing on its pedestal, in a ring of fancy stone paving), four planters with topiary, benches and lanterns.
- West and east gardens: lawns with gravel paths and two long flower beds each, topiary, benches, lanterns. The west path leads from the gallery's garden door; the east one is the service path from the farm's stair to the dining room's door.
- A rear court behind the centre block, off the great room: topiary in stone planters either side of the door, a bench, a lantern.

THE HOUSE: limestone, castle slate roofs with Fancy Stone eaves and ridges (a cornice), eaves at +17 m. It sits on the village's main axis: gatehouse, causeway, altar, grand stair, fountain, portico, cupola. From the square it reads tower, gable, portico and cupola, gable, tower.
- Stonework (Fancy Stone): a base course with sills under the ground floor windows, hoods over every ground floor window and outside door, a string course at the upper floor line (+13 m) that the upper windows sit on, quoins up every outside corner.
- Windows: tall ones of two stacked Wooden Window Frames (3 m), symmetric about the axis.
- Centre block (16 x 16 m, two storeys):
  - the portico: paired 9 m columns either side of the axis, an entablature at the eaves rising in the middle into the pediment round an oculus (a Round Wooden Window Frame), the pediment roof carried over it all; a lantern hanging in it;
  - the front hall, double height, with twin stairs up its sides to a balcony landing, chandeliers;
  - the great room behind (two stone fireplaces under the two rear chimneys, benches, a table, shelves), joining the wings and the rear court;
  - upstairs: the landing and balcony, two guest rooms with beds;
  - roof: a pyramid cut flat near the top, with a cupola on four stone posts and a lantern glowing inside it, a stone finial on top: the highest point (+29 m).
- West wing: the Collector's gallery, one 9 m hall: tall windows and a clerestory, a great round window (3 m) high in its front gable, a hearth under its rear chimney; the Collector, showcases along the walls, four mannequins down the middle, lanterns hung high.
- East wing (two storeys): the dining room (a long table for eight, a hearth, a cabinet, the service door) and the parlour (its own round door to the terrace) below; the master bedroom (a double bed, nightstands, a wardrobe, a great round window high in the gable above it) and the study above. No kitchen: food comes up from the farm.
- The towers, flanking the wings, 1 m proud of the front: three storeys (+8, +13, +17) with a belvedere on top (windows all round), a stone spiral stair in the back corner from the ground to the belvedere, quoins, a course under the belvedere, red banners on their fronts, pyramid roofs with stone finials (+26 m).
  - West tower: off the gallery, with its own door to the terrace; the Collector's study on the first floor.
  - East tower: off the parlour and the master bedroom, with its own door to the terrace; the master bath on the first floor.
- Chimneys: four, limestone with stone caps, all to +26 m: up the wings' rear gables (the gallery's and the dining room's hearths) and either side of the great room.
- Stone finials on the wings' front gable apexes, the towers and the cupola.

CONNECTIONS
- South: the grand stair from the square arrives at x 76..84 between its stepped flanks (lamps on top); the terrace balustrade leaves that gap.
- South-west: the west stair from the smithy's landing arrives at x 50..56 by the west garden.
- East: the farm's service stair arrives at the east garden's edge (y 34..40); the service path leads from it to the dining room.

ITEMS: furniture and light sizes are estimates until measured; stations and the Collector use the planner's placeholders.

STILTS: 1 m posts on the layout's 4 m grid, from the lake bed 4 m down to the deck's underside.
"""
A.save('laketown_manor.json', NOTES, 'r-claude-laketown-manor-3c')
