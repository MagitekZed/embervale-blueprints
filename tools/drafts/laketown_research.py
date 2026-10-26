"""Laketown: the research hall. 0.5 m detail plan. Pass 3 of 3: review and finishing touches.

The Ancient Researcher's (Loraine Crim's) seat in the town's north-east corner, at +6 m on polished granite,
up a stair from the farm. A forecourt opens off the stair; round it stand the hall of research (refined
stone under a granite roof, its Ancients' door on the stair's line) with the Infusion Altar, the Ancient
Workbench and the Placeable Gem Forge; the Researcher's round tower on the west, her study and bedroom below an
observatory under a copper dome; and on the east, over the open lake, the mill-house with the Mill (it grinds
the gem and mineral dusts) and a water wheel turning beside it to drive it.

Coordinates are the layout's (doc `laketown`): this plan's corner is the layout's (114, 4).
Run: python laketown_research.py  ->  writes laketown_research.json
"""
import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laketown_common import Area, WOOD, STONE, BED
from mage_common import ROOF_MATS

ROOF_MATS.setdefault('granite', ('Granite Ornamented Roof Block', '#6e6d65'))
ROOF_MATS.setdefault('copper', ('Copper Block', '#8d694b'))
RS, RCS, REF = '#7d776a', '#62605d', '#84837e'
POL, BLUE = '#b3b0a9', '#6c9dc3'                                    # polished stone trim, the Ancients' blue glow
OX, OY = 114, 4
A = Area('Laketown: the research hall (detail)', OX, OY, 42, 28, {
    'g': {'name': 'Polished Granite Block', 'kind': 'floor', 'color': '#626c7a'},       # the deck
    'k': {'name': 'Roughly Cut Stone Block', 'kind': 'floor', 'color': RCS},            # its edge
    'H': {'name': 'Refined Stone Block', 'kind': 'wall', 'color': REF, 'height': 6},    # the hall, 6 m
    'O': {'name': 'Refined Stone Block', 'kind': 'wall', 'color': REF},                 # the tower, a storey a level
    'M': {'name': 'Rough Stone Block', 'kind': 'wall', 'color': RS},                    # the mill-house
    'p': {'name': 'Roughly Cut Stone Block (parapet)', 'kind': 'block', 'color': RCS, 'height': 1},
    'o': {'name': 'Roughly Cut Stone Block (parapet pier)', 'kind': 'block', 'color': RCS, 'height': 1.5},
})
P, R, zone, put = A.P, A.R, A.zone, A.put
stl = A.level('stilts', 'Stilts, standing on the lake bed (-4 m)', BED, 12)
lake = A.level('lake', 'Lake (water level, 0 m)', 0, 1)
up5 = A.level('up5', 'The farm, its north edge (+5 m)', 5, 4)
high = A.level('high', 'The research hall: deck, hall, tower, mill (+6 m)', 6, 4)
ob10 = A.level('ob10', "Tower: the Researcher's bedroom (+10 m)", 10, 4)
ob14 = A.level('ob14', 'Tower: the observatory (+14 m)', 14, 4)
obroof = A.level('obroof', 'Tower: the copper dome (+18 m)', 18, 5)
hroof = A.level('hroof', 'Hall: the granite roof (+12 m)', 12, 4)
mroof = A.level('mroof', 'Mill-house: the roof (+10 m)', 10, 5)
s6 = A.level('s6', 'Tower: spiral stair (+6 m)', 6, 4)
s10 = A.level('s10', 'Tower: spiral stair (+10 m)', 10, 4)
dais = A.level('dais', 'Hall: the dais under the Infusion Altar (+6.5 m)', 6.5, 4)
port = A.level('port', "Hall: the portico's entablature (+11 m)", 11, 1)
fr11 = A.level('fr11', 'Hall: the glowing frieze under the eaves (+11 m)', 11, 1)
sc10 = A.level('sc10', 'Tower: the string course (+10 m)', 10, 1)
sc14 = A.level('sc14', 'Tower: the string course (+14 m)', 14, 1)
apex = A.level('apex', "Tower: the glow at the dome's crown (+21.5 m)", 21.5, 1)
relic = A.level('relic', 'Forecourt: the Ancient crystal (+7 m)', 7, 3)
glow = A.level('glow', 'Forecourt: the glowing caps on the posts and piers (+7.5 m)', 7.5, 1)


