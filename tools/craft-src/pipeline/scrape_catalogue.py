"""Scrape enshrouded.tools for one catalogue batch (catalogue_batches.py says which items), the resource tree under
their recipes, and the stations those recipes need, so build_catalogue.py can say where each one becomes makeable.

Usage: python -I scrape_catalogue.py <batch> <cache_dir> <out_json> <building.html> <building-blocks.html>

<building.html> and <building-blocks.html> are the site's /building and /building-blocks pages, saved: the first
lists every building item (with a "New" badge on the ones 1.0 added), the second every block, which is left out.
Item pages are fetched into <cache_dir> by scrape_objects.py's parse_item, and reused from there.

Besides what parse_item reads, each item keeps its badges (comfort type and value, frost resistance) and the text
of what unlocks its recipe ("Unlocks once you reach level 5 or ...").
"""
import html
import json
import os
import re
import subprocess
import sys
import time

BATCH = sys.argv[1]
sys.argv = [sys.argv[0]] + sys.argv[2:]                    # scrape_objects reads <cache_dir> <out_json>
from scrape_objects import CACHE, OUT, parse_item, primary_recipe  # noqa: E402
from catalogue_batches import classify  # noqa: E402

BUILDING, BLOCKS = sys.argv[3], sys.argv[4]
NPC = {"Alchemist", "Collector", "Hunter", "Huntress", "Blacksmith", "Carpenter", "Farmer", "Bard", "Fisher", "Barber",
       "Ancient Researcher", "Lunar New Year Trader"}
HAND = {"By hand", "Manual Crafting", None}
slugify = lambda n: re.sub(r"[^a-z0-9]+", "-", n.lower().replace("'", "")).strip("-")


def building_items():
    """{slug: (name, new in 1.0)} from the /building page."""
    s = open(BUILDING, encoding="utf-8", errors="replace").read()
    out = {}
    for m in re.finditer(r'href="/items/([a-z0-9-]+)"[^>]*>(.*?)</a>', s, re.S):
        txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))).strip()
        if not txt or m.group(1) in out:
            continue
        new = txt.startswith("New ")
        name = re.sub(r" Building$", "", re.sub(r"^New ", "", txt)).strip()
        out[m.group(1)] = (name, new)
    return out


def page_lines(slug):
    t = open(os.path.join(CACHE, "item-" + slug + ".html"), encoding="utf-8", errors="replace").read()
    m = re.sub(r"<!--.*?-->", "", t[t.find("<main"):t.find("</main>")], flags=re.S)
    return [l.strip() for l in html.unescape(re.sub(r"<[^>]+>", "\n", m)).split("\n") if l.strip()]


def extras(slug):
    """The page's badges ({"Comfort - Illumination": 1, "Frost Resistance": 3}) and unlock text."""
    L = page_lines(slug)
    top = L[:L.index("Category")] if "Category" in L else []
    badges = {}
    for i, l in enumerate(top[:-1]):
        if re.match(r"Comfort - |.*Resistance$", l) and re.fullmatch(r"-?\d+", top[i + 1]):
            badges[l] = int(top[i + 1])
    unlock = None
    if "Unlocks once you" in L:
        k = L.index("Unlocks once you")
        words = []
        for w in L[k + 1:k + 40]:
            if w == ".":
                break
            words.append(w)
        unlock = re.sub(r"\s+([,.])", r"\1", " ".join(words)).strip()
    return badges, unlock


def enemy_regions(name):
    """The regions an enemy's page lists ("Regions: Revelwood, Nomad Highlands"), fetched into the cache."""
    slug = slugify(name)
    path = os.path.join(CACHE, "enemy-" + slug + ".html")
    if not (os.path.exists(path) and os.path.getsize(path) > 1000):
        subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "-o", path, "https://www.enshrouded.tools/enemies/" + slug])
        time.sleep(0.6)
    if not os.path.exists(path) or os.path.getsize(path) < 1000:
        return []
    t = open(path, encoding="utf-8", errors="replace").read()
    m = re.sub(r"<!--.*?-->", "", t[t.find("<main"):t.find("</main>")], flags=re.S)
    L = [l.strip() for l in html.unescape(re.sub(r"<[^>]+>", "\n", m)).split("\n") if l.strip()]
    if "Regions" not in L:
        return []
    out = []
    for w in L[L.index("Regions") + 1:L.index("Regions") + 20]:
        if w == ",":
            continue
        if w in ("XP multiplier", "Health per extra player", "Behavior", "Boss", "Faction"):
            break
        out.append(w)
    return out


def drop_regions(info):
    """For a resource only dropped by enemies: {enemy: [regions]} for the first few that drop it."""
    d = info.get("sections", {}).get("Dropped by") or []
    names = [w for w in d[1:] if not re.fullmatch(r"\d+", w)][0::2][:6]   # (a count, then name and faction pairs)
    return {n: enemy_regions(n) for n in names}


def main():
    blocks = set(re.findall(r'href="/items/([a-z0-9-]+)"', open(BLOCKS, encoding="utf-8", errors="replace").read()))
    listed = building_items()
    items = {}
    for slug, (name, new) in sorted(listed.items()):
        if slug in blocks or not classify(BATCH, name):
            continue
        info = parse_item(slug)
        info["listedName"], info["new"] = name, new
        info["badges"], info["unlock"] = extras(slug)
        items[slug] = info
        print("item", slug, info.get("name"), len(info["recipes"]), info["badges"], file=sys.stderr)
    # the resource tree, and every station or requirement a followed recipe names
    resources, seen, queue = {}, set(), []

    def enqueue(r, depth):
        if not r:
            return
        for inp in r["inputs"]:
            if "slug" in inp:
                queue.append((inp["slug"], depth))
            for opt in inp.get("anyOf", []):
                queue.append((slugify(opt), depth))
        for m in [r["crafter"]] + ([n.strip() for n in r["needs"].split(" and ")] if r["needs"] else []):
            if m not in HAND and m not in NPC:
                queue.append((slugify(m), depth))

    for it in items.values():
        for r in it["recipes"]:
            enqueue(r, 1)
    while queue:
        slug, depth = queue.pop(0)
        if slug in seen:
            continue
        seen.add(slug)
        try:
            info = items.get(slug) or parse_item(slug)
        except RuntimeError as e:
            print("missing", slug, e, file=sys.stderr)
            continue
        if not info["recipes"] and (info.get("sections", {}).get("Dropped by")):
            info["dropRegions"] = drop_regions(info)
        resources[slug] = info
        print("res", depth, slug, info.get("name"), info.get("dropRegions") or "", file=sys.stderr)
        if depth < 10:
            enqueue(primary_recipe(info), depth + 1)
    json.dump({"batch": BATCH, "items": items, "resources": resources}, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"{len(items)} items, {len(resources)} resources -> {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
