"""Superseded (2026-10-20) by the catalogue batches (scrape_catalogue.py, build_catalogue.py), which cover every
decoration in 1.0; its output, decorations.json, is gone. Kept for reference.

Scrape the "Building" recipes of the crafters you can have in the Springlands from enshrouded.tools crafting
pages (furniture, lights, decorations), plus the resource tree under them. build_decor.py keeps the ones made
from Springlands materials.

Usage: python -I scrape_decor.py <cache_dir> <out_json>

Crafting pages are fetched into <cache_dir> (crafting-<crafter>.html); resource pages use scrape_objects.py's
parse_item (imported; it reads the same two arguments).
"""
import html
import json
import os
import re
import subprocess
import sys
import time

from scrape_objects import CACHE, OUT, parse_item, primary_recipe

CRAFTERS = ["workbench", "carpenter", "decoration-workbench", "hunter", "bard", "collector", "farmer",
            "alchemist", "blacksmith"]
ROW = '<div class="flex flex-col gap-2 border-b border-line px-3 py-3 md:flex-row'
IN_ITEM = re.compile(r'<a data-tt="i:([^"]+)"[^>]*>([^<]+)</a><span class="tabular-nums text-gold">x<!-- -->(\d+)</span>')
IN_ANY = re.compile(r'<span class="text-muted" title="([^"]+)">([^<]+)</span><span class="tabular-nums text-gold">x<!-- -->(\d+)</span>')


def fetch_page(crafter):
    path = os.path.join(CACHE, "crafting-" + crafter + ".html")
    if not (os.path.exists(path) and os.path.getsize(path) > 1000):
        subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "-o", path, "https://www.enshrouded.tools/crafting/" + crafter])
        time.sleep(0.6)
    return open(path, encoding="utf-8", errors="replace").read()


def building_rows(page):
    """The rows of the page's Building section: product slug, name, how many a craft makes, time and
    needs, and the inputs."""
    hs = [(m.start(), html.unescape(m.group(1)).strip()) for m in re.finditer(r'<h2[^>]*>(.*?)</h2>', page)]
    start = next((p for p, t in hs if t == "Building"), None)
    if start is None:
        return []
    end = next((p for p, t in hs if p > start), len(page))
    out = []
    for row in page[start:end].split(ROW)[1:]:
        m = re.search(r'<a data-tt="i:([^"]+)" class="es-rowhover[^"]*"[^>]*>.*?leading-tight"[^>]*>([^<]+)</span>'
                      r'<span class="mt-\[2px\][^"]*">([^<]*)</span>', row, re.S)
        if not m:
            continue
        slug, name, sub = m.group(1), html.unescape(m.group(2)).strip(), html.unescape(m.group(3)).strip()
        mk = re.match(r"(.*) x(\d+)$", name)
        makes = 1
        if mk:
            name, makes = mk.group(1), int(mk.group(2))
        needs = None
        nm = re.search(r"needs (.+)$", sub)
        if nm:
            needs = nm.group(1)
        inputs = []
        body = row[m.end():]
        found = [(x.start(), {"item": html.unescape(x.group(2)).strip(), "slug": x.group(1), "qty": int(x.group(3))}) for x in IN_ITEM.finditer(body)]
        found += [(x.start(), {"item": html.unescape(x.group(2)).strip(), "anyOf": [s.strip() for s in html.unescape(x.group(1)).split(",")],
                               "qty": int(x.group(3))}) for x in IN_ANY.finditer(body)]
        inputs = [f for _, f in sorted(found, key=lambda f: f[0])]
        out.append({"slug": slug, "name": name, "makes": makes, "time": sub.split(",")[0].strip(), "needs": needs, "inputs": inputs})
    return out


def main():
    items = {}
    for c in CRAFTERS:
        rows = building_rows(fetch_page(c))
        print("crafter", c, len(rows), file=sys.stderr)
        for r in rows:
            r["crafter"] = c
            items.setdefault(r["slug"] + "@" + c, r)
    resources, seen = {}, set()
    queue = [(i["slug"], 1) for r in items.values() for i in r["inputs"] if "slug" in i]
    while queue:
        slug, depth = queue.pop(0)
        if slug in seen:
            continue
        seen.add(slug)
        try:
            info = parse_item(slug)
        except Exception as ex:                                  # a page that won't load: note it and go on
            print("fail", slug, ex, file=sys.stderr)
            continue
        resources[slug] = info
        print("res", depth, slug, info.get("name"), file=sys.stderr)
        r = primary_recipe(info)
        if r and depth < 8:
            queue += [(i["slug"], depth + 1) for i in r["inputs"] if "slug" in i and i["slug"] not in seen]
    json.dump({"items": items, "resources": resources}, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
