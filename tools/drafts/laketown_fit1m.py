"""Where things land at 1 m: builds the site plan as `laketown_site.py --try` does (pending blueprints too, nothing
saved) and shows, for a region in layout metres, each of one blueprint's items in its 1 m squares (after the
stamp's rounding and nudging) and the 1 m notes there. For clearing 1 m notes.
Usage: python laketown_fit1m.py "<DETAILS label>" x0 y0 x1 y1 [site level id, e.g. cp-up6 or mid]
  e.g. python laketown_fit1m.py "Bathhouse and arena" 47 88 62 98 cp-up6"""
import os, re, sys, io, contextlib
os.chdir(os.path.dirname(os.path.abspath(__file__)))
label, X0, Y0, X1, Y1 = sys.argv[1], *map(float, sys.argv[2:6])
lev = sys.argv[6] if len(sys.argv) > 6 else None
src = open('laketown_site.py', encoding='utf-8').read()
src = src.replace("TRY = '--try' in sys.argv", "TRY = True")
cut = src.index("NOTES = \"\"\"Laketown: the site plan")
src = src[:cut]
ns = {'__name__': 'fit1m', '__file__': os.path.abspath('laketown_site.py')}
sys.argv = ['laketown_site.py', '--try']
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    exec(compile(src, 'laketown_site.py', 'exec'), ns)
P = ns['P']
D = next(d for d in ns['DETAILS'] if d['label'] == label)
tag = D['tag'] + '-'
print('items at 1 m:')
for it in P.items:
    if not it['id'].startswith(tag):
        continue
    w, d = (it['d'], it['w']) if it['rot'] in (90, 270) else (it['w'], it['d'])
    if X0 <= it['x'] < X1 and Y0 <= it['y'] < Y1 and (lev is None or it['level'] == lev):
        print(f"  {it['level']:10s} {it['label'][:44]:44s} x {it['x']}..{it['x'] + w - 1}  y {it['y']}..{it['y'] + d - 1}  z {it.get('z', 0)} h {it['h']} {it.get('mount') or ''}")
print('notes:')
for m in ns['inside']:
    pts = [(float(a), float(b)) for a, b in re.findall(r'at (-?[\d.]+),(-?[\d.]+)', m)]
    if any(X0 <= x < X1 and Y0 <= y < Y1 for x, y in pts):
        print('  ', m)
