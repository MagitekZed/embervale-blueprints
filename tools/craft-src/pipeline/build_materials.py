"""Build building-materials.json from the scraped enshrouded.tools pages.

Usage:
  python -I build_materials.py <materials-raw.json> <cache_dir> <recipes.json> <tools-1-0.txt> <out.json>

<materials-raw.json>  output of `scrape_materials.py items`
<cache_dir>           the page cache (page-building-blocks.html is read for tiers)
<recipes.json>        tools/blocks-src/recipes.json (pre-1.0 wiki recipes, for changes1_0)
<tools-1-0.txt>       text of enshrouded.tools/1-0 (one line per text node), for the
                      site's own 1.0 recipe diff and its "New items" lists
<out.json>            tools/craft-src/building-materials.json

Output shape matches eternal-spells.json: {fetched, notes, items, resources}.
make_craft_js.py merges every *.json in craft-src, so nothing else is written there.
"""
import html
import json
import re
import sys

RAW, CACHE, OLD, CHANGELOG, OUT = sys.argv[1:6]
sys.stdout.reconfigure(encoding="utf-8")
raw = json.load(open(RAW, encoding="utf-8"))
items_raw = raw["items"]
res_raw = raw["resources"]
old_all = json.load(open(OLD, encoding="utf-8"))
old = old_all["recipes"]
old_inter = {k: v for k, v in old_all.get("intermediates", {}).items() if not k.startswith("_")}

SITE = "https://www.enshrouded.tools"
CHANGELOG_URL = SITE + "/1-0"
BLOCKS_URL = SITE + "/building-blocks"
NPC_CRAFTERS = {"Alchemist", "Collector", "Hunter", "Blacksmith", "Carpenter", "Farmer", "Bard", "Fisher",
                "Ancient Researcher"}

# ---- planner catalogue grouping (tools/blocks-src catalogue, as the planner groups it) ----
GROUPS = {
    "Stone blocks": ["Castle Block", "Castle Wall Stone Block", "Citywall Block", "Desert City Wall",
                     "Desert Temple Block", "Drak Temple Block", "Fancy Stone Block", "Fired Bricks Block",
                     "Granite Block", "Highly Polished Stone Block", "Hollow Halls Block", "Limestone Block",
                     "Mixed Sandstone Block", "Mycelium Overgrown Block", "Polished Granite Block",
                     "Refined Sandstone Block", "Refined Stone Block", "Regular Sandstone Block",
                     "Regular Stone Block", "Rough Flintstone Block", "Rough Sandstone Block", "Rough Stone Block",
                     "Roughly Cut Stone Block", "Shell Limestone Block", "Temple Stones", "Weathered Stone Block",
                     "Well Block"],
    "Wood blocks": ["Bamboo Wood Block", "Brick-Timbered Block", "Conifer Wood Block", "Half-Timbered Block",
                    "Half-timbered Shell Limestone Block", "Palm Wood Block", "Plaited Block", "Refined Wood Block",
                    "Rough Wood Block", "Shroud Wood Block", "Tarred Wood Block"],
    "Luminescent blocks": ["Blue Luminescent Block", "Green Luminescent Block", "White Luminescent Block",
                           "Yellow Luminescent Block"],
    "Other blocks": ["Bone Block", "Bronze Block", "Copper Block", "Ectoplasm Block", "Iron Block", "Metal Block",
                     "Midnight Tomb Block", "Obsidian Block", "Red Carpet Block", "Red Marble Block",
                     "Starlight Block"],
    "Roof blocks": ["Castle Roof Block", "Desert Shingle Roof Block", "Drak Temple Roof Block",
                    "Granite Ornamented Roof Block", "Granite Shingle Roof Block", "Palm Leaf Roof Block",
                    "Plant Fiber Roof Block", "Roof Tiles Block", "Shell Limestone Shingles",
                    "Stone Shingle Roof Block", "Straw Roof Block", "Tarred Shingle Roof Block",
                    "Tarred Straw Block"],
    "Roads": ["Dirt Road Block", "Field Stones", "Granite Rubble Road Block", "Limestone Road Block",
              "Rocky Stone Road Block", "Shell Limestone Road Block", "Smooth Stone Road Block"],
}
CATEGORY_OF = {n: g for g, ns in GROUPS.items() for n in ns}
# Tiers the building-blocks table parse misses (its row for the overgrowth reads plain "Mycelium").
TIER_FIX = {"Mycelium (overgrowth)": "3, Nomad Highlands"}
# Everything else in the catalogue is soil / terrain.
# Building materials new in 1.0 and the planner group they join:
NEW_CATEGORY = {
    "Ancient Beacon Block": "Stone blocks", "Ancient Circles Block": "Stone blocks",
    "Ancient Dungeon Block": "Stone blocks", "Ancient Stone Block": "Stone blocks",
    "Weathered Ancient Stone Block": "Stone blocks", "Moonstone Block": "Stone blocks",
    "Ancient Gold Block": "Other blocks", "Ornate Wood Block": "Wood blocks",
    "Ancient Road Block": "Roads",
    "Ivy": "Overgrowth", "Climbing Rose": "Overgrowth", "Mycelium (overgrowth)": "Overgrowth", "Wisteria": "Overgrowth",
    "Underwater Overgrowth": "Overgrowth",
}
# Names changed here so they don't clash with a resource of the same name (the site calls this overgrowth just
# "Mycelium", the same as the Mycelium used in recipes).
DISPLAY = {"mycelium-decoration": "Mycelium (overgrowth)"}
# New 1.0 "Building" items that turned out to be furniture props (Decoration Workbench,
# stack 50, not on the site's building-blocks list), so not Construction Hammer materials.
NOT_MATERIALS = {"Ancient Column Block", "Red Marble Column Block"}

