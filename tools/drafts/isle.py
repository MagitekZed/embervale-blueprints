"""The Anchored Isle: a floating island base. 0.5 m plan, 128 x 128 m, a 120 m build area. Pass 2: the buildings.

A rock 60 x 50 m floats over a lake, its top at +28 m, held by chains to three rune pylons. Four areas:
- the crown (the island's top, +28 m): the showpiece, round the Flame Rotunda;
- inside the rock (+3 to +27.5 m): the forge, the mill behind the water wheel, the dormitory, the vault, the keel;
- the ground round the anchors (0 m): the farm, the lodges and yards, the Fisher's lake, the arrival;
- hidden below (-16 m): the summoning chamber under the lake, reached by a secret stair.
A real waterfall pours off the east rim past a water wheel set into the island's side, into the lake.

Pass 2 gives every building and room its character. The crown's masonry walls are 2 m thick, with depth carved
out of them (recessed bays under arches, deep reveals, niches inside), a projecting plinth and cornice; the rooms
in the rock and below ground are vaulted, with pillars, alcoves and niches cut from the rock. Walls and rock are
drawn as blocks with Vox (mage_common), so a square can hold a sill and a lintel with an opening between: the
extra pieces go on trim levels ('top_t1' and on) at the same height.

Coordinates are metres on the plan: x east, y south; heights in metres above each level's floor. Bearings are
compass degrees (0 = north, clockwise). Run: python isle.py  ->  writes isle.json
"""
import math
import os
import re
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mage_common import Plan, PALETTE, ROOF_MATS, Vox, hide_unseen
from laketown_common import ITEM, MOUNT, LIB, LIB_COLOR           # furniture, light and station sizes (estimates until measured)

PALETTE.clear()
P = Plan('Anchored Isle', 0.5, 128, 128, 120)
P.project = 'Anchored Isle'

# ---- the arcane palette (catalogue colours where the block is in the catalogue; 1.0 blocks estimated)
MOON, ASTONE, GOLD = '#c4c8cf', '#a39e92', '#c9a24a'            # Moonstone, Ancient Stone, Ancient Gold (1.0: estimates)
GRANITE, STAR, TOMB = '#626c7a', '#585a69', '#626d6e'
DUNGEON, CIRCLES = '#4f5458', '#7e74a8'                          # Ancient Dungeon, Ancient Circles (1.0: estimates)
ROCK, TURF, ROAD, SOIL = '#5d5a55', '#95b261', '#8b8577', '#6e483f'
TIMBER, WATERC = '#71665e', '#5f8fbf'
ROOF_MATS.setdefault('copper', ('Copper Block', '#8d694b'))
ROOF_MATS.setdefault('granite', ('Granite Shingle Roof Block', '#626454'))
ROOF_MATS.setdefault('gold', ('Ancient Gold Block', GOLD))
ROOF_MATS.setdefault('stone', ('Ancient Stone Block', ASTONE))
ROOF_MATS.setdefault('straw', ('Straw Roof Block', '#a7753d'))

# materials for carved work: (block name, colour)
MOONSTONE = ('Moonstone Block', MOON)
ANCIENT = ('Ancient Stone Block', ASTONE)
GOLDB = ('Ancient Gold Block', GOLD)
STARL = ('Starlight Block', STAR)
PGRAN = ('Polished Granite Block', GRANITE)
ROCKB = ("Granite (the isle's rock)", ROCK)
TOMBB = ('Midnight Tomb Block', TOMB)
DUNGB = ('Ancient Dungeon Block', DUNGEON)
RUNE = ('Blue Luminescent Block', '#6c9dc3')
RSTONE = ('Rough Stone Block', '#7d776a')
TIMB = ('Half-Timbered Block', TIMBER)
RWOOD = ('Rough Wood Block', '#7a6653')
TWOOD = ('Tarred Wood Block', '#5d5652')
IRON = ('Iron Block', '#848483')
COPPERB = ('Copper Block', '#8d694b')
BANNER = ('Red Carpet Block', '#9e3742')
STARGLOW = ('White Luminescent Block', '#d1cac6')
BRICK = ('Fired Bricks Block', '#aa7657')
ITEM.update({'Bow and Arrow Wall Mount': (2, 0.5, 1), 'Crypt Wall Torch': (0.5, 0.5, 1)})
MOUNT.update({'Bow and Arrow Wall Mount': 'wall', 'Crypt Wall Torch': 'wall'})

# Doors and windows: (wide, tall) in metres. The wooden ones were measured by the user; the rest are estimates
# until measured (the Ancient doors and windows and the stone round window are later-biome items, so they
# aren't in the planner's catalogue, and nobody publishes their sizes).
OPEN_SIZE = {
    'Wooden Door': (2, 2.5), 'Wooden Double Door': (4, 3.5), 'Wooden Window Frame': (1, 1.5),
    'Round Wooden Window Frame': (1, 1),                                                     # measured
    'Carved Wooden Double Door': (4, 3.5), 'Metal Bound Wooden Double Door': (4, 3.5),       # estimates
    'Ancients Night Door': (4, 3.5), 'Huge Ancient Door': (4, 5), 'Round Ancient Door': (3, 3),
    'Ancient Temple Door': (2, 3), 'High Ancient Window Frame': (1, 3), 'Large Ancient Window Frame': (2, 3),
    'Large Round Stone Window Frame': (3, 3), 'Round Carved Window Frame': (1, 1),
}


def M(name, kind, color, height=None, base=None):
    """A palette entry (made as needed): kind wall / block / floor / water / roof / dig."""
    e = {'name': name, 'kind': kind, 'color': color}
    if height is not None:
        e['height'] = height
    if base:
        e['base'] = base
    return P._alloc(e)


def each(x0, y0, x1, y1):
    """Squares (x, y) with their centres (mx, my) in metres, inside x0..x1, y0..y1."""
    for x, y in P.cells_rect(x0, y0, x1, y1):
        yield x, y, (x + 0.5) / P.C, (y + 0.5) / P.C


def line_squares(a, b, half):
    """Squares within `half` metres of the segment a-b (metres), with t (0 at a, 1 at b) for each."""
    (ax, ay), (bx, by) = a, b
    L2 = (bx - ax) ** 2 + (by - ay) ** 2
    for x, y, mx, my in each(min(ax, bx) - half - 1, min(ay, by) - half - 1, max(ax, bx) + half + 1, max(ay, by) + half + 1):
        t = max(0, min(1, ((mx - ax) * (bx - ax) + (my - ay) * (by - ay)) / L2))
        if math.hypot(mx - (ax + t * (bx - ax)), my - (ay + t * (by - ay))) <= half:
            yield x, y, t


def paint(g, mask, sym, only=None):
    """Paint a symbol into a level grid over a mask."""
    for y, x in zip(*np.nonzero(mask)):
        if only is None or g[y][x] in only:
            g[y][x] = sym


# ---- carving: walls in blocks (see Vox). A wall is described by a frame: ('box', (x0, y0, x1, y1), side) for one
# side of a rectangle, or ('ring', (cx, cy), r, bearing) for a round wall of outer radius r about a bearing.
VX = {}


def vox(lid):
    if lid not in VX:
        VX[lid] = Vox(P, lid)
    return VX[lid]


def snap(z):
    return np.round(np.asarray(z, dtype=float) * 2) / 2


def frame(v, geo, straight=False):
    """(along, depth) arrays for a wall: along it in metres (x or y for a box side; for a ring, the arc length from
    the bearing at the outer face, or with straight=True the distance across a straight cut through it), and
    depth in from the outer face."""
    if geo[0] == 'box':
        (x0, y0, x1, y1), s = geo[1], geo[2]
        return {'n': (v.mx, v.my - y0), 's': (v.mx, y1 - v.my), 'w': (v.my, v.mx - x0), 'e': (v.my, x1 - v.mx)}[s]
    (cx, cy), r, b = geo[1], geo[2], geo[3]
    dx, dy = v.mx - cx, v.my - cy
    dth = np.radians((np.degrees(np.arctan2(dx, -dy)) - b + 180) % 360 - 180)
    d = np.hypot(dx, dy)
    far = np.abs(dth) > math.radians(80)
    if straight:
        return np.where(far, 1e9, d * np.sin(dth)), np.where(far, -1e9, r - d * np.cos(dth))
    return np.where(far, 1e9, dth * r), r - d


def arch(u, hw, spring, shape='round'):
    """The top of an opening at offset u from its centre line: flat at `spring`, or a round or pointed arch
    springing there, in whole blocks."""
    u = np.abs(u)
    if shape == 'flat':
        return np.full(np.shape(u), float(spring))
    if shape == 'round':
        rise = np.sqrt(np.maximum(0, hw * hw - u * u))
    else:                                                          # pointed (two arcs of radius = the span)
        rise = np.sqrt(np.maximum(0, (2 * hw) ** 2 - (u + hw) ** 2))
    return spring + snap(rise)


def carve(v, geo, ac, hw, d0, d1, z0, spring, shape='round', m=0):
    """Cut (or with m, fill) the wall `d0`..`d1` metres in from its outer face, within hw of `ac` along it, from
    z0 up to an arch springing at `spring`: bays, niches, portals, slits."""
    along, depth = frame(v, geo)
    u = along - ac
    mask = (np.abs(u) < hw - 1e-6) & (depth > d0) & (depth < d1)
    v.put(mask, z0, arch(u, hw, spring, shape), m)
    return mask


def item_rect(geo, ac, w, dc):
    """The squares a door or window item covers: w along the wall at ac, one square thick, dc in from the outer
    face (rings: at a cardinal bearing only, since items can't turn diagonally)."""
    if geo[0] == 'ring':
        (cx, cy), r, b = geo[1], geo[2], geo[3]
        s = {0: 'n', 90: 'e', 180: 's', 270: 'w'}[b % 360]
        a = (cx if s in 'ns' else cy) + ac * (1 if s in 'ne' else -1)
        return item_rect(('box', (cx - r, cy - r, cx + r, cy + r), s), a, w, dc)
    (x0, y0, x1, y1), s = geo[1], geo[2]
    lo, hi = ac - w / 2, ac + w / 2
    return {'n': (lo, y0 + dc, hi, y0 + dc + 0.5), 's': (lo, y1 - dc - 0.5, hi, y1 - dc),
            'w': (x0 + dc, lo, x0 + dc + 0.5, hi), 'e': (x1 - dc - 0.5, lo, x1 - dc, hi)}[s]


def opening(lid, v, geo, ac, name, z, T, d0=-0.1, dc=None):
    """A door or window: cut straight through a wall T metres thick (from d0 in from its face), and place the
    item in its innermost course (or dc in). Doors take d0=-0.6 to cut the plinth in front too."""
    w, h = OPEN_SIZE[name]
    along, depth = frame(v, geo, straight=True)
    v.cut((np.abs(along - ac) < w / 2 - 1e-6) & (depth > d0) & (depth < T + 1), z, z + h)
    return P.opening(lid, name, *item_rect(geo, ac, w, T - 0.5 if dc is None else dc), h, z)


def ring_arch(v, geo, ac, hw, spring, m=ANCIENT, key=None, shape='round', d0=-0.1):
    """An archivolt: the face course over an arch (and its imposts) re-faced in another material; with key, a
    keystone at its crown, two courses tall, standing half a block proud. d0 is where the face is, in from the
    wall's outer face (deeper for an arch at the back of a recess, or for the inside face)."""
    along, depth = frame(v, geo)
    u = along - ac
    face = (depth > d0) & (depth < d0 + 0.6) & (np.abs(u) < hw + 0.5 - 1e-6)
    bot = np.where(np.abs(u) < hw - 1e-6, arch(u, hw, spring, shape), spring - 0.5)
    top = np.maximum(arch(u, hw + 0.5, spring, shape), bot + 0.5)
    v.put(face, bot, top, m, only='solid')
    if key:
        kb = arch(u, hw, spring, shape)
        v.put((np.abs(u) < 0.5 - 1e-6) & (depth > d0 - 0.5) & (depth < d0 + 0.6), kb, kb + 1, key)


def bay(v, geo, ac, hw, depth, z0, spring, shape='round', d0=-0.1, ring=ANCIENT, key=None):
    """A recess or a portal under an arch (see carve), framed by an archivolt."""
    carve(v, geo, ac, hw, d0, depth, z0, spring, shape)
    if ring:
        ring_arch(v, geo, ac, hw, spring, ring, key, shape)


def sill(v, geo, ac, hw, z, d0, d1, m=ANCIENT):
    """A sill course under a window: hw either side of ac, d0..d1 in from the wall's face, its top at z."""
    along, depth = frame(v, geo, straight=True)
    v.put((np.abs(along - ac) < hw - 1e-6) & (depth > d0) & (depth < d1), z - 0.5, z, m)


def round_frame(v, geo, ac, zc, r0, r1, d0=-0.1, m=ANCIENT):
    """A ring of stone round a round window centred at (ac, zc), re-facing the wall's face d0 in from its outer
    face (the back of a recess, for a window in one)."""
    along, depth = frame(v, geo, straight=True)
    u = np.abs(along - ac)
    face = (depth > d0) & (depth < d0 + 0.6) & (u < r1)
    hi, lo = np.sqrt(np.maximum(0, r1 * r1 - u * u)), np.sqrt(np.maximum(0, r0 * r0 - u * u))
    v.put(face, zc + lo, zc + hi, m, only='solid')
    v.put(face, zc - hi, zc - lo, m, only='solid')


def roof_top(rf, elev, x0, y0, x1, y1):
    """The highest roof top (absolute metres) over a rectangle."""
    return elev + max(rf.h.get((x, y), 0) for x, y in P.cells_rect(x0, y0, x1, y1))


def finial(v, x0, y0, x1, y1, z, parts):
    """A finial or pinnacle: blocks stacked from z (above v's level floor), parts [(height, material)]."""
    for h, m in parts:
        v.put(v.rect(x0, y0, x1, y1), z, z + h, m)
        z += h


def put(lid, name, x, y, rot=0, z=None, label=None):
    """A catalogue item by its game name, the top-left of its footprint at x, y (turned for rot 90 and 270).
    rot 0 faces south, 90 west, 180 north, 270 east. Sizes are estimates until measured (laketown_common.ITEM)."""
    w, d, h = ITEM[name]
    mount = MOUNT.get(name)
    typ = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    color = {'wall': '#b08a4a', 'ceiling': '#c9a23a'}.get(mount, '#8a7a6a')
    return P.item(lid, typ, label or name, x, y, w, d, h, rot, color, z=z, mount=mount)


def box_mask(v, box, out=0.0):
    x0, y0, x1, y1 = box
    return v.rect(x0 - out, y0 - out, x1 + out, y1 + out)


def shell(v, box, T, z0, z1, m):
    """A rectangular wall T metres thick inside the outer faces of box."""
    x0, y0, x1, y1 = box
    v.put(v.rect(*box) & ~v.rect(x0 + T, y0 + T, x1 - T, y1 - T), z0, z1, m)


def band(v, box, out, z0, z1, m, keep=None):
    """A course projecting `out` metres round a rectangle: a plinth or a cornice."""
    mask = box_mask(v, box, out) & ~box_mask(v, box)
    v.put(mask if keep is None else mask & keep, z0, z1, m)


def radial(v, c, b, half, r0, r1):
    """Squares within `half` metres of the ray from c at bearing b, between r0 and r1 from c."""
    along, depth = frame(v, ('ring', c, 0, b), straight=True)
    return (np.abs(along) < half) & (-depth > r0) & (-depth < r1)


def polar(c, r, b):
    return c[0] + r * math.sin(math.radians(b)), c[1] - r * math.cos(math.radians(b))


# ================================================================= levels
deep = P.level('deep', 'Hidden: the summoning chamber (-16 m)', -16, 10)
deep_step = P.level('deep_step', 'Hidden: the step down to the circle (-16.5 m)', -16.5, 0.5)
deep_sunk = P.level('deep_sunk', 'Hidden: the sunken summoning circle (-17 m)', -17, 1)
deepc = P.level('deepc', 'Hidden: the passage and the study (-16 m)', -16, 6)
deep_dais = P.level('deep_dais', "Hidden: the study's reading dais (-15.5 m)", -15.5, 1)
ugs = P.level('ugs', 'Hidden: the secret stair shaft (-6 m)', -6, 6)
ocul = P.level('ocul', 'Hidden: the oculus shaft (-6 m)', -6, 2)
oculg = P.level('oculg', 'Hidden: the oculus glass, in the lake bed (-4 m)', -4, 1)
lake = P.level('lake', 'Lake (water level, 0 m)', 0, 1)
gnd = P.level('ground', 'Ground: farm, lodges, yards, arrival, the stair tower (0 m)', 0, 30)
up35 = P.level('farm2', "Ground: the farmhouse's upper floor (+3.5 m)", 3.5, 3.5)
pyl = P.level('pyl', 'Anchor pylons, on their knolls (+3 m)', 3, 12)
chain = P.level('chain', 'The chains (0 m)', 0, 28)
falls = P.level('falls', 'The waterfall (0 m)', 0, 28)
rk0 = P.level('rk0', 'Isle: the crags hanging below (+3 m)', 3, 6)
rkA = P.level('rkA', 'Isle: the keel lookout (+9 m)', 9, 6)
rkB = P.level('rkB', 'Isle: dormitory, vault, cellars (+15 m)', 15, 6)
rkC = P.level('rkC', 'Isle: the forge, the mill, the hall of the descent (+21 m)', 21, 6.5)
top = P.level('top', 'Isle: the crown (+28 m)', 28, 34)
dais = P.level('dais', "Isle: the altar dais's first step (+28.5 m)", 28.5, 1)
up29 = P.level('up29', "Isle: raised floors (+29 m): the altar dais, the bard's stage, the bath's podium", 29, 1)
sp48 = P.level('sp48', "Isle: the Starspire's top room (+48 m)", 48, 4)

# ================================================================= the ground: a lake basin under the isle, knolls for the pylons
LAKE = (68, 66, 30, 21)                                            # centre, radii (metres)
PYLONS = {'nw': (22, 30), 'ne': (106, 28), 'se': (116, 92)}
TOWER = (17, 91, 29, 103)                                          # the stair tower (SW)


def lake_d(x, y):
    cx, cy, rx, ry = LAKE
    th = math.atan2(y - cy, x - cx)
    wob = 1 + 0.035 * math.sin(3 * th + 0.7) + 0.025 * math.sin(7 * th + 2.0)   # (a less perfect shore)
    return math.hypot((x - cx) / rx, (y - cy) / ry) / wob


# ---- the grounds: everything built sits on a flat pad at 0 m, lanes at 0 m run between the pads, and the open land
# rolls into hills between them, easing up from the pads and the lake shore and dying away to flat ground within
# 14 m of the canvas's edge, so it blends into whatever flat land lies round it.
PADS = [(40, 4, 90, 44), (4, 42, 32, 78), (14, 88, 78, 108), (55, 104, 65, 128), (51, 106, 69, 112),
        (76, 86, 124, 124), (100, 58, 118, 74)]                   # yards, the lodge, the plaza, the road, the farm, the boathouse
LANES = [[(63, 107.25), (75, 107.25), (78, 105), (88, 105)],      # the plaza to the farmyard
         [(76, 92), (86, 86), (98, 81), (110, 75)],               # the plaza to the boathouse, by the south-east shore
         [(30, 89), (31, 77)],                                     # the plaza to the lodge
         [(31, 43), (36, 40), (40, 36)],                           # the lodge to the timber yard
         [(90, 38), (98, 44), (99, 52), (103, 57)]]               # the timber yard to the boathouse, by the north-east shore
HILLS = [(16, 16, 6, 11), (34, 10, 3, 7), (6, 30, 2.5, 6), (8, 98, 3, 8), (20, 118, 2.5, 9), (44, 122, 1.5, 6),
         (114, 14, 6, 11), (97, 9, 3, 7), (124, 30, 2.5, 6), (115, 41, 4.5, 7), (124, 66, 2, 6)]   # (x, y, height, spread)
PLATEAUS = [(16, 16, 5), (114, 14, 5)]                             # flattened hilltops: the stone circle, the pavilion
BROOK = [(115, 41), (111, 45), (106, 49), (102, 51.5), (98.5, 53), (93, 55)]   # from a spring in the hills down to the lake
POND = (36, 116, 4)                                                # the lily pond in the south-west meadow


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def seg_near(px, py, a, b):
    """Distance from (px, py) to the segment a-b, and how far along it (0..1)."""
    (ax, ay), (bx, by) = a, b
    L2 = (bx - ax) ** 2 + (by - ay) ** 2
    t = max(0.0, min(1.0, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / L2))
    return math.hypot(px - ax - t * (bx - ax), py - ay - t * (by - ay)), t


