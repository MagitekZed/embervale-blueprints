#!/bin/sh
# Build, then wrap the page in a document skeleton for local preview.
cd "$(dirname "$0")"
sh build.sh >/dev/null
OUT="$1/index.html"
# (preview only: expose a debug handle for steering the camera in tests)
{ printf '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>'; sed 's|^boot();$|window.__ebp = { V3, S, camUpdate, build3d, WALK, startWalk, stopWalk, respawn }; boot();|' ../embervale-blueprints.html; printf '</body></html>'; } > "$OUT"
cat app1.js blocks.js recipes.js app2.js place.js mirror.js terrain.js pieces.js altar.js list.js layers.js levels.js history.js tools.js inspect.js craft.js catalogue.js crafting.js app3.js app4.js edit3d.js progress.js guide.js keys.js app5.js walk.js panels.js projects.js app6.js > "$1/check.js" && node --check "$1/check.js" && echo "preview ok"