# Pre-1.0 (wiki) input names that the 1.0 data spells differently.
ALIASES = {"fired brick": "fired bricks", "mycelium (material)": "mycelium", "indigo plant (material)": "indigo plant"}
# ...of which only these are real renames ("(Material)" is just the wiki's page disambiguation).
REAL_RENAMES = {"fired brick"}


def norm(n):
    n = n.strip().lower()
    return ALIASES.get(n, n)


def page_lines(path):
    t = open(path, encoding="utf-8").read()
    b, e = t.find("<main"), t.find("</main>")
    m = re.sub(r"<!--.*?-->", "", t[b:e], flags=re.S)
    m = html.unescape(re.sub(r"<[^>]+>", "\n", m))
    return [l.strip() for l in m.split("\n") if l.strip()]


def find_count(slug):
    """'Where to find it' header count (map spots), e.g. '1,867 in Embervale'."""
    L = page_lines(f"{CACHE}/item-{slug}.html")
    if "Where to find it" in L:
        nxt = L[L.index("Where to find it") + 1]
        if re.match(r"^[\d,]+ in ", nxt):
            return nxt
    return None


# ---- tiers from the building-blocks table ----
BL = page_lines(f"{CACHE}/page-building-blocks.html")
TIER = {}
if "Every block and its recipe" in BL:
    k = BL.index("Every block and its recipe")
    for i in range(k, len(BL) - 2):
        if BL[i + 1] in ("Block", "Roof block", "Overgrowth") and re.match(r"^\d+, ", BL[i + 2]):
            TIER[BL[i]] = BL[i + 2]

# ---- 1.0 changelog (enshrouded.tools diff of Early Access vs 1.0 game data) ----
CL = open(CHANGELOG, encoding="utf-8").read().split("\n")
new_item_names = set()
a = next(i for i, l in enumerate(CL) if re.match(r"^Materials \(\d+\)$", l))
b = next(i for i, l in enumerate(CL) if re.match(r"^Tools and gear \(\d+\)$", l))
for l in CL[a + 1:b]:
    if not re.match(r"^Building \(\d+\)$", l):
        new_item_names.add(l)


def _is_diff(x):
    return "→" in x or x.startswith("+ ") or x.startswith("- ")


changed_recipes = {}
a = next(i for i, l in enumerate(CL) if l.startswith("Changed recipes ("))
b = next(i for i in range(a + 1, len(CL)) if re.match(r"^Changed skill tree nodes \(", CL[i]))
i = a + 3
while i < b:
    name, crafter = CL[i], CL[i + 1] if i + 1 < b else None
    j = i + 2
    diff = []
    while j < b and _is_diff(CL[j]):
        diff.append(CL[j])
        j += 1
    if diff:
        changed_recipes.setdefault((name, crafter), []).extend(diff)
        i = j
    else:
        i += 1