def line_near(px, py, pts):
    """Distance from (px, py) to a polyline, and how far along it (0..1 of its length)."""
    lens = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    total, run, best = sum(lens), 0.0, (1e9, 0.0)
    for (a, b), L in zip(zip(pts, pts[1:]), lens):
        d, t = seg_near(px, py, a, b)
        if d < best[0]:
            best = (d, (run + t * L) / total)
        run += L
    return best


def pad_d(x, y):
    """How far (x, y) is from the nearest pad or lane."""
    d = min(math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1)) for (x0, y0, x1, y1) in PADS)
    return min([d] + [max(0.0, line_near(x, y, L)[0] - 1) for L in LANES])


def brook_s(t):
    """The brook's surface at t along it: following the hillside down in whole-block steps, never rising, to the
    lake's level (see BROOK_PROF)."""
    return BROOK_PROF[min(len(BROOK_PROF) - 1, int(round(t * (len(BROOK_PROF) - 1))))]


def hills(x, y):
    h = sum(hh * math.exp(-((x - hx) ** 2 + (y - hy) ** 2) / (r * r)) for hx, hy, hh, r in HILLS)
    h += 0.6 * math.sin(x * 0.31 + 1.7) * math.sin(y * 0.27 + 0.4) + 0.3 * math.sin(x * 0.11 - y * 0.13)
    return max(0.0, h)


def land(x, y):
    """The ground before the brook and the pond are cut in (metres, not yet in whole blocks)."""
    d = lake_d(x, y)
    if d < 1:                                                      # the basin, shelving to 4 m
        s = (1 - d) * min(LAKE[2], LAKE[3])
        return -min(4, max(1, round(s / 1.5)))
    e = min(x, y, 128 - x, 128 - y)
    h = hills(x, y) * smooth((e - 2) / 12) * smooth(pad_d(x, y) / 5) * smooth((d - 1.05) / 0.35)
    for (px, py, pr) in PLATEAUS:                                  # hilltops cut flat
        cap = math.floor(hills(px + pr, py) * 2) / 2
        if math.hypot(x - px, y - py) < pr + 3:
            h = cap if math.hypot(x - px, y - py) < pr else min(h, cap)
    for (px, py) in PYLONS.values():                               # a knoll under each pylon
        r = math.hypot(x - px, y - py)
        if r < 9:
            h = max(h, 3 if r < 5 else (9 - r) / 4 * 3)
    return h


def _profile(n=240):
    lens = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(BROOK, BROOK[1:])]
    total, out, low = sum(lens), [], 1e9
    for k in range(n):
        dist, run = k / (n - 1) * total, 0.0
        for seg, L in zip(zip(BROOK, BROOK[1:]), lens):
            if dist <= run + L or seg == (BROOK[-2], BROOK[-1]):
                a, b = seg
                t = (dist - run) / L
                break
            run += L
        low = min(low, math.floor((land(a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])) - 0.75) * 2) / 2)
        out.append(max(0.0, low))
    return out


BROOK_PROF = _profile()


def ground(x, y):
    h = land(x, y)
    if h < 0:
        return h
    bd, bt = line_near(x, y, BROOK)
    s = brook_s(bt)
    if bd < 2.5 and s > 0:
        h = max(h, s + 0.5)                                        # its banks
    if bd < 0.8:
        h = s - 0.5                                                # its bed, a block under its surface
    pd = math.hypot(x - POND[0], y - POND[1]) / (POND[2] * (1 + 0.12 * math.sin(3 * math.atan2(y - POND[1], x - POND[0]))))
    if pd < 1:
        h = -1 if pd < 0.75 else -0.5
    return round(h * 2) / 2


P.ground_fn(ground)
WATER = M('Water', 'water', '#3f6f8f')
for x, y, mx, my in each(0, 0, 128, 128):
    if P.ground_at(x, y) < 0:
        lake[y][x] = WATER

# ================================================================= the isle: an irregular rock, flat on top, a cone below
IC, IRX, IRY = (64, 64), 30, 25                                    # the outline (the altar at its heart, the canvas's centre)
APEX = (64, 79.5)                                                  # the cone's tip, under the court
TOP, RIM_UNDER, BELLY, TIP = 28, 23, 9, 3                         # a 5 m rim, a full belly to +9 m, crags to +3 m
# pointed crags hanging from the belly, clustered under the middle (the keel, the deepest, has the lookout in it),
# lesser ones under the rim: (x, y, the tip's height, radius where it meets the belly)
CRAGS = ((64, 79.5, 3, 8), (64, 66, 5, 6), (55, 72, 7, 4.5), (73, 71, 6, 5), (58, 86.5, 8, 3.5), (71, 85, 7.5, 4),
         (45, 64, 13.5, 4), (80, 50, 14.5, 4), (86, 75, 16.5, 3), (52, 48, 17, 3))


def isle_dn(x, y):
    """0 at the island's centre, 1 at its rim (an irregular outline, a prow to the east for the falls)."""
    dx, dy = (x - IC[0]) / IRX, (y - IC[1]) / IRY
    th = math.atan2(dy, dx)
    s = 1 + 0.05 * math.sin(3 * th + 0.5) + 0.035 * math.sin(5 * th + 2.1) + 0.07 * math.exp(-(th ** 2) / 0.03)
    return math.hypot(dx, dy) / s


RIM_R = []                                                         # distance from the apex to the rim, by degree
for deg in range(360):
    u = (math.cos(math.radians(deg)), math.sin(math.radians(deg)))
    lo, hi = 0.0, 80.0
    for _ in range(30):
        mid = (lo + hi) / 2
        if isle_dn(APEX[0] + mid * u[0], APEX[1] + mid * u[1]) <= 1:
            lo = mid
        else:
            hi = mid
    RIM_R.append(lo)


def apex_dn(x, y):
    """0 at the cone's tip, 1 at the rim, along the ray from the tip."""
    dx, dy = x - APEX[0], y - APEX[1]
    a = math.degrees(math.atan2(dy, dx)) % 360
    i = int(a) % 360
    f = a - int(a)
    r = RIM_R[i] * (1 - f) + RIM_R[(i + 1) % 360] * f
    return math.hypot(dx, dy) / max(r, 0.01)


def underside(x, y):
    """The rock's underside: 23 m at the rim, steep under it, down to a full belly at 9 m under the court; then
    pointed crags hang from the belly, a cluster under the middle down to the keel at 3 m."""
    dn = apex_dn(x, y)
    rough = 1.1 * (math.sin(x * 0.9 + y * 0.4) + math.sin(x * 0.35 - y * 0.8 + 1.3) + 0.6 * math.sin(x * 1.7 - y * 1.3)) / 2.6
    belly = RIM_UNDER - (RIM_UNDER - BELLY) * max(0.0, 1 - dn) ** 0.4 + rough
    b = belly
    for (sx, sy, tip, r) in CRAGS:                                 # straight-sided points, a little ragged
        d = math.hypot(x - sx, y - sy) + 0.4 * math.sin(math.atan2(y - sy, x - sx) * 5 + sx)
        if d < r:
            b = min(b, tip + max(0.0, d) / r * (belly - tip))
    return max(TIP, min(RIM_UNDER, round(b * 2) / 2))


def inside(x, y):
    return isle_dn(x, y) <= 1


U = np.full((P.H, P.W), np.inf)                                    # the underside's height per square (inf: off the isle)
for x, y, mx, my in each(30, 35, 100, 93):
    if inside(mx, my):
        U[y, x] = underside(mx, my)
INSIDE = np.isfinite(U)
_n = INSIDE.copy()
for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    _n &= np.roll(np.roll(INSIDE, dy, 0), dx, 1)
RIM = INSIDE & ~_n                                                 # the outermost squares of the crown

# ================================================================= the rock, in four slices, and the rooms cut in it
SLICES = [(rk0, 'rk0', 3, 6), (rkA, 'rkA', 9, 6), (rkB, 'rkB', 15, 6), (rkC, 'rkC', 21, 6.5)]
FLOOR_CARVED = M('Ancient Stone Block (carved floor)', 'floor', ASTONE)
SHAFT = (64, 80, 3.5)                                              # the descent: a round shaft from the crown to the keel
for g, lid, z0, h in SLICES:
    v = vox(lid)
    m = INSIDE & (U < z0 + h)
    v.put(m, np.where(m, np.maximum(0, U - z0), 0), h, ROCKB)


def cuttable(z0):
    """Squares where a room on a floor at z0 can be cut: rock under its floor, and rock reaching down to the floor
    for a metre all round, so the room's walls never open to the sky under the rim."""
    walled = INSIDE & (U <= z0)
    w = walled.copy()
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            w &= np.roll(np.roll(walled, dy, 0), dx, 1)
    return INSIDE & (U <= z0 - 0.5) & w


CUT = {lid: cuttable(z0) for g, lid, z0, h in SLICES}
ZOFF = {lid: z0 for g, lid, z0, h in SLICES}
ROOM_NAMES = []


def room(lid, mask, ceiling, name=None, floor=FLOOR_CARVED):
    """Cut a room in a rock slice where the rock allows, its ceiling (metres above its floor; a value per square for
    a vault) under the rock left above; give it a carved floor. Returns the squares cut."""
    v = VX[lid]
    m = mask & CUT[lid]
    v.cut(m, 0, ceiling)
    paint(P.grids[lid], m, floor, only=(' ',))
    if name:
        ROOM_NAMES.append((lid, name, m))
    return m


def vault(axis, a0, a1, spring, crown, v):
    """A barrel vault's ceiling per square: `crown` along the middle of a0..a1 (x for axis 'x' meaning it runs
    east-west and curves across y), down to `spring` at the sides."""
    c, hw = (a0 + a1) / 2, (a1 - a0) / 2
    u = (v.my if axis == 'x' else v.mx) - c
    return spring + snap((crown - spring) * np.sqrt(np.maximum(0, 1 - (u / hw) ** 2)))


def cupola(c, r, spring, crown, v):
    """A dome-shaped ceiling per square, `crown` at c, down to `spring` at radius r."""
    d = np.hypot(v.mx - c[0], v.my - c[1])
    return spring + snap((crown - spring) * np.sqrt(np.maximum(0, 1 - (d / r) ** 2)))


RC = (64, 64)                                                      # the rotunda's centre, over the hall of the descent

# ---- rkC (+21 m, 6.5 m): the forge, the hall of the descent, the passages, the mill behind the wheel
v = VX['rkC']
room('rkC', v.rect(40, 50, 56, 64), vault('x', 50, 64, 4, 6.5, v), 'The forge (Oswald Anders)')
for xc in (44, 48, 52):                                            # bays for the tool racks along the north wall
    room('rkC', v.rect(xc - 1.25, 48.5, xc + 1.25, 50.5), arch(v.mx - xc, 1.25, 2.5))
room('rkC', v.rect(38.5, 54.5, 40.5, 59.5), arch(v.my - 57, 2.5, 3))  # the hearth's hood in the west wall
room('rkC', v.rect(56, 61.5, 58.5, 65), arch(v.my - 63.25, 1.75, 3), None)   # the forge's door to the hall
HALL_D = v.rect(58.5, 63, 69.5, 75.5) | v.disc(SHAFT[0], SHAFT[1], 5.5)
room('rkC', HALL_D, np.minimum(cupola((64, 69), 8, 4.5, 6.5, v), 6.5), 'Hall of the descent')
for (px, py) in ((61.5, 66), (66.5, 66), (61.5, 72), (66.5, 72)):  # four rock pillars carry its dome
    v.put(v.rect(px - 0.75, py - 0.75, px + 0.75, py + 0.75), 0, 6.5, ROCKB)
room('rkC', v.rect(69.5, 61.5, 84.5, 64.5), arch(v.my - 63, 1.5, 3.5), None)   # the passage to the mill
MILL = room('rkC', v.rect(84.5, 58, 94, 68), vault('y', 84.5, 94, 4.5, 6, v), 'The mill, behind the wheel')
for xb in (86.5, 89.25, 92):                                       # its beams, tarred wood under the vault
    v.put(v.rect(xb - 0.25, 58, xb + 0.25, 68) & MILL, 4, 4.5, TWOOD)
v.cut(v.rect(95, 60, 98.5, 67) & INSIDE, 0, 6.5)                   # the wheel pit, cut into the island's side
v.cut(v.rect(93, 63, 95.5, 64) & INSIDE, 2, 3)                     # the axle's hole through to the mill
v.cut(v.rect(93, 60.5, 95.5, 62) & INSIDE, 1.5, 4)                 # a window onto the wheel and the falls
v.cut(v.rect(93, 65, 95.5, 66.5) & INSIDE, 1.5, 4)
# the shaft, open from the keel up to the crown, and the parapet round it here
for lid in ('rkB', 'rkC'):
    sv = VX[lid]
    sm = sv.disc(SHAFT[0], SHAFT[1], SHAFT[2])
    sv.cut(sm, 0, sv.height)
    paint(P.grids[lid], sm, ' ')
v.put(v.ring(SHAFT[0], SHAFT[1], 4, 0.5) & CUT['rkC'], 0, 1, ANCIENT)

# ---- rkB (+15 m, 6 m): the corridor, the dormitory with its bed alcoves, the vault, the cellars
v = VX['rkB']
room('rkB', v.rect(62.5, 55, 65.5, 77), arch(v.mx - 64, 1.5, 3.5), 'Corridor')
room('rkB', v.disc(SHAFT[0], SHAFT[1], 5.5), cupola((SHAFT[0], SHAFT[1]), 5.5, 4, 6, v))
v.put(v.ring(SHAFT[0], SHAFT[1], 4, 0.5) & CUT['rkB'], 0, 1, ANCIENT)
DORM = room('rkB', v.rect(48, 62, 61.5, 76), vault('y', 48, 61.5, 3.5, 6, v), 'Dormitory (beds for the other survivors)')
for yc in (64.25, 67.75, 71.25, 74.75):                            # bed alcoves, arched, along the long walls
    room('rkB', v.rect(45.5, yc - 1.25, 48, yc + 1.25), arch(v.my - yc, 1.25, 2.5))
for xc in (51, 54.5, 58):                                          # and the north wall
    room('rkB', v.rect(xc - 1.25, 59.5, xc + 1.25, 62), arch(v.mx - xc, 1.25, 2.5))
room('rkB', v.rect(61.5, 67.5, 62.5, 70.5), arch(v.my - 69, 1.5, 2.5))    # the dormitory's door off the corridor
VAULT = room('rkB', v.rect(66.5, 64, 82, 74), vault('x', 64, 74, 3.5, 6, v), 'Vault (magic chests)')
for px in (70.5, 74.5, 78.5):                                      # piers making bays for the chests
    for py in (66.75, 71.25):
        v.put(v.rect(px - 0.75, py - 0.75, px + 0.75, py + 0.75), 0, 6, ROCKB)
room('rkB', v.rect(65.5, 67.5, 66.5, 70.5), 3.5)                   # the vault's door (a round one, in the rock)
CELL = room('rkB', v.rect(66.5, 54, 80, 62), np.where(v.my < 58, vault('x', 54, 57.5, 3, 4.5, v),
                                                    vault('x', 58.5, 62, 3, 4.5, v)), 'Cellars and stores')
for px in (69.5, 73, 76.5):                                        # the piers between its two vaulted aisles
    v.put(v.rect(px - 0.5, 57.5, px + 0.5, 58.5), 0, 6, ROCKB)
v.put(v.rect(66.5, 57.5, 80, 58.5) & CELL, 3, 6, ROCKB)            # (the spine wall over them)
room('rkB', v.rect(65.5, 56.5, 66.5, 59.5), arch(v.my - 58, 1.5, 2.5))    # the cellars' door

for (x_, y_, r_) in ((62.5, 61, 270), (62.5, 73, 270), (65, 64, 90), (65, 74.5, 90)):
    put('rkB', 'Crypt Wall Torch', x_, y_, r_, z=2)                # torches down the corridor

# ---- rkA (+9 m, 6 m): the keel lookout, slits looking out all round
v = VX['rkA']
room('rkA', v.disc(APEX[0], APEX[1], 4.5), cupola(APEX, 4.5, 4, 6, v), 'Keel lookout')
for b in range(0, 360, 45):
    v.cut(radial(v, APEX, b, 0.5, 3.5, 14), 1.5, 3)

# ---- the rock's rooms, labelled
for lid, name, m in ROOM_NAMES:
    ys, xs = np.nonzero(m)
    if len(xs):
        P.zone(lid, name, xs.min() / 2, ys.min() / 2, xs.max() / 2 + 0.5, ys.max() / 2 + 0.5, '#7e74a8')

# ================================================================= the crown (+28 m): the showpiece
# The Flame Rotunda at the heart (the altar at the canvas's centre, so the 120 m build area covers it all);
# Valory's great hall to the west, Alden Crowley's gallery to the north, Elio Ricci's bathhouse and the spring
# to the east on the prow, the court with the descent's mouth to the south, Balthazar's glass dome to the
# south-east, the Starspire by the bridge's landing to the south-west. Moonstone walls 2 m thick with the depth
# carved out of them; Ancient Stone for the plinths, cornices and trim; gold only on the rotunda and the descent.
TURFC = M('Fertile Springlands Dirt (turf)', 'floor', TURF)
PAVE = M('Moonstone Block (paving)', 'floor', MOON)
INLAY = M('Ancient Stone Block (paving)', 'floor', ASTONE)
paint(top, INSIDE, TURFC)
T = vox('top')                                                     # (nothing built on the crown yet: it starts empty)


def pave(mask, sym=PAVE):
    paint(top, mask & INSIDE, sym)


# the court and the ways across the crown
for r_ in ((52, 74, 76, 87), (42, 80.5, 53, 86), (52, 62, 55, 66), (73, 62, 77, 66), (62, 52, 66, 55),
           (42, 75, 48, 81)):
    pave(T.rect(*r_))

# ---- the Flame Rotunda: a drum 19 m across with 2 m walls, eight bays under round arches, a copper dome with a
# lantern over an oculus. The altar on a two-step dais under the oculus.
RR = 9.5
pave(T.disc(*RC, RR + 0.5))
pave(T.ring(*RC, 6.5, 0.5), INLAY)                                 # a ring of Ancient Stone set in the floor
T.put(T.ring(*RC, RR, 2), 0, 10, MOONSTONE)
T.put(T.ring(*RC, RR + 0.5, 0.5), 0, 1, ANCIENT)                   # the plinth
T.put(T.ring(*RC, RR + 0.5, 0.5), 9, 10, ANCIENT)                  # the cornice
for k in range(8):
    b = 45 * k
    g = ('ring', RC, RR, b)
    if k % 2 == 0:                                                 # N, E, S, W: doors, the main one to the court
        bay(T, g, 0, 2.5, 1, 1, 6, key=GOLDB)                      # the bay, 1 m deep, a gold keystone
        if b == 180:
            opening('top', T, g, 0, 'Huge Ancient Door', 0, 2, d0=-0.6)
            opening('top', T, g, 0, 'Round Carved Window Frame', 6.5, 2)
            round_frame(T, g, 0, 7, 0.5, 1, d0=0.9)
        else:
            opening('top', T, g, 0, 'Ancients Night Door', 0, 2, d0=-0.6)
            opening('top', T, g, 0, 'Large Round Stone Window Frame', 4.5, 2)   # a lunette over each
            round_frame(T, g, 0, 6, 1.5, 2, d0=0.9)
    else:
        bay(T, g, 0, 2, 1, 1, 6)                                   # blind arches between, a brazier in each
        bx, by = polar(RC, 9, b)
        put('top', 'Brazier', round((bx - 0.5) * 2) / 2, round((by - 0.5) * 2) / 2, z=1)
    carve(T, ('ring', RC, RR, b + 22.5), 0, 1, 1, 2.1, 0.5, 3)    # niches inside, in the piers
P.disc(dais, *RC, 4.5, M('Ancient Stone Block (the dais)', 'floor', ASTONE))
P.disc(up29, *RC, 3.5, M('Ancient Circles Block (the dais)', 'floor', CIRCLES))
P.item('up29', 'altar', 'Flame Altar', RC[0] - 2, RC[1] - 2, 4, 4, 3, color='#d9541e', iid='altar')
for x_ in (60.5, 67):
    put('top', 'Wall Lantern', x_, 73, 0, z=3)                     # either side of the main door
P.zone('top', 'The Flame Rotunda (the altar)', RC[0] - 7, RC[1] - 7, RC[0] + 7, RC[1] + 7, '#d9541e')

