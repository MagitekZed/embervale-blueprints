"""The catalogue batches: which of enshrouded.tools' building items each batch takes, and how each item sits in the
planner. Shared by scrape_catalogue.py and build_catalogue.py.

classify(batch, name) -> (category, mount, opening) or None.

  structural  doors (with door frames, secret doors and the portcullis), windows, gates, trapdoors (with secret floor
              passages), stairs, ladders, fences and railings, grates, supports and columns, boardwalks, awnings and
              the standalone wall pieces. Sparkworks shapes (ramps, cubes, trampolines, water barriers) wait for the
              Sparkworks batch.
  lights      torches, lanterns, lamps, candles, chandeliers, braziers and fire bowls, fireplaces and campfires,
              coloured lights, prayer beacons and Hollow's Eve pumpkins.
  storage     chests, magic chests and quick stack stations (the only things that hold items: the planner files
              these as Storage), weapon racks (they display weapons and shields: Displays), and storage-style
              furniture that holds nothing (cabinets and cupboards, shelves, baskets, barrels and crates, vases, pots
              and urns: decoration). Nightstands and bedside tables (Table comfort) are furniture. The user's rule: Storage only if it stores items, Displays if it shows them,
              otherwise decoration.
  displays    collection showcases, weapon wall mounts, mannequins and display stands (Displays), and trophies and
              wig heads (decoration).
  furniture   beds, chairs and stools, benches and sofas, thrones, tables, desks and counters (Furniture), and
              decorative cushions (decoration).
  wallart     paintings, banners and flags, tapestries, rugs and mats, emblems, signs, wall flowers and wreaths (all
              decoration).
  categorized seedlings, plants, plant pots, farming, animal care, farm animals, pets, tableware, kitchen, bathroom
              (with the bathtubs) and Sparkworks.
  other       everything left: crafting stations and their parts, survivors, building tools and reward bundles,
              statues, books, crypt and graveyard, room dividers, festive, science and curios, sideboards, training,
              paintings with plain titles, and other decorations.

Earlier batches win (classify()), so every building item is in exactly one batch.

Blocks (the site's building-blocks page) are always left to the materials files.
"""
import re


def light_mount(name):
    if re.search(r"\bWall\b|Wall Mounted|Sconce", name):
        return "wall"
    if re.search(r"Ceiling|Chandelier|Hanging|Pendant", name):
        return "ceiling"
    return "floor"


def refile_categorized(name, cat, desc, comfort):
    """Batch "categorized" sorted by what each piece does, from its page's description (the user's rule: Storage only
    if it holds items, Displays if it shows them, decoration if it's just decoration)."""
    deco = "decorative object" in desc
    if cat == "Kitchen":
        return "Station parts" if name == "Cauldron" else "Kitchenware" if deco else "Kitchen stations"
    if cat == "Tableware":
        return "Platters" if "display foods" in desc else "Station parts" if name == "Kettle" else "Tableware"
    if cat == "Farming":
        if deco or name == "Scare Crow":
            return "Farm decor"
        if "water" in desc.lower():
            return "Water"                                  # wells, dispensers, irrigation gates
        if name == "Cultivation Rack":
            return "Display stands"                         # holds up to 3 ancient plant pots
        if name == "Beehive Smoker":
            return "Station parts"                          # unlocks the Honey Beehive
        return "Farming"
    if cat == "Bathroom":
        return "Water" if "drain" in desc.lower() else "Bathroom" if comfort else "Bathroom decor"
    if cat == "Animal care":
        if "decorative pillow" in desc or (comfort and comfort.get("type") == "Wellness"):
            return "Cushions"
        if name == "Snap Trap":
            return "Sparkworks"                             # a trap, with the Sparkworks traps
        return "Farm decor" if deco else "Animal care"
    if cat == "Sparkworks":
        if "pre-defined structures" in desc:
            return "Building tools"                         # the shape tools (cubes, ramps, discs)
        if "Water Barrier" in name:
            return "Water"
        if name == "Logo Symbol Projector":
            return "Coloured lights"
        if "decorative" in desc and not name.startswith("Trampoline"):   # (trampolines read "decorative" but launch you)
            return "Mechanical props"
    return cat


def refile_other(name, cat, desc, comfort):
    """Batch "other" sorted by what each piece does, from its page's description."""
    if "force for a mill" in desc or "power a mill" in desc:
        return "Mill power"                                 # water wheels and windmill sails
    if "fireworks" in desc:
        return "Festive"                                    # the fountains are fireworks too
    if "attach direction signs" in desc:
        return "Signs"
    if "buff" in desc.lower() and "Shrine" in name:
        return "Buff shrines"                               # the Vukah Shrine grants a damage buff
    if cat == "Paintings" and "painting" not in desc.lower():
        return "Other decorations"
    return cat


