"""Laketown: a village on stilts in a lake, 1 m layout plan (foundations and labels only).

The main square sits in the middle with the Flame Altar (level 4, a 160 m build area that covers the whole
canvas). Platforms ring it at different heights, every one joined by stairs: docks at +1 m, low decks at
+2 m, walkways at +3 m, the square and its neighbours at +4 m, upper decks at +5 m, the alchemist at +6 m
and the manor at +8 m. The shore runs along the south, where the gatehouse straddles the waterline.
Round the square: a tavern, a lodging house for survivors, a barber and bathhouse, and the storage halls.
A villagers' quarter (NW) and a research hall for the Ancient Researcher (NE) fill the far corners.
Loops join the outer platforms (west: smithy to manor; east: farm to manor and farm to alchemist; south:
main dock to the smokehouse), so nowhere is a dead end. Everything stays 2 m inside the build area's edge.
Decks and stilts (down to a lake bed 4 m below the surface) for now; railings and buildings come later.
Areas are labelled with zones.
Run: python laketown.py  ->  writes laketown.json
"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mage_common import Plan, PALETTE, ALTAR_W, ALTAR_D, ALTAR_H

PALETTE.clear()
PALETTE.update({                                       # catalogue names and colours (blocks.js), all as floors
    '~': {'name': 'Water', 'kind': 'water', 'color': '#3f6f8f'},
    'w': {'name': 'Rough Wood Block', 'kind': 'floor', 'color': '#7a6653'},          # walkways and the causeway
    'r': {'name': 'Refined Wood Block', 'kind': 'floor', 'color': '#75675f'},        # workshop, farm and town decks
    't': {'name': 'Tarred Wood Block', 'kind': 'floor', 'color': '#5d5652'},         # docks, piers, deck edges
    'c': {'name': 'Conifer Wood Block', 'kind': 'floor', 'color': '#6e5a51'},        # the hunting lodge
    'L': {'name': 'Limestone Road Block', 'kind': 'floor', 'color': '#a38b79'},      # the main square's paving
    'f': {'name': 'Fancy Stone Block', 'kind': 'floor', 'color': '#92908c'},         # stone edges
    'P': {'name': 'Highly Polished Stone Block', 'kind': 'floor', 'color': '#b3b0a9'},  # the manor terrace
    'B': {'name': 'Fired Bricks Block', 'kind': 'floor', 'color': '#aa7657'},        # the smithy
    'k': {'name': 'Roughly Cut Stone Block', 'kind': 'floor', 'color': '#62605d'},   # smithy edge, arena stands
    'g': {'name': 'Polished Granite Block', 'kind': 'floor', 'color': '#626c7a'},    # the alchemist's platform
    'C': {'name': 'Castle Block', 'kind': 'floor', 'color': '#7c8084'},              # the gatehouse
    'd': {'name': 'Dirt Road Block', 'kind': 'floor', 'color': '#8c7455'},           # the shore road
    'q': {'name': 'Rocky Stone Road Block', 'kind': 'floor', 'color': '#84715f'},    # the path through the gate
    'S': {'name': 'Field Stones', 'kind': 'floor', 'color': '#8a8170'},              # the shore landing
    's': {'name': 'Sand', 'kind': 'floor', 'color': '#f3dfc9'},                      # the arena floor
    'F': {'name': 'Farm Soil', 'kind': 'floor', 'color': '#90450d'},                 # fields
    'o': {'name': 'Flower Soil', 'kind': 'floor', 'color': '#a77e63'},               # flower and herb beds
    'e': {'name': 'Springlands Dirt', 'kind': 'floor', 'color': '#b39672'},          # animal pens
    'G': {'name': 'Fertile Springlands Dirt', 'kind': 'floor', 'color': '#95b261'},  # the manor's lawns
    'h': {'name': 'Brick-Timbered Block', 'kind': 'floor', 'color': '#947f75'},      # the town plots round the square
})

P = Plan('Laketown village (layout)', 1, 160, 160, 160)
P.project = 'Laketown'
lake = P.level('lake', 'Lake (water level, 0 m)', 0, 1)
dock = P.level('dock', 'Docks, piers, boardwalk (+1 m)', 1, 3)
low = P.level('low', 'Low decks: carpentry, smokehouse, bathhouse, arena floor (+2 m)', 2, 4)
walk = P.level('walk', 'Walkways, causeway, gatehouse (+3 m)', 3, 4)
mid = P.level('mid', 'Square, smithy, lodge, arena stands (+4 m)', 4, 4)
up5 = P.level('up5', 'Upper decks: farm, tavern, lodging house (+5 m)', 5, 4)
high = P.level('high', 'Alchemist (+6 m)', 6, 4)
mnr = P.level('manor', 'Manor grounds (+8 m)', 8, 5)
R, Z, D = P.rect, P.zone, P.disc
EDGE = 2                                                # keep this far inside the build area's edge


def deck(g, x0, y0, x1, y1, ch, edge=None):
    """A platform deck, with a 1 m edge in another material if given."""
    R(g, x0, y0, x1, y1, edge or ch)
    if edge:
        R(g, x0 + 1, y0 + 1, x1 - 1, y1 - 1, ch)


def stairs(lid, label, x0, y0, x1, y1, rise, up):
    """Stairs over the squares x0..x1, y0..y1 (metres) on the lower level, rising `rise` m towards `up`
    (N, S, E or W), no steeper than 45 degrees."""
    rot = {'N': 0, 'S': 180, 'E': 90, 'W': 270}[up]
    w, d = (x1 - x0, y1 - y0) if up in 'NS' else (y1 - y0, x1 - x0)
    assert d >= rise, (label, d, rise)
    P.item(lid, 'stairs', label, x0, y0, w, d, rise, rot, '#a98a62')


# ================================================================= the shore: ground along the south
def shoreline(x):
    return 140 + 2 * math.sin(x / 21) + 1.2 * math.sin(x / 8.3 + 1.3)


BED = -4                                               # where the stilts stand: 4 m below the surface (extend deeper in game)


def ground(x, y):
    s = shoreline(x)
    if y < s:                                           # the lake bed, shelving down from the shore to 4 m
        return -min(-BED, max(1, round((s - y) / 1.5)))
    return min(3, 1 + math.floor((y - s) / 3))          # a beach, then two banks up to the meadow


P.ground_fn(ground)
P.ground_rect(60, 142, 100, 160, 3, 'max')             # the shore road and landing sit on the meadow
P.ground_rect(74, 139, 86, 142, 3, 'max')              # so does the gatehouse's forecourt
for y in range(160):
    for x in range(160):
        if P.ground_at(x, y) < 0:
            lake[y][x] = '~'

# ================================================================= the main square (+4 m), its altar and halls
deck(mid, 64, 64, 96, 96, 'L', 'f')
P.item('mid', 'altar', 'Flame Altar', 80 - ALTAR_W / 2, 80 - ALTAR_D / 2, ALTAR_W, ALTAR_D, ALTAR_H, color='#d9541e', iid='altar')
Z('mid', 'Main square', 64, 64, 96, 96, '#b8862b')
Z('mid', 'Market stalls (two)', 66, 66, 73, 76, '#c4501a')          # in the north corners, clear of the side entrances
Z('mid', 'Market stall', 87, 71, 95, 76, '#c4501a')
Z('mid', "Trader's stall (Mei-Yin Chen)", 87, 66, 95, 71, '#c4501a')
# storage in the middle of town: every station is within ~85 m, inside a magic chest's ~100 m reach
Z('mid', 'Storage hall (magic chests), west wing', 66, 87, 76, 94, '#8a5cc2')
Z('mid', 'Storage hall, east wing', 84, 87, 94, 94, '#8a5cc2')
stairs('walk', 'Stairs: square to the causeway', 77, 96, 83, 98, 1, 'N')
stairs('walk', 'Stairs: square to the west walkway', 62, 77, 64, 83, 1, 'E')
stairs('walk', 'Stairs: square to the east walkway', 96, 77, 98, 83, 1, 'W')
R(mid, 74, 42, 86, 64, 'L')                                      # the north promenade
Z('mid', 'North promenade', 74, 50, 86, 64, '#b8862b')
# the town plots either side of the promenade, a step up
deck(up5, 58, 46, 72, 62, 'h', 't')
R(mid, 72, 51, 74, 57, 'L')
stairs('mid', 'Stairs up to the tavern', 72, 51, 74, 57, 1, 'W')
R(mid, 56, 50, 58, 52, 'w')                                      # the tavern's side stair, down to the west landing
stairs('mid', 'Side stair: tavern to the west landing', 56, 50, 58, 52, 1, 'E')
Z('up5', 'Tavern (Bard): food and rooms', 58, 46, 72, 62, '#b0596f')
deck(up5, 88, 46, 108, 62, 'h', 't')
R(mid, 86, 51, 88, 57, 'L')
stairs('mid', 'Stairs up to the lodging house', 86, 51, 88, 57, 1, 'E')
Z('up5', 'Lodging house (assistants and guests)', 88, 46, 108, 62, '#9c6b8e')

# ================================================================= the manor (+8 m): grand stair, side stairs
stairs('mid', 'Grand stair to the manor', 76, 42, 84, 50, 4, 'N')
deck(mnr, 50, 6, 110, 42, 'P', 'f')
R(mnr, 52, 8, 61, 40, 'G'); R(mnr, 99, 8, 108, 40, 'G')        # lawns either side
for y in (11, 19, 27):                                          # flower beds in them (clear of the side stairs)
    R(mnr, 54, y, 59, y + 3, 'o'); R(mnr, 101, y, 106, y + 3, 'o')
Z('manor', 'Manor grounds', 50, 6, 110, 42, '#8a5cc2')
Z('manor', 'Manor house', 62, 9, 98, 28, '#6b4fa3')
Z('manor', "Gallery (Collector's showcases)", 62, 9, 74, 28, '#8a6aa8')
Z('manor', 'Front terrace (over the square)', 62, 30, 98, 41, '#b7a3dc')
Z('manor', 'West garden', 52, 8, 61, 40, '#3f8a4f')
Z('manor', 'East garden', 99, 8, 108, 40, '#3f8a4f')

# ================================================================= west: smithy (+4 m), carpentry (+2 m), bathhouse
R(walk, 34, 77, 64, 83, 'w')                                    # the west walkway
Z('walk', 'West walkway', 40, 77, 62, 83, '#2f8f8a')
R(walk, 34, 70, 40, 77, 'w')                                    # up to the smithy
stairs('walk', 'Stairs up to the smithy', 34, 70, 40, 72, 1, 'N')
deck(mid, 12, 40, 44, 70, 'B', 'k')
Z('mid', 'Smithy and smelting', 12, 40, 44, 70, '#5f6770')
Z('mid', 'Forge hall (Blacksmith)', 14, 44, 30, 55, '#5f6770')               # as built in the smithy blueprint
Z('mid', 'Furnace shed', 32, 42, 43, 47, '#8a8f96')
Z('mid', 'Smelting yard', 32, 47, 44, 55, '#8a8f96')
Z('mid', 'Work yard', 14, 55, 44, 59, '#8a8f96')
Z('mid', 'Ore and fuel store', 14, 59, 25, 68, '#8a8f96')
Z('mid', "Blacksmith's cottage", 26, 59, 33, 68, '#9c6b8e')
Z('mid', 'Smithy lane', 34, 59, 40, 70, '#8a8f96')
Z('mid', 'Fuel bunkers', 40, 58, 44, 69, '#8a8f96')
# the villagers' quarter (NW, +5 m), as built in its blueprint: eight homes round a green with a well, the dining
# hall at the head of the green; the deck grows to the build area's edge on the west and north. Up from the
# smithy, and back steps off its south-east corner down onto the west landing.
deck(up5, 3, 3, 46, 34, 'r', 't')
R(up5, 14, 16, 32, 24, 'G')
R(mid, 20, 34, 26, 40, 'w')
stairs('mid', "Stairs up to the villagers' quarter", 20, 34, 26, 36, 1, 'N')
R(up5, 44, 30, 48, 39, 'w'); R(mid, 44, 39, 48, 42, 'w')
stairs('mid', 'Back steps down to the west landing', 45, 39, 47, 41, 1, 'N')
Z('up5', "Villagers' quarter", 3, 3, 46, 34, '#9c6b8e')
Z('up5', 'Dining hall (food stations)', 16, 4, 30, 15, '#c46a2a')
Z('up5', 'Village green and well', 14, 16, 32, 24, '#3f8a4f')
Z('up5', "The Godwins' house", 4, 4, 12, 12, '#9c6b8e')
Z('up5', "The Reeds' house", 35, 4, 45, 12, '#9c6b8e')
Z('up5', 'Wattle cottage', 4, 16, 12, 24, '#9c6b8e')
Z('up5', 'Stone cottage', 35, 16, 43, 24, '#9c6b8e')
Z('up5', 'Allotments', 44, 16, 46, 24, '#6f8a43')
Z('up5', 'The pair (two cottages)', 4, 26, 19, 33, '#9c6b8e')
Z('up5', "Kaori's cottage", 27, 26, 34, 33, '#9c6b8e')
Z('up5', 'Tarred cottage', 36, 26, 43, 33, '#9c6b8e')
Z('up5', 'Back steps', 44, 30, 48, 39, '#2f8f8a')
# the west loop: from the smithy's corner up a side stair to the manor's west garden
R(mid, 44, 42, 56, 52, 'w')
stairs('mid', 'West stair: smithy to the manor', 50, 42, 56, 50, 4, 'N')
Z('mid', 'West landing', 44, 42, 56, 52, '#2f8f8a')
R(walk, 34, 83, 40, 90, 'w')                                    # down to the carpentry
R(low, 34, 90, 40, 92, 'r')
stairs('low', 'Stairs down to the carpentry', 34, 90, 40, 92, 1, 'N')
deck(low, 10, 92, 44, 126, 'r', 't')                           # as built in its blueprint (34 x 34 m)
Z('low', 'Carpentry and storehouse', 10, 92, 44, 126, '#9a7344')
Z('low', 'Storehouse (bulk wood and stone)', 11, 93, 19, 106, '#8a5cc2')
Z('low', 'Workshop (Carpenter)', 19, 93, 33, 106, '#9a7344')
Z('low', 'Kiln shed', 41, 93, 44, 104, '#a0613f')
Z('low', 'Stone yard', 11, 106, 19, 110, '#8a8f96')
Z('low', 'Timber yard and drying shed', 11, 110, 34, 126, '#7a6653')
Z('low', 'Work yard', 34, 107, 44, 117, '#8a8f96')
Z('low', "Carpenter's cottage", 35, 117, 44, 125, '#9c6b8e')
R(dock, EDGE, 96, 10, 124, 't')                                 # the west dock, a step down
stairs('dock', 'Stairs down to the west dock', 8, 110, 10, 116, 1, 'E')
Z('dock', 'West dock (timber and stone in)', EDGE, 96, 10, 124, '#2f7fb3')
R(walk, 54, 83, 58, 86, 'w')                                    # down to the bathhouse (as the square's blueprint has it)
deck(low, 46, 86, 62, 98, 'h', 't')
stairs('low', 'Stairs down to the bathhouse', 54, 86, 58, 88, 1, 'N')
Z('low', 'Barber and bathhouse (Elio Ricci)', 46, 86, 62, 98, '#3f7f9e')
Z('low', 'Bath hall and plunge pool', 47, 89, 62, 97, '#3f7f9e')
R(low, 57, 98, 61, 100, 'h')                                    # the fighters' way: bathhouse up to the stands
stairs('low', 'Stairs: bathhouse to the arena', 57, 98, 61, 100, 2, 'S')

# ================================================================= south: causeway, arena, inner harbour, gatehouse
R(walk, 77, 96, 83, 135, 'w')                                   # the causeway and the drawbridge
Z('walk', 'Causeway', 77, 98, 83, 131, '#2f8f8a')
Z('walk', 'Drawbridge (lifts against the arch)', 77, 131, 83, 135, '#75726e')
# the arena: round stands at +4 m round a round sand floor at +2 m
AX, AY = 59, 113
D(mid, AX, AY, 13, 'k')
D(mid, AX, AY, 7, ' ')
D(low, AX, AY, 7, 's')
R(walk, 72, 110, 77, 116, 'w')
stairs('walk', 'Stairs up to the arena', 72, 110, 74, 116, 1, 'W')
stairs('low', 'Stairs down to the arena floor', 57, 106, 61, 108, 2, 'N')
Z('mid', 'Arena stands (three tiers of seats)', 46, 100, 72, 126, '#c2416e')
Z('mid', "Champion's box", 56, 121, 62, 125, '#9e3742')
Z('mid', "The fighters' way", 57, 100, 61, 106, '#8a8f96')
Z('low', 'Arena floor', 52, 106, 66, 120, '#c2416e')
R(low, 42, 110, 46, 116, 'r')                                   # carpentry to the arena
stairs('low', 'Stairs: carpentry to the arena', 42, 110, 46, 116, 2, 'E')
# the main dock (as built: its blueprint): the quay along the harbour's south side, the open south quay, the
# harbourmaster's office over the water by the causeway, the trading pier, the stone mole with the harbour
# light, the warehouse behind the quay
R(walk, 83, 118, 84, 124, 'w')
R(dock, 84, 114, 108, 124, 't'); R(dock, 84, 124, 96, 132, 't'); R(dock, 96, 124, 106, 134, 't'); R(dock, 106, 122, 108, 128, 't')
R(dock, 85, 104, 94, 114, 't')                                  # the office's deck and landing stage
R(dock, 96, 100, 100, 114, 't')                                 # the trading pier
R(dock, 104, 98, 108, 114, 'k')                                 # the mole
stairs('dock', 'Stairs down to the main dock', 84, 118, 88, 124, 2, 'W')
Z('dock', 'Main dock (boats and trade)', 84, 114, 108, 124, '#2f7fb3')
Z('dock', "Harbourmaster's office", 85, 105, 93, 113, '#9c6b8e')
Z('dock', 'Trading pier and crane', 96, 100, 100, 114, '#2f7fb3')
Z('dock', 'Mole and harbour light', 104, 98, 108, 114, '#8a8f96')
Z('dock', 'Warehouse', 96, 124, 106, 134, '#8a5cc2')
Z('dock', 'South quay', 84, 124, 96, 132, '#2f7fb3')
Z('lake', 'Inner harbour', 84, 98, 112, 113, '#2f7fb3')
# the south loop: a low boardwalk from the main dock to the smokehouse, the boathouse off it
R(dock, 108, 122, 128, 128, 't')
R(dock, 112, 128, 120, 136, 't'); R(dock, 114, 130, 118, 136, ' ')
stairs('dock', 'Stairs up to the smokehouse', 126, 122, 128, 128, 1, 'E')
Z('dock', 'Boardwalk', 108, 122, 126, 128, '#2f8f8a')
Z('dock', 'Boathouse', 112, 128, 120, 136, '#7a6653')
# the gatehouse, over the waterline (as built: its blueprint): two towers either side of an open arch, a moat
# between their prows under the drawbridge, a forecourt between their land ends; the path straight through to
# the shore road, over the landing
R(walk, 66, 133, 74, 142, 'C'); R(walk, 86, 133, 94, 142, 'C'); R(walk, 74, 135, 86, 142, 'C')
R(walk, 66, 142, 94, 146, 'S'); R(walk, 70, 146, 90, 152, 'S')
R(walk, 77, 135, 83, 152, 'q')
R(walk, 77, 152, 83, 160 - EDGE, 'd')
Z('walk', 'Gatehouse', 66, 133, 94, 142, '#75726e')
Z('walk', 'West gate tower (fighting tower)', 66, 133, 74, 142, '#5f6770')
Z('walk', 'East gate tower (watch tower)', 86, 133, 94, 142, '#5f6770')
Z('walk', 'Gate arch (two portcullises)', 77, 135, 83, 139, '#75726e')
Z('walk', 'Forecourt', 74, 139, 86, 142, '#75726e')
Z('walk', 'Shore road', 77, 152, 83, 160 - EDGE, '#8c7455')
Z('walk', 'Shore landing (arrivals)', 60, 142, 100, 160 - EDGE, '#8c7455')

# ================================================================= east: farm (+5), alchemist (+6), lodge (+4), fishing
R(walk, 96, 77, 116, 83, 'w')                                   # the east walkway
Z('walk', 'East walkway', 98, 77, 116, 83, '#2f8f8a')
deck(walk, 116, 72, 130, 90, 'w', 't')
Z('walk', 'East junction', 116, 72, 130, 90, '#2f8f8a')
Z('walk', 'Pavilion', 117, 73, 122, 76.5, '#2f8f8a')
# the farm (as built: its blueprint): the farmhouse (kitchen and bakehouse) by the service stair to the manor,
# the barn, the yard across its width, the byre and pens, the lane down to the junction, the fields, the
# nursery and apiary by the herb bridge
R(walk, 124, 66, 130, 72, 'w')                                  # up to the farm, on the lane's line
stairs('walk', 'Stairs up to the farm', 124, 66, 130, 70, 2, 'N')
deck(up5, 114, 30, 152, 66, 'r', 't')
R(up5, 115, 41, 151, 48, 'S')                                   # the yard
R(up5, 115, 48, 123, 65, 'e'); R(up5, 124, 48, 130, 66, 'd')   # the pens, the lane
R(up5, 131, 48, 143, 65, 'F'); R(up5, 143, 48, 151, 65, 'o')   # the fields, the garden
Z('up5', 'Farm (Farmer)', 114, 30, 152, 66, '#3f8a4f')
Z('up5', 'Farmhouse (kitchen, bakehouse; the Farmer upstairs)', 119, 31, 135, 41, '#c46a2a')
Z('up5', 'Barn and hayloft', 139, 31, 151, 41, '#9a7d55')
Z('up5', 'Farmyard and well', 115, 41, 151, 48, '#9a7d55')
Z('up5', 'Byre and pens (yaks, goats, birds)', 114, 48, 124, 66, '#a0905a')
Z('up5', 'Fields', 131, 48, 143, 66, '#6f8a43')
Z('up5', 'Nursery and apiary', 143, 48, 152, 66, '#d4a017')
# the research hall (NE, +6 m, as built: its blueprint): the hall of research, the Researcher's round tower
# with its observatory, the mill-house with the Mill and its water wheel, round a forecourt up from the farm
R(up5, 135, 28, 139, 30, 'r')
stairs('up5', 'Stairs up to the research hall', 135, 28, 139, 30, 1, 'N')
deck(high, 118, 8, 152, 28, 'g', 'k')
Z('high', 'Research hall (Ancient Researcher)', 118, 8, 152, 28, '#56806c')
Z('high', 'Hall of research (Infusion Altar, Ancient Workbench, Gem Forge)', 129, 9, 144, 21, '#56806c')
Z('high', "The Researcher's tower and observatory", 119, 11, 127, 19, '#56806c')
Z('high', 'Mill-house (the Mill, its water wheel)', 145, 9, 152, 17, '#8a8f96')
Z('high', 'Forecourt', 127, 21, 145, 28, '#56806c')
# the herb bridge: from the farm's south edge up to the alchemist's garden
R(up5, 143, 66, 149, 74, 'r')
stairs('up5', 'Herb bridge: farm to the alchemist', 143, 72, 149, 74, 1, 'S')
# the east loop: a service stair from the farm's kitchen side up to the manor's east garden
R(up5, 110, 34, 114, 40, 'r')
stairs('up5', 'Service stair: farm to the manor', 110, 34, 116, 40, 3, 'W')
# the alchemist's round tower platform
CX, CY = 146, 84
D(high, CX, CY, 10, 'g')
D(high, CX, CY, 10, 'k', r_in=9.2)
for x, y in P.cells_rect(CX - 9, CY + 2, CX + 9, CY + 9):        # herb beds round the south side
    if 6.5 <= P.dist(x, y, CX, CY) <= 8.5:
        high[y][x] = 'o'
R(walk, 130, 81, 136, 87, 'w')                                  # up to the alchemist
stairs('walk', 'Stairs up to the alchemist', 130, 81, 136, 87, 3, 'E')
R(high, 136, 81, 138, 87, 'g'); R(high, 143, 74, 149, 76, 'g')   # landings: the junction's stair, the herb bridge
Z('high', "Alchemist's tower (lab, quarters, drying loft)", 141, 77, 151, 87, '#56806c')    # as built: its blueprint
Z('high', 'Herb garden', 138, 86, 154, 93, '#3f8a4f')
Z('high', 'Copper still', 151.5, 77.5, 154.5, 80, '#8d694b')
R(walk, 118, 90, 124, 96, 'w')                                  # up to the hunting lodge
stairs('walk', 'Stairs up to the hunting lodge', 118, 94, 124, 96, 1, 'S')
deck(mid, 114, 96, 146, 116, 'c', 't')
Z('mid', 'Hunting lodge (Hunter)', 114, 96, 146, 116, '#6d7a45')
Z('mid', "Lodge hall (the Hunter's loft above)", 116, 99, 128, 114, '#6d7a45')          # as built: its blueprint
Z('mid', 'Tannery shed', 130, 98, 138, 104, '#9a7d55')
Z('mid', 'Weaving house', 139, 97.5, 146, 104.5, '#9a7d55')
Z('mid', 'Drying racks', 130.5, 106, 135.5, 112, '#9a7d55')
Z('mid', 'Archery lane', 140, 106, 146, 116, '#6d7a45')
R(low, 134, 116, 140, 120, 't')                                 # down to the smokehouse
stairs('low', 'Stairs down to the smokehouse', 134, 116, 140, 120, 2, 'N')
deck(low, 128, 120, 150, 136, 't')                              # as built: its blueprint (grown 4 m south)
Z('low', "Fisher's yard", 128, 120, 150, 128, '#3f7f9e')
Z('low', "Bunkhouse (the Fisher's, under an upturned hull)", 129, 128, 145, 136, '#9c6b8e')
Z('low', 'Drying green', 145, 128, 150, 136, '#3f8a4f')
R(dock, 150, 112, 156, 128, 't')
R(dock, 150, 126, 160 - EDGE, 136, 't')                         # the pier head, the smokehouse on it
for y in (114, 120):
    R(dock, 156, y, 160 - EDGE, y + 2, 't')
stairs('dock', 'Stairs down to the fishing pier', 150, 122, 152, 128, 1, 'W')
Z('dock', 'Fishing pier', 150, 112, 156, 126, '#2f7fb3')
Z('dock', 'Smokehouse', 150, 128, 158, 136, '#7a6653')

# ================================================================= stilts: posts from the lake bed up to each deck
# One post per square on a 4 m grid under every deck over the water, plus one wherever a narrow pier or
# strip would otherwise be more than 2 m from a post of its own deck. Each post stands on the bed (4 m
# below the surface) and stops under its deck's floor course. Over the beach they're partly buried.
stl = P.level('stilts', 'Stilts, standing on the lake bed (-4 m)', BED, 12)
DECKS = [('dock', 1), ('low', 2), ('walk', 3), ('mid', 4), ('up5', 5), ('high', 6), ('manor', 8)]
post_ch = {lid: P._alloc({'name': f'Tarred Wood Block (stilt to +{el} m)', 'kind': 'block', 'color': '#4e4844', 'height': el - 0.5 - BED})
           for lid, el in DECKS}
lowest = {}
for lid, el in DECKS:                                   # the lowest deck over each square is the one a post holds up
    for y, row in enumerate(P.grids[lid]):
        for x, c in enumerate(row):
            if c != ' ' and (x, y) not in lowest and P.ground_at(x, y) < 0:
                lowest[(x, y)] = lid
posts = {xy: lid for xy, lid in lowest.items() if xy[0] % 4 == 1 and xy[1] % 4 == 1}
for y in range(P.H):
    for x in range(P.W):
        lid = lowest.get((x, y))
        if lid and not any(posts.get((x + dx, y + dy)) == lid for dx in range(-2, 3) for dy in range(-2, 3)):
            posts[(x, y)] = lid
for (x, y), lid in posts.items():
    stl[y][x] = post_ch[lid]
print('stilts:', len(posts))

P.item('mid', 'spawn', 'Spawn point', 79.5, 91, 1, 1, 0.5, 180, '#2fa36b')   # walk mode starts here: the square's south entrance, facing up the promenade
problems = P.check(outdoor_ok=('lake',), ignore_types=('stairs',))
print('item problems:', len(problems))
for p_ in problems:
    print('  ', p_)

NOTES = """Laketown: a village on stilts in a lake, drafted by Claude as a layout at 1 m squares. Decks, stilts and labels: railings and buildings come next. North is up; the shore runs along the south.