# ---- the great hall (Valory): 14 x 22 m, three bays a side under round arches with twin lancets, the fireplace
# and its chimney in the west wall, a stage in an apse to the north behind a proscenium arch, a deep portal and
# a rose window in the south gable.
HB = (38, 53, 52, 75)
pave(box_mask(T, HB, 0.5))
T.put(box_mask(T, HB) & ~T.rect(40, 55, 50, 73), 0, 10, MOONSTONE)
band(T, HB, 0.5, 0, 1, ANCIENT)
band(T, HB, 0.5, 9, 10, ANCIENT)
for s in 'we':
    g = ('box', HB, s)
    for yc in (58, 64, 70):
        if (s, yc) == ('w', 64):
            continue                                               # (the chimney breast)
        bay(T, g, yc, 2, 1, 1, 6.5)
        if (s, yc) == ('e', 64):                                   # the door to the rotunda, a lunette over it
            opening('top', T, g, yc, 'Ancients Night Door', 0, 2, d0=-0.6)
            opening('top', T, g, yc, 'Large Round Stone Window Frame', 4.5, 2)
            round_frame(T, g, yc, 6, 1.5, 2, d0=0.9)
        else:                                                      # twin lancets on a sill, a round window over them
            for du in (-1, 1):
                opening('top', T, g, yc + du, 'High Ancient Window Frame', 2.5, 2)
            opening('top', T, g, yc, 'Round Carved Window Frame', 6.5, 2)
            sill(T, g, yc, 1.75, 2.5, 0.4, 1.1)
# the chimney: a breast on the west wall, the stack rising through the roof, the fireplace inside
T.put(T.rect(37, 62.5, 38, 65.5), 0, 19, MOONSTONE)
T.put(T.rect(36.5, 62, 37, 66) | T.rect(37, 62, 38, 62.5) | T.rect(37, 65.5, 38, 66), 0, 1, ANCIENT)
T.put(T.rect(37, 62.5, 40, 65.5), 10, 19, MOONSTONE)
T.put(T.rect(36.5, 62, 40.5, 66), 18.5, 19.5, ANCIENT)             # its cap
T.cut(T.rect(38.5, 63.5, 39.5, 64.5), 2.5, 19.5)                   # the flue
T.put(T.rect(38, 63, 40, 65) & ~T.rect(38.5, 63.5, 39.5, 64.5), 19.5, 20.5, BRICK)   # its pot
carve(T, ('box', HB, 'w'), 64, 1.5, 1, 2.1, 0, 2.5, 'flat')        # the fireplace
# north: the proscenium arch, the apse and its stage
carve(T, ('box', HB, 'n'), 45, 4, -0.6, 2.1, 0, 5)
ring_arch(T, ('box', HB, 'n'), 45, 4, 5, key=ANCIENT, d0=1.4)     # the proscenium's archivolt, on the hall side
AP = (45, 55)
apse = T.my < 55
pave(T.disc(*AP, 6) & apse)
T.put(T.ring(*AP, 5.5, 1.5) & apse, 0, 7, MOONSTONE)
T.put(T.ring(*AP, 6, 0.5) & (T.my < 53), 0, 1, ANCIENT)
T.put(T.ring(*AP, 6, 0.5) & (T.my < 53), 6, 7, ANCIENT)
opening('top', T, ('ring', AP, 5.5, 0), 0, 'Large Round Stone Window Frame', 2.5, 1.5)   # behind the stage
STAGE = (T.disc(*AP, 4) & apse) | T.rect(41, 55, 49, 57)
T.put(STAGE, 0, 0.5, ANCIENT)                                      # (under the stage's floor)
paint(up29, STAGE, M('Ornate Wood Block (the stage)', 'floor', '#8a5a3c'))
# south: the portal and the rose window in the gable, the middle of the wall run up into the gable for it
g = ('box', HB, 's')
bay(T, g, 45, 2.5, 1.5, 0, 4, d0=-0.6, key=ANCIENT)
opening('top', T, g, 45, 'Carved Wooden Double Door', 0, 2, d0=1.4)
T.put(T.rect(42, 73, 48, 75), 10, 13, MOONSTONE)
T.cut(T.rect(42, 75, 48, 75.5), 9, 10)                             # (the cornice breaks round it)
opening('top', T, g, 45, 'Large Round Stone Window Frame', 8.5, 2)
round_frame(T, g, 45, 10, 1.5, 2.25)
for x_ in (49.5,):                                                 # Valory's banner, on a gold rod
    T.put(T.rect(x_, 75, x_ + 1, 75.5), 3.5, 8, BANNER)
    T.put(T.rect(x_ - 0.5, 75, x_ + 1.5, 75.5), 8, 8.5, GOLDB)
for x_ in (41.5, 48):
    put('top', 'Wall Lantern', x_, 75, 0, z=3)
P.item('up29', 'npc-bard', 'Valory (Bard)', 43.5, 51.5, 3, 3, 2, color='#b0596f')
P.zone('top', 'Great hall (Valory)', 40, 55, 50, 73, '#b0596f')
P.zone('up29', "The bard's stage", 41, 51, 49, 57, '#b0596f')

# ---- the Collector's gallery: a long range on the north rim, its south front in bays with an entrance frontispiece
# facing the rotunda, three oriels hanging over the void on the north, a corbelled turret on the north-east corner.
GB = (53, 41, 75, 52)
paint(top, T.rect(52.5, 39, 75.5, 52.5), PAVE)                     # (the oriels' floors hang past the rim)
T.put(T.rect(*GB) & ~T.rect(55, 42.5, 73, 50), 0, 8, MOONSTONE)
band(T, GB, 0.5, 0, 1, ANCIENT, keep=T.my > 41)
T.cut(T.rect(51.5, 51.5, 53.5, 53.5), 0, 1)                        # (a way between the hall's and the gallery's plinths, to the north-west lawn)
band(T, GB, 0.5, 7, 8, ANCIENT)
FP = (61.5, 50, 66.5, 52)                                          # the frontispiece: the middle run up, with a cross gable
T.put(T.rect(*FP), 0, 10, MOONSTONE)
T.cut(T.rect(61.5, 52, 66.5, 52.5), 7, 8)                          # (the cornice steps up over it)
T.put(T.rect(61, 52, 67, 52.5), 9, 10, ANCIENT)
g = ('box', FP, 's')
bay(T, g, 64, 2.5, 1.5, 0, 4, d0=-0.6, key=ANCIENT)
opening('top', T, g, 64, 'Ancients Night Door', 0, 2, d0=1.4)
opening('top', T, g, 64, 'Round Carved Window Frame', 7, 2)
round_frame(T, g, 64, 7.5, 0.5, 1)
for x_ in (61.5, 66):
    put('top', 'Wall Lantern', x_, 50.5, 0, z=2.5)                 # in the portal, either side of the door
g = ('box', GB, 's')
for xc in (56, 60, 68, 72):
    bay(T, g, xc, 1.5, 1, 1, 4.5)
    opening('top', T, g, xc, 'Large Ancient Window Frame', 1.5, 2)
    sill(T, g, xc, 1.25, 1.5, 0.4, 1.1)
for xc in (58.5, 64, 69.5):                                        # the oriels: window seats over the void
    ob = (xc - 2, 39, xc + 2, 41)
    T.put(T.rect(*ob) & ~T.rect(xc - 1.5, 39.5, xc + 1.5, 41), 0, 6, MOONSTONE)
    T.put(T.rect(xc - 2.5, 38.5, xc + 2.5, 41) & ~T.rect(*ob), 5.5, 6, ANCIENT)   # a cornice round its top
    T.cut(T.rect(xc - 1.5, 39.5, xc + 1.5, 42.6), 0, 5)
    opening('top', T, ('box', ob, 'n'), xc, 'Large Ancient Window Frame', 1.5, 0.5)
    for s_ in 'we':
        opening('top', T, ('box', ob, s_), 40, 'High Ancient Window Frame', 1.5, 0.5)
    for (y0_, z0_) in ((40.5, 4.5), (40, 5), (39.5, 5.5), (39, 6)):   # corbelled out under them (on the rock's slice)
        VX['rkC'].put(VX['rkC'].rect(xc - 2, y0_, xc + 2, y0_ + 0.5), z0_, 6.5, ANCIENT)
TUR = (74.5, 41.5)                                                 # the turret, corbelled out from the corner
gal_in = T.rect(55, 42.5, 73, 50)
for (r_, z0_) in ((1, 1.5), (1.5, 2), (2, 2.5)):
    T.put(T.disc(*TUR, r_) & ~gal_in, z0_, z0_ + 0.5, ANCIENT)
T.put(T.ring(*TUR, 2, 0.75) & ~gal_in, 3, 13, MOONSTONE)
T.put(T.ring(*TUR, 2, 0.5) & ~gal_in, 12.5, 13, ANCIENT)
for (b, z) in ((45, 6), (135, 9), (0, 10)):
    carve(T, ('ring', TUR, 2, b), 0, 0.25, -0.1, 0.8, z, z + 1.5, 'flat')
P.item('top', 'npc-collector', 'Alden Crowley (Collector)', 56, 44, 3, 3, 2, color='#8a6aa8')
P.zone('top', "The Collector's gallery (Alden Crowley)", 55, 42.5, 73, 50, '#8a6aa8')

# ---- the bathhouse at the spring (Elio Ricci): 14 x 14 m, 2 m walls; a deep portal with steps up to the podium
# inside, statue niches beside it; the plunge pool sunk a metre below the podium; a lantern on the roof lets the
# steam out; the spring's terrace and its weir on the east prow.
BB = (77, 57, 91, 71)
pave(box_mask(T, BB, 0.5))
T.put(box_mask(T, BB) & ~T.rect(79, 59, 89, 69), 0, 8, MOONSTONE)
band(T, BB, 0.5, 0, 1, ANCIENT)
band(T, BB, 0.5, 7, 8, ANCIENT)
PODF = M('Ancient Stone Block (the podium)', 'floor', ASTONE)


def podium_door(g, ac, name, d0):
    """A door at the podium's height (+1 m): the reveal through the wall takes the podium's floor."""
    opening('top', T, g, ac, name, 1, 2, d0=d0)
    along, depth = frame(T, g, straight=True)
    rev = (np.abs(along - ac) < OPEN_SIZE[name][0] / 2 - 1e-6) & (depth > d0) & (depth < 2)
    T.cut(rev, 0.5, 1)
    paint(up29, rev, PODF)


g = ('box', BB, 'w')
bay(T, g, 64, 2.5, 1.5, 0, 4, d0=-0.6, key=ANCIENT)
podium_door(g, 64, 'Ancients Night Door', 1.4)
for yc in (59.5, 68.5):
    bay(T, g, yc, 0.75, 0.5, 1.5, 4)                               # statue niches, a figure on a plinth in each
    T.put(T.rect(77, yc - 0.5, 77.5, yc + 0.5), 1.5, 2, ANCIENT)
    T.put(T.rect(77, yc - 0.5, 77.5, yc + 0.5), 2, 3.5, MOONSTONE)
for y_ in (60.5, 67):
    put('top', 'Wall Lantern', 76.5, y_, 90, z=3)
paint(dais, T.rect(76.5, 61.5, 77.5, 66.5), M('Ancient Stone Block (a step)', 'floor', ASTONE))
PODIUM = (T.rect(77.5, 61.5, 78.5, 66.5) | T.rect(79, 59, 89, 69)) & ~T.rect(81.5, 61.5, 86.5, 66.5)
POOL = T.rect(81.5, 61.5, 86.5, 66.5)
paint(top, POOL, WATER)
g = ('box', BB, 'e')
podium_door(g, 64, 'Round Ancient Door', -0.6)
for yc in (60.5, 67.5):
    opening('top', T, g, yc, 'High Ancient Window Frame', 2, 2)
    sill(T, g, yc, 1, 2, -0.6, 0.1)
for s in 'ns':
    g = ('box', BB, s)
    for xc in (81, 87):
        bay(T, g, xc, 1.75, 1, 1, 4.5)
        for du in (-1, 1):
            opening('top', T, g, xc + du, 'High Ancient Window Frame', 2, 2)
        sill(T, g, xc, 1.75, 2, 0.4, 1.1)
LANT = (82, 62, 86, 66)                                            # the lantern over the pool
T.put(T.rect(*LANT) & ~T.rect(82.5, 62.5, 85.5, 65.5), 8, 14, MOONSTONE)
for s, cs in (('n', (83.25, 84.75)), ('s', (83.25, 84.75)), ('w', (63.25, 64.75)), ('e', (63.25, 64.75))):
    for c_ in cs:
        carve(T, ('box', LANT, s), c_, 0.5, -0.1, 0.6, 11.5, 12.5)  # vents
# the spring's terrace at podium height, the spring sunk in it, a parapet along the rim with the weir
TERR = T.rect(89, 58, 98, 70) & INSIDE & ~box_mask(T, BB)
SPRING = T.rect(92.5, 61, 98, 66) & INSIDE
paint(top, SPRING, WATER)
T.put(PODIUM | (TERR & ~SPRING), 0, 0.5, ANCIENT)
paint(up29, PODIUM | (TERR & ~SPRING), PODF)
paint(up29, RIM & TERR & ~SPRING, ' ')
T.put(RIM & TERR & ~SPRING, 0, 2, ANCIENT)                         # the parapet; the water spills over at the weir
T.put(RIM & (T.rect(92, 59.5, 99, 61) | T.rect(92, 66, 99, 67.5)), 0, 3, ANCIENT)   # the weir's piers
for y_ in (61.5, 66):
    put('up29', 'Wall Lantern', 91, y_, 270, z=2)                  # by the spring door
P.item('up29', 'npc-barber', 'Elio Ricci (Barber)', 86.5, 66.5, 2, 2, 2, color='#9c6b8e')
P.zone('top', 'Bathhouse at the spring (Elio Ricci)', 79, 59, 89, 69, '#9c6b8e')
P.zone('top', 'The spring (a Water Dispenser feeds the falls)', 92.5, 61, 97.5, 66, '#3f6f8f')

# ---- the Alchemist's laboratory (Balthazar): a glass dome on a drum 12 m across with eight buttresses that run
# on up the glass as stone ribs; tall windows N, E and S, the door W; his flue on the north-east.
LC = (80, 79)
pave(T.disc(*LC, 7))
T.put(T.ring(*LC, 6, 1), 0, 4.5, MOONSTONE)
T.put(T.ring(*LC, 6.5, 0.5), 0, 1, ANCIENT)
T.put(T.ring(*LC, 6.5, 0.5), 4, 4.5, ANCIENT)
for k in range(8):
    b = 22.5 + 45 * k
    T.put(radial(T, LC, b, 0.5, 5.5, 7), 0, 3.5, ANCIENT)
    T.put(radial(T, LC, b, 0.5, 5.5, 6.5), 3.5, 4.5, ANCIENT)
for b in (0, 90, 180):
    opening('top', T, ('ring', LC, 6, b), 0, 'High Ancient Window Frame', 1, 1)
opening('top', T, ('ring', LC, 6, 270), 0, 'Ancient Temple Door', 0, 1, d0=-0.6)
FLUE = (84, 73.5, 85.5, 75)
T.put(T.rect(*FLUE), 0, 12.5, ANCIENT)
T.put(T.rect(83.5, 73, 86, 75.5), 12, 12.5, ANCIENT)
T.put(T.rect(*FLUE), 12.5, 13.5, COPPERB)                         # a copper cowl
for y_ in (76.5, 80.5):
    put('top', 'Large Grandleaf Cabbage Plant Pot', 72.5, y_)     # his herbs by the door
P.item('top', 'npc-alchemist', 'Balthazar (Alchemist)', 78.5, 77.5, 3, 3, 2, color='#56806c')
P.zone('top', "The Alchemist's glass dome (Balthazar)", 75, 74, 85, 84, '#56806c')

# ---- the Starspire: a slender Starlight tower 7 m across at the hall's south-west corner, by the bridge's landing,
# its west side corbelled out over the rim; a plinth, string courses, a corbelled gallery at the top round its
# observation room, slit windows climbing it, its door onto the forecourt it shares with the hall's portal.
SP = (38.5, 78)
paint(top, T.disc(*SP, 4), PAVE)                                   # (its floor runs out past the rim)
T.put(T.ring(*SP, 3.5, 1), 0, 24, STARL)
T.put(T.ring(*SP, 4, 0.5), 0, 2, ANCIENT)
for (r_, z0_) in ((2.5, 4.5), (3.5, 5), (4, 5.5)):                 # corbelled out under the overhang
    VX['rkC'].put(VX['rkC'].disc(*SP, r_) & ~INSIDE, z0_, 6.5, ANCIENT)
for z in (8, 16):
    T.put(T.ring(*SP, 4, 0.5), z, z + 0.5, ANCIENT)
T.put(T.ring(*SP, 4, 0.5), 18.5, 19, ANCIENT)                      # corbels, stepping out
T.put(T.ring(*SP, 4.5, 1), 19, 19.5, ANCIENT)
T.put(T.ring(*SP, 5, 1.5), 19.5, 20, ANCIENT)                      # the gallery
T.put(T.ring(*SP, 5, 0.5), 20, 21, ANCIENT)                        # its parapet
P.disc(sp48, *SP, 2.5, M('Starlight Block (floor)', 'floor', STAR))
for b in (45, 135, 225, 315):
    carve(T, ('ring', SP, 3.5, b), 0, 0.75, -0.1, 1.1, 20, 22)     # out onto the gallery
for (b, z) in ((270, 4), (0, 6), (150, 10), (240, 12.5), (330, 14), (60, 17.5)):
    carve(T, ('ring', SP, 3.5, b), 0, 0.25, -0.1, 1.1, z, z + 1.5, 'flat')   # slits, climbing round
opening('top', T, ('ring', SP, 3.5, 90), 0, 'Ancient Temple Door', 0, 1, d0=-1.1)
T.put(T.ring(*SP, 3.5, 0.5), 23, 23.5, STARGLOW, only='solid')    # the star band under the eaves
for b in (0, 90, 180, 270):
    px_, py_ = (round(c * 2) / 2 for c in polar(SP, 4.75, b))
    pin = T.rect(px_ - 0.5, py_ - 0.5, px_ + 0.5, py_ + 0.5) & T.ring(*SP, 5, 0.5)
    T.put(pin, 21, 22, ANCIENT)
    T.put(pin, 22, 22.5, GOLDB)
for y_ in (76, 79.5):
    put('top', 'Wall Lantern', SP[0] + 3.5, y_, 270, z=3)
P.zone('top', 'The Starspire (to +58 m)', SP[0] - 2.5, SP[1] - 2.5, SP[0] + 2.5, SP[1] + 2.5, '#585a69')

# ---- the descent: the shaft's mouth in the court, a gold parapet round it, four rune lamps standing guard
P.disc(top, *SHAFT[:2], SHAFT[2], ' ')
pave(T.ring(SHAFT[0], SHAFT[1], 6, 0.5), INLAY)                    # a ring set in the paving through the lamps
T.put(T.ring(SHAFT[0], SHAFT[1], 4, 0.5), 0, 1, GOLDB)
for b in (45, 135, 225, 315):
    cx_, cy_ = (round(c * 2) / 2 for c in polar(SHAFT, 5.5, b))
    lamp = T.rect(cx_ - 0.5, cy_ - 0.5, cx_ + 0.5, cy_ + 0.5)
    T.put(lamp, 0, 3, MOONSTONE)
    T.put(lamp, 3, 3.5, RUNE)
    T.put(lamp, 3.5, 4, GOLDB)
P.zone('top', 'The court', 52, 74, 60, 87, '#c4c8cf')
P.zone('top', 'The descent (to the forge, the vaults, the keel)', 60, 76, 68, 84, '#7e74a8')

# ---- roofs on the crown
r38 = P.roof(P.level('r38', 'Isle: the rotunda dome and the hall roof (+38 m)', 38, 12))
r38.dome(*RC, RR + 0.5, 9, 'copper', rim=0.85)
r38.ribs(*RC, [22.5 + 45 * k for k in range(8)], 0.4, 2, RR + 0.5, 'gold', proud=0.5)
r38.cut_disc(*RC, 1.5)                                             # the oculus, over the altar
r38.gable(*HB, 'y', 'castle', pitch=1.0, overhang=0.5)
r38.caps('stone', min_lower=1, min_h=6)
r38.cut(37, 62.5, 40, 65.5)                                        # (the chimney stack)
r38.cut_disc(*SP, 3.6)                                             # (the Starspire, at the corner)
r38.paint()
# the lantern on the dome round the oculus, its copper cap and a gold finial
LR = T.ring(*RC, 2.5, 1)
lz0 = np.full(LR.shape, 19.0)
for y, x in zip(*np.nonzero(LR)):
    lz0[y, x] = 10 + (r38.top(x, y) or 9)
T.put(LR, lz0, 22.5, MOONSTONE)
for b in (0, 90, 180, 270):
    carve(T, ('ring', RC, 2.5, b), 0, 0.75, -0.1, 1.1, 20, 21.5)