# Each batch: rules (pattern on the name, category, mount or a function of the name, opening; first match wins),
# names to skip, what its items are called, and the file it writes.
BATCHES = {
    "structural": {
        "what": "structural pieces",
        "out": "structural.json",
        "rules": [
            (r"\bTrapdoor\b|Floor Passage", "Trapdoors", "floor", None),
            (r"\bBoardwalk\b|Baordwalk", "Walkways", "floor", None),       # (the site spells one "Baordwalk")
            (r"\bAwning\b|^Tarpaulin( Corner)?$", "Awnings", "floor", None),
            (r"\bArc$", "Arches", "floor", None),
            (r"Handrail", "Railings", "floor", None),
            (r"^(Simple Wooden|Signpost) Pole$", "Supports", "floor", None),
            (r"\bGate\b|Fence Door$", "Gates", "floor", None),
            (r"\b(Stairs?|Stair Passage)\b", "Stairs", "floor", None),
            (r"\bLadder\b", "Ladders", "floor", None),
            (r"\bWindow\b", "Windows", "window", "window"),
            (r"\bDoor\b|\bPortcullis\b", "Doors", "door", "door"),
            (r"\bBanister\b", "Railings", "floor", None),
            (r"\bFence\b|\bPalisade\b|\bBarricade\b", "Fences", "floor", None),
            (r"\bGrate\b", "Grates", "floor", None),
            (r"\bScaffold\b|\bSupport\b|\bStrut\b", "Supports", "floor", None),
            (r"\bColum(n)?\b", "Columns", "floor", None),   # (column blocks are props, not building materials)
            (r"^Wood Wall [IV]+$", "Wall pieces", "floor", None),
        ],
        "skip": r"Wall Mount|Wall Banner|Wall Torch|Wall Lamp|Wall Light|Wall Flower|Wall Emblem|Wall Shelf|"
                r"Wall Drain|Wall Sign|Wall Target|Tapestry|Brazier|Candleholder|Lantern|Display Pillar|"
                r"Irrigation Gate|Goalpost|Signpost|Water Barrier",
    },
    "lights": {
        "what": "lights",
        "out": "lights.json",
        "rules": [
            (r"Hollow's Eve Pumpkin", "Pumpkins", "floor", None),
            (r"Prayer Beacon", "Beacons", "floor", None),
            (r"Chandelier", "Chandeliers", "ceiling", None),
            (r"Fireplace|Campfire|Bonfire", "Fireplaces and campfires", "floor", None),
            (r"Brazier|Fire Bowl", "Braziers and fire bowls", light_mount, None),
            (r"Torch", "Torches", light_mount, None),
            (r"Candle", "Candles", light_mount, None),
            (r"Lantern", "Lanterns", light_mount, None),
            (r"Lamp\b", "Lamps", light_mount, None),
            (r"(Floor|Wall|Pendant) Light\b|^Light$", "Coloured lights", light_mount, None),
        ],
        "skip": r"Block$|^Crystal |Miniature|Emblem|Flame Altar|Showcase|Reward Items|^Tome of|Seedling|Garden Gnome",
    },
    "storage": {
        "what": "storage pieces",
        "out": "storage.json",
        # Only chests (magic ones too) hold anything. The `decor` categories are storage-style furniture that holds
        # nothing, which the build marks (`holdsNothing`). Plant pots, showcases and coffins are other batches.
        "decor": {"Cabinets and cupboards", "Shelves", "Baskets", "Barrels and crates", "Vases, pots and urns"},
        "rules": [
            (r"^Water Barrel$", "Water", "floor", None),       # stores rainwater, not items: a base utility
            (r"Magic Chest|Quick Stack Station", "Magic chests", "floor", None),
            (r"\bChest\b", "Chests", "floor", None),
            (r"Cabinet|Cupboard|Closet|Wardrobe|Dresser", "Cabinets and cupboards", "floor", None),
            (r"\bShel(f|ves)\b|Bookcase", "Shelves", light_mount, None),
            (r"\bBasket\b", "Baskets", "floor", None),
            (r"Barrel|Crate|Container|Decorative Box|Jewelry Box|Sacks?\b|Leather Bag|Resource Bundle", "Barrels and crates", "floor", None),
            (r"\bVases?\b|\bPot\b|\bUrn\b|\bVat\b|Bucket|\bJar\b", "Vases, pots and urns", "floor", None),
            (r"Weapon Rack|Shield Rack", "Weapon racks", "floor", None),
        ],
        "skip": r'^"|Plant Pot|Empty .* Pot|Showcase|Coffin|Explosive Barrel|Box 4m|Switchbox',
    },
    "displays": {
        "what": "displays and trophies",
        "out": "displays.json",
        # Displays show items you place in them (their pages say so): collection showcases, weapon wall mounts,
        # mannequins, and stands for instruments, planetary models and fishing records. Trophies and wig heads are
        # the thing itself, so they're decoration (trophies give Trophy comfort; a wig head unlocks haircuts).
        "rules": [
            (r"Showcase", "Showcases", light_mount, None),
            (r"Wall Mount", "Wall mounts", "wall", None),
            (r"^Mannequin", "Mannequins", "floor", None),
            (r"^Instrument Stand$|^Orrery Display Pillar$", "Display stands", "floor", None),
            (r"^Fish Trophy Board$", "Display stands", "wall", None),
            (r"Wig Head", "Wig heads", "floor", None),
            (r"Skull Trophy", "Trophies", "floor", None),
            (r"Trophy", "Trophies", "wall", None),
        ],
        "skip": r"Grappling Hook|Wall Mounted",
    },
    "furniture": {
        "what": "furniture pieces",
        "out": "furniture.json",
        # Beds, seats and tables: functional (survivors need beds, and they give comfort), so the planner lists them
        # as Furniture. Decorative cushions are decoration. Animal beds and pet pillows wait for the farm batch.
        "decor": {"Cushions"},
        "rules": [
            (r"\bBed\b|Mattress", "Beds", "floor", None),
            (r"Throne", "Thrones", "floor", None),
            (r"Bench|Sofa", "Benches and sofas", "floor", None),
            (r"Chair|Stool|Armchair|Lounger", "Chairs and stools", "floor", None),
            (r"\bDesk\b|Counter", "Desks and counters", "floor", None),
            (r"\bTable\b|Nightstand", "Tables", "floor", None),
            (r"^(Heart|Cylindrical) Pillow", "Cushions", "floor", None),
        ],
        "skip": r"Workbench|Table Saw|Shootable|Throne Room|Farm Animal|^(Cat|Dog|Fae Deer|Hophare|Flightless Redtail) Pillow",
    },
    "wallart": {
        "what": "wall art and textiles",
        "out": "wallart.json",
        # All decoration. (Quoted wig heads and the tapestry showcase are displays.)
        "rules": [
            (r'^"', "Paintings", "wall", None),
            (r"Tapestry", "Tapestries", "wall", None),
            (r"Standing Banner|Flag Pole", "Banners and flags", "floor", None),
            (r"Banner", "Banners and flags", "wall", None),
            (r"\bRug\b|Carpet|\bMat\b", "Rugs and mats", "floor", None),
            (r"Emblem", "Emblems", "wall", None),
            (r"^(Direction|Ground) Sign$", "Signs", "floor", None),
            (r"\bSign\b", "Signs", "wall", None),
            (r"Wall Flower|Wreath", "Wall flowers and wreaths", "wall", None),
        ],
        "skip": r"Wig Head|Showcase",
    },
    "categorized": {
        "what": "plants, farm, kitchen, bathroom and Sparkworks pieces",
        "out": "categorized.json",
        "refile": refile_categorized,
        "rules": [
            (r"Seedling$", "Seedlings", "floor", None),
            (r"Plant Pot|^Empty .* Pot$", "Plant pots", "floor", None),
            (r"\bPlant$|Flower$|^Fern$|^Grass$|^Alpine Rose$", "Plants", "floor", None),
            (r"Farmbed|^Plough$|^Harrow$|^Scare ?Crow$|Wheel ?Barrow|Waggon|^Straw Pile$|Beehive|Cultivation Rack|"
             r"Irrigation Gate|Water Well|Water Dispenser", "Farming", "floor", None),
            (r"Feeder|Pillow|^(Cat|Dog) Bowl$|^Water Trough$|^Snap Trap$", "Animal care", "floor", None),
            (r"^Baby |^(Capybara|Common Goat|Frizzy Goat|Yak|Hophare|Fae Deer|Dune Armadillo|Round-Billed Sailer|"
             r"Flightless Redtail)$", "Farm animals", "floor", None),
            (r"^(Captain Whiskers|Ikko|Pompom Jr\.|Ruffles|Sapphire|Tyger)$", "Pets", "floor", None),
            (r"(Bowl|Cup|Jug|Platter)$|Ladle|Scrap Pan|^Kettle$|Flask$|Pitcher|Coaster", "Tableware", "floor", None),
            (r"Decorative Oven|Butter Churn|Seafood Grill|Coffee Brewery|Coffee Drum Roaster|^Cauldron$|"
             r"Fish Drying Rack|^Fish Trap$|^Small Mortar$", "Kitchen", "floor", None),
            (r"Lavatory|Shower|\bSink\b|Toilet|Salon Mirror|Wall Drain|Bathtub", "Bathroom", light_mount, None),
            (r"Floor Drain", "Bathroom", "floor", None),
            (r"^(Box 4m|Cube [24]m|Disc 3m|Rock 2m)$|ramp [24]m|Trampoline|Water Barrier|Explosive Barrel|"
             r"Grappling Hook|^Robotic Arm$|^Pulley$|^Lever|Button$|^Pressure Plate$|Trap$|^Spawner$|^Sparkworks|"
             r"^Goalpost$|^Logo Symbol Projector$", "Sparkworks", "floor", None),
        ],
        "skip": r"^Crystal Ball$|Garden Gnome",
    },
    "other": {
        "what": "everything else",
        "out": "other.json",
        "refile": refile_other,
        # Whatever no earlier batch takes (classify() lets earlier batches win). The last rule catches the rest.
        "rules": [
            (r"^(Workbench|Forge|Kiln|Charcoal Kiln|Smelter|Blast Furnace|Smithing Tools|Alchemy Station|Grinding Stones|"
             r"Mortar|Laboratory|Table Saw|Masonry Tools|Tanning Station|Drying Rack|Hand Spindle|Loom|Spinning Wheel|"
             r"Spinning Machine|Seedbed|Cooking Station|Oven|Kitchen|Decoration Workbench|Ancient Workbench|"
             r"Infusion Altar|Mill|Improved Millstone|Placeable Gem Forge|Ectoplasm Press|Athanor|Coloring Station)$",
             "Crafting stations", "floor", None),
            (r"^(Crucible|Bellows|Almanac of Plants and Seedlings|Scientific Instruments)$", "Station parts", "floor", None),
            (r"^Flame Altar$", "Base & furniture", "floor", None),
            (r"Construction Hammer|Decay Tool|Overgrowth Tool|^Summoning Staff$", "Building tools", "floor", None),
            (r"Reward Items$|^Deluxe Edition Items$", "Reward bundles", "floor", None),
            (r"^(Alden Crowley|Anton Godwin|Athalan Skree|Aunt Braelyn|Balthazar|Cade Hawthorn|Captain Melville Fontane|"
             r"Chester Loft|Elio Ricci|Emily Fray|Fenrig Mills, Jr\.|Gabrielle Fairburn|Galen Yager|Gunther Galeforth|"
             r"Hannah Reed|Hugo Vanderhall|Kaori Conway|Lady Leclair|Loraine Crim|Marianne Reed|Mei-Yin Chen|"
             r"Nameless One|Oscar Godwin|Oswald Anders|Ramone Jones|Robert Gibson|Rochelle Anders|Valory)$",
             "Survivors", "floor", None),
            (r"^Instrument Holder$", "Display stands", "wall", None),
            (r"Statue|Totem|Shrine|Garden Gnome|Plush", "Statues and figures", "floor", None),
            (r"^Book [IV]+\b|Collection Of Books|Bookrest|^Tome of", "Books", "floor", None),
            (r"Coffin|Mausoleum|Tombstone|Decorative Skull|Spider Web", "Crypt and graveyard", light_mount, None),
            (r"Room Divider", "Room dividers", "floor", None),
            (r"Snowpal|Decorated Tree|Confetti Mortar|Rocket$|Decorative Bells", "Festive", "floor", None),
            (r"Microscope|Pipette|Centrifuge|Cooling Unit|Measuring Device|Telescope|Globe$|^Orrery$|^Crystal Ball$|"
             r"Miniature Model|Ceiling Mobile", "Science and curios", light_mount, None),
            (r"Sideboard", "Cabinets and cupboards", "floor", None),
            (r"Training Doll|Target$", "Training", light_mount, None),
            (r"^(A Spiral Down, Down, Down|Above The Vermin, The Cowards, The Liars|Ashes Of Pikemead's Reach|"
             r"Beginning Of The End|Broken Guard Of The North Crown|Gift Of Violence|Initiation|Jezmina's Journey Begins|"
             r"Servant Of Chaos|The Horde Unleashed|The Last Spark)$", "Paintings", "wall", None),
            (r".", "Other decorations", "floor", None),
        ],
        "skip": r"^$",
    },
}


def _match(batch, name):
    b = BATCHES[batch]
    if not name or re.search(b["skip"], name, re.I):
        return None
    for pat, cat, mount, opening in b["rules"]:
        if re.search(pat, name):
            return cat, (mount(name) if callable(mount) else mount), opening
    return None


def classify(batch, name):
    """The item's (category, mount, opening) in this batch, or None. Earlier batches win: an item one of them takes
    is never in a later one, so the last batch ("other") is simply everything left."""
    for b in BATCHES:
        if b == batch:
            return _match(batch, name)
        if _match(b, name):
            return None
    return None
