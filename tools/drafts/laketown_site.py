"""Laketown: the site plan. The 1 m layout (doc `laketown`, generator laketown.py) with each detail blueprint
stamped into it, simplified to 1 m squares, to check that the areas fit together. The layout itself stays
untouched as the reference.

Each detail blueprint is drawn in the layout's own coordinates with its corner at (OX, OY), so it drops
straight back in. A blueprint also draws the start of its neighbours (walkway stubs, the end of a stair, the
edge of a deck) for context; it only owns the rectangles listed in `own`. The layout is cleared there
(except the lake), and only what the blueprint drew inside them is stamped: its stubs of other areas, and
their items and labels, are left out, so the layout's version (or the neighbour's blueprint) stands.
Blueprints stamp in order, so a later one wins where two own the same strip.
After changing a detail blueprint, rerun its script, then this one, and write both docs.
Run: python laketown_site.py [-v]  ->  writes laketown_site.json (and rewrites laketown.json on the way)
     python laketown_site.py --try  ->  also stamps the blueprints marked pending (waiting for the user's review)
                                       and runs the checks, without saving: a dry run of the fit
"""
import contextlib
import io
import json
import os
import re
import runpy
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from mage_common import doc_to_chars
from laketown_common import LIB

# The site plan keeps everything each blueprint has in the rectangles it owns: every item and room label.
# It's saved packed (mage_common.pack_doc, planner v37), so it fits in one database document (256 KB).
# doors and windows in the planner's catalogue (it fills their labels in); others keep theirs
with open(os.path.join(HERE, '..', 'craft-src', 'doors-windows.json'), encoding='utf-8') as f_:
    CATALOGUE_OPENINGS = {re.sub(r'[^a-z0-9]+', '-', it_['name'].lower()).strip('-') for it_ in json.load(f_)['items']}


def slim(it):
    """An item without what the planner fills in itself: a label that's just its name, rot 0."""
    it = {k: v for k, v in it.items() if not (k == 'rot' and v == 0)}
    lab = it.get('label', '')                           # (only for types the planner's library knows)
    if (it['type'] in LIB and lab == LIB[it['type']][0]) or (it['type'] in CATALOGUE_OPENINGS and re.sub(r'[^a-z0-9]+', '-', lab.lower()).strip('-') == it['type']):
        it.pop('label', None)
    return it

with contextlib.redirect_stdout(io.StringIO()):
    P = runpy.run_path(os.path.join(HERE, 'laketown.py'))['P']    # the layout, with its palette loaded
P.name = 'Laketown: site (layout with the detail blueprints)'
LAYOUT_LEVELS = {L['id'] for L in P.levels}