rcap = P.roof(P.level('r50', "Isle: the lantern's cap (+50.5 m)", 50.5, 5))
rcap.cone(*RC, 2.5, 2.5, 'copper', overhang=0.5)
rcap.paint()
ztop = 50.5 - 28 + max(rcap.h.values())
T.put(T.rect(RC[0] - 0.5, RC[1] - 0.5, RC[0] + 0.5, RC[1] + 0.5), ztop, ztop + 1.5, GOLDB)
r36 = P.roof(P.level('r36', 'Isle: the gallery and bathhouse roofs (+36 m)', 36, 10))
r36.gable(*GB, 'x', 'castle', pitch=1.0, overhang=0.5)
r36.gable(61.5, 46, 66.5, 52, 'y', 'castle', pitch=1.0, overhang=0.5, base=2.5)   # the frontispiece's cross gable
r36.cut_disc(*TUR, 2.1)
r36.hip(*BB, 'castle', pitch=0.5, overhang=0.5)
r36.caps('stone', min_lower=1, min_h=4)
r36.cut(*LANT)
r36.paint()
r42 = P.roof(P.level('r42', "Isle: the bath lantern's roof (+42 m)", 42, 4))
r42.hip(*LANT, 'castle', pitch=1.0, overhang=0.5)
r42.paint()
r41 = P.roof(P.level('r41', "Isle: the gallery turret's cone (+41 m)", 41, 6))
r41.cone(*TUR, 2, 4, 'castle', overhang=0.5)
r41.paint()
r35 = P.roof(P.level('r35', "Isle: the stage apse's roof (+35 m)", 35, 6))
r35.cone(*AP, 5.5, 4, 'castle', overhang=0.5)
r35.cut(37, 53, 53, 62)
r35.paint()
r34 = P.roof(P.level('r34', "Isle: the gallery oriels' roofs (+34 m)", 34, 3))
for xc in (58.5, 64, 69.5):
    r34.shed(xc - 2, 39, xc + 2, 41, 's', 'castle', pitch=1.0, overhang=0.5)
r34.cut(50, 41, 80, 43)
r34.paint()
r325 = P.roof(P.level('r325', "Isle: the Alchemist's glass dome (+32.5 m)", 32.5, 8))
r325.dome(*LC, 6.5, 5.5, 'glass', rim=0.85)
r325.ribs(*LC, [22.5 + 45 * k for k in range(8)], 0.4, 1, 6.5, 'stone', proud=0.5)
r325.cut(*FLUE)
peak = max(r325.h.values())
for (x, y) in list(r325.h):
    if P.dist(x, y, *LC) < 1:
        r325.put(x, y, peak + 0.5, 'stone', 'set')                 # the boss where the ribs meet
r325.paint()
r52 = P.roof(P.level('r52', 'Isle: the Starspire roof (+52 m)', 52, 8))
r52.cone(*SP, 3.5, 6, 'castle', overhang=1.0, flare=(1, 0.5))
r52.paint()
ztop = 52 - 28 + max(r52.h.values())
T.put(T.rect(SP[0] - 0.5, SP[1] - 0.5, SP[0] + 0.5, SP[1] + 0.5), ztop, ztop + 1.5, GOLDB)
# finials: stone with a gold tip on the hall's gables and the gallery's cross gable, gold on the smaller roofs
for (rf, el, r_, parts) in ((r38, 38, (44.5, 52.5, 45.5, 53), ((1, ANCIENT), (0.5, GOLDB))),
                            (r38, 38, (44.5, 75, 45.5, 75.5), ((1, ANCIENT), (0.5, GOLDB))),
                            (r36, 36, (63.5, 52, 64.5, 52.5), ((1, ANCIENT), (0.5, GOLDB))),
                            (r41, 41, (74, 41, 75, 42), ((1, GOLDB),)),
                            (r42, 42, (83.5, 63.5, 84.5, 64.5), ((1, GOLDB),)),
                            (r325, 32.5, (79.5, 78.5, 80.5, 79.5), ((1, GOLDB),))):
    finial(T, *r_, roof_top(rf, el, *r_) - 28, parts)

# ================================================================= the chain bridge: from the stair tower's top to the isle's SW rim
LANDING = (42, 84)
BRIDGE = M('Ancient Stone Block (the chain bridge)', 'floor', ASTONE)
TOPT = (16.5, 90.5, 29.5, 103.5)                                   # the stair tower's top
BR = np.zeros_like(INSIDE)
for x, y, t in line_squares(((TOWER[0] + TOWER[2]) / 2, (TOWER[1] + TOWER[3]) / 2), LANDING, 1.75):
    BR[y, x] = True
BR &= ~INSIDE
paint(top, BR | T.rect(*TOPT), BRIDGE)
_e = BR.copy()
for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    _e &= np.roll(np.roll(BR | INSIDE | T.rect(*TOPT), dy, 0), dx, 1)
T.put(BR & ~_e & ~T.rect(*TOPT), 0, 1, ANCIENT)                    # parapets along the bridge
T.put(T.rect(*TOPT) & ~T.rect(17, 91, 29, 103) & ~BR, 0, 1, ANCIENT)   # and round the tower's top
for (cx_, cy_) in ((17, 91), (29, 91), (17, 103), (29, 103)):
    T.put(T.rect(cx_ - 0.5, cy_ - 0.5, cx_ + 0.5, cy_ + 0.5) & T.rect(*TOPT), 0, 2.5, ANCIENT)   # pinnacles
    T.put(T.rect(cx_ - 0.5, cy_ - 0.5, cx_ + 0.5, cy_ + 0.5) & T.rect(*TOPT), 2.5, 3, GOLDB)
P.zone('top', 'The chain bridge (from the stair tower)', 28, 84, 40, 94, '#a39e92')

# ================================================================= inside the rock: the craftspeople there
P.item('rkC', 'npc-blacksmith', 'Oswald Anders (Blacksmith)', 47, 55, 3, 3, 2, color='#5f6770')
P.item('rkC', 'large-water-wheel', 'Large Water Wheel (turning the mill)', 96, 61, 5, 1, 5, 90, color='#8a7a6a')

# ================================================================= the waterfall: off the east rim, past the wheel, into the lake
FALL = M('Water (the falls: real water from the spring, in game)', 'block', WATERC, TOP - 0.5)
P.rect(falls, 97, 62, 98.5, 65, FALL)
P.zone('lake', 'Where the falls land', 95, 60, 100, 67, '#3f6f8f')

# ================================================================= the ground (0 m)
ROADC = M('Ancient Road Block', 'floor', ROAD)
FIELD = M('Fertilised Farm Soil', 'floor', SOIL)
WOODF = M('Refined Wood Block (floor)', 'floor', '#75675f')
G = vox('ground')
# the arrival: a road from the south edge through the moon gate, a plaza under the isle's south rim
P.rect(gnd, 57, 104, 63, 124, ROADC)
P.rect(gnd, 28, 90, 76, 104, ROADC)
P.zone('ground', 'The moon gate (the way in)', 53, 107, 67, 111, '#c4c8cf')
P.zone('ground', 'The plaza, under the isle', 29, 91, 75, 103, '#8b8577')

# ---- the moon gate: a Moonstone wall 12 m long, a round opening 7 m across through it, a rune keystone
GT = (53, 108, 67, 110)
P.rect(gnd, 52.5, 107.5, 67.5, 110.5, ROADC)
G.put(G.rect(*GT), 0, 10, MOONSTONE)
band(G, GT, 0.5, 0, 1, ANCIENT, keep=np.abs(G.mx - 60) > 1.5)
band(G, GT, 0.5, 9.5, 10, ANCIENT)
dxg = G.mx - 60
half = np.sqrt(np.maximum(0, 4 ** 2 - dxg ** 2))
G.put(G.rect(*GT) & (np.abs(dxg) < 4), np.where(np.abs(dxg) < 1.5, 0, snap(4 - half)), snap(4 + half), 0)
for s_ in 'ns':
    round_frame(G, ('box', GT, s_), 60, 4, 4, 4.5)
G.put(G.rect(59.5, 108, 60.5, 110), 8, 8.5, RUNE)
for x_ in (55.5, 64):
    put('ground', 'Ground Lantern II', x_, 111)

# ---- Mei-Yin Chen's stall: an open-fronted booth on the plaza, a counter, a deep tiled awning on posts
SB = (66, 100, 74, 106)
P.rect(gnd, 64, 100, 74.5, 106.5, ROADC)
G.put(G.rect(73.5, 100, 74, 106) | G.rect(66.5, 100, 74, 100.5) | G.rect(66.5, 105.5, 74, 106), 0, 3.5, TIMB)
for (px, py) in ((66, 100), (66, 105.5), (64.5, 100), (64.5, 105.5)):
    G.put(G.rect(px, py, px + 0.5, py + 0.5), 0, 3.5, TWOOD)
G.put(G.rect(67, 101.5, 67.5, 104.5), 0, 1, RWOOD)                 # the counter (a way round each end)
P.item('ground', 'npc-trader', 'Mei-Yin Chen (trader)', 69, 101.5, 3, 3, 2, color='#c4501a')
for y_ in (101.5, 104):
    put('ground', 'Hanging Lantern', 65, y_, z=3)
put('ground', 'Wooden Crate', 72.5, 101)
put('ground', 'Supply Sacks I', 72.5, 104)
P.zone('ground', "Mei-Yin Chen's stall", 66.5, 100.5, 73.5, 105.5, '#c4501a')

# ---- the stair tower (SW): 12 x 12 m, 2 m walls, carrying the stair up to the bridge (and, hidden, the stair down);
# clasping buttresses at its corners in two stages, a deep portal to the plaza, slits climbing with the stair,
# a corbelled crown, and the bridge's head on top with a parapet and pinnacles.
P.rect(gnd, TOWER[0] - 1, TOWER[1] - 1, TOWER[2] + 1, TOWER[3] + 1, ROADC)
G.put(G.rect(*TOWER) & ~G.rect(19, 93, 27, 101), 0, 27.5, PGRAN)
band(G, TOWER, 0.5, 0, 1.5, ANCIENT)
for (cx_, cy_, sx, sy) in ((17, 91, -1, -1), (29, 91, 1, -1), (17, 103, -1, 1), (29, 103, 1, 1)):
    for (pr, z0_, z1_) in ((1, 0, 12), (0.5, 12, 20)):
        xa, xb = (cx_ - 1.5, cx_ + pr) if sx > 0 else (cx_ - pr, cx_ + 1.5)
        ya, yb = (cy_ - 1.5, cy_ + pr) if sy > 0 else (cy_ - pr, cy_ + 1.5)
        G.put(G.rect(xa, ya, xb, yb), z0_, z1_, PGRAN)
band(G, TOWER, 0.5, 20, 20.5, ANCIENT)                             # a string course where the buttresses stop
cor = box_mask(G, TOWER, 0.5) & ~box_mask(G, TOWER)
G.put(cor & ((np.floor(G.mx * 2) + np.floor(G.my * 2)) % 2 == 0), 25.5, 26, ANCIENT)   # corbels
G.put(cor, 26, 27.5, ANCIENT)
g = ('box', TOWER, 'e')
bay(G, g, 97, 2.5, 1.5, 0, 4, d0=-0.6, key=ANCIENT)
opening('ground', G, g, 97, 'Metal Bound Wooden Double Door', 0, 2, d0=1.4)
for y_ in (93.5, 100):
    put('ground', 'Wall Lantern', 29, y_, 270, z=3)
for (s, a, z) in (('n', 23, 5), ('e', 93.5, 9), ('s', 23, 13), ('w', 97, 17), ('n', 20, 21), ('e', 100.5, 23.5)):
    carve(G, ('box', TOWER, s), a, 0.25, -0.1, 2.1, z, z + 2, 'flat')
P.zone('ground', 'The stair tower (up to the bridge, and the hidden stair down)', 19, 93, 27, 101, '#626c7a')

# ---- the farm (Emily Fray): the farmhouse, stone below and jettied half-timber above, a thatched roof, its
# chimney on the east gable; pens and fields
P.rect(gnd, 80, 106, 122, 122, FIELD)
FB = (88, 88, 110, 100)
P.rect(gnd, *FB, WOODF)
P.rect(gnd, 87.5, 87, 112, 101, ROADC, only=(' ',))
G.put(G.rect(*FB) & ~G.rect(89, 89, 109, 99), 0, 3.5, RSTONE)
UPB = (88, 87.5, 110, 100.5)
G.put(G.rect(*UPB) & ~G.rect(88.5, 88, 109.5, 100), 3.5, 7, TIMB)
G.put(G.rect(88, 87.5, 110, 88) | G.rect(88, 100, 110, 100.5), 3, 3.5, TWOOD)   # the jetty's beams
P.rect(up35, 88.5, 88, 109.5, 100, WOODF)
G.put(G.rect(110, 92.5, 111.5, 95.5), 0, 15.5, RSTONE)              # the chimney
G.put(G.rect(110, 92, 112, 96), 15, 15.5, RSTONE)
opening('ground', G, ('box', FB, 's'), 99, 'Wooden Door', 0, 1)
for px in (97, 100.5):                                             # the porch's posts
    G.put(G.rect(px, 102.5, px + 0.5, 103), 0, 2.5, RWOOD)
P.rect(gnd, 97, 100, 101, 103, M('Rough Wood Block (the porch)', 'floor', '#7a6653'))
DORM_B = (102.5, 98, 106.5, 100.5)                                 # the dormer: its front runs up from the jettied wall
G.put(G.rect(*DORM_B) & ~G.rect(103, 98, 106, 100), 7, 9.5, TIMB)
opening('ground', G, ('box', DORM_B, 's'), 104.5, 'Wooden Window Frame', 7.5, 0.5)
for s in 'ns':
    for xc in (92, 96, 102, 106) if s == 's' else (92, 96, 99, 106):
        opening('ground', G, ('box', FB, s), xc, 'Wooden Window Frame', 1, 1)
    for xc in (91, 95, 99, 103, 107) if s == 'n' else (91, 95, 108):
        opening('ground', G, ('box', UPB, s), xc, 'Wooden Window Frame', 4.5, 0.5)
for xc in (92, 96, 102, 106):                                      # shutters on the south front
    G.put(G.rect(xc - 1, 100, xc - 0.5, 100.5) | G.rect(xc + 0.5, 100, xc + 1, 100.5), 1, 2.5, TWOOD)
for xc in (91, 95, 108):
    G.put(G.rect(xc - 1, 100.5, xc - 0.5, 101) | G.rect(xc + 0.5, 100.5, xc + 1, 101), 4.5, 6, TWOOD)
G.put(G.rect(110.5, 93.5, 111, 94.5), 15.5, 16.5, BRICK)           # the chimney pot
put('ground', 'Wall Lantern', 100.5, 100, 0, z=2)
for x_ in (97.5, 100):
    put('ground', 'Small Aurora Beans Plant Pot', x_, 100)
opening('ground', G, ('box', FB, 'w'), 94, 'Wooden Window Frame', 1, 1)
opening('ground', G, ('box', UPB, 'w'), 94, 'Wooden Window Frame', 4.5, 0.5)
P.rect(gnd, 78, 88, 87, 104, M('Rough Wood Block (pens)', 'floor', '#7a6653'))
P.item('ground', 'npc-farmer', 'Emily Fray (Farmer)', 101.5, 95.5, 3, 3, 2, color='#7c9a3d')
P.zone('ground', 'Farmhouse and kitchen (Emily Fray)', 89, 89, 109, 99, '#7c9a3d')
P.zone('ground', 'Fields and beehives', 80, 106, 122, 122, '#7c9a3d')
P.zone('ground', 'Pens', 78, 88, 87, 104, '#7c9a3d')

# ---- the Hunter's lodge (Athalan Skree): log walls on a stone course, the logs crossing past the corners, a stone
# chimney on the west gable, a porch to the east; the tannery yard
LB = (6, 44, 28, 58)
P.rect(gnd, *LB, WOODF)
lodge_w = G.rect(*LB) & ~G.rect(7, 45, 27, 57)
G.put(lodge_w, 0, 1, RSTONE)
G.put(lodge_w, 1, 5, RWOOD)
for k in range(8):                                                 # log ends, every other course each way
    z = 1 + 0.5 * k
    ends = ((G.rect(28, 44, 28.5, 45) | G.rect(5.5, 44, 6, 45) | G.rect(5.5, 57, 6, 58) | G.rect(28, 57, 28.5, 58))
            if k % 2 == 0 else
            (G.rect(27, 43.5, 28, 44) | G.rect(6, 43.5, 7, 44) | G.rect(6, 58, 7, 58.5) | G.rect(27, 58, 28, 58.5)))
    G.put(ends, z, z + 0.5, RWOOD)
G.put(G.rect(4.5, 49.5, 6, 52.5), 0, 14.5, RSTONE)                  # the chimney
G.put(G.rect(4, 49, 6, 53), 14, 14.5, RSTONE)
carve(G, ('box', LB, 'w'), 51, 1.5, 0.4, 1.1, 0, 2, 'flat')        # the hearth
opening('ground', G, ('box', LB, 'e'), 51, 'Wooden Double Door', 0, 1)
for yc in (46.5, 55.5):
    opening('ground', G, ('box', LB, 'e'), yc, 'Wooden Window Frame', 2, 1)
for s in 'ns':
    for xc in (10, 15, 20, 24.5):
        opening('ground', G, ('box', LB, s), xc, 'Wooden Window Frame', 2, 1)
P.rect(gnd, 28, 47, 31, 55, M('Rough Wood Block (the porch)', 'floor', '#7a6653'))
for py in (47, 54.5):
    G.put(G.rect(30.5, py, 31, py + 0.5), 0, 3, RWOOD)
put('ground', 'Bow and Arrow Wall Mount', 28, 50, 270, z=4)
put('ground', 'Rustic Bench', 28, 47, 270)
put('ground', 'Resource Bundle I', 29, 53.5)
put('ground', 'Wall Lantern', 28, 53.5, 270, z=2.5)
P.rect(gnd, 6, 60, 28, 76, ROADC)
P.item('ground', 'npc-hunter', 'Athalan Skree (Hunter)', 12, 48, 3, 3, 2, color='#6d7a45')
P.zone('ground', 'Hunting lodge (Athalan Skree)', 7, 45, 27, 57, '#6d7a45')
P.zone('ground', 'Tannery yard and drying racks', 6, 60, 28, 76, '#6d7a45')

# ---- the Carpenter's workshop (Cade Hawthorn): half-timber on a stone course, a wagon entrance under a heavy beam,
# a hoist gable over it with its loading door and beam; the timber yard
CB = (46, 6, 70, 18)
P.rect(gnd, *CB, ROADC)
cw = G.rect(*CB) & ~G.rect(47, 7, 69, 17)
G.put(cw, 0, 1, RSTONE)
G.put(cw, 1, 6, TIMB)
g = ('box', CB, 's')
G.put(G.rect(54, 17, 62, 18), 6, 7.5, TIMB)                        # the hoist gable's wall
carve(G, g, 58, 2.5, -0.1, 1.1, 0, 4.5, 'flat')                    # the wagon entrance
carve(G, g, 58, 3, -0.1, 1.1, 4.5, 5, 'flat', m=G.mat(*TWOOD))     # its beam
carve(G, g, 58, 1, -0.1, 1.1, 5, 7.5, 'flat')                     # the loading hatch (open)
G.put(G.rect(57.5, 18, 58.5, 19.5), 9, 9.5, TWOOD)                 # the hoist beam
G.put(G.rect(58, 19, 58.5, 19.5), 6, 9, IRON)                      # its chain and hook
for x_ in (54.5, 61):
    put('ground', 'Wall Lantern', x_, 18, 0, z=3)
for x_ in (47, 48):
    put('ground', 'Resource Bundle II', x_, 18.5)
for xc in (50, 66):
    opening('ground', G, g, xc, 'Wooden Window Frame', 2, 1)
for xc in (50, 55, 61, 66):
    opening('ground', G, ('box', CB, 'n'), xc, 'Wooden Window Frame', 2, 1)
P.rect(gnd, 40, 18, 88, 38, ROADC)
P.item('ground', 'npc-carpenter', 'Cade Hawthorn (Carpenter)', 50, 10, 3, 3, 2, color='#9a7344')
P.zone('ground', "Carpenter's workshop (Cade Hawthorn)", 47, 7, 69, 17, '#9a7344')
P.zone('ground', 'Timber yard (a crane on the rim above lifts to the crown)', 40, 18, 88, 38, '#9a7344')

# ---- the Fisher (Captain Melville Fontane): the boathouse, stone below and tarred wood above, its water door under
# a round window in the lake-side gable, the jetty out from it
BHB = (102, 60, 116, 72)
P.rect(gnd, *BHB, WOODF)
bw = G.rect(*BHB) & ~G.rect(103, 61, 115, 71)
G.put(bw, 0, 2, RSTONE)
G.put(bw, 2, 6, TWOOD)
g = ('box', BHB, 'w')
G.put(G.rect(102, 66, 103, 69), 6, 9, TWOOD)                       # the gable's middle, run up for the window
carve(G, g, 67.5, 2.5, -0.1, 1.1, 0, 3.5)                          # the water door (south of where the falls land)
opening('ground', G, g, 67.5, 'Round Wooden Window Frame', 7, 1)
opening('ground', G, ('box', BHB, 'e'), 66, 'Wooden Door', 0, 1)
for s in 'ns':
    for xc in (106, 112):
        opening('ground', G, ('box', BHB, s), xc, 'Wooden Window Frame', 2.5, 1)
