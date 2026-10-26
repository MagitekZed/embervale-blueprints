"""Build eternal-spells.json from scraped enshrouded.tools data.

Usage: python -I build.py <raw.json> <cache_dir> <tools-1-0.txt> <out.json>
"""
import html
import json
import re
import sys

RAW, CACHE, CHANGELOG, OUT = sys.argv[1:5]
raw = json.load(open(RAW, encoding="utf-8"))
items_raw = raw["items"]
res_raw = raw["resources"]

SITE = "https://www.enshrouded.tools"
CHANGELOG_URL = SITE + "/1-0"
WIKI_SPELLS = "https://enshrouded.wiki.gg/wiki/Spells"
NPC_CRAFTERS = {"Alchemist", "Collector", "Hunter", "Blacksmith", "Carpenter", "Farmer", "Bard", "Fisher"}
STAT_KEYS = {"Damage multiplier", "Mana Cost", "Charge Time", "Radius", "Duration", "Shield Health",
             "Debuff Duration", "Slow", "Damage", "Stack size", "Magical Critical Strike Chance"}


def card_lines(slug):
    t = open(f"{CACHE}/item-{slug}.html", encoding="utf-8").read()
    b, e = t.find("<main"), t.find("</main>")
    m = re.sub(r"<!--.*?-->", "", t[b:e], flags=re.S)
    m = html.unescape(re.sub(r"<[^>]+>", "\n", m))
    return [l.strip() for l in m.split("\n") if l.strip()]


def first_after(lines, key):
    if key in lines:
        i = lines.index(key)
        if i + 1 < len(lines):
            return lines[i + 1]
    return None


def damage_type(lines):
    if "Damage type" not in lines:
        return None
    i = lines.index("Damage type") + 1
    vals = []
    while i < len(lines) and lines[i] not in STAT_KEYS and len(vals) < 4 and len(lines[i]) < 24:
        vals.append(lines[i])
        i += 1
    return " / ".join(vals) if vals else None


def about(lines):
    if "About" in lines:
        i = lines.index("About") + 1
        out = []
        while i < len(lines) and lines[i] not in ("In-game text", "Where to get it", "Used in", "How to craft"):
            out.append(lines[i])
            i += 1
        return re.sub(r"\s+([,.])", r"\1", " ".join(out))
    return None


# ---- 1.0 changelog (enshrouded.tools diff of game data) ----
CL = open(CHANGELOG, encoding="utf-8").read().split("\n")
eternal_names = {it["name"] for it in items_raw.values()}
changes = {}
new_names = set()
# "New spells" and "Arrows and spells (19)" lists come before the changelog (index < 1000)
for i, l in enumerate(CL[:1000]):
    if l in eternal_names:
        new_names.add(l)
_recipes_start = next(i for i, l in enumerate(CL) if l.startswith("Changed recipes ("))
for i, l in enumerate(CL):
    if 2000 < i < _recipes_start and l in eternal_names:
        out = []
        for x in CL[i + 1:i + 30]:
            if x in eternal_names:
                break
            out.append(x)
            if x.startswith("Bonuses"):
                break
        changes.setdefault(l, []).extend(out)
# Recipe diff block for Eternal Chain Lightning II (only Eternal entry in the recipe diff)
recipe_diff = {}
for i, l in enumerate(CL):
    if i > 4000 and l in eternal_names and i + 1 < len(CL) and CL[i + 1] in NPC_CRAFTERS:
        diff = []
        for x in CL[i + 2:i + 10]:
            if "→" in x or x.startswith("+ ") or x.startswith("- "):
                diff.append(x)
            else:
                break
        recipe_diff[l] = diff


# Changed recipes section: "Name | Crafter | diff lines..."
changed_recipes = {}
try:
    a = CL.index("Changed recipes (409)")
except ValueError:
    a = next(i for i, l in enumerate(CL) if l.startswith("Changed recipes ("))
b = next(i for i in range(a + 1, len(CL)) if re.match(r"^Changed skill tree nodes \(", CL[i]))
def _is_diff(x):
    return "→" in x or x.startswith("+ ") or x.startswith("- ")
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


def split_recipe(r):
    crafter = r["crafter"]
    if crafter in NPC_CRAFTERS:
        return {"crafter": crafter, "station": r["needs"], "requires": ["Sheltered Bed"]}
    return {"crafter": None, "station": crafter, "requires": [r["needs"]] if r["needs"] else []}


