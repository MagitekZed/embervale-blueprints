"""English manor: the house, 0.5 m detail plan (every square is one single block).

A Palladian villa: a two-tone stone main block with a giant portico, a round domed saloon that bows out on
the garden front, two-storey bay windows, curved quadrant colonnades to a brick kitchen pavilion and a glass
orangery, and a house full of secrets.
Run: python manor_house.py  ->  writes manor-house.json. Then manor_site.py stamps it into the estate.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manor_common import Plan, PALETTE

PALETTE.update({
    'n': {'name': 'Polished Granite Block', 'kind': 'floor', 'color': '#626c7a'},           # hall checkerboard
    'u': {'name': 'Red Marble Block', 'kind': 'floor', 'color': '#643f43'},                 # saloon inlay
    'W': {'name': 'Refined Wood Block (panelling)', 'kind': 'wall', 'color': '#75675f', 'height': 2.5},   # attic partitions
    'j': {'name': 'Jib door (flush with the wall)', 'kind': 'door', 'color': '#b9ab98'},
    'F': {'name': 'Secret door (swinging fireplace)', 'kind': 'door', 'color': '#6f6a66'},
    'T': {'name': 'Trapdoor', 'kind': 'floor', 'color': '#5d5652'},
})
P = Plan('English manor: the house', 0.5, 72, 48, 120)
P.project = 'English manor'
cel = P.level('cel', 'Cellars, crypt & secret ways (−4 m)', -4, 4)
g0 = P.level('g0', 'Ground floor (state rooms)', 0, 4)
g1 = P.level('g1', 'First floor', 4, 4)
att = P.level('att', 'Attic & whispering gallery (8 m)', 8, 3)
rf = P.level('roof', 'Roofs & cornice (8 m)', 8, 7)
drum = P.level('drum', 'Saloon drum (8 m)', 8, 6)
R = P.rect


def blk(name, h, base=0, color='#b3b0a9', under=None):
    e = {'name': name[:40], 'kind': 'block', 'color': color, 'height': h}
    if base: e['base'] = base
    if under: e['under'] = under
    return P._alloc(e)


def wal(name, h=None, color='#ada198'):
    return P._alloc({'name': name[:40], 'kind': 'wall', 'color': color, **({'height': h} if h else {})})


def ring(g, cx, cy, r0, r1, ch, only=None, keep=None):
    for x, y in P.cells_rect(cx - r1 - 1, cy - r1 - 1, cx + r1 + 1, cy + r1 + 1):
        d = P.dist(x, y, cx, cy)
        if r0 <= d < r1 and (only is None or g[y][x] in only) and (keep is None or keep(*P.centre_m(x, y))):
            g[y][x] = ch


def at_angle(cx, cy, r, deg):                               # the square (top-left, metres) at a compass angle on a circle
    a = math.radians(deg)
    return (math.floor((cx + r * math.sin(a)) * 2) / 2, math.floor((cy - r * math.cos(a)) * 2) / 2)


X0, X1, Y0, Y1 = 20, 52, 14, 34                             # main block outer faces
SC = (36, 30)                                               # the round saloon's centre
SR = 5.0                                                    # its inner radius
ST0, ST1 = 'S', 'A'                                         # rusticated Limestone below, Sandstone ashlar above

# ================================================================= quadrant colonnades and pavilions (drawn first)
def in_quadrant(cx, sign):
    return lambda mx, my: (mx - cx) * sign <= 0.25 and my >= 6


def quadrant(g, cx, sign):
    """A quarter-circle gallery centred at (cx, 6): open columns on the forecourt side, a windowed outer wall."""
    inq = in_quadrant(cx, sign)
    ring(g, cx, 6, 7.0, 8.5, ',', keep=inq)
    ring(g, cx, 6, 8.5, 9.0, ST0, keep=inq)
    for deg in range(0, 91, 15):                            # columns on the inner edge
        a = math.radians(deg)
        x, y = cx - sign * 7.25 * math.cos(a), 6 + 7.25 * math.sin(a)
        R(g, math.floor(x * 2) / 2, math.floor(y * 2) / 2, math.floor(x * 2) / 2 + 0.5, math.floor(y * 2) / 2 + 0.5, 'P')
    for deg in (22, 45, 68):                                # windows in the outer wall
        a = math.radians(deg)
        x, y = cx - sign * 8.75 * math.cos(a), 6 + 8.75 * math.sin(a)
        R(g, math.floor(x * 2) / 2, math.floor(y * 2) / 2, math.floor(x * 2) / 2 + 0.5, math.floor(y * 2) / 2 + 0.5, 'o', only=ST0)


def quadrant_roof(roof, cx, sign):                          # lean-to: low over the colonnade, high at the outer wall
    inq = in_quadrant(cx, sign)
    for x, y in P.cells_rect(cx - 10, 5, cx + 10, 16):
        mx, my = P.centre_m(x, y); d = math.hypot(mx - cx, my - 6)
        if inq(mx, my) and 6.5 <= d <= 9.5:
            roof.put(x, y, 0.5 + (d - 6.5) * 0.6, 'slate')


quadrant(g0, 22, 1); quadrant(g0, 50, -1)
R(g0, 12, 5, 14.5, 7, ','); R(g0, 12, 4.5, 14.5, 5, ST0); R(g0, 12, 7, 14, 7.5, ST0)          # connectors to the pavilions
R(g0, 57.5, 5, 60, 7, ','); R(g0, 57.5, 4.5, 60, 5, ST0); R(g0, 58, 7, 60, 7.5, ST0)
# kitchen pavilion (west): brick, two storeys, a great hearth, a smoke lantern on the roof
for g, fl in ((g0, ';'), (g1, '.')):
    P.box_walls(g, 2, 2, 12, 18, 'K', 1, floor=fl)
    for y in (6, 9.5, 14): R(g, 2, y, 3, y + 1, 'o')
    for x in (4, 9): R(g, x, 17, x + 1, 18, 'o')
R(g0, 3, 11, 11, 11.5, 'K'); R(g0, 7, 11.5, 7.5, 17, 'K'); R(g0, 5, 11, 6.5, 11.5, 'D'); R(g0, 8.5, 11, 10, 11.5, 'D')
R(g0, 11, 5, 12, 7, 'D'); R(g0, 6, 2, 8, 3, 'D')
R(g0, 5, 3, 9, 4, blk('Limestone Block (great hearth)', 2, color='#a79a88'))
R(g0, 3.5, 12, 5.5, 16, ' ')                                # stairwell down to the larder
R(g1, 8.5, 12, 10.5, 16, ' ')                               # stairwell up from the back stairs
R(g1, 3, 11, 11, 11.5, 'K'); R(g1, 5, 11, 6.5, 11.5, 'D')
# orangery (east): stone back walls, glazed front between piers, 8 m tall
for g in (g0, g1):
    P.box_walls(g, 60, 2, 70, 18, 'A', 1)
    R(g, 61, 17, 69, 18, 'q'); R(g, 69, 3, 70, 17, 'q')
    for x in (63, 65.5): R(g, x, 17, x + 0.5, 18, 'P')
    for y in (5.5, 8.5, 11.5, 14.5): R(g, 69, y, 70, y + 0.5, 'P')
R(g0, 61, 3, 69, 17, ','); R(g0, 60, 5, 61, 7, 'D')
for (x0, y0, x1, y1) in ((61.5, 3.5, 68.5, 5), (61.5, 15, 68.5, 16.5), (61.5, 5, 63, 15)):
    R(g0, x0, y0, x1, y1, 'f')
P.disc(g0, 66, 10, 1.8, 'c'); P.disc(g0, 66, 10, 1.3, '~')

# ================================================================= main block shell, both storeys
for g, st in ((g0, ST0), (g1, ST1)):
    P.box_walls(g, X0, Y0, X1, Y1, st, 1)
    fl = ',' if g is g0 else '.'
    for sgn in (-1, 1):                                     # two-storey canted bays: drawing room (W), library (E)
        xa, xb = (X0 - 1.5, X0) if sgn < 0 else (X1, X1 + 1.5)
        R(g, xa, 26, xb, 31, fl)
        R(g, xa, 26, xb, 26.5, st); R(g, xa, 30.5, xb, 31, st)
        face = (xa, xa + 0.5) if sgn < 0 else (xb - 0.5, xb)
        R(g, face[0], 26.5, face[1], 30.5, 'o')
        R(g, X0 if sgn < 0 else X1 - 1, 26.5, X0 + 1 if sgn < 0 else X1, 30.5, fl)
    ring(g, *SC, SR, SR + 0.5, st, keep=lambda mx, my: my < Y1 - 1)            # round saloon wall inside the block
    ring(g, *SC, SR, SR + 1.0, st, keep=lambda mx, my: my >= Y1 - 1)           # and the bow it pushes through the front
    P.disc(g, *SC, SR, ' ')
R(g0, 21, 15, 28.5, 24, '.'); R(g0, 22.5, 16.5, 27, 22.5, 'r')                 # dining room (NW): parquet and a rug
R(g0, 21, 24.5, 28.5, 33, 'r')                                                  # drawing room (SW)
R(g0, 43.5, 15, 51, 24, ',')                                                    # stair hall (NE)
R(g0, 43.5, 24.5, 51, 33, '.')                                                  # library (SE)
for x, y in P.cells_rect(29, 15, 43, 24):                                       # columned hall: checkerboard marble
    g0[y][x] = 'n' if (int(x / 2) + int(y / 2)) % 2 else ','
for x, y in P.cells_rect(SC[0] - SR, SC[1] - SR, SC[0] + SR, SC[1] + SR):       # saloon: marble with a compass rose
    mx, my = P.centre_m(x, y); d = math.hypot(mx - SC[0], my - SC[1])
    if d < SR:
        ang = math.degrees(math.atan2(mx - SC[0], -(my - SC[1]))) % 45
        g0[y][x] = 'u' if (abs(d - 3.6) < 0.3 or d < 0.8 or (d < 3.4 and min(ang, 45 - ang) < 11 * (1 - d / 3.4))) else ','
for (x, y) in ((30.5, 17), (30.5, 21), (40.5, 17), (40.5, 21)):                 # the hall's four columns
    R(g0, x, y, x + 1, y + 1, 'P')
for g in (g0, g1):                                                              # partitions
    R(g, 28.5, 15, 29, 33, 'A'); R(g, 43, 15, 43.5, 33, 'A')
    R(g, 21, 24, 28.5, 24.5, 'A'); R(g, 43.5, 24, 51, 24.5, 'A'); R(g, 29, 24, 43, 24.5, 'A')
    for x, y in P.cells_rect(29, 24.5, 43, Y1 - 1):                             # solid masonry round the saloon...
        mx, my = P.centre_m(x, y)
        if math.hypot(mx - SC[0], my - SC[1]) >= SR + 0.5:
            g[y][x] = 'A'
POCKETS = {                                                                     # ...hollowed out for secrets
    'nw': (29.5, 25, 31, 26.5),                                                 # servants' shaft
    'ne': (41, 25, 42.5, 26.5),                                                 # the scholar's shaft
    'sw': (29.5, 31.5, 30.5, 33),                                               # priest hole
    'se': (41.5, 31.5, 42.5, 33),                                               # muniment room
}
for g in (cel, g0, g1, att):
    for k in ('nw', 'ne'): R(g, *POCKETS[k], ' ')                               # the shafts run through every floor
for k in ('sw', 'se'): R(g0, *POCKETS[k], ';')
# doors, ground floor
R(g0, 34.5, 14, 37.5, 15, 'G'); R(g0, 34.5, 24, 37.5, 25, 'G')                  # entrance; hall to saloon
R(g0, 35, 35, 37, 36, 'D')                                                      # saloon to the terrace, through the bow
R(g0, 28.5, 19, 29, 21, 'D'); R(g0, 43, 19, 43.5, 21, 'D')                       # hall to dining room and stair hall
R(g0, 24, 24, 25.5, 24.5, 'D'); R(g0, 46, 24, 47.5, 24.5, 'D')                   # dining to drawing; stair hall to library
R(g0, 21.5, 14, 23.5, 15, 'D'); R(g0, 48.5, 14, 50.5, 15, 'D')                   # from the quadrants
R(g0, 29.5, 24, 31, 25, 'j'); R(g0, 28.5, 25, 29.5, 26.5, 'j')                   # jib doors to the servants' shaft
R(g0, 42.5, 25, 43.5, 26.5, 'X')                                                 # library bookcase: the scholar's shaft
R(g0, 28.5, 31.5, 29.5, 32.5, 'F')                                               # the drawing-room fireplace swings open
R(g0, 42.5, 31.5, 43.5, 32.5, 'x')                                               # library panel: muniment room
# windows on both floors, one grid
for g, st in ((g0, ST0), (g1, ST1)):
    for x in (22.5, 25.5, 30.5, 40.5, 45.5, 48.5): R(g, x, Y0, x + 1, Y0 + 1, 'o', only=st)
    for x in (22.5, 25.5, 45.5, 48.5): R(g, x, Y1 - 1, x + 1, Y1, 'o', only=st)
    for y in (17, 20.5):
        R(g, X0, y, X0 + 1, y + 1, 'o', only=st); R(g, X1 - 1, y, X1, y + 1, 'o', only=st)
    for deg in (145, 215):                                                      # tall windows in the bow
        x, y = at_angle(*SC, SR + 0.5, deg)
        R(g, x - 0.5, y - 0.5, x + 0.5, y + 0.5, 'o', only=st)
R(g1, 35.5, 35, 36.5, 36, 'o', only=ST1)
# library: shelved walls (the secret doors are bookcases too), a fireplace, the opening to the bay
P.lining(g0, 'A' + ST0, 'Y', '.', P.sq(43.5), P.sq(24.5), P.sq(51), P.sq(33))
R(g0, 43.5, 25, 44, 26.5, '.'); R(g0, 43.5, 31.5, 44, 32.5, '.'); R(g0, 46, 24.5, 47.5, 25, '.'); R(g0, 46.5, 32.5, 48.5, 33, '.')
R(g0, 50.5, 26.5, 51, 30.5, '.')
# imperial stair of floating stone treads, with a landing over a cupboard
tread = lambda top: blk(f'Highly Polished Stone (tread {top:g} m)', 0.5, top - 0.5, under=',' if top > 0.5 else None)
for k in range(5):                                                              # central flight, rising north
    R(g0, 46, 22.5 - k * 0.5, 49.5, 23 - k * 0.5, tread(0.5 * (k + 1)))
R(g0, 44.5, 15, 51, 20.5, blk('Highly Polished Stone (stair landing)', 0.5, 2.0, under=','))   # landing at 2.5 m...
pier = blk('Highly Polished Stone (landing pier)', 2.5)                         # ...walled underneath: a cupboard
R(g0, 44.5, 15, 45, 20.5, pier); R(g0, 44.5, 20, 51, 20.5, pier)
R(g0, 44.5, 17, 45, 18, 'j')                                                    # cupboard door, off the side passage
R(g0, 49.5, 17, 50, 17.5, blk('Highly Polished Stone (stair landing)', 0.5, 2.0, under='T'))   # trapdoor in the cupboard floor
for k in range(3):                                                              # return flights, rising south to 4 m
    for (xa, xb) in ((44.5, 46), (49.5, 51)):
        R(g0, xa, 20.5 + k * 0.5, xb, 21 + k * 0.5, tread(3.0 + 0.5 * k))

# ================================================================= first floor
R(g1, 21, 15, 28.5, 24, 'r')                                                    # state bedroom
R(g1, 21, 24.5, 28.5, 33, '.')                                                  # guest room & bath
R(g1, 29, 15, 43, 24, 'r'); R(g1, 29.5, 15.5, 42.5, 16, ','); R(g1, 29.5, 23, 42.5, 23.5, ',')   # long gallery
ring(g1, *SC, SR - 1.25, SR, ','); ring(g1, *SC, SR - 1.25, SR - 1.0, 'w')      # saloon gallery round the void
R(g1, 43.5, 22, 51, 24, ','); R(g1, 46, 22, 49.5, 22.5, 'w')                    # stair landing, open over the flights
lib_gal = lambda mx, my: mx < 44.5 or mx >= 50 or my < 25.5 or my >= 32
for x, y in P.cells_rect(43.5, 24.5, 51, 33):                                   # library gallery round the walls
    if lib_gal(*P.centre_m(x, y)): g1[y][x] = '.'
R(g1, 44.5, 25.5, 50, 26, 'w'); R(g1, 44.5, 31.5, 48, 32, 'w'); R(g1, 44.5, 25.5, 45, 32, 'w'); R(g1, 49.5, 25.5, 50, 32, 'w')
R(g1, 34.5, 24, 37.5, 25, 'D')                                                  # long gallery to the saloon gallery
R(g1, 43, 22, 43.5, 23.5, 'D'); R(g1, 46, 24, 47.5, 24.5, 'D'); R(g1, 28.5, 19, 29, 21, 'D'); R(g1, 24, 24, 25.5, 24.5, 'D')
R(g1, 28.5, 25, 29.5, 26.5, 'j')                                                # jib door: guest room to the servants' shaft
R(g1, 41, 24, 42.5, 25, 'x')                                                    # panel: long gallery to the scholar's shaft
# portico: six giant columns on a stylobate step, entablature, pediment
for g in (g0, g1):
    for x in (30.5, 32.5, 34.5, 36.5, 38.5, 40.5): R(g, x, 9, x + 1, 10, 'P')
R(g0, 30, 10, 42, 14, ',', only=' ')
R(g0, 30, 8.5, 42, 10.5, blk('Highly Polished Stone (stylobate step)', 0.5), only=' ')
R(g1, 30, 8.5, 42, 10.5, blk('Highly Polished Stone (entablature)', 1, 3), only=' ')
# garden terrace round the bow, balustraded, with a gap for the steps down to the parterre
R(g0, 18, Y1, 54, 40, 'm', only=' ')
R(g0, 18, 39.5, 32, 40, 'b'); R(g0, 40, 39.5, 54, 40, 'b'); R(g0, 18, Y1, 18.5, 40, 'b'); R(g0, 53.5, Y1, 54, 40, 'b')

# ================================================================= stone trim: sills, string course, aprons, cornice, quoins
foot = set()                                                                    # the main block's footprint
for x, y in P.cells_rect(X0 - 1.5, 8, X1 + 1.5, 37):
    mx, my = P.centre_m(x, y)
    if (X0 <= mx < X1 and Y0 <= my < Y1) or (X0 - 1.5 <= mx < X1 + 1.5 and 26 <= my < 31) \
            or math.hypot(mx - SC[0], my - SC[1]) < SR + 1 or (30 <= mx < 42 and 8.5 <= my < Y0):
        foot.add((x, y))
outside = sorted({(x + dx, y + dy) for (x, y) in foot for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - foot)
win_near = lambda g, x, y: any(g[y + dy][x + dx] == 'o' for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= y + dy < P.H and 0 <= x + dx < P.W)
apron, band, cornice = blk('Highly Polished Stone (window apron)', 1), blk('Highly Polished Stone (string course)', 0.5), blk('Highly Polished Stone (cornice)', 0.5)
for (x, y) in outside:
    mx, my = P.centre_m(x, y)
    if 29.5 <= mx < 42.5 and my < Y0 + 0.5: continue                            # behind the portico
    if win_near(g0, x, y) and g0[y][x] in (' ', 'm'):
        P.overlay(g0, x, y, 'Highly Polished Stone (window sill)', '#b3b0a9', 0.5, 0.5)
    if g1[y][x] == ' ': g1[y][x] = apron if win_near(g1, x, y) else band
    if rf[y][x] == ' ': rf[y][x] = cornice
for (cx, cy) in ((X0, Y0), (X1 - 1, Y0), (X0, Y1 - 1), (X1 - 1, Y1 - 1)):     # quoins at the corners
    R(g0, cx, cy, cx + 1, cy + 1, 'P'); R(g1, cx, cy, cx + 1, cy + 1, 'S')

# ================================================================= attic (8 m): maids' rooms, a secret room, a gallery inside the dome
R(att, 23, 17, 49, 31, '.')
ring(att, *SC, 0, SR + 1.0, ' ')
R(att, 24, 22, 48, 22.5, 'W')                                                   # maids' rooms along the north, a corridor behind
for x in (29.5, 36, 42.5): R(att, x, 18, x + 0.5, 22, 'W')     # partitions stop short of the eaves
for x in (26, 32.5, 39, 45.5): R(att, x, 22, x + 1, 22.5, 'D')
R(att, 24, 23.5, 31, 24, 'W'); R(att, 25, 23.5, 26, 24, 'D')                     # linen room (W): the servants' shaft comes up here
R(att, 41, 23.5, 48, 24, 'W'); R(att, 45, 23.5, 46, 24, 'x')                     # astronomer's room (E): only a panel, and the scholar's shaft
R(att, 40.5, 24, 41, 25, 'W')
ring(att, *SC, SR - 1.0, SR + 0.5, ','); ring(att, *SC, SR - 1.0, SR - 0.75, 'w')   # whispering gallery inside the drum
ring(drum, *SC, SR + 0.5, SR + 1.0, 'A')
for deg in range(0, 360, 45):                                                   # thermal windows round the drum
    x, y = at_angle(*SC, SR + 0.75, deg + 22.5)
    R(drum, x, y, x + 0.5, y + 0.5, 'o', only='A')
ring(drum, *SC, SR + 1.0, SR + 1.5, blk('Highly Polished Stone (drum cornice)', 0.5, 5.5))   # cornice where the dome sits
for x, y in P.cells_rect(SC[0] + SR + 0.4, SC[1] - 0.5, SC[0] + SR + 1.1, SC[1] + 0.5):   # door from the astronomer's room
    if drum[y][x] == 'A': drum[y][x] = 'x'

# ================================================================= cellars (−4 m)
P.box_walls(cel, X0, Y0, X1, Y1, 'R', 1, floor=';')
R(cel, 21, 21.5, 51, 22, 'R'); R(cel, 21, 24, 51, 24.5, 'R')                     # spine corridor (y 22-24)
R(cel, 28, 15, 28.5, 21.5, 'R'); R(cel, 40, 15, 40.5, 21.5, 'R'); R(cel, 28.5, 24.5, 29, 33, 'R'); R(cel, 43, 24.5, 43.5, 33, 'R')
for x, y in P.cells_rect(29, 24.5, 43, Y1 - 1):
    mx, my = P.centre_m(x, y)
    if math.hypot(mx - SC[0], my - SC[1]) >= SR + 0.5: cel[y][x] = 'R'
ring(cel, *SC, SR, SR + 0.5, 'R', keep=lambda mx, my: my < Y1 - 1)
ring(cel, *SC, SR, SR + 1.0, 'R', keep=lambda mx, my: my >= Y1 - 1)
P.disc(cel, *SC, SR, ',')                                                       # the crypt under the saloon
P.disc(cel, *SC, 0.75, 'R')                                                     # its central pier
for k in ('nw', 'ne'): R(cel, *POCKETS[k], ' ')
R(cel, 35, 24, 37, 25, 'D')                                                     # crypt door from the spine
R(cel, 28.5, 25, 29.5, 26.5, 'D')                                               # servants' shaft to the servants' hall
for t in range(12):                                                             # scholar's shaft: a crawl to a hidden door in the crypt
    mx, my = 41.75 + (SC[0] - 41.75) * t / 12, 25.75 + (SC[1] - 25.75) * t / 12
    x, y = P.sq(mx - 0.25), P.sq(my - 0.25)
    d = math.hypot(mx - SC[0], my - SC[1])
    if SR <= d < SR + 0.6: cel[y][x] = 'x'
    elif d >= SR + 0.6 and cel[y][x] == 'R': cel[y][x] = ';'
R(cel, 35, 35, 37, 36, 'x')                                                     # crypt to the deep tunnel (boathouse)
R(cel, 35, 36, 37, 40, ';'); R(cel, 34.5, 36, 35, 40, 'K'); R(cel, 37, 36, 37.5, 40, 'K')
R(cel, 24.5, 21.5, 26, 22, 'I'); R(cel, 33.5, 21.5, 35, 22, 'D'); R(cel, 45, 21.5, 46.5, 22, 'D')   # strong room, beer & wine cellars
R(cel, 24, 24, 25.5, 24.5, 'D'); R(cel, 46, 24, 47.5, 24.5, 'D')                # servants' hall, laundry
R(cel, 24, 15, 24.5, 21.5, 'R'); R(cel, 21, 18, 24, 18.5, 'R'); R(cel, 24, 16, 24.5, 17.5, 'x')   # false back wall: the treasure vault
for y in (16.5, 18.5, 20): R(cel, 41.5, y, 50.5, y + 0.5, 'v')                   # wine racks
R(cel, 51, 17, 52, 19, 'Q')                                                     # the wine-rack door: tunnel to the grotto
R(cel, 52, 17, 56, 19, ';'); R(cel, 52, 16.5, 56, 17, 'K'); R(cel, 52, 19, 56, 19.5, 'K')
R(cel, 20, 22, 21, 24, 'D')                                                     # servants' passage to the larder
R(cel, 7, 22, 20, 24, ';'); R(cel, 7, 21.5, 20, 22, 'K'); R(cel, 9, 24, 20, 24.5, 'K')
R(cel, 7, 18, 9, 22, ';'); R(cel, 6.5, 18, 7, 24.5, 'K'); R(cel, 9, 18, 9.5, 21.5, 'K'); R(cel, 7, 24, 9, 24.5, 'K')
P.box_walls(cel, 2, 2, 12, 18, 'K', 1, floor=';')
R(cel, 7, 17, 9, 18, 'D'); R(cel, 3, 11, 11, 11.5, 'K'); R(cel, 7.5, 11, 9, 11.5, 'D')

# ================================================================= roofs
roof = P.roof(rf)
roof.hip(X0, Y0, X1, Y1, 'slate', pitch=0.5, overhang=0.0, base=0.5)            # main block, behind a balustrade
roof.cut_disc(*SC, SR + 1.1)                                                    # the drum rises through it
for (x, y) in list(roof.h):                                                     # skylights over the maids' rooms
    mx, my = P.centre_m(x, y)
    if 17.5 <= my < 18.5 and any(a <= mx < a + 1.5 for a in (25, 32.5, 38, 45)):
        roof.mat[(x, y)] = 'glass'
roof.gable(30, 8.5, 42, Y0 + 0.5, 'y', 'stone', pitch=0.45, overhang=0.5, base=0.5)   # portico pediment
roof.hip(X0 - 1.5, 26, X0, 31, 'slate', pitch=0.8, overhang=0.0, base=0.5)      # bay roofs
roof.hip(X1, 26, X1 + 1.5, 31, 'slate', pitch=0.8, overhang=0.0, base=0.5)
roof.caps('slatecap', min_h=1.0)
roof.hip(2, 2, 12, 18, 'slate', pitch=0.8, overhang=0.5, base=0.5)              # kitchen pavilion...
LAN = 5.0                                                                       # ...and its smoke lantern on posts
roof.gable(5.5, 8, 8.5, 12, 'y', 'slate', pitch=0.8, overhang=0.5, base=LAN)
roof.hip(60, 2, 70, 18, 'stone', pitch=0.6, overhang=0.5, base=0.5)             # orangery: stone roof, glass lantern
for (x, y) in list(roof.h):
    mx, my = P.centre_m(x, y)
    if 63 <= mx < 67 and 4 <= my < 16 and roof.mat[(x, y)] == 'stone': roof.mat[(x, y)] = 'glass'
roof.paint(only=' ')
for x, y in P.cells_rect(X0, Y0, X1, Y1):                                       # balustrade round the main roof
    mx, my = P.centre_m(x, y)
    edge = mx < X0 + 0.5 or mx >= X1 - 0.5 or my < Y0 + 0.5 or my >= Y1 - 0.5
    if edge and not (30 <= mx < 42 and my < Y0 + 0.5) and PALETTE.get(rf[y][x], {}).get('kind') == 'roof':
        P.overlay(rf, x, y, 'Highly Polished Stone Block (balustrade)', '#b3b0a9', 1.0, 0)
for (x, y) in ((5.5, 8), (8, 8), (5.5, 11.5), (8, 11.5)):                       # lantern posts
    P.overlay(rf, P.sq(x), P.sq(y), 'Fired Bricks Block (lantern post)', '#aa7657', 1.5, LAN - 1.5)
stack = wal('Refined Sandstone Block (chimney)', 7.5)
for (cx, cy) in ((23, 17), (23, 29), (47.5, 17), (47.5, 29), (6.5, 2)):         # chimney stacks
    R(rf, cx, cy, cx + 1.5, cy + 1, stack)
qroof = P.roof(g1)                                                              # quadrant roofs (4 m up)
quadrant_roof(qroof, 22, 1); quadrant_roof(qroof, 50, -1)
qroof.paint(only=' ')
# the dome over the saloon: ribbed copper on the drum, an oculus, a lantern, a finial
DZ = 14
dl = P.level('dome', f'Dome ({DZ} m)', DZ, 6)
dm = P.roof(dl)
dm.dome(*SC, SR + 1.25, 4.0, 'copper', base=0.5, rim=0.8)
dm.ribs(*SC, [i * 45 for i in range(8)], 0.3, 1.6, SR + 1.25, 'stone', proud=0.5)
dm.cut_disc(*SC, 1.2)
dm.paint()
LZ = DZ + math.floor((dm.top(P.sq(SC[0] + 1.5), P.sq(SC[1])) or 4) * 2) / 2
lan = P.level('lan', f'Dome lantern ({LZ:g} m)', LZ, 2)
ring(lan, *SC, 1.0, 1.5, 'q')
for deg in (0, 90, 180, 270):
    x, y = at_angle(*SC, 1.25, deg); R(lan, x, y, x + 0.5, y + 0.5, 'P')
lanr = P.level('lanr', f'Lantern cap ({LZ + 2:g} m)', LZ + 2, 2)
lr = P.roof(lanr); lr.dome(*SC, 1.8, 1.2, 'copper', base=0.5, rim=0.9); lr.paint()

# ================================================================= items
I = P.item
I('g0', 'altar', 'Flame Altar', 34.5, 28.5, 3, 3, 3, color='#d9541e', iid='altar')
I('g0', 'npc-bard', 'Bard (in the columned hall)', 34.5, 17.5, 3, 3, 2, color='#b0596f', iid='bard')
for k, (x, y) in enumerate(((29.5, 17), (29.5, 21.5), (42, 17), (42, 21.5))):
    I('g0', 'custom', 'Statue in a niche', x, y, 0.5, 0.5, 2.5, color='#b3b0a9', iid=f'hst{k}')
I('g0', 'table', 'Dining table', 23, 18, 3.5, 4, 1, color='#9a7b52', iid='dine')
I('g0', 'custom', 'Sideboard', 21, 15.5, 2, 0.5, 1, color='#6b4a2e', iid='side')
I('g0', 'custom', 'Settee', 22, 27, 1, 3, 1, color='#8c6b4f', iid='set1')
I('g0', 'custom', 'Harpsichord', 24, 31.5, 2, 1, 1, color='#6b4a2e', iid='harp')
I('g0', 'lever', 'Candlestick lever (turns the fireplace)', 27.5, 32.5, 0.5, 0.5, 1, color='#c9a227', iid='lv_fire')
I('g0', 'table', 'Library table', 45.5, 28, 3, 1.5, 1, color='#9a7b52', iid='libt')
I('g0', 'custom', 'Armchair', 47.5, 26, 1, 1, 1, color='#8c6b4f', iid='arm1')
I('g0', 'custom', 'Globe', 50.5, 28, 1, 1, 1.5, color='#3fc2b0', iid='globe')
I('g0', 'ladder', 'Library ladder (to the gallery)', 48, 32, 1, 0.5, 4, color='#7a5236', iid='libladder')
I('g0', 'lever', 'A book that opens the bookcase', 44, 27, 0.5, 0.5, 1, color='#c9a227', iid='lv_book')
I('g0', 'table', 'Map table', 41.5, 31.5, 1, 1, 1, color='#9a7b52', iid='maps')
I('g0', 'chest-silver', 'Deed chest', 41.5, 32.5, 1, 0.5, 1, color='#9aa3ad', iid='deeds')
I('g0', 'chest-small', 'Priest hole: a hidden chest', 29.5, 32, 1, 1, 1, color='#7a4f27', iid='priest')
I('g0', 'mchest-small', 'Small Magic Chest', 50, 22.5, 1, 1, 1, color='#7b68b5', iid='mc1')
I('g0', 'oven', 'Oven', 3.5, 4.5, 2, 2, 2, color='#b0643a', iid='oven')
I('g0', 'cooking-station', 'Cooking Station', 3.5, 7.5, 2, 2, 1.5, color='#c46a2a', iid='cook')
I('g0', 'kitchen', 'Kitchen', 9, 4.5, 2, 2, 1.5, color='#9a6a48', iid='kit')
I('g0', 'table', 'Kitchen table', 6, 6.5, 2.5, 3.5, 1, color='#9a7b52', iid='ktab')
I('g0', 'chest-large', 'Large Chest', 9, 9, 2, 1, 1, color='#7a4f27', iid='kc1')
I('g0', 'stairs', 'Back stairs', 8.5, 12, 2, 4, 4, 180, '#a98a62', 'bst')
I('g0', 'mchest-small', 'Small Magic Chest', 5.5, 14, 1, 1, 1, color='#7b68b5', iid='mc2')
I('g0', 'npc-farmer', 'Head gardener (Farmer)', 66, 13, 2, 2, 2, color='#7c9a3d', iid='garden')
for k, (x, y) in enumerate(((62, 3.5), (64.5, 3.5), (67, 3.5), (62, 15.5), (64.5, 15.5), (67, 15.5))):
    I('g0', 'custom', 'Orange tree', x, y, 1, 1, 3, color='#4f7a26', iid=f'orange{k}')
I('g0', 'seedbed', 'Seedbed', 63.5, 11.5, 2, 2, 0.5, color='#6f8a43', iid='seed1')
for k, (x, y) in enumerate(((19, 35), (52.5, 35), (31, 39), (40.5, 39))):
    I('g0', 'custom', 'Stone urn', x, y, 0.5, 0.5, 1.5, color='#b3b0a9', iid=f'urn{k}')
for k, x in enumerate((29.5, 42)):
    I('g0', 'light', 'Lantern', x, 11, 0.5, 0.5, 1.5, color='#e3b341', iid=f'plan{k}')
I('g1', 'bed2', 'State bed', 23, 16, 3, 3, 1.5, color='#7d5d43', iid='sbed')
I('g1', 'chest-silver', 'Wardrobe', 26, 22.5, 2, 1, 2, color='#9aa3ad', iid='ward')
I('g1', 'bed', 'Guest bed', 22, 26, 2, 3, 1, color='#8c6b4f', iid='gbed')
I('g1', 'bathtub', 'Bathtub', 25.5, 30, 2, 2.5, 1, color='#6f8fa3', iid='tub')
I('g1', 'npc-collector', 'Collector (long gallery)', 34.5, 18.5, 3, 3, 2, color='#8a6aa8', iid='coll')
for k, x in enumerate((30, 33, 39, 41.5)):
    I('g1', 'custom', 'Painting on an easel', x, 16, 1, 0.5, 2, color='#c9a227', iid=f'art{k}')
for k, x in enumerate((3.5, 6, 8.5)):
    I('g1', 'bed', 'Servant\'s bed', x, 3.5, 2, 3, 1, color='#8c6b4f', iid=f'sv{k}')
for k, x in enumerate((25, 31, 37.5, 43.5)):
    I('att', 'mattress', 'Maid\'s bed', x, 18.5, 2, 1, 0.5, color='#8c6b4f', iid=f'mb{k}')
I('att', 'chest-medium', 'Linen chest', 24, 26, 2, 1, 1, color='#7a4f27', iid='linen')
I('att', 'custom', 'Telescope (astronomer\'s room)', 46, 27, 1, 1, 2, color='#c9a227', iid='scope')
I('att', 'table', 'Star charts', 44, 29.5, 2, 1, 1, color='#9a7b52', iid='charts')
I('lanr', 'spire', 'Gilded finial', 35.5, 29.5, 1, 1, 2, color='#c9a227', iid='finial')
for lid in ('cel', 'g0', 'g1'):                                                 # ladders up the two secret shafts
    I(lid, 'ladder', 'Scholar\'s shaft ladder', 41.5, 25.5, 0.5, 0.5, 4, color='#7a5236', iid=f'sl_{lid}')
    I(lid, 'ladder', 'Servants\' shaft ladder', 30, 25.5, 0.5, 0.5, 4, color='#7a5236', iid=f'vl_{lid}')
I('cel', 'ladder', 'Ladder up to the trapdoor', 49.5, 17, 0.5, 0.5, 4, color='#7a5236', iid='trapl')
I('cel', 'custom', 'Founder\'s tomb', 34.5, 26.5, 3, 1.5, 1, color='#b3b0a9', iid='tomb')
I('cel', 'chest-huge', 'Huge Chest (the family silver)', 25, 15.5, 2, 2, 1, color='#7a4f27', iid='silver')
I('cel', 'chest-silver', 'The real treasure', 21.5, 15.5, 2, 1, 1, color='#c9a227', iid='treasure')
I('cel', 'lever', 'Loose brick (opens the false wall)', 26.5, 20.5, 0.5, 0.5, 1, color='#c9a227', iid='lv_brick')
I('cel', 'lever', 'Bottle lever (opens the wine rack)', 50, 15.5, 0.5, 0.5, 1, color='#c9a227', iid='lv_wine')
for k, x in enumerate((29.5, 31.5, 33.5, 35.5, 37.5)):
    I('cel', 'custom', 'Barrel', x, 15.5, 1, 1, 1.5, color='#6b4a32', iid=f'bar{k}')
I('cel', 'table', 'Servants\' hall table', 22, 27, 2, 4, 1, color='#9a7b52', iid='sht')
I('cel', 'chest-large', 'Laundry chest', 45, 27, 2, 1, 1, color='#7a4f27', iid='laund')
I('cel', 'stairs', 'Larder stair up', 3.5, 12, 2, 4, 4, 180, '#a98a62', 'lst')
for k, x in enumerate((3.5, 6, 8.5)):
    I('cel', 'chest-large', 'Larder chest', x, 3.5, 2, 1, 1, color='#7a4f27', iid=f'ld{k}')

Z = P.zone
for (lid, name, x0, y0, x1, y1, col) in (
    ('g0', 'Columned hall', 29, 15, 43, 24, '#b8862b'), ('g0', 'Round saloon (altar)', 31, 25, 41, 35, '#b0596f'),
    ('g0', 'Dining room', 21, 15, 28.5, 24, '#c4501a'), ('g0', 'Drawing room (fireplace door)', 21, 24.5, 28.5, 33, '#8a5cc2'),
    ('g0', 'Stair hall', 43.5, 15, 51, 24, '#5f7d3a'), ('g0', 'Library (bookcase door, panel)', 43.5, 24.5, 51, 33, '#2f7fb3'),
    ('g0', 'Priest hole', 29.5, 31.5, 30.5, 33, '#c2416e'), ('g0', 'Muniment room', 41.5, 31.5, 42.5, 33, '#c2416e'),
    ('g0', 'Cupboard under the stairs (trapdoor)', 45, 15, 51, 20, '#c2416e'),
    ('g0', 'Kitchen', 3, 3, 11, 11, '#b0643a'), ('g0', 'Scullery & back stairs', 3, 11.5, 11, 17, '#9a7344'),
    ('g0', 'Orangery', 61, 3, 69, 17, '#6f8a43'), ('g0', 'Garden terrace', 18.5, 34, 53.5, 39.5, '#8b8478'),
    ('g1', 'State bedroom', 21, 15, 28.5, 24, '#b0596f'), ('g1', 'Guest room & bath', 21, 24.5, 28.5, 33, '#5f7d3a'),
    ('g1', 'Long gallery', 29, 15, 43, 24, '#8a6aa8'), ('g1', 'Saloon gallery', 31, 25, 41, 35, '#b8862b'),
    ('g1', 'Library gallery', 43.5, 24.5, 51, 33, '#2f7fb3'), ('g1', 'Servants\' dormitory', 3, 3, 11, 11, '#9a7344'),
    ('att', 'Maids\' rooms', 23, 17, 49, 22, '#9a7344'), ('att', 'Linen room', 23, 24, 30, 31, '#8b8478'),
    ('att', 'Astronomer\'s room (secret)', 41, 24, 49, 31, '#c2416e'), ('att', 'Whispering gallery (inside the dome)', 31, 25, 41, 35, '#c2416e'),
    ('cel', 'Strong room', 24.5, 15, 28, 21.5, '#c2416e'), ('cel', 'Treasure vault (behind the false wall)', 21, 15, 24, 18, '#c2416e'),
    ('cel', 'Beer cellar', 28.5, 15, 40, 21.5, '#8b8478'), ('cel', 'Wine cellar (rack door)', 40.5, 15, 51, 21.5, '#8a5cc2'),
    ('cel', 'Crypt', 31, 25, 41, 35, '#5f7d3a'), ('cel', 'Servants\' hall', 21, 24.5, 28.5, 33, '#9a7344'),
    ('cel', 'Laundry', 43.5, 24.5, 51, 33, '#2f7fb3'), ('cel', 'Larder', 3, 3, 11, 11, '#b0643a')):
    Z(lid, name, x0, y0, x1, y1, col)

problems = P.check(outdoor_ok=('g0',), ignore_types=('stairs', 'spire', 'ladder'))
print('item problems:', len(problems))
for p_ in problems[:60]: print('  ', p_)

NOTES = """English manor house, drafted by Claude. Uses 0.5 m squares, so every square is one single block. The estate plan ("English manor: the estate") places it in its grounds.

