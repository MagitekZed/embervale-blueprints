"""The building materials the wiki catalogue lacks (new in 1.0, and the overgrowths), with colours sampled from
enshrouded.tools' icons the same way as the wiki ones (lit-face tone, lifted as finalize.py does).

Usage: python -I colours_1_0.py <scratch dir>
Downloads each icon (webp) into <scratch dir>/icons-1-0, converts it to PNG with ffmpeg, and writes
catalogue_1_0.json here, which make_blocks_js.py adds to the catalogue. Regions come from
../craft-src/building-materials.json (the site's building-blocks tiers), so rebuild that first.
"""
import colorsys
import json
import os
import subprocess
import sys

from colours import read_png, tone_of

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://www.enshrouded.tools"
# slug, catalogue name, planner group, kind
NEW = [
    ("ancient-beacon-block", "Ancient Beacon Block", "Stone blocks", "wall"),
    ("ancient-circles-block", "Ancient Circles Block", "Stone blocks", "wall"),
    ("ancient-dungeon-block", "Ancient Dungeon Block", "Stone blocks", "wall"),
    ("ancient-stone-block", "Ancient Stone Block", "Stone blocks", "wall"),
    ("weathered-ancient-stone-block", "Weathered Ancient Stone Block", "Stone blocks", "wall"),
    ("moonstone-block", "Moonstone Block", "Stone blocks", "wall"),
    ("ancient-gold-block", "Ancient Gold Block", "Other blocks", "wall"),
    ("ornate-wood-block", "Ornate Wood Block", "Wood blocks", "wall"),
    ("ivy", "Ivy", "Overgrowth", "wall"),
    ("climbing-rose", "Climbing Rose", "Overgrowth", "wall"),
    ("mycelium-decoration", "Mycelium (overgrowth)", "Overgrowth", "wall"),
    ("wisteria", "Wisteria", "Overgrowth", "wall"),
    ("underwater-overgrowth", "Underwater Overgrowth", "Overgrowth", "wall"),
]


def lift(hexc, amt=0.18):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = l + (1 - l) * amt
    r, g, b = colorsys.hls_to_rgb(h, l, min(1.0, s * 1.08))
    return '#%02x%02x%02x' % tuple(int(round(v * 255)) for v in (r, g, b))


def main():
    root = os.path.join(sys.argv[1], "icons-1-0")
    os.makedirs(root, exist_ok=True)
    mats = json.load(open(os.path.join(HERE, "..", "craft-src", "building-materials.json"), encoding="utf-8"))
    by_name = {it["name"]: it for it in mats["items"]}
    out = []
    for slug, name, group, kind in NEW:
        webp, png = os.path.join(root, slug + ".webp"), os.path.join(root, slug + ".png")
        if not os.path.exists(webp):
            subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "-o", webp, f"{SITE}/img/items/{slug}.webp"], check=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", webp, "-pix_fmt", "rgba", png], check=True)
        w, h, px = read_png(png)
        tone = tone_of(px)
        it = by_name.get(name) or {}
        tier = it.get("tier") or ""
        region = tier.split(", ", 1)[1] if ", " in tier else ""
        maker = it.get("station") or it.get("crafter") or ""
        unlock = ("New in 1.0" if it.get("newIn1_0") else "") + (f"{' · ' if it.get('newIn1_0') else ''}made at the {maker}" if maker else "")
        out.append({"n": name, "g": group, "k": kind, "c": lift(tone) if tone else "#888888", "r": region, "u": unlock[:90],
                    "icon": f"{SITE}/img/items/{slug}.webp"})
        print(name, tone, out[-1]["c"], region, unlock)
    json.dump(out, open(os.path.join(HERE, "catalogue_1_0.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(len(out), "-> catalogue_1_0.json")


if __name__ == "__main__":
    main()