def block(name, color, h, base=0):
    e = {'name': name, 'kind': 'block', 'color': color, 'height': h}
    if base:
        e['base'] = base
    return P._alloc(e)

# ================================================================= the lake
def shoreline(x):
    return 140 + 2 * math.sin(x / 21) + 1.2 * math.sin(x / 8.3 + 1.3)


def ground(x, y):
    s = shoreline(x)
    if y < s:
        return -min(4, max(1, round((s - y) / 1.5)))
    return min(3, 1 + math.floor((y - s) / 3))


P.ground_fn(lambda mx, my: ground(mx + OX, my + OY))
for x, y in P.cells_rect(0, 0, 42, 28):
    if P.ground_at(x, y) < 0:
        lake[y][x] = '~'

# ================================================================= the deck (+6 m)
# Polished granite on a roughly cut stone edge, the layout's 32 x 20 m grown 2 m east for the mill-house; a
# low stone parapet with piers round it, open where the farm's stair arrives
A.deck(high, 118, 8, 152, 28, 'g', 'k')
A.parapet(high, 118, 8, 152, 8.5, every=4)                           # north
A.parapet(high, 118, 8.5, 118.5, 27.5, every=4)                      # west
A.parapet(high, 118, 27.5, 152, 28, [(135, 139)], every=4)           # south, open to the farm's stair
A.parapet(high, 151.5, 17, 152, 27.5, every=4)                       # east (the mill-house's wall north of it)
zone('high', 'Research hall (Ancient Researcher)', 118, 8, 152, 28, '#56806c')
zone('high', 'Forecourt', 127, 21, 145, 27.5, '#56806c')
# on the axis between the stair and the door, an Ancient crystal on a polished plinth, glowing blue
R(high, 136, 23.5, 138, 25.5, block('Highly Polished Stone Block (plinth)', POL, 1))
R(relic, 136.5, 24, 137.5, 25, block('Blue Luminescent Block (an Ancient crystal)', BLUE, 2))
R(relic, 136, 24, 136.5, 24.5, block('Blue Luminescent Block (a crystal shard)', BLUE, 1))
R(relic, 137.5, 24.5, 138, 25, block('Blue Luminescent Block (a crystal shard)', BLUE, 1.5))
R(relic, 137, 23.5, 137.5, 24, block('Blue Luminescent Block (a crystal shard)', BLUE, 0.5))
zone('relic', 'Ancient crystal', 136, 23.5, 138, 25.5, '#6c9dc3')
# the Researcher's specimen pots between the columns and either side of the crystal; benches; posts with a
# blue glow at the forecourt's corners, and on the piers either side of the stair
put('high', 'Large Grandleaf Cabbage Plant Pot', 131.5, 22); put('high', 'Large Bloomheart Fruit Plant Pot I', 141.5, 22)
put('high', 'Small Aurora Beans Plant Pot', 135, 24.5); put('high', 'Small Prickle Pearl Plant Pot', 138.5, 24.5)
put('high', 'Bench', 131.5, 26); put('high', 'Bench', 140.5, 26)
for (x, y) in ((128, 26.5), (144.5, 26.5)):
    R(high, x, y, x + 0.5, y + 0.5, block('Highly Polished Stone Block (lamp post)', POL, 1.5))
    R(glow, x, y, x + 0.5, y + 0.5, block('Blue Luminescent Block (a glowing cap)', BLUE, 0.5))
for x0 in (134, 139):
    R(glow, x0, 27.5, x0 + 1, 28, block('Blue Luminescent Block (a glowing cap)', BLUE, 0.5))