renamed = {}
s0 = next((i for i, l in enumerate(CL) if l.startswith("Items with new stats (")), None)
if s0 is not None:
    for i in range(s0, a):
        if CL[i].startswith("Renamed from "):
            renamed[CL[i - 1]] = CL[i][len("Renamed from "):].strip('"')


def split_recipe(r):
    crafter = r["crafter"]
    if crafter in NPC_CRAFTERS:
        return {"station": r["needs"], "crafter": crafter, "requires": []}
    return {"station": crafter, "crafter": None, "requires": [r["needs"]] if r["needs"] else []}


def water_of(r):
    for h in r.get("header_text", []):
        m = re.match(r"(\d+) water charges?", h)
        if m:
            return int(m.group(1))
    return None


def inputs_of(r):
    out = []
    for x in r["inputs"]:
        d = {"item": x["item"], "qty": x["qty"]}
        if "anyOf" in x:
            d["anyOf"] = x["anyOf"]
        out.append(d)
    w = water_of(r)
    if w:
        out.append({"item": "Water", "qty": w, "waterCharges": True})
    return out


def where_lines(info):
    return info.get("Where to get it") or []


def pick_primary(info):
    recipes = info["recipes"]
    if not recipes:
        return None
    get = where_lines(info)
    for r in recipes:
        if r["crafter"] in get[:3]:
            return r
    return recipes[0]


def old_crafter(c):
    if not c or c.startswith("Player") or c.startswith("None"):
        return None
    return re.split(r"[\s(,:]", c)[0]


def diff_recipe(o_inputs, o_makes, o_station, o_crafter, r, compare_crafter=True):
    """Differences between a pre-1.0 wiki recipe and the 1.0 recipe r ('old -> new').

    compare_crafter is off for production-station parts: there the wiki's Crafter
    field names who builds the station (Kiln -> Carpenter), not who crafts the part."""
    out = []
    new_inputs = inputs_of(r)  # includes water charges as 'Water'
    oi = {norm(x["item"]): (x["item"], x["qty"]) for x in o_inputs}
    ni = {norm(x["item"]): (x["item"], x["qty"]) for x in new_inputs}
    any_of = {norm(x["item"]): [o.lower() for o in x["anyOf"]] for x in new_inputs if "anyOf" in x}
    for k, (nm, q) in ni.items():
        if k in oi:
            onm, oq = oi[k]
            if oq != q:
                out.append(f"{nm} {oq} -> {q}")
            if onm.lower() in REAL_RENAMES:
                out.append(f"Input renamed {onm} -> {nm}")
    for k, (nm, q) in ni.items():
        if k in oi:
            continue
        # an old single input that is now one option of an "Any ..." slot
        hit = next((ok for ok in oi if ok not in ni and ok in any_of.get(k, [])), None)
        if hit:
            onm, oq = oi.pop(hit)
            opts = next(x["anyOf"] for x in r["inputs"] if norm(x["item"]) == k)
            out.append(f"{onm} {oq} -> {nm} {q} (slot takes any of {', '.join(opts)})")
            continue
        out.append(f"+ {nm} {q}")
    for k, (onm, oq) in oi.items():
        if k not in ni:
            out.append(f"- {onm} {oq}")
    if o_makes is not None and o_makes != r["makes"]:
        out.append(f"Makes {o_makes} -> {r['makes']}")
    sr = split_recipe(r)
    if (o_station or None) != (sr["station"] or None):
        out.append(f"Station {o_station or 'none'} -> {sr['station'] or 'none'}")
    oc = old_crafter(o_crafter)
    if compare_crafter and oc != sr["crafter"]:
        out.append(f"Crafter {oc or 'player'} -> {sr['crafter'] or 'player'}")
    return out


def diff_old(o, r):
    if o is None:
        return []
    if not o.get("craftable"):
        return ["Now craftable (pre-1.0 wiki: not craftable)"] if r is not None else []
    if r is None:
        return ["No recipe in the 1.0 data (pre-1.0 wiki: craftable)"]
    return diff_recipe(o.get("inputs", []), o.get("makes"), o.get("station"), o.get("crafter"), r)


