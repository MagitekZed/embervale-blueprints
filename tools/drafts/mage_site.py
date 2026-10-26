"""Mage library campus: 1 m site plan for an altar level 4 (160 m) build area.

Run: python mage_site.py  ->  writes mage-site.json.
The buildings come from the 0.5 m detail plans (run their scripts first): each is stamped in with
Plan.stamp, which simplifies it to 1 m squares. This script only draws the landscape between them.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mage_common import Plan

P = Plan('Mage library: campus site plan', 1, 160, 160, 160)
P.project = 'Mage library'
g0 = P.level('g0', 'Ground', 0, 4)
g1 = P.level('g1', 'Upper storey (4 m)', 4, 4)
g2 = P.level('g2', 'Roofs & roof gardens (8 m)', 8, 4)
g3 = P.level('g3', 'Rotunda drum, tower (12 m)', 12, 4)

# ======================================================================= landscape
# paths between the buildings (the detail plans bring their own plazas, bridges and path ends)
P.rect(g0, 52, 78, 59, 83, ':')                                # forge yard -> rotunda
P.rect(g0, 40, 33, 57, 36, ':'); P.rect(g0, 37, 33, 40, 62, ':')   # cloister -> smithy
P.rect(g0, 102.5, 78, 111, 83, ':')                            # rotunda -> tower bridge
P.rect(g0, 93, 108, 104, 111, ':'); P.rect(g0, 123, 122, 128, 128, ':')   # survivors' hall
P.rect(g0, 99, 125, 128, 128, ':'); P.rect(g0, 122, 95, 127, 100, ':')
P.rect(g0, 77, 145, 84, 160, ':')                              # approach road

# farm, pens, fishing (south-west)
P.box_walls(g0, 14, 108, 44, 140, 'w', 1, floor='h')
for y0 in (110, 116, 122, 128, 134):
    P.rect(g0, 16, y0, 42, y0 + 4, 'f')
P.rect(g0, 43, 124, 44, 127, ':')
P.rect(g0, 44, 124, 47, 139, ':'); P.rect(g0, 44, 136, 62, 139, ':')
P.disc(g0, 40.5, 150.5, 7, '~'); P.rect(g0, 39, 141, 42, 147, 'b')
P.scatter(g0, 14, 108, 44, 140, 'V', 0.02, 'h', 71)

# overgrown grove + spring (north-east)
P.disc(g0, 130, 36, 13, ';')
P.disc(g0, 130, 36, 7, '~'); P.disc(g0, 137, 41, 5, '~')
for k in range(12):
    a = math.radians(k * 30)
    x, y = 130 + 11.5 * math.sin(a), 36 - 11.5 * math.cos(a)
    if k in (2, 7):
        continue                                              # fallen columns
    P.rect(g0, int(x), int(y), int(x) + 1, int(y) + 1, 'R' if k in (4, 9, 11) else 'P')
P.rect(g0, 104, 33, 118, 36, ':'); P.rect(g0, 122, 49, 127, 66, ':')
P.scatter(g0, 104, 20, 150, 60, 'V', 0.04, ';:', 81)

# ======================================================================= buildings, from the detail plans
# (plan, where its north-west corner sits on the site in metres, tag, label); later ones win overlaps,
# so the rotunda goes last and its plaza and canal stay whole
DETAILS = [
    ('mage-cloister.json', 55, 2, 'clo', 'Cloister'),
    ('mage-forge.json', 12, 60, 'frg', 'Forge'),
    ('mage-hall.json', 102, 98, 'hal', 'Hall'),
    ('mage-gate.json', 58, 96, 'gat', 'Gate'),
    ('mage-tower.json', 109.5, 65.5, 'twr', 'Tower'),
    ('mage-rotunda.json', 56.5, 56.5, 'rot', 'Rotunda'),
]
for fn, ox, oy, tag, label in DETAILS:
    doc = json.load(open(os.path.join(HERE, fn), encoding='utf-8'))
    P.stamp(doc, ox, oy, tag, label)

# ======================================================================= items (outside the detailed buildings)
I = P.item
I('g0', 'npc-farmer', 'Farmer', 45, 128, 2, 2, 2, color='#7c9a3d', iid='farmer')
for k in range(3):
    I('g0', 'seedbed', 'Seedbed', 48, 129 + k * 3, 2, 2, 0.5, color='#6f8a43', iid=f'seed{k}')
I('g0', 'pen', 'Animal pen', 48, 108, 8, 8, 1, color='#a0905a', iid='pen1')
I('g0', 'pen', 'Animal pen', 48, 117, 8, 8, 1, color='#a0905a', iid='pen2')
I('g0', 'npc-fisher', 'Fisher', 43, 141, 2, 2, 2, color='#3f7f9e', iid='fisher')
I('g0', 'fishing', 'Fishing spot', 39, 145, 2, 2, 1, color='#3f8fc1', iid='fish')
for k, (x, y) in enumerate(((112, 15), (145, 20), (114, 51), (145, 52))):
    I('g0', 'tree', 'Ancient tree', x, y, 4, 4, 14, color='#4f6b34', iid=f'gtree{k}')
I('g0', 'custom', 'Arcane obelisk', 121, 25, 1, 1, 6, color='#3fc2b0', iid='ob1')
I('g0', 'custom', 'Arcane obelisk', 139, 49, 1, 1, 6, color='#3fc2b0', iid='ob2')
for k, (x, y) in enumerate(((106, 79), (55, 82))):
    I('g0', 'light', 'Lantern', x, y, 1, 1, 1, color='#e3b341', iid=f'lan{k}')

Z = P.zone
Z('g0', 'Farm', 15, 109, 43, 139, '#3f8a4f')
Z('g0', 'Animals', 47, 107, 57, 126, '#a0905a')
Z('g0', 'Fishing pond', 33, 141, 49, 158, '#3f7f9e')
Z('g0', 'Overgrown grove & spring', 108, 12, 152, 60, '#5f7d3a')
Z('g0', 'Expansion (future builds)', 8, 8, 52, 56, '#8a5cc2')

problems = P.check(outdoor_ok=('g0',), ignore_types=('stairs', 'spiral', 'tree', 'spire'))
print('item problems:', len(problems))
for p_ in problems[:40]: print('  ', p_)

NOTES = """Mage library campus, drafted by Claude. This is the 1 m site plan: every square is 1 m (a 1M cube).