CHARACTER
- A Palladian villa, symmetrical about its north-south axis.
- The ground floor is rusticated Limestone and the upper floor Refined Sandstone ashlar, divided by a projecting string course and crowned by a cornice and a stone balustrade.
- Highly Polished Stone trim: window sills, aprons under the upper windows, and quoins at the corners.
- Six giant columns stand on a stylobate step under a stone pediment.
- Two-storey canted bay windows light the drawing room (west) and the library (east).
- The round saloon pushes a bow out through the garden front. It rises through the house into a windowed drum and a ribbed copper dome with a glazed lantern and a gilded finial.
- Curved quadrant colonnades embrace the forecourt and lead to the pavilions:
  - a brick kitchen with a great hearth and a louvred smoke lantern;
  - a glazed orangery with a glass roof lantern.

GROUND FLOOR (state rooms)
- Columned hall: four columns, checkerboard marble, statues in niches, and the Bard.
- Round saloon: the Flame Altar on a compass-rose floor, double height under the dome.
- Dining room (NW, beside the kitchen quadrant). Drawing room (SW). Library (SE). Stair hall (NE).
- The imperial stair has floating stone treads. The central flight rises to a landing, then two return flights climb to the first floor.

FIRST FLOOR
- Long gallery with the Collector. State bedroom, and a guest room with a bath.
- A gallery runs round the saloon's void, and another round the double-height library, reached by the library ladder.