def fmt_inputs(inputs):
    return ", ".join(f"{x['item']} x{x['qty']}" for x in inputs)


CATALOGUE = list(old.keys())
CAT_BY_NORM = {norm(n): n for n in CATALOGUE}

# Per-item notes added by hand after reading the pages (keyed by 1.0 name).
EXTRA_FLAGS = {
    "Weathered Ancient Stone Block": "Conversion recipe: 100 Ancient Stone Block + 5 Blackmire Stone make 100, so it costs a full stack of Ancient Stone Block plus the stone.",
    "Brick-Timbered Block": "Uses 1 Fired Bricks Block (the building block, itself crafted 100 at a time), not loose Fired Bricks. The pre-1.0 data marked this as suspicious; the 1.0 data confirms it.",
    "Well Block": "Odd: a Kindlewastes (tier 4) block that now takes plain Stone instead of Sandstone, the opposite of 1.0's 'use the biome's stone' change. The site's 1.0 diff confirms it.",
    "Fertile Altered Dirt": "Same recipe as Fertile Cinder's Cradle Dirt (Cinder Rock 1, Basalt 1, Cinder's Cradle Dirt 8). Two separate items in the game data; what sets them apart in game isn't known.",
    "Fertile Cinder's Cradle Dirt": "Same recipe as Fertile Altered Dirt (Cinder Rock 1, Basalt 1, Cinder's Cradle Dirt 8). Two separate items in the game data; what sets them apart in game isn't known.",
    "Ectoplasm Block": "Tier conflict: Keen's 1.0 changelog (as quoted on enshrouded.tools/1-0) says it is 'now a tier 2 building material', but the site's building-blocks table puts it in tier 3, Nomad Highlands.",
    "Blackmire Rubble": "The pre-1.0 wiki said it had no recipe, unlike the other biome rubbles, and the site's (Early Access) About blurb says the same, but the 1.0 data has a Grinding Stones recipe. It isn't in the site's changed-recipe list, so it is probably one of 1.0's 617 new recipes.",
}

items = []
gathered = {}      # slug -> (name, catalogueName, old, isNew) for materials with no recipe
excluded = []
unmatched = []
for slug, info in items_raw.items():
    is_new = (info["name"] or slug) in new_item_names
    name = DISPLAY.get(slug) or info["name"] or slug
    cat_name = CAT_BY_NORM.get(norm(name))
    if name in NOT_MATERIALS:
        excluded.append(name)
        continue
    if cat_name is None and not is_new:
        unmatched.append(name)
    r = pick_primary(info)
    o = old.get(cat_name) if cat_name else None
    if r is None:
        gathered[slug] = (name, cat_name, o, is_new)
        continue
    sr = split_recipe(r)
    kv = info.get("kv", {})
    category = CATEGORY_OF.get(cat_name) or NEW_CATEGORY.get(name) or "Soil & terrain"
    ch = diff_old(o, r)
    site_diff = changed_recipes.get((name, r["crafter"]))
    flags = []
    entry = {
        "name": name,
        "category": category,
        "tier": TIER_FIX.get(name) or TIER.get(name),
        "level": int(kv["Item level"]) if kv.get("Item level", "").isdigit() else None,
        "rarity": kv.get("Rarity"),
        "station": sr["station"],
        "crafter": sr["crafter"],
        "requires": sr["requires"],
        "makes": r["makes"],
        "craftTime": r["time"],
        "inputs": inputs_of(r),
        "stackSize": int(kv["Stack size"]) if kv.get("Stack size", "").isdigit() else None,
        "confidence": "likely-1.0",
        "catalogueName": cat_name if cat_name and cat_name != name else None,
        "changes1_0": ch or None,
        "recipeChanged1_0": site_diff,
        "renamedFrom": renamed.get(name),
        "newIn1_0": bool(is_new),
    }
    others = [x for x in info["recipes"] if x is not r]
    if others:
        entry["otherRecipes"] = [dict(split_recipe(x), makes=x["makes"], time=x["time"], inputs=inputs_of(x))
                                 for x in others]
    get = where_lines(info)
    extra_src = [g for g in get if g != r["crafter"]]
    if extra_src:
        entry["alsoFrom"] = extra_src[:6]
    if r.get("makes_item") and r["makes_item"] != name and slug not in DISPLAY:
        flags.append(f"Recipe output is named '{r['makes_item']}', not '{name}'.")
    real_ch = [c for c in ch if "slot takes any of" not in c and not c.startswith("Input renamed")]
    # (an 'Any ...' slot where the wiki named one option, or the Fired Brick rename, is not flagged)
    if real_ch and o is not None and o.get("craftable") and not site_diff:
        flags.append("Differs from the pre-1.0 wiki recipe, but the site's diff of the last Early Access build "
                     "against 1.0 lists no change to it: the wiki was probably stale or wrong before 1.0.")
    if site_diff and o is not None and not ch:
        flags.append("The site's 1.0 diff lists a change, but the 1.0 recipe matches the pre-1.0 wiki recipe, "
                     "so the wiki already had the 1.0 numbers.")
    if name in EXTRA_FLAGS:
        flags.append(EXTRA_FLAGS[name])
    if flags:
        entry["flags"] = flags
    srcs = [info["url"]]
    if name in TIER:
        srcs.append(BLOCKS_URL)
    if site_diff or is_new or entry["renamedFrom"]:
        srcs.append(CHANGELOG_URL)
    entry["sources"] = srcs
    items.append(entry)