P.rect(lake, 94, 66, 102, 69, M('Tarred Wood Block (the jetty)', 'floor', '#5d5652'))
put('ground', 'Wall Lantern', 116, 64, 270, z=2)
put('ground', 'Fish Trophy Board', 116, 65.5, 270, z=3)
put('lake', 'Standing Wooden Barrel', 99, 66)
put('lake', 'Wooden Crate', 100, 66)
LV = vox('lake')                                                   # the rowing boat, its bow pointing out
hull = LV.rect(92.5, 69.5, 96.5, 71) & ~(LV.rect(92.5, 69.5, 93, 70) | LV.rect(92.5, 70.5, 93, 71))
LV.put(hull & ~LV.rect(93, 70, 96, 70.5), 0, 1, TWOOD)
LV.put(LV.rect(93, 70, 96, 70.5), 0, 0.5, RWOOD)
P.item('ground', 'npc-fisher', 'Captain Melville Fontane (Fisher)', 108, 62, 3, 3, 2, color='#3f7f9e')
P.zone('ground', "The Fisher's boathouse (Captain Melville Fontane)", 103, 61, 115, 71, '#3f7f9e')

# ---- ground roofs
gr5 = P.roof(P.level('gr5', "Ground: the lodge's roof (+5 m)", 5, 10))
gr5.gable(*LB, 'x', 'lead', pitch=1.0, overhang=0.5)
gr5.cut(4.5, 49.5, 6, 52.5)
gr5.paint()
gr3 = P.roof(P.level('gr3', "Ground: the lodge's porch (+3 m)", 3, 3))
gr3.shed(28, 46.5, 31, 55.5, 'w', 'lead', pitch=0.5, overhang=0.5)
gr3.cut(26, 44, 28.5, 58)
gr3.paint()
gr6 = P.roof(P.level('gr6', 'Ground: the workshop and boathouse roofs (+6 m)', 6, 10))
gr6.gable(*CB, 'x', 'granite', pitch=1.0, overhang=0.5)
gr6.gable(54, 11, 62, 18, 'y', 'granite', pitch=1.0, overhang=0.5, base=1.5)
gr6.gable(*BHB, 'x', 'lead', pitch=1.0, overhang=0.5)
gr6.paint()
finial(G, 101.5, 65.5, 102, 66.5, roof_top(gr6, 6, 101.5, 65.5, 102, 66.5), ((1, TWOOD),))   # the lake gable's
gr7 = P.roof(P.level('gr7', "Ground: the farmhouse's thatch (+7 m)", 7, 10))
gr7.gable(*UPB, 'x', 'straw', pitch=1.0, overhang=0.5)
gr7.cut(110, 92.5, 112, 95.5)
gr7.cut(*DORM_B)
gr7.paint()
gr95 = P.roof(P.level('gr95', "Ground: the farmhouse dormer's roof (+9.5 m)", 9.5, 3))
gr95.gable(102.5, 96, 106.5, 100.5, 'y', 'straw', pitch=1.0, overhang=0.5)
gr95.cut(100, 90, 110, 97)                                         # (it dies into the thatch)
gr95.paint()
gr25 = P.roof(P.level('gr25', "Ground: the farmhouse porch's roof (+2.5 m)", 2.5, 3))
gr25.gable(97, 100.5, 101, 103, 'y', 'straw', pitch=1.0, overhang=0.5)
gr25.cut(95, 99, 103, 100.5)
gr25.paint()
gr35 = P.roof(P.level('gr35', "Ground: the stall's awning (+3.5 m)", 3.5, 3))
gr35.shed(64.5, 100, 74, 106, 'e', 'tiles', pitch=0.5, overhang=0.5)
gr35.paint()
gr9 = P.roof(P.level('gr9', "Ground: the moon gate's coping (+10 m)", 10, 3))
gr9.gable(*GT, 'x', 'granite', pitch=1.0, overhang=0.5)
gr9.paint()

# ================================================================= the anchor pylons and their chains
# Stepped obelisks of polished granite on Ancient Stone steps, a gold pyramidion, a rune glowing at the back of
# a recessed panel on each face.
PV = vox('pyl')
for key, (px, py) in PYLONS.items():
    for (hw, z0_, z1_, m) in ((3.5, 0, 0.5, ANCIENT), (3, 0.5, 1, ANCIENT), (2.5, 1, 4, PGRAN), (2, 4, 7, PGRAN),
                             (1.5, 7, 9, PGRAN), (1, 9, 9.5, GOLDB), (0.5, 9.5, 10.5, GOLDB)):
        PV.put(PV.rect(px - hw, py - hw, px + hw, py + hw), z0_, z1_, m)
    pb = (px - 2.5, py - 2.5, px + 2.5, py + 2.5)
    for s in 'nsew':
        a = px if s in 'ns' else py
        carve(PV, ('box', pb, s), a, 0.5, -0.1, 0.5, 1.5, 3.5, 'pointed')
        carve(PV, ('box', pb, s), a, 0.5, 0.4, 1, 1.5, 3.5, 'pointed', m=PV.mat(*RUNE))
    P.zone('pyl', f'Rune pylon ({key.upper()})', px - 2.5, py - 2.5, px + 2.5, py + 2.5, '#6c9dc3')
    # the chain: from the pylon's head (+11 m) up to the isle's rim underside (+23 m), taut
    ang = math.atan2(py - IC[1], px - IC[0])
    r = 0
    while inside(IC[0] + r * math.cos(ang), IC[1] + r * math.sin(ang)):
        r += 0.25
    rim = (IC[0] + (r - 1) * math.cos(ang), IC[1] + (r - 1) * math.sin(ang))
    for x, y, t in line_squares((px, py), rim, 0.5):
        z = 11 + t * (RIM_UNDER - 11)
        z = round(z * 2) / 2
        chain[y][x] = M('Iron Block (a chain)', 'block', '#848483', 1, z)

# ================================================================= hidden below: the summoning chamber under the lake
# A round chamber 24 m across: Midnight Tomb walls with twelve pilasters and niches between them (the four facing
# the compass glow), a stepped dome with the oculus at its top, the circle sunk two steps into the floor.
CC = (64, 79.5)
D = vox('deep')
DFLOOR = M('Ancient Dungeon Block (floor)', 'floor', DUNGEON)
P.disc(deep, *CC, 12, DFLOOR)
P.disc(deep, *CC, 6, M('Dug out (the sunken circle)', 'dig', '#3a3a3a'))
P.disc(deep_step, *CC, 6, M('Ancient Dungeon Block (the step)', 'floor', DUNGEON), r_in=5)
P.disc(deep_sunk, *CC, 5, M('Ancient Circles Block (the summoning circle)', 'floor', CIRCLES))
D.put(D.ring(*CC, 12, 1.5), 0, 10, TOMBB)
dd = np.hypot(D.mx - CC[0], D.my - CC[1])
DOME = (dd < 10.5) & (dd >= 3)
D.put(DOME, np.minimum(10, 6 + snap(4 * np.sqrt(np.maximum(0, 1 - (dd / 10.5) ** 2)))), 10, TOMBB)
for k in range(12):
    D.put(radial(D, CC, 15 + 30 * k, 0.75, 9.5, 10.6), 0, 7, TOMBB)  # pilasters
    g = ('ring', CC, 12, 30 * k)
    carve(D, g, 0, 1.25, 0.75, 1.6, 0.5, 3.5)                       # niches
    if k % 3 == 0:
        carve(D, g, 0, 1.25, 0.25, 0.75, 1, 3.5, m=D.mat(*RUNE))   # the four facing the compass glow
P.rect(deep, 62, 90, 66, 92.5, DFLOOR)                             # the way in from the passage
opening_arch = carve(D, ('ring', CC, 12, 180), 0, 2, -0.6, 1.6, 0, 4)
P.zone('deep', 'The summoning chamber', 54, 70, 74, 90, '#7e74a8')
# the oculus: a shaft from the chamber's ceiling to a glass disc in the lake bed, the isle's keel above it
P.disc(ocul, *CC, 3, M('Dug out (the oculus shaft)', 'dig', '#3a3a3a'))
P.disc(oculg, *CC, 3, M('Glass (the oculus)', 'block', '#a9d8e6', 0.5))
# the hidden passage from the stair tower's shaft: vaulted, with ribs every 4 m and rune lamps in niches
P.disc(deep, 23, 97, 3.5, DFLOOR)
P.disc(ugs, 23, 97, 3.5, M('Dug out (the secret stair)', 'dig', '#3a3a3a'))
Dc = vox('deepc')
PAS = Dc.rect(25, 94, 67, 100) | Dc.rect(61, 91, 67, 94)
PAS_IN = Dc.rect(25, 95, 66, 99) | Dc.rect(62, 91, 66, 95)
paint(deepc, PAS, DFLOOR)
Dc.put(PAS & ~PAS_IN & ~Dc.disc(23, 97, 3.5), 0, 6, DUNGB)
rib = (np.floor(Dc.mx) % 4 == 1)
ceil_ew = vault('x', 95, 99, 3, 5, Dc) - np.where(rib, 0.5, 0)
ceil_ns = vault('y', 62, 66, 3, 5, Dc) - np.where(np.floor(Dc.my) % 4 == 1, 0.5, 0)
Dc.put(PAS_IN & (Dc.my >= 95) & ~Dc.disc(23, 97, 3.6), ceil_ew, 6, DUNGB)   # (not over the secret stair's shaft)
Dc.put(PAS_IN & (Dc.my < 95), ceil_ns, 6, DUNGB)
for (s, a) in (('n', 33), ('s', 45), ('n', 53)):
    carve(Dc, ('box', (25, 94, 67, 100), s), a, 0.5, 0.4, 1.1, 1.5, 2.5, 'flat')
    carve(Dc, ('box', (25, 94, 67, 100), s), a, 0.5, -0.1, 0.4, 1.5, 2.5, 'flat', m=Dc.mat(*RUNE))
P.zone('deepc', 'The hidden passage', 26, 95, 62, 99, '#7e74a8')
# Loraine's study off it: shelves in niches down both walls, a barrel vault, her reading dais
SB2 = (32, 99, 46, 111)
paint(deepc, Dc.rect(*SB2), DFLOOR)
Dc.put(Dc.rect(*SB2) & ~Dc.rect(33, 100, 45, 110), 0, 6, DUNGB)
Dc.put(Dc.rect(33, 100, 45, 110), vault('y', 33, 45, 4, 6, Dc), 6, DUNGB)
carve(Dc, ('box', SB2, 'n'), 39, 1.25, -0.1, 1.1, 0, 2.5)          # the way in from the passage
for s in 'we':
    for yc in ((102.5, 105.5, 108.5) if s == 'w' else (102.5, 105.5)):
        carve(Dc, ('box', SB2, s), yc, 1, 0.4, 1.1, 0.5, 3, 'flat')   # shelf niches
paint(deep_dais, Dc.rect(36, 107, 42, 110), M('Ancient Stone Block (the dais)', 'floor', ASTONE))
P.item('deepc', 'npc-researcher', 'Loraine Crim (Ancient Researcher)', 40.5, 102.5, 3, 3, 2, color='#56806c')
P.zone('deepc', "Loraine's study (Loraine Crim)", 33, 100, 45, 110, '#56806c')

# ================================================================= pass 3: the stairs, the crane, the furnishing and the small things
# Spiral stairs are block treads, one block thick, each a block higher and a step further round; a stair that passes
# through several levels puts each tread on the level whose height holds it (vabs). Furniture, stations and lights
# go in by game name (put) or by the planner's library type (lib); their sizes are estimates until measured.
LIB.update({'mattress': ('Crude Mattress', 1, 2, 1), 'mchest-huge': ('Huge Magic Chest', 2.5, 1.5, 1.5),
            'mchest-enormous': ('Enormous Magic Chest', 3, 1.5, 1.5), 'fishing': ('Fishing spot', 2, 2, 1)})
ITEM.update({'Wooden Chair': (1, 1, 1), 'Ground Lantern I': (0.5, 0.5, 1.5), 'Crypt Skull Torch': (0.5, 0.5, 1.5),
             'Shield Wall Mount': (1, 0.5, 1), 'Supply Sacks III': (1, 1, 1), 'Water Dispenser': (1, 1, 1),
             'Secret Stone Floor Passage': (2, 2, 0.5), 'Big Farm Animal Pillow': (2, 2, 0.5)})
MOUNT.update({'Shield Wall Mount': 'wall'})
CARPET = M('Red Carpet Block (a carpet)', 'floor', '#9e3742')
FLOWERS = M('Flower Soil (a flower bed)', 'floor', '#a77e63')
STRAW = ('Straw Roof Block', '#a7753d')
PLAIT = ('Plaited Block', '#867561')


def lib(lid, typ, x, y, rot=0, z=None, label=None, h=None):
    """A planner library item (chests, beds, stations) by type, the top-left of its footprint at x, y."""
    nm, w, d, hh = LIB[typ]
    color = LIB_COLOR.get(typ, '#7b68b5' if 'mchest' in typ else '#8c6b4f')
    return P.item(lid, typ, label or nm, x, y, w, d, h or hh, rot, color, z=z)


def vabs(mask, z0, z1, m, lids):
    """Fill voxels between absolute heights z0 and z1, each level in lids taking the part its height holds."""
    for lid in lids:
        v = vox(lid)
        el = v.L['elev']
        a, b = max(z0, el), min(z1, el + v.height)
        if b > a:
            v.put(mask, a - el, b - el, m)


def bearings(c, b0, b1):
    """Squares whose bearing from c lies between b0 and b1 (clockwise)."""
    ang = np.degrees(np.arctan2(T.mx - c[0], -(T.my - c[1]))) % 360
    return ((ang - b0) % 360) < ((b1 - b0) % 360)


def spiral(c, r0, r1, z_bottom, n, step, theta0, m, lids):
    """A spiral stair round c: n treads between r0 and r1, the first one's top at z_bottom + 0.5 (absolute), each a
    block higher and `step` degrees further round (negative: anticlockwise), the first starting at bearing theta0.
    Returns [(i, squares, top)] for each tread."""
    d = np.hypot(T.mx - c[0], T.my - c[1])
    ring_ = (d >= r0) & (d <= r1)
    out = []
    for i in range(1, n + 1):
        a0 = theta0 + (i - 1) * step
        lo = a0 + min(0, step)
        sec = ring_ & bearings(c, lo % 360, (lo + abs(step)) % 360)
        top_ = z_bottom + 0.5 * i
        vabs(sec, top_ - 0.5, top_, m, lids)
        out.append((i, sec, top_))
    return out


def door_in_rock(lid, name, x0, y0, x1, y1):
    """A door item in an opening cut through the rock (the rock over it holds it)."""
    return P.opening(lid, name, x0, y0, x1, y1, OPEN_SIZE[name][1], 0)


# ---- the stair tower: a spiral up round a granite newel to the bridge's head (55 treads, 2.9 m wide), lanterns in the
# corners; under its floor, behind a secret stone hatch, the hidden spiral down to the passage (-16 m)
TC = ((TOWER[0] + TOWER[2]) / 2, (TOWER[1] + TOWER[3]) / 2)
UP = spiral(TC, 1, 3.9, 0, 55, 18, 180, ANCIENT, ['ground'])
vox('ugs')
vabs(T.disc(*TC, 0.9), -16, 27.5, PGRAN, ['deep', 'ugs', 'ground'])   # the newel, from the passage to the top
for i, sec, t_ in UP[50:]:
    paint(top, sec, ' ')                                           # the way out onto the bridge's head
DOWN = spiral(TC, 1, 3.5, -16, 31, 18, 228, DUNGB, ['deep', 'ugs'])     # (its top step by the door, curling away from it as it goes down)
OPEN_D = np.zeros_like(INSIDE)
for i, sec, t_ in DOWN[25:]:
    OPEN_D |= sec
    paint(gnd, sec, ' ')                                           # the opening, where the secret floor goes
_ys, _xs = np.nonzero(OPEN_D)
P.zone('ground', 'Secret floor (a Secret Stone Floor Passage) over the hidden stair', _xs.min() / 2, _ys.min() / 2,
       _xs.max() / 2 + 0.5, _ys.max() / 2 + 0.5, '#7e74a8')
for (x_, y_, z) in ((19, 93, 3), (26.5, 93, 9), (26.5, 100.5, 15), (19, 100.5, 21),
                    (19, 100.5, 6), (19, 93, 12), (26.5, 93, 18), (26.5, 100.5, 24)):
    put('ground', 'Wall Lantern', x_, y_, 0, z=z)                  # lanterns climbing the corners

# ---- the descent: a spiral round the open well of the shaft, from the keel lookout (+9 m) up to the court, stepping
# off at the dormitory level (+15 m) and the hall of the descent (+21 m) through gaps in the parapets
VX['rkA'].cut(VX['rkA'].disc(SHAFT[0], SHAFT[1], 3.6), 0.5, 6)    # the shaft opens through the lookout's dome
spiral(SHAFT[:2], 2, 3.5, 9, 37, 15, 15, ANCIENT, ['rkA', 'rkB', 'rkC'])
for lid, (b0, b1) in (('rkC', (345, 30)), ('rkB', (165, 210))):
    VX[lid].cut(VX[lid].ring(SHAFT[0], SHAFT[1], 4, 0.5) & bearings(SHAFT[:2], b0, b1), 0, 1)
T.cut(T.ring(SHAFT[0], SHAFT[1], 4, 0.5) & bearings(SHAFT[:2], 180, 225), 0, 1)   # the gold parapet's gap at the top
for lid in ('rkB', 'rkC'):
    paint(P.grids[lid], T.disc(SHAFT[0], SHAFT[1], SHAFT[2]), ' ')    # (no floor across the shaft: the walkway round it re-floored it)
put('rkA', 'Brazier', 63.5, 79.5)                                  # a fire at the bottom of the well

# ---- the Starspire: a spiral round a Starlight newel from the door up to the top room (+48 m)
SPT = spiral(SP, 0.75, 2.5, 28, 40, 22.5, 180, ANCIENT, ['top'])
vabs(T.disc(*SP, 0.75), 28, 48, STARL, ['top'])
for i, sec, t_ in SPT[33:39]:
    paint(sp48, sec, ' ')                                          # (the opening over the last treads, with headroom)
put('sp48', 'Wooden Side Table', 39.5, 78.5)
put('sp48', 'Rustic Chair', 39.5, 77)
lib('sp48', 'chest-small', 38.5, 79.5)

# ---- steps up to the bard's stage; the farmhouse's stair; the workshop's loft and its ladder
P.item('top', 'stairs', 'Staircase (up to the stage)', 43, 57, 4, 1, 1, 0, '#a98a62')
P.item('ground', 'stairs', 'Staircase (to the upper floor)', 101.5, 89, 1.5, 3.5, 3.5, 90, '#a98a62')
paint(up35, T.rect(101.5, 89, 105, 90.5), ' ')
wloft = P.level('wloft', "Ground: the workshop's loft (+5 m)", 5, 3)
P.rect(wloft, 54, 13, 62, 17, WOODF)
P.item('ground', 'stairs', 'Staircase (up to the loft)', 49, 15, 1.5, 5, 5, 90, '#a98a62')

# ---- the crane on the north-west rim: a timber post and jib out over the void, its brace and counterweight, the
# winch, and its chain hanging 25 m down to a crate over the timber yard's landing below
T.put(T.rect(47.5, 45.5, 48.5, 46.5), 0, 7, TWOOD)                 # the post
T.put(T.rect(47.5, 39, 48.5, 48), 6.5, 7, TWOOD)                   # the jib
for k in range(4):
    T.put(T.rect(47.5, 45 - 0.5 * k, 48.5, 45.5 - 0.5 * k), 4.5 + 0.5 * k, 5 + 0.5 * k, TWOOD)   # its brace
T.put(T.rect(47.5, 47, 48.5, 48), 5.5, 6.5, RSTONE)                # the counterweight
T.put(T.rect(46.5, 45.5, 47.5, 46.5) | T.rect(48.5, 45.5, 49.5, 46.5), 0, 1.5, RWOOD)   # the winch's frame
T.put(T.rect(46.5, 46, 49.5, 46.5), 1, 1.5, IRON)                  # its drum
T.put(T.rect(48, 39.5, 48.5, 40), 0, 6.5, IRON)                    # the chain, over the rim
crane = P.level('crane', "The crane's chain and its load (0 m)", 0, 28)
CV = vox('crane')
CV.put(CV.rect(48, 39.5, 48.5, 40), 3.5, 28, IRON)
CV.put(CV.rect(47.5, 39, 48.5, 40), 2.5, 3.5, RWOOD)               # a crate on the hook
P.rect(gnd, 44, 38, 54, 42, ROADC)                                 # the landing under it
P.zone('top', 'The crane (lifts from the timber yard)', 46.5, 39, 50, 48, '#9a7344')

