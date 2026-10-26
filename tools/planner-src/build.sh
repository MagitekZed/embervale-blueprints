#!/bin/sh
# Assemble the single-file planner page from its parts.
cd "$(dirname "$0")"
OUT=../embervale-blueprints.html
{
  cat head.html
  echo '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'
  echo '<script src="https://cdnjs.cloudflare.com/ajax/libs/pako/2.1.0/pako.min.js"></script>'
  echo '<script>'
  cat app1.js blocks.js recipes.js app2.js place.js mirror.js terrain.js pieces.js altar.js list.js layers.js levels.js history.js tools.js inspect.js craft.js catalogue.js crafting.js app3.js app4.js edit3d.js progress.js inventory.js guide.js keys.js app5.js walk.js panels.js projects.js app6.js
  echo '</script>'
} > "$OUT"
echo "built $OUT"