# ================================================================= lived in (pass 3)
# the quiet corner behind the tower, up the alley: a bench looking out over the lake, a glowing post
put('high', 'Bench', 121, 9, 180, label='Bench (over the lake)')
R(high, 125, 9, 125.5, 9.5, block('Highly Polished Stone Block (lamp post)', POL, 1.5))
R(glow, 125, 9, 125.5, 9.5, block('Blue Luminescent Block (a glowing cap)', BLUE, 0.5))
# specimen pots either side of the tower's door
put('high', 'Large Bloomheart Fruit Plant Pot II', 120.5, 19.5); put('high', 'Large Grandleaf Cabbage Plant Pot', 124.5, 19.5)
# her study cat (its bed and bowl), her cup on the desk; Ancient shards in a bowl and a jug on the study table;
# a stool by the telescope; a bucket of sweepings in the mill
put('high', 'Cat Pillow', 122, 16, label="Cat Pillow (the Researcher's cat)"); put('high', 'Cat Bowl', 123, 16)
put('high', 'Wooden Cup', 121, 14, z=1)
put('high', 'Wooden Bowl', 141, 16, z=1, label='Wooden Bowl (Ancient shards)'); put('high', 'Crude Wooden Jug', 142, 16, z=1)
put('ob14', 'Crude Wooden Stool', 121.5, 16)
put('high', 'Scrap Bucket', 146, 10, label='Scrap Bucket (sweepings of dust)')

# ================================================================= the hall of research (centre)
# Refined stone, 15 x 12 m and 6 m tall, under a granite roof; polished stone floor; its Ancients' door south
# onto the forecourt on the line of the farm's stair. Inside: the Infusion Altar facing the door, the Ancient
# Workbench and the Placeable Gem Forge either side
A.walls(high, 129, 9, 144, 21, 'H', 'P')
A.door('high', 'Ancients Night Door', 135, 20.5, 139, 21)
# tall windows (two frames one above the other, a transom between): three over the forecourt either side of
# the door, three to the north, the middle one behind the altar
for x0, y0 in ((130.5, 20.5), (132.5, 20.5), (140, 20.5), (142, 20.5), (130.5, 9), (133, 9), (136.5, 9), (140, 9), (142, 9)):   # (a metre in from the east wall, so they stay clear of it at 1 m)
    for z in (1, 3):
        A.win('high', 'Wooden Window Frame', x0, y0, x0 + 1, y0 + 0.5, z)
rh = A.roof(hroof)
rh.gable(129, 9, 144, 21, 'x', 'granite', pitch=0.5, overhang=0.5)
rh.paint()
# the Infusion Altar on a polished dais (a step up) facing the door, the tall north window behind it, four
# blue glowing pillars at the dais's corners
R(dais, 134.5, 10, 139.5, 14.5, 'P')
for (x, y) in ((134.5, 10), (139, 10), (134.5, 14), (139, 14)):
    R(dais, x, y, x + 0.5, y + 0.5, block('Blue Luminescent Block (an infusion light)', BLUE, 2))
put('dais', 'Infusion Altar', 136, 11.5, label='Infusion Altar (a 2 x 2 m placeholder)')
zone('dais', 'Dais (the Infusion Altar)', 134.5, 10, 139.5, 14.5, '#56806c')
put('high', 'Ancient Workbench', 130.5, 11, label='Ancient Workbench (a 2 x 2 m placeholder)')
put('high', 'Placeable Gem Forge', 141, 11, label='Placeable Gem Forge (a 2 x 2 m placeholder)')
P.item('high', 'npc-researcher', 'Ancient Researcher (Loraine Crim)', 130.5 - OX, 16 - OY, 3, 3, 2, 0, '#56806c')
zone('high', 'Hall of research', 129.5, 9.5, 143.5, 20.5, '#56806c')
# the room: miniatures of Embervale in showcases by the stations, bookshelves on the end walls, a long study
# table with chairs, a chest of Ancient materials, lanterns hung high
put('high', 'Embervale Miniature Showcase', 130.5, 13.5); put('high', 'Embervale Miniature Showcase', 141, 13.5)
put('high', 'Carved Wooden Shelf', 129.5, 14.5, 270, label='Carved Wooden Shelf (books)')
put('high', 'Carved Wooden Shelf', 143, 14.5, 90, label='Carved Wooden Shelf (books)')
put('high', 'Wooden Banquet Table', 140, 16, label='Wooden Banquet Table (the study table)')
put('high', 'Rustic Chair', 140.5, 17, 180); put('high', 'Rustic Chair', 142, 17, 180)
put('high', 'chest-large', 139.5, 19, label='Large Chest (Ancient materials)')
put('high', 'Ceiling Lantern', 133.5, 17.5); put('high', 'Ceiling Lantern', 141, 18.5)
# the portico: polished stone columns (5 m) across the front, an entablature on them with a glowing blue frieze
# on its face; a glowing band under the eaves round the other three sides
for x in (130, 133, 140, 143):
    R(high, x, 22, x + 1, 23, P._alloc({'name': 'Highly Polished Stone Block (column)', 'kind': 'wall', 'color': POL, 'height': 5}))