# file, corner, tag, label;
# own: the rectangles (layout metres) the blueprint owns;
# heights: level heights to change so its layers merge with the layout's (or stay apart from them);
# joins: its stairs that join it to its neighbours (checked in full)
# pending=True: stamped only by --try, until the user has reviewed the blueprint
DETAILS = [
    dict(file='laketown_square.json', ox=54, oy=40, tag='sq', label='Square',
         own=[(56, 42, 112, 86), (62, 86, 112, 100)],
         # the stilts and the manor's front edge are the layout's own levels; the hall roofs share the
         # manor's elevation but not its level
         heights={'stilts': 12, 'manor': 5, 'hallroof': 4},
         joins=('Stairs: square to the causeway', 'Stairs: square to the west walkway', 'Stairs: square to the east walkway',
                'Grand stair to the manor', 'Side stair: tavern to the west landing')),
    dict(file='laketown_smithy.json', ox=10, oy=32, tag='sm', label='Smithy',
         own=[(12, 34, 44, 77), (44, 41.5, 56.5, 52.5)],
         heights={},
         joins=('West stair to the manor', "Stairs up to the villagers' quarter", 'Stairs up to the smithy')),
    dict(file='laketown_manor.json', ox=48, oy=4, tag='mn', label='Manor',
         own=[(50, 6, 110, 42)],
         heights={},
         joins=()),                                     # the stairs up to it belong to the square, smithy and farm
    dict(file='laketown_villagers.json', ox=2, oy=2, tag='vq', label='Villagers',
         own=[(3, 3, 46, 34), (44, 30, 48, 41.5)],
         heights={},
         joins=('Back steps down to the west landing',)),
    dict(file='laketown_carpentry.json', ox=0, oy=68, tag='cp', label='Carpentry',
         own=[(33.5, 76.5, 56, 83.5), (33.5, 83.5, 40.5, 92), (53.5, 83.5, 56, 86), (10, 92, 44, 126), (2, 96, 10, 124),
              (42, 109.5, 46, 116.5)],
         heights={},
         joins=('Stairs down to the carpentry', 'Stairs: carpentry to the arena', 'Stairs down to the west dock')),
    dict(file='laketown_bathhouse.json', ox=40, oy=76, tag='ba', label='Bathhouse and arena',
         own=[(46, 86, 62, 98), (57, 98, 61, 100), (46, 100, 72, 126)],
         heights={},
         joins=('Stairs down to the bathhouse', 'Stairs: bathhouse to the arena', 'Stairs down to the arena floor')),
    dict(file='laketown_gatehouse.json', ox=58, oy=98, tag='gh', label='Gatehouse',
         own=[(76.5, 100, 83.5, 132), (72, 109.5, 76.5, 116.5), (83.5, 118, 84, 124), (66, 132, 94, 142), (58, 142, 102, 158),
              (94, 135.5, 96, 140.5)],             # the east tower's lookout gallery
         heights={},
         joins=('Stairs up to the arena',)),
    dict(file='laketown_dock.json', ox=80, oy=96, tag='md', label='Main dock',
         own=[(84, 98, 112, 114), (84, 114, 108, 132), (95.5, 132, 106.5, 135), (108, 121.5, 128, 137)],
         heights={},
         joins=('Stairs down to the main dock', 'Stairs up to the smokehouse')),
    dict(file='laketown_farm.json', ox=106, oy=24, tag='fm', label='Farm',
         own=[(110, 30, 152, 66), (130, 28, 139, 30), (118, 66, 130, 72), (142.5, 66, 149.5, 74), (143, 74, 149, 76)],
         heights={},
         joins=('Service stair: farm to the manor', 'Stairs up to the research hall', 'Stairs up to the farm',
                'Herb bridge: farm to the alchemist')),
    dict(file='laketown_research.json', ox=114, oy=4, tag='rh', label='Research hall',
         own=[(118, 8, 152, 28), (152, 9, 154, 17)],
         heights={},
         joins=('Stairs up to the research hall',)),
    dict(file='laketown_alchemist.json', ox=110, oy=64, tag='al', label='Alchemist',
         own=[(112, 76.5, 116, 83.5), (115.5, 71.5, 130.5, 90.5), (130, 80.5, 136, 87.5), (117.5, 90, 124.5, 96), (136, 74, 156, 94)],
         heights={},
         joins=('Stairs up to the alchemist', 'Stairs up to the hunting lodge', 'Stairs up to the farm',
                'Herb bridge: farm to the alchemist')),
    dict(file='laketown_lodge.json', ox=110, oy=92, tag='hl', label='Hunting lodge',
         own=[(113.5, 95.5, 146.5, 116.5), (133.5, 116.5, 140.5, 120)],
         heights={},
         joins=('Stairs up to the hunting lodge', 'Stairs down to the smokehouse')),
    dict(file='laketown_smokehouse.json', ox=124, oy=108, tag='fs', label='Smokehouse',
         own=[(128, 120, 150, 136.5), (150, 112, 158, 136.5), (147, 112, 150, 120)],
         heights={},
         joins=('Stairs down to the fishing pier',)),
]

TRY = '--try' in sys.argv
DETAILS = [D for D in DETAILS if TRY or not D.get('pending')]


def in_own(own, x, y):
    return any(x0 <= x < x1 and y0 <= y < y1 for x0, y0, x1, y1 in own)


def centre(it, s, x0, y0):
    """An item's footprint centre in layout metres (s = metres per square, x0, y0 = the plan's corner)."""
    fw, fd = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
    return x0 + (it['x'] + fw / 2) * s, y0 + (it['y'] + fd / 2) * s


