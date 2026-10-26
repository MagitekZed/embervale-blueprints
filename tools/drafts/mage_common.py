"""Shared helpers for the mage library drafts (site plan + detail plans).

Grids are lists of lists of single characters, indexed g[y][x] in squares.
Helpers take metres and convert with the plan's squares-per-metre (C).
"""
import base64, json, math, random, re, time, zlib
from collections import Counter

# Ancient & overgrown palette, shared by every mage library plan
PALETTE = {
    # Real blocks from the planner's block catalogue (enshrouded.wiki.gg names, icon-sampled colours)
    'A': {'name': 'Temple Stones', 'kind': 'wall', 'color': '#857f5d'},
    'S': {'name': 'Roughly Cut Stone Block', 'kind': 'wall', 'color': '#62605d'},
    'P': {'name': 'Highly Polished Stone Block', 'kind': 'wall', 'color': '#b3b0a9'},
    'U': {'name': 'Castle Roof Block', 'kind': 'wall', 'color': '#8b9987'},
    'R': {'name': 'Weathered Stone Block', 'kind': 'wall', 'color': '#6a6c67', 'height': 2},
    'w': {'name': 'Limestone Block', 'kind': 'block', 'color': '#a79a88', 'height': 1},
    'V': {'name': 'Moss', 'kind': 'block', 'color': '#92af22', 'height': 0.5},
    ',': {'name': 'Limestone Block', 'kind': 'floor', 'color': '#a79a88'},
    ';': {'name': 'Field Stones', 'kind': 'floor', 'color': '#8a8170'},
    '.': {'name': 'Refined Wood Block', 'kind': 'floor', 'color': '#75675f'},
    ':': {'name': 'Rocky Stone Road Block', 'kind': 'floor', 'color': '#84715f'},
    'h': {'name': 'Fertile Revelwood Dirt', 'kind': 'floor', 'color': '#7aa85e'},
    'f': {'name': 'Farm Soil', 'kind': 'floor', 'color': '#90450d'},
    'g': {'name': 'Blue Luminescent Block', 'kind': 'floor', 'color': '#6c9dc3'},
    'b': {'name': 'Rough Wood Block', 'kind': 'floor', 'color': '#7a6653'},
    # Not blocks: furniture placeholders, water, doors and windows
    'Y': {'name': 'Bookshelf wall (3 m)', 'kind': 'wall', 'color': '#7a5236', 'height': 3},
    'y': {'name': 'Bookshelf (2 m)', 'kind': 'block', 'color': '#8a6040', 'height': 2},
    '~': {'name': 'Water', 'kind': 'water', 'color': '#3f8fc1'},
    'D': {'name': 'Door', 'kind': 'door', 'color': '#6b4a2e'},
    'G': {'name': 'Great door', 'kind': 'door', 'color': '#4d3a2a'},
    'o': {'name': 'Window', 'kind': 'window', 'color': '#8fc3df'},
    'O': {'name': 'Arcane stained glass', 'kind': 'window', 'color': '#5fd0c0'},
    'q': {'name': 'Glass wall', 'kind': 'window', 'color': '#a9d8e6'},
}
FLOORS = set(',;.:hfgb')

# Roof materials for Roof shapes: key -> (catalogue name, colour). Each (material, height) pair becomes one
# palette symbol of kind 'roof', drawn from ROOF_POOL.
ROOF_MATS = {
    'castle': ('Castle Roof Block', '#8b9987'),
    'shingle': ('Stone Shingle Roof Block', '#7a7976'),
    'tiles': ('Roof Tiles Block', '#a37b69'),
    'ridge': ('Temple Stones', '#857f5d'),             # ridge caps, ribs and hips
    'rib': ('Roughly Cut Stone Block', '#62605d'),
    'glass': ('Glass roof', '#a9d8e6'),
    'glow': ('Blue Luminescent Block', '#6c9dc3'),
    'lead': ('Tarred Shingle Roof Block', '#6b6b66'),
    'moss': ('Drak Temple Roof Block', '#8a8a5a'),     # mossy patches
}
ROOF_POOL = '0123456789!$%&*+-/<=>?@^_`|{}[]()\'#IJKLMNQXZaceijklnprstuvxz'

# ---------------------------------------------------------------------------
# Palette symbols, as the planner keeps them. In memory a square holds one character, a palette key: keys
# 1 to 94 are the visible ASCII characters ! to ~ (so plans saved before numbered symbols keep theirs) and
# keys 95 to 999 are the characters from U+0100 on, which only live in memory. Saved plans (fmt 2) write
# every key as its number, 001 to 999, and every row as runs of numbers: "045x12,000x3,007" is twelve
# squares of symbol 45, three empty squares, then one of symbol 7.
MAX_SYMBOLS = 999
MAX_LEVELS = 200                                        # levels per plan (the planner's MAX_LEVELS)


def sym_code(k):
    c = ord(k)
    return c - 32 if c <= 126 else c - 0x100 + 95


def sym_char(n):
    return chr(n + 32) if n <= 94 else chr(0x100 + n - 95)


def encode_row(cells):
    """A row of palette keys (' ' for empty) as runs of three-digit symbol numbers."""
    out, i = [], 0
    while i < len(cells):
        j = i + 1
        while j < len(cells) and cells[j] == cells[i]:
            j += 1
        c = 0 if cells[i] == ' ' else sym_code(cells[i])
        out.append(f'{c:03d}' + (f'x{j - i}' if j - i > 1 else ''))
        i = j
    return ','.join(out)


def decode_row(s):
    """The palette keys of a row saved as runs (' ' for empty). A token it can't read raises ValueError."""
    out = []
    for tok in (s.split(',') if s else []):
        m = re.fullmatch(r'(\d{3})(?:x(\d{1,4}))?', tok)
        if not m:
            raise ValueError(f'unreadable run {tok!r}')
        c, n = int(m.group(1)), int(m.group(2) or 1)
        if c > MAX_SYMBOLS:
            raise ValueError(f'symbol {c} out of range')
        out.extend([' ' if c == 0 else sym_char(c)] * n)
    return out


# Big plans are stored packed (planner v37): everything but the fields below deflated (raw deflate, as the
# planner's pako does) into `z`, base64, with `zip: 1`. A database document is at most 256 KB, and plans like
# the Laketown site would not fit otherwise. The planner packs the same way when it saves.
PACK_OVER = 64000                                       # pack a plan whose compact JSON is longer than this
PACK_KEEP = ('v', 'fmt', 'name', 'project', 'w', 'h', 'cell', 'altar', 'rev', 'editor', 'updatedAt')


def compact_json(d):
    return json.dumps(d, ensure_ascii=False, separators=(',', ':'))


def pack_doc(d):
    """A plan document, packed if it's big."""
    if isinstance(d.get('z'), str) or len(compact_json(d)) <= PACK_OVER:
        return d
    out = {k: v for k, v in d.items() if k in PACK_KEEP}
    co = zlib.compressobj(9, zlib.DEFLATED, -15)
    z = co.compress(compact_json({k: v for k, v in d.items() if k not in PACK_KEEP}).encode('utf-8')) + co.flush()
    out['zip'] = 1
    out['z'] = base64.b64encode(z).decode('ascii')
    return out


def unpack_doc(d):
    """A plan document as it was before packing (unpacked ones come back as they are)."""
    if not isinstance(d.get('z'), str):
        return d
    rest = json.loads(zlib.decompress(base64.b64decode(d['z']), -15).decode('utf-8'))
    return {**rest, **{k: v for k, v in d.items() if k not in ('z', 'zip')}}


def load_doc(path):
    """A plan document from a JSON file (a generator's output or a database read), unpacked."""
    with open(path, encoding='utf-8') as f:
        return unpack_doc(json.load(f))


def doc_to_chars(doc):
    """A plan document (either format, packed or not) with its palette keyed, and its rows written, in single
    characters, as the generators work with them."""
    doc = unpack_doc(doc)
    if doc.get('fmt') != 2:
        return doc
    key = lambda k: sym_char(int(k))
    pal = {}
    for k, e in doc['palette'].items():
        e = dict(e)
        if 'under' in e:
            e['under'] = key(e['under'])
        pal[key(k)] = e
    levels = [{**L, 'rows': [''.join(decode_row(r)) for r in L.get('rows', [])]} for L in doc['levels']]
    out = {**doc, 'fmt': 1, 'palette': pal, 'levels': levels}
    t = doc.get('terrain')
    if t and t.get('enc') == 2:                             # ground rows as runs too
        out['terrain'] = {'ox': t.get('ox', 0), 'oy': t.get('oy', 0), 'rows': [''.join(decode_row(r)) for r in t.get('rows', [])]}
    return out