# ---- rune posts along the chain bridge's parapets
PAR = BR & ~_e & ~T.rect(*TOPT)
(ax_, ay_), (bx_, by_) = TC, LANDING
Ln = math.hypot(bx_ - ax_, by_ - ay_)
nx_, ny_ = -(by_ - ay_) / Ln, (bx_ - ax_) / Ln
for t in (0.25, 0.45, 0.65, 0.85):
    for sgn in (1, -1):
        qx, qy = ax_ + t * (bx_ - ax_) + sgn * 1.5 * nx_, ay_ + t * (by_ - ay_) + sgn * 1.5 * ny_
        sq = T.rect(math.floor(qx * 2) / 2, math.floor(qy * 2) / 2, math.floor(qx * 2) / 2 + 0.5, math.floor(qy * 2) / 2 + 0.5) & PAR
        T.put(sq, 1, 2, ANCIENT)
        T.put(sq, 2, 2.5, RUNE)

# ---- the rotunda: braziers in the eight niches round the altar, a carpet from the main door to the dais
for k in range(8):
    bx, by = polar(RC, 8, 22.5 + 45 * k)
    put('top', 'Brazier', round((bx - 0.5) * 2) / 2, round((by - 0.5) * 2) / 2, z=0.5)
paint(top, T.rect(63, 68.5, 65, 71), CARPET)

# ---- Valory's hall: tie beams with lanterns hung from them, banqueting tables down both sides of a carpeted aisle,
# the fireplace, shields on the piers, lanterns on the stage, her bed in the corner
for yb in (60.5, 66.5):
    T.put(T.rect(40, yb, 50, yb + 1), 9, 10, TWOOD)
    put('top', 'Ceiling Lantern', 44.5, yb, z=7.5)
paint(top, T.rect(44.5, 58, 46.5, 72.5), CARPET)
for xt in (42.5, 46.5):
    for yt in (61, 64, 67):
        put('top', 'Wooden Banquet Table', xt, yt, 90)
    for xb in (xt - 0.5, xt + 1):
        for yb in (61.5, 64.5, 67.5):
            put('top', 'Rustic Bench', xb, yb, 90)
put('top', 'Kettle', 42.5, 64.5, z=1)
for (x_, y_) in ((42.5, 61.5), (46.5, 62), (47, 65), (46.5, 68.5)):
    put('top', 'Wooden Cup', x_, y_, z=1)
put('top', 'Crude Wooden Jug', 43, 67.5, z=1)
put('top', 'Stone Fireplace', 39, 63, 270)
for y_ in (60.5, 66.5):
    put('top', 'Shield Wall Mount', 40, y_, 270, z=3.5)
    put('top', 'Shield Wall Mount', 49.5, y_, 90, z=3.5)
for x_ in (41, 48.5):
    put('up29', 'Ground Lantern II', x_, 55)
lib('top', 'bed', 40, 70, label="Valory's bed")
lib('top', 'chest-medium', 48.5, 71.5)

# ---- the Collector's gallery: tie beams and lanterns, mannequins and showcases, cabinets, window seats in the oriels,
# his bed at the far end, curios on a side table
for xb in (60, 68):
    T.put(T.rect(xb, 42.5, xb + 1, 50), 7.5, 8, TWOOD)
    put('top', 'Hanging Lantern', xb + 0.5, 46, z=6.5)
put('top', 'Mannequin "Strike A Pose"', 60.5, 42.5)
put('top', 'Mannequin "Victory"', 66, 42.5)
for x_ in (61, 65):
    put('top', 'Embervale Miniature Showcase', x_, 46.5)
for x_ in (57, 69):
    put('top', 'Large Carved Wooden Cabinet', x_, 49, 180)
for xc in (58.5, 64, 69.5):
    put('top', 'Bench', xc - 1, 40)
lib('top', 'bed', 70, 46.5, 90, label="Alden Crowley's bed")
put('top', 'Wooden Side Table', 55, 48)
put('top', 'Scrap Pot II', 55.25, 48.25, z=1)
paint(top, T.rect(63, 47.5, 65, 49.5), CARPET)

# ---- the bathhouse: a tub on the podium, the Barber's bed, his basin and chair, benches by the pool, plants and
# lanterns; the Water Dispenser feeding the spring
lib('up29', 'bathtub', 82, 59, 90, label='Bronze Bathtub')
lib('up29', 'bed', 86.5, 59, label="Elio Ricci's bed")
put('up29', 'Wooden Sink', 82, 68)
put('up29', 'Rustic Chair', 84.5, 67.5)
for y_ in (62, 64.5):
    put('up29', 'Bench', 80.5, y_, 270)
for y_ in (61, 66.5):
    put('up29', 'Ground Lantern II', 81, y_)
for y_ in (59, 68):
    put('up29', 'Large Bloomheart Fruit Plant Pot I', 79, y_)
put('up29', 'Water Dispenser', 91.5, 63)

# ---- the Alchemist's laboratory: his four stations round the room, his cot, the cauldron, herbs, a cat
lib('top', 'alchemy', 76.5, 75.5)
lib('top', 'laboratory', 81.5, 75.5)
lib('top', 'mortar', 81.5, 80.5)
lib('top', 'grinding-stones', 76.5, 80.5)
lib('top', 'mattress', 83.5, 78, label="Balthazar's cot")
put('top', 'Scrap Vat I', 76, 78, label='Scrap Vat I (a cauldron)')
put('top', 'Small Prickle Pearl Plant Pot', 78.5, 74.5)
put('top', 'Small Aurora Beans Plant Pot', 81, 83.5)
put('top', 'Cat Pillow', 79.5, 82)
put('top', 'Ceiling Lantern', 79.5, 78.5, z=3.5)

# ---- the crown's ways and gardens: lamp posts, benches looking out over the rim, flower beds in the north-east lawn
for (x_, y_) in ((53, 61), (53, 66.5), (74.5, 61), (74.5, 66.5), (61, 53), (66.5, 53), (43, 81), (52.5, 81)):
    put('top', 'Ground Lantern II', x_, y_)
for x_ in (57, 69):
    put('top', 'Bench', x_, 86)
for r_ in ((79, 50, 83, 51.5), (84.5, 52, 88, 53.5), (79, 53.5, 82, 55)):
    paint(top, T.rect(*r_), FLOWERS)
put('top', 'Bench', 83, 54.5, 180)

# ---- inside the rock: doors in the carved openings
door_in_rock('rkC', 'Wooden Door', 56, 62, 56.5, 64)               # the forge's
door_in_rock('rkC', 'Wooden Door', 84, 62, 84.5, 64)               # the mill's
door_in_rock('rkB', 'Wooden Door', 61.5, 68, 62, 70)               # the dormitory's
door_in_rock('rkB', 'Round Ancient Door', 65.5, 67.5, 66, 70.5)    # the vault's
door_in_rock('rkB', 'Wooden Door', 65.5, 57, 66, 59)               # the cellars'

# ---- Oswald's forge: the forge under its hood, smelter and blast furnace, the charcoal kiln, smithing tools, a quench
# trough, weapon racks in the bays, chests, coal and his bed
lib('rkC', 'forge', 38.5, 56)
lib('rkC', 'smelter', 41, 51)
lib('rkC', 'blast-furnace', 40.5, 60.5)
lib('rkC', 'charcoal-kiln', 53.5, 51)
lib('rkC', 'smithing-tools', 50.5, 58.5)
lib('rkC', 'trough', 40.5, 58.5, label='Trough (for quenching)')
put('rkC', 'Sword and Shield Rack', 43, 49)
put('rkC', 'Two-Handed Melee Weapon Rack', 47, 49)
put('rkC', 'Shield Rack', 51.5, 49)
lib('rkC', 'chest-large', 44, 63)
lib('rkC', 'chest-huge', 50.5, 62.5)
lib('rkC', 'quickstack', 53.5, 62.5)
put('rkC', 'Resource Bundle I', 44.5, 51, label='Resource Bundle I (coal)')
put('rkC', 'Supply Sacks II', 45.5, 51)
lib('rkC', 'bed', 47, 61.5, 90, label="Oswald Anders's bed")
put('rkC', 'Crypt Wall Torch', 55.5, 55, 90, z=2)
put('rkC', 'Crypt Wall Torch', 43, 63.5, 180, z=2)

# ---- the hall of the descent: braziers in its corners, a lantern under the dome, benches
for (x_, y_) in ((61, 63.5), (66, 63.5), (59, 74.5), (68.5, 74.5)):
    put('rkC', 'Brazier', x_, y_)
put('rkC', 'Ceiling Lantern', 63.5, 68.5, z=4)
for x_ in (59.5, 68.5):
    put('rkC', 'Bench', x_, 69.5 if x_ < 60 else 67, 270 if x_ < 60 else 90)

# ---- the mill: the Mill by the axle, sacks of grain and flour, barrels, crates, a bucket
put('rkC', 'Mill', 91, 62.5)
for (x_, y_, nm) in ((85, 58.5, 'Supply Sacks I'), (86, 58.5, 'Supply Sacks II'), (85, 59.5, 'Supply Sacks III'),
                     (88, 66.5, 'Wooden Crate'), (89, 66.5, 'Wooden Crate'), (89, 58.5, 'Standing Wooden Barrel')):
    put('rkC', nm, x_, y_)
put('rkC', 'Lying Wooden Barrel', 85, 66.5)
put('rkC', 'Scrap Bucket', 90.5, 64.5)

# ---- the dormitory: seventeen beds for the other survivors (seven in the alcoves), a long table with benches, lanterns
BEDS = [(45.5, y_, 90) for y_ in (63.5, 67, 70.5, 74)] + [(x_, 59.5, 0) for x_ in (50, 53.5, 57)]
BEDS += [(58.5, y_, 90) for y_ in (62.5, 71.5, 73.5)] + [(58.5, 64.5, 90)]
BEDS += [(x_, y_, 0) for x_ in (49.5, 52.5, 55.5) for y_ in (70, 73)]
for (x_, y_, r_) in BEDS:
    lib('rkB', 'bed', x_, y_, r_)
for x_ in (50.5, 53.5):
    put('rkB', 'Wooden Banquet Table', x_, 65.5)
for x_ in (50.5, 52.5, 54.5):
    for y_ in (65, 66.5):
        put('rkB', 'Rustic Bench', x_, y_)
for (x_, y_) in ((53, 63.5), (53, 68.5)):
    put('rkB', 'Ceiling Lantern', x_, y_, z=4)
for (x_, y_) in ((51, 65.5), (55, 65.5)):
    put('rkB', 'Wooden Bowl', x_, y_, z=1)
put('rkB', 'Ground Lantern I', 60.5, 67)
lib('rkB', 'chest-large', 57.5, 66.5)

# ---- the vault: magic chests in the bays, an enormous one at the end, quick stack stations by the door, a map table
for x_ in (67, 71.5, 75.5, 79.5):
    lib('rkB', 'mchest-large', x_, 64)
    lib('rkB', 'mchest-large', x_, 73, 180)
lib('rkB', 'mchest-enormous', 80.5, 67.5, 270)
for y_ in (66.5, 71):
    lib('rkB', 'quickstack', 67, y_)
lib('rkB', 'table', 73.5, 68.5, label='Table (the map table)')
for x_ in (72.5, 76.5):
    put('rkB', 'Ceiling Lantern', x_, 68.5, z=4)

# ---- the cellars: shelves, barrels and crates in the two aisles
for x_ in (67, 70):
    put('rkB', 'High Crude Wooden Shelf', x_, 54)
for (x_, y_, nm) in ((67, 55.5, 'Standing Wooden Barrel'), (68, 55.5, 'Standing Wooden Barrel'),
                     (67, 61, 'Wooden Crate'), (68, 61, 'Wooden Crate'), (69.5, 61, 'Supply Sacks III'),
                     (71, 61, 'Half Wooden Barrel')):
    put('rkB', nm, x_, y_)
put('rkB', 'Lying Wooden Barrel', 70, 55.5)

# ---- hidden below: the Infusion Altar on the summoning circle under the oculus, skull torches round it
put('deep_sunk', 'Infusion Altar', 63, 78.5)
for (x_, y_) in ((63.5, 72.5), (63.5, 86), (70, 79), (57.5, 79)):
    put('deep', 'Crypt Skull Torch', x_, y_)

# ---- Loraine's study: shelves in the niches, the Gem Forge and the Ancient Workbench by the door, a miniature of the
# isle in the middle, her desk on the dais, her bed, a lantern, her cat
for s, x_, r_ in (('w', 32.5, 270), ('e', 45, 90)):
    for y_ in ((101.5, 104.5, 107.5) if s == 'w' else (101.5, 104.5)):
        put('deepc', 'Carved Wooden Shelf', x_, y_, r_, z=0.5)      # (on the niche's sill)
put('deepc', 'Placeable Gem Forge', 34, 100)
put('deepc', 'Ancient Workbench', 42, 100)
put('deepc', 'Embervale Miniature Showcase', 37, 104, label='Embervale Miniature Showcase (a model of the isle)')
lib('deep_dais', 'table', 38, 108, label='Table (her desk)')
put('deep_dais', 'Rustic Chair', 38.5, 109)
put('deep_dais', 'Ground Lantern I', 36, 107)
lib('deepc', 'bed', 42.5, 107, label="Loraine Crim's bed")
lib('deepc', 'chest-medium', 36.5, 100)
put('deepc', 'Cat Pillow', 35, 105.5)
put('deepc', 'Ceiling Lantern', 39, 102, z=3.5)

# ---- the stair tower's plaza: benches under the isle, lamp posts, a notice board, market crates by the stall
for x_ in (34, 40, 46):
    put('ground', 'Bench', x_, 103.5, 180)
for x_ in (37.5, 43.5, 49.5):
    put('ground', 'Ground Lantern II', x_, 103.5)
G.put(G.rect(52, 92, 52.5, 92.5) | G.rect(54.5, 92, 55, 92.5), 0, 2.5, RWOOD)   # the notice board
G.put(G.rect(52, 92, 55, 92.5), 1.5, 2.5, PLAIT)
for (x_, y_, nm) in ((62, 100.5, 'Wooden Crate'), (62, 101.5, 'Wooden Crate'), (63, 100.5, 'Standing Wooden Barrel')):
    put('ground', nm, x_, y_)
lib('ground', 'mattress', 70, 104.5, 90, label="Mei-Yin Chen's mattress")
put('ground', 'Low Crude Wooden Shelf', 73, 102, 270)

# ---- the farm: the kitchen by the chimney, the table, the Farmer's rooms upstairs, window boxes, the well in the yard,
# seedbeds, beehives and a scarecrow in the fields, the pen's fence and gate, the animals' beds and feeders
lib('ground', 'oven', 107, 92.5)
lib('ground', 'kitchen', 107, 95.5)
lib('ground', 'cooking-station', 107, 89.5)
put('ground', 'Wooden Sink', 105, 89)
put('ground', 'Wooden Banquet Table', 93, 93)
for y_ in (92.5, 94):
    put('ground', 'Rustic Bench', 93.5, y_)
put('ground', 'Kettle', 95, 93, z=1)
put('ground', 'Wooden Bowl', 93.5, 93, z=1)
lib('farm2', 'bed2', 106.5, 96.5, label="Emily Fray's bed")
lib('farm2', 'chest-medium', 103.5, 99)
lib('farm2', 'bed', 89, 89)
put('farm2', 'Crude Wooden Closet', 92, 88)
put('farm2', 'Crude Wooden Nightstand', 91, 89)
for xc in (91, 95, 108):                                           # window boxes under the upper south windows
    G.put(G.rect(xc - 0.5, 100.5, xc + 0.5, 101), 3.5, 4, RWOOD)
    G.put(G.rect(xc - 0.5, 100.5, xc + 0.5, 101), 4, 4.5, ('Flower Soil', '#a77e63'))
WELL = (106, 103.5)
G.put(G.ring(*WELL, 1.25, 0.5), 0, 1, RSTONE)
paint(gnd, G.disc(*WELL, 0.75), WATER)
for x_ in (104.5, 107):
    G.put(G.rect(x_, 103, x_ + 0.5, 104), 0, 2.5, RWOOD)
G.put(G.rect(105, 103, 107, 103.5), 2, 2.5, RWOOD)                 # the windlass
put('ground', 'Scrap Bucket', 107.5, 104.5)
gwell = P.roof(P.level('gwell', "Ground: the well's roof (+2.5 m)", 2.5, 3))
gwell.gable(104.5, 102.5, 107.5, 104.5, 'x', 'straw', pitch=1.0, overhang=0.5)
gwell.paint()
for x_ in (84, 87, 90, 93):
    lib('ground', 'seedbed', x_, 108)
for x_ in (113, 115.5, 118):
    put('ground', 'Beehive', x_, 107)
put('ground', 'Plough', 110, 106.5)
G.put(G.rect(100, 113.5, 100.5, 114), 0, 2.5, RWOOD)               # the scarecrow
G.put(G.rect(99, 113.5, 101.5, 114) & ~G.rect(100, 113.5, 100.5, 114), 1.5, 2, RWOOD)
G.put(G.rect(100, 113.5, 100.5, 114), 2.5, 3, STRAW)
PEN = (78, 88, 87, 104)
pen_e = G.rect(*PEN) & ~G.rect(78.5, 88.5, 86.5, 103.5)
pen_h = pen_e & ((G.my < 88.5) | (G.my > 103.5))
posts = (pen_h & (np.floor(G.mx * 2) % 4 == 0)) | (pen_e & ~pen_h & (np.floor(G.my * 2) % 4 == 0))
gate = G.rect(86.5, 95, 87, 97)
G.put(posts & ~gate, 0, 1.5, RWOOD)
G.put(pen_e & ~posts & ~gate, 0.5, 1, RWOOD)
put('ground', 'Crude Wooden Gate I', 86.5, 95, 90)
for x_ in (79, 80.5, 82):
    put('ground', 'Farm Animal Pillow', x_, 89.5)
put('ground', 'Big Farm Animal Pillow', 79, 95)
put('ground', 'Goat Feeder', 79.5, 102)
lib('ground', 'trough', 83, 102, label='Trough (water)')

# ---- the Hunter's lodge: the fireplace, a straw mat and the dog's bed before it, his bed, the loom and spinning wheel,
# weapon racks, a table, a chest; firewood stacked under the eaves; the tannery yard's stations and hide frames
put('ground', 'Stone Fireplace', 6.5, 50, 270)
put('ground', 'Big Straw Mat', 8, 49.5)
put('ground', 'Dog Pillow', 8.5, 52)
lib('ground', 'bed', 8, 54, label="Athalan Skree's bed")
lib('ground', 'loom', 24, 45)
lib('ground', 'spinning', 21, 45)
put('ground', 'Bow Weapon Rack', 16.5, 45)
put('ground', 'Staff Weapon Rack', 9, 45)
put('ground', 'Wooden Banquet Table', 17, 51)
for (x_, y_) in ((17.5, 50), (19, 52)):
    put('ground', 'Rustic Chair', x_, y_)
put('ground', 'Kettle', 18, 51, z=1)
lib('ground', 'chest-large', 25, 56)
G.put(G.rect(16, 58, 19, 59), 0, 1.5, RWOOD)                      # firewood under the south eaves
lib('ground', 'tannery', 8, 62)
for x_ in (11, 14):
    lib('ground', 'drying-rack', x_, 62)
lib('ground', 'hand-spindle', 17, 62)
lib('ground', 'spinning-machine', 20, 62)
for x_ in (8, 11, 14):
    put('ground', 'Fish Drying Rack', x_, 70, label='Fish Drying Rack (stretching hides)')
for x_ in (18, 19.5):
    put('ground', 'Scrap Vat I', x_, 70, label='Scrap Vat I (a tanning vat)')
put('ground', 'Resource Bundle I', 22, 70)

# ---- the Carpenter's workshop: his stations along the north wall, timber stacked inside and in the yard, a chest, the
# hammer left on the workbench; his bed and stores up in the loft; log piles in the yard
for (typ, x_) in (('kiln', 47), ('workbench', 54), ('table-saw', 60), ('masonry-tools', 66)):
    lib('ground', typ, x_, 7)
for (nm, x_) in (('Decoration Workbench', 57), ('Sparkworks Workbench', 63)):
    put('ground', nm, x_, 7)
put('ground', 'Construction Hammer', 54.5, 7.5, z=1)
for y_ in (11, 12, 13):
    put('ground', 'Resource Bundle II', 68, y_)
