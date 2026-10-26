"""Mage library: the wizard tower, 0.5 m detail plan (every square is one single block).

Run: python mage_tower.py  ->  writes mage-tower.json
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mage_common import Plan, PALETTE

PALETTE['m'] = {'name': 'Mycelium Overgrown Block', 'kind': 'wall', 'color': '#72664f'}
PALETTE['u'] = {'name': 'Drak Temple Roof Block', 'kind': 'wall', 'color': '#8a8a5a'}
PALETTE['k'] = {'name': 'Roughly Cut Stone Block (corbel)', 'kind': 'block', 'color': '#62605d', 'height': 1, 'base': 3}
for i in range(8):        # spiral stair treads: 0.5 m thick, each 0.5 m higher than the last
    PALETTE[str(i + 1)] = {'name': f'Refined Stone tread {i + 1} (+{i * 0.5:g} m)', 'kind': 'block',
                           'color': ['#6f6e6a', '#767571', '#7d7c78', '#84837e', '#8b8a85', '#92918c', '#999893', '#a09f9a'][i],
                           'height': 0.5, **({'base': i * 0.5} if i else {})}

P = Plan('Mage library: wizard tower', 0.5, 30, 30, 160)
P.project = 'Mage library'
CX = CY = 15.0
R = 7.0                 # outer radius; walls 1 m (2 blocks) thick
R_STAIR = 2.8           # spiral stair well
STOREYS = [
    ('s0', 'Ground: entrance hall', ','),
    ('s1', 'Study (4 m)', '.'),
    ('s2', 'Arcane lab (8 m)', '.'),
    ('s3', 'Your quarters (12 m)', '.'),
    ('s4', 'Treasury (16 m)', '.'),
    ('s5', 'Summoning circle (20 m)', ','),
    ('s6', 'Balcony (24 m)', '.'),
    ('s7', 'Map room (28 m)', '.'),
]
G = {}
for n, (lid, name, floor) in enumerate(STOREYS):
    G[lid] = P.level(lid, name, n * 4, 4)
obs = P.level('obs', 'Observatory (32 m)', 32, 4)
roofL = P.level('roof', 'Witch-hat roof (36 m)', 36, 12)

def spiral(g):
    """One full turn per storey: eight 45-degree treads round a central column."""
    for x, y in P.cells_rect(CX - R_STAIR - 1, CY - R_STAIR - 1, CX + R_STAIR + 1, CY + R_STAIR + 1):
        mx, my = P.centre_m(x, y)
        d = math.hypot(mx - CX, my - CY)
        if d < 0.8:
            g[y][x] = 'P'                                     # newel column
        elif d <= R_STAIR:
            a = math.degrees(math.atan2(mx - CX, -(my - CY))) % 360   # 0 = north, clockwise
            g[y][x] = str(int(a // 45) + 1)

# ======================================================================= island & pond (ground only)
s0 = G['s0']
P.disc(s0, CX, CY, 15.5, '~')
P.disc(s0, CX, CY, 8.6, ',')
P.scatter(s0, 0, 0, 30, 30, ';', 0.35, ',', 301)
P.scatter(s0, 0, 0, 30, 30, 'V', 0.07, ',;', 302)
for a in (270, 0, 180):                                       # bridge stubs with railings
    P.radial(s0, CX, CY, [a], 2.5, 8.4, 16, 'w')
    P.radial(s0, CX, CY, [a], 2.0, 8.4, 16, 'b')

# ======================================================================= storeys
BUTTRESS = [30, 90, 150, 210, 330]
for n, (lid, name, floor) in enumerate(STOREYS):
    g = G[lid]
    P.disc(g, CX, CY, R, floor, r_in=R_STAIR)
    P.ring_wall(g, CX, CY, R, 'S' if n == 0 else 'A', 1.0)
    spiral(g)
    if n < 3:                                                 # moss climbing the lower storeys
        P.scatter(g, 0, 0, 30, 30, 'm', (0.3, 0.18, 0.08)[n], 'AS', 310 + n)
    if n < 2:                                                 # buttresses on the lower two storeys
        P.radial(g, CX, CY, BUTTRESS, 0.5, R - 0.2, R + (1.0 if n == 0 else 0.5), 'S' if n == 0 else 'A')
    # openings
    if n == 0:
        P.radial(g, CX, CY, [270], 1.0, R - 1.2, R + 1.1, 'G', only='SAm')
        P.radial(g, CX, CY, [0, 180], 0.5, R - 1.2, R + 1.1, 'D', only='SAm')
        P.radial(g, CX, CY, [45, 135, 225, 315], 0.25, R - 1.2, R + 0.1, 'o', only='SAm')
    elif n == 3:
        P.radial(g, CX, CY, [60, 180, 300], 0.75, R - 1.2, R + 0.1, 'O', only='Am')
    elif n == 5:
        P.radial(g, CX, CY, [i * 45 + 22.5 for i in range(8)], 0.5, R - 1.2, R + 0.1, 'O', only='Am')
    elif n == 6:
        P.radial(g, CX, CY, [90, 270], 0.5, R - 1.2, R + 0.1, 'D', only='Am')
        P.radial(g, CX, CY, [0, 180], 0.5, R - 1.2, R + 0.1, 'o', only='Am')
    else:
        P.radial(g, CX, CY, [(a + n * 30) % 360 for a in (20, 110, 200, 290)], 0.5, R - 1.2, R + 0.1, 'o', only='Am')

# Study: shelving along the wall
P.lining(G['s1'], 'Am', 'y', '.', 0, 0, 60, 60)
P.radial(G['s1'], CX, CY, [0], 1.5, R_STAIR, R, '.', only='y')       # keep the stair exit clear
# Summoning circle inlay
P.ring_wall(G['s5'], CX, CY, 5.0, 'g', 0.5)
P.radial(G['s5'], CX, CY, [i * 60 for i in range(6)], 0.25, 3.2, 4.6, 'g', only=',')
# Balcony: cantilevered walk with a parapet, carried on corbels below
P.disc(G['s6'], CX, CY, 8.6, ',', only=' ', r_in=R - 0.1)
P.ring_wall(G['s6'], CX, CY, 8.6, 'w', 0.5)
P.radial(G['s5'], CX, CY, [i * 22.5 for i in range(16)], 0.3, R - 0.1, 8.4, 'k', only=' ')

# ======================================================================= observatory and roof
P.disc(obs, CX, CY, R, ',', r_in=R_STAIR)
P.ring_wall(obs, CX, CY, R_STAIR + 0.5, 'w', 0.5)                      # railing round the stairwell
P.radial(obs, CX, CY, [337.5], 0.9, 0, R_STAIR + 0.6, ' ', only='w')  # gap where the stair arrives
P.ring_wall(obs, CX, CY, R, 'q', 0.5)
P.radial(obs, CX, CY, [i * 45 for i in range(8)], 0.5, R - 1.0, R + 0.1, 'P')
# witch-hat roof: a steep 11 m Castle Roof cone on a flared brim that overhangs the walls by 1 m,
# with mossy patches low down and a glowing tip under the spire
hat = P.roof(roofL)
hat.cone(CX, CY, R, 11.0, 'castle', overhang=1.0, base=0.5, flare=(1.5, 0.5))
hat.scatter('moss', 0.25, 330, max_h=2.5)
hat.scatter('moss', 0.08, 331, max_h=5.0)
for (x, y) in list(hat.h):
    if P.dist(x, y, CX, CY) < 0.75:
        hat.put(x, y, hat.h[(x, y)] + 0.5, 'glow', 'set')
hat.paint()
TIP_Z = 36 + math.floor(hat.top(P.sq(CX), P.sq(CY)) * 2) / 2
fin = P.level('fin', f'Spire ({TIP_Z:g} m)', TIP_Z, 6)

# ======================================================================= items
I = P.item
def at(a, r, w, d):
    ar = math.radians(a)
    return (round((CX + r * math.sin(ar) - w / 2) * 2) / 2, round((CY - r * math.cos(ar) - d / 2) * 2) / 2)

x, y = at(135, 4.6, 1, 1); I('s0', 'mchest-small', 'Small Magic Chest', x, y, 1, 1, 1, color='#7b68b5', iid='mc1')
x, y = at(225, 4.6, 1, 1); I('s0', 'mchest-small', 'Small Magic Chest', x, y, 1, 1, 1, color='#7b68b5', iid='mc2')
x, y = at(90, 4.6, 1, 1); I('s0', 'custom', 'Waypoint stone', x, y, 1, 1, 2, color='#3fc2b0', iid='way')
x, y = at(150, 4.0, 2, 1); I('s1', 'table', 'Writing desk', x, y, 2, 1, 1, color='#9a7b52', iid='desk')
x, y = at(230, 4.0, 1, 1); I('s1', 'custom', 'Lectern', x, y, 1, 1, 1.5, color='#7a5236', iid='lect')
x, y = at(90, 4.4, 2, 2); I('s2', 'alchemy', 'Alchemy Station', x, y, 2, 2, 1.5, color='#5f7d6e', iid='alch')
x, y = at(180, 4.4, 2, 2); I('s2', 'mortar', 'Mortar (spells)', x, y, 2, 2, 1, color='#6f8a7a', iid='mortar')
x, y = at(270, 4.4, 2, 2); I('s2', 'laboratory', 'Laboratory', x, y, 2, 2, 1.5, color='#4f7a6a', iid='lab')
I('s3', 'bed2', 'Your bed', 18, 14, 2, 3, 1, 270, '#7d5d43', 'bed')
x, y = at(180, 4.5, 2, 3); I('s3', 'bathtub', 'Bathtub', x, y, 2, 3, 1, 0, '#6f8fa3', 'tub')
x, y = at(240, 4.5, 1, 1); I('s3', 'chest', 'Wardrobe chest', x, y, 1, 1, 1, color='#8a5a2b', iid='ward')
x, y = at(140, 4.5, 1, 1); I('s3', 'custom', 'Lantern', x, y, 1, 1, 1, color='#e3b341', iid='lamp3')
for k, a in enumerate((60, 100, 140, 220, 260, 300)):
    x, y = at(a, 4.8, 1, 1); I('s4', 'chest', 'Treasure chest', x, y, 1, 1, 1, color='#8a5a2b', iid=f'tc{k}')
x, y = at(180, 4.6, 1, 1); I('s4', 'custom', 'Trophy stand', x, y, 1, 1, 2, color='#c9a227', iid='trophy')
for k, a in enumerate((45, 135, 225, 315)):
    x, y = at(a, 4.9, 0.5, 0.5); I('s5', 'custom', 'Arcane brazier', x, y, 0.5, 0.5, 1.5, color='#3fc2b0', iid=f'braz{k}')
x, y = at(90, 4.5, 2, 2); I('s7', 'custom', 'Star chart table', x, y, 2, 2, 1, color='#6a5a9a', iid='chart')
x, y = at(270, 4.5, 2, 1); I('s7', 'table', 'Map table', x, y, 2, 1, 1, color='#9a7b52', iid='map')
x, y = at(90, 4.8, 1, 2); I('obs', 'custom', 'Telescope', x, y, 1, 2, 2, color='#c9a227', iid='scope')
x, y = at(225, 4.8, 1, 1); I('obs', 'custom', 'Orrery', x, y, 1, 1, 1.5, color='#3fc2b0', iid='orrery')
I('fin', 'spire', 'Arcane spire', 14.5, 14.5, 1, 1, 6, color='#3fc2b0', iid='spire')

Z = P.zone
Z('s0', 'Entrance hall', 8, 8, 22, 22, '#b8862b')
Z('s1', 'Study', 8, 8, 22, 22, '#2f7fb3')
Z('s2', 'Arcane lab', 8, 8, 22, 22, '#8a5cc2')
Z('s3', 'Your quarters', 8, 8, 22, 22, '#c2416e')
Z('s4', 'Treasury', 8, 8, 22, 22, '#c9a227')
Z('s5', 'Summoning circle', 8, 8, 22, 22, '#2f8f8a')
Z('s6', 'Balcony', 6.4, 6.4, 23.6, 23.6, '#5f7d3a')
Z('s7', 'Map room', 8, 8, 22, 22, '#6a5a9a')
Z('obs', 'Observatory', 8, 8, 22, 22, '#2f7fb3')

problems = P.check(outdoor_ok=('s0',), ignore_types=('spire',))
print('item problems:', len(problems))
for p_ in problems[:30]: print('  ', p_)

NOTES = """Wizard tower of the mage library, drafted by Claude. Uses 0.5 m squares, so every square is one single block. It stands on an island in the pond east of the rotunda. See the campus site plan.

