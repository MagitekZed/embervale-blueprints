"""Superseded (2026-10-20) by the catalogue batches (scrape_catalogue.py, build_catalogue.py), which cover every
decoration in 1.0; its output, decorations.json, is gone. Kept for reference.

Build decorations.json: furniture, lights and decorations you can make from Springlands materials alone, from
scrape_decor.py's data, for the planner's item catalogue and the Crafting list.

Usage: python -I build_decor.py <raw_decor.json> <tools-1-0.txt> <craft-src dir> <out.json>

Leaves out what the other data files already have (blocks, chests, stations, doors and windows) and anything
whose recipe tree needs a material, crafter or station from outside the Springlands. `mount` (floor, wall or
ceiling) and the category are guessed from the name; sizes aren't published, so the planner asks for them.
"""
import glob
import json
import os
import re
import sys

RAW, CHANGELOG, SRC, OUT = sys.argv[1:5]
raw = json.load(open(RAW, encoding="utf-8"))
items_raw, res_raw = raw["items"], raw["resources"]
SITE = "https://www.enshrouded.tools"

SPRING_RAW = {"Wood Logs", "Plant Fiber", "Twigs", "Resin", "Stone", "Flintstone", "Springlands Dirt", "Rubble",
              "Metal Scraps", "Animal Fur", "Bones", "Torn Cloth", "Shroud Spores", "Feather", "Hide"}
# Crafters rescued in the Springlands (the Collector in its Hollow Halls) and the stations you can build there.
# Not the Kiln (Revelwood Stone), Table Saw (sawblades from the Revelwood), Masonry or Smithing Tools (iron).
SPRING_MAKERS = {"Workbench", "By hand", "Manual Crafting", "Carpenter", "Blacksmith", "Alchemist", "Farmer", "Hunter",
                 "Collector", "Forge", "Charcoal Kiln", "Grinding Stones", "Drying Rack", "Seedbed", "Decoration Workbench"}
CRAFTER = {"workbench": ("Workbench", None), "carpenter": (None, "Carpenter"), "decoration-workbench": ("Decoration Workbench", None),
           "hunter": (None, "Hunter"), "bard": (None, "Bard"), "collector": (None, "Collector"), "farmer": (None, "Farmer"),
           "alchemist": (None, "Alchemist"), "blacksmith": (None, "Blacksmith")}
NPC = {"Alchemist", "Collector", "Hunter", "Blacksmith", "Carpenter", "Farmer", "Bard", "Fisher", "Barber"}
GATHERED_FIRST = {"Twigs", "Animal Fur"}

CL = open(CHANGELOG, encoding="utf-8").read().split("\n")
_ni = [i for i, l in enumerate(CL) if l == "New items"][-1]
_nq = next(i for i in range(_ni, len(CL)) if CL[i] == "New quests, lore and places")
NEW_NAMES = {l for l in CL[_ni:_nq] if not re.search(r"\(\d+\)$", l)}

# names the other files already cover
taken = set()
for p in glob.glob(os.path.join(SRC, "*.json")):
    if os.path.basename(p) in ("decorations.json", "source-overrides.json"):
        continue
    for it in json.load(open(p, encoding="utf-8")).get("items", []):
        taken.add(it["name"]); taken.add(it.get("catalogueName") or "")


def primary(info):
    if info.get("name") in GATHERED_FIRST:
        return None
    src = (info.get("sections", {}).get("Where to get it") or [None])[0]
    src = {"Manual Crafting": "By hand", "Huntress": "Hunter"}.get(src, src)
    recs = info["recipes"]
    return next((r for r in recs if r["crafter"] == src), recs[0] if recs else None)


def springlands(slug, why, seen=()):
    info = res_raw.get(slug)
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


def guess_mount(name):
    n = name.lower()
    if re.search(r"chandelier|hanging|pendant|ceiling|wind chime", n):
        return "ceiling"
    if re.search(r"\bwall\b(?! iv| v| vi| ii| iii| i\b)|wall-mounted|wall mounted|trophy|painting|banner|tapestry|mirror|sconce|wall mount|mounted|wreath|curtain|clock", n) and "wall i" not in n:
        return "wall"
    return "floor"


CATS = [("Lights & fires", r"lamp|lantern|torch|candle|brazier|chandelier|light|fire bowl|sconce|lightbringer|fireplace|bonfire"),
        ("Animals", r"feeder|\bcat\b|\bdog\b|snap trap"),
        ("Seating", r"chair|stool|bench|throne|sofa|armchair|seat"),
        ("Tables", r"table|desk|counter|nightstand"),
        ("Beds & comfort", r"bed\b|mattress|pillow|bath|tub|rug|carpet|mat\b|blanket|cushion|hammock"),
        ("Storage & shelves", r"shelf|shelves|cabinet|crate|barrel|cupboard|wardrobe|dresser|rack|basket|box|sack|bundle|bag"),
        ("Walls & fences", r"fence|palisade|wall|divider|railing|banister|scaffold|strut|pole|post|pillar|column|beam|arc|arch|stairs?\b|ladder"),
        ("Kitchenware", r"pot\b|pan\b|bowl|plate|platter|cup|jug|mug|flask|vat|kettle|ladle|bottle|jar|cauldron|goblet|tray"),
        ("Plants", r"plant|flower|tree|bush|vine|seedling|hedge|ivy|rose|fern|moss"),
        ("Trophies & art", r"trophy|statue|painting|banner|bust|figure|sculpture|skull|tapestry|mirror|globe|map|book|clock|instrument|drum|lute|harp")]