ATTIC
- Maids' rooms with skylights and a linen room.
- A secret astronomer's room opens onto the whispering gallery inside the dome.

SECRETS
1. Library bookcase door (pull the right book): the scholar's shaft. Its ladder reaches the long gallery (panel), the astronomer's room, and a crawl to a hidden door in the crypt.
2. Jib doors, flush with the walls, in the hall, the drawing room and the guest room: the servants' shaft from the servants' hall in the cellars up to the linen room.
3. The drawing-room fireplace swings open (turn the candlestick) onto a priest hole.
4. A library panel slides back to the muniment room: maps and deeds.
5. A cupboard under the stair landing hides a trapdoor and a ladder down to the wine cellar.
6. The strong room's back wall is false (push the loose brick). The real treasure is in a vault behind it.
7. The astronomer's room has no door, only a panel from the attic corridor and the shaft. A door in the drum wall opens onto the whispering gallery.
8. The wine-rack door (pull the bottle) opens on the tunnel east to the grotto.
9. A hidden door in the crypt opens on the deep tunnel south to the boathouse.

CELLARS (−4 m)
- A spine corridor serves: the strong room and treasure vault, the beer cellar, the wine cellar, the servants' hall and the laundry.
- The round crypt under the saloon holds the founder's tomb round a central pier.
- A brick passage leads to the larder under the kitchen.

DOUBLE-CHECK IN GAME
- What levers and pressure plates can trigger in 1.0, and how doors can be disguised. Here the secret doors are ordinary doors dressed as bookcases, panels and racks.
- Crafting stations are 2 x 2 m placeholders. Furniture sizes are estimates.
"""
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manor-house.json')
print('bytes', P.save(out, NOTES, 'r-claude-manor-house-2'))
for a, b in P.merged: print('  folded:', a, '->', b)
print('palette', len(set(c for g in P.grids.values() for r in g for c in r) - {' '}))
print('levels', [(L['id'], L['elev'], L['height']) for L in P.levels])
