"""Shared helpers for the Laketown detail blueprints: 0.5 m plans drawn in the layout's own coordinates
(doc `laketown`), each with its corner at (OX, OY) so it stamps straight back into the site plan.

    A = Area('Laketown: smithy (detail)', ox=10, oy=32, w=48, h=48)
    mid = A.level('mid', 'Smithy deck (+4 m)', 4, 4)
    A.R(mid, 12, 40, 44, 70, 'b')          # layout metres
    A.save('laketown_smithy.json', NOTES, 'r-claude-laketown-smithy-1')

Conventions carried over from the main square (laketown_square.py, which predates this module):
- walkways are 6 m of rough wood at +3 m with a wooden railing (newel posts at the ends) just outside each edge;
- short stairs get 2 m Fancy Stone cheek walls just outside their sides; long ones stepped flanks;
- stilts are 1 m posts on the layout's 4 m grid down to the lake bed 4 m below the surface;
- roofs rise in even steps (pitch 1 = 45 degrees, or 0.5);
- doors and windows are placed items at their measured sizes; furniture uses real item names.
"""
import math
import os
import re
from mage_common import Plan, PALETTE, ROOF_MATS

BED = -4                                                # the lake bed, 4 m below the surface
ALTAR = (80, 80, 4, 160)                                # the Flame Altar: centre (layout metres), its level's floor, build area
STONE, WOOD = '#92908c', '#75675f'

# Shared palette entries; each blueprint adds its own on top. Catalogue names and colours (blocks.js).
BASE_PALETTE = {
    '~': {'name': 'Water', 'kind': 'water', 'color': '#3f6f8f'},
    'w': {'name': 'Rough Wood Block', 'kind': 'floor', 'color': '#7a6653'},           # walkways, landings
    'r': {'name': 'Refined Wood Block', 'kind': 'floor', 'color': WOOD},              # floors indoors
    't': {'name': 'Tarred Wood Block', 'kind': 'floor', 'color': '#5d5652'},          # deck edges
    'f': {'name': 'Fancy Stone Block', 'kind': 'floor', 'color': STONE},
    'P': {'name': 'Highly Polished Stone Block', 'kind': 'floor', 'color': '#b3b0a9'},  # the manor
    'G': {'name': 'Fertile Springlands Dirt', 'kind': 'floor', 'color': '#95b261'},   # lawns
    'i': {'name': 'Refined Wood Block (rail)', 'kind': 'block', 'color': WOOD, 'height': 1},
    'u': {'name': 'Refined Wood Block (newel post)', 'kind': 'block', 'color': WOOD, 'height': 1.5},
    '1': {'name': 'Fancy Stone Block (stair flank)', 'kind': 'wall', 'color': STONE, 'height': 2},
    '2': {'name': 'Fancy Stone Block (stair flank)', 'kind': 'wall', 'color': STONE, 'height': 3},
    '3': {'name': 'Fancy Stone Block (stair flank)', 'kind': 'wall', 'color': STONE, 'height': 4},
    '4': {'name': 'Fancy Stone Block (stair flank)', 'kind': 'wall', 'color': STONE, 'height': 5},
}
ROOF_MATS.setdefault('straw', ('Straw Roof Block', '#a7753d'))
ROOF_MATS.setdefault('tarstraw', ('Tarred Straw Block', '#3b4457'))
ROOF_MATS.setdefault('cornice', ('Fancy Stone Block', STONE))      # stone eaves and ridges
ROOF_MATS.setdefault('fiber', ('Plant Fiber Roof Block', '#725e4f'))   # like wooden shingles
ROOF_MATS.setdefault('tarwood', ('Tarred Wood Block', '#5d5652'))      # a boat's hull
ROOF_MATS.setdefault('wood', ('Refined Wood Block', WOOD))            # a keel

