"""Laketown: the fisher's smokehouse and the fishing pier. 0.5 m detail plan. Pass 3 of 3: review and finishing touches.

The Fisher's place at the south-east corner of the lake, where the boardwalk from the main dock and the stair
down from the hunting lodge meet. On a deck of sun-bleached planks (+2 m): the Fisher's yard, where the ways
cross, with fish drying on racks; the bunkhouse, low tarred board walls under an old boat's hull turned upside
down for a roof, its bow jutting out over a porch; a drying green behind. Down a stair, the fishing pier (+1 m)
with its finger piers for the boats, and on its head the smokehouse: weathered stone, a steep stone-shingle
roof with a smoke louvre on the ridge, the smoking fire inside.

Coordinates are the layout's (doc `laketown`): this plan's corner is the layout's (124, 108).
Run: python laketown_smokehouse.py  ->  writes laketown_smokehouse.json
"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laketown_common import Area, WOOD, BED
from mage_common import ROOF_MATS

PALM, TAR, WST, RS = '#958580', '#5d5652', '#6a6c67', '#7d776a'
ROOF_MATS.setdefault('palm', ('Palm Wood Block', PALM))            # the hull's gunwale strake
ROOF_MATS.setdefault('net', ('Plaited Block', '#867561'))          # a net thrown over the hull
OX, OY = 124, 108
A = Area('Laketown: the smokehouse and fishing pier (detail)', OX, OY, 36, 34, {
    'd': {'name': 'Palm Wood Block', 'kind': 'floor', 'color': PALM},                   # sun-bleached planks
    'c': {'name': 'Conifer Wood Block', 'kind': 'floor', 'color': '#6e5a51'},           # the hunting lodge (its)
    'k': {'name': 'Roughly Cut Stone Block', 'kind': 'floor', 'color': '#62605d'},      # the smokehouse floor
    'B': {'name': 'Tarred Wood Block (boards)', 'kind': 'wall', 'color': TAR, 'height': 3},          # the bunkhouse
    'S': {'name': 'Weathered Stone Block', 'kind': 'wall', 'color': WST, 'height': 5},              # the smokehouse
    'K': {'name': 'Rough Stone Block (chimney)', 'kind': 'wall', 'color': RS, 'height': 7.5},
    'h': {'name': 'Rough Stone Block (foundation)', 'kind': 'wall', 'color': RS, 'height': 4.5},
    'p': {'name': 'Refined Wood Block (bulkhead)', 'kind': 'wall', 'color': WOOD, 'height': 3},
    'U': {'name': 'Refined Wood Block (lamp post)', 'kind': 'block', 'color': WOOD, 'height': 2},
})
P, R, zone, put = A.P, A.R, A.zone, A.put
stl = A.level('stilts', 'Stilts and foundations, standing on the lake bed (-4 m)', BED, 12)
lake = A.level('lake', 'Lake (water level, 0 m)', 0, 1)
dock = A.level('dock', 'Fishing pier and the smokehouse; the boardwalk, its end (+1 m)', 1, 3)
low = A.level('low', "The Fisher's deck: the yard, the bunkhouse (+2 m)", 2, 4)
mid = A.level('mid', 'Hunting lodge, its edge (+4 m)', 4, 4)
hroof = A.level('hroof', 'Bunkhouse: the upturned hull (+5 m)', 5, 5)
sroof = A.level('sroof', 'Smokehouse: the roof (+6 m)', 6, 6)
fish = A.level('fish', 'Smokehouse: fish hanging in the smoke (+1 m)', 1, 4)
fig = A.level('fig', 'Bunkhouse: the figurehead on the stem post (+2 m)', 2, 4)
chim = A.level('chim', 'Bunkhouse: the chimney cap (+9.5 m)', 9.5, 1)
lamp3 = A.level('lamp3', 'Lamps on the pier (+3 m)', 3, 1)
lamp4 = A.level('lamp4', 'Lamps on the deck (+4 m)', 4, 1)
bellb = A.level('bellb', "The ship's bell (+3.5 m)", 3.5, 1)
bella = A.level('bella', "The ship's bell: its arm (+4.5 m)", 4.5, 1)
mast = A.level('mast', "The Fisher's boat: mast and boom (+0 m)", 0, 8)
cartload = A.level('cartload', 'Yard: the handcart, its load (+2 m)', 2, 2)
oars = A.level('oars', 'Rowing boat: its oars (+0 m)', 0, 2)


def block(name, color, h, base=0):
    e = {'name': name, 'kind': 'block', 'color': color, 'height': h}
    if base:
        e['base'] = base
    return P._alloc(e)


LAMP = block('Yellow Luminescent Block (lamp)', '#bd9a5f', 0.5)


def lamp(x, y, g):
    """A lamp on a 2 m post (the walkways' style): in the deck's railing (g = low), or over the pier (g = dock)."""
    if g is low:
        R(low, x, y, x + 0.5, y + 0.5, 'U'); R(lamp4, x, y, x + 0.5, y + 0.5, LAMP)
    else:
        A.overlay(dock, x, y, x + 0.5, y + 0.5, 'Refined Wood Block (lamp post)', WOOD, 2, 0); R(lamp3, x, y, x + 0.5, y + 0.5, LAMP)


def bollard(x, y):
    A.overlay(dock, x, y, x + 0.5, y + 0.5, 'Tarred Wood Block (bollard)', '#4e4844', 1, 0)


def boat(cells, name, color=WOOD):
    """A boat built from blocks on the water: cells are (x0, y0, x1, y1, height, base) in layout metres."""
    for x0, y0, x1, y1, h, b in cells:
        A.overlay(lake, x0, y0, x1, y1, name, color, h, b)


def rowing_boat(x0, y0, label):
    """A rowing boat 1.5 m wide and 4 m long from (x0, y0), its bow north: a 1 m gunwale round a 0.5 m floor."""
    boat([(x0 + 0.5, y0, x0 + 1, y0 + 0.5, 1, 0), (x0, y0 + 3.5, x0 + 1.5, y0 + 4, 1, 0),
          (x0, y0 + 0.5, x0 + 0.5, y0 + 3.5, 1, 0), (x0 + 1, y0 + 0.5, x0 + 1.5, y0 + 3.5, 1, 0),
          (x0 + 0.5, y0 + 0.5, x0 + 1, y0 + 3.5, 0.5, 0)], 'Refined Wood Block (rowing boat)')
    zone('lake', label, x0, y0, x0 + 1.5, y0 + 4, '#2f7fb3')


# ================================================================= the lake
def shoreline(x):
    return 140 + 2 * math.sin(x / 21) + 1.2 * math.sin(x / 8.3 + 1.3)


def ground(x, y):
    s = shoreline(x)
    if y < s:
        return -min(4, max(1, round((s - y) / 1.5)))
    return min(3, 1 + math.floor((y - s) / 3))


P.ground_fn(lambda mx, my: ground(mx + OX, my + OY))
for x, y in P.cells_rect(0, 0, 36, 34):
    if P.ground_at(x, y) < 0:
        lake[y][x] = '~'

# ================================================================= the Fisher's deck (+2 m)
# The layout's deck, grown 4 m south (to 22 x 16 m) so the bunkhouse has room: sun-bleached palm planks on a
# tarred edge, a railing round it, open where the boardwalk's stair arrives (west), the lodge's stair comes down
# (north) and the stair down to the pier leaves (east)
A.deck(low, 128, 120, 150, 136, 'd', 't')
A.rail(low, 128, 120, 150, 120.5, [(134, 140)])                     # north (the lodge's stair)
A.rail(low, 128, 120.5, 128.5, 136, [(122, 128)])                   # west (the boardwalk's stair)
A.rail(low, 149.5, 120.5, 150, 128, [(122, 128)])                   # east, over the pier (the stair down)
A.rail(low, 128.5, 135.5, 133, 136); A.rail(low, 145, 135.5, 149.5, 136)   # south, either side of the bunkhouse
zone('low', "The Fisher's deck", 128, 120, 150, 136, '#3f7f9e')
lamp(128, 121.5, low); lamp(128, 128, low); lamp(133.5, 120, low); lamp(140, 120, low); lamp(149.5, 121.5, low)
# the ship's bell, salvaged with the hull, on a post in the railing over the pier: rung when the boats come in
R(low, 149.5, 120.5, 150, 121, block('Refined Wood Block (bell post)', WOOD, 2.5))
R(bella, 149, 120.5, 150, 121, block('Refined Wood Block (bell arm)', WOOD, 0.5))
R(bellb, 149, 120.5, 149.5, 121, block("Bronze Block (the ship's bell)", '#8b7852', 1))

# ---- the yard, where the three ways meet: fish drying on racks along its north side, clear of the ways
zone('low', "Fisher's yard", 128.5, 120.5, 149.5, 128.5, '#3f7f9e')
for x in (129, 131.5, 141, 143.5, 146):
    put('low', 'Fish Drying Rack', x, 120.5)
put('low', 'Lying Wooden Barrel', 133.5, 127.5, label='Lying Wooden Barrel (pickled herring)')
put('low', 'Standing Wooden Barrel', 135, 127.5, label='Standing Wooden Barrel (a water butt)')
put('low', 'Standing Wooden Barrel', 139, 127.5, label='Standing Wooden Barrel (salt)')
put('low', 'table', 140.5, 127.5, label='Table (the gutting table)')
put('low', 'Wooden Bucket', 143, 128, label='Wooden Bucket (for the guts)')
put('low', 'Wooden Crate', 143.5, 127.5, label='Wooden Crate (the catch)')

# ================================================================= the bunkhouse: an upturned hull
# Low tarred board walls (3 m), 12 x 7 m, under an old boat's hull turned keel-up: tarred planking at 45
# degrees from a pale gunwale strake, a flat shoulder and the keel along the top; its bow curving to a point
# 4.5 m west over a porch (the front door), the keel dipping down the stem; its transom over the east wall. A
# door north onto the yard; the hearth on the south wall, its stone chimney up through the hull. Portholes (round
# windows) along the sides; a net thrown over the hull to dry; the boat's stem post, a figurehead salvaged
# from a wreck carved at its top, holding up the bow; the boat's name board on the transom. Inside: the common
# room (the Fisher, the hearth, a table, his rods and a chest of tackle, the Fish Trophy Board) and, through a
# bulkhead, the cabin: his bed and two bunks for the crew, side by side.
A.walls(low, 133, 128.5, 145, 135.5, 'B', 'r')
A.door('low', 'Wooden Door', 133, 131, 133.5, 133)                 # under the bow
A.door('low', 'Wooden Door', 136.5, 128.5, 138.5, 129)             # onto the yard
R(low, 137, 135, 138, 136, 'K')                                     # the chimney, in the south wall
rh = A.roof(hroof)
rh.gable(133, 128.5, 145, 135.5, 'x', 'tarwood', pitch=1.0, overhang=0.5, end_overhang=4.5)
BOW, BEAM = 128.5, 4                                                # the bow's tip; the half-beam over the eaves


def hull(mx, my, h, mat):
    """The hull as a heightfield: 45 degree sides up from the gunwale (0.5 m over the walls' tops) to a flat
    shoulder at 3 m, the keel a course proud along the middle. Its half-width narrows towards the bow on a
    curve (full beam at the west wall), so the sides draw in and the keel comes down the stem to the tip."""
    if mx > 145.5 or (137 <= mx < 138 and my > 134.5):              # past the transom; the chimney
        return None
    hw = BEAM * min(1, math.sqrt(max(0, mx - BOW) / (133 - BOW)))
    e = hw - abs(my - 132)                                          # how far in from the gunwale
    if e <= 0:
        return None
    h = min(3, 0.5 + 0.5 * math.floor(e / 0.5))
    if abs(my - 132) < 0.5:                                         # the keel, and the stem at the bow
        return h + 0.5, 'wood'
    if h == 0.5:
        return h, 'palm'
    if 141 <= mx < 144.5 and my < 130.5:                            # a net thrown over the north side to dry
        return h, 'net'
    return h, mat


rh.shape(hull)
rh.paint()
A.ring(chim, 137, 135, 138, 136, block('Rough Stone Block (chimney cap)', RS, 0.5))
R(low, 139.5, 130.5, 140, 135, 'p')                                 # the bulkhead, open by the north wall
for x0 in (135, 140.5):                                             # portholes: north, south
    A.win('low', 'Round Wooden Window Frame', x0, 128.5, x0 + 1, 129, 1.5)
for x0 in (135, 140):
    A.win('low', 'Round Wooden Window Frame', x0, 135, x0 + 1, 135.5, 1.5)
# the common room: the Fisher by the hearth, his trophy over it, a table, his rods on the wall, a chest of tackle
put('low', 'Stone Fireplace', 136.5, 134, 180, label='Stone Fireplace (the hearth)')
put('low', 'npc-fisher', 134.5, 130.5)
put('low', 'table', 138, 130.5, 90); put('low', 'Crude Wooden Stool', 137.5, 132.5); put('low', 'Crude Wooden Stool', 138.5, 133)
put('low', 'Staff Weapon Rack', 133.5, 129, 270, label='Staff Weapon Rack (fishing rods)')
put('low', 'chest-medium', 133.5, 133.5, label='Medium Chest (tackle)')
put('low', 'Fish Trophy Board', 137, 134.5, 180, z=2, label='Fish Trophy Board (over the hearth)')
put('low', 'Hanging Lantern', 138.5, 133.5, z=2.5)
# the cabin: the Fisher's bed and two bunks for his crew side by side against the transom, an aisle along the
# bulkhead
put('low', 'bed', 141.5, 129, 90, label='Bed (the Fisher)')
put('low', 'bed', 141.5, 131, 90, label='Bed (a bunk for the crew)'); put('low', 'bed', 141.5, 133, 90, label='Bed (a bunk for the crew)')
put('low', 'Hanging Lantern', 140.5, 131.5, z=2.5)
zone('low', 'Common room', 133.5, 129, 139.5, 135, '#9c6b8e')
zone('low', 'Cabin (the Fisher and his crew)', 140, 129, 144.5, 135, '#9c6b8e')
# the porch under the bow: the stem post holding it up (a figurehead from a wreck at its top), a bench against
# the wall, oars stood by the door, a lantern
A.overlay(low, 128.5, 131.5, 129, 132.5, 'Refined Wood Block (the stem post)', WOOD, 2, 0)
R(fig, 128.5, 131.5, 129, 132.5, block('Palm Wood Block (a figurehead from a wreck)', PALM, 1.5, 2))
put('low', 'Rustic Bench', 132.5, 133.5, 90, label='Rustic Bench (on the porch)')
A.overlay(low, 132.5, 130, 133, 130.5, 'Refined Wood Block (oars, stood against the wall)', WOOD, 2.5, 0)
put('low', 'Wall Lantern', 132.5, 130.5, 90, 2.5)
# the boat's name board on the transom
A.overlay(low, 145, 130.5, 145.5, 133.5, "Palm Wood Block (the boat's name board)", PALM, 0.5, 2)
zone('low', 'Porch, under the bow', 129.5, 129.5, 133, 134.5, '#3f7f9e')

# ---- the drying green behind, between the bunkhouse and the smokehouse: more racks, out of the wind
for y in (129.5, 131.5, 133.5):
    put('low', 'Fish Drying Rack', 147.5, y, 90)
zone('low', 'Drying green', 145, 128.5, 150, 136, '#3f8a4f')
A.overlay(low, 145.5, 129, 147, 132, 'Plaited Block (a net, laid out for mending)', '#867561', 0.5, 0)
put('low', 'Crude Wooden Stool', 146, 132.5)
put('low', 'Half Wooden Barrel', 145.5, 134, label='Half Wooden Barrel (brine)')

# ================================================================= the fishing pier (+1 m)
# 6 m of sun-bleached planks on a tarred edge running north from the deck's east side, two finger piers east
# for the boats; on its head the smokehouse. Down to it from the deck between stone cheeks.
A.deck(dock, 150, 112, 156, 128.5, 'd', 't')
R(dock, 156, 114, 158, 116, 't'); R(dock, 156, 120, 158, 122, 't')        # the finger piers
R(dock, 156, 126, 158, 128.5, 't')                                  # the pier head, before the smokehouse door
A.stairs('dock', 'Stairs down to the fishing pier', 150, 122, 152, 128, 1, 'W')
A.cheeks(dock, 150, 122, 152, 128, 'W')
zone('dock', 'Fishing pier', 150, 112, 156, 126, '#2f7fb3')
for y in (113, 117, 119):                                           # along the west edge, for the Fisher's boat
    bollard(150, y)
for (x, y) in ((157.5, 114.5), (157.5, 121), (155.5, 124.5), (157.5, 126.5)):    # the fingers' ends, the head
    bollard(x, y)
lamp(150, 112, dock); lamp(155.5, 112, dock); lamp(152.5, 121.5, dock)
for y in (116.5, 119):                                              # a net rack along the east edge
    A.overlay(dock, 155.5, y, 156, y + 0.5, 'Refined Wood Block (net rack post)', WOOD, 2, 0)
A.overlay(dock, 155.5, 117, 156, 119, 'Plaited Block (fishing net, drying)', '#867561', 1.5, 0.5)
# the Fisher's boat moored along the west side: a 7 m fishing boat, bow north, a mast and its boom with the sail
# furled along it
boat([(148, 112.5, 149, 113, 1.5, 0), (147.5, 113, 148, 119, 1.5, 0), (149, 113, 149.5, 119, 1.5, 0),
      (147.5, 119, 149.5, 119.5, 1.5, 0), (148, 113, 149, 119, 0.5, 0)], "Refined Wood Block (the Fisher's boat)")
R(mast, 148.5, 115, 149, 115.5, block("Refined Wood Block (the Fisher's boat: mast)", WOOD, 6, 0.5))
R(mast, 148.5, 115.5, 149, 118.5, block("Plaited Block (the boom, the sail furled on it)", '#867561', 0.5, 2.5))
zone('lake', "The Fisher's boat", 147.5, 112.5, 149.5, 119.5, '#2f7fb3')
rowing_boat(156, 116, 'Rowing boat'); rowing_boat(156, 122, 'Rowing boat')

# ---- the smokehouse on the pier head: weathered stone (5 m) on a stone footing from the lake bed, a steep
# stone-shingle roof (45 degrees, ridge north-south) with a smoke louvre on the ridge; a door north onto the
# pier; the smoking fire in the middle
A.walls(dock, 150, 128.5, 157.5, 136, 'S', 'k')
A.door('dock', 'Wooden Door', 153, 128.5, 155, 129)
rs = A.roof(sroof)
rs.gable(150, 128.5, 157.5, 136, 'y', 'shingle', pitch=1.0, overhang=0.5)
rs.cut(153, 131, 154.5, 133.5)                                      # the smoke vent, under the louvre
rs.caps('lead')                                                     # a dark ridge
rs.paint()
ridge = 6 + rs.top(153.5, 130.5)
vent = A.level('vent', f'Smokehouse: the louvre posts (+{ridge:g} m)', ridge, 1)
vcap = A.level('vcap', f'Smokehouse: the louvre cap (+{ridge + 0.5:g} m)', ridge + 0.5, 2)
for y in (130.5, 133.5):                                            # posts on the ridge either end of the vent
    R(vent, 153.5, y, 154, y + 0.5, block('Weathered Stone Block (louvre post)', WST, 1))
rv = A.roof(vcap)
rv.gable(153, 131, 154.5, 133.5, 'y', 'shingle', pitch=1.0, overhang=0.5)
rv.caps('lead')
rv.paint()
put('dock', 'campfire', 153, 131.5, label='Campfire (the smoking fire)')
zone('dock', 'Smokehouse', 150.5, 129, 157, 135.5, '#7a6653')
# rafters across the room 3 m up, fish hung from them in the smoke (every other square), clear of the door
for y in (130, 132, 134):
    A.overlay(dock, 150.5, y, 157, y + 0.5, 'Refined Wood Block (rafter)', WOOD, 0.5, 3)
    for x in (151, 152, 153, 154, 155, 156):
        R(fish, x, y, x + 0.5, y + 0.5, block('Rough Sandstone Block (fish, hung in the smoke)', '#8b6954', 0.5, 2.5))
# smoking wood stacked by the door, a lantern
A.overlay(dock, 156, 127.5, 157.5, 128.5, 'Rough Wood Block (smoking wood, stacked)', '#7a6653', 1.5, 0)
put('dock', 'Wall Lantern', 155.5, 128, 180, 2.0)

# ================================================================= the neighbours' edges (their own blueprints)
R(mid, 124, 112, 146, 116, 't'); R(mid, 124, 112, 145, 115, 'c')   # the hunting lodge's south edge
A.rail(mid, 124, 116, 146, 116.5, [(134, 140)]); A.rail(mid, 146, 112, 146.5, 116.5)
zone('mid', 'Hunting lodge (its blueprint)', 124, 112, 146, 116, '#6d7a45')
R(low, 134, 116, 140, 120, 't')                                     # its stair down onto the deck
A.stairs('low', 'Stairs down to the smokehouse (hunting lodge blueprint)', 134, 116, 140, 120, 2, 'N')
A.cheeks(low, 134, 116, 140, 120, 'N')
R(dock, 124, 122, 128, 128, 't')                                    # the boardwalk's end and its stair up here
A.rail(dock, 124, 121.5, 126, 122); A.rail(dock, 124, 128, 126, 128.5)
A.stairs('dock', 'Stairs up to the smokehouse (main dock blueprint)', 126, 122, 128, 128, 1, 'E')
A.cheeks(dock, 126, 122, 128, 128, 'E')
zone('dock', 'Boardwalk (main dock blueprint)', 124, 122, 126, 128, '#2f8f8a')

# ================================================================= lived in (pass 3)
# the yard: the morning's catch on a handcart by the pier stair; the pier: someone fishing off its north end,
# crab pots on a finger, oars left in a rowing boat; the bunkhouse: supper on the table (a jug, cups, fish stew),
# the kettle on the hearth, a mat in the cabin's aisle; the porch: the Captain's chair facing the harbour, his
# cup on a side table by the bench; the smokehouse: a crate of fresh fish waiting to be hung, a stool by the
# fire, a bucket of wood chips
for y in (123.5, 125.5):                                            # the handcart, its shafts towards the pier
    A.overlay(low, 145.5, y, 146.5, y + 0.5, 'Tarred Wood Block (cart wheel)', TAR, 1, 0)
A.overlay(low, 145, 124, 147.5, 125.5, 'Refined Wood Block (cart bed)', WOOD, 0.5, 0.5)
for y in (124, 125):
    A.overlay(low, 147.5, y, 149, y + 0.5, 'Refined Wood Block (cart shafts)', WOOD, 0.5, 0.5)
R(cartload, 145, 124, 146.5, 125.5, block("Refined Wood Block (crates of the morning's catch)", '#8c6b4f', 1, 1))
zone('low', 'Handcart (the catch)', 145, 123.5, 149, 126, '#7a6653')
put('dock', 'Crude Wooden Stool', 152.5, 112.5); put('dock', 'Wooden Bucket', 153.5, 112.5, label='Wooden Bucket (the catch)')
A.overlay(lake, 152.5, 111.5, 153, 112, 'Refined Wood Block (a fishing rod)', WOOD, 0.5, 1.5)
put('dock', 'Scrap Pot I', 156, 120.5, label='Scrap Pot I (a crab pot)'); put('dock', 'Scrap Pot I', 156.5, 121, label='Scrap Pot I (a crab pot)')
R(oars, 156, 118, 157.5, 118.5, block('Refined Wood Block (oars, shipped across the thwart)', WOOD, 0.5, 1))
put('low', 'Crude Wooden Jug', 138, 130.5, z=1); put('low', 'Wooden Cup', 138.5, 131.5, z=1)
put('low', 'Wooden Bowl', 138.5, 132, z=1, label='Wooden Bowl (fish stew)')
put('low', 'Kettle', 136.5, 134, z=1.5, label='Kettle (on the hearth)')
put('low', 'Straw Mat', 140, 131)
put('low', 'Rustic Chair', 129.5, 133.5, 90, label="Rustic Chair (the Captain's, facing the harbour)")
put('low', 'Crude Wooden Side Table', 131.5, 134); put('low', 'Wooden Cup', 131.5, 134, z=1, label="Wooden Cup (the Captain's)")
put('dock', 'Wooden Crate', 151, 129, label='Wooden Crate (fresh fish, to be hung)')
put('dock', 'Crude Wooden Stool', 155.5, 132); put('dock', 'Wooden Bucket', 155.5, 133.5, label='Wooden Bucket (wood chips)')

# ================================================================= stilts, foundations, rim beams and checks
print('stilts:', A.stilts(stl, [('dock', 1), ('low', 2), ('mid', 4)]))
FOUND = ((150, 128.5, 157.5, 136),)                                 # stone on stone: the smokehouse


def in_found(mx, my):
    return any(x0 <= mx < x1 and y0 <= my < y1 for x0, y0, x1, y1 in FOUND)


n_found = 0
for x, y in P.cells_rect(0, 0, 36, 34):
    mx, my = OX + x / 2, OY + y / 2
    if in_found(mx, my):
        near = [in_found(mx + dx, my + dy) for dx in (-0.5, 0, 0.5) for dy in (-0.5, 0, 0.5)]
        stl[y][x] = 'h' if not all(near) else ' '
        n_found += not all(near)
print('foundation squares:', n_found)
own = lambda x, y: (128 <= x < 150 and 120 <= y < 136) or (150 <= x < 158 and 112 <= y < 136)
print('rim beam squares:', A.rim_beams(stl, [('dock', 1), ('low', 2)], own))
A.spawn('low', 130, 124.5, 270)                                 # walk mode starts here: the yard by the boardwalk, facing past the hull's bow to the smokehouse
A.checks()

NOTES = """Laketown: the fisher's smokehouse and the fishing pier, as a 0.5 m detail blueprint. Pass 3 of 3 (review and finishing touches): done. Drafted by Claude.
This plan's corner is the layout's (124, 108), so it lines up with the Laketown layout and stamps back into the site plan there.

PASSES
1. Design and bones: the Fisher's deck and its railing, the yard, the bunkhouse under its upturned hull (walls, doors, hearth, chimney, the hull), the drying green, the fishing pier, its finger piers and stair, the smokehouse (walls, door, roof, louvre, the smoking fire); the Fisher, the beds, the drying racks; the neighbours' edges, stilts, foundations, labels.
2. Details: the bunkhouse's portholes, bulkhead and rooms, the net over the hull, the stem post and its figurehead, the name board, the chimney cap; the yard's gutting station and stores; the drying green's net; the smokehouse's rafters hung with fish, ridge caps, woodpile; the pier's bollards, lamps and net rack, the Fisher's boat and two rowing boats; the ship's bell; then a 3D review and a refining round.
3. Review and finishing touches (done): the morning's catch on a handcart, someone fishing off the pier's end, crab pots, oars left in a rowing boat, supper on the bunkhouse table and the kettle on the hearth, a mat in the cabin, the Captain's chair and cup on the porch, fresh fish waiting in the smokehouse, a stool by the fire; the layout redrawn as built; the hand-offs checked (this is the last area).

THE IDEA: the Fisher's place at the lake's south-east corner, where the boardwalk from the main dock (west) and the stair down from the hunting lodge (north) meet. The Fisher, Captain Melville Fontane, lives aboard what's left of an old boat: its hull, turned keel-up, roofs his bunkhouse. His catch comes in at the pier, hangs on racks in the yard and the drying green, and goes into the smokehouse on the pier head.

THE FISHER'S DECK (+2 m): the layout's 22 x 12 m grown 4 m south to 22 x 16 m (x 128..150, y 120..136), so the bunkhouse has room. Sun-bleached palm planks on a tarred edge, a wooden railing round it, open where the three ways arrive.
- The yard (north): where the ways cross, west to east from the boardwalk's stair to the pier's, with the lodge's stair coming down in the middle. Fish drying racks along its north side, clear of all three. Along the bunkhouse's front: the gutting table with a bucket and a crate for the catch, barrels of salt and pickled herring, a water butt. Lamps in the railing either side of each way in, and at the top of the pier stair the ship's bell, salvaged with the hull, on a post over the water.
- The bunkhouse (south): low tarred board walls (3 m), 12 x 7 m, under an old boat's hull turned upside down: tarred planking at 45 degrees up from a pale gunwale strake, a flat shoulder and a keel along the top (+8.5 m), the transom over the east wall; the bow curves to a point 4.5 m west over a porch, the keel dipping down its stem. A net is thrown over its north side to dry. The boat's stem post comes down to the deck under the bow, a figurehead from a wreck carved at its top; the boat's name board is on the transom. Round portholes along the sides.
  - The porch, under the bow: the front door, a bench, oars stood against the wall, a lantern.
  - The common room (the door from the yard): the Fisher by the hearth (its stone chimney up through the hull, a cap on top) with the Fish Trophy Board over it, a table and stools, his fishing rods on the wall, a chest of tackle, a lantern.
  - The cabin, through a bulkhead: the Fisher's bed and two bunks for his crew side by side against the transom, an aisle along the bulkhead, a lantern.
- The drying green (south-east): between the bunkhouse and the smokehouse, more racks out of the wind, a net laid out for mending with a stool by it, a tub of brine.

THE FISHING PIER (+1 m): 6 m of the same planks on a tarred edge, from the lodge's corner (y 112) south to the smokehouse; two finger piers east (y 114 and 120) for the boats; the stair down from the deck (x 150..152, y 122..128, stone cheeks) lands on it. Bollards along its west side and at the fingers' ends, lamps at its north end and the stair's foot, a net rack along its east side.
- The boats: the Fisher's boat (7 m, a mast and a boom with the sail furled on it) moored along the west side; a rowing boat in each slip between the fingers.
- The smokehouse, on the pier head: weathered stone walls (5 m), 7.5 x 7.5 m, on a stone footing from the lake bed; a steep stone-shingle roof (45 degrees, ridge north-south) with a dark ridge and a smoke louvre on it (a vent under a small cap on posts); a door north onto the pier, a lantern and the smoking wood stacked by it; the smoking fire (a Campfire) in the middle, under rafters 3 m up hung with fish.

HAND-OFFS: none left. This is the last of the thirteen areas, and both its neighbours' hand-offs are kept: 1 m clear at the top of the boardwalk's stair (x 128..129) and at the foot of the lodge's stair (y 120..121).

CONNECTIONS
- West: the boardwalk's stair (the main dock blueprint's, x 126..128, y 122..128) rises 1 m east onto the deck at x 128; 1 m clear at its top.
- North: the hunting lodge's stair (its blueprint's, x 134..140, y 116..120) comes down 2 m onto the deck at y 120; 1 m clear at its foot.
- East: the stair down 1 m to the fishing pier (x 150..152, y 122..128).

SIZES: the Fisher is the planner's 3 x 3 m placeholder; the Campfire is the library's 2 x 2 m; the Fish Drying Racks (1.0 decorations, from the Decoration Workbench) and the furniture are estimates until measured.

STILTS: 1 m posts on the layout's 4 m grid, from the lake bed 4 m down to each deck's underside; tarred rim beams under the edges; a stone footing under the smokehouse.
"""
A.save('laketown_smokehouse.json', NOTES, 'r-claude-laketown-smokehouse-3')