lib('ground', 'chest-huge', 65.5, 15.5)
lib('wloft', 'bed', 58.5, 13, 90, label="Cade Hawthorn's bed")
put('wloft', 'Wooden Crate', 61, 15.5)
put('wloft', 'Supply Sacks II', 54.5, 13)
for (r_, h) in (((64, 22, 70, 23.5), 1.5), ((64, 24, 70, 25.5), 1), ((72, 22, 78, 23.5), 1.5)):
    G.put(G.rect(*r_), 0, h, RWOOD)                                # log piles

# ---- the Fisher's boathouse: a boat on the slip inside the water door, hide frames for the catch, his bed, a chest,
# barrels, nets hung on the wall; a fishing spot at the end of the jetty
hull2 = G.rect(104, 66.5, 108, 68) & ~(G.rect(104, 66.5, 104.5, 67) | G.rect(104, 67.5, 104.5, 68))
G.put(hull2 & ~G.rect(104.5, 67, 107.5, 67.5), 0, 1, TWOOD)
G.put(G.rect(104.5, 67, 107.5, 67.5), 0, 0.5, RWOOD)
for x_ in (103.5, 112):
    put('ground', 'Fish Drying Rack', x_, 61)
lib('ground', 'bed', 112.5, 67.5, label="Captain Melville Fontane's bed")
lib('ground', 'chest-medium', 110, 70)
put('ground', 'Standing Wooden Barrel', 113, 65)
G.put(G.rect(108, 70.5, 110, 71), 1.5, 3, PLAIT)                   # nets drying on the wall
lib('lake', 'fishing', 94, 67)

# ---- the pylons: a ring of glowing rune stones round each; the keel's tip glows where it points at the circle
for (px, py) in PYLONS.values():
    for k in range(8):
        sx_, sy_ = (math.floor(c * 2) / 2 for c in polar((px, py), 4.5, 22.5 + 45 * k))
        PV.put(PV.rect(sx_, sy_, sx_ + 0.5, sy_ + 0.5), 0, 0.5, RUNE)
VX['rk0'].put(VX['rk0'].disc(APEX[0], APEX[1], 1.5), 0, 1, RUNE, only='solid')

# ---- finishing touches from the last review: a rail round the stair's opening on the tower top (open where you step
# off), and a balustrade along the crown's rim wherever the paving runs out to the drop (not where the bridge lands
# or anything stands)
OPEN_T = np.zeros_like(INSIDE)
for i, sec, t_ in UP[50:]:
    OPEN_T |= sec
grown = OPEN_T.copy()
for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
    grown |= np.roll(np.roll(OPEN_T, dy, 0), dx, 1)
d_tc = np.hypot(T.mx - TC[0], T.my - TC[1])
T.put(grown & ~OPEN_T & T.rect(*TOPT) & ~(bearings(TC, 85, 115) & (d_tc < 4.5)), 0, 1, ANCIENT)
PAVED = np.zeros_like(INSIDE)
for y, x in zip(*np.nonzero(RIM)):
    PAVED[y, x] = top[y][x] in (PAVE, INLAY, CARPET)
TAKEN = np.zeros_like(INSIDE)
for it in P.items:
    if it['level'] == 'top':
        w_, d_ = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
        TAKEN[it['y']:it['y'] + d_, it['x']:it['x'] + w_] = True
NEAR_BRIDGE = np.zeros_like(INSIDE)
for x, y, t in line_squares(TC, LANDING, 3):
    NEAR_BRIDGE[y, x] = True
T.put(PAVED & ~TAKEN & ~NEAR_BRIDGE, 0, 1, ANCIENT)

# ================================================================= the grounds: lanes and hill paths, the shore, the brook and the pond,
# fallen boulders, the stone circle and the pavilion, trees, walls and lamps
# A level digs out any ground above its floor wherever it's painted, so anything on raised ground (a path, water, a
# rock, a tree) goes on the level at that ground's height: gl(h) makes them as needed ('g010' is +1 m).
GL = {}
LIB.update({'tree-broadleaf': ('Broadleaf Tree', 1, 1, 8), 'tree-evergreen': ('Evergreen Tree', 1, 1, 10), 'shrub': ('Shrub', 1, 1, 1)})
LIB_COLOR.update({'tree-broadleaf': '#5a8a3c', 'tree-evergreen': '#3f6b4a', 'shrub': '#6a9a4a'})


def gl(h):
    """The level for things standing on the ground at height h."""
    h = round(h * 2) / 2
    if h <= 0:
        return 'ground'
    if h not in GL:
        lid = f'g{int(round(h * 10)):03d}'
        P.level(lid, f'Grounds at +{h:g} m: paths, water, rocks, plants', h, 10)
        GL[h] = lid
    return GL[h]


def gz(x, y):
    """The ground's height under square (x, y)."""
    return P.ground_at(x, y)


def gfloor(mask, sym, only=(' ',)):
    """Paint a floor over the ground, each square on the level at its ground's height (lanes, paths, flower beds)."""
    for y, x in zip(*np.nonzero(mask)):
        g = P.grids[gl(gz(x, y))]
        if g[y][x] in only:
            g[y][x] = sym


def path_mask(pts, half):
    m = np.zeros_like(INSIDE)
    for x, y, t in [(x, y, t) for a, b in zip(pts, pts[1:]) for (x, y, t) in line_squares(a, b, half)]:
        m[y, x] = True
    return m


def foot(x, y, w, d):
    """The ground heights under a footprint (metres), as a set."""
    return {gz(i, j) for i, j in P.cells_rect(x, y, x + w, y + d)}


def gput(name, x, y, rot=0, z=None, label=None, typ=None):
    """An item standing on the ground: put on the level at the ground's height, nudged up to 1.5 m to find level
    ground under its whole footprint. typ: a planner library type instead of a game name."""
    if typ:
        nm, w, d, h = LIB[typ] if typ in LIB else (name, 1, 1, 1)
    else:
        w, d, h = ITEM[name]
    W, D = (d, w) if rot in (90, 270) else (w, d)
    for dx, dy in [(0, 0)] + [(a, b) for r in (0.5, 1, 1.5) for a in (-r, 0, r) for b in (-r, 0, r) if (a, b) != (0, 0)]:
        hs = foot(x + dx, y + dy, W, D)
        if len(hs) == 1 and min(hs) >= 0:
            lid = gl(min(hs))
            if typ:
                return lib(lid, typ, x + dx, y + dy, rot, z, label)
            return put(lid, name, x + dx, y + dy, rot, z, label)
    print('  no level ground for', name or typ, 'near', x, y)


def boulder(x, y, r, h, m, seed, lid=None):
    """A rough boulder: a lumpy dome r across and h tall, built up from the floor of the level it stands on (the lowest
    ground under it; on a slope its uphill side is half buried)."""
    sq = [(i, j) for i, j in P.cells_rect(x - r - 1, y - r - 1, x + r + 1, y + r + 1)]
    lid = lid or gl(min(max(0, gz(i, j)) for i, j in sq))
    v = vox(lid)
    dx, dy = v.mx - x, v.my - y
    th = np.arctan2(dy, dx)
    rr = r * (1 + 0.18 * np.sin(5 * th + seed) + 0.1 * np.sin(3 * th - seed))
    d = np.hypot(dx, dy) / rr
    top_ = snap(h * np.sqrt(np.maximum(0, 1 - d * d)) + 0.4 * np.sin(dx * 2.1 + seed) * (d < 1))
    el = v.L['elev']
    for i, j in sq:                                                # (never lower than the ground it's sunk into)
        if d[j, i] < 1:
            top_[j, i] = max(top_[j, i], max(0, gz(i, j)) - el + 0.5)
    v.put((d < 1) & (top_ > 0), 0, top_, m)


DIRT = M('Dirt Road Block (a lane)', 'floor', '#8c7455')
PEBBLE = M('Field Stones (the shore)', 'floor', '#8a8170')
STONEPATH = M('Field Stones (a path)', 'floor', '#8a8170')
WSTONE = ('Weathered Ancient Stone Block', '#8f8b80')

# ---- the lanes at 0 m (where nothing else is painted), and the brook's mouth crossed by a plank bridge
BROOK_CH = np.zeros_like(INSIDE)
for x, y, mx, my in each(85, 36, 126, 60):
    bd, bt = line_near(mx, my, BROOK)
    if bd < 0.8:
        BROOK_CH[y, x] = True
for L in LANES:
    paint(gnd, path_mask(L, 1) & ~BROOK_CH, DIRT)
BRIDGE_SQ = path_mask(LANES[4], 1.25) & BROOK_CH
G.put(BRIDGE_SQ, 0, 0.5, RWOOD)                                    # the plank bridge
_bn = BRIDGE_SQ.copy()
for dx, dy in ((1, 0), (-1, 0)):
    _bn |= np.roll(BRIDGE_SQ, dx, 1)
G.put(_bn & ~path_mask(LANES[4], 1.25) & BROOK_CH, 0, 1.5, RWOOD)  # its rails, on the brook's banks either side
P.zone('ground', 'The plank bridge over the brook', 97.5, 51.5, 101.5, 54.5, '#7a6653')

# ---- the shore: a pebble strand round the lake, where nothing else is
SHORE = np.zeros_like(INSIDE)
for x, y, mx, my in each(30, 36, 106, 96):
    d = lake_d(mx, my)
    if 1 <= d < 1.08 and gz(x, y) == 0:
        SHORE[y, x] = True
paint(gnd, SHORE, PEBBLE)

# ---- the brook: its water stepping down in little cascades from the spring pool to the lake
for x, y, mx, my in each(85, 36, 126, 60):
    bd, bt = line_near(mx, my, BROOK)
    s = brook_s(bt)
    if s > 0 and (bd < 0.8 or math.hypot(mx - BROOK[0][0], my - BROOK[0][1]) < 1.6):
        P.grids[gl(s)][y][x] = WATER
for (bx, by, r_, h_, sd) in ((113.5, 39.5, 0.8, 1, 1), (116.5, 42.5, 0.7, 1, 2), (108.5, 47.5, 0.6, 0.5, 3)):
    boulder(bx, by, r_, h_, RSTONE, sd)                            # stones round the spring and in the stream
P.zone('ground', 'The brook (from a spring in the hills)', 100, 40, 117, 54, '#3f6f8f')

# ---- the lily pond in the south-west meadow, stepping stones across it, a bench
for k, (sx_, sy_) in enumerate(((33, 114), (34.5, 115.5), (36, 116.5), (37.5, 117.5), (39, 118.5))):
    LV.put(LV.rect(sx_, sy_, sx_ + 0.5, sy_ + 0.5), 0, 0.5, RSTONE)
gput('Bench', 35, 121.5, 180)
P.zone('lake', 'The lily pond', 32, 112, 40, 120, '#3f6f8f')

# ---- boulders that fell when the isle rose: half sunk round the lake, one at the plaza's edge
for (bx, by, r_, h_, sd, lid) in ((44, 56, 2.2, 2.5, 1, 'lake'), (40, 71, 1.8, 2, 2, 'lake'), (86, 84.5, 2.5, 3, 3, None),
                                 (60, 43.5, 2, 2.5, 4, None), (77, 44.5, 1.6, 2, 5, None), (35, 63, 1.8, 2, 6, None),
                                 (51, 88.5, 2.5, 3, 7, None), (94.5, 60.5, 1.4, 1.5, 8, 'lake'), (100.5, 59.5, 1.2, 1.5, 9, None)):
    boulder(bx, by, r_, h_, ROCKB, sd, lid)

# ---- the stone circle on the north-west hilltop: eight weathered monoliths, four rune-capped, round a low altar stone
SC = (16, 16)
SCL = gl(gz(P.sq(SC[0]), P.sq(SC[1])))
SV = vox(SCL)
P.disc(P.grids[SCL], *SC, 4.75, M('Ancient Stone Block (the circle)', 'floor', ASTONE), r_in=3.75)
for k in range(8):
    cx_, cy_ = (round(c * 2) / 2 for c in polar(SC, 4.25, 22.5 + 45 * k))
    stone = SV.rect(cx_ - 0.5, cy_ - 0.5, cx_ + 0.5, cy_ + 0.5)
    SV.put(stone, 0, 3 + 0.5 * (k % 3), WSTONE)
    if k % 2 == 0:
        SV.put(stone, 3 + 0.5 * (k % 3), 3.5 + 0.5 * (k % 3), RUNE)
SV.put(SV.rect(15, 15.5, 17, 16.5), 0, 1, ANCIENT)                  # the altar stone
P.zone(SCL, 'The stone circle (where the isle was first anchored)', 11, 11, 21, 21, '#6c9dc3')

# ---- the pavilion on the north-east hilltop, looking out at the isle: six columns, a copper roof, a bench
PC = (114, 14)
PCH = gz(P.sq(PC[0]), P.sq(PC[1]))
PCL = gl(PCH)
PVV = vox(PCL)
P.disc(P.grids[PCL], *PC, 3.5, PAVE)
for k in range(6):
    cx_, cy_ = (round(c * 2) / 2 for c in polar(PC, 2.75, 30 + 60 * k))
    PVV.put(PVV.rect(cx_ - 0.5, cy_ - 0.5, cx_ + 0.5, cy_ + 0.5), 0, 3.5, MOONSTONE)
PVV.put(PVV.ring(*PC, 3.25, 1), 3.5, 4, ANCIENT)                    # the ring beam
rpav = P.roof(P.level('gpav', "Grounds: the pavilion's roof", PCH + 4, 4))
rpav.cone(*PC, 3.25, 2.5, 'copper', overhang=0.5)
rpav.paint()
put(PCL, 'Bench', 113, 12)
P.zone(PCL, 'The pavilion (a view of the isle)', 110.5, 10.5, 117.5, 17.5, '#8d694b')

# ---- the second secret way down: a secret floor in the pavilion over a spiral stair 20 m down a lined shaft, and the
# long tunnel south-west from its foot under the lake into the summoning chamber, a rest room halfway, rune lamps
# along it
tun = P.level('tun', 'Hidden: the long tunnel from the pavilion (-16 m)', -16, 6)
tsh = P.level('tunshaft', "Hidden: the shaft under the pavilion (-10 m)", -10, PCH + 10)
TV = vox('tun')
P.disc(tsh, *PC, 3, M('Dug out (the shaft under the pavilion)', 'dig', '#3a3a3a'))
P.disc(tun, *PC, 3, DFLOOR)
vabs(T.ring(*PC, 3, 0.5), -16, PCH - 0.5, DUNGB, ['tun', 'tunshaft'])   # its lining
vabs(T.disc(*PC, 0.75), -16, PCH - 0.5, ANCIENT, ['tun', 'tunshaft'])   # the newel
PSP = spiral(PC, 0.75, 2.5, -16, 40, 22.5, 67.5, ANCIENT, ['tun', 'tunshaft'])
OPEN_P = np.zeros_like(INSIDE)
for i, sec, t_ in PSP[32:39]:
    OPEN_P |= sec
    paint(P.grids[PCL], sec, ' ')                                  # the opening, where the secret floor goes
_ys, _xs = np.nonzero(OPEN_P)
P.zone(PCL, 'Secret floor (a Secret Stone Floor Passage) over the stair down', _xs.min() / 2, _ys.min() / 2,
       _xs.max() / 2 + 0.5, _ys.max() / 2 + 0.5, '#7e74a8')
TUN = [(114, 14), (106, 25), (99, 35), (90, 48), (80, 60), (69.5, 70)]
REST = (94.85, 41)
L_TUN = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(TUN, TUN[1:]))
clear_of_chamber = np.hypot(T.mx - CC[0], T.my - CC[1]) > 11.9
t_in = (path_mask(TUN, 1.5) | T.disc(*REST, 3.5)) & clear_of_chamber & ~T.disc(*PC, 2.6)
t_out = (path_mask(TUN, 2.5) | T.disc(*REST, 4.5)) & clear_of_chamber & ~T.disc(*PC, 3.1)
paint(tun, t_out, DFLOOR)
TV.put(t_out & ~t_in, 0, 6, DUNGB)
TV.cut(path_mask(TUN, 1.5) & T.ring(*PC, 3.1, 0.6), 0, 3.5)       # (its mouth, through the shaft's lining)
t_ceil = np.full(t_in.shape, 6.0)
for y, x in zip(*np.nonzero(t_in)):
    mx, my = (x + 0.5) / 2, (y + 0.5) / 2
    dr = math.hypot(mx - REST[0], my - REST[1])
    if dr < 3.5:                                                   # a shallow dome over the rest room
        t_ceil[y, x] = 4 + float(snap(1.5 * math.sqrt(max(0.0, 1 - (dr / 3.5) ** 2))))
    else:                                                          # a round vault, ribs every 4 m
        d_, t_ = line_near(mx, my, TUN)
        t_ceil[y, x] = 3 + float(snap(1.5 * math.sqrt(max(0.0, 1 - (d_ / 1.5) ** 2)))) - (0.5 if (t_ * L_TUN) % 4 < 1 else 0)
TV.put(t_in, t_ceil, 6, DUNGB)
carve(D, ('ring', CC, 12, 30), 0, 1.5, -0.6, 1.6, 0, 3)           # its door into the chamber (in place of a niche)
for k, dist in enumerate((8, 22, 36, 50, 64)):                     # rune lamps, on alternate sides
    run = 0.0
    for a, b in zip(TUN, TUN[1:]):
        Ln = math.hypot(b[0] - a[0], b[1] - a[1])
        if run + Ln >= dist:
            t = (dist - run) / Ln
            sg = 1 if k % 2 == 0 else -1
            qx = a[0] + t * (b[0] - a[0]) - sg * 1.75 * (b[1] - a[1]) / Ln
            qy = a[1] + t * (b[1] - a[1]) + sg * 1.75 * (b[0] - a[0]) / Ln
            TV.put(T.rect(math.floor(qx * 2) / 2, math.floor(qy * 2) / 2, math.floor(qx * 2) / 2 + 0.5,
                          math.floor(qy * 2) / 2 + 0.5), 1.5, 2.5, RUNE, only='solid')
            break
        run += Ln
put('tun', 'Brazier', 94.5, 41.5, label='Brazier (the halfway room)')
put('tun', 'Bench', 94, 38)
put('tun', 'Bench', 94, 44, 180)
_ys, _xs = np.nonzero(t_in)
P.zone('tun', 'The long tunnel (the pavilion to the summoning chamber)', 82, 30, 100, 40, '#7e74a8')
P.zone('tun', 'The halfway room', REST[0] - 3, REST[1] - 3, REST[0] + 3, REST[1] + 3, '#7e74a8')

# ---- paths up the hills, following the ground: to the circle, the pavilion and the three pylons
for pts in ([(40, 22), (32, 21), (26, 18.5), (21.5, 16.5)], [(90, 20), (98, 18), (106, 16), (110.5, 15)],
            [(31, 41), (27.5, 35.5), (25, 33.5)], [(92, 37), (97, 33.5), (102.5, 31)], [(112, 101), (114.5, 97)]):
    gfloor(path_mask(pts, 0.75), STONEPATH)

# ---- trees (from the Farmer's seedlings): an avenue up the road in, an orchard by the pond, woods on the hills, a
# shade tree in the farmyard and one by the spring; shrubs along the road's verges
BROAD, EVER = 'tree-broadleaf', 'tree-evergreen'
TREES = [(BROAD, 53.5, y_) for y_ in (114, 118.5, 123)] + [(BROAD, 65.5, y_) for y_ in (114, 118.5, 123)]
TREES += [(BROAD, x_, y_) for x_ in (42.5, 46.5, 50) for y_ in (113, 117, 121)]
TREES += [(EVER, x_, y_) for (x_, y_) in ((7, 9), (11, 25), (26, 7), (30, 27), (5, 19), (35, 18), (26.5, 23.5), (9, 35),
                                           (6, 86), (10, 106), (5, 113), (16, 110))]
TREES += [(BROAD, x_, y_) for (x_, y_) in ((96, 24), (100, 26.5), (122, 21), (112, 37), (119, 44), (112, 103.5),
                                            (122.5, 78), (120, 84))]
TREES += [(EVER, x_, y_) for (x_, y_) in ((106, 6), (121, 7), (108, 22), (122.5, 14), (102, 12), (122.5, 58))]
for typ, x_, y_ in TREES:
    gput(None, x_, y_, typ=typ, label='Evergreen Tree' if typ == EVER else 'Broadleaf Tree')
for y_ in (116, 120.5):
    for x_ in (54, 65.5):
        gput(None, x_, y_, typ='shrub', label='Shrub')

# ---- flowers: drifts of wildflowers in the meadow and along the road's verges
for r_ in ((22, 104, 28, 108), (12, 120, 18, 124), (26, 121, 31, 123.5), (44, 108, 49, 110), (52, 116, 53, 123.5),
           (67, 113, 68, 123.5)):
    gfloor(T.rect(*r_), FLOWERS)

