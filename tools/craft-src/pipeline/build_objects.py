"""Build base-objects.json (chests, crafting stations, base furniture, Sparkworks parts) from scraped
enshrouded.tools data.

Usage: python -I build_objects.py <raw_objects.json> <cache_dir> <tools-1-0.txt> <app1.js> <out.json>

<raw_objects.json> comes from scrape_objects.py, <tools-1-0.txt> is the text of enshrouded.tools/1-0 (the site's
diff of the last Early Access build against 1.0, also used by build.py), and <app1.js> is the planner source whose
LIBRARY holds the pre-1.0 wiki notes on chests and stations (compared here into changes1_0).
"""
import html
import json
import re
import sys

RAW, CACHE, CHANGELOG, APP1, OUT = sys.argv[1:6]
raw = json.load(open(RAW, encoding="utf-8"))
items_raw, res_raw = raw["items"], raw["resources"]
by_slug = dict(res_raw)
by_slug.update(items_raw)

SITE = "https://www.enshrouded.tools"
CHANGELOG_URL = SITE + "/1-0"
SPARKWORKS_URL = SITE + "/sparkworks"
HUSBANDRY_URL = SITE + "/animal-husbandry"
NPC_CRAFTERS = {"Alchemist", "Collector", "Hunter", "Blacksmith", "Carpenter", "Farmer", "Bard", "Fisher",
                "Ancient Researcher", "Lunar New Year Trader"}
# 'Where to get it' wording that names a recipe header differently
SOURCE_ALIAS = {"Manual Crafting": "By hand", "Huntress": "Hunter"}
# No 'Where to get it' line, but the About text says they drop or are picked up; the recipe is a side route.
GATHERED_FIRST = {"Twigs", "Animal Fur"}