def guess_cat(name):
    n = name.lower()
    return next((c for c, rx in CATS if re.search(rx, n)), "Other decorations")


items, left_out, seen_names = [], [], set()
for key, r in items_raw.items():
    name = r["name"]
    if name in taken or name in seen_names or re.search(r"\bBlock\b|Door|Window|Trapdoor|\bGate\b", name):
        continue
    station, crafter = CRAFTER[r["crafter"]]
    why = set()
    ok = True
    for m in (station or crafter, r["needs"]):
        if m and m not in SPRING_MAKERS:
            why.add(m); ok = False
    for i in r["inputs"]:
        if "anyOf" in i:
            if not SPRING_RAW & set(i["anyOf"]):
                why.add(i["item"]); ok = False
        elif not springlands(i["slug"], why):
            ok = False
    if not ok:
        left_out.append(f"{name} (needs {', '.join(sorted(why))})")
        continue
    seen_names.add(name)
    mount = guess_mount(name)
    it = {"name": name, "category": guess_cat(name), "station": station, "crafter": crafter,
          "requires": [r["needs"]] if r["needs"] and r["needs"] not in NPC else [], "makes": r["makes"], "craftTime": r["time"],
          "inputs": [dict({"item": i["item"], "qty": i["qty"]}, **({"anyOf": i["anyOf"]} if "anyOf" in i else {})) for i in r["inputs"]],
          "mount": mount, "confidence": "likely-1.0", "newIn1_0": name in NEW_NAMES,
          "note": f"Placed {'on a wall' if mount == 'wall' else 'from the ceiling' if mount == 'ceiling' else 'on the floor'} (a guess from its name). Its size in blocks isn't published: measure it in game.",
          "sources": [SITE + "/items/" + r["slug"]]}
    items.append(it)

# resources under the kept items, as the other files do them
resources, seen, queue = {}, set(), []
by_name = {r["name"]: r for r in items_raw.values()}
for it in items:
    queue += [i for i in by_name[it["name"]]["inputs"] if "slug" in i]
while queue:
    inp = queue.pop(0)
    if inp["slug"] in seen:
        continue
    seen.add(inp["slug"])
    info = res_raw.get(inp["slug"])
    if info is None:
        continue
    r = primary(info)
    src = (info.get("sections", {}).get("Where to get it") or [None])[0]
    if r:
        c = r["crafter"]
        sr = {"station": r["needs"], "crafter": c, "requires": []} if c in NPC else \
             {"station": None, "crafter": None, "requires": [r["needs"]] if r["needs"] else []} if c in ("By hand", "Manual Crafting") else \
             {"station": c, "crafter": None, "requires": [r["needs"]] if r["needs"] else []}
        e = {"kind": "crafted", "source": src or c,
             "recipe": dict(sr, makes=r["makes"], time=r["time"],
                            inputs=[dict({"item": i["item"], "qty": i["qty"]}, **({"anyOf": i["anyOf"]} if "anyOf" in i else {})) for i in r["inputs"]])}
        queue += [i for i in r["inputs"] if "slug" in i]
    else:
        e = {"kind": "gathered", "source": src, "recipe": None}
    e["sources"] = [SITE + "/items/" + inp["slug"]]
    resources[info["name"]] = e

cats = sorted({it["category"] for it in items})
data = {
    "fetched": "2026-10-15",
    "notes": (f"{len(items)} furniture, lights and decorations you can make from Springlands materials alone "
              f"({', '.join(f'{sum(i['category'] == c for i in items)} {c}' for c in cats)}), from the Building recipes of the "
              "Workbench, Carpenter, Decoration Workbench, Hunter, Collector, Farmer, Alchemist and Blacksmith on enshrouded.tools "
              "(1.0 game files, Steam build 25936191; likely-1.0, not checked in game). Springlands only, as for doors-windows.json, "
              "but the Collector counts (rescued in the Springlands Hollow Halls) and the Kiln, Table Saw, Masonry Tools and Smithing "
              "Tools don't (they need Revelwood Stone, Revelwood sawblades or iron). Each item's mount (floor, wall, ceiling) and "
              "category are guessed from its name; sizes aren't published, so the planner asks for them."),
    "leftOut": sorted(left_out),
    "items": sorted(items, key=lambda it: (it["category"], it["name"])),
    "resources": resources,
}
json.dump(data, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"{len(items)} kept, {len(left_out)} left out, {len(resources)} resources -> {OUT}", file=sys.stderr)