TALL = {'Wooden Door': 2.5, 'Crude Wooden Door': 2.5, 'Round Wooden Door': 3, 'Wooden Double Door': 3.5}  # measured
TALL.update({'Carved Wooden Door': 2.5, 'Carved Wooden Double Door': 3.5, 'Metal Bound Wooden Double Door': 3.5})  # estimates (the plain ones' sizes) until measured
TALL['Steel Portcullis'] = 6                            # measured by the user: 6 m tall, 3 m wide
TALL['Ancients Night Door'] = 3.5                       # an estimate (the double door's) until measured
WIN = {'Wooden Window Frame': 1.5, 'Round Wooden Window Frame': 1, 'Large Round Wooden Window Frame': 3}
WIN.update({'Carved Wooden Window Frame I': 1.5, 'Round Carved Window Frame': 1})                          # estimates until measured
# Furniture and lights by real name: (w along the front, d deep, h) in metres, estimates until measured.
ITEM = {
    'Brazier': (1, 1, 1), 'Bench': (2, 0.5, 0.5), 'Ground Lantern II': (0.5, 0.5, 2), 'Wall Lantern': (0.5, 0.5, 0.5),
    'Hanging Lantern': (0.5, 0.5, 0.5), 'Supply Sacks I': (1, 1, 1), 'Supply Sacks II': (1, 1, 1),
    'Resource Bundle I': (1, 1, 1), 'Resource Bundle II': (1, 1, 1), 'Scrappy Crate': (1, 1, 1),
    'Stone Fireplace': (2, 1, 1.5), 'Fireplace': (2, 1, 1.5), 'Wooden Tavern Counter': (2, 1, 1),
    'Wooden Banquet Table': (3, 1, 1), 'Rustic Chair': (1, 1, 1), 'Wooden Sink': (2, 1, 1),
    'Wooden Side Table': (1, 1, 1), 'Rustic Bench': (2, 0.5, 0.5),
    'Sword and Shield Rack': (2, 0.5, 2), 'Two-Handed Melee Weapon Rack': (2, 0.5, 2), 'Shield Rack': (1, 0.5, 2),
    'Embervale Miniature Showcase': (2, 1, 1.5), 'Mannequin "Strike A Pose"': (1, 1, 2), 'Mannequin "Victory"': (1, 1, 2),
    'Mannequin "Look At Me"': (1, 1, 2), 'Mannequin "Here I Come"': (1, 1, 2), 'Carved Wooden Shelf': (2, 0.5, 2),
    'Large Carved Wooden Cabinet': (2, 1, 2), 'Carved Wooden Nightstand': (1, 1, 1), 'Wooden Lavatory': (1, 1, 1),
    'Crude Wooden Closet': (2, 1, 2), 'Crude Wooden Nightstand': (1, 1, 1), 'Low Crude Wooden Shelf': (2, 0.5, 1),
    'High Crude Wooden Shelf': (2, 0.5, 2), 'Crude Wooden Stool': (0.5, 0.5, 0.5), 'Ceiling Lantern': (1, 1, 1),
    'Dog Pillow': (1, 1, 0.5), 'Dog Bowl': (0.5, 0.5, 0.5), 'Cat Pillow': (1, 1, 0.5), 'Cat Bowl': (0.5, 0.5, 0.5),
    'Scrap Vat I': (1, 1, 1), 'Plough': (2, 1, 1),
    'Decoration Workbench': (2, 2, 1), 'Sparkworks Workbench': (2, 2, 1),      # 1.0 stations: 2 x 2 m placeholders
    'Wooden Cup': (0.5, 0.5, 0.5), 'Wooden Bowl': (0.5, 0.5, 0.5), 'Crude Wooden Jug': (0.5, 0.5, 0.5), 'Kettle': (0.5, 0.5, 0.5),
    'Construction Hammer': (1, 0.5, 0.5), 'Big Straw Mat': (2, 2, 0.5), 'Straw Mat': (1, 2, 0.5), 'Crude Wooden Side Table': (1, 1, 1),
    'Scrap Pot I': (0.5, 0.5, 0.5), 'Scrap Pot II': (0.5, 0.5, 0.5),
    'Bow Weapon Rack': (2, 0.5, 2), 'Staff Weapon Rack': (2, 0.5, 2), 'Scrap Bucket': (0.5, 0.5, 0.5),
    # the farm (1.0, the Farmer's; sizes unpublished, estimates until measured; the Beehive is a station, so 2 x 2 m)
    'Beehive': (2, 2, 1), 'Farm Animal Pillow': (1, 1, 0.5), 'Big Farm Animal Pillow': (2, 2, 0.5),
    'Goat Feeder': (2, 1, 1), 'Yak Feeder': (2, 1, 1), 'Bird Feeder': (1, 1, 1),
    'Crude Wooden Gate I': (2, 0.5, 1.5),
    # the research hall (1.0, the Ancient Researcher's and the Alchemist's; sizes unpublished: stations 2 x 2 m)
    'Infusion Altar': (2, 2, 1.5), 'Ancient Workbench': (2, 2, 1), 'Placeable Gem Forge': (2, 2, 1.5), 'Mill': (2, 2, 2),
    'Large Water Wheel': (5, 1, 5),
    'Large Grandleaf Cabbage Plant Pot': (1, 1, 1), 'Small Aurora Beans Plant Pot': (0.5, 0.5, 0.5),
    'Large Bloomheart Fruit Plant Pot I': (1, 1, 1), 'Small Prickle Pearl Plant Pot': (0.5, 0.5, 0.5),
    'Large Bloomheart Fruit Plant Pot II': (1, 1, 1),
    'Fish Trophy Board': (1, 0.5, 1),                   # the Fisher's (an estimate; it hangs on a wall)
    # the smokehouse (1.0 decorations from the Decoration Workbench; sizes unpublished, estimates until measured)
    'Fish Drying Rack': (2, 1, 2), 'Standing Wooden Barrel': (1, 1, 1), 'Lying Wooden Barrel': (1.5, 1, 1),
    'Half Wooden Barrel': (1, 1, 0.5), 'Wooden Crate': (1, 1, 1), 'Wooden Bucket': (0.5, 0.5, 0.5),
}
MOUNT = {'Wall Lantern': 'wall', 'Hanging Lantern': 'ceiling', 'Ceiling Lantern': 'ceiling', 'Fish Trophy Board': 'wall'}
# Library items by type: (name, w, d, h) as in the planner's LIBRARY (stations are 2 x 2 m placeholders)
LIB = {
    'mchest-large': ('Large Magic Chest', 2, 1, 1), 'quickstack': ('Quick Stack Station', 1, 1, 2),
    'chest-small': ('Small Chest', 1, 1, 1), 'chest-medium': ('Medium Chest', 1.5, 1, 1), 'chest-large': ('Large Chest', 2, 1, 1), 'bed': ('Bed', 2, 3, 1),
    'forge': ('Forge', 2, 2, 2), 'charcoal-kiln': ('Charcoal Kiln', 2, 2, 2.5), 'smelter': ('Smelter', 2, 2, 3),
    'blast-furnace': ('Blast Furnace', 2, 2, 4), 'smithing-tools': ('Smithing Tools', 2, 2, 1),
    'trough': ('Trough', 2, 1, 1), 'npc-blacksmith': ('Blacksmith', 3, 3, 2), 'npc-bard': ('Bard', 3, 3, 2),
    'npc-collector': ('Collector', 3, 3, 2), 'bed2': ('Double bed', 3, 3, 1), 'table': ('Table', 2, 1, 1),
    'bathtub': ('Bathtub', 2, 3, 1), 'ladder': ('Ladder', 1, 1, 4), 'seedbed': ('Seedbed', 2, 2, 0.5),
    'npc-carpenter': ('Carpenter', 3, 3, 2), 'npc-farmer': ('Farmer', 3, 3, 2), 'npc-alchemist': ('Alchemist', 3, 3, 2),
    'alchemy': ('Alchemy Station', 2, 2, 1.5), 'laboratory': ('Laboratory', 2, 2, 1.5), 'mortar': ('Mortar', 2, 2, 1),
    'grinding-stones': ('Grinding Stones', 2, 2, 1), 'npc-hunter': ('Hunter', 3, 3, 2), 'npc-fisher': ('Fisher', 3, 3, 2),
    'tannery': ('Tanning Station', 2, 2, 1.5), 'drying-rack': ('Drying Rack', 2, 2, 2), 'hand-spindle': ('Hand Spindle', 2, 2, 1),
    'loom': ('Loom', 2, 2, 2), 'spinning': ('Spinning Wheel', 2, 2, 1.5), 'spinning-machine': ('Spinning Machine', 2, 2, 2), 'npc-barber': ('Barber', 3, 3, 2), 'kiln': ('Kiln', 2, 2, 2), 'table-saw': ('Table Saw', 2, 2, 1),
    'masonry-tools': ('Masonry Tools', 2, 2, 1), 'workbench': ('Workbench', 2, 2, 1), 'chest-huge': ('Huge Chest', 2.5, 1.5, 1.5),
    'cooking-station': ('Cooking Station', 2, 2, 1.5), 'campfire': ('Campfire', 2, 2, 1), 'oven': ('Oven', 2, 2, 2), 'kitchen': ('Kitchen', 2, 2, 1.5),
}
LIB_COLOR = {'forge': '#6f6a66', 'charcoal-kiln': '#5f5550', 'smelter': '#7b5a4a', 'blast-furnace': '#6a4a3c',
             'smithing-tools': '#5a6066', 'npc-blacksmith': '#5f6770', 'trough': '#8a7550', 'campfire': '#c46a2a'}


