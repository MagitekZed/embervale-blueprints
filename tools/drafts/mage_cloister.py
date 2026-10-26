"""Mage library: herb garden cloister and north range, 0.5 m detail plan (every square is one single block).

Run: python mage_cloister.py  ->  writes mage-cloister.json
Local coordinates: the site plan's cloister corner (57, 4) sits at (2, 2) here.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mage_common import Plan, PALETTE

# Extra real blocks for this plan (names/colours from the block catalogue)
PALETTE['m'] = {'name': 'Mycelium Overgrown Block', 'kind': 'wall', 'color': '#72664f'}
PALETTE['E'] = {'name': 'Weathered Stone Block', 'kind': 'block', 'color': '#6a6c67', 'height': 0.5}   # bed edging
PALETTE['L'] = {'name': 'Limestone Block', 'kind': 'block', 'color': '#a79a88', 'height': 1.5}         # fountain tier
PALETTE['N'] = {'name': 'Temple Stones (arch haunch)', 'kind': 'block', 'color': '#857f5d', 'height': 1.5, 'base': 2.5, 'under': ','}
PALETTE['n'] = {'name': 'Temple Stones (arch crown)', 'kind': 'block', 'color': '#857f5d', 'height': 1, 'base': 3, 'under': ','}

P = Plan('Mage library: herb garden cloister', 0.5, 54, 60, 160)
P.project = 'Mage library'
g0 = P.level('g0', 'Ground: cloister & north range', 0, 4)
g1 = P.level('g1', 'Upper floor & arcade roof walk', 4, 4)
g2 = P.level('g2', 'Roofs', 8, 4)

# ---------------------------------------------------------------- key lines (metres)
X0, X1 = 2, 50          # outer east-west faces
RY0, RY1 = 2, 13        # north range: outer north face, south face (shared with the cloister)
CY1 = 54                # cloister outer south face
COL_W, COL_E = 6, 45    # colonnade lines (west line x 6-7, east line x 45-46)
COL_N, COL_S = 16, 49   # colonnade lines (north y 16-17, south y 49-50)
GX0, GX1, GY0, GY1 = 7, 45, 17, 49      # garden
CX, CY = 26.0, 33.0                     # fountain centre
COLS_X = [COL_W + 3 * k for k in range(14)]   # 6, 9, ... 45
COLS_Y = [COL_N + 3 * k for k in range(12)]   # 16, 19, ... 49

# ================================================================= ground
# north range shell + cloister outer walls
P.box_walls(g0, X0, RY0, X1, RY1, 'A', 1, floor=',')
P.box_walls(g0, X0, RY1 - 1, X1, CY1, 'A', 1, floor=',')
P.scatter(g0, 0, 0, 54, 60, 'm', 0.14, 'A', 401)                       # overgrown wall patches
# range partitions: lab | workshop | greenhouse
P.rect(g0, 20, 3, 21, 12, 'A'); P.rect(g0, 20, 7, 21, 9, 'D')
P.rect(g0, 35, 3, 36, 12, 'A'); P.rect(g0, 35, 7, 36, 9, 'D')
P.rect(g0, 36, RY0, X1 - 1, RY0 + 1, 'q', only='Am'); P.rect(g0, X1 - 1, RY0 + 1, X1, RY1 - 1, 'q', only='Am')   # greenhouse glass
for x in (40, 44): P.rect(g0, x, RY0, x + 0.5, RY0 + 1, 'A')                    # glass mullion piers
P.rect(g0, X1 - 1, 7, X1, 7.5, 'A')
for x in (5, 9, 13, 17): P.rect(g0, x, RY0, x + 1, RY0 + 1, 'o', only='Am')     # lab windows
for x in (24, 28, 32): P.rect(g0, x, RY0, x + 1, RY0 + 1, 'O', only='Am')       # workshop stained glass
for x in (10, 25, 41): P.rect(g0, x, RY1 - 1, x + 2, RY1, 'D')                  # doors onto the arcade
# workshop arcane circle
P.ring_wall(g0, 28, 8, 2.2, 'g', 0.5)
P.radial(g0, 28, 8, [0, 90, 180, 270], 0.25, 0.4, 1.6, 'g')
# greenhouse beds
for y0 in (4, 8.5):
    P.rect(g0, 37, y0, 48, y0 + 2.5, 'E'); P.rect(g0, 37.5, y0 + 0.5, 47.5, y0 + 2, 'f')
P.rect(g0, 36, 6.5, 49, 8.5, ':'); P.rect(g0, 36, 11, 49, 12, ':')
# lab shelving along the west wall
P.rect(g0, 3, 3, 3.5, 7, 'y')

# arcade, colonnade and arches
P.rect(g0, 3, RY1, X1 - 1, CY1 - 1, ',', only=',')
P.scatter(g0, 3, RY1, X1 - 1, CY1 - 1, ';', 0.22, ',', 402)
def colonnade(horizontal, line, positions):
    for k, p in enumerate(positions):
        if horizontal: P.rect(g0, p, line, p + 1, line + 1, 'P')
        else:          P.rect(g0, line, p, line + 1, p + 1, 'P')
        if k + 1 < len(positions):                       # arch over the 2 m gap: haunch, crown, crown, haunch
            for j, ch in enumerate('NnnN'):
                a = p + 1 + j * 0.5
                if horizontal: P.rect(g0, a, line, a + 0.5, line + 1, ch)
                else:          P.rect(g0, line, a, line + 1, a + 0.5, ch)
colonnade(True, COL_N, COLS_X); colonnade(True, COL_S, COLS_X)
colonnade(False, COL_W, COLS_Y); colonnade(False, COL_E, COLS_Y)

# garden
P.rect(g0, GX0, GY0, GX1, GY1, 'h')
P.rect(g0, GX0, GY0, GX1, GY0 + 1, ':'); P.rect(g0, GX0, GY1 - 1, GX1, GY1, ':')     # perimeter gravel walk
P.rect(g0, GX0, GY0, GX0 + 1, GY1, ':'); P.rect(g0, GX1 - 1, GY0, GX1, GY1, ':')
P.rect(g0, 25, GY0, 27, GY1, ':'); P.rect(g0, GX0, 32, GX1, 34, ':')               # cross paths (in line with the arch gaps)

# herb beds, north quadrants: raised beds with weathered-stone edging, kept clear of the fountain plaza
def bed(x0, y0, x1, y1):
    corners = [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]
    if min(math.hypot(x - CX, y - CY) for x, y in corners) < 6.0:
        return False
    P.rect(g0, x0, y0, x1, y1, 'E'); P.rect(g0, x0 + 0.5, y0 + 0.5, x1 - 0.5, y1 - 0.5, 'f')
    return True
for y0 in (19, 22.5, 26, 29.5):
    for (x0, x1) in ((9, 16), (17.5, 24), (28, 34.5), (36, 43)):
        if not bed(x0, y0, x1, y0 + 2):            # too close to the fountain: keep a shorter bed on the outer end
            if x1 <= CX: bed(x0, y0, x0 + 3.5, y0 + 2)
            else:        bed(x1 - 3.5, y0, x1, y0 + 2)
for y0 in (19, 22.5, 26, 29.5):                                                      # gravel between the beds
    P.rect(g0, GX0 + 1, y0 + 2, 25, y0 + 3.5, ':', only='h'); P.rect(g0, 27, y0 + 2, GX1 - 1, y0 + 3.5, ':', only='h')
P.rect(g0, GX0 + 1, GY0 + 1, 25, 19, ':', only='h'); P.rect(g0, 27, GY0 + 1, GX1 - 1, 19, ':', only='h')

# fountain plaza: two-tier basin with a spire
P.disc(g0, CX, CY, 5.5, ',')
P.scatter(g0, CX - 6, CY - 6, CX + 6, CY + 6, ';', 0.2, ',', 403)
P.disc(g0, CX, CY, 4.0, '~')
P.ring_wall(g0, CX, CY, 4.0, 'w', 0.5)
P.disc(g0, CX, CY, 1.6, 'L')
P.disc(g0, CX, CY, 0.6, ',')

# south lawns: lily pond with stepping stones (SE), ruins (SW), moss
P.disc(g0, 37, 41, 3.6, ';', only='h'); P.disc(g0, 40.5, 44, 2.6, ';', only='h')
P.disc(g0, 37, 41, 3.0, '~'); P.disc(g0, 40.5, 44, 2.0, '~')
for (x, y) in ((34.5, 39.5), (35.5, 41), (37, 42), (38.5, 42.5), (40, 43.5)):
    P.rect(g0, x, y, x + 0.5, y + 0.5, ';')
P.rect(g0, 10, 39, 10.5, 45, 'R'); P.rect(g0, 10, 45, 15, 45.5, 'R'); P.rect(g0, 12.5, 45, 13.5, 45.5, 'h')
P.scatter(g0, GX0, 36, 25, GY1 - 1, 'V', 0.025, 'h', 404)
P.scatter(g0, 27, 36, GX1, GY1 - 1, 'V', 0.015, 'h', 405)
P.scatter(g0, 3, RY1, X1 - 1, CY1 - 1, 'V', 0.01, ',;', 406)

# gates and doors in the outer wall, approach path
P.rect(g0, 23.5, CY1 - 1, 28.5, CY1, 'G')
P.rect(g0, X0, 32, X0 + 1, 34, 'D'); P.rect(g0, X1 - 1, 32, X1, 34, 'D')
P.rect(g0, 23.5, CY1, 28.5, 60, ':')
P.rect(g0, 0, 32, X0, 34, ':'); P.rect(g0, X1, 32, 54, 34, ':')

# ================================================================= upper floor (4-8 m)
P.box_walls(g1, X0, RY0, 36, RY1, 'A', 1, floor='.')
P.rect(g1, 20, 3, 21, 12, 'A'); P.rect(g1, 20, 7, 21, 9, 'D')
for x in (5, 9, 13, 17): P.rect(g1, x, RY0, x + 1, RY0 + 1, 'o')
for x in (24, 28, 32): P.rect(g1, x, RY0, x + 1, RY0 + 1, 'O')
for x in (8, 15, 24, 31): P.rect(g1, x, RY1 - 1, x + 1, RY1, 'o')
P.rect(g1, 3.5, 7.5, 5.5, 11.5, ' ')                                          # stairwell
P.lining(g1, 'A', 'y', '.', P.sq(21), P.sq(3), P.sq(35), P.sq(5))             # scriptorium shelves on the north wall
P.rect(g1, 21, 3, 35, 3.5, 'O', only='O')
# greenhouse: glass walls carry on up (double height)
P.rect(g1, 35.5, RY0, X1, RY0 + 1, 'q'); P.rect(g1, X1 - 1, RY0, X1, RY1, 'q'); P.rect(g1, 35.5, RY1 - 1, X1, RY1, 'q')
for x in (40, 44): P.rect(g1, x, RY0, x + 0.5, RY0 + 1, 'A')
# arcade roof walk with parapets
for (x0, y0, x1, y1) in ((X0, RY1, COL_W + 1, CY1), (COL_E, RY1, X1, CY1), (X0, CY1 - 5, X1, CY1), (X0, RY1, X1, COL_N + 1)):
    P.rect(g1, x0, y0, x1, y1, ';', only=' ')
P.rect(g1, X0, CY1 - 0.5, X1, CY1, 'w'); P.rect(g1, X0, RY1, X0 + 0.5, CY1, 'w'); P.rect(g1, X1 - 0.5, RY1, X1, CY1, 'w')
P.rect(g1, COL_W + 0.5, COL_N + 0.5, COL_W + 1, COL_S + 1, 'w'); P.rect(g1, COL_E, COL_N + 0.5, COL_E + 0.5, COL_S + 1, 'w')
P.rect(g1, COL_W + 0.5, COL_N + 0.5, COL_E + 0.5, COL_N + 1, 'w'); P.rect(g1, COL_W + 0.5, COL_S, COL_E + 0.5, COL_S + 0.5, 'w')
P.rect(g1, 3.5, 45, 5.5, 49, ' '); P.rect(g1, 46.5, 45, 48.5, 49, ' ')              # stairwells up from the arcade
P.scatter(g1, X0, RY1, X1, CY1, 'V', 0.015, ';', 407)
# corner pavilions (south corners of the roof walk): four slim columns
for (px, py) in ((3, 50), (46, 50)):
    P.rect(g1, px, py, px + 3, py + 3, ',')
    for (cx, cy) in ((px, py), (px + 2.5, py), (px, py + 2.5), (px + 2.5, py + 2.5)):
        P.rect(g1, cx, cy, cx + 0.5, cy + 0.5, 'P')

# ================================================================= roofs (8 m up), as sloped roof squares
roof = P.roof(g2)
# north range: a 45 degree Castle Roof gable over the lab and workshop, ridge east-west. The eaves overhang
# 1 m; the west end overhangs 0.5 m and the east end stops against the greenhouse roof.
roof.gable(X0, RY0, 36, RY1, 'x', 'castle', pitch=1.0, overhang=1.0, end_overhang=0.5)
# three dormers on the garden side, their fronts flush with the south wall (the wall fills up under them)
DORMERS = (7, 17, 27)
for dx in DORMERS:
    roof.gable(dx, RY1 - 5.5, dx + 3.5, RY1, 'y', 'castle', pitch=1.2, overhang=0.5, base=1.5)
# greenhouse: a lower pitched glass roof on a stone frame, glazing bars every 3 m
roof.gable(36, RY0, X1, RY1, 'x', 'glass', pitch=0.6, overhang=0.5)
for (x, y), m in list(roof.mat.items()):
    mx = x / 2
    if m == 'glass' and (any(b <= mx < b + 0.5 for b in (39, 42, 45)) or mx >= X1 - 0.5):
        roof.mat[(x, y)] = 'rib'
roof.caps('ridge')                                            # Temple Stones ridge caps
# corner pavilions on the roof walk: small ribbed domes with a stone knob
for (px, py) in ((3, 50), (46, 50)):
    pcx, pcy = px + 1.5, py + 1.5
    roof.dome(pcx, pcy, 2.0, 2.0, 'castle', base=0.5, rim=0.85)
    roof.ribs(pcx, pcy, [0, 90, 180, 270], 0.25, 0.3, 2.0, 'rib', proud=0.5)
    for (x, y) in list(roof.h):
        if P.dist(x, y, pcx, pcy) < 0.5:
            roof.put(x, y, roof.h[(x, y)] + 0.5, 'ridge', 'set')
roof.paint()

# ================================================================= items
I = P.item
# alchemy lab
I('g0', 'npc-alchemist', 'Alchemist (mage gear)', 4, 3.5, 3, 3, 2, color='#56806c', iid='alch')
I('g0', 'alchemy', 'Alchemy Station', 8, 3.5, 2, 2, 1.5, color='#5f7d6e', iid='as1')
I('g0', 'alchemy', 'Alchemy Station', 11, 3.5, 2, 2, 1.5, color='#5f7d6e', iid='as2')
I('g0', 'grinding-stones', 'Grinding Stones', 14, 3.5, 2, 2, 1, color='#7d8a80', iid='grst')
for k in range(3):
    I('g0', 'mchest-small', 'Small Magic Chest', 17 + k, 3.5, 1, 1, 1, color='#7b68b5', iid=f'mcl{k}')
I('g0', 'stairs', 'Stairs up', 3.5, 7.5, 2, 4, 4, 0, '#a98a62', 'st1')
I('g0', 'table', 'Herb drying table', 9, 8, 3, 1, 1, color='#9a7b52', iid='dry')
# arcane workshop
I('g0', 'mortar', 'Mortar (spells)', 22, 3.5, 2, 2, 1, color='#6f8a7a', iid='mortar')
I('g0', 'laboratory', 'Laboratory', 31.5, 3.5, 2, 2, 1.5, color='#4f7a6a', iid='lab')
I('g0', 'mchest-small', 'Small Magic Chest', 33.5, 10.5, 1, 1, 1, color='#7b68b5', iid='mcw')
I('g0', 'custom', 'Lectern', 27.5, 7.5, 1, 1, 1.5, color='#7a5236', iid='lect')
# greenhouse
I('g0', 'seedbed', 'Seedbed', 46.5, 6.5, 2, 2, 0.5, color='#6f8a43', iid='seed1')
I('g0', 'custom', 'Water barrel', 37, 11, 1, 1, 1, color='#3f8fc1', iid='barrel')
# upper floor
I('g1', 'bed', 'Alchemist’s bed', 16, 3.5, 2, 3, 1, 0, '#8c6b4f', 'bedal')
I('g1', 'chest', 'Wardrobe chest', 13.5, 3.5, 1, 1, 1, color='#8a5a2b', iid='ward')
I('g1', 'table', 'Writing table', 9, 4, 2, 1, 1, color='#9a7b52', iid='wt')
for k, x in enumerate((22.5, 26.5, 30.5)):
    I('g1', 'table', 'Scriptorium desk', x, 7, 2, 1, 1, color='#9a7b52', iid=f'desk{k}')
I('g1', 'custom', 'Lectern', 33, 10, 1, 1, 1.5, color='#7a5236', iid='lect2')
# arcade
I('g0', 'stairs', 'Stairs to the roof walk', 3.5, 45, 2, 4, 4, 0, '#a98a62', 'st2')
I('g0', 'stairs', 'Stairs to the roof walk', 46.5, 45, 2, 4, 4, 0, '#a98a62', 'st3')
for k, (x, y) in enumerate(((4, 20), (4, 30), (4, 38), (47, 20), (47, 30), (47, 38), (13, 51), (38, 51))):
    I('g0', 'light', 'Lantern', x, y, 0.5, 0.5, 1.5, color='#e3b341', iid=f'lan{k}')
# garden
I('g0', 'spire', 'Fountain spire', 25.5, 32.5, 1, 1, 3, color='#3fc2b0', iid='fspire')
I('g0', 'npc-farmer', 'Herbalist (Farmer)', 41.5, 13.5, 2, 2, 2, color='#7c9a3d', iid='herb')
I('g0', 'seedbed', 'Seedbed', 8.5, 13.5, 2, 2, 0.5, color='#6f8a43', iid='seed2')
for k, (x, y) in enumerate(((14, 37.5), (19.5, 44.5), (31.5, 45), (43, 37.5))):
    I('g0', 'tree', 'Ancient tree', x, y, 3, 3, 12, color='#4f6b34', iid=f'tree{k}')
for k, (x, y, r) in enumerate(((20, 36.5, 0), (29.5, 36.5, 0), (21, 28, 180), (29, 28, 180))):
    I('g0', 'custom', 'Stone bench', x, y, 2, 0.5, 0.5, r, '#a79a88', f'bench{k}')
I('g0', 'custom', 'Fallen column', 15.5, 41.5, 4, 1, 1, color='#b3b0a9', iid='fallen')
I('g0', 'custom', 'Arcane obelisk', 42.5, 46.5, 0.5, 0.5, 4, color='#3fc2b0', iid='obelisk')
for k, (px, py) in enumerate(((3, 50), (46, 50))):
    I('g2', 'spire', 'Pavilion finial', px + 1, py + 1, 1, 1, 2, color='#3fc2b0', iid=f'fin{k}')

Z = P.zone
Z('g0', 'Alchemy lab', 3, 3, 20, 12, '#56806c')
Z('g0', 'Arcane workshop', 21, 3, 35, 12, '#8a5cc2')
Z('g0', 'Greenhouse', 36, 3, 49, 12, '#6f8a43')
Z('g0', 'Herb beds', 8, 18, 25, 32, '#3f8a4f')
Z('g0', 'Herb beds', 27, 18, 44, 32, '#3f8a4f')
Z('g0', 'Ruin lawn', 8, 34, 25, 48, '#8a8a5a')
Z('g0', 'Lily pond lawn', 27, 34, 44, 48, '#2f7fb3')
Z('g1', 'Alchemist’s quarters', 3, 3, 20, 12, '#c2416e')
Z('g1', 'Scriptorium', 21, 3, 35, 12, '#2f7fb3')
Z('g1', 'Roof walk', 2, 49, 50, 54, '#5f7d3a')

# moss is ground cover: clear it from under furniture so items sit on lawn or paving
for it in P.items:
    g = P.grids[it['level']]
    w, d = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
    for y in range(it['y'], it['y'] + d):
        for x in range(it['x'], it['x'] + w):
            if g[y][x] == 'V':
                g[y][x] = 'h' if P.sq(GX0) <= x < P.sq(GX1) and P.sq(GY0) <= y < P.sq(GY1) else ','
problems = P.check(outdoor_ok=('g0',), ignore_types=('stairs', 'spire', 'tree'))
print('item problems:', len(problems))
for p_ in problems[:40]: print('  ', p_)

NOTES = """Herb garden cloister and north range of the mage library, drafted by Claude. Uses 0.5 m squares, so every square is one single block. On the campus site plan it's the block north of the rotunda.

