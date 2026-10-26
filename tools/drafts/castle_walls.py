"""Draft: small castle keep inside a curtain wall with a gatehouse. 0.5 m squares.

Run: python castle_walls.py  ->  writes castle-walls.json next to this script.
Everything is laid out in metres and converted to squares (x2).
The canvas is 80 x 80 m, the most a 0.5 m plan can hold.
"""
import json, os, time

C = 2
WM = HM = 80
W, H = WM * C, HM * C

def sq(m): return int(round(m * C))
def off(r, ox, oy): return (r[0] + ox, r[1] + oy, r[2] + ox, r[3] + oy)
def in_rect(x, y, r): return sq(r[0]) <= x < sq(r[2]) and sq(r[1]) <= y < sq(r[3])
def blank(): return [[' '] * W for _ in range(H)]

def stamp(g, r, ch, only=None):
    x0, y0, x1, y1 = r
    for y in range(sq(y0), sq(y1)):
        for x in range(sq(x0), sq(x1)):
            if 0 <= x < W and 0 <= y < H and (only is None or g[y][x] in only):
                g[y][x] = ch

class Shape:
    """A union of rectangles. Walls follow its outline, 1 m (2 blocks) thick."""
    def __init__(self, rects): self.rects = list(rects)
    def inside(self, x, y): return 0 <= x < W and 0 <= y < H and any(in_rect(x, y, r) for r in self.rects)
    def near_edge(self, x, y, radius):
        return any(not self.inside(x + dx, y + dy) for dx in range(-radius, radius + 1) for dy in range(-radius, radius + 1))
    def cells(self):
        x0 = min(sq(r[0]) for r in self.rects); x1 = max(sq(r[2]) for r in self.rects)
        y0 = min(sq(r[1]) for r in self.rects); y1 = max(sq(r[3]) for r in self.rects)
        for y in range(max(0, y0), min(H, y1)):
            for x in range(max(0, x0), min(W, x1)):
                if self.inside(x, y):
                    yield x, y

def shell(g, shape, floor, wall):
    for x, y in shape.cells():
        g[y][x] = wall if shape.near_edge(x, y, 2) else floor