class Roof:
    """A sloped roof on one level, built from shapes and painted as 'roof' squares.

    Heights are metres above the level floor, at square centres (the planner's 'Top at'). Shapes combine by
    taking the higher roof in each square, so crossing wings meet in proper valleys. Set the roof level's
    floor at the wall tops: in the planner a roof square over a full-height wall below fills down to it, so
    gable ends close on their own. Heights snap to 0.5 m courses when painted.
    """
    def __init__(self, plan, g):
        self.P, self.g, self.h, self.mat = plan, g, {}, {}

    # -- building blocks
    def _rise(self, dist, pitch, base):
        """Height `dist` metres in from the eave square, in even steps so every step is the same width and can
        be built with the game's brushes: a whole number of courses per square (pitch 1 on a 0.5 m plan = 45
        degrees), or one course every whole number of squares (pitch 0.5 = one up per two across). A pitch
        between those (0.75 gives a mix of one- and two-wide steps) is rounded to the nearest even one."""
        cell = self.P.cell
        n = math.floor(dist / cell + 1e-6)                # whole squares in from the eave square
        per = pitch * cell / 0.5                          # courses gained per square
        if per >= 1:
            k = max(1, round(per)); used = k * 0.5 / cell
            step = n * k * 0.5
        else:
            m = max(1, round(1 / per)); used = 0.5 / (m * cell)
            step = (n // m) * 0.5
        if abs(used - pitch) > 1e-6 and pitch not in self.P._pitch_notes:
            self.P._pitch_notes.add(pitch)
            print(f'  roof pitch {pitch:g} steps unevenly on {cell:g} m squares: using {used:g}')
        return base + step

    def put(self, x, y, h, mat, mode='max'):
        if not (0 <= x < self.P.W and 0 <= y < self.P.H):
            return
        if mode == 'set' or h > self.h.get((x, y), -1e9):
            self.h[(x, y)] = h
            self.mat[(x, y)] = mat

    def _cells(self, x0, y0, x1, y1):
        for x, y in self.P.cells_rect(x0, y0, x1, y1):
            yield (x, y) + self.P.centre_m(x, y)

    def gable(self, x0, y0, x1, y1, ridge, mat, pitch=1.0, overhang=0.5, base=0.5, ridge_h=None, end_overhang=None):
        """Gable over walls whose outer faces are x0..x1, y0..y1 (metres). ridge 'x' runs east-west, 'y'
        north-south. pitch is the rise per metre (1 = 45 degrees). The eaves overhang by `overhang` and their
        outer squares sit at `base`; the gable ends overhang by `end_overhang` (default: the same).
        ridge_h caps the height (a flat-topped ridge)."""
        eo = overhang if end_overhang is None else end_overhang
        ox, oy = (eo, overhang) if ridge == 'x' else (overhang, eo)
        X0, Y0, X1, Y1 = x0 - ox, y0 - oy, x1 + ox, y1 + oy
        half = 0.5 / self.P.C
        for x, y, mx, my in self._cells(X0, Y0, X1, Y1):
            d = min(my - Y0, Y1 - my) if ridge == 'x' else min(mx - X0, X1 - mx)
            h = self._rise(d - half, pitch, base)
            if ridge_h is not None:
                h = min(h, ridge_h)
            self.put(x, y, h, mat)

    def hip(self, x0, y0, x1, y1, mat, pitch=1.0, overhang=0.5, base=0.5, ridge_h=None):
        """Hipped roof (all four sides slope); on a square plan it's a pyramid."""
        X0, Y0, X1, Y1 = x0 - overhang, y0 - overhang, x1 + overhang, y1 + overhang
        half = 0.5 / self.P.C
        for x, y, mx, my in self._cells(X0, Y0, X1, Y1):
            d = min(my - Y0, Y1 - my, mx - X0, X1 - mx)
            h = self._rise(d - half, pitch, base)
            if ridge_h is not None:
                h = min(h, ridge_h)
            self.put(x, y, h, mat)

    def shed(self, x0, y0, x1, y1, high_side, mat, pitch=0.5, overhang=0.5, base=0.5):
        """A single slope over walls x0..x1, y0..y1 (metres) rising in even steps (see _rise) from its low
        eave towards `high_side` ('n', 's', 'e' or 'w'), overhanging by `overhang` all round."""
        X0, Y0, X1, Y1 = x0 - overhang, y0 - overhang, x1 + overhang, y1 + overhang
        half = 0.5 / self.P.C
        for x, y, mx, my in self._cells(X0, Y0, X1, Y1):
            d = {'n': Y1 - my, 's': my - Y0, 'e': mx - X0, 'w': X1 - mx}[high_side]
            self.put(x, y, self._rise(d - half, pitch, base), mat)

    def lean_to(self, x0, y0, x1, y1, high_side, h_high, h_low, mat):
        """A single slope from h_high along `high_side` ('n', 's', 'e' or 'w') down to h_low opposite."""
        for x, y, mx, my in self._cells(x0, y0, x1, y1):
            t = {'n': (my - y0) / (y1 - y0), 's': (y1 - my) / (y1 - y0),
                 'w': (mx - x0) / (x1 - x0), 'e': (x1 - mx) / (x1 - x0)}[high_side]
            self.put(x, y, h_high + (h_low - h_high) * t, mat)

    def cone(self, cx, cy, r, height, mat, overhang=0.0, base=0.5, flare=None):
        """Conical roof over a round wall of radius r. height is the rise from base to the tip.
        flare=(width_m, pitch): the outermost width_m (overhang included) is a shallower skirt,
        like a witch's hat brim."""
        R = r + overhang
        fw, fp = flare if flare else (0, 0)
        steep = (height - fw * fp) / max(0.01, R - fw)
        for x, y, mx, my in self._cells(cx - R, cy - R, cx + R, cy + R):
            d = math.hypot(mx - cx, my - cy)
            if d > R:
                continue
            k = R - d                                   # metres in from the eave
            h = base + (k * fp if k <= fw else fw * fp + (k - fw) * steep)
            self.put(x, y, h, mat)

    def dome(self, cx, cy, r, height, mat, base=0.5, rim=0.85):
        """Dome over a round wall of radius r, rising `height` above `base`. The profile is a slice of an
        ellipsoid trimmed at the rim (rim = how far down the curve the rim sits, 1 = a full hemisphere),
        so the edge has a finite slope instead of a vertical wall."""
        R = r / rim
        z0 = math.sqrt(max(0.0, 1 - rim * rim))
        for x, y, mx, my in self._cells(cx - r, cy - r, cx + r, cy + r):
            d = math.hypot(mx - cx, my - cy)
            if d > r:
                continue
            z = (math.sqrt(max(0.0, 1 - (d / R) ** 2)) - z0) / (1 - z0)
            self.put(x, y, base + height * z, mat)

    # -- trim
    def ribs(self, cx, cy, angles_deg, half_width_m, r_min, r_max, mat, proud=0.5):
        """Raise radial strips (dome ribs) by `proud` metres, in another material."""
        for (x, y), h in list(self.h.items()):
            if self.P.on_angle(x, y, cx, cy, angles_deg, half_width_m, r_min, r_max):
                self.put(x, y, h + proud, mat, 'set')

    def caps(self, mat, proud=0.0, min_h=0.0, min_lower=2):
        """Ridge and hip caps: squares with no higher neighbour and lower ones (ridges, hips, peaks). An
        even-width gable has a two-wide ridge, each square with only one lower neighbour: use min_lower=1."""
        hits = []
        for (x, y), h in self.h.items():
            if h < min_h:
                continue
            nb = [v for v in (self.h.get((x + dx, y + dy)) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) if v is not None]
            if not any(v > h + 1e-6 for v in nb) and sum(v < h - 1e-6 for v in nb) >= min_lower:
                hits.append((x, y, h))
        for x, y, h in hits:
            self.put(x, y, h + proud, mat, 'set')
        return hits

    def scatter(self, mat, density, seed, max_h=None, only=None):
        """Swap a random share of squares (below max_h, of material `only`) to another material: moss, patches."""
        rnd = random.Random(seed)
        for (x, y) in sorted(self.h):
            if (max_h is None or self.h[(x, y)] <= max_h) and (only is None or self.mat[(x, y)] == only) and rnd.random() < density:
                self.mat[(x, y)] = mat

    def cut_disc(self, cx, cy, r):
        """Remove the roof inside radius r (an oculus)."""
        for (x, y) in list(self.h):
            if self.P.dist(x, y, cx, cy) < r:
                self.h.pop((x, y)); self.mat.pop((x, y))

    def cut(self, x0, y0, x1, y1):
        """Remove the roof from a rectangle (collapsed bays, light wells, a roof garden)."""
        for x, y in self.P.cells_rect(x0, y0, x1, y1):
            self.h.pop((x, y), None); self.mat.pop((x, y), None)

    def top(self, x, y):
        return self.h.get((x, y))

    def paint(self, only=None):
        """Write the roof into its level grid (only over squares whose current symbol is in `only`, if set)."""
        for (x, y), h in self.h.items():
            if only is None or self.g[y][x] in only:
                self.g[y][x] = self.P.roof_symbol(self.mat[(x, y)], max(0.5, h))
        return self


def standable(c):
    """Can furniture stand in a square with this symbol? Floors, pieces raised over a floor, and FLOORS extras."""
    e = PALETTE.get(c, {})
    if c in FLOORS or e.get('kind') == 'floor':
        return True
    u = e.get('under')
    return bool(u) and (u in FLOORS or PALETTE.get(u, {}).get('kind') == 'floor')


# The Flame Altar's footprint in metres, measured in game (2026-10-15); its height is a guess.
ALTAR_W, ALTAR_D, ALTAR_H = 4, 4, 3


class Plan:
    def __init__(self, name, cell, w_m, h_m, altar):
        self.name, self.cell, self.altar = name, cell, altar
        self.C = int(round(1 / cell))
        self.W, self.H = int(w_m * self.C), int(h_m * self.C)
        self.levels, self.items, self.zones = [], [], []
        self.grids = {}
        self._roof_syms = {}
        self.terrain = None                                 # ground height per square in metres, or None (flat)
        self.merged = []                                    # (entry, merged into) when the palette ran out
        self.project = None                                 # the project the planner groups it in
        self._pitch_notes = set()                           # roof pitches rounded to even steps (printed once)

    # --- units
    def sq(self, m): return int(round(m * self.C))

    # --- levels
    def level(self, lid, name, elev, height, group=None):
        """A new level (its grid). `group` is the heading it's listed under in the planner (planner v45); without
        one it goes by the part of its name before a colon. Trim levels follow their main level."""
        g = [[' '] * self.W for _ in range(self.H)]
        self.levels.append({'id': lid, 'name': name, 'elev': elev, 'height': height, **({'group': group} if group else {})})
        self.grids[lid] = g
        return g

    # --- shapes (all in metres)
    def cells_rect(self, x0, y0, x1, y1):
        for y in range(max(0, self.sq(y0)), min(self.H, self.sq(y1))):
            for x in range(max(0, self.sq(x0)), min(self.W, self.sq(x1))):
                yield x, y

    def centre_m(self, x, y):
        return ((x + 0.5) / self.C, (y + 0.5) / self.C)

    def dist(self, x, y, cx, cy):
        mx, my = self.centre_m(x, y)
        return math.hypot(mx - cx, my - cy)

    def rect(self, g, x0, y0, x1, y1, ch, only=None):
        for x, y in self.cells_rect(x0, y0, x1, y1):
            if only is None or g[y][x] in only:
                g[y][x] = ch

    def disc(self, g, cx, cy, r, ch, only=None, r_in=0.0):
        for x, y in self.cells_rect(cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1):
            d = self.dist(x, y, cx, cy)
            if r_in <= d <= r and (only is None or g[y][x] in only):
                g[y][x] = ch

    def ring_wall(self, g, cx, cy, r, ch, thick_m, only=None):
        """Watertight round wall: cells inside radius r within `thick_m` of the edge (8-neighbour test)."""
        t = max(1, self.sq(thick_m))
        inside = lambda x, y: self.dist(x, y, cx, cy) <= r
        for x, y in self.cells_rect(cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1):
            if not inside(x, y):
                continue
            edge = any(not inside(x + dx, y + dy) for dx in range(-t, t + 1) for dy in range(-t, t + 1))
            if edge and (only is None or g[y][x] in only):
                g[y][x] = ch

    def box_walls(self, g, x0, y0, x1, y1, ch, thick_m, floor=None):
        t = self.sq(thick_m)
        for x, y in self.cells_rect(x0, y0, x1, y1):
            edge = x < self.sq(x0) + t or x >= self.sq(x1) - t or y < self.sq(y0) + t or y >= self.sq(y1) - t
            if edge:
                g[y][x] = ch
            elif floor:
                g[y][x] = floor

    def on_angle(self, x, y, cx, cy, angles_deg, half_width_m, r_min, r_max):
        """True if the cell lies within a radial strip at any of the given compass angles (0 = north, clockwise)."""
        mx, my = self.centre_m(x, y)
        dx, dy = mx - cx, my - cy
        d = math.hypot(dx, dy)
        if not (r_min <= d <= r_max):
            return False
        for a in angles_deg:
            ar = math.radians(a)
            ux, uy = math.sin(ar), -math.cos(ar)          # unit vector for the angle
            along = dx * ux + dy * uy
            across = abs(-dx * uy + dy * ux)
            if along > 0 and across <= half_width_m:
                return True
        return False

    def radial(self, g, cx, cy, angles_deg, half_width_m, r_min, r_max, ch, only=None):
        for x, y in self.cells_rect(cx - r_max - 1, cy - r_max - 1, cx + r_max + 1, cy + r_max + 1):
            if self.on_angle(x, y, cx, cy, angles_deg, half_width_m, r_min, r_max) and (only is None or g[y][x] in only):
                g[y][x] = ch

    def lining(self, g, wall_chars, ch, only, x0=0, y0=0, x1=None, y1=None):
        """Cells in `only` that touch a wall cell (8-neighbour) become `ch`: a continuous one-block lining."""
        x1 = self.W if x1 is None else x1; y1 = self.H if y1 is None else y1
        hits = []
        for y in range(max(0, y0), min(self.H, y1)):
            for x in range(max(0, x0), min(self.W, x1)):
                if g[y][x] in only and any(0 <= x + dx < self.W and 0 <= y + dy < self.H and g[y + dy][x + dx] in wall_chars
                                           for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                    hits.append((x, y))
        for x, y in hits:
            g[y][x] = ch

    def gable_roofs(self, g, wings, course_chars, infill_chars, pitch=0.75, overhang=0.0):
        """Stepped gable roofs over one or more wings, meeting as cross-gables where they overlap.

        wings: [(x0, y0, x1, y1, ridge)] in metres; ridge 'x' runs east-west, 'y' runs north-south.
        Each square gets the highest course of any wing over it (so crossing wings form valleys).
        course_chars[i] must be a block raised i * 0.5 m (0.5 m thick); infill_chars[i] a solid block
        (i + 1) * 0.5 m tall, used under the courses along the outer walls (gable ends).
        Returns {(x, y): raise_in_metres} for later use (chimneys, dormers, roof upgrades).
        """
        half = 1 / self.C
        raise_at = {}
        for (x0, y0, x1, y1, ridge) in wings:
            for x, y in self.cells_rect(x0 - overhang, y0 - overhang, x1 + overhang, y1 + overhang):
                mx, my = x / self.C, y / self.C
                d = (min(my - y0, y1 - (my + half)) if ridge == 'x' else min(mx - x0, x1 - (mx + half))) + overhang
                step = max(0, min(len(course_chars) - 1, int(max(d, 0) * pitch / 0.5)))
                if step * 0.5 > raise_at.get((x, y), -1):
                    raise_at[(x, y)] = step * 0.5
        inside = lambda x, y: (x, y) in raise_at
        for (x, y), r in raise_at.items():
            step = int(r / 0.5)
            g[y][x] = course_chars[step]
        for (x, y), r in raise_at.items():                        # gable infill on the outer edge
            if r > 0 and any(not inside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                step = int(r / 0.5)
                g[y][x] = infill_chars[min(step, len(infill_chars) - 1)]   # solid up to the top of the course
        return raise_at

    # --- terrain: ground height per square, in whole blocks (the planner's ground tool)
    def _ground(self):
        if self.terrain is None:
            self.terrain = [[0.0] * self.W for _ in range(self.H)]
        return self.terrain

    def ground_at(self, x, y):
        return self.terrain[y][x] if self.terrain is not None and 0 <= x < self.W and 0 <= y < self.H else 0.0

    def ground_rect(self, x0, y0, x1, y1, h, mode='set'):
        """Set the ground in a rectangle (metres) to h. mode 'max' only raises, 'min' only lowers."""
        t = self._ground()
        for x, y in self.cells_rect(x0, y0, x1, y1):
            t[y][x] = h if mode == 'set' else max(t[y][x], h) if mode == 'max' else min(t[y][x], h)

    def ground_disc(self, cx, cy, r, h, mode='set', r_in=0.0):
        t = self._ground()
        for x, y in self.cells_rect(cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1):
            d = self.dist(x, y, cx, cy)
            if r_in <= d <= r:
                t[y][x] = h if mode == 'set' else max(t[y][x], h) if mode == 'max' else min(t[y][x], h)

    def ground_fn(self, fn, x0=0, y0=0, x1=None, y1=None, mode='set'):
        """Ground from a function of square-centre metres; None leaves a square alone. Snapped to whole blocks."""
        t = self._ground()
        for x, y in self.cells_rect(x0, y0, x1 if x1 is not None else self.W / self.C, y1 if y1 is not None else self.H / self.C):
            v = fn(*self.centre_m(x, y))
            if v is None:
                continue
            v = round(v / self.cell) * self.cell
            t[y][x] = v if mode == 'set' else max(t[y][x], v) if mode == 'max' else min(t[y][x], v)

    def _terrain_doc(self):
        if self.terrain is None or not any(v for row in self.terrain for v in row):
            return None
        rows = [[' ' if not v else chr(max(33, min(126, 79 + round(v / self.cell)))) for v in row] for row in self.terrain]
        ys = [y for y in range(self.H) if any(c != ' ' for c in rows[y])]
        x0 = min(next(x for x, c in enumerate(rows[y]) if c != ' ') for y in ys)
        # rows of runs like the level rows (enc 2, since planner v36)
        return {'enc': 2, 'ox': x0, 'oy': ys[0], 'rows': [encode_row(list(''.join(rows[y][x0:]).rstrip())) for y in range(ys[0], ys[-1] + 1)]}

    # --- sloped roofs (the planner's 'roof' kind)
    def roof(self, g):
        """Start a sloped roof on level grid g. See Roof."""
        return Roof(self, g)

    def roof_symbol(self, mat, h):
        """Palette symbol for a roof square of material `mat` (a ROOF_MATS key) with its top h metres above the level floor."""
        h = math.floor(h * 2 + 0.5) / 2                 # nearest 0.5 m course, halves round up
        key = (mat, h)
        if key in self._roof_syms:
            return self._roof_syms[key]
        name, color = ROOF_MATS[mat]
        ch = self._alloc({'name': f'{name} {h:g} m'[:40], 'kind': 'roof', 'color': color, 'height': h})
        self._roof_syms[key] = ch
        return ch

    def _alloc(self, entry, fallback=True):
        """A palette symbol for this entry: an existing identical one, or a fresh unused character.
        Past the 94 printable characters it hands out stand-ins that compact() folds away when saving."""
        for k, v in PALETTE.items():
            if v == entry:
                return k
        # (symbols painted without a palette entry are rare, so the grids are only scanned for them once,
        # and again when the pool runs out)
        if getattr(self, '_live', None) is None:
            self._live = set(c for gg in self.grids.values() for r in gg for c in r) - {' '}
        used = set(PALETTE) | self._live
        bad = ' \\"'
        pool = ROOF_POOL + ''.join(chr(i) for i in range(33, 127)) + ''.join(sym_char(n) for n in range(95, MAX_SYMBOLS + 1))
        ch = next((c for c in pool if c not in used and c not in bad), None)
        if ch is None:                                      # reuse a symbol nothing in this plan uses
            live = set(c for gg in self.grids.values() for r in gg for c in r) - {' '}
            ch = next((c for c in PALETTE if c not in live and c not in bad and ord(c) < 127), None)
        if ch is None:
            if not fallback:
                raise RuntimeError('out of palette symbols')
            ch = next(chr(0xE000 + k) for k in range(6000) if chr(0xE000 + k) not in PALETTE)
        PALETTE[ch] = entry
        return ch

    def compact(self, limit=MAX_SYMBOLS - 9):            # (a few spare for edits made in the planner)
        """Fit the palette in `limit` printable symbols: fold the entries that matter least into their
        nearest relative (a roof into the same roof a course higher or lower, a wall into a similar wall),
        then give stand-in symbols real characters. Records each fold in self.merged."""
        count = Counter(c for gg in self.grids.values() for r in gg for c in r if c != ' ')
        for c in list(count):                               # pieces over a floor or roof need that symbol too
            u = PALETTE.get(c, {}).get('under')
            if u:
                count[u] += 0
        strip = lambda n: re.sub(r'\s+[\d.]+ m$', '', n)
        material = lambda n: re.sub(r'\s*\(.*\)$', '', strip(n))     # "Fancy Stone Block (pier)" -> "Fancy Stone Block"
        def cost(a, b):
            ea, eb = PALETTE[a], PALETTE[b]
            if ea['kind'] != eb['kind'] or ea.get('under') != eb.get('under'):
                return 1e9
            ca, cb = int(ea['color'][1:], 16), int(eb['color'][1:], 16)
            dc = sum(abs(((ca >> k) & 255) - ((cb >> k) & 255)) for k in (16, 8, 0)) / 255
            dh = abs(ea.get('height', 0) - eb.get('height', 0)) + abs(ea.get('base', 0) - eb.get('base', 0))
            if strip(ea['name']) == strip(eb['name']):
                return dh                                   # the same piece a course or two off
            if material(ea['name']) == material(eb['name']):
                return dh + 1                               # the same material, another piece (a column into a pier)
            return dh + 8 + 4 * dc                          # another material: only when nothing closer is left
        remap = {}
        while len(count) > limit:
            best = None
            for a in count:
                for b in count:
                    if a != b:
                        c_ = count[a] * cost(a, b) if count[a] else 0
                        if best is None or c_ < best[0]:
                            best = (c_, a, b)
            _, a, b = best
            self.merged.append((PALETTE[a]['name'], PALETTE[b]['name']))
            remap[a] = b
            count[b] += count.pop(a)
            for k in list(remap):
                if remap[k] == a:
                    remap[k] = b
        if remap:
            for gg in self.grids.values():
                for r in gg:
                    for i, c in enumerate(r):
                        if c in remap:
                            r[i] = remap[c]
            for c in count:
                u = PALETTE[c].get('under')
                if u in remap:
                    PALETTE[c] = {**PALETTE[c], 'under': remap[u]}
        # stand-ins -> free printable characters
        stand = [c for c in count if ord(c) >= 0xE000]     # stand-ins past the 999 symbols
        if stand:
            free = [c for c in [chr(i) for i in range(33, 127)] + [sym_char(n) for n in range(95, MAX_SYMBOLS + 1)] if c not in count and c not in ' \\"']
            ren = dict(zip(stand, free))
            for gg in self.grids.values():
                for r in gg:
                    for i, c in enumerate(r):
                        if c in ren:
                            r[i] = ren[c]
            for old, new in ren.items():
                PALETTE[new] = PALETTE[old]
            for c in set(count) - set(stand) | set(ren.values()):
                u = PALETTE[c].get('under')
                if u in ren:
                    PALETTE[c] = {**PALETTE[c], 'under': ren[u]}

    # --- plan in plan
    def stamp(self, doc, ox, oy, tag, label=None):
        """Place another plan (a plan document) into this one, its north-west corner at (ox, oy) metres.

        Coarser squares than the source: each square takes the main piece under it. Walls, doors and
        windows always survive (doors first, then windows), so buildings stay closed and keep their
        openings. Anything else goes by majority, so scattered moss doesn't thicken, with ties going to
        raised pieces, then roofs, water and floors. Roof heights are averaged over the square and rounded
        to the square size. Finer squares: each source square is split. Levels match on elevation and
        height, or are added. Items and areas come along, scaled. Returns {source level id: target level id}.
        """
        doc = doc_to_chars(doc)
        sc, tc = doc['cell'], self.cell
        spal = doc['palette']
        sw, sh = doc['w'], doc['h']
        label = label or tag
        strip = lambda n: re.sub(r'\s+[\d.]+ m$', '', n)
        cache = {}

        def target_entry(c, hs, hd, top):
            e = dict(spal[c])
            if e['kind'] == 'roof':
                h = top if top is not None else e.get('base', 0) + e.get('height', sc)
                h = max(tc, round(h / tc) * tc)
                e = {'name': f"{strip(e['name'])} {h:g} m"[:40], 'kind': 'roof', 'color': e['color'], 'height': h}
            elif e['kind'] in ('wall', 'door', 'window') and 'height' not in e and abs(hs - hd) > 0.01:
                e['height'] = hs                            # keep its own storey height in a taller or shorter level
            if 'under' in e:
                if e['under'] in spal:
                    e['under'] = map_char(e['under'], hs, hd, None)
                else:
                    del e['under']
            return e

        def map_char(c, hs, hd, top):
            key = (c, hs, hd, top)
            if key not in cache:
                cache[key] = self._alloc(target_entry(c, hs, hd, top), fallback=True)
            return cache[key]

        def roof_top(c):
            e = spal.get(c)
            if e and e['kind'] != 'roof' and e.get('under') in spal:
                e = spal[e['under']]
            return e.get('base', 0) + e.get('height', sc) if e and e['kind'] == 'roof' else None

        pri = {'block': 3, 'roof': 2, 'water': 1, 'floor': 0}

        level_count = Counter()
        def pick(chars):
            ents = [c for c in chars if c != ' ' and c in spal]
            if not ents:
                return None, None
            for kd in ('door', 'window', 'wall'):
                hits = [c for c in ents if spal[c]['kind'] == kd]
                if hits:
                    return Counter(hits).most_common(1)[0][0], None
            if len(ents) * 2 < len(chars):
                return None, None
            cnt = Counter(ents)
            best = max(cnt, key=lambda c: (cnt[c], pri.get(spal[c]['kind'], 0), level_count[c]))
            tops = [t for t in (roof_top(c) for c in ents) if t is not None]
            return best, (sum(tops) / len(tops) if tops and spal[best]['kind'] == 'roof' else None)

        lev_map = {}
        for L in doc['levels']:
            T = next((t for t in self.levels if abs(t['elev'] - L['elev']) < 0.01 and abs(t['height'] - L['height']) < 0.01), None)
            if T is None:
                self.level(f"{tag}-{L['id']}"[:24], f"{label}: {L['name']}"[:40], L['elev'], L['height'])
                T = self.levels[-1]
            lev_map[L['id']] = T['id']
            g = self.grids[T['id']]
            src = [[' '] * sw for _ in range(sh)]
            x0, y0 = L.get('ox', 0), L.get('oy', 0)
            for j, row in enumerate(L['rows']):
                for i, c in enumerate(row):
                    if 0 <= y0 + j < sh and 0 <= x0 + i < sw:
                        src[y0 + j][x0 + i] = c
            level_count.clear(); level_count.update(c for row in L['rows'] for c in row if c != ' ')
            tx0, ty0 = math.floor(ox / tc + 1e-9), math.floor(oy / tc + 1e-9)
            tx1, ty1 = math.ceil((ox + sw * sc) / tc - 1e-9), math.ceil((oy + sh * sc) / tc - 1e-9)
            for ty in range(max(0, ty0), min(self.H, ty1)):
                for tx in range(max(0, tx0), min(self.W, tx1)):
                    if tc >= sc:                            # the source squares under this square
                        i0, i1 = round((tx * tc - ox) / sc), round(((tx + 1) * tc - ox) / sc)
                        j0, j1 = round((ty * tc - oy) / sc), round(((ty + 1) * tc - oy) / sc)
                        chars = [src[j][i] if 0 <= i < sw and 0 <= j < sh else ' ' for j in range(j0, j1) for i in range(i0, i1)]
                    else:                                   # the source square under this square's centre
                        i, j = math.floor(((tx + 0.5) * tc - ox) / sc), math.floor(((ty + 0.5) * tc - oy) / sc)
                        chars = [src[j][i] if 0 <= i < sw and 0 <= j < sh else ' ']
                    c, top = pick(chars)
                    if c is not None:
                        g[ty][tx] = map_char(c, L['height'], T['height'], top)
        if doc.get('terrain') and doc['terrain'].get('rows'):
            t = doc['terrain'];  src_t = [[0.0] * sw for _ in range(sh)]
            for j, row in enumerate(t['rows']):
                for i, c in enumerate(row):
                    if c != ' ' and 0 <= t.get('oy', 0) + j < sh and 0 <= t.get('ox', 0) + i < sw:
                        src_t[t.get('oy', 0) + j][t.get('ox', 0) + i] = (ord(c) - 79) * sc
            tg = self._ground()
            for ty in range(max(0, math.floor(oy / tc)), min(self.H, math.ceil((oy + sh * sc) / tc))):
                for tx in range(max(0, math.floor(ox / tc)), min(self.W, math.ceil((ox + sw * sc) / tc))):
                    vals = [src_t[j][i] for j in range(round((ty * tc - oy) / sc), round(((ty + 1) * tc - oy) / sc))
                            for i in range(round((tx * tc - ox) / sc), round(((tx + 1) * tc - ox) / sc)) if 0 <= i < sw and 0 <= j < sh]
                    if vals and any(vals):
                        tg[ty][tx] = round(sum(vals) / len(vals) / tc) * tc
        f = sc / tc
        cell = lambda m: math.floor(m / tc + 0.5)           # metres -> squares, halves up (shared edges stay shared)
        taken = {}
        for it in self.items:
            rw, rd = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
            for y in range(it['y'], it['y'] + rd):
                for x in range(it['x'], it['x'] + rw):
                    taken[(it['level'], x, y)] = it['id']
        loose = ('stairs', 'spiral', 'tree', 'spire')
        def fits(lid, x0, y0, rw, rd, typ, ground):
            g = self.grids[lid]
            for y in range(y0, y0 + rd):
                for x in range(x0, x0 + rw):
                    if not (0 <= x < self.W and 0 <= y < self.H) or (lid, x, y) in taken:
                        return False
                    if typ not in loose and not (standable(g[y][x]) or (ground and g[y][x] == ' ')):
                        return False
            return True
        NUDGE = sorted(((dx, dy) for dx in range(-3, 4) for dy in range(-3, 4)), key=lambda d: (abs(d[0]) + abs(d[1]), abs(d[0])))
        # whatever furniture stood on in the source plan (its check passed) can carry it here too
        for it in doc.get('items', []):
            L = next((l for l in doc['levels'] if l['id'] == it['level']), None)
            T = next((t for t in self.levels if t['id'] == lev_map.get(it['level'])), None)
            if not L or not T:
                continue
            x0, y0 = L.get('ox', 0), L.get('oy', 0)
            rw, rd = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
            for y in range(it['y'], it['y'] + rd):
                for x in range(it['x'], it['x'] + rw):
                    j, i = y - y0, x - x0
                    if 0 <= j < len(L['rows']) and 0 <= i < len(L['rows'][j]):
                        k = (L['rows'][j][i], L['height'], T['height'], None)
                        if k in cache:
                            FLOORS.add(cache[k])
        for it in doc.get('items', []):
            n = dict(it)
            n['id'] = f"{tag}-{it['id']}"[:24]
            n['level'] = lev_map.get(it['level'], self.levels[0]['id'])
            rot = it['rot'] in (90, 270)
            fw, fd = (it['d'], it['w']) if rot else (it['w'], it['d'])      # footprint on the grid
            x0, y0 = cell(it['x'] * sc + ox), cell(it['y'] * sc + oy)
            x1, y1 = max(x0 + 1, cell((it['x'] + fw) * sc + ox)), max(y0 + 1, cell((it['y'] + fd) * sc + oy))
            if tc > sc and it.get('mount') in ('door', 'window'):   # stays in the square its (thin) wall went to
                if it['rot'] in (0, 180):
                    y0 = math.floor((it['y'] * sc + oy) / tc + 1e-9); y1 = y0 + 1
                else:
                    x0 = math.floor((it['x'] * sc + ox) / tc + 1e-9); x1 = x0 + 1
            rw, rd = x1 - x0, y1 - y0
            if tc > sc and it.get('mount') not in ('door', 'window'):   # simplified: nudge off thickened walls and neighbours
                ground = next(t for t in self.levels if t['id'] == n['level'])['elev'] <= 0
                for dx, dy in NUDGE:
                    if fits(n['level'], x0 + dx, y0 + dy, rw, rd, it['type'], ground):
                        x0, y0 = x0 + dx, y0 + dy
                        break
            n['x'], n['y'] = x0, y0
            n['w'], n['d'] = (rd, rw) if rot else (rw, rd)
            for y in range(y0, y0 + rd):
                for x in range(x0, x0 + rw):
                    taken[(n['level'], x, y)] = n['id']
            self.items.append(n)
        for z in doc.get('zones', []):
            n = dict(z)
            n['id'] = f"{tag}-{z['id']}"[:24]
            n['level'] = lev_map.get(z['level'], self.levels[0]['id'])
            n['x'], n['y'] = round((z['x'] * sc + ox) / tc), round((z['y'] * sc + oy) / tc)
            n['w'], n['h'] = max(1, round(z['w'] * f)), max(1, round(z['h'] * f))
            self.zones.append(n)
        return lev_map

    def overlay(self, g, x, y, name, color, height, base, kind='block'):
        """Put a raised piece in square (x, y) of grid g, keeping what was there (a floor or roof square)
        underneath it: vent posts and chimney caps over a roof, beams over paving."""
        e = {'name': name[:40], 'kind': kind, 'color': color, 'height': height}
        if base:
            e['base'] = base
        under = g[y][x]
        if under != ' ' and PALETTE.get(under, {}).get('kind') in ('floor', 'water', 'roof'):
            e['under'] = under
        g[y][x] = self._alloc(e)

    def clear_under_items(self, chars, repl):
        """Swap ground cover (e.g. moss) out from under furniture: repl(level_id, x, y) gives the replacement."""
        for it in self.items:
            g = self.grids[it['level']]
            w, d = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
            for y in range(it['y'], it['y'] + d):
                for x in range(it['x'], it['x'] + w):
                    if 0 <= x < self.W and 0 <= y < self.H and g[y][x] in chars:
                        g[y][x] = repl(it['level'], x, y)

    def scatter(self, g, x0, y0, x1, y1, ch, density, only, seed):
        rnd = random.Random(seed)
        for x, y in self.cells_rect(x0, y0, x1, y1):
            if g[y][x] in only and rnd.random() < density:
                g[y][x] = ch

    # --- items and zones (metres in, squares out)
    def item(self, lid, typ, label, x, y, w, d, h, rot=0, color='#8a7a6a', iid=None, z=None, mount=None):
        """An item, in metres. mount: None (on the floor), 'door' or 'window' (in a wall, cutting its opening:
        x, y, w, d cover the wall squares, w along the wall), 'wall' (hung on a wall face) or 'ceiling'. z is
        its bottom above the level floor (a window's sill, how high a wall item hangs)."""
        it = {'id': iid or f'i{len(self.items)}', 'level': lid, 'type': typ, 'label': label,
              'x': self.sq(x), 'y': self.sq(y), 'w': max(1, self.sq(w)), 'd': max(1, self.sq(d)), 'h': h, 'rot': rot, 'color': color}
        if z:
            it['z'] = z
        if mount:
            it['mount'] = mount
        self.items.append(it)
        return it

    def opening(self, lid, name, x0, y0, x1, y1, h, z=0, color=None):
        """A door or window item in a wall, over the wall squares x0..x1, y0..y1 (metres; one square thick):
        its type is the item's slug, it faces south (or west) unless turned in the planner."""
        horiz = (x1 - x0) >= (y1 - y0)
        mount = 'window' if 'window' in name.lower() else 'door'
        typ = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        w, d = (x1 - x0, y1 - y0) if horiz else (y1 - y0, x1 - x0)
        return self.item(lid, typ, name, x0, y0, w, d, h, 0 if horiz else 90,
                         color or ('#8fc3df' if mount == 'window' else '#6b4a2e'), iid=None, z=z or None, mount=mount)

    def zone(self, lid, name, x0, y0, x1, y1, color):
        self.zones.append({'id': f'z{len(self.zones)}', 'level': lid, 'name': name,
                           'x': self.sq(x0), 'y': self.sq(y0), 'w': self.sq(x1) - self.sq(x0), 'h': self.sq(y1) - self.sq(y0), 'color': color})

    # --- checks and output
    def check(self, outdoor_ok=('g0',), ignore_types=('stairs', 'spiral', 'tree')):
        """Items that stand on a wall, a hole or each other, or run into a raised piece over the floor (a lamp in a
        bracket). Doors and windows must sit in a wall instead, and items only clash where their heights overlap
        too (a shelf over a table, a lamp under a beam)."""
        problems, taken = [], {}
        for it in self.items:
            g = self.grids[it['level']]
            w, d = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
            mount = it.get('mount')
            z0 = it.get('z', 0); z1 = z0 + it['h']
            for y in range(it['y'], it['y'] + d):
                for x in range(it['x'], it['x'] + w):
                    if not (0 <= x < self.W and 0 <= y < self.H):
                        problems.append(f"{it['id']} off canvas"); continue
                    c = g[y][x]
                    if mount in ('door', 'window'):
                        if PALETTE.get(c, {}).get('kind') not in ('wall', 'block'):
                            problems.append(f"{it['id']} ({it['label']}) not in a wall at {x / self.C},{y / self.C} m")
                        for (oz0, oz1, oid) in taken.get((it['level'], x, y, 'wall'), []):
                            if oz0 < z1 and z0 < oz1:
                                problems.append(f"{it['id']} overlaps {oid} at {x / self.C},{y / self.C} m")
                        taken.setdefault((it['level'], x, y, 'wall'), []).append((z0, z1, it['id']))
                        continue
                    ok = standable(c) or (c == ' ' and it['level'] in outdoor_ok)
                    if self.terrain is not None and c == ' ' and it['type'] not in ignore_types:
                        gz, ez = self.terrain[y][x], next(L['elev'] for L in self.levels if L['id'] == it['level'])
                        if abs(gz - ez) > 0.01:
                            problems.append(f"{it['id']} ({it['label']}) {'buried' if gz > ez else 'floating'}: ground {gz:g} m, level {ez:g} m at {x / self.C},{y / self.C} m")
                    if not ok and it['type'] not in ignore_types:
                        problems.append(f"{it['id']} ({it['label']}) on '{c}' at {x / self.C},{y / self.C} m")
                    e = PALETTE.get(c, {})                  # a raised piece over the floor here (a bracket, a beam)
                    if ok and e.get('kind') == 'block' and it['type'] not in ignore_types:
                        b0 = e.get('base', 0) or 0
                        if b0 < z1 and z0 < b0 + (e.get('height') or 1):
                            problems.append(f"{it['id']} ({it['label']}) runs into {e['name']} at {x / self.C},{y / self.C} m")
                    key = (it['level'], x, y)
                    for (oz0, oz1, oid) in taken.get(key, []):
                        if oz0 < z1 and z0 < oz1:
                            problems.append(f"{it['id']} overlaps {oid} at {x / self.C},{y / self.C} m")
                    taken.setdefault(key, []).append((z0, z1, it['id']))
        return problems

    # --- access: what's in the way of doors, windows and stairs
    def _spans(self, x, y):
        """What's solid in square (x, y) on every level, as (bottom, top, name, level id) in absolute metres.
        Floor courses come back named 'floor'. Roof columns run down to a neighbour up to three courses lower,
        as the planner draws them."""
        out = []
        for L in self.levels:
            g, el = self.grids[L['id']], L['elev']
            c = g[y][x]
            if c == ' ':
                continue
            e = PALETTE.get(c, {})
            k, base = e.get('kind'), e.get('base', 0) or 0
            if k in ('wall', 'door', 'window'):
                out.append((el + base, el + base + (e.get('height') or max(self.cell, L['height'] - base)), e.get('name', c), L['id']))
            elif k == 'block':
                out.append((el + base, el + base + (e.get('height') or 1), e.get('name', c), L['id']))
            elif k == 'roof':
                top = el + e.get('height', 0.5)
                bot = top - 0.5
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if 0 <= x + dx < self.W and 0 <= y + dy < self.H:
                        n = PALETTE.get(g[y + dy][x + dx], {})
                        if n.get('kind') == 'roof':
                            nt = el + n.get('height', 0.5)
                            if top - 1.5 - 1e-6 <= nt < bot:
                                bot = nt
                out.append((bot, top, e.get('name', c), L['id']))
            if k in ('floor', 'water') or (k in ('block', 'wall') and e.get('under')):
                out.append((el - 0.5, el, 'floor', L['id']))
        return out

    def altar_problems(self, altar=None):
        """Squares and items outside the Flame Altar's build volume, as the planner draws it: a cube of the plan's
        altar size centred on each altar item's footprint, reaching half its size above and below its level's
        floor (players' reports; unconfirmed). `altar` = (x, y, z, size) in plan metres stands in when the plan
        has no altar item (a detail blueprint of a bigger site). Returns a summary per level."""
        lv = {L['id']: L for L in self.levels}
        vols = []
        for it in self.items:
            if it['type'] == 'altar':
                w, d = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
                vols.append(((it['x'] + w / 2) / self.C, (it['y'] + d / 2) / self.C, lv[it['level']]['elev'], self.altar))
        vols = vols or ([altar] if altar else [])
        if not vols:
            return []
        inside = lambda mx, my, z0, z1: any(abs(mx - cx) <= s / 2 and abs(my - cy) <= s / 2 and z0 >= cz - s / 2 - 0.01
                                            and z1 <= cz + s / 2 + 0.01 for cx, cy, cz, s in vols)
        out = Counter()
        for L in self.levels:
            g = self.grids[L['id']]
            for y in range(self.H):
                for x in range(self.W):
                    e = PALETTE.get(g[y][x]) if g[y][x] != ' ' else None
                    if not e:
                        continue
                    k = e['kind']
                    if k in ('floor', 'water'):
                        z0, z1 = -0.5, 0
                    elif k == 'roof':
                        z0, z1 = 0, e.get('base', 0) + e.get('height', self.cell)
                    else:
                        z0 = e.get('base', 0)
                        z1 = z0 + e.get('height', 1 if k == 'block' else L['height'])
                    if not inside((x + 0.5) / self.C, (y + 0.5) / self.C, L['elev'] + z0, L['elev'] + z1):
                        out[L['id']] += 1
        for it in self.items:
            if it['type'] != 'altar':
                w, d = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
                z = lv[it['level']]['elev'] + it.get('z', 0)
                if not inside((it['x'] + w / 2) / self.C, (it['y'] + d / 2) / self.C, z, z + it['h']):
                    out[f"{it['level']} (items)"] += 1
        return [f"{n} outside the altar's build volume on {lid}" for lid, n in out.items()]

    def check_access(self, head=2.0, clear=1.0):
        """Doors and windows with something in front of them or behind them, doors that open onto a drop, and
        stairs without `clear` metres of floor at the foot and the top or without `head` metres of headroom
        over the steps. Items count too, except stairs (they're the way through). Returns the problems."""
        probs, eps = [], 1e-6
        elev = {L['id']: L['elev'] for L in self.levels}
        occ = {}                                            # (x, y) -> [(bottom, top, label)] of items, absolute
        for it in self.items:
            if it.get('mount') in ('door', 'window') or it['type'] in ('stairs', 'spiral'):
                continue
            w, d = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
            z0 = elev[it['level']] + it.get('z', 0)
            for y in range(it['y'], it['y'] + d):
                for x in range(it['x'], it['x'] + w):
                    occ.setdefault((x, y), []).append((z0, z0 + it['h'], it['label']))

        def inb(x, y): return 0 <= x < self.W and 0 <= y < self.H

        def solid(x, y, z0, z1, floors=False):
            """Names of whatever fills square (x, y) between z0 and z1."""
            hit = [f"{n} ({lid})" for (b, t, n, lid) in self._spans(x, y) if (floors or n != 'floor') and b < z1 - eps and z0 < t - eps]
            return hit + [lab for (b, t, lab) in occ.get((x, y), []) if b < z1 - eps and z0 < t - eps]

        def floor_at(x, y, z):
            return any(n == 'floor' and abs(t - z) < 0.01 for (b, t, n, lid) in self._spans(x, y))

        m = lambda v: f'{v / self.C:g}'
        for it in self.items:
            mount = it.get('mount')
            if mount in ('door', 'window'):
                el = elev[it['level']]
                z = it.get('z', 0 if mount == 'door' else max(0.5, 2.5 - it['h']))
                z0, z1 = el + z, el + z + it['h']
                horiz = it['rot'] in (0, 180)
                w, d = (it['d'], it['w']) if not horiz else (it['w'], it['d'])
                for y in range(it['y'], it['y'] + d):
                    for x in range(it['x'], it['x'] + w):
                        for sx, sy in (((x, y - 1), (x, y + 1)) if horiz else ((x - 1, y), (x + 1, y))):
                            if not inb(sx, sy):
                                continue
                            hit = solid(sx, sy, z0, z1)
                            if hit:
                                probs.append(f"{it['label']} at {m(x)},{m(y)} ({it['level']}): {', '.join(sorted(set(hit)))} in front at {m(sx)},{m(sy)}")
                            elif mount == 'door' and not floor_at(sx, sy, z0):
                                probs.append(f"{it['label']} at {m(x)},{m(y)} ({it['level']}): no floor at {m(sx)},{m(sy)}")
            elif it['type'] == 'stairs':
                el, rise = elev[it['level']], it['h']
                fx, fy = {0: (0, 1), 90: (-1, 0), 180: (0, -1), 270: (1, 0)}[it['rot']]    # facing: towards the foot
                w, d = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
                sqs = [(x, y) for y in range(it['y'], it['y'] + d) for x in range(it['x'], it['x'] + w)]
                run = d if fy else w                        # squares from the foot to the top
                n = self.sq(clear)
                for (x, y) in sqs:
                    # distance from the foot edge, in squares (0 = the bottom tread)
                    k = {(0, 1): it['y'] + d - 1 - y, (0, -1): y - it['y'], (-1, 0): x - it['x'], (1, 0): it['x'] + w - 1 - x}[(fx, fy)]
                    step = el + min(rise, (math.floor(k * rise / 0.5 / run) + 1) * 0.5)
                    hit = solid(x, y, step, step + head, floors=True)
                    if hit:
                        probs.append(f"{it['label']}: headroom at {m(x)},{m(y)} ({', '.join(sorted(set(hit)))})")
                    if k == 0:                               # the foot: clear floor beyond it
                        for j in range(1, n + 1):
                            sx, sy = x + fx * j, y + fy * j
                            if inb(sx, sy) and (solid(sx, sy, el, el + head) or not floor_at(sx, sy, el)):
                                probs.append(f"{it['label']}: foot blocked at {m(sx)},{m(sy)} {solid(sx, sy, el, el + head) or 'no floor'}")
                    if k == run - 1:                         # the top: clear floor beyond it at the arrival height
                        for j in range(1, n + 1):
                            sx, sy = x - fx * j, y - fy * j
                            if inb(sx, sy) and (solid(sx, sy, el + rise, el + rise + head) or not floor_at(sx, sy, el + rise)):
                                probs.append(f"{it['label']}: top blocked at {m(sx)},{m(sy)} {solid(sx, sy, el + rise, el + rise + head) or 'no floor'}")
        return probs

    def grid_problems(self):
        """Heights that aren't whole 0.5 m blocks (the planner snaps them, so the plan wouldn't match)."""
        off = lambda v: abs(v * 2 - round(v * 2)) > 1e-6
        out = [f"level {L['id']} {k} {L[k]}" for L in self.levels for k in ('elev', 'height') if off(L[k])]
        out += [f"palette {k!r} {e['name']} {f} {e[f]}" for k, e in PALETTE.items() for f in ('height', 'base') if f in e and off(e[f])]
        out += [f"item {it['id']} {k} {it[k]}" for it in self.items for k in ('h', 'z') if k in it and off(it[k])]
        return out

    def to_json(self, notes, rev):
        if len(self.levels) > MAX_LEVELS:                   # the planner only loads the first MAX_LEVELS
            raise ValueError(f'{len(self.levels)} levels: a plan can have at most {MAX_LEVELS}')
        for p_ in self.grid_problems():
            print('  off the 0.5 m block grid:', p_)
        self.compact()                                      # fit the palette before writing any rows
        def crop(g):
            ys = [y for y in range(self.H) if any(c != ' ' for c in g[y])]
            if not ys:
                return 0, 0, []
            x0 = min(next(x for x, c in enumerate(g[y]) if c != ' ') for y in ys)
            return x0, ys[0], [encode_row(list(''.join(g[y][x0:]).rstrip())) for y in range(ys[0], ys[-1] + 1)]
        levels = []
        for L in self.levels:
            ox, oy, rows = crop(self.grids[L['id']])
            levels.append({**L, 'hidden': False, 'ox': ox, 'oy': oy, 'rows': rows})
        used = set(c for g in self.grids.values() for r in g for c in r if c != ' ')
        used |= set(PALETTE[c]['under'] for c in list(used) if PALETTE[c].get('under'))
        num = lambda k: f'{sym_code(k):03d}'
        palette = {}
        for k, v in PALETTE.items():
            if k in used:
                e = dict(v)
                if 'under' in e:
                    e['under'] = num(e['under'])
                palette[num(k)] = e
        return {
            'v': 1, 'fmt': 2, 'name': self.name, 'notes': notes, 'cell': self.cell, 'w': self.W, 'h': self.H, 'altar': self.altar,
            **({'project': self.project} if self.project else {}),
            'palette': palette,
            'levels': levels, 'items': self.items, 'zones': self.zones,
            **({'terrain': self._terrain_doc()} if self._terrain_doc() else {}),
            'rev': f'{rev}-{int(time.time())}', 'editor': 'claude', 'updatedAt': int(time.time() * 1000),  # fresh rev so open pages adopt it
        }

    def save(self, path, notes, rev):
        """Write the plan document (packed if it's big); returns its size in bytes, as the database counts it."""
        txt = compact_json(pack_doc(self.to_json(notes, rev)))
        open(path, 'w', encoding='utf-8').write(txt)
        return len(txt.encode('utf-8'))

    def preview(self, lid, step=1, x0=0, y0=0, x1=None, y1=None):
        g = self.grids[lid]
        x1 = x1 or self.W; y1 = y1 or self.H
        return '\n'.join(''.join(g[y][x] for x in range(x0, x1, step)).rstrip() for y in range(y0, y1, step))


# ---------------------------------------------------------------------------
# Carving in blocks: thick walls with recessed bays, deep reveals, niches, arches and vaults.
class Vox:
    """One level's walls and blocks as 0.5 m voxels, to carve depth into them.

    Vox(P, lid) takes over the level's wall and block squares (their floors, and the level's water and roofs,
    stay in its grid). put() fills voxels and cut() empties them, over a mask of squares and a height range
    in metres above the level floor (either can be an array, one value per square). emit() writes it back:
    each square's solid runs become wall pieces, the lowest on the level itself (over the square's floor,
    as `under`) and any others on trim levels at the same elevation ('<lid>_t1' and on, placed just after it
    in the level list), since a square holds one piece per level.

    Masks are boolean arrays over the canvas, rows y and columns x: build them from V.mx and V.my, the square
    centres in metres (rect(), disc() and ring() do the common ones).
    """
    VZ = 0.5

    def __init__(self, plan, lid):
        import numpy as np
        self.np, self.P, self.lid = np, plan, lid
        self.L = next(L for L in plan.levels if L['id'] == lid)
        self.height = self.L['height']
        self.nz = int(round(self.height / self.VZ))
        self.g = plan.grids[lid]
        self.a = np.zeros((self.nz, plan.H, plan.W), np.uint16)
        self.mats, self._mi = [None], {}
        ys, xs = np.mgrid[0:plan.H, 0:plan.W]
        self.mx, self.my = (xs + 0.5) / plan.C, (ys + 0.5) / plan.C
        self.zc = (np.arange(self.nz) + 0.5) * self.VZ        # voxel centres, metres above the level floor
        for y in range(plan.H):
            row = self.g[y]
            for x in range(plan.W):
                e = PALETTE.get(row[x]) if row[x] != ' ' else None
                if not e or e.get('kind') not in ('wall', 'block'):
                    continue
                b = e.get('base', 0) or 0
                h = e.get('height') or (self.height - b if e['kind'] == 'wall' else 1)
                self.a[self._k(b):self._k(b + h), y, x] = self.mat(e['name'], e['color'])
                row[x] = e.get('under') or ' '

    def _k(self, z):
        return max(0, min(self.nz, int(round(z / self.VZ))))

    def mat(self, name, color):
        """The index of a material (a block name and its colour)."""
        key = (name[:40], color)
        if key not in self._mi:
            self._mi[key] = len(self.mats)
            self.mats.append(key)
        return self._mi[key]

    # -- masks
    def rect(self, x0, y0, x1, y1):
        return (self.mx > x0) & (self.mx < x1) & (self.my > y0) & (self.my < y1)

    def disc(self, cx, cy, r, r_in=None):
        d = self.np.hypot(self.mx - cx, self.my - cy)
        return (d <= r) & (d > r_in) if r_in is not None else d <= r

    def ring(self, cx, cy, r, thick):
        return self.disc(cx, cy, r, r - thick)

    # -- filling and carving
    def put(self, mask, z0, z1, m, only=None):
        """Fill the voxels over `mask` between z0 and z1 (metres; scalars or one value per square) with material
        m, a (name, colour) pair or an index from mat() (0 empties them). only='solid' changes only voxels already filled (re-facing), 'air' only empty ones."""
        np = self.np
        if isinstance(m, tuple):
            m = self.mat(*m)
        z0 = np.broadcast_to(z0, mask.shape); z1 = np.broadcast_to(z1, mask.shape)
        for k in range(self.nz):
            sel = mask & (self.zc[k] > z0) & (self.zc[k] < z1)
            if only == 'solid':
                sel &= self.a[k] != 0
            elif only == 'air':
                sel &= self.a[k] == 0
            self.a[k][sel] = m

    def cut(self, mask, z0=0, z1=None):
        self.put(mask, z0, self.height if z1 is None else z1, 0)

    def solid(self, mask, z0, z1):
        """Is anything solid over the mask between z0 and z1?"""
        k0, k1 = self._k(z0), self._k(z1)
        return bool(self.a[k0:k1][:, mask].any())

    def floor(self, mask, sym, only=(' ',)):
        """Paint a floor symbol into the level's grid over the mask (where the grid holds one of `only`)."""
        np = self.np
        for y, x in zip(*np.nonzero(mask)):
            if self.g[y][x] in only or (only is None):
                self.g[y][x] = sym

    # -- writing it back
    def emit(self):
        """Write the voxels back into the level (and its trim levels) as wall pieces. Returns the trim levels used."""
        np, P = self.np, self.P
        filled = np.nonzero(self.a.any(axis=0))
        pieces = {}                                         # (y, x) -> [(k0, k1, m)]
        for y, x in zip(*filled):
            col = self.a[:, y, x]
            runs, k = [], 0
            while k < self.nz:
                m = col[k]
                if not m:
                    k += 1; continue
                k0 = k
                while k < self.nz and col[k] == m:
                    k += 1
                runs.append((k0, k, int(m)))
            pieces[(y, x)] = runs
        trims, sym = [], {}
        idx = P.levels.index(self.L)
        for (y, x), runs in pieces.items():
            for i, (k0, k1, m) in enumerate(runs):
                name, color = self.mats[m]
                e = {'name': name, 'kind': 'wall', 'color': color, 'height': (k1 - k0) * self.VZ}
                if k0:
                    e['base'] = k0 * self.VZ
                if i == 0:
                    u = self.g[y][x]
                    if u != ' ' and PALETTE.get(u, {}).get('kind') in ('floor', 'water', 'roof'):
                        e['under'] = u
                    g = self.g
                else:
                    while len(trims) < i:
                        n = len(trims) + 1
                        lid = f"{self.lid}_t{n}"
                        g_new = P.level(lid, f"{self.L['name']} · trim {n}", self.L['elev'], self.height)
                        P.levels.insert(idx + n, P.levels.pop())
                        trims.append(g_new)
                    g = trims[i - 1]
                key = tuple(sorted(e.items()))
                if key not in sym:
                    sym[key] = P._alloc(e)
                g[y][x] = sym[key]
        return [f"{self.lid}_t{n + 1}" for n in range(len(trims))]


# ---------------------------------------------------------------------------
# Blocks nobody can see: the core of a thick wall, the inside of a rock. hide_unseen() swaps them for a cheap block
# before the Vox levels are written back, so the build costs less and looks the same.
def hide_unseen(P, voxes, cheap, skin=None, keep=None, snap=1, min_run=1):
    """Swap every carved voxel that can't be seen for `cheap` (a (name, colour) pair). Call it once everything is
    carved, before the Vox levels' emit().

    A voxel can be seen when anything that isn't solid touches it, faces, edges or corners (all 26 neighbours):
    air, water, glass, the opening a door or window item cuts, or the canvas's edge. Solid is every level's
    blocks, walls, roofs and floor courses, the ground (less what the levels dig out of it) and the Vox voxels;
    items don't hide anything. skin(name) is how many voxels deep each material's seen face stays (default 1;
    2 for a terrain material, whose smoothed surface reaches further in). keep(name) leaves a material alone
    (glass and water always are). Each square's hidden stretch of a material is swapped only where it's at least
    min_run voxels long, trimmed in to whole multiples of `snap` voxels above its level's floor: the pieces then
    come in fewer sizes, which keeps the palette small (each size of piece is a symbol). Returns {material
    name: voxels swapped}."""
    import itertools
    import numpy as np
    VZ = 0.5
    clear = lambda n: 'glass' in n.lower() or n.lower().startswith('water')
    skin = skin or (lambda n: 1)
    keep = keep or (lambda n: False)
    zlo = min(L['elev'] for L in P.levels) - 2
    zhi = max(L['elev'] + L['height'] for L in P.levels) + 1
    nz = int(round((zhi - zlo) / VZ))
    kz = lambda z: max(0, min(nz, int(round((z - zlo) / VZ))))
    occ = np.zeros((nz, P.H, P.W), bool)
    vox_at = {v.lid: v.a.any(axis=0) for v in voxes}       # squares a Vox level holds blocks in (they dig the ground)
    for y in range(P.H):
        for x in range(P.W):
            for (b, t, n, lid) in P._spans(x, y):
                c = P.grids[lid][y][x]
                if n == 'floor' and PALETTE.get(c, {}).get('kind') == 'water':
                    continue
                if n != 'floor' and clear(n):
                    continue
                occ[kz(b):kz(t), y, x] = True
            top = P.terrain[y][x] if P.terrain is not None else 0
            if top <= zlo:
                continue
            air = []                                        # what the levels dig out of the ground here
            for L in P.levels:
                c = P.grids[L['id']][y][x]
                held = L['id'] in vox_at and vox_at[L['id']][y, x]
                if c == ' ' and not held:
                    continue
                e = PALETTE.get(c, {})
                fl = 0.5 if (e.get('kind') in ('floor', 'water') or e.get('under')) else 0
                if L['elev'] - fl < top:
                    air.append((L['elev'] - fl, min(top, L['elev'] + L['height'])))
            z = zlo
            for a, b in sorted(air):
                if a > z:
                    occ[kz(z):kz(a), y, x] = True
                z = max(z, b)
            if z < top:
                occ[kz(z):kz(top), y, x] = True
    for v in voxes:
        k0 = kz(v.L['elev'])
        see = np.array([False] + [clear(m[0]) for m in v.mats[1:]])
        for k in range(v.nz):
            if k0 + k < nz:
                occ[k0 + k] |= (v.a[k] != 0) & ~see[v.a[k]]
    lv = {L['id']: L for L in P.levels}
    for it in P.items:                                      # the openings door and window items cut
        if it.get('mount') not in ('door', 'window'):
            continue
        el = lv[it['level']]['elev']
        z0 = el + it.get('z', 0 if it['mount'] == 'door' else max(0.5, 2.5 - it['h']))
        w, d = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
        occ[kz(z0):kz(z0 + it['h']), it['y']:it['y'] + d, it['x']:it['x'] + w] = False

    def erode(a):
        pad = np.pad(a, 1, constant_values=False)
        out = a.copy()
        for dz, dy, dx in itertools.product((0, 1, 2), repeat=3):
            out &= pad[dz:dz + nz, dy:dy + P.H, dx:dx + P.W]
        return out
    hidden = {1: erode(occ)}
    for n in range(2, 1 + max(skin(m[0]) for v in voxes for m in v.mats[1:])):
        hidden[n] = erode(hidden[n - 1])
    swapped = Counter()
    for v in voxes:
        k0, ci = kz(v.L['elev']), v.mat(*cheap)
        ok = np.zeros(len(v.mats), bool)
        sk = np.ones(len(v.mats), int)
        for mi in range(1, len(v.mats)):
            name = v.mats[mi][0]
            ok[mi] = not (mi == ci or clear(name) or keep(name))
            sk[mi] = max(1, skin(name))
        kk = min(v.nz, nz - k0)
        if kk <= 0:
            continue
        a = v.a[:kk]
        hid = np.zeros(a.shape, bool)
        for n_ in set(sk[ok].tolist()):                     # hidden, at each material's own skin depth
            hid |= ok[a] & (sk[a] == n_) & hidden[n_][k0:k0 + kk]
        for y, x in zip(*np.nonzero(hid.any(axis=0))):
            col, h = a[:, y, x], hid[:, y, x]
            k = 0
            while k < kk:
                if not h[k]:
                    k += 1
                    continue
                m, s0 = col[k], k
                while k < kk and h[k] and col[k] == m:
                    k += 1
                lo, hi = -(-s0 // snap) * snap, (k // snap) * snap    # trimmed in to the snap
                if hi - lo >= max(min_run, 1):
                    col[lo:hi] = ci
                    swapped[v.mats[m][0]] += hi - lo
    return dict(swapped)


# ---------------------------------------------------------------------------
# Can you walk there? A rough model of the planner's walk mode: what's solid in each square, and where a body
# 2 m tall can stand, searched outward from the spawn point with steps of a block up (or a jump) and any drop down.
def _merge(iv):
    iv.sort()
    out = []
    for a, b in iv:
        if out and a <= out[-1][1] + 1e-6:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def walk_columns(P):
    """Every square's solid intervals in absolute metres: the levels' blocks, walls, roofs and floor courses (water is
    left out: you swim it), the ground below the terrain less what the levels dig out of it, and the items walk mode
    stops you at (furniture, stations, windows' glass, tree trunks, stairs as their steps; not the survivors'
    stand-ins, the spawn point, open doors or canopies)."""
    cols = {}
    lv = {L['id']: L for L in P.levels}
    deep = min([-1] + [L['elev'] - 1 for L in P.levels])
    for y in range(P.H):
        for x in range(P.W):
            iv = [(b, t) for (b, t, n, lid) in P._spans(x, y)
                  if not (n == 'floor' and PALETTE.get(P.grids[lid][y][x], {}).get('kind') == 'water')]
            top = P.terrain[y][x] if P.terrain is not None else 0
            air = []
            for L in P.levels:
                c = P.grids[L['id']][y][x]
                if c == ' ':
                    continue
                e = PALETTE.get(c, {})
                fl = 0.5 if (e.get('kind') in ('floor', 'water') or e.get('under')) else 0
                if L['elev'] - fl < top:
                    air.append((L['elev'] - fl, min(top, L['elev'] + L['height'])))
            earth, z = [], deep
            for a, b in sorted(air):
                if a > z:
                    earth.append((z, a))
                z = max(z, b)
            if z < top:
                earth.append((z, top))
            cols[(x, y)] = iv + earth
    for it in P.items:
        typ, mount = it['type'], it.get('mount')
        if typ.startswith('npc-') or typ in ('spawn',) or mount == 'door' or 'gate' in typ:
            continue                                        # (gates open, like doors)
        el = lv[it['level']]['elev']
        w, d = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
        z0 = el + it.get('z', 0 if mount != 'window' else max(0.5, 2.5 - it['h']))
        h = it['h'] * (0.45 if typ.startswith('tree-') else 1)
        for j in range(it['y'], it['y'] + d):
            for i in range(it['x'], it['x'] + w):
                if typ == 'stairs':
                    fx, fy = {0: (0, 1), 90: (-1, 0), 180: (0, -1), 270: (1, 0)}[it['rot']]
                    run = d if fy else w
                    k = {(0, 1): it['y'] + d - 1 - j, (0, -1): j - it['y'], (-1, 0): i - it['x'], (1, 0): it['x'] + w - 1 - i}[(fx, fy)]
                    cols.setdefault((i, j), []).append((el, el + min(it['h'], (math.floor(k * it['h'] / 0.5 / run) + 1) * 0.5)))
                else:
                    cols.setdefault((i, j), []).append((z0, z0 + h))
    return {k: _merge(v) for k, v in cols.items()}


def walk_reach(P, step=0.5, head=2.0, cols=None, body=2):
    """Where you can stand and get to on foot from the spawn point: {(x, y): [heights]}. step: the highest step up
    without jumping (walk mode steps a block; it jumps 1.2 m with a tap). body: the body's width in squares; walk
    mode's is 0.6 m, so on a 0.5 m plan it takes 2 x 2 squares (1 for a quick, looser search)."""
    cols = cols or walk_columns(P)
    if body == 2:
        return _walk_reach2(P, step, head, cols)
    stands = {}
    for k, iv in cols.items():
        hs = []
        for n, (a, b) in enumerate(iv):
            nxt = iv[n + 1][0] if n + 1 < len(iv) else 1e9
            if nxt - b >= head - 1e-6:
                hs.append(b)
        stands[k] = hs

    def free(k, a, b):
        for (s, t) in cols.get(k, ()):
            if s < b - 1e-6 and a < t - 1e-6:
                return False
        return True
    sp = next(it for it in P.items if it['type'] == 'spawn')
    el = next(L['elev'] for L in P.levels if L['id'] == sp['level'])
    k0 = (sp['x'], sp['y'])
    z0 = min(stands[k0], key=lambda h: abs(h - el))
    seen = {(k0, z0)}
    todo = [(k0, z0)]
    while todo:
        (x, y), z = todo.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            k = (x + dx, y + dy)
            for z2 in stands.get(k, ()):
                if z2 > z + step + 1e-6 or (k, z2) in seen:
                    continue
                if z2 > z and not free((x, y), z, z2 + head):
                    continue
                if z2 < z and not free(k, z2, z + head):
                    continue
                seen.add((k, z2))
                todo.append((k, z2))
    out = {}
    for k, z in seen:
        out.setdefault(k, []).append(z)
    return out


def walk_problems(P, reach, levels_ok=None, slack=1.0):
    """The items and labelled areas you can't get to on foot: an item needs a reachable spot beside it (or on it, for
    a stand-in) within `slack` of its floor; an area needs one inside it at its level's floor."""
    lv = {L['id']: L for L in P.levels}
    probs = []
    for it in P.items:
        if it.get('mount') in ('door', 'window') or it['type'] in ('spawn', 'stairs') or it['type'].startswith('tree-') \
                or it['type'] == 'shrub' or it.get('mount') in ('wall', 'ceiling'):
            continue
        el = lv[it['level']]['elev'] + it.get('z', 0)
        w, d = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
        ring = [(i, j) for j in range(it['y'] - 2, it['y'] + d + 2) for i in range(it['x'] - 2, it['x'] + w + 2)]
        if not any(abs(z - el) <= slack for k in ring for z in reach.get(k, ())):
            probs.append(f"{it['label']} ({it['level']}) at {it['x'] / P.C:g},{it['y'] / P.C:g}")
    for zn in P.zones:
        el = lv[zn['level']]['elev']
        sq = [(i, j) for j in range(zn['y'] - 2, zn['y'] + zn['h'] + 2) for i in range(zn['x'] - 2, zn['x'] + zn['w'] + 2)]
        if not any(abs(z - el) <= slack for k in sq for z in reach.get(k, ())):
            probs.append(f"area: {zn['name']} ({zn['level']})")
    return probs


def _walk_reach2(P, step, head, cols):
    """walk_reach for a body 2 x 2 squares across: a position is its north-west square; it stands at a height where
    one of its squares has a solid top and all four are clear for the headroom above."""
    def free(k, a, b):
        for (s, t) in cols.get(k, ()):
            if s < b - 1e-6 and a < t - 1e-6:
                return False
        return True

    def foot(x, y):
        return ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1))

    stands = {}

    def heights(x, y):
        if (x, y) in stands:
            return stands[(x, y)]
        sq = foot(x, y)
        tops = sorted({b for k in sq for (a, b) in cols.get(k, ())})
        hs = [z for z in tops if all(free(k, z, z + head) for k in sq)]
        stands[(x, y)] = hs
        return hs

    def free4(x, y, a, b):
        return all(free(k, a, b) for k in foot(x, y))
    sp = next(it for it in P.items if it['type'] == 'spawn')
    el = next(L['elev'] for L in P.levels if L['id'] == sp['level'])
    k0 = (sp['x'], sp['y'])
    z0 = min(heights(*k0), key=lambda h: abs(h - el))
    seen = {(k0, z0)}
    todo = [(k0, z0)]
    while todo:
        (x, y), z = todo.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            k = (x + dx, y + dy)
            if not (0 <= k[0] < P.W - 1 and 0 <= k[1] < P.H - 1):
                continue
            for z2 in heights(*k):
                if z2 > z + step + 1e-6 or (k, z2) in seen:
                    continue
                if z2 > z and not free4(x, y, z, z2 + head):
                    continue
                if z2 < z and not free4(k[0], k[1], z2, z + head):
                    continue
                seen.add((k, z2))
                todo.append((k, z2))
    out = {}
    for (x, y), z in seen:
        for k in foot(x, y):
            out.setdefault(k, []).append(z)
    return out