R(port, 129.5, 21, 144, 22.5, block('Highly Polished Stone Block (entablature)', POL, 1))
R(port, 129.5, 22.5, 144, 23, block('Blue Luminescent Block (the frieze)', BLUE, 1))
for x, y in P.cells_rect(128.5 - OX, 8.5 - OY, 144.5 - OX, 21 - OY):
    mx, my = OX + x / 2, OY + y / 2
    if not (129 <= mx < 144 and 9 <= my < 21):
        fr11[y][x] = block('Blue Luminescent Block (a band under the eaves)', BLUE, 0.5)
zone('high', 'Portico', 129.5, 21, 144, 23, '#56806c')

# ================================================================= the Researcher's tower (west)
# Round, 8 m across, three storeys of refined stone: her study (ground), her bedroom, and the observatory at
# the top under a copper dome; a stone spiral stair up the east side; the door south onto the forecourt
TX, TY = 123, 15
for g, fl in ((high, 'P'), (ob10, 'r'), (ob14, 'r')):
    A.circle(g, TX, TY, 8, 'O')
    A.circle(g, TX, TY, 7, fl)
for g in (ob10, ob14):
    A.circle(g, 125, 15, 3, ' ')
A.spiral(s6, 125, 15, 3, 4, 'Tower stair', STONE, start=180)
A.spiral(s10, 125, 15, 3, 4, 'Tower stair', STONE, start=180)
A.door('high', 'Wooden Door', 122, 18.5, 124, 19)
ro = A.roof(obroof)
ro.dome(TX, TY, 4.5, 3, 'copper')
ro.paint()
zone('high', "The Researcher's study", 119.5, 11.5, 123.5, 18.5, '#56806c')
zone('ob10', "The Researcher's bedroom", 119.5, 11.5, 123.5, 18.5, '#9c6b8e')
zone('ob14', 'Observatory', 119.5, 11.5, 123.5, 18.5, '#56806c')
for g in (sc10, sc14):                                              # polished stone bands round it at each floor
    A.circle(g, TX, TY, 9, block('Highly Polished Stone Block (string course)', POL, 0.5))
    A.circle(g, TX, TY, 8, ' ')
R(apex, 122.5, 14.5, 123.5, 15.5, block("Blue Luminescent Block (the glow at the dome's crown)", BLUE, 0.5))
# windows round each storey (west and north; south and east above the door and stair); a lantern by the door
for g in ('high', 'ob10', 'ob14'):
    A.win(g, 'Wooden Window Frame', 119, 14.5, 119.5, 15.5, 1)
    if g != 'ob10':                                                 # (the bedroom's wardrobe stands there; the study's
        A.win(g, 'Wooden Window Frame', 122.5, 11, 123.5, 11.5, 2 if g == 'high' else 1)   # sits high, over her notes)
for g in ('ob10', 'ob14'):
    A.win(g, 'Wooden Window Frame', 122.5, 18.5, 123.5, 19, 1)
A.win('ob14', 'Wooden Window Frame', 126.5, 14.5, 127, 15.5, 1)
put('high', 'Wall Lantern', 124.5, 19, 0, 2.0)
# her study: a desk and chair, a shelf of notes, a chest; her bedroom: bed, wardrobe, nightstand, a chest;
# the observatory: a telescope (copper, on an iron stand) trained on the west window, a table of star charts
put('high', 'table', 120.5, 14, label='Table (her desk)'); put('high', 'Rustic Chair', 121, 15, 180)
put('high', 'Carved Wooden Shelf', 122, 12, label='Carved Wooden Shelf (her notes)'); put('high', 'chest-small', 120, 16)
put('high', 'Hanging Lantern', 122, 15.5, z=3)
put('ob10', 'bed', 120.5, 13.5, label='Bed (the Ancient Researcher)'); put('ob10', 'Crude Wooden Closet', 122, 12)
put('ob10', 'Carved Wooden Nightstand', 120.5, 16.5); put('ob10', 'chest-small', 122.5, 17)
put('ob10', 'Hanging Lantern', 123, 15, z=3)
A.overlay(ob14, 121.5, 15, 122, 15.5, 'Iron Block (telescope stand)', '#848483', 1, 0)
for i, x in enumerate((121, 120.5, 120)):
    A.overlay(ob14, x, 15, x + 0.5, 15.5, 'Copper Block (telescope)', '#8d694b', 0.5, 1 + i * 0.5)