def battlements(g, shape, floor):
    for x, y in shape.cells():
        g[y][x] = (('M' if ((x // C) + (y // C)) % 2 == 0 else 'c') if shape.near_edge(x, y, 1) else floor)

def notch(g, rects, skip_if_inside):
    """Cosmetic: knock the outermost corner block off each tower."""
    for r in rects:
        for cx, cy in [(sq(r[0]), sq(r[1])), (sq(r[2]) - 1, sq(r[1])), (sq(r[0]), sq(r[3]) - 1), (sq(r[2]) - 1, sq(r[3]) - 1)]:
            if not any(in_rect(cx, cy, s) for s in skip_if_inside) and g[cy][cx] != ' ':
                g[cy][cx] = ' '

# ------------------------------------------------------------------ geometry (metres)
OX, OY = 25, 22                                   # keep moved to the middle of the bailey
KEEP = off((8, 7, 22, 21), OX, OY)               # 14 x 14 m keep: x 33-47, y 29-43
KTOW = {k: off(r, OX, OY) for k, r in {'NW': (6, 5, 11, 10), 'NE': (19, 5, 24, 10), 'SW': (6, 18, 11, 23), 'SE': (19, 18, 24, 23)}.items()}
PORCH = off((12, 21, 18, 25), OX, OY)            # x 37-43, y 43-47
keep_shape = Shape([KEEP, *KTOW.values()])

BAILEY = (16, 12, 64, 60)                         # open ground inside the curtain (48 x 48 m)
FRAME = [(14, 10, 66, 12), (14, 60, 66, 62), (14, 10, 16, 62), (64, 10, 66, 62)]   # 2 m thick curtain
CTOW = {'NW': (10, 6, 18, 14), 'NE': (62, 6, 70, 14), 'SW': (10, 58, 18, 66), 'SE': (62, 58, 70, 66)}  # 8 x 8 m
GATE_MAIN = (32, 55, 48, 63)                      # gatehouse block straddling the south wall
GATE_TOW = [(31, 59, 37, 67), (43, 59, 49, 67)]   # twin towers projecting outward
PASSAGE = (38, 55, 42, 63)                        # 4 m gate passage
curtain_shape = Shape([*FRAME, *CTOW.values(), GATE_MAIN, *GATE_TOW])
towers_shape = {k: Shape([r]) for k, r in CTOW.items()}
gate_shape = Shape([GATE_MAIN, *GATE_TOW])

def mx(r): return (WM - r[2], r[1], WM - r[0], r[3])      # mirror east-west
def my(r): return (r[0], 72 - r[3], r[2], 72 - r[1])      # mirror north-south (bailey centre is y 36)
def corner(r, k):
    if k[1] == 'E': r = mx(r)
    if k[0] == 'S': r = my(r)
    return r
def corner_rot(rot, k):
    if k[1] == 'E': rot = {0: 0, 180: 180, 90: 270, 270: 90}[rot]
    if k[0] == 'S': rot = {0: 180, 180: 0, 90: 90, 270: 270}[rot]
    return rot

# Corner tower fittings, drawn for the NW tower and mirrored to the others
CT_STAIRS_G = ((11, 8, 13, 12), 0)       # ground -> first
CT_STAIRS_F1 = ((13.5, 7, 15.5, 11), 180)  # first -> wall-walk level
CT_DOOR_YARD = (16, 13, 17, 14)          # into the bailey (south wall of the NW tower)
CT_DOOR_WALK_N = (17, 10.5, 18, 11.5)    # onto the north (or south) wall walk
CT_DOOR_WALK_W = (14.5, 13, 15.5, 14)    # onto the west (or east) wall walk
CT_LADDER = (11, 12, 12, 13)             # wall-walk level -> tower roof
CT_SLITS = [(10, 9.75, 11, 10.25), (13.75, 6, 14.25, 7)]

# ------------------------------------------------------------------ keep (from the first draft, moved)
def keep_levels():
    k = {}
    g0, g1, g2, g3, g4 = blank(), blank(), blank(), blank(), blank()
    def kshell(g, floor):
        for x, y in keep_shape.cells():
            tower = any(in_rect(x, y, r) for r in KTOW.values()) and not in_rect(x, y, KEEP)
            g[y][x] = ('K' if tower else '#') if keep_shape.near_edge(x, y, 2) else floor
    o = lambda r: off(r, OX, OY)
    # ground
    kshell(g0, ',')
    for xm in (13, 15, 17): stamp(g0, o((xm, 7, xm + 0.5, 8)), 'x', '#K')
    for ym in (12, 14, 16):
        stamp(g0, o((8, ym, 9, ym + 0.5)), 'x', '#K'); stamp(g0, o((21, ym, 22, ym + 0.5)), 'x', '#K')
    for key, (x0, y0, x1, y1) in {k_: (r[0] - OX, r[1] - OY, r[2] - OX, r[3] - OY) for k_, r in KTOW.items()}.items():
        xm = (x0 + x1) / 2 - 0.25; ym = (y0 + y1) / 2 - 0.25
        stamp(g0, o((xm, y0, xm + 0.5, y0 + 1) if key[0] == 'N' else (xm, y1 - 1, xm + 0.5, y1)), 'x', 'K')
        stamp(g0, o((x0, ym, x0 + 1, ym + 0.5) if key[1] == 'W' else (x1 - 1, ym, x1, ym + 0.5)), 'x', 'K')
    for y in range(sq(PORCH[1]), sq(PORCH[3])):
        for x in range(sq(PORCH[0]), sq(PORCH[2])):
            g0[y][x] = '#' if (x < sq(PORCH[0] + 1) or x >= sq(PORCH[2] - 1) or y >= sq(PORCH[3] - 1)) else ','
    stamp(g0, o((14, 20, 16, 21)), 'D'); stamp(g0, o((14, 24, 16, 25)), 'D')
    # first
    kshell(g1, '.')
    for xm in (12.5, 16.5): stamp(g1, o((xm, 7, xm + 1, 8)), 'o', '#')
    for ym in (13, 16):
        stamp(g1, o((8, ym, 9, ym + 1)), 'o', '#'); stamp(g1, o((21, ym, 22, ym + 1)), 'o', '#')
    stamp(g1, o((9, 11, 11, 15)), ' '); stamp(g1, o((14, 20, 16, 21)), 'D')
    for y in range(sq(PORCH[1]), sq(PORCH[3])):
        for x in range(sq(PORCH[0]), sq(PORCH[2])):
            g1[y][x] = '=' if (x == sq(PORCH[0]) or x == sq(PORCH[2]) - 1 or y == sq(PORCH[3]) - 1) else ','
    # second
    kshell(g2, '.')
    for xm in (12.5, 16.5):
        stamp(g2, o((xm, 7, xm + 1, 8)), 'o', '#'); stamp(g2, o((xm, 20, xm + 1, 21)), 'o', '#')
    for ym in (13, 16):
        stamp(g2, o((8, ym, 9, ym + 1)), 'o', '#'); stamp(g2, o((21, ym, 22, ym + 1)), 'o', '#')
    stamp(g2, o((9, 16, 11, 20)), ' ')
    stamp(g2, o((15.5, 8, 16, 20)), 'W', '.'); stamp(g2, o((15.5, 16, 16, 17)), 'D')
    # roof
    battlements(g3, keep_shape, ',')
    for r in KTOW.values():
        ts = Shape([r])
        for x, y in ts.cells():
            g3[y][x] = 'K' if ts.near_edge(x, y, 2) else ','
    for key, r in KTOW.items():
        dx = 9 if key[1] == 'W' else 20
        dy0 = (r[3] - OY) - 1 if key[0] == 'N' else (r[1] - OY)
        stamp(g3, o((dx, dy0, dx + 1, dy0 + 1)), 'D')
    stamp(g3, o((9, 11, 11, 15)), ' ')
    # tower tops
    for r in KTOW.values(): battlements(g4, Shape([r]), ',')
    for lx, ly in [(7, 6), (22, 6), (7, 21), (22, 21)]: stamp(g4, o((lx, ly, lx + 1, ly + 1)), ' ')
    for g in (g0, g1, g2, g3, g4): notch(g, KTOW.values(), [KEEP])
    return g0, g1, g2, g3, g4

g0, g1, g2, g3, g4 = keep_levels()

# ------------------------------------------------------------------ curtain wall and towers
# Ground and first: solid wall with tower rooms; the gatehouse gets its own rooms.
shell(g0, curtain_shape, ',', 'C')
shell(g1, curtain_shape, '.', 'C')
# Second (8 m): wall walk on the curtain, towers and gatehouse keep rising.
battle_frame = Shape(FRAME)
for x, y in battle_frame.cells():
    outer = x < sq(14.5) or x >= sq(65.5) or y < sq(10.5) or y >= sq(61.5)
    g2[y][x] = (('M' if ((x // C) + (y // C)) % 2 == 0 else 'c') if outer else ',')
for k, ts in towers_shape.items(): shell(g2, ts, '.', 'C')
shell(g2, gate_shape, '.', 'C')
# Roof (12 m): battlemented tops on the four towers and the gatehouse.
for ts in towers_shape.values(): battlements(g3, ts, ',')
battlements(g3, gate_shape, ',')

for k in CTOW:
    sr, srot = CT_STAIRS_G
    stamp(g1, corner(sr, k), ' ')                       # opening above the ground flight
    sr, srot = CT_STAIRS_F1
    stamp(g2, corner(sr, k), ' ')                       # opening above the first-floor flight
    stamp(g0, corner(CT_DOOR_YARD, k), 'D')
    stamp(g2, corner(CT_DOOR_WALK_N, k), 'D')
    stamp(g2, corner(CT_DOOR_WALK_W, k), 'D')
    stamp(g3, corner(CT_LADDER, k), ' ')               # hatch onto the tower roof
    for s in CT_SLITS:
        stamp(g0, corner(s, k), 'x', 'C'); stamp(g1, corner(s, k), 'x', 'C')

# ------------------------------------------------------------------ gatehouse
stamp(g0, PASSAGE, ':')                                 # passage floor runs through
stamp(g0, (37, 56, 38, 62), 'C'); stamp(g0, (42, 56, 43, 62), 'C')   # passage side walls
stamp(g0, (37, 58, 38, 59), 'D'); stamp(g0, (42, 58, 43, 59), 'D')   # guard room doors
stamp(g0, (38, 55, 42, 56), 'G'); stamp(g0, (38, 62, 42, 63), 'G')   # inner gate, outer portcullis
for xm in (33.5, 46):                                   # arrow slits in the twin towers
    stamp(g0, (xm, 66, xm + 0.5, 67), 'x', 'C'); stamp(g1, (xm, 66, xm + 0.5, 67), 'x', 'C')
for ym in (62.5, 64.5):
    stamp(g0, (31, ym, 32, ym + 0.5), 'x', 'C'); stamp(g0, (48, ym, 49, ym + 0.5), 'x', 'C')
    stamp(g1, (31, ym, 32, ym + 0.5), 'x', 'C'); stamp(g1, (48, ym, 49, ym + 0.5), 'x', 'C')
stamp(g1, (33, 56, 35, 60), ' ')                        # opening above the west guard-room stairs
for hx in (39, 40.5):                                   # murder holes over the passage
    stamp(g1, (hx, 59, hx + 0.5, 59.5), ' ')
stamp(g2, (45, 56, 47, 60), ' ')                        # opening above the gate-room stairs
stamp(g2, (32, 60, 33, 61), 'D'); stamp(g2, (47, 60, 48, 61), 'D')   # onto the wall walk
stamp(g3, (33, 61, 34, 62), ' ')                        # hatch to the gatehouse roof
notch(g0, CTOW.values(), [BAILEY]); notch(g1, CTOW.values(), [BAILEY]); notch(g2, CTOW.values(), [BAILEY]); notch(g3, CTOW.values(), [BAILEY])
for g in (g0, g1, g2, g3):
    notch(g, GATE_TOW, [GATE_MAIN, (0, 0, 80, 63)])

# ------------------------------------------------------------------ bailey: paths, farm
for r in [(39, 47, 41, 55), (38, 63, 42, 75),          # porch -> gate, gate -> road (ends inside the altar area)
          (18, 50, 62, 52),                              # cross path
          (22, 23, 24, 50), (56, 26, 58, 50)]:           # branches to the pen and the farm
    stamp(g0, r, ':', ' ')
stamp(g0, (52, 15, 62, 25), 'f')                         # farm plots
for y in range(sq(15), sq(25)):
    for x in range(sq(52), sq(62)):
        if x in (sq(52), sq(62) - 1) or y in (sq(15), sq(25) - 1):
            g0[y][x] = '='
stamp(g0, (56, 24.5, 58, 25), ':')                       # gap in the farm wall
stamp(g0, (56, 25, 58, 26), ':')

rows = lambda g: [''.join(r).rstrip() for r in g]

def item(i, lv, t, label, xm, ym, wm, dm, hm, rot, color, ox=0, oy=0):
    return {'id': i, 'level': lv, 'type': t, 'label': label, 'x': sq(xm + ox), 'y': sq(ym + oy), 'w': sq(wm), 'd': sq(dm), 'h': hm, 'rot': rot, 'color': color}
K = dict(ox=OX, oy=OY)

items = [
    # Keep (unchanged layout)
    item('altar', 'g', 'altar', 'Flame Altar', 13.5, 12.5, 3, 3, 3, 0, '#d9541e', **K),
    item('st1', 'g', 'stairs', 'Stairs up', 9, 11, 2, 4, 4, 0, '#a98a62', **K),
    item('wb', 'g', 'workbench', 'Workbench', 11.5, 8, 2, 2, 1, 0, '#9a7b52', **K),
    item('forge', 'g', 'forge', 'Forge', 14.5, 8, 2, 2, 2, 0, '#6f6a66', **K),
    item('stools', 'g', 'smithing-tools', 'Smithing Tools', 17.5, 8, 2, 2, 1, 0, '#5a6066', **K),
    item('smelt', 'g', 'smelter', 'Smelter', 20.5, 6.5, 2, 2, 3, 0, '#7b5a4a', **K),
    item('tan', 'g', 'tannery', 'Tanning Station', 7.5, 6.5, 2, 2, 1.5, 0, '#8b6a4a', **K),
    item('smith', 'g', 'npc-blacksmith', 'Blacksmith', 20.5, 19.5, 2, 2, 2, 180, '#5f6770', **K),
    item('alch', 'g', 'npc-alchemist', 'Alchemist', 7.5, 19.5, 2, 2, 2, 180, '#56806c', **K),
    *[item(f'mc{i}', 'g', 'mchest-small', 'Small Magic Chest', 20, 11 + i, 1, 1, 1, 270, '#7b68b5', **K) for i in range(6)],
    item('qs', 'g', 'quickstack', 'Quick Stack Station', 18.5, 17, 1, 1, 2, 270, '#4f7f8f', **K),
    item('lan1', 'g', 'light', 'Lantern', 13, 21, 1, 1, 1, 0, '#e3b341', **K),
    item('lan2', 'g', 'light', 'Lantern', 16, 21, 1, 1, 1, 0, '#e3b341', **K),
    item('st2', 'f1', 'stairs', 'Stairs up', 9, 16, 2, 4, 4, 180, '#a98a62', **K),
    item('hearth', 'f1', 'campfire', 'Hearth', 14, 8, 2, 2, 1, 0, '#c46a2a', **K),
    item('table', 'f1', 'table', 'Long table', 12, 12.5, 6, 1.5, 1, 0, '#9a7b52', **K),
    item('carp', 'f1', 'npc-carpenter', 'Carpenter', 20.5, 6.5, 2, 2, 2, 0, '#9a7344', **K),
    item('bard', 'f1', 'npc-bard', 'Bard', 20.5, 19.5, 2, 2, 2, 180, '#b0596f', **K),
    item('loom', 'f1', 'loom', 'Loom', 7.5, 6.5, 2, 2, 2, 0, '#a7896a', **K),
    item('spin', 'f1', 'spinning', 'Spinning Wheel', 11.5, 8, 2, 2, 1.5, 0, '#b49770', **K),
    item('alchst', 'f1', 'alchemy', 'Alchemy Station', 18, 16, 2, 2, 1.5, 270, '#5f7d6e', **K),
    item('st3', 'f2', 'stairs', 'Stairs to roof', 9, 11, 2, 4, 4, 0, '#a98a62', **K),
    item('bed1', 'f2', 'bed', 'Bed', 12, 8, 2, 3, 1, 0, '#8c6b4f', **K),
    item('bed2', 'f2', 'bed', 'Bed', 12, 16.5, 2, 3, 1, 180, '#8c6b4f', **K),
    item('bed3', 'f2', 'bed', 'Bed', 7.5, 6, 2, 3, 1, 0, '#8c6b4f', **K),
    item('bed4', 'f2', 'bed', 'Bed', 7, 19, 2, 3, 1, 180, '#8c6b4f', **K),
    item('mybed', 'f2', 'bed2', 'Your bed', 18, 8, 3, 3, 1, 0, '#7d5d43', **K),
    item('tub', 'f2', 'bathtub', 'Bathtub', 21, 19, 2, 3, 1, 180, '#6f8fa3', **K),
    item('desk', 'f2', 'table', 'Desk', 17, 13, 2, 1, 1, 0, '#9a7b52', **K),
    item('chest', 'f2', 'chest', 'Chest', 20.5, 6.5, 1, 1, 1, 0, '#8a5a2b', **K),
    item('banner', 'roof', 'custom', 'Banner pole', 15, 14, 1, 1, 6, 0, '#c4501a', **K),
    *[item(f'lad{k}', 'roof', 'ladder', 'Ladder up', lx, ly, 1, 1, 4, 0, '#8f7350', **K) for k, (lx, ly) in {'NW': (7, 6), 'NE': (22, 6), 'SW': (7, 21), 'SE': (22, 21)}.items()],
    # Gatehouse
    item('gst1', 'g', 'stairs', 'Stairs up', 33, 56, 2, 4, 4, 0, '#a98a62'),
    item('gst2', 'f1', 'stairs', 'Stairs up', 45, 56, 2, 4, 4, 0, '#a98a62'),
    item('guard1', 'g', 'chest', 'Armoury chest', 35.5, 60.5, 1, 1, 1, 0, '#8a5a2b'),
    item('guard2', 'g', 'table', 'Guard table', 44, 59, 2, 1, 1, 0, '#9a7b52'),
    item('glev', 'f1', 'lever', 'Gate lever (Sparkworks)', 37.5, 57, 1, 1, 1, 0, '#c9a227'),
    item('glad', 'f2', 'ladder', 'Ladder up', 33, 61, 1, 1, 4, 0, '#8f7350'),
    item('glan1', 'g', 'light', 'Lantern', 36.5, 53.5, 1, 1, 1, 0, '#e3b341'),
    item('glan2', 'g', 'light', 'Lantern', 42.5, 53.5, 1, 1, 1, 0, '#e3b341'),
    item('glan3', 'g', 'light', 'Lantern', 37, 67.5, 1, 1, 1, 0, '#e3b341'),
    item('glan4', 'g', 'light', 'Lantern', 42, 67.5, 1, 1, 1, 0, '#e3b341'),
    # Bailey
    item('pen', 'g', 'pen', 'Animal pen', 18.5, 14.5, 8, 8, 1, 0, '#a0905a'),
    item('trough', 'g', 'trough', 'Trough', 27.5, 17, 2, 1, 1, 90, '#8a7550'),
    item('farmer', 'g', 'npc-farmer', 'Farmer', 53, 26.5, 2, 2, 2, 0, '#7c9a3d'),
    item('seed', 'g', 'seedbed', 'Seedbed', 59, 26.5, 2, 2, 0.5, 0, '#6f8a43'),
    item('well', 'g', 'custom', 'Well', 34, 52.5, 2, 2, 1, 0, '#5f7f9a'),
]
for k in CTOW:
    for n, ((sr, srot), lv) in enumerate([(CT_STAIRS_G, 'g'), (CT_STAIRS_F1, 'f1')]):
        r = corner(sr, k)
        items.append(item(f'ct{k}{n}', lv, 'stairs', 'Stairs up', r[0], r[1], r[2] - r[0], r[3] - r[1], 4, corner_rot(srot, k), '#a98a62'))
    lr = corner(CT_LADDER, k)
    items.append(item(f'ctl{k}', 'f2', 'ladder', 'Ladder up', lr[0], lr[1], 1, 1, 4, 0, '#8f7350'))

# Stairs footprints are given unrotated (w x d); rotated ones swap back here.
for it in items:
    if it['type'] == 'stairs' and it['rot'] in (90, 270):
        it['w'], it['d'] = it['d'], it['w']

# Sanity check: items on open floor, no overlaps (stairs and ladders may sit over openings)
LV = {'g': g0, 'f1': g1, 'f2': g2, 'roof': g3, 'tt': g4}
FLOORS = set(',.:')
taken, problems = {}, []
for it in items:
    g = LV[it['level']]
    w, d = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
    for y in range(it['y'], it['y'] + d):
        for x in range(it['x'], it['x'] + w):
            if it['type'] != 'stairs' and g[y][x] not in FLOORS and not (it['level'] == 'g' and g[y][x] == ' '):
                problems.append(f"{it['id']} on '{g[y][x]}' at {x / C},{y / C} m")
            key = (it['level'], x, y)
            if key in taken: problems.append(f"{it['id']} overlaps {taken[key]} at {x / C},{y / C} m")
            taken[key] = it['id']
print('item problems:', len(problems))
for p_ in problems[:40]: print('  ', p_)

def kz(i, lv, name, r, color, ox=OX, oy=OY):
    return {'id': i, 'level': lv, 'name': name, 'x': sq(r[0] + ox), 'y': sq(r[1] + oy), 'w': sq(r[2] - r[0]), 'h': sq(r[3] - r[1]), 'color': color}
zones = [
    kz('zw', 'g', 'Workshop', (9, 8, 21, 20), '#c4501a'),
    kz('zh', 'f1', 'Great hall', (9, 8, 21, 20), '#2f7fb3'),
    kz('zt', 'f1', 'Terrace', (12.5, 21, 17.5, 24.5), '#3f8a4f'),
    kz('zb', 'f2', 'Bunk room', (9, 8, 15.5, 20), '#8a5cc2'),
    kz('zc', 'f2', 'Your chamber', (16, 8, 21, 20), '#c2416e'),
    kz('zr', 'roof', 'Keep roof', (9, 8, 21, 20), '#2f8f8a'),
    kz('zpass', 'g', 'Gate passage', (38, 56, 42, 62), '#b8862b', 0, 0),
    kz('zgw', 'g', 'Guard room', (33, 56, 37, 62), '#5f6770', 0, 0),
    kz('zfarm', 'g', 'Farm', (52.5, 15.5, 61.5, 24.5), '#3f8a4f', 0, 0),
    kz('zpen', 'g', 'Animals', (18, 14, 31, 23), '#a0905a', 0, 0),
    kz('zyard', 'g', 'Open yard (future builds)', (17, 26, 31, 49), '#8a5cc2', 0, 0),
    kz('zyard2', 'g', 'Open yard (future builds)', (49, 28, 63, 49), '#8a5cc2', 0, 0),
    kz('zwalk', 'f2', 'Wall walk', (14, 10, 66, 12), '#2f8f8a', 0, 0),
]

palette = {
    # Real blocks from the planner's block catalogue (enshrouded.wiki.gg names, icon-sampled colours)
    '#': {'name': 'Castle Wall Stone Block', 'kind': 'wall', 'color': '#75726e'},
    'K': {'name': 'Granite Block', 'kind': 'wall', 'color': '#676a6f'},
    'C': {'name': 'Citywall Block', 'kind': 'wall', 'color': '#6f6f69'},
    'W': {'name': 'Refined Wood Block', 'kind': 'wall', 'color': '#75675f'},
    'M': {'name': 'Castle Wall Stone Block', 'kind': 'wall', 'color': '#75726e', 'height': 2},
    'c': {'name': 'Castle Wall Stone Block', 'kind': 'block', 'color': '#75726e', 'height': 1},
    '=': {'name': 'Rough Stone Block', 'kind': 'block', 'color': '#7d776a', 'height': 1},
    ',': {'name': 'Castle Block', 'kind': 'floor', 'color': '#7c8084'},
    '.': {'name': 'Refined Wood Block', 'kind': 'floor', 'color': '#75675f'},
    ':': {'name': 'Smooth Stone Road Block', 'kind': 'floor', 'color': '#746553'},
    'f': {'name': 'Farm Soil', 'kind': 'floor', 'color': '#90450d'},
    # Not blocks
    'D': {'name': 'Door', 'kind': 'door', 'color': '#7b4a26'},
    'G': {'name': 'Gate / portcullis', 'kind': 'door', 'color': '#4d3a2a'},
    'o': {'name': 'Window', 'kind': 'window', 'color': '#8fc3df'},
    'x': {'name': 'Arrow slit', 'kind': 'window', 'color': '#6f8fa8'},
}

notes = """Small castle keep with a curtain wall and gatehouse, drafted by Claude. Uses 0.5 m squares, so every square is one single block.

MATERIALS (real blocks, see the planner's block catalogue)
- Keep and battlements: Castle Wall Stone Block. Merlons are 2 m, crenels 1 m.
- Keep towers: Granite Block. Curtain wall and gatehouse: Citywall Block.
- Floors: Castle Block downstairs, Refined Wood Block upstairs. The timber partition is Refined Wood Block too.
- Roads: Smooth Stone Road Block. Farm: Farm Soil inside Rough Stone Block walls.
- Not blocks: doors, gates, windows and arrow slits.

ALTAR
- Altar level 2 (80 m build area) is enough. The castle spans about 60 x 61 m around the altar, which sits in the middle of the keep.
- That leaves roughly 8-10 m of margin on each side, so level 4 isn't needed. Level 3 (120 m) is worth it if you want room outside the walls later.
- The canvas is 80 x 80 m, the most a 0.5 m plan can hold.

CURTAIN WALL
- Encloses a 48 x 48 m bailey. The wall is 2 m (4 blocks) thick and 8 m tall.
- Its top is a 1.5 m wall walk behind 2 m merlons and 1 m crenels.
- Four 8 x 8 m corner towers rise to 12 m with battlemented roofs.
- Each tower has a door to the bailey, stairs inside up to the wall walk (doors onto both walks), and a ladder to its roof.

GATEHOUSE
- South side, lined up with the keep's porch.
- Twin towers project 4 m beyond the wall.
- A 4 m wide passage has an outer portcullis and an inner gate.
- Guard rooms on both sides, a gate room above with two murder holes, and a Sparkworks lever for the gate.
- Stairs go up to the top storey, which has doors onto the wall walk and a ladder to the roof. It's 12 m tall.

BAILEY
- Path from the gate to the porch, plus a cross path.
- Walled farm plots NE with the Farmer, an animal pen NW, and a well.
- Two open yards are marked for future buildings (stables, workshops, storage).

KEEP
- Unchanged from the first draft, just moved to the centre. See the zones on each level.

TO TUNE
- Crafting stations are 2 x 2 m placeholders until measured in game. Other furniture sizes are estimates.
- The curtain is 8 m tall. Drop it to 6 m if the wall walk feels too high: change the level heights or the merlon heights.
"""

plan = {
    'v': 1, 'name': 'Castle keep with curtain wall', 'project': 'Castle', 'notes': notes, 'cell': 0.5, 'w': W, 'h': H, 'altar': 80,
    'palette': palette,
    'levels': [
        {'id': 'g', 'name': 'Ground', 'elev': 0, 'height': 4, 'hidden': False, 'rows': rows(g0)},
        {'id': 'f1', 'name': 'First floor', 'elev': 4, 'height': 4, 'hidden': False, 'rows': rows(g1)},
        {'id': 'f2', 'name': 'Second floor & wall walk', 'elev': 8, 'height': 4, 'hidden': False, 'rows': rows(g2)},
        {'id': 'roof', 'name': 'Roofs (12 m)', 'elev': 12, 'height': 4, 'hidden': False, 'rows': rows(g3)},
        {'id': 'tt', 'name': 'Keep tower tops', 'elev': 16, 'height': 2, 'hidden': False, 'rows': rows(g4)},
    ],
    'items': items, 'zones': zones,
    'rev': f'r-claude-walls-{int(time.time())}', 'editor': 'claude', 'updatedAt': int(time.time() * 1000),
}
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'castle-walls.json')
json.dump(plan, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
print('bytes', len(json.dumps(plan, ensure_ascii=False).encode('utf-8')))

# Quick overview at 1 m per character (top-left square of each 2 x 2)
import sys
for name, g in [('ground', g0), ('wall walk level', g2)]:
    print(f'--- {name}')
    for y in range(0, H, 2):
        print(''.join(g[y][x] for x in range(0, W, 2)).rstrip())
