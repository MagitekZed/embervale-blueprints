"""Mage library: entrance gate, reflecting pool and colonnades, 0.5 m detail plan (every square is one single block).

Run: python mage_gate.py  ->  writes mage-gate.json
Local coordinates: site point (58, 96) sits at (0, 0) here.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mage_common import Plan, PALETTE, FLOORS

# Extra real blocks for this plan (names/colours from the block catalogue)
PALETTE['m'] = {'name': 'Mycelium Overgrown Block', 'kind': 'wall', 'color': '#72664f'}
PALETTE['p'] = {'name': 'Highly Polished Stone Block (column top)', 'kind': 'wall', 'color': '#b3b0a9', 'height': 2}
PALETTE['x'] = {'name': 'Temple Stones (architrave)', 'kind': 'block', 'color': '#857f5d', 'height': 1, 'base': 2}
PALETTE['c'] = {'name': 'Limestone Block (pool coping)', 'kind': 'block', 'color': '#a79a88', 'height': 0.5}
PALETTE['L'] = {'name': 'Temple Stones (lintel)', 'kind': 'block', 'color': '#857f5d', 'height': 2, 'base': 2}
PALETTE['J'] = {'name': 'Temple Stones (broken lintel end)', 'kind': 'block', 'color': '#857f5d', 'height': 1.5, 'base': 2.5}
PALETTE['r'] = {'name': 'Weathered Stone Block (column stump)', 'kind': 'block', 'color': '#6a6c67', 'height': 1.5}

P = Plan('Mage library: entrance gate & colonnades', 0.5, 46, 64, 160)
P.project = 'Mage library'
g0 = P.level('g0', 'Ground: pool, colonnades & plaza', 0, 4)
g1 = P.level('g1', 'Column tops & pylons (4 m)', 4, 4)
g2 = P.level('g2', 'Pylon caps (8 m)', 8, 6)

# ================================================================= the rotunda's edge (north)
RCX, RCY = 22.5, -15.5                         # rotunda centre in local coordinates (off the canvas)
P.disc(g0, RCX, RCY, 22, ',')
P.scatter(g0, 0, 0, 46, 8, ';', 0.3, ',', 701)
P.disc(g0, RCX, RCY, 19.5, '~', r_in=17)
P.rect(g0, 20, 0, 25, 8, '~')                                   # channel from the canal to the pool
P.rect(g0, 19.5, 0, 25.5, 6.5, 'b'); P.rect(g0, 19.5, 0, 20, 6.5, 'w'); P.rect(g0, 25, 0, 25.5, 6.5, 'w')

# ================================================================= reflecting pool
P.rect(g0, 17, 7, 28, 37, 'c')
P.rect(g0, 18, 8, 27, 36, '~')
P.rect(g0, 20, 6.5, 25, 8, '~')

# ================================================================= walks and colonnades
for (x0, x1) in ((9, 17), (28, 36)):
    P.rect(g0, x0, 6, x1, 38, ',', only=' ,;')
P.scatter(g0, 9, 6, 36, 38, ';', 0.35, ',', 702)
COLS_Y = list(range(9, 34, 4))                                  # 9, 13, ... 33
BROKEN = {('W', 21), ('E', 13), ('E', 29)}                       # ruined bays: stumps, no beam
for side, cx in (('W', 12), ('E', 32)):
    for k, y in enumerate(COLS_Y):
        if (side, y) in BROKEN:
            P.rect(g0, cx, y, cx + 1, y + 1, 'r')                # broken column stump
            continue
        P.rect(g0, cx, y, cx + 1, y + 1, 'P'); P.rect(g1, cx, y, cx + 1, y + 1, 'p')
    # architrave along the tops, missing over the broken columns and one fallen span per side
    for k in range(len(COLS_Y) - 1):
        y0, y1 = COLS_Y[k], COLS_Y[k + 1]
        if (side, y0) in BROKEN or (side, y1) in BROKEN or (side, k) in (('W', 1), ('E', 4)):
            continue
        P.rect(g1, cx, y0, cx + 1, y1 + 1, 'x', only=' ')
P.scatter(g0, 9, 6, 36, 38, 'V', 0.02, ',;', 703)
# covered walks: a Castle Roof lean-to over each outer walk, from the beam (7 m) down to a row of Temple
# Stones piers on the outer edge (5.5 m). Partly collapsed: some bays have fallen in.
walks = P.roof(g1)
COLLAPSED = {'W': ((13, 17), (21, 25)), 'E': ((13, 17), (29, 33))}
for side, x0, x1, high, pier_x in (('W', 8.5, 12, 'e', 9), ('E', 33, 36.5, 'w', 35.5)):
    walks.lean_to(x0, COLS_Y[0] - 0.5, x1, COLS_Y[-1] + 1.5, high, 3.0, 1.5, 'castle')
    for (y0, y1) in COLLAPSED[side]:
        walks.cut(x0, y0 + 1, x1, y1)
    for y in COLS_Y:
        P.rect(g0, pier_x, y, pier_x + 0.5, y + 1, 'A')
walks.scatter('moss', 0.12, 710)
walks.paint()

# ================================================================= entrance plaza
P.rect(g0, 4, 38, 42, 49, ',')
P.scatter(g0, 4, 38, 42, 49, ';', 0.3, ',', 704)
P.ring_wall(g0, 22.5, 42.5, 3.0, 'g', 0.5)                      # glowing compass inlay
P.radial(g0, 22.5, 42.5, [0, 90, 180, 270], 0.25, 0.5, 2.6, 'g')
P.radial(g0, 22.5, 42.5, [45, 135, 225, 315], 0.25, 0.8, 1.8, 'g')
# pylons: 3 x 3 m, 8 m tall, glowing arcane panels on the road and plaza faces
caps = P.roof(g2)
for px in (13, 29):
    P.rect(g0, px, 43, px + 3, 46, 'S'); P.rect(g1, px, 43, px + 3, 46, 'A')
    for g in (g0, g1):
        P.rect(g, px + 1, 45.5, px + 2, 46, 'O'); P.rect(g, px + 1, 43, px + 2, 43.5, 'O')
    P.scatter(g1, px, 43, px + 3, 46, 'm', 0.2, 'A', 705 + px)
    # a pointed Temple Stones pyramid cap overhanging 0.5 m, with a glowing tip
    caps.hip(px, 43, px + 3, 46, 'ridge', pitch=2.0, overhang=0.5, base=0.5)
    for (x, y) in list(caps.h):
        if P.dist(x, y, px + 1.5, 44.5) < 0.6:
            caps.put(x, y, caps.h[(x, y)] + 0.5, 'glow', 'set')
caps.paint()
# the lintel between the pylons (6-8 m, just under the caps), snapped in the middle
P.rect(g1, 16, 44, 29, 45, 'L')
P.rect(g1, 20, 44, 25, 45, ' ')
P.rect(g1, 19.5, 44, 20, 45, 'J'); P.rect(g1, 25, 44, 25.5, 45, 'J')
# ruined flanking walls with gaps
P.rect(g0, 4, 45, 13, 46, 'R'); P.rect(g0, 32, 45, 42, 46, 'R')
for (x0, x1) in ((7, 8.5), (36, 37), (39.5, 40)):
    P.rect(g0, x0, 45, x1, 46, ',')
P.rect(g0, 4, 44.5, 4.5, 46.5, 'R'); P.rect(g0, 41.5, 44.5, 42, 46.5, 'R')
P.scatter(g0, 4, 44, 42, 47, 'V', 0.06, ',;', 709)
# approach road
P.rect(g0, 19, 49, 26, 64, ':')
P.rect(g0, 18.5, 49, 19, 64, 'c'); P.rect(g0, 26, 49, 26.5, 64, 'c')

# ================================================================= items
I = P.item
for k, y in enumerate((12, 18, 24, 30)):
    I('g0', 'spire', 'Water jet', 22, y, 1, 1, 1.5, color='#a9d8e6', iid=f'jet{k}')
for side, x in (('W', 10), ('E', 34)):                          # statues in the outer bays
    for k, y in enumerate((11, 19, 27)):
        I('g0', 'custom', 'Ancient statue', x, y, 1, 1, 4, color='#b3b0a9', iid=f'st{side}{k}')
for side, x, r in (('W', 15, 90), ('E', 29.5, 270)):             # benches facing the pool
    for k, y in enumerate((15, 23, 31)):
        I('g0', 'custom', 'Stone bench', x, y, 2, 0.5, 0.5, r, '#a79a88', f'bn{side}{k}')
I('g0', 'custom', 'Fallen column', 9.5, 22.5, 1, 4, 1, color='#b3b0a9', iid='fallen1')
I('g0', 'custom', 'Fallen column', 34, 14, 1, 4, 1, color='#b3b0a9', iid='fallen2')
I('g0', 'custom', 'Fallen column', 6, 47, 4, 1, 1, color='#b3b0a9', iid='fallen3')
I('g0', 'tree', 'Ancient tree', 5, 39, 3, 3, 12, color='#4f6b34', iid='tree1')
I('g0', 'tree', 'Ancient tree', 37.5, 39.5, 3, 3, 12, color='#4f6b34', iid='tree2')
I('g0', 'custom', 'Arcane obelisk', 17.5, 39.5, 0.5, 0.5, 5, color='#3fc2b0', iid='ob1')
I('g0', 'custom', 'Arcane obelisk', 27.5, 39.5, 0.5, 0.5, 5, color='#3fc2b0', iid='ob2')
for k, (x, y) in enumerate(((16.5, 7.5), (28, 7.5), (16.5, 36.5), (28, 36.5), (12, 47), (33.5, 47), (18, 55), (26.5, 55))):
    I('g0', 'light', 'Lantern', x, y, 0.5, 0.5, 1.5, color='#e3b341', iid=f'lan{k}')
I('g0', 'custom', 'Fallen roof slabs', 10, 14.5, 1.5, 1, 0.5, color='#8b9987', iid='slab1')
I('g0', 'custom', 'Fallen roof slabs', 33.5, 30.5, 1.5, 1, 0.5, color='#8b9987', iid='slab2')

Z = P.zone
Z('g0', 'Reflecting pool', 17, 7, 28, 37, '#2f7fb3')
Z('g0', 'West colonnade', 9, 7, 17, 37, '#8a8a5a')
Z('g0', 'East colonnade', 28, 7, 36, 37, '#8a8a5a')
Z('g0', 'Entrance plaza', 4, 38, 42, 49, '#b8862b')

P.clear_under_items('V', lambda lid, x, y: ',')
problems = P.check(outdoor_ok=('g0',), ignore_types=('stairs', 'tree', 'spire'))
print('item problems:', len(problems))
for p_ in problems[:40]: print('  ', p_)

NOTES = """Entrance gate, reflecting pool and colonnades of the mage library, drafted by Claude. Uses 0.5 m squares, so every square is one single block. On the campus site plan this is the processional way south of the rotunda.

