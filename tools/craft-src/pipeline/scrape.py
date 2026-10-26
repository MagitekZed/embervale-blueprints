"""Scrape enshrouded.tools item pages for Eternal spells and their resource trees.

Usage: python -I scrape.py <cache_dir> <out_json>
"""
import html
import json
import os
import re
import sys
import time
import urllib.request

BASE = "https://www.enshrouded.tools/items/"
CACHE = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(CACHE, exist_ok=True)


def fetch(slug):
    path = os.path.join(CACHE, "item-" + slug + ".html")
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return open(path, encoding="utf-8").read()
    import subprocess
    err = None
    for attempt in range(3):
        r = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "-o", path, BASE + slug], capture_output=True)
        if r.returncode == 0 and os.path.exists(path) and os.path.getsize(path) > 1000:
            time.sleep(0.3)
            return open(path, encoding="utf-8").read()
        err = r.stderr
        time.sleep(2)
    raise RuntimeError(f"fetch failed {slug}: {err}")


def text_of(fragment):
    t = re.sub(r"<!--.*?-->", "", fragment, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    t = html.unescape(t)
    return [l.strip() for l in t.split("\n") if l.strip()]


H2 = re.compile(r'<h2 class="[^"]*">([^<]+)</h2>')


def sections(main):
    """Return {title: html_fragment} for each h2 section in main."""
    out = {}
    ms = list(H2.finditer(main))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(main)
        out.setdefault(html.unescape(m.group(1)).strip(), main[m.end():end])
    return out


A_INPUT = re.compile(
    r'<a data-tt="i:([^"]+)"[^>]*>.*?leading-tight"[^>]*>([^<]+)</span>.*?tabular-nums text-text2">x(\d+)</span></a>',
    re.S,
)
G_INPUT = re.compile(
    r'<span class="flex items-center gap-3 px-3 py-2">.*?leading-tight"[^>]*>([^<]+)</span>'
    r'<span class="mt-\[2px\][^"]*"><span class="whitespace-normal">([^<]+)</span></span></span>'
    r'<span class="shrink-0[^"]*">x(\d+)</span></span>',
    re.S,
)
MAKES = re.compile(r'Makes <span><span class="font-bold text-cream">(\d+) x <!-- -->([^<]+)</span>')


def parse_recipes(frag):
    recipes = []
    panels = frag.split('<div class="es-panel">')[1:]
    for p in panels:
        hdr_m = re.search(r'<div class="flex flex-wrap items-center[^"]*border-b[^"]*">(.*?)</div>', p, re.S)
        hdr = hdr_m.group(1) if hdr_m else ""
        crafter_m = re.search(r"<a [^>]*>([^<]+)</a>", hdr)
        crafter = html.unescape(crafter_m.group(1)).strip() if crafter_m else None
        if not crafter:
            ht = text_of(hdr)
            crafter = ht[0] if ht else None
        needs = None
        nm = re.search(r'<span class="text-muted">Needs <!-- -->([^<]+)</span>', hdr)
        if nm:
            needs = html.unescape(nm.group(1)).strip()
        tm = re.search(r'<span class="ml-auto text-muted">([^<]+)</span>', hdr)
        ctime = html.unescape(tm.group(1)).strip() if tm else None
        hdr_text = text_of(hdr)
        # collect inputs in document order
        found = []
        for m in A_INPUT.finditer(p):
            found.append((m.start(), {"item": html.unescape(m.group(2)).strip(), "slug": m.group(1), "qty": int(m.group(3))}))
        for m in G_INPUT.finditer(p):
            found.append((m.start(), {"item": html.unescape(m.group(1)).strip(), "anyOf": [s.strip() for s in html.unescape(m.group(2)).split(",")], "qty": int(m.group(3))}))
        found.sort(key=lambda x: x[0])
        mk = MAKES.search(p)
        recipes.append({
            "crafter": crafter,
            "needs": needs,
            "time": ctime,
            "header_text": hdr_text,
            "inputs": [f for _, f in found],
            "makes": int(mk.group(1)) if mk else 1,
            "makes_item": html.unescape(mk.group(2)).strip() if mk else None,
        })
    return recipes


def parse_item(slug):
    d = fetch(slug)
    b = d.find("<main")
    e = d.find("</main>")
    main = d[b:e]
    lines = text_of(main)
    info = {"slug": slug, "url": BASE + slug}
    # key/value table between 'Category' and 'Description' (or 'About')
    try:
        i = lines.index("Category")
    except ValueError:
        i = None
    if i is not None:
        j = i
        stop = {"Description", "About", "In-game text", "Perks", "How to craft", "Where to get it"}
        kv = {}
        while j + 1 < len(lines) and lines[j] not in stop:
            kv[lines[j]] = lines[j + 1]
            j += 2
        info["kv"] = kv
    secs = sections(main)
    info["section_titles"] = list(secs.keys())
    if "How to craft" in secs:
        info["recipes"] = parse_recipes(secs["How to craft"])
    else:
        info["recipes"] = []
    for key in ("Where to get it", "Where to find it", "Perks", "Description", "Reward from", "Rewarded by", "Sold by", "Found in", "Dropped by"):
        if key in secs:
            info[key] = text_of(secs[key])[:60]
    # perks parse from lines
    if "Perks" in lines:
        k = lines.index("Perks") + 1
        perks = []
        while k + 2 < len(lines) and lines[k + 1] == "+":
            perks.append({"stat": lines[k], "value": lines[k + 2]})
            k += 3
        info["perks"] = perks
    info["title"] = lines[lines.index(info["kv"].get("Category", "")) - 1] if False else None
    # name: breadcrumb last element appears in ld+json
    nm = re.search(r'"position":4,"name":"([^"]+)"', d) or re.search(r'"position":3,"name":"([^"]+)"\}\]', d)
    info["name"] = html.unescape(nm.group(1)) if nm else None
    return info


def main():
    eternal_slugs = [l.strip() for l in open(os.path.join(CACHE, "eternal_slugs.txt"), encoding="utf-8") if l.strip()]
    items = {}
    for s in eternal_slugs:
        items[s] = parse_item(s)
        print("item", s, items[s].get("name"), len(items[s]["recipes"]), file=sys.stderr)
    # resource tree
    resources = {}
    queue = []
    for it in items.values():
        for r in it["recipes"]:
            for inp in r["inputs"]:
                if "slug" in inp:
                    queue.append((inp["slug"], 1))
    seen = set()
    while queue:
        slug, depth = queue.pop(0)
        if slug in seen:
            continue
        seen.add(slug)
        info = parse_item(slug)
        resources[slug] = info
        print("res", depth, slug, info.get("name"), file=sys.stderr)
        if depth < 6:
            for r in info["recipes"]:
                for inp in r["inputs"]:
                    if "slug" in inp and inp["slug"] not in seen:
                        queue.append((inp["slug"], depth + 1))
    json.dump({"items": items, "resources": resources}, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


main()