MATERIALS (real blocks, see the planner's block catalogue)
- Walls: Temple Stones on a Roughly Cut Stone Block plinth. Weathered Stone Block for ruins, Highly Polished Stone Block for columns, Mycelium Overgrown Block for mossy patches.
- Roofs: Castle Roof Block, with Drak Temple Roof Block for the mossy patches. Roughly Cut Stone ribs.
- Floors: Limestone Block indoors and on plazas, Field Stones outdoors, Rocky Stone Road Block paths, Refined Wood Block upstairs, Rough Wood Block bridges.
- Blue Luminescent Block inlays, Moss, Fertile Revelwood Dirt lawns, Farm Soil beds.
- Not blocks: doors, windows and glass, bookshelves and water.

SIZE
- 14 m across, walls 1 m (2 blocks) thick.
- Eight 4 m storeys, a glass observatory, then a witch-hat roof and an arcane spire, about 53 m to the tip.
- The lower storeys are dark plinth stone with buttresses, and moss climbs the walls.

SPIRAL STAIR
- A newel column runs the full height, with eight treads per storey. Each tread is 0.5 m thick and 0.5 m higher than the last, so you climb one full turn per storey.
- The treads are separate materials with "Raise by" set, so they float like real steps and leave 3.5 m of headroom.
- In game, build them as stair blocks or single blocks round a column.

STOREYS
- 0 m: entrance hall. Great door west, small doors north and south, arrow slits, magic chests, a waypoint stone.
- 4 m: study with shelving round the walls, a writing desk and a lectern.
- 8 m: arcane lab with the Alchemist's Alchemy Station, Mortar (spells) and Laboratory.
- 12 m: your quarters. Bed, bath, wardrobe, three arcane windows.
- 16 m: treasury with chests and a trophy stand.
- 20 m: summoning circle. Glowing inlay, four braziers, eight stained-glass windows.
- 24 m: balcony storey. Doors east and west onto a cantilevered walk round the tower with a parapet, carried on 16 corbels.
- 28 m: map room with star charts.
- 32 m: observatory. Glass walls between eight columns, a telescope and an orrery, and a railing round the stairwell.

ROOF
- A witch-hat roof of Castle Roof Block: a steep cone rising 11 m over the observatory.
  - It sits on a flared brim, a gentle skirt 1.5 m wide that overhangs the walls by 1 m.
  - Drak Temple Roof Block moss patches cover the lower part.
- The tip is a glowing Blue Luminescent cap carrying the arcane spire.

DOUBLE-CHECK IN GAME
- Crafting stations are 2 x 2 m placeholders until measured. Other furniture sizes are estimates.
- The roof is drawn as a smooth sloped skin. In game, build it from 0.5 m roof blocks, about two courses per 0.5 m inwards, and let the voxel smoothing take the steps off.
"""
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mage-tower.json')
print('bytes', P.save(out, NOTES, 'r-claude-mage-tower-1'))
for lid in ('s0', 's6', 'obs'):
    print('---', lid); print(P.preview(lid, 1))