def no_where_note(slug, info):
    """Note for a page with no 'Where to get it' line: map count and droppers, if shown."""
    bits = []
    fc = find_count(slug)
    if fc:
        bits.append(f"the site's map shows {fc}")
    drop = info.get("Dropped by") or []
    if drop and drop[0].isdigit():
        names = drop[1::2][:3]
        bits.append(f"dropped by {drop[0]} enemies (e.g. {', '.join(names)})")
    return "No 'Where to get it' line on enshrouded.tools" + ("; " + "; ".join(bits) if bits else "") + "."


def wiki_where(notes):
    """The gathering-location sentence from a pre-1.0 catalogue note (tools/blocks-src/recipes.json)."""
    m = re.search(r"pickaxe\. (.+?\.)(?= |$)", notes) or re.search(r"obtaining column says: (.+?\.)(?= |$)", notes)
    return m.group(1) if m else None


GATHERED_NOTES = {
    "Gold Coins": "1.0 changelog (enshrouded.tools/1-0): found in chests all over Embervale and traded for vanity items; now part of the Springlands material set.",
    "Revelwood Stone": "1.0 recipes for Citywall Block, Weathered Stone Block and Revelwood Rubble now take it, and with no recipe it has to be dug or mined (no 'How to craft' section on its page, and the site's terraforming table lists it as a Hard terrain material).",
}

# ---- resources: every input down to raw materials (primary recipes) ----
resources = {}
groups = {}
queue = []
for slug, info in items_raw.items():
    if info["name"] in NOT_MATERIALS:
        continue
    for rr in info["recipes"]:
        queue.extend(rr["inputs"])