# ---- dry-stone walls round the fields, a gateway from the farmyard; lamps along the lanes; a signpost at the
# plaza's corner; benches looking out over the lake
FIELDS = (80, 106, 122, 122)
fw = G.rect(*FIELDS) & ~G.rect(80.5, 106.5, 121.5, 121.5) & ~G.rect(92, 106, 94, 106.5)
G.put(fw, 0, 1, RSTONE)
G.put(fw & ((np.floor(G.mx * 2) + np.floor(G.my * 2)) % 6 == 0), 1, 1.5, RSTONE)   # a few stones stand proud
for L, side in zip(LANES, (None, -1, 1, 1, 1)):                  # (the farm lane is lit by the farmyard)
    if side is None:
        continue
    lens = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(L, L[1:])]
    run = 6.0
    for (a, b), Ln in zip(zip(L, L[1:]), lens):
        while run < Ln:
            t = run / Ln
            px_, py_ = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
            nx_, ny_ = -side * (b[1] - a[1]) / Ln, side * (b[0] - a[0]) / Ln
            gput('Ground Lantern II', math.floor((px_ + 1.5 * nx_) * 2) / 2, math.floor((py_ + 1.5 * ny_) * 2) / 2)
            run += 12
        run -= Ln
G.put(G.rect(77, 88.5, 77.5, 89), 0, 3, RWOOD)                     # the signpost
G.put(G.rect(76, 88.5, 78.5, 89), 2.5, 3, RWOOD)
G.put(G.rect(77, 87.5, 77.5, 90), 2, 2.5, RWOOD)
for (x_, y_, r_) in ((98.5, 55.5, 90), (70, 88.5, 180), (58, 87.5, 180)):
    gput('Bench', x_, y_, r_)

# ---- outcrops of stone on the hills
for (bx, by, r_, h_, sd) in ((10, 20, 1.5, 1.5, 11), (28, 12, 1.2, 1, 12), (6.5, 34, 1, 1, 13), (104, 9, 1.4, 1.5, 14),
                            (121.5, 26, 1.2, 1, 15), (6, 96, 1.2, 1, 16), (122, 70, 1, 1, 17)):
    boulder(bx, by, r_, h_, RSTONE, sd)

# ================================================================= blocks nobody can see: the rock's heart, the walls' cores
# and the like, swapped for Rough Stone (2 Stone makes 100) before they're written back, for the costly materials
# only. The rock keeps a 1 m skin of granite wherever it shows (a terrain material's smoothed surface reaches
# further in), the walls 0.5 m. A core is swapped only where it's a metre or more, trimmed to whole metres, so the
# pieces come in few sizes and the palette keeps room to spare.
CORE = ('Rough Stone Block (hidden core)', '#7d776a')
CORE_OF = {"Granite (the isle's rock)", 'Polished Granite Block', 'Ancient Dungeon Block', 'Midnight Tomb Block',
           'Moonstone Block', 'Ancient Stone Block'}
SWAPPED = hide_unseen(P, list(VX.values()), CORE, skin=lambda n: 2 if n.startswith('Granite') else 1,
                      keep=lambda n: n not in CORE_OF, snap=2, min_run=2)

# ================================================================= write the carved blocks back as pieces
TRIMS = {}
for lid, v in VX.items():
    TRIMS[lid] = v.emit()

# ================================================================= the levels' groups in the planner's lists (trim levels follow
# their main level)
LEVEL_GROUPS = [
    ('Crown and roofs', r'top|dais|up29|sp48|r\d+'),
    ('Rock rooms', r'rk0|rkA|rkB|rkC'),
    ('Ground buildings', r'ground|farm2|wloft|gwell|crane|gr\d+'),
    ('Grounds', r'g\d{3}|gpav'),
    ('Hidden levels', r'deep\w*|ocul\w*|ugs|tun|tunshaft'),
    ('Anchors and water', r'pyl|chain|falls|lake'),
]
for L in P.levels:
    if re.search(r'_t\d+$', L['id']):
        continue
    g_ = next((g for g, pat in LEVEL_GROUPS if re.fullmatch(pat, L['id'])), None)
    if g_:
        L['group'] = g_
    else:
        print('level without a group:', L['id'])

# ================================================================= the spawn point, and checks
P.item('ground', 'spawn', 'Spawn point', 59.5, 116, 1, 1, 0.5, 180, '#2fa36b')   # the road in, facing the isle
if __name__ == '__main__':
    print('hidden blocks swapped for Rough Stone:', sum(SWAPPED.values()), {k: v for k, v in sorted(SWAPPED.items(), key=lambda kv: -kv[1])})
    print('trim levels:', {k: len(v) for k, v in TRIMS.items() if v})
    print('levels:', len(P.levels))
    problems = P.check(outdoor_ok=('lake', 'ground') + tuple(GL.values()), ignore_types=('stairs', 'large-water-wheel', 'secret-stone-floor-passage'))
    print('item problems:', len(problems))
    for p_ in problems[:30]:
        print('  ', p_)
    access = P.check_access()
    print('access problems:', len(access))
    for p_ in access[:40]:
        print('  ', p_)
    outside = P.altar_problems()
    print("outside the altar's build volume:", len(outside))
    for p_ in outside[:10]:
        print('  ', p_)

NOTES = """The Anchored Isle: a floating island base, as a 0.5 m plan (128 x 128 m, a 120 m build area). Pass 3 of 3 (the stairs, the furnishing and the small things). Drafted by Claude.

THE IDEA: a rock 60 x 50 m floats over a lake, its top at +28 m. Under it: a 5 m rim, a full belly down to +9 m, and pointed crags hanging from the belly, clustered under the middle, the deepest (the keel) down to +3 m. Chains hold it to three rune pylons. It floats because of what's buried beneath it: a summoning circle in a hidden chamber under the lake, whose oculus looks up through the water at the keel. A real waterfall pours off the east rim past a water wheel set into the island's side.

PASSES
1. The blockout: the terrain, the isle's shape and the rooms carved in it, every building as plain massing, the bridge, the pylons and chains, the falls, the hidden chamber; the 11 craftspeople as placeholders.
2. The buildings: every building and room given its character, with doors and windows; then a second go-over for the details and accents (below).
3. The stairs, the furnishing and the small things (below).
4. The grounds: terraforming and dressing the land round it all (below).
5. The final review: connections, details and finish (this one, below).

HOW THE BUILDINGS ARE MADE
- Crown masonry walls are 2 m thick, with depth carved out of them: bays recessed 1 m under round arches between full-thickness piers, deep reveals for every door and window, niches inside. A projecting Ancient Stone plinth and cornice round each building. Moonstone walls, Ancient Stone trim, gold only on the rotunda and the descent. Few materials, so the shapes do the work.
- The rooms in the rock are vaulted (barrel vaults and shallow domes), with rock pillars left standing, and alcoves and niches cut into the walls. A room is only cut where the rock is thick enough under it and round it.
- A square that holds two pieces (a sill and a lintel, a wall and a cornice) puts the extra one on a trim level at the same height: top_t1, ground_t1 and so on.
- Hidden cores: blocks nobody can see (the heart of the rock, the cores of the thick walls, the walls of the hidden levels behind the earth) are Rough Stone Block (hidden core), which is 2 Stone a hundred, instead of granite, Moonstone, Ancient Stone, Ancient Dungeon, Midnight Tomb or Polished Granite. A block counts as seen if anything open touches it, even at an edge or corner: air, water, glass, a door or window. The rock keeps a 1 m skin of granite wherever it shows, the walls 0.5 m. Cores are swapped in whole metres, a metre or more at a time. Build a thick wall's core in Rough Stone and face it with the real block; the Layers view shows where the cores run.

THE CROWN (+28 m)
- The Flame Rotunda: a drum 19 m across, 10 m tall. Eight arched bays round it: doors in the four facing the court (Huge Ancient Door), the hall, the bathhouse and the gallery (Ancients Night Doors with a round lunette window over each); blind arches between. Eight niches inside. A copper dome with eight gold ribs, an oculus over the altar, and a lantern round the oculus with a copper cap and a gold finial. The altar stands on a two-step dais (Ancient Stone, then Ancient Circles) under the oculus.
- Valory's great hall (14 x 22 m, 10 m walls): three arched bays a side with twin lancets and a round window in each arch; the door to the rotunda; a great fireplace in the west wall, its chimney stack rising through the roof; a proscenium arch to a stage in an apse to the north, a big round window behind the stage; a deep portal and a rose window in the south gable.
- Alden Crowley's gallery (22 x 11 m, 8 m walls) on the north rim: four arched bays on its south front, a taller frontispiece with a cross gable over the door; three oriels hanging over the void on stepped corbels, with window seats; a corbelled turret on the north-east corner.
- Elio Ricci's bathhouse (14 x 14 m): a deep portal with steps up to a podium inside, statue niches beside it; the plunge pool sunk a metre below the podium; a lantern on the low hip roof to let the steam out; a round door onto the spring's terrace, where the spring is sunk in the podium and spills over a weir to the falls.
- Balthazar's laboratory: a glass dome on a 12 m drum, eight stone buttresses that run on up the glass as ribs to a stone boss; tall windows N, E and S; his flue to the north-east.
- The Starspire (7 m across, to +58 m): at the hall's south-west corner by the bridge's landing, its west side corbelled out over the rim; Starlight walls on a plinth, string courses, slits climbing round it, a corbelled gallery round the top room, a flared cone and a gold finial. Its door shares a small forecourt with the hall's portal.
- The descent: the shaft's gold parapet, four rune lamps round it.
- The chain bridge: parapets along it; the stair tower's top has a parapet and four pinnacles.

INSIDE THE ROCK
- +21 m: the forge (16 x 14 m, barrel-vaulted, three tool bays and the hearth's hood cut in its walls); the hall of the descent (a shallow dome on four rock pillars, a walkway and parapet round the shaft); the mill (vaulted, tarred beams, a window and the axle's hole onto the wheel, which turns in a pit cut into the island's side).
- +15 m: the corridor; the dormitory (barrel-vaulted, seven arched bed alcoves); the vault behind a round door (six piers making bays for the chests); the cellars (two vaulted aisles on a row of piers).
- +9 m: the keel lookout (domed, eight slits looking out all round).

THE GROUND (0 m)
- The moon gate: a Moonstone wall with a round opening 8 m across and a rune keystone, under a shingled coping.
- Mei-Yin Chen's stall: open-fronted, a counter, a deep tiled awning on posts.
- The stair tower (12 x 12 m, 28 m): clasping buttresses in two stages, a deep portal to the plaza, slits climbing with the stair, a corbelled crown.
- Emily Fray's farmhouse: stone below, half-timber jettied out above, a thatched roof with a dormer, a porch, its chimney on the east gable.
- Athalan Skree's lodge: log walls on a stone course, the logs crossing past the corners, a stone chimney on the west gable, a porch to the east.
- Cade Hawthorn's workshop: half-timber on stone, a wagon entrance under a tarred beam, a hoist gable over it with an open loading hatch and its beam.
- Captain Melville Fontane's boathouse: stone below, tarred wood above, the water door under a round window in the lake-side gable, the jetty out from it (south of where the falls land).
- The rune pylons: stepped polished granite obelisks with gold pyramidions, a rune glowing in a pointed recess on each face.

HIDDEN BELOW (-16 m) - two secret ways in: the hidden stair under the stair tower, and the long tunnel from the pavilion on the north-east hill
- The summoning chamber (24 m across): Midnight Tomb walls with twelve pilasters and niches between them (the four facing the compass glow blue), a stepped dome up to the oculus, the circle sunk two steps into the floor.
- The hidden passage: barrel-vaulted with ribs every 4 m, rune lamps in niches.
- Loraine Crim's study: shelf niches down both walls, a barrel vault, a reading dais.

DETAILS AND ACCENTS (the second go-over)
- Archivolts: every arched bay and portal on the crown, and the stair tower's portal, is framed by a ring of Ancient Stone; keystones over the main portals, gold over the rotunda's four doors. Stone rings round the round windows and the moon gate.
- Sills under the windows set in bays; the hall's lancets share one.
- Finials: stone with a gold tip on the hall's gables and the gallery's cross gable; gold on the turret, the bath's lantern and the lab's boss; gold tips on the tower-top pinnacles and the Starspire's gallery pinnacles. A glowing band under the Starspire's eaves.
- Lights: wall lanterns either side of the main doors (rotunda, hall, gallery, bath, Starspire, stair tower, workshop, farmhouse, lodge, boathouse), braziers in the rotunda's four blind arches, lanterns under the stall's awning, ground lanterns at the moon gate, torches down the corridor in the rock.
- Valory's red banner on a gold rod by the hall's portal; a brick pot on the hall's chimney; a ring set in the court's paving through the four rune lamps.
- The bath: a figure on a plinth in each niche by its portal, taller piers at the weir. The lab: herb pots by the door, a copper cowl on the flue.
- On the ground: shutters on the farmhouse's south front, pots on its porch, a chimney pot; the Hunter's bow over the lodge door, a bench and firewood on the porch; the hoist's chain and hook, timber by the workshop wall; the Fisher's trophy over the boathouse door, a finial on its lake gable, a barrel and a crate on the jetty and a rowing boat moored by it; crates and sacks behind the trader's counter.
- Furniture and light sizes are estimates until measured (the same table as Laketown's).

PASS 3: THE STAIRS, THE FURNISHING AND THE SMALL THINGS
- Stairs: spiral stairs in blocks, a tread a block higher each step. The stair tower's climbs 28 m round a granite newel to the bridge's head (2.9 m wide treads); under its floor, beneath a Secret Stone Floor Passage, the hidden spiral goes down 16 m to the passage. The descent's spirals round the open well of the shaft from the keel lookout up to the court, stepping off at the dormitory level and the hall of the descent through gaps in the parapets, a fire burning at the bottom of the well. The Starspire's climbs round a Starlight newel to its top room. Steps up to the bard's stage; a staircase in the farmhouse; a ladder to the workshop's loft.
- The crane on the north-west rim: post, jib out over the void, brace, counterweight, winch, and its chain hanging 25 m to a crate over the timber yard's landing.
- Every craftsperson's stations: the Blacksmith's forge (under the hood), smelter, blast furnace, charcoal kiln, smithing tools and quench trough; the Alchemist's alchemy station, laboratory, mortar and grinding stones; the Carpenter's kiln, workbench, decoration and Sparkworks workbenches, table saw and masonry tools; the Hunter's tanning station, drying racks, hand spindle, spinning machine, loom and spinning wheel; the Farmer's oven, kitchen and cooking station, seedbeds and beehives; the Mill by the wheel's axle; the Researcher's Infusion Altar on the summoning circle under the oculus, her Gem Forge and Ancient Workbench in the study.
- Beds: seventeen in the dormitory for the other survivors (seven in the alcoves), and one for each craftsperson near their work (Valory in her hall, Alden in his gallery, Elio by the bath, Balthazar's cot in the lab, Oswald in the forge, Emily upstairs at the farm, Athalan in the lodge, Cade in the workshop's loft, the Captain in the boathouse, Mei-Yin behind her counter, Loraine in her study).
- Storage: magic chests in the vault's bays and an enormous one at its end, quick stack stations by its round door, a map table; chests in each workshop; the cellars' shelves, barrels and crates.
- Living detail: the hall's banqueting tables down a carpeted aisle, tie beams with lanterns hung from them, shields on the piers, a fireplace; mannequins, showcases, cabinets and window seats in the gallery; braziers in the rotunda's niches and a carpet to the altar; a tub, the Barber's basin and chair and benches by the pool; the Water Dispenser feeding the spring; herbs, a cauldron and a cat in the lab; a model of the isle, shelves, a desk on the dais and a cat in Loraine's study; skull torches round the circle; a long table in the dormitory; the farmhouse's window boxes, its well with a windlass and a thatched roof, the scarecrow, the pen's fence, gate, feeders and the animals' beds; the lodge's fireplace, rug, dog's bed, racks and firewood under the eaves, hide frames and vats in the tannery yard; the workshop's hammer left on the bench, stacked timber and log piles; the boathouse's boat on the slip, nets on the wall, a fishing spot; benches, lamp posts, a notice board and market crates on the plaza; lamp posts, benches and flower beds on the crown; rune posts along the bridge, rune stones round each pylon, and a glow at the keel's tip.

THE GROUNDS (pass 4)
- The land: everything built sits on a flat pad at 0 m, and lanes at 0 m run between the pads. The open land rolls into hills between them, easing up from the pads and the lake shore and dying away to flat ground within 14 m of the canvas's edge, so it blends into flat land round it. Hills: the north-west and the north-east, up to 5 m (their tops cut flat at 4 m for the stone circle and the pavilion), the west and the south-west meadow, softer rises in the east. The lake's shore is less regular, with a pebble strand round it.
- Lanes: plaza to farmyard, plaza to boathouse along the south-east shore, plaza to lodge, lodge to timber yard, timber yard to boathouse along the north-east shore, lamps along them. Hill paths of field stones follow the ground up to the stone circle, the pavilion and all three pylons.
- Water: a brook from a spring pool high in the north-east hills, stepping down in little cascades, then winding across the low ground into the lake under a plank bridge where the lane crosses it. A lily pond in the south-west meadow with stepping stones and a bench.
- The stone circle on the north-west hilltop, where the isle was first anchored: eight weathered monoliths (four rune-capped) round a low altar stone, on a ring of Ancient Stone. The pavilion on the north-east hilltop: six Moonstone columns, a copper roof, a bench looking out at the isle.
- Boulders that fell when the isle rose, half sunk round the lake and one at the plaza's edge, in the isle's own rock; outcrops of stone on the hills.
- Trees (from the Farmer's seedlings): an avenue of broadleaf trees up the road in, with shrubs between; an orchard of nine by the pond; evergreen woods on the north-west hill and the west; broadleaf and evergreen clumps on the north-east hills; a shade tree in the farmyard. Drifts of wildflowers in the meadow and along the road. Dry-stone walls round the fields with a gateway from the farmyard. A signpost at the plaza's corner, benches looking out over the lake.
- Anything on raised ground (a path, water, a rock, a tree, a bench) is on the level at that ground's height ('Grounds at +1 m' and so on), since a level digs out the ground above its floor wherever it's painted.

THE FINAL REVIEW (pass 5)
- Walked it: a check that searches on foot from the spawn point, as walk mode does (steps of a block, any drop, 2 m of headroom), now finds every room, bed, station, chest and survivor reachable. On the way it caught and fixed: the walkway round the shaft had re-floored the shaft at the dormitory level, so the descent stopped there; the Starspire's opening into its top room was a tread short for headroom; the north-west lawn (the crane) was walled off by the hall's and the gallery's plinths meeting at a corner, now with a way between them; the workshop's loft had only a ladder, which walk mode can't climb, now a staircase.
- Nothing clips: the study's shelves now stand on their niches' sills, and a tree moved off a pylon's rune stone.
- The secret ways down (at the user's ask): the tower's hidden stair turned so its top opens where the stair up is 4 m and more overhead, one tread more open, the passage's vault kept out of its shaft; the trapdoor is now a label on the map ("Secret floor"), not an item. A second secret way from the pavilion: a secret floor over a spiral stair 20 m down a lined shaft, then the long tunnel (about 70 m, vaulted, ribbed, rune-lit, a rest room halfway with benches and a brazier) south-west under the lake into the summoning chamber, through a door in place of one of its niches. The walking check now models walk mode's body (0.6 m across, so 2 x 2 squares); it caught braziers pinching the forge's and mill's passages, beds 0.5 m apart in the dormitory, and the stall's counter shutting Mei-Yin in, all fixed.
- Finishing touches: a rail round the stair's opening on the tower top (open where you step off), a balustrade along the crown's rim wherever the paving runs out to the drop, the jetty's barrel and crate moved to its land end so the fishing spot's end is clear.

SIZES: the Ancient doors and windows, the stone round window and the Carved and Metal Bound doors are estimates until measured; the wooden ones are the user's measurements. Rooms stay generous: the hall 10 x 18 m inside, the gallery 18 x 7.5 m, the bath 10 x 10 m, the lab 10 m across, the forge 16 x 14 m, the dormitory 13.5 x 14 m.

IN GAME, TO CHECK: that the Farmer's seed list has the Broadleaf and Evergreen Trees and Shrubs in 1.0 (a guide lists them; older posts say trees couldn't be planted), and their sizes; the sizes of the stations, furniture and lights (estimates, as in Laketown) and of the Secret Stone Floor Passage; that blocks stay put in mid-air (most sources say Enshrouded has no structural integrity); a Water Dispenser for the falls and a drain in the lake.
CONFIRMED IN GAME (2026-10-18): the Flame Altar can be placed up in the air, on a built floor, as it is here.
"""
if __name__ == '__main__':
    print('bytes', P.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'isle.json'), NOTES, 'r-claude-isle-11'))
    print('levels', len(P.levels), 'items', len(P.items), 'palette', len(PALETTE))