def perks_of(lines):
    idx = [k for k, l in enumerate(lines) if l == "Perks"]
    if not idx:
        return []
    k = idx[-1] + 1
    out = []
    while k + 1 < len(lines) and lines[k] != "How to craft" and lines[k + 1].startswith("+"):
        v = lines[k + 1]
        v = v[1:] if v.startswith("+-") else v
        out.append({"stat": lines[k], "value": v})
        k += 2
    return out


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


# ---- items ----
items = []
order = sorted(items_raw.values(), key=lambda it: (it["kv"].get("Type") != "Spells", it["name"]))
for it in order:
    slug = it["slug"]
    kv = it["kv"]
    lines = card_lines(slug)
    is_spell = kv.get("Type") == "Spells"
    r = it["recipes"][0] if it["recipes"] else None
    rec = split_recipe(r) if r else {"crafter": None, "station": None, "requires": []}
    name = it["name"]
    ch = changes.get(name, [])
    renamed = next((c[len("Renamed from "):] for c in ch if c.startswith("Renamed from ")), None)
    flags = []
    entry = {
        "name": name,
        "category": "Eternal spells" if is_spell else "Eternal arrows",
        "school": damage_type(lines),
        "class": kv.get("Class"),
        "level": int(kv["Item level"]) if kv.get("Item level", "").isdigit() else None,
        "rarity": kv.get("Rarity"),
        "station": rec["station"],
        "crafter": rec["crafter"],
        "requires": rec["requires"],
        "makes": r["makes"] if r else None,
        "craftTime": r["time"] if r else None,
        "inputs": inputs_of(r) if r else [],
        "manaCost": first_after(lines, "Mana Cost"),
        "chargeTime": first_after(lines, "Charge Time"),
        "perks": perks_of(lines),
        "newIn1_0": name in new_names,
        "renamedFrom": renamed,
        "changes1_0": [c for c in ch if not c.startswith("Renamed from ")] or None,
    }
    if len(it["recipes"]) > 1:
        entry["otherRecipes"] = [dict(split_recipe(x), makes=x["makes"], inputs=inputs_of(x)) for x in it["recipes"][1:]]
    if name in recipe_diff:
        entry["recipeChanged1_0"] = recipe_diff[name]
    srcs = [it["url"]]
    if name in changes or name in recipe_diff:
        srcs.append(CHANGELOG_URL)
    if name == "Eternal Light Burst I":
        entry["confidence"] = "confirmed-1.0"
        flags.append("Matches the user's in-game 1.0 screenshot exactly (level 20, Epic, Laboratory/Alchemist, same 4 inputs).")
        srcs.append(WIKI_SPELLS)
    else:
        entry["confidence"] = "likely-1.0"
    if name == "Eternal Chain Heal II":
        flags.append("Recipe looks unusually cheap for a level-45 Legendary (Mortar, 3 cheap inputs). Data is from the game files, but worth checking in game.")
    if name == "Eternal Chain Lightning II":
        flags.append("Pre-1.0 'Eternal Chain Lightning' (lvl 32) was Steel Bars x25 + Silver Dust x43 at the Mortar (wiki); 1.0 data: Steel Bars x10 + Silver Dust x3, needs Laboratory.")
    if rec["crafter"] and rec["crafter"] != "Alchemist":
        flags.append(f"'Sheltered Bed' on the {rec['crafter']} line is inferred (all survivor crafters need a sheltered bed); only the Alchemist's is confirmed from the screenshot.")
    if flags:
        entry["flags"] = flags
    entry["sources"] = srcs
    items.append(entry)

# ---- resources (primary recipe chain) ----
by_slug = res_raw
resources = {}
queue = []
for it in items_raw.values():
    for r in it["recipes"]:
        for i in r["inputs"]:
            queue.append(i)
