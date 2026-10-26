"""Draft: small castle keep, 0.5 m squares (1 square = one single block).

Run: python castle_keep.py  ->  writes castle-keep.json next to this script.
Coordinates below are written in metres and converted to squares (x2).
"""
import json, os, time

C = 2            # squares per metre
W = H = 32 * C   # 32 x 32 m canvas

def sq(m): return int(round(m * C))

KEEP = (8, 7, 22, 21)                      # x0, y0, x1, y1 in metres (outer faces)
TOWERS = {                                 # 5 x 5 m corner towers
    'NW': (6, 5, 11, 10), 'NE': (19, 5, 24, 10),
    'SW': (6, 18, 11, 23), 'SE': (19, 18, 24, 23),
}
FORE = (12, 21, 18, 25)                    # entrance porch

def in_rect(x, y, r):
    return sq(r[0]) <= x < sq(r[2]) and sq(r[1]) <= y < sq(r[3])

def chamfered(x, y):
    # Knock the outer corners off each tower so it reads rounder.
    for r in TOWERS.values():
        if not in_rect(x, y, r):
            continue
        for cx, cy in [(sq(r[0]), sq(r[1])), (sq(r[2]) - 1, sq(r[1])), (sq(r[0]), sq(r[3]) - 1), (sq(r[2]) - 1, sq(r[3]) - 1)]:
            if in_rect(cx, cy, KEEP):
                continue
            if abs(x - cx) + abs(y - cy) <= 1:
                return True
    return False

def inside(x, y):
    if not (0 <= x < W and 0 <= y < H):
        return False
    return in_rect(x, y, KEEP) or any(in_rect(x, y, r) for r in TOWERS.values())

def notch(g):
    """Cosmetic: knock the outermost corner block off each tower."""
    for r in TOWERS.values():
        for cx, cy in [(sq(r[0]), sq(r[1])), (sq(r[2]) - 1, sq(r[1])), (sq(r[0]), sq(r[3]) - 1), (sq(r[2]) - 1, sq(r[3]) - 1)]:
            if not in_rect(cx, cy, KEEP):
                g[cy][cx] = ' '
    return g

def ring(x, y, radius):
    """Inside the keep outline and within `radius` squares of its edge."""
    if not inside(x, y):
        return False
    return any(not inside(x + dx, y + dy) for dx in range(-radius, radius + 1) for dy in range(-radius, radius + 1))

def tower_of(x, y):
    for k, r in TOWERS.items():
        if in_rect(x, y, r):
            return k
    return None

def blank(): return [[' '] * W for _ in range(H)]

def stamp(g, x0, y0, x1, y1, ch, only=None):
    """Fill a metre rectangle; `only` limits it to cells already holding one of those chars."""
    for y in range(sq(y0), sq(y1)):
        for x in range(sq(x0), sq(x1)):
            if 0 <= x < W and 0 <= y < H and (only is None or g[y][x] in only):
                g[y][x] = ch

def shell(floor):
    """Walls (2 blocks = 1 m thick) following the keep + tower outline, floor inside."""
    g = blank()
    for y in range(H):
        for x in range(W):
            if inside(x, y):
                g[y][x] = ('K' if tower_of(x, y) and not in_rect(x, y, KEEP) else '#') if ring(x, y, 2) else floor
    return g

