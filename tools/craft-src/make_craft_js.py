"""Build planner-src/craft.js (the Crafting list's recipes) from the JSON files in this folder.

Each JSON file has { fetched, notes, items: [...], resources: {...} } (see eternal-spells.json). Files are
merged in name order; a later file's resource entry fills in fields an earlier one left empty.
Run: python make_craft_js.py   then rebuild the planner (sh ../planner-src/build.sh).
"""
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'planner-src', 'craft.js')

# What the planner needs from an item and a resource (perks, stat changes and the like stay in the JSON).
ITEM_KEYS = ('name', 'category', 'school', 'level', 'rarity', 'station', 'crafter', 'requires', 'makes', 'inputs', 'confidence', 'renamedFrom', 'sources',
             'catalogueName', 'libraryType', 'placeholder', 'slots', 'quest', 'foundAt', 'newIn1_0', 'note', 'opening', 'size', 'mount',
             'region', 'regionBy', 'found', 'comfort', 'resist', 'unlock', 'holdsNothing', 'tier')
RES_KEYS = ('source', 'kind', 'recipe', 'note')
# Notes the planner doesn't need to flag: things the data itself already says.
QUIET = ("'Sheltered Bed'", "Matches the user's")

items, resources, fetched, cats, replaced, merged = [], {}, set(), [], [], []
primaries = set()                                           # the first (basic) item for each planner library type
OVERRIDES = os.path.join(HERE, 'source-overrides.json')
for path in sorted(glob.glob(os.path.join(HERE, '*.json'))):
    if os.path.samefile(path, OVERRIDES):
        continue
    d = json.load(open(path, encoding='utf-8'))
    if d.get('fetched'):
        fetched.add(d['fetched'])
    for raw in d.get('items', []):
        it = {k: raw[k] for k in ITEM_KEYS if raw.get(k) not in (None, [], '')}
        it.setdefault('makes', 1)
        it['inputs'] = [dict({'item': i['item'], 'qty': i['qty']}, **({'water': True} if i.get('waterCharges') else {}))
                        for i in raw.get('inputs', []) if i.get('item') and i.get('qty')]
        it['sources'] = it.get('sources', [])[:1]
        check = [f for f in raw.get('flags', []) if not f.startswith(QUIET)]
        if check:
            it['check'] = check
        if it.get('libraryType') and it['libraryType'] not in primaries:
            primaries.add(it['libraryType']); it['primary'] = True
        # A name in two files: the later file's entry replaces the earlier one (structural.json takes over the
        # fences and trapdoors decorations.json and base-objects.json had). When the earlier one stands for a planner
        # library type it stays, and only takes the details it lacks (region, comfort, what unlocks it).
        k = next((j for j, x in enumerate(items) if x['name'] == it['name']), None)
        if k is not None:
            if items[k].get('libraryType'):
                for key in ('region', 'regionBy', 'found', 'comfort', 'resist', 'unlock', 'newIn1_0'):
                    if key in it and items[k].get(key) in (None, [], ''):
                        items[k][key] = it[key]
                if it.get('category'):                      # filed with its batch (a Wall Torch under Torches)
                    items[k]['category'] = it['category']
                merged.append(it['name'])
            else:
                items[k] = it; replaced.append(it['name'])
            continue
        items.append(it)
        if it.get('category') and it['category'] not in cats:
            cats.append(it['category'])
    for name, r in (d.get('resources') or {}).items():
        cur = resources.setdefault(name, {})
        for k in RES_KEYS:
            v = r.get(k)
            if v not in (None, [], '') and not cur.get(k):
                cur[k] = v
        rec = cur.get('recipe')
        if rec:                                             # keep a crafted part's recipe lean too
            cur['recipe'] = {k: rec[k] for k in ('station', 'crafter', 'requires', 'makes', 'inputs') if rec.get(k) not in (None, [], '')}
            for i in cur['recipe'].get('inputs', []):
                if i.get('anyOf'):                          # "Any wood": name the options as its source
                    r2 = resources.setdefault(i['item'], {})
                    if not r2.get('source'):
                        r2['source'] = 'any of: ' + ', '.join(i['anyOf'])
                    r2.setdefault('kind', 'gathered')
                    i.pop('anyOf')
        if cur.get('kind') == 'water' and not cur.get('source'):
            cur['source'] = 'water charges from your base water'

SURVIVORS = {'blacksmith', 'alchemist', 'carpenter', 'hunter', 'huntress', 'farmer', 'collector', 'fisher', 'bard', 'barber'}
# Crafted or gathered: a resource is crafted when its "where to get it" line names the station (or crafter) of
# its recipe. When it names a region instead, it's gathered there, and the recipe is only an alternative
# ("or craft at …"), which the breakdown doesn't follow.
for name, r in resources.items():
    rec = r.get('recipe')
    if not rec:
        continue
    makers = [m for m in (rec.get('station'), rec.get('crafter')) if m]
    src = (r.get('source') or '').lower()
    survivor = src in SURVIVORS                             # "Huntress", "Blacksmith": made by that survivor
    if src and makers and not survivor and not any(m.lower() in src or src in m.lower() for m in makers):
        r['alt'] = rec; r.pop('recipe'); r['kind'] = 'gathered'
    else:
        r['kind'] = 'crafted'
        if not src and makers:
            r['source'] = makers[0]

# a short source for resources the site gives none, summarised from their notes
for name, src in json.load(open(OVERRIDES, encoding='utf-8')).items():
    if not name.startswith('_') and name in resources and not resources[name].get('source'):
        resources[name]['source'] = src

# every input needs an entry, even if all we know is that it exists
for it in items:
    for i in it['inputs']:
        resources.setdefault(i['item'], {})

items.sort(key=lambda it: (cats.index(it['category']) if it.get('category') in cats else 99, it['name']))
unsure = sum(1 for it in items if it.get('confidence') not in ('confirmed-1.0', 'likely-1.0') or it.get('check'))
note = (f"{len(items)} recipes for 1.0, from enshrouded.tools, which reads them from the "
        f"1.0 game files (checked {', '.join(sorted(fetched)) or '?'}). Eternal Light Burst I matches the game exactly. "
        f"Quantities are crafts, so a stack of ammo counts once."
        + (f" ⚠ marks {unsure} worth double-checking in game." if unsure else ''))
data = {'note': note, 'items': items, 'resources': resources}
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('// Generated by tools/craft-src/make_craft_js.py from the JSON files there. Don\'t edit by hand.\n')
    f.write('const CRAFT = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
print(f'{len(items)} recipes, {len(resources)} resources, {unsure} flagged to check in game -> {os.path.relpath(OUT, HERE)}')
if replaced:
    print(f'{len(replaced)} taken over by a later file: {", ".join(replaced)}')
if merged:
    print(f'{len(merged)} library-type items given details from a later file: {", ".join(merged)}')
