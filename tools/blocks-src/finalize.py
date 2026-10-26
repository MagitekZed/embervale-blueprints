"""Pick the final swatch colour per block (lit-face tone with a gentle lightness lift) and write a compact contact grid."""
import json, os, sys, colorsys
root = sys.argv[1]
items = json.load(open(os.path.join(root, 'catalogue_colours.json'), encoding='utf-8'))
def lift(hexc, amt=0.18):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = l + (1 - l) * amt
    r, g, b = colorsys.hls_to_rgb(h, l, min(1.0, s * 1.08))
    return '#%02x%02x%02x' % tuple(int(round(v * 255)) for v in (r, g, b))
for it in items:
    it['color'] = lift(it['tone'])
json.dump(items, open(os.path.join(root, 'catalogue_colours.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
cells = ''.join(f"<div style='display:flex;gap:4px;align-items:center;width:190px'><img src='wiki_dl/icons/{os.path.basename(i['icon'])}' width=40>"
                f"<span style='width:40px;height:40px;background:{i['color']};display:inline-block'></span><span style='font-size:10px'>{i['name']}</span></div>" for i in items)
open(os.path.join(root, 'grid.html'), 'w', encoding='utf-8').write(
    f"<!doctype html><meta charset=utf-8><body style='margin:4px;font-family:sans-serif;background:#cfcfcf'><div style='display:flex;flex-wrap:wrap;gap:4px'>{cells}</div>")
print('ok', len(items))
