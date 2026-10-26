"""Build tools/flameborn-build-tester.html (the skill tree build tester) from page.html and tree.json.

tree.json is the 1.0 skill tree as enshrouded.tools has it (game build 25988036, read 2026-10-21): its skill
tree planner page embeds { key, links, nodes, levelCap }. To refresh after a game update, save
https://www.enshrouded.tools/skill-tree, pull that object out of the page's self.__next_f payload (the one
holding "links" and "nodes") into tree.json, and rerun this script. Build codes index nodes in tree.json's
order, so a refresh that adds or reorders nodes should bump CODE_VERSION in page.html.

gear.json is the gear that raises each skill, from the site's skill pages (scrape_gear.py). Gear is indexed
by name in build codes too (sorted by name and version), so a refresh that changes the item list also wants a
new CODE_VERSION.

Run: python build_tree.py   then republish tools/flameborn-build-tester.html.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'flameborn-build-tester.html')
TYPES = {'Root': 'R', 'Attribute': 'A', 'PassiveSkill': 'P', 'ActiveSkill': 'S'}
CLASSES = {'Neutral': 'N', 'Warrior': 'W', 'Ranger': 'G', 'Mage': 'M'}
FMT = {'Percentage': 'p', 'Normal': 'n', 'Duration': 'd'}
# Gear slots, from the item's name (the skill pages don't say). Armour slots take one item each.
SLOTS = [('Head', r'\b(helmet|hat|hood|crown|mask|cap|helm|circlet|headgear|headpiece|headwrap|cowl|headdress|headband|diadem|tiara|horns|visor|bandana|turban|veil|goggles|beret|bonnet)\b'),
         ('Chest', r'\b(chest|chestplate|robe|armou?r|tunic|coat|vest|jacket|shirt|cuirass|breastplate|top|dress|harness|garb|mantle|cloak|blouse|torso|body|plate)\b'),
         ('Hands', r'\b(gloves|gauntlets|bracers|handwraps|wraps|mitts|mittens|hands|arms|vambraces|grips|cuffs)\b'),
         ('Legs', r'\b(pants|trousers|legs|leggings|greaves|skirt|shorts|breeches|kilt|tassets|legguards|cuisses)\b'),
         ('Feet', r'\b(boots|shoes|sandals|swimfins|treads|feet|slippers|footwraps|sabatons|clogs)\b'),
         ('Ring', r'\bring\b'),
         ('Tool', r'\b(pickaxe|sieve)\b'),
         ('Weapon', r'\b(staff|wand|sword|axe|bow|dagger|shield|mace|hammer|club|spear|scythe|blade|knife|longbow|greatsword|cleaver|sceptre|scepter|rod|crossbow|torch|maul|warhammer|claymore|sabre|saber|rapier|flail|halberd|glaive|katana|ward|orb|tome|lantern|totem|eternal|helix|riptide|weaver|stormshield|eye|bulwark)\b')]


def slot_of(name):
    return next((s for s, pat in SLOTS if re.search(pat, name, re.I)), 'Other')


def arg(a):
    if a['k'] == 'input':
        return ['i', a['label']]
    return [FMT[a['fmt']], round(a['base'], 6), round(a['scale'], 6)]


T = json.load(open(os.path.join(HERE, 'tree.json'), encoding='utf-8'))
idx = {n['id']: i for i, n in enumerate(T['nodes'])}
nodes = []
for n in T['nodes']:
    nodes.append([round(n['x'], 1), round(n['y'], 1), TYPES[n['type']], CLASSES[n['cls']], n['max'], n['cost'], n['name'],
                  n['desc'].strip(), [arg(a) for a in n['descArgs']], (n['perLevel'] or '').strip(), [arg(a) for a in n['perLevelArgs']]])
links = sorted({tuple(sorted((idx[a], idx[b]))) for a, b in T['links']})
# gear: [name, version ('' / 'drop' / 'crafted'), slot, [[node index, +ranks], ...]], sorted by name
G = json.load(open(os.path.join(HERE, 'gear.json'), encoding='utf-8'))
by_name = {n['name']: i for i, n in enumerate(T['nodes']) if n['type'] in ('PassiveSkill', 'ActiveSkill')}
items = {}
for skill, gear in G['skills'].items():
    for g in gear:
        m = re.match(r'(.+?)(?: (drop|crafted))?$', g['item'])
        key = (m.group(1), m.group(2) or '')
        items.setdefault(key, []).append([by_name[skill], g['plus']])
gear = [[name, ver, slot_of(name), sorted(perks)] for (name, ver), perks in sorted(items.items())]
data = {'levelCap': T['levelCap'], 'nodes': nodes, 'links': links, 'gear': gear, 'gearFetched': G['fetched']}
page = open(os.path.join(HERE, 'page.html'), encoding='utf-8').read()
assert page.count('/*TREE_DATA*/null') == 1
page = page.replace('/*TREE_DATA*/null', json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
open(OUT, 'w', encoding='utf-8').write(page)
from collections import Counter
print(f'{len(nodes)} nodes, {len(links)} links, {len(gear)} gear items ({dict(Counter(g[2] for g in gear))}), {len(page) // 1024} KB -> {os.path.relpath(OUT, HERE)}')