seen = set()
groups = {}
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
    lines = card_lines(slug)
    get = info.get("Where to get it")
    source = get[0] if get else None
    recipes = info["recipes"]
    primary = None
    if source:
        primary = next((r for r in recipes if r["crafter"] == source), None)
    elif recipes:
        primary = recipes[0]
    entry = {}
    inferred = False
    if primary:
        sr = split_recipe(primary)
        entry["kind"] = "crafted"
        if not source:
            source = primary["crafter"]
            inferred = True
        entry["source"] = source
        entry["recipe"] = {
            "station": sr["station"] if sr["station"] else None,
            "crafter": sr["crafter"],
            "requires": sr["requires"],
            "makes": primary["makes"],
            "time": primary["time"],
            "inputs": inputs_of(primary),
        }
        for i in primary["inputs"]:
            queue.append(i)
    else:
        entry["kind"] = "gathered"
        entry["source"] = source
        entry["recipe"] = None
    others = [r for r in recipes if r is not primary]
    if others:
        if len(others) <= 4:
            entry["otherRecipes"] = [dict(split_recipe(x), makes=x["makes"], time=x["time"], inputs=inputs_of(x)) for x in others]
        else:
            entry["otherRecipes"] = f"{len(others)} other recipes (e.g. {others[0]['crafter']}: {', '.join(i['item'] for i in others[0]['inputs'])})"
    if inferred:
        entry["sourceInferred"] = True
    ab = about(lines)
    if not get:
        entry["note"] = (ab or "No 'Where to get it' line on enshrouded.tools.")[:300]
    if primary:
        key = (info["name"], primary["crafter"])
        entry["recipe"]["changed1_0"] = changed_recipes.get(key)
    entry["category"] = info["kv"].get("Category")
    entry["sources"] = [info["url"]]
    resources[info["name"]] = entry

resources.setdefault("Water", {"source": None, "kind": "water", "recipe": None,
    "note": "Water charges, not an inventory item: drawn from base water storage near the crafter. enshrouded.tools shows them as 'N water charges' in the recipe header; the wiki lists them as 'Water xN'.",
    "sources": [SITE + "/items/eternal-ice-bolt-ii"]})
for g, opts in groups.items():
    resources.setdefault(g, {"source": None, "kind": "any-of", "options": opts, "recipe": None,
                             "note": "Recipe slot that accepts any one of the options.",
                             "sources": [SITE]})

spells = [i for i in items if i["category"] == "Eternal spells"]
arrows = [i for i in items if i["category"] == "Eternal arrows"]
lines_ = sorted({re.sub(r" (I|II|III|IV)$", "", i["name"]) for i in spells})
notes = (
    f"{len(spells)} Eternal spell items in {len(lines_)} spell lines (tiers I-IV; Entangle, Protective Barrier, Shock Totem, Shroud Beam and Shroud Meteor have one untiered item; Ball Lightning and Pillar Of Flames only a tier I), plus {len(arrows)} Eternal arrows "
    "(category 'Eternal arrows', included because they share the system). Source: enshrouded.tools item pages, which are read from the 1.0 game files "
    "(site footer: 'Game data: Steam build 25936191', 'Out now - version 1.0'). The 22 level-45 spell items are the '22 tier-7' Eternal spells from the 1.0 notes. "
    "Eternal Light Burst I matches the user's 1.0 screenshot exactly, so it is confirmed-1.0; every other item is likely-1.0 (same datamined source, not checked in game). "
    "No second post-1.0 source with recipes exists yet: enshrouded.wiki.gg Spells (last edited 2026-06-16) and the guide sites are pre-1.0 (old names like 'Eternal Light Burst' lvl 22). "
    "'school' is the game's 'Damage type' field. 'station' is the station the crafter needs nearby (null = crafter alone). "
    "'Sheltered Bed' is confirmed only for the Alchemist (screenshot); for Collector/Hunter/Fisher it is inferred. "
    "Resource 'source' is enshrouded.tools' 'Where to get it' line, which matches the game's source line in the screenshot (Smelter, Charcoal Kiln, Kindlewastes, Springlands); "
    "where that line is missing, source is null (or the recipe's crafter, flagged sourceInferred). Resource recipes use the recipe matching that source line; alternatives are in otherRecipes. "
    "Craft times and quantities come from the site's recipe tables, which agree with its 1.0 recipe diff (e.g. Charcoal 17 wood -> 12, makes 15 -> 10); the site's prose 'About' blurbs still quote Early Access numbers, so ignore them. "
    "Water appears as an input with waterCharges: true (recipe-header 'N water charges', drawn from base water storage). "
    "renamedFrom and changes1_0 come from the enshrouded.tools 1.0 changelog (a diff against Early Access game data)."
)
out = {"fetched": "2026-10-15", "notes": notes, "items": items, "resources": dict(sorted(resources.items()))}
json.dump(out, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("items", len(items), "spells", len(spells), "lines", len(lines_), "arrows", len(arrows), "resources", len(resources))
print(lines_)
