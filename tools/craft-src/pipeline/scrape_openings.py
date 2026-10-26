"""Superseded (2026-10-20) by scrape_catalogue.py and build_catalogue.py (batch "structural"), which cover every structural piece.
Kept for reference; its output, doors-windows.json, is gone.

Scrape enshrouded.tools item pages for doors and windows (frames, double doors, secret doors), plus the
resource tree under their recipes. build_openings.py keeps the ones made from Springlands materials.

Usage: python -I scrape_openings.py <cache_dir> <out_json>

The page parsing is scrape_objects.py's (imported; it reads the same two arguments).
"""
import json
import sys

from scrape_objects import OUT, parse_item, primary_recipe

# Every door and window item in the site's sitemap (2026-10-15), less the trapdoors and fence gates
# (in base-objects.json) and the non-buildable "fake" and quest doors, which are fetched anyway to check.
SLUGS = """
crude-wooden-door crude-wooden-double-door wooden-door wooden-double-door rustic-door polished-wooden-door
polished-wooden-double-door carved-wooden-door carved-wooden-double-door carved-round-door round-wooden-door
round-wooden-door-frame metal-bound-wooden-door metal-bound-wooden-double-door fine-hardwood-door
fine-hardwood-double-door boreal-wood-door boreal-wood-double-door bamboo-door copper-door copper-double-door
iron-door iron-double-door iron-adorned-round-door iron-prison-door iron-prison-double-door ornate-steel-door
ornate-steel-double-door stone-door stone-double-door vault-door steel-portcullis lunar-new-year-door
ancient-temple-door ancients-night-door blackmire-temple-door huge-ancient-door huge-crypt-door large-crypt-door
large-drakdal-door round-ancient-door
secret-wooden-door secret-crude-wooden-bookshelf-door secret-bookshelf-door carved-secret-bookshelf-door
carved-secret-bookshelf-door-crafted secret-stone-door secret-flintstone-door secret-granite-door
secret-polished-granite-door secret-limestone-door secret-shell-limestone-door secret-sandstone-door
secret-red-marble-door secret-castle-door secret-basement-door secret-temple-door secret-ancient-door
fake-wooden-door fake-stone-door fake-castle-door fake-basement-door fake-temple-door fake-ancient-door-ancient
wooden-window-frame rustic-window-frame-i rustic-window-frame-ii carved-wooden-window-frame-i
carved-wooden-window-frame-ii high-carved-wooden-window-frame-i high-carved-wooden-window-frame-ii
wide-carved-wooden-window-frame polished-window-frame high-polished-window-frame stone-window-frame
granite-window-frame high-ornamented-stone-window-frame iron-window-frame-i iron-window-frame-ii
high-iron-window-frame-i high-iron-window-frame-ii large-iron-window-frame iron-prison-window-frame
high-iron-prison-window-frame large-golden-window-frame high-golden-window-frame large-ancient-window-frame
high-ancient-window-frame large-ancient-temple-window-frame high-ancient-temple-window-frame
round-wooden-window-frame round-polished-window-frame round-carved-window-frame round-stone-window-frame
round-iron-window-frame round-steel-window-frame large-round-wooden-window-frame large-round-polished-window-frame
large-round-carved-window-frame large-round-stone-window-frame large-round-iron-window-frame
large-round-steel-window-frame bamboo-window-i bamboo-window-ii bamboo-window-iii small-bamboo-window-i
small-bamboo-window-ii high-bamboo-window
""".split()


def main():
    items = {}
    for s in SLUGS:
        info = parse_item(s)
        items[s] = info
        print("item", s, info.get("name"), len(info["recipes"]), file=sys.stderr)
    resources, seen = {}, set()
    queue = [(inp["slug"], 1) for it in items.values() for r in it["recipes"] for inp in r["inputs"] if "slug" in inp]
    while queue:
        slug, depth = queue.pop(0)
        if slug in seen:
            continue
        seen.add(slug)
        info = items.get(slug) or parse_item(slug)
        resources[slug] = info
        print("res", depth, slug, info.get("name"), file=sys.stderr)
        r = primary_recipe(info)
        if r and depth < 8:
            queue += [(inp["slug"], depth + 1) for inp in r["inputs"] if "slug" in inp and inp["slug"] not in seen]
    json.dump({"items": items, "resources": resources}, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