SIZE
- 48 x 52 m overall: a 48 x 11 m north range plus a cloister 48 x 42 m.
- About 1 m smaller than on the 1 m site plan, so the colonnade spacing works out evenly.

CLOISTER
- Outer walls: Temple Stones, 4 m, patched with Mycelium Overgrown Block.
- Arcade: a 3 m covered walk of Limestone and Field Stones round the garden. Highly Polished Stone columns every 3 m carry arches.
  - The arches are raised Temple Stones: haunches lifted 2.5 m and crowns lifted 3 m.
- Roof walk at 4 m: Field Stones with Limestone parapets.
  - Stairs up in the two south corners of the arcade.
  - A pavilion at each south corner: four slim columns under a small ribbed Castle Roof dome with a stone knob.
- Gates: a 5 m great door south (towards the rotunda), doors east and west.

GARDEN (38 x 32 m)
- Gravel cross paths line up with the centre arch on each side.
- North half: 16 raised herb beds of Farm Soil in Weathered Stone edging, half a block tall. The Herbalist and a Seedbed sit beside them.
- Centre: a two-tier fountain. Limestone rim and basin, a raised inner tier, and an arcane spire.
- South-west lawn: ruined wall fragments, a fallen column, ancient trees, moss.
- South-east lawn: a lily pond with Field Stones stepping stones, a tree and an arcane obelisk.
- Stone benches face the fountain, with lanterns along the arcade.

NORTH RANGE
- Alchemy lab (west): Alchemist, two Alchemy Stations, Grinding Stones, magic chests, a herb drying table, stairs up.
- Arcane workshop (middle): Mortar (spells), Laboratory, a lectern, and a Blue Luminescent circle in the floor. Stained glass.
- Greenhouse (east): double-height glass walls, raised beds, a Seedbed and a water barrel. Pitched glass roof (lower than the range) on Roughly Cut Stone glazing bars every 3 m.
- Upstairs: the Alchemist's quarters and a scriptorium (desks, shelving, lectern).
- Roof: a 45 degree Castle Roof Block gable over the lab and workshop, about 7 m high.
  - The eaves overhang 1 m. A Temple Stones ridge cap runs along the top, and the gable ends are Temple Stones.
  - Three dormers on the garden side, with their fronts flush with the south wall.

NOTES
- Crafting stations are 2 x 2 m placeholders. Benches and other furniture are estimates.
- Glass, doors, windows and bookshelves aren't blocks.
"""
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mage-cloister.json')
print('bytes', P.save(out, NOTES, 'r-claude-mage-cloister-1'))
print(P.preview('g0', 2))