# ---- what to output: (slug, category, libraryType, placeholder) ----
CH, MC, ST, BF, SW = "Chests", "Magic chests", "Crafting stations", "Base & furniture", "Sparkworks"
CATALOG = [
    ("tiny-chest", CH, "chest-tiny", None), ("small-chest", CH, "chest-small", None),
    ("wooden-chest", CH, "chest-wooden", None), ("medium-chest", CH, "chest-medium", None),
    ("large-chest", CH, "chest-large", None), ("silver-chest", CH, "chest-silver", None),
    ("huge-chest", CH, "chest-huge", None),
    ("small-magic-chest", MC, "mchest-small", None), ("medium-magic-chest", MC, "mchest-medium", None),
    ("large-magic-chest", MC, "mchest-large", None), ("huge-magic-chest", MC, "mchest-huge", None),
    ("enormous-magic-chest", MC, "mchest-enormous", None), ("quick-stack-station", MC, "quickstack", None),
    ("large-quick-stack-station", MC, None, None),
    ("workbench", ST, "workbench", None),
    ("forge", ST, "forge", None), ("charcoal-kiln", ST, "charcoal-kiln", None), ("smelter", ST, "smelter", None),
    ("blast-furnace", ST, "blast-furnace", None), ("smithing-tools", ST, "smithing-tools", None),
    ("alchemy-station", ST, "alchemy", None), ("grinding-stones", ST, "grinding-stones", None),
    ("mortar", ST, "mortar", None), ("laboratory", ST, "laboratory", None),
    ("kiln", ST, "kiln", None), ("table-saw", ST, "table-saw", None), ("masonry-tools", ST, "masonry-tools", None),
    ("tanning-station", ST, "tannery", None), ("drying-rack", ST, "drying-rack", None),
    ("hand-spindle", ST, "hand-spindle", None), ("loom", ST, "loom", None),
    ("spinning-wheel", ST, "spinning", None), ("spinning-machine", ST, "spinning-machine", None),
    ("seedbed", ST, "seedbed", None), ("cooking-station", ST, "cooking-station", None),
    ("oven", ST, "oven", None), ("kitchen", ST, "kitchen", None),
    ("sparkworks-workbench", ST, None, None), ("decoration-workbench", ST, None, None),
    ("flame-altar", BF, "altar", None),
    ("crude-wooden-bed", BF, "bed", "Bed"), ("wooden-bed", BF, "bed", "Bed"),
    ("ornate-wooden-bed", BF, "bed", "Bed"), ("boreal-wood-bed", BF, "bed", "Bed"),
    ("kingsize-bed", BF, "bed2", "Double bed"), ("large-boreal-wood-bed", BF, "bed2", "Double bed"),
    ("crude-mattress", BF, "mattress", "Crude mattress"),
    ("campfire", BF, "campfire", "Campfire"),
    ("wooden-bathtub", BF, "bathtub", "Bathtub"), ("bronze-bathtub", BF, "bathtub", "Bathtub"),
    ("granite-stone-bathtub", BF, "bathtub", "Bathtub"), ("maritime-bathtub", BF, "bathtub", "Bathtub"),
    ("farm-animal-pillow", BF, "pen", "Animal pen"), ("big-farm-animal-pillow", BF, "pen", "Animal pen"),
    ("crude-wooden-fence-i", BF, "pen", "Animal pen"), ("crude-wooden-gate-i", BF, "pen", "Animal pen"),
    ("goat-feeder", BF, "trough", "Trough"), ("yak-feeder", BF, "trough", "Trough"),
    ("bird-feeder", BF, "trough", "Trough"), ("water-trough", BF, "trough", "Trough"),
    ("wooden-ladder", BF, "ladder", "Ladder"), ("bamboo-ladder", BF, "ladder", "Ladder"),
    ("standing-torch", BF, "light", "Light / lantern"), ("wall-torch", BF, "light", "Light / lantern"),
    ("standing-lantern", BF, "light", "Light / lantern"),
    ("crude-wooden-table", BF, "table", "Table"), ("wooden-table", BF, "table", "Table"),
    ("polished-wooden-table", BF, "table", "Table"), ("stone-table", BF, "table", "Table"),
    ("lever", SW, "lever", "Lever / switch"), ("lever-with-indicator", SW, "lever", "Lever / switch"),
    ("switch-button", SW, "lever", "Lever / switch"), ("push-button", SW, "lever", "Lever / switch"),
    ("pressure-plate", SW, "plate", "Pressure plate"),
    ("light", SW, "light", "Light / lantern"),
    ("shootable-button", SW, None, None), ("goalpost", SW, None, None),
    ("lightning-trap", SW, None, None), ("spike-trap", SW, None, None),
    ("trapdoor-wood-2m", SW, None, None), ("trapdoor-wood-4m", SW, None, None),
    ("trapdoor-stone-2m", SW, None, None), ("trapdoor-stone-4m", SW, None, None),
    ("trapdoor-metal-2m", SW, None, None), ("trapdoor-metal-4m", SW, None, None),
    ("sparkworks-switchbox", SW, None, None), ("sparkworks-tool", SW, None, None),
    ("spawner", SW, None, None), ("sparkworks-trigger-zone", SW, None, None),
]