THE ALTAR: the Flame Altar stands in the middle of the main square. At altar level 4 its 160 m build area covers the whole canvas (160 x 160 m); everything stays at least 2 m inside its edge.

LEVELS (deck tops above the water)
- -4 m Stilts: posts stand on the lake bed, 4 m below the surface, on a 4 m grid under every deck (plus extra under narrow piers). The real lake may be deeper: extend them in game. Near the shore the bed shelves up, so posts there are partly buried.
- +1 m Docks, piers and the boardwalk: the west dock, the main dock (its quay, the trading pier and the stone mole round the inner harbour), the fishing pier, the boardwalk from the main dock to the smokehouse.
- +2 m Low decks: carpentry and storehouse, the barber and bathhouse, the fisher's smokehouse, the arena floor.
- +3 m Walkways: the causeway (with a drawbridge at the gate end), the west and east walkways, the east junction, the gatehouse.
- +4 m The main square and north promenade, the smithy, the hunting lodge, the arena stands.
- +5 m Upper decks: the villagers' quarter, the farm, the tavern, the lodging house.
- +6 m The alchemist and the research hall. +8 m The manor grounds.
Every area is a different height from its neighbours and joined by stairs (45 degrees or gentler, with landings top and bottom).

GETTING ROUND: the square is the hub, and loops join the outer platforms so nothing important is a dead end.
- West loop: square, west walkway, smithy, west stair up to the manor, grand stair down to the square. The tavern's side stair drops onto the west landing too, and the villagers' quarter has back steps down to it, so the quarter reaches the tavern and the manor without crossing the smithy or the square.
- East loops: square, east walkway, farm, service stair up to the manor, grand stair down; and farm, herb bridge, alchemist, east junction.
- South loop: square, causeway, main dock, boardwalk, smokehouse, hunting lodge, east junction, east walkway.

