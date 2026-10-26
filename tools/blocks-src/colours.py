"""Decode the wiki block icons (pure Python PNG reader) and compute a representative colour for each.

Usage: python -I colours.py <scratchpad dir>
Writes catalogue_colours.json and contact.html (icon next to swatches) in the scratchpad dir.
"""
import json, os, random, struct, sys, zlib, colorsys

def read_png(path):
    data = open(path, 'rb').read()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('not a png')
    pos, idat, plte, trns = 8, b'', None, None
    while pos < len(data):
        n, typ = struct.unpack('>I4s', data[pos:pos + 8]); body = data[pos + 8:pos + 8 + n]; pos += 12 + n
        if typ == b'IHDR':
            w, h, depth, ctype, _, _, inter = struct.unpack('>IIBBBBB', body)
        elif typ == b'PLTE': plte = body
        elif typ == b'tRNS': trns = body
        elif typ == b'IDAT': idat += body
        elif typ == b'IEND': break
    if inter:
        raise ValueError('interlaced')
    chans = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    bits = chans * depth
    bpp = max(1, bits // 8)
    stride = (w * bits + 7) // 8
    raw = zlib.decompress(idat)
    rows, prev = [], bytearray(stride)
    i = 0
    for _ in range(h):
        f = raw[i]; line = bytearray(raw[i + 1:i + 1 + stride]); i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = prev[x]; c = prev[x - bpp] if x >= bpp else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + b) & 255
            elif f == 3: line[x] = (line[x] + ((a + b) >> 1)) & 255
            elif f == 4:
                p = a + b - c; pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(line); prev = line
    px = []
    for line in rows:
        if depth == 8:
            for x in range(w):
                o = x * chans
                if ctype == 6: px.append(tuple(line[o:o + 4]))
                elif ctype == 2: px.append((line[o], line[o + 1], line[o + 2], 255))
                elif ctype == 0: px.append((line[o],) * 3 + (255,))
                elif ctype == 4: px.append((line[o],) * 3 + (line[o + 1],))
                elif ctype == 3:
                    k = line[o]; r, g, b = plte[k * 3:k * 3 + 3]
                    px.append((r, g, b, trns[k] if trns and k < len(trns) else 255))
        elif ctype == 3:
            per = 8 // depth
            for x in range(w):
                byte = line[x // per]; shift = 8 - depth * (x % per + 1)
                k = (byte >> shift) & ((1 << depth) - 1); r, g, b = plte[k * 3:k * 3 + 3]
                px.append((r, g, b, trns[k] if trns and k < len(trns) else 255))
        else:
            raise ValueError(f'unsupported depth {depth} ctype {ctype}')
    return w, h, px

def kmeans(points, k, seed=1, iters=12):
    rnd = random.Random(seed)
    cents = rnd.sample(points, k) if len(points) >= k else points[:]
    for _ in range(iters):
        groups = [[] for _ in cents]
        for p in points:
            j = min(range(len(cents)), key=lambda c: sum((p[t] - cents[c][t]) ** 2 for t in range(3)))
            groups[j].append(p)
        cents = [tuple(sum(p[t] for p in g) / len(g) for t in range(3)) if g else cents[j] for j, g in enumerate(groups)]
    return sorted(((len(g), c) for g, c in zip(groups, cents)), reverse=True)

hexc = lambda c: '#%02x%02x%02x' % tuple(max(0, min(255, int(round(v)))) for v in c)


def tone_of(px):
    """The lit-face tone of an icon's opaque pixels (what finalize.py lifts into the swatch), or None."""
    opaque = [p[:3] for p in px if p[3] >= 200]
    if len(opaque) < 30:
        return None
    lum = lambda p: 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]
    srt = sorted(opaque, key=lum)
    lit = srt[int(len(srt) * 0.55):int(len(srt) * 0.92)]
    return hexc(tuple(sum(p[t] for p in lit) / len(lit) for t in range(3)))


def main():
    root = sys.argv[1]
    items = json.load(open(os.path.join(root, 'catalogue_raw.json'), encoding='utf-8'))
    out, failures = [], []
    for it in items:
        f = os.path.join(root, 'wiki_dl', 'icons', os.path.basename(it['icon']))
        try:
            w, h, px = read_png(f)
        except Exception as e:
            failures.append((it['name'], str(e))); continue
        opaque = [p[:3] for p in px if p[3] >= 200]
        if len(opaque) < 30:
            failures.append((it['name'], 'mostly transparent')); continue
        # trim the darkest and brightest 6% (outlines, specular highlights) before averaging
        lum = lambda p: 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]
        srt = sorted(opaque, key=lum); cut = len(srt) // 16
        core = srt[cut:len(srt) - cut]
        avg = tuple(sum(p[t] for p in core) / len(core) for t in range(3))
        lit = srt[int(len(srt) * 0.55):int(len(srt) * 0.92)]           # the lit faces, minus highlights
        # top face: the upper part of the cube, between its top tip and the front edge
        ys = [i // w for i, p in enumerate(px) if p[3] >= 200]
        y0, y1 = min(ys), max(ys)
        topband = [p[:3] for i, p in enumerate(px) if p[3] >= 200 and y0 + (y1 - y0) * 0.08 <= i // w <= y0 + (y1 - y0) * 0.38]
        tb = sorted(topband, key=lum); cut2 = len(tb) // 10
        tb = tb[cut2:len(tb) - cut2] or topband
        top = tuple(sum(p[t] for p in tb) / len(tb) for t in range(3))
        tone = tuple(sum(p[t] for p in lit) / len(lit) for t in range(3))
        sample = random.Random(7).sample(core, min(1500, len(core)))
        clusters = kmeans(sample, 3)
        dom = clusters[0][1]
        share = clusters[0][0] / len(sample)
        out.append({**it, 'top': hexc(top), 'tone': hexc(tone), 'avg': hexc(avg), 'dominant': hexc(dom), 'dom_share': round(share, 2),
                    'clusters': [(round(n / len(sample), 2), hexc(c)) for n, c in clusters]})

    json.dump(out, open(os.path.join(root, 'catalogue_colours.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    rows = ''.join(f"<tr><td><img src='wiki_dl/icons/{os.path.basename(o['icon'])}' width=56></td><td>{o['name']}<br><small>{o['group']}</small></td>"
                   f"<td style='background:{o['top']};width:60px'></td><td style='background:{o['tone']};width:60px'></td><td style='background:{o['avg']};width:60px'></td><td style='background:{o['dominant']};width:60px'></td>"
                   f"<td><small>{' '.join(f'{s}:{c}' for s, c in o['clusters'])}</small></td></tr>" for o in out)
    open(os.path.join(root, 'contact.html'), 'w', encoding='utf-8').write(
        f"<!doctype html><meta charset=utf-8><body style='font:12px sans-serif;background:#d8d8d8'><table cellspacing=2>"
        f"<tr><th></th><th>name</th><th>top face</th><th>lit tone</th><th>avg</th><th>dominant</th><th>clusters</th></tr>{rows}</table>")
    print('coloured', len(out), 'failed', len(failures))
    for f in failures: print('  ', f)


if __name__ == '__main__':
    main()
