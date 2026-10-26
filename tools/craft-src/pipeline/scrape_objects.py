"""Scrape enshrouded.tools item pages for chests, crafting stations, base furniture and Sparkworks parts,
plus the resource tree under their recipes and the quests that introduce the stations.

Usage: python -I scrape_objects.py <cache_dir> <out_json>

Pages are fetched with curl into <cache_dir> (item-<slug>.html) and reused from there on later runs.
The parsing follows scrape.py (Eternal spells); that script runs on import, so the helpers are copied here.
"""
import html
import json
import os
import re
import subprocess
import sys
import time

BASE = "https://www.enshrouded.tools/items/"
CACHE = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(CACHE, exist_ok=True)
DELAY = 0.6  # seconds between live fetches

# Item pages to read. Placeholder candidates are fetched generously; build_objects.py picks from them.
SLUGS = {
    "chests": ["tiny-chest", "small-chest", "wooden-chest", "medium-chest", "large-chest", "silver-chest", "huge-chest"],
    "magic": ["small-magic-chest", "medium-magic-chest", "large-magic-chest", "huge-magic-chest", "enormous-magic-chest",
              "quick-stack-station", "large-quick-stack-station"],
    "stations": ["workbench", "forge", "charcoal-kiln", "smelter", "blast-furnace", "smithing-tools",
                 "alchemy-station", "grinding-stones", "mortar", "laboratory",
                 "kiln", "table-saw", "masonry-tools",
                 "tanning-station", "drying-rack", "hand-spindle", "loom", "spinning-wheel", "spinning-machine",
                 "seedbed", "cooking-station", "oven", "kitchen", "sparkworks-workbench", "decoration-workbench"],
    "base": ["flame-altar",
             "crude-wooden-bed", "wooden-bed", "rustic-bed", "camp-bed", "ornate-wooden-bed", "boreal-wood-bed",
             "stone-bed", "palm-wood-bed", "ancient-bed", "kingsize-bed", "large-boreal-wood-bed",
             "crude-mattress", "campfire", "fire-bowl",
             "wooden-bathtub", "bronze-bathtub", "granite-stone-bathtub", "maritime-bathtub",
             "farm-animal-pillow", "big-farm-animal-pillow", "crude-wooden-fence-i", "crude-wooden-gate-i",
             "pinewood-fence-gate-i",
             "water-trough", "goat-feeder", "hophare-feeder", "fae-deer-feeder", "yak-feeder", "bird-feeder",
             "wooden-ladder", "bamboo-ladder", "bamboo-ladder-ii", "bamboo-ladder-iii",
             "torch", "standing-torch", "wall-torch", "wax-torch", "resin-torch", "lantern", "standing-lantern",
             "wall-lantern", "hanging-lantern", "candle", "lamp",
             "crude-wooden-table", "wooden-table", "rustic-table", "polished-wooden-table", "stone-table"],
    "sparkworks": ["lever", "lever-with-indicator", "switch-button", "push-button", "shootable-button", "pressure-plate",
                   "light", "goalpost", "lightning-trap", "spike-trap", "sparkworks-switchbox", "sparkworks-tool",
                   "trapdoor-metal-2m", "trapdoor-metal-4m", "trapdoor-stone-2m", "trapdoor-stone-4m",
                   "trapdoor-wood-2m", "trapdoor-wood-4m", "spawner", "sparkworks-trigger-zone"],
}


# "Any X" recipe slots name their options as plain text, so the crawl can't follow them. These option pages
# are read as extra resources (the cheapest option of a slot that isn't simply gathered). The Almanac is a
# recipe requirement (Oven), read for its note.
EXTRA_RES = ["archaic-essence-i", "almanac-of-plants-and-seedlings"]


# Quests that hand out a station or a station part (the first one; most can also be crafted in 1.0).
QUESTS = ["a-black-cauldron-for-the-alchemist", "a-blast-furnace-for-the-blacksmith", "a-spinning-machine-for-the-hunter",
          "almanac-of-plants-and-seedlings-for-the-farmer", "cooking-equipment-for-the-farmer", "crucible-needed-for-a-smelter",
          "finding-masonry-tools", "in-need-of-a-tanning-station", "loom-for-the-hunter", "scientific-instruments-for-a-laboratory",
          "table-saw-for-the-carpenter", "the-alchemists-mortar", "the-hunters-hand-spindle", "the-blacksmiths-request",
          "the-blacksmith-needs-a-shop", "using-the-spinning-wheel", "contraptions-and-mechanisms",
          "flame-altar-and-base-improvements", "claim-a-spot-for-your-base", "animal-farming"]