# Informational notes (not things to check in game).
NOTES = {
    "large-quick-stack-station": "Not in the planner library: the bigger Quick Stack Station (24 m reach against 16 m). Not new in 1.0.",
    "sparkworks-workbench": "Not in the planner library. Makes the 18 Sparkworks parts and the Sparkworks Tool. Sparkworks opens with the Carpenter's quest Contraptions And Mechanisms (enshrouded.tools/sparkworks).",
    "decoration-workbench": "Not in the planner library. Needed here for the Water Trough; it makes decorations with the Carpenter's help.",
    "farm-animal-pillow": "There is no pen item: a pen is fences and a gate round a bed and a feeder. This is the bed for goats, Fae Deer, Hophares and birds; an animal looks for one within 50 m that counts as sheltered at 20% cover (enshrouded.tools/animal-husbandry).",
    "big-farm-animal-pillow": "Bed for Yaks and Dune Armadillos (enshrouded.tools/animal-husbandry).",
    "crude-wooden-fence-i": "The cheapest Workbench fence, as a stand-in for pen fencing. Fences and gates come in many styles.",
    "crude-wooden-gate-i": "The cheapest Workbench gate, for a pen.",
    "goat-feeder": "Feeds Common and Frizzy Goats. Each farm animal species has its own food and feeder; both goats share this one and both birds share the Bird Feeder.",
    "yak-feeder": "Feeds Yaks.",
    "bird-feeder": "Feeds Flightless Redtails and Round-Billed Sailers.",
    "water-trough": "Decoration only ('a decorative object'); animals eat from their feeders.",
    "standing-torch": "The basic placed light at the Workbench. (The hand-held Torch is a weapon-slot item.)",
    "light": "The Sparkworks light. Torches, braziers and the other 96 lights also work in Sparkworks.",
    "lever": "Holds its state (ON/OFF) until used again.",
    "lever-with-indicator": "A lever with a light that shows the ON state.",
    "switch-button": "Holds its state until pressed again, with an indicator light.",
    "push-button": "Sends a short ON signal, then switches off.",
    "pressure-plate": "Stays on while something stands on it.",
    "shootable-button": "Flips each time an arrow or spell hits it.",
    "sparkworks-switchbox": "Opens a Sparkworks graph where it stands; removing it keeps the graph.",
    "sparkworks-tool": "The wiring tool (Tools and gear). The 1.0 quest Contraptions And Mechanisms sends you to a Night Sanctum for the first one.",
    "spinning-machine": "Takes a Spinning Wheel as an input, so building it uses up the wheel.",
    "masonry-tools": "The Carpenter uses it and his quest Finding Masonry Tools gives the first one, but the recipe for more is the Blacksmith's (with a Forge).",
}
# Not crafted anywhere: how they're obtained instead.
NOT_CRAFTED = {
    "tiny-chest": "Unknown. enshrouded.tools has no recipe and no 'Where to get it' line for it in 1.0, and it isn't among the Workbench's 166 recipes.",
    "spawner": "Not crafted: picked from the Sparkworks Tool's own menu and placed directly, visible only while holding the tool (enshrouded.tools/sparkworks).",
    "sparkworks-trigger-zone": "Not crafted: picked from the Sparkworks Tool's own menu and placed directly, visible only while holding the tool (enshrouded.tools/sparkworks).",
}
FLAGS = {
    "tiny-chest": ["Check in game whether Tiny Chests can still be built. The site's 1.0 diff counts 35 removed recipes without listing them, so its "
                   "recipe may have been cut. The Small Chest's cheap by-hand recipe (Any wood x1, String x1) looks like the in-place upgrade from a Tiny Chest."],
    "kingsize-bed": ["Its page calls it 'a decorative object to design and beautify your home', not a bed like the single beds' text, though it gives Bed comfort 6. Check in game that it works as a bed."],
    "large-boreal-wood-bed": ["Its page calls it 'a decorative object to design and beautify your home', not a bed like the single beds' text, though it gives Bed comfort 7. Check in game that it works as a bed."],
}
# 1.0 changes that Keen's own notes (on the site's 1.0 page) give for a kind of object rather than one recipe.
KEEN_CHEST = "Keen's 1.0 notes: storage chests can be upgraded or turned into magic chests without emptying them, and chests can be named."
KEEN_BED = "Keen's 1.0 notes: you can fast travel from a bed (which beds count isn't stated)."
KEEN = {"flame-altar": ["Keen's 1.0 notes: your first level-up now comes from placing your first Flame Altar."],
        "table-saw": ["The planner's pre-1.0 note puts the Circular Sawblades at Thornhold; in 1.0 the quest goes to Thornhold and then the "
                      "Fawnsong Frontier Scavenger camp, where the sawblades are, and the Blacksmith can also make them (Iron Bars x2, Charcoal x6, with a Forge)."]}
# Quest rewards that are a part of a station: the quest belongs to the station too.
QUEST_PART_OF = {"cauldron": ["alchemy-station"], "crucible": ["smelter"], "scientific-instruments": ["laboratory"],
                 "almanac-of-plants-and-seedlings": ["oven"], "common-goat": ["goat-feeder", "farm-animal-pillow"]}
SIGNALS = {"Sends", "Takes", "Takes and sends", "none"}

