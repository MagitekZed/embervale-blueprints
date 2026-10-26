"""Scrape enshrouded.tools item pages for building materials (blocks, roofs, roads,
soils, terrain) and the resource trees behind their recipes.

Usage:
  python -I scrape_materials.py index <cache_dir>
      Fetch the sitemap and the index pages (building-blocks, terraforming,
      materials, building) into the cache.
  python -I scrape_materials.py items <cache_dir> <slugs.txt> <out_raw.json>
      Fetch every item page listed in slugs.txt (one slug per line, '#' comments
      allowed), then follow recipe inputs down to raw resources, and write the
      parsed pages to out_raw.json.
  python -I scrape_materials.py text <cache_dir> <out.txt>
      Write the text of the cached enshrouded.tools/1-0 page, one line per text
      node (the <tools-1-0.txt> input of build_materials.py).

Full run (cache and outputs in the session scratchpad):
  python -I scrape_materials.py index <cache>
  python -I scrape_materials.py items <cache> materials_slugs.txt <raw.json>
  python -I scrape_materials.py text <cache> <tools-1-0.txt>
  python -I build_materials.py <raw.json> <cache> ../../blocks-src/recipes.json <tools-1-0.txt> ../building-materials.json

Pages are cached as <cache_dir>/item-<slug>.html (items) or page-<name>.html
(index pages); a cached page is never fetched again. Requests are spaced out.
The cached HTML is untrusted data: it is only parsed with regexes here.
Parsing mirrors scrape.py (the Eternal spells run) so both outputs line up.
"""
import html
import json
import os
import re
import subprocess
import sys
import time

SITE = "https://www.enshrouded.tools"
BASE = SITE + "/items/"
DELAY = 0.8  # seconds between live requests


def _curl(url, path):
    err = None
    for attempt in range(3):
        r = subprocess.run(["curl", "-sL", "--max-time", "60", "-A", "Mozilla/5.0", "-o", path, url],
                           capture_output=True)
        if r.returncode == 0 and os.path.exists(path) and os.path.getsize(path) > 1000:
            time.sleep(DELAY)
            return
        err = r.stderr
        time.sleep(3)
    raise RuntimeError(f"fetch failed {url}: {err}")


def fetch_url(cache, url, name):
    path = os.path.join(cache, name)
    if not (os.path.exists(path) and os.path.getsize(path) > 1000):
        _curl(url, path)
    return open(path, encoding="utf-8").read()


def fetch(cache, slug):
    return fetch_url(cache, BASE + slug, "item-" + slug + ".html")


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
        found = []
        for m in A_INPUT.finditer(p):
            found.append((m.start(), {"item": html.unescape(m.group(2)).strip(), "slug": m.group(1), "qty": int(m.group(3))}))
        for m in G_INPUT.finditer(p):
            found.append((m.start(), {"item": html.unescape(m.group(1)).strip(),
                                      "anyOf": [s.strip() for s in html.unescape(m.group(2)).split(",")],
                                      "qty": int(m.group(3))}))
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
            "panel_text": text_of(p)[:80],
        })
    return recipes


def parse_item(cache, slug):
    d = fetch(cache, slug)
    b = d.find("<main")
    e = d.find("</main>")
    main = d[b:e]
    lines = text_of(main)
    info = {"slug": slug, "url": BASE + slug}
    kv = {}
    if "Category" in lines:
        j = lines.index("Category")
        stop = {"Description", "About", "In-game text", "Perks", "How to craft", "Where to get it", "Used in"}
        while j + 1 < len(lines) and lines[j] not in stop and len(kv) < 20:
            kv[lines[j]] = lines[j + 1]
            j += 2
    info["kv"] = kv
    secs = sections(main)
    info["section_titles"] = list(secs.keys())
    info["recipes"] = parse_recipes(secs["How to craft"]) if "How to craft" in secs else []
    for key in ("Where to get it", "Where to find it", "Description", "About", "In-game text",
                "Reward from", "Rewarded by", "Sold by", "Found in", "Dropped by", "Obtained from"):
        if key in secs:
            info[key] = text_of(secs[key])[:60]
    info["head_lines"] = lines[:60]
    nm = re.search(r'"position":4,"name":"([^"]+)"', d) or re.search(r'"position":3,"name":"([^"]+)"\}\]', d)
    info["name"] = html.unescape(nm.group(1)) if nm else None
    return info


def primary_recipe(info):
    """The recipe matching the page's 'Where to get it' line, else the first one."""
    recipes = info["recipes"]
    if not recipes:
        return None
    get = info.get("Where to get it") or []
    for r in recipes:
        if r["crafter"] in get[:3]:
            return r
    return recipes[0]


INDEX_PAGES = ["building-blocks", "terraforming", "materials", "building", "1-0"]


def cmd_index(cache):
    os.makedirs(cache, exist_ok=True)
    fetch_url(cache, SITE + "/sitemap.xml", "sitemap.xml")
    for p in INDEX_PAGES:
        fetch_url(cache, SITE + "/" + p, "page-" + p + ".html")
        print("page", p, file=sys.stderr)


def cmd_items(cache, slugs_file, out):
    os.makedirs(cache, exist_ok=True)
    slugs = []
    for l in open(slugs_file, encoding="utf-8"):
        l = l.split("#", 1)[0].strip()
        if l and l not in slugs:
            slugs.append(l)
    items = {}
    for s in slugs:
        items[s] = parse_item(cache, s)
        print("item", s, items[s].get("name"), len(items[s]["recipes"]), file=sys.stderr)
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
        info = parse_item(cache, slug)
        resources[slug] = info
        print("res", depth, slug, info.get("name"), file=sys.stderr)
        # Follow only the resource's primary recipe (the one its "Where to get it"
        # line names, else the first): alternatives such as burning food for
        # Charcoal would pull in hundreds of unrelated pages.
        r = primary_recipe(info)
        if r and depth < 8:
            for inp in r["inputs"]:
                if "slug" in inp and inp["slug"] not in seen:
                    queue.append((inp["slug"], depth + 1))
    json.dump({"items": items, "resources": resources}, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    if sys.argv[1] == "index":
        cmd_index(sys.argv[2])
    elif sys.argv[1] == "text":
        page = open(os.path.join(sys.argv[2], "page-1-0.html"), encoding="utf-8").read()
        b, e = page.find("<main"), page.find("</main>")
        open(sys.argv[3], "w", encoding="utf-8").write(chr(10).join(text_of(page[b:e])))
    elif sys.argv[1] == "items":
        cmd_items(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        raise SystemExit(__doc__)