def fetch(slug, kind="items"):
    path = os.path.join(CACHE, ("item-" if kind == "items" else "quest-") + slug + ".html")
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return open(path, encoding="utf-8", errors="replace").read()
    err = None
    for attempt in range(3):
        url = BASE + slug if kind == "items" else BASE.replace("/items/", "/quests/") + slug
        r = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "-o", path, url], capture_output=True)
        time.sleep(DELAY)
        if r.returncode == 0 and os.path.exists(path) and os.path.getsize(path) > 1000:
            return open(path, encoding="utf-8", errors="replace").read()
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
    for p in frag.split('<div class="es-panel">')[1:]:
        hdr_m = re.search(r'<div class="flex flex-wrap items-center[^"]*border-b[^"]*">(.*?)</div>', p, re.S)
        hdr = hdr_m.group(1) if hdr_m else ""
        crafter_m = re.search(r"<a [^>]*>([^<]+)</a>", hdr)
        crafter = html.unescape(crafter_m.group(1)).strip() if crafter_m else None
        if not crafter:
            ht = text_of(hdr)
            crafter = ht[0] if ht else None
        nm = re.search(r'<span class="text-muted">Needs <!-- -->([^<]+)</span>', hdr)
        needs = html.unescape(nm.group(1)).strip() if nm else None
        tm = re.search(r'<span class="ml-auto text-muted">([^<]+)</span>', hdr)
        ctime = html.unescape(tm.group(1)).strip() if tm else None
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
            "header_text": text_of(hdr),
            "inputs": [f for _, f in found],
            "makes": int(mk.group(1)) if mk else 1,
            "makes_item": html.unescape(mk.group(2)).strip() if mk else None,
        })
    return recipes


KV_STOP = {"Description", "About", "In-game text", "Perks", "How to craft", "Where to get it", "Where to find it"}


def parse_item(slug):
    d = fetch(slug)
    b, e = d.find("<main"), d.find("</main>")
    main = d[b:e]
    lines = text_of(main)
    info = {"slug": slug, "url": BASE + slug}
    kv = {}
    if "Category" in lines:
        j = lines.index("Category")
        while j + 1 < len(lines) and lines[j] not in KV_STOP:
            kv[lines[j]] = lines[j + 1]
            j += 2
    info["kv"] = kv
    secs = sections(main)
    info["section_titles"] = list(secs.keys())
    info["recipes"] = parse_recipes(secs["How to craft"]) if "How to craft" in secs else []
    for key, frag in secs.items():
        if key != "How to craft":
            info.setdefault("sections", {})[key] = text_of(frag)[:80]
    nm = re.search(r'"position":4,"name":"((?:[^"\\]|\\.)+)"', d) or re.search(r'"position":3,"name":"((?:[^"\\]|\\.)+)"\}\]', d)
    info["name"] = html.unescape(nm.group(1).replace('\\"', '"')) if nm else None   # (names can hold escaped quotes)
    return info


def parse_quest(slug):
    d = fetch(slug, "quests")
    main = d[d.find("<main"):d.find("</main>")]
    lines = text_of(main)
    q = {"slug": slug, "url": BASE.replace("/items/", "/quests/") + slug}
    nm = re.search(r"<h1[^>]*>([^<]+)</h1>", main)
    q["name"] = html.unescape(nm.group(1)).strip() if nm else None
    if q["name"] in lines:
        k = lines.index(q["name"], lines.index(q["name"]) + 1) if lines.count(q["name"]) > 1 else lines.index(q["name"])
        out = []
        for x in lines[k + 1:k + 12]:
            if x == "Steps":
                break
            out.append(x)
        q["summary"] = re.sub(r"\s+([,.])", r"\1", " ".join(out))
    for key, field in (("Given by", "givenBy"), ("Survivor", "survivor"), ("XP", "xp")):
        if key in lines:
            q[field] = lines[lines.index(key) + 1]
    rw = main.split(">Rewards</h2>")
    q["rewards"] = re.findall(r'data-tt="i:([^"]+)"', rw[1]) if len(rw) > 1 else []
    return q


def primary_recipe(info):
    """The recipe build_objects.py follows: the one made where the 'Where to get it' line says, else the first.
    Only that one is crawled; following every alternative pulls in hundreds of unrelated pages (food, fish)."""
    src = (info.get("sections", {}).get("Where to get it") or [None])[0]
    recs = info["recipes"]
    return next((r for r in recs if r["crafter"] == src), recs[0] if recs else None)


def main():
    items = {}
    for group, slugs in SLUGS.items():
        for s in slugs:
            info = parse_item(s)
            info["group"] = group
            items[s] = info
            print("item", group, s, info.get("name"), len(info["recipes"]), file=sys.stderr)
    resources = {}
    queue = [(inp["slug"], 1) for it in items.values() for r in it["recipes"] for inp in r["inputs"] if "slug" in inp]
    queue += [(s, 1) for s in EXTRA_RES]
    seen = set()
    while queue:
        slug, depth = queue.pop(0)
        if slug in seen:
            continue
        seen.add(slug)
        info = items.get(slug) or parse_item(slug)
        resources[slug] = info
        print("res", depth, slug, info.get("name"), file=sys.stderr)
        r = primary_recipe(info)
        if r and depth < 8:
            for inp in r["inputs"]:
                if "slug" in inp and inp["slug"] not in seen:
                    queue.append((inp["slug"], depth + 1))
    quests = {}
    for s in QUESTS:
        quests[s] = parse_quest(s)
        print("quest", s, quests[s].get("name"), quests[s]["rewards"], file=sys.stderr)
    json.dump({"items": items, "resources": resources, "quests": quests}, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
