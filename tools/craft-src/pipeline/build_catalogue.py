"""Build one catalogue batch's JSON (structural.json, lights.json, ...; catalogue_batches.py says which items):
every item in the batch with its recipe, the region where you can first make it, its comfort and what unlocks it.

Usage: python -I build_catalogue.py <batch> <raw.json> <tools-1-0.txt> <out.json>

<raw.json> comes from scrape_catalogue.py for the same batch; <tools-1-0.txt> is the text of enshrouded.tools/1-0
(the site's diff of the last Early Access build against 1.0), for what 1.0 renamed.

"Makeable from" is the latest region the recipe tree reaches, following each part's main recipe down to raw
resources: where each raw resource is first found (its page's "Where to get it"), where each crafter is rescued
(enshrouded.tools/survivors), and the same for every station and requirement on the way. The regions run in the
order the Flame opens them (enshrouded.tools/regions); the Low Meadows count as the Springlands and the Blackmire
as the Revelwood. It says when you could first make it, not when the recipe unlocks.
"""
import json
import re
import sys

from catalogue_batches import BATCHES, classify

BATCH, RAW, CHANGELOG, OUT = sys.argv[1:5]
WHAT = BATCHES[BATCH]["what"]
raw = json.load(open(RAW, encoding="utf-8"))
items_raw, res_raw = raw["items"], raw["resources"]
by_slug = dict(res_raw)
by_slug.update(items_raw)
SITE = "https://www.enshrouded.tools"
slugify = lambda n: re.sub(r"[^a-z0-9]+", "-", n.lower().replace("'", "")).strip("-")

REGIONS = ["Springlands", "Revelwood", "Nomad Highlands", "Kindlewastes", "Albaneve Summits", "Veilwater Basin",
           "Cinder's Cradle"]
ALIAS = {"Low Meadows": "Springlands", "Blackmire": "Revelwood"}
# Where each crafter is rescued (enshrouded.tools/survivors, 2026-10-20).
NPC_REGION = {"Alchemist": "Springlands", "Collector": "Springlands", "Hunter": "Springlands", "Huntress": "Springlands",
              "Carpenter": "Springlands", "Blacksmith": "Springlands", "Farmer": "Springlands",
              "Lunar New Year Trader": "Springlands", "Bard": "Revelwood", "Barber": "Revelwood",
              "Fisher": "Veilwater Basin", "Ancient Researcher": "Cinder's Cradle"}
HAND = {"By hand", "Manual Crafting", None}
# Station parts whose first copy a survivor's quest hands you, earlier than their recipe could (enshrouded.tools
# quest and place pages): the region the quest sends you to.
QUEST_FIRST = {"Crucible": ("Revelwood", "the Crucible from a Scavenger mine (Blacksmith's quest)"),
               "Circular Sawblades": ("Revelwood", "Circular Sawblades from Fawnsong Frontier (Carpenter's quest)"),
               "Masonry Tools": ("Nomad Highlands", "Masonry Tools from the Pillars of Creation (Carpenter's quest)"),
               "Bellows": ("Albaneve Summits", "Bellows from the Forge of Obsidia (Blacksmith's quest)"),
               "Almanac of Plants and Seedlings": ("Nomad Highlands", "the Almanac from Surat's Rest (Farmer's quest)")}
# Raw resources found in the Springlands whose pages name no region (they turn up everywhere: trees, bushes,
# small stones, ruins, Scavenger and wildlife drops).
SPRING_RAW = {"Wood Logs", "Plant Fiber", "Twigs", "Resin", "Stone", "Flintstone", "Springlands Dirt", "Rubble",
              "Metal Scraps", "Animal Fur", "Bones", "Torn Cloth", "Paper Reed", "Fur Patch"}
# Resources whose pages name no region, placed by what the site says about them.
REGION_FIX = {"Wax": ("Springlands", "Wax from wild beehives, a few near Longkeep"),
              "Honey": ("Springlands", "Honey from wild beehives, a few near Longkeep"),
              "Mycelium (material)": ("Springlands", "Mycelium from the Shroud (the first is in the Springlands)"),
              "Luminous Growth": ("Springlands", "Luminous Growth, found in caves (the site names no region)"),
              "Toxic Slime": ("Springlands", "Toxic Slime from the Hollow Halls (the first is in the Springlands)"),
              "Hollow Cyclops Head": ("Revelwood", "Hollow Cyclops Head from the Hollow Cyclops, first in the Revelwood"),
              "Shroud Wood": ("Springlands", "Shroud Wood from dead trees in the Shroud (the first is in the Springlands)"),
              "Hollow Titan Head": ("Albaneve Summits", "Hollow Titan Head from a Hollow Halls boss that drops Icy Giant Bones (Albaneve Summits on)"),
              "Hollow Wispwyvern Head": ("Albaneve Summits", "Hollow Wispwyvern Head from a Hollow Halls boss that drops Icy Giant Bones (Albaneve Summits on)")}