def battlement(x, y):
    # Alternate 2 m merlons and 1 m crenels every metre along the edge.
    return 'M' if ((x // C) + (y // C)) % 2 == 0 else 'c'

# ---------------------------------------------------------------- Ground floor
g0 = shell(',')
# Arrow slits (single block wide) on the straight keep faces and the tower faces
for xm in (13, 15, 17):                     stamp(g0, xm, 7, xm + 0.5, 8, 'x', '#K')
for ym in (12, 14, 16):
    stamp(g0, 8, ym, 9, ym + 0.5, 'x', '#K'); stamp(g0, 21, ym, 22, ym + 0.5, 'x', '#K')
for k, (x0, y0, x1, y1) in TOWERS.items():
    xm = (x0 + x1) / 2 - 0.25; ym = (y0 + y1) / 2 - 0.25
    if k[0] == 'N': stamp(g0, xm, y0, xm + 0.5, y0 + 1, 'x', 'K')
    else:           stamp(g0, xm, y1 - 1, xm + 0.5, y1, 'x', 'K')
    if k[1] == 'W': stamp(g0, x0, ym, x0 + 1, ym + 0.5, 'x', 'K')
    else:           stamp(g0, x1 - 1, ym, x1, ym + 0.5, 'x', 'K')
# Porch: walls on three sides, door out, door into the keep
for y in range(sq(FORE[1]), sq(FORE[3])):
    for x in range(sq(FORE[0]), sq(FORE[2])):
        g0[y][x] = '#' if (x < sq(FORE[0] + 1) or x >= sq(FORE[2] - 1) or y >= sq(FORE[3] - 1)) else ','
stamp(g0, 14, 20, 16, 21, 'D')             # keep door (2 m wide)
stamp(g0, 14, 24, 16, 25, 'D')             # porch door
stamp(g0, 14, 25, 16, 32, ':')             # approach path

# ---------------------------------------------------------------- First floor
g1 = shell('.')
for xm in (12.5, 16.5):                     stamp(g1, xm, 7, xm + 1, 8, 'o', '#')
for ym in (13, 16):
    stamp(g1, 8, ym, 9, ym + 1, 'o', '#'); stamp(g1, 21, ym, 22, ym + 1, 'o', '#')
for k, (x0, y0, x1, y1) in TOWERS.items():
    xm = (x0 + x1) / 2 - 0.25
    stamp(g1, xm, y0 if k[0] == 'N' else y1 - 1, xm + 0.5, (y0 + 1) if k[0] == 'N' else y1, 'x', 'K')
stamp(g1, 9, 11, 11, 15, ' ')              # stairwell from below
stamp(g1, 14, 20, 16, 21, 'D')             # door onto the porch roof
for y in range(sq(21), sq(25)):            # porch roof terrace with a low parapet
    for x in range(sq(12), sq(18)):
        g1[y][x] = '=' if (x == sq(12) or x == sq(18) - 1 or y == sq(25) - 1) else ','

# ---------------------------------------------------------------- Second floor
g2 = shell('.')
for xm in (12.5, 16.5):
    stamp(g2, xm, 7, xm + 1, 8, 'o', '#'); stamp(g2, xm, 20, xm + 1, 21, 'o', '#')
for ym in (13, 16):
    stamp(g2, 8, ym, 9, ym + 1, 'o', '#'); stamp(g2, 21, ym, 22, ym + 1, 'o', '#')
stamp(g2, 9, 16, 11, 20, ' ')              # stairwell from below
stamp(g2, 15.5, 8, 16, 20, 'W', '.')       # timber partition (single block thick)
stamp(g2, 15.5, 16, 16, 17, 'D')           # doorway in the partition

# ---------------------------------------------------------------- Roof
g3 = blank()
for y in range(H):
    for x in range(W):
        if inside(x, y):
            g3[y][x] = battlement(x, y) if ring(x, y, 1) else ','
for k, r in TOWERS.items():                # towers rise a storey above the wall walk
    for y in range(sq(r[1]), sq(r[3])):
        for x in range(sq(r[0]), sq(r[2])):
            if not inside(x, y):
                continue
            edge = any(not (in_rect(x + dx, y + dy, r) and inside(x + dx, y + dy)) for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2))
            g3[y][x] = 'K' if edge else ','
door_x = {'NW': 9, 'SW': 9, 'NE': 20, 'SE': 20}
for k, r in TOWERS.items():                # doorway from the wall walk into each tower
    dy0 = r[3] - 1 if k[0] == 'N' else r[1]
    stamp(g3, door_x[k], dy0, door_x[k] + 1, dy0 + 1, 'D')
stamp(g3, 9, 11, 11, 15, ' ')              # hatch over the last flight

# ---------------------------------------------------------------- Tower tops
g4 = blank()
for k, r in TOWERS.items():
    for y in range(sq(r[1]), sq(r[3])):
        for x in range(sq(r[0]), sq(r[2])):
            if not inside(x, y):
                continue
            edge = any(not (in_rect(x + dx, y + dy, r) and inside(x + dx, y + dy)) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            g4[y][x] = battlement(x, y) if edge else ','

# Ladders from each tower room up to its lookout, with a hatch above
LADDERS = {'NW': (7, 6), 'NE': (22, 6), 'SW': (7, 21), 'SE': (22, 21)}
for lx, ly in LADDERS.values(): stamp(g4, lx, ly, lx + 1, ly + 1, ' ')
for _g in (g0, g1, g2, g3, g4): notch(_g)
rows = lambda g: [''.join(r).rstrip() for r in g]

def item(i, lv, t, label, xm, ym, wm, dm, hm, rot, color):
    return {'id': i, 'level': lv, 'type': t, 'label': label, 'x': sq(xm), 'y': sq(ym), 'w': sq(wm), 'd': sq(dm), 'h': hm, 'rot': rot, 'color': color}

items = [
    # Ground: workshop around the altar
    item('altar', 'g', 'altar', 'Flame Altar', 13.5, 12.5, 3, 3, 3, 0, '#d9541e'),
    item('st1', 'g', 'stairs', 'Stairs up', 9, 11, 2, 4, 4, 0, '#a98a62'),
    item('wb', 'g', 'workbench', 'Workbench', 11.5, 8, 3, 2, 1, 0, '#9a7b52'),
    item('forge', 'g', 'forge', 'Forge', 15, 8, 3, 2, 2, 0, '#6f6a66'),
    item('anvil', 'g', 'anvil', 'Anvil', 18.5, 8.5, 2, 1, 1, 0, '#5a6066'),
    item('smelt', 'g', 'smelter', 'Smelter', 20.5, 6.5, 2, 2, 3, 0, '#7b5a4a'),
    item('tan', 'g', 'tannery', 'Tanning station', 7.5, 6.5, 2, 2, 2, 0, '#8b6a4a'),
    item('smith', 'g', 'npc-blacksmith', 'Blacksmith', 20.5, 19.5, 2, 2, 2, 180, '#5f6770'),
    item('alch', 'g', 'npc-alchemist', 'Alchemist', 7.5, 19.5, 2, 2, 2, 180, '#56806c'),
    *[item(f'mc{i}', 'g', 'chest-m', 'Magic chest', 20, 11 + i, 1, 1, 1, 270, '#6b5aa8') for i in range(6)],
    item('qs', 'g', 'quickstack', 'Quick Stack', 18.5, 17, 1, 1, 2, 270, '#4f7f8f'),
    item('lan1', 'g', 'light', 'Lantern', 13, 21, 1, 1, 1, 0, '#e3b341'),
    item('lan2', 'g', 'light', 'Lantern', 16, 21, 1, 1, 1, 0, '#e3b341'),
    # First: great hall
    item('st2', 'f1', 'stairs', 'Stairs up', 9, 16, 2, 4, 4, 180, '#a98a62'),
    item('hearth', 'f1', 'campfire', 'Hearth', 14, 8, 2, 2, 1, 0, '#c46a2a'),
    item('table', 'f1', 'table', 'Long table', 12, 12.5, 6, 1.5, 1, 0, '#9a7b52'),
    item('carp', 'f1', 'npc-carpenter', 'Carpenter', 20.5, 6.5, 2, 2, 2, 0, '#9a7344'),
    item('bard', 'f1', 'npc-bard', 'Bard', 20.5, 19.5, 2, 2, 2, 180, '#b0596f'),
    item('loom', 'f1', 'loom', 'Loom', 7.5, 6.5, 2, 2, 2, 0, '#a7896a'),
    item('spin', 'f1', 'spinning', 'Spinning wheel', 11.5, 8, 2, 1, 2, 0, '#b49770'),
    item('alchst', 'f1', 'alchemy', 'Alchemy station', 18, 16, 2, 2, 2, 270, '#5f7d6e'),
    # Second: bunk room (west) and your chamber (east)
    item('st3', 'f2', 'stairs', 'Stairs to roof', 9, 11, 2, 4, 4, 0, '#a98a62'),
    item('bed1', 'f2', 'bed', 'Bed', 12, 8, 2, 3, 1, 0, '#8c6b4f'),
    item('bed2', 'f2', 'bed', 'Bed', 12, 16.5, 2, 3, 1, 180, '#8c6b4f'),
    item('bed3', 'f2', 'bed', 'Bed', 7.5, 6, 2, 3, 1, 0, '#8c6b4f'),
    item('bed4', 'f2', 'bed', 'Bed', 7, 19, 2, 3, 1, 180, '#8c6b4f'),
    item('mybed', 'f2', 'bed2', 'Your bed', 18, 8, 3, 3, 1, 0, '#7d5d43'),
    item('tub', 'f2', 'bathtub', 'Bathtub', 21, 19, 2, 3, 1, 180, '#6f8fa3'),
    item('desk', 'f2', 'table', 'Desk', 17, 13, 2, 1, 1, 0, '#9a7b52'),
    item('chest', 'f2', 'chest', 'Chest', 20.5, 6.5, 1, 1, 1, 0, '#8a5a2b'),
    # Roof
    item('banner', 'roof', 'custom', 'Banner pole', 15, 14, 1, 1, 6, 0, '#c4501a'),
    *[item(f'lad{k}', 'roof', 'ladder', 'Ladder up', lx, ly, 1, 1, 4, 0, '#8f7350') for k, (lx, ly) in LADDERS.items()],
]

# Sanity check: every non-stair item must sit on open floor, clear of walls, holes and other items.
LV = {'g': 'g0', 'f1': 'g1', 'f2': 'g2', 'roof': 'g3', 'tt': 'g4'}
FLOORS = set(',.:')
taken = {}
problems = []
for it in items:
    g = globals()[LV[it['level']]]
    w, d = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
    for y in range(it['y'], it['y'] + d):
        for x in range(it['x'], it['x'] + w):
            if it['type'] != 'stairs' and g[y][x] not in FLOORS:
                problems.append(f"{it['id']} on '{g[y][x]}' at {x/C},{y/C} m")
            key = (it['level'], x, y)
            if key in taken:
                problems.append(f"{it['id']} overlaps {taken[key]} at {x/C},{y/C} m")
            taken[key] = it['id']
print('item problems:', len(problems))
for p_ in problems[:40]: print('  ', p_)

zones = [
    {'id': 'zw', 'level': 'g', 'name': 'Workshop', 'x': sq(9), 'y': sq(8), 'w': sq(12), 'h': sq(12), 'color': '#c4501a'},
    {'id': 'zp', 'level': 'g', 'name': 'Porch', 'x': sq(13), 'y': sq(21), 'w': sq(4), 'h': sq(3), 'color': '#b8862b'},
    {'id': 'zh', 'level': 'f1', 'name': 'Great hall', 'x': sq(9), 'y': sq(8), 'w': sq(12), 'h': sq(12), 'color': '#2f7fb3'},
    {'id': 'zt', 'level': 'f1', 'name': 'Terrace', 'x': sq(12.5), 'y': sq(21), 'w': sq(5), 'h': sq(3.5), 'color': '#3f8a4f'},
    {'id': 'zb', 'level': 'f2', 'name': 'Bunk room', 'x': sq(9), 'y': sq(8), 'w': sq(6.5), 'h': sq(12), 'color': '#8a5cc2'},
    {'id': 'zc', 'level': 'f2', 'name': 'Your chamber', 'x': sq(16), 'y': sq(8), 'w': sq(5), 'h': sq(12), 'color': '#c2416e'},
    {'id': 'zr', 'level': 'roof', 'name': 'Wall walk', 'x': sq(9), 'y': sq(8), 'w': sq(12), 'h': sq(12), 'color': '#2f8f8a'},
]

palette = {
    '#': {'name': 'Keep stone wall', 'kind': 'wall', 'color': '#7f8a93'},
    'K': {'name': 'Tower stone wall', 'kind': 'wall', 'color': '#69737d'},
    'W': {'name': 'Timber partition', 'kind': 'wall', 'color': '#9a6a3c'},
    'M': {'name': 'Merlon (2 m)', 'kind': 'wall', 'color': '#8a949c', 'height': 2},
    'c': {'name': 'Crenel (1 m)', 'kind': 'block', 'color': '#9ea7ad', 'height': 1},
    '=': {'name': 'Low parapet', 'kind': 'block', 'color': '#8f9a86', 'height': 1},
    ',': {'name': 'Stone floor', 'kind': 'floor', 'color': '#a9b0b3'},
    '.': {'name': 'Wood floor', 'kind': 'floor', 'color': '#c9a574'},
    ':': {'name': 'Path', 'kind': 'floor', 'color': '#b9a98a'},
    'D': {'name': 'Door', 'kind': 'door', 'color': '#7b4a26'},
    'o': {'name': 'Window', 'kind': 'window', 'color': '#8fc3df'},
    'x': {'name': 'Arrow slit', 'kind': 'window', 'color': '#6f8fa8'},
}

notes = """Small castle keep, drafted by Claude. Uses 0.5 m squares, so every square is one single block.

FOOTPRINT
- 14 x 14 m keep with four 5 x 5 m corner towers (18 x 18 m overall), plus a 6 x 4 m entrance porch on the south side.
- Walls are 1 m (2 blocks) thick. Tower corners are chamfered by one block so they read rounder.
- Four storeys of 4 m, then tower tops. Overall height is about 18 m to the top of the tower merlons.
- Fits easily inside a level 1 altar area (40 m), with the altar inside the keep.

LEVELS
- Ground (0 m): workshop around the Flame Altar.
  - Forge corner to the NE, smelter in the NW tower.
  - A wall of magic chests and a Quick Stack on the east side.
  - Blacksmith and Alchemist in the south towers.
  - Arrow slits all round. 2 m doors through the porch.
- First (4 m): great hall with a hearth and a long table.
  - Craftspeople in the tower bays.
  - A door out onto the porch roof terrace.
- Second (8 m): bunk room for survivors (west), and your chamber with bath (east), behind a single-block timber partition.
- Roof (12 m): wall walk behind 2 m merlons and 1 m crenels. Doors into all four towers, which rise one more storey. A ladder in each tower climbs to its lookout.
- Tower tops (16 m): small lookout platforms.

STAIRS
- Switchback flights along the west wall, each 2 x 4 m rising 4 m.
- Leave the floor open above each flight. The plan shows the gaps.

TO TUNE
- Station and furniture sizes are estimates. Measure them in game and resize the items.
- Want a raised entrance (very castle)? Move the keep door up to the first floor and turn the porch into a stair tower.
"""

plan = {
    'v': 1, 'name': 'Small castle keep', 'project': 'Castle', 'notes': notes, 'cell': 0.5, 'w': W, 'h': H, 'altar': 40,
    'palette': palette,
    'levels': [
        {'id': 'g', 'name': 'Ground: workshop', 'elev': 0, 'height': 4, 'hidden': False, 'rows': rows(g0)},
        {'id': 'f1', 'name': 'First: great hall', 'elev': 4, 'height': 4, 'hidden': False, 'rows': rows(g1)},
        {'id': 'f2', 'name': 'Second: quarters', 'elev': 8, 'height': 4, 'hidden': False, 'rows': rows(g2)},
        {'id': 'roof', 'name': 'Roof: wall walk', 'elev': 12, 'height': 4, 'hidden': False, 'rows': rows(g3)},
        {'id': 'tt', 'name': 'Tower tops', 'elev': 16, 'height': 2, 'hidden': False, 'rows': rows(g4)},
    ],
    'items': items, 'zones': zones,
    'rev': 'r-claude-keep-1', 'editor': 'claude', 'updatedAt': int(time.time() * 1000),
}
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'castle-keep.json')
json.dump(plan, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
for name, g in [('ground', g0), ('first', g1), ('second', g2), ('roof', g3), ('towers', g4)]:
    print(f'--- {name}')
    for r in g[8:52]:
        print(''.join(r[8:52]))
print('bytes', len(json.dumps(plan)))