put('ob14', 'table', 122, 12.5, label='Table (star charts)'); put('ob14', 'Rustic Chair', 122.5, 13.5)

# ================================================================= the mill-house (east, over the open lake)
# Rough stone, 7 x 8 m, its gable to the forecourt under a lead-grey shingle roof; the Mill inside (the
# Alchemist makes it; it grinds the gem and mineral dusts the Gem Forge and the Alchemist need); its driver,
# a large water wheel, beside its east wall in the lake (it only needs to be nearby, not connected)
A.walls(high, 145, 9, 152, 17, 'M', 'w')
A.door('high', 'Wooden Door', 147.5, 16.5, 149.5, 17)
rm = A.roof(mroof)
rm.gable(145, 9, 152, 17, 'y', 'lead', pitch=1.0, overhang=0.5)
rm.paint()
put('high', 'Mill', 147, 11, label='Mill (a 2 x 2 m placeholder; needs a water wheel nearby)')
put('lake', 'Large Water Wheel', 152.5, 10.5, 90, label='Large Water Wheel (drives the Mill; set it partly in the water)')
zone('high', 'Mill-house', 145.5, 9.5, 151.5, 16.5, '#8a8f96')
put('high', 'Supply Sacks I', 150, 10, label='Supply Sacks I (gold dust)'); put('high', 'Supply Sacks I', 150, 11.5, label='Supply Sacks I (moonstone dust)')
put('high', 'Supply Sacks II', 150, 13, label='Supply Sacks II (diamond dust)'); put('high', 'Resource Bundle I', 146, 14, label='Resource Bundle I (ore to grind)')
A.win('high', 'Wooden Window Frame', 145, 12, 145.5, 13, 1); A.win('high', 'Wooden Window Frame', 151.5, 12, 152, 13, 1)
put('high', 'Hanging Lantern', 148, 14, z=3)

# ================================================================= the neighbours' edges (their own blueprints)
R(up5, 114, 30, 152, 32, 'r')                                       # the farm's north edge and its stair up here
R(up5, 135, 28, 139, 30, 'r')
A.stairs('up5', 'Stairs up to the research hall (farm blueprint)', 135, 28, 139, 30, 1, 'N')
A.cheeks(up5, 135, 28, 139, 30, 'N')
zone('up5', 'Farm (its blueprint)', 114, 30, 152, 32, '#3f8a4f')

# ================================================================= stilts, rim beams and checks
print('stilts:', A.stilts(stl, [('up5', 5), ('high', 6)]))
own = lambda x, y: 118 <= x < 152 and 8 <= y < 28
print('rim beam squares:', A.rim_beams(stl, [('high', 6)], own))
A.spawn('high', 143, 24, 90)                                     # walk mode starts here: the forecourt's east end, looking along the portico past the crystal to the tower
A.checks(ignore_types=('stairs', 'large-water-wheel'))             # (the wheel stands in the water by design)

