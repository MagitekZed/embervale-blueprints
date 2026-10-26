# Embervale Blueprints

Unofficial, fan-made planning tools for **Enshrouded 1.0**. They run in the browser, with nothing to install.

- **[Embervale Blueprints](https://magitekzed.github.io/embervale-blueprints/)**: a block-by-block base planner. Draw plans in 0.5 m blocks over levels or single block layers, see them in 3D, walk through them, and track a build as you go. It includes every 1.0 building block and item, a crafting list that totals resources down to what you gather and where, and an inventory the build tracking counts from.
- **[Flameborn Build Tester](https://magitekzed.github.io/embervale-blueprints/build-tester.html)**: the full 1.0 skill tree (243 nodes) laid out as in the game. Set your level, Elixir Wells, Shroud Roots and Flame level, spend points, add item skill bonuses and worn gear, and see your attributes and stats. Builds share as a link.
- **[Build guide](https://magitekzed.github.io/embervale-blueprints/build-guide.html)**: how the planner's build tracking works, from counting what you have to marking blocks built.

Plans, the inventory and saved builds are kept in your browser (local storage). Clearing your site data removes them, so copy out anything you want to keep: the planner's Plan tab has "Copy plan JSON", and the Build Tester gives each build a code.

## Data and credits

- Recipes, items, regions, the skill tree and the gear that raises each skill come from [enshrouded.tools](https://www.enshrouded.tools), which reads them from the 1.0 game files (build 25988036). Fetched in October 2026; the game changes, so check anything important in game.
- The block catalogue and its colours (sampled from the block icons), and the older recipes, come from the [Enshrouded Wiki](https://enshrouded.wiki.gg). Its content is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (the wiki's copyright page also names CC BY-NC-SA 3.0). This project is non-commercial.
- Enshrouded and its names and data belong to [Keen Games](https://www.keengames.com). This project isn't affiliated with or endorsed by them.

## Licence

Source-available under the [PolyForm Strict License 1.0.0](LICENSE.md). You may use the tools for personal and other noncommercial purposes, but not change them, build new works from them, or redistribute them. The licence covers only the original work here: the game, its data and the wiki material belong to others and keep their own terms (see [NOTICE.md](NOTICE.md)).

## Building from source

The pages are assembled from parts. You need a POSIX shell and Python 3.

```sh
sh tools/planner-src/build.sh             # tools/embervale-blueprints.html
python tools/skill-tree-src/build_tree.py  # tools/flameborn-build-tester.html
python tools/site/build_site.py _site      # the GitHub Pages site
```

Pushing to `main` builds and deploys the site (`.github/workflows/pages.yml`).

| Folder | What's in it |
| --- | --- |
| `tools/planner-src/` | The planner's source, in parts, and its generated data (`craft.js`, `blocks.js`) |
| `tools/skill-tree-src/` | The Build Tester's page, the skill tree and gear data, and their build and fetch scripts |
| `tools/craft-src/` | Recipe data for the crafting list and the scripts that fetch and merge it |
| `tools/blocks-src/` | The block catalogue's pipeline: wiki extraction and colour sampling |
| `tools/drafts/` | Python generators for drafted plans (the plans themselves are the `.json` files beside them) |
| `tools/site/` | Turns the built pages into the Pages site |

The pages were first built as claude.ai artifacts, where they save to a shared database. On GitHub Pages they fall back to the browser's own storage.
