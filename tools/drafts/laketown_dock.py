"""Laketown: the main dock, the inner harbour and the boardwalk. 0.5 m detail plan. Pass 3 of 3: review and finishing touches.

The town's harbour, for boats and trade, at +1 m. The causeway's stair comes down onto the quay, which runs
along the harbour's south side between the causeway and the boardwalk. Into the harbour reach the trading
pier, with a jib crane at its head, and the stone mole on the east, sheltering the moorings, with the harbour
light at its end. The harbourmaster's office stands over the water at the harbour's south-west corner by the
causeway, looking out over the moorings, with a landing stage for the harbour boat. Behind the quay: the
warehouse (stone below, a tarred timber gable to the quay, a loft) and the open south quay, kept low so the
gatehouse's watch tower can see over. The boardwalk runs east to the smokehouse's stair, past the boathouse.

Coordinates are the layout's (doc `laketown`): this plan's corner is the layout's (80, 96).
Run: python laketown_dock.py  ->  writes laketown_dock.json
"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laketown_common import Area, WOOD, STONE, BED
from mage_common import PALETTE, load_doc, doc_to_chars

RS, RCS, TAR, CASTLE = '#7d776a', '#62605d', '#5d5652', '#7c8084'
OX, OY = 80, 96
A = Area('Laketown: main dock, harbour and boardwalk (detail)', OX, OY, 50, 47, {
    'k': {'name': 'Roughly Cut Stone Block', 'kind': 'floor', 'color': RCS},            # the mole
    'c': {'name': 'Conifer Wood Block', 'kind': 'floor', 'color': '#6e5a51'},           # the hunting lodge (its blueprint)
    'H': {'name': 'Half-Timbered Block', 'kind': 'wall', 'color': '#71665e'},           # the harbourmaster's office
    'S': {'name': 'Rough Stone Block', 'kind': 'wall', 'color': RS},                    # the warehouse
    'm': {'name': 'Tarred Wood Block (gable course)', 'kind': 'wall', 'color': TAR, 'height': 0.5},
    'L': {'name': 'Rough Stone Block (harbour light)', 'kind': 'wall', 'color': RS, 'height': 6},
    'h': {'name': 'Rough Stone Block (foundation)', 'kind': 'wall', 'color': RS, 'height': 4.5},
    'p': {'name': 'Roughly Cut Stone Block (parapet)', 'kind': 'block', 'color': RCS, 'height': 1},
    'o': {'name': 'Roughly Cut Stone Block (parapet pier)', 'kind': 'block', 'color': RCS, 'height': 1.5},
    'n': {'name': 'Tarred Wood Block (boathouse post)', 'kind': 'block', 'color': '#4e4844', 'height': 3.5},
    'U': {'name': 'Refined Wood Block (lamp post)', 'kind': 'block', 'color': WOOD, 'height': 2},
    'B': {'name': 'Tarred Wood Block (boathouse wall)', 'kind': 'wall', 'color': TAR, 'height': 3.5},
})
P, R, zone, put = A.P, A.R, A.zone, A.put
stl = A.level('stilts', 'Stilts and foundations, standing on the lake bed (-4 m)', BED, 12)
lake = A.level('lake', 'Lake (water level, 0 m)', 0, 1)
dock = A.level('dock', 'Quay, piers, office, warehouse, boardwalk (+1 m)', 1, 4)
low = A.level('low', 'Smokehouse, its edge (+2 m)', 2, 4)
walk = A.level('walk', 'Causeway and gatehouse, their edges (+3 m)', 3, 4)
mid = A.level('mid', 'Hunting lodge, its edge (+4 m)', 4, 4)
o5 = A.level('o5', "Harbourmaster's office: upstairs (+5 m)", 5, 4)
wh5 = A.level('wh5', 'Warehouse: the loft (+5 m)', 5, 4)
whroof = A.level('whroof', 'Warehouse: the roof (+5.5 m)', 5.5, 6)
oroof = A.level('oroof', "Harbourmaster's office: the roof (+9 m)", 9, 5)
bhroof = A.level('bhroof', 'Boathouse: the roof (+4.5 m)', 4.5, 5)
jib = A.level('jib', 'Trading pier: the crane jib (+6.5 m)', 6.5, 1)
hook = A.level('hook', 'Trading pier: the crane hook (+3.5 m)', 3.5, 1)
light7 = A.level('light7', 'Harbour light: the lantern (+7 m)', 7, 1.5)
lightcap = A.level('lightcap', 'Harbour light: its cap (+8.5 m)', 8.5, 2)
lt6 = A.level('lt6', 'Harbour light: its string course (+6 m)', 6, 1)
lamp3 = A.level('lamp3', 'Lamps on the posts (+3 m)', 3, 1)
brace = A.level('brace', 'Trading pier: the crane brace (+1 m)', 1, 7)
cargo1 = A.level('cargo1', "Trading boat: cargo on its deck (+1 m)", 1, 2)
cartload = A.level('cartload', 'Quay: the handcart, its load (+1 m)', 1, 2)
yard = A.level('yard', 'Trading boat: the yard and the furled sail (+6.5 m)', 6.5, 1.5)
hoist = A.level('hoist', 'Warehouse: the hoist beam (+8.5 m)', 8.5, 1)
mast13 = A.level('mast13', "Harbourmaster's office: the signal mast (+13 m)", 13, 5)
pennant = A.level('pennant', "Harbourmaster's office: the pennant (+17 m)", 17, 1)
ocap = A.level('ocap', "Harbourmaster's office: the chimney pot (+14.5 m)", 14.5, 1)
hang = A.level('hang', 'Trading pier: a bale on the crane hook (+1 m)', 1, 4)


def lamp(x, y, g=None):
    """A lamp post (2 m) with a lamp on top: over the deck (keeping its floor), or in a railing (g = its level)."""
    if g is None:
        A.overlay(dock, x, y, x + 0.5, y + 0.5, 'Refined Wood Block (lamp post)', WOOD, 2, 0)
    else:
        R(g, x, y, x + 0.5, y + 0.5, 'U')
    R(lamp3, x, y, x + 0.5, y + 0.5, P._alloc({'name': 'Yellow Luminescent Block (lamp)', 'kind': 'block', 'color': '#bd9a5f', 'height': 0.5}))


def bollard(x, y, stone=False):
    A.overlay(dock, x, y, x + 0.5, y + 0.5, 'Rough Stone Block (bollard)' if stone else 'Tarred Wood Block (bollard)', RS if stone else '#4e4844', 1, 0)


def boat(cells, name, color=WOOD):
    """A boat built from blocks on the water: cells are (x0, y0, x1, y1, height, base) in layout metres."""
    for x0, y0, x1, y1, h, b in cells:
        A.overlay(lake, x0, y0, x1, y1, name, color, h, b)


def rowing_boat(x0, y0, along, label):
    """A rowing boat 1.5 m wide and 4 m long from (x0, y0), its bow towards -x ('x') or -y ('y'): a 1 m gunwale
    round a 0.5 m floor, the bow pointed."""
    if along == 'x':
        cells = [(x0, y0 + 0.5, x0 + 0.5, y0 + 1, 1, 0), (x0 + 3.5, y0, x0 + 4, y0 + 1.5, 1, 0),
                 (x0 + 0.5, y0, x0 + 3.5, y0 + 0.5, 1, 0), (x0 + 0.5, y0 + 1, x0 + 3.5, y0 + 1.5, 1, 0),
                 (x0 + 0.5, y0 + 0.5, x0 + 3.5, y0 + 1, 0.5, 0)]
        z = (x0, y0, x0 + 4, y0 + 1.5)
    else:
        cells = [(x0 + 0.5, y0, x0 + 1, y0 + 0.5, 1, 0), (x0, y0 + 3.5, x0 + 1.5, y0 + 4, 1, 0),
                 (x0, y0 + 0.5, x0 + 0.5, y0 + 3.5, 1, 0), (x0 + 1, y0 + 0.5, x0 + 1.5, y0 + 3.5, 1, 0),
                 (x0 + 0.5, y0 + 0.5, x0 + 1, y0 + 3.5, 0.5, 0)]
        z = (x0, y0, x0 + 1.5, y0 + 4)
    boat(cells, 'Refined Wood Block (rowing boat)')
    zone('lake', label, *z, '#2f7fb3')

# ================================================================= the lake and the shore
# The layout's ground: the lake bed 4 m down, shelving up to the beach along the south.
def shoreline(x):
    return 140 + 2 * math.sin(x / 21) + 1.2 * math.sin(x / 8.3 + 1.3)


def ground(x, y):
    s = shoreline(x)
    if y < s:
        return -min(4, max(1, round((s - y) / 1.5)))
    return min(3, 1 + math.floor((y - s) / 3))


P.ground_fn(lambda mx, my: ground(mx + OX, my + OY))
P.ground_rect(74 - OX, 139 - OY, 86 - OX, 142 - OY, 3, 'max')      # the gatehouse's forecourt
P.ground_rect(60 - OX, 142 - OY, 100 - OX, 160 - OY, 3, 'max')     # and its landing, on the meadow
for x, y in P.cells_rect(0, 0, 50, 47):
    if P.ground_at(x, y) < 0:
        lake[y][x] = '~'
zone('lake', 'Inner harbour', 84, 98, 112, 114, '#2f7fb3')

# ================================================================= the quay (+1 m)
# Tarred wood along the harbour's south side, from the causeway to the boardwalk; the causeway's stair comes
# down onto its west end (stone cheeks, as the walkways' stairs have)
R(dock, 84, 114, 108, 124, 't')
A.stairs('dock', 'Stairs down to the main dock', 84, 118, 88, 124, 2, 'W')
A.cheeks(dock, 84, 118, 88, 124, 'W')
zone('dock', 'Quay (goods landed)', 88, 114, 108, 122, '#2f7fb3')
# the south quay, between the stair and the warehouse: open, kept low in front of the gatehouse's watch tower
# (its edge 1 m short of the tower's prow, out of the moat)
R(dock, 84, 124, 96, 132, 't')
zone('dock', 'South quay (open)', 84, 124.5, 96, 132, '#2f7fb3')
# goods waiting on the quay either side of the warehouse door, a handcart, a bench over the rowing boats'
# slot, lamps at the stair's foot and where the boardwalk starts
put('dock', 'Scrappy Crate', 96.5, 121); put('dock', 'Scrappy Crate', 97.5, 121); put('dock', 'Supply Sacks II', 96.5, 122)
put('dock', 'Scrap Vat I', 104.5, 121.5, label='Scrap Vat I (a barrel)'); put('dock', 'Scrap Vat I', 105.5, 121.5, label='Scrap Vat I (a barrel)')
put('dock', 'Scrap Vat I', 104.5, 122.5, label='Scrap Vat I (a barrel)')
for x in (90, 92):
    A.overlay(dock, x, 116.5, x + 0.5, 117.5, 'Tarred Wood Block (cart wheel)', TAR, 1, 0)
A.overlay(dock, 90.5, 116, 92, 118.5, 'Refined Wood Block (cart bed)', WOOD, 0.5, 0.5)
for x in (90.5, 91.5):
    A.overlay(dock, x, 118.5, x + 0.5, 119, 'Refined Wood Block (cart shafts)', WOOD, 0.5, 0.5)
    A.overlay(dock, x, 119, x + 0.5, 120, 'Refined Wood Block (cart shafts)', WOOD, 0.5, 0)
R(cartload, 90.5, 116, 92, 117, P._alloc({'name': 'Refined Wood Block (crates on the cart)', 'kind': 'block', 'color': '#8c6b4f', 'height': 1, 'base': 1}))
zone('dock', 'Handcart', 90, 116, 92.5, 120, '#7a6653')
put('dock', 'Bench', 94, 114.5, 180, label='Bench (over the rowing boats)')
rowing_boat(94.5, 106, 'y', 'Rowing boat (moored)')
lamp(88, 117.5); lamp(107.5, 121.5); lamp(95.5, 131.5)
put('dock', 'Scrap Vat I', 85, 126.5, label='Scrap Vat I (a barrel)'); put('dock', 'Scrap Vat I', 86, 126.5, label='Scrap Vat I (a barrel)')
put('dock', 'Resource Bundle II', 93.5, 128.5); put('dock', 'Resource Bundle I', 93.5, 129.5)

# ================================================================= the harbourmaster's office (+1 m and +5 m)
# Over the water at the harbour's south-west corner, by the causeway, looking out over the moorings: two
# storeys of half-timbering, 8 x 8 m, a tiled gable roof with its gables to the causeway and the trading pier,
# a landing stage round its north and east sides for the harbour boat, its door onto the quay. The stair runs
# up the west wall (on whole metres, so it stays clean at 1 m).
R(dock, 85, 104, 94, 114, 't')
for g in (dock, o5):
    A.walls(g, 85, 105, 93, 113, 'H', 'r')
A.door('dock', 'Wooden Door', 88, 112.5, 90, 113)
A.stairs('dock', 'Office stair', 86, 107, 88, 111, 4, 'N')
R(o5, 85.5, 107, 88, 111, ' ')                                       # the stairwell, a railing round it
A.rail(o5, 88, 107, 88.5, 111.5); A.rail(o5, 85.5, 111, 88, 111.5)
# windows: the office looks out over the moorings and the pier; upstairs over the causeway and the quay too
for x0 in (89, 91):
    A.win('dock', 'Wooden Window Frame', x0, 105, x0 + 1, 105.5, 1)
for y0 in (108.5, 110.5):
    A.win('dock', 'Wooden Window Frame', 92.5, y0, 93, y0 + 1, 1)
A.win('o5', 'Wooden Window Frame', 86.5, 105, 87.5, 105.5, 1)
A.win('o5', 'Wooden Window Frame', 85, 108.5, 85.5, 109.5, 1)
for x0 in (87.5, 90.5):
    A.win('o5', 'Wooden Window Frame', x0, 112.5, x0 + 1, 113, 1)
# the harbour side: a balcony off the harbourmaster's room over the landing stage, on brackets, where he can
# watch the moorings
A.door('o5', 'Wooden Door', 89, 105, 91, 105.5)
R(o5, 86, 103.5, 92, 105, 'r')
A.rail(o5, 86, 103.5, 92, 104); A.rail(o5, 86, 104, 86.5, 105); A.rail(o5, 91.5, 104, 92, 105)
for x in (86.5, 91):
    A.overlay(dock, x, 104, x + 0.5, 105, 'Refined Wood Block (balcony bracket)', WOOD, 0.5, 3.5)
zone('o5', 'Balcony (over the moorings)', 86.5, 104, 91.5, 105, '#9c6b8e')
# a stone chimney corbelled out from the east gable, for the fire upstairs, a pot on top
put('o5', 'Stone Fireplace', 91.5, 108, 90, label="Stone Fireplace (the harbourmaster's)")
R(o5, 93.5, 108.5, 94.5, 109.5, P._alloc({'name': 'Rough Stone Block (chimney)', 'kind': 'wall', 'color': RS, 'height': 9.5}))
A.overlay(dock, 93.5, 108.5, 94, 109.5, 'Rough Stone Block (chimney corbel)', RS, 0.5, 3.5)
R(ocap, 93.5, 108.5, 94, 109, P._alloc({'name': 'Fired Bricks Block (chimney pot)', 'kind': 'block', 'color': '#aa7657', 'height': 0.5}))
ro = A.roof(oroof)
ro.gable(85, 105, 93, 113, 'x', 'tiles', pitch=1.0, overhang=0.5)
ro.paint()
# the signal mast on the west gable's apex, over the causeway, its pennant streaming
R(mast13, 85.5, 108.5, 86, 109, P._alloc({'name': 'Refined Wood Block (signal mast)', 'kind': 'block', 'color': WOOD, 'height': 4.5}))
R(pennant, 86, 108.5, 88, 109, P._alloc({'name': 'Red Carpet Block (pennant)', 'kind': 'block', 'color': '#9e3742', 'height': 0.5}))
# inside: the office below (the harbourmaster's counter facing the door, a map table under the harbour
# windows, a shelf of ledgers, the strongbox), his room above (bed, wardrobe, chest, a chair by the fire)
put('dock', 'Wooden Tavern Counter', 89.5, 109.5); put('dock', 'Rustic Chair', 90, 108.5)
put('dock', 'table', 89.5, 106, label='Table (charts of the lake)'); put('dock', 'Rustic Chair', 90, 107, 180)
put('dock', 'High Crude Wooden Shelf', 92, 106, 90, label='High Crude Wooden Shelf (ledgers)')
put('dock', 'chest-medium', 91, 111.5, 180, label='Medium Chest (the strongbox)')
put('dock', 'Hanging Lantern', 89, 108.5)
put('dock', 'Wall Lantern', 90.5, 113, 0, 2.0)
put('o5', 'bed', 88.5, 109, label='Bed (the harbourmaster)'); put('o5', 'Crude Wooden Closet', 91.5, 106, 90)
put('o5', 'chest-small', 91.5, 110.5); put('o5', 'Rustic Chair', 90.5, 107, 90)
put('o5', 'Hanging Lantern', 89.5, 107.5)
zone('dock', "Harbourmaster's office", 88.5, 105.5, 92.5, 112.5, '#9c6b8e')
zone('o5', "Harbourmaster's room", 88.5, 105.5, 92.5, 112.5, '#9c6b8e')
zone('dock', 'Landing stage (the harbour boat)', 85, 104, 94, 105, '#2f7fb3')
# the harbour boat at the landing stage, its line to a bollard; bollards round the stage
rowing_boat(86.5, 102, 'x', 'Harbour boat (moored)')
A.overlay(lake, 86.5, 103.5, 87, 104, 'Plaited Block (mooring line)', '#867561', 0.5, 0.5)
for (x, y) in ((85, 104), (92.5, 104)):                          # (none on the 1 m strip down its east side)
    bollard(x, y)

# ================================================================= the trading pier, the crane, the mole and the light
# The trading pier: 4 m wide, 14 m into the harbour, boats along both sides; a jib crane at its head swinging
# out over the trading boat's berth on its east side
R(dock, 96, 100, 100, 114, 't')
zone('dock', 'Trading pier', 96, 102, 100, 114, '#2f7fb3')
A.overlay(dock, 99, 100, 100, 101, 'Refined Wood Block (crane mast)', WOOD, 5.5, 0)
R(jib, 99, 100, 103, 101, P._alloc({'name': 'Refined Wood Block (crane jib)', 'kind': 'block', 'color': WOOD, 'height': 0.5}))
A.overlay(dock, 102.5, 100, 103, 100.5, 'Plaited Block (crane rope)', '#867561', 2.5, 3)
R(hook, 102.5, 100, 103, 100.5, P._alloc({'name': 'Iron Block (crane hook)', 'kind': 'block', 'color': '#848483', 'height': 0.5}))
for i, x in enumerate((100, 100.5, 101, 101.5)):                  # a brace stepping up from the mast under the jib
    R(brace, x, 100, x + 0.5, 101, P._alloc({'name': 'Refined Wood Block (crane brace)', 'kind': 'block', 'color': WOOD, 'height': 0.5, 'base': 4.5 + i * 0.5}))
A.overlay(dock, 98, 100, 99, 101, 'Refined Wood Block (crane winch)', WOOD, 1, 0.5)
zone('dock', 'Jib crane', 99, 100, 103, 101, '#7a6653')
for y in (103, 107, 111):
    bollard(96, y); bollard(99.5, y + 0.5)
lamp(96, 100)
put('dock', 'Resource Bundle II', 96.5, 101); put('dock', 'Scrappy Crate', 97.5, 102)
# the trading boat in its berth between the pier and the mole, a cog: a tarred hull 3 x 10 m, bow north under
# the crane's hook, a raised deck aft, its rudder; one mast, the yard across it with the red sail furled;
# crates and sacks on deck; lines to the pier
HX0, HX1, HY0, HY1 = 100.5, 103.5, 100.5, 110.5
cells = [(101.5, HY0, 102.5, HY0 + 0.5, 2, 0), (101, HY0 + 0.5, 103, HY0 + 1, 2, 0),         # the bow, rising to the stem
         (HX0, HY0 + 1, HX0 + 0.5, HY0 + 1.5, 2, 0), (HX1 - 0.5, HY0 + 1, HX1, HY0 + 1.5, 2, 0),
         (HX0, HY0 + 1.5, HX0 + 0.5, HY1 - 2.5, 1.5, 0), (HX1 - 0.5, HY0 + 1.5, HX1, HY1 - 2.5, 1.5, 0),   # waist
         (HX0 + 0.5, HY0 + 1, HX1 - 0.5, HY1 - 2.5, 1, 0),                                         # the main deck
         (HX0, HY1 - 2.5, HX0 + 0.5, HY1 - 0.5, 2, 0), (HX1 - 0.5, HY1 - 2.5, HX1, HY1 - 0.5, 2, 0),   # the aftcastle,
         (HX0 + 0.5, HY1 - 2.5, HX1 - 0.5, HY1 - 0.5, 1.5, 0),                                     # its deck raised
         (101, HY1 - 0.5, 103, HY1, 2, 0)]                                                        # a rounded stern
boat(cells, 'Tarred Wood Block (trading boat)', TAR)
A.overlay(lake, 101.5, 104.5, 102, 105, 'Refined Wood Block (mast)', WOOD, 8, 0)
A.overlay(lake, 101.5, 99.5, 102, 100.5, 'Refined Wood Block (bowsprit)', WOOD, 0.5, 1.5)
A.overlay(lake, 102, HY1, 102.5, HY1 + 0.5, 'Tarred Wood Block (rudder)', TAR, 1.5, 0)
# the yard across the mast with the red sail furled along it (its wooden ends showing)
spar = P._alloc({'name': 'Refined Wood Block (yard)', 'kind': 'block', 'color': WOOD, 'height': 0.5, 'base': 0.5})
R(yard, 100, 104, 100.5, 104.5, spar); R(yard, 103.5, 104, 104, 104.5, spar)
R(yard, 100.5, 104, 103.5, 104.5, P._alloc({'name': 'Red Carpet Block (the sail, furled on the yard)', 'kind': 'block', 'color': '#9e3742', 'height': 1}))
R(cargo1, 101, 106, 102, 107.5, P._alloc({'name': 'Refined Wood Block (crates on deck)', 'kind': 'block', 'color': '#8c6b4f', 'height': 1}))
R(cargo1, 102, 106.5, 103, 107.5, P._alloc({'name': 'Straw Roof Block (sacks on deck)', 'kind': 'block', 'color': '#a7753d', 'height': 0.5}))
for y in (102, 109):
    A.overlay(lake, 100, y, 100.5, y + 0.5, 'Plaited Block (mooring line)', '#867561', 0.5, 1)
zone('lake', 'Trading boat (moored)', HX0, HY0, HX1, HY1 + 0.5, '#2f7fb3')
# the mole: a stone pier on the harbour's east side, a parapet along its outer edge, sheltering the moorings;
# the harbour light at its end, a little stone tower with a lantern under a slate cap
R(dock, 104, 98, 108, 114, 'k')
A.parapet(dock, 107.5, 102, 108, 114, every=3)
zone('dock', 'Mole', 104, 102, 107.5, 114, '#8a8f96')
A.walls(dock, 104, 98, 108, 102, 'L', 'k')
A.door('dock', 'Wooden Door', 105, 101.5, 107, 102)
R(light7, 104, 98, 108, 102, 'k')
for (x, y) in ((104, 98), (107.5, 98), (104, 101.5), (107.5, 101.5)):
    A.overlay(light7, x, y, x + 0.5, y + 0.5, 'Rough Stone Block (lantern post)', RS, 1.5, 0)
A.overlay(light7, 105.5, 99.5, 106.5, 100.5, 'Yellow Luminescent Block (the harbour light)', '#bd9a5f', 1, 0)
rl = A.roof(lightcap)
rl.hip(104, 98, 108, 102, 'castle', pitch=1.0, overhang=0.5)
rl.paint()
zone('dock', 'Harbour light', 104, 98, 108, 102, '#d4a017')
A.win('dock', 'Wooden Window Frame', 105.5, 98, 106.5, 98.5, 3)                 # a window over the harbour
put('dock', 'ladder', 106.5, 98.5, label='Ladder up to the light'); P.items[-1]['h'] = 6
R(light7, 106.5, 98.5, 107.5, 99.5, ' ')                                        # the hatch
for x, y in P.cells_rect(103.5 - OX, 97.5 - OY, 108.5 - OX, 102.5 - OY):        # a stone string course under the lantern
    mx, my = OX + x / 2, OY + y / 2
    if not (104 <= mx < 108 and 98 <= my < 102):
        lt6[y][x] = P._alloc({'name': 'Roughly Cut Stone Block (string course)', 'kind': 'block', 'color': RCS, 'height': 0.5})
for y in (104, 108, 112):
    bollard(104, y, stone=True)

# ================================================================= the warehouse (+1 m, its loft at +5 m)
# Behind the quay: rough stone, 10 x 10 m, its gable to the quay in tarred timber with the loft's hoist in it
# (pass 2), a double door onto the quay and a side door onto the boardwalk's start; the loft up a stair along
# the south gable. Low enough (ridge +10.5 m) for the watch tower's gallery (+11 m) to see over.
R(dock, 96, 124, 106, 134, 't')
A.walls(dock, 96, 124, 106, 134, 'S', 'w')
A.walls(wh5, 96, 124, 106, 134, 'm', 'w')
A.door('dock', 'Wooden Double Door', 99, 124, 103, 124.5)
A.door('dock', 'Wooden Door', 105.5, 125, 106, 127)
A.stairs('dock', 'Warehouse stair', 98, 131, 102, 133, 4, 'E')        # along the south gable, up towards the ridge
R(wh5, 98, 131, 102, 133, ' ')
A.rail(wh5, 98, 130.5, 102, 131); A.rail(wh5, 97.5, 130.5, 98, 133.5)
rw = A.roof(whroof)
rw.gable(96, 124, 106, 134, 'y', 'lead', pitch=1.0, overhang=0.5)
rw.paint()
# the hoist: a door in the north gable (in a stretch of wall of its own) onto a little railed platform over the
# quay on brackets, a hoist beam above it with its rope
R(wh5, 99.5, 124, 102.5, 124.5, P._alloc({'name': 'Tarred Wood Block (gable, round the hoist door)', 'kind': 'wall', 'color': TAR, 'height': 3}))
A.door('wh5', 'Wooden Door', 100, 124, 102, 124.5)
R(wh5, 100, 122.5, 102, 124, 'r')
A.rail(wh5, 99.5, 122.5, 100, 124); A.rail(wh5, 102, 122.5, 102.5, 124); A.rail(wh5, 100, 122.5, 102, 123)
for x in (100, 101.5):
    A.overlay(dock, x, 122.5, x + 0.5, 123, 'Refined Wood Block (bracket)', WOOD, 0.5, 3)
R(hoist, 100.5, 121.5, 101.5, 124, P._alloc({'name': 'Refined Wood Block (hoist beam)', 'kind': 'block', 'color': WOOD, 'height': 0.5}))
A.overlay(wh5, 100.5, 121.5, 101, 122, 'Plaited Block (hoist rope)', '#867561', 2.5, 1)
zone('wh5', 'Hoist (goods up to the loft)', 99.5, 122.5, 102.5, 124, '#8a5cc2')
# a round window in the south gable, high windows down the sides, lanterns either side of the double door
R(wh5, 100, 133.5, 102, 134, P._alloc({'name': 'Tarred Wood Block (gable, round the window)', 'kind': 'wall', 'color': TAR, 'height': 2.5}))
A.win('wh5', 'Round Wooden Window Frame', 100.5, 133.5, 101.5, 134, 1)
for y0 in (127, 130):
    A.win('dock', 'Wooden Window Frame', 96, y0, 96.5, y0 + 1, 2)
for y0 in (129, 131.5):
    A.win('dock', 'Wooden Window Frame', 105.5, y0, 106, y0 + 1, 2)
for x in (98, 103.5):
    put('dock', 'Wall Lantern', x, 123.5, 180, 2.5)
# the goods: chests down the west wall, sacks, crates, bundles and barrels, a tally table by the side door;
# more in the loft, under the ridge
for y in (125, 127, 129):
    put('dock', 'chest-large', 96.5, y, 90)
put('dock', 'Supply Sacks I', 100, 127); put('dock', 'Supply Sacks II', 101, 127); put('dock', 'Supply Sacks I', 100, 128)
put('dock', 'Scrappy Crate', 103.5, 128.5); put('dock', 'Scrappy Crate', 103.5, 129.5); put('dock', 'Resource Bundle I', 102, 129)
put('dock', 'Scrap Vat I', 104.5, 131.5, label='Scrap Vat I (a barrel)'); put('dock', 'Scrap Vat I', 104.5, 132.5, label='Scrap Vat I (a barrel)')
put('dock', 'table', 102, 125.5, label='Table (the tally)'); put('dock', 'Rustic Chair', 102.5, 126.5, 180)
put('dock', 'Hanging Lantern', 101, 129.5)
put('wh5', 'Supply Sacks II', 99.5, 127); put('wh5', 'Supply Sacks I', 100.5, 127)
put('wh5', 'Scrappy Crate', 101.5, 128); put('wh5', 'Resource Bundle II', 99.5, 128.5)
zone('dock', 'Warehouse (goods)', 96.5, 124.5, 103, 133.5, '#8a5cc2')
zone('wh5', 'Warehouse loft', 96.5, 124.5, 103, 133.5, '#8a5cc2')

# ================================================================= the boardwalk and the boathouse
# 6 m of tarred wood east from the quay's corner to the smokehouse's stair, railings along both sides; the stair
# up 1 m to the smokehouse (its blueprint) between stone cheeks
R(dock, 106, 122, 108, 128, 't')                                    # where the quay meets it
R(dock, 108, 122, 126, 128, 't')
A.rail(dock, 108, 121.5, 126, 122); A.rail(dock, 108, 128, 126, 128.5, [(112, 120)])
A.stairs('dock', 'Stairs up to the smokehouse', 126, 122, 128, 128, 1, 'E')
A.cheeks(dock, 126, 122, 128, 128, 'E')
zone('dock', 'Boardwalk (to the smokehouse)', 108, 122, 126, 128, '#2f8f8a')
lamp(115, 121.5, dock); lamp(122.5, 121.5, dock); lamp(110, 128, dock)
for x in (121, 124.5):                                              # nets drying on a rack by the boathouse
    A.overlay(dock, x, 127.5, x + 0.5, 128, 'Refined Wood Block (net rack post)', WOOD, 2, 0)
A.overlay(dock, 121.5, 127.5, 124.5, 128, 'Plaited Block (fishing net, drying)', '#867561', 1.5, 0.5)
# the boathouse off its south side: an open shed over a wet dock, walkways down both sides, a tarred straw gable
# on posts, open to the water at its south end
R(dock, 112, 128, 120, 136, 't')
R(dock, 114, 130, 118, 136, ' ')
R(dock, 112, 128, 112.5, 136, 'B'); R(dock, 119.5, 128, 120, 136, 'B')    # tarred board walls down its sides
# a fishing boat in the wet dock being refitted: planked forward, its ribs bare aft, a keel showing
boat([(115.5, 130.5, 116.5, 131, 1.5, 0), (114.5, 131, 115, 133, 1.5, 0), (117, 131, 117.5, 133, 1.5, 0),
      (115, 131, 117, 133, 0.5, 0), (115.5, 133, 116.5, 135.5, 0.5, 0)], 'Refined Wood Block (fishing boat)')
for y in (133.5, 134.5, 135):
    boat([(114.5, y, 115, y + 0.5, 1.5, 0), (117, y, 117.5, y + 0.5, 1.5, 0)], 'Refined Wood Block (fishing boat, a rib)')
zone('lake', 'Fishing boat (being refitted)', 114.5, 130.5, 117.5, 135.5, '#2f7fb3')
put('dock', 'Low Crude Wooden Shelf', 112.5, 130.5, 270, label='Low Crude Wooden Shelf (tools)')
put('dock', 'table', 115, 128.5, label='Table (the boatwright\'s bench)'); put('dock', 'Construction Hammer', 115.5, 128.5, z=1)
put('dock', 'Resource Bundle I', 118.5, 129, label='Resource Bundle I (planks)'); put('dock', 'Scrap Bucket', 113, 134, label='Scrap Bucket (pitch)')
put('dock', 'Hanging Lantern', 113, 132, z=3)
rb = A.roof(bhroof)
rb.gable(112, 128, 120, 136, 'y', 'tarstraw', pitch=1.0, overhang=0.5)
rb.paint()
zone('dock', 'Boathouse (a wet dock)', 112, 128, 120, 136, '#7a6653')

# ================================================================= lived in (pass 3)
# unloading: a bale swinging on the crane's hook over the cog's bow, a gangplank from the pier onto its deck,
# its stern lantern lit
R(hang, 102.5, 100, 103, 100.5, P._alloc({'name': 'Straw Roof Block (a bale on the hook)', 'kind': 'block', 'color': '#a7753d', 'height': 1, 'base': 1.5}))
A.overlay(lake, 100, 106, 100.5, 107, 'Refined Wood Block (gangplank)', WOOD, 0.5, 1)
R(cargo1, 102, 110, 102.5, 110.5, P._alloc({'name': 'Yellow Luminescent Block (stern lantern)', 'kind': 'block', 'color': '#bd9a5f', 'height': 0.5, 'base': 1}))
# the harbourmaster's sign hanging by his door; his cup on the counter
A.overlay(dock, 92, 113, 92.5, 114, "Tarred Wood Block (the harbourmaster's sign)", TAR, 1, 2.5)
put('dock', 'Wooden Cup', 90, 110, z=1)
# the warehouse cat (it keeps the mice off the grain), a cup on the tally table
put('dock', 'Cat Pillow', 98.5, 129, label="Cat Pillow (the warehouse cat)"); put('dock', 'Cat Bowl', 99.5, 129.5)
put('dock', 'Wooden Cup', 103, 125.5, z=1)
# on the south quay, a sail spread out for mending, a stool and a basket of thread
A.overlay(dock, 86.5, 128, 90.5, 131, 'Red Carpet Block (a sail, spread for mending)', '#9e3742', 0.5, 0)
put('dock', 'Crude Wooden Stool', 91, 129); put('dock', 'Scrap Bucket', 91, 130, label='Scrap Bucket (thread and needles)')
# someone fishing over the mole's parapet into the open lake, a stool and a bucket for the catch
put('dock', 'Crude Wooden Stool', 106.5, 108.5); put('dock', 'Scrap Bucket', 107, 109, label='Scrap Bucket (the catch)')
A.overlay(lake, 108, 108.5, 109.5, 109, 'Refined Wood Block (a fishing rod)', WOOD, 0.5, 1.5)
# a bench on the boardwalk looking north over the channel to the hunting lodge
put('dock', 'Bench', 117, 122, 180, label='Bench (over the channel)')

# ================================================================= the neighbours' edges (their own blueprints)
R(walk, 80, 96, 83, 131, 'w'); R(walk, 83, 118, 84, 124, 'w')      # the causeway and its strip (gatehouse)
A.rail(walk, 83, 96, 83.5, 131, [(118, 124)])
zone('walk', 'Causeway (gatehouse blueprint)', 80, 98, 83, 131, '#2f8f8a')
zone('walk', 'East gate tower (gatehouse blueprint)', 86.5, 133.5, 93.5, 139.5, '#5f6770')
R(mid, 114, 96, 116, 116, 'c')                                      # the hunting lodge's west edge
zone('mid', 'Hunting lodge (its blueprint)', 114, 96, 116, 116, '#6d7a45')
R(low, 128, 120, 130, 132, 't')                                     # the smokehouse's west edge
zone('low', 'Smokehouse (its blueprint)', 128, 120, 130, 132, '#3f7f9e')

# ================================================================= stilts, foundations, rim beams and checks
print('stilts:', A.stilts(stl, [('dock', 1), ('low', 2), ('walk', 3), ('mid', 4)]))
post_el = {c: float(PALETTE[c]['name'].split('+')[1].split(' ')[0]) for row in stl for c in row if c != ' '}
FOUND = ((96, 124, 106, 134), (104, 98, 108, 114))                  # stone on stone: the warehouse, the mole and light


def in_found(mx, my):
    return any(x0 <= mx < x1 and y0 <= my < y1 for x0, y0, x1, y1 in FOUND)


n_found = 0
for x, y in P.cells_rect(0, 0, 50, 44):
    mx, my = OX + x / 2, OY + y / 2
    if in_found(mx, my):
        near = [in_found(mx + dx, my + dy) for dx in (-0.5, 0, 0.5) for dy in (-0.5, 0, 0.5)]
        stl[y][x] = 'h' if not all(near) else ' '
        n_found += not all(near)
print('foundation squares:', n_found)
buried = 0                                                          # no posts where a deck sits on the ground
for y in range(P.H):
    for x in range(P.W):
        c = stl[y][x]
        if c in post_el and P.ground_at(x, y) >= post_el[c] - 0.5:
            stl[y][x] = ' '; buried += 1
print('posts left out on the ground:', buried)
own = lambda x, y: (84 <= x < 108 and 98 <= y < 135) or (106 <= x < 128 and 121.5 <= y < 137)
print('rim beam squares:', A.rim_beams(stl, [('dock', 1)], lambda x, y: own(x, y) and P.ground_at(*A.sq(x, y)) < 0.5))

# The gatehouse's east tower (its blueprint), copied in as it is so the 3D shows what stands 1 m off the south
# quay: its foundation and battered base, walls, string courses, gallery, roof and lantern, and its windows.
# Its furniture, doors and labels stay in its own blueprint. It isn't this blueprint's: the site plan takes it
# from the gatehouse.
GOX, GOY = 58, 98                                                   # the gatehouse blueprint's corner
gh = doc_to_chars(load_doc(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'laketown_gatehouse.json')))


def tower_keeps(lid, mx, my):
    if not (85.5 <= mx < 96 and 132.5 <= my < 143) or lid == 'lake':
        return False
    if mx < 86:                                                     # its west string courses and roof eave, not the
        return lid in ('g7', 'g11', 'roof15', 'stilts') and not (lid == 'g11' and 135 <= my < 139)   # arch block
    return True


for L in gh['levels']:
    lx, ly = L.get('ox', 0), L.get('oy', 0)
    L['rows'] = [''.join(c if tower_keeps(L['id'], GOX + (lx + i) / 2, GOY + (ly + j) / 2) else ' ' for i, c in enumerate(row))
                 for j, row in enumerate(L['rows'])]
gh['levels'] = [L for L in gh['levels'] if any(c != ' ' for row in L['rows'] for c in row)]


def tower_window(it):
    w, d = (it['d'], it['w']) if it.get('rot') in (90, 270) else (it['w'], it['d'])
    x0, y0 = GOX + it['x'] / 2, GOY + it['y'] / 2
    return it.get('mount') == 'window' and 85.5 <= x0 and x0 + w / 2 <= 96 and 132.5 <= y0 and y0 + d / 2 <= 143


gh['items'] = [it for it in gh['items'] if tower_window(it)]
gh['zones'] = []
gh.pop('terrain', None)
TOWER_LEVELS = {'g7': 'first floor (+7 m)', 'g11': 'second floor (+11 m)', 'roof15': 'roof (+15 m)', 'galb': 'gallery brackets (+10.5 m)',
                'gal14': 'gallery roof (+14 m)', 'lantern': 'watch lantern (+18.5 m)', 'lantcap': 'lantern cap (+20 m)'}
for sid, tid in P.stamp(gh, GOX - OX, GOY - OY, 'gh', 'Gatehouse').items():
    if tid.startswith('gh-') and sid in TOWER_LEVELS:
        next(L for L in P.levels if L['id'] == tid)['name'] = f'Gate tower: {TOWER_LEVELS[sid]}'
A.spawn('dock', 100.5, 119, 180)                                 # walk mode starts here: the quay, facing the trading pier, the crane and the harbour light
A.checks()

NOTES = """Laketown: the main dock, the inner harbour and the boardwalk, as a 0.5 m detail blueprint. Pass 3 of 3 (review and finishing touches): done. Drafted by Claude.
This plan's corner is the layout's (80, 96), so it lines up with the Laketown layout and stamps back into the site plan there.

