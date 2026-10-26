"""Superseded (2026-10-20) by scrape_catalogue.py and build_catalogue.py (batch "structural"), which cover every structural piece.
Kept for reference; its output, doors-windows.json, is gone.

Build doors-windows.json: the doors and windows you can make from Springlands materials alone, from
scraped enshrouded.tools data.

Usage: python -I build_openings.py <raw_openings.json> <tools-1-0.txt> <out.json>

<raw_openings.json> comes from scrape_openings.py; <tools-1-0.txt> is the text of enshrouded.tools/1-0 (the
site's diff of the last Early Access build against 1.0), for what's new or renamed in 1.0.

"Springlands only" means every raw resource down the recipe tree (following each part's main recipe) can be
had in the Springlands, and every station on the way can be built there: the Workbench, and the stations and
crafters of the survivors rescued in the Springlands. The Table Saw is out: it needs Circular Sawblades, from
the Fawnsong Frontier camp in the Revelwood (or Iron Bars), so anything with Wood Planks is out too.
"""
import json
import re
import sys

RAW, CHANGELOG, OUT = sys.argv[1:4]
raw = json.load(open(RAW, encoding="utf-8"))
items_raw, res_raw = raw["items"], raw["resources"]
by_slug = dict(res_raw)
by_slug.update(items_raw)
SITE = "https://www.enshrouded.tools"

# Raw resources found in the Springlands (each page's "Where to get it" or About line says so, or they turn up
# everywhere: trees, bushes, small stones, ruins, Scavenger drops).
SPRING_RAW = {"Wood Logs", "Plant Fiber", "Twigs", "Resin", "Stone", "Flintstone", "Springlands Dirt", "Rubble",
              "Metal Scraps", "Animal Fur", "Bones", "Torn Cloth"}
# Survivors rescued in the Springlands (enshrouded.tools/regions/springlands): the Alchemist, Blacksmith,
# Carpenter, Farmer and Hunter. Their stations and the basic ones built from Springlands materials.
SPRING_MAKERS = {"Workbench", "By hand", "Manual Crafting", "Carpenter", "Blacksmith", "Alchemist", "Farmer", "Hunter",
                 "Collector", "Forge", "Charcoal Kiln", "Grinding Stones", "Drying Rack", "Seedbed", "Decoration Workbench"}
NPC = {"Alchemist", "Collector", "Hunter", "Blacksmith", "Carpenter", "Farmer", "Bard", "Fisher", "Barber"}
GATHERED_FIRST = {"Twigs", "Animal Fur"}            # gathered, though a station can also make them
# Sizes the user measured in game (2026-10-15), in blocks: height, width. Nothing publishes them.
MEASURED = {"Crude Wooden Door": (5, 4), "Wooden Door": (5, 4), "Round Wooden Door": (6, 6),
            "Round Wooden Door Frame": (6, 6), "Wooden Double Door": (7, 8),
            "Wooden Window Frame": (3, 2), "Round Wooden Window Frame": (2, 2), "Large Round Wooden Window Frame": (6, 6)}

CL = open(CHANGELOG, encoding="utf-8").read().split("\n")
_ni = [i for i, l in enumerate(CL) if l == "New items"][-1]
_nq = next(i for i in range(_ni, len(CL)) if CL[i] == "New quests, lore and places")
NEW_NAMES = {l for l in CL[_ni:_nq] if not re.search(r"\(\d+\)$", l)}
RENAMED = {}
for i, l in enumerate(CL[:-1]):
    m = re.match(r"Renamed from (.+)$", CL[i + 1])
    if m:
        RENAMED[l] = m.group(1)


def primary(info):
    """The recipe followed: the one made where 'Where to get it' says, else the first (none for things
    that are gathered first)."""
    if info.get("name") in GATHERED_FIRST:
        return None
    src = (info.get("sections", {}).get("Where to get it") or [None])[0]
    src = {"Manual Crafting": "By hand", "Huntress": "Hunter"}.get(src, src)
    recs = info["recipes"]
    return next((r for r in recs if r["crafter"] == src), recs[0] if recs else None)


def split(r):
    c = r["crafter"]
    if c in NPC:
        return {"station": r["needs"], "crafter": c, "requires": []}
    if c in ("By hand", "Manual Crafting"):
        return {"station": None, "crafter": None, "requires": [r["needs"]] if r["needs"] else []}
    return {"station": c, "crafter": None, "requires": [r["needs"]] if r["needs"] else []}


def inputs(r):
    return [dict({"item": i["item"], "qty": i["qty"]}, **({"anyOf": i["anyOf"]} if "anyOf" in i else {})) for i in r["inputs"]]