sources = {}                                            # site level id -> the blueprints stamped into it
for D in DETAILS:
    doc = doc_to_chars(json.load(open(os.path.join(HERE, D['file']), encoding='utf-8')))
    ox, oy, own, sc = D['ox'], D['oy'], D['own'], doc['cell']
    # clear the layout where the blueprint owns whole squares (keep the lake), and its items and labels there
    for L in P.levels:
        if L['id'] == 'lake':
            continue
        g = P.grids[L['id']]
        for x0, y0, x1, y1 in own:
            for y in range(int(-(-y0 // 1)), int(y1 // 1)):
                for x in range(int(-(-x0 // 1)), int(x1 // 1)):
                    g[y][x] = ' '
    n_items, n_zones = len(P.items), len(P.zones)
    P.items = [it for it in P.items if not in_own(own, *centre(it, P.cell, 0, 0))]
    P.zones = [z for z in P.zones if not in_own(own, z['x'] + z['w'] / 2, z['y'] + z['h'] / 2)]
    n_items, n_zones = n_items - len(P.items), n_zones - len(P.zones)
    # keep only what the blueprint drew inside the rectangles it owns
    for L in doc['levels']:
        if L['id'] in D['heights']:
            L['height'] = D['heights'][L['id']]
        lx, ly = L.get('ox', 0), L.get('oy', 0)
        L['rows'] = [''.join(c if in_own(own, ox + (lx + i + 0.5) * sc, oy + (ly + j + 0.5) * sc) else ' ' for i, c in enumerate(row))
                     for j, row in enumerate(L['rows'])]
    doc['items'] = [it for it in doc['items'] if in_own(own, *centre(it, sc, ox, oy)) and it['type'] != 'spawn']   # (one spawn point, below)
    doc['zones'] = [z for z in doc['zones'] if in_own(own, ox + (z['x'] + z['w'] / 2) * sc, oy + (z['y'] + z['h'] / 2) * sc)]
    lev = P.stamp(doc, ox, oy, D['tag'], D['label'])
    if '-v' in sys.argv:
        print('  levels:', {k: v for k, v in lev.items()})
    for sid, tid in lev.items():
        sources.setdefault(tid, []).append(D['label'])
        if tid not in LAYOUT_LEVELS:                    # "Square: Tavern porch roof", without the height
            base = re.sub(r'\s*\([^)]*\)\s*$', '', next(L['name'] for L in doc['levels'] if L['id'] == sid))
            base = re.sub(rf"^{re.escape(D['label'])}:\s*", '', base)      # "Manor: base course", not "Manor: Manor: ..."
            name = f"{D['label']}: {base}"
            next(L for L in P.levels if L['id'] == tid)['name'] = name if len(name) <= 40 else name[:38].rstrip(' ,:') + '…'
    print(f"{D['label']}: replaced {n_items} items and {n_zones} labels already there")
# walk mode starts at the square's south entrance, facing up the promenade (each blueprint keeps its own spawn)
P.items = [it for it in P.items if it['type'] != 'spawn']
P.item('mid', 'spawn', 'Spawn point', 79.5, 91, 1, 1, 0.5, 180, '#2fa36b')
# levels left empty at 1 m (a row of lamps, a banner) go
keep = {it['level'] for it in P.items} | {z['level'] for z in P.zones}
for L in [L for L in P.levels if L['id'] not in keep and not any(c != ' ' for r in P.grids[L['id']] for c in r)]:
    P.levels.remove(L); del P.grids[L['id']]
    print('empty at 1 m, left out:', L['name'])
print('levels:', len(P.levels))
# a level two blueprints stamped into gets a name for both
for L in P.levels:
    labs = sorted(set(sources.get(L['id'], [])))
    if L['id'] not in LAYOUT_LEVELS and len(labs) > 1:
        name = f"+{L['elev']:g} m, {L['height']:g} m tall: {', '.join(labs)}"
        L['name'] = name if len(name) <= 40 else name[:39].rstrip(' ,') + '…'

# The checks. What matters here is the joins: the layout's own items and the stairs that join areas.
# Inside a stamped blueprint, doors and furniture squeezed onto 1 m squares throw up problems the 0.5 m
# blueprint doesn't have (it passes its own checks): those are only counted.
tags = tuple(D['tag'] + '-' for D in DETAILS)
join_stairs = {lab for D in DETAILS for lab in D['joins']}
own_ids = {it['id'] for it in P.items if it['id'].startswith(tags)}
own_labels = {it['label'] for it in P.items if it['id'].startswith(tags)} - {it['label'] for it in P.items if not it['id'].startswith(tags)}
problems = P.check(outdoor_ok=('lake',), ignore_types=('stairs',))
access = P.check_access(clear=1.0)
outside = P.altar_problems()
subject = lambda m: m.split(':')[0].split(' at ')[0]
at_joins = [m for m in problems if m.split(' ')[0] not in own_ids] + \
           [m for m in access if subject(m) not in own_labels or subject(m) in join_stairs]
inside = [m for m in problems + access if m not in at_joins]
print('problems at the joins:', len(at_joins))
for m in at_joins:
    print('  ', m)
print(f'inside the stamped blueprints, from simplifying to 1 m: {len(inside)}')


def area_of(m):
    """The blueprint a problem is in, by its coordinates (both formats: 'at 62.0,55.0 m' and 'at 72,86')."""
    pts = [(float(a), float(b)) for a, b in re.findall(r'at (-?[\d.]+),(-?[\d.]+)', m)]
    for D in reversed(DETAILS):                         # a later blueprint wins where two own the same strip
        if any(in_own(D['own'], x + 0.5, y + 0.5) for x, y in pts):
            return D['label']
    return 'the layout'


per_area = {}
for m in inside:
    per_area[area_of(m)] = per_area.get(area_of(m), 0) + 1
print('  by area:', ', '.join(f'{k} {v}' for k, v in per_area.items()) or 'none')
print("outside the altar's build volume:", outside or 'nothing')
if '-v' in sys.argv:
    for m in inside:
        print('    (1 m)', m)

NOTES = """Laketown: the site plan, generated by Claude. It's the 1 m layout (doc laketown) with each detail blueprint stamped in, simplified to 1 m squares, to check that the areas fit together. Don't edit it by hand: change the layout or a detail blueprint and regenerate it. The layout stays as the reference.

STAMPED IN (all thirteen areas)
- The main square (doc laketown-square, 0.5 m, finished), at its corner (54, 40): the square, promenade and grand stair, the storage halls, the market stalls, the tavern and the lodging house.
- The smithy (doc laketown-smithy, 0.5 m, finished), at its corner (10, 32): the forge hall, furnace shed, store, cottage and yards, the west landing and the west stair up to the manor.
- The manor (doc laketown-manor, 0.5 m, finished), at its corner (48, 4): the house (gallery, centre block with portico and cupola, east wing), the two towers (the west one the Collector's clock tower), the front terrace, and the gardens with the pavilion.
- The villagers' quarter (doc laketown-villagers, 0.5 m, finished), at its corner (2, 2): eight homes round a green with a well, the dining hall with its bell-cote at the head of the green, allotments, and the back steps down to the west landing.
- The carpentry and west walkway (doc laketown-carpentry, 0.5 m, finished), at its corner (0, 68): the west walkway and its branches, the north range (storehouse and workshop), the kiln shed, the stone and timber yards with the drying shed and jib crane, the work yard, the Carpenter's cottage, the west dock, and the stairs to the dock and the arena.
- The bathhouse and arena (doc laketown-bathhouse, 0.5 m, finished), at its corner (40, 76): the Barber's bathhouse with its plunge pool, salon and loggia; the arena with its sand floor, three tiers of seats, champion's box and the ways in from the carpentry, the causeway and the bathhouse.
- The causeway, gatehouse and shore landing (doc laketown-gatehouse, 0.5 m, finished), at its corner (58, 98): the causeway with its drawbridge and the arena branch, the gatehouse (two towers either side of an open arch, two portcullises, the wall-walk), and the shore landing.
- The main dock (doc laketown-dock, 0.5 m, finished), at its corner (80, 96): the quay and the south quay, the harbourmaster's office, the trading pier and its crane, the stone mole and the harbour light, the warehouse, the boardwalk and the boathouse.
- The farm (doc laketown-farm, 0.5 m, finished), at its corner (106, 24): the farmhouse, the barn, the yard and lane, the byre and pens, the fields, the nursery and apiary, the service stair to the manor and the herb bridge.
- The research hall (doc laketown-research, 0.5 m, finished), at its corner (114, 4): the hall of research, the Researcher's round tower with its observatory, and the mill-house with the Mill and its water wheel.
- The alchemist and east junction (doc laketown-alchemist, 0.5 m, finished), at its corner (110, 64): the east walkway's end, the junction with its pavilion and stairs, and the Alchemist's round tower and herb garden.
- The hunting lodge (doc laketown-lodge, 0.5 m, finished), at its corner (110, 92): the lodge hall with the Hunter's loft, the tannery shed, the weaving house, the drying racks and the archery lane.
- The Fisher's smokehouse and fishing pier (doc laketown-smokehouse, 0.5 m, finished), at its corner (124, 108): the yard, the bunkhouse under an upturned boat's hull, the drying green, the fishing pier with its boats, and the stone smokehouse on the pier head.

Each blueprint only replaces the area it owns; the starts of its neighbours that it drew for context are left to the layout (or the neighbour's own blueprint).

AT 1 M: walls, doors and windows always survive; everything else goes by majority, so 0.5 m trim (railings, kerbs, window boxes) thickens to 1 m or drops out, and roofs step a metre at a time. A lone 0.5 m post drops out too, so the flag over the manor's cupola floats and the finials are gone. Furniture is nudged off walls that thickened. The detail blueprint is the one to build from.
"""
P.items = [slim(it) for it in P.items]
out = os.path.join(HERE, 'laketown_site.json')
if TRY:                                                 # its size, to check it would still fit in one document
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), 'laketown_site.try.json')
    print('bytes it would take', P.save(tmp, NOTES, 'r-claude-laketown-site-try'), '(at most 262144)')
    os.remove(tmp)
    print('dry run (--try): with the pending blueprints, not saved')
    sys.exit()
print('bytes', P.save(out, NOTES, 'r-claude-laketown-site-23'))
for a, b in P.merged:
    print('  folded:', a, '->', b)