PASSES
1. Design and bones: the quay and the south quay, the causeway's stair, the trading pier and its crane, the mole and the harbour light, the harbourmaster's office, the warehouse, the boardwalk and the boathouse, with floors, doors, stairs and roof shapes; the neighbours' edges, stilts and foundations, labels.
2. Details: the boats, bollards and cargo, the warehouse's hoist, the office's harbour side, its chimney and signal mast, the crane's brace and winch, the light's details, lamps, the rooms; then a 3D review and a refining round.
3. Review and finishing touches (done): unloading under way (a bale on the crane's hook, a gangplank onto the cog, its stern lantern lit), the harbourmaster's sign and his cup, the warehouse cat, a sail spread for mending on the south quay, someone fishing off the mole, a bench on the boardwalk; the landing stage's east strip kept clear; the layout redrawn as built; the hand-offs for the smokehouse and the hunting lodge.

THE IDEA: the town's harbour, for boats and trade, at +1 m, the lowest deck in town. The square looks down on it from the north, the causeway passes along its west side, and the gatehouse's watch tower looks over it from the south.

THE QUAY (+1 m, tarred wood): along the harbour's south side, from the causeway to the boardwalk, 24 x 10 m, for landing goods. The causeway's stair comes down onto its west end (x 84..88, y 118..124, 2 m) between stone cheeks, a lamp at its foot. Crates, sacks and barrels wait either side of the warehouse door; a handcart stands by the stair; a bench looks over the rowing boats' slot; a lamp where the boardwalk starts. Behind it the open south quay, kept low in front of the gatehouse's watch tower, its edge 1 m short of the tower's prow (y 132) and out of the moat: barrels and bundles, a lamp.

THE HARBOURMASTER'S OFFICE (+1 and +5 m): over the water at the harbour's south-west corner, by the causeway, looking out over the moorings. Two storeys of half-timbering, 8 x 8 m, under a tiled gable roof, its gables to the causeway and the trading pier.
- Below, the office: his counter facing the door, a table of charts under the harbour windows, a shelf of ledgers, the strongbox. The stair runs up the west wall.
- Above, his room: bed, wardrobe, chest, a chair by the fire. A door onto a balcony on brackets over the landing stage, where he watches the moorings.
- A stone chimney corbelled out from the east gable, with a pot; a signal mast on the west gable's apex over the causeway, its red pennant streaming.
- The landing stage round its north and east sides, with bollards; the harbour boat (a rowing boat) moored there.

THE TRADING PIER: 4 m wide, 14 m into the harbour, bollards down both sides, a lamp at its head. A rowing boat lies in the slot by the office. The jib crane at its head (a mast, a brace under the jib, a winch at its foot) swings out over the trading boat's berth, with bundles and a crate waiting by it.

THE TRADING BOAT: a cog in the berth between the pier and the mole, built from blocks. A tarred hull 3 x 10 m, its bow under the crane's hook rising to the stem, a bowsprit, a raised aftcastle, a rounded stern and its rudder; one mast with the yard across it and the red sail furled along it; crates and sacks on deck; lines to the pier.

THE MOLE AND THE HARBOUR LIGHT: a 4 m stone pier along the harbour's east side, a parapet along its outer edge, stone bollards on its inner edge, sheltering the moorings; the way in is between its end and the hunting lodge. At its end the harbour light: a rough stone tower (4 x 4 m) with a window over the harbour, a ladder up inside to a hatch, a string course under the lantern, the lantern on four posts under a slate cap. Stone on stone: they stand on a foundation from the lake bed.

THE WAREHOUSE (+1 m, the loft at +5 m): behind the quay, 10 x 10 m, rough stone below, its gable to the quay in tarred timber, a lead-grey shingle roof, on a stone foundation.
- A double door onto the quay with a lantern either side, a side door onto the boardwalk's start, high windows down the sides, a round window in the south gable.
- The hoist: a door in the north gable onto a little railed platform over the quay, on brackets, a hoist beam above it with its rope.
- Inside: large chests down the west wall, sacks, crates, bundles and barrels, a tally table by the side door; the loft up a stair along the south gable, more goods under the ridge.
- Its ridge (+10.5 m) is low enough for the watch tower's gallery (+11 m) to see over.

THE BOARDWALK AND THE BOATHOUSE: 6 m of tarred wood east from the quay's corner to the smokehouse's stair (up 1 m between stone cheeks), railings along both sides with lamps in them, nets drying on a rack. Off its south side the boathouse: tarred board walls under a tarred straw gable, open to the boardwalk and to the water, over a wet dock with walkways down both sides. In it a fishing boat being refitted, planked forward with its ribs bare aft; the boatwright's bench with a hammer, a tool shelf, planks, a bucket of pitch, a lantern.

HAND-OFF FOR THE SMOKEHOUSE (area 13):
- The boardwalk (+1 m, tarred wood, 6 m wide, railings with lamps in them) ends at the stair up to the smokehouse: x 126..128, y 122..128, rising 1 m east between stone cheeks onto its deck (+2 m) at x 128. Keep 1 m clear at the stair's top (x 128..129).
- Nets drying on a rack at the boardwalk's east end and the boathouse's refit point the fisher's way.

HAND-OFF FOR THE HUNTING LODGE (area 12):
- Its west edge (x 114, +4 m) faces the harbour's mouth, between the mole's end (x 108) and the lodge: keep that water open, and the channel south of the lodge (y 116..122) too, so the boats can come and go.
- From the lodge's west side the harbour light, the cog and the office's signal mast are the view; a bench on the boardwalk looks back at it.

CONNECTIONS
- West: the causeway (+3 m), down its stair from the strip at x 83..84 (the gatehouse blueprint).
- East: the smokehouse (+2 m, its blueprint), up the stair at the boardwalk's end (x 126..128, y 122..128) onto its deck at x 128.
- The hunting lodge (+4 m) stands across the harbour's mouth to the east (x 114); no stair to it here.
- South: the gatehouse's east tower, 1 m off the south quay's edge.

THE GATEHOUSE'S EAST TOWER, south of the quay, is copied in from its own blueprint (the gatehouse) so the 3D shows what stands there: its foundation, walls, string courses, windows, gallery, roof and lantern. It isn't part of this blueprint; the site plan takes it from the gatehouse. Rerun this script after changing the tower.

BOATS are built from blocks (1.0 has none to place), on the water.

SIZES: furniture, light and cargo sizes are estimates until measured. The ladder in the light is 6 m (the library's is 4 m).

STILTS: 1 m posts on the layout's 4 m grid, from the lake bed 4 m down to each deck's underside, left out where a deck sits on the ground; the warehouse and the mole stand on rough stone foundations instead; tarred rim beams under the edges over the water.
"""
A.save('laketown_dock.json', NOTES, 'r-claude-laketown-dock-4')