# Sizes the user measured in game (2026-10-15), in blocks: height, width. Nothing publishes them.
MEASURED = {"Crude Wooden Door": (5, 4), "Wooden Door": (5, 4), "Round Wooden Door": (6, 6),
            "Round Wooden Door Frame": (6, 6), "Wooden Double Door": (7, 8), "Steel Portcullis": (12, 6),
            "Wooden Window Frame": (3, 2), "Round Wooden Window Frame": (2, 2), "Large Round Wooden Window Frame": (6, 6)}

CL = open(CHANGELOG, encoding="utf-8").read().split("\n")
RENAMED = {}
for i, l in enumerate(CL[:-1]):
    m = re.match(r"Renamed from (.+)$", CL[i + 1])
    if m:
        RENAMED[l] = m.group(1)


def where(info):
    return info.get("sections", {}).get("Where to get it") or []


def region_in(lines):
    """The earliest region named in some lines of text, as an index into REGIONS (None if none is)."""
    best = None
    for l in lines:
        for name in REGIONS + list(ALIAS):
            if name in l:
                k = REGIONS.index(ALIAS.get(name, name))
                best = k if best is None else min(best, k)
    return best


def primary(info):
    """The recipe followed: none when the item is gathered first (its "Where to get it" names a region), else the
    one made where that line says, else the first."""
    w = where(info)
    if w and region_in(w[:1]) is not None:
        return None
    src = {"Manual Crafting": "By hand", "Huntress": "Hunter"}.get(w[0], w[0]) if w else None
    recs = info["recipes"]
    return next((r for r in recs if r["crafter"] == src), recs[0] if recs else None)


def needs_of(r):
    """A recipe's requirements: "Needs Smelter and Forge" is two stations, but "Almanac of Plants and Seedlings" is
    one thing (split only when every part is a page of its own)."""
    if not r["needs"]:
        return []
    parts = [n.strip() for n in r["needs"].split(" and ")]
    real = lambda p: p in NPC_REGION or (by_slug.get(slugify(p)) or {}).get("name") == p
    return parts if len(parts) > 1 and all(real(p) for p in parts) else [r["needs"]]


def split(r):
    c, n = r["crafter"], needs_of(r)
    if c in NPC_REGION:
        return {"station": n[0] if n else None, "crafter": c, "requires": n[1:]}
    if c in HAND:
        return {"station": None, "crafter": None, "requires": n}
    return {"station": c, "crafter": None, "requires": n}


MEMO = {}


def tier(slug, stack=()):
    """(region index or None, what sets it, things whose region isn't known) for one item or resource."""
    if slug in MEMO:
        return MEMO[slug]
    if slug in stack:
        return (None, None, set())
    info = by_slug.get(slug)
    if info is None:                                        # (a page not fetched: a pinned region still counts)
        pin = next((v for k, v in {**REGION_FIX, **QUEST_FIRST}.items() if slugify(k) == slug), None)
        return (REGIONS.index(pin[0]), pin[1], set()) if pin else (None, None, {slug})
    fix = REGION_FIX.get(info.get("name"))
    if fix:
        MEMO[slug] = (REGIONS.index(fix[0]), fix[1], set())
        return MEMO[slug]
    r = primary(info)
    if r is None:
        nm = info.get("name") or slug
        sec = info.get("sections", {})
        about = " ".join(sec.get("About", []))
        k = region_in(where(info))                          # where to get it, else
        if k is None:
            k = region_in([nm])                             # a region in its name (Revelwood Stone), else
        if k is None and (nm in SPRING_RAW or re.search(r"(all over|across) Embervale", about)):
            k = 0                                           # found everywhere, else
        if k is None:
            k = region_in([about])                          # the first region its description names, else
        if k is None:
            k = region_in(sec.get("Where to mine it", []))  # where it's mined, else
        why = nm
        if k is None and info.get("dropRegions"):           # the earliest region an enemy that drops it lives in
            best_e = min(((region_in(r), e) for e, r in info["dropRegions"].items() if region_in(r) is not None), default=None)
            if best_e:
                k, why = best_e[0], f"{nm} from the {best_e[1]}"
        out = (k, why, set() if k is not None else {nm})
        MEMO[slug] = out
        return out
    best, why, unknown = 0, None, set()

    def take(k, name, unk=()):
        nonlocal best, why
        unknown.update(unk)
        if k is not None and (why is None or k > best):
            best, why = k, name

    for m in [r["crafter"]] + needs_of(r):
        if m in HAND:
            continue
        if m in NPC_REGION:
            take(REGIONS.index(NPC_REGION[m]), m)
        else:
            k, w, u = tier(slugify(m), stack + (slug,))
            take(k, f"{m} ({w})" if w and w != m else m, u)
    for i in r["inputs"]:
        if "anyOf" in i:                                    # "Any wood": the earliest option
            opts = [tier(slugify(o), stack + (slug,)) + (o,) for o in i["anyOf"]]
            known = [o for o in opts if o[0] is not None]
            if known:
                k, w, u, o = min(known, key=lambda o: o[0])
                take(k, i["item"])
            else:
                unknown.add(i["item"])
        else:
            k, w, u = tier(i["slug"], stack + (slug,))
            take(k, i["item"] if not w or w == i["item"] else f"{i['item']} ({w})", u)
    q = QUEST_FIRST.get(info.get("name"))
    if q and REGIONS.index(q[0]) <= best:
        best, why, unknown = REGIONS.index(q[0]), q[1], set()
    out = (best, why, unknown)
    MEMO[slug] = out
    return out