SURVIVORS: 1.0 has 28 (11 craftspeople, 7 assistants, 10 villagers), each wanting a sheltered bed, with a stocked food station nearby; the Flame needs 18 happy ones by level 11 (enshrouded.tools). Beds are planned for all of them:
- Craftspeople live at their work: the Blacksmith's and Carpenter's cottages, the farmhouse, the alchemist's quarters, the Hunter's lodge hall, the fisher's bunkhouse, rooms at the tavern (Bard) and the bathhouse (Barber), the research hall (Ancient Researcher), the lodging house (the Collector and the trader).
- Villagers: the villagers' quarter (eight homes round a green, with a dining hall). Assistants and guests: the lodging house.
- Food: the dining hall and the tavern hold the food stations. Which station counts as a survivor's "food station" isn't published: check in game.

AREAS
- Main square (32 x 32 m): the altar in the middle, market stalls and the trader's stall (Mei-Yin Chen), and the storage halls (magic chests) either side of the south entrance, within about 85 m of every station (a magic chest's reach is about 100 m: the planner's wiki note, unconfirmed for 1.0).
- Round the square: the tavern and the lodging house a step up either side of the north promenade; the barber and bathhouse a step down off the west walkway.
- Manor grounds (+8 m): the manor house with a gallery for the Collector's showcases, the front terrace over the square, lawns either side. Reached by the grand stair, the west stair from the smithy and the service stair from the farm.
- Villagers' quarter (NW, +5 m, 43 x 31 m): eight homes for the ten villagers round a village green with a well, the dining hall at the head of the green, allotments. Up from the smithy, and back steps down to the west landing.
- Smithy and smelting (fired brick, +4 m): forge hall, furnace shed, smelting and work yards, ore and fuel store, fuel bunkers, the Blacksmith's cottage, a lane up from the walkway stair.
- Carpentry and storehouse (+2 m, 34 x 34 m): the north range (storehouse and workshop under one roof), the kiln shed, the stone yard, the timber yard with its drying shed and jib crane, the work yard, the Carpenter's cottage; the west dock below. Down the west walkway's branch on the smithy lane's line.
- Arena: round stands at +4 m (26 m across, a promenade, three tiers of seats, a champion's box) round a sand floor at +2 m (14 m across); ways in from the carpentry, the causeway and the bathhouse (the fighters' way).
- Barber and bathhouse (+2 m, Elio Ricci): a bath hall with a plunge pool and four bathtubs, the Barber's salon and rooms upstairs, a loggia over the arena.
- Main dock (+1 m): the quay round the inner harbour's south side, the harbourmaster's office over the water by the causeway, the trading pier and its crane, the stone mole with the harbour light, the warehouse, the boardwalk and the boathouse. Gatehouse (castle stone, +3 m): straddles the waterline, two towers either side of an open arch closed by two portcullises, a forecourt between them on the land side, the shore road and landing beyond, a drawbridge over the moat between the towers onto the causeway.
- East: the farm (+5 m: the farmhouse with the kitchen and bakehouse by the service stair, the barn, the farmyard, the byre and pens, fields, seedbeds and an apiary for the Beehives); the research hall (NE, +6 m): the hall of research (Infusion Altar, Ancient Workbench, Placeable Gem Forge), the Researcher's round tower with its observatory, and the mill-house with the Mill and its water wheel; the alchemist's round tower and herb garden (+6 m, linked to the farm by the herb bridge); the hunting lodge (+4 m); the fisher's smokehouse and bunkhouse (+2 m) and the fishing pier (+1 m).

