"""Mage library: the domed rotunda, 0.5 m detail plan (every square is one single block).

Run: python mage_rotunda.py  ->  writes mage-rotunda.json
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mage_common import Plan, PALETTE

PALETTE['u'] = {'name': 'Drak Temple Roof Block', 'kind': 'wall', 'color': '#8a8a5a'}

P = Plan('Mage library: rotunda', 0.5, 48, 48, 160)
P.project = 'Mage library'
CX = CY = 24.0                       # rotunda centre (metres) = the altar
R_OUT, R_IN = 14.0, 13.0             # walls 1 m (2 blocks) thick

g0 = P.level('g0', 'Ground: altar & archive', 0, 4)
g1 = P.level('g1', 'Gallery 1 (4 m)', 4, 4)
g2 = P.level('g2', 'Gallery 2 (8 m)', 8, 4)
g3 = P.level('g3', 'Drum & catwalk (12 m)', 12, 4)
dome = P.level('dome', 'Dome (16 m)', 16, 12)

DOORS = {0: 1.0, 90: 1.0, 270: 1.0}          # half widths in metres
MAIN = {180: 1.5}
PILASTERS = [i * 22.5 + 11.25 for i in range(16)]
WINDOWS = [i * 22.5 + 11.25 for i in range(16)]    # windows sit between the pilasters

def walls(g, ch='A'):
    P.ring_wall(g, CX, CY, R_OUT, ch, 1.0)

def pilasters(g, ch):
    P.radial(g, CX, CY, PILASTERS, 0.5, R_OUT - 0.1, R_OUT + 0.6, ch)

# ======================================================================= surroundings (ground)
P.disc(g0, CX, CY, 22, ',')
P.scatter(g0, 0, 0, 48, 48, ';', 0.3, ',', 101)
P.scatter(g0, 0, 0, 48, 48, 'V', 0.04, ',;', 102)
P.disc(g0, CX, CY, 19.5, '~', r_in=17)
P.rect(g0, 21.5, 41, 26.5, 48, '~')                          # channel south to the reflecting pool
for a in (0, 90, 180, 270):                                  # bridges with low railings
    P.radial(g0, CX, CY, [a], 2.5, 16.5, 20.2, 'w')
    P.radial(g0, CX, CY, [a], 2.0, 16.5, 20.2, 'b')
P.rect(g0, 21.5, 41, 26.5, 46.5, 'b', only='~,;V'); P.rect(g0, 21.5, 41, 22, 46.5, 'w'); P.rect(g0, 26, 41, 26.5, 46.5, 'w')

# ======================================================================= ground: altar hall & archive
P.disc(g0, CX, CY, R_OUT, ',')
P.disc(g0, CX, CY, 4.0, 'g', r_in=3.5)                       # inlay ring round the altar
P.radial(g0, CX, CY, [45, 135, 225, 315], 0.25, 4.0, 9.5, 'g')
P.disc(g0, CX, CY, 10.0, 'g', r_in=9.5)
walls(g0, 'S')                                               # dark plinth course on the ground storey
pilasters(g0, 'S')
P.lining(g0, 'S', 'Y', ',;g', 0, 0, 96, 96)                  # shelving lines the wall
P.disc(g0, CX, CY, 22, ',', only='Y', r_in=13.6)              # (not outside)
for a, hw in {**DOORS, **MAIN}.items():
    P.radial(g0, CX, CY, [a], hw + 0.5, 11.5, R_OUT + 0.7, ',', only='YS')
    P.radial(g0, CX, CY, [a], hw, R_IN - 0.2, R_OUT + 0.7, 'G' if a == 180 else 'D', only=',SY')
for x0 in (20.5, 26.5):                                      # portico columns at the main doors
    P.rect(g0, x0, 38.5, x0 + 1, 39.5, 'P')
for a in range(0, 360, 15):                                  # vines creeping up the plinth
    ar = math.radians(a + 4)
    x, y = CX + 14.6 * math.sin(ar), CY - 14.6 * math.cos(ar)
    if (a // 15) % 3 == 0:
        P.rect(g0, round(x * 2) / 2, round(y * 2) / 2, round(x * 2) / 2 + 0.5, round(y * 2) / 2 + 0.5, 'V', only=',;')

# ======================================================================= galleries
for g, lid in ((g1, 'g1'), (g2, 'g2')):
    P.disc(g, CX, CY, R_OUT, '.', r_in=8.0)
    P.ring_wall(g, CX, CY, 9.0, 'w', 0.5)                   # gallery railing
    P.disc(g, CX, CY, 8.7, ' ', only='.')                    # open atrium
    walls(g)
    pilasters(g, 'A')
    P.radial(g, CX, CY, WINDOWS, 0.5, R_IN - 0.3, R_OUT + 0.1, 'O', only='A')    # tall narrow stained glass
    P.lining(g, 'A', 'Y', '.', 0, 0, 96, 96)                 # wall shelving between the windows
    P.radial(g, CX, CY, [i * 45 + 22.5 for i in range(8)], 0.5, 9.8, 11.8, 'y')  # double-sided book stacks
# south balcony over the main doors (4 m)
P.radial(g1, CX, CY, [180], 2.5, R_OUT - 0.1, 16.5, ',')
P.radial(g1, CX, CY, [180], 2.5, 16.0, 16.5, 'w'); P.radial(g1, CX, CY, [180], 2.5, R_OUT, 16.5, 'w', only=' ')
P.radial(g1, CX, CY, [180], 1.0, R_IN - 0.2, R_OUT + 0.1, 'D', only='AO.')
for x0, y0 in ((21.0, 37.5), (26.5, 37.5)):
    P.rect(g1, x0, y0, x0 + 0.5, y0 + 3, 'w')

# Stairwells (items placed below)
P.rect(g1, 15, 17, 17, 21, ' ')
P.rect(g2, 33, 26, 35, 30, ' ')
P.rect(g1, 33, 26, 35, 30, '.', only='yw')
P.rect(g2, 20, 12, 24, 14, '.', only='yw')

# ======================================================================= drum & catwalk (12-16 m)
P.disc(g3, CX, CY, R_OUT, '.', r_in=10.0)
P.ring_wall(g3, CX, CY, 10.8, 'w', 0.5)
P.disc(g3, CX, CY, 10.4, ' ', only='.')
walls(g3)
pilasters(g3, 'A')
P.radial(g3, CX, CY, WINDOWS, 0.75, R_IN - 0.3, R_OUT + 0.1, 'O', only='A')
P.rect(g3, 20, 12, 24, 14, ' ')
P.disc(g3, CX, CY, R_OUT + 0.6, 'w', only=' ', r_in=R_OUT)   # cornice / parapet at the top of the drum

# ======================================================================= dome (16 m up): one smooth sloped roof
# Castle Roof Block, overhanging the drum by 0.5 m, on a trimmed-ellipse profile 11 m high. Eight stone ribs
# stand 0.5 m proud, moss creeps over the lower courses, and a 5 m oculus opens under the lantern.
D_R, D_H, D_RIM = R_OUT + 0.5, 11.0, 0.9
def dome_h(d):                                               # dome height above its level at radius d (metres)
    R = D_R / D_RIM; z0 = math.sqrt(1 - D_RIM ** 2)
    return 0.5 + D_H * (math.sqrt(max(0.0, 1 - (d / R) ** 2)) - z0) / (1 - z0)
RIBS = [i * 45 for i in range(8)]
roof = P.roof(dome)
roof.dome(CX, CY, D_R, D_H, 'castle', base=0.5, rim=D_RIM)
roof.scatter('moss', 0.22, 201, max_h=3.5)
roof.scatter('moss', 0.08, 202, max_h=6.0)
roof.ribs(CX, CY, RIBS, 0.3, 3.0, D_R, 'rib', proud=0.5)
roof.cut_disc(CX, CY, 2.5)
roof.paint()

# lantern: a 4 m glass drum standing on the dome round the oculus, under its own ribbed mini dome
LAN_Z = 16 + math.floor(dome_h(3.0) * 2) / 2
lan = P.level('lan', f'Lantern ({LAN_Z:g} m)', LAN_Z, 4)
P.ring_wall(lan, CX, CY, 3.0, 'q', 0.5)
P.radial(lan, CX, CY, [i * 45 for i in range(8)], 0.3, 2.0, 3.1, 'P', only='q')
lroof = P.level('lroof', f'Lantern dome ({LAN_Z + 4:g} m)', LAN_Z + 4, 3)
lr = P.roof(lroof)
lr.dome(CX, CY, 3.5, 2.5, 'castle', base=0.5, rim=0.9)
lr.ribs(CX, CY, RIBS, 0.3, 0.6, 3.5, 'rib', proud=0.5)
for (x, y) in list(lr.h):                                    # glowing crown under the finial
    if P.dist(x, y, CX, CY) < 0.75:
        lr.put(x, y, lr.h[(x, y)] + 0.5, 'glow', 'set')
lr.paint()
FIN_Z = LAN_Z + 4 + math.floor((lr.top(P.sq(CX), P.sq(CY)) or 3.0) * 2) / 2
fin = P.level('fin', f'Finial ({FIN_Z:g} m)', FIN_Z, 3)

# ======================================================================= items
I = P.item
I('g0', 'altar', 'Flame Altar', 22.5, 22.5, 3, 3, 3, color='#d9541e', iid='altar')
I('g0', 'stairs', 'Stairs up', 15, 17, 2, 4, 4, 0, '#a98a62', 'st1')
I('g1', 'stairs', 'Stairs up', 33, 26, 2, 4, 4, 180, '#a98a62', 'st2')
I('g2', 'stairs', 'Stairs to the catwalk', 20, 12, 2, 4, 4, 90, '#a98a62', 'st3')
chest_angles = [a for a in range(15, 360, 30) if min(abs(((a - d) + 180) % 360 - 180) for d in (0, 90, 180, 270)) > 20]
for k, a in enumerate(chest_angles):
    ar = math.radians(a)
    x = round((CX + 11.0 * math.sin(ar) - 0.5) * 2) / 2
    y = round((CY - 11.0 * math.cos(ar) - 0.5) * 2) / 2
    I('g0', 'mchest-small', 'Small Magic Chest', x, y, 1, 1, 1, color='#7b68b5', iid=f'mc{k}')
I('g0', 'quickstack', 'Quick Stack Station', 27.5, 31.5, 1, 1, 2, color='#4f7f8f', iid='qs')
I('g0', 'custom', 'Lectern', 23.5, 31.5, 1, 1, 1.5, color='#7a5236', iid='lect0')
def at(a, r, w, d):
    ar = math.radians(a)
    return (round((CX + r * math.sin(ar) - w / 2) * 2) / 2, round((CY - r * math.cos(ar) - d / 2) * 2) / 2)
x, y = at(45, 10.6, 2, 2); I('g1', 'custom', 'Scholar (1.0 survivor)', x, y, 2, 2, 2, color='#6a5a9a', iid='scholar')
for k, a in enumerate((135, 225, 315)):
    x, y = at(a, 10.6, 2, 1); I('g1', 'table', 'Reading table', x, y, 2, 1, 1, 0, '#9a7b52', f'rt{k}')
for k, a in enumerate((45, 135, 225, 315)):
    x, y = at(a, 10.6, 2, 1); I('g2', 'table', 'Map table' if k == 0 else 'Reading table', x, y, 2, 1, 1, 0, '#9a7b52', f'rt2{k}')
x, y = at(180, 10.6, 1, 1); I('g2', 'custom', 'Celestial globe', x, y, 1, 1, 2, color='#3fc2b0', iid='globe')
# lanterns at the bridge heads
for k, (x, y) in enumerate(((20.5, 2.0), (27.0, 2.0), (20.5, 45.5), (27.0, 45.5), (1.5, 20.5), (1.5, 27.0), (46.0, 20.5), (46.0, 27.0))):
    I('g0', 'light', 'Lantern', x, y, 0.5, 0.5, 1.5, color='#e3b341', iid=f'lan{k}')
I('fin', 'spire', 'Arcane finial', 23.5, 23.5, 1, 1, 3, color='#3fc2b0', iid='finial')

Z = P.zone
Z('g0', 'Altar & archive', 12, 12, 36, 36, '#2f8f8a')
Z('g1', 'Reading gallery', 12, 12, 36, 36, '#2f7fb3')
Z('g1', 'Balcony', 20, 38, 28, 40.5, '#b8862b')
Z('g2', 'Map & star gallery', 12, 12, 36, 36, '#8a5cc2')
Z('g3', 'Catwalk', 12, 12, 36, 36, '#5f7d3a')

problems = P.check(outdoor_ok=('g0',), ignore_types=('stairs', 'spire'))
print('item problems:', len(problems))
for p_ in problems[:30]: print('  ', p_)

NOTES = """Domed rotunda of the mage library, drafted by Claude. Uses 0.5 m squares, so every square is one single block. The campus site plan shows where it sits.