class Area:
    def __init__(self, name, ox, oy, w, h, palette=None):
        self.P = Plan(name, 0.5, w, h, 160)
        self.P.project = 'Laketown'
        self.OX, self.OY = ox, oy
        PALETTE.clear()
        PALETTE.update(BASE_PALETTE)
        PALETTE.update(palette or {})

    # ---- levels and painting, in layout metres
    def level(self, lid, name, elev, height):
        return self.P.level(lid, name, elev, height)

    def R(self, g, x0, y0, x1, y1, ch):
        self.P.rect(g, x0 - self.OX, y0 - self.OY, x1 - self.OX, y1 - self.OY, ch)

    def sq(self, x, y):
        return self.P.sq(x - self.OX), self.P.sq(y - self.OY)

    def zone(self, lid, name, x0, y0, x1, y1, c):
        self.P.zone(lid, name, x0 - self.OX, y0 - self.OY, x1 - self.OX, y1 - self.OY, c)

    def deck(self, g, x0, y0, x1, y1, ch, edge=None, w=1):
        self.R(g, x0, y0, x1, y1, edge or ch)
        if edge:
            self.R(g, x0 + w, y0 + w, x1 - w, y1 - w, ch)

    def walls(self, g, x0, y0, x1, y1, ch, floor=None):
        """A building's outer walls, one block (0.5 m) thick, with a floor inside if given."""
        self.P.box_walls(g, x0 - self.OX, y0 - self.OY, x1 - self.OX, y1 - self.OY, ch, 0.5, floor)

    def overlay(self, g, x0, y0, x1, y1, name, color, height, base, kind='block'):
        """A raised piece over each square of x0..x1, y0..y1, keeping the floor (or roof) under it."""
        for x, y in self.P.cells_rect(x0 - self.OX, y0 - self.OY, x1 - self.OX, y1 - self.OY):
            self.P.overlay(g, x, y, name, color, height, base, kind)

    # ---- stairs, doors, windows, items
    def stairs(self, lid, label, x0, y0, x1, y1, rise, up):
        """Stairs over x0..x1, y0..y1 on the lower level, rising `rise` m towards `up`, no steeper than 45 degrees."""
        rot = {'N': 0, 'S': 180, 'E': 90, 'W': 270}[up]
        w, d = (x1 - x0, y1 - y0) if up in 'NS' else (y1 - y0, x1 - x0)
        assert d >= rise, (label, d, rise)
        self.P.item(lid, 'stairs', label, x0 - self.OX, y0 - self.OY, w, d, rise, rot, '#a98a62')

    def door(self, lid, name, x0, y0, x1, y1):
        self.P.opening(lid, name, x0 - self.OX, y0 - self.OY, x1 - self.OX, y1 - self.OY, TALL[name], 0, '#6b4a2e')

    def win(self, lid, name, x0, y0, x1, y1, z=1.0):
        """A window item in the wall squares x0..x1, y0..y1, its sill z metres above the level floor."""
        self.P.opening(lid, name, x0 - self.OX, y0 - self.OY, x1 - self.OX, y1 - self.OY, WIN[name], z)

    def put(self, lid, name, x, y, rot=0, z=None, label=None):
        """A catalogue item (by game name) or a library item (by type) with the top-left of its footprint at
        x, y (turned for rot 90 and 270). rot 0 faces south, 90 west, 180 north, 270 east."""
        if name in LIB:
            nm, w, d, h = LIB[name]
            typ, mount = name, None
            color = LIB_COLOR.get(name, '#7b68b5' if 'chest' in name else '#8c6b4f')
        else:
            (w, d, h), nm, typ = ITEM[name], name, re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')   # the planner's slug
            mount = MOUNT.get(name)
            color = {'wall': '#b08a4a', 'ceiling': '#c9a23a'}.get(mount, '#8a7a6a')
        if mount == 'ceiling' and z is None:
            z = next(L['height'] for L in self.P.levels if L['id'] == lid) - h
        return self.P.item(lid, typ, label or nm, x - self.OX, y - self.OY, w, d, h, rot, color, z=z, mount=mount)

    def spawn(self, lid, x, y, rot):
        """The Spawn point for walk mode (the planner's Walk button): a 1 x 1 m marker with its top-left at x, y,
        facing rot (0 south, 90 west, 180 north, 270 east), the way you look when you arrive."""
        return self.P.item(lid, 'spawn', 'Spawn point', x - self.OX, y - self.OY, 1, 1, 0.5, rot, '#2fa36b')

    # ---- roofs
    def roof(self, g):
        rf, ox, oy = self.P.roof(g), self.OX, self.OY

        class W:                                        # the Roof helper, in layout metres
            def gable(self, x0, y0, x1, y1, *a, **k): rf.gable(x0 - ox, y0 - oy, x1 - ox, y1 - oy, *a, **k)
            def hip(self, x0, y0, x1, y1, *a, **k): rf.hip(x0 - ox, y0 - oy, x1 - ox, y1 - oy, *a, **k)
            def shed(self, x0, y0, x1, y1, *a, **k): rf.shed(x0 - ox, y0 - oy, x1 - ox, y1 - oy, *a, **k)
            def dome(self, cx, cy, r, *a, **k): rf.dome(cx - ox, cy - oy, r, *a, **k)
            def cone(self, cx, cy, r, *a, **k): rf.cone(cx - ox, cy - oy, r, *a, **k)
            def cut_disc(self, cx, cy, r): rf.cut_disc(cx - ox, cy - oy, r)
            def lean_to(self, x0, y0, x1, y1, *a, **k): rf.lean_to(x0 - ox, y0 - oy, x1 - ox, y1 - oy, *a, **k)
            def cut(self, x0, y0, x1, y1): rf.cut(x0 - ox, y0 - oy, x1 - ox, y1 - oy)
            def caps(self, *a, **k): return rf.caps(*a, **k)
            def top(self, x, y): return rf.top(int(round((x - ox) * 2)), int(round((y - oy) * 2)))
            def eaves(self, mat, upto=0.5):
                """The eave course (every square no higher than `upto`) in another material: a stone cornice."""
                for k, h in rf.h.items():
                    if h <= upto + 1e-6:
                        rf.mat[k] = mat
            def shape(self, fn):
                """Reshape the roof square by square: fn(mx, my, h, mat), with the square's centre in layout
                metres, returns None to cut the square or (h, mat) to keep it (a hull's pointed bow, its keel)."""
                for k in list(rf.h):
                    r = fn(ox + (k[0] + 0.5) / rf.P.C, oy + (k[1] + 0.5) / rf.P.C, rf.h[k], rf.mat[k])
                    if r is None:
                        del rf.h[k]; rf.mat.pop(k, None)
                    else:
                        rf.h[k], rf.mat[k] = r
            def paint(self): rf.paint()
        return W()

    # ---- railings, cheeks, flanks
    def rail(self, g, x0, y0, x1, y1, gaps=()):
        """A wooden railing (1 m) along a straight edge, leaving `gaps` open, with a newel post (1.5 m) at the
        ends of each piece."""
        horiz = (x1 - x0) >= (y1 - y0)
        a0, a1 = (x0, x1) if horiz else (y0, y1)
        seg = lambda a, b, ch: self.R(g, a, y0, b, y1, ch) if horiz else self.R(g, x0, a, x1, b, ch)
        cur = a0
        for (g0, g1) in sorted(gaps) + [(a1, a1)]:
            if g0 > cur:
                seg(cur, g0, 'i'); seg(cur, cur + 0.5, 'u'); seg(g0 - 0.5, g0, 'u')
            cur = max(cur, g1)

    def parapet(self, g, x0, y0, x1, y1, gaps=(), every=4, wall='p', pier='o'):
        """A low stone wall along a straight edge (0.5 m thick), with piers at the ends of each piece and about
        every `every` metres, leaving `gaps` (spans along the run) open. `wall` and `pier` are palette symbols."""
        horiz = (x1 - x0) >= (y1 - y0)
        a0, a1 = (x0, x1) if horiz else (y0, y1)
        seg = lambda a, b, ch: self.R(g, a, y0, b, y1, ch) if horiz else self.R(g, x0, a, x1, b, ch)
        pieces, cur = [], a0
        for (g0, g1) in sorted(gaps):
            if g0 > cur:
                pieces.append((cur, g0))
            cur = max(cur, g1)
        if cur < a1:
            pieces.append((cur, a1))
        for s0, s1 in pieces:
            seg(s0, s1, wall)
            seg(s0, min(s0 + 1, s1), pier); seg(max(s1 - 1, s0), s1, pier)
            n = int((s1 - s0) // every)
            for i in range(1, n):
                c = round((s0 + (s1 - s0) * i / n) * 2) / 2
                seg(c - 0.5, c + 0.5, pier)

    def spiral(self, g, cx, cy, diam, height, name, color, start=0, rise=0.5):
        """A spiral stair on its own level g, one full turn over `height`, centred on (cx, cy) (layout metres):
        treads as raised blocks (`rise` each) clockwise from the compass bearing `start` (degrees from north),
        where you step on at the bottom and off at the top, round a newel. Stack one per storey with the same
        centre and start and they join up; cut the floor above out over the circle."""
        P, n, rs = self.P, max(4, round(height / rise)), diam / 2
        for x, y in P.cells_rect(cx - rs - self.OX, cy - rs - self.OY, cx + rs - self.OX, cy + rs - self.OY):
            mx, my = P.centre_m(x, y)
            dx, dy = mx - (cx - self.OX), my - (cy - self.OY)
            d = math.hypot(dx, dy)
            if d > rs:
                continue
            if d < 0.5:
                e = {'name': f'{name} (newel)', 'kind': 'wall', 'color': color, 'height': height}
            else:
                ang = (math.degrees(math.atan2(dx, -dy)) - start) % 360
                k = min(n - 1, int(ang / (360 / n)))
                e = {'name': f'{name} (tread)', 'kind': 'block', 'color': color, 'height': rise}
                if k:
                    e['base'] = k * rise
            g[y][x] = P._alloc(e)

    def circle(self, g, cx, cy, diam, ch):
        """Paint (or with ' ', clear) every square within diam/2 of (cx, cy)."""
        P, rs = self.P, diam / 2
        for x, y in P.cells_rect(cx - rs - self.OX, cy - rs - self.OY, cx + rs - self.OX, cy + rs - self.OY):
            mx, my = P.centre_m(x, y)
            if math.hypot(mx - (cx - self.OX), my - (cy - self.OY)) <= rs:
                g[y][x] = ch

    def ring(self, g, x0, y0, x1, y1, ch):
        """A course 0.5 m proud all round the rectangle x0..x1, y0..y1 (a chimney cap)."""
        self.R(g, x0 - 0.5, y0 - 0.5, x1 + 0.5, y1 + 0.5, ch); self.R(g, x0, y0, x1, y1, ' ')

    def rim_beams(self, stl, decks, keep=lambda x, y: True):
        """A course of tarred wood under each deck's floor course round its exposed edges, on the stilts level
        (posts take precedence). decks: (level id, elevation) pairs; keep(x, y) in layout metres limits it to
        this blueprint's own decks."""
        P, n = self.P, 0
        for lid, el in decks:
            beam = P._alloc({'name': f'Tarred Wood Block (rim beam, +{el} m)', 'kind': 'block', 'color': '#4e4844', 'height': 0.5, 'base': el - 1 - BED})
            g = P.grids[lid]
            for y in range(P.H):
                for x in range(P.W):
                    if g[y][x] == ' ' or stl[y][x] != ' ' or not keep(self.OX + x / 2, self.OY + y / 2):
                        continue
                    if any(0 <= x + dx < P.W and 0 <= y + dy < P.H and g[y + dy][x + dx] == ' ' for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                        stl[y][x] = beam; n += 1
        return n

    def cheeks(self, g, x0, y0, x1, y1, up, ch='1'):
        """Stone cheek walls either side of a short stair over x0..x1, y0..y1 rising towards `up`, just outside
        its sides."""
        if up in 'NS':
            self.R(g, x0 - 0.5, y0, x0, y1, ch); self.R(g, x1, y0, x1 + 0.5, y1, ch)
        else:
            self.R(g, x0, y0 - 0.5, x1, y0, ch); self.R(g, x0, y1, x1, y1 + 0.5, ch)

    def flanks(self, g, x0, y0, x1, y1, up, thick=0.5, steps=('1', '2', '3', '4')):
        """Stepped stone flanks either side of a 4 m stair over x0..x1, y0..y1 rising towards `up`: 2 m high at
        the foot, rising a metre every 2 m to 5 m at the top (1 m or more above the treads). For a 3 m stair
        pass steps=('1', '2', '3')."""
        n = len(steps)
        if up in 'NS':
            run = y1 - y0
            for k, ch in enumerate(steps):
                a = (y1 - (k + 1) * run / n, y1 - k * run / n) if up == 'N' else (y0 + k * run / n, y0 + (k + 1) * run / n)
                self.R(g, x0 - thick, a[0], x0, a[1], ch); self.R(g, x1, a[0], x1 + thick, a[1], ch)
        else:                                               # the foot is at x1 for a stair rising west, x0 rising east
            run = x1 - x0
            for k, ch in enumerate(steps):
                a = (x1 - (k + 1) * run / n, x1 - k * run / n) if up == 'W' else (x0 + k * run / n, x0 + (k + 1) * run / n)
                self.R(g, a[0], y0 - thick, a[1], y0, ch); self.R(g, a[0], y1, a[1], y1 + thick, ch)

    # ---- stilts and checks
    def stilts(self, stl, decks):
        """1 m posts (2 x 2 blocks) on the layout's 4 m grid under every deck level in `decks`
        ((level id, elevation) pairs, lowest first), plus wherever a narrow deck would otherwise be more than
        2 m from a post of its own. Each stands on the bed and stops under its deck."""
        P = self.P
        post_ch = {lid: P._alloc({'name': f'Tarred Wood Block (stilt to +{el} m)', 'kind': 'block', 'color': '#4e4844', 'height': el - 0.5 - BED})
                   for lid, el in decks}
        lowest = {}
        for lid, el in decks:
            g = P.grids[lid]
            for y in range(P.H):
                for x in range(P.W):
                    if g[y][x] != ' ':
                        lowest.setdefault((self.OX + x // 2, self.OY + y // 2), lid)
        posts = {m: lid for m, lid in lowest.items() if m[0] % 4 == 1 and m[1] % 4 == 1}
        for (mx, my), lid in sorted(lowest.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            if not any(posts.get((mx + dx, my + dy)) == lid for dx in range(-2, 3) for dy in range(-2, 3)):
                posts[(mx, my)] = lid
        for (mx, my), lid in posts.items():
            self.R(stl, mx, my, mx + 1, my + 1, post_ch[lid])
        return len(posts)

    def checks(self, outdoor_ok=('lake',), ignore_types=('stairs',)):
        """The item, access and altar checks. ignore_types: item types the item check leaves out (stairs, and
        anything that stands in the water by design, like a water wheel)."""
        P = self.P
        problems = P.check(outdoor_ok=outdoor_ok, ignore_types=ignore_types)
        print('item problems:', len(problems))
        for p_ in problems:
            print('  ', p_)
        access = P.check_access()
        print('access problems:', len(access))
        seen = {}
        for p_ in access:
            seen.setdefault(p_.split(' at ')[0] + ' / ' + p_.split(': ', 1)[1].split(' at ')[0][:60], []).append(p_)
        for k, v in seen.items():
            print(f'   [{len(v)}] {v[0]}')
        outside = P.altar_problems((ALTAR[0] - self.OX, ALTAR[1] - self.OY, ALTAR[2], ALTAR[3]))
        print("outside the altar's build volume:", len(outside))
        for p_ in outside:
            print('  ', p_)
        return problems, access

    def save(self, fn, notes, rev):
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), fn)
        print('bytes', self.P.save(out, notes, rev))
        for a, b in self.P.merged:
            print('  folded:', a, '->', b)
        print('palette', len(PALETTE))