def springlands(slug, why, seen=()):
    """True if everything under this item can be had in the Springlands; reasons it can't go in `why`."""
    info = by_slug.get(slug)
    if info is None:
        why.add(slug); return False
    r = primary(info)
    if r is None:
        ok = info["name"] in SPRING_RAW
        if not ok:
            why.add(info["name"])
        return ok
    ok = True
    for m in (r["crafter"], r["needs"]):
        if m and m not in SPRING_MAKERS:
            why.add(m); ok = False
    for i in r["inputs"]:
        if "anyOf" in i:
            if not SPRING_RAW & set(i["anyOf"]):
                why.add(i["item"]); ok = False
        elif i["slug"] not in seen:
            ok = springlands(i["slug"], why, seen + (slug,)) and ok
    return ok


def about(info):
    a = info.get("sections", {}).get("About")
    return re.sub(r"\s+([,.])", r"\1", " ".join(a)) if a else None


items, left_out = [], []
for slug, info in items_raw.items():
    r = primary(info)
    name = info["name"]
    if not r:
        left_out.append(f"{name} (no recipe: found or bought, not crafted)")
        continue
    why = set()
    if not springlands(slug, why):
        left_out.append(f"{name} (needs {', '.join(sorted(why))})")
        continue
    kind = "window" if "window" in name.lower() else "door"
    it = {"name": name, "category": "Windows" if kind == "window" else "Doors", "rarity": info["kv"].get("Rarity")}
    it.update(split(r))
    it.update({"makes": r["makes"], "craftTime": r["time"], "inputs": inputs(r), "opening": kind,
               "confidence": "likely-1.0", "newIn1_0": name in NEW_NAMES})
    if name in RENAMED:
        it["renamedFrom"] = RENAMED[name]
    notes = []
    if "Secret" in name:
        notes.append("A hidden door that looks like a wall of its blocks.")
    if name.endswith("Frame") and "Door" in name:
        notes.append("A door frame with no door in it.")
    if name in MEASURED:
        hb, wb = MEASURED[name]
        it["size"] = {"h": hb, "w": wb}
        notes.append(f"{hb} blocks tall and {wb} wide (measured in game, 2026-10-15).")
    else:
        notes.append("Its size in blocks isn't published: measure it in game.")
    it["note"] = " ".join(notes)
    it["sources"] = [SITE + "/items/" + slug]
    items.append(it)

# resources: every part under the kept items, as the other files do it
resources, seen, kept = {}, set(), {it["name"] for it in items}
queue = [i for slug, info in items_raw.items() if info["name"] in kept for i in primary(info)["inputs"]]
while queue:
    inp = queue.pop(0)
    if "anyOf" in inp:
        continue
    if inp["slug"] in seen:
        continue
    seen.add(inp["slug"])
    info = by_slug.get(inp["slug"])
    if info is None:
        resources[inp["item"]] = {"kind": "unknown", "source": None, "recipe": None}
        continue
    r = primary(info)
    src = (info.get("sections", {}).get("Where to get it") or [None])[0]
    e = {}
    if r:
        sr = split(r)
        e = {"kind": "crafted", "source": src or r["crafter"],
             "recipe": dict(sr, makes=r["makes"], time=r["time"], inputs=inputs(r))}
        queue.extend(r["inputs"])
    else:
        e = {"kind": "gathered", "source": src, "recipe": None}
        if not src and about(info):
            e["note"] = about(info)
    e["sources"] = [SITE + "/items/" + inp["slug"]]
    resources[info["name"]] = e

data = {
    "fetched": "2026-10-15",
    "notes": (f"{len(items)} doors and windows you can make from Springlands materials alone "
              f"({sum(it['category'] == 'Doors' for it in items)} doors, {sum(it['category'] == 'Windows' for it in items)} windows). "
              "Source: enshrouded.tools item pages, read from the 1.0 game files (Steam build 25936191); every recipe is likely-1.0 "
              "(datamined, not checked in game). 'Springlands only' follows each part's main recipe down to raw resources and "
              "stations: Springlands resources, the Workbench, and the five survivors rescued there (the Carpenter is in the Low "
              "Meadows) with their stations. The Table Saw is out (its Circular Sawblades come from the Revelwood), so anything "
              "with Wood Planks is out. Sizes in blocks aren't published anywhere: `size` (blocks, h and w) is on the ones "
              "measured in game, and the rest note to measure them."),
    "leftOut": sorted(left_out),
    "items": sorted(items, key=lambda it: (it["category"], it["name"])),
    "resources": resources,
}
json.dump(data, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"{len(items)} kept, {len(left_out)} left out, {len(resources)} resources -> {OUT}", file=sys.stderr)