MATERIALS: wood decks throughout (rough wood walkways, refined wood workshops and farm, tarred wood docks, edges and stilts, conifer for the lodge, brick-timbered decks for the town plots); stone where it suits: limestone paving and a fancy stone edge for the square, fired brick for the smithy, castle stone for the gatehouse, polished stone for the manor, polished granite for the alchemist and research hall, rough-cut stone for the arena.

DETAIL BLUEPRINTS (0.5 m, each in the Laketown project, in this layout's coordinates)
- Main square (doc laketown-square): done (bones, roofs, details, review).
- Smithy (doc laketown-smithy): done (bones, details, review).
- Manor (doc laketown-manor): done (bones, details, review, character).
- Villagers' quarter (doc laketown-villagers): done (bones, details, review). Its deck grew to 43 x 31 m and it gained back steps; this layout matches.
- Carpentry and west walkway (doc laketown-carpentry): done (bones, details, review). Its deck grew to 34 x 34 m and the west dock runs on south; this layout matches.
- Bathhouse and arena (doc laketown-bathhouse): done (bones, details, review); this layout matches.

NEXT
- Detail blueprints for the other areas, one at a time: buildings, railings, roofs.
- Stilts deeper if the lake is.
"""
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'laketown.json')
print('bytes', P.save(out, NOTES, 'r-claude-laketown-18'))
for a, b in P.merged:
    print('  folded:', a, '->', b)