NOTES = """Laketown: the research hall, as a 0.5 m detail blueprint. Pass 3 of 3 (review and finishing touches): done. Drafted by Claude.
This plan's corner is the layout's (114, 4), so it lines up with the Laketown layout and stamps back into the site plan there.

PASSES
1. Design and bones: the deck and its parapet, the hall of research, the Researcher's tower and the mill-house with floors, doors, stairs and roofs, the stations; the farm's stair up; stilts, labels.
2. Details: the Ancients' look (polished stone and a blue glow: the portico and its frieze, the band under the eaves, the infusion lights, the crystal, the glowing caps), tall windows, the tower's string courses and windows, the rooms and the observatory's telescope, the mill's dusts, the specimen pots, benches, lamps; then a 3D review and a refining round.
3. Review and finishing touches (done): a bench and a glowing post in the quiet corner behind the tower looking over the lake, specimen pots by the tower's door, the Researcher's cat and her cup, Ancient shards and a jug on the study table, a stool by the telescope, sweepings in the mill; the layout redrawn as built; the hand-off for the alchemist.

THE IDEA: the Ancient Researcher's (Loraine Crim's) seat at +6 m in the town's north-east corner, reached up a stair from the farm, round a forecourt: the hall of research ahead, her round tower with its observatory on the west, the mill-house on the east over the open lake. The Ancients' look: refined and polished stone with a blue glow.

THE DECK (+6 m): polished granite on a roughly cut stone edge, the layout's 32 x 20 m grown 2 m east for the mill-house, a low stone parapet with piers round it, open where the farm's stair arrives, a blue glowing cap on the piers either side.

THE FORECOURT: on the axis between the stair and the hall's door, an Ancient crystal glowing blue on a polished plinth; the Researcher's specimen pots (Grandleaf Cabbage and Bloomheart Fruit between the portico's columns, Aurora Beans and Prickle Pearl either side of the crystal); benches; polished posts with blue glowing caps at its corners.

THE HALL OF RESEARCH: refined stone, 15 x 12 m and 6 m tall, under a granite roof (1 in 2), a polished stone floor, a blue glowing band under the eaves.
- Across its front a portico: four polished stone columns (5 m), an entablature on them with a blue glowing frieze along its face. Its Ancients Night Door opens on the line of the farm's stair.
- Tall windows (two frames one above the other): four over the forecourt, five to the north, the middle one behind the altar.
- Inside: the Infusion Altar on a polished dais a step up, facing the door, four blue glowing pillars at the dais's corners; the Ancient Workbench and the Placeable Gem Forge either side, each with a showcase of an Embervale miniature beside it; bookshelves on the end walls; a long study table with chairs; a chest of Ancient materials; lanterns hung high; the Researcher.

THE RESEARCHER'S TOWER (west): round, 8 m across, three storeys of refined stone (+6, +10, +14 m) with polished stone bands at each floor, windows round each storey; a stone spiral stair up the east side; the door south onto the forecourt, a lantern by it.
- Her study: a desk and chair, a shelf of her notes, a chest.
- Her bedroom: bed, wardrobe, nightstand, a chest.
- The observatory: a copper telescope on an iron stand trained on the west window, a table of star charts; under a copper dome with a blue glow at its crown.

THE MILL-HOUSE (east, over the open lake): rough stone, 7 x 8 m, its gable to the forecourt, a lead-grey shingle roof; the Mill inside, sacks of gold, moonstone and diamond dust, ore to grind, windows (one onto the wheel), a lantern. Its driver, a Large Water Wheel, stands beside its east wall in the lake.

1.0 (enshrouded.tools, the wiki):
- The Ancient Researcher, Loraine Crim, makes the Infusion Altar, the Ancient Workbench and the Placeable Gem Forge (upgrade gems and set them in weapons at base), and four specimen plant pots. Before 1.0 the Gem Forge was only an object out in the world.
- The Mill is the Alchemist's. It grinds gem and mineral dusts (gold, moonstone, diamond and more), and only works with a force generator nearby: a Small or Large Water Wheel, or Small Windmill Sails. It doesn't need to be connected. enshrouded.tools says the water wheel must be partly in the water.
- The Ancients Night Door needs the Infusion Altar and the Mill to make.

HAND-OFF FOR THE ALCHEMIST (area 11): the Mill is the Alchemist's station, but it stands here, in the mill-house beside its water wheel, where the layout kept its spot (its dusts feed the Placeable Gem Forge too). The alchemist's tower doesn't need another.

CONNECTIONS
- South: the farm's stair (x 135..139, y 28..30), up 1 m from the farm (+5 m) between stone cheeks (the farm blueprint's); it arrives in the parapet's gap, 1 m clear in front of it.
- It's the only way in, as the layout has it. A footbridge west to the manor's east garden (8 m, up 2 m) would make a loop, but needs a gap in the finished manor's balustrade.

GLOW: the blue is Blue Luminescent Block (it needs Luminous Growth from caves); the crystal and the telescope are drawn in blocks, to show where things go.

SIZES: the stations (Infusion Altar, Ancient Workbench, Placeable Gem Forge, Mill) are 2 x 2 m placeholders until measured; the water wheel, the Ancients Night Door, the plant pots and the furniture are estimates.

STILTS: 1 m posts on the layout's 4 m grid, from the lake bed 4 m down to the deck's underside; tarred rim beams under the edges.
"""
A.save('laketown_research.json', NOTES, 'r-claude-laketown-research-3')