seen = set()
while queue:
    inp = queue.pop(0)
    if "anyOf" in inp:
        groups[inp["item"]] = inp["anyOf"]
        continue
    slug = inp["slug"]
    if slug in seen:
        continue
    seen.add(slug)
    key = inp["item"]                      # keyed by the name recipes use
    info = res_raw.get(slug) or items_raw.get(slug)
    if info is None:
        resources[key] = {"source": None, "kind": "unknown", "recipe": None,
                          "note": "Page not scraped.", "sources": [SITE + "/items/" + slug]}
        continue
    get = where_lines(info)
    source = get[0] if get else None
    primary = pick_primary(info)
    entry = {}
    notes = []
    if primary:
        sp = split_recipe(primary)
        entry["kind"] = "crafted"
        if not source:
            source = primary["crafter"]
            entry["sourceInferred"] = True
        entry["source"] = source
        rec = {"station": sp["station"], "crafter": sp["crafter"], "requires": sp["requires"],
               "makes": primary["makes"], "time": primary["time"], "inputs": inputs_of(primary)}
        rec["changed1_0"] = changed_recipes.get((info["name"], primary["crafter"]))
        # compare with the pre-1.0 wiki intermediate recipe at the same station, if any
        oi = old_inter.get(info["name"]) or old_inter.get(re.sub(r"s$", "", info["name"]))
        if oi:
            cands = [x for x in oi["recipes"] if (x.get("station") or None) == (sp["station"] or None)]
            ox = cands[0] if cands else None
            if ox:
                d = diff_recipe(ox["inputs"], ox.get("makes"), ox.get("station"), ox.get("crafter"), primary,
                                compare_crafter=False)
                rec["changes1_0"] = d or None
            else:
                notes.append("Pre-1.0 wiki recipe stations: " + ", ".join(sorted({str(x.get('station')) for x in oi['recipes']})) + ".")
        entry["recipe"] = rec
        queue.extend(primary["inputs"])
    else:
        entry["kind"] = "gathered"
        entry["source"] = source
        entry["recipe"] = None
        if not get:
            notes.append(no_where_note(slug, info))
    if len(get) > 1:
        entry["alsoFrom"] = get[1:6]
    others = [x for x in info["recipes"] if x is not primary]
    if others:
        if len(others) <= 4:
            entry["otherRecipes"] = [dict(split_recipe(x), makes=x["makes"], time=x["time"], inputs=inputs_of(x))
                                     for x in others]
        else:
            entry["otherRecipes"] = (f"{len(others)} other recipes (e.g. {others[0]['crafter']}: "
                                     f"{fmt_inputs(others[0]['inputs'])})")
    if not get and not notes:
        notes.append("No 'Where to get it' line on enshrouded.tools.")
    if notes:
        entry["note"] = " ".join(notes)
    if info["name"] != key:
        entry["pageName"] = info["name"]
    entry["category"] = info.get("kv", {}).get("Category")
    entry["sources"] = [info["url"]]
    resources[key] = entry

# ---- catalogue (and new) terrain materials with no recipe: gathered only ----
WIKI_HINT = {n: v.get("notes", "") for n, v in old.items()}
gathered_names = []
for slug, (name, cat_name, o, is_new) in gathered.items():
    info = items_raw[slug]
    get = where_lines(info)
    e = resources.get(name, {})
    e.update({"kind": "gathered", "source": get[0] if get else None, "recipe": None})
    if len(get) > 1:
        e["alsoFrom"] = get[1:6]
    notes = []
    if cat_name:
        notes.append("Planner catalogue terrain material; no recipe on enshrouded.tools (1.0 data).")
    if is_new:
        notes.append("New in 1.0 (Cinder's Cradle).")
        e["newIn1_0"] = True
    if not get:
        notes.append(no_where_note(slug, info))
    if o is not None and o.get("craftable"):
        notes.append("FLAG: the pre-1.0 wiki had a recipe for it (" + (o.get("station") or "?") + ": "
                     + fmt_inputs(o.get("inputs", [])) + f", makes {o.get('makes')}); the 1.0 data has none, "
                     "so it looks gathered-only now (the site's About blurb, which quotes Early Access, still "
                     "describes the old recipe).")
    if not get and cat_name:
        hint = wiki_where(WIKI_HINT.get(cat_name, ""))
        if hint:
            notes.append(f"Pre-1.0 wiki: {hint}")
    if name in GATHERED_NOTES:
        notes.append(GATHERED_NOTES[name])
    e["note"] = " ".join(notes)
    if cat_name and cat_name != name:
        e["catalogueName"] = cat_name
    e["category"] = info.get("kv", {}).get("Category")
    e["sources"] = [info["url"]]
    resources[name] = e
    gathered_names.append(name)

resources.setdefault("Water", {"source": None, "kind": "water", "recipe": None,
                               "note": "Water charges, not an inventory item: drawn from base water storage near the crafter.",
                               "sources": [SITE]})
for g, opts in groups.items():
    resources.setdefault(g, {"source": None, "kind": "any-of", "options": opts, "recipe": None,
                             "note": "Recipe slot that accepts any one of the options.", "sources": [SITE]})

# ---- catalogue names with no page at all ----
covered = {norm(i["catalogueName"] or i["name"]) for i in items}
covered |= {norm(v[1] or v[0]) for v in gathered.values()}
missing = [n for n in CATALOGUE if norm(n) not in covered]
for n in missing:
    items.append({"name": n, "category": CATEGORY_OF.get(n, "Soil & terrain"), "station": None, "crafter": None,
                  "requires": [], "makes": None, "inputs": [], "confidence": "unknown", "catalogueName": None,
                  "changes1_0": None, "flags": ["No enshrouded.tools page matched this catalogue name."],
                  "newIn1_0": False, "sources": []})