def inputs(r):
    return [dict({"item": i["item"], "qty": i["qty"]}, **({"anyOf": i["anyOf"]} if "anyOf" in i else {})) for i in r["inputs"]]


def about(info):
    a = info.get("sections", {}).get("About") or info.get("sections", {}).get("Description")
    return re.sub(r"\s+([,.])", r"\1", " ".join(a)) if a else None


items, found_only, dupes, seen_names = [], [], [], {}
for slug, info in sorted(items_raw.items()):
    name = info.get("name") or info.get("listedName")
    if "\\" in name and info.get("listedName"):         # (a name with quotes the page parse cut short: Mannequin "Victory")
        name = info["listedName"]
    c = classify(BATCH, name)
    if not c:
        continue
    cat, mount, opening = c
    recs = info["recipes"]
    r = next((x for x in recs if x["crafter"] == (where(info) or [None])[0]), recs[0] if recs else None)
    if name in seen_names:                                  # same name, another page: keep one per recipe
        prev = seen_names[name]
        if prev is None or (r and prev and inputs(r) == prev["inputs"] and split(r) == {k: prev[k] for k in ("station", "crafter", "requires")}):
            dupes.append(f"{name} ({slug}): same as the one kept")
            continue
        if r is None:
            dupes.append(f"{name} ({slug}): not crafted; the crafted one is kept")
            continue
    it = {"name": name, "category": cat, "mount": mount, "rarity": info["kv"].get("Rarity")}
    if opening:
        it["opening"] = opening
    notes = []
    if r:
        it.update(split(r))
        it.update({"makes": r["makes"], "craftTime": r["time"], "inputs": inputs(r)})
        k, why, unknown = tier(slug)
        if k is not None:
            it["region"] = REGIONS[k]
            if why:
                it["regionBy"] = why
        if unknown:
            it["regionUnknown"] = sorted(unknown)
            notes.append("Where some of its parts come from isn't on the site (" + ", ".join(sorted(unknown)) + "), so its region may be later.")
    else:
        it.update({"station": None, "crafter": None, "requires": [], "makes": 1, "inputs": []})
        k = region_in(where(info) + info.get("sections", {}).get("Where to find it", []))
        if k is not None:
            it["region"] = REGIONS[k]
        it["found"] = True
        src = ", ".join(where(info)) or None
        notes.append("Not crafted: " + (f"from {src}." if src else "found in the world, not made."))
        found_only.append(name)
    it.update({"confidence": "likely-1.0", "newIn1_0": bool(info.get("new"))})
    for b, v in (info.get("badges") or {}).items():         # "Comfort - Illumination": 1, "Frost Resistance": 3
        if b.startswith("Comfort - "):
            it["comfort"] = {"type": b[len("Comfort - "):].replace("Category ", ""), "value": v}   # ("Category Bed")
        else:
            it.setdefault("resist", {})[b.replace(" Resistance", "").lower()] = v
    if info.get("unlock"):
        it["unlock"] = info["unlock"]
    if cat in BATCHES[BATCH].get("decor", ()):
        it["holdsNothing"] = True                           # storage-style furniture that stores nothing
    if BATCHES[BATCH].get("refile"):                        # sorted by what it does, from its description
        desc = " ".join(info.get("sections", {}).get("Description", []))
        it["category"] = BATCHES[BATCH]["refile"](name, cat, desc, it.get("comfort"))
    if name in RENAMED:
        it["renamedFrom"] = RENAMED[name]
    if name.startswith("Secret "):
        notes.append("A hidden door that looks like a wall of its blocks.")
    if name.startswith("Fake "):
        notes.append("Looks like a door but doesn't open.")
    if name.endswith("Frame") and "Door" in name:
        notes.append("A door frame with no door in it.")
    if name in MEASURED:
        hb, wb = MEASURED[name]
        it["size"] = {"h": hb, "w": wb}
        notes.append(f"{hb} blocks tall and {wb} wide (measured in game).")
    else:
        notes.append("Its size in blocks isn't published: measure it in game.")
    it["note"] = " ".join(notes)
    it["sources"] = [SITE + "/items/" + slug]
    seen_names[name] = it if r else None
    if name in [x["name"] for x in items]:                  # a second crafted variant with its own recipe
        n = sum(x["name"].startswith(name) for x in items) + 1
        it["name"] = f"{name} ({n})"
        it["note"] = f"Another piece the game also calls {name}, with its own recipe. " + it["note"]
    items.append(it)