REFLECTING POOL
- 9 x 28 m of water inside a Limestone coping half a block tall. Four water jets run down the centre line.
- The north end runs into the channel under the bridge to the rotunda's canal. That edge of the rotunda is drawn for context.

COLONNADES
- A colonnade on each side of the pool: 6 m Highly Polished Stone columns every 4 m.
- A Temple Stones beam runs along the column tops. It's lifted 2 m within the upper level, so it sits at 6-7 m.
- Ruined: three columns are broken down to Weathered Stone stumps, two spans of beam have fallen, and fallen columns lie on the walks.
- Covered walks: a Castle Roof Block lean-to over each outer walk, sloping from the beam (7 m) down to Temple Stones piers on the outer edge (5.5 m).
  - Partly collapsed: two bays on each side have fallen in, with roof slabs lying on the walk. Moss grows on the rest.
- Ancient statues stand in the outer bays, and stone benches face the pool.
- The walks are Limestone and Field Stones, with moss.

ENTRANCE PLAZA & GATE
- A plaza with a glowing Blue Luminescent compass inlay, two arcane obelisks, ancient trees at the corners, and lanterns.
- The gate is two 3 x 3 m pylons, 8 m tall: Roughly Cut Stone below, mossy Temple Stones above.
  - Each face has a glowing panel of arcane stained glass.
  - Each pylon wears a pointed Temple Stones pyramid cap, about 4 m tall and overhanging 0.5 m, with a glowing Blue Luminescent tip.
- A Temple Stones lintel spans the pylons at 6-8 m, just under the caps. It's snapped in the middle, with broken ends.
- Ruined Weathered Stone walls run out either side, with gaps.

APPROACH
- A Rocky Stone road with a Limestone kerb runs south from the gate.

NOTES
- Statues, obelisks, benches, fallen columns and water jets are custom placeholders. Build them from blocks or props in game.
"""
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mage-gate.json')
print('bytes', P.save(out, NOTES, 'r-claude-mage-gate-1'))
print(P.preview('g0', 2))