CAT_ORDER = ["Stone blocks", "Wood blocks", "Luminescent blocks", "Other blocks", "Roof blocks", "Overgrowth", "Roads",
             "Soil & terrain"]
items.sort(key=lambda it: (CAT_ORDER.index(it["category"]), it["newIn1_0"], it["name"]))
for it in items:
    for k in ("tier", "level", "rarity", "recipeChanged1_0", "renamedFrom", "stackSize"):
        if it.get(k) is None:
            it.pop(k, None)

with_recipe = [i for i in items if i["confidence"] != "unknown"]
changed = [i for i in items if i.get("changes1_0") and not i["newIn1_0"]]
new = [i for i in items if i["newIn1_0"]]
new_gathered = [n for n in gathered_names if resources[n].get("newIn1_0")]
cat_gathered = [n for n in gathered_names if not resources[n].get("newIn1_0")]

notes = (
    f"{len(with_recipe)} building materials with a 1.0 recipe ({len(with_recipe) - len(new)} from the planner's 118-entry "
    f"block catalogue, {len(new)} new in 1.0), plus {len(cat_gathered)} catalogue terrain materials and "
    f"{len(new_gathered)} new 1.0 terrain materials that have no recipe and are listed under resources as gathered "
    "(with catalogueName where the names differ). "
    "Source: enshrouded.tools item pages, read from the 1.0 game files (footer: 'Data from game build 25988036'), "
    "cross-checked against the site's building-blocks table (tiers, per-craft yields) and its 1.0 page, which diffs the "
    "last Early Access build (23966345) against 1.0. Every recipe is likely-1.0 (datamined, not checked in game). "
    "changes1_0 compares the 1.0 recipe with the pre-1.0 wiki recipe in tools/blocks-src/recipes.json "
    "('old -> new', '+ item qty' added, '- item qty' dropped); recipeChanged1_0 is the site's own diff against the "
    "last Early Access build. Where the two disagree, the item is flagged: a wiki-only difference means the wiki was "
    "stale or wrong before 1.0. The input 'Fired Brick' is 'Fired Bricks' in 1.0 (a rename, same item). "
    "station is the station the recipe uses (Workbench, Grinding Stones); crafter is null for the player's own "
    "Workbench and the survivor (Farmer) otherwise; requires is [] because no page shows a requirement. "
    "Yields: blocks 100, roofs 50, roads, soils, fertile dirts and rubbles 10, all read from each page's 'Makes' line. "
    "tier is the site's building tier (biome); roads and soils have none. Rubbles are timed Grinding Stones recipes (70-80s). "
    "Resources follow each input's primary recipe (the one its 'Where to get it' line names) down to raw materials; "
    "alternatives are in otherRecipes. Resource recipes carry the site's diff (changed1_0) and, where the pre-1.0 "
    "intermediates list has the same station, a wiki comparison (changes1_0). The site's 'About' blurbs quote Early "
    "Access and are ignored (e.g. Revelwood Stone's still says Workbench, Blackmire Rubble's says no recipe). "
    "The site also lists 5 Overgrowth paints (Ivy, Climbing Rose, Mycelium, Wisteria, Underwater Overgrowth; Farmer, "
    "100 per craft) that are not in the catalogue and not new in 1.0, so they are left out. "
    f"Left out as not hammer materials: {', '.join(excluded)} (new 1.0 furniture props, Decoration Workbench)."
)
out = {"fetched": "2026-10-20", "notes": notes, "items": items, "resources": dict(sorted(resources.items()))}
json.dump(out, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("items", len(items), "with recipe", len(with_recipe), "new", len(new), "changed", len(changed))
print("gathered catalogue", len(cat_gathered), cat_gathered)
print("gathered new", new_gathered)
print("missing", missing, "unmatched", unmatched, "excluded", excluded)
print("resources", len(resources))
for i in changed:
    print(" ", i["name"], "|", i["changes1_0"], "| site:", i.get("recipeChanged1_0"))