HOW IT'S MADE
- Every building has its own 0.5 m detail plan: rotunda, wizard tower, cloister, forge court, survivors' hall, and gate & colonnades.
- This map stamps each of them in, simplified to 1 m squares:
  - Walls, doors and windows always survive.
  - Everything else goes by what covers most of each square.
  - Roof heights are averaged and rounded to whole metres.
- Change a building in its detail plan, then rebuild this map from it. Edit the landscape between the buildings here.

STYLE
- Ancient & overgrown: weathered temple stone, dark plinths, green-grey roofs, glowing blue inlays, ruined colonnades, moss everywhere.

ROOFS
- Rotunda: a smooth ribbed dome with a lantern and mini dome.
- Wizard tower: a witch-hat cone.
- North range: a gable with dormers, plus a glass greenhouse roof.
- Forge court: cross-gables, with a monitor over the smithy.
- Survivors' hall: a tall tiled gable with a roof garden beside it.
- Gate: pointed pylon caps, and lean-tos over the colonnades.

ALTAR
- Altar level 4 (160 m). The Flame Altar sits under the dome at the heart of the rotunda, and the campus is laid out around it.
- Everything here is within about 80 m of it. Magic chests reach crafting stations within about 100 m, so the rotunda archive covers the whole campus.

LAYOUT (north is up)
- Centre: domed rotunda library, 28 m across, ringed by a canal with four bridges.
- South: reflecting pool between ruined colonnades, down to an entrance plaza and the broken ancient gate.
- North: herb garden cloister, with the north range behind it (alchemy lab, arcane workshop, greenhouse).
- East: wizard tower on an island in a pond.
- West: forge court, three wings round a work yard.
- South-east: survivors' hall with its roof garden.
- South-west: walled farm with the Farmer, animal pens, and a fishing pond with the Fisher.
- North-east: an overgrown grove with a spring and a ring of ruined columns.
- North-west: left open for future builds.

NOTES
- Every crafting station is a 2 x 2 m placeholder until measured in game. Chest and furniture sizes are estimates.
- The Scholar is the new 1.0 survivor who specialises in Ancient knowledge. Keen hasn't published a name yet.
"""
out = os.path.join(HERE, 'mage-site.json')
print('bytes', P.save(out, NOTES, 'r-claude-mage-site-2'))
for a, b in P.merged:
    print('  folded:', a, '->', b)
print('levels', [(L['id'], L['elev'], L['height']) for L in P.levels])
print('palette', len(set(c for g in P.grids.values() for r in g for c in r) - {' '}))