def page_lines(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    b, e = t.find("<main"), t.find("</main>")
    m = re.sub(r"<!--.*?-->", "", t[b:e], flags=re.S)
    m = html.unescape(re.sub(r"<[^>]+>", "\n", m))
    return [l.strip() for l in m.split("\n") if l.strip()]


def about(info):
    a = info.get("sections", {}).get("About")
    if a:
        return re.sub(r"\s+([,.])", r"\1", " ".join(a))
    return None


# ---- 1.0 changelog ----
CL = open(CHANGELOG, encoding="utf-8").read().split("\n")
_ni = [i for i, l in enumerate(CL) if l == "New items"][-1]
_nq = next(i for i in range(_ni, len(CL)) if CL[i] == "New quests, lore and places")
NEW_NAMES = {l for l in CL[_ni:_nq] if not re.search(r"\(\d+\)$", l)}


def _is_diff(x):
    return "→" in x or x.startswith("+ ") or x.startswith("- ")


changed_recipes = {}
_a = next(i for i, l in enumerate(CL) if l.startswith("Changed recipes ("))
_b = next(i for i in range(_a + 1, len(CL)) if CL[i].startswith("Changed skill tree nodes ("))
i = _a + 3
while i < _b:
    name, crafter = CL[i], CL[i + 1] if i + 1 < _b else None
    j, diff = i + 2, []
    while j < _b and _is_diff(CL[j]):
        diff.append(CL[j])
        j += 1
    if diff:
        changed_recipes.setdefault((name, crafter), []).extend(diff)
        i = j
    else:
        i += 1
_s = next(i for i, l in enumerate(CL) if l.startswith("Items with new stats ("))
STAT_SECTION = CL[_s + 1:_a]
STAT_LINE = re.compile(r"→|^New: |^No longer |^Bonuses|^Renamed from |^Description reworded|^Drops as |^Level ")


def stat_changes(name):
    out = []
    for k, l in enumerate(STAT_SECTION):
        if l == name:
            for x in STAT_SECTION[k + 1:k + 12]:
                if STAT_LINE.search(x):
                    out.append(x)
                else:
                    break
    return out


def tidy_diff(diff):
    """Fold '+ N X' / '- N Y' pairs that are a rename (Fired Brick -> Fired Bricks) into one line."""
    plus = {m.group(2): m.group(1) for m in (re.match(r"\+ (\d+) (.+)", d) for d in diff) if m}
    out, used = [], set()
    for d in diff:
        m = re.match(r"- (\d+) (.+)", d)
        if m and m.group(2) + "s" in plus and plus[m.group(2) + "s"] == m.group(1):
            out.append(f"{m.group(2)} renamed {m.group(2)}s (same item, same {m.group(1)})")
            used.add(m.group(2) + "s")
    for d in diff:
        m = re.match(r"([+-]) (\d+) (.+)", d)
        if m and (m.group(3) in used or (m.group(1) == "-" and m.group(3) + "s" in used)):
            continue
        out.append(d)
    return out


# ---- planner LIBRARY (pre-1.0 wiki notes) ----
LIB = {}
for line in open(APP1, encoding="utf-8"):
    m = re.search(r"\{ type: '([^']+)',\s*name: '([^']+)'", line)
    if not m:
        continue
    d = {"type": m.group(1), "name": m.group(2)}
    for k in ("by", "role", "recipe"):
        mm = re.search(k + r": (['\"])(.*?)\1", line)
        d[k] = mm.group(2) if mm else None
    LIB[d["type"]] = d


def parse_planner_recipe(txt):
    out = {}
    for part in [p.strip() for p in (txt or "").split(",") if p.strip()]:
        m = re.match(r"(.+?) ×(\d+)$", part)
        name, qty = (m.group(1), int(m.group(2))) if m else (re.sub(r"\s*\(.*\)$", "", part), 1)
        out[name.strip()] = qty
    return out


def fmt(inputs):
    return ", ".join(f"{k} ×{v}" for k, v in inputs.items())


GENERALISED = {"Wood Logs": "Any wood", "Sand": "Any sand", "Stone": "Any stone"}


def is_quest_note(by):
    return by.startswith("Quest") or "quest" in by or by == "Forging the Path"


def compare_planner(lib, inputs, rec, flags, cl_diff):
    """changes1_0 lines comparing the planner's pre-1.0 wiki note (LIBRARY) with the 1.0 recipe."""
    out = []
    old = parse_planner_recipe(lib.get("recipe"))
    new = {i["item"]: i["qty"] for i in inputs}
    by = lib.get("by") or ""
    who = rec["crafter"] or rec["station"] or "by hand"
    if not inputs:
        if old:
            out.append(f"No recipe in the 1.0 data. The planner's pre-1.0 wiki note: {by}, {fmt(old)}.")
        return out
    if not old:
        if is_quest_note(by):
            out.append(f"The planner's pre-1.0 note names only a quest ('{by}') and no recipe; 1.0 also has a recipe at the {who} (see quest for how the first one comes).")
        elif by and by not in (who, "Hand crafting"):
            out.append(f"The planner's pre-1.0 note says '{by}' with no recipe; the 1.0 recipe is at the {who}.")
        else:
            out.append(f"The planner had no recipe for it (pre-1.0 note: '{by}').")
        return out
    if by != who and not (by == "Hand crafting" and who == "by hand") and not is_quest_note(by):
        out.append(f"The planner's pre-1.0 note says '{by}'; the 1.0 recipe is at the {who}.")
    old_n = {("Fired Bricks" if k == "Fired Brick" else k): v for k, v in old.items()}
    gen = []
    for k, g in GENERALISED.items():
        if k in old_n and g in new and k not in new and old_n[k] == new[g]:
            old_n[g] = old_n.pop(k)
            gen.append(f"{k} → {g}")
    if old_n == new:
        if gen:
            out.append("Same recipe as the planner's pre-1.0 note, except " + ", ".join(gen) + " (any type now counts).")
    elif all(new.get(k) == v for k, v in old_n.items()):
        out.append(f"The planner's pre-1.0 note listed only {fmt(old)}; the full 1.0 recipe is {fmt(new)}.")
    else:
        out.append(f"Recipe differs from the planner's pre-1.0 wiki note: {fmt(old)} → {fmt(new)}.")
        if not cl_diff:
            flags.append("The recipe differs from the planner's pre-1.0 wiki note, but the 1.0 changelog shows no change for it, "
                         "so the wiki was probably stale or wrong before 1.0.")
    if "Fired Brick" in old and not any("Fired Brick" in d for d in cl_diff):
        out.append("'Fired Brick' is called 'Fired Bricks' in 1.0 (same item).")
    return out


# ---- recipe helpers ----
def split_recipe(r):
    c = r["crafter"]
    if c in NPC_CRAFTERS:
        return {"station": r["needs"], "crafter": c, "requires": []}
    if c == "By hand":
        return {"station": None, "crafter": None, "requires": [r["needs"]] if r["needs"] else []}
    return {"station": c, "crafter": None, "requires": [r["needs"]] if r["needs"] else []}


def water_of(r):
    for h in r.get("header_text", []):
        m = re.match(r"(\d+) water charges?", h)
        if m:
            return int(m.group(1))
    return None


def inputs_of(r):
    out = []
    for i in r["inputs"]:
        d = {"item": i["item"], "qty": i["qty"]}
        if "anyOf" in i:
            d["anyOf"] = i["anyOf"]
        out.append(d)
    w = water_of(r)
    if w:
        out.append({"item": "Water", "qty": w, "waterCharges": True})
    return out


def comfort_of(kv):
    for k, v in kv.items():
        if k.startswith("Comfort - "):
            t = k[len("Comfort - "):].replace("Category ", "")
            return {"type": t, "value": int(v) if v.isdigit() else v}
    return None


def found_at(info):
    f = info.get("sections", {}).get("Where to find it")
    if not f:
        return None
    return f[0] + (": " + "; ".join(f[1:6]) if len(f) > 1 else "")


UPGRADE_NOTE = {
    "small-chest": "Not labelled on the site; probably the 1.0 in-place upgrade of a placed Tiny Chest.",
    "medium-chest": "Not labelled on the site; probably the 1.0 in-place upgrade of a placed Small Chest.",
    "large-chest": "Not labelled on the site; probably the 1.0 in-place upgrade of a placed Medium Chest.",
    "huge-chest": "Not labelled on the site; probably the 1.0 in-place upgrade of a placed Large Chest.",
    "enormous-magic-chest": "Not labelled on the site; probably the 1.0 in-place upgrade of a placed Huge Magic Chest.",
}


def other_recipe_note(slug, r, k):
    if slug in UPGRADE_NOTE:
        return UPGRADE_NOTE[slug]
    if "magic-chest" in slug:
        plain = slug.replace("-magic", "")
        if len(r["inputs"]) <= 2:
            return f"Not labelled on the site; probably turns a placed {plain.replace('-', ' ').title()} into this magic chest in place (the magic part of the main recipe only)."
        return "Not labelled on the site; the main recipe with the plain chest's own materials instead of the chest, probably the in-place upgrade from the magic chest one size down."
    return None


# ---- Sparkworks signal types (the parts table on enshrouded.tools/sparkworks) ----
SIGNAL = {}
_sp = page_lines(CACHE + "/pg-sparkworks.html")
for k in range(len(_sp) - 1):
    if _sp[k + 1] in SIGNALS and _sp[k] not in SIGNAL and _sp[k] not in ("Signal", "Type"):
        SIGNAL[_sp[k]] = _sp[k + 1]

# ---- quests that introduce a station (or hand out its key part) ----
QUEST_FOR = {}
for q in raw.get("quests", {}).values():
    for rw in q["rewards"]:
        for target in [rw] + QUEST_PART_OF.get(rw, []):
            QUEST_FOR.setdefault(target, []).append(q)

# ---- items ----
items = []
for slug, cat, lib_type, placeholder in CATALOG:
    it = items_raw[slug]
    kv = it["kv"]
    name = it["name"]
    recs = it["recipes"]
    r = recs[0] if recs else None
    rec = split_recipe(r) if r else {"station": None, "crafter": None, "requires": []}
    flags = list(FLAGS.get(slug, []))
    changes = []
    srcs = [it["url"]]
    cl_diff = []
    if r:
        for (n, c), d in changed_recipes.items():
            if n == name:
                cl_diff.extend(d)
    if cl_diff:
        changes.append("1.0 changelog: " + "; ".join(tidy_diff(cl_diff)) + ".")
    stats = stat_changes(name)
    changes.extend(stats)
    if cl_diff or stats:
        srcs.append(CHANGELOG_URL)
    lib = LIB.get(lib_type) if lib_type else None
    inputs = inputs_of(r) if r else []
    if lib and cat in (CH, MC, ST):
        changes.extend(compare_planner(lib, inputs, rec, flags, cl_diff))
    if len(recs) > 1 and cat in (CH, MC):
        changes.append(KEEN_CHEST)
        srcs.append(CHANGELOG_URL)
    if placeholder in ("Bed", "Double bed", "Crude mattress"):
        changes.append(KEEN_BED)
        srcs.append(CHANGELOG_URL)
    if slug in KEEN:
        changes.extend(KEEN[slug])
        if any(x.startswith("Keen's") for x in KEEN[slug]):
            srcs.append(CHANGELOG_URL)
    entry = {"name": name, "category": cat}
    if kv.get("Item level", "").isdigit():
        entry["level"] = int(kv["Item level"])
    entry["rarity"] = kv.get("Rarity")
    entry.update({
        "station": rec["station"],
        "crafter": rec["crafter"],
        "requires": rec["requires"],
        "makes": r["makes"] if r else None,
        "craftTime": r["time"] if r else None,
        "inputs": inputs,
    })
    if len(recs) > 1:
        entry["otherRecipes"] = []
        for k, x in enumerate(recs[1:]):
            o = dict(split_recipe(x), makes=x["makes"], inputs=inputs_of(x))
            note = other_recipe_note(slug, x, k)
            if note:
                o["note"] = note
            entry["otherRecipes"].append(o)
    if lib_type:
        entry["libraryType"] = lib_type
    if placeholder:
        entry["placeholder"] = placeholder
    if lib and lib.get("role") and re.match(r"\d+ slots", lib["role"]):
        entry["slots"] = int(lib["role"].split()[0])
    c = comfort_of(kv)
    if c:
        entry["comfort"] = c
    fa = found_at(it)
    if fa:
        entry["foundAt"] = fa
    if slug in QUEST_FOR:
        entry["quest"] = [{"name": q["name"], "givenBy": q.get("givenBy"), "summary": q.get("summary"), "url": q["url"]}
                          for q in QUEST_FOR[slug]]
        srcs.extend(q["url"] for q in QUEST_FOR[slug])
    if slug in NOT_CRAFTED:
        entry["obtained"] = NOT_CRAFTED[slug]
    if slug in NOTES:
        entry["note"] = NOTES[slug]
    if cat == SW and name in SIGNAL:
        entry["signal"] = SIGNAL[name]
    if cat == SW or slug == "sparkworks-workbench":
        srcs.append(SPARKWORKS_URL)
    if placeholder in ("Animal pen", "Trough"):
        srcs.append(HUSBANDRY_URL)
    entry["confidence"] = "likely-1.0" if r else "unknown"
    entry["newIn1_0"] = name in NEW_NAMES
    entry["changes1_0"] = changes or None
    if flags:
        entry["flags"] = flags
    entry["sources"] = list(dict.fromkeys(srcs))
    items.append(entry)

# ---- resources: every input down to raw materials (primary recipe chain) ----
def primary_of(info):
    get = info.get("sections", {}).get("Where to get it")
    source = get[0] if get else None
    recipes = info["recipes"]
    if source:
        want = SOURCE_ALIAS.get(source, source)
        p = next((x for x in recipes if x["crafter"] == want), None)
        if p is None:
            p = next((x for x in recipes if want.startswith(x["crafter"] + " or ")), None)
        return source, p, False
    if info["name"] in GATHERED_FIRST:
        return None, None, False
    return None, (recipes[0] if recipes else None), bool(recipes)


# Notes where the site's About blurb (Early Access text) contradicts the 1.0 data.
RES_NOTE = {
    "Revelwood Stone": "No 'Where to get it' line; the site's map shows 1,867 in Embervale. It's a Revelwood terrain material with no recipe in 1.0 "
                       "(the site's About blurb, which quotes Early Access, still describes a Workbench recipe from Stone and Revelwood Dirt).",
}
resources, groups = {}, {}
water = any(i.get("waterCharges") for it in items for i in it["inputs"])
queue = [i for slug, *_ in CATALOG for r in items_raw[slug]["recipes"] for i in r["inputs"]]
queue += [{"item": "Archaic Essence I", "slug": "archaic-essence-i"}]
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
    info = by_slug.get(slug)
    if info is None:
        resources[inp["item"]] = {"source": None, "kind": "unknown", "recipe": None, "sources": [SITE + "/items/" + slug]}
        continue
    source, primary, inferred = primary_of(info)
    entry = {}
    if primary:
        sr = split_recipe(primary)
        entry["kind"] = "crafted"
        if not source:
            source = primary["crafter"]
        entry["source"] = source
        entry["recipe"] = {"station": sr["station"], "crafter": sr["crafter"], "requires": sr["requires"],
                           "makes": primary["makes"], "time": primary["time"], "inputs": inputs_of(primary)}
        queue.extend(primary["inputs"])
        water = water or bool(water_of(primary))
    else:
        entry["kind"] = "gathered"
        entry["source"] = source
        entry["recipe"] = None
    others = [x for x in info["recipes"] if x is not primary]
    if others:
        if len(others) <= 4:
            entry["otherRecipes"] = [dict(split_recipe(x), makes=x["makes"], time=x["time"], inputs=inputs_of(x)) for x in others]
        else:
            entry["otherRecipes"] = f"{len(others)} other recipes (e.g. {others[0]['crafter']}: {', '.join(i['item'] for i in others[0]['inputs'])})"
    if inferred:
        entry["sourceInferred"] = True
    if not info.get("sections", {}).get("Where to get it"):
        ab = about(info)
        fa = found_at(info)
        note = ab or "No 'Where to get it' line on enshrouded.tools."
        if fa and not ab:
            note += f" Where to find it: {fa}."
        entry["note"] = RES_NOTE.get(info["name"], note[:300])
    if primary:
        d = [x for (n, c), x in changed_recipes.items() if n == info["name"] and c == primary["crafter"]]
        entry["recipe"]["changed1_0"] = tidy_diff(d[0]) if d else None
    entry["category"] = info["kv"].get("Category")
    if info["name"] != inp["item"]:
        entry["pageName"] = info["name"]
    entry["sources"] = [info["url"]]
    resources[inp["item"]] = entry          # keyed by the name recipes use ('Indigo Plant', page 'Indigo Plant (material)')

if water:
    resources["Water"] = {"source": None, "kind": "water", "recipe": None,
        "note": "Water charges, not an inventory item: drawn from base water storage near the crafter. enshrouded.tools shows them as 'N water charges' in the recipe header.",
        "sources": [SITE + "/items/green-vitriol-dust"]}
ae = resources.get("Archaic Essence I")
if ae is not None:
    ae["note"] = ("The cheapest option for 'Any Archaic Essence' (item level 5). " + (ae.get("note") or "")).strip()
for g, opts in groups.items():
    entry = {"source": "any of: " + ", ".join(opts), "kind": "gathered", "options": opts, "recipe": None,
             "note": "Recipe slot that accepts any one of the options.", "sources": [SITE]}
    if g == "Any Archaic Essence":
        entry["note"] += (" Archaic Essence I is the cheapest (gathered in Springlands Shroud Lairs, dropped by the Shroud Gazer); "
                          "Sparkworks parts take one each, the Sparkworks Workbench two.")
        entry["sources"] = [SITE + "/items/archaic-essence-i", SPARKWORKS_URL]
    resources[g] = entry

# ---- summary ----
n_rec = sum(1 for i in items if i["inputs"])
cats = {}
for i in items:
    cats[i["category"]] = cats.get(i["category"], 0) + 1
no_rec = [i["name"] for i in items if not i["inputs"]]
new = [i["name"] for i in items if i["newIn1_0"]]
notes = (
    f"{len(items)} base objects ({', '.join(f'{v} {k}' for k, v in cats.items())}); {n_rec} have a 1.0 recipe. "
    f"Not crafted: {', '.join(no_rec)} (confidence 'unknown', with 'obtained' saying how). "
    "Source: enshrouded.tools item pages, read from the 1.0 game files (footer: 'Game data: Steam build 25936191'); "
    "every recipe is likely-1.0 (datamined, not checked in game). "
    "Every station has a craft recipe in 1.0, including the ones the planner notes only as quest rewards; the quests still exist (see quest). "
    "Some also have one placed in the world (foundAt, the site's 'Where to find it' line): Smithing Tools, Mortar, Hand Spindle, Loom, "
    "Tanning Station, and the parts Crucible, Kettle, Scientific Instruments and Circular Sawblades. "
    "station is the station the recipe is made at or needs nearby (for a survivor's recipe, the 'Needs' station, e.g. Masonry Tools; the Oven's "
    "'Almanac of Plants and Seedlings' is a placeable the Farmer makes from Paper x25 and String x5); crafter is the survivor, null for the player. "
    "requires is the 'Needs' line of a player station's recipe (none here) and is otherwise empty. Unlike eternal-spells.json it doesn't add "
    "'Sheltered Bed' to survivor recipes: the site's quest The Blacksmith Needs A Shop says only that 'some recipes only craft while their "
    "crafter is sheltered', and no item page says which. "
    "quest is the quest that introduces the station or hands out its key part (Cauldron, Crucible, Scientific Instruments, Almanac), from the "
    "site's quest pages; its Rewards list doesn't say whether you get the item or just its recipe. "
    "otherRecipes on chests and magic chests are the site's extra 'By hand' recipes; they aren't labelled, but they match Keen's 1.0 note that "
    "'storage chests can be upgraded or turned into magic chests without emptying them', so they're probably the in-place upgrade costs (inferred). "
    "slots come from the planner's pre-1.0 wiki notes: enshrouded.tools doesn't list chest sizes. "
    "Placeholders: each planner placeholder maps to up to four real items (placeholder + libraryType); there is no pen or trough item in the game, "
    "so 'Animal pen' maps to the animal beds and the cheapest fence and gate, and 'Trough' to the feeders plus the decorative Water Trough. "
    f"newIn1_0 comes from the site's 1.0 list of new items ({', '.join(new)}). "
    "changes1_0 combines the site's 1.0 changelog (a diff of the last Early Access build against 1.0, also kept raw in resources' recipe.changed1_0) "
    "with a comparison against the planner's LIBRARY notes (pre-1.0 wiki); a difference the changelog doesn't show is flagged as a stale wiki note. "
    "Wood Planks only come from the Table Saw in 1.0, so every plank recipe (Wooden, Medium, Large, Huge Chest, Enormous Magic Chest, Loom, "
    "Masonry Tools, Tanning Station...) needs the Table Saw first. "
    "Resources follow each input's primary recipe (the one matching the site's 'Where to get it' line; 'Manual Crafting' is the by-hand recipe and "
    "'Huntress' the Hunter); Twigs and Animal Fur are listed as gathered (the site says they drop) with their recipes under otherRecipes. "
    "'Any X' slots are resources of kind gathered with their options; for 'Any Archaic Essence', Archaic Essence I is also listed. "
    "The site's prose 'About' blurbs can still quote Early Access numbers; recipe tables are 1.0."
)
out = {"fetched": "2026-10-15", "notes": notes, "items": items, "resources": dict(sorted(resources.items()))}
json.dump(out, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("items", len(items), "with recipes", n_rec, "resources", len(resources))
print("no recipe:", no_rec)
print("new in 1.0:", new)