MATERIALS (real blocks, see the planner's block catalogue)
- Walls: Temple Stones on a Roughly Cut Stone Block plinth. Weathered Stone Block for ruins, Highly Polished Stone Block for columns, Mycelium Overgrown Block for mossy patches.
- Roofs: Castle Roof Block, with Drak Temple Roof Block for the mossy patches. Roughly Cut Stone ribs.
- Floors: Limestone Block indoors and on plazas, Field Stones outdoors, Rocky Stone Road Block paths, Refined Wood Block upstairs, Rough Wood Block bridges.
- Blue Luminescent Block inlays, Moss, Fertile Revelwood Dirt lawns, Farm Soil beds.
- Not blocks: doors, windows and glass, bookshelves and water.

SIZE
- 28 m across, walls 1 m (2 blocks) thick, about 36 m to the top of the lantern dome.
- 16 shallow pilasters ring the outside (half a block proud of the wall). Stained-glass windows sit between them.

LEVELS
- Ground (0-4 m): the Flame Altar sits at the centre inside rings of glowing inlay.
  - Shelving lines the walls, with magic chests in front: the campus archive.
  - Four doors. The south one is the great door, under a balcony between two portico columns.
  - The ground course is dark plinth stone with vines creeping up it.
- Galleries (4 m and 8 m): rings of floor round an open atrium, with railings.
  - Wall shelving (3 m) between tall stained-glass windows.
  - 8 double-sided book stacks (2 m tall) radiating between the windows, leaving the four axes clear.
  - The Scholar (the new 1.0 survivor), reading and map tables, and a celestial globe.
  - The south balcony opens off gallery 1.
- Drum (12-16 m): clerestory windows and a catwalk round the base of the dome. A stone cornice runs round the outside.
- Dome (16 m up): one smooth sloped roof of Castle Roof Block, 11 m high, overhanging the drum by 0.5 m.
  - The profile is a trimmed ellipse, so the dome meets the drum at a steep slope rather than straight down.
  - In game, build it in 0.5 m courses and let the voxel smoothing round them off.
  - Eight Roughly Cut Stone ribs stand 0.5 m proud. Drak Temple Roof Block moss patches creep over the lower courses.
  - A 5 m oculus opens at the top, under the lantern.
- Lantern: a 4 m tall glass drum with Highly Polished Stone posts, standing on the dome round the oculus.
  - Its own ribbed mini dome has a glowing Blue Luminescent crown, with the arcane finial on top.

STAIRS
- Straight flights: ground to 4 m (west), 4 to 8 m (east), 8 to 12 m (north, up to the catwalk).

OUTSIDE
- Mossy paving, a canal ring with four railed bridges, and the channel south to the reflecting pool.
"""
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mage-rotunda.json')
print('bytes', P.save(out, NOTES, 'r-claude-mage-rotunda-1'))
for lid in ('dome',):
    print('---', lid); print(P.preview(lid, 2, 0, 0, 96, 96))