# resources: every part under the kept items, as the other files do it
resources, seen = {}, set()
queue = [i for it in items for i in it["inputs"]]
for it in items:
    for m in [it.get("station")] + it.get("requires", []):
        if m:
            queue.append({"item": m, "slug": slugify(m)})
while queue:
    inp = queue.pop(0)
    if "anyOf" in inp:
        for o in inp["anyOf"]:
            queue.append({"item": o, "slug": slugify(o)})
        continue
    slug = inp.get("slug") or slugify(inp["item"])
    if slug in seen:
        continue
    seen.add(slug)
    info = by_slug.get(slug)
    if info is None:
        resources[inp["item"]] = {"kind": "unknown", "source": None, "recipe": None}
        continue
    r = primary(info)
    w = where(info)
    if r:
        e = {"kind": "crafted", "source": (w[0] if w else None) or r["crafter"],
             "recipe": dict(split(r), makes=r["makes"], time=r["time"], inputs=inputs(r))}
        queue.extend(r["inputs"])
        for m in [r["crafter"]] + needs_of(r):
            if m not in HAND and m not in NPC_REGION:
                queue.append({"item": m, "slug": slugify(m)})
    else:
        e = {"kind": "gathered", "source": ", ".join(w) if w else None, "recipe": None}
        if not w and about(info):
            e["note"] = about(info)
    k = tier(slug)[0]
    if k is not None:
        e["region"] = REGIONS[k]
    e["sources"] = [SITE + "/items/" + slug]
    resources[info["name"]] = e

cats = {}
for it in items:
    cats[it["category"]] = cats.get(it["category"], 0) + 1
by_region = {}
for it in items:
    by_region[it.get("region", "unknown")] = by_region.get(it.get("region", "unknown"), 0) + 1
data = {
    "fetched": "2026-10-20",
    "notes": (f"{len(items)} {WHAT} in 1.0 ({', '.join(f'{n} {c.lower()}' for c, n in cats.items())}). "
              "Source: enshrouded.tools item pages, read from the game files (build 25988036); every recipe is likely-1.0 "
              "(datamined, not checked in game). `region` is the first region where you could make it: the latest region its "
              "recipe tree reaches (raw resources where first found, crafters where rescued, every station on the way). "
              "`comfort` is the comfort it gives (type and value), `resist` any resistance it adds, and `unlock` the site's "
              "text for what unlocks the recipe. Sizes in blocks aren't published anywhere: `size` (blocks, h and w) is on the "
              "ones measured in game. Items that stand for planner library types in base-objects.json get these details "
              "merged in by make_craft_js.py."),
    "byRegion": {r: by_region[r] for r in REGIONS + ["unknown"] if r in by_region},
    "notCrafted": sorted(found_only),
    "duplicates": dupes,
    "items": sorted(items, key=lambda it: (it["category"], REGIONS.index(it["region"]) if it.get("region") in REGIONS else 9, it["name"])),
    "resources": resources,
}
json.dump(data, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"{len(items)} {WHAT} ({len(found_only)} not crafted), {len(dupes)} duplicates dropped, {len(resources)} resources -> {OUT}",
      file=sys.stderr)
print("by region:", data["byRegion"], file=sys.stderr)
print("by category:", cats, file=sys.stderr)
